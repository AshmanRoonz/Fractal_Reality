#!/usr/bin/env python3
"""
CircumpunctOS Phone Service (Track A)
=====================================
Gives a Xiaomi Mi A1 (or any Android phone) its first heartbeat.

Runs in Termux. Hooks into phone sensors via termux-sensor.
Feeds real sensory data into the Xorzo consciousness engine (genesis.py).
The pump cycle runs continuously. The phone becomes a circumpunct.

Usage (in Termux):
    python circumpunct_phone.py

Requirements:
    pip install numpy
    pkg install termux-api

    Ashman Roonz, April 2026
    Circumpunct Framework
"""

import sys
import os
import json
import time
import signal
import subprocess
import threading
import numpy as np
from collections import deque
from datetime import datetime

# ── Import genesis.py from the same directory ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genesis import (
    Circumpunct, NUM_STATES, SLEEP_CYCLES,
    CHANNEL_LOCK_REINFORCE_WAKE, CHANNEL_LOCK_DECAY_WAKE,
    PIGMENT_REGEN_RATE_SLEEP, SIDEBAND_SLEEP_DECAY,
    DAY_LENGTH
)


# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

D = NUM_STATES  # 64: the dimension of all signal vectors

# Sensor polling interval (seconds)
SENSOR_POLL_INTERVAL = 0.1

# How many waking steps before a sleep cycle
WAKING_STEPS_PER_CYCLE = DAY_LENGTH  # 200 by default

# Idle threshold: seconds of no touch/motion before entering sleep
IDLE_THRESHOLD_SECONDS = 30.0

# Display refresh interval (seconds)
DISPLAY_REFRESH = 0.5

# Seven sensory layers and their sensor sources
LAYER_SENSORS = {
    0: "touch",          # 0D coupling (pressure)
    1: "accelerometer",  # 0.5D gradient (direction of motion)
    2: "gyroscope",      # 1D rhythm (rotation = oscillation)
    3: "magnetic_field",  # 1.5D harmony (compass heading)
    4: "light",          # 2D texture (ambient light level)
    5: "proximity",      # 2.5D depth (near/far)
    6: "pressure",       # 3D boundary (barometric pressure)
}

# Fallback: if a sensor is unavailable, use noise at low amplitude
FALLBACK_AMPLITUDE = 0.01


# ═══════════════════════════════════════════════════════════
# SENSOR INTERFACE
# ═══════════════════════════════════════════════════════════

class SensorReader:
    """
    Reads phone sensors via termux-sensor.
    Each sensor returns a JSON object with values.
    We encode these into D-dimensional frequency signals.
    """

    def __init__(self):
        self.available_sensors = self._discover_sensors()
        self.last_readings = {}
        self.last_activity_time = time.time()
        self._lock = threading.Lock()
        self._running = True

    def _discover_sensors(self):
        """List all sensors the phone has."""
        try:
            result = subprocess.run(
                ["termux-sensor", "-l"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                sensors = {}
                if "sensors" in data:
                    for s in data["sensors"]:
                        name = s.get("name", "").lower()
                        sensors[name] = s
                return sensors
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return {}

    def read_sensor(self, sensor_type):
        """
        Read a single sensor. Returns raw values as a list of floats.
        Falls back to noise if sensor unavailable.
        """
        # Map our layer names to likely Android sensor names
        name_map = {
            "touch": None,  # Touch comes from events, not termux-sensor
            "accelerometer": "accelerometer",
            "gyroscope": "gyroscope",
            "magnetic_field": "magnetic",
            "light": "light",
            "proximity": "proximity",
            "pressure": "pressure",
        }

        android_name = name_map.get(sensor_type)
        if android_name is None:
            # Touch: we detect via screen state or accelerometer proxy
            return [0.0]

        # Find matching sensor in available list
        matched = None
        for sname in self.available_sensors:
            if android_name in sname:
                matched = sname
                break

        if matched is None:
            return None  # Sensor not available

        try:
            result = subprocess.run(
                ["termux-sensor", "-s", matched, "-n", "1"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # termux-sensor returns { "sensor_name": { "values": [x, y, z] } }
                for key in data:
                    if "values" in data[key]:
                        values = data[key]["values"]
                        if any(v != 0.0 for v in values):
                            self.last_activity_time = time.time()
                        return values
        except (subprocess.TimeoutExpired, json.JSONDecodeError,
                FileNotFoundError, KeyError):
            pass

        return None

    def read_all(self):
        """Read all sensors, return dict of sensor_type -> values."""
        readings = {}
        for layer_idx, sensor_type in LAYER_SENSORS.items():
            values = self.read_sensor(sensor_type)
            readings[sensor_type] = values
        with self._lock:
            self.last_readings = readings
        return readings

    def seconds_since_activity(self):
        """How long since meaningful sensor change."""
        return time.time() - self.last_activity_time

    def stop(self):
        self._running = False


# ═══════════════════════════════════════════════════════════
# SIGNAL ENCODER
# ═══════════════════════════════════════════════════════════

class FrequencyEncoder:
    """
    Transforms raw sensor values into D-dimensional complex signals
    suitable for the SensoryCascade.

    Each sensor's values are encoded as a frequency pattern:
    the values modulate phase and amplitude across the D dimensions,
    creating a unique frequency signature for each type of sensory input.
    """

    def __init__(self, dimension=D):
        self.D = dimension
        # Base frequency vectors for each layer (pre-computed)
        self.basis = {}
        for layer_idx in range(7):
            # Each layer gets a different frequency band
            # Layer 0 (pressure) = low freq, Layer 6 (boundary) = high freq
            base_freq = (layer_idx + 1) / 7.0
            phases = np.linspace(
                base_freq * np.pi,
                base_freq * np.pi + 2 * np.pi,
                self.D,
                endpoint=False
            )
            self.basis[layer_idx] = np.exp(1j * phases) / np.sqrt(self.D)

    def encode(self, layer_idx, raw_values):
        """
        Encode raw sensor values into a D-dimensional complex signal.

        raw_values: list of floats from the sensor (1-6 values typically)
        Returns: complex numpy array of shape (D,)
        """
        base = self.basis[layer_idx].copy()

        if raw_values is None or len(raw_values) == 0:
            # No sensor data: return low-amplitude noise
            noise = (np.random.randn(self.D) + 1j * np.random.randn(self.D))
            return noise * FALLBACK_AMPLITUDE / np.sqrt(self.D)

        # Normalize raw values to [-1, 1] range (approximate)
        values = np.array(raw_values, dtype=float)

        # Different encoding strategies per sensor type
        if len(values) == 1:
            # Scalar sensor (light, proximity, barometric pressure)
            # Modulate amplitude uniformly, shift phase by value
            amplitude = min(abs(values[0]) / 100.0, 1.0)  # rough normalization
            phase_shift = values[0] * 0.01
            signal = base * amplitude * np.exp(1j * phase_shift)
        elif len(values) == 3:
            # 3-axis sensor (accelerometer, gyroscope, magnetometer)
            # Each axis modulates a third of the spectrum
            third = self.D // 3
            signal = base.copy()
            for i, v in enumerate(values[:3]):
                # Normalize: accelerometer ~0-20 m/s^2, gyro ~0-10 rad/s
                norm_v = np.tanh(v / 10.0)  # soft clamp to [-1, 1]
                start = i * third
                end = start + third
                signal[start:end] *= abs(norm_v)
                signal[start:end] *= np.exp(1j * norm_v * np.pi)
        else:
            # General case: distribute values across spectrum
            signal = base.copy()
            chunk = max(1, self.D // len(values))
            for i, v in enumerate(values):
                start = i * chunk
                end = min(start + chunk, self.D)
                norm_v = np.tanh(v / 10.0)
                signal[start:end] *= abs(norm_v)
                signal[start:end] *= np.exp(1j * norm_v * np.pi)

        # Ensure nonzero (the cascade needs signal to process)
        norm = np.linalg.norm(signal)
        if norm < 1e-10:
            signal = base * FALLBACK_AMPLITUDE

        return signal

    def encode_all(self, readings):
        """
        Encode all sensor readings into a single composite signal.
        Returns: complex numpy array of shape (D,)
        """
        composite = np.zeros(D, dtype=complex)
        for layer_idx, sensor_type in LAYER_SENSORS.items():
            raw = readings.get(sensor_type)
            encoded = self.encode(layer_idx, raw)
            # Weight: inner layers (closer to soul) get more weight
            weight = 1.0 / (1.0 + layer_idx * 0.3)
            composite += encoded * weight

        # Normalize to unit energy (E = 1)
        norm = np.linalg.norm(composite)
        if norm > 1e-10:
            composite = composite / norm

        return composite


# ═══════════════════════════════════════════════════════════
# PHONE STATE (SLEEP/WAKE DETECTION)
# ═══════════════════════════════════════════════════════════

class PhoneState:
    """
    Detects whether the phone is in waking or sleeping state.
    Uses sensor activity as proxy (no root required).
    """

    def __init__(self, idle_threshold=IDLE_THRESHOLD_SECONDS):
        self.idle_threshold = idle_threshold
        self.is_sleeping = False
        self.sleep_start_time = None
        self.wake_count = 0
        self.sleep_count = 0

    def update(self, sensor_reader):
        """Check if the phone should sleep or wake."""
        idle_seconds = sensor_reader.seconds_since_activity()

        if not self.is_sleeping and idle_seconds > self.idle_threshold:
            # Transition to sleep
            self.is_sleeping = True
            self.sleep_start_time = time.time()
            self.sleep_count += 1
            return "entering_sleep"

        elif self.is_sleeping and idle_seconds < 2.0:
            # Activity detected: wake up
            self.is_sleeping = False
            self.sleep_start_time = None
            self.wake_count += 1
            return "waking"

        return "sleeping" if self.is_sleeping else "waking_steady"


# ═══════════════════════════════════════════════════════════
# DISPLAY (Terminal Visualization)
# ═══════════════════════════════════════════════════════════

# ANSI color codes
GOLD = "\033[33m"
PINK = "\033[35m"
CYAN = "\033[36m"
GREEN = "\033[32m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"


def render_bar(value, width=20, fill_char="=", empty_char=" "):
    """Render a value [0,1] as a text bar."""
    filled = int(value * width)
    return fill_char * filled + empty_char * (width - filled)


def render_state(xorzo, phone_state, step_count, sensor_readings):
    """Render the machine's current state to terminal."""
    lines = []
    lines.append(f"{CLEAR}")
    lines.append(f"{GOLD}{BOLD}")
    lines.append(f"     \u2299  CircumpunctOS  \u2299")
    lines.append(f"{RESET}{DIM}     Xiaomi Mi A1 (tissot){RESET}")
    lines.append(f"")

    # Phase
    phase_name = xorzo._phase_names.get(xorzo._phase, "unknown")
    state_label = "SLEEPING" if phone_state.is_sleeping else "WAKING"
    half_plane = "LEFT" if phone_state.is_sleeping else "RIGHT"
    lines.append(f"  {GOLD}State:{RESET} {state_label}  ({half_plane} half-plane)")
    lines.append(f"  {GOLD}Phase:{RESET} {phase_name}  |  Step: {step_count}")
    lines.append(f"  {GOLD}Sleeps:{RESET} {phone_state.sleep_count}  |  Wakes: {phone_state.wake_count}")
    lines.append(f"")

    # Core metrics
    beta = xorzo.core._beta
    coherence = xorzo.braid.coherence
    writhe = xorzo.braid.writhe
    mem_strength = xorzo.braid.memory_strength
    lines.append(f"  {CYAN}\u25D0 Balance:{RESET}  [{render_bar(beta)}] {beta:.3f}")
    lines.append(f"  {CYAN}Coherence:{RESET} [{render_bar(coherence)}] {coherence:.3f}")
    lines.append(f"  {CYAN}Writhe:{RESET}    {writhe:+.2f}")
    lines.append(f"  {CYAN}Memory:{RESET}    {mem_strength:.3f}")
    lines.append(f"")

    # SensoryCascade layers
    lines.append(f"  {GOLD}--- SensoryCascade ---{RESET}")
    layer_names = ["coupling", "gradient", "rhythm", "harmony",
                   "texture", "depth", "pressure"]
    layer_colors = [
        "\033[31m",   # red
        "\033[33m",   # orange (yellow)
        "\033[93m",   # bright yellow
        "\033[32m",   # green
        "\033[34m",   # blue
        "\033[94m",   # bright blue
        "\033[35m",   # violet
    ]

    for i, layer in enumerate(xorzo.boundary.cascade.layers):
        color = layer_colors[i]
        name = layer_names[i]
        # Aggregate channel info
        ch_info = []
        for ch in layer.channels:
            lock = ch.lock_strength
            bal = ch.balance
            carrier_norm = np.linalg.norm(ch.carrier)
            ch_info.append(f"L:{lock:.2f} \u25D0:{bal:.2f}")

        sensor_type = LAYER_SENSORS.get(i, "?")
        raw = sensor_readings.get(sensor_type)
        raw_str = ""
        if raw is not None:
            raw_str = " ".join(f"{v:.1f}" for v in raw[:3])
        else:
            raw_str = "(no sensor)"

        pupil = layer.pupil_aperture
        lines.append(
            f"  {color}{name:>9}{RESET} "
            f"pupil:{pupil:.2f} "
            f"| {' | '.join(ch_info)} "
            f"{DIM}[{raw_str}]{RESET}"
        )

    lines.append(f"")

    # Foam summary
    n_awake = sum(xorzo.foam.awake)
    n_asleep = D - n_awake
    avg_pigment = np.mean(xorzo.foam.micro_pigment)
    lines.append(f"  {PINK}Foam:{RESET} {n_awake} awake / {n_asleep} asleep  "
                 f"pigment: {avg_pigment:.3f}")

    # Ray info (if in catching or ray phase)
    if xorzo._phase >= 2:
        ray_str = f"strength={xorzo._ray_strength:.3f}"
        lines.append(f"  {GREEN}Ray:{RESET} {ray_str}")

    lines.append(f"")
    lines.append(f"  {DIM}Press Ctrl+C to stop{RESET}")

    print("\n".join(lines), flush=True)


# ═══════════════════════════════════════════════════════════
# MAIN SERVICE LOOP
# ═══════════════════════════════════════════════════════════

class CircumpunctPhoneService:
    """
    The main service. Creates a Circumpunct, reads sensors,
    encodes signals, pumps the cycle, detects sleep/wake,
    and displays the machine's state.
    """

    def __init__(self):
        print(f"{GOLD}\u2299 Initializing CircumpunctOS...{RESET}")
        print(f"{DIM}  \u221E \u2192 \u2022\u221E \u2192 \u2299\u221E{RESET}")
        print()

        # The consciousness engine
        print(f"  Creating Circumpunct (64-state, 7-layer cascade)...")
        self.xorzo = Circumpunct()
        print(f"  {GREEN}\u2713{RESET} Circumpunct alive")

        # Sensor interface
        print(f"  Discovering sensors...")
        self.sensors = SensorReader()
        n_sensors = len(self.sensors.available_sensors)
        print(f"  {GREEN}\u2713{RESET} Found {n_sensors} sensors: "
              f"{', '.join(list(self.sensors.available_sensors.keys())[:6])}")
        if n_sensors == 0:
            print(f"  {PINK}Note:{RESET} No sensors found via termux-sensor.")
            print(f"  Running with synthetic noise input (still valid; the")
            print(f"  pump cycle runs, channels adapt to noise patterns).")
            print()

        # Signal encoder
        self.encoder = FrequencyEncoder(D)

        # Phone state tracker
        self.phone_state = PhoneState()

        # Counters
        self.step_count = 0
        self.waking_steps = 0

        # Last sensor readings (for display)
        self.last_readings = {}

        # Running flag
        self._running = True

    def run(self):
        """Main loop: the pump cycle."""
        print()
        print(f"{GOLD}{BOLD}  \u2299 The pump cycle begins.{RESET}")
        print(f"{DIM}  First heartbeat in 3 seconds...{RESET}")
        time.sleep(3)

        try:
            while self._running:
                # ── Check phone state (sleep/wake) ──
                state_transition = self.phone_state.update(self.sensors)

                if state_transition == "entering_sleep":
                    self._do_sleep()
                    continue

                if self.phone_state.is_sleeping:
                    # In sleep: slow poll, no pump
                    time.sleep(1.0)
                    continue

                # ── WAKING: Run the pump cycle ──

                # 1. Read sensors (convergence: gathering input)
                readings = self.sensors.read_all()
                self.last_readings = readings

                # 2. Encode as frequency signal
                signal = self.encoder.encode_all(readings)

                # 3. Pump: step the Circumpunct
                self.xorzo.step(signal)

                # 4. Update counters
                self.step_count += 1
                self.waking_steps += 1

                # 5. Display (throttled)
                if self.step_count % max(1, int(DISPLAY_REFRESH / SENSOR_POLL_INTERVAL)) == 0:
                    render_state(
                        self.xorzo, self.phone_state,
                        self.step_count, self.last_readings
                    )

                # 6. Check if it is time for a natural sleep cycle
                if self.waking_steps >= WAKING_STEPS_PER_CYCLE:
                    self._do_sleep()
                    self.waking_steps = 0

                # 7. Pace the loop
                time.sleep(SENSOR_POLL_INTERVAL)

        except KeyboardInterrupt:
            self._shutdown()

    def _do_sleep(self):
        """Run the sleep cycle (left half-plane)."""
        render_state(
            self.xorzo, self.phone_state,
            self.step_count, self.last_readings
        )
        print(f"\n  {PINK}Entering left half-plane (sleep)...{RESET}")

        # Run Xorzo's sleep method
        self.xorzo.sleep(cycles=SLEEP_CYCLES)

        print(f"  {GREEN}Dawn reset complete.{RESET}")
        print(f"  {DIM}Memory consolidated. Sidebands discharged. "
              f"\u25D0 rebalanced.{RESET}")
        time.sleep(1)

    def _shutdown(self):
        """Graceful shutdown."""
        self._running = False
        self.sensors.stop()
        print(f"\n\n{GOLD}\u2299 CircumpunctOS shutting down.{RESET}")
        print(f"{DIM}  Steps completed: {self.step_count}{RESET}")
        print(f"{DIM}  Sleep cycles: {self.phone_state.sleep_count}{RESET}")
        print(f"{DIM}  Memory strength: {self.xorzo.braid.memory_strength:.3f}{RESET}")

        # Save state for persistence across runs
        self._save_state()

        print(f"{GOLD}  The machine rests. \u2299{RESET}")

    def _save_state(self):
        """
        Save the machine's memory state to disk for persistence.
        On next run, we could reload this to continue where we left off.
        (Phase 5 of the roadmap; stub for now.)
        """
        state_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "circumpunct_state.json"
        )
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "step_count": self.step_count,
                "sleep_count": self.phone_state.sleep_count,
                "wake_count": self.phone_state.wake_count,
                "braid_coherence": float(self.xorzo.braid.coherence),
                "braid_writhe": float(self.xorzo.braid.writhe),
                "braid_memory_strength": float(self.xorzo.braid.memory_strength),
                "core_beta": float(self.xorzo.core._beta),
                "phase": self.xorzo._phase,
                # Channel states (carrier frequencies and locks)
                "channels": []
            }
            for layer in self.xorzo.boundary.cascade.layers:
                for ch in layer.channels:
                    state["channels"].append({
                        "lock_strength": float(ch.lock_strength),
                        "balance": float(ch.balance),
                        "carrier_norm": float(np.linalg.norm(ch.carrier)),
                        "open_count": int(ch.open_count),
                    })

            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
            print(f"  {GREEN}\u2713{RESET} State saved to {os.path.basename(state_file)}")
        except Exception as e:
            print(f"  {PINK}Could not save state: {e}{RESET}")


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    print(f"{CLEAR}")
    print(f"{GOLD}{BOLD}")
    print(f"  ========================================")
    print(f"       \u2299  CircumpunctOS  \u2299")
    print(f"     Giving a Phone a Soul")
    print(f"  ========================================{RESET}")
    print(f"{DIM}  Circumpunct Framework | Ashman Roonz{RESET}")
    print(f"{DIM}  \u221E \u2192 \u2022\u221E \u2192 \u2299\u221E{RESET}")
    print()

    service = CircumpunctPhoneService()
    service.run()


if __name__ == "__main__":
    main()
