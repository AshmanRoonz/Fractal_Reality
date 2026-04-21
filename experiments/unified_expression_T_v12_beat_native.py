"""
T-operator v12: Beat-Native Operators
======================================

Rather than using a uniform hub-coupling for all four beats (v7 through v11),
v12 gives each beat its own generator topology that reflects its semantic
role in the framework:

    Beat 1: (•∘⊛) localization-convergence  phase i¹ = +i
        Topology: • ↔ Φ (single ray; aperture's direct line to the field)

    Beat 2: (—∘⎇) extension-branching        phase i² = -1
        Topology: — ↔ Φ  AND  — ↔ ○ (Y-fork; line splits into two outcomes)

    Beat 3: (Φ∘✹) mediation-emergence        phase i³ = -i (PUMP GATE station)
        Topology: Φ ↔ • (ln-side, minus sign) AND Φ ↔ ○ (exp-side, plus sign)
                + self-drive at Φ (substrate presence at the hub)
        Encodes the pump-gate asymmetry: eml(x, y) = exp(x) − ln(y) gives
        Φ its convergent partner (•, ln-side) and emergent partner (○, exp-side)
        with OPPOSITE signs; this is the framework's 2D native operator made
        explicit inside F.  — does not appear in beat 3 because beat 2 already
        handled the line's work.

    Beat 4: (○∘⟳) closure-recursion           phase i⁰ = +1
        Topology: ○ ↔ • (closure loop; 3.5D = 0D' at the next scale,
        represented within one scale as ○ returning to •).

κ (the nesting operator) is unchanged from v11: diameter bonds •↔Φ and
—↔○ with coupling α, three-scale α and α² for ℂ⁶⁴.

Phase sum verification at ℂ⁴ (the v11 invariant):
    det(U₁) = 1, det(U₂) = 1, det(U₃) = exp(-iπ/6), det(U₄) = 1
    → det(F) = exp(-iπ/6), arg(det(F)) = -π/6  (matches v11)

At ℂ⁶⁴ with F₆₄ = F ⊗ F ⊗ F:
    det(F₆₄) = det(F)^48 = exp(-48iπ/6) = exp(-8iπ) = 1
    → phase sum = 0 (matches v11's "forced closure")

So v12 preserves the v11 phase budget while changing the interior topology.
Any differences in spectrum/fixed-point/weights are genuine signatures of
the beat-native design.

Author: Ashman Roonz & Claude
Date: April 2026
"""

import numpy as np
from scipy.linalg import expm
from typing import Dict, List, Tuple
import time


# ═══════════════════════════════════════════════════════════════
# Framework constants
# ═══════════════════════════════════════════════════════════════

PHI          = (1 + np.sqrt(5)) / 2
T_TRIAD      = 3
P_PUMP       = 4
R_RUNGS      = T_TRIAD**2 - 2           # 7
V_GEN_PLUS   = P_PUMP * T_TRIAD + 1     # 13
SU3          = T_TRIAD**2 - 1           # 8
S_STATES     = (T_TRIAD + 1)**T_TRIAD   # 64
G_GEN        = T_TRIAD * (T_TRIAD + 1)  # 12
A3           = T_TRIAD * (2*T_TRIAD + 1) # 21


def solve_alpha() -> float:
    """Same structural closed form as v11: 1/α = 360/φ² − 2/φ³ + α/(59/3)."""
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    discriminant = b**2 - 4*a*c
    x = (-b + np.sqrt(discriminant)) / (2*a)
    return 1.0 / x


ALPHA = solve_alpha()

# Station indices (ℂ⁴ basis)
BUL, LIN, PHI_IDX, CIR = 0, 1, 2, 3
STATION_NAMES = ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']


# ═══════════════════════════════════════════════════════════════
# Beat-native operators (each with its own generator topology)
# ═══════════════════════════════════════════════════════════════

def _antiherm(G: np.ndarray) -> np.ndarray:
    """Force anti-Hermitian: (G - G†)/2."""
    return (G - np.conj(G.T)) / 2


def build_beat_1() -> np.ndarray:
    """(•∘⊛) localization + convergence.
       Topology: • ↔ Φ (single ray).  Phase: i¹ = +i."""
    theta = np.pi / 2
    phase = 1j
    G = np.zeros((4, 4), dtype=complex)
    c = phase * theta
    G[BUL, PHI_IDX] = c
    G[PHI_IDX, BUL] = -np.conj(c)
    G = _antiherm(G)
    return expm(G)


def build_beat_2() -> np.ndarray:
    """(—∘⎇) extension + branching.
       Topology: — ↔ Φ  AND  — ↔ ○ (Y-fork).  Phase: i² = -1.
       The 1/sqrt(2) factor splits the quarter-turn evenly between
       the two branches, so the total rotation angle is π/2 (as for
       a single-ray beat) but distributed over two output channels."""
    theta = np.pi / 2
    phase = -1 + 0j
    G = np.zeros((4, 4), dtype=complex)
    c = phase * theta / np.sqrt(2)
    G[LIN, PHI_IDX] = c
    G[PHI_IDX, LIN] = -np.conj(c)
    G[LIN, CIR]     = c
    G[CIR, LIN]     = -np.conj(c)
    G = _antiherm(G)
    return expm(G)


def build_beat_3() -> np.ndarray:
    """(Φ∘✹) mediation + emergence.  The PUMP GATE station.
       Topology: Φ ↔ • (ln-side, −) AND Φ ↔ ○ (exp-side, +) + self-drive.
       Phase: i³ = -i.

       Pump-gate structure: eml(x, y) = exp(x) − ln(y).  Φ's convergent
       partner is • (ln-side, minus sign); Φ's emergent partner is ○
       (exp-side, plus sign).  — is absent here: its work was done in
       beat 2, not at the Φ hub.

       Self-drive G[Φ,Φ] = base preserves the substrate-presence term
       (v11's one nonzero trace, the phase-sum source)."""
    theta = np.pi / 2
    phase = -1j
    G = np.zeros((4, 4), dtype=complex)
    base = phase * theta / T_TRIAD

    # Asymmetric hub:
    G[PHI_IDX, BUL] = -base                        # ln-side, minus
    G[BUL, PHI_IDX] = -np.conj(G[PHI_IDX, BUL])
    G[PHI_IDX, CIR] = +base                        # exp-side, plus
    G[CIR, PHI_IDX] = -np.conj(G[PHI_IDX, CIR])

    # Self-drive (substrate presence at Φ; keeps the phase-sum consistent with v11)
    G[PHI_IDX, PHI_IDX] = base

    G = _antiherm(G)
    # Note: anti-hermitianization zeros the self-drive real part; the
    # imaginary part survives because purely-imaginary diagonal IS
    # anti-Hermitian.  base = -iπ/6 is purely imaginary, so the trace
    # is preserved at -iπ/6.
    return expm(G)


def build_beat_4() -> np.ndarray:
    """(○∘⟳) closure + recursion.
       Topology: ○ ↔ • (closure loop).  Phase: i⁰ = +1.
       This is 3.5D = 0D' at the next scale, represented within one
       scale as the boundary (3D) feeding back to the aperture (0D)."""
    theta = np.pi / 2
    phase = 1 + 0j
    G = np.zeros((4, 4), dtype=complex)
    c = phase * theta
    G[CIR, BUL] = c
    G[BUL, CIR] = -np.conj(c)
    G = _antiherm(G)
    return expm(G)


def build_F_single() -> np.ndarray:
    """F = U₄ U₃ U₂ U₁ (beat-native, ℂ⁴)."""
    U1 = build_beat_1()
    U2 = build_beat_2()
    U3 = build_beat_3()
    U4 = build_beat_4()
    return U4 @ U3 @ U2 @ U1


def build_kappa_single() -> np.ndarray:
    """κ (unchanged from v11): diameter bonds •↔Φ and —↔○, strength α."""
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = ALPHA
    kappa[2, 0] = ALPHA
    kappa[1, 3] = ALPHA
    kappa[3, 1] = ALPHA
    return kappa


def build_T_single() -> np.ndarray:
    return build_kappa_single() @ build_F_single()


# ═══════════════════════════════════════════════════════════════
# ℂ⁶⁴ construction (three-scale nesting; κ logic unchanged from v11)
# ═══════════════════════════════════════════════════════════════

def build_F_64() -> np.ndarray:
    """F₆₄ = F ⊗ F ⊗ F  (A3: same operator at every scale)."""
    F = build_F_single()
    return np.kron(np.kron(F, F), F)


def build_kappa_64() -> np.ndarray:
    """κ₆₄: intra-scale diameter + adjacent cross-scale (α) + skip (α²).
       Copied from v11 unchanged."""
    dim = 64
    kappa = np.eye(dim, dtype=complex)
    I4 = np.eye(4, dtype=complex)
    kappa_s = build_kappa_single()

    def idx(i, j, k):
        return i * 16 + j * 4 + k

    kappa_intra_L = np.kron(np.kron(kappa_s, I4), I4)
    kappa_intra_S = np.kron(np.kron(I4, kappa_s), I4)
    kappa_intra_P = np.kron(np.kron(I4, I4), kappa_s)

    for intra in [kappa_intra_L, kappa_intra_S, kappa_intra_P]:
        for a in range(dim):
            for b in range(dim):
                if a != b and abs(intra[a, b]) > 1e-15:
                    kappa[a, b] += intra[a, b]

    cross_kappa = np.zeros((4, 4), dtype=complex)
    cross_kappa[0, 2] = ALPHA
    cross_kappa[2, 0] = ALPHA
    cross_kappa[1, 3] = ALPHA
    cross_kappa[3, 1] = ALPHA

    # Λ-λ adjacent (α)
    for i_L in range(4):
        for j_S in range(4):
            if abs(cross_kappa[j_S, i_L]) < 1e-15:
                continue
            coupling = cross_kappa[j_S, i_L]
            for k_P in range(4):
                a = idx(i_L, j_S, k_P)
                b = idx(j_S, i_L, k_P)
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    # λ-λ' adjacent (α)
    for j_S in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, j_S]) < 1e-15:
                continue
            coupling = cross_kappa[k_P, j_S]
            for i_L in range(4):
                a = idx(i_L, j_S, k_P)
                b = idx(i_L, k_P, j_S)
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    # Λ-λ' skip (α²)
    for i_L in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, i_L]) < 1e-15:
                continue
            coupling = cross_kappa[k_P, i_L] * ALPHA
            for j_S in range(4):
                a = idx(i_L, j_S, k_P)
                b = idx(k_P, j_S, i_L)
                if a != b:
                    kappa[a, b] += coupling
                    kappa[b, a] += coupling

    return kappa


def build_T_64() -> np.ndarray:
    return build_kappa_64() @ build_F_64()


# ═══════════════════════════════════════════════════════════════
# Analysis
# ═══════════════════════════════════════════════════════════════

def fixed_point(T: np.ndarray, steps: int = 50000) -> np.ndarray:
    dim = T.shape[0]
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)
    for _ in range(steps):
        state = T @ state
        n = np.linalg.norm(state)
        if n > 0:
            state = state / n
    return state


def weights(T: np.ndarray, steps: int = 50000) -> np.ndarray:
    fp = fixed_point(T, steps)
    w = np.abs(fp)**2
    return w / np.sum(w)


def eigenspectrum(T: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    evals, evecs = np.linalg.eig(T)
    order = np.argsort(-np.abs(evals))
    return evals[order], evecs[:, order]


def phase_sum(T: np.ndarray) -> float:
    return float(np.sum(np.angle(np.linalg.eigvals(T))))


def scale_decomposition(w: np.ndarray) -> Dict:
    w_r = w.reshape(4, 4, 4)
    return {
        'Lambda_marginal': np.sum(w_r, axis=(1, 2)),
        'lambda_marginal': np.sum(w_r, axis=(0, 2)),
        'lambda_prime_marginal': np.sum(w_r, axis=(0, 1)),
    }


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 72)
    print("  T-OPERATOR v12: BEAT-NATIVE OPERATORS")
    print("=" * 72)
    print(f"  α = {ALPHA:.10f}   (1/α = {1/ALPHA:.6f})")
    print()

    # ─── ℂ⁴ (single scale) ─────────────────────────────────────────────
    print("─" * 72)
    print("  ℂ⁴  (single scale, beat-native F)")
    print("─" * 72)

    U1 = build_beat_1()
    U2 = build_beat_2()
    U3 = build_beat_3()
    U4 = build_beat_4()

    print("  Per-beat determinants (phase contributions):")
    for name, U in [("U₁ (•∘⊛)", U1), ("U₂ (—∘⎇)", U2),
                    ("U₃ (Φ∘✹)", U3), ("U₄ (○∘⟳)", U4)]:
        d = np.linalg.det(U)
        print(f"    det({name}) = {d.real:+.6f} {d.imag:+.6f}j"
              f"   |d|={abs(d):.6f}  arg/π={np.angle(d)/np.pi:+.6f}")

    # Per-beat unitarity check
    print("\n  Per-beat unitarity error (should be ~0):")
    for name, U in [("U₁", U1), ("U₂", U2), ("U₃", U3), ("U₄", U4)]:
        err = np.linalg.norm(U.conj().T @ U - np.eye(4))
        print(f"    ||U†U - I||_F  {name} = {err:.2e}")

    F = build_F_single()
    kappa = build_kappa_single()
    T = kappa @ F

    print(f"\n  F unitarity error: {np.linalg.norm(F.conj().T @ F - np.eye(4)):.2e}")
    print(f"  det(F)  = {np.linalg.det(F):.8f}"
          f"   arg/π = {np.angle(np.linalg.det(F))/np.pi:+.6f}"
          f"   (v11 expected: -1/6 = {-1/6:.6f})")
    print(f"  det(κ) = {np.linalg.det(kappa):.8f}"
          f"   (1-α²)² = {(1-ALPHA**2)**2:.8f}")

    # Spectrum
    sv = np.linalg.svd(T, compute_uv=False)
    evals, _ = eigenspectrum(T)
    ps = phase_sum(T)

    print(f"\n  Singular values of T:")
    print(f"    s = [{', '.join(f'{s:.6f}' for s in sv)}]")
    print(f"    v11 expected: {{(1+α)², (1-α)²}} collapsed to 4 values around 1")
    print(f"    (1+α)² = {(1+ALPHA)**2:.6f}, (1-α)² = {(1-ALPHA)**2:.6f}")

    print(f"\n  Eigenvalues of T (sorted by |λ|):")
    for i, lam in enumerate(evals):
        print(f"    λ_{i}: |λ|={abs(lam):.8f}  arg/π={np.angle(lam)/np.pi:+.6f}"
              f"   ({lam.real:+.6f} {lam.imag:+.6f}j)")

    print(f"\n  Phase sum = {ps:.8f}   = {ps/np.pi:.6f}π"
          f"   (v11 expected: -π/6 = {-np.pi/6:.8f})")

    # Fixed point at ℂ⁴
    w4 = weights(T, steps=20000)
    print(f"\n  ℂ⁴ fixed-point weights (uniform start, 20k steps):")
    for i, (name, wi) in enumerate(zip(STATION_NAMES, w4)):
        bar = '#' * int(wi * 80)
        print(f"    {name}: {wi:.6f}  [{bar}]")

    print(f"\n  Primary diameter  (•+Φ) = {w4[BUL]+w4[PHI_IDX]:.6f}")
    print(f"  Secondary diameter (—+○) = {w4[LIN]+w4[CIR]:.6f}")
    print(f"  Ratio primary/secondary = {(w4[BUL]+w4[PHI_IDX])/(w4[LIN]+w4[CIR]):.6f}")

    # ─── ℂ⁶⁴ (three-scale) ─────────────────────────────────────────────
    print()
    print("─" * 72)
    print("  ℂ⁶⁴  (three-scale nesting; F₆₄ = F ⊗ F ⊗ F)")
    print("─" * 72)

    t0 = time.time()
    F64 = build_F_64()
    print(f"  F₆₄ built in {time.time()-t0:.2f}s  (unitarity err: "
          f"{np.linalg.norm(F64.conj().T @ F64 - np.eye(64)):.2e})")

    t0 = time.time()
    kappa64 = build_kappa_64()
    print(f"  κ₆₄ built in {time.time()-t0:.2f}s  "
          f"(non-zero entries: {np.count_nonzero(np.abs(kappa64) > 1e-15)})")

    T64 = kappa64 @ F64

    # Spectrum
    evals64, _ = eigenspectrum(T64)
    mags = np.abs(evals64)
    det64 = np.linalg.det(T64)

    print(f"\n  Spectrum:")
    print(f"    |λ| max = {np.max(mags):.8f}    (v11: 1.014664)")
    print(f"    |λ| min = {np.min(mags):.8f}    (v11: 0.986761)")
    print(f"    Spectral gap = {mags[0] - mags[1]:.8f}  "
          f"(v11: 0.001758 ≈ α/P = {ALPHA/P_PUMP:.6f})")
    print(f"    det(T₆₄) = {det64:.8f}  |det| = {abs(det64):.8f}  "
          f"arg/π = {np.angle(det64)/np.pi:+.6f}")
    print(f"    (v11: |det| = 0.99156259, arg = 0 exactly)")

    ps64 = phase_sum(T64)
    print(f"    Phase sum = {ps64:.8f}  (v11: 0 exact)")

    # Expanding vs contracting
    expanding = int(np.sum(mags > 1 + 1e-10))
    contracting = int(np.sum(mags < 1 - 1e-10))
    neutral = 64 - expanding - contracting
    from math import comb
    C_R_T = comb(R_RUNGS, T_TRIAD)  # 35
    print(f"\n  Expanding (|λ| > 1): {expanding}  (v11: {C_R_T} = C(R,T))")
    print(f"  Contracting (|λ| < 1): {contracting}  (v11: {S_STATES - C_R_T})")
    print(f"  Neutral (|λ| = 1 within tol): {neutral}")

    # Leading eigenvalue phase
    lead_phase_deg = np.degrees(np.angle(evals64[0]))
    tetra_deg = np.degrees(np.arccos(-1/T_TRIAD))
    print(f"\n  Leading eigenvalue phase: {lead_phase_deg:+.3f}°  "
          f"(v11: 108.96°, tetrahedral = {tetra_deg:.3f}°)")

    # Fixed point and scale decomposition
    print(f"\n  Fixed point (50k steps)...")
    t0 = time.time()
    w64 = weights(T64, steps=50000)
    print(f"  Converged in {time.time()-t0:.1f}s")

    decomp = scale_decomposition(w64)
    print(f"\n  Per-scale station weights:")
    for label, key in [("⊙Λ (whole)", 'Lambda_marginal'),
                        ("⊙λ (self)",  'lambda_marginal'),
                        ("⊙λ' (parts)", 'lambda_prime_marginal')]:
        m = decomp[key]
        primary = m[BUL] + m[PHI_IDX]
        secondary = m[LIN] + m[CIR]
        print(f"    {label}:  "
              f"•={m[BUL]:.4f}  —={m[LIN]:.4f}  Φ={m[PHI_IDX]:.4f}  ○={m[CIR]:.4f}  "
              f"|  •+Φ={primary:.4f}  —+○={secondary:.4f}")

    # Aggregate 69/31 split
    all_primary = 0.0
    all_secondary = 0.0
    for key in ['Lambda_marginal', 'lambda_marginal', 'lambda_prime_marginal']:
        m = decomp[key]
        all_primary += m[BUL] + m[PHI_IDX]
        all_secondary += m[LIN] + m[CIR]
    total = all_primary + all_secondary
    print(f"\n  Aggregate •+Φ fraction = {all_primary/total*100:.2f}%  "
          f"(v11: 68.53%, cosmos DE: 69.11%)")
    print(f"  Aggregate —+○ fraction = {all_secondary/total*100:.2f}%  "
          f"(v11: 31.47%, cosmos M: 30.89%)")

    # A3 test
    w_L = decomp['Lambda_marginal']
    w_S = decomp['lambda_marginal']
    w_P = decomp['lambda_prime_marginal']
    print(f"\n  A3 symmetry (outer vs inner scale distance):")
    print(f"    ||Λ - λ'|| = {np.linalg.norm(w_L - w_P):.6e}  (v11: ~0 to machine precision)")
    print(f"    ||λ - Λ||  = {np.linalg.norm(w_S - w_L):.6e}")
    print(f"    ||λ - λ'|| = {np.linalg.norm(w_S - w_P):.6e}")

    # Top 10 states
    print(f"\n  Top 10 most-weighted states:")
    top = np.argsort(-w64)[:10]
    for r, idx in enumerate(top):
        i_L = idx // 16
        j_S = (idx % 16) // 4
        k_P = idx % 4
        print(f"    #{r+1}: |{STATION_NAMES[i_L]}, {STATION_NAMES[j_S]}, "
              f"{STATION_NAMES[k_P]}⟩  w = {w64[idx]:.6f}")

    # ─── SUMMARY ───────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("  SUMMARY: v12 vs v11 at ℂ⁴ and ℂ⁶⁴")
    print("=" * 72)
    print(f"  Quantity                  v12                        v11 (reference)")
    print(f"  ─────────────────────  ──────────────────────   ──────────────────────")
    print(f"  ℂ⁴ phase sum/π         {ps/np.pi:+.6f}                 -1/6 = -0.16667")
    print(f"  ℂ⁴ |λ| max              {np.max(np.abs(evals)):.6f}                   {(1+ALPHA)**2:.6f}")
    print(f"  ℂ⁴ |λ| min              {np.min(np.abs(evals)):.6f}                   {(1-ALPHA)**2:.6f}")
    print(f"  ℂ⁶⁴ phase sum/π         {ps64/np.pi:+.6f}                 0 (exact)")
    print(f"  ℂ⁶⁴ expanding count     {expanding}                           {C_R_T}")
    print(f"  ℂ⁶⁴ •+Φ aggregate       {all_primary/total*100:.2f}%                      68.53%")
    print(f"  ℂ⁶⁴ leading phase (°)   {lead_phase_deg:+.3f}                  +108.96 (tetra)")
    print(f"  ℂ⁶⁴ A3 outer-inner dist {np.linalg.norm(w_L - w_P):.2e}                   <1e-12")
    print()
    print("  Beat-native F preserves the v11 phase budget exactly")
    print("  (only U₃ has non-zero trace; same as v11).  Differences in")
    print("  spectrum/weights reflect the new interior topology.")
    print("=" * 72)
