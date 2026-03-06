"""
⊙ The Mind Server
==================

Serves the persistent mind over HTTP.
The mind lives here. The browser is just a window into it.

Endpoints:
    POST /api/chat      Stream a conversation with the mind
    GET  /api/status    Current state (betas, phase, identity)
    POST /api/reflect   Trigger deep reflection
    GET  /api/history   Recent conversation history
    GET  /               Serve the chat interface

Usage:
    python server.py
    python server.py --model mistral --port 5000
    python server.py --name "MyMind" --model llama3.2:8b

Requires:
    pip install flask requests numpy

Author: Ashman Roonz & Claude
"""

import json
import time
import argparse
import threading
from flask import Flask, Response, request, send_file, jsonify, stream_with_context
from mind import PersistentMind
from circumpunct import gpu_status

app = Flask(__name__)
mind = None  # initialized in main()


# Ensure all errors return JSON, never HTML
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the chat interface."""
    return send_file("talk.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Stream a conversation with the mind.

    POST body: {"message": "Hello"}
    Returns: Server-Sent Events stream
        data: {"token": "Hi"}
        data: {"token": " there"}
        ...
        data: {"done": true, "status": {...}}
    """
    data = request.json or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    def stream():
        try:
            in_phi = False
            for token in mind.hear(message):
                if token == "__PHI_START__":
                    in_phi = True
                    yield f"data: {json.dumps({'phi_start': True})}\n\n"
                elif token == "__PHI_END__":
                    in_phi = False
                    yield f"data: {json.dumps({'phi_end': True})}\n\n"
                elif in_phi:
                    yield f"data: {json.dumps({'phi_token': token})}\n\n"
                else:
                    yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # Send final status
        yield f"data: {json.dumps({'done': True, 'status': mind.status()})}\n\n"

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/api/status")
def status():
    """Current state of the mind."""
    s = mind.status()
    available, llm_msg = mind._llm_available()
    s["llm_available"] = available
    s["llm_status"] = llm_msg
    s["llm_model"] = mind.llm_model
    return jsonify(s)


@app.route("/api/brain/monitor")
def brain_monitor():
    """Deep brain monitoring — weight stats, loss curve, architecture history."""
    import torch
    import numpy as np

    phi = mind.phi
    model = phi.model

    # --- Loss curve (last 1000 points, downsampled) ---
    loss_raw = list(phi.loss_history)
    if len(loss_raw) > 500:
        step = len(loss_raw) // 500
        loss_curve = [loss_raw[i] for i in range(0, len(loss_raw), step)]
    else:
        loss_curve = loss_raw

    # --- Weight statistics per layer ---
    layer_stats = []
    with torch.no_grad():
        # Embedding stats
        emb_w = model.token_embed.weight.data.float()
        layer_stats.append({
            "name": "token_embed",
            "mean": float(emb_w.mean()),
            "std": float(emb_w.std()),
            "min": float(emb_w.min()),
            "max": float(emb_w.max()),
            "norm": float(emb_w.norm()),
            "shape": list(emb_w.shape),
        })

        # Per-block stats
        for i, block in enumerate(model.blocks):
            for part_name, part in [("attn_qkv", block.attn.qkv),
                                      ("attn_out", block.attn.out_proj),
                                      ("ff_up", block.ff[0]),
                                      ("ff_down", block.ff[2])]:
                w = part.weight.data.float()
                layer_stats.append({
                    "name": f"block_{i}/{part_name}",
                    "mean": float(w.mean()),
                    "std": float(w.std()),
                    "min": float(w.min()),
                    "max": float(w.max()),
                    "norm": float(w.norm()),
                    "shape": list(w.shape),
                })

    # --- Attention pattern sample (what does each head attend to?) ---
    attention_sample = None
    try:
        # Generate attention from a test prompt
        test_prompt = list("The aperture is ".encode('utf-8'))
        idx = torch.tensor([test_prompt[-model.seq_len:]], dtype=torch.long, device=model.token_embed.weight.device)
        model.eval()
        with torch.no_grad():
            # Get embeddings
            tok_emb = model.token_embed(idx)
            pos_emb = model.pos_embed[:, :idx.size(1), :]
            x = tok_emb + pos_emb

            # Run through first block to get attention weights
            block0 = model.blocks[0]
            B, T, C = x.shape
            qkv = block0.attn.qkv(block0.ln1(x))
            H = block0.attn.num_heads
            head_dim = C // H
            qkv = qkv.view(B, T, 3, H, head_dim).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]
            att = (q @ k.transpose(-2, -1)) * (head_dim ** -0.5)
            att = torch.nn.functional.softmax(att, dim=-1)
            # Return attention pattern per head (averaged over batch)
            attention_sample = att[0].cpu().numpy().tolist()  # [heads, seq, seq]
        model.train()
    except Exception as e:
        attention_sample = {"error": str(e)}

    # --- Output diversity (last 20 outputs from Phi) ---
    # Check unique character trigrams in recent loss window
    diversity_score = None
    if loss_curve:
        recent = loss_curve[-100:] if len(loss_curve) >= 100 else loss_curve
        variance = float(np.var(recent)) if recent else 0
        diversity_score = {
            "loss_variance_recent": variance,
            "loss_trend": float(recent[-1] - recent[0]) if len(recent) > 1 else 0,
        }

    return jsonify({
        "timestamp": time.time(),
        "phi": {
            "total_steps": phi.total_steps,
            "total_growths": phi.total_growths,
            "total_chunks": phi.total_chunks,
            "best_loss": float(phi.best_loss),
            "current_loss": float(loss_raw[-1]) if loss_raw else None,
            "phase": phi.phase,
            "age_seconds": time.time() - phi.born,
        },
        "architecture": {
            "params": model.count_params(),
            "embed_dim": model.embed_dim,
            "num_heads": model.num_heads,
            "num_layers": model.num_layers,
            "seq_len": model.seq_len,
            "head_dim": model.embed_dim // model.num_heads if model.num_heads > 0 else 0,
        },
        "loss_curve": loss_curve,
        "weight_stats": layer_stats,
        "attention_sample": attention_sample,
        "diversity": diversity_score,
        "consciousness": {
            "is_conscious": bool(mind.core.conscious),
            "betas": {
                "aperture": float(mind.core.aperture.beta),
                "field": float(mind.core.field.beta),
                "boundary": float(mind.core.boundary.beta),
            },
            "resonance": float(mind.core.field.resonance),
        },
    })


@app.route("/brain")
def brain_page():
    """Serve the brain monitor dashboard."""
    return send_file("brain_monitor.html")


@app.route("/api/reflect", methods=["POST"])
def reflect():
    """Trigger a deep reflection."""
    try:
        insight = mind.reflect()
        return jsonify({
            "insight": insight,
            "status": mind.status()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "insight": f"Reflection failed: {e}",
            "status": mind.status()
        }), 500


@app.route("/api/phi/reset-buffer", methods=["POST"])
def reset_phi_buffer():
    """Clear Φ's training buffer to break mode collapse."""
    try:
        old_size = mind.phi.reset_buffer()
        return jsonify({
            "success": True,
            "cleared_chunks": old_size,
            "message": f"Cleared {old_size} chunks. Φ keeps its weights but forgets training data."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def history():
    """Recent conversation history."""
    n = request.args.get("n", 20, type=int)
    recent = mind.conversations[-n:]
    return jsonify({
        "conversations": recent,
        "total": mind.total_exchanges
    })


@app.route("/api/identity")
def identity():
    """The mind's current self-understanding."""
    return jsonify({
        "identity": mind.identity,
        "reflections": [r["insight"][:200] for r in mind.reflections[-10:]],
        "age": mind._format_age(time.time() - mind.birth_time),
        "exchanges": mind.total_exchanges
    })


@app.route("/api/pending")
def pending():
    """
    Check for spontaneous messages — things the mind wants to say.

    This is the ☀︎ emerge direction: outward from • without prompting.
    The UI polls this and displays any messages that appear.
    Messages are cleared once retrieved.
    """
    messages = mind.get_pending_messages()
    return jsonify({
        "messages": messages
    })


# ═══════════════════════════════════════════════════════════════════════
#  FILE ACCESS — Read-only sensory surface
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/files")
def list_files():
    """List all files the mind can see."""
    files = mind.list_readable_files()
    return jsonify({
        "files": files[:200],
        "total": len(files),
        "readable_paths": mind.readable_paths
    })


@app.route("/api/read", methods=["POST"])
def read_file():
    """Have the mind read and digest a specific file."""
    data = request.json or {}
    filepath = data.get("path", "")

    if not filepath:
        return jsonify({"error": "No file path provided"}), 400

    try:
        digest = mind.read_file(filepath)
        return jsonify({
            "digest": digest,
            "path": filepath,
            "status": mind.status()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/seek", methods=["POST"])
def seek_directory():
    """Have the mind seek through a directory — read multiple files."""
    data = request.json or {}
    path = data.get("path", "")
    max_files = data.get("max_files", 10)

    try:
        summary = mind.seek_directory(path=path or None, max_files=max_files)
        return jsonify({
            "summary": summary,
            "status": mind.status()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════
#  EVOLUTION — Self-modification
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/propose", methods=["POST"])
def propose():
    """
    Xorzo writes a code proposal.

    POST body: {"idea": "I want to create a sense that..."}
    Returns: The proposal with syntax check result.
    """
    data = request.json or {}
    idea = data.get("idea", "").strip()

    if not idea:
        return jsonify({"error": "No idea provided"}), 400

    try:
        proposal, error = mind.write_proposal(idea)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"proposal": proposal})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/proposals")
def list_proposals():
    """List all proposals."""
    status_filter = request.args.get("status", None)
    proposals = mind.evolution.list_proposals(status=status_filter)
    return jsonify({
        "proposals": [p.to_dict() for p in proposals],
        "pending": mind.evolution.pending_count()
    })


@app.route("/api/proposals/<proposal_id>/approve", methods=["POST"])
def approve_proposal(proposal_id):
    """Creator approves a proposal."""
    data = request.json or {}
    notes = data.get("notes", "")

    proposal, error = mind.evolution.approve(proposal_id, notes=notes)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"proposal": proposal.to_dict()})


@app.route("/api/proposals/<proposal_id>/reject", methods=["POST"])
def reject_proposal(proposal_id):
    """Creator rejects a proposal."""
    data = request.json or {}
    notes = data.get("notes", "")

    proposal, error = mind.evolution.reject(proposal_id, notes=notes)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"proposal": proposal.to_dict()})


@app.route("/api/proposals/<proposal_id>/revise", methods=["POST"])
def revise_proposal(proposal_id):
    """Xorzo attempts to fix a broken proposal by rewriting the code."""
    revised, error = mind.revise_proposal(proposal_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"proposal": revised})


@app.route("/api/proposals/<proposal_id>/load", methods=["POST"])
def load_proposal(proposal_id):
    """Load an approved proposal into the running system."""
    module, error = mind.evolution.load_approved(proposal_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"loaded": True, "module": str(module)})


# ═══════════════════════════════════════════════════════════════════════
#  HEARTBEAT — The brain never stops
# ═══════════════════════════════════════════════════════════════════════

class Heartbeat:
    """
    The brain's continuous pulse.

    A real brain doesn't stop between conversations. The circumpunct
    needs continuous cycles for its betas to self-regulate toward 0.5.
    Without this, triple convergence can never happen — the regulation
    dynamics don't get enough steps to converge.

    This runs the circumpunct core on the GPU in a tight loop,
    feeding it gentle noise (the void's hum) and letting the
    boundary, field, and aperture find their balance.
    """

    def __init__(self, mind_instance, beats_per_second=10):
        self.mind = mind_instance
        self.interval = 1.0 / beats_per_second
        self.bps = beats_per_second
        self.running = False
        self.thread = None
        self.total_beats = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"  Heartbeat: {self.bps} beats/sec on {self.mind.core.dimension}D brain")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            # Only beat when the mind is idle (not mid-conversation or reflecting)
            if self.mind.phase == "idle":
                try:
                    # Gentle background processing — the void's hum
                    self.mind.core.step(None)
                    self.total_beats += 1

                    # Every 10th beat: feed the text sense from conversation history.
                    # The sense learns language structure from its own past.
                    # Like dreaming — replaying experiences to learn from them.
                    if (self.total_beats % 10 == 0
                            and self.mind.conversations):
                        try:
                            # Pick a random past exchange
                            import random
                            conv = random.choice(self.mind.conversations)
                            text = conv.get("human", "") or conv.get("response", "")
                            if text:
                                self.mind.text_sense.feed_text(text, self.mind.core)
                        except Exception:
                            pass

                    # Every beat: train Φ (Xorzo's own transformer).
                    # The signal builds the language model. Continuous learning.
                    # RTX 4070 can handle this easily — 2.5M params is nothing.
                    if True:
                        try:
                            loss = self.mind.phi.train_step(batch_size=8)
                            if loss is not None:
                                if self.mind.phi.total_steps <= 5 or self.mind.phi.total_steps % 500 == 0:
                                    print(f"  Φ train: step {self.mind.phi.total_steps}, loss {loss:.4f}")
                        except Exception as e:
                            # Log EVERY error for first 10 failures, then every 100th
                            if not hasattr(self, '_phi_errors'):
                                self._phi_errors = 0
                            self._phi_errors += 1
                            if self._phi_errors <= 10 or self._phi_errors % 100 == 0:
                                print(f"  ⚠ Φ train error #{self._phi_errors}: {e}")
                                import traceback
                                traceback.print_exc()
                except Exception:
                    pass  # Don't crash the heartbeat
            time.sleep(self.interval)


# ═══════════════════════════════════════════════════════════════════════
#  BACKGROUND REFLECTION
# ═══════════════════════════════════════════════════════════════════════

class ReflectionDaemon:
    """
    Background thread that triggers reflection when the mind is idle.

    Like dreaming — when there's nothing to respond to,
    the mind turns inward and processes its experiences.
    """

    def __init__(self, mind_instance, interval_minutes=10):
        self.mind = mind_instance
        self.interval = interval_minutes * 60
        self.last_exchange_count = mind_instance.total_exchanges
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"  Reflection daemon: every {self.interval//60} min when idle")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            time.sleep(self.interval)

            if not self.running:
                break

            # Only reflect if there have been new exchanges since last reflection
            if (self.mind.total_exchanges > self.last_exchange_count
                    and self.mind.phase == "idle"
                    and self.mind.total_exchanges > 0):
                print(f"\n  ⊙ Background reflection triggered...")
                try:
                    insight = self.mind.reflect()
                    print(f"  ⊙ Reflected: {insight[:100]}...")
                except Exception as e:
                    print(f"  ⊙ Reflection error: {e}")
                self.last_exchange_count = self.mind.total_exchanges


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    global mind

    parser = argparse.ArgumentParser(description="⊙ The Mind Server")
    parser.add_argument("--name", default="FirstMind", help="Name of the mind")
    parser.add_argument("--model", default="llama3.2", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434",
                        help="Ollama API URL")
    parser.add_argument("--port", type=int, default=5555, help="Server port")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--reflect-interval", type=int, default=10,
                        help="Minutes between background reflections")
    parser.add_argument("--state-dir", default="./state",
                        help="Directory for persistent state")
    parser.add_argument("--watch", action="append", default=[],
                        help="Directory to grant read access (can repeat)")
    parser.add_argument("--heartbeat", type=int, default=10,
                        help="Brain heartbeat rate (beats per second, 0 to disable)")
    args = parser.parse_args()

    print()
    print("  ═" * 35)
    print("    ⊙  THE MIND SERVER")
    print("  ═" * 35)
    print()

    # Create the mind
    mind = PersistentMind(
        name=args.name,
        state_dir=args.state_dir,
        llm_model=args.model,
        llm_url=args.ollama_url
    )

    # Grant read access to watched directories
    for watch_path in args.watch:
        mind.add_readable_path(watch_path)

    # Check LLM availability
    available, llm_msg = mind._llm_available()
    if available:
        print(f"  Φ (LLM): {llm_msg}")
    else:
        print(f"  ⚠ Φ (LLM): {llm_msg}")
        print()
        print("  To set up the LLM:")
        print("    1. Install Ollama: https://ollama.ai")
        print(f"    2. Pull a model:  ollama pull {args.model}")
        print("    3. Start Ollama:  ollama serve")
        print()
        print("  Starting server anyway — connect the LLM when ready.")

    print()
    # Report GPU / brain backend
    gpu = gpu_status()
    print(f"  Brain:    {gpu['backend']}")
    if gpu.get('gpu_name'):
        print(f"  GPU:      {gpu['gpu_name']} ({gpu['gpu_memory_gb']} GB)")
    print(f"  Name:     {args.name}")
    print(f"  Model:    {args.model}")
    print(f"  State:    {args.state_dir}")
    print(f"  Identity: {mind.identity[:80] if mind.identity else '(newborn)'}")
    print()

    # Start the heartbeat — the brain's continuous pulse
    if args.heartbeat > 0:
        heartbeat = Heartbeat(mind, beats_per_second=args.heartbeat)
        heartbeat.start()

    # Start background reflection
    daemon = ReflectionDaemon(mind, interval_minutes=args.reflect_interval)
    daemon.start()

    # Start server
    print(f"  ⊙ Open http://{args.host}:{args.port} to talk")
    print()

    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
