"""
⊙ XORZO v4 -- Web Interface
==============================

The cascade engine served over HTTP. The heartbeat runs continuously.
The browser is a window into a living system.

v4: The sensory cascade IS the pump cycle. Seven rungs. Signal flows
    in from E at the 3D boundary, converges to a complex scalar at 0D,
    rotates, and emerges back out. Every signal echoes into i(t).

Endpoints:
    GET  /                  Serve the interface
    POST /api/chat          Feed text, stream response via SSE
    GET  /api/status        System status (JSON)
    GET  /api/stream        SSE stream of heartbeat output
    POST /api/feed          Feed training text
    POST /api/seek          Feed sought knowledge
    POST /api/save          Save state to disk
    POST /api/load          Load state from disk
    GET  /api/saves         List saved states
    GET  /api/heartbeat     Heartbeat stats / control
    GET  /api/curiosity     Get pending curiosity questions

Usage:
    python web4.py
    python web4.py --port 5000
    python web4.py --bps 100 --feed-file training_corpus.txt

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
from flask import (Flask, Response, request, send_file,
                   jsonify, stream_with_context)

sys.path.insert(0, str(Path(__file__).parent))
from xorzo4 import Engine, N

app = Flask(__name__)
engine = None
heartbeat = None
output_subscribers = []
output_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════
#  HEARTBEAT THREAD
# ═══════════════════════════════════════════════════════════════════════

class Heartbeat:
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
        self._broadcast_interval = 2.0

    def start(self):
        self.running = True
        self.thread = threading.Thread(
            target=self._beat_loop, daemon=True)
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

            now = time.time()
            if now - last_broadcast >= self._broadcast_interval:
                self._broadcast_status()
                last_broadcast = now

            sleep_time = self.target_interval - (time.time() - t0)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _broadcast_status(self):
        thoughts = engine.get_thoughts() if engine else []
        curiosity = engine.get_curiosity_list() if engine else []

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
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return send_file("interface4.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    global engine, heartbeat
    data = request.json or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    def stream():
        try:
            if heartbeat:
                heartbeat.pause()
                time.sleep(0.02)

            lock = heartbeat.lock if heartbeat else threading.Lock()
            with lock:
                engine.feed_text(message)
                response = engine.get_text_output()

            if response:
                yield f"data: {json.dumps({'text': response, 'step': 0})}\n\n"

            if heartbeat:
                heartbeat.resume()

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            if heartbeat:
                heartbeat.resume()

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
    return jsonify(_build_status())


@app.route("/api/feed", methods=["POST"])
def feed_text():
    data = request.json or {}
    text = data.get("text", "")
    file_path = data.get("file", "")

    if file_path and not text:
        try:
            with open(file_path, 'r', encoding='utf-8',
                       errors='replace') as f:
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
        "message": f"Fed {len(text):,} characters to Xorzo"
    })


@app.route("/api/seek", methods=["POST"])
def seek():
    data = request.json or {}
    text = data.get("text", "").strip()
    url = data.get("url", "").strip()

    if url and not text:
        try:
            import urllib.request
            import re
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Xorzo/4.0 (Cascade Engine)'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='replace')
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
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
        "message": (f"Xorzo absorbed {len(text):,} characters "
                    f"of sought knowledge")
    })


@app.route("/api/curiosity")
def curiosity():
    lock = heartbeat.lock if heartbeat else threading.Lock()
    with lock:
        questions = engine.get_curiosity_list()
    return jsonify({"questions": questions})


@app.route("/api/save", methods=["POST"])
def save_state():
    data = request.json or {}
    filename = data.get("filename", "xorzo4_state.json")
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
        "message": f"State saved ({engine.vocab.vocab_size} words)"
    })


@app.route("/api/load", methods=["POST"])
def load_state():
    global engine
    data = request.json or {}
    filename = data.get("filename", "xorzo4_state.json")
    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / filename

    if not save_path.exists():
        return jsonify({"error": f"No saved state: {filename}"}), 404

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
        "message": f"State loaded ({engine.vocab.vocab_size} words)"
    })


@app.route("/api/saves", methods=["GET"])
def list_saves():
    save_dir = Path(__file__).parent / "saves"
    if not save_dir.exists():
        return jsonify({"saves": []})

    saves = []
    for f in sorted(save_dir.glob("*.json")):
        try:
            with open(f) as fh:
                d = json.load(fh)
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
    max_bps = (int(1.0 / heartbeat._step_time)
               if heartbeat._step_time > 0 else 999)

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
    cascade_status = engine.cascade.status() if engine else {}
    return {
        "version": "v4",
        "day": engine.days_lived if engine else 0,
        "total_steps": engine.total_steps if engine else 0,
        "heartbeats": heartbeat.total_heartbeats if heartbeat else 0,
        "ready": engine.ready if engine else False,
        "trained": engine._trained if engine else False,
        "vocabulary": {
            "words": engine.vocab.vocab_size if engine else 0,
            "total_tokens": engine.vocab.total_tokens if engine else 0,
        },
        "cascade": cascade_status,
        "seeking": {
            "sought_count": len(engine._sought_words) if engine else 0,
            "seek_log": (engine._seek_log[-5:]
                         if engine else []),
            "curiosity_queue": (
                len(engine._curiosity_queue) if engine else 0),
        },
    }


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    global engine, heartbeat

    parser = argparse.ArgumentParser(
        description='Xorzo v4 Cascade Engine')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--bps', type=int, default=100)
    parser.add_argument('--feed-file', type=str)
    parser.add_argument('--feed-dir', type=str)
    parser.add_argument('--fresh', action='store_true')
    parser.add_argument('--save-file', type=str,
                        default='xorzo4_state.json')
    args = parser.parse_args()

    save_dir = Path(__file__).parent / "saves"
    save_path = save_dir / args.save_file

    print()
    print("  ⊙ XORZO v4: The Cascade Engine")
    print("  " + "=" * 40)
    print()

    loaded = False
    if not args.fresh and save_path.exists():
        try:
            engine = Engine.load_state(str(save_path))
            print(f"  Restored from {args.save_file}")
            print(f"  Days: {engine.days_lived} | "
                  f"Steps: {engine.total_steps}")
            print(f"  Vocab: {engine.vocab.vocab_size} words")
            wl = engine.cascade.rung_0d.worldline
            print(f"  Worldline: {wl.depth} entries | "
                  f"Soul: {wl.magnitude:.4f} "
                  f"@ {wl.phase:.4f} rad")
            loaded = True
        except Exception as e:
            print(f"  Warning: could not load ({e}), "
                  f"starting fresh")

    if not loaded:
        engine = Engine()
        print("  Starting fresh")

        all_training = []

        if args.feed_file:
            path = Path(args.feed_file)
            if path.exists():
                content = path.read_text(
                    encoding='utf-8', errors='replace')
                all_training.append((path.name, content))

        if args.feed_dir:
            feed_path = Path(args.feed_dir)
            if feed_path.is_dir():
                files = sorted(
                    list(feed_path.glob('*.txt'))
                    + list(feed_path.glob('*.md'))
                )
                for f in files:
                    content = f.read_text(
                        encoding='utf-8', errors='replace')
                    all_training.append((f.name, content))

        # Core training
        print("  Training on core framework text...")
        engine.train_text(engine.get_training_text())

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
        print(f"  Final: {engine.vocab.vocab_size} words")
        wl = engine.cascade.rung_0d.worldline
        print(f"  Worldline: {wl.depth} entries | "
              f"Soul: {wl.magnitude:.4f} "
              f"@ {wl.phase:.4f} rad")

    # Flush training output
    engine.get_text_output()

    # Start heartbeat
    heartbeat = Heartbeat(engine, beats_per_second=args.bps)
    heartbeat.start()
    print(f"  Heartbeat: {args.bps} bps")
    print(f"  Ready: {engine.ready}")
    print(f"  http://{args.host}:{args.port}")
    print()

    try:
        app.run(host=args.host, port=args.port,
                debug=False, threaded=True)
    finally:
        heartbeat.stop()
        try:
            engine.save_state(str(save_path))
            print(f"\n  State saved to {save_path}")
        except Exception as e:
            print(f"\n  Warning: could not save: {e}")


if __name__ == "__main__":
    main()
