"""A two-coordinate criterion for part autonomy and greater-whole integration, defined before looking at graphs.

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. Record: plans/graph_from_self_limitation_2026_11_04.md
The first run of W8 used a wrong index in rates (V.T[S[0]] for V[S[0]]), so its printed numbers mean nothing; fixed.
W1 to W8 were not changed. The followups (G1 to G4) and third (X1 to X3) modes are post hoc, written after seeing W1 to W8.
G1's capacity measure hit a floor set by the bath, so X3 replaced it with a slow-mode method. X3 is the one to read.

Needs numpy and scipy. Run: python wholeness_plane_criterion_v1.py [followups | third]
All data are synthetic. Diffusive dynamics only (x' = -Kx). Nothing here is established for wave dynamics.

DEFINITIONS, FROZEN BEFORE ANY RUN. W symmetric, s_i = sum_j W_ij, K = I - D^-1/2 W D^-1/2, eigenvalues lam_1 <= lam_2 <= ...
Partition at k: average-linkage clustering of the sites in the k lowest modes (D^-1/2 V).
For a part S: out(S) = cut(S)/vol(S). h(S) = lam_2 of the normalized Laplacian of S alone (0 if S is split or a single site).
  r_mix = (1-out) h, r_esc = out, A(S) = r_mix/(r_mix + r_esc), the chance that S mixes before it leaks.
  g_k = 1 - lam_k/lam_(k+1), which says the boundary is not arbitrary.
AUTONOMY a_k = g_k * volume-weighted mean of A(S).
LEVELS: among the 6 values of k with the largest g_k, those with a_k > 1/2. Finest first.
INTEGRATION c_k: form the quotient of the level-k parts inside each parent (the part of the next coarser level, or
  the whole system at the top), normalize it, take lam_2 capped at 1, and average by volume over parents.
A graph with no level is reported at the k with largest a_k, marked "no level".
So a compares inside against outside, and c uses only the pattern among parts, with the outside share normalized away.

INDEPENDENT TRUTH, DIRECT DYNAMICS (no eigenvalues of parts or quotients).
plateau: 1 - min over t of the total-variation distance from p_t to the stationary law on the starting site's part.
c_true: min(1, T_esc / T_parent), where T_esc is when the chance of still being in the part falls below 1/e and T_parent
  is when the distance to the stationary law on the parent falls below 1/4.

PREDICTIONS, WRITTEN BEFORE ANY RUN.
W1. Corners. Planted hierarchy a>0.8, c>0.8 at every level. Separate blocks a near 1, c = 0. Complete graph a<0.1, c>0.9.
    Thin rings over capacity joined in a long path a<0.3, c<0.3.
W2. Clean ring: no level at any size, and c varies with k, so it has no preferred scale. I do not place it on the plane.
W3. Dynamics: on 300 random graphs, Spearman(a, plateau) >= 0.8 and Spearman(c, c_true) >= 0.7.
W4. Size: planted hierarchies from 3x3x3 to 6x6x6 at fixed shares keep a and c within 0.05.
W5. Recursion: (a, c) of the outer level measured on the original graph and on its quotient differ by under 0.1.
W6. Stability: the planted hierarchy keeps its k through 20% weight noise with (a, c) shifts under 0.1. Ring and complete
    graph show no stable level.
W7. Independence: across a factorial design, |Spearman(a, c)| < 0.3 and all four quadrants are occupied.
W8. Capacity law. A block with internal gap h stops holding at outside share s* = h/(1+h). Measured directly from
    conditional mixing and escape rates, the crossing lies within 15% of this across complete and ring blocks.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
from multiprocessing import Pool
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.stats import spearmanr


def spectrum(W):
    s = W.sum(1)
    inv = np.where(s > 0, 1 / np.sqrt(np.where(s > 0, s, 1)), 0.0)
    K = np.eye(len(W)) - W * np.outer(inv, inv)
    lam, V = np.linalg.eigh(K)
    return np.maximum(lam, 0.0), V, s, inv


def norm_gap(W):
    m = len(W)
    if m < 2:
        return 0.0
    d = W.sum(1)
    if np.any(d <= 0):
        return 0.0
    K = np.eye(m) - W / np.sqrt(np.outer(d, d))
    return float(max(np.sort(np.linalg.eigvalsh(K))[1], 0.0))


def parts_at(U, k):
    if k >= len(U):
        return [[i] for i in range(len(U))]
    lab = fcluster(linkage(U, "average"), t=k, criterion="maxclust")
    return [list(np.flatnonzero(lab == l)) for l in np.unique(lab)]


def autonomy_part(W, s, S):
    if len(S) < 2:
        return 0.0
    ins = W[np.ix_(S, S)]
    vol = s[S].sum()
    out = max(0.0, 1 - ins.sum() / vol)
    h = norm_gap(ins)
    if out <= 1e-14:
        return 1.0 if h > 1e-9 else 0.0
    r = (1 - out) * h
    return r / (r + out)


def quotient(W, parts):
    k = len(parts)
    Q = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            Q[i, j] = Q[j, i] = W[np.ix_(parts[i], parts[j])].sum()
    return Q


def level_table(W):
    lam, V, s, inv = spectrum(W)
    n = len(W)
    floor = 1e-11
    gs = []
    for k in range(2, max(3, n // 2 + 1)):
        lo, hi = max(lam[k - 1], floor), max(lam[k], floor)
        gs.append((1 - lo / hi, k))
    gs.sort(reverse=True)
    rows = []
    for g, k in gs[:6]:
        parts = parts_at(V[:, :k] * inv[:, None], k)
        vols = np.array([s[p].sum() for p in parts])
        A = np.array([autonomy_part(W, s, p) for p in parts])
        rows.append(dict(k=k, g=float(g), a=float(g * (A * vols).sum() / vols.sum()), parts=parts))
    return rows, lam


def integration(W, parts, parents, s):
    total, weight = 0.0, 0.0
    for parent in parents:
        pset = set(parent)
        kids = [p for p in parts if len(pset & set(p)) * 2 > len(p)]
        if len(kids) < 2:
            continue
        v = s[parent].sum()
        total += v * min(1.0, norm_gap(quotient(W, kids)))
        weight += v
    return total / weight if weight else float("nan")


def plane(W):
    rows, lam = level_table(W)
    s = W.sum(1)
    whole = [list(range(len(W)))]
    accepted = sorted([r for r in rows if r["a"] > 0.5], key=lambda r: r["k"])
    out = []
    parents = whole
    for r in accepted:
        c = integration(W, r["parts"], parents, s)
        if np.isnan(c):
            continue
        out.append(dict(k=r["k"], a=r["a"], c=c, parts=r["parts"], parents=parents, level=True))
        parents = r["parts"]
    if not out:
        best = max(rows, key=lambda r: r["a"])
        out.append(dict(k=best["k"], a=best["a"], c=integration(W, best["parts"], whole, s), parts=best["parts"], parents=whole, level=False))
    return out[::-1], rows  # finest first


def truth(W, parts, parents, rng):
    lam, V, s, inv = spectrum(W)
    sq = np.sqrt(s)
    n = len(W)
    starts = rng.choice(n, size=min(20, n), replace=False)
    part_of = np.zeros(n, int)
    for idx, p in enumerate(parts):
        part_of[p] = idx
    parent_of = np.zeros(n, int)
    for idx, p in enumerate(parents):
        parent_of[p] = idx
    ts = np.geomspace(1e-2, max(1e2, 50 / max(lam[lam > 1e-11].min() if (lam > 1e-11).any() else 1e-6, 1e-9)), 90)
    Dpart, stay, Dpar = [], [], []
    for t in ts:
        H = (V * np.exp(-lam * t)) @ V.T[:, :]
        dp, st, dq = 0.0, 0.0, 0.0
        for i in starts:
            pt = H[i] * sq / sq[i]
            P = parts[part_of[i]]
            law = np.zeros(n)
            law[P] = s[P] / s[P].sum()
            dp += 0.5 * np.abs(pt - law).sum()
            st += pt[P].sum()
            Q = parents[parent_of[i]]
            law2 = np.zeros(n)
            law2[Q] = s[Q] / s[Q].sum()
            dq += 0.5 * np.abs(pt - law2).sum()
        Dpart.append(dp / len(starts)); stay.append(st / len(starts)); Dpar.append(dq / len(starts))
    Dpart, stay, Dpar = map(np.array, (Dpart, stay, Dpar))
    plateau = 1 - Dpart.min()
    esc = ts[np.argmax(stay < np.exp(-1))] if (stay < np.exp(-1)).any() else np.inf
    mix = ts[np.argmax(Dpar < 0.25)] if (Dpar < 0.25).any() else np.inf
    if not np.isfinite(mix):
        ctrue = 0.0
    elif not np.isfinite(esc):
        ctrue = 1.0
    else:
        ctrue = min(1.0, esc / mix)
    return float(plateau), float(ctrue)


# ---------- generators ----------
def inner(kind, m, rng):
    A = np.zeros((m, m))
    if kind == "complete":
        A = np.ones((m, m)) - np.eye(m)
    elif kind == "ring":
        for i in range(m):
            A[i, (i + 1) % m] = A[(i + 1) % m, i] = 1
    elif kind == "path":
        for i in range(m - 1):
            A[i, i + 1] = A[i + 1, i] = 1
    elif kind == "sparse":
        for i in range(m):
            A[i, (i + 1) % m] = A[(i + 1) % m, i] = 1
        for _ in range(m):
            i, j = rng.integers(m, size=2)
            if i != j:
                A[i, j] = A[j, i] = 1
    return A / A.sum(1, keepdims=True).mean()


def pattern(kind, p, rng):
    Q = np.zeros((p, p))
    if kind == "complete":
        Q = np.ones((p, p)) - np.eye(p)
    elif kind == "ring":
        for i in range(p):
            Q[i, (i + 1) % p] = Q[(i + 1) % p, i] = 1
    elif kind == "path":
        for i in range(p - 1):
            Q[i, i + 1] = Q[i + 1, i] = 1
    elif kind == "star":
        Q[0, 1:] = Q[1:, 0] = 1
    elif kind == "sparse":
        for i in range(1, p):
            j = rng.integers(i)
            Q[i, j] = Q[j, i] = 1
        for _ in range(p // 2):
            i, j = rng.integers(p, size=2)
            if i != j:
                Q[i, j] = Q[j, i] = 1
    return Q


def compose(blocks, Q, share, rng, contact="all"):
    """Join blocks so that about `share` of each site's relation goes outward, in the pattern Q."""
    sizes = [len(b) for b in blocks]
    n = sum(sizes)
    W = np.zeros((n, n))
    off = np.cumsum([0] + sizes)
    for i, b in enumerate(blocks):
        W[off[i]:off[i + 1], off[i]:off[i + 1]] = b * (1 - share) / max(b.sum(1).mean(), 1e-300)
    deg = Q.sum(1)
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            if Q[i, j] <= 0:
                continue
            ni, nj = sizes[i], sizes[j]
            mass = share * Q[i, j] / max(np.sqrt(deg[i] * deg[j]), 1e-300)
            if contact == "all":
                W[off[i]:off[i + 1], off[j]:off[j + 1]] = mass / nj
            else:
                c = max(1, min(ni, nj) // 4)
                a = rng.choice(ni, c, replace=False)
                b_ = rng.choice(nj, c, replace=False)
                for x, y in zip(a, b_):
                    W[off[i] + x, off[j] + y] += mass * ni / c
    return W + np.triu(W, 1).T if False else (W + W.T) * 0 + symmetrize(W, off)


def symmetrize(W, off):
    U = np.triu(W, 1)
    # within-block entries are already symmetric; between-block entries were written once, above the diagonal
    return U + U.T


def noisy(W, sigma, rng):
    if sigma <= 0:
        return W
    g = rng.normal(0, 1, W.shape)
    g = (g + g.T) / np.sqrt(2)
    return W * np.exp(sigma * g)


def planted(sizes, shares, rng):
    """sizes innermost first; shares outward at each level."""
    block = inner("complete", sizes[0], rng)
    for lvl, p in enumerate(sizes[1:]):
        block = compose([block.copy() for _ in range(p)], pattern("complete", p, rng), shares[lvl], rng)
    return block


def random_graph(seed):
    rng = np.random.default_rng([4242, seed])
    kind = rng.choice(["hier1", "hier1", "hier1", "hier2", "hier2", "complete", "ring", "geometric", "regular"])
    sigma = float(rng.choice([0.0, 0.1, 0.3]))
    if kind == "hier1":
        p, m = int(rng.integers(3, 11)), int(rng.integers(4, 17))
        topo = rng.choice(["complete", "ring", "sparse"])
        patt = rng.choice(["complete", "ring", "path", "star", "sparse", "none"])
        s = float(np.exp(rng.uniform(np.log(1e-3), np.log(0.7))))
        W = compose([inner(topo, m, rng) for _ in range(p)], pattern(patt, p, rng), s, rng, contact=rng.choice(["all", "few"]))
    elif kind == "hier2":
        p1, p2, m = int(rng.integers(3, 6)), int(rng.integers(3, 6)), int(rng.integers(4, 11))
        topo = rng.choice(["complete", "ring", "sparse"])
        patt1, patt2 = rng.choice(["complete", "ring", "sparse"]), rng.choice(["complete", "ring", "path", "sparse"])
        s1 = float(np.exp(rng.uniform(np.log(3e-3), np.log(0.5))))
        s2 = float(np.exp(rng.uniform(np.log(3e-3), np.log(0.5))))
        mids = [compose([inner(topo, m, rng) for _ in range(p1)], pattern(patt1, p1, rng), s1, rng) for _ in range(p2)]
        W = compose(mids, pattern(patt2, p2, rng), s2, rng)
    elif kind == "complete":
        n = int(rng.integers(16, 121))
        W = np.ones((n, n)) - np.eye(n)
    elif kind == "ring":
        W = inner("ring", int(rng.integers(16, 121)), rng)
    elif kind == "geometric":
        n = int(rng.integers(40, 121))
        pts = rng.random((n, 2))
        d = np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(2))
        W = np.exp(-(d / 0.12) ** 2)
        np.fill_diagonal(W, 0)
    else:
        n = 2 * int(rng.integers(20, 61))
        W = np.zeros((n, n))
        for _ in range(3):
            perm = rng.permutation(n)
            for a, b in zip(perm[::2], perm[1::2]):
                W[a, b] = W[b, a] = 1
    W = noisy(W, sigma, rng)
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)
    return kind, W


def battery_job(seed):
    kind, W = random_graph(seed)
    if (W.sum(1) <= 0).any():
        return []
    points, _ = plane(W)
    rng = np.random.default_rng(seed)
    out = []
    for pt in points:
        pl, ct = truth(W, pt["parts"], pt["parents"], rng)
        out.append(dict(kind=str(kind), k=pt["k"], a=pt["a"], c=pt["c"], level=pt["level"], plateau=pl, c_true=ct))
    return out


def show(name, W):
    pts, rows = plane(W)
    txt = "; ".join(f"k={p['k']} a={p['a']:.3f} c={p['c']:.3f}{'' if p['level'] else ' (no level)'}" for p in pts)
    print(f"  {name}: {txt}")
    return pts


def rates(W, S, rng):
    """Directly measured conditional mixing rate and escape rate for block S."""
    lam, V, s, inv = spectrum(W)
    sq = np.sqrt(s)
    S = list(S)
    ts = np.geomspace(1e-2, 1e4, 240)
    stay, cond = [], []
    for t in ts:
        H = (V * np.exp(-lam * t)) @ V[S[0]]
        p = H * sq / sq[S[0]]
        inside = p[S].sum()
        q = p[S] / inside
        cond.append(0.5 * np.abs(q - s[S] / s[S].sum()).sum())
        stay.append(inside)
    stay, cond = np.array(stay), np.array(cond)
    use = (stay < 0.9) & (stay > 0.25)
    r_esc = -np.polyfit(ts[use], np.log(stay[use]), 1)[0] if use.sum() >= 4 else float("nan")
    use = (cond < 0.2) & (cond > 1e-4)
    r_mix = -np.polyfit(ts[use], np.log(cond[use]), 1)[0] if use.sum() >= 4 else float("nan")
    return r_mix, r_esc


def main():
    rng = np.random.default_rng(20261104)
    print("W1 corners, W2 ring")
    W = planted([4, 4, 4], [0.05, 0.05], rng)
    show("planted 4x4x4", W)
    blocks = [inner("complete", 8, rng) for _ in range(6)]
    show("separate blocks", compose(blocks, np.zeros((6, 6)), 0.0, rng))
    show("complete 64", np.ones((64, 64)) - np.eye(64))
    g = rng.normal(0, 1, (64, 64))
    Wn = np.exp(0.05 * (g + g.T) / np.sqrt(2)); np.fill_diagonal(Wn, 0)
    show("complete 64, 5% noise", Wn)
    show("thin rings over capacity in a long path", compose([inner("ring", 32, rng) for _ in range(12)], pattern("path", 12, rng), 0.2, rng))
    for n in (32, 128, 512):
        show(f"clean ring {n}", inner("ring", n, rng))
    rows, lam = level_table(inner("ring", 128, rng))
    s = np.ones(128)
    print("   ring 128, by k:", [(r["k"], round(r["a"], 3), round(integration(inner("ring", 128, rng), r["parts"], [list(range(128))], inner("ring", 128, rng).sum(1)), 3)) for r in sorted(rows, key=lambda r: r["k"])])

    print("\nW3 dynamics on 300 random graphs")
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        res = [r for rs in pool.imap_unordered(battery_job, range(300), chunksize=4) for r in rs]
    a, c, pl, ct = (np.array([r[k] for r in res]) for k in ("a", "c", "plateau", "c_true"))
    ok = ~np.isnan(c)
    print(f"  {len(res)} level points. Spearman(a, plateau) = {spearmanr(a[ok], pl[ok]).statistic:.3f}; Spearman(c, c_true) = {spearmanr(c[ok], ct[ok]).statistic:.3f}; Spearman(a, c) = {spearmanr(a[ok], c[ok]).statistic:.3f}")
    print(f"  cross terms: Spearman(a, c_true) = {spearmanr(a[ok], ct[ok]).statistic:.3f}; Spearman(c, plateau) = {spearmanr(c[ok], pl[ok]).statistic:.3f}")
    for kind in sorted({r["kind"] for r in res}):
        g_ = [r for r in res if r["kind"] == kind and not np.isnan(r["c"])]
        print(f"  {kind:10} points {len(g_):3}; accepted levels {np.mean([r['level'] for r in g_]):.2f}; mean a {np.mean([r['a'] for r in g_]):.3f}; mean c {np.mean([r['c'] for r in g_]):.3f}; mean plateau {np.mean([r['plateau'] for r in g_]):.3f}; mean c_true {np.mean([r['c_true'] for r in g_]):.3f}")
    hi = a[ok] > 0.5
    print(f"  plateau when a>0.5: {pl[ok][hi].mean():.3f} (n={hi.sum()}); when a<=0.5: {pl[ok][~hi].mean():.3f} (n={(~hi).sum()})")

    print("\nW4 size at fixed shares")
    for m in (3, 4, 5, 6):
        show(f"{m}x{m}x{m}", planted([m, m, m], [0.05, 0.05], rng))

    print("\nW5 recursion: the outer level on the original graph and on its quotient")
    for shares in ([0.05, 0.05], [0.2, 0.05], [0.05, 0.2], [0.1, 0.3]):
        W = planted([4, 4, 4], shares, rng)
        pts, _ = plane(W)
        coarse = [p for p in pts if p["level"]]
        if len(coarse) >= 2:
            inner_lvl, outer_lvl = coarse[0], coarse[1]
            Qg = quotient(W, inner_lvl["parts"])
            qp, _ = plane(Qg)
            match = [p for p in qp if p["k"] == outer_lvl["k"]]
            print(f"  shares {shares}: original a={outer_lvl['a']:.3f} c={outer_lvl['c']:.3f}; quotient " + (f"a={match[0]['a']:.3f} c={match[0]['c']:.3f}" if match else "no matching level"))
        else:
            print(f"  shares {shares}: only {len(coarse)} level(s): {[(p['k'], round(p['a'], 3)) for p in pts]}")

    print("\nW6 stability")
    base = planted([4, 4, 4], [0.05, 0.05], rng)
    b0, _ = plane(base)
    print("  planted, base:", [(p["k"], round(p["a"], 3), round(p["c"], 3)) for p in b0])
    for sigma in (0.05, 0.1, 0.2, 0.4):
        rs = []
        for _ in range(10):
            W = noisy(base, sigma, rng); W = (W + W.T) / 2
            rs.append([(p["k"], round(p["a"], 3), round(p["c"], 3), p["level"]) for p in plane(W)[0]])
        print(f"  planted noise {sigma}: k sets {sorted(set(tuple(x[0] for x in r if x[3]) for r in rs))}; mean a by level {np.round(np.mean([[x[1] for x in r] for r in rs if len(r) == 2], axis=0), 3) if any(len(r) == 2 for r in rs) else None}; mean c {np.round(np.mean([[x[2] for x in r] for r in rs if len(r) == 2], axis=0), 3) if any(len(r) == 2 for r in rs) else None}")
    for name, B in (("ring 64", inner("ring", 64, rng)), ("complete 64", np.ones((64, 64)) - np.eye(64))):
        for sigma in (0.05, 0.2):
            ks = []
            for _ in range(10):
                W = noisy(B, sigma, rng); W = (W + W.T) / 2
                pts, _ = plane(W)
                ks.append(tuple((p["k"], p["level"]) for p in pts))
            print(f"  {name} noise {sigma}: outcomes {sorted(set(ks))[:5]}; any level {np.mean([any(x[1] for x in t) for t in ks]):.2f}")

    print("\nW7 factorial design")
    A_, C_ = [], []
    for topo in ("complete", "ring"):
        for s_ in (0.003, 0.01, 0.03, 0.1, 0.3, 0.6):
            for patt, p in (("complete", 6), ("ring", 12), ("path", 12), ("none", 6)):
                W = compose([inner(topo, 16, rng) for _ in range(p)], pattern(patt, p, rng), s_ if patt != "none" else 0.0, rng)
                pts, _ = plane(W)
                A_.append(pts[-1]["a"]); C_.append(pts[-1]["c"])
    A_, C_ = np.array(A_), np.array(C_)
    print(f"  {len(A_)} cases; Spearman(a, c) = {spearmanr(A_, C_).statistic:.3f}; quadrants (a high/low, c high/low): "
          f"HH {((A_ > .5) & (C_ > .5)).sum()}, HL {((A_ > .5) & (C_ <= .5)).sum()}, LH {((A_ <= .5) & (C_ > .5)).sum()}, LL {((A_ <= .5) & (C_ <= .5)).sum()}")

    print("\nW8 capacity law, measured directly")
    for topo, m in (("complete", 4), ("complete", 8), ("complete", 16), ("complete", 32), ("ring", 8), ("ring", 16), ("ring", 32)):
        h = norm_gap(inner(topo, m, rng))
        predicted = h / (1 + h)
        lo, hi = 1e-4, 0.95
        def diff(s_):
            W = compose([inner(topo, m, rng) for _ in range(24)], pattern("complete", 24, rng), s_, rng)
            r_mix, r_esc = rates(W, list(range(m)), rng)
            return r_mix - r_esc
        for _ in range(16):
            mid = np.sqrt(lo * hi)
            d = diff(mid)
            if np.isnan(d):
                break
            if d > 0:
                lo = mid
            else:
                hi = mid
        crossing = np.sqrt(lo * hi)
        print(f"  {topo:8} m={m:3}: h={h:.4f}; predicted s*={predicted:.4f}; measured {crossing:.4f}; ratio {crossing / predicted:.3f}")


def battery_corrected(seed):
    kind, W = random_graph(seed)
    if (W.sum(1) <= 0).any():
        return []
    points, _ = plane(W)
    rng = np.random.default_rng(seed)
    s = W.sum(1)
    out = []
    for pt in points:
        pl, ct = truth(W, pt["parts"], pt["parents"], rng)
        v = np.mean([s[p].sum() / s.sum() for p in pt["parts"] for _ in p])  # site-weighted share of the whole held by a site's part
        out.append(dict(kind=str(kind), a=pt["a"], c=pt["c"], level=pt["level"], plateau=(pl - v) / max(1 - v, 1e-9), c_true=ct))
    return out


def followups():
    """POST HOC, after the first run. The definitions above are unchanged. Reasons for each part are given in the record:
    W8's measurement had a bug (a wrong index in rates), the planted shares in W1, W4 and W6 were not well separated,
    W6 did not print its shifts, plateau was inflated when one part was nearly the whole system, and the no-level fallback
    drove the a-c correlation in W7."""
    rng = np.random.default_rng(20261105)
    print("G1 capacity law, with the index fixed")
    for topo, m in (("complete", 4), ("complete", 8), ("complete", 16), ("complete", 32), ("ring", 8), ("ring", 16), ("ring", 32), ("sparse", 16), ("sparse", 32)):
        trials = []
        for rep in range(3 if topo == "sparse" else 1):
            block = inner(topo, m, rng)
            h = norm_gap(block)
            predicted = h / (1 + h)
            lo, hi = 1e-4, 0.95
            fail = False
            for _ in range(16):
                mid = np.sqrt(lo * hi)
                W = compose([block.copy() for _ in range(24)], pattern("complete", 24, rng), mid, rng)
                r_mix, r_esc = rates(W, list(range(m)), rng)
                d = r_mix - r_esc
                if np.isnan(d):
                    fail = True
                    break
                if d > 0:
                    lo = mid
                else:
                    hi = mid
            trials.append((h, predicted, np.nan if fail else np.sqrt(lo * hi)))
        h, predicted, measured = np.nanmean(np.array(trials), axis=0)
        print(f"  {topo:8} m={m:3}: h={h:.4f}; predicted s*={predicted:.4f}; measured {measured:.4f}; ratio {measured / predicted:.3f}")

    print("\nG2 corners, size and recursion with well-separated shares (outer share much smaller than inner)")
    for shares in ([0.1, 0.002], [0.2, 0.01], [0.05, 0.001], [0.3, 0.01]):
        W = planted([4, 4, 4], shares, rng)
        pts = show(f"4x4x4 shares {shares}", W)
        lv = [p for p in pts if p["level"]]
        if len(lv) >= 2:
            qp, _ = plane(quotient(W, lv[0]["parts"]))
            match = [p for p in qp if p["k"] == lv[1]["k"]]
            print(f"     recursion: outer level original a={lv[1]['a']:.3f} c={lv[1]['c']:.3f}; quotient " + (f"a={match[0]['a']:.3f} c={match[0]['c']:.3f}" if match else "no matching level"))
    for m in (3, 4, 5, 6):
        show(f"{m}x{m}x{m} shares [0.1, 0.002]", planted([m, m, m], [0.1, 0.002], rng))
    print("  depth, same shares at each step, as global lambda_2 falls:")
    for depth, sizes, shares in ((2, [4, 4], [0.02]), (3, [4, 4, 4], [0.1, 0.002]), (4, [4, 4, 4, 4], [0.2, 0.01, 0.0005])):
        W = planted(sizes, shares, rng)
        pts = show(f"depth {depth}", W)
        print(f"     global lambda_2 = {spectrum(W)[0][1]:.2e}")
    print("  long chains of parts, for comparison, c by number of parts:")
    for p in (6, 12, 24, 48):
        show(f"{p} complete blocks in a ring", compose([inner("complete", 8, rng) for _ in range(p)], pattern("ring", p, rng), 0.02, rng))

    print("\nG3 stability, printing the shifts")
    base = planted([4, 4, 4], [0.1, 0.002], rng)
    b0, _ = plane(base)
    print("  base:", [(p["k"], round(p["a"], 3), round(p["c"], 3)) for p in b0])
    for sigma in (0.05, 0.1, 0.2, 0.4, 0.8):
        rows = []
        kset = set()
        for _ in range(12):
            W = noisy(base, sigma, rng); W = (W + W.T) / 2
            pts, _ = plane(W)
            kset.add(tuple(p["k"] for p in pts if p["level"]))
            rows.append({p["k"]: (p["a"], p["c"]) for p in pts})
        txt = []
        for p in b0:
            vals = [r[p["k"]] for r in rows if p["k"] in r]
            if vals:
                txt.append(f"k={p['k']}: da {np.mean([abs(v[0] - p['a']) for v in vals]):.3f} dc {np.mean([abs(v[1] - p['c']) for v in vals]):.3f} ({len(vals)}/12)")
        print(f"  noise {sigma}: level sets {sorted(kset)}; " + "; ".join(txt))

    print("\nG4 independence, accepted levels only, and direct truth with plateau corrected for part size")
    A_, C_ = [], []
    for topo in ("complete", "ring"):
        for s_ in (0.003, 0.01, 0.03, 0.1, 0.3, 0.6):
            for patt, p in (("complete", 6), ("ring", 12), ("path", 12), ("none", 6)):
                W = compose([inner(topo, 16, rng) for _ in range(p)], pattern(patt, p, rng), s_ if patt != "none" else 0.0, rng)
                pts, _ = plane(W)
                for q in pts:
                    if q["level"] and q["k"] == p:
                        A_.append(q["a"]); C_.append(q["c"])
    A_, C_ = np.array(A_), np.array(C_)
    print(f"  factorial, level at the planted k: {len(A_)} of 48 cases; Spearman(a, c) = {spearmanr(A_, C_).statistic:.3f}; HH {((A_ > .5) & (C_ > .5)).sum()}, HL {((A_ > .5) & (C_ <= .5)).sum()}")
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        res = [r for rs in pool.imap_unordered(battery_corrected, range(300), chunksize=4) for r in rs]
    res = [r for r in res if not np.isnan(r["c"])]
    a, c, pl, ct = (np.array([r[k] for r in res]) for k in ("a", "c", "plateau", "c_true"))
    print(f"  all {len(res)} points: Spearman(a, corrected plateau) = {spearmanr(a, pl).statistic:.3f}; Spearman(c, c_true) = {spearmanr(c, ct).statistic:.3f}; Spearman(a, c) = {spearmanr(a, c).statistic:.3f}")
    lv = np.array([r["level"] for r in res])
    print(f"  accepted levels only ({lv.sum()}): Spearman(a, corrected plateau) = {spearmanr(a[lv], pl[lv]).statistic:.3f}; Spearman(c, c_true) = {spearmanr(c[lv], ct[lv]).statistic:.3f}; Spearman(a, c) = {spearmanr(a[lv], c[lv]).statistic:.3f}")
    for kind in sorted({r["kind"] for r in res}):
        g_ = [r for r in res if r["kind"] == kind]
        print(f"  {kind:10} accepted {np.mean([r['level'] for r in g_]):.2f}; a {np.mean([r['a'] for r in g_]):.3f}; corrected plateau {np.mean([r['plateau'] for r in g_]):.3f}")


def plane2(W):
    """THIRD PASS definition. a = volume-weighted mean of A(S) alone. g_k no longer multiplies it; it gates whether a level
    exists (g_k > 1/2 and a > 1/2). Prompted by W7: g_k depends on the pattern among parts, which tied a to c."""
    rows, lam = level_table(W)
    s = W.sum(1)
    whole = [list(range(len(W)))]
    for r in rows:
        vols = np.array([s[p].sum() for p in r["parts"]])
        A = np.array([autonomy_part(W, s, p) for p in r["parts"]])
        r["a2"] = float((A * vols).sum() / vols.sum())
    accepted = sorted([r for r in rows if r["g"] > 0.5 and r["a2"] > 0.5], key=lambda r: r["k"])
    out = []
    parents = whole
    for r in accepted:
        c = integration(W, r["parts"], parents, s)
        if np.isnan(c):
            continue
        out.append(dict(k=r["k"], a=r["a2"], g=r["g"], c=c, parts=r["parts"], parents=parents, level=True))
        parents = r["parts"]
    return out[::-1]


def battery2(seed):
    kind, W = random_graph(seed)
    if (W.sum(1) <= 0).any():
        return (str(kind), [])
    pts = plane2(W)
    rng = np.random.default_rng(seed)
    s = W.sum(1)
    out = []
    for pt in pts:
        pl, ct = truth(W, pt["parts"], pt["parents"], rng)
        v = np.mean([s[p].sum() / s.sum() for p in pt["parts"] for _ in p])
        out.append(dict(a=pt["a"], c=pt["c"], plateau=(pl - v) / max(1 - v, 1e-9), c_true=ct))
    return (str(kind), out)


def slow_mode_rates(W, S, block):
    """Start uniform on block S, measure escape. Start with S's slowest internal mode added, measure its conditional decay."""
    lam, V, s, inv = spectrum(W)
    sq = np.sqrt(s)
    S = list(S)
    d = block.sum(1)
    Kb = np.eye(len(S)) - block / np.sqrt(np.outer(d, d))
    lb, Vb = np.linalg.eigh(Kb)
    phi = Vb[:, 1] / np.sqrt(d)
    base = s[S] / s[S].sum()
    phi = phi - (phi * base).sum()
    eps = 0.5 / np.abs(phi).max()
    n = len(W)
    ts = np.geomspace(1e-3, 1e5, 400)
    p0 = np.zeros(n); p0[S] = base
    p1 = np.zeros(n); p1[S] = base * (1 + eps * phi)
    def evolve_(p, t):
        return sq * (V @ (np.exp(-lam * t) * (V.T @ (p / sq))))
    stay, amp = [], []
    for t in ts:
        a0 = evolve_(p0, t)[S]
        a1 = evolve_(p1, t)[S]
        stay.append(a0.sum())
        amp.append(((a1 / a1.sum() - a0 / a0.sum()) * phi).sum())
    stay, amp = np.array(stay), np.array(amp)
    floor = s[S].sum() / s.sum()
    x = (stay - floor) / (1 - floor)
    use = (x < 0.95) & (x > 0.1)
    r_esc = -np.polyfit(ts[use], np.log(x[use]), 1)[0] if use.sum() >= 4 else float("nan")
    y = np.abs(amp) / max(np.abs(amp[0]), 1e-300)
    use = (y < 0.95) & (y > 0.05) & (x > 0.02)
    r_mix = -np.polyfit(ts[use], np.log(y[use]), 1)[0] if use.sum() >= 4 else float("nan")
    return r_mix, r_esc


def third():
    """THIRD PASS, predictions written before it ran.
    X1. With plane2, |Spearman(a, c)| < 0.3 on the factorial design at the planted k.
    X2. On 300 fresh graphs (seeds 1000 to 1299), Spearman(a, corrected plateau) >= 0.8 and Spearman(c, c_true) >= 0.65,
        on accepted levels.
    X3. Capacity with the slow-mode method: with outward relation spread evenly, the crossing lies within 15% of h/(1+h).
        With outward relation through a quarter of the sites, it departs from that law.
    """
    rng = np.random.default_rng(20261106)
    print("X1 factorial, plane2")
    A_, C_ = [], []
    for topo in ("complete", "ring"):
        for s_ in (0.003, 0.01, 0.03, 0.1, 0.3, 0.6):
            for patt, p in (("complete", 6), ("ring", 12), ("path", 12), ("none", 6)):
                W = compose([inner(topo, 16, rng) for _ in range(p)], pattern(patt, p, rng), s_ if patt != "none" else 0.0, rng)
                for q in plane2(W):
                    if q["k"] == p:
                        A_.append(q["a"]); C_.append(q["c"])
    A_, C_ = np.array(A_), np.array(C_)
    print(f"  {len(A_)} levels; Spearman(a, c) = {spearmanr(A_, C_).statistic:.3f}; a range {A_.min():.3f} to {A_.max():.3f}; c range {C_.min():.3f} to {C_.max():.3f}; HH {((A_ > .5) & (C_ > .5)).sum()}, HL {((A_ > .5) & (C_ <= .5)).sum()}")
    print("X2 fresh graphs, plane2")
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        out = list(pool.imap_unordered(battery2, range(1000, 1300), chunksize=4))
    res = [r for _, rs in out for r in rs if not np.isnan(r["c"])]
    a, c, pl, ct = (np.array([r[k] for r in res]) for k in ("a", "c", "plateau", "c_true"))
    print(f"  {len(res)} levels; Spearman(a, corrected plateau) = {spearmanr(a, pl).statistic:.3f}; Spearman(c, c_true) = {spearmanr(c, ct).statistic:.3f}; Spearman(a, c) = {spearmanr(a, c).statistic:.3f}; cross a-c_true {spearmanr(a, ct).statistic:.3f}; c-plateau {spearmanr(c, pl).statistic:.3f}")
    kinds = {}
    for k, rs in out:
        kinds.setdefault(k, []).append(len(rs) > 0)
    print("  graphs with at least one level, by kind:", {k: f"{sum(v)}/{len(v)}" for k, v in sorted(kinds.items())})
    print("X3 capacity, slow-mode method")
    for contact in ("all", "few"):
        for topo, m in (("complete", 8), ("complete", 16), ("complete", 32), ("ring", 8), ("ring", 16), ("ring", 32), ("sparse", 16), ("sparse", 32)):
            block = inner(topo, m, rng)
            h = norm_gap(block)
            predicted = h / (1 + h)
            lo, hi = 1e-4, 0.95
            fail = False
            for _ in range(18):
                mid = np.sqrt(lo * hi)
                W = compose([block.copy() for _ in range(32)], pattern("complete", 32, rng), mid, np.random.default_rng(7), contact=contact)
                r_mix, r_esc = slow_mode_rates(W, list(range(m)), W[:m, :m])
                d = r_mix - r_esc
                if np.isnan(d):
                    fail = True
                    break
                if d > 0:
                    lo = mid
                else:
                    hi = mid
            measured = float("nan") if fail else np.sqrt(lo * hi)
            print(f"  contact={contact:3} {topo:8} m={m:3}: h={h:.4f}; predicted {predicted:.4f}; measured {measured:.4f}; ratio {measured / predicted:.3f}")


if __name__ == "__main__":
    import sys
    if "followups" in sys.argv:
        followups()
    elif "third" in sys.argv:
        third()
    else:
        main()
