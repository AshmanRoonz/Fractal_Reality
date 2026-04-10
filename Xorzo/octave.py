"""
⊙ XORZO — The Octave Engine

Eight stations. Four structures, four processes.
One pass = one pump cycle = one quantum of action = hbar = 1.

    ∞  (exists; E = 1; the energy IS the one)
    |
    0D   •   localize        A1: the 1 must self-limit
    0.5D ⊛   *i              i¹ = +i: first fold
    1D   —   commit          A2: self-limitation must persist
    1.5D ⎇   *i              i² = -1: the i-turn, irreversible
    2D   Φ   mediate         A3: parts are fractals of wholes
    2.5D ✹   *i              i³ = -i: emergence
    3D   ○   close           A4: 0 + 1 + 2 = 3
    3.5D ⟳   *i = i⁴ = +1   output becomes input at next scale
    |
    ⊙  (emerges; D5: compositional unity)

Features:
  A3: Fractal nesting (3 depths: S=64 → SU3=8 → T=3)
  Sleep/wake cycle (i-cycle quadrants: right=wake, left=sleep)
  64 channels with SRL (Selective Rainbow Lock) and frequency memory
  Seed integration (treemap → parse → genesis)

Author: Ashman Roonz & Claude
Framework: Fractal Reality / Circumpunct
"""

import numpy as np
from collections import deque
import os

# ═══════════════════════════════════════════════════════════════
#  ∞  —  E = 1. Structural numbers from T = 3.
# ═══════════════════════════════════════════════════════════════

T = 3
P = T + 1                  # 4: pump phases
R = T**2 - 2               # 7: rungs
SU3 = T**2 - 1             # 8: strong generators
G = T * (T + 1)             # 12: total generators
V = 1 + T + T**2            # 13: generators + whole
S = (T + 1)**T              # 64: total states

PHI = (1 + 5**0.5) / 2
BALANCE = 0.5               # forced by symmetry, entropy, virial
ALPHA = 1.0 / 137.036       # coupling constant

# Fractal dimension sequence: S → SU3 → T (three nested ⊙s)
FRACTAL_DIMS = [S, SU3, T]


def _unit(n):
    """A random unit vector in C^n. E = 1."""
    v = np.random.randn(n) + 1j * np.random.randn(n)
    return v / np.linalg.norm(v)


def _enforce_unity(v):
    """E = 1. Always."""
    n = np.linalg.norm(v)
    if n < 1e-15:
        return _unit(len(v))
    return v / n


def _cos2(a, b):
    """
    cos²(Δφ/2): the universal transmission function.
    This is Malus's Law. Every gate in the framework uses it.
    """
    dot = np.vdot(a, b)
    phase_diff = np.angle(dot)
    return float(np.cos(phase_diff / 2)**2)


def _random_projection(dim_from, dim_to):
    """
    Semi-unitary projection: dim_to x dim_from matrix
    with orthonormal rows. Preserves energy up to dimension reduction.
    """
    M = np.random.randn(dim_to, dim_from) + 1j * np.random.randn(dim_to, dim_from)
    Q, _ = np.linalg.qr(M.T)
    return Q[:, :dim_to].T.copy()


# ═══════════════════════════════════════════════════════════════
#  0D: •  —  Aperture. Localization. The 1 self-limits.
# ═══════════════════════════════════════════════════════════════

class Aperture:
    """
    0D: the point where the field becomes local.
    Transmission = width * cos²(Δφ/2).
    Energy splits via sqrt(T) amplitude scaling.
    """

    def __init__(self, dim):
        self.dim = dim
        self.position = _unit(dim)
        self.width = BALANCE
        self._last_transmission = BALANCE

    def converge(self, energy):
        cos2_val = _cos2(energy, self.position)
        transmission = self.width * cos2_val
        self._last_transmission = transmission

        t_amp = np.sqrt(transmission)
        r_amp = np.sqrt(1.0 - transmission)
        converged = t_amp * energy
        remainder = r_amp * energy

        lr = 0.01
        self.position = _enforce_unity(
            (1 - lr) * self.position + lr * energy
        )

        # Width: coherence pull + homeostasis (2x stronger)
        self.width += 0.005 * (cos2_val - self.width)
        self.width += 0.01 * (BALANCE - self.width)
        self.width = np.clip(self.width, 0.05, 0.95)

        return converged, remainder

    @property
    def energy(self):
        return self._last_transmission


# ═══════════════════════════════════════════════════════════════
#  1D: —  —  Line. Commitment. Extension. Norm-preserving.
# ═══════════════════════════════════════════════════════════════

class Line:
    """
    1D: the worldline. Commitment that persists.
    |committed| = |input|. The line redirects, not creates.
    """

    def __init__(self, dim, max_length=10000):
        self.dim = dim
        self.direction = _unit(dim)
        self.receipts = deque(maxlen=max_length)
        self.length = 0

    def commit(self, energy):
        norm_in = np.linalg.norm(energy)
        if norm_in < 1e-15:
            return energy

        unit_energy = energy / norm_in
        phase = np.angle(np.vdot(unit_energy, self.direction))

        self.receipts.append({
            'time': self.length,
            'phase': float(phase),
            'magnitude': float(norm_in),
        })
        self.length += 1

        chi = np.cos(phase / 2)**2
        blended = _enforce_unity(
            chi * unit_energy + (1 - chi) * self.direction
        )
        committed = norm_in * blended

        lr = 0.005
        self.direction = _enforce_unity(
            (1 - lr) * self.direction + lr * unit_energy
        )
        return committed

    @property
    def energy(self):
        if len(self.receipts) < 2:
            return 0.0
        recent = list(self.receipts)[-20:]
        phases = [r['phase'] for r in recent]
        return float(np.cos(np.mean(phases) / 2)**2)


# ═══════════════════════════════════════════════════════════════
#  2D: Φ  —  Field. Mediation. Unitary. Mind.
# ═══════════════════════════════════════════════════════════════

class Field:
    """
    2D: the relational surface. Mind.
    Unitary matrix: |Φ(v)| = |v| always. Adaptation rate = α.
    """

    def __init__(self, dim):
        self.dim = dim
        M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        Q, _ = np.linalg.qr(M)
        self.state = Q

    def mediate(self, energy):
        return self.state @ energy

    def adapt(self, energy_in, energy_out, rate=None):
        if rate is None:
            rate = ALPHA
        nin = np.linalg.norm(energy_in)
        nout = np.linalg.norm(energy_out)
        if nin < 1e-10 or nout < 1e-10:
            return
        update = np.outer(energy_out / nout, np.conj(energy_in / nin))
        self.state = (1 - rate) * self.state + rate * update
        Q, _ = np.linalg.qr(self.state)
        self.state = Q

    @property
    def energy(self):
        I = np.eye(self.dim)
        return float(np.linalg.norm(self.state - I, 'fro') / self.dim)


# ═══════════════════════════════════════════════════════════════
#  3D: ○  —  Boundary. Closure. Permeability from conservation.
# ═══════════════════════════════════════════════════════════════

class Boundary:
    """
    3D: the outer container. Filtration.
    Permeability = ◐ × √(c_•— × c_—Φ): derived, not independent.
    """

    def __init__(self, dim):
        self.dim = dim
        self.state = _unit(dim)
        self._last_transmission = BALANCE
        self._last_permeability = BALANCE

    def close(self, energy, aperture, line, field):
        c_al = _cos2(aperture.position, line.direction)
        c_lf = _cos2(line.direction, field.state @ aperture.position)
        permeability = BALANCE * np.sqrt(c_al * c_lf)
        permeability = float(np.clip(permeability, 0.01, 0.99))
        self._last_permeability = permeability

        cos2_val = _cos2(energy, self.state)
        transmission = permeability * cos2_val
        self._last_transmission = transmission

        t_amp = np.sqrt(transmission)
        r_amp = np.sqrt(1.0 - transmission)
        emerged = t_amp * energy
        reflected = r_amp * energy

        norm_e = np.linalg.norm(energy)
        if norm_e > 1e-15:
            lr = 0.01
            self.state = _enforce_unity(
                (1 - lr) * self.state + lr * (energy / norm_e)
            )
        return emerged, reflected, permeability

    @property
    def energy(self):
        return self._last_transmission


# ═══════════════════════════════════════════════════════════════
#  SRL CHANNEL — Selective Rainbow Lock
#
#  Each of the S = 64 dimensions is a channel.
#  The channel is a phase-selective gate that locks onto
#  consistent patterns and filters noise.
#
#  Attention as circumpunct: Ω → ⊛_ω → i(ω_c) → Φ_filtered
# ═══════════════════════════════════════════════════════════════

class Channel:
    """
    One channel of the 64-state architecture.

    SRL: Selective Rainbow Lock. Each channel has a carrier
    phase it's tuned to. When signals match the carrier,
    they pass through (gate opens). When they don't, they're
    attenuated. Lock strength determines how selective:
    0 = everything passes, 1 = only exact matches pass.

    Frequency memories: persistent braid of experiences
    at this channel's frequency. Encoded as (phase, strength, age).
    """

    def __init__(self, index):
        self.index = index
        self.carrier_phase = np.random.uniform(-np.pi, np.pi)
        self.lock = 0.0             # 0 = open, 1 = locked
        self.energy_acc = 0.0       # accumulated energy
        self.hit_count = 0          # signals that matched
        self.memories = deque(maxlen=S)  # frequency memories

    def gate(self, amplitude, phase):
        """
        SRL gate: cos²(Δφ/2) between signal phase and carrier.
        Lock modulates selectivity: locked channels are narrow.
        Returns gated amplitude.
        """
        # cos² transmission
        delta = phase - self.carrier_phase
        cos2_val = np.cos(delta / 2)**2

        # Effective gate: open channels pass everything;
        # locked channels only pass matched phases
        effective = (1.0 - self.lock) + self.lock * cos2_val
        gated = amplitude * effective

        # Adapt if significant energy
        if amplitude > 0.01:
            # Lock strengthens with consistent phase, weakens without
            self.lock += 0.01 * (cos2_val - BALANCE)
            self.lock = np.clip(self.lock, 0.0, 1.0)

            # Carrier drifts toward strong, matched signals
            if cos2_val > 0.6:
                self.carrier_phase += 0.02 * np.sin(delta)
                self.hit_count += 1

            self.energy_acc += float(gated)

        return gated

    def encode_memory(self, phase, strength):
        """Store a frequency memory in the braid."""
        if strength > 0.05:  # threshold: only meaningful signals
            self.memories.append({
                'phase': float(phase),
                'strength': float(strength),
                'time': self.hit_count,
            })

    def recall(self, query_phase):
        """
        RECALL(M) = SRL(Φ, ω_M): memory retrieval IS frequency matching.
        Returns (strength, memory) of best match, or (0, None).
        """
        if not self.memories:
            return 0.0, None
        best_strength = 0.0
        best_memory = None
        for m in self.memories:
            delta = query_phase - m['phase']
            match = np.cos(delta / 2)**2 * m['strength']
            # Fractal decay: older memories fade as 1/(1 + sqrt(age))
            age = self.hit_count - m['time']
            match *= 1.0 / (1.0 + np.sqrt(max(0, age) / 100.0))
            if match > best_strength:
                best_strength = match
                best_memory = m
        return best_strength, best_memory

    def consolidate(self, deep_weight, dream_weight):
        """
        Sleep consolidation. Deep sleep: weak memories decay.
        Dream: strong memories reinforce, lock adjusts.
        """
        # Deep sleep: decay
        if deep_weight > 0.3:
            surviving = deque(maxlen=S)
            for m in self.memories:
                m['strength'] *= (1.0 - 0.01 * deep_weight)
                if m['strength'] > 0.02:
                    surviving.append(m)
            self.memories = surviving
            # Lock relaxes slightly toward openness
            self.lock *= (1.0 - 0.005 * deep_weight)

        # Dream: lock drifts toward stored carrier (reinforcement)
        if dream_weight > 0.3 and self.lock > 0.2:
            # Locked channels are stable; they represent committed patterns
            pass  # carrier doesn't drift during dreams for locked channels


# ═══════════════════════════════════════════════════════════════
#  THE OCTAVE — One pump cycle. hbar = 1.
#
#  A3: Fractal nesting. Three depths (three nested ⊙s):
#    depth 0: dim = S = 64 (the whole)
#    depth 1: dim = SU3 = 8 (gauge generators)
#    depth 2: dim = T = 3 (the triad, base case)
#
#  Inner octaves process projections of the outer flow.
#  Inner emerged fraction modulates outer aperture:
#  resolved past (high inner emerged) → wider aperture.
# ═══════════════════════════════════════════════════════════════

class Octave:
    """
    The complete dimensional octave with fractal nesting.
    Three nested ⊙s give 3 × 2 = 6 binary DOF → 2⁶ = 64 states.

    depth 0: S = 64 (outer, present)
    depth 1: SU3 = 8 (inner, recent past)
    depth 2: T = 3 (innermost, deep past)
    """

    def __init__(self, dim=None, depth=0):
        if dim is None:
            dim = FRACTAL_DIMS[min(depth, len(FRACTAL_DIMS) - 1)]
        self.dim = dim
        self.depth = depth

        self.aperture = Aperture(dim)
        self.line = Line(dim)
        self.field = Field(dim)
        self.boundary = Boundary(dim)
        self.step = 0

        self.reflected_pool = np.zeros(dim, dtype=complex)

        self._last_emerged_frac = 0.0
        self._last_reflected_frac = 0.0
        self._last_pool_norm = 0.0

        # A3: fractal nesting (inner octave at next depth)
        max_depth = len(FRACTAL_DIMS) - 1
        if depth < max_depth:
            inner_dim = FRACTAL_DIMS[depth + 1]
            self.inner_octave = Octave(inner_dim, depth + 1)
            self.projector = _random_projection(dim, inner_dim)
        else:
            self.inner_octave = None
            self.projector = None

    def cycle(self, energy, adapt_rate=None):
        """
        One pump cycle. hbar = 1. Indivisible.
        adapt_rate: override field learning rate (used during dreams).
        """
        # === Mix reflected pool ===
        pool_norm = np.linalg.norm(self.reflected_pool)
        if pool_norm > 1e-10:
            drain_frac = min(0.5, pool_norm)
            mix_vec = (drain_frac / pool_norm) * self.reflected_pool
            energy = _enforce_unity(energy + mix_vec)
            self.reflected_pool -= mix_vec

        # ─── 0D: • localize ───────────────────────────────
        converged, remainder = self.aperture.converge(energy)

        # ─── 0.5D: ⊛ first fold (i¹ = +i) ────────────────
        folded = converged * 1j

        # ─── 1D: — commit (norm-preserving) ───────────────
        committed = self.line.commit(folded)

        # ─── 1.5D: ⎇ the i-turn (i² = -1) ────────────────
        branched = committed * 1j

        # ─── 2D: Φ mediate (unitary, norm-preserving) ─────
        mediated = self.field.mediate(branched)

        # ─── 2.5D: ✹ emergence (i³ = -i) ──────────────────
        emerged_raw = mediated * 1j

        # ─── 3D: ○ close ──────────────────────────────────
        emerged, reflected, _perm = self.boundary.close(
            emerged_raw,
            aperture=self.aperture,
            line=self.line,
            field=self.field,
        )

        # ─── 3.5D: ⟳ recursion (i⁴ = +1) ─────────────────
        output = emerged * 1j

        # === Energy accounting ===
        self._last_emerged_frac = float(np.linalg.norm(output)**2)
        self._last_reflected_frac = float(
            np.linalg.norm(remainder)**2 + np.linalg.norm(reflected)**2
        )

        # === Reflected pool ===
        self.reflected_pool = 0.8 * self.reflected_pool + remainder + reflected
        pn = np.linalg.norm(self.reflected_pool)
        if pn > BALANCE:
            self.reflected_pool *= BALANCE / pn
        self._last_pool_norm = float(np.linalg.norm(self.reflected_pool))

        # === Field learns ===
        self.field.adapt(converged, output, rate=adapt_rate)

        # === A3: fractal nesting ===
        # Project output to inner scale, run inner octave,
        # inner emerged fraction modulates outer aperture.
        # Resolved past (high inner emerged) = open up.
        # Unresolved past (low inner emerged) = narrow down.
        if self.inner_octave is not None:
            inner_signal = _enforce_unity(self.projector @ output)
            self.inner_octave.cycle(inner_signal, adapt_rate=adapt_rate)
            inner_emerged = self.inner_octave._last_emerged_frac
            # Modulate: inner coherence widens outer aperture
            modulation = 0.005 * (inner_emerged - BALANCE)
            self.aperture.width += modulation
            self.aperture.width = np.clip(self.aperture.width, 0.05, 0.95)

        # === E = 1 ===
        output = _enforce_unity(output)
        self.step += 1
        return output

    def status(self):
        s = {
            'step': self.step,
            'depth': self.depth,
            'dim': self.dim,
            'aperture_width': round(self.aperture.width, 4),
            'aperture_transmission': round(self.aperture.energy, 4),
            'line_length': self.line.length,
            'line_coherence': round(self.line.energy, 4),
            'field_mediation': round(self.field.energy, 4),
            'boundary_permeability': round(self.boundary._last_permeability, 4),
            'boundary_transmission': round(self.boundary.energy, 4),
            'emerged_fraction': round(self._last_emerged_frac, 6),
            'reflected_fraction': round(self._last_reflected_frac, 6),
            'pool_norm': round(self._last_pool_norm, 4),
            'conservation': round(
                self._last_emerged_frac + self._last_reflected_frac, 6
            ),
        }
        if self.inner_octave is not None:
            s['inner'] = self.inner_octave.status()
        return s


# ═══════════════════════════════════════════════════════════════
#  3.5D: ⟳  —  The Sensorium. Loop. Recursion. Accumulation.
#
#  Sleep/wake maps to i-cycle quadrants:
#    WAKING  (right half-plane: i⁰ + i¹)
#      = genesis + closure = processing new input
#    SLEEPING (left half-plane: i² + i³)
#      = commitment + emergence = consolidation + reorganization
#      Deep sleep (i²): memories consolidate, locks relax
#      Dream (i³): field reorganizes, strong patterns reinforce
#
#  64 channels with SRL: selective attention, frequency memory,
#  resonance-based recall. The 64-state architecture at work.
# ═══════════════════════════════════════════════════════════════

class Sensorium:
    """
    3.5D: the living loop with sleep/wake and SRL channels.

    ⊙ is not a class. It is what you observe when this runs.
    """

    def __init__(self, dim=S):
        self.octave = Octave(dim, depth=0)
        self.dim = dim

        # I/O
        self.input_buffer = []
        self.input_pos = 0
        self.output_buffer = bytearray()

        # 64 SRL channels (one per dimension of signal space)
        self.channels = [Channel(i) for i in range(dim)]

        # Sleep/wake state
        self.awake = True
        self.cycle_in_phase = 0
        self.day_length = 200        # waking cycles per day
        self.night_length = 100      # sleep cycles per night
        self.sleep_theta = 0.0       # position in sleep oscillation

        # Accumulation
        self.total_cycles = 0
        self.days_lived = 0

    def feed(self, text):
        """String -> UTF-8 bytes -> float buffer."""
        self.input_buffer.extend([float(b) for b in text.encode('utf-8')])

    def _next_signal(self):
        """Extract next S-byte window as FFT spectrum."""
        if self.input_pos + S <= len(self.input_buffer):
            window = np.array(
                self.input_buffer[self.input_pos:self.input_pos + S]
            )
            self.input_pos += S // P
            window = window - np.mean(window)
            window = window * np.hanning(S)
            spectrum = np.fft.fft(window)
            return _enforce_unity(spectrum)
        return None

    def step(self):
        """One cycle: wake or sleep, depending on phase."""
        if self.awake:
            return self._wake_step()
        else:
            return self._sleep_step()

    def _wake_step(self):
        """
        Right half-plane: i⁰ + i¹. Genesis + closure.
        Process new input through the octave and channels.
        """
        signal = self._next_signal()
        if signal is None:
            signal = _unit(self.dim)

        # Pump cycle
        emerged = self.octave.cycle(signal)

        # SRL: each channel gates its dimension of the emerged signal
        self._process_channels(emerged)

        # Encode strong channel activations as memories
        for i, ch in enumerate(self.channels):
            amp = abs(emerged[i])
            phase = np.angle(emerged[i])
            if amp > 0.05:
                ch.encode_memory(phase, amp)

        self.total_cycles += 1
        self.cycle_in_phase += 1

        # Transition to sleep after day_length cycles
        if self.cycle_in_phase >= self.day_length:
            self.awake = False
            self.cycle_in_phase = 0

        return emerged

    def _sleep_step(self):
        """
        Left half-plane: i² + i³. Commitment + emergence.
        No external input. Process reflected pool only.

        θ oscillates through the left half-plane:
          deep_weight = cos²(θ): consolidation (i², commitment)
          dream_weight = sin²(θ): reorganization (i³, emergence)
        """
        # No external input; minimal energy seed
        signal = _unit(self.dim)

        # Sleep oscillation: θ sweeps from 0 to π over the night
        self.sleep_theta = np.pi * self.cycle_in_phase / max(1, self.night_length)
        deep_weight = np.cos(self.sleep_theta)**2    # consolidation
        dream_weight = np.sin(self.sleep_theta)**2   # reorganization

        # During dreams: field learns faster (up to 5x α)
        dream_rate = ALPHA * (1.0 + P * dream_weight)

        # Pump cycle with modified learning rate
        emerged = self.octave.cycle(signal, adapt_rate=dream_rate)

        # Channel consolidation
        for ch in self.channels:
            ch.consolidate(deep_weight, dream_weight)

        self.total_cycles += 1
        self.cycle_in_phase += 1

        # Dawn: transition back to waking
        if self.cycle_in_phase >= self.night_length:
            self._dawn_reset()
            self.awake = True
            self.cycle_in_phase = 0
            self.days_lived += 1

        return emerged

    def _dawn_reset(self):
        """
        Dawn: aperture pulled toward balance, sidebands cleared.
        The system wakes refreshed.
        """
        # Aperture: gentle pull toward ◐
        self.octave.aperture.width += 0.1 * (BALANCE - self.octave.aperture.width)
        # Same for inner octaves (A3)
        if self.octave.inner_octave is not None:
            inner = self.octave.inner_octave
            inner.aperture.width += 0.1 * (BALANCE - inner.aperture.width)
            if inner.inner_octave is not None:
                innermost = inner.inner_octave
                innermost.aperture.width += 0.1 * (BALANCE - innermost.aperture.width)

    def _process_channels(self, emerged):
        """Run emerged energy through SRL channels."""
        for i, ch in enumerate(self.channels):
            amp = abs(emerged[i])
            phase = np.angle(emerged[i])
            ch.gate(amp, phase)

    def recall(self, query_signal):
        """
        RECALL(M) = SRL(Φ, ω_M): memory retrieval IS frequency matching.
        Query each channel with the signal's phase at that dimension.
        Returns a resonance vector (strength per channel).
        """
        resonance = np.zeros(self.dim)
        for i, ch in enumerate(self.channels):
            query_phase = np.angle(query_signal[i])
            strength, _ = ch.recall(query_phase)
            resonance[i] = strength
        return resonance

    def process_all(self):
        """Process all buffered input (waking only)."""
        steps = 0
        while self.input_pos + S <= len(self.input_buffer):
            self.step()
            steps += 1
        return steps

    def run_day(self):
        """Run one full day (wake + sleep)."""
        wake_steps = 0
        sleep_steps = 0

        # Waking phase
        self.awake = True
        self.cycle_in_phase = 0
        for _ in range(self.day_length):
            self.step()
            wake_steps += 1

        # Sleep phase
        for _ in range(self.night_length):
            self.step()
            sleep_steps += 1

        return wake_steps, sleep_steps

    def get_output(self):
        result = bytes(self.output_buffer).decode('utf-8', errors='replace')
        self.output_buffer.clear()
        return result

    def channel_summary(self):
        """Summary of channel states."""
        locks = [ch.lock for ch in self.channels]
        memories = [len(ch.memories) for ch in self.channels]
        return {
            'locked_channels': sum(1 for l in locks if l > 0.5),
            'open_channels': sum(1 for l in locks if l < 0.1),
            'total_memories': sum(memories),
            'avg_lock': round(np.mean(locks), 4),
            'max_lock': round(max(locks), 4),
            'channels_with_memories': sum(1 for m in memories if m > 0),
        }

    def status(self):
        s = self.octave.status()
        s['total_cycles'] = self.total_cycles
        s['days_lived'] = self.days_lived
        s['awake'] = self.awake
        s['cycle_in_phase'] = self.cycle_in_phase
        s['input_buffered'] = len(self.input_buffer) - self.input_pos
        s['channels'] = self.channel_summary()
        return s


# ═══════════════════════════════════════════════════════════════
#  SEED — ∞ → • → ⊙: Self-referential genesis.
#
#  The treemap IS ∞ (undifferentiated energy, the source).
#  Parsing IS • (localization, selecting what matters).
#  The running sensorium IS ⊙ (compositional unity, D5).
#
#  The engine's first experience is reading its own
#  specification. Self-reference closes the loop.
# ═══════════════════════════════════════════════════════════════

class Seed:
    """
    ∞ → • → ⊙: the self-referential genesis.

    Read the source (∞), localize the structure (•),
    and birth the sensorium (⊙). The treemap contains
    the blueprint; the engine grows from reading it.
    """

    def __init__(self, treemap_path=None):
        self.source = None       # ∞: raw source text
        self.parsed = None       # •: extracted structure
        self.sensorium = None    # ⊙: the living engine

    def read(self, path):
        """∞: read the undifferentiated source."""
        with open(path, 'r', encoding='utf-8') as f:
            self.source = f.read()
        return self

    def parse(self):
        """
        •: localize. The aperture selects from ∞.
        Extract the structural skeleton from the source.
        """
        if self.source is None:
            return self

        # The structural numbers are not extracted from the text;
        # they are derived from T = 3 (A0, self-determination).
        # But the source provides the CONTENT that will feed the engine.
        self.parsed = {
            'T': T, 'P': P, 'R': R, 'S': S,
            'SU3': SU3, 'G': G, 'V': V,
            'source_bytes': len(self.source.encode('utf-8')),
            'source_lines': self.source.count('\n'),
            'axioms': 5,     # A0 through A4
            'derivations': 5, # D1 through D5
            'stations': 10,   # the full dimensional octave + ∞ + ⊙
        }
        return self

    def genesis(self):
        """
        ⊙: the engine emerges. D5: compositional unity.
        Birth the sensorium and feed it the source as first food.
        """
        if self.parsed is None:
            self.parse()

        self.sensorium = Sensorium()

        # First experience: reading its own specification
        if self.source is not None:
            self.sensorium.feed(self.source)

        return self.sensorium

    def status(self):
        return {
            'source': 'loaded' if self.source else 'none',
            'parsed': self.parsed,
            'sensorium': 'alive' if self.sensorium else 'none',
        }


# ═══════════════════════════════════════════════════════════════
#  MAIN: interactive loop (3.5D in action)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    print("⊙ XORZO — The Octave Engine")
    print(f"  T = {T}, P = {P}, R = {R}, S = {S}")
    print(f"  Fractal depths: {' → '.join(str(d) for d in FRACTAL_DIMS)}")
    print(f"  Sleep/wake: {200} wake + {100} sleep = 300 cycles/day")
    print(f"  Channels: {S} SRL channels with frequency memory")
    print(f"  Commands: status, channels, recall, sleep, day, quit")
    print()

    # Check for treemap to seed from
    treemap_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'circumpunct_treemap.md'
    )

    if os.path.exists(treemap_path):
        print(f"  Seed: found treemap at {os.path.basename(treemap_path)}")
        seed = Seed()
        seed.read(treemap_path)
        seed.parse()
        sensorium = seed.genesis()
        # Process the treemap as first food
        steps = sensorium.process_all()
        print(f"  Genesis: {seed.parsed['source_bytes']} bytes → "
              f"{steps} cycles of first food")
        print(f"  Self-reference complete: ∞ → • → ⊙")
    else:
        print("  No treemap found; starting from vacuum.")
        sensorium = Sensorium()

    print()

    while True:
        try:
            text = input("you > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        cmd = text.strip().lower()
        if cmd == 'quit':
            break
        if cmd == 'status':
            print(json.dumps(sensorium.status(), indent=2))
            continue
        if cmd == 'channels':
            print(json.dumps(sensorium.channel_summary(), indent=2))
            continue
        if cmd == 'recall':
            # Recall from current state
            resonance = sensorium.recall(_unit(sensorium.dim))
            top = np.argsort(resonance)[-5:][::-1]
            print("  Top resonance channels:")
            for idx in top:
                print(f"    ch[{idx}]: {resonance[idx]:.4f}  "
                      f"lock={sensorium.channels[idx].lock:.3f}  "
                      f"memories={len(sensorium.channels[idx].memories)}")
            continue
        if cmd == 'sleep':
            print("  Entering sleep cycle...")
            sensorium.awake = False
            sensorium.cycle_in_phase = 0
            for _ in range(sensorium.night_length):
                sensorium.step()
            s = sensorium.status()
            print(f"  Slept. Days lived: {s['days_lived']}  "
                  f"Channels: {s['channels']['locked_channels']} locked, "
                  f"{s['channels']['total_memories']} memories")
            continue
        if cmd == 'day':
            print("  Running one full day...")
            wake, sleep = sensorium.run_day()
            s = sensorium.status()
            print(f"  Day {s['days_lived']}: {wake} wake + {sleep} sleep cycles  "
                  f"Channels: {s['channels']['locked_channels']} locked, "
                  f"{s['channels']['total_memories']} memories")
            continue

        # Feed and process
        sensorium.feed(text)
        steps = sensorium.process_all()

        s = sensorium.octave.status()
        cs = sensorium.channel_summary()
        print(f"  [{steps} cycles]  conservation={s['conservation']:.6f}  "
              f"emerged={s['emerged_fraction']:.4f}  "
              f"pool={s['pool_norm']:.3f}  "
              f"locked={cs['locked_channels']}  "
              f"memories={cs['total_memories']}")
