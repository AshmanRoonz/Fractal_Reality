"""
unified_expression_T_v14_staggered_chain.py

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0
History:
  - 2026-07-16 v1.0: initial. The staggered-octave chain operator.

THE STAGGERED-OCTAVE CHAIN (v14 of the T-operator series)

Prior multi-scale work (v11, C64) modeled three scales as a tensor product
F4 (x) F4 (x) F4: 24 stations, no shared stations. The staggered octave
(framework section 27.7t; docs/octave_wrap_lemma.html section 8) says
adjacent octaves share exactly ONE station, the tonic (3.5D = 0D').
This experiment builds that geometry directly: n octaves on the
continuation lattice, 7n + 1 nodes, each octave an 8-station block
(v9's C8 construction) sharing its recursion node with the next
octave's aperture node.

Directions:
  E1  Fixed point and weight structure (structural/processual split vs 69/31)
  E2  Spectral scaling with octave count n = 1..8
  E3  Parity double-cover observable hunt (period-2 structure across octaves)
  E4  Single-period collapse demo (second return coupling at 4D offset)
  E5  Attractor uniqueness and A3 (interior octaves identical)

Station convention per octave (local index l = 0..7, half-step lattice):
  l: 0     1    2    3    4    5    6    7
     tonic ⊛    —    ⎇    Φ    ✹    ○    tonic'
  Node j of the chain sits at continuation coordinate j/2.
  Node 7k is shared: recursion (i^0) of octave k-1 AND aperture of octave k.
Glyph positions follow the legacy v-series basis; under the corrected
ladder read station labels as coordinates (interim glyph-integer rule).
"""

import numpy as np
from scipy.linalg import expm

alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = 4
R = 7

STATIONS = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']
theta = np.pi / 2
I_PHASES = [1j, -1 + 0j, -1j, 1 + 0j]


def n_nodes(n_oct):
    return 7 * n_oct + 1


def build_octave_beats(N, base):
    """The four C8 beats of one octave, embedded at node offset `base`
    in an N-node chain. Mirrors v9's build_beats_8D exactly."""
    beats = []
    struct_idx = [0, 2, 4, 6]
    proc_idx = [1, 3, 5, 7]
    PHI_s, PHI_p = 4, 5
    for (s, p, ph) in zip(struct_idx, proc_idx, I_PHASES):
        G = np.zeros((N, N), dtype=complex)
        S, Pn = base + s, base + p
        c = ph * theta
        G[S, Pn] = c
        G[Pn, S] = -np.conj(c)
        if s == PHI_s:
            for o in [0, 2, 6]:
                h = ph * theta / T_triad
                G[base + PHI_s, base + o] = h
                G[base + o, base + PHI_s] = -np.conj(h)
            G[base + PHI_s, base + PHI_s] = ph * theta / T_triad
            for o in [1, 3, 7]:
                h = ph * theta / T_triad
                G[base + PHI_p, base + o] = h
                G[base + o, base + PHI_p] = -np.conj(h)
            G[base + PHI_p, base + PHI_p] = ph * theta / T_triad
        else:
            G[S, base + PHI_s] = c
            G[base + PHI_s, S] = -np.conj(c)
            G[Pn, base + PHI_p] = c
            G[base + PHI_p, Pn] = -np.conj(c)
        G = (G - np.conj(G.T)) / 2
        beats.append(expm(G))
    return beats


def build_F_chain(n_oct):
    """Ascending composition: octave 0's four beats act first."""
    N = n_nodes(n_oct)
    F = np.eye(N, dtype=complex)
    for k in range(n_oct):
        for B in build_octave_beats(N, 7 * k):
            F = B @ F
    return F


def build_kappa_chain(n_oct, g_second_period=0.0, g_extra_tonic=0.0):
    """Per-octave diameter couplings (v9's kappa_8D per block).
    Optional: g_second_period bonds nodes 8 half-steps apart (a 4D offset,
    the forbidden second period); g_extra_tonic bonds nodes 7 half-steps
    apart (commensurate with the wrap; control condition)."""
    N = n_nodes(n_oct)
    kappa = np.eye(N, dtype=complex)
    for k in range(n_oct):
        b = 7 * k
        for (a, c) in [(0, 4), (2, 6), (1, 5), (3, 7)]:
            kappa[b + a, b + c] += alpha
            kappa[b + c, b + a] += alpha
    if g_second_period:
        for j in range(N - 8):
            kappa[j, j + 8] += g_second_period
            kappa[j + 8, j] += g_second_period
    if g_extra_tonic:
        for j in range(N - 7):
            kappa[j, j + 7] += g_extra_tonic
            kappa[j + 7, j] += g_extra_tonic
    return kappa


def leading_fixed_point(Top):
    ev, V = np.linalg.eig(Top)
    i = np.argmax(np.abs(ev))
    psi = V[:, i]
    w = np.abs(psi) ** 2
    return ev, w / w.sum(), psi


def split_weights(w, n_oct):
    """Structural vs processual split; tonic nodes are their own
    double-natured class. Per-residue and per-octave sums."""
    N = n_nodes(n_oct)
    w_struct = w_proc = w_tonic = 0.0
    residue = np.zeros(7)
    for j in range(N):
        l = j % 7
        residue[l] += w[j]
        if l == 0:
            w_tonic += w[j]
        elif l in (2, 4, 6):
            w_struct += w[j]
        else:
            w_proc += w[j]
    oct_w = np.array([w[7 * k:7 * k + 8].sum() for k in range(n_oct)])
    return w_struct, w_proc, w_tonic, residue, oct_w


def E1(n_oct=4):
    print("=" * 70)
    print(f"E1: FIXED POINT OF THE STAGGERED CHAIN (n = {n_oct} octaves, "
          f"{n_nodes(n_oct)} nodes)")
    print("=" * 70)
    F = build_F_chain(n_oct)
    print(f"  F unitary: {np.allclose(F @ np.conj(F.T), np.eye(len(F)), atol=1e-9)}")
    K = build_kappa_chain(n_oct)
    Top = K @ F
    ev, w, psi = leading_fixed_point(Top)
    evs = sorted(np.abs(ev), reverse=True)
    print(f"  leading |lambda| = {evs[0]:.8f}   (|lambda|-1)/alpha = {(evs[0]-1)/alpha:.4f}")
    print(f"  spectral gap = {evs[0]-evs[1]:.3e}   gap/alpha = {(evs[0]-evs[1])/alpha:.4f}")
    ws, wp, wt, res, ow = split_weights(w, n_oct)
    tot_sp = ws + wp
    print(f"\n  structural residues (—, Φ, ○):  {ws:.4f}")
    print(f"  processual residues (⊛, ⎇, ✹):  {wp:.4f}")
    print(f"  tonic class (• ≡ ⟳):             {wt:.4f}")
    print(f"  split excluding tonic: {100*ws/tot_sp:.2f} / {100*wp/tot_sp:.2f}")
    h = ws + wt / 2; q = wp + wt / 2
    print(f"  split, tonic half-half: {100*h:.2f} / {100*q:.2f}   (cosmos 69.11/30.89; C8 68.7/31.3)")
    lab = ['tonic', '⊛', '—', '⎇', 'Φ', '✹', '○']
    print("\n  residue-class weights: " + "  ".join(f"{l}={r:.4f}" for l, r in zip(lab, res)))
    print("  per-octave weights:    " + "  ".join(f"oct{k}={x:.4f}" for k, x in enumerate(ow)))


def E2(n_max=8):
    print("\n" + "=" * 70)
    print("E2: SPECTRAL SCALING WITH OCTAVE COUNT")
    print("=" * 70)
    print(f"  {'n':>2} {'nodes':>6} {'|l1|':>12} {'(|l1|-1)/a':>11} {'gap':>12} {'gap/a':>9} {'mix~1/gap':>10}")
    for n in range(1, n_max + 1):
        Top = build_kappa_chain(n) @ build_F_chain(n)
        m = sorted(np.abs(np.linalg.eigvals(Top)), reverse=True)
        gap = m[0] - m[1]
        print(f"  {n:>2} {n_nodes(n):>6} {m[0]:>12.8f} {(m[0]-1)/alpha:>11.4f} "
              f"{gap:>12.3e} {gap/alpha:>9.4f} {1/gap:>10.1f}")


def E3(n_oct=8):
    print("\n" + "=" * 70)
    print(f"E3: PARITY DOUBLE-COVER HUNT (n = {n_oct}, interior octaves)")
    print("=" * 70)
    Top = build_kappa_chain(n_oct) @ build_F_chain(n_oct)
    ev, w, psi = leading_fixed_point(Top)
    fr = []
    for k in range(1, n_oct - 1):
        b = 7 * k
        s = sum(w[b + l] for l in (2, 4, 6))
        p = sum(w[b + l] for l in (1, 3, 5))
        fr.append(s / (s + p))
    fr = np.array(fr)
    alt = np.array([(-1) ** k for k in range(len(fr))])
    witness = float(np.dot(fr - fr.mean(), alt) / len(fr))
    print(f"  interior per-octave structural fractions: {[f'{x:.6f}' for x in fr]}")
    print(f"  fixed-point alternation witness: {witness:.3e}  (|w|/mean = {abs(witness)/fr.mean():.3e})")
    idx = np.argsort(-np.abs(ev))
    _, V = np.linalg.eig(Top)
    print("  subleading eigenvectors: period-2 octave component (1 = pure alternation):")
    for r in range(1, min(13, len(idx))):
        v = V[:, idx[r]]
        oc = np.array([np.abs(v[7 * k:7 * k + 8]).sum() for k in range(n_oct)])
        c2 = abs(np.dot(oc, [(-1) ** k for k in range(n_oct)])) / oc.sum()
        flag = '  <-- parity-structured' if c2 > 0.5 else ''
        print(f"    rank {r:>2}: {c2:.4f}{flag}")


def E4(n_oct=5):
    print("\n" + "=" * 70)
    print("E4: SINGLE-PERIOD COLLAPSE DEMO (second return coupling at 4D offset)")
    print("=" * 70)
    print("  metric: variance of residue-class weights, normalized to g = 0")
    print("  (station distinguishability; -> 0 means the ladder flattens)")
    rows = []
    for gm in [0, 0.25, 0.5, 1, 2, 4, 8, 16]:
        g = gm * alpha
        out = []
        for kind in ['second', 'tonic']:
            kw = dict(g_second_period=g) if kind == 'second' else dict(g_extra_tonic=g)
            Top = build_kappa_chain(n_oct, **kw) @ build_F_chain(n_oct)
            _, w, _ = leading_fixed_point(Top)
            _, _, _, res, _ = split_weights(w, n_oct)
            resn = res / res.sum()
            out.append(float(np.var(resn)))
        rows.append((gm, out[0], out[1]))
    base = rows[0][1]
    print(f"\n  {'g/alpha':>8} {'4D offset (forbidden)':>24} {'7-half-step control':>24}")
    for gm, a4, t7 in rows:
        print(f"  {gm:>8.2f} {a4/base:>24.4f} {t7/base:>24.4f}")
    print("\n  single-period lemma prediction: left column collapses, control does not.")


def E5(n_oct=4, n_ic=60):
    print("\n" + "=" * 70)
    print(f"E5: ATTRACTOR UNIQUENESS + A3 (n = {n_oct}, {n_ic} random ICs)")
    print("=" * 70)
    Top = build_kappa_chain(n_oct) @ build_F_chain(n_oct)
    ev, wref, _ = leading_fixed_point(Top)
    rng = np.random.default_rng(7)
    N = n_nodes(n_oct)
    worst = 0.0
    for _ in range(n_ic):
        psi = rng.normal(size=N) + 1j * rng.normal(size=N)
        psi /= np.linalg.norm(psi)
        for _ in range(15000):
            psi = Top @ psi
            psi /= np.linalg.norm(psi)
        w = np.abs(psi) ** 2
        worst = max(worst, float(np.max(np.abs(w - wref))))
    print(f"  max deviation from eig fixed point across ICs: {worst:.3e}")
    _, _, _, _, ow = split_weights(wref, n_oct)
    ow = ow / ow.sum()
    print(f"  per-octave weight shares: {[f'{x:.5f}' for x in ow]}")
    print("  A3 expectation: interior octaves identical, edge octaves differ.")




# ============================================================
# Ring topology: n octaves closed tonic-to-tonic (7n nodes).
# Removes chain edges; translation-invariant up to cyclic
# reordering of the beat product (spectrum exactly invariant).
# ============================================================

def build_F_ring(n_oct):
    N = 7 * n_oct
    F = np.eye(N, dtype=complex)
    for k in range(n_oct):
        beats = build_octave_beats_ring(N, 7 * k)
        for B in beats:
            F = B @ F
    return F


def build_octave_beats_ring(N, base):
    beats = []
    struct_idx = [0, 2, 4, 6]
    proc_idx = [1, 3, 5, 7]
    PHI_s, PHI_p = 4, 5
    def nd(l):
        return (base + l) % N
    for (s, p, ph) in zip(struct_idx, proc_idx, I_PHASES):
        G = np.zeros((N, N), dtype=complex)
        c = ph * theta
        G[nd(s), nd(p)] += c
        G[nd(p), nd(s)] += -np.conj(c)
        if s == PHI_s:
            for o in [0, 2, 6]:
                h = ph * theta / T_triad
                G[nd(PHI_s), nd(o)] += h
                G[nd(o), nd(PHI_s)] += -np.conj(h)
            G[nd(PHI_s), nd(PHI_s)] += ph * theta / T_triad
            for o in [1, 3, 7]:
                h = ph * theta / T_triad
                G[nd(PHI_p), nd(o)] += h
                G[nd(o), nd(PHI_p)] += -np.conj(h)
            G[nd(PHI_p), nd(PHI_p)] += ph * theta / T_triad
        else:
            G[nd(s), nd(PHI_s)] += c
            G[nd(PHI_s), nd(s)] += -np.conj(c)
            G[nd(p), nd(PHI_p)] += c
            G[nd(PHI_p), nd(p)] += -np.conj(c)
        G = (G - np.conj(G.T)) / 2
        beats.append(expm(G))
    return beats


def build_kappa_ring(n_oct, g_second_period=0.0, g_extra_tonic=0.0):
    N = 7 * n_oct
    kappa = np.eye(N, dtype=complex)
    for k in range(n_oct):
        b = 7 * k
        for (a, c) in [(0, 4), (2, 6), (1, 5), (3, 7)]:
            kappa[(b + a) % N, (b + c) % N] += alpha
            kappa[(b + c) % N, (b + a) % N] += alpha
    if g_second_period:
        for j in range(N):
            kappa[j, (j + 8) % N] += g_second_period
            kappa[(j + 8) % N, j] += g_second_period
    if g_extra_tonic:
        for j in range(N):
            kappa[j, (j + 7) % N] += g_extra_tonic
            kappa[(j + 7) % N, j] += g_extra_tonic
    return kappa


def ring_split(w, n_oct):
    N = 7 * n_oct
    residue = np.zeros(7)
    for j in range(N):
        residue[j % 7] += w[j]
    ws = residue[2] + residue[4] + residue[6]
    wp = residue[1] + residue[3] + residue[5]
    wt = residue[0]
    oct_w = np.array([w[7 * k:7 * k + 7].sum() for k in range(n_oct)])
    return ws, wp, wt, residue, oct_w


def E6(n_min=2, n_max=9):
    print("\n" + "=" * 70)
    print("E6: RING OF OCTAVES: SPECTRUM, SPLIT, AND EVEN/ODD PARITY PROBE")
    print("=" * 70)
    print(f"  {'n':>2} {'|l1|':>12} {'(|l1|-1)/a':>11} {'gap/a':>9} "
          f"{'struct%':>8} {'proc%':>7} {'tonic%':>7} {'maxP2even?':>10}")
    rows = []
    for n in range(n_min, n_max + 1):
        Top = build_kappa_ring(n) @ build_F_ring(n)
        ev, V = np.linalg.eig(Top)
        idx = np.argsort(-np.abs(ev))
        m = np.abs(ev)[idx]
        w = np.abs(V[:, idx[0]]) ** 2
        w = w / w.sum()
        ws, wp, wt, res, ow = ring_split(w, n)
        # period-2 octave component maximized over the top R eigenvectors
        best_c2 = 0.0
        for r in range(min(2 * n, len(idx))):
            v = V[:, idx[r]]
            oc = np.array([np.abs(v[7 * k:7 * k + 7]).sum() for k in range(n)])
            c2 = abs(np.dot(oc, [(-1) ** k for k in range(n)])) / oc.sum()
            best_c2 = max(best_c2, c2)
        rows.append((n, m[0], m[0] - m[1], ws, wp, wt, best_c2))
        print(f"  {n:>2} {m[0]:>12.8f} {(m[0]-1)/alpha:>11.4f} {(m[0]-m[1])/alpha:>9.4f} "
              f"{100*ws:>8.2f} {100*wp:>7.2f} {100*wt:>7.2f} {best_c2:>10.4f}")
    ev_even = [r for r in rows if r[0] % 2 == 0]
    ev_odd = [r for r in rows if r[0] % 2 == 1]
    print("\n  parity probe: max period-2 component, even rings vs odd rings")
    print(f"    even n: {[f'{r[6]:.4f}' for r in ev_even]}")
    print(f"    odd  n: {[f'{r[6]:.4f}' for r in ev_odd]}")
    print(f"    leading |l1|, even: {[f'{r[1]:.8f}' for r in ev_even]}")
    print(f"    leading |l1|, odd : {[f'{r[1]:.8f}' for r in ev_odd]}")
    print("  double-cover signature: a mode requiring antiperiodicity is exact")
    print("  on even rings and frustrated on odd rings.")


def station_distinguishability(Top, n_oct):
    """Mean over ALL eigenvectors of the variance of their residue-class
    profile. High = stations play distinct roles across the spectrum;
    0 = every eigenvector sees every residue equally (flattened ladder)."""
    ev, V = np.linalg.eig(Top)
    N = 7 * n_oct
    vals = []
    for r in range(N):
        w = np.abs(V[:, r]) ** 2
        w = w / w.sum()
        res = np.zeros(7)
        for j in range(N):
            res[j % 7] += w[j]
        vals.append(np.var(res))
    return float(np.mean(vals))


def E7(n_oct=6):
    print("\n" + "=" * 70)
    print("E7: COLLAPSE DEMO ON THE RING (forbidden 4D offset vs tonic control)")
    print("=" * 70)
    print("  metric: mean over ALL eigenvectors of residue-profile variance,")
    print("  normalized to g = 0. Collapse of the ladder -> 0.")
    rows = []
    for gm in [0, 1, 4, 16, 64, 137, 274]:
        g = gm * alpha
        out = []
        for kind in ['second', 'tonic']:
            kw = dict(g_second_period=g) if kind == 'second' else dict(g_extra_tonic=g)
            Top = build_kappa_ring(n_oct, **kw) @ build_F_ring(n_oct)
            out.append(station_distinguishability(Top, n_oct))
        rows.append((gm, out[0], out[1]))
    base = rows[0][1]
    print(f"\n  {'g/alpha':>8} {'g':>8} {'4D offset (forbidden)':>24} {'7-half-step control':>24}")
    for gm, a4, t7 in rows:
        print(f"  {gm:>8.0f} {gm*alpha:>8.3f} {a4/base:>24.4f} {t7/base:>24.4f}")
    print("\n  single-period lemma prediction: left column falls toward 0,")
    print("  the commensurate control column does not.")


if __name__ == '__main__':
    E1(4)
    E2(8)
    E6(2, 9)
    E7(6)
    E5(4, 30)
