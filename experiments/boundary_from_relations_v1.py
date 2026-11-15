"""Can a whole's boundary be derived from relation strengths without picking the system first?

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. Record: plans/graph_from_self_limitation_2026_11_04.md
B1 to B9 were not changed. The followups mode (F1 to F5) is post hoc, written after seeing B1 to B9.

Needs numpy and scipy. Run: python boundary_from_relations_v1.py [followups]
All data are synthetic. Tests the threshold construction in "Deriving Wholeness from First Principles"
(groups = strongly connected components at a strength threshold, then quotient) against two rules with no
strength threshold. The rule names below are mine.

SHARE RULE. Each site's relations sum to its budget. A partition is a level of wholes if every site in every
group sends more than half of its relations inside its own group. Take the finest such partition found by
agglomeration on two-step relation, form the quotient, renormalize, and repeat until none exists. The only
number is the majority, one half.
SPECTRAL RULE. Count wholes from gaps in the low spectrum of K = I - D^-1/2 W D^-1/2.

INDEPENDENT TRUTH, DYNAMICS. A boundary physically holds when an excitation stays inside for longer than it
takes to spread inside. hold = tau_escape / tau_internal_mixing = (1-out) lambda2_internal / out, and wave
energy started inside a group is tracked until it falls below one half, in units of the internal period.

PREDICTIONS, WRITTEN BEFORE ANY RUN OF THIS SCRIPT.
B1. With symmetric relations, reciprocity is vacuous: strongly connected components equal connected components.
B2. Planted hierarchy (4x4x4): an oracle threshold and the share rule both recover all levels.
B3. Hierarchy plus a few strong cross-links: no threshold recovers the truth; the share rule does.
B4. Rings with dense outside relations (each member sends most relation out): the threshold reports wholes with
    high internal cut strength, but hold < 1; the share rule reports none.
B5. Complete graph with noise: thresholds give a full dendrogram of n-1 merges; the share rule reports none.
B6. Noisy ring: the share rule reports spurious arcs with thin margins and hold near or below 1, so the majority
    alone is not enough; the margin matters. Clean ring: none.
B7. Directed feed-forward layers: strongly connected components correctly report no wholes, and a symmetrized
    share rule wrongly reports some. So reciprocity earns its place only for directed relations.
B8. The quotient of strongly connected components at a fixed threshold is always acyclic, so recursion needs the
    threshold to move. The construction has no fixed-scale recursion.
B9. For a well-mixed block of m sites with outside share s, hold = 1 near s* = m/(2m-1), so one half is where
    escape and mixing cross. For a poorly mixed block (a ring) s* falls far below one half, so the majority
    rule is a statement about well-mixed wholes, not a general law.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

rng = np.random.default_rng(20261104)


def comps(W, t, strong=False):
    n, lab = connected_components(csr_matrix((W > t).astype(int)), directed=strong, connection="strong")
    return lab


def as_partition(lab):
    groups = {}
    for i, l in enumerate(lab):
        groups.setdefault(int(l), []).append(i)
    return frozenset(frozenset(g) for g in groups.values())


def threshold_levels(W):
    ts = np.unique(W[W > 0])
    levels = []
    last = None
    for t in np.concatenate(([0.0], ts)):
        p = as_partition(comps(W, t))
        if p != last:
            levels.append((float(t), p))
            last = p
    return levels


def passes(W, groups, margin=0.0):
    s = W.sum(1)
    worst = 1.0
    for g in groups:
        if len(g) < 2:
            return False, 0.0
        g = list(g)
        inside = W[np.ix_(g, g)].sum(1) / np.maximum(s[g], 1e-300)
        worst = min(worst, inside.min())
    return worst > 0.5 + margin, worst


def agglomerate_paths(W):
    """Average-linkage merges on P + P^2, yielding every partition along the path, finest first."""
    n = len(W)
    s = np.maximum(W.sum(1), 1e-300)
    P = W / s[:, None]
    Q = P + P @ P
    Q = (Q + Q.T) / 2
    np.fill_diagonal(Q, 0)
    groups = [[i] for i in range(n)]
    S = Q.copy()
    np.fill_diagonal(S, -1)
    sizes = np.ones(n)
    alive = list(range(n))
    yield [list(g) for g in groups]
    while len(alive) > 1:
        sub = S[np.ix_(alive, alive)]
        a, b = np.unravel_index(np.argmax(sub), sub.shape)
        a, b = alive[a], alive[b]
        na, nb = sizes[a], sizes[b]
        new = (na * S[a] + nb * S[b]) / (na + nb)
        S[a] = new
        S[:, a] = new
        S[a, a] = -1
        sizes[a] = na + nb
        groups[a] = groups[a] + groups[b]
        alive.remove(b)
        yield [groups[i] for i in alive]


def quotient(W, groups):
    k = len(groups)
    R = np.zeros((k, k))
    for i, a in enumerate(groups):
        for j, b in enumerate(groups):
            if i != j:
                R[i, j] = W[np.ix_(a, b)].sum() / len(a)
    return (R + R.T) / 2


def share_levels(W):
    """Finest passing partition, quotient, repeat. Returns levels in original site labels."""
    labels = [[i] for i in range(len(W))]
    current = W.copy()
    out = []
    while len(current) > 2:
        found = None
        for part in agglomerate_paths(current):
            if 1 < len(part) < len(current):
                ok, worst = passes(current, part)
                if ok:
                    found = (part, worst)
                    break
        if found is None:
            break
        part, worst = found
        labels = [sum((labels[i] for i in g), []) for g in part]
        out.append(([list(g) for g in labels], float(worst)))
        current = quotient(current, part)
    return out


def hold_ratio(W, g):
    g = list(g)
    s = W.sum(1)
    inside = W[np.ix_(g, g)]
    out = 1 - inside.sum() / s[g].sum()
    d = inside.sum(1)
    if np.any(d <= 0) or out <= 0:
        return 0.0 if out > 0 else float("inf")
    K = np.eye(len(g)) - inside / np.sqrt(np.outer(d, d))
    lam = np.sort(np.linalg.eigvalsh(K))
    return float((1 - out) * max(lam[1], 0) / out)


def wave_hold(W, g, seed=0):
    """Energy started inside g: time until under half, in units of the internal period."""
    n = len(W)
    s = W.sum(1)
    inv = 1 / np.sqrt(np.maximum(s, 1e-300))
    K = np.diag(s) - W
    K = K / s.mean()
    lam, V = np.linalg.eigh(K)
    om = np.sqrt(np.maximum(lam, 0))
    r = np.random.default_rng(seed)
    g = list(g)
    v0 = np.zeros(n)
    v0[g] = r.normal(0, 1, len(g))
    v0[g] -= v0[g].mean()
    c = V.T @ v0
    total = 0.5 * v0 @ v0
    Wn = W / s.mean()
    inside = np.zeros(n, bool)
    inside[g] = True
    sub = Wn[np.ix_(g, g)]
    dg = sub.sum(1)
    if len(g) < 2 or np.any(dg <= 0):
        return 0.0
    L = np.diag(dg) - sub
    lamg = np.linalg.eigvalsh(L)
    period = 2 * np.pi / np.sqrt(max(lamg[1], 1e-12))
    safe = np.where(om > 1e-9, om, 1.0)
    for t in np.geomspace(0.05, 4000, 500) * period / 10:
        sn = np.where(om > 1e-9, np.sin(om * t) / safe, t)
        q = V @ (c * sn)
        v = V @ (c * np.cos(om * t))
        pot = 0.0
        ii, jj = np.nonzero(Wn)
        d2 = 0.5 * Wn[ii, jj] * (q[ii] - q[jj]) ** 2 * 0.5
        share = (inside[ii].astype(float) + inside[jj].astype(float)) / 2
        pot = (d2 * share).sum()
        e = 0.5 * (v[g] ** 2).sum() + pot
        if e < 0.5 * total:
            return float(t / period)
    return float(4000 / 10)


def internal_cut(W, g):
    """Weakest internal cut of the pasted I(S), by exact minimum over small groups, or a ring/block bound."""
    g = list(g)
    m = len(g)
    if m > 16:
        return float("nan")
    sub = W[np.ix_(g, g)]
    best = float("inf")
    for mask in range(1, 2 ** (m - 1)):
        a = [i for i in range(m) if mask >> i & 1]
        b = [i for i in range(m) if not mask >> i & 1]
        best = min(best, sub[np.ix_(a, b)].sum())
    return float(best)


def spectral(W):
    s = W.sum(1)
    K = np.eye(len(W)) - W / np.sqrt(np.outer(s, s))
    lam = np.sort(np.linalg.eigvalsh(K))
    lam = np.maximum(lam, 1e-14)
    ratios = [(k + 1, lam[k + 1] / lam[k]) for k in range(1, len(lam) - 1)]
    return sorted(ratios, key=lambda x: -x[1])[:3], lam


def planted(levels=(4, 4, 4), w=(1.0, 0.02, 0.0004)):
    n = int(np.prod(levels))
    W = np.zeros((n, n))
    def code(i):
        out = []
        for b in reversed(levels):
            out.append(i % b)
            i //= b
        return out[::-1]
    c = [code(i) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            depth = 0
            while depth < len(levels) and c[i][depth] == c[j][depth]:
                depth += 1
            # depth = shared prefix length: full match minus one is the innermost block
            W[i, j] = W[j, i] = w[len(levels) - 1 - depth] if depth < len(levels) else 0
    truth = []
    for lv in range(len(levels) - 1, 0, -1):
        groups = {}
        for i in range(n):
            groups.setdefault(tuple(c[i][:lv]), []).append(i)
        truth.append(frozenset(frozenset(g) for g in groups.values()))
    return W, truth


def matches(levels, truth):
    got = [frozenset(frozenset(g) for g in part) for part, _ in levels]
    return [t in got for t in truth]


def report(name, W, truth=None, wave=True):
    th = threshold_levels(W)
    nontrivial = [p for _, p in th if 1 < len(p) < len(W)]
    sh = share_levels(W)
    top = spectral(W)[0]
    print(f"\n{name}: n={len(W)}")
    print(f"  threshold: {len(nontrivial)} distinct nontrivial levels", end="")
    if truth:
        print("; oracle recovers truth levels:", [t in [p for _, p in th] for t in truth], end="")
    print()
    print(f"  share rule: {len(sh)} levels; groups per level {[len(p) for p, _ in sh]}; worst inside share {[round(w, 3) for _, w in sh]}", end="")
    if truth:
        print("; recovers truth levels:", matches(sh, truth), end="")
    print()
    print("  largest low-spectrum gaps (k wholes, ratio):", [(k, round(float(r), 2)) for k, r in top])
    return th, sh


def judge(W, part, label):
    holds = [hold_ratio(W, g) for g in part]
    waves = [wave_hold(W, g, i) for i, g in enumerate(part[:6])]
    print(f"  dynamics of {label}: hold median {np.median(holds):.3g} min {np.min(holds):.3g}; wave retention (internal periods) median {np.median(waves):.3g} min {np.min(waves):.3g}")


def main():
    print("Pasted example: A,B and C,D strong (1), weak B->C and D->A (0.2)")
    W = np.zeros((4, 4))
    W[0, 1] = W[1, 0] = W[2, 3] = W[3, 2] = 1
    W[1, 2] = W[3, 0] = 0.2
    print("  SCC at t=0.5:", sorted(map(sorted, as_partition(comps(W, 0.5, True)))), " t=0.1:", sorted(map(sorted, as_partition(comps(W, 0.1, True)))))

    print("\nB1, B8. Random weighted graphs")
    same, acyclic, nested = 0, 0, 0
    for trial in range(200):
        n = 30
        A = rng.random((n, n)) * (rng.random((n, n)) < 0.15)
        np.fill_diagonal(A, 0)
        S = (A + A.T) / 2
        t = 0.2
        same += as_partition(comps(S, t, True)) == as_partition(comps(S, t, False))
        lab = comps(A, t, True)
        k = lab.max() + 1
        Q = np.zeros((k, k))
        for i in range(n):
            for j in range(n):
                if A[i, j] > t and lab[i] != lab[j]:
                    Q[lab[i], lab[j]] = 1
        ncc, qlab = connected_components(csr_matrix(Q), directed=True, connection="strong")
        acyclic += ncc == k
        low = comps(A, 0.05, True)
        hi = lab
        nested += all(len(set(low[hi == h])) == 1 for h in set(hi))
    print(f"  symmetric: SCC equals connected components in {same}/200; quotient at fixed threshold acyclic in {acyclic}/200; higher threshold refines lower in {nested}/200")

    # B2
    W, truth = planted()
    th, sh = report("B2 planted hierarchy 4x4x4", W, truth)
    for t, part in zip(("inner blocks", "outer blocks"), truth):
        judge(W, [sorted(g) for g in part], t)

    # B3
    W2 = W.copy()
    n = len(W2)
    for _ in range(24):
        i, j = rng.integers(n, size=2)
        if i != j and W2[i, j] < 0.5:
            W2[i, j] = W2[j, i] = 1.0
    th, sh = report("B3 hierarchy plus 24 strong cross-links", W2, truth)
    for t, part in zip(("inner blocks", "outer blocks"), truth):
        judge(W2, [sorted(g) for g in part], "truth " + t)
    if th:
        ps = [p for _, p in th if 1 < len(p) < n]
        if ps:
            biggest = max(ps, key=len)
            print(f"  finest threshold partition: {len(biggest)} groups; sizes {sorted(map(len, biggest), reverse=True)[:6]}")

    # B4
    m, r = 8, 8
    n4 = m * r
    W4 = np.full((n4, n4), 0.9)
    np.fill_diagonal(W4, 0)
    rings = []
    for k in range(r):
        members = list(range(k * m, (k + 1) * m))
        rings.append(members)
        for a in range(m):
            i, j = members[a], members[(a + 1) % m]
            W4[i, j] = W4[j, i] = 1.0
    print("\nB4 rings of 1.0 inside dense 0.9 relations")
    p = as_partition(comps(W4, 0.95))
    print(f"  threshold at 0.95: {len(p)} groups, sizes {sorted(map(len, p))[:3]}; internal cut I(S) at that threshold {internal_cut((W4 > 0.95) * W4, rings[0]):.2f}; full-weight I(S) {internal_cut(W4, rings[0]):.2f}")
    share = W4[np.ix_(rings[0], rings[0])].sum(1)[0] / W4[rings[0][0]].sum()
    print(f"  inside share of a member: {share:.3f}")
    sh = share_levels(W4)
    print(f"  share rule: {len(sh)} levels; {[len(q) for q, _ in sh]}")
    judge(W4, rings, "rings")
    print("  largest gaps:", [(k, round(float(x), 2)) for k, x in spectral(W4)[0]])

    # B5
    n5 = 64
    g = rng.normal(0, 1, (n5, n5))
    W5 = np.exp(0.05 * (g + g.T) / np.sqrt(2))
    np.fill_diagonal(W5, 0)
    report("B5 complete graph with 5% noise", W5)

    # B6
    n6 = 64
    W6 = np.zeros((n6, n6))
    for i in range(n6):
        W6[i, (i + 1) % n6] = W6[(i + 1) % n6, i] = 1
    report("B6 clean ring", W6)
    W6n = W6.copy()
    for i in range(n6):
        x = float(np.exp(0.1 * rng.normal()))
        W6n[i, (i + 1) % n6] = W6n[(i + 1) % n6, i] = x
    th, sh = report("B6 noisy ring (10%)", W6n)
    if sh:
        judge(W6n, sh[0][0], "share-rule arcs")

    # B7
    layers, width = 8, 8
    n7 = layers * width
    W7 = np.zeros((n7, n7))
    for l in range(layers - 1):
        for a in range(width):
            for b in range(width):
                W7[l * width + a, (l + 1) * width + b] = 1
    p = as_partition(comps(W7, 0.5, True))
    print(f"\nB7 feed-forward layers: SCC gives {len(p)} groups of size {max(map(len, p))}")
    sym = (W7 + W7.T) / 2
    sh = share_levels(sym)
    print(f"  symmetrized share rule: {len(sh)} levels; {[len(q) for q, _ in sh]}; worst inside share {[round(w, 3) for _, w in sh]}")

    # B9
    print("\nB9. Where hold = 1, as outside share s varies, for one block inside a bath")
    def block_hold(kind, m, s):
        # inside relation total (1-s) per site, outside s spread over a large bath
        if kind == "complete":
            inner = (np.ones((m, m)) - np.eye(m)) * (1 - s) / (m - 1)
        else:
            inner = np.zeros((m, m))
            for i in range(m):
                inner[i, (i + 1) % m] = inner[(i + 1) % m, i] = (1 - s) / 2
        d = inner.sum(1)
        K = np.eye(m) - inner / np.sqrt(np.outer(d, d))
        lam = np.sort(np.linalg.eigvalsh(K))
        return (1 - s) * lam[1] / s
    for kind in ("complete", "ring"):
        for m in (2, 4, 8, 16, 32, 64):
            if kind == "ring" and m < 4:
                continue
            lo, hi = 1e-6, 1 - 1e-6
            for _ in range(60):
                mid = (lo + hi) / 2
                if block_hold(kind, m, mid) > 1:
                    lo = mid
                else:
                    hi = mid
            extra = f" predicted {m / (2 * m - 1):.4f}" if kind == "complete" else ""
            print(f"  {kind:8} m={m:3}: s* = {lo:.4f}{extra}")


def followups():
    """POST HOC. Added after the first run, because B3, B6 and B7 did not come out as predicted, and because wave
    retention stayed at its cap in B4 while hold was below 1. These are not frozen predictions."""
    r = np.random.default_rng(20261104 + 1)

    def random_groups(n, size, count):
        return [list(r.choice(n, size=size, replace=False)) for _ in range(count)]

    print("F1. Criterion against search on the strong cross-link case, over 8 random placements")
    W, truth = planted()
    n = len(W)
    inner = [sorted(g) for g in truth[0]]
    for trial in range(8):
        W2 = W.copy()
        for _ in range(24):
            i, j = r.integers(n, size=2)
            if i != j and W2[i, j] < 0.5:
                W2[i, j] = W2[j, i] = 1.0
        ok, worst = passes(W2, inner)
        sh = share_levels(W2)
        first = sh[0][0] if sh else []
        intact = sum(1 for g in first if frozenset(g) in truth[0])
        cross_blocks = sum(1 for g in first if any(set(g) >= set(t) for t in inner) and frozenset(g) not in truth[0])
        print(f"  trial {trial}: truth passes majority {ok} (worst {worst:.3f}); search found {len(first)} groups, {intact} exactly true, {cross_blocks} merged blocks; "
              f"gap at 16: {dict((k, round(float(x), 2)) for k, x in spectral(W2)[0]).get(16, 'not top 3')}; truth hold min {min(hold_ratio(W2, g) for g in inner):.2f}")

    print("\nF2. Wave retention against random sets of the same size (internal periods, cap 400)")
    for name, Wx, groups in [
        ("planted inner", W, inner),
        ("planted outer", W, [sorted(g) for g in truth[1]]),
    ]:
        size = len(groups[0])
        a = [wave_hold(Wx, g, i) for i, g in enumerate(groups[:6])]
        b = [wave_hold(Wx, g, i) for i, g in enumerate(random_groups(len(Wx), size, 6))]
        h = [hold_ratio(Wx, g) for g in random_groups(len(Wx), size, 6)]
        print(f"  {name}: groups {np.median(a):.3g}; random sets {np.median(b):.3g}; random-set hold {np.median(h):.3g}")
    m, k = 8, 8
    W4 = np.full((m * k, m * k), 0.9)
    np.fill_diagonal(W4, 0)
    rings = []
    for q in range(k):
        mem = list(range(q * m, (q + 1) * m))
        rings.append(mem)
        for a_ in range(m):
            i, j = mem[a_], mem[(a_ + 1) % m]
            W4[i, j] = W4[j, i] = 1.0
    a = [wave_hold(W4, g, i) for i, g in enumerate(rings[:6])]
    b = [wave_hold(W4, g, i) for i, g in enumerate(random_groups(m * k, m, 6))]
    print(f"  dense rings: groups {np.median(a):.3g}; random sets {np.median(b):.3g}")
    K = np.diag(W4.sum(1)) - W4
    lam = np.linalg.eigvalsh(K / W4.sum(1).mean())
    print(f"  dense rings spectrum: bandwidth of nonzero modes {lam[-1] - lam[1]:.4f} around {lam[1:].mean():.4f}, so a wave barely moves")

    print("\nF3. Noisy ring, cutting by hand at bonds weaker than both neighbours")
    n6 = 64
    for noise in (0.01, 0.1, 0.5):
        holds, worsts = [], []
        for trial in range(20):
            x = np.exp(noise * r.normal(size=n6))
            W6 = np.zeros((n6, n6))
            for i in range(n6):
                W6[i, (i + 1) % n6] = W6[(i + 1) % n6, i] = x[i]
            cuts = [i for i in range(n6) if x[i] < x[i - 1] and x[i] < x[(i + 1) % n6]]
            arcs = []
            for a_, b_ in zip(cuts, cuts[1:] + [cuts[0] + n6]):
                arcs.append([(i % n6) for i in range(a_ + 1, b_ + 1)])
            ok, worst = passes(W6, arcs)
            if ok:
                worsts.append(worst)
                holds += [hold_ratio(W6, g) for g in arcs]
        print(f"  noise {noise}: partition passes majority in {len(worsts)}/20 trials; worst inside share {np.median(worsts) if worsts else float('nan'):.3f}; hold median {np.median(holds) if holds else float('nan'):.2f}, fraction of arcs with hold>1 {np.mean(np.array(holds) > 1) if holds else float('nan'):.2f}")

    print("\nF4. Feed-forward layers with alternating forward strength, so ties break")
    layers, width = 8, 8
    n7 = layers * width
    W7 = np.zeros((n7, n7))
    for l in range(layers - 1):
        for a_ in range(width):
            for b_ in range(width):
                W7[l * width + a_, (l + 1) * width + b_] = 1.0 if l % 2 == 0 else 0.3
    p = as_partition(comps(W7, 0.0, True))
    sh = share_levels((W7 + W7.T) / 2)
    print(f"  SCC groups {len(p)} of size {max(map(len, p))}; symmetrized share rule levels {[len(q) for q, _ in sh]}, worst share {[round(w, 3) for _, w in sh]}")

    print("\nF5. Does a whole collapse to a point in low-mode space? Spread inside groups over distance between groups")

    def embed(Wx, k):
        s = Wx.sum(1)
        Kx = np.eye(len(Wx)) - Wx / np.sqrt(np.outer(s, s))
        lamx, Vx = np.linalg.eigh(Kx)
        return Vx[:, :k] / np.sqrt(s)[:, None]

    def collapse(X, groups):
        cents = np.array([X[g].mean(0) for g in groups])
        within = np.sqrt(np.mean([((X[g] - c) ** 2).sum(1).mean() for g, c in zip(groups, cents)]))
        d = np.sqrt(((cents[:, None] - cents[None]) ** 2).sum(2))
        between = np.median(d[np.triu_indices(len(groups), 1)])
        return within / between

    def cluster(X, k):
        n_ = len(X)
        groups = [[i] for i in range(n_)]
        D = np.sqrt(((X[:, None] - X[None]) ** 2).sum(2))
        np.fill_diagonal(D, np.inf)
        sizes = np.ones(n_)
        alive = list(range(n_))
        while len(alive) > k:
            sub = D[np.ix_(alive, alive)]
            a_, b_ = np.unravel_index(np.argmin(sub), sub.shape)
            a_, b_ = alive[a_], alive[b_]
            new = (sizes[a_] * D[a_] + sizes[b_] * D[b_]) / (sizes[a_] + sizes[b_])
            D[a_] = new
            D[:, a_] = new
            D[a_, a_] = np.inf
            sizes[a_] += sizes[b_]
            groups[a_] += groups[b_]
            alive.remove(b_)
        return frozenset(frozenset(groups[i]) for i in alive)

    outer = [sorted(g) for g in truth[1]]
    print(f"  planted, 16 low modes, inner blocks: {collapse(embed(W, 16), inner):.2e}; 4 low modes, inner blocks: {collapse(embed(W, 4), inner):.2e}; 4 low modes, outer blocks: {collapse(embed(W, 4), outer):.2e}")
    print(f"  planted, 64 modes (all), inner blocks: {collapse(embed(W, 64), inner):.3f}")
    print(f"  planted, clustering in low modes recovers: inner {cluster(embed(W, 16), 16) == truth[0]}, outer {cluster(embed(W, 4), 4) == truth[1]}")
    hits = []
    fr = []
    for trial in range(8):
        W2 = W.copy()
        for _ in range(24):
            i, j = r.integers(n, size=2)
            if i != j and W2[i, j] < 0.5:
                W2[i, j] = W2[j, i] = 1.0
        got = cluster(embed(W2, 16), 16)
        hits.append(got == truth[0])
        fr.append(len(got & truth[0]) / 16)
    print(f"  with 24 strong cross-links, clustering in 16 low modes: exact in {sum(hits)}/8 trials, mean fraction of blocks exact {np.mean(fr):.2f}")
    W6 = np.zeros((64, 64))
    for i in range(64):
        W6[i, (i + 1) % 64] = W6[(i + 1) % 64, i] = 1
    arcs16 = [list(range(q * 4, (q + 1) * 4)) for q in range(16)]
    arcs4 = [list(range(q * 16, (q + 1) * 16)) for q in range(4)]
    print(f"  clean ring, any arcs: 16 modes, 16 arcs {collapse(embed(W6, 16), arcs16):.3f}; 4 modes, 4 arcs {collapse(embed(W6, 4), arcs4):.3f}")
    Wk = np.ones((64, 64)) - np.eye(64)
    print(f"  complete graph, 4 modes, 4 arbitrary groups: {collapse(embed(Wk + 1e-9 * r.random((64, 64)) * 0, 4), arcs4):.3f}")


if __name__ == "__main__":
    import sys
    if "followups" in sys.argv:
        followups()
    else:
        main()
