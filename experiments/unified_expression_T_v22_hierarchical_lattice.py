"""
unified_expression_T_v22_hierarchical_lattice.py

Created: 2026-10-16
Last updated: 2026-10-16
Version: 1.0
History:
  - 2026-10-16 v1.0: initial. Dynamical self-similarity test of the
    hierarchical (bridged) octave lattice: the change of geometry named in
    T_operator_findings_v21_seam_modulated.md section 4.

THE BRIDGED LATTICE (v22 of the T-operator series)

v20 and v21 found the staggered chain is not dynamically self-similar, and v21
traced what remains after its seam modulation to two things: a leak-or-freeze
dilemma (exact identity delta^2 = 1 - |<F_c, R F^m R^dag>| / N_c for any
co-isometric coarse-graining R) and a locality mismatch (the coarse octave's
generator puts 80 to 82% of its weight on station pairs two or more apart,
which a chain whose octaves meet only at shared tonics cannot carry). v21
section 4 named the remaining constructive step: change the geometry, bridging
each coupled pair of coarse stations with a fine octave whose two tonics are
those stations, as in the hierarchical lattices of renormalization theory.
This experiment builds that geometry and tests it.

THE CONSTRUCTION (substitution rules; one rule per geometry)
  Under tonic decimation a fine octave spans two coarse stations (its two
  tonics), so a fine geometry is a choice of which coarse pairs get a fine
  octave. A rule replaces every octave of level L by bridge octaves on a
  graph over its eight stations; the stations become the bridges' shared
  tonics (local 0 opens, local 7 closes) and each bridge adds six new nodes.
  Level L+1 is the same rule applied to every octave of level L, so the family
  is self-similar as a construction by definition. Rules:
    chain      the path 0-1-2-...-7: reproduces the v20/v21 chain exactly;
    beat       the ten pairs coupled by the octave's four beats (s-p pairs and
               the hub couplings), in order of first appearance in the beats;
               the geometry v21 section 4 asked for;
    parity720  the beat pairs, with each same-parity pair (the six hub pairs)
               carried by two bridges in series through a new fine tonic: a
               coarse coupling that keeps coordinate parity spans 7D (two
               octaves, 720 degrees) and one that flips it spans 3.5D (one
               octave, 360); Ashman's 720 made geometric;
    complete   all 28 pairs (carries every within-octave coupling).
  Root (level 0): the canonical two-octave staggered ring (14 nodes), as in
  v20 E2. Composition: octave-sequential in the order the rule lists (seq,
  the StaggeredOperator convention) and beat-synchronous (sync, v16).
  Canon strokes, theta = pi/2, kappa diameter bonds at the measured alpha.

SCALE MAPS (level L+1 -> level L; the coarse nodes keep their ids)
  R_dec    restriction to the level-L nodes (the bridges' tonics): the literal
           3.5D = 0D' reading, as in v20/v21;
  R_cell   block spin over Voronoi cells (each new node belongs to its nearer
           tonic: bridge locals 1-3 to the opening tonic, 4-6 to the closing);
  R_whole  the cell weighted by the octave whole-mode of each bridge;
  per-node cell family: any weights on the cells (contains all three);
  its constrained optimum keeps every coarse row at unit norm.

NULLS (a small defect counts only if it beats these clearly)
  Haar co-isometries of the same shape; random decimations; random-geometry
  lattices (random connected 10-pair graphs, canonical octaves); random-block
  lattices (same geometry, one Haar 8x8 octave block everywhere); tensor
  nesting (closed form, v20 E8).

ALSO
  E5 the leakage split and the carrying capacity of each geometry (the share
     of the coarse generator its pairs can carry at leading order, and the
     share a uniform bridge can carry); E6 weak seams (the protected channel
     v21 section 4 called for: bridges whose tonic couplings are scaled by
     eps), with the effective coarse generator extracted and compared; E8 the
     Xorzo octave tree (the v3 engine's geometry, and regular trees) as the
     corpus's existing non-chain control.

PRE-STATED VERDICT RULE (v20's): SUPPORTED at m only if delta <= 0.10 AND below
the 1st percentile of every null family.

Station labels are legacy continuation coordinates (v14+ convention).
Run: python unified_expression_T_v22_hierarchical_lattice.py   (about 12 minutes)
Raw output of the committed run: v22_output.txt.
"""

import os
import sys
import time

import numpy as np
from scipy.linalg import expm, eigh, logm, schur
from scipy.optimize import linear_sum_assignment
import scipy.sparse as sp

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'Xorzo'))
sys.path.insert(0, HERE)

import t_operator as tops                                          # noqa: E402
import unified_expression_T_v20_self_similarity as v20             # noqa: E402
import unified_expression_T_v21_seam_modulated as v21              # noqa: E402

ALPHA = v20.ALPHA
DIAMETERS = v20.DIAMETERS
defect = v20.defect
RNG_SEED = 20261022
M_LIST = list(range(1, 9))

GENS = v21.octave_generators(v20.I_PHASES, [1.0, 1.0, 1.0, 1.0])
E8 = np.eye(8, dtype=complex)
for _G in GENS:
    E8 = expm(_G) @ E8
PSI = v21.whole_modes([E8])[0]          # the open octave's whole (T attractor, C8)


def hr(title):
    print()
    print('=' * 78)
    print(title)
    print('=' * 78)


def fmt_row(vals, w=6, p=3):
    return ' '.join(f'{v:>{w}.{p}f}' for v in vals)


# ============================================================ rules

def beat_edges():
    """Pairs of stations coupled by the four canonical beats, in order of
    first appearance (beat 1, 2, 3, 4), lower local index first."""
    seen, out = set(), []
    for ent in v20.beat_template():
        for (a, b, _h) in ent:
            if a == b:
                continue
            e = (min(a, b), max(a, b))
            if e not in seen:
                seen.add(e)
                out.append(e)
    return out


BEAT = beat_edges()


def make_rule(name):
    """List of ((open, close), subdivide) in composition order."""
    if name == 'chain':
        return [((l, l + 1), False) for l in range(7)]
    if name == 'beat':
        return [(e, False) for e in BEAT]
    if name == 'parity720':
        return [(e, (e[1] - e[0]) % 2 == 0) for e in BEAT]
    if name == 'complete':
        rest = [(a, b) for a in range(8) for b in range(a + 1, 8) if (a, b) not in BEAT]
        return [(e, False) for e in BEAT + rest]
    if name == 'beat-flipped':
        return [((e[1], e[0]), False) for e in BEAT]
    if name == 'beat-ascending':
        return [(e, False) for e in sorted(BEAT)]
    if name == 'beat-reversed':
        return [(e, False) for e in BEAT[::-1]]
    raise ValueError(name)


GEOMS = ['chain', 'beat', 'parity720', 'complete']


class Lattice:
    """A graph of octaves joined only at shared tonics. octaves: 8-lists of
    node ids in composition order. Nodes 0 .. n_prev-1 are the previous
    level's nodes; owner[f] is the coarse node whose Voronoi cell holds f."""

    def __init__(self, N, octaves, n_prev=None, owner=None):
        self.N = N
        self.octaves = [list(o) for o in octaves]
        self.n_prev = n_prev
        self.owner = None if owner is None else np.asarray(owner)


def ring_root(n_c=2):
    N = 7 * n_c
    return Lattice(N, [[(7 * k + l) % N for l in range(8)] for k in range(n_c)])


def open_root():
    return Lattice(8, [list(range(8))])


def substitute(lat, rule):
    nid, owner, octs = lat.N, list(range(lat.N)), []
    for o in lat.octaves:
        for (l1, l2), sub in rule:
            a, b = o[l1], o[l2]
            if not sub:
                inner = list(range(nid, nid + 6))
                nid += 6
                octs.append([a] + inner + [b])
                owner += [a, a, a, b, b, b]
            else:
                x = nid
                nid += 1
                in1 = list(range(nid, nid + 6))
                in2 = list(range(nid + 6, nid + 12))
                nid += 12
                octs.append([a] + in1 + [x])
                octs.append([x] + in2 + [b])
                owner += [a] + [a] * 6 + [b] * 6
    return Lattice(nid, octs, lat.N, owner)


def level(rule_name, L, root=None):
    lat = ring_root(2) if root is None else root
    rule = make_rule(rule_name)
    for _ in range(L):
        lat = substitute(lat, rule)
    return lat


def node_count(rule_name, L, root=None):
    """Node count without building (octave count grows by the rule's bridges)."""
    lat = ring_root(2) if root is None else root
    N, n_oct = lat.N, len(lat.octaves)
    rule = make_rule(rule_name)
    for _ in range(L):
        new = sum(6 if not s else 13 for _e, s in rule)
        N += n_oct * new
        n_oct *= sum(1 if not s else 2 for _e, s in rule)
    return N, n_oct


# ============================================================ operators

def F_seq(lat, E=E8):
    F = np.eye(lat.N, dtype=complex)
    for o in lat.octaves:
        F[o, :] = E @ F[o, :]
    return F


def F_sync(lat, gens=GENS):
    F = np.eye(lat.N, dtype=complex)
    for G8 in gens:
        G = np.zeros((lat.N, lat.N), dtype=complex)
        for o in lat.octaves:
            G[np.ix_(o, o)] += G8
        F = expm(G) @ F
    return F


def kappa(lat, sparse=False):
    rows, cols = [], []
    for o in lat.octaves:
        for (a, b) in DIAMETERS:
            rows += [o[a], o[b]]
            cols += [o[b], o[a]]
    K = sp.identity(lat.N, dtype=complex, format='csr') + sp.csr_matrix(
        (np.full(len(rows), ALPHA, dtype=complex), (rows, cols)), shape=(lat.N, lat.N))
    return K if sparse else K.toarray()


def right_apply(X, lat, E=E8, K=None):
    """X <- X T (T = K F) without forming F: X K, then the octave blocks."""
    if K is not None:
        X = np.asarray((K.T @ X.T).T)
    for o in reversed(lat.octaves):
        X[:, o] = X[:, o] @ E
    return X


def curve_dense(R, A, B, ms=M_LIST):
    out, X, done = [], R.astype(complex).copy(), 0
    Y = B @ R
    for m in ms:
        while done < m:
            X = X @ A
            done += 1
        out.append(defect(X, Y))
    return np.array(out)


def curve_lat(R, lat, B, ms=M_LIST, E=E8, K=None):
    out, X, done = [], R.astype(complex).copy(), 0
    Y = B @ R
    for m in ms:
        while done < m:
            X = right_apply(X, lat, E, K)
            done += 1
        out.append(defect(X, Y))
    return np.array(out)


def departure(T):
    return float((np.max(np.abs(np.linalg.eigvals(T))) - 1.0) / ALPHA)


# ============================================================ scale maps

def R_dec(lat):
    R = np.zeros((lat.n_prev, lat.N), dtype=complex)
    R[np.arange(lat.n_prev), np.arange(lat.n_prev)] = 1.0
    return R


def R_cell(lat):
    R = np.zeros((lat.n_prev, lat.N), dtype=complex)
    R[lat.owner, np.arange(lat.N)] = 1.0
    return R / np.linalg.norm(R, axis=1)[:, None]


def R_whole(lat):
    R = np.zeros((lat.n_prev, lat.N), dtype=complex)
    for o in lat.octaves:
        for l, f in enumerate(o):
            R[lat.owner[f], f] += np.conj(PSI[l])
    return R / np.linalg.norm(R, axis=1)[:, None]


MAPS = {'R_dec': R_dec, 'R_cell': R_cell, 'R_whole': R_whole}


# ============================================================ cell-family optimizers (unitary A, B)

def cell_H(A, B, owner):
    """<Y(w), X(w)> = w^dag H w for R(w)[owner[f], f] = w[f]; for unitary A, B
    the Gram blocks XX, YY are the identity, so delta^2 = 1 - |w^H H w|/|w|^2."""
    return np.conj((np.conj(A) * B[np.ix_(owner, owner)]).T)


def cell_unconstrained(H, nphi=48, refine=2):
    def top(phi):
        K = (np.exp(-1j * phi) * H + np.exp(1j * phi) * np.conj(H.T)) / 2
        ev, V = eigh(K, subset_by_index=[K.shape[0] - 1, K.shape[0] - 1])
        return ev[0], V[:, 0]
    best = (-np.inf, None, 0.0)
    for phi in np.linspace(0, 2 * np.pi, nphi, endpoint=False):
        e, v = top(phi)
        if e > best[0]:
            best = (e, v, phi)
    step = 2 * np.pi / nphi
    for _ in range(refine):
        for phi in np.linspace(best[2] - step, best[2] + step, 7):
            e, v = top(phi)
            if e > best[0]:
                best = (e, v, phi)
        step /= 4
    w = best[1]
    val = abs(np.conj(w) @ H @ w) / np.vdot(w, w).real
    return float(np.sqrt(max(0.0, 1 - val))), w


def cell_constrained(H, owner, n_c, w0=None, nphi=36, sweeps=50, seed=0):
    """Every coarse row (cell) at unit norm: delta^2 = 1 - |w^H H w| / N_c.
    Block majorize-maximize ascent at each global phase (v21's method, with
    variable block sizes). Returns (delta, w)."""
    rng = np.random.default_rng(seed)
    blocks = [np.where(owner == a)[0] for a in range(n_c)]

    def normalize(w):
        w = w.copy()
        for b in blocks:
            n = np.linalg.norm(w[b])
            w[b] = w[b] / n if n > 0 else 1.0 / np.sqrt(len(b))
        return w
    n = len(owner)
    starts = [] if w0 is None else [normalize(np.asarray(w0, dtype=complex))]
    starts += [normalize(rng.normal(size=n) + 1j * rng.normal(size=n)) for _ in range(2)]
    best = (-1.0, None)
    for phi in np.linspace(0, 2 * np.pi, nphi, endpoint=False):
        K = (np.exp(-1j * phi) * H + np.exp(1j * phi) * np.conj(H.T)) / 2
        sig = [max(0.0, -np.linalg.eigvalsh(K[np.ix_(b, b)])[0]) + 1e-9 for b in blocks]
        for w in starts:
            w = w.copy()
            for _ in range(sweeps):
                for bi, b in enumerate(blocks):
                    v = K[b, :] @ w + sig[bi] * w[b]
                    nv = np.linalg.norm(v)
                    if nv > 0:
                        w[b] = v / nv
            val = abs(np.conj(w) @ H @ w)
            if val > best[0]:
                best = (val, w.copy())
    return float(np.sqrt(max(0.0, 1 - best[0] / n_c))), best[1]


def ceilings(A, B, lat, nphi_u=48, nphi_c=36, sweeps=50):
    H = cell_H(A, B, lat.owner)
    du, wu = cell_unconstrained(H, nphi=nphi_u)
    dc, wc = cell_constrained(H, lat.owner, lat.n_prev, w0=wu, nphi=nphi_c, sweeps=sweeps)
    return du, dc, wc


def R_from_w(w, lat):
    R = np.zeros((lat.n_prev, lat.N), dtype=complex)
    R[lat.owner, np.arange(lat.N)] = w
    return R


def leakage_from_X(X, R, B):
    """Leakage split for a co-isometric R, from X = R A^m: M = X R^dag."""
    Nc = B.shape[0]
    M = X @ np.conj(R.T)
    leak = np.sqrt(max(0.0, 1 - np.linalg.norm(M) ** 2 / Nc))
    ov = abs(np.vdot(B, M))
    cos = ov / (np.linalg.norm(B) * np.linalg.norm(M))
    return leak, cos, np.sqrt(max(0.0, 1 - ov / Nc))


def spectral_match(A, B, nphi=72):
    """Best unrestricted co-isometry (no locality): match eigenvalues."""
    a = np.linalg.eigvals(A)
    b = np.linalg.eigvals(B)
    best = 0.0
    for phi in np.linspace(0, 2 * np.pi, nphi, endpoint=False):
        C = -np.real(np.conj(np.exp(1j * phi) * b)[:, None] * a[None, :])
        r, c = linear_sum_assignment(C)
        best = max(best, -C[r, c].sum())
    return float(np.sqrt(max(0.0, 1 - best / len(b))))


# ============================================================ shared builds (cached)

_CACHE = {}


def pair(geom, L, comp='seq'):
    """Fine level L and coarse level L-1 of a geometry, dense operators."""
    key = (geom, L, comp)
    if key not in _CACHE:
        fine = level(geom, L)
        coarse = level(geom, L - 1)
        if comp == 'seq':
            Ff, Fc = F_seq(fine), F_seq(coarse)
        else:
            Ff, Fc = F_sync(fine), F_sync(coarse)
        _CACHE[key] = dict(fine=fine, coarse=coarse, Ff=Ff, Fc=Fc,
                           Tf=kappa(fine) @ Ff, Tc=kappa(coarse) @ Fc)
    return _CACHE[key]


def random_connected_graph(rng, n_edges=10):
    pairs = [(a, b) for a in range(8) for b in range(a + 1, 8)]
    while True:
        idx = rng.choice(len(pairs), size=n_edges, replace=False)
        E = [pairs[i] for i in idx]
        adj = {v: set() for v in range(8)}
        for a, b in E:
            adj[a].add(b)
            adj[b].add(a)
        seen, stack = {0}, [0]
        while stack:
            v = stack.pop()
            for u in adj[v] - seen:
                seen.add(u)
                stack.append(u)
        if len(seen) == 8:
            return [(e, False) for e in E]


# ============================================================ E0

def E0_instruments():
    hr('E0  INSTRUMENTS AND VERIFICATION')
    ok = True
    # (a) the chain rule reproduces the v20/v21 rings exactly
    S1 = level('chain', 1)
    perm = np.zeros(S1.N, dtype=int)
    for j in range(14):
        perm[j] = 7 * j
    for b in range(14):
        for i in range(6):
            perm[14 + 6 * b + i] = 7 * b + 1 + i
    ref_seq, _ = v21.build_ring(14, None, 'seq')
    ref_sync, _, _ = v20.sync_ring(14)
    e_seq = np.abs(F_seq(S1) - ref_seq[np.ix_(perm, perm)]).max()
    e_sync = np.abs(F_sync(S1) - ref_sync[np.ix_(perm, perm)]).max()
    print(f'  chain rule, level 1 (98 nodes) vs v21.build_ring(14) [seq]: {e_seq:.1e}; '
          f'vs v20.sync_ring(14) [sync]: {e_sync:.1e}')
    ok &= e_seq < 1e-12 and e_sync < 1e-12
    # (b) departure of the chain ring vs StaggeredOperator.ring
    d_ours = departure(kappa(S1) @ F_seq(S1))
    d_ref = tops.StaggeredOperator.ring(14, alpha=ALPHA).departure()
    print(f'  departure (|l1|-1)/alpha, 14-octave ring: ours {d_ours:.6f}, '
          f'StaggeredOperator.ring {d_ref:.6f}')
    ok &= abs(d_ours - d_ref) < 1e-9
    # (c) the Xorzo v3 tree reproduced (departure 0.6659 in the v3 notes)
    fine, _ = xorzo_v3_tree()
    d_tree = departure(kappa(fine) @ F_seq(fine))
    d_tree_ref = tops.StaggeredOperator(fine.N, fine.octaves, alpha=ALPHA).departure()
    print(f'  Xorzo v3 tree (169 nodes): departure ours {d_tree:.4f}, StaggeredOperator '
          f'{d_tree_ref:.4f} (v3 notes: 0.6659)')
    ok &= abs(d_tree - d_tree_ref) < 1e-9
    # (d) octave blocks are t_operator's, and the leakage identity holds
    E_ref = np.eye(8, dtype=complex)
    for B in tops.build_octave_beats_at(8, list(range(8))):
        E_ref = B @ E_ref
    print(f'  octave block vs t_operator.build_octave_beats_at: {np.abs(E8 - E_ref).max():.1e}')
    P = pair('beat', 1)
    R = R_dec(P['fine'])
    X = R @ np.linalg.matrix_power(P['Ff'], 4)
    leak, cos, d_id = leakage_from_X(X, R, P['Fc'])
    d_dir = defect(X, P['Fc'] @ R)
    print(f'  leakage identity on the beat lattice (R_dec, m = 4): direct {d_dir:.6f}, '
          f'identity {d_id:.6f}')
    ok &= abs(d_dir - d_id) < 1e-10
    print(f'  all instrument checks pass: {ok}')


# ============================================================ E1

def bipartition(edges, n=8):
    color = {0: 0}
    stack = [0]
    adj = {v: set() for v in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in color:
                color[u] = 1 - color[v]
                stack.append(u)
            elif color[u] == color[v]:
                return None
    return color


def E1_construction():
    hr('E1  CONSTRUCTION AND PRECONDITIONS')
    print(f'  beat pairs (first appearance): {BEAT}')
    print('  node counts (octaves) by level, root = two-octave ring (14 nodes):')
    for g in GEOMS:
        cells = []
        for L in range(4):
            N, no = node_count(g, L)
            cells.append(f'L{L} {N} ({no})')
        print(f'    {g:<10} ' + ', '.join(cells))
    print('  tonic degree of the 14 root nodes at level 1:')
    for g in GEOMS:
        lat = level(g, 1)
        deg = np.bincount(np.array([o[0] for o in lat.octaves] + [o[7] for o in lat.octaves]),
                          minlength=lat.N)
        print(f'    {g:<10} {deg[:14].tolist()}')
    print('  conservation departure (|lambda_1| - 1)/alpha of T = kappa F (O(1) = no compounding):')
    for comp in ('seq', 'sync'):
        vals = [f'{g} {departure(pair(g, 1, comp)["Tf"]):.3f}' for g in GEOMS]
        print(f'    level 1, {comp:<4}: ' + ', '.join(vals))
    vals = [f'{g} {departure(pair(g, 2)["Tf"]):.3f}' for g in ('chain', 'beat')]
    print('    level 2, seq : ' + ', '.join(vals) + '   (root ring: '
          f'{departure(kappa(ring_root(2)) @ F_seq(ring_root(2))):.3f})')
    S = np.roll(np.eye(14), 7, axis=0)
    Fs = F_sync(ring_root(2))
    print('  symmetry: rules act octave by octave, so level L+1 keeps the root\'s one-octave')
    print(f'  translation (sync root: ||S F S^-1 - F|| = {np.linalg.norm(S @ Fs @ S.T - Fs):.1e}).')
    print('  v20 Theorem 1\'s floor came from a fine translation that acts on the coarse ring as')
    print('  a one-station shift, which the coarse octave lacks. A rule has such a translation')
    print('  only if its pair set is invariant under the station shift j -> j+1 (mod 14);')
    print('  share of pairs mapped onto pairs:', end='')
    root = ring_root(2)
    for g in GEOMS:
        E = edge_sets(g, root)
        Es = {(min((a + 1) % 14, (b + 1) % 14), max((a + 1) % 14, (b + 1) % 14)) for a, b in E}
        print(f'  {g} {len(E & Es)}/{len(E)}', end='')
    print('\n  (the chain alone is invariant: the lattices carry no finer translation, so the')
    print('  Theorem 1 floor has no analog on them).')
    col = bipartition(BEAT)
    side = [l for l in range(8) if col[l] == col[4]]
    other = [l for l in range(8) if col[l] != col[4]]
    print(f'  the beat graph is bipartite: {side} | {other}; coordinate parity (local')
    print('  index mod 2) disagrees with it exactly at the two hubs (local 4 sits with the')
    print('  processual stations, local 5 with the structural): the six hub pairs are the')
    print('  same-parity pairs, which parity720 carries through two octaves.')


# ============================================================ E2 + E3

def E2_fixed_maps():
    hr('E2  CORPUS MAPS: delta(m), m = 1..8 (rows F then T)')
    rows = []
    for comp in ('seq', 'sync'):
        print(f'\n  level 1 -> level 0 ({comp}):')
        print(f'    {"geometry  map":<20}' + ' '.join(f'{m:>6d}' for m in M_LIST))
        for g in GEOMS:
            P = pair(g, 1, comp)
            for mn, mk in MAPS.items():
                R = mk(P['fine'])
                cF = curve_dense(R, P['Ff'], P['Fc'])
                cT = curve_dense(R, P['Tf'], P['Tc'])
                print(f'    {g:<10}{mn:<10}' + fmt_row(cF))
                print(f'    {"":<10}{"  T":<10}' + fmt_row(cT))
                rows.append(dict(level=1, comp=comp, geom=g, map=mn, F=cF, T=cT))
    print('\n  level 2 -> level 1 (seq; lattice to lattice):')
    print(f'    {"geometry  map":<20}' + ' '.join(f'{m:>6d}' for m in M_LIST))
    for g in ('chain', 'beat', 'parity720'):
        fine, coarse = level(g, 2), level(g, 1)
        Fc = F_seq(coarse)
        Tc = kappa(coarse) @ Fc
        Kf = kappa(fine, sparse=True)
        for mn, mk in MAPS.items():
            R = mk(fine)
            cF = curve_lat(R, fine, Fc)
            cT = curve_lat(R, fine, Tc, K=Kf)
            print(f'    {g:<10}{mn:<10}' + fmt_row(cF))
            print(f'    {"":<10}{"  T":<10}' + fmt_row(cT))
            rows.append(dict(level=2, comp='seq', geom=g, map=mn, F=cF, T=cT))
    return rows


def R_randcell(lat, rng):
    """Same shape as R_cell / R_whole: random complex weights on the same cells."""
    w = rng.normal(size=lat.N) + 1j * rng.normal(size=lat.N)
    R = np.zeros((lat.n_prev, lat.N), dtype=complex)
    R[lat.owner, np.arange(lat.N)] = w
    return R / np.linalg.norm(R, axis=1)[:, None]


def E3_nulls(rows, n_haar=200, n_haar2=40, n_rand=50):
    hr('E3  NULLS FOR THE CORPUS MAPS (level 1 -> 0 seq/sync; level 2 -> 1 seq)')
    print('  families: Haar co-isometries (same shape); random decimations (same sparsity as')
    print('  R_dec); random cell weights (same sparsity as R_cell, R_whole); and, at level 1')
    print(f'  seq, random-geometry and random-block lattices under R_dec ({n_rand} draws each).')
    rng = np.random.default_rng(RNG_SEED)
    nulls = {}
    for (L, comp, g) in sorted({(r['level'], r['comp'], r['geom']) for r in rows}):
        if L == 1:
            P = pair(g, 1, comp)
            fine, Fc, Tc = P['fine'], P['Fc'], P['Tc']
            curF = lambda R: curve_dense(R, P['Ff'], Fc)          # noqa: E731
            curT = lambda R: curve_dense(R, P['Tf'], Tc)          # noqa: E731
            n_h = n_haar
        else:
            fine, coarse = level(g, 2), level(g, 1)
            Fc = F_seq(coarse)
            Tc = kappa(coarse) @ Fc
            Kf = kappa(fine, sparse=True)
            curF = lambda R: curve_lat(R, fine, Fc)               # noqa: E731
            curT = lambda R: curve_lat(R, fine, Tc, K=Kf)         # noqa: E731
            n_h = n_haar2
        acc = {'haar': ([], []), 'randdec': ([], []), 'randcell': ([], [])}
        for _ in range(n_h):
            Rd = np.zeros((fine.n_prev, fine.N), dtype=complex)
            Rd[np.arange(fine.n_prev), rng.choice(fine.N, fine.n_prev, replace=False)] = 1.0
            for fam, R in (('haar', v20.haar_coisometry(fine.n_prev, fine.N, rng)),
                           ('randdec', Rd), ('randcell', R_randcell(fine, rng))):
                acc[fam][0].append(curF(R))
                acc[fam][1].append(curT(R))
        for fam, (aF, aT) in acc.items():
            nulls[(L, comp, g, fam)] = (np.array(aF), np.array(aT))
    root = ring_root(2)
    gF, gT = [], []
    for _ in range(n_rand):
        lat = substitute(root, random_connected_graph(rng))
        Ff, Fc = F_seq(lat), F_seq(root)
        gF.append(curve_dense(R_dec(lat), Ff, Fc))
        gT.append(curve_dense(R_dec(lat), kappa(lat) @ Ff, kappa(root) @ Fc))
    for g in GEOMS:
        nulls[(1, 'seq', g, 'randgeom')] = (np.array(gF), np.array(gT))
        lat = level(g, 1)
        bF, bT = [], []
        for _ in range(n_rand):
            E = v20.haar_unitary(8, rng)
            Ff, Fc = F_seq(lat, E), F_seq(root, E)
            bF.append(curve_dense(R_dec(lat), Ff, Fc))
            bT.append(curve_dense(R_dec(lat), kappa(lat) @ Ff, kappa(root) @ Fc))
        nulls[(1, 'seq', g, 'randblock')] = (np.array(bF), np.array(bT))
    fams = ['haar', 'randdec', 'randcell', 'randgeom', 'randblock']
    print('  null mean (min) over draws and m = 1..8, F:')
    print(f'    {"":<22}' + ''.join(f'{f:>16}' for f in fams))
    for (L, comp, g) in sorted({k[:3] for k in nulls}):
        cells = []
        for f in fams:
            k = (L, comp, g, f)
            cells.append(f'{nulls[k][0].mean():.3f} ({nulls[k][0].min():.3f})' if k in nulls else '-')
        print(f'    level {L} {comp:<4} {g:<10}' + ''.join(f'{c:>16}' for c in cells))
    # verdict counts
    n_cells = n_small = n_below = n_sup = 0
    below = []
    lo, hi = 1.0, 0.0
    for r in rows:
        for op, vals in (('F', r['F']), ('T', r['T'])):
            lo, hi = min(lo, vals.min()), max(hi, vals.max())
            for i, m in enumerate(M_LIST):
                n_cells += 1
                keys = [k for k in nulls if k[:3] == (r['level'], r['comp'], r['geom'])]
                pct = [float(np.mean(nulls[k][0 if op == 'F' else 1][:, i] <= vals[i]))
                       for k in keys]
                small = vals[i] <= 0.10
                beats = all(p < 0.01 for p in pct)
                n_small += small
                n_below += beats
                n_sup += small and beats
                if beats and not small:
                    below.append((r['level'], r['comp'], r['geom'], r['map'], op, m, vals[i]))
    print(f'\n  cells: {n_cells} (delta range {lo:.3f} to {hi:.3f}); delta <= 0.10: {n_small}; '
          f'below the 1st percentile of every null family: {n_below}; SUPPORTED: {n_sup}')
    if below:
        vals = np.array([b[6] for b in below])
        by = {}
        for b in below:
            by[(b[3], b[5])] = by.get((b[3], b[5]), 0) + 1
        common = sorted(by.items(), key=lambda kv: -kv[1])[:6]
        print(f'  the cells below every null (structure beyond chance, not self-similarity) have')
        print(f'  delta {vals.min():.3f} to {vals.max():.3f}; most frequent (map, m): ' +
              ', '.join(f'{k[0]} m={k[1]} x{v}' for k, v in common))
    return nulls, n_cells, n_small, n_below, n_sup


# ============================================================ E4

def E4_ceilings(n_rand=20):
    hr('E4  CEILINGS: PER-NODE CELL FAMILY (F, seq; unconstrained / constrained)')
    rng = np.random.default_rng(RNG_SEED + 4)
    out = {}
    print(f'  level 1 -> 0:        ' + '   '.join(f'm={m}' + ' ' * 9 for m in (1, 2, 4, 8)))
    for g in GEOMS:
        P = pair(g, 1)
        cells = []
        for m in (1, 2, 4, 8):
            A = np.linalg.matrix_power(P['Ff'], m)
            du, dc, wc = ceilings(A, P['Fc'], P['fine'])
            out[(g, 1, m)] = (du, dc, wc)
            cells.append(f'{du:.3f} / {dc:.3f}')
        print(f'    {g:<16} ' + '   '.join(cells))
    # cross-check with v21's PN window family on the same chain
    Ff21, _ = v21.build_ring(14, None, 'seq')
    Fc21, _ = v21.build_ring(2, None, 'seq')
    ent = v21.family_entries(14, 98, 8, 14, -7)
    A = np.linalg.matrix_power(Ff21, 4)
    _, Ru = v21.fast_family(ent, A, Fc21, nphi=48)
    dc21, _ = v21.constrained_family(ent, A, Fc21, 8, nphi=36, w0=v21.weights_from_R(Ru, ent))
    print(f'    cross-check: v21 per-node window family (8 nodes, the closing octave) on the')
    print(f'    same chain, m = 4, constrained: {dc21:.3f}')
    # nulls at m = 4: random blocks (same geometry) and random geometry
    print('  nulls at m = 4 (constrained):')
    root = ring_root(2)
    stats = {}
    for g in GEOMS:
        lat = level(g, 1)
        draws = []
        for _ in range(n_rand if g != 'complete' else n_rand // 2):
            E = v20.haar_unitary(8, rng)
            A = np.linalg.matrix_power(F_seq(lat, E), 4)
            draws.append(ceilings(A, F_seq(root, E), lat, nphi_u=24, nphi_c=24, sweeps=40)[1])
        draws = np.array(draws)
        canon = out[(g, 1, 4)][1]
        stats[g] = draws
        print(f'    random octave blocks, {g:<10}: {draws.mean():.3f} +/- {draws.std():.3f} '
              f'(min {draws.min():.3f}); canonical {canon:.3f} at pct {np.mean(draws <= canon):.2f}')
    draws = []
    for _ in range(n_rand):
        lat = substitute(root, random_connected_graph(rng))
        A = np.linalg.matrix_power(F_seq(lat), 4)
        draws.append(ceilings(A, F_seq(root), lat, nphi_u=24, nphi_c=24, sweeps=40)[1])
    draws = np.array(draws)
    stats['randgeom'] = draws
    print(f'    random connected 10-pair geometries (canonical octaves): {draws.mean():.3f} +/- '
          f'{draws.std():.3f} (min {draws.min():.3f}); beat lattice {out[("beat", 1, 4)][1]:.3f} '
          f'at pct {np.mean(draws <= out[("beat", 1, 4)][1]):.2f}')
    P = pair('beat', 1)
    print(f'  reference: the best UNRESTRICTED co-isometry (eigenvalue matching, no locality),')
    print(f'  beat lattice m = 4: delta = '
          f'{spectral_match(np.linalg.matrix_power(P["Ff"], 4), P["Fc"]):.3f}; locality is what the')
    print('  test measures.')
    print('  level 2 -> 1 (lattice to lattice), m = 4:')
    for g in ('chain', 'beat'):
        P2 = pair(g, 2)
        fine = P2['fine']
        A = np.linalg.matrix_power(P2['Ff'], 4)
        t0 = time.time()
        du, dc, _ = ceilings(A, P2['Fc'], fine, nphi_u=24, nphi_c=12, sweeps=30)
        out[(g, 2, 4)] = (du, dc, None)
        print(f'    {g:<16} {du:.3f} / {dc:.3f}   [{time.time() - t0:.0f}s]')
    return out, stats


# ============================================================ E5

def edge_sets(rule_name, root):
    E = set()
    for o in root.octaves:
        for (l1, l2), _s in make_rule(rule_name):
            a, b = o[l1], o[l2]
            E.add((min(a, b), max(a, b)))
    return E


def uniform_span(lat):
    """Real span of the second-order effective generator of identical bridges:
    i D_open, i D_close, (A - A^T), i (A + A^T) on the coarse nodes."""
    n = lat.n_prev
    Do, Dc, A = np.zeros((n, n)), np.zeros((n, n)), np.zeros((n, n))
    for o in lat.octaves:
        a, b = o[0], o[7]
        Do[a, a] += 1
        Dc[b, b] += 1
        A[a, b] += 1
    basis = [1j * Do, 1j * Dc, (A - A.T).astype(complex), 1j * (A + A.T)]
    Q = []
    for Bm in basis:
        v = Bm.copy()
        for q in Q:
            v = v - np.real(np.vdot(q, v)) * q
        nv = np.linalg.norm(v)
        if nv > 1e-12:
            Q.append(v / nv)
    return Q


def span_project(G, Q):
    return sum(np.real(np.vdot(q, G)) * q for q in Q)


def E5_leakage_and_carrying(ceil):
    hr('E5  LEAKAGE SPLIT AND CARRYING CAPACITY')
    print('  For a co-isometric R: delta^2 = 1 - |<F_c, M>|/N_c, M = R F^m R^dag; leak^2 =')
    print('  1 - ||M||^2/N_c. Every fixed-map cell (level 1 -> 0, seq, F), ranges over m = 1..8:')
    for g in GEOMS:
        P = pair(g, 1)
        for mn, mk in MAPS.items():
            R = mk(P['fine'])
            X, leaks, coss = R.astype(complex), [], []
            for _m in M_LIST:
                X = X @ P['Ff']
                lk, cs, _ = leakage_from_X(X, R, P['Fc'])
                leaks.append(lk)
                coss.append(cs)
            print(f'    {g:<10} {mn:<8} leak {min(leaks):.2f} to {max(leaks):.2f};  '
                  f'cos(M, F_c) {min(coss):.2f} to {max(coss):.2f}')
    print('  At m = 4, with the constrained optima:')
    print(f'    {"geometry":<10} {"map":<14} {"leak":>6} {"cos(M,Fc)":>10} {"delta":>7}')
    for g in GEOMS:
        P = pair(g, 1)
        A = np.linalg.matrix_power(P['Ff'], 4)
        Rc = R_from_w(ceil[(g, 1, 4)][2], P['fine'])
        for mn, R in (('R_dec', R_dec(P['fine'])), ('R_cell', R_cell(P['fine'])),
                      ('cell constr.', Rc)):
            leak, cos, d = leakage_from_X(R @ A, R, P['Fc'])
            print(f'    {g:<10} {mn:<14} {leak:>6.3f} {cos:>10.3f} {d:>7.3f}')
    print('\n  Carrying capacity: share of the squared weight of the coarse generator')
    print('  G_c = log F_c (root ring) that a geometry can carry at leading order in weak')
    print('  seams: per-pair (each bridge its own effective coupling: diagonal + its pairs)')
    print('  and uniform (identical canonical bridges: a four-dimensional real span).')
    root = ring_root(2)
    for comp in ('seq', 'sync'):
        Fc = F_seq(root) if comp == 'seq' else F_sync(root)
        G = logm(Fc)
        G = (G - np.conj(G.T)) / 2
        tot = np.linalg.norm(G) ** 2
        diag = np.sum(np.abs(np.diag(G)) ** 2) / tot
        print(f'    {comp}: diagonal share {diag:.3f}; best achievable cos(G_eff, G_c):')
        for g in GEOMS:
            E = edge_sets(g, root)
            sh = sum(np.abs(G[a, b]) ** 2 + np.abs(G[b, a]) ** 2 for a, b in E) / tot
            if g == 'parity720':
                uni = 'n/a (two-bridge paths)'
            else:
                Q = uniform_span(level(g, 1))
                uni = f'{np.linalg.norm(span_project(G, Q)) / np.linalg.norm(G):.3f}'
            print(f'      {g:<10} pairs {len(E):>3}: per-pair {np.sqrt(diag + sh):.3f} (weight share '
                  f'{diag + sh:.3f}); uniform bridges {uni}')


# ============================================================ E6

def gens_eps(eps):
    out = []
    for G in GENS:
        G = G.copy()
        for i in range(8):
            for j in range(8):
                if i != j and (i in (0, 7) or j in (0, 7)):
                    G[i, j] *= eps
        out.append(G)
    return out


def block_of(gens):
    E = np.eye(8, dtype=complex)
    for G in gens:
        E = expm(G) @ E
    return E


def schur_unitary(Ff):
    Tm, Z = schur(Ff, output='complex')
    return np.diag(Tm), Z


def scan_m(dZ, Fc, n_c, m_max):
    """min over 1 <= m <= m_max of delta(R_dec), exact via the Schur form
    (dZ = schur_unitary(F_fine); unitary, so the Schur form is diagonal)."""
    d, Z = dZ
    W = Z[:n_c, :]
    c = np.einsum('ik,ij,jk->k', W.conj(), np.conj(Fc.T), W)
    best = (2.0, 1)
    for s in range(0, m_max, 4000):
        mm = np.arange(s + 1, min(m_max, s + 4000) + 1)
        val = np.abs((d[None, :] ** mm[:, None]) @ c) / n_c
        dl = np.sqrt(np.clip(1 - val, 0, None))
        i = int(np.argmin(dl))
        if dl[i] < best[0]:
            best = (float(dl[i]), int(mm[i]))
    M = W @ np.diag(d ** best[1]) @ np.conj(W.T)
    leak = np.sqrt(max(0.0, 1 - np.linalg.norm(M) ** 2 / n_c))
    cos = abs(np.vdot(Fc, M)) / (np.linalg.norm(Fc) * np.linalg.norm(M))
    return best[0], best[1], leak, cos


def effective_generator(Ff, n_c):
    """Coarse effective generator from the n_c Floquet modes of largest weight
    on the coarse nodes (weak seams). Returns (G_eff, min weight)."""
    Tm, Z = schur(Ff, output='complex')
    d = np.diag(Tm)
    pw = np.sum(np.abs(Z[:n_c, :]) ** 2, axis=0)
    sel = np.argsort(pw)[::-1][:n_c]
    W = Z[:n_c, sel] / np.sqrt(pw[sel])
    U = W @ np.diag(d[sel]) @ np.linalg.inv(W)
    u, s, vh = np.linalg.svd(U)
    G = logm(u @ vh)
    return (G - np.conj(G.T)) / 2, float(pw[sel].min())


def E6_weak_seams(n_targets=4):
    hr('E6  WEAK SEAMS: THE PROTECTED CHANNEL (bridges with tonic couplings x eps)')
    print('  v21 section 4: self-similarity would need an octave-local protected channel')
    print('  whose induced dynamics is the coarse octave\'s. Weak seams protect the tonics')
    print('  (leak -> 0 as eps -> 0); the coarse target stays the canonical root ring.')
    print('  min over 1 <= m <= m_max of delta(R_dec), with leak and cos(M, F_c) at the best m;')
    print(f'  null: the same statistic against {n_targets} random-block coarse rings.')
    rng = np.random.default_rng(RNG_SEED + 6)
    root = ring_root(2)
    Fc = F_seq(root)
    targets = [F_seq(root, v20.haar_unitary(8, rng)) for _ in range(n_targets)]
    frozen = lambda F: np.sqrt(1 - abs(np.trace(F)) / 14)        # noqa: E731
    fz_t = np.array([frozen(F) for F in targets])
    print(f'  A frozen channel (M = phase x I) scores delta = sqrt(1 - |tr F_c|/N_c): '
          f'{frozen(Fc):.3f} for the canonical')
    print(f'  ring, {fz_t.mean():.3f} on average for the random targets. Columns: min delta, the m')
    print('  where it occurs, leak and cos(M, F_c) there; then the random targets\' mean min delta.')
    for eps in (1.0, 0.3, 0.1, 0.05):
        Ee = block_of(gens_eps(eps))
        m_max = int(min(20000, max(200, 50 / eps ** 2)))
        print(f'\n  eps = {eps}   (m <= {m_max})')
        for g in GEOMS:
            lat = level(g, 1)
            dZ = schur_unitary(F_seq(lat, Ee))
            dl, m, leak, cos = scan_m(dZ, Fc, 14, m_max)
            nd = np.array([scan_m(dZ, Ft, 14, m_max)[0] for Ft in targets])
            print(f'    {g:<10} canon {dl:.3f} at m = {m:<6d} (leak {leak:.2f}, cos {cos:.2f});  '
                  f'random targets {nd.mean():.3f}')
    print('\n  effective coarse generator at weak seams vs G_c = log F_c (seq root):')
    Gc = logm(Fc)
    Gc = (Gc - np.conj(Gc.T)) / 2
    for eps in (0.05, 0.02):
        Ee = block_of(gens_eps(eps))
        for g in ('chain', 'beat', 'complete'):
            lat = level(g, 1)
            Geff, pwmin = effective_generator(F_seq(lat, Ee), 14)
            Q = uniform_span(lat)
            res = np.linalg.norm(Geff - span_project(Geff, Q)) / np.linalg.norm(Geff)
            cos = np.real(np.vdot(Geff, Gc)) / (np.linalg.norm(Geff) * np.linalg.norm(Gc))
            print(f'    eps {eps:<5} {g:<9} ||G_eff|| = {np.linalg.norm(Geff):.2e}, outside the '
                  f'uniform span {res:.3f}, cos(G_eff, G_c) = {cos:+.3f} (mode weight >= {pwmin:.3f})')


# ============================================================ E7

def E7_720():
    hr('E7  THE 720 IN THE LATTICE')
    print('  parity720 vs beat (same pairs; same-parity pairs carried through two octaves):')
    print('  see E2 and E4. Two scale steps (level 2 -> level 0, R_dec o R_dec, seq):')
    MS = [1, 2, 3, 4, 5, 6, 7, 8, 16, 49, 64]
    print(f'    {"geometry":<12}' + ' '.join(f'{m:>6d}' for m in MS))
    rng = np.random.default_rng(RNG_SEED + 7)
    root = ring_root(2)
    F0 = F_seq(root)
    for g in ('chain', 'beat', 'parity720'):
        fine = level(g, 2)
        R = np.zeros((14, fine.N), dtype=complex)
        R[np.arange(14), np.arange(14)] = 1.0
        print(f'    {g:<12}' + fmt_row(curve_lat(R, fine, F0, MS)))
        if g == 'beat':
            hz = np.array([curve_lat(v20.haar_coisometry(14, fine.N, rng), fine, F0, MS)
                           for _ in range(10)])
            print(f'    {"Haar (beat)":<12}' + fmt_row(hz.mean(0)))


# ============================================================ E8

def xorzo_v3_tree():
    """The v3 engine's tree (Xorzo/genesis_toperator_v3.py): top 0..7; layer j
    locals 0..6 at 8+7j.., local 7 = top node 0; channels locals 0..6 private,
    local 7 = its layer's node 0. Ascending: channels, layers, top."""
    counts = [2, 2, 2, 3, 3, 2, 2]
    top = list(range(8))
    layers = [list(range(8 + 7 * j, 8 + 7 * j + 7)) + [0] for j in range(7)]
    chans, owner, base = [], list(range(57)), 57
    for j, k in enumerate(counts):
        for _ in range(k):
            chans.append(list(range(base, base + 7)) + [layers[j][0]])
            owner += [layers[j][0]] * 7
            base += 7
    fine = Lattice(base, chans + layers + [top], 57, owner)
    coarse = Lattice(57, layers + [top])
    return fine, coarse


def regular_tree(k, D):
    """k-ary octave tree of depth D, Xorzo style: children's closing tonic is the
    parent's opening tonic. Nodes numbered top-down (depth D-1's nodes come
    first); octaves listed deepest first (parts complete before wholes)."""
    levels = [[list(range(8))]]
    nid = 8
    for _ in range(1, D):
        nxt = []
        for par in levels[-1]:
            for _c in range(k):
                nxt.append(list(range(nid, nid + 7)) + [par[0]])
                nid += 7
        levels.append(nxt)
    octs = [o for lev in levels[::-1] for o in lev]
    n_prev = nid - 7 * len(levels[-1]) if D > 1 else None
    owner = None
    if D > 1:
        owner = list(range(n_prev)) + [o[7] for o in levels[-1] for _ in range(7)]
    return Lattice(nid, octs, n_prev, owner)


def E8_trees(n_haar=100, n_rb=20):
    hr('E8  XORZO TREE CONTROL (peel: the coarse tree is the fine tree minus its leaves)')
    rng = np.random.default_rng(RNG_SEED + 8)
    cases = [('Xorzo v3 tree 169 -> 57',) + xorzo_v3_tree()]
    for (k, D) in ((2, 4), (3, 3)):
        cases.append((f'{k}-ary depth {D} -> {D - 1}', regular_tree(k, D), regular_tree(k, D - 1)))
    for name, fine, coarse in cases:
        Ff, Fc = F_seq(fine), F_seq(coarse)
        Tf, Tc = kappa(fine) @ Ff, kappa(coarse) @ Fc
        R = R_dec(fine)
        cF = curve_dense(R, Ff, Fc)
        cT = curve_dense(R, Tf, Tc)
        print(f'  {name} (N {fine.N} -> {coarse.N}; departure {departure(Tf):.3f})')
        print(f'    R_peel F: ' + fmt_row(cF))
        print(f'    R_peel T: ' + fmt_row(cT))
        # the peel map keeps the time scale (m = 1): the relation must propagate,
        # R F^n = F_c^n R, for the coarse tree to shadow the fine one
        X, Y, it = R.astype(complex), R.astype(complex), []
        for _n in M_LIST:
            X = X @ Ff
            Y = Fc @ Y
            it.append(defect(X, Y))
        print(f'    iterated, R F^n vs F_c^n R (n = 1..8): ' + fmt_row(it))
        rb, rbc = [], []
        for _ in range(n_rb):
            E = v20.haar_unitary(8, rng)
            Ffr, Fcr = F_seq(fine, E), F_seq(coarse, E)
            rb.append(defect(R @ Ffr, Fcr @ R))
            rbc.append(ceilings(Ffr, Fcr, fine, nphi_u=24, nphi_c=24, sweeps=40)[1])
        print(f'    random octave blocks, same tree, m = 1: R_peel {np.mean(rb):.3f} +/- '
              f'{np.std(rb):.3f}; constrained ceiling {np.mean(rbc):.3f} +/- {np.std(rbc):.3f}')
        for m in (1, 4):
            A = np.linalg.matrix_power(Ff, m)
            leak, cos, _ = leakage_from_X(R @ A, R, Fc)
            du, dc, _ = ceilings(A, Fc, fine, nphi_u=24, nphi_c=24, sweeps=40)
            hz = np.array([defect(Rh @ A, Fc @ Rh) for Rh in
                           (v20.haar_coisometry(fine.n_prev, fine.N, rng) for _ in range(n_haar))])
            print(f'    m = {m}: leak {leak:.3f}, cos {cos:.3f}; per-node ceiling {du:.3f} / {dc:.3f}; '
                  f'Haar {hz.mean():.3f} (min {hz.min():.3f})')


# ============================================================ E9 / E10

def E9_robustness():
    hr('E9  ROBUSTNESS OF THE BEAT LATTICE (level 1 -> 0, seq, F, m = 4)')
    variants = [('beat (as built)', level('beat', 1), ring_root(2)),
                ('orientation flipped', level('beat-flipped', 1), ring_root(2)),
                ('ascending order', level('beat-ascending', 1), ring_root(2)),
                ('reversed order', level('beat-reversed', 1), ring_root(2)),
                ('root: one open octave', substitute(open_root(), make_rule('beat')), open_root())]
    for name, lat, root in variants:
        Ff, Fc = F_seq(lat), F_seq(root)
        A = np.linalg.matrix_power(Ff, 4)
        d_dec = defect(R_dec(lat) @ A, Fc @ R_dec(lat))
        du, dc, _ = ceilings(A, Fc, lat, nphi_u=24, nphi_c=24, sweeps=40)
        print(f'  {name:<24} N {lat.N:>4}: R_dec {d_dec:.3f}; cell ceiling {du:.3f} / {dc:.3f}')


def E10_tensor():
    hr('E10 TENSOR-NESTING NULL (closed form from v20 E8)')
    F8 = tops.build_F_8D()
    t = [abs(np.trace(np.linalg.matrix_power(F8, k))) / 8 for k in range(9)]
    for depth in (2, 3):
        print(f'  depth {depth}: ' + fmt_row([np.sqrt(max(0.0, 1 - t[m - 1] ** (depth - 1)))
                                           for m in M_LIST]))


# ============================================================ main

def main():
    t0 = time.time()
    print('unified_expression_T_v22_hierarchical_lattice.py  (v1.0, 2026-10-16)')
    print(f'alpha = 1/{1 / ALPHA:.9f} (measured); numpy {np.__version__}; seed {RNG_SEED}')

    def timed(fn, *a):
        t = time.time()
        out = fn(*a)
        print(f'  [{fn.__name__}: {time.time() - t:.0f}s]')
        return out
    timed(E0_instruments)
    timed(E1_construction)
    rows = timed(E2_fixed_maps)
    _, n_cells, n_small, n_below, n_sup = timed(E3_nulls, rows)
    ceil, stats = timed(E4_ceilings)
    timed(E5_leakage_and_carrying, ceil)
    timed(E6_weak_seams)
    timed(E7_720)
    timed(E8_trees)
    timed(E9_robustness)
    timed(E10_tensor)
    hr('VERDICT (pre-stated rule: supported iff delta <= 0.10 AND below the 1st '
       'percentile of every null)')
    print(f'  corpus-map cells: {n_cells}; small: {n_small}; below every null: {n_below}; '
          f'supported: {n_sup}.')
    best = min(v[1] for k, v in ceil.items())
    print(f'  best constrained cell ceiling anywhere: {best:.3f}')
    print('  constrained ceilings at m = 4 against their same-geometry random-block nulls:')
    for g in GEOMS:
        d = stats[g]
        c = ceil[(g, 1, 4)][1]
        print(f'    {g:<10} {c:.3f} vs {d.mean():.3f} +/- {d.std():.3f} (pct {np.mean(d <= c):.2f}, '
              f'z {(c - d.mean()) / d.std():+.1f})')
    d = stats['randgeom']
    c = ceil[('beat', 1, 4)][1]
    print(f'    beat vs random 10-pair geometries: {c:.3f} vs {d.mean():.3f} +/- {d.std():.3f} '
          f'(pct {np.mean(d <= c):.2f}, z {(c - d.mean()) / d.std():+.1f})')
    print(f'\n[total runtime {time.time() - t0:.0f}s]')


if __name__ == '__main__':
    main()
