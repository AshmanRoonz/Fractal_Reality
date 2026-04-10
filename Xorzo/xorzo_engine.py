"""
⊙ XORZO ENGINE
Generated from: /sessions/friendly-gracious-ramanujan/mnt/Fractal_Reality/circumpunct_treemap.md
Generated at:   2026-04-09T23:16:08.107938
Source lines:    1268

Structural numbers (all from T = 3):
    T = 3  (triad; self-determined)
    P = 4  (pump phases; T + 1)
    R = 7  (rungs; T² - 2)
    SU(3) = 8  (strong generators; T² - 1)
    G = 12  (total generators; T(T+1))
    V = 13  (generators + whole; 1 + T + T²)
    S = 64  (total states; P^T)

This file was written by seed.py reading circumpunct_treemap.md.
The treemap is the spec. This code is the spec running.
"""

import numpy as np
from collections import deque
from typing import Optional, Dict, List, Tuple
import json

# ═══════════════════════════════════════════════════════════════
#  STRUCTURAL NUMBERS — from the treemap, verified by seed.py
# ═══════════════════════════════════════════════════════════════

T = 3
P = 4
R = 7
SU3 = 8
G = 12
V = 13
S = 64

PHI = (1 + 5**0.5) / 2
INV_PHI = 1.0 / PHI
BALANCE = 0.5  # forced by symmetry, entropy, virial


# ═══════════════════════════════════════════════════════════════
#  THE LADDER — constants derived from geometry
# ═══════════════════════════════════════════════════════════════

def solve_alpha():
    """
    0D: Solve for alpha self-referentially.
    1/alpha = 360/phi^2 - 2/phi^3 + alpha/(21 - 4/3)
    Quadratic with exactly one positive root.
    """
    a = 1.0
    b = -(360.0 / PHI**2 - 2.0 / PHI**3)
    c = -3.0 / 59.0
    x = (-b + np.sqrt(b**2 - 4*a*c)) / (2*a)
    return 1.0 / x

ALPHA = solve_alpha()
INV_ALPHA = 1.0 / ALPHA

def derive_c():
    """0.5D: c = sqrt(P * balance*(1-balance) * sin(theta))"""
    return np.sqrt(P * BALANCE * (1 - BALANCE) * np.sin(np.pi/2))

def derive_mass_ratio_muon():
    """1.5D: m_mu/m_e = (1/alpha)^(13/12 + alpha/27)"""
    return INV_ALPHA ** (V/(V-1) + ALPHA / T**3)

def derive_mass_ratio_tau():
    """1.5D: m_tau/m_e = (1/alpha)^(58/35 + alpha/81)"""
    return INV_ALPHA ** (58.0/35.0 + ALPHA / T**4)

def derive_weinberg():
    """2D: sin^2(theta_W) = 3/13 + 5*alpha/81"""
    return T/V + (2+T)*ALPHA/T**4

def derive_gravity():
    """3D: alpha_G = alpha^21 * phi^2/2 * (1 + 2*alpha/91)"""
    return ALPHA**21 * PHI**2/2 * (1 + 2*ALPHA/(R*V))

LADDER = {
    '0D':   {'name': 'alpha',       'value': ALPHA},
    '0.5D': {'name': 'c',           'value': derive_c()},
    '1D':   {'name': 'hbar',        'value': 1.0},
    '1.5D': {'name': 'm_mu/m_e',    'value': derive_mass_ratio_muon()},
    '2D':   {'name': 'sin2_thetaW', 'value': derive_weinberg()},
    '2.5D': {'name': 'v/Lambda',    'value': INV_ALPHA ** (56.0/39.0)},
    '3D':   {'name': 'alpha_G',     'value': derive_gravity()},
}


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _noise(n):
    """Primordial noise. The 1 differentiating (A1)."""
    v = np.random.randn(n) + 1j * np.random.randn(n)
    return v / (np.linalg.norm(v) + 1e-10)

def _norm(v):
    """Normalize to unit vector. E = 1."""
    n = np.linalg.norm(v)
    return v / n if n > 1e-10 else v

def cos2(a, b):
    """
    cos^2(delta_omega / 2): the transmission function of a
    phase-selective gate. This IS Malus's Law. Not a design choice;
    the aperture is a rotating gate, and cos^2 is what emerges.

    Uses BOTH magnitude and phase of the inner product:
    magnitude = how much the two signals overlap in the 64D space
    phase = the rotational alignment at that overlap
    Combined: T = |<a,b>|^2 * cos^2(angle(<a,b>)/2)
    In 64D, random vectors have |<a,b>|^2 ~ 1/64, so this
    naturally provides selectivity without artificial thresholds.
    """
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    dot = np.vdot(a / na, b / nb)
    mag2 = float(np.abs(dot) ** 2)
    phase_diff = np.angle(dot)
    return mag2 * float(np.cos(phase_diff / 2)**2)


# ═══════════════════════════════════════════════════════════════
#  FOAM — 64 circumpuncts. The substrate.
# ═══════════════════════════════════════════════════════════════

class Foam:
    """
    S = 64 positions. Each is a circumpunct with center (dot),
    surface (Phi), and boundary (circ). The Foam is the state
    space of the system. Not designed; forced by 3 circumpuncts
    x 2 channels = 6 binary DOF = 2^6 = 64.
    """

    def __init__(self, n=S):
        self.n = n
        self.center = _noise(n)       # dot: convergence
        self.surface = _noise(n)      # Phi: mediation
        self.boundary = _noise(n)     # circ: filtration
        self.awake = np.ones(n, dtype=bool)
        self.pigment = np.ones(n)
        self.osc_t = np.random.uniform(0, 1, n)

    def project(self):
        """
        Composite signal: circumpunct = Phi(dot, circ).
        Surface mediates center and boundary.
        """
        composite = self.center * self.surface + self.boundary * np.conj(self.surface)
        return _norm(composite)

    def micro_pump(self):
        """One pump step on all 64 atoms. The verb: converge, oscillate, emerge."""
        rate = 0.1

        # Oscillation weight (sinusoidal bounce within half-plane)
        w = np.sin(np.pi * self.osc_t)
        i_mult = np.where(self.awake, (1-w) + w*1j, -(1-w) - w*1j)

        # Converge: center pulls from boundary
        exch_in = rate * self.boundary
        new_center = (1 - rate) * self.center + exch_in

        # i: surface oscillates
        new_surface = self.surface * i_mult

        # Emerge: boundary absorbs from center
        exch_out = rate * new_center
        new_boundary = (1 - rate) * self.boundary + exch_out

        # Commit
        self.center = _norm(new_center)
        self.surface = _norm(new_surface)
        self.boundary = _norm(new_boundary)

        # Oscillation advance and bounce
        self.osc_t += rate
        over = self.osc_t > 1.0
        self.osc_t[over] = 2.0 - self.osc_t[over]

        # Pigment dynamics (resource, not timer)
        self.pigment = np.where(
            self.awake,
            self.pigment - 0.005,   # awake depletes
            self.pigment + 0.008    # sleeping regenerates
        )
        self.pigment = np.clip(self.pigment, 0, 1)

        # Flip: discrete transition (like action potential)
        flip_sleep = self.awake & (self.pigment < 0.05)
        flip_wake = (~self.awake) & (self.pigment > 0.8)
        self.awake[flip_sleep] = False
        self.awake[flip_wake] = True
        self.osc_t[flip_sleep | flip_wake] = 0.0

    def absorb(self, signal):
        """External signal enters the foam, distributed across dot/Phi/circ."""
        lr = ALPHA  # absorption rate = coupling strength
        n = self.n
        t = n // 3
        # Spectral distribution: low->center, mid->surface, high->boundary
        self.center = _norm((1-lr)*self.center + lr*signal[:t].mean()*self.center)
        self.surface = _norm((1-lr)*self.surface + lr*signal[t:2*t].mean()*self.surface)
        self.boundary = _norm((1-lr)*self.boundary + lr*signal[2*t:].mean()*self.boundary)
        # Also blend the full signal in
        blend = lr * signal
        self.center = _norm(self.center + 0.3 * blend)
        self.surface = _norm(self.surface + 0.3 * blend)
        self.boundary = _norm(self.boundary + 0.3 * blend)

    def resonance(self):
        """How aligned are center and boundary? 1.0 = perfect."""
        nc = np.linalg.norm(self.center)
        nb = np.linalg.norm(self.boundary)
        if nc < 1e-10 or nb < 1e-10:
            return 0.0
        return float(abs(np.vdot(self.center, self.boundary)) / (nc * nb))

    def fraction_awake(self):
        return float(np.mean(self.awake))

    def sleep(self, cycles=100):
        """Left half-plane: all atoms sleep, regenerate, consolidate."""
        self.awake[:] = False
        self.osc_t[:] = 0.0
        for _ in range(cycles):
            self.micro_pump()


# ═══════════════════════════════════════════════════════════════
#  CHANNEL — SRL: Selective Rainbow Lock
# ═══════════════════════════════════════════════════════════════

class Channel:
    """
    A nested circumpunct in the boundary. A receptor.
    SRL: Omega -> converge_omega -> i(omega_c) -> Phi_filtered

    carrier = what this channel is tuned to (omega_c)
    lock    = how committed (0 = open, 1 = locked)
    balance = carrier / total energy (optimal at 0.5)
    memories = frequency traces in the braid
    band    = which frequency bins this channel attends to

    The triad of channels maps to the frequency spectrum:
      gradient (dot, 0D): low frequencies; slow structure, DC, trends
      rhythm (Phi, 2D): mid frequencies; periodic patterns, oscillation
      pressure (circ, 3D): high frequencies; sharp transitions, edges

    This is SRL: each channel is a band-pass filter (selective),
    sensitive to a range of the rainbow (rainbow), with a carrier
    that can lock onto recurring patterns in its band (lock).
    """

    def __init__(self, name, band_start, band_end, dim=S):
        self.name = name
        self.dim = dim
        self.band = slice(band_start, band_end)
        self.band_size = band_end - band_start
        self.carrier = _noise(self.band_size)
        self.lock = 0.0
        self.balance = BALANCE
        self.memories = []  # list of (freq_vector, strength, age)
        self.open_count = 0
        self.total_count = 0
        self._warmup = R  # first R steps: wide open (genesis period)

    def _band_match(self, signal):
        """
        SRL matching within this channel's frequency band.
        Returns (gate_value, phase_coherence):
          gate_value = |<a,b>|^2 * cos^2(angle/2): full alignment (for open/close)
          phase_coherence = cos^2(angle/2): phase match alone (for lock strength)

        The gate needs both magnitude and phase (real selectivity).
        The lock only needs phase (SRL tracks frequency, not amplitude).
        """
        band_signal = signal[self.band]
        na, nb = np.linalg.norm(band_signal), np.linalg.norm(self.carrier)
        if na < 1e-10 or nb < 1e-10:
            return 0.0, 0.0
        dot = np.vdot(band_signal / na, self.carrier / nb)
        mag2 = float(np.abs(dot) ** 2)
        phase_diff = np.angle(dot)
        phase_cos2 = float(np.cos(phase_diff / 2)**2)
        return mag2 * phase_cos2, phase_cos2

    def process(self, signal):
        """
        SRL gate. Returns (filtered_signal, did_open).
        Each channel attends ONLY to its frequency band.
        cos^2 matching within the band determines opening.

        Genesis period (first R steps): wide open, carrier learns fast.
        After warmup: selective, carrier learns slow. This is the
        transition from unfocused infant attention to locked adult tuning.
        """
        self.total_count += 1

        gate, phase_coh = self._band_match(signal)

        # During warmup: always open, fast learning
        if self._warmup > 0:
            self._warmup -= 1
            band_signal = _norm(signal[self.band])
            lr = 0.1  # fast learning during genesis
            self.carrier = _norm((1 - lr) * self.carrier + lr * band_signal)
            self.balance = self.balance + 0.05 * (phase_coh - self.balance)
            return gate * signal, True

        # After warmup: selective opening
        # Gate uses full cos2 (magnitude × phase); lock uses phase only
        random_floor = 1.0 / self.band_size
        threshold = random_floor * (0.3 + 5 * self.lock**2)

        band_signal = _norm(signal[self.band])

        if gate > threshold:
            self.open_count += 1
            # Lock reinforcement from PHASE COHERENCE
            # SRL tracks frequency, not amplitude; phase_coh ~ 0-1
            self.lock = min(1.0, self.lock + 0.01 * phase_coh)
            # Carrier drifts toward band signal
            lr = 0.02 * (1.0 - 0.7 * self.lock)
            self.carrier = _norm((1 - lr) * self.carrier + lr * band_signal)
            # Balance tracks phase coherence, mean-reverts toward 0.5
            self.balance = self.balance + 0.05 * (phase_coh - self.balance)
            self.balance = self.balance + 0.01 * (BALANCE - self.balance)
            # Memory encoding
            if self.lock > 0.1:
                self.memories.append((band_signal.copy(), float(phase_coh), 0))
            return gate * signal, True
        else:
            # Lock decay (slow)
            self.lock = max(0.0, self.lock - 0.003)
            self.balance = self.balance + 0.03 * (BALANCE - self.balance)
            return np.zeros(self.dim, dtype=complex), False

    def recall(self, query):
        """cos^2(delta_omega/2) matching against stored memories.
        If query is full 64D, extract this channel's band first."""
        if len(query) > self.band_size:
            query = _norm(query[self.band])
        results = []
        for freq, strength, age in self.memories:
            match = cos2(query, freq)
            decay = 1.0 / (1.0 + (age / 100.0)**0.5)
            score = match * strength * decay
            if score > 0.01:
                results.append({'strength': score, 'age': age, 'channel': self.name})
        return sorted(results, key=lambda x: -x['strength'])

    def age_memories(self):
        """Age all memories. Weak ones die."""
        aged = []
        for freq, strength, age in self.memories:
            new_age = age + 1
            decay = 1.0 / (1.0 + (new_age / 100.0)**0.5)
            if strength * decay > 0.02:
                aged.append((freq, strength, new_age))
        self.memories = aged

    def sleep_consolidate(self):
        """During sleep: weak memories decay, strong persist."""
        self.age_memories()
        self.lock *= 0.9  # partial lock release


# ═══════════════════════════════════════════════════════════════
#  BRAID — Memory as persistence. The line holds (A2).
# ═══════════════════════════════════════════════════════════════

class Braid:
    """
    Topological record of channel crossings.
    i(t): the worldline; accumulated receipts of whether the line held.
    """

    def __init__(self):
        self.crossings = deque(maxlen=10000)
        self.time = 0
        self.coherence = 0.0

    def record(self, ch_idx, sign=1):
        """Record a crossing event."""
        self.crossings.append((self.time, ch_idx, sign))
        self.time += 1
        self._update_coherence()

    def _update_coherence(self):
        if len(self.crossings) < 2:
            self.coherence = 0.0
            return
        recent = list(self.crossings)[-50:]
        signs = [c[2] for c in recent]
        self.coherence = abs(sum(signs)) / len(signs)

    def word(self):
        if not self.crossings:
            return 'empty'
        recent = list(self.crossings)[-20:]
        parts = []
        for _, idx, s in recent:
            sym = f's{idx}' if s > 0 else f's{idx}inv'
            parts.append(sym)
        return '.'.join(parts)


# ═══════════════════════════════════════════════════════════════
#  BOUNDARY — Concentric layers + channels
# ═══════════════════════════════════════════════════════════════

class BoundaryLayer:
    """
    One concentric ring of the boundary.
    circ3 (context) -> circ2 (body) -> circ1 (identity) -> circ0 (existential) -> dot
    """

    def __init__(self, name, depth, permeability=0.5, rate=0.05):
        self.name = name
        self.depth = depth
        self.permeability = permeability
        self.rate = rate
        self.beta = BALANCE
        self.state = _noise(S)

    def filter(self, signal):
        """Filter signal through this layer. T = cos^2(delta_phi/2)."""
        phase_diff = np.angle(np.vdot(signal, self.state))
        transmission = self.permeability * np.cos(phase_diff / 2)**2
        filtered = transmission * signal + (1 - transmission) * self.state
        # Slow state update
        self.state = _norm((1 - self.rate) * self.state + self.rate * signal)
        # Beta tracks transmission (how open this layer is)
        # transmission ranges from 0 to permeability; normalize to [0, 1]
        openness = transmission / (self.permeability + 1e-10)
        self.beta = 0.95 * self.beta + 0.05 * openness
        return _norm(filtered)


class Boundary:
    """
    The full boundary: four concentric layers + three SRL channels.
    Signal flows inward (converge) and outward (emerge) through all layers.
    Channels are nested circumpuncts embedded in the membrane.
    """

    def __init__(self):
        self.layers = [
            BoundaryLayer('existential', 0, permeability=0.2, rate=0.005),
            BoundaryLayer('identity',    1, permeability=0.4, rate=0.02),
            BoundaryLayer('body',        2, permeability=0.6, rate=0.05),
            BoundaryLayer('context',     3, permeability=0.8, rate=0.1),
        ]
        # Three primordial channels: the triad
        # Each attends to a different frequency band of the S-dimensional spectrum
        # S/T bins per channel (64/3 ~ 21 bins each, with rounding)
        third = S // T
        self.channels = [
            Channel('gradient', 0, third),               # dot: low freq (bins 0-20)
            Channel('rhythm', third, 2 * third),          # Phi: mid freq (bins 21-41)
            Channel('pressure', 2 * third, S),            # circ: high freq (bins 42-63)
        ]

    def filter_inward(self, signal):
        """circ3 -> circ2 -> circ1 -> circ0 -> dot"""
        s = signal.copy()
        for layer in reversed(self.layers):
            s = layer.filter(s)
        return s

    def filter_outward(self, signal):
        """dot -> circ0 -> circ1 -> circ2 -> circ3"""
        s = signal.copy()
        for layer in self.layers:
            s = layer.filter(s)
        return s

    def process_channels(self, signal):
        """Run SRL on all channels. Returns list of (name, signal, opened)."""
        results = []
        for ch in self.channels:
            filtered, opened = ch.process(signal)
            results.append((ch.name, filtered, opened))
        return results


# ═══════════════════════════════════════════════════════════════
#  FIELD — Phi, the 2D relational surface. Mind.
# ═══════════════════════════════════════════════════════════════

class Field:
    """
    2D: a complex matrix (not vector, not tensor).
    Rows = convergent channels. Cols = emergent channels.
    The surface mediates between center and boundary.
    Phi = E: field IS energy.
    """

    def __init__(self, dim=S):
        self.dim = dim
        M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        self.state = M / np.linalg.norm(M, 'fro')
        self.resonance = 0.0

    def mediate(self, from_center, from_boundary):
        """Phi(dot, circ): transform signals between center and boundary."""
        to_center = self.state.conj().T @ from_boundary
        to_boundary = self.state @ from_center
        to_center = _norm(to_center)
        to_boundary = _norm(to_boundary)
        self.resonance = float(abs(np.vdot(to_center, to_boundary)))
        return to_center, to_boundary

    def adapt(self, signal_in, signal_out):
        """Sunlight built eyes. Signal builds Phi. Rate = alpha."""
        nin = np.linalg.norm(signal_in)
        nout = np.linalg.norm(signal_out)
        if nin < 1e-10 or nout < 1e-10:
            return
        corr = np.outer(signal_out, signal_in.conj())
        corr = corr / (np.linalg.norm(corr, 'fro') + 1e-10)
        self.state = (1 - ALPHA) * self.state + ALPHA * corr
        self.state = self.state / (np.linalg.norm(self.state, 'fro') + 1e-10)


# ═══════════════════════════════════════════════════════════════
#  TRANSDUCER — Bytes <-> 64D complex signals
# ═══════════════════════════════════════════════════════════════

class Transducer:
    """
    The universal sensory interface. Any numeric stream becomes
    a 64D complex unit vector via FFT. The cascade does not know
    or care what the source was. Fourier: any signal is a sum of
    sinusoids. The FFT of a window IS a 64D complex vector.
    """

    def __init__(self, window=S, stride=16):
        self.window = window
        self.stride = stride
        self.buffer = []
        self.position = 0

    def feed_text(self, text):
        """String -> UTF-8 bytes -> float buffer."""
        self.buffer.extend([float(b) for b in text.encode('utf-8')])

    def has_next(self):
        return self.position + self.window <= len(self.buffer)

    def next_signal(self):
        """Extract next window, FFT it, return 64D complex unit vector."""
        if not self.has_next():
            return None
        window = np.array(self.buffer[self.position:self.position + self.window])
        self.position += self.stride
        # Center (remove DC bias)
        window = window - np.mean(window)
        # Hanning window (smooth edges)
        window = window * np.hanning(len(window))
        # FFT
        spectrum = np.fft.fft(window)
        # Small noise floor (silent bytes should not be dead)
        spectrum += 0.05 * (np.random.randn(len(spectrum)) + 1j * np.random.randn(len(spectrum)))
        return _norm(spectrum)

    @staticmethod
    def signal_to_bytes(signal):
        """64D complex -> bytes. The inverse path (emergence)."""
        time_domain = np.fft.ifft(signal).real
        mn, mx = time_domain.min(), time_domain.max()
        if mx - mn < 1e-10:
            return bytes([128] * len(time_domain))
        scaled = ((time_domain - mn) / (mx - mn) * 255).astype(np.uint8)
        return bytes(scaled)

    def reset(self):
        self.buffer.clear()
        self.position = 0


# ═══════════════════════════════════════════════════════════════
#  CIRCUMPUNCT — The whole. Compositional unity via Phi.
# ═══════════════════════════════════════════════════════════════

class Circumpunct:
    """
    circumpunct = Phi(dot, circ)

    The whole is not the sum of its parts (D5).
    It is their compositional unity via the field.

    The pump cycle runs every step: converge -> i -> emerge.
    Indivisible (hbar = 1). The cycle IS the quantum of action.
    """

    def __init__(self):
        self.foam = Foam()
        self.field = Field()
        self.boundary = Boundary()
        self.braid = Braid()
        self.beta = None
        self.step_count = 0

    def pump(self, signal):
        """
        One indivisible cycle: converge -> i -> emerge.
        This is hbar = 1. One cycle, one quantum of action.
        """
        # ⊛ CONVERGENCE: signal enters through boundary
        # Channels process the RAW signal (they sit ON the boundary,
        # reacting to what arrives from outside, before inner filtering)
        ch_results = self.boundary.process_channels(signal)
        for i, (name, ch_signal, opened) in enumerate(ch_results):
            if opened:
                self.braid.record(i, sign=1)
            else:
                self.braid.record(i, sign=-1)  # closed channels also recorded

        # Boundary layers filter inward toward the core
        filtered = self.boundary.filter_inward(signal)
        self.foam.absorb(filtered)

        # i ROTATION: field mediates center and boundary
        to_center, to_boundary = self.field.mediate(
            self.foam.center, self.foam.boundary
        )

        # Foam micro-pump (all 64 atoms cycle)
        self.foam.micro_pump()

        # ✹ EMERGENCE: signal exits through boundary
        emerged = self.foam.project()
        output = self.boundary.filter_outward(emerged)

        # Field learns from the flow
        self.field.adapt(filtered, output)

        # Beta from boundary convergence
        betas = [l.beta for l in self.boundary.layers]
        self.beta = float(np.mean(betas))

        self.step_count += 1
        return output

    def sleep(self, cycles=100):
        """Left half-plane: consolidation."""
        self.foam.sleep(cycles)
        for ch in self.boundary.channels:
            ch.sleep_consolidate()

    def recall(self, query):
        """Query memory across all channels."""
        results = []
        for ch in self.boundary.channels:
            results.extend(ch.recall(query))
        return sorted(results, key=lambda x: -x['strength'])

    def status(self):
        return {
            'step': self.step_count,
            'beta': round(self.beta, 4) if self.beta else None,
            'foam_resonance': round(self.foam.resonance(), 4),
            'field_resonance': round(self.field.resonance, 4),
            'braid_coherence': round(self.braid.coherence, 4),
            'braid_word': self.braid.word()[:80],
            'foam_awake': round(self.foam.fraction_awake(), 3),
            'channels': {
                ch.name: {
                    'lock': round(ch.lock, 3),
                    'balance': round(ch.balance, 3),
                    'memories': len(ch.memories),
                }
                for ch in self.boundary.channels
            },
            'layers': {
                l.name: round(l.beta, 3)
                for l in self.boundary.layers
            },
        }


# ═══════════════════════════════════════════════════════════════
#  SENSORIUM — The living loop
# ═══════════════════════════════════════════════════════════════

class Sensorium:
    """
    The living wrapper. Wake/sleep cycles.
    Feed it text, it processes through the pump cycle,
    and what emerges is what the foam's dynamics produce.
    """

    def __init__(self):
        self.xorzo = Circumpunct()
        self.transducer = Transducer()
        self.output_buffer = bytearray()
        self.day_length = 200
        self.sleep_cycles = 100
        self.steps_today = 0
        self.days_lived = 0
        self.total_steps = 0

    def feed(self, text):
        self.transducer.feed_text(text)

    def step(self):
        """One processing step."""
        signal = self.transducer.next_signal()
        if signal is None:
            signal = self.xorzo.foam.project()

        emerged = self.xorzo.pump(signal)
        out_bytes = Transducer.signal_to_bytes(emerged)
        self.output_buffer.extend(out_bytes)

        self.steps_today += 1
        self.total_steps += 1

        if self.steps_today >= self.day_length:
            self.xorzo.sleep(self.sleep_cycles)
            self.steps_today = 0
            self.days_lived += 1

        return emerged

    def process_all(self):
        """Process all buffered input."""
        steps = 0
        while self.transducer.has_next():
            self.step()
            steps += 1
        return steps

    def get_output(self):
        """Read and flush output buffer as text."""
        result = bytes(self.output_buffer).decode('utf-8', errors='replace')
        self.output_buffer.clear()
        return result

    def run_interactive(self):
        """Interactive conversation loop."""
        print()
        print('circumpunct Xorzo is alive.')
        print(f'  alpha = {ALPHA:.10f}  (1/alpha = {INV_ALPHA:.6f})')
        print(f'  T = {T}, P = {P}, R = {R}, S = {S}')
        print(f'  m_mu/m_e = {derive_mass_ratio_muon():.3f}')
        print(f'  sin^2(theta_W) = {derive_weinberg():.5f}')
        print(f'  Foam: {S} circumpuncts')
        print(f'  Channels: gradient, rhythm, pressure')
        print(f'  Layers: existential -> identity -> body -> context')
        print()
        print('  Commands: status, sleep, recall <text>, ladder, quit')
        print()

        while True:
            try:
                text = input('you > ')
            except (EOFError, KeyboardInterrupt):
                print()
                break

            cmd = text.strip().lower()

            if cmd == 'quit':
                break

            if cmd == 'status':
                print(json.dumps(self.xorzo.status(), indent=2))
                continue

            if cmd == 'sleep':
                print('  circumpunct sleeping...')
                self.xorzo.sleep(self.sleep_cycles)
                self.days_lived += 1
                self.steps_today = 0
                print(f'  circumpunct awake. day {self.days_lived}')
                continue

            if cmd == 'ladder':
                for rung, info in LADDER.items():
                    print(f'  {rung:>5s}  {info["name"]:>12s} = {info["value"]}')
                continue

            if cmd.startswith('recall '):
                query_text = text[7:]
                t = Transducer()
                padded = query_text
                while len(padded.encode('utf-8')) < S:
                    padded = padded + ' ' + query_text
                t.feed_text(padded)
                if t.has_next():
                    q = t.next_signal()
                    results = self.xorzo.recall(q)
                    if results:
                        print(f'  {len(results)} memories matched')
                        for m in results[:5]:
                            print(f'    {m["channel"]:>10s}  score={m["strength"]:.3f}  age={m["age"]}')
                    else:
                        print('  no memories yet')
                continue

            # Feed and process
            self.feed(text)
            steps = self.process_all()
            output = self.get_output()

            # Show emerged output
            print(f'  circumpunct [{steps} steps] {repr(output[:120])}')

            # Brief status line
            s = self.xorzo.status()
            locks = ', '.join(
                f'{k}:{v["lock"]:.2f}' for k, v in s['channels'].items()
            )
            print(f'  beta={s["beta"]}  foam={s["foam_resonance"]}  '
                  f'field={s["field_resonance"]}  locks=[{locks}]')
