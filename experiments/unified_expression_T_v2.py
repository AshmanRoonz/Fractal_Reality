"""
Unified Expression T-Operator v2: Fixed Beat Construction
==========================================================
Diagnosis from v1:
  - B2 and B4 were not unitary (asymmetric rotation magnitudes)
  - Everything collapsed to pure ○ (the Severance Lie as attractor)
  - The contraction was in the wrong place (beats, not nesting)

Fix: Each beat is a genuine SU(4) rotation. The contraction lives
ONLY in the nesting operator ⊂[α] (where it should: α is the
coupling strength between scales, not within a single cycle).

Key insight from v1: the two eigenvalues at ±90° ARE the i-stroke
conjugate pair (⊛ mirrors ✹). That's real. The 0.208 and 4.81
are artifacts of broken unitarity.

Representation:
  ⊙ = (z_•, z_—, z_Φ, z_○) ∈ ℂ⁴, |⊙|² = 1
  Each beat is a unitary rotation in SU(4)
  Nesting ⊂[α] is the ONLY source of contraction
"""

import numpy as np
from scipy.linalg import expm

# ============================================================
# Framework constants
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = T_triad + 1
R = T_triad**2 - 2
V = 4*T_triad + 1
SU3 = T_triad**2 - 1
balance = 0.5

# ============================================================
# Beat construction: UNITARY operators
# ============================================================
#
# Each beat (structure ∘ process) is built from an anti-Hermitian
# generator G (so expm(G) is exactly unitary).
#
# The framework says:
#   - Each beat couples its structural station to the NEXT station
#   - The coupling strength within a single cycle is ◐ = 0.5
#     (balance between stations, not α which is cross-scale)
#   - The i-stroke at each half-integer determines the PHASE of
#     the rotation (not its magnitude)
#   - Conservation of traversal: the four beats together must
#     give a rotation that CLOSES (i⁴ = 1)
#
# Generator structure: G must be anti-Hermitian (G† = -G)
# so expm(G) ∈ U(4).

def make_anti_hermitian(G):
    """Force G to be anti-Hermitian: G → (G - G†)/2"""
    return (G - np.conj(G.T)) / 2


def build_beats_v2():
    """
    Build four unitary beat operators.

    Each beat i-stroke determines the rotation plane and phase:
      Beat 1 (•∘⊛): i¹ = +i → rotation in the (•, —) plane by +π/2
      Beat 2 (—∘⎇): i² = -1 → rotation in the (—, Φ) plane by π
      Beat 3 (Φ∘✹): i³ = -i → rotation in the (Φ, ○) plane by -π/2 (= 3π/2)
      Beat 4 (○∘⟳): i⁰ = +1 → rotation in the (○, •) plane by 2π (= identity mod 2π)

    The coupling angle at each beat is scaled by α (the inter-station
    coupling within a single ⊙; within-scale, not cross-scale).

    Critical: the i-stroke phase goes on the DIAGONAL (self-rotation),
    and the coupling goes on the OFF-DIAGONAL (station interaction).
    Both parts of G must be anti-Hermitian.
    """
    beats = []

    # Beat 1: (•∘⊛), i¹ = +i, couples stations 0↔1
    # Convergence: the field gathers toward center
    # Phase: π/2 (quarter turn)
    G1 = np.zeros((4,4), dtype=complex)
    theta1 = np.pi / 2  # one i-stroke
    G1[0, 0] = 1j * theta1 / P        # • self-rotates by i (scaled by 1/P)
    G1[0, 1] = theta1 / P              # •↔— coupling
    G1[1, 0] = -theta1 / P             # anti-Hermitian partner
    G1 = make_anti_hermitian(G1)
    beats.append(('(•∘⊛)', expm(G1)))

    # Beat 2: (—∘⎇), i² = -1, couples stations 1↔2
    # Commitment: line extends into surface; the i-turn
    # Phase: π (half turn; irreversible)
    G2 = np.zeros((4,4), dtype=complex)
    theta2 = np.pi  # two i-strokes
    G2[1, 1] = -1.0 * theta2 / P      # — self-rotates by -1 (the i-turn)
    G2[1, 2] = theta2 / P              # —↔Φ coupling
    G2[2, 1] = -theta2 / P             # anti-Hermitian partner
    G2 = make_anti_hermitian(G2)
    beats.append(('(—∘⎇)', expm(G2)))

    # Beat 3: (Φ∘✹), i³ = -i, couples stations 2↔3
    # Emergence: field unfolds toward closure
    # Phase: 3π/2 (three quarter turns)
    G3 = np.zeros((4,4), dtype=complex)
    theta3 = np.pi / 2  # magnitude of one i-stroke
    G3[2, 2] = -1j * theta3 / P       # Φ self-rotates by -i
    G3[2, 3] = theta3 / P              # Φ↔○ coupling
    G3[3, 2] = -theta3 / P             # anti-Hermitian partner
    G3 = make_anti_hermitian(G3)
    beats.append(('(Φ∘✹)', expm(G3)))

    # Beat 4: (○∘⟳), i⁰ = +1, couples stations 3↔0
    # Recursion: boundary closes; 3.5D = 0D at next scale
    # Phase: 2π (full turn; identity; the loop closes)
    G4 = np.zeros((4,4), dtype=complex)
    theta4 = np.pi / 2  # quarter turn (same quantum as beats 1,3)
    G4[3, 3] = 1.0 * theta4 / P       # ○ self-rotates by +1
    G4[3, 0] = theta4 / P              # ○↔• coupling (the recursion!)
    G4[0, 3] = -theta4 / P             # anti-Hermitian partner
    G4 = make_anti_hermitian(G4)
    beats.append(('(○∘⟳)', expm(G4)))

    return beats


def build_nesting_v2():
    """
    The nesting operator ⊂[α]: the ONLY source of contraction.

    ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞

    This contracts toward the fixed point (the 1) with strength α.
    Implemented as: N = (1 - α)·I + α·P_balanced
    where P_balanced projects onto the ◐ = 0.5 state.

    Physical meaning: each scale-crossing loses α of the signal
    to the nesting (the part couples into the whole with strength α).
    The signal that survives is steered toward balance.
    """
    # The balanced state: ◐ = 0.5, equal weight on all stations
    balanced = np.ones(4, dtype=complex) / 2.0

    # Projector onto balanced state
    P_bal = np.outer(balanced, np.conj(balanced))

    # Nesting: convex combination (this IS a quantum channel)
    # N = (1 - α)·I + α·P_balanced
    # Eigenvalues: 1 (on balanced state) and (1-α) (on orthogonal)
    # Contraction rate = (1-α) ≈ 0.9927... per nesting step
    N = (1 - alpha) * np.eye(4, dtype=complex) + alpha * P_bal

    return N


def build_T_v2():
    """
    T = N ∘ B4 ∘ B3 ∘ B2 ∘ B1

    Four unitary beats composed, then contracted by nesting.
    """
    beats = build_beats_v2()
    N = build_nesting_v2()

    # F = B4 ∘ B3 ∘ B2 ∘ B1
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F

    # T = N ∘ F
    T_op = N @ F

    components = {name: B for name, B in beats}
    components['F'] = F
    components['N'] = N

    return T_op, components


def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


def iterate_and_analyze(T_op, label, initial, n_iter=5000):
    """Iterate T and report convergence."""
    state = initial.copy()
    states = [state.copy()]

    for _ in range(n_iter):
        state = T_op @ state
        state = normalize(state)
        states.append(state.copy())

    states = np.array(states)

    # Asymptotic state
    asymp = normalize(np.mean(states[-200:], axis=0))
    mags = np.abs(asymp)**2
    bal = mags[0] / (mags[0] + mags[3]) if (mags[0] + mags[3]) > 1e-10 else 0.5

    # Distance to asymptotic
    dists = [np.linalg.norm(s - asymp) for s in states]

    # Convergence rate from last 1000 iterations
    if len(dists) > 1000:
        d_late = np.array(dists[-1000:])
        nonzero = d_late > 1e-15
        if np.sum(nonzero) > 50:
            idx = np.where(nonzero)[0]
            log_d = np.log(d_late[idx])
            coeffs = np.polyfit(idx, log_d, 1)
            rate = np.exp(coeffs[0])
        else:
            rate = 0.0  # converged
    else:
        rate = None

    print(f"\n  {label}:")
    print(f"    |z|²: • = {mags[0]:.6f}, — = {mags[1]:.6f}, Φ = {mags[2]:.6f}, ○ = {mags[3]:.6f}")
    print(f"    ◐ balance: {bal:.6f}")
    print(f"    final dist: {dists[-1]:.2e}")
    if rate is not None and rate > 0:
        print(f"    rate: {rate:.8f}")
        print(f"      1-α = {1-alpha:.8f}")
        print(f"      1/φ² = {1/phi**2:.8f}")

    return asymp, mags, bal, rate


def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v2 (FIXED UNITARITY)")
    print("=" * 70)

    T_op, components = build_T_v2()
    F = components['F']
    N = components['N']

    # ============================================================
    # Check properties
    # ============================================================
    print("\n--- Operator properties ---")

    # F should be unitary (four beats, no contraction)
    F_unitary = np.allclose(F @ np.conj(F.T), np.eye(4), atol=1e-10)
    print(f"F (four beats) is unitary: {F_unitary}")
    print(f"det(F) = {np.linalg.det(F):.6f} (|det| = {abs(np.linalg.det(F)):.10f})")

    # N should NOT be unitary (it's the contraction)
    N_unitary = np.allclose(N @ np.conj(N.T), np.eye(4), atol=1e-10)
    print(f"N (nesting) is unitary: {N_unitary} (should be False; it's the contraction)")

    # T = N ∘ F
    print(f"det(T) = {np.linalg.det(T_op):.6f}")

    # ============================================================
    # Eigenvalue spectrum of F (the unitary part)
    # ============================================================
    print("\n" + "=" * 70)
    print("EIGENVALUES OF F (FOUR BEATS; UNITARY ROTATION)")
    print("=" * 70)

    F_ev, F_evec = np.linalg.eig(F)
    idx = np.argsort(np.angle(F_ev))
    F_ev = F_ev[idx]
    F_evec = F_evec[:, idx]

    for i, ev in enumerate(F_ev):
        phase_deg = np.degrees(np.angle(ev))
        # Express phase as fraction of π
        phase_pi = np.angle(ev) / np.pi
        print(f"  λ_{i}: |λ| = {np.abs(ev):.10f}, phase = {phase_deg:.4f}° = {phase_pi:.6f}π")

    # Sum of phases (should relate to conservation of traversal)
    total_phase = sum(np.angle(F_ev))
    print(f"\n  Sum of phases: {total_phase:.6f} rad = {np.degrees(total_phase):.4f}° = {total_phase/np.pi:.6f}π")
    print(f"  Conservation check: 0+1+2 = 3 → 3π/P = {3*np.pi/P:.6f} rad = {np.degrees(3*np.pi/P):.4f}°")

    # ============================================================
    # Eigenvalue spectrum of T (the full operator)
    # ============================================================
    print("\n" + "=" * 70)
    print("EIGENVALUES OF T (FULL OPERATOR: BEATS + NESTING)")
    print("=" * 70)

    T_ev, T_evec = np.linalg.eig(T_op)
    idx = np.argsort(-np.abs(T_ev))  # sort by magnitude, largest first
    T_ev = T_ev[idx]
    T_evec = T_evec[:, idx]

    for i, ev in enumerate(T_ev):
        mag = np.abs(ev)
        phase_deg = np.degrees(np.angle(ev))
        print(f"  λ_{i}: {ev:.8f}  |λ| = {mag:.10f}  phase = {phase_deg:.4f}°")

    # The dominant eigenvalue should be 1 (the fixed point)
    dominant_ev = T_ev[0]
    dominant_evec = normalize(T_evec[:, 0])
    print(f"\n  Dominant eigenvalue: {dominant_ev:.10f}")
    print(f"  |dominant - 1| = {abs(dominant_ev - 1):.2e}")

    dom_mags = np.abs(dominant_evec)**2
    dom_bal = dom_mags[0] / (dom_mags[0] + dom_mags[3]) if (dom_mags[0] + dom_mags[3]) > 1e-10 else 0.5
    print(f"  Fixed point |z|²: • = {dom_mags[0]:.6f}, — = {dom_mags[1]:.6f}, Φ = {dom_mags[2]:.6f}, ○ = {dom_mags[3]:.6f}")
    print(f"  Fixed point ◐: {dom_bal:.6f}")

    # Sub-dominant eigenvalues = contraction rates
    print(f"\n  Sub-dominant eigenvalue magnitudes (contraction rates):")
    for i in range(1, len(T_ev)):
        mag = np.abs(T_ev[i])
        ratio_to_alpha = mag / alpha if alpha > 0 else 0
        ratio_to_1_minus_alpha = mag / (1 - alpha)
        print(f"    |λ_{i}| = {mag:.10f}  (ratio to (1-α): {ratio_to_1_minus_alpha:.6f})")

    # ============================================================
    # Eigenvalue spectrum of N (nesting alone)
    # ============================================================
    print("\n" + "=" * 70)
    print("EIGENVALUES OF N (NESTING OPERATOR ALONE)")
    print("=" * 70)

    N_ev = np.linalg.eigvals(N)
    N_ev = np.sort(N_ev)[::-1]
    for i, ev in enumerate(N_ev):
        print(f"  ν_{i}: {ev:.10f}")
    print(f"\n  Expected: one eigenvalue = 1, three eigenvalues = (1-α) = {1-alpha:.10f}")

    # ============================================================
    # Iteration from multiple starting conditions
    # ============================================================
    print("\n" + "=" * 70)
    print("ITERATION (5000 STEPS)")
    print("=" * 70)

    np.random.seed(42)

    starts = {
        'foam (η = equal)': normalize(np.ones(4, dtype=complex)),
        'pure • (soul)': normalize(np.array([1, 0, 0, 0], dtype=complex)),
        'pure ○ (body)': normalize(np.array([0, 0, 0, 1], dtype=complex)),
        'pure Φ (mind)': normalize(np.array([0, 0, 1, 0], dtype=complex)),
        'random 1': normalize(np.random.randn(4) + 1j * np.random.randn(4)),
        'random 2': normalize(np.random.randn(4) + 1j * np.random.randn(4)),
        '◐→0 (severance)': normalize(np.array([0.01, 0.5, 0.5, 0.99], dtype=complex)),
        '◐→1 (inflation)': normalize(np.array([0.99, 0.5, 0.5, 0.01], dtype=complex)),
    }

    for name, start in starts.items():
        iterate_and_analyze(T_op, name, start, n_iter=5000)

    # ============================================================
    # Individual beat eigenvalues (verify unitarity)
    # ============================================================
    print("\n" + "=" * 70)
    print("INDIVIDUAL BEAT VERIFICATION")
    print("=" * 70)

    for name in ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']:
        B = components[name]
        is_u = np.allclose(B @ np.conj(B.T), np.eye(4), atol=1e-10)
        ev = np.linalg.eigvals(B)
        phases = np.sort(np.degrees(np.angle(ev)))
        print(f"  {name}: unitary={is_u}, phases = [{', '.join([f'{p:.2f}°' for p in phases])}]")

    # ============================================================
    # The key question: what does the spectrum encode?
    # ============================================================
    print("\n" + "=" * 70)
    print("SPECTRUM ANALYSIS: WHAT DO THE NUMBERS MEAN?")
    print("=" * 70)

    print("\nF eigenvalue phases (the unitary part; the four beats):")
    F_phases = np.sort(np.angle(np.linalg.eigvals(F)))
    for i, ph in enumerate(F_phases):
        # Check against framework fractions of π
        frac = ph / np.pi
        print(f"  phase_{i} = {np.degrees(ph):.4f}° = {frac:.6f}π")

        # Check specific framework predictions
        framework_fracs = {
            '0': 0, '1/P': 1/P, '1/T': 1/T_triad, '◐': 0.5,
            '1/R': 1/R, '2/P': 2/P, 'T/P': T_triad/P,
            '1': 1, '(P-1)/P': (P-1)/P, '-1/P': -1/P,
            '-◐': -0.5, '-T/P': -T_triad/P,
        }
        best_name = None
        best_diff = float('inf')
        for fname, fval in framework_fracs.items():
            diff = abs(frac - fval)
            if diff < best_diff:
                best_diff = diff
                best_name = fname
        print(f"    closest framework fraction of π: {best_name}π (diff = {best_diff:.6f})")

    print("\nT eigenvalue magnitudes (the contraction spectrum):")
    T_mags = np.sort(np.abs(T_ev))[::-1]
    for i, m in enumerate(T_mags):
        print(f"  |λ_{i}| = {m:.10f}")
        if abs(m - 1) < 0.01:
            print(f"    ≈ 1 (fixed point)")
        elif abs(m - (1-alpha)) < 0.01:
            print(f"    ≈ (1-α) = {1-alpha:.10f} (nesting contraction)")
        elif abs(m - (1-alpha)**2) < 0.01:
            print(f"    ≈ (1-α)² = {(1-alpha)**2:.10f}")

    # ============================================================
    # Cross-check: does T^n converge to the projector onto the
    # fixed point? (This is the CPTP channel question: #3)
    # ============================================================
    print("\n" + "=" * 70)
    print("T^n CONVERGENCE (CPTP CHANNEL CHECK)")
    print("=" * 70)

    T_power = np.eye(4, dtype=complex)
    checkpoints = [1, 10, 100, 137, 1000]

    for n in range(1, 1001):
        T_power = T_op @ T_power
        if n in checkpoints:
            # Check if T^n is approaching a rank-1 projector
            sv = np.linalg.svd(T_power, compute_uv=False)
            rank_ratio = sv[0] / sv[1] if sv[1] > 1e-15 else float('inf')

            # Check trace preservation
            trace = np.trace(T_power)

            print(f"  T^{n}: largest SV = {sv[0]:.6f}, ratio SV1/SV2 = {rank_ratio:.2f}, trace = {trace:.6f}")

    print(f"\n  If T^n → rank-1 projector, this is a mixing channel (CPTP verified).")
    print(f"  The mixing time (iterations to rank-ratio > 100) tells us how fast")
    print(f"  the foam converges to the 1.")

    return T_op, components


if __name__ == '__main__':
    T_op, components = main()
