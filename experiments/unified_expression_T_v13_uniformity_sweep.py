"""
T-operator v13: Uniformity Sweep
=================================

v11 (uniform hub-coupling) hits the cosmological 69/31 split and the
tetrahedral leading-eigenvalue phase (109°) at ℂ⁶⁴, but its ℂ⁴ singular
values double-count α (they fit (1±α)² rather than (1±α)).

v12 (beat-native generators) fixes the singular-value double-count
cleanly (fit error ~1e-16 to (1±α)) but loses the 69/31 match (reads
~77/23) and the tetrahedral leading phase (reads ~74°).

v13 interpolates between them with a single uniformity parameter
μ ∈ [0, 1]:

    G_k(μ) = (1 − μ) · G_v12_k  +  μ · G_v11_k       (per-beat generator)
    U_k(μ) = expm( antiherm( G_k(μ) ) )
    F(μ)   = U_4(μ) U_3(μ) U_2(μ) U_1(μ)

κ is unchanged (diameter bonds, strength α).  At μ = 0 we reproduce v12
exactly; at μ = 1 we reproduce v11 exactly.

Phase budget invariance along the dial: only beat 3 contributes to trace,
and both v11 and v12 put G[Φ,Φ] = −iπ/6 on Φ.  The interpolation is
linear in the generator, so trace is preserved for every μ.  Therefore
det(U₃(μ)) = exp(−iπ/6) and det(F₆₄(μ)) = 1 for all μ.

What we sweep:
  · ℂ⁴ singular values (should deviate from (1±α) as μ rises)
  · ℂ⁴ |λ_max|, |λ_min|
  · ℂ⁶⁴ aggregate (•+Φ) primary-diameter fraction
  · ℂ⁶⁴ leading eigenvalue phase (degrees)
  · ℂ⁶⁴ expanding vs contracting count
  · ℂ⁶⁴ phase sum (invariance check)
  · ℂ⁶⁴ A3 symmetry (outer vs inner scale distance)

Key questions:
  1. Does primary split move monotonically from 77% → 68.5% as μ: 0→1?
  2. Is there a unique μ* at which split = 69.11% (cosmos DE) or
     leading phase = 109.47° (tetrahedral)?  If yes, those two μ*
     should agree (or we have two inconsistent fitting dials).
  3. Does the expanding count transition through 35 = C(R,T) at the
     same μ, or at a different one?

Author: Ashman Roonz & Claude
Date: April 2026
"""

import numpy as np
from scipy.linalg import expm
from typing import Dict, List, Tuple
from math import comb
import time


# ═══════════════════════════════════════════════════════════════
# Framework constants (identical to v11/v12)
# ═══════════════════════════════════════════════════════════════

PHI          = (1 + np.sqrt(5)) / 2
T_TRIAD      = 3
P_PUMP       = 4
R_RUNGS      = T_TRIAD**2 - 2
V_GEN_PLUS   = P_PUMP * T_TRIAD + 1
SU3          = T_TRIAD**2 - 1
S_STATES     = (T_TRIAD + 1)**T_TRIAD
G_GEN        = T_TRIAD * (T_TRIAD + 1)
A3           = T_TRIAD * (2*T_TRIAD + 1)
C_R_T        = comb(R_RUNGS, T_TRIAD)  # 35


def solve_alpha() -> float:
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    return 1.0 / ((-b + np.sqrt(b**2 - 4*a*c)) / (2*a))


ALPHA = solve_alpha()

BUL, LIN, PHI_IDX, CIR = 0, 1, 2, 3
STATION_NAMES = ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']


# ═══════════════════════════════════════════════════════════════
# Per-beat generator definitions (pre-antiherm)
# ═══════════════════════════════════════════════════════════════

def _antiherm(G: np.ndarray) -> np.ndarray:
    return (G - np.conj(G.T)) / 2


def build_G_v11(k: int) -> np.ndarray:
    """v11-style generator: active station couples to Φ hub.  For beats
    whose active station is NOT Φ, this is a single-ray active ↔ Φ coupling.
    For beat 3 (active = Φ), Φ couples uniformly to all three other stations
    with strength i_phase·θ/T, plus a self-drive of the same strength.  This
    matches build_F_single() in unified_expression_T_v11_C64.py exactly.

    Beat 1 (•∘⊛, +i):  G[•,Φ] = iπ/2                            (single ray)
    Beat 2 (—∘⎇, -1):  G[—,Φ] = -π/2                            (single ray)
    Beat 3 (Φ∘✹, -i):  G[Φ, •] = G[Φ, —] = G[Φ, ○] = -iπ/6;
                       G[Φ, Φ] = -iπ/6                          (hub + self-drive)
    Beat 4 (○∘⟳, +1):  G[○,Φ] = +π/2                            (single ray)
    """
    theta = np.pi / 2
    G = np.zeros((4, 4), dtype=complex)
    if k == 1:
        c = 1j * theta
        G[BUL, PHI_IDX] = c
        G[PHI_IDX, BUL] = -np.conj(c)
    elif k == 2:
        c = -1.0 * theta
        G[LIN, PHI_IDX] = c
        G[PHI_IDX, LIN] = -np.conj(c)
    elif k == 3:
        coupling = -1j * theta / T_TRIAD                # -iπ/6
        for other in [BUL, LIN, CIR]:
            G[PHI_IDX, other] = coupling
            G[other, PHI_IDX] = -np.conj(coupling)
        G[PHI_IDX, PHI_IDX] = coupling                  # self-drive (trace source)
    elif k == 4:
        c = 1.0 * theta
        G[CIR, PHI_IDX] = c
        G[PHI_IDX, CIR] = -np.conj(c)
    return G


def build_G_v12(k: int) -> np.ndarray:
    """v12 beat-native generator.

    Beat 1 (•∘⊛):  single ray • ↔ Φ (same as v11)
    Beat 2 (—∘⎇):  Y-fork — ↔ Φ  AND  — ↔ ○ (1/√2 split)
    Beat 3 (Φ∘✹):  asymmetric hub Φ ↔ • (ln, −) + Φ ↔ ○ (exp, +) + self-drive
    Beat 4 (○∘⟳):  closure loop ○ ↔ • (3.5D = 0D')
    """
    theta = np.pi / 2
    G = np.zeros((4, 4), dtype=complex)
    if k == 1:
        c = 1j * theta
        G[BUL, PHI_IDX] = c
        G[PHI_IDX, BUL] = -np.conj(c)
    elif k == 2:
        c = -1.0 * theta / np.sqrt(2)
        G[LIN, PHI_IDX] = c
        G[PHI_IDX, LIN] = -np.conj(c)
        G[LIN, CIR]     = c
        G[CIR, LIN]     = -np.conj(c)
    elif k == 3:
        base = -1j * theta / T_TRIAD                     # -iπ/6
        G[PHI_IDX, BUL] = -base
        G[BUL, PHI_IDX] = -np.conj(G[PHI_IDX, BUL])
        G[PHI_IDX, CIR] = +base
        G[CIR, PHI_IDX] = -np.conj(G[PHI_IDX, CIR])
        G[PHI_IDX, PHI_IDX] = base                       # trace source (matches v11)
    elif k == 4:
        c = 1.0 * theta
        G[CIR, BUL] = c
        G[BUL, CIR] = -np.conj(c)
    return G


def build_U_mixed(k: int, mu: float) -> np.ndarray:
    """U_k(μ) = expm( antiherm( (1-μ) G_v12 + μ G_v11 ) )."""
    G = (1.0 - mu) * build_G_v12(k) + mu * build_G_v11(k)
    return expm(_antiherm(G))


def build_F_single(mu: float) -> np.ndarray:
    U1 = build_U_mixed(1, mu)
    U2 = build_U_mixed(2, mu)
    U3 = build_U_mixed(3, mu)
    U4 = build_U_mixed(4, mu)
    return U4 @ U3 @ U2 @ U1


# ═══════════════════════════════════════════════════════════════
# κ (unchanged from v11/v12) and ℂ⁶⁴ construction
# ═══════════════════════════════════════════════════════════════

def build_kappa_single() -> np.ndarray:
    k = np.eye(4, dtype=complex)
    k[0, 2] = ALPHA; k[2, 0] = ALPHA
    k[1, 3] = ALPHA; k[3, 1] = ALPHA
    return k


def build_kappa_64() -> np.ndarray:
    dim = 64
    kappa = np.eye(dim, dtype=complex)
    I4 = np.eye(4, dtype=complex)
    kappa_s = build_kappa_single()

    def idx(i, j, k):
        return i * 16 + j * 4 + k

    for intra in [np.kron(np.kron(kappa_s, I4), I4),
                  np.kron(np.kron(I4, kappa_s), I4),
                  np.kron(np.kron(I4, I4), kappa_s)]:
        for a in range(dim):
            for b in range(dim):
                if a != b and abs(intra[a, b]) > 1e-15:
                    kappa[a, b] += intra[a, b]

    cross_kappa = np.zeros((4, 4), dtype=complex)
    cross_kappa[0, 2] = ALPHA; cross_kappa[2, 0] = ALPHA
    cross_kappa[1, 3] = ALPHA; cross_kappa[3, 1] = ALPHA

    for i_L in range(4):
        for j_S in range(4):
            if abs(cross_kappa[j_S, i_L]) < 1e-15: continue
            coupling = cross_kappa[j_S, i_L]
            for k_P in range(4):
                a, b = idx(i_L, j_S, k_P), idx(j_S, i_L, k_P)
                if a != b:
                    kappa[a, b] += coupling; kappa[b, a] += coupling

    for j_S in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, j_S]) < 1e-15: continue
            coupling = cross_kappa[k_P, j_S]
            for i_L in range(4):
                a, b = idx(i_L, j_S, k_P), idx(i_L, k_P, j_S)
                if a != b:
                    kappa[a, b] += coupling; kappa[b, a] += coupling

    for i_L in range(4):
        for k_P in range(4):
            if abs(cross_kappa[k_P, i_L]) < 1e-15: continue
            coupling = cross_kappa[k_P, i_L] * ALPHA
            for j_S in range(4):
                a, b = idx(i_L, j_S, k_P), idx(k_P, j_S, i_L)
                if a != b:
                    kappa[a, b] += coupling; kappa[b, a] += coupling

    return kappa


KAPPA_64 = build_kappa_64()   # reuse across μ-sweep


def build_F_64(mu: float) -> np.ndarray:
    F = build_F_single(mu)
    return np.kron(np.kron(F, F), F)


# ═══════════════════════════════════════════════════════════════
# Analysis helpers
# ═══════════════════════════════════════════════════════════════

def fixed_point(T: np.ndarray, steps: int = 30000, seed: int = 0) -> np.ndarray:
    dim = T.shape[0]
    rng = np.random.default_rng(seed)
    state = rng.standard_normal(dim) + 1j * rng.standard_normal(dim)
    state = state / np.linalg.norm(state)
    for _ in range(steps):
        state = T @ state
        n = np.linalg.norm(state)
        if n > 0:
            state = state / n
    return state


def weights(T: np.ndarray, steps: int = 30000, seed: int = 0) -> np.ndarray:
    fp = fixed_point(T, steps, seed)
    w = np.abs(fp)**2
    return w / np.sum(w)


def measure(mu: float, steps_fp: int = 30000) -> Dict:
    """Single-μ measurement bundle."""
    F = build_F_single(mu)
    T = build_kappa_single() @ F
    F64 = build_F_64(mu)
    T64 = KAPPA_64 @ F64

    sv = np.linalg.svd(T, compute_uv=False)
    evals4 = np.linalg.eigvals(T)
    evals64 = np.linalg.eigvals(T64)
    order = np.argsort(-np.abs(evals64))
    evals64 = evals64[order]

    ps4  = float(np.sum(np.angle(evals4)))
    ps64 = float(np.sum(np.angle(evals64)))

    mags = np.abs(evals64)
    expanding   = int(np.sum(mags > 1 + 1e-10))
    contracting = int(np.sum(mags < 1 - 1e-10))

    lead_phase = float(np.degrees(np.angle(evals64[0])))

    w = weights(T64, steps=steps_fp, seed=0)
    w_r = w.reshape(4, 4, 4)
    marg_L = np.sum(w_r, axis=(1, 2))
    marg_S = np.sum(w_r, axis=(0, 2))
    marg_P = np.sum(w_r, axis=(0, 1))

    primary   = (marg_L[BUL]+marg_L[PHI_IDX] + marg_S[BUL]+marg_S[PHI_IDX]
                 + marg_P[BUL]+marg_P[PHI_IDX]) / 3.0
    secondary = (marg_L[LIN]+marg_L[CIR] + marg_S[LIN]+marg_S[CIR]
                 + marg_P[LIN]+marg_P[CIR]) / 3.0

    A3_outin = float(np.linalg.norm(marg_L - marg_P))

    return {
        'mu': mu,
        'sv_min': float(np.min(sv)),
        'sv_max': float(np.max(sv)),
        'sv_fit_1pm_alpha': float(
            abs(np.max(sv) - (1 + ALPHA)) + abs(np.min(sv) - (1 - ALPHA))),
        'sv_fit_1pm_alpha_sq': float(
            abs(np.max(sv) - (1 + ALPHA)**2) + abs(np.min(sv) - (1 - ALPHA)**2)),
        '|lam_max|': float(np.max(np.abs(evals4))),
        '|lam_min|': float(np.min(np.abs(evals4))),
        'ps4_over_pi': ps4 / np.pi,
        'ps64_over_pi_mod2': float(((ps64 + np.pi) % (2*np.pi)) - np.pi) / np.pi,
        'expanding': expanding,
        'contracting': contracting,
        'lead_phase_deg': lead_phase,
        'primary_pct': primary * 100,
        'secondary_pct': secondary * 100,
        'A3_outer_inner_dist': A3_outin,
    }


# ═══════════════════════════════════════════════════════════════
# Main: sweep μ from 0 to 1
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 84)
    print("  T-OPERATOR v13: UNIFORMITY SWEEP  (v12 → v11)")
    print("=" * 84)
    print(f"  α = {ALPHA:.10f}   1/α = {1/ALPHA:.6f}")
    print(f"  cosmological target: •+Φ = 69.11%  (DE/total)")
    print(f"  tetrahedral target : arccos(-1/T) = {np.degrees(np.arccos(-1/T_TRIAD)):.4f}°")
    print(f"  C(R,T) target      : expanding = {C_R_T}")
    print()

    mus = np.linspace(0.0, 1.0, 11)
    results: List[Dict] = []

    print(f"  Sweeping μ ∈ {{{', '.join(f'{m:.2f}' for m in mus)}}}  "
          f"(fixed-point: 30k steps each)")
    print()

    hdr = (f"  {'μ':>5} | {'|λ|max':>9} {'|λ|min':>9} "
           f"| {'ps64/π':>8} | {'exp':>4} {'con':>4} "
           f"| {'lead°':>8} | {'•+Φ %':>7} | {'A3 dist':>9}")
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))

    t0 = time.time()
    for mu in mus:
        r = measure(float(mu))
        results.append(r)
        print(f"  {r['mu']:>5.2f} | {r['|lam_max|']:>9.6f} {r['|lam_min|']:>9.6f} "
              f"| {r['ps64_over_pi_mod2']:>+8.1e} "
              f"| {r['expanding']:>4} {r['contracting']:>4} "
              f"| {r['lead_phase_deg']:>+8.2f} "
              f"| {r['primary_pct']:>7.2f} "
              f"| {r['A3_outer_inner_dist']:>9.2e}")
    print(f"\n  Sweep time: {time.time()-t0:.1f}s")

    # Locate μ where primary ≈ 69.11 and where lead_phase ≈ 109.47
    TARGET_PRIMARY = 69.11
    TARGET_LEAD    = np.degrees(np.arccos(-1/T_TRIAD))  # 109.4712

    # Linear interpolation between the two μ values that bracket each target
    def bracket_mu(key, target):
        for i in range(len(results) - 1):
            v1, v2 = results[i][key], results[i+1][key]
            if (v1 - target) * (v2 - target) <= 0:
                m1, m2 = results[i]['mu'], results[i+1]['mu']
                if v2 == v1:
                    return m1
                frac = (target - v1) / (v2 - v1)
                return m1 + frac * (m2 - m1)
        return None

    mu_star_split = bracket_mu('primary_pct', TARGET_PRIMARY)
    mu_star_lead  = bracket_mu('lead_phase_deg', TARGET_LEAD)
    mu_star_exp   = bracket_mu('expanding', C_R_T)

    print()
    print("  μ* estimates (linear bracket interpolation):")
    print(f"    μ* at •+Φ = 69.11%        : "
          f"{mu_star_split if mu_star_split is None else f'{mu_star_split:.4f}'}")
    print(f"    μ* at lead phase = 109.47°: "
          f"{mu_star_lead  if mu_star_lead  is None else f'{mu_star_lead:.4f}'}")
    print(f"    μ* at expanding = 35      : "
          f"{mu_star_exp   if mu_star_exp   is None else f'{mu_star_exp:.4f}'}")

    if mu_star_split is not None and mu_star_lead is not None:
        agree = abs(mu_star_split - mu_star_lead)
        print(f"\n    |μ*_split − μ*_lead| = {agree:.4f}")
        print(f"    Interpretation:")
        if agree < 0.03:
            print(f"      DIALS AGREE.  Single μ* ≈ {(mu_star_split+mu_star_lead)/2:.3f} "
                  f"satisfies both.")
        elif agree < 0.15:
            print(f"      Partial agreement.  Two dials within ~{agree*100:.0f}%. "
                  f"Framework may accommodate with residual correction.")
        else:
            print(f"      DIALS DISAGREE by ~{agree*100:.0f}%.  Single-parameter blend "
                  f"cannot hit both targets; need richer interpolation or one target "
                  f"is wrong.")

    print()
    print("=" * 84)
        agree = abs(mu_star_split - mu_star_lead)
        print(f"\n    |mu*_split - mu*_lead| = {agree:.4f}")
        print(f"    Interpretation:")
        if agree < 0.03:
            print(f"      DIALS AGREE.  Single mu* approx {(mu_star_split+mu_star_lead)/2:.3f} "
                  f"satisfies both.")
        elif agree < 0.15:
            print(f"      Partial agreement.  Two dials within ~{agree*100:.0f}%. "
                  f"Framework may accommodate with residual correction.")
        else:
            print(f"      DIALS DISAGREE by ~{agree*100:.0f}%.  Single-parameter blend "
                  f"cannot hit both targets; need richer interpolation or one target "
                  f"is wrong.")

    print()
    print("=" * 84)
