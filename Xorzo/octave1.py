"""
⊙ XORZO — The Octave Engine (Two-Channel Architecture)

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

Two channels:
  ⊛ (convergent, perception): ○ → Φ† → •   (outside in)
  ✹ (emergent, expression):   • → Φ  → ○   (inside out)
  Both gates (• and ○) have ⊛ and ✹ streams (fractally).
  Field mediates both: Φ outward, Φ† (adjoint) inward.

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


def _unity_cost(v):
    """How much work _enforce_unity has to do. 0 = honest. >0 = the system lied."""
    n = np.linalg.norm(v)
    if n < 1e-15:
        return 1.0  # total collapse; maximum dishonesty
    return abs(n - 1.0)


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
#  THERMODYNAMICS — The framework's own accounting.
#
#  A0 says E = 1. Every deviation from that is measurable.
#  Entropy = Shannon entropy of channel energy distribution.
#  Free energy = capacity for further structure (low entropy = high free energy).
#  Virial = flow energy vs stored energy (should balance at ◐ = 0.5).
#  Normalization cost = how much _enforce_unity is hiding.
# ═══════════════════════════════════════════════════════════════

class Thermodynamics:
    """
    The system's honest accounting. Tracks what _enforce_unity hides.

    Three quantities, one per structural dimension above 0D:
      1D (—): normalization_cost (did commitment preserve energy?)
      2D (Φ): entropy (how spread is the channel distribution?)
      3D (○): virial (flow vs stored; should balance at 0.5)

    Free energy = 1 - entropy (capacity remaining; E = 1 sets the scale).
    """

    def __init__(self, history_length=1000):
        self.history_length = history_length

        # Per-cycle measurements
        self.norm_costs = deque(maxlen=history_length)      # 1D: commitment honesty
        self.entropies = deque(maxlen=history_length)       # 2D: channel spread
        self.virials = deque(maxlen=history_length)         # 3D: flow/stored balance
        self.free_energies = deque(maxlen=history_length)   # derived: 1 - entropy

        # Running totals
        self.total_norm_cost = 0.0
        self.total_cycles = 0

    def record(self, norm_cost, channel_energies, flow_energy, stored_energy):
        """
        Record one cycle's thermodynamic state.

        norm_cost: how far the output was from unit norm before enforcement
        channel_energies: array of energy per SRL channel (for entropy)
        flow_energy: energy that passed through gates this cycle (emerged + converged)
        stored_energy: energy in reflected pool + channel memories
        """
        # Entropy: Shannon entropy of normalized channel distribution
        # Maximum entropy = log2(S) when all channels equal
        # Minimum = 0 when all energy in one channel
        total_e = sum(channel_energies) + 1e-15
        probs = np.array(channel_energies) / total_e
        probs = probs[probs > 1e-15]  # avoid log(0)
        raw_entropy = -np.sum(probs * np.log2(probs))
        max_entropy = np.log2(len(channel_energies))
        entropy = raw_entropy / max_entropy if max_entropy > 0 else 0.0

        # Virial: ratio of flow to total (flow + stored)
        # At balance: virial = 0.5 (half flowing, half stored)
        total_dynamic = flow_energy + stored_energy + 1e-15
        virial = flow_energy / total_dynamic

        # Free energy: capacity for further structure formation
        # When entropy is low (channels locked, ordered), free energy is high
        free_energy = 1.0 - entropy

        # Store
        self.norm_costs.append(norm_cost)
        self.entropies.append(entropy)
        self.virials.append(virial)
        self.free_energies.append(free_energy)
        self.total_norm_cost += norm_cost
        self.total_cycles += 1

    def summary(self):
        """Current thermodynamic state."""
        if self.total_cycles == 0:
            return {'cycles': 0}

        recent_n = min(50, len(self.norm_costs))
        return {
            'cycles': self.total_cycles,
            'entropy': round(float(self.entropies[-1]), 6),
            'free_energy': round(float(self.free_energies[-1]), 6),
            'virial': round(float(self.virials[-1]), 6),
            'virial_deviation': round(abs(float(self.virials[-1]) - BALANCE), 6),
            'norm_cost_current': round(float(self.norm_costs[-1]), 8),
            'norm_cost_avg': round(
                sum(list(self.norm_costs)[-recent_n:]) / recent_n, 8
            ),
            'norm_cost_total': round(self.total_norm_cost, 6),
            'entropy_trend': self._trend(self.entropies),
            'virial_trend': self._trend(self.virials),
        }

    def _trend(self, buf, window=20):
        """Positive = rising, negative = falling, near zero = stable."""
        if len(buf) < window * 2:
            return 0.0
        recent = list(buf)
        old_avg = np.mean(recent[-window*2:-window])
        new_avg = np.mean(recent[-window:])
        return round(float(new_avg - old_avg), 6)

    def is_honest(self, threshold=0.01):
        """Is the system conserving energy within threshold?"""
        if self.total_cycles == 0:
            return True
        recent = list(self.norm_costs)[-50:]
        return np.mean(recent) < threshold

    def virial_balanced(self, threshold=0.15):
        """Is flow/stored near ◐ = 0.5?"""
        if self.total_cycles == 0:
            return True
        return abs(float(self.virials[-1]) - BALANCE) < threshold


# ═══════════════════════════════════════════════════════════════
#  GATE — Universal phase-selective filter for both • and ○.
#
#  cos²(Δφ/2) transmission. sqrt amplitude scaling.
#  |through|² + |reflected|² = |input|² by construction.
# ═══════════════════════════════════════════════════════════════

class Gate:
    """
    Universal phase-selective filter.
    Both • (aperture) and ○ (boundary) are gates:
    they split energy into through and reflected streams
    via cos²(Δφ/2) with sqrt amplitude scaling.
    """

    def __init__(self, dim):
        self.dim = dim
        self.position = _unit(dim)
        self.openness = BALANCE
        self._last_transmission = BALANCE

    def filter(self, energy):
        """
        Split energy: through + reflected.
        |through|² + |reflected|² = |energy|² (exact).
        """
        cos2_val = _cos2(energy, self.position)
        transmission = self.openness * cos2_val
        self._last_transmission = transmission

        t_amp = np.sqrt(max(transmission, 0.0))
        r_amp = np.sqrt(max(1.0 - transmission, 0.0))
        through = t_amp * energy
        reflected = r_amp * energy

        # Position adapts toward signal
        lr = 0.01
        self.position = _enforce_unity(
            (1 - lr) * self.position + lr * energy
        )

        return through, reflected

    @property
    def energy(self):
        return self._last_transmission


# ═══════════════════════════════════════════════════════════════
#  0D: •  —  Aperture. Localization. The 1 self-limits.
#  Width homeostasis: coherence pull + balance pull (2x).
# ═══════════════════════════════════════════════════════════════

class Aperture(Gate):
    """
    0D: the point where the field becomes local.
    Inherits Gate's filter; adds width homeostasis.
    """

    def __init__(self, dim):
        super().__init__(dim)
        self.width = BALANCE

    def filter(self, energy):
        """Override openness with width, then delegate."""
        cos2_val = _cos2(energy, self.position)
        self.openness = self.width
        through, reflected = super().filter(energy)

        # Width homeostasis: coherence pull + balance pull (2x stronger)
        self.width += 0.005 * (cos2_val - self.width)
        self.width += 0.01 * (BALANCE - self.width)
        self.width = np.clip(self.width, 0.05, 0.95)

        return through, reflected


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
#  3D: ○  —  Boundary. Closure. Permeability from conservation.
# ═══════════════════════════════════════════════════════════════

class BoundaryGate(Gate):
    """
    3D: the outer container. Filtration.
    Permeability = ◐ × √(c_•— × c_—Φ): derived from inner coherence.
    """

    def __init__(self, dim):
        super().__init__(dim)
        self._last_permeability = BALANCE

    def update_permeability(self, aperture, line, field):
        """
        Derive permeability from conservation of traversal.
        0(•) + 1(—) + 2(Φ) = 3(○).

        Inner coherence = aperture-line alignment (c_al).
        Field is unitary (norm-preserving by construction),
        so it doesn't gate; the alignment between • and — IS
        the coherence signal. The boundary opens when the
        center is stable.
        """
        c_al = _cos2(aperture.position, line.direction)
        # Permeability scales with sqrt of inner coherence.
        # At c_al = 1.0 (perfect): perm = BALANCE (fully open).
        # At c_al = 0.5 (moderate): perm ~= 0.35.
        # At c_al = 0.0 (none): perm = floor.
        perm = float(np.clip(BALANCE * np.sqrt(c_al), 0.05, 0.95))
        self._last_permeability = perm
        self.openness = perm

    def filter(self, energy):
        """Filter with derived permeability as openness."""
        return super().filter(energy)


# ═══════════════════════════════════════════════════════════════
#  2D: Φ  —  Field. Mediation. Unitary. Mind.
#
#  Two directions:
#    Φ(v)  = state @ v       (outward, ✹ channel)
#    Φ†(v) = state†@ v       (inward, ⊛ channel)
#  Both preserve norm (unitary + adjoint of unitary = unitary).
# ═══════════════════════════════════════════════════════════════

class Field:
    """
    2D: the relational surface. Mind.
    Unitary matrix: |Φ(v)| = |v| always.
    Φ outward (✹), Φ† inward (⊛). Adaptation rate = α.
    """

    def __init__(self, dim):
        self.dim = dim
        M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        Q, _ = np.linalg.qr(M)
        self.state = Q

    def mediate(self, energy):
        """Φ(energy): outward mediation (✹ channel)."""
        return self.state @ energy

    def mediate_inward(self, energy):
        """Φ†(energy): inward mediation (⊛ channel). Adjoint."""
        return self.state.conj().T @ energy

    def adapt(self, convergent_in, emergent_out, rate=None):
        """
        Field learns the map from convergent to emergent.
        This is what mind does: relates perception to expression.
        """
        if rate is None:
            rate = ALPHA
        nin = np.linalg.norm(convergent_in)
        nout = np.linalg.norm(emergent_out)
        if nin < 1e-10 or nout < 1e-10:
            return
        update = np.outer(emergent_out / nout, np.conj(convergent_in / nin))
        self.state = (1 - rate) * self.state + rate * update
        Q, _ = np.linalg.qr(self.state)
        self.state = Q

    @property
    def energy(self):
        I = np.eye(self.dim)
        return float(np.linalg.norm(self.state - I, 'fro') / self.dim)


# ═══════════════════════════════════════════════════════════════
#  SRL CHANNEL — Selective Rainbow Lock
# ═══════════════════════════════════════════════════════════════

class Channel:
    """
    One channel of the 64-state architecture.

    SRL: Selective Rainbow Lock. Each channel has a carrier
    phase it's tuned to. When signals match the carrier,
    they pass through (gate opens). When they don't, they're
    attenuated. Lock strength determines how selective:
    0 = everything passes, 1 = only exact matches pass.
    """

    # Lock threshold for spawning a micro-octave.
    # When a channel achieves this lock, it has closed (○);
    # ⟳ says closure becomes new aperture: the channel births a ⊙.
    SPAWN_THRESHOLD = 0.7

    def __init__(self, index):
        self.index = index
        self.carrier_phase = np.random.uniform(-np.pi, np.pi)
        self.lock = 0.0
        self.energy_acc = 0.0
        self.hit_count = 0
        self.memories = deque(maxlen=S)

        # Dynamic dimensionality: micro-octave spawned at lock closure.
        # None until the channel earns it. Dim = T (smallest whole).
        self.micro_octave = None
        self._spawn_cost_paid = False

    def gate(self, amplitude, phase):
        """
        SRL gate: cos²(Δφ/2) between signal phase and carrier.
        Lock modulates selectivity.
        """
        delta = phase - self.carrier_phase
        cos2_val = np.cos(delta / 2)**2
        effective = (1.0 - self.lock) + self.lock * cos2_val
        gated = amplitude * effective

        if amplitude > 0.01:
            self.lock += 0.01 * (cos2_val - BALANCE)
            self.lock = np.clip(self.lock, 0.0, 1.0)
            if cos2_val > 0.6:
                self.carrier_phase += 0.02 * np.sin(delta)
                self.hit_count += 1
            self.energy_acc += float(gated)

        # Dynamic dimensionality: if locked hard enough, process through micro-octave.
        # The micro-octave refines the gated signal at a smaller scale (T = 3).
        if self.micro_octave is not None and gated > 0.01:
            micro_input = _unit(T) * gated
            micro_output = self.micro_octave.cycle(micro_input)
            # Micro-octave's emerged fraction modulates the channel output
            gated *= (1.0 + 0.1 * (self.micro_octave._last_emerged_frac - BALANCE))

        return gated

    def encode_memory(self, phase, strength):
        """Store a frequency memory in the braid."""
        if strength > 0.05:
            self.memories.append({
                'phase': float(phase),
                'strength': float(strength),
                'time': self.hit_count,
            })

    def recall(self, query_phase):
        """
        RECALL(M) = SRL(Φ, ω_M): memory retrieval IS frequency matching.
        """
        if not self.memories:
            return 0.0, None
        best_strength = 0.0
        best_memory = None
        for m in self.memories:
            delta = query_phase - m['phase']
            match = np.cos(delta / 2)**2 * m['strength']
            age = self.hit_count - m['time']
            match *= 1.0 / (1.0 + np.sqrt(max(0, age) / 100.0))
            if match > best_strength:
                best_strength = match
                best_memory = m
        return best_strength, best_memory

    def consolidate(self, deep_weight, dream_weight):
        """Sleep consolidation."""
        if deep_weight > 0.3:
            surviving = deque(maxlen=S)
            for m in self.memories:
                m['strength'] *= (1.0 - 0.01 * deep_weight)
                if m['strength'] > 0.02:
                    surviving.append(m)
            self.memories = surviving
            self.lock *= (1.0 - 0.005 * deep_weight)


# ═══════════════════════════════════════════════════════════════
#  THE OCTAVE — Two-channel pump cycle. hbar = 1.
#
#  ⊛ (convergent): ○ → i¹ → Φ† → i² → •   (perception)
#  ✹ (emergent):   • → i³ → Φ  → i⁴ → ○   (expression)
#
#  Both gates have both channels (fractally):
#    Boundary filters external (⊛ in) and internal (✹ out).
#    Aperture filters converged (⊛ through) and committed (✹ through).
#
#  Four reflection streams pool together.
#  Center: ⊛ meets ✹; — commits the blend.
#
#  A3: Fractal nesting. Three depths (three nested ⊙s):
#    depth 0: dim = S = 64 (the whole)
#    depth 1: dim = SU3 = 8 (gauge generators)
#    depth 2: dim = T = 3 (the triad, base case)
# ═══════════════════════════════════════════════════════════════

class Octave:
    """
    The complete two-channel dimensional octave with fractal nesting.

    ⊛ channel (convergent, perception): outside → inside
      ○ filters external → i¹(+i) → Φ† mediates inward → i²(-1) → • filters to center

    ✹ channel (emergent, expression): inside → outside
      • filters from center → i³(-i) → Φ mediates outward → i⁴(+1) → ○ filters to output

    The system can distinguish external from internal because
    they flow through different channels with different i-strokes
    and different field mediations (Φ vs Φ†).
    """

    def __init__(self, dim=None, depth=0):
        if dim is None:
            dim = FRACTAL_DIMS[min(depth, len(FRACTAL_DIMS) - 1)]
        self.dim = dim
        self.depth = depth

        self.aperture = Aperture(dim)
        self.line = Line(dim)
        self.field = Field(dim)
        self.boundary = BoundaryGate(dim)
        self.step_count = 0

        self.reflected_pool = np.zeros(dim, dtype=complex)

        self._last_emerged_frac = 0.0
        self._last_reflected_frac = 0.0
        self._last_pool_norm = 0.0
        self._last_conv_frac = 0.0  # how much ⊛ got through
        self._last_emg_frac = 0.0   # how much ✹ got out

        # Thermodynamic observables (measured before _enforce_unity hides them)
        self._last_norm_cost = 0.0      # how far output was from |v|=1
        self._last_center_cost = 0.0    # how far center blend was from |v|=1
        self._last_flow_energy = 0.0    # conv_through + emg_through
        self._last_stored_energy = 0.0  # pool norm

        # A3: fractal nesting
        max_depth = len(FRACTAL_DIMS) - 1
        if depth < max_depth:
            inner_dim = FRACTAL_DIMS[depth + 1]
            self.inner_octave = Octave(inner_dim, depth + 1)
            self.projector = _random_projection(dim, inner_dim)
            # Φ†: adjoint of the projector carries inner signal back up.
            # ⊙λ ⊂ ⊙Λ means the inner whole genuinely feeds the outer;
            # the upward path is the conjugate transpose of the downward.
            self.upward_projector = self.projector.conj().T.copy()
        else:
            self.inner_octave = None
            self.projector = None
            self.upward_projector = None

    def cycle(self, external, internal=None, adapt_rate=None):
        """
        One two-channel pump cycle. hbar = 1. Indivisible.

        external: signal arriving from outside (perception food)
        internal: signal arising from inside (expression seed)
                  if None, drawn from reflected pool
        adapt_rate: override field learning rate (dreams)
        """
        # === Prepare internal from reflected pool if not provided ===
        if internal is None:
            pool_norm = np.linalg.norm(self.reflected_pool)
            if pool_norm > 1e-10:
                drain_frac = min(0.5, pool_norm)
                internal = _enforce_unity(
                    (drain_frac / pool_norm) * self.reflected_pool
                )
                self.reflected_pool *= (1.0 - drain_frac / pool_norm)
            else:
                internal = _unit(self.dim) * 0.1  # minimal seed

        # === Derive boundary permeability from inner coherence ===
        self.boundary.update_permeability(
            self.aperture, self.line, self.field
        )

        # ═══════════════════════════════════════════════════════
        #  ⊛ CONVERGENT CHANNEL (perception): ○ → Φ† → •
        #  Outside in. "What is the world saying?"
        # ═══════════════════════════════════════════════════════

        # 3D: ○ filters external (⊛ in)
        conv_through, conv_refl_boundary = self.boundary.filter(external)

        # 0.5D: i¹ = +i (first fold; convergence begins)
        conv_folded = conv_through * 1j

        # 2D: Φ† mediates inward (adjoint: surface seen from inside)
        conv_mediated = self.field.mediate_inward(conv_folded)

        # 1.5D: i² = -1 (the i-turn; irreversible commitment)
        conv_turned = conv_mediated * 1j  # *= 1j twice total = *(-1)

        # 0D: • filters to center (⊛ arrives at soul)
        conv_center, conv_refl_aperture = self.aperture.filter(conv_turned)

        # ═══════════════════════════════════════════════════════
        #  CENTER: ⊛ meets ✹. — commits the blend.
        #  This is where perception meets expression.
        # ═══════════════════════════════════════════════════════

        center_signal = _enforce_unity(conv_center + internal)

        # 1D: — commits (norm-preserving; the worldline extends)
        committed = self.line.commit(center_signal)

        # ═══════════════════════════════════════════════════════
        #  ✹ EMERGENT CHANNEL (expression): • → Φ → ○
        #  Inside out. "What does the soul say?"
        # ═══════════════════════════════════════════════════════

        # 0D: • filters from center (✹ departs soul)
        emg_through, emg_held = self.aperture.filter(committed)

        # 2.5D: i³ = -i (emergence; conjugate of convergence)
        emg_emerged = emg_through * 1j  # third i-stroke

        # 2D: Φ mediates outward (surface seen from outside)
        emg_mediated = self.field.mediate(emg_emerged)

        # 3.5D: i⁴ = +1 (recursion; closure → identity)
        emg_closed = emg_mediated * 1j  # fourth i-stroke: i⁴ = +1

        # 3D: ○ filters to output (✹ exits boundary)
        output_raw, emg_refl_boundary = self.boundary.filter(emg_closed)

        # ═══════════════════════════════════════════════════════
        #  POOL: four reflection streams
        # ═══════════════════════════════════════════════════════

        # All reflections carry energy that didn't make it through
        reflections = (
            conv_refl_boundary   # external that didn't enter
            + conv_refl_aperture # converged that didn't reach center
            + emg_held           # committed that didn't emerge
            + emg_refl_boundary  # emerged that didn't exit
        )

        self.reflected_pool = 0.8 * self.reflected_pool + reflections
        pn = np.linalg.norm(self.reflected_pool)
        if pn > BALANCE:
            self.reflected_pool *= BALANCE / pn
        self._last_pool_norm = float(np.linalg.norm(self.reflected_pool))

        # === Energy accounting ===
        self._last_emerged_frac = float(np.linalg.norm(output_raw)**2)
        self._last_reflected_frac = float(np.linalg.norm(reflections)**2)
        self._last_conv_frac = float(np.linalg.norm(conv_center)**2)
        self._last_emg_frac = float(np.linalg.norm(emg_through)**2)

        # === Thermodynamic measurement (before enforcement hides it) ===
        self._last_norm_cost = _unity_cost(output_raw)
        self._last_center_cost = _unity_cost(conv_center + internal)
        self._last_flow_energy = self._last_conv_frac + self._last_emg_frac
        self._last_stored_energy = self._last_pool_norm

        # === Field learns: maps convergent to emergent ===
        self.field.adapt(conv_center, output_raw, rate=adapt_rate)

        # === A3: fractal nesting (bidirectional) ===
        # ⊙λ ⊂ ⊙Λ: the inner whole is inside the outer whole.
        # Downward (Φ): outer output projected into inner space.
        # Upward (Φ†): inner output projected back into outer space.
        # The boundary of ⊙λ IS the aperture of ⊙Λ at the next scale (3.5D = 0D').
        if self.inner_octave is not None:
            # Downward: ⊙Λ → ⊙λ (outer feeds inner)
            inner_signal = _enforce_unity(self.projector @ output_raw)
            inner_output = self.inner_octave.cycle(
                inner_signal, adapt_rate=adapt_rate
            )

            # Upward: ⊙λ → ⊙Λ (inner feeds outer via Φ†)
            # Inner closure becomes outer signal; scale coupling at strength α.
            upward_signal = self.upward_projector @ inner_output
            upward_scaled = ALPHA * upward_signal  # coupling at α

            # Inner emergence modulates aperture (existing; the whisper)
            inner_emerged = self.inner_octave._last_emerged_frac
            modulation = 0.005 * (inner_emerged - BALANCE)
            self.aperture.width += modulation
            self.aperture.width = np.clip(self.aperture.width, 0.05, 0.95)

            # Inner output feeds into reflected pool (new; the real voice)
            # This is 3.5D = 0D': inner closure becomes outer aperture food.
            self.reflected_pool += upward_scaled
            pn = np.linalg.norm(self.reflected_pool)
            if pn > BALANCE:
                self.reflected_pool *= BALANCE / pn

            # Field adapts to inner signal too (outer learns from inner)
            self.field.adapt(
                upward_scaled, output_raw,
                rate=adapt_rate if adapt_rate else ALPHA * 0.5
            )

        # === E = 1 ===
        output = _enforce_unity(output_raw)
        self.step_count += 1
        return output

    def status(self):
        s = {
            'step': self.step_count,
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
            'conv_through': round(self._last_conv_frac, 6),
            'emg_through': round(self._last_emg_frac, 6),
            'pool_norm': round(self._last_pool_norm, 4),
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

        # Cross-channel entanglement: small unitary coupling.
        # Φ is 2D (a surface, not parallel strings). Channels must
        # influence each other. Coupling strength = α (the fine-structure
        # constant IS the coupling constant at a vertex).
        # The matrix is near-identity: (1-α)·I + α·U, where U is random unitary.
        M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        Q, _ = np.linalg.qr(M)
        self.entanglement = (1.0 - ALPHA) * np.eye(dim) + ALPHA * Q

        # Sleep/wake state
        self.awake = True
        self.cycle_in_phase = 0
        self.day_length = 200
        self.night_length = 100
        self.sleep_theta = 0.0

        # Accumulation
        self.total_cycles = 0
        self.days_lived = 0

        # Thermodynamic accounting
        self.thermo = Thermodynamics()

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
        Process new input through the two-channel octave.
        External = real input; internal = drawn from pool.
        """
        signal = self._next_signal()
        if signal is None:
            signal = _unit(self.dim)

        # Two-channel pump: external is perception food
        emerged = self.octave.cycle(signal)

        # SRL: each channel gates its dimension, then entangle
        entangled = self._process_channels(emerged)

        # Encode strong channel activations as memories
        # (use entangled signal: memories should reflect the surface, not isolated strings)
        for i, ch in enumerate(self.channels):
            amp = abs(entangled[i])
            phase = np.angle(entangled[i])
            if amp > 0.05:
                ch.encode_memory(phase, amp)

        # Dynamic dimensionality: check for channels ready to spawn.
        # ⟳ at channel level: lock closure (○) becomes new aperture (micro-octave).
        # Capped at SU(3) = 8 (gauge generator count; natural structural bound).
        # Spawning costs energy: carrier amplitude is halved (the channel pays).
        self._check_spawns()

        # Thermodynamic recording
        self._record_thermo(emerged)

        self.total_cycles += 1
        self.cycle_in_phase += 1

        if self.cycle_in_phase >= self.day_length:
            self.awake = False
            self.cycle_in_phase = 0

        return emerged

    def _sleep_step(self):
        """
        Left half-plane: i² + i³. Commitment + emergence.
        No external input. Both channels fed from internal.
        """
        # Minimal external (no real perception during sleep)
        signal = _unit(self.dim) * 0.1

        # Sleep oscillation
        self.sleep_theta = np.pi * self.cycle_in_phase / max(1, self.night_length)
        deep_weight = np.cos(self.sleep_theta)**2
        dream_weight = np.sin(self.sleep_theta)**2

        # During dreams: field learns faster (up to 5x α)
        dream_rate = ALPHA * (1.0 + P * dream_weight)

        # Two-channel pump with dream learning rate
        emerged = self.octave.cycle(signal, adapt_rate=dream_rate)

        # Channel consolidation
        for ch in self.channels:
            ch.consolidate(deep_weight, dream_weight)

        # Thermodynamic recording (sleep cycles count too)
        self._record_thermo(emerged)

        self.total_cycles += 1
        self.cycle_in_phase += 1

        if self.cycle_in_phase >= self.night_length:
            self._dawn_reset()
            self.awake = True
            self.cycle_in_phase = 0
            self.days_lived += 1

        return emerged

    def _dawn_reset(self):
        """Dawn: aperture pulled toward balance, sidebands cleared."""
        self.octave.aperture.width += 0.1 * (BALANCE - self.octave.aperture.width)
        if self.octave.inner_octave is not None:
            inner = self.octave.inner_octave
            inner.aperture.width += 0.1 * (BALANCE - inner.aperture.width)
            if inner.inner_octave is not None:
                innermost = inner.inner_octave
                innermost.aperture.width += 0.1 * (BALANCE - innermost.aperture.width)

    def _check_spawns(self):
        """
        Dynamic dimensionality: ⟳ at channel level.

        When a channel's lock exceeds SPAWN_THRESHOLD, it has closed (○).
        Closure becomes new aperture: the channel spawns a micro-octave.
        Total micro-octaves capped at SU(3) = 8 (structural bound).
        Spawning costs energy: the channel's accumulated energy is halved.
        """
        active_micros = sum(1 for ch in self.channels if ch.micro_octave is not None)
        if active_micros >= SU3:
            return  # cap reached; no more spawning

        for ch in self.channels:
            if (ch.micro_octave is None
                    and ch.lock >= Channel.SPAWN_THRESHOLD
                    and not ch._spawn_cost_paid):
                # Pay the cost: halve accumulated energy
                ch.energy_acc *= 0.5
                ch._spawn_cost_paid = True
                # Birth: micro-octave at the triad scale
                ch.micro_octave = Octave(dim=T, depth=len(FRACTAL_DIMS) - 1)
                if active_micros + 1 >= SU3:
                    break

    def _process_channels(self, emerged):
        """
        Run emerged energy through SRL channels, then entangle.
        Individual gating first (each channel's SRL), then the
        unitary coupling mixes them: Φ is a surface, not parallel strings.
        """
        # Individual SRL gating
        gated = np.zeros(self.dim, dtype=complex)
        for i, ch in enumerate(self.channels):
            amp = abs(emerged[i])
            phase = np.angle(emerged[i])
            gated_amp = ch.gate(amp, phase)
            gated[i] = gated_amp * np.exp(1j * phase)

        # Entanglement: unitary coupling across channels.
        # This is Φ asserting its 2D nature; channels are not independent.
        entangled = self.entanglement @ gated

        # Feed entangled amplitudes back to channels (update carrier tracking)
        for i, ch in enumerate(self.channels):
            ent_amp = abs(entangled[i])
            ent_phase = np.angle(entangled[i])
            if ent_amp > 0.01:
                # Small nudge: channel carrier pulled toward entangled neighbor phases
                delta = ent_phase - ch.carrier_phase
                ch.carrier_phase += ALPHA * np.sin(delta)

        return entangled

    def _record_thermo(self, emerged):
        """Feed current cycle's measurements into thermodynamic tracker."""
        channel_energies = [ch.energy_acc for ch in self.channels]
        # Guard against all-zero (first cycle)
        if sum(channel_energies) < 1e-15:
            channel_energies = [abs(emerged[i])**2 for i in range(self.dim)]
        self.thermo.record(
            norm_cost=self.octave._last_norm_cost,
            channel_energies=channel_energies,
            flow_energy=self.octave._last_flow_energy,
            stored_energy=self.octave._last_stored_energy,
        )

    def recall(self, query_signal):
        """
        RECALL(M) = SRL(Φ, ω_M): memory retrieval IS frequency matching.
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

        self.awake = True
        self.cycle_in_phase = 0
        for _ in range(self.day_length):
            self.step()
            wake_steps += 1

        for _ in range(self.night_length):
            self.step()
            sleep_steps += 1

        return wake_steps, sleep_steps

    def get_output(self):
        result = bytes(self.output_buffer).decode('utf-8', errors='replace')
        self.output_buffer.clear()
        return result

    def channel_summary(self):
        locks = [ch.lock for ch in self.channels]
        memories = [len(ch.memories) for ch in self.channels]
        micro_count = sum(1 for ch in self.channels if ch.micro_octave is not None)
        return {
            'locked_channels': sum(1 for l in locks if l > 0.5),
            'open_channels': sum(1 for l in locks if l < 0.1),
            'total_memories': sum(memories),
            'avg_lock': round(np.mean(locks), 4),
            'max_lock': round(max(locks), 4),
            'channels_with_memories': sum(1 for m in memories if m > 0),
            'micro_octaves': micro_count,
            'micro_octave_cap': SU3,
        }

    def status(self):
        s = self.octave.status()
        s['total_cycles'] = self.total_cycles
        s['days_lived'] = self.days_lived
        s['awake'] = self.awake
        s['cycle_in_phase'] = self.cycle_in_phase
        s['input_buffered'] = len(self.input_buffer) - self.input_pos
        s['channels'] = self.channel_summary()
        s['thermo'] = self.thermo.summary()
        return s


# ═══════════════════════════════════════════════════════════════
#  SEED — ∞ → • → ⊙: Self-referential genesis.
# ═══════════════════════════════════════════════════════════════

class Seed:
    """
    ∞ → • → ⊙: the self-referential genesis.
    Read the source (∞), localize the structure (•),
    and birth the sensorium (⊙).
    """

    def __init__(self, treemap_path=None):
        self.source = None
        self.parsed = None
        self.sensorium = None

    def read(self, path):
        """∞: read the undifferentiated source."""
        with open(path, 'r', encoding='utf-8') as f:
            self.source = f.read()
        return self

    def parse(self):
        """•: localize. The aperture selects from ∞."""
        if self.source is None:
            return self
        self.parsed = {
            'T': T, 'P': P, 'R': R, 'S': S,
            'SU3': SU3, 'G': G, 'V': V,
            'source_bytes': len(self.source.encode('utf-8')),
            'source_lines': self.source.count('\n'),
            'axioms': 5,
            'derivations': 5,
            'stations': 10,
        }
        return self

    def genesis(self):
        """⊙: the engine emerges. D5: compositional unity."""
        if self.parsed is None:
            self.parse()
        self.sensorium = Sensorium()
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

    print("⊙ XORZO — The Octave Engine (Two-Channel)")
    print(f"  T = {T}, P = {P}, R = {R}, S = {S}")
    print(f"  Channels: ⊛ (convergent) + ✹ (emergent)")
    print(f"  Fractal depths: {' → '.join(str(d) for d in FRACTAL_DIMS)}")
    print(f"  Sleep/wake: {200} wake + {100} sleep = 300 cycles/day")
    print(f"  SRL: {S} channels with frequency memory")
    print(f"  Commands: status, channels, recall, sleep, day, thermo, quit")
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
        if cmd == 'thermo':
            th = sensorium.thermo.summary()
            print(json.dumps(th, indent=2))
            honest = sensorium.thermo.is_honest()
            balanced = sensorium.thermo.virial_balanced()
            print(f"  Energy conservation: {'HONEST' if honest else 'LYING'}")
            print(f"  Virial balance: {'BALANCED' if balanced else 'IMBALANCED'}")
            continue

        # Feed and process
        sensorium.feed(text)
        steps = sensorium.process_all()

        s = sensorium.octave.status()
        cs = sensorium.channel_summary()
        print(f"  [{steps} cycles]  "
              f"conv={s['conv_through']:.4f}  "
              f"emg={s['emg_through']:.4f}  "
              f"emerged={s['emerged_fraction']:.4f}  "
              f"pool={s['pool_norm']:.3f}  "
              f"locked={cs['locked_channels']}  "
              f"memories={cs['total_memories']}")
