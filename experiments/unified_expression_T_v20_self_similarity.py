"""
unified_expression_T_v20_self_similarity.py

Created: 2026-10-16
Last updated: 2026-10-16
Version: 1.0
History:
  - 2026-10-16 v1.0: initial. Numerical test of dynamical self-similarity,
    R o F^m = F o R, for the staggered (tonic-shared) octave operator.

DYNAMICAL SELF-SIMILARITY OF THE STAGGERED OCTAVE (v20 of the T-operator series)

The question (from the 2026-10-15 outside review relayed by Ashman's session):
repeating the same rule at every level is not self-similarity. Self-similarity
needs an explicit scale map R from a finer configuration to the next coarser one
such that advancing m fine steps and then rescaling agrees with rescaling and
advancing one coarse step:

    R o F_fine^m  =  F_coarse o R        (and the same for T = kappa o F)

Here F is the four-beat unitary of the staggered octave (v14 construction, canon
strokes i^1, i^2, i^3, i^0, theta = pi/2, hub theta/T) and T = kappa o F with the
four per-octave diameter bonds at the measured alpha = 1/137.035999177. One
application of F is one complete stroke cycle; m = 4 therefore means "one
completed fine cycle per coarse stroke" (four coarse strokes = one coarse F), and
m = 8 means two fine cycles per coarse stroke. E7 also tests the literal
stroke-level reading.

THE SCALE MAPS (readings of the corpus; findings file section 2 argues each)

  R_dec    tonic decimation. Coarse node j <- fine tonic node 7j. The literal
           3.5D = 0D' reading: a completed octave's closure node IS the next
           scale's station ("every point, heard from outside, is a completed
           boundary"). Ratio 7: one fine octave per coarse half-step.
  R_whole  octave-to-station block map. Coarse node j <- the completed fine
           octave j-1 (nodes 7j-7 .. 7j) projected onto the octave's own whole
           (the C8 attractor of T). The speaker-shift reading: "the individual
           of octave n+1 is the whole produced by octave n"; "an individual IS a
           point". R_unif is the same window with uniform weights.
  R_harm   harmonic 2:1 decimation (the 2026-07-30 string model: the octave is
           f2 = 2 f1, finer scales are more nodes in a fixed extent). Natural m = 2.
  R_shift  adjacency reading: the next scale is the next octave on the
           continuation axis (same-size map, the octave shift). On the open
           chain the analogue peels the bottom octave into its closure tonic.

CONTROLS AND NULLS
  * random R of the same shape: Haar co-isometries (same matrix shape), random
    decimations (same sparsity), wrong-residue decimations s = 1..6, random
    block weights (same sparsity as R_whole);
  * family ceilings: the best R inside corpus-shaped families (translation-
    covariant octave windows, 8 weights; station-dependent windows, 56 and 105
    weights), compared against misaligned windows, Haar-random fine dynamics,
    and random-block staggered constructions of identical geometry;
  * the tensor nesting construction (v11 / v14-C512 kappa conventions,
    generalized to depth n), with R = contraction of the finest factor;
  * a frozen-image diagnostic (E3b) for the only cells that beat the nulls.

PRE-STATED VERDICT RULE (fixed before the final run; exploratory runs had
already shown every corpus-map defect above 0.9, so the rule decides nothing
by its threshold): self-similarity is SUPPORTED at m only if the defect is small
(delta <= 0.10) AND below the 1st percentile of every null family. A defect
below the nulls but not small is "structure beyond chance", not self-similarity.

METRIC
  delta(X, Y) = min_phi ||X - e^{i phi} Y||_F / sqrt(||X||_F^2 + ||Y||_F^2)
              = sqrt(1 - 2|<Y, X>| / (||X||^2 + ||Y||^2))        in [0, 1]
  with X = R A^m, Y = B R. 0 = exact (up to a global phase, which a unitary
  cannot observe); 1 = uncorrelated. The Frobenius norm is the RMS over
  Haar-random input states, so delta is a state-averaged defect.

Station convention: legacy v-series coordinates (Phi at coordinate 2, boundary
at coordinate 3), read as continuation coordinates per the v14+ convention and
the interim glyph-integer rule. Glyph positions are coordinates, not station
claims. Run: python unified_expression_T_v20_self_similarity.py
Raw output of the committed run: v20_output.txt.
"""

import functools
import os
import sys
import time

import numpy as np
from scipy.linalg import expm, eigh

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'Xorzo'))
sys.path.insert(0, HERE)

import t_operator as tops                                         # noqa: E402
from unified_expression_T_v16_bloch_sectors import (              # noqa: E402
    ring_T_sync as v16_ring_T_sync, bloch_T as v16_bloch_T)
from unified_expression_T_v14_C512 import (                       # noqa: E402
    build_T_512 as c512_build_T_512, ALPHA as C512_ALPHA)

ALPHA = 1.0 / 137.035999177        # measured (CODATA 2022), as in v14/v16
THETA = np.pi / 2
T_TRIAD = 3
I_PHASES = [1j, -1 + 0j, -1j, 1 + 0j]   # canon strokes i^1, i^2, i^3, i^0
STRUCT = [0, 2, 4, 6]
PROC = [1, 3, 5, 7]
HUB_S, HUB_P = 4, 5
DIAMETERS = [(0, 4), (2, 6), (1, 5), (3, 7)]
Q_STAR_V17 = 0.362487638892 * np.pi     # v17's alpha -> 0 limit q*_0 (v16 sign convention)

RNG_SEED = 20261016
M_LIST = list(range(1, 9))


def hr(title):
    print()
    print('=' * 78)
    print(title)
    print('=' * 78)


def fmt_row(vals, w=6, p=3):
    return ' '.join(f'{v:>{w}.{p}f}' for v in vals)


# ============================================================ metric

def defect(X, Y):
    """Phase-optimized normalized defect, in [0, 1]."""
    ip = abs(np.vdot(Y, X))
    den = np.vdot(X, X).real + np.vdot(Y, Y).real
    return float(np.sqrt(max(0.0, 1.0 - 2.0 * ip / den)))


def defect_curve(R, A, B, m_list=M_LIST):
    out = []
    Am = np.eye(A.shape[0], dtype=complex)
    m_done = 0
    for m in m_list:
        while m_done < m:
            Am = A @ Am
            m_done += 1
        out.append(defect(R @ Am, B @ R))
    return np.array(out)


def powers(A, m_max):
    P = [np.eye(A.shape[0], dtype=complex)]
    for _ in range(m_max):
        P.append(A @ P[-1])
    return P


# ============================================================ builders

def beat_template(theta=THETA, phases=I_PHASES):
    """The four beats as entry lists [(a, b, h)] on the 8-station template
    (local 0..7; 7 is the next octave's 0). Exactly the v9/v14/v16 entries."""
    beats = []
    for (s, p, ph) in zip(STRUCT, PROC, phases):
        c = ph * theta
        ent = [(s, p, c), (p, s, -np.conj(c))]
        if s == HUB_S:
            for o in [0, 2, 6]:
                h = ph * theta / T_TRIAD
                ent += [(HUB_S, o, h), (o, HUB_S, -np.conj(h))]
            ent += [(HUB_S, HUB_S, ph * theta / T_TRIAD)]
            for o in [1, 3, 7]:
                h = ph * theta / T_TRIAD
                ent += [(HUB_P, o, h), (o, HUB_P, -np.conj(h))]
            ent += [(HUB_P, HUB_P, ph * theta / T_TRIAD)]
        else:
            ent += [(s, HUB_S, c), (HUB_S, s, -np.conj(c)),
                    (p, HUB_P, c), (HUB_P, p, -np.conj(c))]
        beats.append(ent)
    return beats


def ring_kappa(n_oct, alpha=ALPHA):
    N = 7 * n_oct
    K = np.eye(N, dtype=complex)
    for k in range(n_oct):
        for (a, b) in DIAMETERS:
            K[(7 * k + a) % N, (7 * k + b) % N] += alpha
            K[(7 * k + b) % N, (7 * k + a) % N] += alpha
    return K


def sync_ring(n_oct, theta=THETA, alpha=ALPHA):
    """Beat-synchronous staggered ring (v16): beat b = expm(sum over octaves of
    beat b's generator); F = B4 B3 B2 B1. Exactly octave-translation invariant.
    Returns (F, kappa, [B1, B2, B3, B4])."""
    N = 7 * n_oct
    beats = []
    for ent in beat_template(theta):
        G = np.zeros((N, N), dtype=complex)
        for k in range(n_oct):
            for (a, b, h) in ent:
                G[(7 * k + a) % N, (7 * k + b) % N] += h
        G = (G - np.conj(G.T)) / 2
        beats.append(expm(G))
    F = np.eye(N, dtype=complex)
    for B in beats:
        F = B @ F
    return F, ring_kappa(n_oct, alpha), beats


def seq_ring_from_block(n_oct, E8):
    """Octave-sequential ring (v14 convention, ascending) from any 8x8 octave
    unitary E8 acting on the octave's nodes [7k .. 7k+7] (mod N)."""
    N = 7 * n_oct
    F = np.eye(N, dtype=complex)
    for k in range(n_oct):
        idx = [(7 * k + l) % N for l in range(8)]
        E = np.eye(N, dtype=complex)
        E[np.ix_(idx, idx)] = E8
        F = E @ F
    return F


def canonical_octave_block():
    E = np.eye(8, dtype=complex)
    for B in tops.build_octave_beats_at(8, list(range(8))):
        E = B @ E
    return E


def haar_unitary(N, rng):
    Z = (rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))) / np.sqrt(2)
    Q, Rr = np.linalg.qr(Z)
    d = np.diag(Rr)
    return Q * (d / np.abs(d))


def haar_coisometry(Nc, Nf, rng):
    X = rng.normal(size=(Nf, Nc)) + 1j * rng.normal(size=(Nf, Nc))
    Q, _ = np.linalg.qr(X)
    return Q.conj().T


def leading(T):
    ev, V = np.linalg.eig(T)
    i = int(np.argmax(np.abs(ev)))
    v = V[:, i]
    return ev[i], v / np.linalg.norm(v)


# ---------------------------------------------------- tensor nesting (v11/C512)

_DIAM_ADJ = np.zeros((8, 8))
for (_a, _b) in DIAMETERS:
    _DIAM_ADJ[_a, _b] = _DIAM_ADJ[_b, _a] = 1.0


def tensor_ops(depth, alpha=ALPHA):
    """F = F8^{(x)depth}; kappa = intra-scale diameters at alpha on every factor
    + cross-scale diameter swaps between factors s < t at alpha^(t-s), with the
    exact loop convention of experiments/unified_expression_T_v14_C512.py
    (adjacent alpha, skip alpha^2). Factor 0 = greatest whole, last = finest."""
    F8 = tops.build_F_8D()
    d = 8 ** depth
    F = F8.copy()
    for _ in range(depth - 1):
        F = np.kron(F, F8)
    K = np.eye(d, dtype=complex)
    I8 = np.eye(8)
    for s in range(depth):
        ops = [I8] * depth
        ops[s] = alpha * _DIAM_ADJ
        M = ops[0]
        for o in ops[1:]:
            M = np.kron(M, o)
        K += M
    idx = np.arange(d).reshape([8] * depth)
    for s in range(depth):
        for t in range(s + 1, depth):
            c = alpha ** (t - s)
            for x in range(8):
                for y in range(8):
                    if _DIAM_ADJ[y, x] == 0:
                        continue
                    sl = [slice(None)] * depth
                    sl[s], sl[t] = x, y
                    sl2 = [slice(None)] * depth
                    sl2[s], sl2[t] = y, x
                    for ai, bi in zip(idx[tuple(sl)].ravel(),
                                      idx[tuple(sl2)].ravel()):
                        if ai != bi:
                            K[ai, bi] += c
                            K[bi, ai] += c
    return F, K


# ============================================================ scale maps R

def R_windows(Nc, Nf, weights, stride=7, offset=0, ring=True, normalize=True):
    """Row j reads fine nodes stride*j + offset + l (l = 0..W-1) with
    weights[j % P][l]; weights has shape (P, W). Ring: indices mod Nf. Chain:
    out-of-range entries dropped. Rows normalized to unit norm."""
    weights = np.atleast_2d(np.asarray(weights, dtype=complex))
    P, W = weights.shape
    R = np.zeros((Nc, Nf), dtype=complex)
    for j in range(Nc):
        for l in range(W):
            i = stride * j + offset + l
            if ring:
                i %= Nf
            elif not (0 <= i < Nf):
                continue
            R[j, i] += weights[j % P, l]
        if normalize:
            n = np.linalg.norm(R[j])
            if n > 0:
                R[j] /= n
    return R


def R_dec(Nc, Nf, ring=True, s=0):
    return R_windows(Nc, Nf, [[1.0]], stride=7, offset=s, ring=ring)


def whole_mode():
    """The C8 attractor of T = kappa o F on one octave (measured alpha): the
    octave's completed whole, local 0..7 (structural share 0.687, v10)."""
    K8 = np.eye(8, dtype=complex)
    for (a, b) in DIAMETERS:
        K8[a, b] = K8[b, a] = ALPHA
    _, v = leading(K8 @ tops.build_F_8D())
    return v


PSI_WHOLE = None   # set in main


def R_whole(Nc, Nf, ring=True, s=0):
    return R_windows(Nc, Nf, [np.conj(PSI_WHOLE)], stride=7, offset=-7 + s,
                     ring=ring)


def R_unif(Nc, Nf, ring=True, s=0):
    return R_windows(Nc, Nf, [np.ones(8) / np.sqrt(8)], stride=7,
                     offset=-7 + s, ring=ring)


def R_harm(Nc, Nf, ring=True):
    return R_windows(Nc, Nf, [[1.0]], stride=2, offset=0, ring=ring)


def family_basis(Nc, Nf, window, period, offset, ring=True, stride=7):
    """Basis matrices E_(r,l) of the family R(w) = sum w_(r,l) E_(r,l): row j
    reads fine node stride*j + offset + l with weight w_(j % period, l)."""
    Es = []
    for r in range(period):
        for l in range(window):
            E = np.zeros((Nc, Nf), dtype=complex)
            for j in range(r, Nc, period):
                i = stride * j + offset + l
                if ring:
                    i %= Nf
                elif not (0 <= i < Nf):
                    continue
                E[j, i] = 1.0
            if np.any(E):
                Es.append(E)
    return Es


def optimize_family(Es, A, B, nphi=72):
    """min over weights w and global phase of the normalized defect of
    R(w) = sum w_i E_i:  ||R A - e^{i phi} B R||^2 / (||R A||^2 + ||B R||^2).
    Exact in w (generalized Rayleigh quotient); phase by scan + refinement.
    Returns (delta, R_opt)."""
    k = len(Es)
    X = np.array([(E @ A).ravel() for E in Es])
    Y = np.array([(B @ E).ravel() for E in Es])
    XX = X.conj() @ X.T
    YY = Y.conj() @ Y.T
    XY = X.conj() @ Y.T
    D = XX + YY
    D = (D + D.conj().T) / 2 + 1e-14 * np.eye(k) * np.trace(D).real / k

    def solve(phi):
        c = np.exp(1j * phi)
        M = XX + YY - c * XY - np.conj(c) * XY.conj().T
        M = (M + M.conj().T) / 2
        ev, V = eigh(M, D)
        return ev[0], V[:, 0]

    best = (np.inf, None, None)
    for phi in np.linspace(0, 2 * np.pi, nphi, endpoint=False):
        e, v = solve(phi)
        if e < best[0]:
            best = (e, v, phi)
    step = 2 * np.pi / nphi
    for _ in range(3):
        for phi in np.linspace(best[2] - step, best[2] + step, 21):
            e, v = solve(phi)
            if e < best[0]:
                best = (e, v, phi)
        step /= 10
    w = best[1]
    R = sum(wi * E for wi, E in zip(w, Es))
    return float(np.sqrt(max(best[0], 0.0))), R


# ============================================================ experiments

def E0_instruments():
    hr('E0  INSTRUMENTS AND VERIFICATION')
    ok = True
    for n, ref in tops.V14_CHAIN_REFERENCE.items():
        S = tops.StaggeredOperator.chain(n, alpha=ALPHA)
        lam, _ = S.leading()
        good = abs(abs(lam) - ref) < 1e-9
        ok &= good
        print(f'  StaggeredOperator.chain({n}): |l1| = {abs(lam):.10f}  v14 ref '
              f'{ref:.10f}  {"ok" if good else "MISMATCH"}')
    for n in [2, 3, 6]:
        F, K, _ = sync_ring(n)
        d = np.abs(K @ F - v16_ring_T_sync(n)).max()
        ok &= d < 1e-12
        print(f'  sync ring n={n} vs v16 ring_T_sync: max |diff| = {d:.1e}')
    E8 = canonical_octave_block()
    d = np.abs(E8 - tops.build_F_8D()).max()
    print(f'  canonical octave block vs t_operator.build_F_8D: {d:.1e}')
    for n in [2, 3]:
        d = np.abs(seq_ring_from_block(n, E8)
                   - tops.StaggeredOperator.ring(n, alpha=ALPHA).F).max()
        ok &= d < 1e-12
        print(f'  sequential ring n={n} from block vs StaggeredOperator.ring: '
              f'{d:.1e}')
    Ft, Kt = tensor_ops(3, alpha=C512_ALPHA)
    d = np.abs(Kt @ Ft - c512_build_T_512()).max()
    ok &= d < 1e-12
    print(f'  tensor depth-3 builder vs v14-C512 build_T_512: {d:.1e}')
    print(f'  departure (|l1|-1)/alpha, tensor depth 1, 2, 3: ' + ', '.join(
        f'{(np.abs(np.linalg.eigvals(K @ F)).max() - 1) / ALPHA:.4f}'
        for (F, K) in [tensor_ops(n) for n in (1, 2, 3)])
          + '   (compounds)')
    print(f'  departure, staggered chain n = 1, 2, 3, 7, 14: ' + ', '.join(
        f'{tops.StaggeredOperator.chain(n, alpha=ALPHA).departure():.4f}'
        for n in (1, 2, 3, 7, 14)) + '   (stays in the v14 band; no compounding)')
    print(f'  whole-mode |psi|^2 (C8 attractor, local 0..7): '
          + ' '.join(f'{x:.4f}' for x in np.abs(PSI_WHOLE) ** 2))
    print(f'  all instrument checks: {"PASS" if ok else "FAIL"}')
    return ok


@functools.lru_cache(maxsize=None)
def build_systems(n_c):
    """Fine/coarse operator pairs for the ratio-7 maps (fine has 7 n_c octaves)."""
    sysd = {}
    Sf = tops.StaggeredOperator.chain(7 * n_c, alpha=ALPHA)
    Sc = tops.StaggeredOperator.chain(n_c, alpha=ALPHA)
    sysd['chain'] = dict(Ff=Sf.F, Tf=Sf.T, Fc=Sc.F, Tc=Sc.T, ring=False,
                         Nf=Sf.N, Nc=Sc.N)
    Rf = tops.StaggeredOperator.ring(7 * n_c, alpha=ALPHA)
    Rc = tops.StaggeredOperator.ring(n_c, alpha=ALPHA)
    sysd['seq ring'] = dict(Ff=Rf.F, Tf=Rf.T, Fc=Rc.F, Tc=Rc.T, ring=True,
                            Nf=Rf.N, Nc=Rc.N)
    Ff, Kf, _ = sync_ring(7 * n_c)
    Fc, Kc, _ = sync_ring(n_c)
    sysd['sync ring'] = dict(Ff=Ff, Tf=Kf @ Ff, Fc=Fc, Tc=Kc @ Fc, ring=True,
                             Nf=Ff.shape[0], Nc=Fc.shape[0])
    return sysd


def E2_fixed_maps(n_c=2):
    hr(f'E2  CORPUS SCALE MAPS: DEFECT delta(m), m = 1..8 '
       f'(fine {7 * n_c} octaves -> coarse {n_c})')
    print('  delta = 0 exact (up to phase), 1 uncorrelated.  Columns m = 1..8; '
          'm = 4 and m = 8 are columns 4 and 8.')
    print(f'  {"system":<10} {"R":<8} {"op":<3} ' + ' '.join(f'{m:>6d}' for m in M_LIST))
    out = {}
    for name, S in build_systems(n_c).items():
        for rname, rfun in [('R_dec', R_dec), ('R_whole', R_whole),
                            ('R_unif', R_unif)]:
            R = rfun(S['Nc'], S['Nf'], ring=S['ring'])
            for op in ('F', 'T'):
                dc = defect_curve(R, S[op + 'f'], S[op + 'c'])
                out[(name, rname, op)] = dc
                print(f'  {name:<10} {rname:<8} {op:<3} {fmt_row(dc)}')
    # harmonic 2:1 and adjacency maps
    for name in ('chain', 'sync ring'):
        if name == 'chain':
            Sf = tops.StaggeredOperator.chain(2 * n_c, alpha=ALPHA)
            Sc = tops.StaggeredOperator.chain(n_c, alpha=ALPHA)
            pairs = dict(F=(Sf.F, Sc.F), T=(Sf.T, Sc.T))
            Nf, Nc, ring = Sf.N, Sc.N, False
        else:
            Ff, Kf, _ = sync_ring(2 * n_c)
            Fc, Kc, _ = sync_ring(n_c)
            pairs = dict(F=(Ff, Fc), T=(Kf @ Ff, Kc @ Fc))
            Nf, Nc, ring = Ff.shape[0], Fc.shape[0], True
        R = R_harm(Nc, Nf, ring=ring)
        for op in ('F', 'T'):
            dc = defect_curve(R, *pairs[op])
            out[(name, 'R_harm', op)] = dc
            print(f'  {name:<10} {"R_harm":<8} {op:<3} {fmt_row(dc)}   '
                  f'(fine {2 * n_c} oct, 2:1)')
    Ff, Kf, _ = sync_ring(7 * n_c)
    N = Ff.shape[0]
    U = np.roll(np.eye(N), 7, axis=0)
    for op, A in (('F', Ff), ('T', Kf @ Ff)):
        dc = defect_curve(U, A, A)
        out[('sync ring', 'R_shift', op)] = dc
        print(f'  {"sync ring":<10} {"R_shift":<8} {op:<3} {fmt_row(dc)}   '
              f'(same size: octave shift)')
    pred = [np.sqrt(max(0.0, 1 - abs(np.trace(np.linalg.matrix_power(Ff, m - 1)))
                        / N)) for m in M_LIST]
    print(f'  {"":<10} {"closed":<8} {"F":<3} {fmt_row(pred)}   '
          f'sqrt(1 - |tr F^(m-1)| / N): exact for the shift')
    Sf = tops.StaggeredOperator.chain(n_c + 1, alpha=ALPHA)
    Sc = tops.StaggeredOperator.chain(n_c, alpha=ALPHA)
    Rp = np.zeros((Sc.N, Sf.N))
    for i in range(Sc.N):
        Rp[i, i + 7] = 1.0
    for op in ('F', 'T'):
        dc = defect_curve(Rp, getattr(Sf, op), getattr(Sc, op))
        out[('chain', 'R_peel', op)] = dc
        print(f'  {"chain":<10} {"R_peel":<8} {op:<3} {fmt_row(dc)}   '
              f'({n_c + 1} -> {n_c} oct: bottom octave into its closure tonic)')
    return out


def E2b_depth_and_long_m():
    hr('E2b DEPTH TREND (m = 4, 8) AND LONG-m SCAN (m = 1..49)')
    print(f'  {"system":<10} {"R":<8} ' + ' '.join(
        f'{"n_c=" + str(n) + " m4":>10} {"m8":>6}' for n in (1, 2, 3)))
    for name in ('chain', 'seq ring', 'sync ring'):
        for rname, rfun in [('R_dec', R_dec), ('R_whole', R_whole)]:
            cells = []
            for n_c in (1, 2, 3):
                if name == 'seq ring' and n_c == 1:
                    cells.append('       n/a    n/a')
                    continue
                S = build_systems(n_c)[name]
                R = rfun(S['Nc'], S['Nf'], ring=S['ring'])
                dc = defect_curve(R, S['Ff'], S['Fc'], [4, 8])
                cells.append(f'{dc[0]:>10.3f} {dc[1]:>6.3f}')
            print(f'  {name:<10} {rname:<8} ' + ' '.join(cells))
    S = build_systems(2)['sync ring']
    for rname, rfun in [('R_dec', R_dec), ('R_whole', R_whole)]:
        R = rfun(S['Nc'], S['Nf'])
        dc = defect_curve(R, S['Ff'], S['Fc'], list(range(1, 50)))
        i = int(np.argmin(dc))
        print(f'  sync ring n_c=2 {rname}: min over m = 1..49 is {dc[i]:.3f} at '
              f'm = {i + 1};  m = 7, 14, 21, 28, 49: '
              + ' '.join(f'{dc[m - 1]:.3f}' for m in (7, 14, 21, 28, 49)))


def null_stats(val, null):
    null = np.asarray(null)
    return null.mean(), null.std(), null.min(), float(np.mean(null <= val))


def E3_nulls(fixed, n_c=2, n_draw=200):
    hr(f'E3  RANDOM-R NULLS FOR THE CORPUS MAPS (n_c = {n_c}, {n_draw} draws each)')
    print('  pct = fraction of null draws with defect <= the corpus value '
          '(small pct = corpus map beats the null)')
    rng = np.random.default_rng(RNG_SEED)
    systems = build_systems(n_c)
    verdict_rows = []
    for name in ('chain', 'sync ring'):
        S = systems[name]
        Nf, Nc, ring = S['Nf'], S['Nc'], S['ring']
        P = powers(S['Ff'], 8)
        Fc = S['Fc']

        def curve(R):
            return np.array([defect(R @ P[m], Fc @ R) for m in M_LIST])

        N1 = np.array([curve(haar_coisometry(Nc, Nf, rng)) for _ in range(n_draw)])
        N2 = []
        for _ in range(n_draw):
            sel = np.sort(rng.choice(Nf, size=Nc, replace=False))
            R = np.zeros((Nc, Nf))
            R[np.arange(Nc), sel] = 1.0
            N2.append(curve(R))
        N2 = np.array(N2)
        N3 = np.array([curve(R_dec(Nc, Nf, ring=ring, s=s)) for s in range(1, 7)])
        N4 = []
        for _ in range(n_draw):
            w = rng.normal(size=8) + 1j * rng.normal(size=8)
            N4.append(curve(R_windows(Nc, Nf, [w], stride=7, offset=-7,
                                      ring=ring)))
        N4 = np.array(N4)
        print(f'\n  [{name}]  m:            ' + ' '.join(f'{m:>6d}' for m in M_LIST))
        print(f'  Haar co-isometry  mean  {fmt_row(N1.mean(0))}')
        print(f'                    min   {fmt_row(N1.min(0))}')
        print(f'  random decimation mean  {fmt_row(N2.mean(0))}')
        print(f'                    min   {fmt_row(N2.min(0))}')
        print(f'  wrong residue s=1..6 min{fmt_row(N3.min(0))}')
        print(f'  random weights    mean  {fmt_row(N4.mean(0))}')
        print(f'                    min   {fmt_row(N4.min(0))}')
        for rname, nulls in [('R_dec', [N1, N2, N3]), ('R_whole', [N1, N4]),
                             ('R_unif', [N1, N4])]:
            dc = fixed[(name, rname, 'F')]
            pcts = np.array([[float(np.mean(nl[:, k] <= dc[k])) for k in range(8)]
                             for nl in nulls])
            worst = pcts.max(0)
            print(f'  {rname:<8} corpus  {fmt_row(dc)}')
            print(f'  {"":<8} max pct {fmt_row(worst, p=2)}')
            for k, m in enumerate(M_LIST):
                verdict_rows.append((name, rname, m, dc[k], worst[k]))
    return verdict_rows


def E3b_frozen_image(n_c=2):
    hr('E3b DIAGNOSTIC: WHY R_whole BEATS THE NULLS AT SMALL m (the frozen image)')
    _, V = np.linalg.eig(tops.build_F_8D())
    ov = np.sort(np.abs(np.conj(V.T) @ PSI_WHOLE))[::-1]
    print('  overlap of the whole-mode with the eight F8 eigenvectors: '
          + ' '.join(f'{x:.4f}' for x in ov))
    print('  R_whole reads each fine octave in a near-eigenmode of its own beat block, so')
    print('  its coarse image barely moves (R F_f^m ~ mu^m R) and can overlap F_c R only')
    print('  through the identity (trace) part of F_c. Frozen defect d(R F^m, R), m = 1..8,')
    print('  and the frozen-image level d(R, F_c R) (= sqrt(1 - |tr F_c|/N_c) for co-isometric R):')
    systems = build_systems(n_c)
    for name in ('chain', 'sync ring'):
        S = systems[name]
        P = powers(S['Ff'], 8)
        Fc = S['Fc']
        for rname, rfun in (('R_whole', R_whole), ('R_unif', R_unif),
                            ('R_dec', R_dec)):
            R = rfun(S['Nc'], S['Nf'], ring=S['ring'])
            fz = [defect(R @ P[m], R) for m in M_LIST]
            print(f'    {name:<10} {rname:<8} frozen {fmt_row(fz)}   level '
                  f'{defect(R, Fc @ R):.3f}')
        print(f'    {name:<10} sqrt(1 - |tr F_c| / N_c) = '
              f'{np.sqrt(1 - abs(np.trace(Fc)) / S["Nc"]):.3f}')
    print('  The above-chance cells (R_whole, m <= 3) sit just above the frozen-image level and')
    print('  return to the null level as leakage through the shared tonics unfreezes the image.')


def symmetry_floor(B, R, A=None):
    """Theorem 1 lower bound for a translation-covariant R (R U_f = S R) on an
    exactly octave-invariant fine operator:
      delta >= ||(S B S^dag - B) R||_F / (2 sqrt(||R A||^2 + ||B R||^2))."""
    Nc = B.shape[0]
    S = np.roll(np.eye(Nc), 1, axis=0)
    num = np.linalg.norm((S @ B @ S.T - B) @ R)
    if A is None:
        den = np.sqrt(2) * np.linalg.norm(R)
    else:
        den = np.sqrt(np.linalg.norm(R @ A) ** 2 + np.linalg.norm(B @ R) ** 2)
    return num / (2 * den)


def E4_theorem1():
    hr('E4  THEOREM 1: THE SYMMETRY FLOOR FOR TRANSLATION-COVARIANT MAPS')
    print('  If F_f commutes with the fine octave shift U_f (exact on the sync ring)')
    print('  and R U_f = S R (S = coarse one-node shift), then for every m and phase:')
    print('    R F_f^m - c F_c R  -  S (R F_f^m - c F_c R) U_f^dag  =  c (S F_c S^dag - F_c) R')
    print('  so delta >= ||(S F_c S^dag - F_c) R||_F / (2 sqrt(||R F^m||^2+||F_c R||^2)).')
    print('  For a co-isometric R (R R^dag = 1) the floor is R-independent:')
    print('    delta >= ||S F_c S^dag - F_c||_F / (2 sqrt(2 N_c))  for ALL m.')
    for n_c in (1, 2, 3, 4):
        Fc, Kc, _ = sync_ring(n_c)
        Nc = Fc.shape[0]
        S = np.roll(np.eye(Nc), 1, axis=0)
        fl = np.linalg.norm(S @ Fc @ S.T - Fc) / (2 * np.sqrt(2 * Nc))
        Tc = Kc @ Fc
        flT = np.linalg.norm(S @ Tc @ S.T - Tc) / (2 * np.sqrt(2 * Nc))
        print(f'    n_c = {n_c}: floor(F) = {fl:.4f}   floor(T) ~ {flT:.4f}')
    # verification on every translation-covariant R used (sync ring, n_c = 2)
    rng = np.random.default_rng(RNG_SEED + 4)
    Ff, Kf, _ = sync_ring(14)
    Fc, Kc, _ = sync_ring(2)
    Nf, Nc = Ff.shape[0], Fc.shape[0]
    P = powers(Ff, 8)
    maps = [('R_dec', R_dec(Nc, Nf)), ('R_whole', R_whole(Nc, Nf)),
            ('R_unif', R_unif(Nc, Nf))]
    maps += [(f'dec s={s}', R_dec(Nc, Nf, s=s)) for s in range(1, 7)]
    for t in range(20):
        w = rng.normal(size=8) + 1j * rng.normal(size=8)
        maps.append((f'rand w {t}', R_windows(Nc, Nf, [w], 7, -7)))
    for s in range(7):
        Es = family_basis(Nc, Nf, 8, 1, -7 + s)
        _, Ropt = optimize_family(Es, P[4], Fc)
        maps.append((f'TC-opt s={s}', Ropt))
    margins = []
    for label, R in maps:
        for m in M_LIST:
            d = defect(R @ P[m], Fc @ R)
            fl = symmetry_floor(Fc, R, P[m])
            margins.append(d - fl)
    print(f'  verified on {len(maps)} translation-covariant maps x 8 m (sync ring '
          f'n_c=2): min(delta - floor) = {min(margins):.4f}  (>= 0 required)')
    print(f'  the floor is m-independent: no time dilation m can rescue any '
          f'translation-covariant octave-to-station map.')


def E5_theorem2():
    hr('E5  THEOREM 2: THE ATTRACTOR SELECTION RULE (momentum maps q -> 7q)')
    print('  Any R covariant at the coarse-lattice level (R U_f^7 = U_c^7 R: seven fine')
    print('  octaves = one coarse octave; every ratio-7 map in E2-E6) sends a fine')
    print('  Bloch mode of momentum q (per octave) to coarse momentum 7q (mod 2 pi).')
    print('  (For the 2:1 harmonic map the same argument gives q -> 2q, whose only fixed')
    print('  point is q = 0; the adjacency shift maps the attractor to itself up to e^{iq*}.)')
    print('  The fine and coarse attractors are the same construction, both at q*.')
    print('  So <psi_c, R psi_f> = 0 unless 7 q* = q* (mod 2 pi), i.e. q* in (pi/3) Z.')
    qs = np.linspace(0, 2 * np.pi, 721, endpoint=False)
    lead_mod = np.array([np.abs(np.linalg.eigvals(v16_bloch_T(q))).max() for q in qs])
    i0 = int(np.argmax(lead_mod))
    dq = qs[1] - qs[0]
    lo, hi = qs[i0] - dq, qs[i0] + dq
    for _ in range(4):
        qf = np.linspace(lo, hi, 81)
        lf = np.array([np.abs(np.linalg.eigvals(v16_bloch_T(q))).max() for q in qf])
        j = int(np.argmax(lf))
        step = qf[1] - qf[0]
        lo, hi = qf[j] - step, qf[j] + step
    q_star = qf[j]
    print(f'  q* at the measured alpha (recomputed from v16 Bloch blocks) = '
          f'{q_star / np.pi:.9f} pi   (v16: 0.3621 pi)')
    print(f'  q*_0, the alpha -> 0 limit (v17 perturbation theorem) = '
          f'{Q_STAR_V17 / np.pi:.12f} pi')
    for lab, q in (('q*', q_star), ('q*_0', Q_STAR_V17)):
        k3 = round(q / (np.pi / 3))
        print(f'  {lab:<5} nearest RG-compatible momentum {k3} pi/3; offset '
              f'{(q - k3 * np.pi / 3) / np.pi:+.6f} pi '
              f'({np.degrees(q - k3 * np.pi / 3):+.3f} deg); image 7 {lab} mod 2 pi = '
              f'{(7 * q) % (2 * np.pi) / np.pi:.6f} pi vs {lab} = {q / np.pi:.6f} pi')
    print('  different momentum sectors in both cases: the attractor-to-attractor '
          'overlap is 0 exactly.')
    print('  Finite rings (sync; momentum = phase advance per octave of the leading T mode):')
    rng = np.random.default_rng(RNG_SEED + 5)
    for n_c in (2, 3, 4):
        Ff, Kf, _ = sync_ring(7 * n_c)
        Fc, Kc, _ = sync_ring(n_c)
        _, pf = leading(Kf @ Ff)
        _, pc = leading(Kc @ Fc)
        Nf, Nc = Ff.shape[0], Fc.shape[0]
        # momentum = phase advance per octave, psi_(i+7) = e^{iq} psi_i (v16 convention)
        Uf = np.roll(np.eye(Nf), -7, axis=0)
        Uc7 = np.roll(np.eye(Nc), -7, axis=0)
        qf_ = np.angle(np.vdot(pf, Uf @ pf)) % (2 * np.pi)
        Qc = np.angle(np.vdot(pc, Uc7 @ pc)) % (2 * np.pi)
        img_q = (7 * qf_) % (2 * np.pi)
        ovs = []
        for R in (R_dec(Nc, Nf), R_whole(Nc, Nf), R_unif(Nc, Nf)):
            v = R @ pf
            ovs.append(abs(np.vdot(pc, v)) / np.linalg.norm(v))
        coincide = abs(np.angle(np.exp(1j * (img_q - Qc)))) < 1e-6
        # within-sector chance: random vectors in the coarse momentum sector Q_c
        proj = np.zeros((Nc, Nc), dtype=complex)
        for k in range(n_c):
            proj += np.exp(-1j * Qc * k) * np.linalg.matrix_power(Uc7, k)
        proj /= n_c
        ch = []
        for _ in range(400):
            v = proj @ (rng.normal(size=Nc) + 1j * rng.normal(size=Nc))
            ch.append(abs(np.vdot(pc, v)) / np.linalg.norm(v))
        print(f'    n_c={n_c}: q_f = {qf_ / np.pi:.4f} pi, 7 q_f = {img_q / np.pi:.4f} pi, '
              f'Q_c = {Qc / np.pi:.4f} pi  {"COINCIDE (finite-size rounding)" if coincide else "differ"};'
              f'  overlap dec/whole/unif = ' + '/'.join(f'{o:.2e}' for o in ovs)
              + (f';  within-sector chance {np.mean(ch):.3f} +/- {np.std(ch):.3f}'
                 if coincide else ''))
    Ff, Kf, _ = sync_ring(14)
    Fc, Kc, _ = sync_ring(2)
    _, pf = leading(Kf @ Ff)
    _, pc = leading(Kc @ Fc)
    per_oct = (np.abs(pf) ** 2).reshape(14, 7).sum(1)
    wc = np.abs(pc[:7]) ** 2
    print(f'  Weight level (|psi|^2 instead of amplitudes), n_c=2: fine attractor per-octave '
          f'weights max/min = {per_oct.max() / per_oct.min():.9f} (uniform, v16), so every')
    print('  block-summed octave-to-station image is uniform over coarse nodes; the coarse '
          'attractor within one octave is not:')
    print('    coarse station shares (local 0..6): ' + ' '.join(f'{x:.4f}' for x in wc / wc.sum()))
    print('  Open chain (no momentum; attractor = standing dome): tonic-decimation overlap')
    for n_c in (1, 2, 3):
        Sf = tops.StaggeredOperator.chain(7 * n_c, alpha=ALPHA)
        Sc = tops.StaggeredOperator.chain(n_c, alpha=ALPHA)
        _, pf = Sf.leading()
        _, pc = Sc.leading()
        v = R_dec(Sc.N, Sf.N, ring=False) @ pf
        ch = [abs(np.vdot(pc, u)) / np.linalg.norm(u) for u in
              (rng.normal(size=(400, Sc.N)) + 1j * rng.normal(size=(400, Sc.N)))]
        print(f'    n_c={n_c}: overlap {abs(np.vdot(pc, v)) / np.linalg.norm(v):.3f}   '
              f'random-vector chance {np.mean(ch):.3f} +/- {np.std(ch):.3f}')
    return q_star


def E6_family_ceilings(n_draw_blocks=40, n_draw_haar=20):
    hr('E6  FAMILY CEILINGS: THE BEST R INSIDE CORPUS-SHAPED FAMILIES')
    print('  TC w8  = translation-covariant octave window, 8 free complex weights')
    print('  SD w8  = station-dependent window (weights depend on coarse residue '
          'j mod 7), 56 weights')
    print('  SD w15 = station-dependent two-octave window, 105 weights')
    print('  offset s: window starts at fine node 7j - 7 + s (s = 0: one fine octave, '
          'tonic to tonic)')
    Ff, Kf, _ = sync_ring(14)
    Fc, Kc, _ = sync_ring(2)
    Nf, Nc = Ff.shape[0], Fc.shape[0]
    P = powers(Ff, 8)
    res = {}
    print(f'\n  sync ring n_c=2, m = 1..8:')
    for label, window, period in [('TC w8', 8, 1), ('SD w8', 8, 7), ('SD w15', 15, 7)]:
        for s in ((0, 1, 2, 3, 4, 5, 6) if window == 8 else (0, 3)):
            Es = family_basis(Nc, Nf, window, period, -7 + s)
            dc = np.array([optimize_family(Es, P[m], Fc)[0] for m in M_LIST])
            res[(label, s)] = dc
            print(f'    {label:<7} s={s}: {fmt_row(dc)}')
    for label in ('TC w8', 'SD w8'):
        al = res[(label, 0)]
        mis = np.min([res[(label, s)] for s in range(1, 7)], axis=0)
        print(f'    {label}: aligned minus best misaligned, per m: {fmt_row(al - mis)}')
    print('\n  sequential ring (StaggeredOperator.ring) n_c=2 and the same-geometry nulls (m = 4, 8):')
    E8c = canonical_octave_block()
    Ffs = seq_ring_from_block(14, E8c)
    Fcs = seq_ring_from_block(2, E8c)
    Es_sd = family_basis(Nc, Nf, 8, 7, -7)
    Es_tc = family_basis(Nc, Nf, 8, 1, -7)
    canon = {lab: [optimize_family(E, np.linalg.matrix_power(Ffs, m), Fcs)[0]
                   for m in (4, 8)] for lab, E in (('SD w8', Es_sd), ('TC w8', Es_tc))}
    print(f'    canonical: SD w8 {canon["SD w8"][0]:.3f} {canon["SD w8"][1]:.3f}   '
          f'TC w8 {canon["TC w8"][0]:.3f} {canon["TC w8"][1]:.3f}')
    rng = np.random.default_rng(RNG_SEED + 6)
    both, fine_only = [], []
    t0 = time.time()
    for _ in range(n_draw_blocks):
        E8r = haar_unitary(8, rng)
        Ffr = seq_ring_from_block(14, E8r)
        Fcr = seq_ring_from_block(2, E8r)
        both.append([optimize_family(Es_sd, np.linalg.matrix_power(Ffr, m), Fcr, 48)[0]
                     for m in (4, 8)])
        fine_only.append([optimize_family(Es_sd, np.linalg.matrix_power(Ffr, m), Fcs, 48)[0]
                          for m in (4, 8)])
    both, fine_only = np.array(both), np.array(fine_only)
    for lab, arr in (('random-block construction, both scales', both),
                     ('random-block fine, canonical coarse', fine_only)):
        pct = [float(np.mean(arr[:, k] <= canon['SD w8'][k])) for k in range(2)]
        print(f'    {lab:<40} SD w8 m=4: {arr[:, 0].mean():.3f} +/- {arr[:, 0].std():.3f} '
              f'(min {arr[:, 0].min():.3f}); m=8: {arr[:, 1].mean():.3f} +/- '
              f'{arr[:, 1].std():.3f};  canonical pct {pct[0]:.2f}/{pct[1]:.2f}')
    hv = []
    for _ in range(n_draw_haar):
        H = haar_unitary(Nf, rng)
        hv.append([optimize_family(Es_sd, np.linalg.matrix_power(H, m), Fcs, 48)[0]
                   for m in (4, 8)])
    hv = np.array(hv)
    print(f'    Haar-random fine unitary (non-local)          SD w8 m=4: '
          f'{hv[:, 0].mean():.3f} +/- {hv[:, 0].std():.3f} (min {hv[:, 0].min():.3f})'
          f'   [{time.time() - t0:.0f}s]')
    print('\n  depth trend of the ceilings (sync ring, m = 1, 4, 8):')
    for n_c in (1, 2, 3):
        Ff_, _, _ = sync_ring(7 * n_c)
        Fc_, _, _ = sync_ring(n_c)
        P_ = powers(Ff_, 8)
        cells = []
        for label, window, period in [('TC w8', 8, 1), ('SD w8', 8, 7)]:
            Es = family_basis(Fc_.shape[0], Ff_.shape[0], window, period, -7)
            cells.append(f'{label} ' + ' '.join(
                f'{optimize_family(Es, P_[m], Fc_)[0]:.3f}' for m in (1, 4, 8)))
        print(f'    n_c={n_c} (fine {7 * n_c} oct): ' + '   '.join(cells))
    return res


def E7_stroke_level(n_c=2):
    hr('E7  STROKE-LEVEL READING (sync ring; F only)')
    print('  (a) one completed fine cycle per coarse stroke, stroke by stroke:')
    print('      R F_f^k  vs  (B_c[k-1] ... B_c[0]) R,  k = 1..4  (k = 4 is the cycle-level m = 4)')
    print('  (b) literal "m fine strokes per coarse stroke": R S_f(m) vs B_c[0] R, m = 1..8,')
    print('      S_f(m) = first m fine strokes in canon order (S_f(4) = F_f)')
    Ff, _, Bf = sync_ring(7 * n_c)
    Fc, _, Bc = sync_ring(n_c)
    Nf, Nc = Ff.shape[0], Fc.shape[0]
    rng = np.random.default_rng(RNG_SEED + 7)
    for rname, R in (('R_dec', R_dec(Nc, Nf)), ('R_whole', R_whole(Nc, Nf)),
                     ('Haar', None)):
        def run(Rm):
            a, Pc, Fk = [], np.eye(Nc, dtype=complex), np.eye(Nf, dtype=complex)
            for k in range(4):
                Fk = Ff @ Fk
                Pc = Bc[k] @ Pc
                a.append(defect(Rm @ Fk, Pc @ Rm))
            b, Sm = [], np.eye(Nf, dtype=complex)
            for m in range(8):
                Sm = Bf[m % 4] @ Sm
                b.append(defect(Rm @ Sm, Bc[0] @ Rm))
            return np.array(a), np.array(b)
        if R is None:
            runs = [run(haar_coisometry(Nc, Nf, rng)) for _ in range(100)]
            a = np.mean([r[0] for r in runs], 0)
            b = np.mean([r[1] for r in runs], 0)
            rname = 'Haar mean'
        else:
            a, b = run(R)
        print(f'    {rname:<10} (a) {fmt_row(a)}    (b) {fmt_row(b)}')


def E8_tensor():
    hr('E8  TENSOR-NESTING NULL (v11 / v14-C512 construction, R = contract finest factor)')
    F8 = tops.build_F_8D()
    ev, V = np.linalg.eig(F8)
    w_eig = V[:, 0] / np.linalg.norm(V[:, 0])
    t = [np.trace(np.linalg.matrix_power(F8, k)) / 8 for k in range(9)]
    print('  |tr F8^k| / 8, k = 0..8: ' + ' '.join(f'{abs(x):.4f}' for x in t))
    print(f'  {"depth":<6} {"R":<16} {"op":<3} ' + ' '.join(f'{m:>6d}' for m in M_LIST))
    for depth in (2, 3):
        Ff, Kf = tensor_ops(depth)
        Fc, Kc = tensor_ops(depth - 1)
        for wlabel, w in (('<whole| (C8 FP)', PSI_WHOLE), ('<F8 eigvec|', w_eig)):
            R = np.kron(np.eye(8 ** (depth - 1)), np.conj(w)[None, :])
            for op, (A, B) in (('F', (Ff, Fc)), ('T', (Kf @ Ff, Kc @ Fc))):
                if op == 'T' and wlabel.startswith('<F8'):
                    continue
                print(f'  {depth}->{depth - 1:<3} {wlabel:<16} {op:<3} '
                      f'{fmt_row(defect_curve(R, A, B))}')
    print('  closed form (pure F, w an eigenvector of F8): delta^2 = 1 - |tr F8^(m-1)/8|^(depth-1)')
    for depth in range(2, 9):
        print(f'    depth {depth}: ' + fmt_row(
            [np.sqrt(max(0.0, 1 - abs(t[m - 1]) ** (depth - 1))) for m in M_LIST]))
    print('  m = 1 is exact for any separable nesting (the same rule at every level);')
    print('  for m >= 2 the defect compounds toward 1 with depth.')


def E9_renormalized_angle(n_c=2):
    hr('E9  ROBUSTNESS: LET THE COARSE BEAT ANGLE (AND ALPHA) RENORMALIZE')
    Ff, Kf, _ = sync_ring(7 * n_c)
    Nf, Nc = Ff.shape[0], 7 * n_c
    R = R_dec(Nc, Nf)
    ths = np.linspace(0, np.pi, 61)
    Es = family_basis(Nc, Nf, 8, 7, -7)
    for m in (4, 8):
        A = np.linalg.matrix_power(Ff, m)
        dd = np.array([defect(R @ A, sync_ring(n_c, theta=th)[0] @ R) for th in ths])
        i = int(np.argmin(dd))
        sd = np.array([optimize_family(Es, A, sync_ring(n_c, theta=th)[0], 48)[0]
                       for th in ths[::2]])
        j = int(np.argmin(sd))
        print(f'  m={m}: R_dec   min over theta\' {dd[i]:.3f} at {ths[i] / np.pi:.3f} pi '
              f'(canonical pi/2: {dd[30]:.3f})')
        print(f'        SD w8   min over theta\' {sd[j]:.3f} at {ths[::2][j] / np.pi:.3f} pi '
              f'(canonical pi/2: {sd[15]:.3f});  profile: ' + ' '.join(
                  f'{x:.2f}' for x in sd[::3]))
    A4 = np.linalg.matrix_power(Kf @ Ff, 4)
    Fc, _, _ = sync_ring(n_c)
    print('  T with renormalized coarse alpha\' (R_dec, m = 4): ' + ', '.join(
        f"alpha'={mult:g} alpha: {defect(R @ A4, ring_kappa(n_c, mult * ALPHA) @ Fc @ R):.4f}"
        for mult in (0, 1, 2, 10)))


def verdict(rows):
    hr('VERDICT (pre-stated rule: supported iff delta <= 0.10 AND below the 1st '
       'percentile of every null)')
    supported = [r for r in rows if r[3] <= 0.10 and r[4] <= 0.01]
    beyond = [r for r in rows if r[3] > 0.10 and r[4] <= 0.01]
    print(f'  corpus map x system x m cells tested: {len(rows)}')
    print(f'  SUPPORTED: {len(supported)}')
    print(f'  below every null but not small (structure beyond chance): {len(beyond)}')
    for r in beyond:
        print(f'    {r[0]:<10} {r[1]:<8} m={r[2]}: delta {r[3]:.3f}, max pct {r[4]:.3f}')
    print(f'  smallest corpus-map defect anywhere: '
          f'{min(r[3] for r in rows):.3f}')


def main():
    global PSI_WHOLE
    t0 = time.time()
    PSI_WHOLE = whole_mode()
    print('unified_expression_T_v20_self_similarity.py  (v1.0, 2026-10-16)')
    print(f'alpha = 1/{1 / ALPHA:.9f} (measured); numpy {np.__version__}')
    if not E0_instruments():
        print('INSTRUMENT CHECK FAILED; aborting.')
        return
    fixed = E2_fixed_maps(2)
    E2b_depth_and_long_m()
    rows = E3_nulls(fixed)
    E3b_frozen_image()
    E4_theorem1()
    E5_theorem2()
    E6_family_ceilings()
    E7_stroke_level()
    E8_tensor()
    E9_renormalized_angle()
    verdict(rows)
    print(f'\n[total runtime {time.time() - t0:.0f}s]')


if __name__ == '__main__':
    main()
