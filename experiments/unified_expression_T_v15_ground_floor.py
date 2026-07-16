"""
unified_expression_T_v15_ground_floor.py

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0
History:
  - 2026-07-16 v1.0: initial. The ground-floor localization study.

THE GROUND FLOOR (v15 of the T-operator series)

v14 found that OPEN staggered chains localize their fixed point on the
lowest octave (n = 4 shares: 0.569, 0.137, 0.080, 0.214), while rings
do not. This experiment asks: boundary artifact, or structure?

Hypothesis: a non-Hermitian skin effect. For non-normal lattice
operators, open boundaries can localize not just the leading mode but
an extensive fraction of ALL eigenmodes at one edge, with the direction
set by a winding (a nonreciprocity). Here the candidate source of
nonreciprocity is the pump itself: the beats are applied in ascending
octave order, and the i-strokes cycle with a fixed chirality
(i^1 -> i^2 -> i^3 -> i^0).

Directions:
  G1  Long-chain profile: per-octave weights of the leading mode,
      exponential decay fit from the bottom edge.
  G2  Skin test: localization of ALL eigenmodes (center of mass and
      participation), chain vs ring.
  G3  Direction controls: descending beat order; conjugated i-phases
      (reversed chirality); both. Does the floor move?
  G4  Decay length vs alpha (multipliers 1, 2, 4, 8).
  G5  Robustness: random perturbation of hub couplings; does the
      floor survive?

Reuses v14 builders via import.
"""

import numpy as np
import unified_expression_T_v14_staggered_chain as v14
from scipy.linalg import expm

alpha0 = v14.alpha
theta = v14.theta
T_triad = v14.T_triad


def build_F_chain_variant(n_oct, order='ascending', chirality=+1):
    """Chain F with controllable beat application order across octaves
    and i-stroke chirality (+1 standard [i, -1, -i, +1]; -1 conjugate)."""
    N = 7 * n_oct + 1
    F = np.eye(N, dtype=complex)
    octaves = range(n_oct) if order == 'ascending' else range(n_oct - 1, -1, -1)
    saved = v14.I_PHASES[:]
    if chirality == -1:
        v14.I_PHASES[:] = [np.conj(p) for p in saved]
    try:
        for k in octaves:
            for B in v14.build_octave_beats(N, 7 * k):
                F = B @ F
    finally:
        v14.I_PHASES[:] = saved
    return F


def leading_profile(n_oct, order='ascending', chirality=+1, kappa=None):
    F = build_F_chain_variant(n_oct, order, chirality)
    K = v14.build_kappa_chain(n_oct) if kappa is None else kappa
    Top = K @ F
    ev, V = np.linalg.eig(Top)
    i = np.argmax(np.abs(ev))
    w = np.abs(V[:, i]) ** 2
    w = w / w.sum()
    ow = np.array([w[7 * k:7 * k + 8].sum() for k in range(n_oct)])
    return Top, ev, V, w, ow


def G1(n_oct=12):
    print("=" * 70)
    print(f"G1: LONG-CHAIN PROFILE AND DECAY FIT (n = {n_oct})")
    print("=" * 70)
    Top, ev, V, w, ow = leading_profile(n_oct)
    print("  per-octave weights of leading mode:")
    for k, x in enumerate(ow):
        bar = '#' * int(round(60 * x / ow.max()))
        print(f"    oct {k:>2}: {x:.6f} {bar}")
    # exponential fit from the bottom, interior region
    ks = np.arange(1, n_oct - 2)
    y = np.log(ow[1:n_oct - 2])
    A = np.vstack([ks, np.ones_like(ks)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    xi = -1.0 / slope if slope < 0 else np.inf
    print(f"\n  interior log-linear fit: slope = {slope:.4f}/octave")
    print(f"  decay length xi = {xi:.3f} octaves" if np.isfinite(xi)
          else "  no decay (slope >= 0): profile not bottom-anchored")
    print(f"  bottom octave share: {ow[0]:.4f}   top octave share: {ow[-1]:.4f}")
    print(f"  bottom/top ratio: {ow[0]/ow[-1]:.3f}")
    return xi


def G2(n_oct=10):
    print("\n" + "=" * 70)
    print(f"G2: SKIN TEST: ALL EIGENMODES, CHAIN vs RING (n = {n_oct})")
    print("=" * 70)
    # chain
    Top, ev, V, w, ow = leading_profile(n_oct)
    N = 7 * n_oct + 1
    coms, prs = [], []
    for r in range(N):
        wr = np.abs(V[:, r]) ** 2
        wr = wr / wr.sum()
        coms.append(float(np.dot(np.arange(N), wr) / (N - 1)))
        prs.append(float(1.0 / np.sum(wr ** 2) / N))
    coms = np.array(coms); prs = np.array(prs)
    lo = np.mean(coms < 1/3); mid = np.mean((coms >= 1/3) & (coms <= 2/3)); hi = np.mean(coms > 2/3)
    print(f"  chain: fraction of modes with COM in bottom/middle/top third: "
          f"{lo:.2f} / {mid:.2f} / {hi:.2f}")
    print(f"  chain: mean COM = {coms.mean():.4f} (0.5 = unbiased), "
          f"mean participation = {prs.mean():.3f}")
    # ring comparison: participation only (COM is circular)
    Fr = v14.build_F_ring(n_oct); Kr = v14.build_kappa_ring(n_oct)
    evr, Vr = np.linalg.eig(Kr @ Fr)
    Nr = 7 * n_oct
    prr = []
    for r in range(Nr):
        wr = np.abs(Vr[:, r]) ** 2
        wr = wr / wr.sum()
        prr.append(float(1.0 / np.sum(wr ** 2) / Nr))
    print(f"  ring : mean participation = {np.mean(prr):.3f}")
    print(f"  skin-effect signature: chain modes pile into one third and")
    print(f"  chain participation collapses relative to the ring.")
    # spectral clouds
    print(f"  chain |lambda| range: [{np.abs(ev).min():.6f}, {np.abs(ev).max():.6f}]")
    print(f"  ring  |lambda| range: [{np.abs(evr).min():.6f}, {np.abs(evr).max():.6f}]")


def G3(n_oct=8):
    print("\n" + "=" * 70)
    print(f"G3: DIRECTION CONTROLS (n = {n_oct})")
    print("=" * 70)
    print(f"  {'variant':>34} {'bottom-3rd share':>16} {'top-3rd share':>14} {'floor':>8}")
    for order in ['ascending', 'descending']:
        for ch in [+1, -1]:
            Top, ev, V, w, ow = leading_profile(n_oct, order, ch)
            n3 = n_oct // 3 or 1
            bshare = ow[:n3].sum(); tshare = ow[-n3:].sum()
            floor = 'bottom' if bshare > tshare else 'top'
            name = f"{order}, chirality {'+' if ch>0 else '-'}"
            print(f"  {name:>34} {bshare:>16.4f} {tshare:>14.4f} {floor:>8}")
    print("  reading: if order flips the floor, the ascent direction sets it;")
    print("  if chirality flips it, the i-cycle's winding sets it;")
    print("  if neither flips it, the kappa edge asymmetry sets it.")




def octave_shares(w, n_oct):
    """Non-overlapping windows: octave k owns nodes 7k..7k+6 (each tonic
    assigned to the octave it opens); final tonic node joins the last."""
    N = 7 * n_oct + 1
    ow = np.array([w[7 * k:7 * k + 7].sum() for k in range(n_oct)])
    ow[-1] += w[N - 1]
    return ow


def G4(n_min=3, n_max=14):
    print("\n" + "=" * 70)
    print("G4: MODE-FAMILY CROSSOVER: FLOOR MODE vs DOME MODE vs TOWER HEIGHT")
    print("=" * 70)
    print(f"  {'n':>3} {'bottom-oct share':>16} {'peak octave':>12} {'profile type':>14}")
    for n in range(n_min, n_max + 1):
        Top, ev, V, w, _ = leading_profile(n)
        ow = octave_shares(w, n)
        peak = int(np.argmax(ow))
        kind = 'floor' if peak == 0 else ('ceiling' if peak == n - 1 else 'dome')
        print(f"  {n:>3} {ow[0]:>16.4f} {peak:>12} {kind:>14}")
    print("\n  top-3 modes at n = 4 and n = 12 (profile peaks and bottom shares):")
    for n in [4, 12]:
        Top, ev, V, w, _ = leading_profile(n)
        idx = np.argsort(-np.abs(ev))
        for r in range(3):
            wr = np.abs(V[:, idx[r]]) ** 2
            wr = wr / wr.sum()
            owr = octave_shares(wr, n)
            print(f"    n={n} rank {r}: |l| = {np.abs(ev[idx[r]]):.6f}  "
                  f"bottom = {owr[0]:.4f}  peak oct = {int(np.argmax(owr))}")


def G5(n_oct=12):
    print("\n" + "=" * 70)
    print(f"G5: THE DESCENDING REGIME (n = {n_oct})")
    print("=" * 70)
    Top, ev, V, w, _ = leading_profile(n_oct, order='descending')
    ow = octave_shares(w, n_oct)
    print("  per-octave shares, descending composition:")
    for k, x in enumerate(ow):
        bar = '#' * int(round(60 * x / ow.max()))
        print(f"    oct {k:>2}: {x:.6f} {bar}")
    y = np.log(np.maximum(ow, 1e-300))
    ks = np.arange(0, min(8, n_oct))
    A = np.vstack([ks, np.ones_like(ks)]).T
    slope, _ = np.linalg.lstsq(A, y[:len(ks)], rcond=None)[0]
    print(f"  bottom-region log slope: {slope:.3f}/octave "
          f"(decay length {abs(1/slope):.2f} octaves)" )
    print(f"  leading |lambda| = {np.abs(ev).max():.6f} "
          f"(ascending at same n: see G1 run)")
    print("  reading: applying the beats top-down dams the 1 at the floor;")
    print("  the canonical ascending order spreads it through the bulk.")




def G6():
    print("\n" + "=" * 70)
    print("G6: CROSSOVER HEIGHT vs ALPHA, AND DOME SCALING")
    print("=" * 70)
    import unified_expression_T_v14_staggered_chain as v14mod
    base = v14mod.alpha
    print(f"  {'alpha mult':>10} {'crossover n*':>13}")
    for mult in [0.5, 1, 2, 4, 8]:
        v14mod.alpha = base * mult
        nstar = None
        for n in range(3, 10):
            Top, ev, V, w, _ = leading_profile(n)
            ow = octave_shares(w, n)
            if int(np.argmax(ow)) != 0:
                nstar = n
                break
        print(f"  {mult:>10.1f} {str(nstar):>13}")
    v14mod.alpha = base
    print("\n  dome scaling (ascending, standard alpha): max octave share vs n")
    print(f"  {'n':>3} {'max share':>10} {'n * max share':>14}")
    for n in range(6, 15):
        Top, ev, V, w, _ = leading_profile(n)
        ow = octave_shares(w, n)
        print(f"  {n:>3} {ow.max():>10.4f} {n * ow.max():>14.3f}")
    print("  box-ground-state scaling predicts n * max share -> constant (= 2")
    print("  for a pure sin^2 envelope); no privileged scale in the limit.")


if __name__ == '__main__':
    G1(12)
    G2(10)
    G3(8)
    G4(3, 14)
    G5(12)
    G6()
