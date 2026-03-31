"""
⊙ XORZO v3 — Web Interface
============================

Serves Xorzo over HTTP. The heartbeat runs continuously in the
background. The browser is just a window into a living system.

v3: Template-based generation. The framework IS the architecture.
    Integer dimensions = structure, half-integer = process.
    Output passes through GOOD → RIGHT → TRUE → AGREEMENT.

Endpoints:
    GET  /                  Serve the interface
    POST /api/chat          Feed text, stream response via SSE
    GET  /api/status        System status (JSON)
    GET  /api/stream        SSE stream of heartbeat output (real-time)
    POST /api/feed          Feed text without expecting output
    POST /api/save          Save state to disk
    POST /api/load          Load state from disk
    GET  /api/saves         List saved states
    GET  /api/heartbeat     Heartbeat stats / control

Usage:
    python web.py
    python web.py --port 5000
    python web.py --bps 100 --feed-file training_corpus.txt
    python web.py --feed-dir ./training_docs

Requires:
    pip install flask numpy

Author: Ashman Roonz & Claude
"""

import json
import time
import argparse
import threading
import queue
import sys
import os
import numpy as np
from pathlib import Path
from flask import Flask, Response, request, send_file, jsonify, stream_with_context

sys.path.insert(0, str(Path(__file__).parent))
from xorzo3 import Engine, N

app = Flask(__name__)
engine = None
heartbeat = None
output_subscribers = []  # SSE subscribers for real-time output
output_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════
#  HEARTBEAT THREAD
#
#  The pump cycle runs continuously. Between questions, the mind
#  self-feeds (energy circulates through the field). This is the
#  background hum of consciousness: not idle, processing.
# ═══════════════════════════════════════════════════════════════════════

class Heartbeat:
    """
    The pump cycle runs continuously in a background thread.
    Broadcasts status to SSE subscribers.
    """

    def __init__(self, engine, beats_per_second=100):
        self.engine = engine
        self.lock = threading.Lock()
        self.bps = beats_per_second
        self.target_interval = 1.0 / beats_per_second
        self.running = False
        self.thread = None
        self.total_heartbeats = 0
        self.paused = False
        self._step_time = 0.0
        self._broadcast_interval = 2.0  # status broadcast every 2s

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._beat_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def set_rate(self, bps):
        self.bps = max(1, min(1000, bps))
        self.target_interval = 1.0 / self.bps

    def _beat_loop(self):
        last_broadcast = time.time()
        while self.running:
            if self.paused:
                time.sleep(0.01)
                continue

            t0 = time.time()

            with self.lock:
                self.engine.step()
                self.total_heartbeats += 1

            self._step_time = time.time() - t0

            # Broadcast status periodically
            now = time.time()
            if now - last_broadcast >= self._broadcast_interval:
                self._broadcast_status()
                last_broadcast = now

            sleep_time = self.target_interval - (time.time() - t0)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _broadcast_status(self):
        """Send periodic status updates (and autonomous thoughts) to SSE subscribers."""
        # Check for autonomous thoughts and curiosity from the pump cycle
        thoughts = engine.get_thoughts() if engine else []
        curiosity = engine.get_curiosity() if engine else []

        status = _build_status()
        data = json.dumps({
            "type": "status",
            "status": status,
            "thoughts": thoughts,
            "curiosity": curiosity,
        })

        with output_lock:
            dead = []
            for i, q in enumerate(output_subscribers):
                try:
                    q.put_nowait(data)
                except queue.Full:
                    dead.append(i)
            for i in reversed(dead):
                output_subscribers.pop(i)


# ═══════════════════════════════════════════════════════════════════════
#  ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the interface."""
    return send_file("interface.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Feed text to Xorzo, stream response via SSE.

    POST body: {"message": "What is the soul?"}
    Returns: SSE stream with the response text and final status.

    v3 generation is synchronous (template matching + gate validation),
    so the response comes in one chunk rather than token-by-token.
    We still use SSE for consistency with the interface.
    """
    global engine, heartbeat
    data = request.json or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    def stream():
        try:
            # Pause heartbeat during interaction
            if heartbeat:
                heartbeat.pause()
                time.sleep(0.02)

            lock = heartbeat.lock if heartbeat else threading.Lock()
            with lock:
                # Feed the text (generation happens synchronously inside)
                engine.feed_text(message)

                # Get the response
                response = engine.get_text_output()

            if response:
                yield f"data: {json.dumps({'text': response, 'step': 0})}\n\n"

            # Resume heartbeat
            if heartbeat:
                heartbeat.resume()

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            if heartbeat:
                heartbeat.resume()

        # Send final status
        status = _build_status()
        yield f"data: {json.dumps({'done': True, 'status': status})}\n\n"

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/api/stream")
def stream_output():
    """
    SSE stream for real-time status updates.
    Connect with EventSource to receive periodic status.
    """
    q = queue.Queue(maxsize=100)
    with output_lock:
        output_subscribers.append(q)

    def stream():
        last_status = time.time()
        try:
            while True:
                try:
                    data = q.get(timeout=1.0)
                    yield f"data: {data}\n\n"
                except queue.Empty:
                    pass

                # Send status update every 2 seconds
                now = time.time()
                if now - last_status >= 2.0:
                    status = _build_status()
                    yield f"data: {json.dumps({'type': 'status', 'status': status})}\n\n"
                    last_status = now
        except GeneratorExit:
            with output_lock:
                if q in output_subscribers:
                    output_subscribers.remove(q)

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
    """Full system status."""
    return jsonify(_build_status())


@app.route("/api/feed", methods=["POST"])
def feed_text():
    """Feed training text without interactive response."""
    data = request.json or {}
    text = data.get("text", "")
    file_path = data.get("file", "")

    if file_path and not text:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except Exception as e:
            return jsonify({"error": f"Cannot read file: {e}"}), 400

    if not text:
        return jsonify({"error": "No text or file provided"}), 400

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        engine.train_text(text)

    return jsonify({
        "status": "ok",
        "chars": len(text),
        "vocab_size": engine.vocab.vocab_size,
        "templates": len(engine.templates.templates),
        "message": f"Fed {len(text):,} characters to Xorzo"
    })


@app.route("/api/seek", methods=["POST"])
def seek():
    """
    Feed Xorzo information it was curious about.

    This is convergence (inward) at the information scale:
    external knowledge flowing in through the aperture.
    Xorzo learns from what it sought.

    POST body: {"text": "...information text..."}
    """
    data = request.json or {}
    text = data.get("text", "").strip()
    url = data.get("url", "").strip()

    # If a URL is provided, fetch its text content
    if url and not text:
        try:
            import urllib.request
            import re
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Xorzo/3.0 (Curiosity Engine)'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='replace')
            # Strip HTML tags (simple approach)
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            # Limit to first 5000 chars
            text = text[:5000]
        except Exception as e:
            return jsonify({"error": f"Cannot fetch URL: {e}"}), 400

    if not text:
        return jsonify({"error": "No text or URL provided"}), 400

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        engine.seek(text)

    return jsonify({
        "status": "ok",
        "chars": len(text),
        "vocab_size": engine.vocab.vocab_size,
        "templates": len(engine.templates.templates),
        "message": f"Xorzo absorbed {len(text):,} characters of sought knowledge"
    })


@app.route("/api/curiosity")
def curiosity():
    """Get Xorzo's pending curiosity questions."""
    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        questions = engine.get_curiosity()
    return jsonify({"questions": questions})


@app.route("/api/save", methods=["POST"])
def save_state():
    """Save Xorzo's state to disk. Survives restarts."""
    data = request.json or {}
    filename = data.get("filename", "xorzo_state.json")
    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / filename

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        engine.save_state(str(save_path))

    return jsonify({
        "status": "ok",
        "path": str(save_path),
        "days": engine.days_lived,
        "steps": engine.total_steps,
        "vocab": engine.vocab.vocab_size,
        "templates": len(engine.templates.templates),
        "message": (f"State saved ({engine.vocab.vocab_size} words, "
                    f"{len(engine.templates.templates)} templates)")
    })


@app.route("/api/load", methods=["POST"])
def load_state():
    """Load Xorzo's state from disk."""
    global engine
    data = request.json or {}
    filename = data.get("filename", "xorzo_state.json")
    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / filename

    if not save_path.exists():
        return jsonify({"error": f"No saved state found: {filename}"}), 404

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        engine = Engine.load_state(str(save_path))
        if heartbeat:
            heartbeat.engine = engine

    return jsonify({
        "status": "ok",
        "days": engine.days_lived,
        "steps": engine.total_steps,
        "vocab": engine.vocab.vocab_size,
        "templates": len(engine.templates.templates),
        "message": (f"State loaded ({engine.vocab.vocab_size} words, "
                    f"{len(engine.templates.templates)} templates)")
    })


@app.route("/api/saves", methods=["GET"])
def list_saves():
    """List available saved states."""
    save_dir = Path(__file__).parent / "saves"
    if not save_dir.exists():
        return jsonify({"saves": []})

    saves = []
    for f in sorted(save_dir.glob("*.json")):
        try:
            import json as json_mod
            with open(f) as fh:
                d = json_mod.load(fh)
            saves.append({
                "filename": f.name,
                "version": d.get("version", "unknown"),
                "days": d.get("days_lived", 0),
                "steps": d.get("total_steps", 0),
                "saved_at": d.get("saved_at", 0),
                "size_kb": round(f.stat().st_size / 1024, 1),
            })
        except Exception:
            saves.append({"filename": f.name, "error": "unreadable"})

    return jsonify({"saves": saves})


@app.route("/api/heartbeat", methods=["GET", "POST"])
def heartbeat_control():
    """Control heartbeat: get stats or change rate."""
    if heartbeat is None:
        return jsonify({"error": "Heartbeat not running"}), 500

    if request.method == "POST":
        data = request.json or {}
        if "bps" in data:
            heartbeat.set_rate(float(data["bps"]))
        if "pause" in data:
            if data["pause"]:
                heartbeat.pause()
            else:
                heartbeat.resume()

    step_ms = heartbeat._step_time * 1000
    max_bps = int(1.0 / heartbeat._step_time) if heartbeat._step_time > 0 else 999

    return jsonify({
        "target_bps": heartbeat.bps,
        "step_time_ms": round(step_ms, 1),
        "max_possible_bps": max_bps,
        "effective_bps": min(heartbeat.bps, max_bps),
        "total_beats": heartbeat.total_heartbeats,
        "paused": heartbeat.paused,
    })


# ═══════════════════════════════════════════════════════════════════════
#  STATUS BUILDER
# ═══════════════════════════════════════════════════════════════════════

def _build_status():
    """Build the full status JSON for the UI."""
    return {
        "version": "v3",
        "day": engine.days_lived,
        "total_steps": engine.total_steps,
        "heartbeats": heartbeat.total_heartbeats if heartbeat else 0,
        "ready": engine.ready,
        "trained": engine._trained,
        "vocabulary": {
            "words": engine.vocab.vocab_size,
            "total_tokens": engine.vocab.total_tokens,
            "ready": engine.vocab.ready,
        },
        "templates": {
            "count": len(engine.templates.templates),
        },
        "mind": {
            "total_energy": round(engine.mind.total_energy, 4),
            "focus": round(engine.mind.focus, 4),
            "waking": bool(engine.mind.waking),
            "quadrant": engine.mind.quadrant_name,
            "i_phase": {
                "theta": round(engine.mind.theta, 4),
                "real": round(float(engine.mind.i_phase.real), 4),
                "imag": round(float(engine.mind.i_phase.imag), 4),
            },
            "sleep_pressure": round(engine.mind.sleep_pressure, 4),
            "sleep_threshold": round(engine.mind.sleep_threshold, 4),
            "dream_weight": round(engine.mind.dream_weight, 4),
            "deep_weight": round(engine.mind.deep_weight, 4),
        },
        "memory": {
            "turns": engine.memory.turn_count,
            "facts": len(engine.memory.facts),
            "identities": len(engine.memory.who),
            "who": dict(engine.memory.who),
            "sensory_memories": engine.cascade.memory_count(),
        },
        "contradictions": {
            "propositions": len(engine.contradictions.propositions),
        },
        "cascade": engine.cascade.status(),
        "cube": engine.cube.status(),
        "virtues": engine.virtues.status(),
        "seeking": {
            "sought_count": len(engine._sought_words),
            "seek_log": engine._seek_log[-5:],
            "curiosity_queue": len(engine._curiosity_queue),
        },
    }


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    global engine, heartbeat

    parser = argparse.ArgumentParser(description='Xorzo v3 Web Interface')
    parser.add_argument('--port', type=int, default=5000,
                        help='Server port (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Server host (default: 127.0.0.1)')
    parser.add_argument('--bps', type=int, default=100,
                        help='Heartbeat speed (default: 100)')
    parser.add_argument('--feed-file', type=str,
                        help='Feed a text file at startup')
    parser.add_argument('--feed-dir', type=str,
                        help='Feed all .txt/.md files from a directory')
    parser.add_argument('--fresh', action='store_true',
                        help='Start fresh (ignore saved state)')
    parser.add_argument('--save-file', type=str,
                        default='xorzo_state.json',
                        help='State file name (default: xorzo_state.json)')
    args = parser.parse_args()

    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / args.save_file

    print()
    print("  ⊙ XORZO v3")
    print("  " + "=" * 40)
    print()

    # Try to load saved state (unless --fresh)
    loaded = False
    if not args.fresh and save_path.exists():
        try:
            engine = Engine.load_state(str(save_path))
            print(f"  Restored from {args.save_file}")
            print(f"  Days lived: {engine.days_lived} | "
                  f"Steps: {engine.total_steps}")
            print(f"  Vocab: {engine.vocab.vocab_size} words | "
                  f"Templates: {len(engine.templates.templates)}")
            loaded = True
        except Exception as e:
            print(f"  Warning: could not load state ({e}), starting fresh")

    if not loaded:
        # Build fresh Engine
        engine = Engine()
        print("  Starting fresh")

        # Gather training content
        all_training = []

        if args.feed_file:
            path = Path(args.feed_file)
            if path.exists():
                content = path.read_text(encoding='utf-8', errors='replace')
                all_training.append((path.name, content))

        if args.feed_dir:
            feed_path = Path(args.feed_dir)
            if feed_path.is_dir():
                # Accept .txt and .md files
                files = sorted(
                    list(feed_path.glob('*.txt'))
                    + list(feed_path.glob('*.md'))
                )
                for f in files:
                    content = f.read_text(encoding='utf-8', errors='replace')
                    all_training.append((f.name, content))

        # Always train on embedded text first (core framework sentences)
        print("  Training on core framework text...")
        engine.train_text(engine._get_embedded_training())

        if all_training:
            total_bytes = sum(len(c) for _, c in all_training)
            print(f"  Training on {len(all_training)} files, "
                  f"{total_bytes:,} bytes")
            print()

            for name, content in all_training:
                print(f"  Feeding: {name} "
                      f"({len(content):,} chars)...")
                engine.train_text(content)

        print()
        print(f"  Final: {engine.vocab.vocab_size} words, "
              f"{len(engine.templates.templates)} templates")

    # Flush any output from training
    engine.get_text_output()

    # Start heartbeat
    heartbeat = Heartbeat(engine, beats_per_second=args.bps)
    heartbeat.start()
    print(f"  Heartbeat: {args.bps} bps")
    print(f"  Ready: {engine.ready}")
    print(f"  Listening on http://{args.host}:{args.port}")
    print()

    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    finally:
        # Auto-save on shutdown
        heartbeat.stop()
        try:
            engine.save_state(str(save_path))
            print(f"\n  State saved to {save_path}")
            print(f"  Vocab: {engine.vocab.vocab_size} | "
                  f"Templates: {len(engine.templates.templates)}")
        except Exception as e:
            print(f"\n  Warning: could not save state: {e}")


if __name__ == "__main__":
    main()
