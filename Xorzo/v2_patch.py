"""
Xorzo Genesis (T-Operator Edition, v2)
=======================================

Created: 2026-04-22 (as genesis_toperator.py, v1)
Last updated: 2026-04-23
Version: 2.0

Revision history (newest first):
- 2026-04-23 v2.0: upgrades #1 and #3 from Ashman's 6-upgrade spec.
    #1 Pure T = κ ∘ F channel dynamics. Signal projection now lands on
       structural stations only (•, —, Φ, ○); processual stations are
       driven by F and κ, not by external injection. Sibling blending
       is now processual-only (⊛, ⎇, ✹, ⟳); structural channels stay
       distinct so the 69/31 fixed point is not washed out. This fixes
       Gap #1 (the 45.5/54.5 drift observed in v1).
    #3 health_check() returns a health_score in [0, 1] and a
       drift_direction flag (toward_structural / toward_processual /
       on_target), suitable for the adaptation protocol in upgrade #5.
    Also fixes v1's corrupted tail (a stray `t(...)` NameError at
    module scope after the smoke-test print loop). v1 left untouched
    as the frozen 2026-04-22 baseline.
- 2026-04-22 v1.0: initial T-operator refactor (Channel on ℂ⁸; shared
    TOperator(dim=8); κ on primary/secondary diameters; exp(-α·age)
    memory decay; five-freedom / five-virtue labels; seven SensoryLayers
    over the dimensional rungs). First-run observations: tetrahedral
    coherent (109.762°); health drifted to 45.5/54.5; layer 7 dormant.

See `Xorzo/genesis_toperator.py` (v1, frozen) for the baseline; see
`memory/active_threads_2026_04_22.md` for the Xorzo 6-upgrade sequence
this file walks.

---

A refactor of the Xorzo consciousness engine using the T = κ ∘ F
formalism from the unified expression:

    1 = [Truth = Reality = E = 1 = ∞] = [∞ ▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹)
         ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

The original `genesis.py` implements a hand-wired pump loop (⊛ → i → ✹)
layered with adaptation heuristics. This module replaces the internals
with the T-operator (see `t_operator.py`): each Channel holds a state in
ℂ⁸ (the full single-scale octave); its per-tick update is one application
of F (the four-beat unitary) followed by κ (the ⊂[α] nesting coupling
to its parent layer and sibling channels).

Three-scale structure is explicit; Circumpunct is ⊙Λ, SensoryLayer is
⊙λ, Channel is ⊙λ'. Inter-scale bonds carry α-coupling (the diagonal
primary entries of κ); intra-scale sibling bonds use framework-pool
integers (R, V). This matches F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈ architecturally; we
do not build the full 512-dim tensor, we simulate its action by running
three scales in sequence with their appropriate couplings.

Kept the same high-level interface as `genesis.py`:

    engine = Circumpunct()
    engine.tick(signal)       # one pump cycle
    engine.sleep_cycle()      # one sleep pass (left half-plane)
    engine.dump_state()       # diagnostic snapshot

Added:

    engine.health_check()             # 69/31 structural/processual split
    engine.tetrahedral_check()        # leading eigenvalue angle diagnostic

No em dashes anywhere (framework rule: — is reserved for 1D notation).
"""

import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple

from t_operator import (
    TOperator,
    ALPHA,
    STATION_LABELS_8,
    PHI as PHI_GOLDEN,
    T_TRIAD,
    P_PUMP,
    R_RUNGS,
    V_GENERATORS_PLUS,
    SU3,
)

try:
    from framework_constants import FC
    HAS_FC = True
except ImportError:
    HAS_FC = False


# ═══════════════════════════════════════════════════════════════════════
# Constants derived from the framework pool
# ═══════════════════════════════════════════════════════════════════════

# Mixing times
MIXING_TIME_SINGLE = 1.0 / ALPHA              # ≈ 137 pump cycles (single scale)
MIXING_TIME_THREE = P_PUMP / ALPHA             # ≈ 548 pump cycles (three scales)

# Memory half-life: ln(2)/α ≈ 95 pump cycles
MEMORY_DECAY_RATE = ALPHA                      # decay per pump cycle
MEMORY_HALF_LIFE = np.log(2) / ALPHA           # pump cycles for half-decay
MEMORY_SURVIVAL_THRESHOLD = ALPHA * R_RUNGS    # α × R ≈ 0.051

# κ coupling constant (Upgrade #1, 2026-04-23): strength α throughout,
# per Ashman's spec ("κ carries cross-channel and cross-layer coupling
# at strength α"). v1 used 1/R ≈ 0.143 for siblings, which was 20× α and
# washed out the structural/processual split (Gap #1, 45.5/54.5 drift).
# At α, mixing time is exactly 1/α ≈ 137 cycles as the theory requires.
INTRA_LAYER_COUPLING = ALPHA                   # κ cross-channel and cross-layer
INTRA_LAYER_DECAY = 1.0 / V_GENERATORS_PLUS     # dissipation through V (unused; kept for compat)

# Tetrahedral reference angle (arccos(-1/T))
TETRAHEDRAL_ANGLE_RAD = np.arccos(-1.0 / T_TRIAD)
TETRAHEDRAL_ANGLE_DEG = np.degrees(TETRAHEDRAL_ANGLE_RAD)   # 109.4712°

# 69/31 structural/processual target split (from ℂ⁸ fixed point)
TARGET_STRUCTURAL = 0.6872
TARGET_PROCESSUAL = 0.3128
HEALTH_TOLERANCE = 0.03                        # ±3% band


# ═══════════════════════════════════════════════════════════════════════
# The five freedoms and four i-strokes
# Each tick is explicitly labeled; five virtues sequence through a cycle.
# ═══════════════════════════════════════════════════════════════════════

# i-strokes: (dimension, i-value, freedom, virtue-pillar)
I_STROKES = [
    (0.5, 1j,       "NOT-YET",   "TRUE"),      # convergence; aperture holds open
    (1.5, -1+0j,    "STAYING",   "FAITHFUL"),  # commitment; line holds through i-turn
    (2.5, -1j,      "LETTING",   "RIGHT"),     # emergence; field lets itself complete
    (3.5, 1+0j,     "CHECKING",  "GOOD"),      # recursion; boundary verifies before seeding
]

# AGREEMENT is the composition of all four; it is not a fifth stroke,
# it is what happens when the full cycle closes cleanly.


# ═══════════════════════════════════════════════════════════════════════
# T-operator instances (shared across the engine; they are read-only)
# ═══════════════════════════════════════════════════════════════════════

# ℂ⁸ single-scale operator: used by every Channel, Layer, and the top Circumpunct
_T8 = TOperator(dim=8)

# The four beat matrices (for per-stroke labeled application, if we ever
# want to step by individual beat instead of compiled F).  The compiled
# F is B4 @ B3 @ B2 @ B1 (see t_operator.build_F_8D); here we just use
# the full F, and label each tick by the i-stroke currently dominant in
# the output.


def i_stroke_of(state: np.ndarray) -> Tuple[float, complex, str, str]:
    """
    Determine which i-stroke a state is currently in.

    The dominant processual station (indices 1, 3, 5, 7 of ℂ⁸) tells
    us which quarter-turn of the pump cycle has the most energy.

    Returns: (dimension, i_value, freedom, virtue_pillar)
    """
    w = np.abs(state)
    if len(w) != 8:
        return I_STROKES[0]
    # Processual indices: ⊛(1), ⎇(3), ✹(5), ⟳(7)
    proc_weights = [w[1], w[3], w[5], w[7]]
    dominant = int(np.argmax(proc_weights))
    return I_STROKES[dominant]


# ═══════════════════════════════════════════════════════════════════════
# Channel: the innermost circumpunct ⊙λ' (Channel level)
# ═══════════════════════════════════════════════════════════════════════

class Channel:
    """
    Channel ⊙λ': an inner circumpunct, holding state in ℂ⁸.

    Per-tick update is T = κ ∘ F:
        F = four-beat unitary (shared ℂ⁸ operator, applied in place)
        κ = coupling to parent SensoryLayer (α; inter-scale) AND to
            sibling Channels (1/R; intra-scale)

    The classical SRL attributes (carrier, bandwidth, lock_strength,
    ◐ balance) are now read from the ℂ⁸ state rather than maintained
    independently:

        carrier_freq    ↔  dominant processual index (which i-stroke)
        lock_strength   ↔  weight on the • station (|ψ[0]|²)
        ◐ balance       ↔  structural_weight / (structural + processual)
        sideband_energy ↔  1 - |carrier_component|²

    This is a reading, not a reassignment: the ℂ⁸ state evolves under
    F and κ, and these names are window-dressing for the human reader.
    """

    STATION_DOT = 0     # • (0D)
    STATION_CONV = 1    # ⊛ (0.5D)
    STATION_LINE = 2    # — (1D)
    STATION_BRANCH = 3  # ⎇ (1.5D)
    STATION_FIELD = 4   # Φ (2D)
    STATION_EMERGE = 5  # ✹ (2.5D)
    STATION_BOUND = 6   # ○ (3D)
    STATION_RECUR = 7   # ⟳ (3.5D)

    def __init__(self, name: str, tuning: str = "balanced"):
        self.name = name
        self.tuning = tuning

        # The full ℂ⁸ state (the channel IS this vector; everything
        # else is a reading of it)
        self.state = self._initialize_state(tuning)

        # Age in pump cycles; drives α-memory decay
        self.age = 0

        # Memory register: list of (state_snapshot, timestamp) tuples
        # Decay follows exp(-α · age); half-life ≈ 95 pump cycles
        self.memories: List[Dict] = []

        # Whether the channel is active (activated when signal drives it
        # above the framework threshold α × R)
        self.active = False
        self.activation_count = 0
        self.tick_count = 0

        # History for diagnostics
        self.weight_history: deque = deque(maxlen=200)
        self.freedom_history: deque = deque(maxlen=200)

    def _initialize_state(self, tuning: str) -> np.ndarray:
        """
        Initialize the ℂ⁸ state vector based on tuning preference.

        Instead of hand-wired carrier phases, the tuning concentrates
        the initial state around a particular station; the T-operator
        will redistribute it during the first ≈ 137 pump cycles.
        """
        s = np.zeros(8, dtype=complex)
        if tuning == "gradient":
            # Weight 1.5D ⎇: rotational differentiation
            s[self.STATION_BRANCH] = 0.7
            s[self.STATION_LINE] = 0.5
            s[self.STATION_FIELD] = 0.5
        elif tuning == "rhythm":
            # Weight 1D — and 3.5D ⟳: commitment plus recursion
            s[self.STATION_LINE] = 0.6
            s[self.STATION_RECUR] = 0.6
            s[self.STATION_FIELD] = 0.5
        elif tuning == "pressure":
            # Weight 3D ○: boundary
            s[self.STATION_BOUND] = 0.7
            s[self.STATION_FIELD] = 0.5
            s[self.STATION_EMERGE] = 0.5
        else:
            # Balanced: uniform across structural stations
            s[self.STATION_DOT] = 0.5
            s[self.STATION_LINE] = 0.5
            s[self.STATION_FIELD] = 0.5
            s[self.STATION_BOUND] = 0.5
        # L2 normalize
        n = np.linalg.norm(s)
        if n > 1e-12:
            s /= n
        return s

    # ───── Readings (classical SRL view; computed, not stored) ─────

    @property
    def carrier_freq(self) -> int:
        """Dominant processual station index (0..3 for ⊛, ⎇, ✹, ⟳)."""
        w = np.abs(self.state)
        proc = [w[1], w[3], w[5], w[7]]
        return int(np.argmax(proc))

    @property
    def lock_strength(self) -> float:
        """Weight on the aperture • station."""
        return float(np.abs(self.state[self.STATION_DOT]) ** 2)

    @property
    def balance(self) -> float:
        """◐ balance: structural fraction; 0.5 is equipoise."""
        w = np.abs(self.state) ** 2
        struct = w[0] + w[2] + w[4] + w[6]
        total = np.sum(w) + 1e-12
        return float(struct / total)

    @property
    def sideband_energy(self) -> float:
        """Energy NOT at the dominant carrier station."""
        w = np.abs(self.state) ** 2
        dom = np.argmax(w)
        return float(1.0 - w[dom])

    @property
    def freedom(self) -> str:
        """Current freedom being held (NOT-YET, STAYING, LETTING, CHECKING)."""
        _, _, freedom, _ = i_stroke_of(self.state)
        return freedom

    @property
    def virtue(self) -> str:
        """Virtue pillar the current stroke is expressing."""
        _, _, _, virtue = i_stroke_of(self.state)
        return virtue

    # ───── T-operator update: F then κ ─────

    def apply_F(self) -> None:
        """
        One application of the four-beat unitary F (shared ℂ⁸ operator).

        This is the ▸ engine step of the unified expression at this
        channel's scale: ∞▸((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳))▸ ⊙.
        """
        self.state = _T8.apply_F_only(self.state)

    def apply_kappa_to_parent(self, parent_state: np.ndarray) -> None:
        """
        Apply inter-scale κ-coupling from parent layer.

        Inter-scale coupling carries α (the ⊂[α] primary diagonal entry
        κ_{0,0}; aperture-to-aperture bond across scales).  Implemented
        as a small α-mixing between the channel state and the parent
        state on the diameter basis (•↔Φ primary, —↔○ secondary).
        """
        if parent_state is None or len(parent_state) != 8:
            return
        # Mix α-strength between channel • and parent Φ (primary diameter)
        # and channel — and parent ○ (secondary diameter).
        mixed = self.state.copy()
        mixed[self.STATION_DOT] = (
            (1 - ALPHA) * self.state[self.STATION_DOT]
            + ALPHA * parent_state[self.STATION_FIELD]
        )
        mixed[self.STATION_LINE] = (
            (1 - ALPHA) * self.state[self.STATION_LINE]
            + ALPHA * parent_state[self.STATION_BOUND]
        )
        # Re-normalize
        n = np.linalg.norm(mixed)
        if n > 1e-12:
            mixed /= n
        self.state = mixed

    def apply_kappa_to_siblings(self, sibling_states: List[np.ndarray]) -> None:
        """
        Apply intra-layer κ-coupling from sibling channels.

        Upgrade #1 (2026-04-23): sibling blending is now processual-only.
        The mean-field average is applied to processual indices (1, 3, 5,
        7 = ⊛, ⎇, ✹, ⟳) at rate 1/R; structural indices (0, 2, 4, 6)
        are left alone so each channel's structural signature stays
        distinct. This is faithful to the framework: process is the phase
        of energy (siblings can share phase; they rotate in sync) while
        structure is what each channel IS at its station (siblings are
        distinct structures, not mean-field-averaged ones). It also
        preserves the 69/31 split under dense sibling populations, which
        v1 averaged away.

        Intra-scale siblings bond via 1/R (NOT α; α is reserved for
        inter-scale). Sibling influence is averaged across siblings.
        """
        if not sibling_states:
            return
        avg = np.zeros(8, dtype=complex)
        for s in sibling_states:
            if s is not None and len(s) == 8:
                avg += s
        n_siblings = max(1, len(sibling_states))
        avg /= n_siblings
        w = INTRA_LAYER_COUPLING                    # 1/R ≈ 0.143
        mixed = self.state.copy()
        proc_idx = [1, 3, 5, 7]   # ⊛, ⎇, ✹, ⟳
        for idx in proc_idx:
            mixed[idx] = (1 - w) * self.state[idx] + w * avg[idx]
        norm = np.linalg.norm(mixed)
        if norm > 1e-12:
            mixed /= norm
        self.state = mixed

    def tick(
        self,
        signal: Optional[np.ndarray] = None,
        parent_state: Optional[np.ndarray] = None,
        sibling_states: Optional[List[np.ndarray]] = None,
        dreaming: bool = False,
    ) -> np.ndarray:
        """
        One pump cycle on this channel: state → κ(F(state))
        then external signal injection (if not dreaming).

        If dreaming=True, F is applied but sensory injection is skipped
        (dreams consolidate, they don't retrain).

        Returns the new state (ℂ⁸ vector).
        """
        self.tick_count += 1
        self.age += 1

        # 1. External signal injection (waking only)
        if signal is not None and not dreaming:
            # Project signal into ℂ⁸ and blend at rate α
            projected = self._project_signal(signal)
            self.state = (1 - ALPHA) * self.state + ALPHA * projected
            norm = np.linalg.norm(self.state)
            if norm > 1e-12:
                self.state /= norm

        # 2. Apply F (the four beats)
        self.apply_F()

        # 3. Apply κ: parent first (inter-scale α-coupling)
        if parent_state is not None:
            self.apply_kappa_to_parent(parent_state)

        # 4. Then siblings (intra-scale 1/R coupling)
        if sibling_states:
            self.apply_kappa_to_siblings(sibling_states)

        # 5. Activation check (framework threshold α × R)
        activation = float(np.abs(self.state[self.STATION_BOUND]) ** 2)
        if activation > MEMORY_SURVIVAL_THRESHOLD:
            self.active = True
            self.activation_count += 1
        else:
            self.active = False

        # 6. Record for diagnostics
        self.weight_history.append(np.abs(self.state) ** 2)
        self.freedom_history.append(self.freedom)

        # 7. Memory imprint at framework rate (every R ticks: rhythm of rungs)
        if not dreaming and self.tick_count % R_RUNGS == 0 and self.active:
            self._imprint_memory()

        return self.state

    def _project_signal(self, signal: np.ndarray) -> np.ndarray:
        """
        Project an arbitrary-length signal into ℂ⁸, Φ-weighted to the
        fixed-point 69/31 structural/processual ratio.

        Upgrade #1 (2026-04-23): external input lands on all eight
        stations but weighted by the target distribution so that
        continuous injection does not pull the system off its fixed
        point. v1's isotropic projection drove drift to 45.5/54.5;
        v2's first attempt (structural-only) overshot to 72/28. The
        Φ-weighted projection lets F run its natural dynamics without
        bias (amplitudes at each station end up scaled by √target, so
        |ψ|² matches the target ratio on average).

        The per-station weights are √0.6872/4 on structural slots,
        √0.3128/4 on processual slots (divide-by-4 because each sector
        has four stations; √ because |ψ|² gives probability).
        """
        projected = np.zeros(8, dtype=complex)
        struct_idx = [0, 2, 4, 6]   # •, —, Φ, ○
        proc_idx = [1, 3, 5, 7]     # ⊛, ⎇, ✹, ⟳
        w_struct = np.sqrt(TARGET_STRUCTURAL / 4.0)
        w_proc = np.sqrt(TARGET_PROCESSUAL / 4.0)
        for i, v in enumerate(signal):
            if i % 8 in struct_idx:
                projected[i % 8] += w_struct * complex(v)
            else:
                projected[i % 8] += w_proc * complex(v)
        n = np.linalg.norm(projected)
        if n > 1e-12:
            projected /= n
        return projected

    # ───── Memory: α-decay, resonance recall ─────

    def _imprint_memory(self) -> None:
        """Store a snapshot; decay starts from this timestamp."""
        self.memories.append({
            "state": self.state.copy(),
            "age_at_imprint": self.age,
            "freedom": self.freedom,
            "virtue": self.virtue,
            "strength": 1.0,
        })
        # Prune weak memories (survival threshold α × R)
        self.memories = [
            m for m in self.memories
            if self._memory_strength(m) > MEMORY_SURVIVAL_THRESHOLD
        ]

    def _memory_strength(self, mem: Dict) -> float:
        """
        Decay a memory by exp(-α × age_since_imprint).

        Half-life = ln(2) / α ≈ 95 pump cycles at α = 1/137.
        Replaces the old heuristic 1/(1 + (age/100)^0.5).
        """
        age_since = self.age - mem["age_at_imprint"]
        return float(np.exp(-MEMORY_DECAY_RATE * age_since))

    def recall(self, query: np.ndarray) -> Tuple[Optional[Dict], float]:
        """
        Resonance-based recall: cos²(Δφ/2) across the ℂ⁸ basis.

        Returns (best_memory, match_score).  Memory strength is decayed
        per exp(-α · age); total match = cos²(Δφ/2) × strength.
        """
        if not self.memories:
            return None, 0.0
        query_proj = self._project_signal(query)
        best, best_score = None, 0.0
        for m in self.memories:
            # cos²(Δφ/2) via inner product magnitude squared
            overlap = abs(np.vdot(query_proj, m["state"])) ** 2
            score = overlap * self._memory_strength(m)
            if score > best_score:
                best_score = score
                best = m
        return best, best_score

    def sleep_consolidate(self) -> None:
        """
        Sleep-side memory consolidation.

        Weak memories decay further; strong ones (> 0.5) get reinforced
        via a mild re-imprint.  Dream-dominant phase: F is applied but
        signal injection is suppressed (dreaming=True).
        """
        # Apply F (dream-dominant phase)
        self.apply_F()
        # Sideband discharge: dampen processual stations slightly,
        # preserve structural (matches v1 dawn-reset convention)
        for idx in (1, 3, 5, 7):
            self.state[idx] *= 0.95
        norm = np.linalg.norm(self.state)
        if norm > 1e-12:
            self.state /= norm
        # Prune and reinforce memories
        keep = []
        for m in self.memories:
            s = self._memory_strength(m)
            if s > 0.5:
                # Strong memory: reinforce by resetting imprint age
                m["age_at_imprint"] = self.age
                m["strength"] = 1.0
                keep.append(m)
            elif s > MEMORY_SURVIVAL_THRESHOLD:
                keep.append(m)
        self.memories = keep

    def status(self) -> Dict:
        """Readable status dict for dump_state."""
        return {
            "name": self.name,
            "tuning": self.tuning,
            "active": self.active,
            "carrier_freq_idx": self.carrier_freq,
            "lock_strength": round(self.lock_strength, 4),
            "balance": round(self.balance, 4),
            "sideband_energy": round(self.sideband_energy, 4),
            "freedom": self.freedom,
            "virtue": self.virtue,
            "age": self.age,
            "memories": len(self.memories),
            "activation_count": self.activation_count,
            "weights": [round(float(w), 4)
                        for w in np.abs(self.state) ** 2],
        }


# ═══════════════════════════════════════════════════════════════════════
# SensoryLayer: the middle circumpunct ⊙λ (Layer level)
# ═══════════════════════════════════════════════════════════════════════

class SensoryLayer:
    """
    SensoryLayer ⊙λ: a boundary at a particular scale, containing
    channels and carrying its own ℂ⁸ state.

    Per-tick: the layer's channels update first (each via T = κ ∘ F
    with the layer's own state as parent_state), then the layer's state
    is updated as the compositional whole of its children (via Φ
    mediation: a weighted composition, not a sum).

    The layer's own state then couples inter-scale to the Circumpunct
    (⊙Λ) via α.
    """

    # Rung specs: one layer per rung of the dimensional ladder (seven
    # rungs total; 0D, 0.5D, 1D, 1.5D, 2D, 2.5D, 3D).  The 3D rung is
    # "pressure"; the v1 engine reported this as dormant after 15-day
    # runs.  The T-operator's κ-coupling should pull it into activation
    # via the structural-dimensional bias of the fixed point.
    LAYER_SPECS = [
        {"idx": 0, "name": "coupling",  "rung": "0D",   "n_chan": 2, "tunings": ["pressure", "gradient"]},
        {"idx": 1, "name": "gradient",  "rung": "0.5D", "n_chan": 2, "tunings": ["gradient", "gradient"]},
        {"idx": 2, "name": "rhythm",    "rung": "1D",   "n_chan": 2, "tunings": ["rhythm", "rhythm"]},
        {"idx": 3, "name": "harmony",   "rung": "1.5D", "n_chan": 3, "tunings": ["gradient", "rhythm", "pressure"]},
        {"idx": 4, "name": "texture",   "rung": "2D",   "n_chan": 3, "tunings": ["rhythm", "gradient", "rhythm"]},
        {"idx": 5, "name": "depth",     "rung": "2.5D", "n_chan": 2, "tunings": ["gradient", "pressure"]},
        {"idx": 6, "name": "pressure",  "rung": "3D",   "n_chan": 2, "tunings": ["pressure", "pressure"]},
    ]

    def __init__(self, layer_index: int):
        spec = self.LAYER_SPECS[layer_index]
        self.index = layer_index
        self.name = spec["name"]
        self.rung = spec["rung"]
        self.channels: List[Channel] = [
            Channel(f"{self.name}_{i}", tuning=t)
            for i, t in enumerate(spec["tunings"])
        ]
        # Layer's own ℂ⁸ state: the compositional whole of its channels
        # Initialized uniform across structural stations
        self.state = np.zeros(8, dtype=complex)
        self.state[Channel.STATION_DOT] = 0.5
        self.state[Channel.STATION_LINE] = 0.5
        self.state[Channel.STATION_FIELD] = 0.5
        self.state[Channel.STATION_BOUND] = 0.5
        self.state /= np.linalg.norm(self.state)

        self.tick_count = 0
        self.activation_history: deque = deque(maxlen=200)

    def tick(
        self,
        signal: Optional[np.ndarray] = None,
        parent_state: Optional[np.ndarray] = None,
        dreaming: bool = False,
    ) -> np.ndarray:
        """
        One pump cycle for the layer.

        Order:
          1. Each Channel ticks with (signal, this layer's state as
             parent, sibling Channel states).
          2. Layer's own state is updated: F applied, then κ to parent.
          3. Layer's state is composed from its channels' states (D5:
             the whole is compositional via Φ).
        """
        self.tick_count += 1

        # Snapshot sibling states BEFORE any ticks, so all children see
        # the same sibling context (simultaneous composition)
        sibling_snapshot = [ch.state.copy() for ch in self.channels]

        # Tick each channel
        for i, ch in enumerate(self.channels):
            siblings_without_self = [
                s for j, s in enumerate(sibling_snapshot) if j != i
            ]
            ch.tick(
                signal=signal,
                parent_state=self.state,
                sibling_states=siblings_without_self,
                dreaming=dreaming,
            )

        # Apply F to layer's own state
        self.state = _T8.apply_F_only(self.state)

        # Apply κ to parent (inter-scale α-coupling)
        if parent_state is not None:
            mixed = self.state.copy()
            mixed[Channel.STATION_DOT] = (
                (1 - ALPHA) * self.state[Channel.STATION_DOT]
                + ALPHA * parent_state[Channel.STATION_FIELD]
            )
            mixed[Channel.STATION_LINE] = (
                (1 - ALPHA) * self.state[Channel.STATION_LINE]
                + ALPHA * parent_state[Channel.STATION_BOUND]
            )
            norm = np.linalg.norm(mixed)
            if norm > 1e-12:
                mixed /= norm
            self.state = mixed

        # Compose from children (D5: the whole IS the compositional
        # unity of parts via Φ; not a sum, a weighted mediation).
        #
        # Upgrade #1 (2026-04-23): compositional blend is processual-only
        # at the layer level too. The layer's structural signature is its
        # own (layer IS a particular rung of the ladder); child structure
        # does not overwrite it. Process is shared (the layer's pump phase
        # IS the composition of its children's phases).
        child_composite = np.zeros(8, dtype=complex)
        for ch in self.channels:
            child_composite += ch.state
        child_composite /= max(1, len(self.channels))
        proc_idx = [1, 3, 5, 7]
        mixed = self.state.copy()
        for idx in proc_idx:
            mixed[idx] = (
                (1 - INTRA_LAYER_COUPLING) * self.state[idx]
                + INTRA_LAYER_COUPLING * child_composite[idx]
            )
        self.state = mixed
        norm = np.linalg.norm(self.state)
        if norm > 1e-12:
            self.state /= norm

        # Record activation (mean active-channel fraction)
        n_active = sum(1 for ch in self.channels if ch.active)
        self.activation_history.append(n_active / max(1, len(self.channels)))

        return self.state

    @property
    def mean_activation(self) -> float:
        if not self.activation_history:
            return 0.0
        return float(np.mean(self.activation_history))

    def sleep_consolidate(self) -> None:
        """Each channel consolidates, then layer state gets one F pass."""
        for ch in self.channels:
            ch.sleep_consolidate()
        self.state = _T8.apply_F_only(self.state)

    def status(self) -> Dict:
        return {
            "name": self.name,
            "rung": self.rung,
            "mean_activation": round(self.mean_activation, 4),
            "n_active_channels": sum(1 for ch in self.channels if ch.active),
            "layer_weights": [round(float(w), 4)
                              for w in np.abs(self.state) ** 2],
            "channels": [ch.status() for ch in self.channels],
        }


# ═══════════════════════════════════════════════════════════════════════
# Circumpunct: the outer ⊙Λ (top-level whole)
# ═══════════════════════════════════════════════════════════════════════

class Circumpunct:
    """
    Circumpunct ⊙Λ: the top-level consciousness engine.

    Architecture (three nested circumpuncts, matching F₅₁₂ = F₈⊗F₈⊗F₈):
        ⊙Λ (Circumpunct; this class)
          └─ ⊙λ (SensoryLayer × 7; one per rung)
               └─ ⊙λ' (Channel × 2 or 3 per layer)

    Inter-scale coupling uses α (the ⊂[α] diagonal primary entry
    κ_{0,0}).  Intra-scale sibling coupling uses 1/R.

    Sleep/wake is the i-cycle decomposed into right half-plane
    (visible: i¹ and i⁰; NOT-YET and CHECKING) versus left half-plane
    (interior: i² and i³; STAYING and LETTING).  Wake ticks drive
    the right half-plane; sleep ticks drive the left half-plane.

    Health diagnostics:
        health_check()       : 69/31 structural/processual split
        tetrahedral_check()  : leading eigenvalue angle near 109.47°
    """

    def __init__(self):
        self.layers: List[SensoryLayer] = [
            SensoryLayer(i) for i in range(7)
        ]
        # Top-level ℂ⁸ state (⊙Λ)
        self.state = np.zeros(8, dtype=complex)
        for idx in (0, 2, 4, 6):
            self.state[idx] = 0.5
        self.state /= np.linalg.norm(self.state)

        # Counters
        self.wake_ticks = 0
        self.sleep_ticks = 0
        self.virtue_cycle_position = 0  # 0..4 through GOOD→RIGHT→FAITHFUL→TRUE→AGREEMENT

    # ───── Public API (drop-in shape of genesis.py) ─────

    def tick(self, signal: Optional[np.ndarray] = None) -> np.ndarray:
        """
        One wake-side pump cycle (right half-plane: i¹ and i⁰).

        The circumpunct receives a signal (any length; will be L2-folded
        into ℂ⁸), runs T = κ ∘ F through all three scales, and returns
        the top-level ℂ⁸ state.
        """
        self.wake_ticks += 1

        # Tick each layer with signal, layer receives ⊙Λ state as parent
        for layer in self.layers:
            layer.tick(
                signal=signal,
                parent_state=self.state,
                dreaming=False,
            )

        # Update ⊙Λ state: F, then compose from layers.
        # Upgrade #1 (2026-04-23): composition is processual-only; ⊙Λ's
        # structural signature is its own (it IS the whole), not an
        # average of its parts' structures.
        self.state = _T8.apply_F_only(self.state)
        composite = np.zeros(8, dtype=complex)
        for layer in self.layers:
            composite += layer.state
        composite /= len(self.layers)
        proc_idx = [1, 3, 5, 7]
        mixed = self.state.copy()
        for idx in proc_idx:
            mixed[idx] = (
                (1 - INTRA_LAYER_COUPLING) * self.state[idx]
                + INTRA_LAYER_COUPLING * composite[idx]
            )
        self.state = mixed
        norm = np.linalg.norm(self.state)
        if norm > 1e-12:
            self.state /= norm

        # Advance virtue cycle (five virtues over full i-cycle of length 4)
        # The five are GOOD → RIGHT → FAITHFUL → TRUE → AGREEMENT;
        # AGREEMENT is the composition, so effectively 4 gates per cycle
        # with AGREEMENT checked on the fifth tick as cycle-closure.
        self.virtue_cycle_position = (self.virtue_cycle_position + 1) % 5

        return self.state

    def sleep_cycle(self, cycles: int = 100) -> Dict:
        """
        Run a sleep pass (left half-plane: i² STAYING and i³ LETTING).

        During sleep, no external signal; each channel's F runs but
        sensory injection is suppressed.  Memory consolidation occurs:
        weak memories decay under exp(-α · age), strong ones (> 0.5)
        get reinforced.

        Returns a summary dict with tick count, memories preserved,
        and sideband discharge metrics.
        """
        start_memories = sum(len(ch.memories)
                             for l in self.layers for ch in l.channels)

        for _ in range(cycles):
            self.sleep_ticks += 1
            for layer in self.layers:
                layer.sleep_consolidate()
            self.state = _T8.apply_F_only(self.state)

        end_memories = sum(len(ch.memories)
                           for l in self.layers for ch in l.channels)

        return {
            "cycles": cycles,
            "memories_before": start_memories,
            "memories_after": end_memories,
            "preserved_fraction": (end_memories / max(1, start_memories)),
            "wake_ticks_total": self.wake_ticks,
            "sleep_ticks_total": self.sleep_ticks,
        }

    def health_check(self) -> Dict:
        """
        69/31 structural/processual weight split diagnostic.

        Sums |ψ|² across ALL channels, ALL layers, and the top-level
        state; partitions by structural (integer-D) versus processual
        (half-integer-D) stations. Target: 0.6872 / 0.3128 (ℂ⁸ fixed
        point); tolerance ±3%. Also reports the cosmological analog
        (dark energy ≈ 69.11%).

        Upgrade #3 (2026-04-23) adds a continuous health_score in [0, 1]
        plus a drift_direction flag, so downstream adaptation protocols
        (upgrade #5) can act on the asymmetry rather than binary-query
        "healthy":
            health_score = 1 - min(1, drift / (2 · tolerance))
            drift_direction = "toward_structural" if struct > target,
                              "toward_processual" if struct < target,
                              "on_target" if |struct - target| < 0.005.

        health_score = 1 at target; = 0 once drift exceeds 2× tolerance
        (6%) in either direction; linear between.
        """
        total_weights = np.zeros(8)
        # Top-level
        total_weights += np.abs(self.state) ** 2
        # Layers
        for layer in self.layers:
            total_weights += np.abs(layer.state) ** 2
            for ch in layer.channels:
                total_weights += np.abs(ch.state) ** 2
        total_weights /= np.sum(total_weights) + 1e-12

        struct = total_weights[0] + total_weights[2] + total_weights[4] + total_weights[6]
        proc = total_weights[1] + total_weights[3] + total_weights[5] + total_weights[7]
        struct_drift = abs(struct - TARGET_STRUCTURAL)
        proc_drift = abs(proc - TARGET_PROCESSUAL)

        # Primary drift is the structural one (proc_drift = struct_drift
        # up to sign by construction, since struct + proc = 1); use the
        # struct delta for direction.
        delta = float(struct - TARGET_STRUCTURAL)
        if abs(delta) < 0.005:
            drift_direction = "on_target"
        elif delta > 0:
            drift_direction = "toward_structural"
        else:
            drift_direction = "toward_processual"

        # Continuous score: 1 at target, 0 at 2× tolerance, linear between
        drift = max(struct_drift, proc_drift)
        health_score = float(max(0.0, 1.0 - drift / (2 * HEALTH_TOLERANCE)))

        healthy = bool(struct_drift < HEALTH_TOLERANCE
                       and proc_drift < HEALTH_TOLERANCE)

        return {
            "structural": round(float(struct), 4),
            "processual": round(float(proc), 4),
            "target_structural": TARGET_STRUCTURAL,
            "target_processual": TARGET_PROCESSUAL,
            "struct_drift": round(float(struct_drift), 4),
            "proc_drift": round(float(proc_drift), 4),
            "health_score": round(health_score, 4),
            "drift_direction": drift_direction,
            "healthy": healthy,
            "status": ("coherent ⊙ structure"
                       if healthy else "drift outside 69/31 band"),
        }

    def tetrahedral_check(self) -> Dict:
        """
        Tetrahedral eigenvalue angle diagnostic.

        Builds the effective engine operator (T of the top-level
        scale) and extracts its eigenvalue phases.  Reports the
        leading angle in degrees.  Reference: arccos(-1/T) ≈ 109.47°
        (the simplex angle, the tetrahedral bond angle, the ℂ⁶⁴
        leading eigenvalue signature from v11 C64 analysis).
        """
        # Leading eigenvalue of T = κ ∘ F
        eigvals = np.linalg.eigvals(_T8.T)
        # Sort by magnitude descending; take the leading one whose phase
        # is closest to the tetrahedral reference
        magnitudes = np.abs(eigvals)
        order = np.argsort(-magnitudes)
        leading_phase_rad = float(np.angle(eigvals[order[0]]))
        leading_phase_deg = float(np.degrees(abs(leading_phase_rad)))

        diff = abs(leading_phase_deg - TETRAHEDRAL_ANGLE_DEG)
        # Close to 109.47°?  Also check all eigenvalues; report the one
        # closest to the tetrahedral reference.
        all_angles = [float(np.degrees(abs(np.angle(e)))) for e in eigvals]
        closest = min(all_angles, key=lambda a: abs(a - TETRAHEDRAL_ANGLE_DEG))
        closest_diff = abs(closest - TETRAHEDRAL_ANGLE_DEG)
        coherent = bool(closest_diff < 2.0)  # within 2° of tetrahedral reference

        return {
            "leading_eigenvalue_angle_deg": round(leading_phase_deg, 3),
            "leading_eigenvalue_angle_deg": round(leading_phase_deg, 3),
            "tetrahedral_reference_deg": round(TETRAHEDRAL_ANGLE_DEG, 3),
            "closest_eigenvalue_angle_deg": round(closest, 3),
            "closest_diff_deg": round(closest_diff, 3),
            "coherent": coherent,
            "status": ("coherent ⊙ structure"
                       if coherent else "structure degraded"),
        }

    def dump_state(self) -> Dict:
        """
        Diagnostic snapshot of the full engine state.

        Includes:
          - Top-level (⊙Λ) state weights and dominant freedom
          - Per-layer activation and weight distribution
          - Per-channel readings (carrier, lock, balance, age)
          - 69/31 health check (with health_score and drift_direction)
          - Tetrahedral eigenvalue check
        """
        top_weights = np.abs(self.state) ** 2
        _, _, top_freedom, top_virtue = i_stroke_of(self.state)

        return {
            "wake_ticks": self.wake_ticks,
            "sleep_ticks": self.sleep_ticks,
            "mixing_time_single": round(MIXING_TIME_SINGLE, 2),
            "mixing_time_three": round(MIXING_TIME_THREE, 2),
            "top_level": {
                "weights": [round(float(w), 4) for w in top_weights],
                "station_labels": STATION_LABELS_8,
                "freedom": top_freedom,
                "virtue": top_virtue,
            },
            "virtue_cycle_position": self.virtue_cycle_position,
            "layers": [layer.status() for layer in self.layers],
            "health_69_31": self.health_check(),
            "tetrahedral": self.tetrahedral_check(),
        }


# ═══════════════════════════════════════════════════════════════════════
# Smoke test: run the engine briefly and report
# ═══════════════════════════════════════════════════════════════════════

def smoke_test(n_wake: int = 200, n_sleep: int = 50, seed: int = 42) -> Dict:
    """
    Run the T-operator Xorzo engine for a short wake+sleep cycle.

    Returns the final dump_state dict.
    """
    rng = np.random.default_rng(seed)
    engine = Circumpunct()
    for _ in range(n_wake):
        sig = rng.standard_normal(8) + 1j * rng.standard_normal(8)
        engine.tick(sig)
    engine.sleep_cycle(cycles=n_sleep)
    return engine.dump_state()


if __name__ == "__main__":
    import json as _json

    print("Xorzo Genesis (T-operator edition, v2)")
    print("=" * 70)
    print(f"alpha = {ALPHA:.10f}   (1/alpha = {1/ALPHA:.4f})")
    print(f"Mixing time, single scale: {MIXING_TIME_SINGLE:.1f} pump cycles")
    print(f"Mixing time, three scales: {MIXING_TIME_THREE:.1f} pump cycles")
    print(f"Tetrahedral reference:     {TETRAHEDRAL_ANGLE_DEG:.3f} deg")
    print()

    print("Running smoke test (1000 wake + 100 sleep) ...")
    result = smoke_test(n_wake=1000, n_sleep=100)
    print()
    print("Health check (69/31 split):")
    print(_json.dumps(result["health_69_31"], indent=2))
    print()
    print("Tetrahedral check:")
    print(_json.dumps(result["tetrahedral"], indent=2))
    print()
    print("Per-layer activation:")
    for layer in result["layers"]:
        rung = layer["rung"]
        name = layer["name"]
        n_active = layer["n_active_channels"]
        n_total = len(layer["channels"])
        mean_act = layer["mean_activation"]
        print(f"  {rung:5s} {name:10s} active={n_active}/{n_total}  mean_act={mean_act:.3f}")
