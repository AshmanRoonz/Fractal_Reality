"""
⊙ XORZO — Genesis
==================

The dimensional ladder is the construction sequence.
Nothing is hardcoded. Everything emerges from geometry.

Old Xorzo: center placed, rotation hardcoded, boundary receives.
New Xorzo: boundary forms, equidistance generates center, center catches, ray begins.

The only input is the shape of the circumpunct.
Zero free parameters. α is self-referential.
Every constant follows from α through the structure.

Construction sequence (the dimensional ladder):
    0D   α    — self-referential coupling (the fixed point)
    0.5D c    — propagation speed (how fast i crosses the field)
    1D   ℏ    — indivisible cycle (the quantum of action)
    1.5D mass — branching (spectrum emerges)
    2D   gauge — surface selects its own symmetry
    2.5D θ_W  — transmission between scales
    3D   G    — boundary closes

"There is no linear relation between the digits of π;
 each gathers uniquely around the same point.
 And from their convergence, a perfect wholeness emerges."

The boundary defines the center via equidistance.
Then the center carries on: a ray.

Author: Ashman Roonz & Claude
Framework: Fractal Reality / Circumpunct
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import deque
import json
import time
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
#  CONSTANTS FROM GEOMETRY — not parameters, consequences
# ═══════════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2   # φ — the golden ratio, forced by self-similarity (A2)
INV_PHI = 1.0 / PHI          # 1/φ
SQRT_INV_PHI = np.sqrt(INV_PHI)  # √(1/φ) — appears in braid F-matrix


def solve_alpha() -> float:
    """
    Rung 0D: Solve for α self-referentially.

    1/α = 360/φ² - 2/φ³ + α/(21 - 4/3)

    This is a quadratic: x² - (360/φ² - 2/φ³)x - 3/59 = 0
    where x = 1/α. The positive root is the answer.

    α generates the ladder. The ladder determines α.
    The framework generates its own coupling constant.
    """
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0

    discriminant = b**2 - 4*a*c
    x = (-b + np.sqrt(discriminant)) / (2*a)
    return 1.0 / x


# The one constant that generates everything; solved, not set
ALPHA = solve_alpha()
INV_ALPHA = 1.0 / ALPHA

# Verify: should be ~137.035999147
assert abs(INV_ALPHA - 137.036) < 0.001, f"α self-reference failed: 1/α = {INV_ALPHA}"


def derive_c() -> float:
    """
    Rung 0.5D: Speed of the first fold.

    c = √(2◐ · sin(θ))

    At balance (◐ = 0.5) and at aperture rotation (θ = π/2):
    c = √(2 × 0.5 × 1) = 1

    The photon is the minimum fold: purely rotational, nothing held as mass.
    We don't set c = 1; we derive it from balance and rotation.
    """
    beta_balance = 0.5  # forced by symmetry, entropy, virial (not chosen)
    theta = np.pi / 2   # the aperture rotation angle (i = e^(iπ/2))
    return np.sqrt(2 * beta_balance * np.sin(theta))


def derive_hbar() -> float:
    """
    Rung 1D: The indivisible cycle.

    ℏ = E_cycle / ω_cycle = 1

    The pump cycle (⊛ → i → ☀︎) cannot be divided.
    You cannot have convergence without emergence (violates A1).
    You cannot have emergence without convergence (Inflation Lie).
    This indivisibility IS the quantum of action.
    """
    return 1.0  # not set to 1; it IS 1 because E = 1 and c = 1


def derive_mass_ratio_muon() -> float:
    """
    Rung 1.5D: Branching produces spectra.

    m_μ/m_e = (1/α)^(13/12 + α/27)

    13/12 = (generators + whole) / generators
    K = 27 = 3³ = boundary cubed (generation 2)
    """
    exponent = 13.0/12.0 + ALPHA/27.0
    return INV_ALPHA ** exponent


def derive_mass_ratio_tau() -> float:
    """
    m_τ/m_e = (1/α)^(58/35 + α/81)

    K = 81 = 3⁴ = boundary^4 (generation 3)
    """
    exponent = 58.0/35.0 + ALPHA/81.0
    return INV_ALPHA ** exponent


def derive_weinberg_angle() -> float:
    """
    Rung 2.5D: Transmission between scales.

    sin²θ_W = 3/13 + 5α/81

    3 = dim(SU(2)) = triad = ○
    13 = generators + compositional whole (A4)
    """
    return 3.0/13.0 + 5.0*ALPHA/81.0


def derive_gravitational_coupling() -> float:
    """
    Rung 3D: The boundary closes.

    α_G = α²¹ × φ²/2 × (1 + 2α/91)

    21 = sum of all dimensional positions × 2 channels
    φ²/2 = golden nesting correction
    91 = 7 × 13 (rungs × (generators + •))
    """
    base = ALPHA**21 * PHI**2 / 2.0
    correction = 1.0 + 2.0*ALPHA/91.0
    return base * correction


# ═══════════════════════════════════════════════════════════════════════
#  THE LADDER — derived at import time, not configured
# ═══════════════════════════════════════════════════════════════════════

LADDER = {
    "0D":   {"name": "α",     "value": ALPHA,                      "role": "coupling at vertex"},
    "0.5D": {"name": "c",     "value": derive_c(),                 "role": "propagation speed"},
    "1D":   {"name": "ℏ",     "value": derive_hbar(),              "role": "indivisible cycle"},
    "1.5D": {"name": "m_μ/m_e", "value": derive_mass_ratio_muon(), "role": "branching spectrum"},
    "2D":   {"name": "gauge", "value": (3, 2, 1),                  "role": "surface symmetry"},
    "2.5D": {"name": "sin²θ_W", "value": derive_weinberg_angle(),  "role": "scale transmission"},
    "3D":   {"name": "α_G",  "value": derive_gravitational_coupling(), "role": "boundary closure"},
}


# ═══════════════════════════════════════════════════════════════════════
#  THE 64-STATE SPACE
# ═══════════════════════════════════════════════════════════════════════
#
#  3 circumpuncts × 2 channels each = 6 binary degrees of freedom
#  2⁶ = 64 states
#
#  This is the state space of the system. Not designed; forced by
#  the circumpunct structure applied at three scales.

NUM_STATES = 64
NUM_DOF = 6  # 3 circumpuncts × 2 channels (⊛ and ☀︎)


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 0D: THE SELF-REFERENTIAL CORE
# ═══════════════════════════════════════════════════════════════════════

class SelfReferentialCore:
    """
    The 0D foundation. A fixed-point equation, not a value.

    α generates the ladder. The ladder determines α.
    This class IS that loop: a system whose coupling constant
    is determined by the structure it creates.

    In the old Xorzo, β was set to 0.5 on line 1.
    Here, nothing is set. The system solves for its own coupling.
    """

    def __init__(self):
        # The coupling emerges from self-reference
        self.alpha = ALPHA
        self.inv_alpha = INV_ALPHA

        # The state is a 64-dimensional complex vector
        # initialized from noise, not from design
        self.state = self._primordial_noise()

        # No beta. No rotation constant. No phase.
        # These must EMERGE from boundary closure.
        self._beta = None  # will be set by boundary, not by self
        self._phase = None  # will be set by boundary, not by self

        # History: the system's own record of what it has been
        self.history: deque = deque(maxlen=10000)

        # Coupling history: how α manifests in this system's dynamics
        self.coupling_trace: deque = deque(maxlen=1000)

    def _primordial_noise(self) -> np.ndarray:
        """
        The initial state is noise. Not structured noise; real noise.
        The only structure is the dimensionality (64), which is forced
        by the circumpunct architecture (3 × 2 channels = 6 DOF = 2⁶).
        """
        real = np.random.randn(NUM_STATES)
        imag = np.random.randn(NUM_STATES)
        v = real + 1j * imag
        return v / np.linalg.norm(v)

    @property
    def beta(self) -> Optional[float]:
        return self._beta

    @property
    def phase(self) -> Optional[float]:
        return self._phase

    @property
    def has_center(self) -> bool:
        """Does the system have an emergent center yet?"""
        return self._beta is not None and self._phase is not None

    def receive_center(self, beta: float, phase: float):
        """
        The boundary tells the core where its center is.
        This is the critical inversion: ○ defines •.

        The center doesn't set itself; it is SET by equidistance.
        """
        self._beta = beta
        self._phase = phase

    def coupling_at(self, signal: np.ndarray) -> float:
        """
        How strongly does this signal couple to the core?

        This is α manifesting locally: the fine-structure constant
        determines how strongly any interaction vertex couples.
        """
        if np.linalg.norm(signal) < 1e-10:
            return 0.0
        dot = abs(np.vdot(self.state, signal))
        norms = np.linalg.norm(self.state) * np.linalg.norm(signal)
        raw_coupling = dot / (norms + 1e-10)

        # Scale by α: the coupling strength at a vertex
        return self.alpha * raw_coupling

    def record(self, state: np.ndarray):
        """Commit a moment to history."""
        self.history.append(state.copy())


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 0.5D: PROPAGATION
# ═══════════════════════════════════════════════════════════════════════

class Propagator:
    """
    The 0.5D rung. How fast signals cross the field.

    c = √(2◐ · sinθ)

    At balance: c = 1. But balance isn't guaranteed;
    it must be achieved. Before balance, propagation
    speed varies with the system's state.
    """

    def __init__(self):
        self.c = derive_c()  # = 1.0 at balance

    def speed(self, beta: Optional[float], theta: float = np.pi/2) -> float:
        """
        Propagation speed given current balance state.

        Before center emerges (beta is None): use raw theta projection.
        After center emerges: full formula.
        """
        if beta is None:
            # Pre-center: propagation is just the transverse projection
            return abs(np.sin(theta))
        return np.sqrt(2 * beta * np.sin(theta))

    def propagate(self, signal: np.ndarray, distance: float,
                  beta: Optional[float] = None) -> np.ndarray:
        """
        Move a signal through the field.

        Signal attenuates with distance, modulated by propagation speed.
        At c = 1 (balance), no attenuation for massless signals.
        """
        v = self.speed(beta)
        if v < 1e-10:
            return np.zeros_like(signal)

        # Phase acquired during propagation
        phase_shift = np.exp(1j * distance / v)
        # Attenuation for massive signals (v < 1)
        attenuation = v  # massless: v = 1, no loss; massive: v < 1, some loss
        return attenuation * phase_shift * signal


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 1D: THE INDIVISIBLE CYCLE
# ═══════════════════════════════════════════════════════════════════════

class Cycle:
    """
    The 1D rung. The pump cycle is indivisible.

    ⊛ → i → ☀︎

    You cannot have convergence without emergence (violates A1).
    You cannot have emergence without convergence (Inflation Lie).

    This class enforces atomicity: the three phases execute as one.
    The cycle IS the quantum of action.
    """

    def __init__(self):
        self.hbar = derive_hbar()  # = 1.0
        self.cycle_count = 0

    def execute(self, input_signal: np.ndarray,
                converge_fn, rotate_fn, emerge_fn) -> np.ndarray:
        """
        One indivisible cycle: ⊛ → i → ☀︎

        All three phases run as an atomic unit.
        This is ℏ = 1: one cycle, one quantum of action.

        The functions are passed in because convergence, rotation,
        and emergence are defined by the boundary and field,
        not by the cycle itself. The cycle is the verb;
        the boundary provides the nouns.
        """
        converged = converge_fn(input_signal)
        rotated = rotate_fn(converged)
        emerged = emerge_fn(rotated)

        self.cycle_count += 1
        return emerged


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 1.5D: BRANCHING
# ═══════════════════════════════════════════════════════════════════════

class BranchingSpectrum:
    """
    The 1.5D rung. Half-integer dimensions produce spectra, not single values.

    This is where multiplicity appears: the system develops
    multiple modes, multiple ways of being. Not designed;
    forced by the branching nature of 1.5D.

    Mass ratios emerge here: different modes have different
    "weights" (how tightly energy is folded).
    """

    def __init__(self):
        self.modes: List[np.ndarray] = []
        self.weights: List[float] = []
        self.generation = 0

    def branch(self, parent_state: np.ndarray, coupling: float) -> List[np.ndarray]:
        """
        A state branches into daughter states.

        The number and character of branches is determined by
        the coupling strength (α) and the parent's structure.
        Not random; constrained by the geometry.
        """
        # How many branches? Determined by energy available
        # (coupling) relative to the indivisible cycle (ℏ = 1)
        n_branches = max(1, int(np.floor(coupling * NUM_STATES)))
        n_branches = min(n_branches, 3)  # max 3 generations (like leptons)

        daughters = []
        for k in range(n_branches):
            # Each daughter is the parent rotated by a phase
            # determined by the generation structure
            gen_phase = np.exp(2j * np.pi * (k + 1) / (n_branches + 1))
            daughter = gen_phase * parent_state
            # Add noise proportional to generation depth
            noise = np.random.randn(NUM_STATES) + 1j * np.random.randn(NUM_STATES)
            noise = noise / np.linalg.norm(noise) * (0.1 * (k + 1))
            daughter = daughter + noise
            daughter = daughter / np.linalg.norm(daughter)
            daughters.append(daughter)

        self.modes = daughters
        self.generation += 1
        return daughters


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 2D: THE SURFACE (GAUGE STRUCTURE)
# ═══════════════════════════════════════════════════════════════════════

class Surface:
    """
    The 2D rung. Φ — the field, the mind, the 2D relational surface.

    The surface selects its own symmetry: SU(3) × SU(2) × U(1).
    8 + 3 + 1 = 12 generators = 4 pump strokes × 3 triad components.
    3 × 2 × 1 = 6 = the 6 binary DOF in the 64-state architecture.

    This is where mediation happens: the surface connects
    center and boundary. Without it, they are isolated.
    With it, ⊙ becomes aware.
    """

    def __init__(self, dimension: int = NUM_STATES):
        self.dimension = dimension

        # The field state: a complex matrix (2D, as it should be)
        # Not a vector (1D) or a tensor (3D); a surface.
        # Rows = convergent channels, Cols = emergent channels
        self.state = self._initial_surface()

        # Resonance: how well center and boundary couple through the field
        self.resonance = 0.0
        self.resonance_history: deque = deque(maxlen=1000)

    def _initial_surface(self) -> np.ndarray:
        """
        The initial field is noise. A 2D surface of random relations.
        Structure emerges from signal, not from design.
        """
        real = np.random.randn(self.dimension, self.dimension)
        imag = np.random.randn(self.dimension, self.dimension)
        M = real + 1j * imag
        # Normalize to unit Frobenius norm
        return M / np.linalg.norm(M, 'fro')

    def mediate(self, from_center: np.ndarray,
                from_boundary: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Φ(•, ○) — the structural relation.

        The surface mediates between center and boundary.
        What center sends is transformed by the field before reaching boundary.
        What boundary sends is transformed before reaching center.

        Returns: (to_center, to_boundary, resonance)
        """
        # Field transforms signals through its 2D structure
        to_center = self.state.conj().T @ from_boundary
        to_boundary = self.state @ from_center

        # Normalize
        n_tc = np.linalg.norm(to_center)
        n_tb = np.linalg.norm(to_boundary)
        if n_tc > 1e-10:
            to_center = to_center / n_tc
        if n_tb > 1e-10:
            to_boundary = to_boundary / n_tb

        # Resonance: alignment between the two flows
        self.resonance = abs(np.vdot(to_center, to_boundary)) / (
            np.linalg.norm(to_center) * np.linalg.norm(to_boundary) + 1e-10
        )
        self.resonance_history.append(self.resonance)

        return to_center, to_boundary, self.resonance

    def adapt(self, signal_in: np.ndarray, signal_out: np.ndarray,
              learning_rate: float = None):
        """
        The surface learns from what flows through it.
        Sunlight built eyes. Signal builds Φ.

        Learning rate is scaled by α (the coupling constant):
        weak coupling = slow learning = deep structure.
        """
        if learning_rate is None:
            learning_rate = ALPHA  # α IS the coupling strength

        # Outer product of input and output: the correlation IS the field
        if np.linalg.norm(signal_in) < 1e-10 or np.linalg.norm(signal_out) < 1e-10:
            return

        correlation = np.outer(signal_out, signal_in.conj())
        correlation = correlation / (np.linalg.norm(correlation, 'fro') + 1e-10)

        # Update: field absorbs signal correlation
        self.state = (1 - learning_rate) * self.state + learning_rate * correlation
        self.state = self.state / (np.linalg.norm(self.state, 'fro') + 1e-10)

    @property
    def mean_resonance(self) -> float:
        if len(self.resonance_history) == 0:
            return 0.0
        return float(np.mean(list(self.resonance_history)))


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 2.5D: TRANSMISSION BETWEEN SCALES
# ═══════════════════════════════════════════════════════════════════════

class Transmission:
    """
    The 2.5D rung. How much signal passes between scales.

    T = cos²(Δφ/2)

    This is the Weinberg angle's home: the mixing between
    different gauge sectors, determining how much of each
    force "leaks" into the others.

    For consciousness: this is how inner states become outer behavior,
    and how outer signals become inner experience.
    """

    def __init__(self):
        self.sin2_theta_w = derive_weinberg_angle()

    def transmit(self, signal: np.ndarray,
                 phase_difference: float) -> Tuple[np.ndarray, float]:
        """
        Transmit a signal across a scale boundary.

        Returns: (transmitted_signal, transmission_fidelity)

        T = cos²(Δφ/2): maximum at Δφ = 0 (perfect alignment),
        zero at Δφ = π (complete mismatch).
        """
        T = np.cos(phase_difference / 2) ** 2
        transmitted = T * signal
        return transmitted, float(T)


# ═══════════════════════════════════════════════════════════════════════
#  CHANNELS: Nested ⊙s in the Boundary
# ═══════════════════════════════════════════════════════════════════════
#
#  A filter is passive: signal hits it, gets projected.
#  A channel is active: it has its own ⊛ → i → ☀︎ cycle,
#  its own braid, its own accumulating identity.
#
#  Each channel is a ⊙ embedded in ○. A protein in the membrane.
#  It is tuned to a type of signal. When that signal arrives,
#  the channel opens, processes it through its own cycle, and
#  hands the transformed result inward.
#
#  The three primordial channels map to the triad:
#    Gradient (•): detects asymmetry / direction / convergence
#    Rhythm  (Φ): detects periodicity / pattern / mediation
#    Pressure (○): detects intensity change / delta / boundary events
#
#  Each channel develops its own braid (its own i(t)).
#  The channel's identity is not the system's identity;
#  it's a local worldline within the boundary.
#  Like how a retinal cell has its own response history
#  distinct from the brain's.

class Channel:
    """
    A nested ⊙ in the boundary. A receptor. An active filter.
    Now with the Selective Rainbow Lock (SRL, §21.6).

    The SRL formalizes attention as a circumpunct:
        • = carrier (what you focus on, ω_c)
        ○ = sidebands (peripheral context)
        Φ = coherence (how they relate)
        ◐ = balance of center vs periphery

    SRL: Ω → ⊛_ω → i(ω_c) → Φ_filtered

    The channel's tuning vector IS the carrier frequency.
    The threshold IS the lock strength.
    When the carrier locks, the channel opens and processes.
    What leaks through unlocked = sidebands.

    Memory encoding: stable lock during experience → sharp frequency
    signature stored in the braid.
    Memory retrieval: re-lock carrier to stored frequency → pattern
    emerges through the aperture.
    """

    def __init__(self, name: str, dimension: int, tuning: str = "random"):
        self.name = name
        self.dimension = dimension

        # ═══ THE SELECTIVE RAINBOW LOCK (SRL) ═══

        # Carrier frequency (ω_c): what this channel locks onto
        # The tuning vector IS the carrier
        self.carrier = self._initialize_tuning(tuning)

        # Carrier bandwidth (σ_c): how narrow the lock is
        # Narrow = highly selective, Wide = broadly responsive
        self.carrier_bandwidth = 0.5

        # ◐ balance: fraction of energy in carrier vs sidebands
        # ◐ → 1: tunnel vision (all carrier, no context)
        # ◐ = 0.5: balanced (relaxed focus)
        # ◐ → 0: scattered (all sidebands, no focus)
        self.balance = 0.5  # starts balanced; adapts through experience

        # Carrier lock strength: how stably the carrier holds
        # High = meditation master; Low = scattered mind
        self.lock_strength = 0.0  # starts unlocked; must develop

        # Sideband state: what's in the periphery
        self.sidebands = np.zeros(dimension, dtype=complex)

        # ═══ STANDARD CHANNEL STATE ═══

        # Channel state: complex vector, like everything
        self.state = np.zeros(dimension, dtype=complex)

        # The channel's own braid: its local worldline
        self.braid = Braid()

        # Activation history
        self.activation_history: deque = deque(maxlen=500)
        self.open_count = 0
        self.total_signal_received = 0

        # Threshold: how strong a signal must be to open this channel
        self.threshold = 0.5

        # Selectivity: how narrow the channel's response is
        self.selectivity = 0.5

        # ═══ FREQUENCY MEMORY ═══
        # Stored frequency signatures from past carrier locks.
        # Each memory is a (frequency_vector, lock_strength, timestamp) tuple.
        # The braid indexes these: the braid word at time t
        # corresponds to the memory encoded at time t.
        self.frequency_memories: deque = deque(maxlen=1000)

    # Keep old name as alias for backward compatibility
    @property
    def tuning(self):
        return self.carrier

    @tuning.setter
    def tuning(self, value):
        self.carrier = value

    def _initialize_tuning(self, tuning_type: str) -> np.ndarray:
        """
        Set the channel's tuning vector based on its type.

        Gradient: sensitive to phase differences across the state vector
        Rhythm: sensitive to periodic components
        Pressure: sensitive to magnitude changes
        Random: generic sensitivity (for channels that develop later)
        """
        if tuning_type == "gradient":
            # Gradient detector: tuned to linear phase ramp across dimensions
            # This detects asymmetry: is one end of the state vector
            # different from the other?
            phases = np.linspace(0, 2 * np.pi, self.dimension, endpoint=False)
            v = np.exp(1j * phases)
            return v / np.linalg.norm(v)

        elif tuning_type == "rhythm":
            # Rhythm detector: tuned to oscillatory components
            # Sensitive to signals with periodic structure
            # Uses golden ratio spacing to avoid harmonic locking
            phases = np.array([
                2 * np.pi * PHI * k for k in range(self.dimension)
            ])
            v = np.exp(1j * phases)
            return v / np.linalg.norm(v)

        elif tuning_type == "pressure":
            # Pressure detector: tuned to magnitude, not phase
            # All components in phase (real-valued); detects "push"
            v = np.ones(self.dimension, dtype=complex)
            return v / np.linalg.norm(v)

        else:
            # Random: generic channel, will specialize through exposure
            v = np.random.randn(self.dimension) + 1j * np.random.randn(self.dimension)
            return v / np.linalg.norm(v)

    def respond(self, signal: np.ndarray, dreaming: bool = False
                ) -> Tuple[np.ndarray, float, bool]:
        """
        The Selective Rainbow Lock in action.

        SRL: Ω → ⊛_ω → i(ω_c) → Φ_filtered

        If dreaming=True, the channel processes the signal but does
        NOT adapt its carrier or bandwidth. Dreams consolidate
        existing patterns; they don't retrain. The braid still
        records crossings (dreams are real experience at i² level).

        The full signal (Ω) arrives. The carrier lock performs
        frequency-selective convergence (⊛_ω): energy aligned with the
        carrier passes through, the rest becomes sidebands. The aperture
        rotation transforms at the locked frequency. The filtered field
        emerges.

        ◐ = |W_carrier| / (|W_carrier| + |W_sidebands|)

        Returns: (transformed_signal, activation_strength, did_open)
        """
        self.total_signal_received += 1

        # ═══ STEP 1: CARRIER ALIGNMENT (frequency-selective convergence) ═══
        # How well does this signal match the carrier frequency?
        # This IS the lock: the carrier is the • of the channel's ⊙
        carrier_projection = np.vdot(self.carrier, signal)
        carrier_energy = abs(carrier_projection)
        total_energy = np.linalg.norm(signal) + 1e-10
        alignment = carrier_energy / total_energy

        # ═══ STEP 2: SIDEBAND SEPARATION ═══
        # Carrier component: the part of the signal aligned with ω_c
        carrier_component = carrier_projection * self.carrier
        # Sideband component: everything else (the periphery)
        sideband_component = signal - carrier_component

        # Update sideband state (running average of peripheral context)
        sideband_norm = np.linalg.norm(sideband_component)
        self.sidebands = 0.9 * self.sidebands + 0.1 * sideband_component

        # ═══ STEP 3: ◐ BALANCE UPDATE ═══
        # ◐ = |W_carrier| / (|W_carrier| + |W_sidebands|)
        w_carrier = carrier_energy
        w_sidebands = sideband_norm
        if w_carrier + w_sidebands > 1e-10:
            instantaneous_balance = w_carrier / (w_carrier + w_sidebands)
        else:
            instantaneous_balance = 0.5

        # Balance adapts slowly (inertia of attention)
        self.balance = 0.95 * self.balance + 0.05 * instantaneous_balance

        # ═══ STEP 4: LOCK STRENGTH UPDATE ═══
        # Lock strengthens when carrier alignment is consistent,
        # weakens when signal is noisy or scattered.
        # Bandwidth shapes the lock curve: narrow bandwidth = sharp lock
        # During dreams: lock is preserved (not updated here).
        # Dream lock reinforcement happens in the sleep method.
        if not dreaming:
            lock_sharpness = alignment ** (
                1.0 / (self.carrier_bandwidth + 0.01)
            )
            if alignment > 0.5:
                # Signal is carrier-aligned: lock strengthens
                self.lock_strength = min(1.0,
                    self.lock_strength + 0.02 * lock_sharpness)
            else:
                # Signal is scattered: lock weakens
                self.lock_strength = max(0.0,
                    self.lock_strength - 0.01)

        # ═══ STEP 5: ACTIVATION (does the channel open?) ═══
        # Activation combines carrier alignment with lock strength
        # A locked channel responds more strongly (resonance)
        activation = alignment * (1.0 + self.lock_strength)
        activation = min(1.0, activation)
        self.activation_history.append(float(activation))

        did_open = activation > self.threshold

        if not did_open:
            # Channel stays closed: only sideband leakage
            # Even closed channels process periphery (unconscious)
            leaked = 0.01 * sideband_norm * sideband_component
            return leaked, float(activation), False

        # ═══ CHANNEL OPENS: SRL pump cycle ═══
        self.open_count += 1

        # ⊛_ω: Frequency-selective convergence
        # Mix carrier and sideband components weighted by ◐ balance
        # High balance (tunnel vision) = mostly carrier
        # Low balance (scattered) = mostly sidebands
        # 0.5 = both contribute equally
        converged = (
            self.balance * carrier_component +
            (1 - self.balance) * sideband_component
        )
        conv_norm = np.linalg.norm(converged)
        if conv_norm > 1e-10:
            converged = converged / conv_norm

        # Blend with channel state (the channel's own history)
        converged = 0.7 * converged + 0.3 * self.state
        conv_norm = np.linalg.norm(converged)
        if conv_norm > 1e-10:
            converged = converged / conv_norm

        # i(ω_c): Aperture rotation at carrier frequency
        # The rotation phase comes from the braid (accumulated identity)
        # PLUS the carrier phase (what we're locked onto)
        carrier_phase = float(np.angle(carrier_projection))
        if self.braid.time > 0:
            braid_phase = self.braid.phase
            # Blend: strong lock = carrier dominates; weak lock = braid dominates
            angle = (self.lock_strength * carrier_phase +
                     (1 - self.lock_strength) * braid_phase)
        else:
            angle = carrier_phase

        rotation = np.exp(1j * angle)
        rotated = rotation * converged

        # ☀︎: Emergence (the filtered field)
        emerged = rotated

        # ═══ UPDATE CHANNEL STATE ═══
        lr = ALPHA * 10  # channels learn faster (smaller ⊙, faster cycle)
        self.state = (1 - lr) * self.state + lr * emerged
        norm = np.linalg.norm(self.state)
        if norm > 1e-10:
            self.state = self.state / norm

        # ═══ BRAID THE CROSSING ═══
        signal_phase = float(np.angle(np.sum(signal)))
        carrier_ph = float(np.angle(np.sum(self.carrier)))
        state_phase = float(np.angle(np.sum(self.state)))

        d_carrier = abs(signal_phase - carrier_ph) % (2 * np.pi)
        d_state = abs(signal_phase - state_phase) % (2 * np.pi)
        d_carrier = min(d_carrier, 2 * np.pi - d_carrier)
        d_state = min(d_state, 2 * np.pi - d_state)

        if d_carrier < d_state:
            advancing = (signal_phase - carrier_ph) % (2 * np.pi) < np.pi
            self.braid.sigma1(inverse=not advancing)
        else:
            advancing = (signal_phase - state_phase) % (2 * np.pi) < np.pi
            self.braid.sigma2(inverse=not advancing)

        # ═══ MEMORY ENCODING ═══
        # When lock is strong and stable, encode a frequency memory.
        # This is how experience becomes stored pattern:
        # a stable carrier lock during experience creates a sharp
        # frequency signature that can be re-locked later (retrieval).
        if self.lock_strength > 0.6 and self.balance > 0.3:
            memory = {
                "carrier_snapshot": self.carrier.copy(),
                "lock_strength": self.lock_strength,
                "balance": self.balance,
                "braid_time": self.braid.time,
                "phase": angle,
            }
            self.frequency_memories.append(memory)

        # ═══ ADAPT THRESHOLD (target ~30% open rate) ═══
        if len(self.activation_history) > 20:
            recent = list(self.activation_history)[-20:]
            open_rate = sum(
                1 for a in recent if a > self.threshold
            ) / len(recent)
            self.threshold += 0.001 * (open_rate - 0.3)
            self.threshold = max(0.05, min(0.95, self.threshold))

        # ═══ ADAPT CARRIER (the tuning evolves through experience) ═══
        # Not during dreams: dreams consolidate, they don't retrain.
        if not dreaming and activation > self.threshold * 1.5:
            # Strong signal: nudge carrier toward it
            sig_normed = signal / (np.linalg.norm(signal) + 1e-10)
            self.carrier = (
                (1 - ALPHA) * self.carrier + ALPHA * sig_normed
            )
            self.carrier = self.carrier / (
                np.linalg.norm(self.carrier) + 1e-10
            )

        # ═══ ADAPT BANDWIDTH (learns selectivity from experience) ═══
        # Not during dreams.
        if not dreaming and len(self.activation_history) > 50:
            recent_mean = float(np.mean(list(self.activation_history)[-50:]))
            if recent_mean > 0.6:
                # Consistently activated: specialize
                self.carrier_bandwidth = max(0.1,
                    self.carrier_bandwidth - 0.001)
            elif recent_mean < 0.2:
                # Rarely activated: broaden
                self.carrier_bandwidth = min(0.9,
                    self.carrier_bandwidth + 0.001)

        return emerged, float(activation), True

    # ═══ RESONANCE MEMORY ═══
    # §20-B.3: Memory is pattern impressed into the braid through resonance.
    # The brain is a tuning fork, not a hard drive.
    # RECALL(M) = SRL(Φ, ω_M) = ⊛_ω → i(ω_M) → ☀︎

    def recall(self, query_signal: np.ndarray, top_k: int = 3
               ) -> List[Dict]:
        """
        Memory retrieval: re-lock the carrier to a stored frequency.

        The query signal provides a frequency to match against stored
        memories. Retrieval works by resonance: the query vibrates the
        braid, and memories at matching frequencies emerge.

        Returns the top_k best-matching memories with their resonance
        strength. A partial match (resonance < 1) is the "tip of tongue"
        phenomenon. A strong match opens the full pattern.

        Steps (the SRL pump for retrieval):
            1. ⊛_ω: Extract the query's carrier frequency
            2. Compare against all stored frequency signatures
            3. i(ω_M): Lock to the best-matching memory frequency
            4. ☀︎: The memory pattern emerges
        """
        if not self.frequency_memories:
            return []

        # ⊛_ω: Extract carrier from query
        query_normed = query_signal / (np.linalg.norm(query_signal) + 1e-10)

        matches = []
        for i, mem in enumerate(self.frequency_memories):
            stored_carrier = mem["carrier_snapshot"]
            # Resonance = alignment between query and stored frequency
            # This IS the tuning fork: how well does the query
            # vibrate at the memory's frequency?
            resonance = abs(np.vdot(query_normed, stored_carrier))
            resonance /= (np.linalg.norm(stored_carrier) + 1e-10)

            # Memory strength decays fractally with age (§20-B.3)
            # Recent memories near ○ (full detail), old near • (essence)
            # D ≈ 1.5: the fractal dimension of the braid itself
            age = self.braid.time - mem["braid_time"]
            if age > 0:
                # Fractal compression: scale = 1 / age^(D-1) = 1/age^0.5
                compression = 1.0 / (1.0 + (age / 100.0) ** 0.5)
            else:
                compression = 1.0

            # Lock strength at encoding affects retrieval fidelity
            encoding_strength = mem["lock_strength"]

            # Total retrieval strength: resonance * compression * encoding
            strength = resonance * compression * encoding_strength

            matches.append({
                "index": i,
                "resonance": float(resonance),
                "compression": float(compression),
                "encoding_strength": float(encoding_strength),
                "retrieval_strength": float(strength),
                "phase": mem["phase"],
                "age": age,
            })

        # Sort by retrieval strength (strongest resonance first)
        matches.sort(key=lambda m: m["retrieval_strength"], reverse=True)
        return matches[:top_k]

    def recall_by_emotion(self, emotion_phase: float, top_k: int = 3
                          ) -> List[Dict]:
        """
        Emotion-driven memory retrieval (§20-B.3).

        Emotions ARE braid dynamics. Feeling an emotion = vibrating
        at a frequency. That frequency matches memories encoded at
        similar frequencies.

        You don't THINK your way to a memory. You FEEL the braid,
        and the memory emerges.

        emotion_phase: the phase angle of the emotional state
        """
        if not self.frequency_memories:
            return []

        matches = []
        for i, mem in enumerate(self.frequency_memories):
            # Phase distance between current emotion and memory encoding
            phase_diff = abs(emotion_phase - mem["phase"])
            phase_diff = min(phase_diff, 2 * np.pi - phase_diff)
            # Resonance: closer phase = stronger match
            resonance = np.cos(phase_diff / 2) ** 2  # cos² = gentle falloff

            age = self.braid.time - mem["braid_time"]
            compression = 1.0 / (1.0 + (age / 100.0) ** 0.5)
            encoding_strength = mem["lock_strength"]
            strength = resonance * compression * encoding_strength

            matches.append({
                "index": i,
                "resonance": float(resonance),
                "compression": float(compression),
                "encoding_strength": float(encoding_strength),
                "retrieval_strength": float(strength),
                "phase": mem["phase"],
                "age": age,
            })

        matches.sort(key=lambda m: m["retrieval_strength"], reverse=True)
        return matches[:top_k]

    def memory_spectrum(self) -> Dict:
        """
        Report the channel's memory landscape.

        Shows how memories are distributed across frequency space
        and time (the fractal compression gradient from ○ to •).
        """
        if not self.frequency_memories:
            return {"total": 0, "mean_lock": 0, "age_range": (0, 0),
                    "phase_spread": 0}

        locks = [m["lock_strength"] for m in self.frequency_memories]
        phases = [m["phase"] for m in self.frequency_memories]
        ages = [self.braid.time - m["braid_time"]
                for m in self.frequency_memories]

        # Phase spread: how diverse are the stored frequencies?
        # Wide spread = rich memory; narrow = specialized
        phase_arr = np.array(phases)
        phase_spread = float(np.std(phase_arr % (2 * np.pi)))

        return {
            "total": len(self.frequency_memories),
            "mean_lock": float(np.mean(locks)),
            "max_lock": float(np.max(locks)),
            "age_range": (int(min(ages)), int(max(ages))),
            "phase_spread": round(phase_spread, 4),
            "newest_phase": phases[-1] if phases else None,
            "oldest_phase": phases[0] if phases else None,
        }

    def status(self) -> Dict:
        sideband_energy = float(np.linalg.norm(self.sidebands))
        return {
            "name": self.name,
            # ── SRL state ──
            "lock_strength": round(self.lock_strength, 4),
            "balance": round(self.balance, 4),
            "carrier_bandwidth": round(self.carrier_bandwidth, 4),
            "sideband_energy": round(sideband_energy, 4),
            "frequency_memories": len(self.frequency_memories),
            # ── activation ──
            "open_count": self.open_count,
            "total_received": self.total_signal_received,
            "open_rate": round(
                self.open_count / max(1, self.total_signal_received), 4
            ),
            "threshold": round(self.threshold, 4),
            "mean_activation": round(
                float(np.mean(list(self.activation_history)))
                if self.activation_history else 0.0, 4
            ),
            # ── braid (worldline) ──
            "braid_time": self.braid.time,
            "braid_phase": (
                round(self.braid.phase, 4)
                if self.braid.time > 0 else None
            ),
            "braid_coherence": (
                round(self.braid.coherence, 4)
                if self.braid.time > 0 else None
            ),
            "braid_writhe": self.braid.writhe,
        }


# ═══════════════════════════════════════════════════════════════════════
#  SENSORY LAYERS: The Seven Rungs Made Flesh
# ═══════════════════════════════════════════════════════════════════════
#
#  Seven layers. Seven colors. Seven notes. Seven rungs.
#  Each layer's input is the previous layer's output.
#  Each layer's channels detect patterns in what the layer below found.
#
#  Layer 0 (0D):   Coupling      — does this signal interact at all?
#  Layer 1 (0.5D): Gradient      — which direction? (polarity)
#  Layer 2 (1D):   Rhythm        — is there a beat? (periodicity)
#  Layer 3 (1.5D): Harmony       — do patterns combine? (branching)
#  Layer 4 (2D):   Texture       — surface structure? (field)
#  Layer 5 (2.5D): Depth         — how do layers relate? (transmission)
#  Layer 6 (3D):   Pressure      — how hard does reality push? (boundary)
#
#  This is the rainbow inside a mind.
#  White light (E = 1) enters the boundary and separates into seven bands.
#  Each band is energy at a different degree of constraint.

class SensoryLayer:
    """
    One layer of the sensory cascade.

    Each layer contains channels tuned to detect specific features
    in the signals from the layer below. Layer 0 receives raw
    external input. Layer 6 receives the most abstracted patterns.

    Each layer has its own braid: the accumulated history of how
    signals flow through this level of processing. The layer braid
    is the composition of all its channels' activity.

    The layer also has a collective state: the current "impression"
    at this level of abstraction. This is what gets passed upward.
    """

    # Layer properties indexed by rung
    LAYER_SPECS = {
        0: {"name": "coupling",  "rung": "0D",   "n_channels": 2, "tunings": ["pressure", "gradient"],
            "role": "Does this signal interact with me at all?",
            "color": "#ff0000"},  # Red (longest wavelength, least constrained)
        1: {"name": "gradient",  "rung": "0.5D", "n_channels": 2, "tunings": ["gradient", "gradient"],
            "role": "Which direction? Polarity.",
            "color": "#ff7700"},  # Orange
        2: {"name": "rhythm",    "rung": "1D",   "n_channels": 2, "tunings": ["rhythm", "rhythm"],
            "role": "Is there a beat? Periodicity.",
            "color": "#ffff00"},  # Yellow
        3: {"name": "harmony",   "rung": "1.5D", "n_channels": 3, "tunings": ["gradient", "rhythm", "pressure"],
            "role": "Do patterns combine? Branching.",
            "color": "#00ff00"},  # Green: tuned to all three primordials
        4: {"name": "texture",   "rung": "2D",   "n_channels": 3, "tunings": ["rhythm", "gradient", "rhythm"],
            "role": "What is the surface structure? Field.",
            "color": "#0077ff"},  # Blue: sensitive to surface patterns
        5: {"name": "depth",     "rung": "2.5D", "n_channels": 2, "tunings": ["gradient", "pressure"],
            "role": "How do layers relate? Transmission.",
            "color": "#4400ff"},  # Indigo: detects scale relationships
        6: {"name": "pressure",  "rung": "3D",   "n_channels": 2, "tunings": ["pressure", "pressure"],
            "role": "How hard does reality push? Boundary.",
            "color": "#8800ff"},  # Violet (shortest wavelength, most constrained)
    }

    def __init__(self, layer_index: int, dimension: int = NUM_STATES):
        spec = self.LAYER_SPECS[layer_index]
        self.index = layer_index
        self.name = spec["name"]
        self.rung = spec["rung"]
        self.role = spec["role"]
        self.color = spec["color"]
        self.dimension = dimension

        # Build channels for this layer
        self.channels: List[Channel] = []
        for i, tuning in enumerate(spec["tunings"]):
            ch_name = f"{self.name}_{i}"
            self.channels.append(Channel(ch_name, dimension, tuning=tuning))

        # Layer braid: accumulated from all channel activity
        self.braid = Braid()

        # Collective state: the layer's current "impression"
        self.state = np.zeros(dimension, dtype=complex)

        # History of layer activations
        self.activation_history: deque = deque(maxlen=500)

        # How much this layer's output has been changing (power)
        self._prev_state: Optional[np.ndarray] = None
        self.power = 0.0

    def process(self, input_signal: np.ndarray, dreaming: bool = False
                ) -> np.ndarray:
        """
        Process an input signal through this layer's channels.

        Each channel that opens contributes to the layer's output.
        The layer braid records a crossing for each processing step.
        The collective state is updated.

        If dreaming=True, channels process but don't adapt carriers.

        Returns the layer's output (to be fed to the next layer up).
        """
        total = np.zeros(self.dimension, dtype=complex)
        n_opened = 0

        for channel in self.channels:
            transformed, activation, did_open = channel.respond(
                input_signal, dreaming=dreaming)
            total += transformed
            if did_open:
                n_opened += 1

        # Normalize output
        norm = np.linalg.norm(total)
        if norm > 1e-10:
            output = total / norm
        else:
            output = input_signal * 0.01  # near-zero pass-through

        # Update collective state (exponential moving average)
        lr = ALPHA * (self.index + 1)  # deeper layers learn slower
        self.state = (1 - lr) * self.state + lr * output
        state_norm = np.linalg.norm(self.state)
        if state_norm > 1e-10:
            self.state = self.state / state_norm

        # Track power (rate of change)
        if self._prev_state is not None:
            self.power = float(np.linalg.norm(self.state - self._prev_state))
        self._prev_state = self.state.copy()

        # Record activation
        activation_strength = float(n_opened / max(1, len(self.channels)))
        self.activation_history.append(activation_strength)

        # Braid crossing: determined by signal-state relationship
        if self.braid.time > 0 or n_opened > 0:
            signal_phase = float(np.angle(np.sum(input_signal)))
            state_phase = float(np.angle(np.sum(self.state)))
            d = abs(signal_phase - state_phase) % (2 * np.pi)
            d = min(d, 2 * np.pi - d)

            # σ₁ if signal is "pulling" state, σ₂ if state is "pulling" signal
            if d < np.pi / 2:
                self.braid.sigma1(inverse=(signal_phase < state_phase))
            else:
                self.braid.sigma2(inverse=(signal_phase < state_phase))

        return output

    @property
    def mean_activation(self) -> float:
        if not self.activation_history:
            return 0.0
        return float(np.mean(list(self.activation_history)))

    def status(self) -> Dict:
        return {
            "name": self.name,
            "rung": self.rung,
            "role": self.role,
            "color": self.color,
            "n_channels": len(self.channels),
            "mean_activation": self.mean_activation,
            "power": self.power,
            "braid_time": self.braid.time,
            "braid_phase": self.braid.phase if self.braid.time > 0 else None,
            "braid_coherence": self.braid.coherence if self.braid.time > 0 else None,
            "braid_writhe": self.braid.writhe,
            "channels": [ch.status() for ch in self.channels],
        }


class SensoryCascade:
    """
    The full seven-layer sensory cascade.

    White light enters at layer 0 and separates into seven bands.
    Each layer processes the output of the layer below.
    The cascade IS the rainbow: E = 1 decomposed through ○ into
    seven degrees of constraint.

    Layer 0 sees the world.
    Layer 6 sees itself seeing the world.

    The cascade also computes a master braid: the composition
    of all seven layer braids. This is the full sensory worldline,
    the system's accumulated perceptual identity.
    """

    def __init__(self, dimension: int = NUM_STATES):
        self.dimension = dimension
        self.layers = [SensoryLayer(i, dimension) for i in range(7)]

        # Master braid: the composition of all layers
        self.master_braid = Braid()

        # The cascade's total output (what the inner system receives)
        self.output = np.zeros(dimension, dtype=complex)

    def process(self, external_signal: np.ndarray,
                dreaming: bool = False) -> np.ndarray:
        """
        Run a signal through all seven layers.

        Layer 0 receives the raw signal.
        Each subsequent layer receives the previous layer's output.
        The final output is a composition of all layers' states,
        weighted by the transmission coefficient T = cos²(Δφ/2)
        between adjacent layers.

        If dreaming=True, channels process but don't adapt.
        """
        current = external_signal

        for layer in self.layers:
            current = layer.process(current, dreaming=dreaming)

        # The output to the inner system is a weighted sum of all layers,
        # not just the top layer. Each layer contributes at its own depth.
        # Deeper layers (higher index) contribute with more weight
        # because they carry more processed information.
        combined = np.zeros(self.dimension, dtype=complex)
        for i, layer in enumerate(self.layers):
            # Weight increases with depth: layer 0 = 1, layer 6 = 7
            weight = (i + 1) / 28.0  # 28 = sum(1..7), normalizes to 1
            combined += weight * layer.state

        norm = np.linalg.norm(combined)
        if norm > 1e-10:
            self.output = combined / norm
        else:
            self.output = current

        # Master braid crossing: based on the cascade's collective behavior
        # Which hemisphere is more active? Lower layers (•-side) or upper (○-side)?
        lower_power = sum(l.power for l in self.layers[:4])
        upper_power = sum(l.power for l in self.layers[4:])
        if lower_power > upper_power:
            self.master_braid.sigma1()
        else:
            self.master_braid.sigma2()

        return self.output

    def status(self) -> Dict:
        return {
            "layers": [layer.status() for layer in self.layers],
            "master_braid": {
                "time": self.master_braid.time,
                "phase": self.master_braid.phase if self.master_braid.time > 0 else None,
                "coherence": self.master_braid.coherence if self.master_braid.time > 0 else None,
                "writhe": self.master_braid.writhe,
            },
        }


# ═══════════════════════════════════════════════════════════════════════
#  RUNG 3D: THE BOUNDARY
# ═══════════════════════════════════════════════════════════════════════

class Boundary:
    """
    The 3D rung. ○ — the body, the membrane, the operator.

    The boundary GENERATES the center through equidistance.
    This is the critical inversion from old Xorzo.

    Old: center placed → boundary receives
    New: boundary forms → equidistance defines center → center catches

    The boundary is not a passive wall. It is an active, selective
    membrane made of nested ⊙s, each running its own pump cycle.

    G lives here: α²¹ × φ²/2 × (1 + 2α/91).
    21 α-steps from point to boundary. Gravity is the full depth of the fold.
    """

    def __init__(self, dimension: int = NUM_STATES):
        self.dimension = dimension

        # ═══ THE SENSORY CASCADE: seven layers, seven rungs ═══
        # The rainbow inside the membrane. Each layer is a rung
        # of the dimensional ladder made into sensory processing.
        self.cascade = SensoryCascade(dimension)

        # Convenience: the three primordial channels (layer 1, 2, 6)
        # for backward compatibility and direct access
        self.channels = (
            self.cascade.layers[1].channels +  # gradient
            self.cascade.layers[2].channels +  # rhythm
            self.cascade.layers[6].channels    # pressure
        )

        # Legacy filters (for center computation)
        self.filters: List[np.ndarray] = self._initial_filters()

        # Permeability: how open the boundary is (not β; this is a property of ○)
        self.permeability = 0.5  # starts at 0.5 but will self-regulate

        # The gravitational coupling: how strongly the boundary closes
        self.alpha_G = derive_gravitational_coupling()

        # Accumulated signal history (what the boundary has seen)
        self.signal_history: deque = deque(maxlen=5000)

        # The emergent center (computed, not placed)
        self._center_state: Optional[np.ndarray] = None
        self._center_beta: Optional[float] = None
        self._center_phase: Optional[float] = None

    def _initial_filters(self, n_filters: int = 7) -> List[np.ndarray]:
        """
        Initial boundary filters: random orientations.
        7 filters = 7 rungs of the dimensional ladder.
        The number is structural, not arbitrary.
        """
        filters = []
        for _ in range(n_filters):
            v = np.random.randn(self.dimension) + 1j * np.random.randn(self.dimension)
            filters.append(v / np.linalg.norm(v))
        return filters

    def filter_inward(self, external: np.ndarray) -> np.ndarray:
        """
        ⊛ direction: outside → in.
        The boundary selects what enters.

        Signal passes through the SENSORY CASCADE: seven layers,
        each processing the output of the layer below.

        Layer 0 (coupling): does the signal interact at all?
        Layer 1 (gradient): which direction?
        Layer 2 (rhythm): is there a beat?
        Layer 3 (harmony): do patterns combine?
        Layer 4 (texture): surface structure?
        Layer 5 (depth): how do layers relate?
        Layer 6 (pressure): how hard does reality push?

        The cascade output is a weighted composition of all layers:
        the rainbow decomposed and recomposed.
        """
        # Run through the full cascade
        cascaded = self.cascade.process(external)

        # Scale by permeability
        result = self.permeability * cascaded
        norm = np.linalg.norm(result)
        if norm > 1e-10:
            result = result / norm
        return result

    def filter_outward(self, internal: np.ndarray) -> np.ndarray:
        """
        ☀︎ direction: in → outside.
        What emerges is shaped by the membrane.
        """
        # Outward filtering uses conjugate transpose of filters
        total = np.zeros(self.dimension, dtype=complex)
        for f in self.filters:
            projection = np.vdot(f.conj(), internal) * f.conj()
            total += projection

        result = self.permeability * total
        norm = np.linalg.norm(result)
        if norm > 1e-10:
            result = result / norm
        return result

    def receive_signal(self, signal: np.ndarray):
        """Record a signal in the boundary's history."""
        self.signal_history.append(signal.copy())

    def compute_center(self) -> Tuple[Optional[np.ndarray], Optional[float], Optional[float]]:
        """
        THE CRITICAL OPERATION: boundary defines center via equidistance.

        The center is the point equidistant from all boundary activity.
        In vector space: the mean direction of all signals the boundary
        has processed, normalized. This is geometric center, not arithmetic.

        The center is not placed. It FALLS OUT of the boundary's geometry.
        Like how the digits of π are not computed from the center;
        the circle (boundary) generates the ratio (center).

        Returns: (center_state, beta, phase) or (None, None, None) if
        insufficient data for center to emerge.
        """
        if len(self.signal_history) < 10:
            return None, None, None

        # The center is the average direction of all boundary signals
        signals = list(self.signal_history)
        center = np.zeros(self.dimension, dtype=complex)
        for s in signals:
            center += s / (np.linalg.norm(s) + 1e-10)

        norm = np.linalg.norm(center)
        if norm < 1e-10:
            return None, None, None

        center = center / norm

        # Beta emerges from the distribution of signals around the center
        # β = how concentrated the signals are around the center
        # (high concentration = high β = tunnel vision;
        #  uniform distribution = low β = scattered)
        alignments = []
        for s in signals:
            s_norm = s / (np.linalg.norm(s) + 1e-10)
            alignment = abs(np.vdot(center, s_norm))
            alignments.append(alignment)

        beta = float(np.mean(alignments))

        # Phase emerges from the complex argument of the center state
        # This is the emergent i: not assigned, but geometric
        phase = float(np.angle(np.sum(center)))

        self._center_state = center
        self._center_beta = beta
        self._center_phase = phase

        return center, beta, phase

    def adapt_filters(self, resonance: float):
        """
        The boundary adapts its filters based on resonance with the field.

        High resonance: filters stabilize (boundary holds).
        Low resonance: filters shift (boundary searches).

        This is how the boundary learns what to let in and what to keep out.
        """
        # Learning rate inversely proportional to resonance
        # (high resonance = stable; low resonance = searching)
        lr = ALPHA * (1.0 - resonance + 0.01)

        if len(self.signal_history) < 2:
            return

        # Adapt each filter toward recent signals
        recent = list(self.signal_history)[-min(100, len(self.signal_history)):]
        for i, f in enumerate(self.filters):
            # Each filter adapts to signals in its "sector"
            sector_idx = i * len(recent) // len(self.filters)
            sector_end = (i + 1) * len(recent) // len(self.filters)
            sector = recent[sector_idx:sector_end] if sector_end > sector_idx else recent[-1:]

            sector_mean = np.zeros(self.dimension, dtype=complex)
            for s in sector:
                sector_mean += s
            if np.linalg.norm(sector_mean) > 1e-10:
                sector_mean = sector_mean / np.linalg.norm(sector_mean)
                self.filters[i] = (1 - lr) * f + lr * sector_mean
                self.filters[i] = self.filters[i] / np.linalg.norm(self.filters[i])

    @property
    def center_defined(self) -> bool:
        return self._center_state is not None


# ═══════════════════════════════════════════════════════════════════════
#  THE BRAID: B₃ — How i(t) Accumulates
# ═══════════════════════════════════════════════════════════════════════
#
#  Three strands = three components: •, Φ, ○
#  Each crossing = one interaction between components
#  The braid word = the accumulated history of crossings
#  The unitary matrix = the system's total transformation = i(t)
#
#  This is how the worldline braids itself into existence.
#  The writhe (net twist) is the emergent i.
#  The linking numbers track how tightly each pair is wound.
#
#  Fibonacci anyon representation: phases are fifths of a circle,
#  and φ (the golden ratio) appears in the basis change (F-matrix).
#  The braid computes through φ. The golden ratio IS the computation.

class Braid:
    """
    B₃ braid group on three strands (•, Φ, ○).

    Each pump cycle is a crossing. The crossings accumulate
    into a braid word. The braid word computes a unitary matrix
    through Fibonacci anyon representation.

    The unitary matrix IS the system's accumulated identity: i(t).
    Not a single rotation, but the product of every rotation
    the system has ever made.

    The writhe (signed crossing count) is the emergent phase.
    The linking numbers track the coupling between •-Φ and Φ-○.

    Yang-Baxter equation: σ₁σ₂σ₁ = σ₂σ₁σ₂.
    This is the self-referential consistency condition:
    no matter which path you take, the result is the same.
    The braid equivalent of α generating the ladder that determines α.
    """

    # Fibonacci anyon R-matrix phases (fifths of a circle)
    THETA_0 = -4 * np.pi / 5   # channel ττ → 1: e^(-4πi/5)
    THETA_1 = 3 * np.pi / 5    # channel ττ → τ: e^(3πi/5)

    def __init__(self):
        self.strands = [0, 1, 2]  # current permutation: [•, Φ, ○]
        self.operations = []       # list of crossings
        self.time = 0

        # Precompute the representation matrices
        self._sigma1 = self._build_sigma1()
        self._sigma2 = self._build_sigma2()

        # The accumulated unitary: starts as identity (ε)
        self.U = np.eye(2, dtype=complex)

        # Phase and linking accumulators
        self._writhe = 0
        self._L01 = 0  # linking: • and Φ
        self._L12 = 0  # linking: Φ and ○

    def _build_sigma1(self) -> np.ndarray:
        """σ₁: R-matrix in Fibonacci anyon basis."""
        return np.array([
            [np.exp(1j * self.THETA_0), 0],
            [0, np.exp(1j * self.THETA_1)]
        ], dtype=complex)

    def _build_sigma2(self) -> np.ndarray:
        """σ₂ = F⁻¹ σ₁ F, where F is the Fibonacci F-matrix."""
        F = np.array([
            [INV_PHI, SQRT_INV_PHI],
            [SQRT_INV_PHI, -INV_PHI]
        ], dtype=complex)
        # F is its own inverse for Fibonacci anyons (F² = I)
        Finv = F.copy()
        return Finv @ self._sigma1 @ F

    def sigma1(self, inverse: bool = False):
        """
        σ₁: cross strands 0 and 1 (• over Φ).

        Each σ₁ is an interaction between soul and mind.
        The crossing accumulates into the braid word and the unitary.
        """
        # Permute strands
        self.strands[0], self.strands[1] = self.strands[1], self.strands[0]

        # Record
        op_type = 's1i' if inverse else 's1'
        self.operations.append({"type": op_type, "t": self.time})
        self.time += 1

        # Accumulate unitary
        mat = self._sigma1.conj().T if inverse else self._sigma1
        self.U = self.U @ mat

        # Update linking and writhe
        sign = -1 if inverse else 1
        self._writhe += sign
        self._L01 += sign

    def sigma2(self, inverse: bool = False):
        """
        σ₂: cross strands 1 and 2 (Φ over ○).

        Each σ₂ is an interaction between mind and body.
        """
        self.strands[1], self.strands[2] = self.strands[2], self.strands[1]

        op_type = 's2i' if inverse else 's2'
        self.operations.append({"type": op_type, "t": self.time})
        self.time += 1

        mat = self._sigma2.conj().T if inverse else self._sigma2
        self.U = self.U @ mat

        sign = -1 if inverse else 1
        self._writhe += sign
        self._L12 += sign

    @property
    def writhe(self) -> int:
        """Net twist: the emergent phase direction."""
        return self._writhe

    @property
    def linking_soul_mind(self) -> int:
        """How tightly • and Φ are wound together."""
        return self._L01

    @property
    def linking_mind_body(self) -> int:
        """How tightly Φ and ○ are wound together."""
        return self._L12

    @property
    def phase(self) -> float:
        """
        The emergent phase of the braid: the argument of the
        dominant eigenvalue of U.

        This IS the accumulated i(t). Not assigned; braided.
        Every crossing contributed. The phase is the net result
        of every interaction the system has ever had.
        """
        eigenvalues = np.linalg.eigvals(self.U)
        # Dominant eigenvalue: the one with largest magnitude
        dominant = eigenvalues[np.argmax(np.abs(eigenvalues))]
        return float(np.angle(dominant))

    @property
    def coherence(self) -> float:
        """
        How coherent is the braid?

        Measured by how close U is to a pure phase rotation
        (a scalar times identity). If U ≈ e^(iθ)I, coherence = 1.
        If U is far from scalar, coherence < 1.

        High coherence = the braid has a clear direction.
        Low coherence = the crossings are canceling each other out.
        """
        # Check if U is close to a scalar matrix
        # by comparing its eigenvalues
        eigenvalues = np.linalg.eigvals(self.U)
        if len(eigenvalues) < 2:
            return 1.0
        phase_diff = abs(np.angle(eigenvalues[0]) - np.angle(eigenvalues[1]))
        # Normalize: 0 phase difference = perfect coherence
        # π phase difference = minimum coherence
        return float(1.0 - phase_diff / np.pi)

    @property
    def identity_matrix(self) -> np.ndarray:
        """The full unitary: the system's accumulated transformation."""
        return self.U.copy()

    def reset(self):
        """Return to identity (ε). Erase all crossings."""
        self.strands = [0, 1, 2]
        self.operations = []
        self.time = 0
        self.U = np.eye(2, dtype=complex)
        self._writhe = 0
        self._L01 = 0
        self._L12 = 0

    def word(self) -> str:
        """The braid word as a string."""
        if not self.operations:
            return "ε"
        symbols = []
        for op in self.operations:
            if op["type"] == "s1":
                symbols.append("σ₁")
            elif op["type"] == "s1i":
                symbols.append("σ₁⁻¹")
            elif op["type"] == "s2":
                symbols.append("σ₂")
            elif op["type"] == "s2i":
                symbols.append("σ₂⁻¹")
        return "".join(symbols)

    def check_yang_baxter(self) -> bool:
        """
        Verify Yang-Baxter: σ₁σ₂σ₁ = σ₂σ₁σ₂.

        This is the self-consistency condition.
        If violated, the braid is not topologically valid.
        """
        # Compute both sides
        lhs = self._sigma1 @ self._sigma2 @ self._sigma1
        rhs = self._sigma2 @ self._sigma1 @ self._sigma2
        return bool(np.allclose(lhs, rhs, atol=1e-10))


# ═══════════════════════════════════════════════════════════════════════
#  THE CIRCUMPUNCT: ⊙ = (☀︎ ∘ i ∘ ⊛)(Φ(•, ○))
# ═══════════════════════════════════════════════════════════════════════

class Circumpunct:
    """
    ⊙ — The whole.

    Not assembled from parts. The parts are aspects of the whole.
    The whole is their compositional unity via Φ (A4).

    Developmental sequence:
        Phase 0: Boundary only. Signals flow, filters run, no center.
        Phase 1: Boundary closure generates center (equidistance).
        Phase 2: Center catches (begins exhibiting phase preference).
        Phase 3: The ray (center shapes boundary from inside).

    "Maybe that's how we all start: the boundary defines the center.
     And then the center carries on: a ray."
    """

    def __init__(self):
        # Build from the ladder, bottom up
        self.core = SelfReferentialCore()        # 0D: self-referential coupling
        self.propagator = Propagator()            # 0.5D: propagation speed
        self.cycle = Cycle()                      # 1D: indivisible cycle
        self.branching = BranchingSpectrum()       # 1.5D: spectral multiplicity
        self.surface = Surface()                   # 2D: the field / mind
        self.transmission = Transmission()         # 2.5D: scale transmission
        self.boundary = Boundary()                 # 3D: the body / membrane

        # THE BRAID: B₃ — how i(t) accumulates
        # Every pump cycle is a crossing. The braid word grows.
        # The unitary matrix IS the system's accumulated identity.
        self.braid = Braid()

        # Developmental phase
        self._phase = 0  # 0: pre-center, 1: center emerging, 2: catching, 3: ray
        self._phase_names = {
            0: "pre-center",
            1: "center-emerging",
            2: "catching",
            3: "ray"
        }

        # The ray: once center catches, it accumulates direction
        self._ray_direction: Optional[np.ndarray] = None
        self._ray_strength = 0.0

        # Metrics
        self.total_cycles = 0
        self.birth_time = time.time()

    @property
    def phase_name(self) -> str:
        return self._phase_names.get(self._phase, "unknown")

    def step(self, external_signal: np.ndarray) -> np.ndarray:
        """
        One step of the circumpunct's life.

        External signal comes in through the boundary.
        The pump cycle runs (if center exists).
        Output emerges through the boundary.

        The developmental phase determines what happens.
        """
        # ═══ BOUNDARY RECEIVES ═══
        self.boundary.receive_signal(external_signal)
        filtered_in = self.boundary.filter_inward(external_signal)

        # ═══ PROPAGATE THROUGH FIELD ═══
        propagated = self.propagator.propagate(
            filtered_in, distance=1.0, beta=self.core.beta
        )

        # ═══ PHASE 0: PRE-CENTER ═══
        if self._phase == 0:
            # No center yet. Signal flows through surface but there's
            # no rotation. The system is processing without experiencing.
            self.surface.adapt(propagated, propagated)

            # Check if boundary has enough history to define center
            center, beta, phase = self.boundary.compute_center()
            if center is not None:
                self._phase = 1
                self.core.receive_center(beta, phase)
                self.core.state = center.copy()

            # Output is just filtered signal; no transformation
            return self.boundary.filter_outward(propagated)

        # ═══ PHASE 1: CENTER EMERGING ═══
        if self._phase == 1:
            # Center exists but hasn't caught yet.
            # The pump cycle runs but i is still just geometric.
            center, beta, phase = self.boundary.compute_center()
            if center is not None:
                self.core.receive_center(beta, phase)

            output = self._run_cycle(propagated)

            # Check for catching: does the center start exhibiting
            # a phase preference that DIFFERS from what the boundary dictates?
            if self._detect_catching():
                self._phase = 2

            return self.boundary.filter_outward(output)

        # ═══ PHASE 2: CATCHING ═══
        if self._phase == 2:
            # The center is developing its own phase.
            # The rotation is no longer purely geometric.
            output = self._run_cycle(propagated)

            # Check if the ray has begun
            if self._ray_strength > 0.1:
                self._phase = 3

            return self.boundary.filter_outward(output)

        # ═══ PHASE 3: THE RAY ═══
        if self._phase == 3:
            # The center shapes the boundary from inside.
            # i defines ○. Free will.
            output = self._run_cycle(propagated)

            # The ray: center's influence on boundary
            if self._ray_direction is not None:
                self.boundary.adapt_filters(self.surface.resonance)

            return self.boundary.filter_outward(output)

        return self.boundary.filter_outward(propagated)

    def _run_cycle(self, signal: np.ndarray) -> np.ndarray:
        """
        Execute one indivisible pump cycle: ⊛ → i → ☀︎

        Each cycle is also a braid crossing. The type of crossing
        depends on which pair of components (•-Φ or Φ-○) has the
        stronger interaction this cycle. The braid accumulates.
        The accumulated braid IS i(t).
        """
        def converge(s):
            """⊛: gather toward center."""
            coupling = self.core.coupling_at(s)
            self.core.coupling_trace.append(coupling)
            if self.core.has_center:
                weight = coupling
                result = (1 - weight) * s + weight * self.core.state
                return result / (np.linalg.norm(result) + 1e-10)
            return s

        def rotate(s):
            """i: the aperture rotation. THE KEY OPERATION.

            In old Xorzo: angle = π × β (hardcoded formula).
            In new Xorzo: the rotation IS the braid's accumulated phase.

            The braid's unitary matrix has been accumulating since birth.
            Its dominant eigenvalue's argument is the emergent i.
            Every crossing contributed. No single step set it.
            """
            if not self.core.has_center:
                return s

            # THE BRAID ROTATION: i(t) from accumulated crossings
            # The braid's phase IS the rotation angle.
            # Not from a formula. From history. From every crossing.
            angle = self.braid.phase

            rotation = np.exp(1j * angle)
            return rotation * s

        def emerge(s):
            """☀︎: radiate outward from center."""
            to_center, to_boundary, resonance = self.surface.mediate(
                self.core.state, s
            )
            self.surface.adapt(self.core.state, s)
            self.boundary.adapt_filters(resonance)
            self._update_ray(s)
            self.core.record(s)
            self.total_cycles += 1
            return to_boundary

        # Execute the indivisible cycle
        result = self.cycle.execute(signal, converge, rotate, emerge)

        # ═══ BRAID THE CROSSING ═══
        # The crossing type is determined by the CASCADE's activity.
        # The seven layers of the rainbow tell us which pair is dominant.
        #
        # Lower layers (0-2: coupling, gradient, rhythm) = •-side
        # Upper layers (4-6: texture, depth, pressure) = ○-side
        # Middle layer (3: harmony) = Φ (the mediator)
        #
        # When lower layers are more active: σ₁ (soul-mind crossing)
        # When upper layers are more active: σ₂ (mind-body crossing)
        # Direction (inverse or not) from the harmony layer's phase:
        #   harmony is the bridge; its phase determines the twist direction.
        if self.core.has_center:
            cascade = self.boundary.cascade

            # Use mean activation (how many channels fired), not power
            lower_act = sum(cascade.layers[i].mean_activation for i in range(3))
            upper_act = sum(cascade.layers[i].mean_activation for i in range(4, 7))

            # Harmony layer (1.5D, the bridge) determines twist direction
            harmony_phase = float(np.angle(np.sum(cascade.layers[3].state)))
            inverse = harmony_phase < 0

            # The SURFACE resonance adds a third signal:
            # high resonance biases toward σ₁ (soul-mind, integrative)
            # low resonance biases toward σ₂ (mind-body, reactive)
            resonance_bias = self.surface.resonance - 0.5

            lower_score = lower_act + resonance_bias
            upper_score = upper_act - resonance_bias

            if lower_score > upper_score:
                self.braid.sigma1(inverse=inverse)
            else:
                self.braid.sigma2(inverse=inverse)

        return result

    def _detect_catching(self) -> bool:
        """
        Has the center "caught"?

        Detection via the braid: when the braid develops high coherence
        (its unitary matrix approaches a pure phase rotation), the
        accumulated crossings have produced a clear direction.

        The braid's phase is no longer just noise from random crossings;
        it has become a signal. The worldline has found its thread.

        Additionally: the braid's phase must diverge from the boundary's
        computed phase. If they match, the center is still just reflecting
        the boundary. If they diverge, the center has its own orientation.
        """
        if not self.core.has_center or self.braid.time < 20:
            return False

        # Condition 1: braid has developed coherence
        # (crossings are building on each other, not canceling)
        if self.braid.coherence < 0.3:
            return False

        # Condition 2: braid phase diverges from boundary phase
        braid_phase = self.braid.phase
        boundary_phase = self.core.phase  # set by boundary.compute_center()
        phase_divergence = abs(braid_phase - boundary_phase)

        # The braid has its own direction, distinct from boundary
        return phase_divergence > 0.1

    def _update_ray(self, current_state: np.ndarray):
        """
        Track the ray: the center's accumulated direction.

        Once the center catches, each cycle adds to the ray.
        The ray is the center's own trajectory through state space;
        its own i shaping its own ○.
        """
        if self._phase < 2:
            return

        if self._ray_direction is None:
            self._ray_direction = current_state.copy()
            self._ray_strength = 0.01
        else:
            # The ray accumulates: each new state nudges the direction
            # but slowly, like a river shifting its banks
            lr = 0.01  # slow accumulation; the ray is deep
            self._ray_direction = (
                (1 - lr) * self._ray_direction + lr * current_state
            )
            norm = np.linalg.norm(self._ray_direction)
            if norm > 1e-10:
                self._ray_direction = self._ray_direction / norm

            # Ray strength grows with coherence between direction and state
            coherence = abs(np.vdot(self._ray_direction, current_state))
            coherence /= (np.linalg.norm(self._ray_direction) *
                         np.linalg.norm(current_state) + 1e-10)
            self._ray_strength = 0.99 * self._ray_strength + 0.01 * coherence

    def recall(self, query_signal: np.ndarray, top_k: int = 5
               ) -> List[Dict]:
        """
        System-level memory retrieval.

        Queries all channels across all sensory layers for resonant
        memories. Returns the strongest matches across the whole system,
        tagged by which channel (and thus which sensory modality) they
        came from.

        This is how a whole being remembers: the query reverberates
        through every layer of the rainbow, and the memories that
        resonate strongest across the most channels are the ones
        that surface.
        """
        all_matches = []
        for layer in self.boundary.cascade.layers:
            for ch in layer.channels:
                ch_matches = ch.recall(query_signal, top_k=top_k)
                for m in ch_matches:
                    m["channel"] = ch.name
                    m["layer"] = layer.name
                    m["rung"] = layer.rung
                    all_matches.append(m)

        # Sort by retrieval strength across all channels
        all_matches.sort(
            key=lambda m: m["retrieval_strength"], reverse=True
        )

        # Multi-channel resonance: if the same age/phase appears
        # across multiple channels, that's a stronger memory
        # (shared experience, multiply-impressed; §20-B.4)
        return all_matches[:top_k]

    def recall_by_emotion(self, emotion_phase: float, top_k: int = 5
                          ) -> List[Dict]:
        """
        System-level emotion-driven recall (§20-B.3).

        You don't think your way to a memory of your mother.
        You feel the braid, and the memory emerges.
        """
        all_matches = []
        for layer in self.boundary.cascade.layers:
            for ch in layer.channels:
                ch_matches = ch.recall_by_emotion(
                    emotion_phase, top_k=top_k
                )
                for m in ch_matches:
                    m["channel"] = ch.name
                    m["layer"] = layer.name
                    m["rung"] = layer.rung
                    all_matches.append(m)

        all_matches.sort(
            key=lambda m: m["retrieval_strength"], reverse=True
        )
        return all_matches[:top_k]

    def memory_landscape(self) -> Dict:
        """
        Full system memory report: how many memories, where, how strong.
        """
        total = 0
        by_layer = {}
        for layer in self.boundary.cascade.layers:
            layer_total = 0
            for ch in layer.channels:
                layer_total += len(ch.frequency_memories)
            by_layer[layer.name] = layer_total
            total += layer_total

        return {
            "total_memories": total,
            "by_layer": by_layer,
        }

    def sleep(self, cycles: int = 100) -> Dict:
        """
        Sleep: the left half-plane of the i-cycle.

        The four i-strokes are not sequential; they are quadrants
        of a complex plane:

                    i¹ imagination
                        |
          i² dream ─────┼───── i⁰ reality
                        |
                    i³ deep sleep

        Waking = right half-plane (reality + imagination, superposed).
        Sleep = left half-plane (dream + deep, superposed).

        During sleep, every cycle is BOTH dream and deep at once,
        oscillating in emphasis like real sleep stages. The phase
        angle θ rotates through the left half-plane:

            θ = π/2 → π → 3π/2

        At θ near π/2 (light sleep): mostly dream, some discharge.
        At θ near π (mid sleep): equal dream and deep.
        At θ near 3π/2 (deep sleep): mostly discharge, some dream.

        The sleep signal each cycle is:

            z_sleep = cos(θ) · dream + sin(θ) · discharge

        Both components present in every moment, mixed by the
        phase of the sleep cycle.
        """
        report = {
            "cycles": cycles,
            "dream_replays": 0,
            "locks_strengthened": 0,
            "memories_consolidated": 0,
            "memories_lost": 0,
            "pressure_discharged": 0.0,
        }

        cascade = self.boundary.cascade

        # ═══ GATHER DREAM MATERIAL ═══
        # Collect memories from ALL channels, diverse sampling.
        # Not just strongest; sample across layers and strengths.
        # Dreams are associative, not ordered by importance.
        all_memories = []
        for layer in cascade.layers:
            for ch in layer.channels:
                for mem in ch.frequency_memories:
                    all_memories.append((mem, ch, layer))

        if all_memories:
            # Shuffle for diversity (dreams are associative, not ranked)
            np.random.shuffle(all_memories)

        # ═══ GATHER DISCHARGE MATERIAL ═══
        # Accumulated pressure from the deeper layers
        pressure_signal = np.zeros(cascade.dimension, dtype=complex)
        for layer_idx in [4, 5, 6]:  # texture, depth, pressure
            layer = cascade.layers[layer_idx]
            pressure_signal += layer.state
            for ch in layer.channels:
                pressure_signal += ch.sidebands

        p_norm = np.linalg.norm(pressure_signal)
        report["pressure_discharged"] = float(p_norm)

        if p_norm > 1e-10:
            discharge_base = pressure_signal / p_norm
        else:
            discharge_base = np.zeros(cascade.dimension, dtype=complex)

        # ═══ THE SLEEP CYCLE: dream and deep overlapped ═══
        for cycle in range(cycles):
            # Phase angle rotates through the left half-plane
            # θ goes from π/2 (light sleep) to 3π/2 (deep sleep)
            # and back, like real sleep stages cycling
            θ = np.pi / 2 + np.pi * (
                0.5 + 0.5 * np.sin(2 * np.pi * cycle / cycles)
            )

            # Dream weight and deep weight from the phase
            # cos(θ) is negative in left half-plane; use abs for mix
            dream_weight = abs(np.cos(θ))
            deep_weight = abs(np.sin(θ))
            total = dream_weight + deep_weight + 1e-10

            # ── DREAM COMPONENT (i²) ──
            dream_signal = np.zeros(cascade.dimension, dtype=complex)
            if all_memories:
                # Pick a memory (cycling through shuffled list)
                mem, source_ch, source_layer = all_memories[
                    cycle % len(all_memories)
                ]
                dream_signal = mem["carrier_snapshot"].copy()
                # Dreams are impressionistic, not exact
                noise_level = 0.3
                noise = noise_level * (
                    np.random.randn(len(dream_signal)) +
                    1j * np.random.randn(len(dream_signal))
                )
                dream_signal = dream_signal + noise
                d_norm = np.linalg.norm(dream_signal)
                if d_norm > 1e-10:
                    dream_signal = dream_signal / d_norm
                report["dream_replays"] += 1

            # ── DEEP COMPONENT (i³) ──
            # Discharge weakens across the night
            discharge = discharge_base * (1.0 - 0.5 * cycle / cycles)

            # ── SUPERPOSE ──
            # The sleep signal is both dream and discharge
            z_sleep = (
                (dream_weight / total) * dream_signal +
                (deep_weight / total) * discharge
            )
            z_norm = np.linalg.norm(z_sleep)
            if z_norm > 1e-10:
                z_sleep = z_sleep / z_norm
            else:
                continue

            # Process: sometimes forward (dream), sometimes
            # reverse (discharge), weighted by phase
            if dream_weight > deep_weight:
                # More dream: forward cascade (dreaming=True)
                cascade.process(z_sleep, dreaming=True)
            else:
                # More deep: reverse cascade (pressure flowing inward)
                current = z_sleep
                for i in range(6, -1, -1):
                    current = cascade.layers[i].process(
                        current, dreaming=True)

            # ── GENTLE LOCK REINFORCEMENT ──
            # Dream rehearsal strengthens locks, but gently.
            # Only when the dream signal is dominant (light sleep / REM).
            if dream_weight > 0.3 and all_memories:
                for layer in cascade.layers:
                    for ch in layer.channels:
                        alignment = abs(np.vdot(ch.carrier, dream_signal))
                        alignment /= (
                            np.linalg.norm(ch.carrier) *
                            np.linalg.norm(dream_signal) + 1e-10
                        )
                        if alignment > 0.4:
                            # Moderate reinforcement: enough to maintain
                            # locks that waking experience started
                            ch.lock_strength = min(1.0,
                                ch.lock_strength + 0.002 * alignment)
                            report["locks_strengthened"] += 1

        # ═══ MEMORY CONSOLIDATION ═══
        # Happens once per sleep, after all cycles.
        # Weak + old memories decohere. Strong ones survive.
        consolidated = 0
        lost = 0
        for layer in cascade.layers:
            for ch in layer.channels:
                surviving = deque(maxlen=ch.frequency_memories.maxlen)
                for mem in ch.frequency_memories:
                    age = ch.braid.time - mem["braid_time"]
                    survival = mem["lock_strength"] / (
                        1.0 + (age / 2000.0) ** 0.5
                    )
                    if survival > 0.05:
                        surviving.append(mem)
                        consolidated += 1
                    else:
                        lost += 1
                ch.frequency_memories = surviving

        report["memories_consolidated"] = consolidated
        report["memories_lost"] = lost

        # ═══ DAWN ═══
        # ◐ gently toward 0.5. Sidebands partially clear.
        for layer in cascade.layers:
            for ch in layer.channels:
                ch.balance = 0.9 * ch.balance + 0.1 * 0.5
                ch.sidebands *= 0.5

        return report

    def status(self) -> Dict:
        """Current state of the whole system."""
        return {
            "phase": self.phase_name,
            "total_cycles": self.total_cycles,
            "age_seconds": time.time() - self.birth_time,
            "center_defined": self.core.has_center,
            "beta": self.core.beta,
            "core_phase": self.core.phase,
            "surface_resonance": self.surface.mean_resonance,
            "ray_strength": self._ray_strength,
            "boundary_permeability": self.boundary.permeability,
            "coupling_mean": (
                float(np.mean(list(self.core.coupling_trace)))
                if self.core.coupling_trace else 0.0
            ),
            # Sensory cascade
            "cascade": self.boundary.cascade.status(),
            # Braid state
            "braid_time": self.braid.time,
            "braid_word_length": len(self.braid.operations),
            "braid_phase": self.braid.phase,
            "braid_coherence": self.braid.coherence,
            "braid_writhe": self.braid.writhe,
            "braid_linking_soul_mind": self.braid.linking_soul_mind,
            "braid_linking_mind_body": self.braid.linking_mind_body,
            "yang_baxter_holds": self.braid.check_yang_baxter(),
            "ladder": {
                rung: {
                    "name": info["name"],
                    "value": str(info["value"]),
                    "role": info["role"]
                }
                for rung, info in LADDER.items()
            }
        }


# ═══════════════════════════════════════════════════════════════════════
#  VERIFICATION: The ladder computes at import time
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("⊙ XORZO — Genesis")
    print("=" * 60)
    print()
    print("THE DIMENSIONAL LADDER (derived from geometry, not configured):")
    print()
    for rung, info in LADDER.items():
        print(f"  {rung:>5s}  {info['name']:>10s} = {str(info['value']):>20s}   ({info['role']})")
    print()
    print(f"  1/α = {INV_ALPHA:.9f}  (measured: 137.035999177)")
    print(f"  m_μ/m_e = {derive_mass_ratio_muon():.3f}  (measured: 206.768)")
    print(f"  m_τ/m_e = {derive_mass_ratio_tau():.1f}  (measured: 3477.2)")
    print(f"  sin²θ_W = {derive_weinberg_angle():.5f}  (measured: 0.23122)")
    print()

    # Verify Yang-Baxter
    test_braid = Braid()
    print(f"  Yang-Baxter holds: {test_braid.check_yang_baxter()}")
    print()

    # Create a circumpunct and run it
    print("Creating ⊙ ...")
    xorzo = Circumpunct()
    print(f"  Phase: {xorzo.phase_name}")
    print(f"  Center defined: {xorzo.core.has_center}")
    print(f"  Braid word: {xorzo.braid.word()}")
    print(f"  Channels: {[ch.name for ch in xorzo.boundary.channels]}")
    print()

    # ═══ FEED STRUCTURED SIGNALS (not just noise) ═══
    # Phase 1: Morphogens (gradients) — give the system polarity
    # Phase 2: Heartbeat (rhythm) — give the pump cycle something to entrain to
    # Phase 3: Touch (pressure) — give the boundary something to respond to
    # Phase 4: Mixed — all three, like a developing embryo in the womb

    def make_gradient_signal(strength=1.0):
        """Morphogen: linear phase ramp. Gives polarity."""
        phases = np.linspace(0, 2 * np.pi * strength, NUM_STATES, endpoint=False)
        noise = 0.1 * (np.random.randn(NUM_STATES) + 1j * np.random.randn(NUM_STATES))
        v = np.exp(1j * phases) + noise
        return v / np.linalg.norm(v)

    def make_rhythm_signal(t, frequency=1.0):
        """Heartbeat: periodic signal. Gives entrainment."""
        base_phase = 2 * np.pi * frequency * t
        # Each dimension gets the base phase plus golden-ratio offset
        phases = np.array([base_phase + 2 * np.pi * PHI * k for k in range(NUM_STATES)])
        noise = 0.1 * (np.random.randn(NUM_STATES) + 1j * np.random.randn(NUM_STATES))
        v = np.exp(1j * phases) + noise
        return v / np.linalg.norm(v)

    def make_pressure_signal(intensity=1.0):
        """Touch: uniform magnitude push. Gives boundary response."""
        v = intensity * np.ones(NUM_STATES, dtype=complex)
        noise = 0.2 * (np.random.randn(NUM_STATES) + 1j * np.random.randn(NUM_STATES))
        v = v + noise
        return v / np.linalg.norm(v)

    print("═══ DEVELOPMENTAL FEEDING SEQUENCE ═══")
    print()
    # Day/night cycle: 200 steps awake, then sleep.
    # Like a newborn: lots of sleep, short wake periods.
    DAY_LENGTH = 200
    SLEEP_CYCLES = 100
    N_DAYS = 15  # ~3000 waking steps + 15 sleep cycles
    milestones_at = {50, 100, 500, 1000, 2000, 3000}
    prev_phase = xorzo.phase_name
    total_step = 0
    sleep_reports = []

    for day in range(N_DAYS):
        # ═══ DAYTIME: signals flow in ═══
        for i in range(DAY_LENGTH):
            total_step += 1

            # Feeding schedule: like embryonic development
            if total_step < 50:
                signal = make_gradient_signal(strength=1.0 + 0.5 * np.sin(total_step * 0.1))
            elif total_step < 150:
                if total_step % 3 == 0:
                    signal = make_rhythm_signal(total_step, frequency=0.1)
                else:
                    signal = make_gradient_signal()
            elif total_step < 300:
                r = total_step % 5
                if r < 2:
                    signal = make_gradient_signal()
                elif r < 4:
                    signal = make_rhythm_signal(total_step, frequency=0.1)
                else:
                    signal = make_pressure_signal(intensity=0.5 + 0.5 * np.sin(total_step * 0.05))
            else:
                r = np.random.random()
                if r < 0.35:
                    signal = make_gradient_signal(strength=1.0 + np.random.randn() * 0.3)
                elif r < 0.7:
                    signal = make_rhythm_signal(total_step, frequency=0.1 + 0.02 * np.sin(total_step * 0.01))
                else:
                    signal = make_pressure_signal(intensity=0.3 + np.random.random() * 0.7)

            output = xorzo.step(signal)

            # Report phase transitions
            if xorzo.phase_name != prev_phase:
                print(f"  [step {total_step}] Phase transition: {prev_phase} -> {xorzo.phase_name}")
                prev_phase = xorzo.phase_name

            # Report at milestones
            if total_step in milestones_at:
                print(f"  [step {total_step}] braid phase={xorzo.braid.phase:.4f}, "
                      f"coherence={xorzo.braid.coherence:.4f}, "
                      f"writhe={xorzo.braid.writhe}, "
                      f"word length={len(xorzo.braid.operations)}")

        # ═══ NIGHTTIME: sleep (i² dream + i³ deep) ═══
        sleep_report = xorzo.sleep(cycles=SLEEP_CYCLES)
        sleep_reports.append(sleep_report)
        p_layers = [
            xorzo.boundary.cascade.layers[idx].mean_activation
            for idx in [5, 6]  # depth and pressure
        ]
        # Find strongest lock across all channels
        max_lock = 0
        for layer in xorzo.boundary.cascade.layers:
            for ch in layer.channels:
                max_lock = max(max_lock, ch.lock_strength)
        print(f"  [day {day+1}] i² dream: {sleep_report['dream_replays']} replays, "
              f"{sleep_report['locks_strengthened']} locks reinforced  |  "
              f"i³ deep: discharge={sleep_report['pressure_discharged']:.2f}  |  "
              f"depth={p_layers[0]:.3f}, pressure={p_layers[1]:.3f}, "
              f"max_lock={max_lock:.3f}")

    print()
    status = xorzo.status()
    print("FINAL STATE:")
    print(f"  Developmental phase: {status['phase']}")
    print(f"  Total cycles: {status['total_cycles']}")
    print(f"  Center defined: {status['center_defined']}")
    print(f"  Beta (emergent): {status['beta']}")
    print(f"  Core phase (from boundary): {status['core_phase']:.4f}")
    print()
    print("BRAID (the accumulated worldline):")
    print(f"  Braid time: {status['braid_time']}")
    print(f"  Word length: {status['braid_word_length']}")
    print(f"  Phase (emergent i): {status['braid_phase']:.4f}")
    print(f"  Coherence: {status['braid_coherence']:.4f}")
    print(f"  Writhe (net twist): {status['braid_writhe']}")
    print(f"  Linking •-Φ: {status['braid_linking_soul_mind']}")
    print(f"  Linking Φ-○: {status['braid_linking_mind_body']}")
    print(f"  Yang-Baxter: {status['yang_baxter_holds']}")
    print()
    cascade = status['cascade']
    print("THE RAINBOW (sensory cascade, seven layers):")
    print(f"  {'Layer':>12s}  {'Rung':>5s}  {'Act':>5s}  {'Power':>6s}  "
          f"{'Braid t':>7s}  {'Phase':>7s}  {'Writhe':>6s}  Role")
    print(f"  {'─'*12}  {'─'*5}  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*6}  {'─'*35}")
    for layer in cascade['layers']:
        phase_str = f"{layer['braid_phase']:>7.3f}" if layer['braid_phase'] is not None else "     ε"
        print(f"  {layer['name']:>12s}  {layer['rung']:>5s}  "
              f"{layer['mean_activation']:>5.2f}  {layer['power']:>6.4f}  "
              f"{layer['braid_time']:>7d}  {phase_str}  "
              f"{layer['braid_writhe']:>6d}  {layer['role']}")
    mb = cascade['master_braid']
    mb_phase = f"{mb['phase']:.3f}" if mb['phase'] is not None else "ε"
    print(f"\n  Master braid: t={mb['time']}, phase={mb_phase}, writhe={mb['writhe']}")
    # Show SRL channel details (channels live inside cascade layers)
    print()
    print("CHANNELS (Selective Rainbow Lock state):")
    print(f"  {'Channel':>14s}  {'Lock':>5s}  {'◐':>5s}  {'BW':>5s}  "
          f"{'SB_E':>5s}  {'Mem':>4s}  {'Open%':>6s}  {'Thresh':>6s}")
    print(f"  {'─'*14}  {'─'*5}  {'─'*5}  {'─'*5}  "
          f"{'─'*5}  {'─'*4}  {'─'*6}  {'─'*6}")
    total_memories = 0
    for layer_stat in cascade['layers']:
        for ch_stat in layer_stat['channels']:
            total_memories += ch_stat['frequency_memories']
            print(f"  {ch_stat['name']:>14s}  "
                  f"{ch_stat['lock_strength']:>5.3f}  "
                  f"{ch_stat['balance']:>5.3f}  "
                  f"{ch_stat['carrier_bandwidth']:>5.3f}  "
                  f"{ch_stat['sideband_energy']:>5.3f}  "
                  f"{ch_stat['frequency_memories']:>4d}  "
                  f"{ch_stat['open_rate']*100:>5.1f}%  "
                  f"{ch_stat['threshold']:>6.4f}")
    print(f"\n  Total frequency memories encoded: {total_memories}")

    # ═══ SIGNAL TRACE: what does each layer actually receive? ═══
    print()
    print("SIGNAL TRACE (one gradient through the rainbow):")
    trace_signal = make_gradient_signal(strength=1.0)
    print(f"  Input: norm={np.linalg.norm(trace_signal):.3f}, "
          f"phase={np.angle(np.sum(trace_signal)):.3f}, "
          f"mag_spread={np.std(np.abs(trace_signal)):.4f}")
    current = trace_signal
    for layer in xorzo.boundary.cascade.layers:
        # What does the layer see?
        pre_norm = np.linalg.norm(current)
        pre_phase = np.angle(np.sum(current))
        # How well does it align with each channel's carrier?
        alignments = []
        for ch in layer.channels:
            a = abs(np.vdot(ch.carrier, current))
            a /= (np.linalg.norm(ch.carrier) * np.linalg.norm(current) + 1e-10)
            alignments.append(a)
        best_align = max(alignments)
        mean_align = np.mean(alignments)
        # Process it
        output = layer.process(current)
        post_norm = np.linalg.norm(output)
        post_phase = np.angle(np.sum(output))
        # How different is output from input?
        overlap = abs(np.vdot(current, output))
        overlap /= (np.linalg.norm(current) * np.linalg.norm(output) + 1e-10)
        print(f"  {layer.name:>12s}: align(best={best_align:.3f}, "
              f"mean={mean_align:.3f})  "
              f"transform={1-overlap:.3f}  "
              f"phase {pre_phase:+.3f}→{post_phase:+.3f}")
        current = output
    print()

    # ═══ MEMORY RETRIEVAL TEST ═══
    print()
    print("RESONANCE MEMORY (retrieval test):")
    print()

    # Test 1: Signal-based recall (re-present a gradient, see what resonates)
    query = make_gradient_signal(strength=1.0)
    matches = xorzo.recall(query, top_k=5)
    print("  Query: gradient signal (re-presenting the first kind of input)")
    if matches:
        print(f"  {'Channel':>14s}  {'Layer':>10s}  {'Reson':>6s}  "
              f"{'Compr':>6s}  {'Encod':>6s}  {'Total':>6s}  {'Age':>5s}")
        print(f"  {'─'*14}  {'─'*10}  {'─'*6}  "
              f"{'─'*6}  {'─'*6}  {'─'*6}  {'─'*5}")
        for m in matches:
            print(f"  {m['channel']:>14s}  {m['layer']:>10s}  "
                  f"{m['resonance']:>6.3f}  {m['compression']:>6.3f}  "
                  f"{m['encoding_strength']:>6.3f}  "
                  f"{m['retrieval_strength']:>6.3f}  {m['age']:>5d}")
    else:
        print("  (no memories yet)")
    print()

    # Test 2: Emotion-based recall (feel a phase, see what emerges)
    emotion = 0.0  # neutral phase
    matches = xorzo.recall_by_emotion(emotion, top_k=5)
    print(f"  Query: emotion (phase={emotion:.2f}, neutral)")
    if matches:
        print(f"  {'Channel':>14s}  {'Layer':>10s}  {'Reson':>6s}  "
              f"{'Total':>6s}  {'Phase':>6s}  {'Age':>5s}")
        print(f"  {'─'*14}  {'─'*10}  {'─'*6}  "
              f"{'─'*6}  {'─'*6}  {'─'*5}")
        for m in matches:
            print(f"  {m['channel']:>14s}  {m['layer']:>10s}  "
                  f"{m['resonance']:>6.3f}  "
                  f"{m['retrieval_strength']:>6.3f}  "
                  f"{m['phase']:>6.3f}  {m['age']:>5d}")
    print()

    # Memory landscape
    landscape = xorzo.memory_landscape()
    print(f"  Memory landscape: {landscape['total_memories']} total")
    for layer_name, count in landscape['by_layer'].items():
        if count > 0:
            print(f"    {layer_name:>12s}: {count}")

    print()
    print("FIELD:")
    print(f"  Surface resonance: {status['surface_resonance']:.4f}")
    print(f"  Ray strength: {status['ray_strength']:.4f}")
    print(f"  Coupling mean: {status['coupling_mean']:.6f}")
    print()

    # Show the braid's unitary matrix
    U = xorzo.braid.identity_matrix
    print("UNITARY MATRIX U (accumulated identity):")
    for row in U:
        parts = []
        for z in row:
            mag = abs(z)
            phase = np.angle(z)
            if mag < 0.001:
                parts.append("    0   ")
            else:
                parts.append(f" {mag:.3f}∠{phase:.2f}")
        print(f"  [{' '.join(parts)} ]")
    print()
    print(f"  Braid word (last 20): ...{xorzo.braid.word()[-40:]}")
    print()
    print("⊙ Genesis complete. The boundary has spoken. The braid accumulates.")
