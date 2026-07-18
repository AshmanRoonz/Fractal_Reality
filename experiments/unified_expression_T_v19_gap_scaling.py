"""
unified_expression_T_v19_gap_scaling.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. Gap scaling along the canon-to-whole-tone path.

GAP SCALING BETWEEN THE TWO SCALES (v19 of the T-operator series)

v18 found that the whole-tone stroke field opens gaps at the sector
crossings that canon's octave-translation symmetry protects (9.1e-6 ->
5.05e-3, a factor ~550). This experiment closes that finding with a scaling
law: interpolate continuously between the two fields and measure how the
avoided-crossing gap grows.

THE PATH. The two fields differ, at each beat's processual node J_p, by a
mod-4 stroke-count difference delta(J) = (m_wt(J) - m_canon(J)) mod 4,
which is exactly 56-periodic (both counts advance by 0 mod 4 per 8-octave
cell: 32 and 28). The naive linear blend of the raw counts is NOT
cell-periodic (32 vs 28 strokes per cell leaves a stray flux e^{-2 pi i s}
per cell), so the sweep uses the periodic difference field:

    ph_s(J) = i^{m_canon(J)} * exp(i (pi/2) s delta(J)),   delta in {-1,0,1,2}

giving canon at s = 0 and whole-tone at s = 1 (branch choice for delta:
residue 3 mapped to -1; a convention, flagged).

Measurement: at each s, locate the minimum band separation of the 56-band
Bloch spectrum (coarse scan then local refinement in q), i.e. the smallest
avoided-crossing gap. Fit gap(s) ~ s^nu on the small-s decade. A linear law
(nu = 1) is the generic first-order symmetry-breaking expectation; the
experiment measures rather than assumes.

Construction identical to v18 (56-node cell, beat-synchronous, v9 C8 beats).
Interim glyph-integer rule respected.
"""

import numpy as np
from scipy.optimize import minimize_scalar

alpha = 1.0 / 137.035999177
theta = np.pi / 2
T_triad = 3
STRUCT = [0, 2, 4, 6]
PROC = [1, 3, 5, 7]
PHI_s, PHI_p = 4, 5
KAPPA_BONDS = [(0, 4), (2, 6), (1, 5), (3, 7)]
N_OCT_CELL = 8
N_CELL = 56


def m_canon(J):
    k, l = divmod(J, 7)
    return 4 * k + (l + 1) // 2


def m_wholetone(J):
    return (J + 1) // 2


def delta_branch(J):
    d = (m_wholetone(J) - m_canon(J)) % 4
    return d - 4 if d == 3 else d


def cell_entries(s):
    """Per-beat entry lists for the interpolated field at parameter s."""
    beats = [[] for _ in range(4)]
    for k in range(N_OCT_CELL):
        base = 7 * k
        for bi, (st, p) in enumerate(zip(STRUCT, PROC)):
            Jp = base + p
            ph = (1j ** (m_canon(Jp) % 4)) * np.exp(
                1j * (np.pi / 2) * s * delta_branch(Jp))
            c = ph * theta
            ent = [(st, p, c), (p, st, -np.conj(c))]
            if st == PHI_s:
                for o in [0, 2, 6]:
                    h = ph * theta / T_triad
                    ent += [(PHI_s, o, h), (o, PHI_s, -np.conj(h))]
                ent += [(PHI_s, PHI_s, ph * theta / T_triad)]
                for o in [1, 3, 7]:
                    h = ph * theta / T_triad
                    ent += [(PHI_p, o, h), (o, PHI_p, -np.conj(h))]
                ent += [(PHI_p, PHI_p, ph * theta / T_triad)]
            else:
                ent += [(st, PHI_s, c), (PHI_s, st, -np.conj(c)),
                        (p, PHI_p, c), (PHI_p, p, -np.conj(c))]
            beats[bi] += [(base + a, base + b, h) for (a, b, h) in ent]
    return beats


def compile_s(s):
    beats = []
    for ent in cell_entries(s):
        G0 = np.zeros((N_CELL, N_CELL), dtype=complex)
        seam = []
        for (a, b, h) in ent:
            off = b // N_CELL - a // N_CELL
            if off == 0:
                G0[a % N_CELL, b % N_CELL] += h
            else:
                seam.append((a % N_CELL, b % N_CELL, h, off))
        beats.append((G0, seam))
    K0 = np.eye(N_CELL, dtype=complex)
    kseam = []
    for k in range(N_OCT_CELL):
        base = 7 * k
        for (a, b) in KAPPA_BONDS:
            aa, bb = base + a, base + b
            off = bb // N_CELL - aa // N_CELL
            if off == 0:
                K0[aa % N_CELL, bb % N_CELL] += alpha
                K0[bb % N_CELL, aa % N_CELL] += alpha
            else:
                kseam.append((aa % N_CELL, bb % N_CELL, off))
    return beats, K0, kseam


def expm_ah(G):
    w, V = np.linalg.eigh(1j * G)
    return (V * np.exp(-1j * w)) @ np.conj(V.T)


def bloch_T(q, compiled):
    beats, K0, kseam = compiled
    F = np.eye(N_CELL, dtype=complex)
    for (G0, seam) in beats:
        G = G0.copy()
        for (a, b, h, off) in seam:
            G[a, b] += h * np.exp(1j * q * off)
        G = (G - np.conj(G.T)) / 2
        F = expm_ah(G) @ F
    K = K0.copy()
    for (a, b, off) in kseam:
        K[a, b] += alpha * np.exp(1j * q * off)
        K[b, a] += alpha * np.exp(-1j * q * off)
    return K @ F


def min_sep_at(q, compiled):
    ev = np.linalg.eigvals(bloch_T(q, compiled))
    d = np.abs(ev[:, None] - ev[None, :]) + np.eye(N_CELL) * 1e9
    return float(d.min())


def min_gap_global(s, coarse=384):
    compiled = compile_s(s)
    qs = np.linspace(0, 2 * np.pi, coarse, endpoint=False)
    vals = [min_sep_at(q, compiled) for q in qs]
    i0 = int(np.argmin(vals))
    dq = qs[1] - qs[0]
    res = minimize_scalar(lambda q: min_sep_at(q, compiled),
                          bounds=(qs[i0] - dq, qs[i0] + dq),
                          method='bounded', options={'xatol': 1e-10})
    return float(res.fun), float(res.x)


def pair_gap(q, compiled, Pref):
    """Gap between the two eigenvalues whose eigenvectors live in the
    reference crossing plane (projector Pref); pair identity enforced."""
    ev, V = np.linalg.eig(bloch_T(q, compiled))
    V = V / np.linalg.norm(V, axis=0, keepdims=True)
    scores = np.linalg.norm(Pref @ V, axis=0)
    a, b = np.argsort(-scores)[:2]
    return float(np.abs(ev[a] - ev[b]))


def pair_gap_min(s, q_center, Pref, window=0.03, coarse=61):
    compiled = compile_s(s)
    qs = np.linspace(q_center - window, q_center + window, coarse)
    vals = [pair_gap(q, compiled, Pref) for q in qs]
    i0 = int(np.argmin(vals))
    dq = qs[1] - qs[0]
    res = minimize_scalar(lambda q: pair_gap(q, compiled, Pref),
                          bounds=(qs[i0] - dq, qs[i0] + dq),
                          method='bounded', options={'xatol': 1e-11})
    return float(res.fun), float(res.x)


if __name__ == '__main__':
    print("=" * 72)
    print("GAP SCALING ALONG THE CANON -> WHOLE-TONE PATH")
    print("=" * 72)
    print("  Part 1: GLOBAL minimum gap (reported for honesty; confounded:")
    print("  with ~56 bands the minimum hops between different crossings as")
    print("  s changes, so this observable has no single scaling law):\n")
    print(f"  {'s':>6} {'global min gap':>15} {'q_min':>9}")
    for s in [0.0, 0.1, 0.4, 1.0]:
        g, qm = min_gap_global(s)
        print(f"  {s:>6.2f} {g:>15.4e} {qm:>9.4f}")

    print("\n  Part 2: degenerate perturbation theory at ONE crossing.")
    g0, qc = min_gap_global(0.0)
    print(f"  crossing chosen: q_c = {qc:.6f}, s = 0 gap = {g0:.3e} "
          f"(numerically exact)")
    c0 = compile_s(0.0)
    ev, V = np.linalg.eig(bloch_T(qc, c0))
    V = V / np.linalg.norm(V, axis=0, keepdims=True)
    d = np.abs(ev[:, None] - ev[None, :]) + np.eye(N_CELL) * 1e9
    i, j = np.unravel_index(np.argmin(d), d.shape)
    # biorthonormal left vectors for the crossing pair
    Vinv = np.linalg.inv(V)
    li, lj = Vinv[i], Vinv[j]
    ri, rj = V[:, i], V[:, j]
    # dT/ds at s = 0, fixed q_c (central difference; T analytic in s)
    ds = 1e-4
    Tp = (bloch_T(qc, compile_s(ds)) - bloch_T(qc, compile_s(-ds))) / (2 * ds)
    M = np.array([[li @ Tp @ ri, li @ Tp @ rj],
                  [lj @ Tp @ ri, lj @ Tp @ rj]])
    mu = np.linalg.eigvals(M)
    slope = float(np.abs(mu[0] - mu[1]))
    print(f"  predicted linear law from the projected 2x2: "
          f"gap(s) = {slope:.6f} * s + O(s^2)")

    # orthonormal projector onto the crossing plane for pair tracking
    Q, _ = np.linalg.qr(np.column_stack([ri, rj]))
    Pref = Q @ np.conj(Q.T)
    print(f"\n  Part 3: verification with pair-identity tracking "
          f"(projection onto the crossing plane):\n")
    print(f"  {'s':>7} {'pair gap':>12} {'q_c(s)':>9} {'gap/s':>10} "
          f"{'vs slope':>9}")
    rows = []
    for s in [0.002, 0.005, 0.01, 0.02, 0.04]:
        g, qm = pair_gap_min(s, qc, Pref)
        rows.append((s, g))
        print(f"  {s:>7.3f} {g:>12.4e} {qm:>9.4f} {g/s:>10.4f} "
              f"{g/(slope*s):>9.4f}")
    xs = np.log([s for s, _ in rows])
    ys = np.log([g for _, g in rows])
    nu, logc = np.polyfit(xs, ys, 1)
    print(f"\n  scaling fit on the tracked pair: gap ~ C * s^nu with "
          f"nu = {nu:.4f}, C = {np.exp(logc):.4f}")
    print(f"  (perturbation theory predicts nu = 1, C = {slope:.4f})")
