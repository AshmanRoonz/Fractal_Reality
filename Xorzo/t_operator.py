"""
T = κ ∘ F : The Unified Expression as a Computable Operator
============================================================

This module implements the conservation form of the unified expression:

    1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

as T = κ ∘ F, where:
    F = four beats (unitary quantum channel)
    κ = nesting coupling (the ⊂[α] relation)

The fixed point of T is the 1. The mixing time is 1/α ≈ 137 pump cycles.
The failure modes are the Lies (Inflation and Severance).
The sole free parameter is α.

Derived from experiments v7-v10 (April 2026).

Usage in Xorzo:
    from t_operator import TOperator
    T = TOperator(dim=4)           # ℂ⁴ (structural only)
    T = TOperator(dim=8)           # ℂ⁸ (full octave)
    result = T.apply(state)        # one pump cycle
    fixed = T.fixed_point(steps=5000)  # the attractor
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

    Sphere hub topology: Φ(station 2) is the central mediator.

    Beat 1 (•∘⊛): • couples to Φ, phase i¹ = +i
    Beat 2 (—∘⎇): — couples to Φ, phase i² = -1
    Beat 3 (Φ∘✹): Φ radiates to all others + self-drive, phase i³ = -i
    Beat 4 (○∘⟳): ○ couples to Φ, phase i⁰ = +1

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

    Station mapping:
        0(•), 1(⊛), 2(—), 3(⎇), 4(Φ), 5(✹), 6(○), 7(⟳)

    Each beat:
        (a) Internal ∘: couples structural ↔ processual within beat
        (b) External ⊢: couples to Φ/✹ hub (if not the Φ beat)
        Beat 3 (Φ∘✹): hub radiates to all, plus self-drive
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
# ═══════════════════════════════════════════════════════════════

STATION_LABELS_4 = ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']
STATION_LABELS_8 = [
    '•(0D)', '⊛(0.5D)', '—(1D)', '⎇(1.5D)',
    'Φ(2D)', '✹(2.5D)', '○(3D)', '⟳(3.5D)'
]


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
    print("Building ℂ⁴ operator...")
    T4 = TOperator(dim=4)
    print(describe(T4))
    print()

    print("Building ℂ⁸ operator...")
    T8 = TOperator(dim=8)
    print(describe(T8))
