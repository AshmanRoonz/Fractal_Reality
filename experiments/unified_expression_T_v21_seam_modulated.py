"""
unified_expression_T_v21_seam_modulated.py

Created: 2026-10-16
Last updated: 2026-10-16
Version: 1.0
History:
  - 2026-10-16 v1.0: initial. Dynamical self-similarity test of the
    hierarchically seam-modulated staggered chain (the constructive follow-up
    named in T_operator_findings_v20_self_similarity.md section 4).

THE SEAM-MODULATED CHAIN (v21 of the T-operator series)

v20 found the homogeneous staggered chain is not self-similar under
octave-to-station coarse-graining (R o F^m = F o R fails at every m), for two
exact reasons: the fine chain is homogeneous at the octave level while the
coarse octave is not homogeneous at the station level (a defect floor near
0.50 for translation-covariant maps), and coarse-graining sends the attractor
momentum q to 7q with q* not a multiple of pi/3. v20 section 4 turned this into
a specification: let the seams carry the coarse station pattern, recursively.
This experiment builds that chain and tests it.

THE CONSTRUCTION
  Ring of n = 7^L octaves. Seam j (the tonic shared by octaves j-1 and j) has a
  ROLE: the coarse station it first becomes under repeated tonic decimation,
  i.e. the first nonzero base-7 digit of j (0 for the top seam). Under tonic
  decimation seam 7J goes to coarse seam J with the same role, so the coarse
  ring (7^(L-1) octaves) is the same construction one level up.
  Octave k closes into seam k+1 and opens at seam k; the modulation reads
  those roles. Corpus instances (no free parameters):
    role strokes : an octave that completes into a processual coarse station
                   (residue 1, 3, 5) carries that station's canon stroke
                   (i^1, i^2, i^3) on its completing beat (beat 4, canon i^0);
                   structural roles and the tonic keep i^0 ("one stroke per
                   processual residue class").
    role gates   : the same strokes as a phase on the shared seam node, once per
                   cycle; the beats stay canon.
  General family (35 parameters): per role, a phase and a gain on the
  completing beat, a phase and a gain on the opening beat, and a seam gate
  phase. --optimize searches it for the smallest defect (the committed search
  is embedded below and logged in v21_optimize_output.txt).

INSTRUMENTS
  v20's defect delta(m) (0 exact up to phase, 1 uncorrelated), scale maps
  (R_dec, R_whole with each octave's own whole-mode, R_unif), null families,
  and the tensor-nesting comparison. New here:
  * a fast exact family optimizer from entry-level Gram identities;
  * a CONSTRAINED family optimizer that keeps every coarse row at unit norm.
    The unconstrained optimum can shrink hard-to-match coarse rows toward zero
    (v20's station-dependent ceilings did); a coarse-graining must keep every
    coarse node, so constrained ceilings are the honest ones, bracketed by the
    unconstrained and row-normalized values;
  * an exact leakage identity: for a co-isometric R,
      delta^2 = 1 - |<F_c, R F^m R^dag>| / N_c,
    so self-similarity needs both no leakage out of R's row space and a
    compressed dynamics equal to F_c;
  * E9, THE 720 TEST (added at Ashman's prompt, 2026-10-16): "the point is a
    process at the next scale ... then another scale again and it's a
    structure again ... that's the 720". One scale step moves a point by 3.5D
    (process parity), two steps by 7D = R (structure again): the parity
    double cover, 360 degrees flips, 720 restores. Tested as the two-step map
    (scale n -> n+2) on the canon, seam-modulated and whole-tone chains, and as
    the ratio-3.5 map that sends each octave's closing point to a coarse
    process and its body to a coarse structure.

PRE-STATED VERDICT RULE (v20's): SUPPORTED at m only if delta <= 0.10 AND below
the 1st percentile of every null family.

Station labels are legacy continuation coordinates (v14+ convention).
Run: python unified_expression_T_v21_seam_modulated.py   (about 3 minutes)
     python unified_expression_T_v21_seam_modulated.py --optimize   (the search;
     about 26 minutes)
Raw output of the committed runs: v21_output.txt, v21_optimize_output.txt.
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

import t_operator as tops                                          # noqa: E402
import unified_expression_T_v20_self_similarity as v20             # noqa: E402
import unified_expression_T_v18_wholetone_operator as v18          # noqa: E402

ALPHA = v20.ALPHA
THETA = v20.THETA
T_TRIAD = v20.T_TRIAD
I_PHASES = v20.I_PHASES
STRUCT, PROC = v20.STRUCT, v20.PROC
HUB_S, HUB_P = v20.HUB_S, v20.HUB_P
DIAMETERS = v20.DIAMETERS
Q_STAR_V17 = v20.Q_STAR_V17
defect = v20.defect

# coarse station types d = 0..6 (residue of the coarse node; 0 = coarse tonic)
ROLE_NAMES = ['tonic', 'conv', 'line', 'branch', 'field', 'emerge', 'bound']
# canon stroke exponent carried by each coarse station: processual residues
# 1, 3, 5 carry i^1, i^2, i^3; structural residues and the tonic carry none
# (i^0), per the canon convention "one stroke per processual residue class"
ROLE_STROKE = [0, 1, 0, 2, 0, 3, 0]


# ============================================================ roles

def seam_role(j, n_oct):
    """Role of seam j on a ring of n_oct = 7^L octaves: the coarse station type
    the seam first becomes under repeated tonic decimation, i.e. the first
    nonzero base-7 digit of j (0 for the top seam j = 0)."""
    j %= n_oct
    if j == 0:
        return 0
    while j % 7 == 0:
        j //= 7
    return j % 7


def seam_level(j, n_oct):
    """Number of decimations seam j survives as a tonic (7-adic valuation);
    the top seam gets L = log7(n_oct)."""
    j %= n_oct
    if j == 0:
        return int(round(np.log(n_oct) / np.log(7)))
    v = 0
    while j % 7 == 0:
        j //= 7
        v += 1
    return v


# ============================================================ modulation

def canonical_mod():
    """Per-role modulation arrays (index = role d = 0..6)."""
    return dict(close_phase=np.zeros(7), close_gain=np.ones(7),
                open_phase=np.zeros(7), open_gain=np.ones(7),
                gate_phase=np.zeros(7))


def role_stroke_mod():
    """Corpus instance A ('role strokes'): an octave that completes into a
    processual coarse station carries that station's canon stroke on its
    completing beat (beat 4: i^0 -> i^s); everything else canon."""
    m = canonical_mod()
    m['close_phase'] = np.array([np.pi / 2 * s for s in ROLE_STROKE])
    return m


def role_gate_mod():
    """Corpus instance B ('role gates'): the same strokes applied as a phase
    on the shared seam node once per cycle; the beats stay canon."""
    m = canonical_mod()
    m['gate_phase'] = np.array([np.pi / 2 * s for s in ROLE_STROKE])
    return m


MOD_KEYS = ['close_phase', 'close_gain', 'open_phase', 'open_gain', 'gate_phase']


def mod_to_vec(m):
    return np.concatenate([np.asarray(m[k], dtype=float) for k in MOD_KEYS])


def vec_to_mod(v):
    v = np.asarray(v, dtype=float)
    return {k: v[7 * i:7 * (i + 1)].copy() for i, k in enumerate(MOD_KEYS)}


# ============================================================ builders

def octave_generators(phases, gains, theta=THETA):
    """Four 8x8 anti-Hermitian beat generators of one octave (local 0..7).
    Beat b uses stroke phases[b] and angle gains[b] * theta; with canon
    phases and unit gains this is exactly v20.beat_template / t_operator."""
    gens = []
    for b, (s, p) in enumerate(zip(STRUCT, PROC)):
        ph = phases[b]
        th = gains[b] * theta
        G = np.zeros((8, 8), dtype=complex)
        c = ph * th
        G[s, p] += c
        G[p, s] += -np.conj(c)
        if s == HUB_S:
            for o in [0, 2, 6]:
                h = ph * th / T_TRIAD
                G[HUB_S, o] += h
                G[o, HUB_S] += -np.conj(h)
            G[HUB_S, HUB_S] += ph * th / T_TRIAD
            for o in [1, 3, 7]:
                h = ph * th / T_TRIAD
                G[HUB_P, o] += h
                G[o, HUB_P] += -np.conj(h)
            G[HUB_P, HUB_P] += ph * th / T_TRIAD
        else:
            G[s, HUB_S] += c
            G[HUB_S, s] += -np.conj(c)
            G[p, HUB_P] += c
            G[HUB_P, p] += -np.conj(c)
        gens.append((G - np.conj(G.T)) / 2)
    return gens


def octave_params(k, n_oct, mod):
    """Stroke phases and gains of octave k: its opening seam is k, its closing
    seam is k + 1; the modulation reads the roles of those seams."""
    d_open = seam_role(k, n_oct)
    d_close = seam_role(k + 1, n_oct)
    phases = list(I_PHASES)
    gains = [1.0, 1.0, 1.0, 1.0]
    if mod is not None:
        phases[0] = I_PHASES[0] * np.exp(1j * mod['open_phase'][d_open])
        phases[3] = I_PHASES[3] * np.exp(1j * mod['close_phase'][d_close])
        gains[0] = float(mod['open_gain'][d_open])
        gains[3] = float(mod['close_gain'][d_close])
    return phases, gains


def ring_kappa(n_oct, alpha=ALPHA):
    return v20.ring_kappa(n_oct, alpha)


def build_ring(n_oct, mod=None, composition='seq', theta=THETA, blocks=None):
    """Seam-modulated staggered ring of n_oct octaves (7 n_oct nodes).
    composition 'seq': octave-sequential ascending (v14 / StaggeredOperator);
    'sync': beat-synchronous (v16). The seam gate (if any) acts once per cycle
    after the beats. Returns (F, octave_blocks), octave_blocks[k] the 8x8
    beat product of octave k (used for its whole-mode)."""
    N = 7 * n_oct
    gens_all, oct_blocks = [], []
    for k in range(n_oct):
        ph, ga = octave_params(k, n_oct, mod)
        gens = octave_generators(ph, ga, theta)
        gens_all.append(gens)
        E = np.eye(8, dtype=complex)
        for G in gens:
            E = expm(G) @ E
        oct_blocks.append(E)
    F = np.eye(N, dtype=complex)
    if composition == 'seq' and n_oct >= 2:
        for k in range(n_oct):
            idx = [(7 * k + l) % N for l in range(8)]
            for G in gens_all[k]:
                B = expm(G)
                F[idx, :] = B @ F[idx, :]
    elif composition == 'seq':        # n_oct == 1: fold local 7 onto node 0
        for G8 in gens_all[0]:
            G = np.zeros((N, N), dtype=complex)
            idx = np.array([l % N for l in range(8)])
            np.add.at(G, (idx[:, None], idx[None, :]), G8)
            F = expm(G) @ F
    elif composition == 'sync':
        for b in range(4):
            G = np.zeros((N, N), dtype=complex)
            for k in range(n_oct):
                idx = np.array([(7 * k + l) % N for l in range(8)])
                np.add.at(G, (idx[:, None], idx[None, :]), gens_all[k][b])
            F = expm(G) @ F
    else:
        raise ValueError(composition)
    if mod is not None and np.any(mod['gate_phase']):
        D = np.ones(N, dtype=complex)
        for j in range(n_oct):
            D[7 * j] *= np.exp(1j * mod['gate_phase'][seam_role(j, n_oct)])
        F = D[:, None] * F
    return F, oct_blocks


def whole_modes(oct_blocks, alpha=ALPHA):
    """Each octave's completed whole: leading eigenvector of K8 E8_k."""
    K8 = np.eye(8, dtype=complex)
    for (a, b) in DIAMETERS:
        K8[a, b] = K8[b, a] = alpha
    out = []
    for E in oct_blocks:
        ev, V = np.linalg.eig(K8 @ E)
        i = int(np.argmax(np.abs(ev)))
        out.append(V[:, i] / np.linalg.norm(V[:, i]))
    return out


# ============================================================ scale maps

def R_dec(Nc, Nf):
    return v20.R_windows(Nc, Nf, [[1.0]], stride=7, offset=0, ring=True)


def R_whole_mod(Nc, Nf, psis):
    """Coarse node c <- completed fine octave c-1 projected on its own whole."""
    n_f = len(psis)
    W = np.array([np.conj(psis[(c - 1) % n_f]) for c in range(Nc)])
    return v20.R_windows(Nc, Nf, W, stride=7, offset=-7, ring=True)


def R_unif(Nc, Nf):
    return v20.R_windows(Nc, Nf, [np.ones(8) / np.sqrt(8)], stride=7,
                         offset=-7, ring=True)


def coisometric(R):
    """Same row space, orthonormal rows: (R R^dag)^(-1/2) R."""
    w, U = np.linalg.eigh(R @ np.conj(R.T))
    return (U * (1 / np.sqrt(w))) @ np.conj(U.T) @ R


# ============================================================ fast family optimizer

def family_entries(Nc, Nf, window, period, offset, stride=7):
    """Entry list of the window family: entry e = (coarse c, fine f) with
    parameter index p = (c mod period) * window + l. period = Nc gives the
    per-node family (every coarse node its own weights)."""
    c_e, f_e, p_e = [], [], []
    for c in range(Nc):
        for l in range(window):
            c_e.append(c)
            f_e.append((stride * c + offset + l) % Nf)
            p_e.append((c % period) * window + l)
    return (np.array(c_e), np.array(f_e), np.array(p_e), period * window)


def fast_family(entries, A, B, nphi=72):
    """Exact-in-weights optimum of the normalized defect over the family
    R(w) = sum_p w_p E_p (E_p = sum of its single entries), global phase by
    scan + refinement. Uses entry-level Gram identities:
      <X_e, X_e'> = [c_e = c_e'] conj(A A^dag)[f_e, f_e'],
      <Y_e, Y_e'> = [f_e = f_e'] (B^dag B)[c_e, c_e'],
      <X_e, Y_e'> = conj(A[f_e, f_e']) B[c_e, c_e'],
    with X_e = E_e A, Y_e = B E_e. Returns (delta, R_opt)."""
    c_e, f_e, p_e, n_par = entries
    AAH = A @ np.conj(A.T)
    BHB = np.conj(B.T) @ B
    XXe = (c_e[:, None] == c_e[None, :]) * np.conj(AAH[np.ix_(f_e, f_e)])
    YYe = (f_e[:, None] == f_e[None, :]) * BHB[np.ix_(c_e, c_e)]
    XYe = np.conj(A[np.ix_(f_e, f_e)]) * B[np.ix_(c_e, c_e)]
    S = np.zeros((len(c_e), n_par))
    S[np.arange(len(c_e)), p_e] = 1.0
    XX = S.T @ XXe @ S
    YY = S.T @ YYe @ S
    XY = S.T @ XYe @ S
    D = XX + YY
    D = (D + np.conj(D.T)) / 2
    D += 1e-13 * np.eye(n_par) * np.trace(D).real / n_par

    def solve(phi):
        c = np.exp(1j * phi)
        M = XX + YY - c * XY - np.conj(c) * np.conj(XY.T)
        M = (M + np.conj(M.T)) / 2
        ev, V = eigh(M, D, subset_by_index=[0, 0])
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
    Nc, Nf = B.shape[0], A.shape[0]
    R = np.zeros((Nc, Nf), dtype=complex)
    np.add.at(R, (c_e, f_e), w[p_e])
    return float(np.sqrt(max(best[0], 0.0))), R


def family_grams(entries, A, B):
    """Parameter-level Gram blocks (XX, YY, XY) of a window family."""
    c_e, f_e, p_e, n_par = entries
    AAH = A @ np.conj(A.T)
    BHB = np.conj(B.T) @ B
    XXe = (c_e[:, None] == c_e[None, :]) * np.conj(AAH[np.ix_(f_e, f_e)])
    YYe = (f_e[:, None] == f_e[None, :]) * BHB[np.ix_(c_e, c_e)]
    XYe = np.conj(A[np.ix_(f_e, f_e)]) * B[np.ix_(c_e, c_e)]
    S = np.zeros((len(c_e), n_par))
    S[np.arange(len(c_e)), p_e] = 1.0
    return S.T @ XXe @ S, S.T @ YYe @ S, S.T @ XYe @ S


def constrained_family(entries, A, B, window, nphi=36, sweeps=60, w0=None,
                       rng=None):
    """Family optimum with every coarse row kept at unit norm (a genuine
    coarse-graining: no coarse node may be dropped). Each weight block (one
    per coarse node for the per-node family, one per residue class for the
    station-dependent family) has unit norm, so ||R||^2 = N_c and for unitary
    A, B the defect is delta^2 = 1 - |w^dag H w| / N_c with H = XY^dag.
    Maximized by block-wise majorize-maximize ascent at each global phase
    (each step solves max over the unit sphere of a convex minorant), from the
    given start and two random starts. Returns (delta, R)."""
    c_e, f_e, p_e, n_par = entries
    Nc, Nf = B.shape[0], A.shape[0]
    XX, YY, XY = family_grams(entries, A, B)
    H = np.conj(XY.T)                       # <Y(w), X(w)> = w^dag H w
    nb = n_par // window
    blocks = [slice(b * window, (b + 1) * window) for b in range(nb)]
    rng = np.random.default_rng(0) if rng is None else rng

    def normalize(w):
        w = w.copy()
        for b, sl in enumerate(blocks):
            n = np.linalg.norm(w[sl])
            w[sl] = w[sl] / n if n > 0 else rng.normal(size=window) / np.sqrt(window)
        return w

    def objective(w):
        return abs(np.conj(w) @ H @ w)

    def ascend(K, w):
        sig = [max(0.0, -np.linalg.eigvalsh(K[sl, sl])[0]) + 1e-9 for sl in blocks]
        for _ in range(sweeps):
            for b, sl in enumerate(blocks):
                g = K[sl, :] @ w             # includes the block's own term
                v = g + sig[b] * w[sl]
                n = np.linalg.norm(v)
                if n > 0:
                    w[sl] = v / n
        return w

    starts = []
    if w0 is not None:
        starts.append(normalize(np.asarray(w0, dtype=complex)))
    for _ in range(2):
        starts.append(normalize(rng.normal(size=n_par) + 1j * rng.normal(size=n_par)))
    best = (-1.0, None)
    for phi in np.linspace(0, 2 * np.pi, nphi, endpoint=False):
        c = np.exp(1j * phi)
        K = (np.conj(c) * H + c * np.conj(H.T)) / 2
        for w in starts:
            w = ascend(K, w.copy())
            val = objective(w)
            if val > best[0]:
                best = (val, w.copy())
    w = best[1]
    R = np.zeros((Nc, Nf), dtype=complex)
    np.add.at(R, (c_e, f_e), w[p_e])
    # report the exact phase-optimized defect of this R (valid for T as well)
    return defect(R @ A, B @ R), R


# ============================================================ experiment config

RNG_SEED = 20261021
M_LIST = list(range(1, 9))
SEARCH_SEED = 2101
SEARCH_BOUNDS = ([(-np.pi, np.pi)] * 7 + [(0.0, 2.0)] * 7 + [(-np.pi, np.pi)] * 7
                 + [(0.0, 2.0)] * 7 + [(-np.pi, np.pi)] * 7)

# Results of the committed --optimize run (v21_optimize_output.txt): the best
# 35-parameter modulation found (order: close_phase, close_gain, open_phase,
# open_gain, gate_phase; each indexed by role 0..6) and the search summary.
BEST_VEC = [-0.495932, -0.410785, -1.668735, -0.604646, -0.408764, -0.919452, -0.65052, 1.332635, 1.411935, 1.132559, 1.350686, 1.516123, 1.54442, 1.386543, 0.004847, 0.039781, -0.088732, -0.158371, -0.061119, 0.209888, 0.253927, 1.297393, 1.032094, 1.151107, 1.218821, 1.325976, 1.17805, 1.233755, -2.516864, -0.28746, 0.290544, -0.496894, -1.717017, -1.840208, -2.134552]
SEARCH_SUMMARY = {'stage1': {'canonical': (0.6419, 0.5735), 'role strokes': (0.6732, 0.5867), 'role gates': (0.6513, 0.5775), 'random 0': (0.6382, 0.6389), 'random 1': (0.6759, 0.5973), 'random 2': (0.651, 0.617)}, 'stage2': ('canonical', 0.7269, 0.6998), 'capacity': [(0.5443, 0.507, 0.6932), (0.717, 0.6319, 0.7863), (0.7311, 0.6169, 0.7532)]}


def hr(title):
    print()
    print('=' * 78)
    print(title)
    print('=' * 78)


def fmt_row(vals, w=6, p=3):
    return ' '.join(f'{v:>{w}.{p}f}' for v in vals)


def all_mods():
    mods = {'homogeneous': None, 'role strokes': role_stroke_mod(),
            'role gates': role_gate_mod()}
    if BEST_VEC is not None:
        mods['best (search)'] = vec_to_mod(BEST_VEC)
    return mods


@functools.lru_cache(maxsize=None)
def get_pair(L, mod_name, comp='seq'):
    """Fine ring (7^L octaves) and coarse ring (7^(L-1)), same construction."""
    mod = all_mods()[mod_name]
    nf, nc = 7 ** L, 7 ** (L - 1)
    Ff, blocks = build_ring(nf, mod, comp)
    Fc, _ = build_ring(nc, mod, comp)
    return dict(Ff=Ff, Fc=Fc, Tf=ring_kappa(nf) @ Ff, Tc=ring_kappa(nc) @ Fc,
                Nf=7 * nf, Nc=7 * nc, nf=nf, nc=nc, psis=whole_modes(blocks))


def corpus_maps(P):
    return dict(R_dec=R_dec(P['Nc'], P['Nf']),
                R_whole=R_whole_mod(P['Nc'], P['Nf'], P['psis']),
                R_unif=R_unif(P['Nc'], P['Nf']))


def curve_iter(R, A, B, m_list):
    """delta(m) without storing powers: X = R A^m by repeated right-multiply."""
    out, X, done = [], R.astype(complex), 0
    Y = B @ R
    for m in m_list:
        while done < m:
            X = X @ A
            done += 1
        out.append(defect(X, Y))
    return np.array(out)


def weights_from_R(R, entries):
    c_e, f_e, p_e, n_par = entries
    w = np.zeros(n_par, dtype=complex)
    w[p_e] = R[c_e, f_e]
    return w


def ceilings(P, A, B, window, period, nphi_u=48, nphi_c=36):
    """(unconstrained, constrained, row-normalized) family ceilings, plus the
    unconstrained and constrained optimal maps."""
    ent = family_entries(P['Nc'], P['Nf'], window, period, -7)
    du, Ru = fast_family(ent, A, B, nphi=nphi_u)
    rn = np.linalg.norm(Ru, axis=1)
    Rn = Ru / np.where(rn > 0, rn, 1)[:, None]
    dn = defect(Rn @ A, B @ Rn)
    dc, Rc = constrained_family(ent, A, B, window, nphi=nphi_c,
                                w0=weights_from_R(Ru, ent))
    return du, dc, dn, Ru, Rc


def leakage_split(R, A, B):
    """Exact identity for the co-isometric version of R (same row space):
    delta^2 = 1 - |<B, M>| / N_c with M = R_iso A R_iso^dag; leak^2 =
    1 - ||M||^2 / N_c; floor delta >= sqrt(1 - sqrt(1 - leak^2))."""
    Ri = coisometric(R)
    Nc = B.shape[0]
    M = Ri @ A @ np.conj(Ri.T)
    leak = np.sqrt(max(0.0, 1 - np.linalg.norm(M) ** 2 / Nc))
    ov = abs(np.vdot(B, M))
    d_id = np.sqrt(max(0.0, 1 - ov / Nc))
    d_dir = defect(Ri @ A, B @ Ri)
    cos = ov / (np.linalg.norm(B) * np.linalg.norm(M))
    floor = np.sqrt(max(0.0, 1 - np.sqrt(max(0.0, 1 - leak ** 2))))
    return leak, cos, d_dir, d_id, floor


# ============================================================ E0

def E0_instruments():
    hr('E0  INSTRUMENTS AND VERIFICATION')
    ok = True
    for n in (1, 2, 7):
        d1 = np.abs(build_ring(n, canonical_mod(), 'seq')[0]
                    - tops.StaggeredOperator.ring(n, alpha=ALPHA).F).max()
        d2 = np.abs(build_ring(n, canonical_mod(), 'sync')[0] - v20.sync_ring(n)[0]).max()
        ok &= d1 < 1e-12 and d2 < 1e-12
        print(f'  canonical modulation, n = {n}: seq vs StaggeredOperator.ring {d1:.1e};'
              f' sync vs v20/v16 sync ring {d2:.1e}')
    Ff, _, _ = v20.sync_ring(14)
    Fc, _, _ = v20.sync_ring(2)
    A4 = np.linalg.matrix_power(Ff, 4)
    for lab, W, Pp in (('TC w8', 8, 1), ('SD w8', 8, 7)):
        d_old, _ = v20.optimize_family(v20.family_basis(14, 98, W, Pp, -7), A4, Fc)
        d_new, _ = fast_family(family_entries(14, 98, W, Pp, -7), A4, Fc)
        ok &= abs(d_old - d_new) < 1e-6
        print(f'  fast family optimizer vs v20 ({lab}, v20 sync ring n_c=2, m=4): '
              f'{d_new:.6f} vs {d_old:.6f}')
    for lab, W in (('SD w8', 8), ('SD w15', 15)):
        ent = family_entries(14, 98, W, 7, -7)
        du, Ru = fast_family(ent, A4, Fc)
        rn = np.linalg.norm(Ru, axis=1)
        dn = defect((Ru / rn[:, None]) @ A4, Fc @ (Ru / rn[:, None]))
        dc, Rc = constrained_family(ent, A4, Fc, W, w0=weights_from_R(Ru, ent))
        good = du - 1e-9 <= dc <= dn + 1e-9
        ok &= good
        print(f'  v20 F6 case, {lab} (sync n_c=2, m=4): unconstrained {du:.3f} <= constrained '
              f'{dc:.3f} <= row-normalized {dn:.3f}  {"ok" if good else "FAIL"};  unconstrained '
              f'optimum has {int(np.sum(rn < 0.1 * rn.max()))} of {len(rn)} rows below 10% '
              f'(min {rn.min() / rn.max():.3f})')
    roles = ''.join(str(seam_role(j, 49)) for j in range(49))
    print('  seam roles on the 49-octave ring (seam j = 0..48, grouped by 7): '
          + ' '.join(roles[i:i + 7] for i in range(0, 49, 7)))
    print(f'  all instrument checks: {"PASS" if ok else "FAIL"}')
    return ok


# ============================================================ E1

def E1_construction():
    hr("E1  THE CONSTRUCTION, AND WHETHER V20'S OBSTRUCTIONS STILL APPLY")
    print('  role d: ' + '  '.join(f'{d}={ROLE_NAMES[d]}(i^{ROLE_STROKE[d]})'
                                   for d in range(7)))
    print('  role strokes: the octave closing into role d uses beat-4 stroke i^s(d) '
          '(canon i^0); role gates: seam phase i^s(d) once per cycle.')
    print('  relative non-invariance ||U F U^dag - F|| / ||F|| on the 49-octave ring '
          '(U = 1-octave and 7-octave shifts):')
    for comp in ('sync', 'seq'):
        for name in ('homogeneous', 'role strokes', 'role gates'):
            F = get_pair(2, name, comp)['Ff']
            N = F.shape[0]
            U1 = np.roll(np.eye(N), 7, axis=0)
            U7 = np.roll(np.eye(N), 49, axis=0)
            r1 = np.linalg.norm(U1 @ F @ U1.T - F) / np.linalg.norm(F)
            r7 = np.linalg.norm(U7 @ F @ U7.T - F) / np.linalg.norm(F)
            print(f'    {comp:<4} {name:<13} 1-octave {r1:.3e}   7-octave {r7:.3e}')
    print('  v20 Theorem 1 needs exact octave invariance and Theorem 2 needs a lattice '
          'momentum: the modulation removes both preconditions.')
    print('  conservation (|l1| - 1)/alpha, fine and coarse (seq):')
    for name in ('homogeneous', 'role strokes', 'role gates'):
        P = get_pair(2, name, 'seq')
        lf = np.abs(np.linalg.eigvals(P['Tf'])).max()
        lc = np.abs(np.linalg.eigvals(P['Tc'])).max()
        print(f'    {name:<13} {(lf - 1) / ALPHA:.4f}  {(lc - 1) / ALPHA:.4f}')


# ============================================================ E2

def E2_corpus_maps():
    hr('E2  CORPUS SCALE MAPS ON THE MODULATED CHAIN: delta(m), m = 1..8')
    print(f'  {"L":<2} {"comp":<5} {"modulation":<13} {"R":<8} {"op":<3} '
          + ' '.join(f'{m:>6d}' for m in M_LIST))
    curves = {}
    for L, comps in ((2, ('seq', 'sync')), (1, ('seq',))):
        for comp in comps:
            for name in ('homogeneous', 'role strokes', 'role gates'):
                P = get_pair(L, name, comp)
                for rn, R in corpus_maps(P).items():
                    for op in ('F', 'T'):
                        if L == 1 and op == 'T':
                            continue
                        dc = v20.defect_curve(R, P[op + 'f'], P[op + 'c'])
                        curves[(L, comp, name, rn, op)] = dc
                        print(f'  {L:<2} {comp:<5} {name:<13} {rn:<8} {op:<3} {fmt_row(dc)}')
    print('  depth L = 3 (fine 343 octaves, 2401 nodes -> coarse 49 octaves), seq, F, m = 4, 8:')
    for name in ('homogeneous', 'role strokes', 'role gates'):
        P = get_pair(3, name, 'seq')
        cells = []
        for rn, R in corpus_maps(P).items():
            if rn == 'R_unif':
                continue
            d = curve_iter(R, P['Ff'], P['Fc'], [4, 8])
            curves[(3, 'seq', name, rn, 'F')] = d
            cells.append(f'{rn} {d[0]:.3f} {d[1]:.3f}')
        print(f'    {name:<13} ' + '   '.join(cells))
    return curves


# ============================================================ E3

def random_mod(rng):
    v = mod_to_vec(canonical_mod())
    v[0:7] = rng.uniform(-np.pi, np.pi, 7)
    v[7:14] = rng.uniform(0.5, 1.5, 7)
    v[14:21] = rng.uniform(-np.pi, np.pi, 7)
    v[21:28] = rng.uniform(0.5, 1.5, 7)
    v[28:35] = rng.uniform(-np.pi, np.pi, 7)
    return vec_to_mod(v)


def E3_nulls(curves, n_draw=200, n_mod=30):
    hr(f'E3  NULLS FOR THE CORPUS MAPS (L = 2, seq; {n_draw} draws per family)')
    print('  pct = fraction of null draws with defect <= the corpus value')
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for name in ('role strokes', 'role gates'):
        P = get_pair(2, name, 'seq')
        Nf, Nc = P['Nf'], P['Nc']
        Pw = v20.powers(P['Ff'], 8)
        Fc = P['Fc']

        def curve(R):
            return np.array([defect(R @ Pw[m], Fc @ R) for m in M_LIST])

        N1 = np.array([curve(v20.haar_coisometry(Nc, Nf, rng)) for _ in range(n_draw)])
        N2 = []
        for _ in range(n_draw):
            sel = np.sort(rng.choice(Nf, size=Nc, replace=False))
            R = np.zeros((Nc, Nf))
            R[np.arange(Nc), sel] = 1.0
            N2.append(curve(R))
        N2 = np.array(N2)
        N3 = np.array([curve(v20.R_windows(Nc, Nf, [[1.0]], 7, s, True)) for s in range(1, 7)])
        N4 = np.array([curve(v20.R_windows(Nc, Nf, [rng.normal(size=8) + 1j * rng.normal(size=8)],
                                           7, -7, True)) for _ in range(n_draw)])
        print(f'\n  [{name}]  m:              ' + ' '.join(f'{m:>6d}' for m in M_LIST))
        print(f'  Haar co-isometry  mean    {fmt_row(N1.mean(0))}   min {N1.min():.3f}')
        print(f'  random decimation mean    {fmt_row(N2.mean(0))}   min {N2.min():.3f}')
        print(f'  random weights    mean    {fmt_row(N4.mean(0))}   min {N4.min():.3f}')
        for rn, nulls in (('R_dec', [N1, N2, N3]), ('R_whole', [N1, N4]), ('R_unif', [N1, N4])):
            dc = curves[(2, 'seq', name, rn, 'F')]
            pct = np.array([[float(np.mean(nl[:, k] <= dc[k])) for k in range(8)]
                            for nl in nulls]).max(0)
            print(f'  {rn:<8} corpus   {fmt_row(dc)}')
            print(f'  {"":<8} max pct  {fmt_row(pct, p=2)}')
            for k, m in enumerate(M_LIST):
                rows.append((name, rn, m, dc[k], pct[k]))
    print(f'\n  random-modulation null ({n_mod} random 35-parameter modulations, L = 2, seq):')
    stats = {'R_dec m4': [], 'R_dec m8': [], 'R_whole m4': [], 'R_whole m8': [], 'SD7c m4': []}
    t0 = time.time()
    for _ in range(n_mod):
        mod = random_mod(rng)
        Ff, blocks = build_ring(49, mod, 'seq')
        Fc, _ = build_ring(7, mod, 'seq')
        P = dict(Nf=343, Nc=49, psis=whole_modes(blocks))
        Rs = corpus_maps(P)
        A4 = np.linalg.matrix_power(Ff, 4)
        A8 = A4 @ A4
        for rn in ('R_dec', 'R_whole'):
            stats[f'{rn} m4'].append(defect(Rs[rn] @ A4, Fc @ Rs[rn]))
            stats[f'{rn} m8'].append(defect(Rs[rn] @ A8, Fc @ Rs[rn]))
        ent = family_entries(49, 343, 8, 7, -7)
        _, Ru = fast_family(ent, A4, Fc, nphi=36)
        dcons, _ = constrained_family(ent, A4, Fc, 8, nphi=24, w0=weights_from_R(Ru, ent))
        stats['SD7c m4'].append(dcons)
    for k, v in stats.items():
        v = np.array(v)
        print(f'    {k:<11} mean {v.mean():.3f} +/- {v.std():.3f}   min {v.min():.3f}')
    print(f'    [{time.time() - t0:.0f}s]')
    return rows, stats


# ============================================================ E4

def E4_ceilings():
    hr('E4  FAMILY CEILINGS (L = 2, seq): unconstrained / CONSTRAINED / row-normalized')
    print('  constrained = every coarse row at unit norm (no coarse node dropped); the honest '
          'ceiling, bracketed by the other two.')
    print('  TC = translation-covariant window (8 weights); SD7 = station-dependent (56); '
          'PN = per-node windows (392)')
    res = {}
    for name in ('homogeneous', 'role strokes', 'role gates'):
        P = get_pair(2, name, 'seq')
        for m in (1, 4, 8):
            A = np.linalg.matrix_power(P['Ff'], m)
            cells = []
            for fam, W, Pp in (('TC', 8, 1), ('SD7', 8, 7), ('PN', 8, P['Nc'])):
                if fam == 'PN' and m != 4:
                    continue
                du, dc, dn, _, _ = ceilings(P, A, P['Fc'], W, Pp)
                res[(name, fam, m)] = (du, dc, dn)
                cells.append(f'{fam} {du:.3f}/{dc:.3f}/{dn:.3f}')
            print(f'    {name:<13} m={m}: ' + '   '.join(cells))
    print('\n  same-geometry null under the constraint: random 8x8 octave blocks (seq rings, '
          'same block at both scales), SD7 constrained, m = 4:')
    rng = np.random.default_rng(RNG_SEED + 4)
    E8c = v20.canonical_octave_block()
    for n_f, n_c, tag in ((14, 2, 'v20 size, fine 14 -> coarse 2 octaves'),
                          (49, 7, 'v21 size, fine 49 -> coarse 7 octaves')):
        Nf, Nc = 7 * n_f, 7 * n_c
        ent = family_entries(Nc, Nf, 8, 7, -7)

        def ceiling_of(E8, gates=False):
            Ffr = v20.seq_ring_from_block(n_f, E8)
            Fcr = v20.seq_ring_from_block(n_c, E8)
            if gates:
                for F, n in ((Ffr, n_f), (Fcr, n_c)):
                    for j in range(n):
                        F[7 * j, :] *= 1j ** ROLE_STROKE[seam_role(j, n)]
            A = np.linalg.matrix_power(Ffr, 4)
            _, Ru = fast_family(ent, A, Fcr, nphi=36)
            return constrained_family(ent, A, Fcr, 8, nphi=24, w0=weights_from_R(Ru, ent))[0]

        canon = ceiling_of(E8c)
        draws = np.array([ceiling_of(v20.haar_unitary(8, rng)) for _ in range(30)])
        line = (f'    {tag}: canonical {canon:.3f}; random blocks {draws.mean():.3f} +/- '
                f'{draws.std():.3f} (min {draws.min():.3f}); canonical pct '
                f'{float(np.mean(draws <= canon)):.2f}')
        if n_f == 49:
            canon_g = ceiling_of(E8c, gates=True)
            draws_g = np.array([ceiling_of(v20.haar_unitary(8, rng), gates=True)
                                for _ in range(15)])
            line += (f'\n    {tag}, with role gates: canonical {canon_g:.3f}; random blocks '
                     f'{draws_g.mean():.3f} +/- {draws_g.std():.3f}; pct '
                     f'{float(np.mean(draws_g <= canon_g)):.2f}')
        print(line)
    return res


# ============================================================ E5

def search_objective(v, target_E8=None, constrained=False, nphi=36):
    """Inner objective of the modulation search: SD7 family ceiling at L = 2,
    m = 4, seq; coarse target = the same construction (or, for the capacity
    null, a ring of a different, random octave block)."""
    mod = vec_to_mod(v)
    Ff, _ = build_ring(49, mod, 'seq')
    A = np.linalg.matrix_power(Ff, 4)
    if target_E8 is None:
        Fc, _ = build_ring(7, mod, 'seq')
    else:
        Fc = v20.seq_ring_from_block(7, target_E8)
    ent = family_entries(49, 343, 8, 7, -7)
    du, Ru = fast_family(ent, A, Fc, nphi=nphi)
    if not constrained:
        return du
    return constrained_family(ent, A, Fc, 8, nphi=24, w0=weights_from_R(Ru, ent))[0]


def run_search():
    """The committed modulation search (--optimize). Stage 1: unconstrained SD7
    ceiling, Powell from three corpus starts and three random starts. Stage 2:
    constrained ceiling, Powell refinement from the best stage-1 point.
    Capacity null: stage 1 against coarse targets built from three random
    octave blocks (canonical start), then the constrained value there."""
    from scipy.optimize import minimize
    rng = np.random.default_rng(SEARCH_SEED)
    v0 = mod_to_vec(canonical_mod())
    lo = np.array([b[0] for b in SEARCH_BOUNDS])
    hi = np.array([b[1] for b in SEARCH_BOUNDS])
    starts = {'canonical': v0, 'role strokes': mod_to_vec(role_stroke_mod()),
              'role gates': mod_to_vec(role_gate_mod())}
    for i in range(3):
        r = v0.copy()
        r[0:7] = rng.uniform(-np.pi, np.pi, 7)
        r[14:21] = rng.uniform(-np.pi, np.pi, 7)
        r[28:35] = rng.uniform(-np.pi, np.pi, 7)
        r[7:14] = rng.uniform(0.5, 1.5, 7)
        r[21:28] = rng.uniform(0.5, 1.5, 7)
        starts[f'random {i}'] = r
    opts = dict(maxfev=1200, xtol=1e-3, ftol=1e-4)
    stage1 = {}
    for name, x0 in starts.items():
        # phases are 2pi-periodic: wrap into the search box (3pi/2 -> -pi/2)
        x0 = x0.copy()
        for blk in (0, 2, 4):
            x0[7 * blk:7 * blk + 7] = (x0[7 * blk:7 * blk + 7] + np.pi) % (2 * np.pi) - np.pi
        x0 = np.clip(x0, lo, hi)
        t0 = time.time()
        res = minimize(search_objective, x0, method='Powell', bounds=SEARCH_BOUNDS, options=opts)
        d_start = search_objective(x0, nphi=72)
        d_best = search_objective(res.x, nphi=72)
        stage1[name] = (d_start, d_best, res.x)
        print(f'  stage 1 [{name:<12}] unconstrained {d_start:.4f} -> {d_best:.4f} '
              f'({res.nfev} evals, {time.time() - t0:.0f}s)', flush=True)
    best_name = min(stage1, key=lambda k: stage1[k][1])
    x1 = stage1[best_name][2]
    t0 = time.time()
    c_start = search_objective(x1, constrained=True)
    res2 = minimize(lambda v: search_objective(v, constrained=True), x1, method='Powell',
                    bounds=SEARCH_BOUNDS, options=dict(maxfev=300, xtol=1e-3, ftol=1e-4))
    c_best = search_objective(res2.x, constrained=True)
    print(f'  stage 2 [from {best_name}] constrained {c_start:.4f} -> {c_best:.4f} '
          f'({res2.nfev} evals, {time.time() - t0:.0f}s)', flush=True)
    cap = []
    for i in range(3):
        E8 = v20.haar_unitary(8, rng)
        t0 = time.time()
        d_start = search_objective(v0, target_E8=E8, nphi=72)
        res = minimize(lambda v: search_objective(v, target_E8=E8), v0, method='Powell',
                       bounds=SEARCH_BOUNDS, options=opts)
        d_best = search_objective(res.x, target_E8=E8, nphi=72)
        c_val = search_objective(res.x, target_E8=E8, constrained=True)
        cap.append((d_start, d_best, c_val))
        print(f'  capacity null [random target {i}] unconstrained {d_start:.4f} -> {d_best:.4f}; '
              f'constrained at optimum {c_val:.4f} ({res.nfev} evals, {time.time() - t0:.0f}s)',
              flush=True)
    print('\n  BEST_VEC = ' + repr([round(float(x), 6) for x in res2.x]))
    summary = dict(stage1={k: (round(v[0], 4), round(v[1], 4)) for k, v in stage1.items()},
                   stage2=(best_name, round(c_start, 4), round(c_best, 4)),
                   capacity=[tuple(round(x, 4) for x in c) for c in cap])
    print('  SEARCH_SUMMARY = ' + repr(summary))
    return res2.x, summary


def E5_best_modulation():
    hr('E5  THE BEST SEAM MODULATION (35-parameter search, committed in --optimize)')
    if BEST_VEC is None:
        print('  (no committed search; run with --optimize)')
        return {}
    s = SEARCH_SUMMARY
    print('  stage 1 (unconstrained SD7 ceiling, L = 2, m = 4), start -> best:')
    for k, (a, b) in s['stage1'].items():
        print(f'    {k:<13} {a:.4f} -> {b:.4f}')
    print(f'  stage 2 (constrained, from {s["stage2"][0]}): {s["stage2"][1]:.4f} -> '
          f'{s["stage2"][2]:.4f}')
    print('  capacity null (same search, coarse target from a random octave block): '
          + '; '.join(f'{a:.4f} -> {b:.4f} (constrained {c:.4f})' for a, b, c in s['capacity']))
    m = vec_to_mod(BEST_VEC)
    print('  best modulation (per role 0..6):')
    for k in MOD_KEYS:
        vals = m[k] / np.pi if 'phase' in k else m[k]
        unit = ' pi' if 'phase' in k else ''
        print(f'    {k:<11} ' + ' '.join(f'{x:+.3f}' for x in vals) + unit)
    out = {}
    P = get_pair(2, 'best (search)', 'seq')
    for rn, R in corpus_maps(P).items():
        for op in ('F', 'T'):
            dc = v20.defect_curve(R, P[op + 'f'], P[op + 'c'])
            out[(rn, op)] = dc
            print(f'  L=2 seq {rn:<8} {op}  {fmt_row(dc)}')
    for mm in (1, 4, 8):
        A = np.linalg.matrix_power(P['Ff'], mm)
        du, dc, dn, _, _ = ceilings(P, A, P['Fc'], 8, 7)
        out[('SD7', mm)] = (du, dc, dn)
        line = f'  L=2 seq m={mm}: SD7 {du:.3f}/{dc:.3f}/{dn:.3f}'
        if mm == 4:
            du2, dc2, dn2, _, _ = ceilings(P, A, P['Fc'], 8, P['Nc'])
            out[('PN', mm)] = (du2, dc2, dn2)
            line += f'   PN {du2:.3f}/{dc2:.3f}/{dn2:.3f}'
        print(line + '   (unconstrained/constrained/row-normalized)')
    for L in (1, 3):
        P = get_pair(L, 'best (search)', 'seq')
        A = np.linalg.matrix_power(P['Ff'], 4)
        du, dc, dn, _, _ = ceilings(P, A, P['Fc'], 8, 7)
        Rd = corpus_maps(P)['R_dec']
        d_dec = defect(Rd @ A, P['Fc'] @ Rd)
        out[('L', L)] = (du, dc, dn, d_dec)
        print(f'  L={L} seq m=4: SD7 {du:.3f}/{dc:.3f}/{dn:.3f};  R_dec {d_dec:.3f}')
    P = get_pair(2, 'best (search)', 'sync')
    A = np.linalg.matrix_power(P['Ff'], 4)
    du, dc, dn, _, _ = ceilings(P, A, P['Fc'], 8, 7)
    print(f'  L=2 sync m=4: SD7 {du:.3f}/{dc:.3f}/{dn:.3f}')
    return out


# ============================================================ E6

def E6_leakage():
    hr('E6  THE LEAKAGE IDENTITY: WHY NO LOCAL COARSE-GRAINING WORKS')
    print('  For a co-isometric R with row space V and M = R F^m R^dag (the compressed')
    print('  fine dynamics): delta^2 = 1 - |<F_c, M>| / N_c, and since |<F_c, M>| <=')
    print('  sqrt(N_c) ||M|| = N_c sqrt(1 - leak^2), delta >= sqrt(1 - sqrt(1 - leak^2)).')
    print('  Self-similarity needs BOTH leak -> 0 (V invariant) AND M -> c F_c.')
    print(f'  {"modulation":<14} {"R (m=4)":<12} {"leak":>6} {"cos(M,Fc)":>10} {"delta":>7} '
          f'{"identity":>9} {"floor":>7}')
    names = ['homogeneous', 'role strokes'] + (['best (search)'] if BEST_VEC is not None else [])
    worst = 0.0
    for name in names:
        P = get_pair(2, name, 'seq')
        A = np.linalg.matrix_power(P['Ff'], 4)
        maps = corpus_maps(P)
        _, _, _, _, Rsd = ceilings(P, A, P['Fc'], 8, 7)
        _, _, _, _, Rpn = ceilings(P, A, P['Fc'], 8, P['Nc'])
        for rn, R in (('R_dec', maps['R_dec']), ('R_whole', maps['R_whole']),
                      ('SD7 constr', Rsd), ('PN constr', Rpn)):
            leak, cos, dd, did, fl = leakage_split(R, A, P['Fc'])
            worst = max(worst, abs(dd - did))
            print(f'  {name:<14} {rn:<12} {leak:>6.3f} {cos:>10.3f} {dd:>7.3f} {did:>9.3f} {fl:>7.3f}')
    print(f'  identity check: max |delta - sqrt(1 - |<F_c,M>|/N_c)| = {worst:.1e}')


def E6b_locality():
    hr('E6b LOCALITY OF THE COARSE GENERATOR (why slow seams would not help either)')
    from scipy.linalg import logm
    print('  Octaves coupled only through shared tonics generate, at leading order in a weak')
    print('  seam coupling, a coarse dynamics with nearest-neighbor generator. Share of the')
    print('  squared Frobenius weight of the principal log of the coarse operator, by the')
    print('  ring distance between the stations it couples:')
    F8 = tops.build_F_8D()
    G8 = logm(F8)
    d8 = np.abs(np.arange(8)[:, None] - np.arange(8)[None, :])
    tot = np.linalg.norm(G8) ** 2
    print('    single octave log F8:   ' + '   '.join(
        f'{lab} {np.linalg.norm(G8[msk]) ** 2 / tot:.3f}'
        for lab, msk in (('d=0', d8 == 0), ('d=1', d8 == 1), ('d>=2', d8 >= 2))))
    for name in ('homogeneous', 'role strokes'):
        Fc = get_pair(2, name, 'seq')['Fc']
        N = Fc.shape[0]
        Gc = logm(Fc)
        dd = np.abs(np.arange(N)[:, None] - np.arange(N)[None, :])
        dd = np.minimum(dd, N - dd)
        tot = np.linalg.norm(Gc) ** 2
        print(f'    7-octave coarse ring ({name}): ' + '   '.join(
            f'{lab} {np.linalg.norm(Gc[msk]) ** 2 / tot:.3f}'
            for lab, msk in (('d=0', dd == 0), ('d=1', dd == 1), ('d=2-3', (dd >= 2) & (dd <= 3)),
                             ('d>=4', dd >= 4))))


# ============================================================ E7

def E7_attractor():
    hr('E7  THE ATTRACTOR (T leading mode, L = 2, seq)')
    rng = np.random.default_rng(RNG_SEED + 7)
    names = ['homogeneous', 'role strokes', 'role gates'] + (
        ['best (search)'] if BEST_VEC is not None else [])
    for name in names:
        P = get_pair(2, name, 'seq')
        _, pf = v20.leading(P['Tf'])
        _, pc = v20.leading(P['Tc'])
        maps = corpus_maps(P)
        ovs = []
        for rn in ('R_dec', 'R_whole'):
            v = maps[rn] @ pf
            ovs.append(abs(np.vdot(pc, v)) / np.linalg.norm(v))
        ch = [abs(np.vdot(pc, u)) / np.linalg.norm(u) for u in
              (rng.normal(size=(500, P['Nc'])) + 1j * rng.normal(size=(500, P['Nc'])))]
        # phase advance of the attractor between consecutive seams: per fine
        # octave, directly across seven fine octaves (fine seams 7J -> 7J + 7,
        # which R_dec sends to consecutive coarse seams), and per coarse octave
        s_f = pf[0::7]
        s_f7 = pf[0::49]
        s_c = pc[0::7]
        adv_f = np.angle(np.sum(np.conj(s_f) * np.roll(s_f, -1)))
        adv_f7 = np.angle(np.sum(np.conj(s_f7) * np.roll(s_f7, -1)))
        adv_c = np.angle(np.sum(np.conj(s_c) * np.roll(s_c, -1)))
        print(f'  {name:<14} overlap R_dec {ovs[0]:.3f}, R_whole {ovs[1]:.3f} (chance '
              f'{np.mean(ch):.3f} +/- {np.std(ch):.3f})')
        print(f'  {"":<14} seam phase advance: per fine octave {adv_f / np.pi:+.3f} pi; across '
              f'7 fine octaves {adv_f7 / np.pi:+.3f} pi; coarse per coarse octave '
              f'{adv_c / np.pi:+.3f} pi')


# ============================================================ E8

def E8_tensor():
    hr('E8  TENSOR-NESTING NULL (closed form from v20 E8; R contracts the finest factor)')
    F8 = tops.build_F_8D()
    t = [abs(np.trace(np.linalg.matrix_power(F8, k))) / 8 for k in range(9)]
    print('  delta(m) = sqrt(1 - |tr F8^(m-1)/8|^(depth-1)): exact at m = 1, compounding:')
    for depth in (2, 3, 4):
        print(f'    depth {depth}: ' + fmt_row([np.sqrt(max(0.0, 1 - t[m - 1] ** (depth - 1)))
                                               for m in M_LIST]))


# ============================================================ E9

def R_body_closure(n_f, body):
    """Ratio 3.5 ('the point is a process at the next scale'): coarse node 2j is
    the body of fine octave j (its whole-mode on the interior), coarse node
    2j+1 is the octave's closing tonic. Fine closures land on coarse processes
    in even coarse octaves and on coarse structures in odd ones: the parity
    double cover, returning after two coarse octaves (seven fine octaves)."""
    Nf, Nc = 7 * n_f, 2 * n_f
    R = np.zeros((Nc, Nf), dtype=complex)
    for j in range(n_f):
        for l in range(8):
            R[2 * j, (7 * j + l) % Nf] += np.conj(body[l])
        R[2 * j + 1, (7 * j + 7) % Nf] = 1.0
    return R


def entries_body_closure(n_f, W=8):
    """Per-node windows for the ratio-3.5 map: even rows the fine octave, odd
    rows the eight nodes centred on its closing tonic."""
    Nf = 7 * n_f
    c_e, f_e, p_e = [], [], []
    for j in range(n_f):
        for l in range(W):
            c_e.append(2 * j)
            f_e.append((7 * j + l) % Nf)
            p_e.append(2 * j * W + l)
            c_e.append(2 * j + 1)
            f_e.append((7 * j + 4 + l) % Nf)
            p_e.append((2 * j + 1) * W + l)
    return np.array(c_e), np.array(f_e), np.array(p_e), 2 * n_f * W


def E9_720():
    hr('E9  THE 720 TEST: SELF-SIMILARITY OVER TWO SCALE STEPS')
    print('  Ashman (2026-10-16): "the point is a process at the next scale, in the staggered')
    print('  octave model, but then another scale again and it\'s a structure again... that\'s the 720".')
    print('  Reading: one scale step moves a point by 3.5 (a half-integer: process parity), two steps')
    print('  by 7D = R (integer: structure again); the parity double cover of section 27.7t.5, 360')
    print('  degrees flips, 720 restores. v20 and E2-E8 compared scale n with n+1 only.')
    rng = np.random.default_rng(RNG_SEED + 9)
    v20.PSI_WHOLE = v20.whole_mode()
    MS = [1, 2, 3, 4, 5, 6, 7, 8, 16, 49, 64]
    print('\n  (a) attractor arithmetic (canon ring; q* = phase advance per octave):')
    for lab, q in (('q* (measured alpha)', 0.362109515 * np.pi), ('q*_0 (alpha -> 0, v17)', Q_STAR_V17)):
        for tag, den in (('one step, R(q) = 7q  ', 6), ('two steps, R(q) = 49q', 48)):
            grid = 2 * np.pi / den
            k = round(q / grid)
            print(f'    {lab:<23} {tag}: fixed points 2 pi k/{den}; nearest {k * grid / np.pi:.6f} pi, '
                  f'offset {np.degrees(q - k * grid):+.3f} deg')
        k = round((q - np.pi / 6) / (np.pi / 3))
        qs = np.pi / 6 + k * np.pi / 3
        print(f'    {lab:<23} one step with a sign flip (7q = q + pi): nearest {qs / np.pi:.4f} pi, '
              f'offset {np.degrees(q - qs):+.2f} deg')
    print('\n  (b) canon sync ring, fine 98 octaves: one step (to 14 octaves) vs two steps (to 2):')
    Ff, Kf, _ = v20.sync_ring(98)
    F1, _, _ = v20.sync_ring(14)
    F2, K2, _ = v20.sync_ring(2)
    R1 = v20.R_windows(98, 686, [[1.0]], 7, 0, True)
    R2d = v20.R_windows(14, 98, [[1.0]], 7, 0, True) @ R1
    R2w = v20.R_whole(14, 98) @ v20.R_whole(98, 686)
    print(f'    {"m:":<34}' + ' '.join(f'{m:>6d}' for m in MS))
    print(f'    {"one step  R_dec":<34}' + fmt_row(curve_iter(R1, Ff, F1, MS)))
    print(f'    {"two steps R_dec o R_dec":<34}' + fmt_row(curve_iter(R2d, Ff, F2, MS)))
    print(f'    {"two steps R_whole o R_whole":<34}' + fmt_row(curve_iter(R2w, Ff, F2, MS)))
    haar = np.array([curve_iter(v20.haar_coisometry(14, 686, rng), Ff, F2, MS) for _ in range(20)])
    print(f'    {"Haar co-isometry, same shape (mean)":<34}' + fmt_row(haar.mean(0)))
    S = np.roll(np.eye(14), 1, axis=0)
    print(f'    symmetry floor for any translation-covariant two-step projection: '
          f'{np.linalg.norm(S @ F2 @ S.T - F2) / (2 * np.sqrt(28)):.4f}')
    _, pf = v20.leading(Kf @ Ff)
    _, pc = v20.leading(K2 @ F2)
    q_f = np.angle(np.vdot(pf, np.roll(np.eye(686), -7, axis=0) @ pf)) % (2 * np.pi)
    U7c = np.roll(np.eye(14), -7, axis=0)
    Q_c = np.angle(np.vdot(pc, U7c @ pc)) % (2 * np.pi)
    v = R2d @ pf
    proj = (np.eye(14) + np.exp(-1j * Q_c) * U7c) / 2
    ch = [abs(np.vdot(pc, w)) / np.linalg.norm(w)
          for w in (proj @ (rng.normal(size=(14, 400)) + 1j * rng.normal(size=(14, 400)))).T]
    print(f'    attractor on these finite rings: q_f = {q_f / np.pi:.4f} pi, 49 q_f = '
          f'{(49 * q_f) % (2 * np.pi) / np.pi:.4f} pi, level-2 Q_c = {Q_c / np.pi:.4f} pi (coincide by '
          f'rounding); overlap {abs(np.vdot(pc, v)) / np.linalg.norm(v):.3f} vs within-sector chance '
          f'{np.mean(ch):.3f} +/- {np.std(ch):.3f}')
    print('\n  (c) seam-modulated chain, two levels: fine 343 octaves -> 7 octaves (seq, F):')
    names = ['homogeneous', 'role strokes'] + (['best (search)'] if BEST_VEC is not None else [])
    for name in names:
        mod = all_mods()[name]
        Ff3, b3 = build_ring(343, mod, 'seq')
        F31, b31 = build_ring(49, mod, 'seq')
        F32, _ = build_ring(7, mod, 'seq')
        R2d = R_dec(49, 343) @ R_dec(343, 2401)
        R2w = R_whole_mod(49, 343, whole_modes(b31)) @ R_whole_mod(343, 2401, whole_modes(b3))
        print(f'    {name:<14} two steps R_dec   ' + fmt_row(curve_iter(R2d, Ff3, F32, MS[:9])))
        print(f'    {name:<14} two steps R_whole ' + fmt_row(curve_iter(R2w, Ff3, F32, MS[:9])))
    print('\n  (d) where the parity flip is dynamical: the whole-tone reading (v18 strokes at odd')
    print('      coordinates), one step, sync ring, fine 56 octaves -> 8; canon on the same builder:')
    ent = family_entries(56, 392, 8, 7, -7)
    for lab, field in (('whole-tone', v18.m_wholetone), ('canon', v18.m_canon)):
        Tf = v18.ring_T(56, field)
        Tc = v18.ring_T(8, field)
        Ffw = np.linalg.solve(ring_kappa(56), Tf)
        Fcw = np.linalg.solve(ring_kappa(8), Tc)
        Rd = v20.R_windows(56, 392, [[1.0]], 7, 0, True)
        cells = []
        for m in (1, 4):
            A = np.linalg.matrix_power(Ffw, m)
            _, Ru = fast_family(ent, A, Fcw, nphi=36)
            dc, _ = constrained_family(ent, A, Fcw, 8, nphi=24, w0=weights_from_R(Ru, ent))
            cells.append(f'm={m} constrained SD7 {dc:.3f}')
        print(f'    {lab:<11} R_dec {fmt_row(curve_iter(Rd, Ffw, Fcw, MS[:9]))}   ' + '; '.join(cells))
    print('\n  (e) the reading closest to the sentence: ratio 3.5, each fine octave -> two coarse')
    print('      stations (body = structure, closing point = process); fine 14 octaves -> 4:')
    psi = v20.whole_mode()
    body = psi.copy()
    body[0] = body[7] = 0
    body /= np.linalg.norm(body)
    E8c = v20.canonical_octave_block()
    for comp in ('sync', 'seq'):
        if comp == 'sync':
            Ff, _, _ = v20.sync_ring(14)
            Fc, _, _ = v20.sync_ring(4)
        else:
            Ff = v20.seq_ring_from_block(14, E8c)
            Fc = v20.seq_ring_from_block(4, E8c)
        R = R_body_closure(14, body)
        entbc = entries_body_closure(14)
        cells = []
        for m in (1, 4):
            A = np.linalg.matrix_power(Ff, m)
            _, Ru = fast_family(entbc, A, Fc, nphi=36)
            dc, _ = constrained_family(entbc, A, Fc, 8, nphi=24, w0=weights_from_R(Ru, entbc))
            cells.append(f'm={m} {dc:.3f}')
        print(f'    {comp:<5} fixed R_bc {fmt_row(curve_iter(R, Ff, Fc, MS[:9]))}')
        print(f'    {comp:<5} per-node family, constrained: ' + '; '.join(cells))
    S2 = np.roll(np.eye(28), 2, axis=0)
    Fc, _, _ = v20.sync_ring(4)
    print(f'    symmetry floor (sync; fine one-octave shift = coarse two-node shift): '
          f'{np.linalg.norm(S2 @ Fc @ S2.T - Fc) / (2 * np.sqrt(56)):.4f}')
    print(f'    attractor: 7 fine octaves = 2 coarse octaves, so 7q = 2q, fixed points 2 pi k/5; '
          f'q* offset from 0.4 pi {np.degrees(0.362109515 * np.pi - 0.4 * np.pi):+.2f} deg')
    entbc = entries_body_closure(14)
    draws = []
    for _ in range(15):
        E8 = v20.haar_unitary(8, rng)
        Ffr = v20.seq_ring_from_block(14, E8)
        Fcr = v20.seq_ring_from_block(4, E8)
        A = np.linalg.matrix_power(Ffr, 4)
        _, Ru = fast_family(entbc, A, Fcr, nphi=36)
        draws.append(constrained_family(entbc, A, Fcr, 8, nphi=24, w0=weights_from_R(Ru, entbc))[0])
    draws = np.array(draws)
    A = np.linalg.matrix_power(v20.seq_ring_from_block(14, E8c), 4)
    Fc = v20.seq_ring_from_block(4, E8c)
    _, Ru = fast_family(entbc, A, Fc, nphi=36)
    canon = constrained_family(entbc, A, Fc, 8, nphi=24, w0=weights_from_R(Ru, entbc))[0]
    print(f'    same-geometry null (random octave blocks, seq, m = 4, constrained): '
          f'{draws.mean():.3f} +/- {draws.std():.3f} (min {draws.min():.3f}); canonical {canon:.3f} '
          f'at pct {float(np.mean(draws <= canon)):.2f}')


# ============================================================ verdict

def verdict(rows, best_out):
    hr('VERDICT (pre-stated rule: supported iff delta <= 0.10 AND below the 1st '
       'percentile of every null)')
    sup = [r for r in rows if r[3] <= 0.10 and r[4] <= 0.01]
    beyond = [r for r in rows if r[3] > 0.10 and r[4] <= 0.01]
    print(f'  corpus-instance cells tested (role strokes, role gates; 3 maps; m = 1..8): '
          f'{len(rows)}')
    print(f'  SUPPORTED: {len(sup)}')
    print(f'  below every null but not small: {len(beyond)}')
    for r in beyond:
        print(f'    {r[0]:<13} {r[1]:<8} m={r[2]}: delta {r[3]:.3f}, max pct {r[4]:.3f}')
    print(f'  smallest corpus-instance defect: {min(r[3] for r in rows):.3f}')
    if best_out:
        vals = [v[1] for k, v in best_out.items() if k[0] in ('SD7', 'PN')]
        print(f'  best searched modulation, smallest constrained family ceiling (L = 2): '
              f'{min(vals):.3f}  (small would be <= 0.10)')


def main():
    t0 = time.time()
    print('unified_expression_T_v21_seam_modulated.py  (v1.0, 2026-10-16)')
    print(f'alpha = 1/{1 / ALPHA:.9f} (measured); numpy {np.__version__}')
    if not E0_instruments():
        print('INSTRUMENT CHECK FAILED; aborting.')
        return
    E1_construction()
    curves = E2_corpus_maps()
    rows, _ = E3_nulls(curves)
    E4_ceilings()
    best_out = E5_best_modulation()
    E6_leakage()
    E6b_locality()
    E7_attractor()
    E8_tensor()
    E9_720()
    verdict(rows, best_out)
    print(f'\n[total runtime {time.time() - t0:.0f}s]')


if __name__ == '__main__':
    if '--optimize' in sys.argv:
        print('unified_expression_T_v21_seam_modulated.py --optimize  (v1.0, 2026-10-16)')
        print(f'alpha = 1/{1 / ALPHA:.9f} (measured); numpy {np.__version__}; '
              f'search seed {SEARCH_SEED}')
        t0 = time.time()
        run_search()
        print(f'\n[total runtime {time.time() - t0:.0f}s]')
    else:
        main()
