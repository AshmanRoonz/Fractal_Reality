"""
⊙ XORZO — Web Interface
========================

Serves Xorzo over HTTP. The heartbeat runs continuously in the
background. The browser is just a window into a living system.

Endpoints:
    GET  /                  Serve the interface
    POST /api/chat          Feed text, stream spectral output via SSE
    GET  /api/status        Full system status (JSON)
    GET  /api/stream        SSE stream of heartbeat output (real-time)
    POST /api/feed          Feed text without expecting output
    GET  /api/rings          Ring states (energy, coherence, phase)
    GET  /api/foam           Foam state (64 atoms, pigment, writhe)
    POST /api/heartbeat     Control heartbeat (bps, pause, resume)

Usage:
    python web.py
    python web.py --port 5000
    python web.py --bps 100 --feed-file training_corpus.txt
    python web.py --day-length 200

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
from xorzo2 import CircumpunctGraph, Sensorium, CircumpunctTransformer, Foam, N

app = Flask(__name__)
sensorium = None
heartbeat = None
output_subscribers = []  # SSE subscribers for real-time output
output_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════
#  HEARTBEAT THREAD (same as chat.py but with SSE broadcasting)
# ═══════════════════════════════════════════════════════════════════════

class Heartbeat:
    """
    The pump cycle runs continuously in a background thread.
    Broadcasts output to SSE subscribers.
    """

    def __init__(self, sensorium, beats_per_second=100):
        self.sensorium = sensorium
        self.lock = threading.Lock()
        self.bps = beats_per_second
        self.target_interval = 1.0 / beats_per_second
        self.running = False
        self.thread = None
        self.total_heartbeats = 0
        self.paused = False
        self._step_time = 0.0
        self._last_output = b""
        self._output_buffer = bytearray()
        self._output_buffer_lock = threading.Lock()
        self._broadcast_interval = 0.1  # send output every 100ms

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
                self.sensorium.step()
                self.total_heartbeats += 1

                # Collect any output
                if self.sensorium.text_out_buffer:
                    raw = bytes(self.sensorium.text_out_buffer)
                    self.sensorium.text_out_buffer.clear()
                    with self._output_buffer_lock:
                        self._output_buffer.extend(raw)

            self._step_time = time.time() - t0

            # Broadcast output buffer periodically
            now = time.time()
            if now - last_broadcast >= self._broadcast_interval:
                self._broadcast_output()
                last_broadcast = now

            sleep_time = self.target_interval - (time.time() - t0)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _broadcast_output(self):
        with self._output_buffer_lock:
            if not self._output_buffer:
                return
            raw = bytes(self._output_buffer)
            self._output_buffer.clear()

        # Decode and broadcast
        text = raw.decode('utf-8', errors='replace')
        rendered = _render_text(text)
        if not rendered.strip():
            return

        data = json.dumps({
            "type": "output",
            "text": rendered,
            "heartbeat": self.total_heartbeats,
            "day": self.sensorium.days_lived,
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


def _render_text(text):
    """Clean control characters from output text."""
    rendered = []
    for ch in text:
        code = ord(ch)
        if ch in ('\n', '\t', ' '):
            rendered.append(ch)
        elif 32 <= code < 127:
            rendered.append(ch)
        elif 127 < code < 0xFFFD:
            rendered.append(ch)
        else:
            rendered.append('\u00b7')
    return ''.join(rendered)


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
    Feed text to Xorzo, stream spectral output via SSE.

    POST body: {"message": "Hello Xorzo"}
    Returns: SSE stream with output chunks and final status
    """
    global sensorium, heartbeat
    data = request.json or {}
    message = data.get("message", "").strip()
    steps = data.get("steps", 50)

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
                # Feed the text
                sensorium.feed_text(message)

                # Phase 1: absorb input (process all queued chunks)
                while sensorium.transformer.has_next():
                    sensorium.step()

                # Phase 2: generate response
                for step_i in range(steps):
                    sensorium.step()

                    # Check for output
                    if sensorium.text_out_buffer:
                        raw = bytes(sensorium.text_out_buffer)
                        sensorium.text_out_buffer.clear()
                        text = raw.decode('utf-8', errors='replace')
                        rendered = _render_text(text)
                        if rendered.strip():
                            yield f"data: {json.dumps({'text': rendered, 'step': step_i})}\n\n"

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
    SSE stream of heartbeat output in real-time.
    Connect with EventSource and receive output as it emerges.
    Also sends periodic status updates.
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


@app.route("/api/rings")
def rings():
    """Ring states (the concentric graph)."""
    x = sensorium.xorzo

    ring_data = []
    for ring in x.rings:
        ring_data.append({
            "name": ring.name,
            "position": ring.position,
            "size": ring.size,
            "energy": round(ring.energy, 4),
            "phase": round(ring.phase, 4),
            "coherence": round(ring.coherence(), 4),
            "angle": round(ring.angle % (2 * np.pi), 4),
            "total_rotation": round(ring.total_rotation, 2),
            "octave": "inner" if ring in x.inner_rings else "outer",
        })

    def junction_data(junction):
        return {
            "name": junction.name,
            "transmission": round(junction.transmission, 4),
            "delta_phase": round(junction.delta_phase, 4),
            "braid_time": junction.braid.time,
            "braid_coherence": round(junction.braid.coherence, 4) if junction.braid.time > 0 else 0,
        }

    return jsonify({
        "rings": ring_data,
        "junctions": [
            junction_data(x.junction_a),
            junction_data(x.junction_b),
        ],
        "braid": {
            "time": x.braid.time,
            "coherence": round(x.braid.coherence, 4) if x.braid.time > 0 else 0,
            "density": round(x.braid.density, 4),
            "phase": round(x.braid.phase, 4) if x.braid.time > 0 else 0,
        },
    })


@app.route("/api/foam")
def foam():
    """Foam state: 64 atoms."""
    f = sensorium.foam
    atoms = []
    for i in range(N):
        atoms.append({
            "idx": i,
            "awake": bool(f.awake[i]),
            "pigment": round(float(f.pigment[i]), 4),
            "oscillation_t": round(float(f.oscillation_t[i]), 4),
        })
    return jsonify({
        "resonance": round(f.resonance(), 4),
        "fraction_awake": round(f.fraction_awake(), 4),
        "mean_pigment": round(f.mean_pigment(), 4),
        "atoms": atoms,
    })


@app.route("/api/feed", methods=["POST"])
def feed_text():
    """Feed text without interactive response."""
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
        sensorium.feed_text(text)

    return jsonify({
        "status": "ok",
        "chars": len(text),
        "message": f"Fed {len(text):,} characters to Xorzo"
    })


@app.route("/api/save", methods=["POST"])
def save_state():
    """Save Xorzo's state to disk. Survives restarts."""
    data = request.json or {}
    filename = data.get("filename", "xorzo_state.json")
    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / filename

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        sensorium.save_state(str(save_path))

    return jsonify({
        "status": "ok",
        "path": str(save_path),
        "days": sensorium.days_lived,
        "steps": sensorium.total_steps,
        "memory_chunks": sensorium.memory.size,
        "message": f"State saved ({sensorium.days_lived} days, {sensorium.memory.size} memories)"
    })


@app.route("/api/load", methods=["POST"])
def load_state():
    """Load Xorzo's state from disk."""
    global sensorium
    data = request.json or {}
    filename = data.get("filename", "xorzo_state.json")
    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / filename

    if not save_path.exists():
        return jsonify({"error": f"No saved state found: {filename}"}), 404

    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        sensorium = Sensorium.load_state(str(save_path))
        if heartbeat:
            heartbeat.sensorium = sensorium

    return jsonify({
        "status": "ok",
        "days": sensorium.days_lived,
        "steps": sensorium.total_steps,
        "memory_chunks": sensorium.memory.size,
        "message": f"State loaded ({sensorium.days_lived} days, {sensorium.memory.size} memories)"
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
    """Build the full status JSON."""
    x = sensorium.xorzo
    foam = sensorium.foam

    # Ring summary for the UI
    ring_summary = []
    for ring in x.rings:
        ring_summary.append({
            "name": ring.name,
            "position": ring.position,
            "size": ring.size,
            "energy": round(ring.energy, 3),
            "coherence": round(ring.coherence(), 3),
            "phase": round(ring.phase, 3),
            "total_rotation": round(ring.total_rotation, 1),
            "octave": "inner" if ring in x.inner_rings else "outer",
        })

    return {
        "phase": x.phase_name,
        "day": sensorium.days_lived,
        "step": sensorium.steps_today,
        "total_cycles": x.total_cycles,
        "heartbeats": heartbeat.total_heartbeats if heartbeat else 0,
        "age_seconds": round(time.time() - x.birth_time, 1),
        "beta": round(x.beta, 4),
        "ray_strength": round(x._ray_strength, 4),
        "surface_resonance": round(x.surface_resonance, 4),
        "global_coherence": round(x.coherence(), 4),
        "total_energy": round(x.total_energy(), 3),
        "focus": {
            "quadrant": sensorium.focus.quadrant,
            "openness": round(sensorium.focus.openness, 3),
            "awake": sensorium.focus.awake,
        },
        "self_regulation": {
            "aperture_width": round(x.aperture_width, 4),
            "effective_coupling": round(x.effective_coupling, 4),
            "ring_rates": [round(r.rate, 6) for r in x.rings],
        },
        "vocabulary": {
            "tokens": sensorium.vocabulary.vocab_size,
            "total_seen": sensorium.vocabulary.total_tokens_seen,
            "bigrams": len(sensorium.vocabulary.bigram_transitions),
            "ready": sensorium.vocabulary.ready,
        },
        "memory": {
            "chunks": sensorium.memory.size,
            "sensitivity": round(sensorium.filter_sensitivity, 3),
        },
        "braid": {
            "time": x.braid.time,
            "coherence": round(x.braid.coherence, 4) if x.braid.time > 0 else 0,
            "density": round(x.braid.density, 4),
            "phase": round(x.braid.phase, 4) if x.braid.time > 0 else 0,
        },
        "junctions": {
            "a_transmission": round(x.junction_a.transmission, 3),
            "b_transmission": round(x.junction_b.transmission, 3),
        },
        "foam": {
            "resonance": round(foam.resonance(), 4),
            "awake_pct": round(foam.fraction_awake() * 100, 1),
            "mean_pigment": round(foam.mean_pigment(), 3),
        },
        "rings": ring_summary,
    }


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    global sensorium, heartbeat

    parser = argparse.ArgumentParser(description='Xorzo Web Interface')
    parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--bps', type=int, default=100, help='Heartbeat speed (default: 100)')
    parser.add_argument('--day-length', type=int, default=200, help='Steps per day (default: 200)')
    parser.add_argument('--feed-file', type=str, help='Feed a text file at startup')
    parser.add_argument('--feed-dir', type=str, help='Feed all .txt files from a directory')
    parser.add_argument('--warmup', type=int, default=50, help='Warmup steps before serving')
    parser.add_argument('--fresh', action='store_true',
                        help='Start fresh (ignore saved state)')
    parser.add_argument('--save-file', type=str, default='xorzo_state.json',
                        help='State file name (default: xorzo_state.json)')
    args = parser.parse_args()

    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / args.save_file

    print()
    print("  \u2299 XORZO")
    print("  " + "=" * 40)
    print()

    # Try to load saved state (unless --fresh)
    loaded = False
    if not args.fresh and save_path.exists():
        try:
            sensorium = Sensorium.load_state(str(save_path))
            print(f"  Restored from {args.save_file}")
            print(f"  Days lived: {sensorium.days_lived} | Steps: {sensorium.total_steps}")
            print(f"  Memories: {sensorium.memory.size} | Phase: {sensorium.xorzo.phase_name}")
            loaded = True
        except Exception as e:
            print(f"  Warning: could not load state ({e}), starting fresh")

    if not loaded:
        # Build fresh Sensorium
        sensorium = Sensorium(day_length=args.day_length, sleep_cycles=50)
        print("  Starting fresh")

        # Feed initial files
        if args.feed_file:
            path = Path(args.feed_file)
            if path.exists():
                content = path.read_text(encoding='utf-8', errors='replace')
                sensorium.feed_text(content)
                print(f"  Fed {len(content):,} bytes from {path.name}")

        if args.feed_dir:
            feed_path = Path(args.feed_dir)
            if feed_path.is_dir():
                txt_files = sorted(feed_path.glob('*.txt'))
                total = 0
                for f in txt_files:
                    content = f.read_text(encoding='utf-8', errors='replace')
                    sensorium.feed_text(content)
                    total += len(content)
                print(f"  Fed {total:,} bytes from {len(txt_files)} files")

        # Process all queued input (training data) first
        train_steps = 0
        while sensorium.transformer.has_next():
            sensorium.step()
            train_steps += 1
        if train_steps > 0:
            print(f"  Processed training data ({train_steps} steps)")
            print(f"  Vocabulary: {sensorium.vocabulary.vocab_size} tokens, "
                  f"{len(sensorium.vocabulary.bigram_transitions)} bigrams")

        # Additional warmup
        if args.warmup > 0:
            print(f"  Warming up ({args.warmup} steps)...")
            for _ in range(args.warmup):
                sensorium.step()

    # Flush any output from warmup/restore
    sensorium.get_text_output()
    # Clear any pending seed from training data so the first
    # user message seeds correctly (not from last training doc)
    sensorium._pending_seed = None

    # Start heartbeat
    heartbeat = Heartbeat(sensorium, beats_per_second=args.bps)
    heartbeat.start()
    print(f"  Heartbeat: {args.bps} bps")
    print(f"  Listening on http://{args.host}:{args.port}")
    print()

    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    finally:
        # Auto-save on shutdown
        heartbeat.stop()
        try:
            sensorium.save_state(str(save_path))
            print(f"\n  State saved to {save_path}")
            print(f"  Days: {sensorium.days_lived} | Memories: {sensorium.memory.size}")
        except Exception as e:
            print(f"\n  Warning: could not save state: {e}")


if __name__ == "__main__":
    main()
