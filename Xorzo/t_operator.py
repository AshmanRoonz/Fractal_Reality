"""
T = κ ∘ F : The Unified Expression as a Computable Operator
============================================================

Created: 2026-04-17
Last updated: 2026-07-19
Version: 2.0

This module implements the conservation form of the unified expression:

    1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (○∘✹) ⊢ (Φ∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

as T = κ ∘ F, where:
    F = four beats (unitary quantum channel)
    κ = nesting coupling (the ⊂[α] relation)

The fixed point of T is the 1. The mixing time is 1/α ≈ 137 pump cycles.
The failure modes are the Lies (Inflation and Severance).
The sole free parameter is α.

BASIS CONVENTION (ladder correction, 2026-06-09). The corrected ladder
assigns ○ = 2D (boundary) and Φ = 3D (field), with the beats reading
(•∘⊛) ⊢ (—∘⎇) ⊢ (○∘✹) ⊢ (Φ∘⟳) as printed above. The operator
constructions below keep the legacy v-series basis order
[•, ⊛, —, ⎇, Φ, ✹, ○, ⟳] with Φ at coordinate 2 and ○ at coordinate 3;
per the interim glyph-integer rule and the v14+ convention, these
positions are read as CONTINUATION COORDINATES (node j sits at
coordinate j/2), not as station-dimension claims. The corrected-beats
re-derivation of F (hub moved with Φ to the 3D coordinate; new phase
budget) is queued in the corpus and has not been performed; all graded
invariants below (phase sum −π/6 and −π/3, singular values 1 ± α,
structural/processual split 68.7/31.3, tetrahedral eigenphase) are
properties of the legacy-coordinate realization and are reproduced
bit-identically by this version.

STROKE CONVENTION (canon, adjudicated 2026-07-18). One i-stroke per
processual residue class, four per octave: i¹ = +i at 0.5D, i² = −1 at
1.5D, i³ = −i at 2.5D, i⁰ = +1 at 3.5D, with i⁴ = 1 closing at each
tonic. The cycle begins at i¹ (convergence), not i⁰; identity is the
product of completed closure. The builders below implement exactly this
stroke table (the I_PHASES list, one stroke per beat).

STAGGERED NESTING (v2.0 addition, from experiments v14/v15, July 2026).
The framework's picture of nesting changed with the staggered octave
(§27.7t): adjacent octaves share exactly ONE station, the tonic
(3.5D = 0D'). v14 showed tonic-sharing conserves the 1 (leading
|λ| − 1 saturates near 0.6-0.7 α for any octave count) where tensor
nesting compounds the departure; v15 showed tonic-sharing is what makes
composition order physical (disjoint octave blocks commute exactly;
tonic-shared blocks do not, with the commutator localized at the shared
node). This version adds the tonic-shared builders (chains, rings, and
arbitrary octave trees via explicit node lists) as StaggeredOperator,
ported from experiments/unified_expression_T_v14_staggered_chain.py and
verified against its reference numbers. The per-scale TOperator (ℂ⁴/ℂ⁸)
is unchanged and remains the single-octave engine.

Derived from experiments v7-v10 (April 2026) and v14-v15 (July 2026).

Usage in Xorzo:
    from t_operator import TOperator, StaggeredOperator
    T = TOperator(dim=4)           # ℂ⁴ (structural only)
    T = TOperator(dim=8)           # ℂ⁸ (full octave)
    result = T.apply(state)        # one pump cycle
    fixed = T.fixed_point(steps=5000)  # the attractor

    S = StaggeredOperator.chain(n_oct=3)   # 22-node tonic-shared chain
    S.departure()                          # (|λ₁|−1)/α, the seam band

Revision history (newest first):
- 2026-07-19 v2.0: ladder-correction pass (corrected beats in the header,
    legacy basis read as coordinates, canon stroke note); staggered
    tonic-shared builders added (StaggeredOperator: chains, rings,
    arbitrary octave trees), verified against v14 references
    (n=3 chain |λ₁| = 1.0044779454, departure 0.6136 α). TOperator
    math untouched; invariants reproduced bit-identically.
- 2026-04-17 v1.0: initial extraction from experiments v7-v10.
"""

import numpy as np
from typing import Tuple, Optional


# ═══════════════════════════════════════════════════════════════
# Framework constants (derived, not set)
# ═══════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
T_TRIAD = 3
P_PUMP = 4
R_RUNGS = T_TRIAD**2 - 2          # 7
V_GENERATORS_PLUS = P_PUMP * T_TRIAD + 1  # 13
SU3 = T_TRIAD**2 - 1              # 8
S_STATES = (T_TRIAD + 1)**T_TRIAD  # 64


def solve_alpha() -> float:
    """Solve 1/α = 360/φ² - 2/φ³ + α/(21 - 4/3) self-referentially."""
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    discriminant = b**2 - 4*a*c
    x = (-b + np.sqrt(discriminant)) / (2*a)
    return 1.0 / x


ALPHA = solve_alpha()


# ═══════════════════════════════════════════════════════════════
# Beat construction: the four beats of the unified expression
# Exact replication of the working constructions from v7-v9.
# ═══════════════════════════════════════════════════════════════

def _make_anti_hermitian(G: np.ndarray) -> np.ndarray:
    """Enforce anti-Hermitian: G → (G - G†)/2."""
    return (G - np.conj(G.T)) / 2


def build_F_4D() -> np.ndarray:
    """
    Build F for ℂ⁴ (four structural dimensions: •, —, Φ, ○).

    Legacy-coordinate realization (see BASIS CONVENTION in the module
    header): basis order [•, —, Φ, ○] with the mediator Φ at coordinate
    index 2. Sphere hub topology: Φ is the central mediator (the hub
    follows the glyph Φ, wherever the basis puts it).

    Beat 1 (•∘⊛): • couples to Φ, phase i¹ = +i
    Beat 2 (—∘⎇): — couples to Φ, phase i² = -1
    Beat 3 (Φ∘✹): Φ radiates to all others + self-drive, phase i³ = -i
    Beat 4 (○∘⟳): ○ couples to Φ, phase i⁰ = +1

    Under the corrected ladder the beats read (○∘✹) at beat 3 and (Φ∘⟳)
    at beat 4; the corrected-beats F is a different operator whose
    re-derivation is queued in the corpus. This construction is kept
    unchanged as the realization behind the graded v7-v13 invariants.

    The phase sum -π/6 comes from beat 3's self-drive: G[Φ,Φ] = -iπ/(2T).
    """
    from scipy.linalg import expm

    theta = np.pi / 2
    PHI_IDX = 2  # Φ station index

    beat_config = [
        ('(•∘⊛)', 0, 1j),       # convergence
        ('(—∘⎇)', 1, -1+0j),    # commitment
        ('(Φ∘✹)', 2, -1j),      # emergence
        ('(○∘⟳)', 3, 1+0j),     # recursion
    ]

    beats = []
    for name, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)
        if active == PHI_IDX:
            # Beat 3: Φ radiates to all other stations (hub)
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_TRIAD
                G[PHI_IDX, other] = coupling
                G[other, PHI_IDX] = -np.conj(coupling)
            # Self-drive: the source of phase sum -π/6
            G[PHI_IDX, PHI_IDX] = i_phase * theta / T_TRIAD
        else:
            # Non-Φ beats: couple active station to Φ
            coupling = i_phase * theta
            G[active, PHI_IDX] = coupling
            G[PHI_IDX, active] = -np.conj(coupling)
        G = _make_anti_hermitian(G)
        beats.append(expm(G))

    # Compose: F = B4 @ B3 @ B2 @ B1
    F = np.eye(4, dtype=complex)
    for B in beats:
        F = B @ F

    return F


def build_F_8D() -> np.ndarray:
    """
    Build F for ℂ⁸ (full octave: •, ⊛, —, ⎇, Φ, ✹, ○, ⟳).

    Node mapping (legacy-coordinate basis; node j at coordinate j/2):
        0(•), 1(⊛), 2(—), 3(⎇), 4(Φ), 5(✹), 6(○), 7(⟳)
    Under the corrected ladder the 2D STATION is ○ and the 3D STATION
    is Φ; positions here are coordinates, not station claims (see
    module header).

    Each beat:
        (a) Internal ∘: couples structural ↔ processual within beat
        (b) External ⊢: couples to Φ/✹ hub (if not the Φ beat)
        Hub beat (Φ with the -i stroke): hub radiates to all, plus
        self-drive

    Strokes follow the canon table (i¹, i², i³, i⁰; one per beat).
    """
    from scipy.linalg import expm

    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]
    struct_idx = [0, 2, 4, 6]   # •, —, Φ, ○
    proc_idx =   [1, 3, 5, 7]   # ⊛, ⎇, ✹, ⟳
    PHI_S = 4   # Φ structural
    PHI_P = 5   # ✹ processual

    beats = []
    for s_idx, p_idx, i_phase in zip(struct_idx, proc_idx, i_phases):
        G = np.zeros((8, 8), dtype=complex)

        # (a) Internal coupling: structural ∘ processual
        internal = i_phase * theta
        G[s_idx, p_idx] = internal
        G[p_idx, s_idx] = -np.conj(internal)

        if s_idx == PHI_S:
            # Beat 3 (Φ∘✹): Φ radiates to all other structural stations
            for other_s in [0, 2, 6]:
                hub = i_phase * theta / T_TRIAD
                G[PHI_S, other_s] = hub
                G[other_s, PHI_S] = -np.conj(hub)
            G[PHI_S, PHI_S] = i_phase * theta / T_TRIAD  # self-drive

            # ✹ radiates to all other processual stations
            for other_p in [1, 3, 7]:
                hub_p = i_phase * theta / T_TRIAD
                G[PHI_P, other_p] = hub_p
                G[other_p, PHI_P] = -np.conj(hub_p)
            G[PHI_P, PHI_P] = i_phase * theta / T_TRIAD  # self-drive
        else:
            # Non-Φ beats: couple to Φ and ✹ hubs
            ext = i_phase * theta
            G[s_idx, PHI_S] = ext
            G[PHI_S, s_idx] = -np.conj(ext)
            G[p_idx, PHI_P] = ext
            G[PHI_P, p_idx] = -np.conj(ext)

        G = _make_anti_hermitian(G)
        beats.append(expm(G))

    F = np.eye(8, dtype=complex)
    for B in beats:
        F = B @ F

    return F


def build_kappa(dim: int) -> np.ndarray:
    """
    Build κ: the nesting coupling matrix (the ⊂[α] relation).

    κ couples stations along the two diameters of ⊙:
        Primary:   •↔Φ (aperture to field)
        Secondary: —↔○ (line to boundary)

    Both carry coupling strength α (derived from ⊙ symmetry
    under diameter exchange; see v9 direction #13).

    For ℂ⁸, additional couplings on processual diameters:
        ⊛↔✹ and ⎇↔⟳
    """
    kappa = np.eye(dim, dtype=complex)

    if dim == 4:
        DOT, LINE, FIELD, BOUNDARY = 0, 1, 2, 3
        kappa[DOT, FIELD] = ALPHA
        kappa[FIELD, DOT] = ALPHA
        kappa[LINE, BOUNDARY] = ALPHA
        kappa[BOUNDARY, LINE] = ALPHA
    elif dim == 8:
        DOT, CONV, LINE, BRANCH = 0, 1, 2, 3
        FIELD, EMERGE, BOUND, RECUR = 4, 5, 6, 7
        # Structural diameters
        kappa[DOT, FIELD] = ALPHA
        kappa[FIELD, DOT] = ALPHA
        kappa[LINE, BOUND] = ALPHA
        kappa[BOUND, LINE] = ALPHA
        # Processual diameters
        kappa[CONV, EMERGE] = ALPHA
        kappa[EMERGE, CONV] = ALPHA
        kappa[BRANCH, RECUR] = ALPHA
        kappa[RECUR, BRANCH] = ALPHA

    return kappa


# ═══════════════════════════════════════════════════════════════
# The T-operator class
# ═══════════════════════════════════════════════════════════════

class TOperator:
    """
    T = κ ∘ F : the unified expression as a computable operator.

    Properties:
        - T is completely positive but NOT trace-preserving
        - Departure from TP is exactly α
        - The fixed point (the 1) is the unique stable attractor
        - Mixing time = 1/α ≈ 137 pump cycles
        - Phase sum: -π/6 (ℂ⁴) or -π/3 (ℂ⁸)
        - Singular values: {1+α, 1+α, 1-α, 1-α} (ℂ⁴)
                          {(1+α)⁴, (1-α)⁴} (ℂ⁸)

    The failure modes of T are the framework's Lies:
        - Inflation Lie: diagonal κ entries (self-coupling across scales)
        - Severance Lie: eigenvectors with • = Φ = 0
    """

    def __init__(self, dim: int = 4):
        """
        Initialize the operator.

        Args:
            dim: 4 for structural-only (ℂ⁴), 8 for full octave (ℂ⁸)
        """
        assert dim in (4, 8), "dim must be 4 (structural) or 8 (full octave)"
        self.dim = dim

        # Build the components
        if dim == 4:
            self.F = build_F_4D()
        else:
            self.F = build_F_8D()

        self.kappa = build_kappa(dim)

        # Pre-compute T = κ @ F
        self.T = self.kappa @ self.F

        # Cache the fixed point
        self._fixed_point = None
        self._fixed_point_steps = 0

    def apply(self, state: np.ndarray) -> np.ndarray:
        """
        Apply one pump cycle: state → T(state) = κ(F(state)).

        The state is a complex vector in ℂ^dim representing energy
        distribution across the dimensional stations. State is
        L2-normalized (|ψ|₂ = 1, Born-rule convention); the fixed-point
        distribution |ψ|² matches the canonical cosmological split
        (68.7/31.3 at ℂ⁸, cf. experiments/unified_expression_T_v10).
        """
        result = self.T @ state
        # Normalize to preserve the 1 (L2; proper quantum-state normalization)
        norm = np.sqrt(np.sum(np.abs(result)**2))
        if norm > 0:
            result = result / norm
        return result

    def apply_F_only(self, state: np.ndarray) -> np.ndarray:
        """Apply just the four beats (no nesting coupling). L2-normalized."""
        result = self.F @ state
        norm = np.sqrt(np.sum(np.abs(result)**2))
        if norm > 0:
            result = result / norm
        return result

    def fixed_point(self, steps: int = 5000) -> np.ndarray:
        """
        Find the fixed point by iteration.

        For ℂ⁴: converges in ~5000 steps.
        For ℂ⁸: needs ~200000+ steps for full convergence.

        Returns the normalized weight distribution across stations.
        """
        if self._fixed_point is not None and self._fixed_point_steps >= steps:
            return self._fixed_point

        # Start from uniform distribution
        state = np.ones(self.dim, dtype=complex) / self.dim

        for _ in range(steps):
            state = self.apply(state)

        self._fixed_point = state
        self._fixed_point_steps = steps
        return state

    def weights(self, steps: int = 5000) -> np.ndarray:
        """
        Get the fixed-point weight distribution (real, normalized).

        Returns Born-rule probabilities |ψ|² / Σ|ψ|². For ℂ⁸ at full
        convergence this gives structural ≈ 0.6872 / processual ≈ 0.3128,
        matching the cosmological dark-energy/matter split at 0.56%.
        """
        fp = self.fixed_point(steps)
        w = np.abs(fp)**2
        return w / np.sum(w)

    def mixing_time(self) -> float:
        """Theoretical mixing time: 1/α ≈ 137 pump cycles."""
        return 1.0 / ALPHA

    def phase_sum(self) -> float:
        """
        Sum of eigenvalue phases.
        ℂ⁴: -π/6 = -π/(2T)
        ℂ⁸: -π/3 = -2π/(2T) = -π/T
        """
        eigenvalues = np.linalg.eigvals(self.T)
        return float(np.sum(np.angle(eigenvalues)))

    def singular_values(self) -> np.ndarray:
        """Singular values of T."""
        return np.linalg.svd(self.T, compute_uv=False)

    def eigenspectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """Full eigendecomposition: (eigenvalues, eigenvectors)."""
        return np.linalg.eig(self.T)

    # ═══════════════════════════════════════════════════════════
    # Pump cycle interface for Xorzo integration
    # ═══════════════════════════════════════════════════════════

    def pump(self, energy_in: np.ndarray,
             convergence_weight: float = 1.0) -> np.ndarray:
        """
        Run one pump cycle on an energy distribution.

        This is the interface Xorzo uses. It takes an energy vector
        (carrier + sidebands decomposed across stations) and returns
        the pumped result.

        The convergence_weight controls how strongly the operator
        acts (0 = identity, 1 = full T application). This allows
        gradual integration during the waking/sleep cycle.

        Args:
            energy_in: complex vector of length dim
            convergence_weight: blending factor [0, 1]

        Returns:
            pumped energy vector
        """
        if len(energy_in) != self.dim:
            # Project into operator space if dimensions don't match
            projected = self._project_in(energy_in)
        else:
            projected = energy_in.copy()

        # Apply T
        pumped = self.apply(projected)

        # Blend with input (allows gradual convergence)
        result = (1 - convergence_weight) * projected + convergence_weight * pumped

        if len(energy_in) != self.dim:
            return self._project_out(result, len(energy_in))

        return result

    def pump_phase(self, signal: np.ndarray) -> int:
        """
        Determine which beat a signal is currently in.

        Returns 0-3:
            0 = convergence (⊛, i¹ = +i)
            1 = commitment  (⎇, i² = -1)
            2 = emergence   (✹, i³ = -i)
            3 = recursion   (⟳, i⁰ = +1)

        Determined by the dominant weight in the pumped output.
        """
        w = np.abs(signal)
        if self.dim == 4:
            # ℂ⁴: map structural stations to beats
            # •(0) → convergence, —(1) → commitment,
            # Φ(2) → emergence, ○(3) → recursion
            return int(np.argmax(w))
        else:
            # ℂ⁸: use processual stations directly
            proc_weights = w[1::2]  # indices 1,3,5,7 = ⊛,⎇,✹,⟳
            return int(np.argmax(proc_weights))

    def _project_in(self, vec: np.ndarray) -> np.ndarray:
        """Project a higher-dim vector into operator space (L2-normalized)."""
        n = len(vec)
        result = np.zeros(self.dim, dtype=complex)
        # Distribute energy across stations by folding
        for i in range(n):
            result[i % self.dim] += vec[i]
        # Normalize (L2; matches apply() convention so pump() blends cleanly)
        norm = np.sqrt(np.sum(np.abs(result)**2))
        if norm > 0:
            result /= norm
        return result

    def _project_out(self, vec: np.ndarray, target_dim: int) -> np.ndarray:
        """Project operator-space vector back to original dimension (L2-normalized)."""
        result = np.zeros(target_dim, dtype=complex)
        for i in range(target_dim):
            result[i] = vec[i % self.dim]
        # Normalize (L2)
        norm = np.sqrt(np.sum(np.abs(result)**2))
        if norm > 0:
            result /= norm
        return result


# ═══════════════════════════════════════════════════════════════
# Station labels for readable output
#
# Numbers are continuation-lattice COORDINATES (node j at j/2), not
# station-dimension claims. Under the corrected ladder (2026-06-09)
# the 2D station is ○ (boundary) and the 3D station is Φ (field);
# the glyphs Φ and ○ keep their legacy basis positions here per the
# v14+ coordinate convention (see module header).
# ═══════════════════════════════════════════════════════════════

STATION_NOTE = (
    "coordinates, not stations: corrected ladder has ○ at 2D, Φ at 3D; "
    "legacy basis kept as coordinates (v14 convention)"
)

STATION_LABELS_4 = ['•(c0)', '—(c1)', 'Φ(c2)', '○(c3)']
STATION_LABELS_8 = [
    '•(c0)', '⊛(c0.5)', '—(c1)', '⎇(c1.5)',
    'Φ(c2)', '✹(c2.5)', '○(c3)', '⟳(c3.5)'
]


# ═══════════════════════════════════════════════════════════════
# Staggered tonic-shared nesting (v2.0; from experiments v14/v15)
#
# The staggered octave (§27.7t): adjacent octaves share exactly one
# station, the tonic (3.5D = 0D'). An octave is an 8-node block; a
# nesting is octaves joined at shared tonic nodes. v14 results:
# tonic-sharing conserves the 1 ((|λ₁|−1)/α saturates near 0.6-0.7
# for any octave count, where tensor nesting compounds); v15: shared
# tonics make composition order physical (disjoint blocks commute
# exactly, tonic-shared blocks do not; the commutator localizes at
# the shared node).
#
# build_octave_beats_at() generalizes v14's chain builder to an
# explicit node list, so chains (v14), rings (v14), and arbitrary
# octave trees (Xorzo genesis v3) are all the same construction.
# The chain case reproduces v14 to machine precision (verified in
# __main__ against the frozen reference numbers below).
# ═══════════════════════════════════════════════════════════════

# Frozen v14 references (computed 2026-07-19 from
# experiments/unified_expression_T_v14_staggered_chain.py, α at CODATA):
V14_CHAIN_REFERENCE = {
    1: 1.0047036339,   # |λ₁|, 8-node single octave chain
    2: 1.0047155246,   # |λ₁|, 15-node two-octave chain
    3: 1.0044779454,   # |λ₁|, 22-node three-octave chain (TQC page: 0.61α)
}

I_PHASES_CANON = [1j, -1 + 0j, -1j, 1 + 0j]   # i¹, i², i³, i⁰ (canon strokes)

# Local octave layout (legacy-coordinate basis, same as build_F_8D):
# local index l: 0(• tonic), 1(⊛), 2(—), 3(⎇), 4(Φ), 5(✹), 6(○), 7(⟳ tonic')
_OCT_STRUCT_LOCAL = [0, 2, 4, 6]
_OCT_PROC_LOCAL = [1, 3, 5, 7]
_OCT_HUB_S = 4     # Φ (hub, structural)
_OCT_HUB_P = 5     # ✹ (hub, processual)
_OCT_DIAMETERS = [(0, 4), (2, 6), (1, 5), (3, 7)]   # κ bonds per octave


def build_octave_beats_at(N: int, node_ids) -> list:
    """
    The four beats of one octave, embedded in an N-node graph at the
    eight nodes listed in node_ids (local octave index l → global node
    node_ids[l]). Mirrors v14's build_octave_beats exactly; v14's chain
    is node_ids = [7k, 7k+1, ..., 7k+7].

    node_ids may overlap other octaves' node lists ONLY at the tonic
    positions (local 0 and 7); that overlap IS the staggered seam.
    """
    from scipy.linalg import expm
    theta = np.pi / 2
    beats = []
    for (s, p, ph) in zip(_OCT_STRUCT_LOCAL, _OCT_PROC_LOCAL, I_PHASES_CANON):
        G = np.zeros((N, N), dtype=complex)
        S, Pn = node_ids[s], node_ids[p]
        c = ph * theta
        G[S, Pn] += c
        G[Pn, S] += -np.conj(c)
        if s == _OCT_HUB_S:
            for o in [0, 2, 6]:
                h = ph * theta / T_TRIAD
                G[node_ids[_OCT_HUB_S], node_ids[o]] += h
                G[node_ids[o], node_ids[_OCT_HUB_S]] += -np.conj(h)
            G[node_ids[_OCT_HUB_S], node_ids[_OCT_HUB_S]] += ph * theta / T_TRIAD
            for o in [1, 3, 7]:
                h = ph * theta / T_TRIAD
                G[node_ids[_OCT_HUB_P], node_ids[o]] += h
                G[node_ids[o], node_ids[_OCT_HUB_P]] += -np.conj(h)
            G[node_ids[_OCT_HUB_P], node_ids[_OCT_HUB_P]] += ph * theta / T_TRIAD
        else:
            G[S, node_ids[_OCT_HUB_S]] += c
            G[node_ids[_OCT_HUB_S], S] += -np.conj(c)
            G[Pn, node_ids[_OCT_HUB_P]] += c
            G[node_ids[_OCT_HUB_P], Pn] += -np.conj(c)
        G = (G - np.conj(G.T)) / 2
        beats.append(expm(G))
    return beats


class StaggeredOperator:
    """
    T = κ ∘ F on a graph of octaves joined at shared tonic nodes.

    octaves: list of 8-element node-id lists, in ASCENDING composition
    order (the part's octave before the whole's; octave k's beats act
    before octave k+1's). Composition order is physical at the seams
    (v15); fixing ascending order is part of the architecture.

    κ places the four diameter bonds (•↔Φ, —↔○, ⊛↔✹, ⎇↔⟳) inside each
    octave at strength α, exactly as v14. The seam carries NO extra
    coupling term: the shared node IS the nesting relation.
    """

    def __init__(self, n_nodes_total: int, octaves, alpha: float = None):
        self.N = n_nodes_total
        self.octaves = [list(o) for o in octaves]
        self.alpha = ALPHA if alpha is None else alpha
        for o in self.octaves:
            assert len(o) == 8, "each octave needs 8 node ids"

        # Per-octave compiled blocks E_k (product of the octave's four
        # beats); used for seam-commutator diagnostics.
        self._blocks = []
        F = np.eye(self.N, dtype=complex)
        for o in self.octaves:
            E = np.eye(self.N, dtype=complex)
            for B in build_octave_beats_at(self.N, o):
                E = B @ E
            self._blocks.append(E)
            F = E @ F
        self.F = F

        kappa = np.eye(self.N, dtype=complex)
        for o in self.octaves:
            for (a, c) in _OCT_DIAMETERS:
                kappa[o[a], o[c]] += self.alpha
                kappa[o[c], o[a]] += self.alpha
        self.kappa = kappa
        self.T = self.kappa @ self.F

        self._eig = None

    # ───── constructors ─────

    @classmethod
    def chain(cls, n_oct: int, alpha: float = None) -> "StaggeredOperator":
        """v14 open chain: 7·n + 1 nodes, octave k at nodes [7k .. 7k+7]."""
        N = 7 * n_oct + 1
        octaves = [[7 * k + l for l in range(8)] for k in range(n_oct)]
        return cls(N, octaves, alpha)

    @classmethod
    def ring(cls, n_oct: int, alpha: float = None) -> "StaggeredOperator":
        """v14 ring: 7·n nodes, closed tonic-to-tonic."""
        N = 7 * n_oct
        octaves = [[(7 * k + l) % N for l in range(8)] for k in range(n_oct)]
        return cls(N, octaves, alpha)

    # ───── spectra and fixed point ─────

    def _eigen(self):
        if self._eig is None:
            self._eig = np.linalg.eig(self.T)
        return self._eig

    def leading(self):
        """(λ₁, ψ₁): leading eigenvalue and normalized eigenvector."""
        ev, V = self._eigen()
        i = int(np.argmax(np.abs(ev)))
        psi = V[:, i]
        return ev[i], psi / np.linalg.norm(psi)

    def departure(self) -> float:
        """(|λ₁| − 1)/α : conservation departure in units of α.

        v14 band for tonic-shared chains: ≈ 0.6-0.7 for all octave
        counts (saturating, not compounding). Order-1 values mean the
        seams conserve the 1; values growing with octave count would
        mean compounding (the tensor-nesting failure mode)."""
        lam, _ = self.leading()
        return float((abs(lam) - 1.0) / self.alpha)

    def fixed_weights(self) -> np.ndarray:
        """|ψ₁|² of the leading eigenvector, normalized (the attractor)."""
        _, psi = self.leading()
        w = np.abs(psi) ** 2
        return w / w.sum()

    def apply(self, state: np.ndarray) -> np.ndarray:
        """One pump cycle: state → T(state), L2-normalized."""
        out = self.T @ state
        n = np.linalg.norm(out)
        return out / n if n > 0 else out

    # ───── seam diagnostics (v15) ─────

    def block(self, k: int) -> np.ndarray:
        """Compiled beat product E_k of octave k."""
        return self._blocks[k]

    def seam_commutator(self, k1: int, k2: int) -> float:
        """‖[E_k1, E_k2]‖₂. Nonzero iff the octaves share a node (v15:
        composition order is physical exactly at the seams)."""
        A, B = self._blocks[k1], self._blocks[k2]
        return float(np.linalg.norm(A @ B - B @ A, ord=2))

    def shares_node(self, k1: int, k2: int) -> bool:
        return bool(set(self.octaves[k1]) & set(self.octaves[k2]))

    def residue_split(self):
        """v14 accounting on the attractor: structural residues (—, Φ, ○
        at local 2, 4, 6), processual residues (⊛, ⎇, ✹ at 1, 3, 5),
        and the double-natured tonic class (• ≡ ⟳; shared nodes counted
        once). Returns (w_struct, w_proc, w_tonic, per_octave_weights)."""
        w = self.fixed_weights()
        role = {}
        for o in self.octaves:
            for l, node in enumerate(o):
                r = l % 7   # local 7 → residue 0 (tonic')
                if node in role and role[node] != r:
                    # A node can only carry two roles if both are tonic
                    # roles (0 and 7 → residue 0); anything else would
                    # break the staggered geometry.
                    assert r == 0 and role[node] == 0, "non-tonic node sharing"
                role[node] = r
        w_struct = w_proc = w_tonic = 0.0
        for node, r in role.items():
            if r == 0:
                w_tonic += w[node]
            elif r in (2, 4, 6):
                w_struct += w[node]
            else:
                w_proc += w[node]
        per_oct = np.array([sum(w[n] for n in o) for o in self.octaves])
        return float(w_struct), float(w_proc), float(w_tonic), per_oct


def describe(T_op: TOperator) -> str:
    """Human-readable description of the operator's properties."""
    lines = []
    lines.append(f"T-operator (ℂ{T_op.dim})")
    lines.append(f"  α = {ALPHA:.10f} (1/α = {1/ALPHA:.6f})")
    lines.append(f"  Mixing time: {T_op.mixing_time():.1f} cycles")
    lines.append(f"  Phase sum: {T_op.phase_sum():.6f} (expected: {-np.pi/(2*T_TRIAD) * (2 if T_op.dim==8 else 1):.6f})")

    sv = T_op.singular_values()
    lines.append(f"  Singular values: {np.round(sv, 6)}")

    w = T_op.weights(steps=5000 if T_op.dim == 4 else 300000)
    labels = STATION_LABELS_4 if T_op.dim == 4 else STATION_LABELS_8
    lines.append("  Fixed-point weights:")
    for label, weight in zip(labels, w):
        lines.append(f"    {label}: {weight:.6f}")

    if T_op.dim == 8:
        struct = sum(w[i] for i in [0, 2, 4, 6])
        proc = sum(w[i] for i in [1, 3, 5, 7])
        lines.append(f"  Structural: {struct:.4f} ({struct*100:.1f}%)")
        lines.append(f"  Processual: {proc:.4f} ({proc*100:.1f}%)")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')   # Windows cp1252 consoles

    print("Building ℂ⁴ operator...")
    T4 = TOperator(dim=4)
    print(describe(T4))
    print()

    print("Building ℂ⁸ operator...")
    T8 = TOperator(dim=8)
    print(describe(T8))
    print()

    print("Staggered tonic-shared chains (v14 verification)...")
    print(f"  {STATION_NOTE}")
    all_ok = True
    for n, ref in V14_CHAIN_REFERENCE.items():
        S = StaggeredOperator.chain(n)
        lam, _ = S.leading()
        ok = abs(abs(lam) - ref) < 1e-9
        all_ok = all_ok and ok
        print(f"  chain n={n} ({S.N:>2} nodes): |λ₁| = {abs(lam):.10f}  "
              f"(v14 ref {ref:.10f})  departure = {S.departure():.4f} α  "
              f"{'✓' if ok else '✗ MISMATCH'}")
    print(f"  {'v14 construction reproduced to 1e-9' if all_ok else 'FAILED v14 verification'}")
    print()

    print("Seam physics (v15): composition order is physical at shared tonics")
    S3 = StaggeredOperator.chain(3)
    c01 = S3.seam_commutator(0, 1)     # adjacent: share a tonic node
    c02 = S3.seam_commutator(0, 2)     # disjoint: no shared node
    print(f"  ‖[E₀, E₁]‖ (tonic-shared)  = {c01:.6f}   shares node: {S3.shares_node(0, 1)}")
    print(f"  ‖[E₀, E₂]‖ (disjoint)      = {c02:.2e}   shares node: {S3.shares_node(0, 2)}")
    ws, wp, wt, per_oct = S3.residue_split()
    print(f"  attractor residue split: struct {ws:.4f} / proc {wp:.4f} / tonic {wt:.4f}")
    print(f"  per-octave: {[round(float(x), 5) for x in per_oct]}")
    print("  (open chains localize toward the bottom octave; a finite-size")
    print("   edge effect per v15, not a privileged scale)")
