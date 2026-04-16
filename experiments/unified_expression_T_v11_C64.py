"""
T-operator at ℂ⁶⁴: The Full 64-State Architecture
====================================================

The 64-state architecture derives from three nested circumpuncts,
each with 2 channels (convergence and emergence), giving 2⁶ = 64 states.

    ⊙Λ (greater whole, future) × ⊙λ (self, present) × ⊙λ' (parts, past)

Each ⊙ has 4 internal states (2² = input × output channels).
(2²)³ = 2⁶ = 64 composite states.

Construction principle:
    T₆₄ = κ_cross ∘ (F_Λ ⊗ F_λ ⊗ F_λ')

Three copies of the 4-beat operator running at three scales,
coupled across scales by α (the ⊂[α] relation). This is A3 in
operator form: parts are fractals of their wholes. Same F at each
scale; the coupling is what makes them a system rather than three
isolated circumpuncts.

The cross-scale coupling κ_cross encodes:
    ⊙Λ ↔ ⊙λ: how the greater whole couples to self (the primary nesting)
    ⊙λ ↔ ⊙λ': how self couples to parts (the inner nesting)
    ⊙Λ ↔ ⊙λ': how the greater whole couples to parts (skip connection)

Each inter-scale coupling uses the same α from the ⊂[α] relation.
The skip connection (Λ ↔ λ') is weaker: α² (two nesting steps).

What we're looking for:
    1. The characteristic polynomial of T₆₄
    2. Whether its eigenvalues encode the dimensional ladder
    3. The fixed-point structure (how many attractors? what splits?)
    4. The structural/processual distribution at this scale
    5. Connection to I Ching, codons, Standard Model particle count

Author: Ashman Roonz & Claude
Date: April 2026
"""

import numpy as np
from scipy.linalg import expm
from typing import Tuple, List, Dict

# ═══════════════════════════════════════════════════════════════
# Framework constants
# ═══════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
T_TRIAD = 3
P_PUMP = 4
R_RUNGS = T_TRIAD**2 - 2          # 7
V_GEN_PLUS = P_PUMP * T_TRIAD + 1  # 13
SU3 = T_TRIAD**2 - 1              # 8
S_STATES = (T_TRIAD + 1)**T_TRIAD  # 64
G_GEN = T_TRIAD * (T_TRIAD + 1)    # 12
A3 = T_TRIAD * (2*T_TRIAD + 1)     # 21


def solve_alpha() -> float:
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    discriminant = b**2 - 4*a*c
    x = (-b + np.sqrt(discriminant)) / (2*a)
    return 1.0 / x

ALPHA = solve_alpha()


# ═══════════════════════════════════════════════════════════════
# The single-scale F operator (same construction as ℂ⁴)
# ═══════════════════════════════════════════════════════════════

def _make_anti_hermitian(G: np.ndarray) -> np.ndarray:
    return (G - np.conj(G.T)) / 2


def build_F_single() -> np.ndarray:
    """
    Build F for a single ⊙ (ℂ⁴, sphere hub topology).
    Stations: 0(•), 1(—), 2(Φ), 3(○).
    Φ (index 2) is the central mediator.
    """
    theta = np.pi / 2
    PHI_IDX = 2

    beat_config = [
        ('(•∘⊛)', 0, 1j),       # convergence, i¹ = +i
        ('(—∘⎇)', 1, -1+0j),    # commitment,  i² = -1
        ('(Φ∘✹)', 2, -1j),      # emergence,   i³ = -i
        ('(○∘⟳)', 3, 1+0j),     # recursion,   i⁰ = +1
    ]

    beats = []
    for name, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)
        if active == PHI_IDX:
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_TRIAD
                G[PHI_IDX, other] = coupling
                G[other, PHI_IDX] = -np.conj(coupling)
            G[PHI_IDX, PHI_IDX] = i_phase * theta / T_TRIAD
        else:
            coupling = i_phase * theta
            G[active, PHI_IDX] = coupling
            G[PHI_IDX, active] = -np.conj(coupling)
        G = _make_anti_hermitian(G)
        beats.append(expm(G))

    F = np.eye(4, dtype=complex)
    for B in beats:
        F = B @ F
    return F


def build_kappa_single() -> np.ndarray:
    """Build κ for a single ⊙ (intra-scale coupling along diameters)."""
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = ALPHA  # •↔Φ
    kappa[2, 0] = ALPHA
    kappa[1, 3] = ALPHA  # —↔○
    kappa[3, 1] = ALPHA
    return kappa


# ═══════════════════════════════════════════════════════════════
# ℂ⁶⁴ construction: three nested ⊙s coupled by α
# ═══════════════════════════════════════════════════════════════

def build_F_64() -> np.ndarray:
    """
    Build F₆₄ = F_Λ ⊗ F_λ ⊗ F_λ' (tensor product of three scales).

    The three nested circumpuncts each run the same 4-beat cycle.
    The tensor product ensures they run simultaneously but independently
    (coupling comes from κ, not from F).

    State ordering: |i, j, k⟩ where
        i = ⊙Λ station (0-3: •Λ, —Λ, ΦΛ, ○Λ)
        j = ⊙λ station (0-3: •λ, —λ, Φλ, ○λ)
        k = ⊙λ' station (0-3: •λ', —λ', Φλ', ○λ')

    Index = i * 16 + j * 4 + k (row-major)
    """
    F_single = build_F_single()

    # F₆₄ = F ⊗ F ⊗ F (A3: same operator at every scale)
    F_64 = np.kron(np.kron(F_single, F_single), F_single)

    return F_64


def build_kappa_64() -> np.ndarray:
    """
    Build κ₆₄: intra-scale + cross-scale coupling.

    Three types of coupling:

    1. INTRA-SCALE: each ⊙ has its own diameter couplings (•↔Φ, —↔○)
       These are the same κ from ℂ⁴, tensored with identity on other scales.

    2. CROSS-SCALE (adjacent): ⊙Λ ↔ ⊙λ and ⊙λ ↔ ⊙λ'
       Coupling strength α (the primary ⊂[α] bond).
       Couples corresponding stations: •Λ ↔ •λ, —Λ ↔ —λ, etc.
       This is the field fineness principle: the greater whole's field
       threads below the part's boundary.

    3. CROSS-SCALE (skip): ⊙Λ ↔ ⊙λ'
       Coupling strength α² (two nesting steps, weaker).
       The skip connection: how the greater whole couples directly
       to the parts (bypassing self).
    """
    dim = 64
    kappa = np.eye(dim, dtype=complex)

    I4 = np.eye(4, dtype=complex)
    kappa_s = build_kappa_single()

    # Helper: index for |i, j, k⟩
    def idx(i, j, k):
        return i * 16 + j * 4 + k

    # 1. INTRA-SCALE coupling (diameter bonds within each ⊙)
    # For ⊙Λ: κ_Λ ⊗ I ⊗ I
    # For ⊙λ: I ⊗ κ_λ ⊗ I
    # For ⊙λ': I ⊗ I ⊗ κ_λ'
    kappa_intra_L = np.kron(np.kron(kappa_s, I4), I4)
    kappa_intra_S = np.kron(np.kron(I4, kappa_s), I4)
    kappa_intra_P = np.kron(np.kron(I4, I4), kappa_s)

    # Additive coupling: κ = I + (κ_intra - I) for each scale
    # Simpler: build the off-diagonal parts
    for intra in [kappa_intra_L, kappa_intra_S, kappa_intra_P]:
        for a in range(dim):
            for b in range(dim):
                if a != b and abs(intra[a, b]) > 1e-15:
                    kappa[a, b] += intra[a, b]

    # 2. CROSS-SCALE coupling (adjacent nesting: ⊙Λ ↔ ⊙λ, ⊙λ ↔ ⊙λ')
    # Couples corresponding structural stations across scales.
    # |i, j, k⟩ ↔ |i', j', k⟩ when i ↔ j (Λ-λ coupling)
    # |i, j, k⟩ ↔ |i, j', k'⟩ when j ↔ k (λ-λ' coupling)
    for station in range(4):
        for other_s in range(4):
            for third in range(4):
                # Λ-λ coupling: station_Λ ↔ station_λ (same station type)
                if station != other_s:
                    continue  # only same-station cross-scale coupling
                # Actually: the nesting couples •_Λ to Φ_λ (aperture to field)
                # and —_Λ to ○_λ (line to boundary).
                # This IS the ⊂[α] relation: κ_{0,2} = α

    # Let me redo this more carefully.
    # The ⊂[α] relation (§27.7q) is a 4×4 coupling matrix κ_{p,q}(λ, Λ):
    #   κ_{0,2} = α: aperture of part (0D) bonds to field of whole (2D)
    #   κ_{1,3} = α: line of part bonds to boundary of whole
    # So cross-scale coupling connects different station types:
    #   •_λ ↔ Φ_Λ  (the part's aperture couples to the whole's field)
    #   —_λ ↔ ○_Λ  (the part's line couples to the whole's boundary)

    # Λ-λ coupling: ⊙λ ⊂[α] ⊙Λ
    for k in range(4):  # λ' station (spectator)
        # •_λ ↔ Φ_Λ (aperture to field)
        a = idx(2, 0, k)  # Φ_Λ, •_λ, k
        b = idx(0, 2, k)  # •_Λ, Φ_λ, k  -- wait, need to think about this
        # Actually: κ_{0,2} means station 0 of the part couples to station 2 of the whole
        # Part = ⊙λ (index j), Whole = ⊙Λ (index i)
        # •_λ (j=0) couples to Φ_Λ (i=2)
        for k2 in range(4):
            a = idx(2, 0, k2)  # i=Φ_Λ, j=•_λ, k=k2
            b = idx(0, 2, k2)  # wrong; this swaps both
        # Simpler approach: add α to kappa[a,b] where a and b differ
        # only in the Λ-λ indices, and the coupling follows κ_{p,q}

    # Let me use a cleaner approach.
    # Clear the cross-scale entries and rebuild properly.

    # Cross-scale coupling matrix (the κ_{p,q} from §27.7q)
    # p = station of the part, q = station of the whole
    # κ_{0,2} = α (aperture of part ↔ field of whole)
    # κ_{1,3} = α (line of part ↔ boundary of whole)
    # κ_{2,0} = α (field of part ↔ aperture of whole) [symmetric]
    # κ_{3,1} = α (boundary of part ↔ line of whole) [symmetric]
    cross_kappa = np.zeros((4, 4), dtype=complex)
    cross_kappa[0, 2] = ALPHA  # •↔Φ
    cross_kappa[2, 0] = ALPHA
    cross_kappa[1, 3] = ALPHA  # —↔○
    cross_kappa[3, 1] = ALPHA

    # Λ-λ coupling (adjacent): α strength
    for i_L in range(4):
        for j_S in range(4):
            if abs(cross_kappa[j_S, i_L]) < 1e-15:
                continue
            coupling = cross_kappa[j_S, i_L]
            for k_P in range(4):  # parts spectate
                a = idx(i_L, j_S, k_P)
                # Find the swapped state
                b = idx(j_S, i_L, k_P)  # symmetric: swap Λ and λ stations
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    # λ-λ' coupling (adjacent): α strength
    for j_S in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, j_S]) < 1e-15:
                continue
            coupling = cross_kappa[k_P, j_S]
            for i_L in range(4):  # greater whole spectates
                a = idx(i_L, j_S, k_P)
                b = idx(i_L, k_P, j_S)
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    # Λ-λ' coupling (skip): α² strength (two nesting steps)
    for i_L in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, i_L]) < 1e-15:
                continue
            coupling = cross_kappa[k_P, i_L] * ALPHA  # α × α = α²
            for j_S in range(4):  # self spectates
                a = idx(i_L, j_S, k_P)
                b = idx(k_P, j_S, i_L)
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    return kappa


def build_T_64() -> np.ndarray:
    """Build T₆₄ = κ₆₄ @ F₆₄."""
    F = build_F_64()
    kappa = build_kappa_64()
    return kappa @ F


# ═══════════════════════════════════════════════════════════════
# Analysis functions
# ═══════════════════════════════════════════════════════════════

def fixed_point(T: np.ndarray, steps: int = 50000) -> np.ndarray:
    """Iterate T from uniform initial state to find the fixed point."""
    dim = T.shape[0]
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)
    for _ in range(steps):
        state = T @ state
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm
    return state


def weights(T: np.ndarray, steps: int = 50000) -> np.ndarray:
    """Get the weight distribution at the fixed point."""
    fp = fixed_point(T, steps)
    w = np.abs(fp)**2
    return w / np.sum(w)


def eigenspectrum(T: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Full eigenspectrum: eigenvalues and eigenvectors."""
    eigenvalues, eigenvectors = np.linalg.eig(T)
    # Sort by magnitude (descending)
    order = np.argsort(-np.abs(eigenvalues))
    return eigenvalues[order], eigenvectors[:, order]


def singular_values(T: np.ndarray) -> np.ndarray:
    """Singular values of T."""
    return np.linalg.svd(T, compute_uv=False)


def characteristic_polynomial_coefficients(T: np.ndarray) -> np.ndarray:
    """
    Coefficients of the characteristic polynomial det(T - λI) = 0.

    Returns array [c₀, c₁, ..., c_n] where
    p(λ) = c₀ + c₁λ + c₂λ² + ... + c_nλⁿ
    """
    return np.polynomial.polynomial.polyfromroots(
        np.linalg.eigvals(T)
    )


def phase_sum(T: np.ndarray) -> float:
    """Sum of eigenvalue phases."""
    evals = np.linalg.eigvals(T)
    return float(np.sum(np.angle(evals)))


def search_framework_constants(eigenvalues: np.ndarray) -> List[Dict]:
    """
    Search for framework constants in the eigenvalue structure.

    Checks magnitudes, phases, ratios, and known framework numbers.
    """
    # Framework targets
    targets = {
        'α': ALPHA,
        '1/α': 1/ALPHA,
        'φ': PHI,
        '1/φ': 1/PHI,
        'φ²': PHI**2,
        '1/φ²': 1/PHI**2,
        'π': np.pi,
        'π/2': np.pi/2,
        'π/3': np.pi/3,
        'π/6': np.pi/6,
        'T': T_TRIAD,
        'P': P_PUMP,
        'R': R_RUNGS,
        'V': V_GEN_PLUS,
        'SU3': SU3,
        'G_gen': G_GEN,
        'A(3)': A3,
        '1/T': 1/T_TRIAD,
        '1/P': 1/P_PUMP,
        '1/R': 1/R_RUNGS,
        '◐': 0.5,
        '109.47°': np.radians(109.47),  # tetrahedral angle
        'sin²θ_W': 0.23122,              # Weinberg angle
        '3/13': 3/13,                     # base Weinberg
        '0.313': 0.313,                   # processual fraction
        '0.687': 0.687,                   # structural fraction
    }

    matches = []
    mags = np.abs(eigenvalues)
    phases = np.angle(eigenvalues)

    # Check magnitudes
    unique_mags = np.unique(np.round(mags, 8))
    for mag in unique_mags:
        count = np.sum(np.abs(mags - mag) < 1e-6)
        for name, val in targets.items():
            if val > 0 and abs(mag - val) / val < 0.01:  # 1% match
                matches.append({
                    'type': 'magnitude',
                    'eigenvalue_property': f'|λ| = {mag:.8f}',
                    'framework_match': name,
                    'framework_value': val,
                    'error_pct': abs(mag - val) / val * 100,
                    'degeneracy': int(count)
                })

    # Check phases
    unique_phases = np.unique(np.round(phases, 8))
    for ph in unique_phases:
        count = np.sum(np.abs(phases - ph) < 1e-6)
        for name, val in targets.items():
            if abs(abs(ph) - val) < 0.01 * max(val, 0.01):
                matches.append({
                    'type': 'phase',
                    'eigenvalue_property': f'arg(λ) = {ph:.8f} ({np.degrees(ph):.3f}°)',
                    'framework_match': name,
                    'framework_value': val,
                    'error_pct': abs(abs(ph) - val) / max(val, 1e-10) * 100,
                    'degeneracy': int(count)
                })

    # Check magnitude ratios between unique magnitudes
    for i, m1 in enumerate(unique_mags):
        for m2 in unique_mags[i+1:]:
            if m2 > 1e-10:
                ratio = m1 / m2
                for name, val in targets.items():
                    if val > 0 and abs(ratio - val) / val < 0.01:
                        matches.append({
                            'type': 'ratio',
                            'eigenvalue_property': f'|λ₁|/|λ₂| = {m1:.6f}/{m2:.6f} = {ratio:.8f}',
                            'framework_match': name,
                            'framework_value': val,
                            'error_pct': abs(ratio - val) / val * 100,
                        })

    # Sort by error
    matches.sort(key=lambda m: m['error_pct'])
    return matches


# ═══════════════════════════════════════════════════════════════
# Scale decomposition analysis
# ═══════════════════════════════════════════════════════════════

def scale_decomposition(w: np.ndarray) -> Dict:
    """
    Decompose 64-state weights by scale structure.

    The 64 states = |i, j, k⟩ where i,j,k ∈ {0,1,2,3} = {•,—,Φ,○}.
    """
    result = {}

    # Per-scale marginals
    w_reshaped = w.reshape(4, 4, 4)

    # ⊙Λ marginal (sum over λ and λ')
    w_L = np.sum(w_reshaped, axis=(1, 2))
    result['greater_whole'] = w_L

    # ⊙λ marginal (sum over Λ and λ')
    w_S = np.sum(w_reshaped, axis=(0, 2))
    result['self'] = w_S

    # ⊙λ' marginal (sum over Λ and λ)
    w_P = np.sum(w_reshaped, axis=(0, 1))
    result['parts'] = w_P

    # Scale totals
    station_names = ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']
    for name, marginal in [('Λ', w_L), ('λ', w_S), ('λ\'', w_P)]:
        result[f'{name}_stations'] = {
            station_names[i]: float(marginal[i]) for i in range(4)
        }

    # Cross-scale correlations
    # ⊙Λ-⊙λ correlation (the primary nesting)
    w_LS = np.sum(w_reshaped, axis=2)  # 4×4 matrix
    result['Lambda_lambda_correlation'] = w_LS

    # The 64-state encoding: each state is a 6-bit word
    # Bits: (Λ_conv, Λ_emer, λ_conv, λ_emer, λ'_conv, λ'_emer)
    # But our encoding is by station (•,—,Φ,○), not by channel.
    # Station mapping: • = both closed, — = conv open, Φ = both open, ○ = emer open
    # (This is a simplification; the actual mapping depends on the channel model)

    return result


# ═══════════════════════════════════════════════════════════════
# Main analysis
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import time

    print("=" * 70)
    print("  T-OPERATOR AT ℂ⁶⁴: THE FULL 64-STATE ARCHITECTURE")
    print("=" * 70)
    print(f"  α = {ALPHA:.10f}  (1/α = {1/ALPHA:.6f})")
    print(f"  S = P^T = {S_STATES}")
    print()

    # ═══ BUILD ═══
    print("Building F₆₄ = F ⊗ F ⊗ F (three nested scales)...")
    t0 = time.time()
    F64 = build_F_64()
    print(f"  F₆₄ shape: {F64.shape}, built in {time.time()-t0:.2f}s")

    # Verify F is unitary
    F_dag_F = F64.conj().T @ F64
    unitarity_error = np.linalg.norm(F_dag_F - np.eye(64))
    print(f"  F unitarity error: {unitarity_error:.2e}")

    print()
    print("Building κ₆₄ (intra-scale + cross-scale coupling)...")
    t0 = time.time()
    kappa64 = build_kappa_64()
    print(f"  κ₆₄ shape: {kappa64.shape}, built in {time.time()-t0:.2f}s")
    kappa_nonzero = np.count_nonzero(np.abs(kappa64) > 1e-15)
    kappa_offdiag = kappa_nonzero - 64
    print(f"  κ non-zero entries: {kappa_nonzero} (diagonal: 64, off-diagonal: {kappa_offdiag})")

    print()
    print("Building T₆₄ = κ₆₄ @ F₆₄...")
    T64 = kappa64 @ F64
    print(f"  T₆₄ shape: {T64.shape}")

    # ═══ EIGENSPECTRUM ═══
    print()
    print("=" * 70)
    print("  EIGENSPECTRUM")
    print("=" * 70)
    evals, evecs = eigenspectrum(T64)

    # Basic stats
    mags = np.abs(evals)
    print(f"  Max |λ|: {np.max(mags):.10f}")
    print(f"  Min |λ|: {np.min(mags):.10f}")
    print(f"  Spectral radius: {np.max(mags):.10f}")

    # Phase sum
    ps = phase_sum(T64)
    print(f"  Phase sum: {ps:.8f}")
    print(f"    = {ps/np.pi:.8f}π")
    # Expected: ℂ⁴ gives -π/6, ℂ⁸ gives -π/3 = 2×(-π/6)
    # ℂ⁶⁴ = ℂ⁴ ⊗ ℂ⁴ ⊗ ℂ⁴, so phase sum should be 3×(-π/6) = -π/2
    print(f"    Expected (3 × -π/6 = -π/2): {-np.pi/2:.8f}")

    # Singular values
    sv = singular_values(T64)
    print(f"\n  Singular values (top 10):")
    for i, s in enumerate(sv[:10]):
        print(f"    s_{i}: {s:.10f}")
    print(f"  Singular values (bottom 5):")
    for i, s in enumerate(sv[-5:]):
        print(f"    s_{64-5+i}: {s:.10f}")

    # Unique magnitudes
    unique_mags = np.unique(np.round(mags, 8))
    print(f"\n  Unique eigenvalue magnitudes: {len(unique_mags)}")
    for mag in unique_mags:
        count = np.sum(np.abs(mags - mag) < 1e-6)
        print(f"    |λ| = {mag:.10f}  (degeneracy {count})")

    # Unique phases
    unique_phases = np.unique(np.round(np.angle(evals), 6))
    print(f"\n  Unique eigenvalue phases: {len(unique_phases)}")
    for ph in unique_phases[:20]:  # first 20
        count = np.sum(np.abs(np.angle(evals) - ph) < 1e-4)
        print(f"    arg(λ) = {ph:+.8f} rad  ({np.degrees(ph):+.3f}°)  (degeneracy {count})")
    if len(unique_phases) > 20:
        print(f"    ... ({len(unique_phases) - 20} more)")

    # ═══ FRAMEWORK CONSTANT SEARCH ═══
    print()
    print("=" * 70)
    print("  FRAMEWORK CONSTANT SEARCH")
    print("=" * 70)
    matches = search_framework_constants(evals)
    if matches:
        for m in matches[:30]:
            print(f"  [{m['type']:9s}] {m['eigenvalue_property']}")
            print(f"             ≈ {m['framework_match']} = {m['framework_value']:.8f}  (error: {m['error_pct']:.4f}%)")
            if 'degeneracy' in m:
                print(f"             degeneracy: {m['degeneracy']}")
            print()
    else:
        print("  No matches found within 1% tolerance.")

    # ═══ FIXED POINT ═══
    print()
    print("=" * 70)
    print("  FIXED POINT (iterating from uniform)")
    print("=" * 70)

    print("  Running 50000 iterations...")
    t0 = time.time()
    w = weights(T64, steps=50000)
    dt = time.time() - t0
    print(f"  Converged in {dt:.1f}s")

    # Scale decomposition
    decomp = scale_decomposition(w)

    station_names = ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']
    for scale_name, key in [('⊙Λ (greater whole)', 'Λ'), ('⊙λ (self)', 'λ'), ('⊙λ\' (parts)', 'λ\'')]:
        print(f"\n  {scale_name}:")
        for sn, val in decomp[f'{key}_stations'].items():
            bar = '#' * int(val * 100)
            print(f"    {sn}: {val:.6f}  [{bar}]")

    # Check if all three scales see the same distribution (A3)
    print(f"\n  A3 test (same structure at every scale):")
    w_L = decomp['greater_whole']
    w_S = decomp['self']
    w_P = decomp['parts']
    print(f"    Λ-λ distance: {np.linalg.norm(w_L - w_S):.6f}")
    print(f"    λ-λ' distance: {np.linalg.norm(w_S - w_P):.6f}")
    print(f"    Λ-λ' distance: {np.linalg.norm(w_L - w_P):.6f}")

    # Top 10 most weighted states
    print(f"\n  Top 10 most weighted states:")
    top_indices = np.argsort(-w)[:10]
    for rank, idx in enumerate(top_indices):
        i_L = idx // 16
        j_S = (idx % 16) // 4
        k_P = idx % 4
        print(f"    #{rank+1}: |{station_names[i_L]}, {station_names[j_S]}, {station_names[k_P]}⟩  w = {w[idx]:.6f}")

    # ═══ CHARACTERISTIC POLYNOMIAL ═══
    print()
    print("=" * 70)
    print("  CHARACTERISTIC POLYNOMIAL")
    print("=" * 70)

    coeffs = characteristic_polynomial_coefficients(T64)
    print(f"  Degree: {len(coeffs) - 1}")
    print(f"  Leading coefficient (c₆₄): {coeffs[-1]:.6f}")
    print(f"  Constant term (c₀ = det(T)): {coeffs[0]:.10f}")
    det_T = np.linalg.det(T64)
    print(f"  det(T₆₄) directly: {det_T:.10f}")
    print(f"  |det(T₆₄)|: {abs(det_T):.10f}")
    print(f"  arg(det(T₆₄))/π: {np.angle(det_T)/np.pi:.8f}")

    # Trace
    tr = np.trace(T64)
    print(f"  Tr(T₆₄): {tr:.10f}")
    print(f"  |Tr(T₆₄)|: {abs(tr):.10f}")
    print(f"  arg(Tr(T₆₄))/π: {np.angle(tr)/np.pi:.8f}")

    # Key polynomial invariants
    print(f"\n  Key invariants:")
    print(f"    Tr(T)    = {tr:.8f}  (sum of eigenvalues)")
    print(f"    det(T)   = {det_T:.8f}  (product of eigenvalues)")
    print(f"    |det(T)| = {abs(det_T):.8f}")

    # Check if determinant matches (1+α)^k × (1-α)^(64-k)
    # For ℂ⁴: sv = {(1+α)², (1-α)²}, det = (1+α)²(1-α)² = (1-α²)²
    # For ℂ⁶⁴ (tensor of three ℂ⁴s): det should be (det_4)³
    det_4_pred = (1 - ALPHA**2)**2
    det_64_pred = det_4_pred**3
    print(f"    Predicted |det| from (1-α²)⁶: {det_64_pred:.10f}")
    print(f"    Actual |det|:                  {abs(det_T):.10f}")
    print(f"    Ratio: {abs(det_T) / det_64_pred:.8f}")

    print()
    print("=" * 70)
    print("  DONE")
    print("=" * 70)
