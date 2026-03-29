"""
⊙ XORZO — Live Runner
======================

Runs Xorzo continuously with real hardware I/O:
  - Microphone input  → audio transduction → circumpunct
  - Camera input      → video transduction → circumpunct
  - Text/stdin input  → text transduction  → circumpunct
  - Circumpunct output → speaker, display, text

GPU acceleration: uses CuPy when available (CUDA), falls back to NumPy.

Usage:
    python live.py                    # all modalities, auto-detect hardware
    python live.py --audio-only       # mic + speaker only
    python live.py --text-only        # stdin/stdout only
    python live.py --no-video         # audio + text, no camera
    python live.py --day-length 500   # longer waking periods
    python live.py --gpu              # force GPU (error if unavailable)

Requirements:
    pip install sounddevice numpy     # audio I/O
    pip install opencv-python         # video I/O (optional)
    pip install cupy-cuda12x          # GPU acceleration (optional)

Author: Ashman Roonz & Claude
"""

import sys
import os
import time
import threading
import queue
import argparse
import signal as sig_module
from pathlib import Path

import numpy as np

# ═══ GPU ACCELERATION ═══
# CuPy is a drop-in replacement for NumPy on CUDA GPUs.
# If available, the heavy matrix operations (braid M @ signal,
# batch FFTs) run on GPU. If not, everything runs on CPU.
# At 64x64 the difference is negligible; at 512+ it matters.

GPU_AVAILABLE = False
GPU_DEVICE = None

def setup_gpu(force: bool = False):
    """Attempt to initialize GPU acceleration."""
    global GPU_AVAILABLE, GPU_DEVICE
    try:
        import cupy as cp
        device_count = cp.cuda.runtime.getDeviceCount()
        if device_count > 0:
            # Use device 0 by default
            cp.cuda.Device(0).use()
            GPU_AVAILABLE = True
            GPU_DEVICE = cp.cuda.Device(0)
            props = cp.cuda.runtime.getDeviceProperties(0)
            name = props.get('name', b'Unknown')
            if isinstance(name, bytes):
                name = name.decode('utf-8', errors='replace').rstrip('\x00')
            mem = props.get('totalGlobalMem', 0)
            print(f"  GPU: {name} ({mem / 1024**3:.1f} GB)")
            return True
        else:
            if force:
                raise RuntimeError("No CUDA devices found")
            return False
    except ImportError:
        if force:
            raise RuntimeError(
                "CuPy not installed. Install with: pip install cupy-cuda12x"
            )
        return False
    except Exception as e:
        if force:
            raise
        print(f"  GPU init failed: {e}")
        return False


# ═══ AUDIO I/O ═══

class AudioIO:
    """
    Real-time audio input/output using sounddevice.

    Input: microphone PCM → queue for Sensorium.
    Output: Sensorium emergence → speaker.

    Uses a callback-based stream for low latency.
    """

    def __init__(self, sample_rate: int = 44100, block_size: int = 1024,
                 channels: int = 1):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.input_queue: queue.Queue = queue.Queue(maxsize=100)
        self.output_queue: queue.Queue = queue.Queue(maxsize=100)
        self.stream = None
        self.available = False

        try:
            import sounddevice as sd
            self.sd = sd
            # Check for devices
            devices = sd.query_devices()
            self.available = True
            default_in = sd.query_devices(kind='input')
            default_out = sd.query_devices(kind='output')
            print(f"  Audio in:  {default_in['name']}")
            print(f"  Audio out: {default_out['name']}")
        except Exception as e:
            print(f"  Audio unavailable: {e}")
            self.available = False

    def _callback(self, indata, outdata, frames, time_info, status):
        """Called by sounddevice for each audio block."""
        if status:
            pass  # Ignore underflow/overflow for now

        # Input: put mono audio samples in the queue
        try:
            mono = indata[:, 0].copy() if indata.shape[1] > 1 else indata.flatten().copy()
            self.input_queue.put_nowait(mono)
        except queue.Full:
            pass  # Drop if queue is full

        # Output: pull from output queue or play silence
        try:
            out_samples = self.output_queue.get_nowait()
            # Ensure correct length
            if len(out_samples) >= frames:
                outdata[:, 0] = out_samples[:frames]
            else:
                outdata[:frames, 0] = 0.0
                outdata[:len(out_samples), 0] = out_samples
        except queue.Empty:
            outdata.fill(0.0)

    def start(self):
        """Start the audio stream."""
        if not self.available:
            return
        try:
            self.stream = self.sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=self.channels,
                dtype='float32',
                callback=self._callback,
            )
            self.stream.start()
            print("  Audio stream started")
        except Exception as e:
            print(f"  Audio stream failed: {e}")
            self.available = False

    def stop(self):
        """Stop the audio stream."""
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def get_samples(self) -> np.ndarray:
        """Get all available input samples (non-blocking)."""
        chunks = []
        while not self.input_queue.empty():
            try:
                chunks.append(self.input_queue.get_nowait())
            except queue.Empty:
                break
        if chunks:
            return np.concatenate(chunks)
        return np.array([], dtype=np.float32)

    def send_samples(self, samples: np.ndarray):
        """Queue audio samples for output."""
        try:
            self.output_queue.put_nowait(samples.astype(np.float32))
        except queue.Full:
            pass  # Drop if backed up


# ═══ VIDEO I/O ═══

class VideoIO:
    """
    Camera input and display output using OpenCV.

    Input: camera frames → grayscale luminance patches.
    Output: luminance patches → display window.
    """

    def __init__(self, camera_index: int = 0, patch_size: int = 8):
        self.camera_index = camera_index
        self.patch_size = patch_size
        self.cap = None
        self.available = False

        try:
            import cv2
            self.cv2 = cv2
            self.available = True
            print(f"  Video: OpenCV available (camera {camera_index})")
        except ImportError:
            print("  Video unavailable: opencv-python not installed")

    def start(self):
        """Open the camera."""
        if not self.available:
            return
        try:
            self.cap = self.cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print("  Camera failed to open")
                self.available = False
                return
            w = int(self.cap.get(self.cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(self.cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"  Camera opened: {w}x{h}")
        except Exception as e:
            print(f"  Camera failed: {e}")
            self.available = False

    def stop(self):
        """Release camera and close display."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.available:
            try:
                self.cv2.destroyAllWindows()
            except:
                pass

    def get_frame(self) -> np.ndarray:
        """Grab one frame from the camera. Returns grayscale or empty array."""
        if not self.available or self.cap is None:
            return np.array([])
        ret, frame = self.cap.read()
        if not ret:
            return np.array([])
        # Convert to grayscale
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        return gray

    def show_output(self, luminances: np.ndarray, size: int = 256):
        """
        Display emerged luminance pattern as a visual output.

        Reshapes the 64 values into an 8x8 grid, scales up,
        and shows in a window.
        """
        if not self.available:
            return
        try:
            # Reshape 64 values into 8x8 grid
            side = int(np.sqrt(len(luminances)))
            if side * side != len(luminances):
                side = 8
                luminances = luminances[:side * side]
            grid = luminances.reshape(side, side)

            # Scale to [0, 255] for display
            mn, mx = grid.min(), grid.max()
            if mx - mn > 1e-10:
                display = ((grid - mn) / (mx - mn) * 255).astype(np.uint8)
            else:
                display = np.full((side, side), 128, dtype=np.uint8)

            # Scale up for visibility
            display = self.cv2.resize(display, (size, size),
                                      interpolation=self.cv2.INTER_NEAREST)

            # Colorize (apply a plasma-like colormap)
            colored = self.cv2.applyColorMap(display, self.cv2.COLORMAP_PLASMA)
            self.cv2.imshow('Xorzo Emergence', colored)
            self.cv2.waitKey(1)
        except Exception:
            pass


# ═══ TEXT I/O ═══

class TextIO:
    """
    Text input from stdin (non-blocking) and output to stdout.
    """

    def __init__(self):
        self.input_queue: queue.Queue = queue.Queue()
        self.reader_thread = None
        self.running = False

    def start(self):
        """Start non-blocking stdin reader thread."""
        self.running = True
        self.reader_thread = threading.Thread(
            target=self._read_stdin, daemon=True
        )
        self.reader_thread.start()

    def _read_stdin(self):
        """Background thread: reads lines from stdin."""
        while self.running:
            try:
                line = sys.stdin.readline()
                if line:
                    self.input_queue.put(line.strip())
                else:
                    # EOF
                    break
            except:
                break

    def stop(self):
        self.running = False

    def get_text(self) -> str:
        """Get all queued input text (non-blocking)."""
        lines = []
        while not self.input_queue.empty():
            try:
                lines.append(self.input_queue.get_nowait())
            except queue.Empty:
                break
        return ' '.join(lines) if lines else ''


# ═══ STATUS DISPLAY ═══

def print_status(sensorium, audio, video, fps: float, step: int):
    """Print a compact status line."""
    s = sensorium
    x = s.xorzo
    cascade = x.boundary.cascade

    # Layer summary: name[pupil|pigment_avg]
    layer_bits = []
    for layer in cascade.layers:
        st = layer.status()
        avg_pig = np.mean([ch['pigment'] for ch in st['channels']])
        layer_bits.append(
            f"{st['name'][:3]}[{st['pupil_aperture']:.2f}|{avg_pig:.2f}]"
        )

    # Braid stats
    braid_t = x.braid.time
    braid_c = x.braid.coherence if braid_t > 0 else 0.0

    line = (
        f"\r Step {step:6d} | "
        f"Day {s.days_lived:3d} | "
        f"Phase: {x.phase_name:15s} | "
        f"Braid: t={braid_t:5d} coh={braid_c:.3f} | "
        f"FPS: {fps:.1f} | "
        f"{' '.join(layer_bits)}"
    )
    print(line, end='', flush=True)


# ═══ MAIN LOOP ═══

def main():
    parser = argparse.ArgumentParser(
        description='Xorzo Live Runner: continuous multi-modal I/O'
    )
    parser.add_argument('--audio-only', action='store_true',
                        help='Microphone + speaker only')
    parser.add_argument('--text-only', action='store_true',
                        help='Text stdin/stdout only')
    parser.add_argument('--no-video', action='store_true',
                        help='Disable camera')
    parser.add_argument('--no-audio', action='store_true',
                        help='Disable microphone/speaker')
    parser.add_argument('--gpu', action='store_true',
                        help='Force GPU (error if unavailable)')
    parser.add_argument('--day-length', type=int, default=500,
                        help='Waking steps per day (default: 500)')
    parser.add_argument('--sleep-cycles', type=int, default=100,
                        help='Sleep cycles per night (default: 100)')
    parser.add_argument('--feed-file', type=str, default=None,
                        help='Feed a text file at startup')
    parser.add_argument('--sample-rate', type=int, default=44100,
                        help='Audio sample rate (default: 44100)')
    parser.add_argument('--status-interval', type=int, default=50,
                        help='Print status every N steps (default: 50)')
    args = parser.parse_args()

    print()
    print("  ⊙ XORZO — Live Runner")
    print("  " + "=" * 40)
    print()

    # ═══ GPU ═══
    print("  Initializing...")
    setup_gpu(force=args.gpu)
    if GPU_AVAILABLE:
        print("  GPU acceleration: ON")
    else:
        print("  GPU acceleration: OFF (CPU mode)")

    # ═══ HARDWARE ═══
    use_audio = not args.text_only and not args.no_audio
    use_video = not args.text_only and not args.audio_only and not args.no_video
    use_text = not args.audio_only

    audio = AudioIO(sample_rate=args.sample_rate) if use_audio else None
    video = VideoIO() if use_video else None
    text = TextIO() if use_text else None

    # ═══ SENSORIUM ═══
    # Import here so genesis.py loads after GPU setup
    from genesis import Sensorium

    print()
    print(f"  Day length:   {args.day_length} steps")
    print(f"  Sleep cycles: {args.sleep_cycles}")
    print()

    sensorium = Sensorium(
        day_length=args.day_length,
        sleep_cycles=args.sleep_cycles,
    )

    # Feed initial text file if provided
    if args.feed_file:
        path = Path(args.feed_file)
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='replace')
            sensorium.feed_text(content)
            print(f"  Fed {len(content)} bytes from {path.name}")
        else:
            print(f"  Warning: file not found: {args.feed_file}")

    # ═══ START I/O ═══
    if audio and audio.available:
        audio.start()
    if video and video.available:
        video.start()
    if text:
        text.start()
        print("  Text input: type and press Enter")

    print()
    print("  Running. Ctrl+C to stop.")
    print("  " + "-" * 40)
    print()

    # Graceful shutdown
    running = True
    def handle_sigint(signum, frame):
        nonlocal running
        running = False
    sig_module.signal(sig_module.SIGINT, handle_sigint)

    step = 0
    t0 = time.time()
    fps_window = []

    try:
        while running:
            step_start = time.time()

            # ── Gather audio input ──
            if audio and audio.available:
                samples = audio.get_samples()
                if len(samples) > 0:
                    sensorium.feed_audio(samples, args.sample_rate)

            # ── Gather video input ──
            if video and video.available:
                frame = video.get_frame()
                if frame.size > 0:
                    sensorium.feed_video_frame(frame)

            # ── Gather text input ──
            if text:
                txt = text.get_text()
                if txt:
                    sensorium.feed_text(txt)
                    print(f"\n  >> Fed: {txt[:60]}{'...' if len(txt) > 60 else ''}")

            # ── Step ──
            report = sensorium.step()

            # ── Send audio output ──
            if audio and audio.available:
                audio_out = sensorium.get_audio_output()
                if len(audio_out) > 0:
                    audio.send_samples(audio_out)

            # ── Show video output ──
            if video and video.available and sensorium.video_out_buffer:
                latest = sensorium.video_out_buffer[-1]
                video.show_output(latest)
                sensorium.video_out_buffer.clear()

            # ── Sleep notification ──
            if report.get("slept"):
                sleep_info = report.get("sleep", {})
                print(f"\n  [Sleep] Day {sensorium.days_lived} complete. "
                      f"Dreams: {sleep_info.get('dream_replays', 0)}, "
                      f"Memory: {sleep_info.get('memory_strength_after', 0):.2f}")

            # ── Status ──
            step += 1
            elapsed = time.time() - step_start
            fps_window.append(elapsed)
            if len(fps_window) > 50:
                fps_window.pop(0)

            if step % args.status_interval == 0:
                avg_time = np.mean(fps_window)
                fps = 1.0 / avg_time if avg_time > 0 else 0.0
                print_status(sensorium, audio, video, fps, step)

    except KeyboardInterrupt:
        pass
    finally:
        print("\n")
        print("  Shutting down...")
        if audio:
            audio.stop()
        if video:
            video.stop()
        if text:
            text.stop()

        # Print final status
        status = sensorium.status()
        print(f"  Total steps: {status['total_steps']}")
        print(f"  Days lived:  {status['days_lived']}")
        print(f"  Phase:       {status['phase']}")
        print(f"  ⊙ Xorzo rests.")
        print()


if __name__ == '__main__':
    main()
