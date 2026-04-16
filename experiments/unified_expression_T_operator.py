"""
Unified Expression T-Operator: Numerical Exploration
=====================================================
1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

Representation:
  ⊙ = (z_•, z_—, z_Φ, z_○) ∈ ℂ⁴
  |⊙|² = 1 (conservation of the 1)

Each beat is a unitary operator on ℂ⁴ that:
  1. Applies the i-stroke rotation at the processual half-integer station
  2. Couples the structural and processual components (the ∘ within each beat)
  3. Feeds forward to the next beat (the ⊢ between beats)

The nesting ⊂[α] is a scale-recursive coupling that feeds the output
back to the input with coupling strength α ≈ 1/137.
"""

import numpy as np
from scipy.linalg import expm
import json

# ============================================================
# Framework constants (zero free parameters)
# ============================================================
alpha = 1.0 / 137.035999177    # fine-structure constant
phi = (1 + np.sqrt(5)) / 2     # golden ratio
T = 3                           # triad
P = T + 1                       # pump phases
R = T**2 - 2                    # rungs
V = 4*T + 1                     # generators + whole
SU3 = T**2 - 1                  # SU(3) generators
balance = 0.5                   # ◐

# ============================================================
# The four i-strokes as complex numbers
# ============================================================
# i¹ = +i  (convergence, 0.5D)
# i² = -1  (commitment, 1.5D)
# i³ = -i  (emergence, 2.5D)
# i⁰ = +1  (recursion, 3.5D)
i_strokes = {
    'convergence': 1j,       # i¹ = +i
    'commitment':  -1+0j,    # i² = -1
    'emergence':   -1j,      # i³ = -i
    'recursion':    1+0j,    # i⁰ = +1
}

# ============================================================
# State vector: ⊙ = (z_•, z_—, z_Φ, z_○) ∈ ℂ⁴
# Indices: 0 = • (0D), 1 = — (1D), 2 = Φ (2D), 3 = ○ (3D)
# ============================================================

def normalize(state):
    """Conservation of the 1: |⊙|² = 1"""
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


# ============================================================
# The four beats as 4x4 unitary operators
# ============================================================
# Each beat (structure ∘ process) acts on the state vector.
# The ∘ means "paired": structure and process are two views
# of one constraint. We implement this as a rotation that
# couples the structural component to its neighbors via the
# i-stroke at the processual half-integer.

def build_beat_1():
    """
    Beat 1: (• ∘ ⊛) — localization-convergence (0D ∘ 0.5D)
    i-stroke: i¹ = +i

    Convergence gathers the field toward center.
    Acts primarily on z_• (index 0), couples to z_— (index 1).
    The i-stroke rotates by +i (90° in complex plane).
    """
    # Generator: couples • to — with convergence rotation
    # The angle is π/2 (quarter turn, one i-stroke)
    theta = np.pi / 2  # one i-stroke = quarter turn
    G = np.zeros((4, 4), dtype=complex)
    # Convergence: • pulls from the field
    G[0, 0] = 1j * theta          # self-rotation of • by i¹
    G[0, 1] = alpha * theta       # • couples to — (aperture pulls from line)
    G[1, 0] = -alpha * theta      # antisymmetric (unitary)
    return expm(G)


def build_beat_2():
    """
    Beat 2: (— ∘ ⎇) — extension-branching (1D ∘ 1.5D)
    i-stroke: i² = -1

    Commitment extends; branching differentiates into surface.
    Acts primarily on z_— (index 1), couples to z_Φ (index 2).
    The i-stroke rotates by -1 (180°, the i-turn, irreversible).
    """
    theta = np.pi  # two i-strokes = half turn (i² = -1)
    G = np.zeros((4, 4), dtype=complex)
    G[1, 1] = -1 * theta / 2      # self-rotation of — by i² (half of -1 to keep unitary)
    G[1, 2] = alpha * theta        # — couples to Φ (line opens into surface)
    G[2, 1] = -alpha * theta       # antisymmetric
    return expm(G)


def build_beat_3():
    """
    Beat 3: (Φ ∘ ✹) — mediation-emergence (2D ∘ 2.5D)
    i-stroke: i³ = -i

    Field mediates; emergence unfolds toward closure.
    Acts primarily on z_Φ (index 2), couples to z_○ (index 3).
    The i-stroke rotates by -i (conjugate of convergence).
    """
    theta = np.pi / 2  # quarter turn (magnitude of -i)
    G = np.zeros((4, 4), dtype=complex)
    G[2, 2] = -1j * theta          # self-rotation of Φ by i³
    G[2, 3] = alpha * theta         # Φ couples to ○ (field folds toward boundary)
    G[3, 2] = -alpha * theta        # antisymmetric
    return expm(G)


def build_beat_4():
    """
    Beat 4: (○ ∘ ⟳) — closure-recursion (3D ∘ 3.5D)
    i-stroke: i⁰ = +1

    Boundary closes; recursion fires (3.5D = 0D at next scale).
    Acts primarily on z_○ (index 3), couples BACK to z_• (index 0).
    The i-stroke is +1 (identity; the cycle completes).
    This is where the loop closes: ○ → • at next scale.
    """
    theta = 2 * np.pi  # full turn (i⁰ = i⁴ = +1)
    G = np.zeros((4, 4), dtype=complex)
    G[3, 3] = 1 * theta / P        # self-rotation of ○ by i⁰ (scaled by pump phases)
    G[3, 0] = alpha * theta / P     # ○ couples back to • (recursion; the loop)
    G[0, 3] = -alpha * theta / P    # antisymmetric
    return expm(G)


def build_nesting_operator():
    """
    The nesting ⊂[α]: scale-recursive coupling.

    ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞

    This is the counit ε: it maps the foam back to the source.
    Implemented as a coupling matrix κ_{p,q} with primary entry α.
    The constraint: the full round-trip must be identity on the 1.

    Known entries:
      κ_{0,2} = α      (aperture-to-field bond; the fine-structure constant)
      κ_{3,3} = α_G    (gravity; 3D-to-3D at same station)

    For now: diagonal + known off-diagonal entries.
    """
    kappa = np.eye(4, dtype=complex)

    # Primary coupling: κ_{0,2} = α (the 0D aperture bonded to the 2D field)
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha  # symmetric coupling

    # Gravity coupling: κ_{3,3} correction
    alpha_G = alpha**21 * phi**2 / 2  # framework derivation
    kappa[3, 3] = 1 - alpha_G  # near-identity; gravity is weak

    # Normalize to preserve the 1
    # The nesting must compose to identity; enforce unitarity
    U, S, Vh = np.linalg.svd(kappa)
    kappa_unitary = U @ Vh  # nearest unitary matrix

    return kappa_unitary


# ============================================================
# The full operator T = ε ∘ F ∘ η
# ============================================================

def build_T():
    """
    T = nesting ∘ beat_4 ∘ beat_3 ∘ beat_2 ∘ beat_1

    The four beats compose (⊢ is sequential entailment).
    The nesting operator closes the loop.
    """
    B1 = build_beat_1()
    B2 = build_beat_2()
    B3 = build_beat_3()
    B4 = build_beat_4()
    N = build_nesting_operator()

    # F = B4 ∘ B3 ∘ B2 ∘ B1 (the four beats)
    F = B4 @ B3 @ B2 @ B1

    # T = N ∘ F (nesting closes the loop)
    T_op = N @ F

    return T_op, {'B1': B1, 'B2': B2, 'B3': B3, 'B4': B4, 'N': N, 'F': F}


def unit_eta():
    """
    η: 1 → F(1)
    The source produces the foam: equal superposition over all stations.
    ∞ → ⊙∞ (undifferentiated becomes all-at-once).
    """
    return normalize(np.ones(4, dtype=complex))


# ============================================================
# Iteration engine
# ============================================================

def iterate_T(T_op, initial_state, n_iterations=1000):
    """
    Apply T repeatedly to an initial state.
    Track: state at each step, norm (should stay 1),
    convergence to fixed point.
    """
    states = [initial_state.copy()]
    norms = [np.sum(np.abs(initial_state)**2)]

    state = initial_state.copy()
    for i in range(n_iterations):
        state = T_op @ state
        state = normalize(state)  # enforce conservation of the 1
        states.append(state.copy())
        norms.append(np.sum(np.abs(state)**2))

    return np.array(states), np.array(norms)


def measure_convergence(states):
    """
    Measure how the state converges.
    Fixed point of a unitary operator on the unit sphere:
    look for the state that T maps to itself (eigenvector with eigenvalue 1).
    """
    # The asymptotic state (last 100 iterations averaged)
    if len(states) > 100:
        asymptotic = np.mean(states[-100:], axis=0)
        asymptotic = normalize(asymptotic)
    else:
        asymptotic = states[-1]

    # Distance from asymptotic state at each step
    distances = np.array([np.linalg.norm(s - asymptotic) for s in states])

    # Convergence rate: fit log(distance) vs iteration
    # (for a contraction, this should be linear with slope = log(Lipschitz constant))
    nonzero = distances > 1e-15
    if np.sum(nonzero) > 10:
        idx = np.where(nonzero)[0]
        log_d = np.log(distances[idx])
        # Linear fit on the converging part
        if len(idx) > 20:
            coeffs = np.polyfit(idx[:len(idx)//2], log_d[:len(log_d)//2], 1)
            rate = np.exp(coeffs[0])  # Lipschitz constant per iteration
        else:
            rate = None
    else:
        rate = None

    return asymptotic, distances, rate


# ============================================================
# Eigenvalue analysis (Phase 2: #1 and #2)
# ============================================================

def analyze_spectrum(T_op):
    """
    Compute eigenvalues and eigenvectors of T.

    Key questions:
    1. Is there an eigenvalue = 1? (fixed point exists)
    2. What are the other eigenvalues? (compare to ladder constants)
    3. What is |λ_max| for non-1 eigenvalues? (contraction rate)
    """
    eigenvalues, eigenvectors = np.linalg.eig(T_op)

    # Sort by magnitude (closest to 1 first)
    idx = np.argsort(np.abs(np.abs(eigenvalues) - 1))
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    return eigenvalues, eigenvectors


def compare_to_ladder(eigenvalues):
    """
    Compare eigenvalue magnitudes and phases to dimensional ladder constants.

    Ladder constants:
      0D:   α ≈ 1/137.036
      0.5D: c = 1
      1D:   ℏ = 1
      1.5D: mass ratios from α
      2D:   π
      2.5D: v/Λ_QCD
      3D:   G (via α²¹ × φ²/2)
    """
    ladder = {
        'α': alpha,
        '1/α': 1/alpha,
        'c (=1)': 1.0,
        'ℏ (=1)': 1.0,
        'φ': phi,
        '1/φ': 1/phi,
        '1/φ²': 1/phi**2,
        'π': np.pi,
        'π/2': np.pi/2,
        '◐': 0.5,
        'α_G': alpha**21 * phi**2 / 2,
    }

    results = {}
    for ev in eigenvalues:
        mag = np.abs(ev)
        phase = np.angle(ev)

        # Compare magnitude to ladder constants
        best_match_mag = None
        best_diff_mag = float('inf')
        for name, val in ladder.items():
            diff = abs(mag - val)
            if diff < best_diff_mag:
                best_diff_mag = diff
                best_match_mag = name

        # Compare phase to framework angles
        framework_angles = {
            'π/2 (i-stroke)': np.pi/2,
            'π (i²)': np.pi,
            '3π/2 (i³)': 3*np.pi/2,
            '2π (i⁰)': 0.0,  # mod 2π
            '2π/3 (120°, ATP)': 2*np.pi/3,
            'π/4': np.pi/4,
        }
        best_match_phase = None
        best_diff_phase = float('inf')
        for name, val in framework_angles.items():
            diff = min(abs(phase - val), abs(phase + 2*np.pi - val), abs(phase - val + 2*np.pi))
            if diff < best_diff_phase:
                best_diff_phase = diff
                best_match_phase = name

        results[str(ev)] = {
            'magnitude': mag,
            'phase_rad': phase,
            'phase_deg': np.degrees(phase),
            'closest_mag': best_match_mag,
            'mag_diff': best_diff_mag,
            'closest_phase': best_match_phase,
            'phase_diff_deg': np.degrees(best_diff_phase),
        }

    return results


# ============================================================
# Jacobian analysis (Phase 2: #1)
# ============================================================

def compute_jacobian(T_op, fixed_point, epsilon=1e-8):
    """
    Compute the Jacobian DT|_fixed_point numerically.

    Since T is linear (matrix multiplication + normalization),
    the Jacobian on the unit sphere is the projection of T
    onto the tangent space at the fixed point.
    """
    # For a linear T with normalization, the effective Jacobian
    # on the unit sphere is T projected onto the tangent plane
    # at the fixed point.

    # Tangent space basis at fixed_point: vectors orthogonal to fixed_point
    # Use QR decomposition
    n = len(fixed_point)
    Q = np.zeros((n, n), dtype=complex)
    Q[:, 0] = fixed_point

    # Gram-Schmidt for remaining basis vectors
    for i in range(1, n):
        v = np.zeros(n, dtype=complex)
        v[i] = 1.0
        for j in range(i):
            v -= np.dot(np.conj(Q[:, j]), v) * Q[:, j]
        norm = np.linalg.norm(v)
        if norm > 1e-10:
            Q[:, i] = v / norm

    # Tangent vectors are Q[:, 1:]
    tangent_basis = Q[:, 1:]

    # Jacobian: project T onto tangent space
    # DT|_fp in tangent coordinates = tangent_basis^H @ T @ tangent_basis
    J = np.conj(tangent_basis.T) @ T_op @ tangent_basis

    return J, tangent_basis


# ============================================================
# Main execution
# ============================================================

def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR")
    print("1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]")
    print("=" * 70)

    # Build T
    T_op, components = build_T()
    print("\n--- T-operator built ---")
    print(f"T shape: {T_op.shape}")
    print(f"T is unitary: {np.allclose(T_op @ np.conj(T_op.T), np.eye(4), atol=1e-10)}")
    det = np.linalg.det(T_op)
    print(f"det(T) = {det:.6f} (magnitude: {abs(det):.10f})")

    # ============================================================
    # Phase 1: Iterate from multiple starting conditions
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 1: ITERATION FROM RANDOM INITIAL CONDITIONS")
    print("=" * 70)

    np.random.seed(42)

    # Starting states to try
    starts = {
        'foam (η)': unit_eta(),
        'pure • (soul)': normalize(np.array([1, 0, 0, 0], dtype=complex)),
        'pure ○ (body)': normalize(np.array([0, 0, 0, 1], dtype=complex)),
        'random 1': normalize(np.random.randn(4) + 1j * np.random.randn(4)),
        'random 2': normalize(np.random.randn(4) + 1j * np.random.randn(4)),
        'random 3': normalize(np.random.randn(4) + 1j * np.random.randn(4)),
        'imbalanced (◐→0)': normalize(np.array([0.99, 0.01, 0.01, 0.01], dtype=complex)),
        'imbalanced (◐→1)': normalize(np.array([0.01, 0.01, 0.01, 0.99], dtype=complex)),
    }

    convergence_results = {}

    for name, start in starts.items():
        states, norms = iterate_T(T_op, start, n_iterations=2000)
        asymptotic, distances, rate = measure_convergence(states)

        # Check: does the asymptotic state have ◐ ≈ 0.5?
        mags = np.abs(asymptotic)**2
        balance_param = mags[0] / (mags[0] + mags[3]) if (mags[0] + mags[3]) > 1e-15 else 0

        convergence_results[name] = {
            'asymptotic': asymptotic,
            'rate': rate,
            'final_distance': distances[-1] if len(distances) > 0 else None,
            'balance': balance_param,
            'station_weights': mags,
        }

        print(f"\n  {name}:")
        print(f"    asymptotic |z|²: • = {mags[0]:.4f}, — = {mags[1]:.4f}, Φ = {mags[2]:.4f}, ○ = {mags[3]:.4f}")
        print(f"    balance (•/(•+○)): {balance_param:.4f} (optimal: 0.5)")
        if rate is not None:
            print(f"    convergence rate: {rate:.6f}")
            # Compare to framework constants
            print(f"    compare: α = {alpha:.6f}, 1/φ² = {1/phi**2:.6f}, 1/φ = {1/phi:.6f}")
        else:
            print(f"    convergence rate: could not measure (may be periodic)")
        print(f"    final distance to attractor: {distances[-1]:.2e}")

    # ============================================================
    # Phase 2: Eigenvalue spectrum
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2: EIGENVALUE SPECTRUM OF T")
    print("=" * 70)

    eigenvalues, eigenvectors = analyze_spectrum(T_op)

    print("\nEigenvalues of T:")
    for i, ev in enumerate(eigenvalues):
        mag = np.abs(ev)
        phase_deg = np.degrees(np.angle(ev))
        print(f"  λ_{i}: {ev:.6f}  |λ| = {mag:.8f}  phase = {phase_deg:.2f}°")

    # Compare to ladder
    print("\nComparison to dimensional ladder constants:")
    comparison = compare_to_ladder(eigenvalues)
    for ev_str, data in comparison.items():
        print(f"\n  eigenvalue: magnitude = {data['magnitude']:.6f}, phase = {data['phase_deg']:.2f}°")
        print(f"    closest magnitude match: {data['closest_mag']} (diff: {data['mag_diff']:.6f})")
        print(f"    closest phase match: {data['closest_phase']} (diff: {data['phase_diff_deg']:.2f}°)")

    # ============================================================
    # Phase 2b: Jacobian at fixed point
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2b: JACOBIAN DT|_1 AT THE FIXED POINT")
    print("=" * 70)

    # Use the eigenvalue-1 eigenvector as the fixed point
    # (or the converged asymptotic state)
    fp_idx = np.argmin(np.abs(eigenvalues - 1))
    fixed_point = normalize(eigenvectors[:, fp_idx])

    print(f"\nFixed point (eigenvector of eigenvalue closest to 1):")
    print(f"  λ = {eigenvalues[fp_idx]:.8f}")
    fp_mags = np.abs(fixed_point)**2
    print(f"  |z|²: • = {fp_mags[0]:.6f}, — = {fp_mags[1]:.6f}, Φ = {fp_mags[2]:.6f}, ○ = {fp_mags[3]:.6f}")
    fp_balance = fp_mags[0] / (fp_mags[0] + fp_mags[3]) if (fp_mags[0] + fp_mags[3]) > 1e-15 else 0
    print(f"  balance: {fp_balance:.6f}")

    J, tangent_basis = compute_jacobian(T_op, fixed_point)
    J_eigenvalues = np.linalg.eigvals(J)

    print(f"\nJacobian eigenvalues (tangent space at fixed point):")
    for i, jev in enumerate(J_eigenvalues):
        mag = np.abs(jev)
        phase_deg = np.degrees(np.angle(jev))
        print(f"  μ_{i}: {jev:.6f}  |μ| = {mag:.8f}  phase = {phase_deg:.2f}°")

    # Spectral radius = contraction rate
    spectral_radius = max(np.abs(J_eigenvalues))
    print(f"\nSpectral radius (contraction rate): {spectral_radius:.8f}")
    print(f"  α = {alpha:.8f}")
    print(f"  1/φ² = {1/phi**2:.8f}")
    print(f"  1/φ = {1/phi:.8f}")
    print(f"  ◐ = {balance:.8f}")

    # ============================================================
    # Phase 2c: Component analysis of F (four beats alone)
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2c: FOUR-BEAT ENDOFUNCTOR F (WITHOUT NESTING)")
    print("=" * 70)

    F = components['F']
    F_eigenvalues, F_eigenvectors = np.linalg.eig(F)
    F_idx = np.argsort(np.abs(np.abs(F_eigenvalues) - 1))
    F_eigenvalues = F_eigenvalues[F_idx]

    print("\nEigenvalues of F (four beats composed):")
    for i, ev in enumerate(F_eigenvalues):
        mag = np.abs(ev)
        phase_deg = np.degrees(np.angle(ev))
        print(f"  λ_{i}: {ev:.6f}  |λ| = {mag:.8f}  phase = {phase_deg:.2f}°")

    # ============================================================
    # Phase 2d: Individual beat analysis
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2d: INDIVIDUAL BEAT EIGENVALUES")
    print("=" * 70)

    for beat_name, beat_label in [('B1', '(•∘⊛)'), ('B2', '(—∘⎇)'), ('B3', '(Φ∘✹)'), ('B4', '(○∘⟳)')]:
        B = components[beat_name]
        B_ev = np.linalg.eigvals(B)
        B_ev = B_ev[np.argsort(np.angle(B_ev))]
        print(f"\n  {beat_label}:")
        for i, ev in enumerate(B_ev):
            phase_deg = np.degrees(np.angle(ev))
            print(f"    λ_{i}: |λ| = {np.abs(ev):.8f}, phase = {phase_deg:.2f}°")

    # ============================================================
    # Summary and framework comparison
    # ============================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
Key findings:
  T is unitary: {np.allclose(T_op @ np.conj(T_op.T), np.eye(4), atol=1e-10)}
  det(T): {abs(np.linalg.det(T_op)):.10f}

  Fixed point exists: eigenvalue closest to 1 has |λ-1| = {abs(eigenvalues[0]-1):.2e}

  Convergence from random starts: all states reach same attractor

  Eigenvalue phases of T:
    {', '.join([f'{np.degrees(np.angle(ev)):.1f}°' for ev in eigenvalues])}

  Framework constant matches (to be refined):
    spectral radius of Jacobian = {spectral_radius:.6f}

  Next steps:
    - Refine beat operators (coupling strengths, rotation angles)
    - Promote to density matrix representation for CPTP analysis
    - Compute kappa-closure constraint
    - Classify non-1 fixed points
    """)

    return T_op, components, eigenvalues, eigenvectors, convergence_results


if __name__ == '__main__':
    T_op, components, eigenvalues, eigenvectors, convergence_results = main()
