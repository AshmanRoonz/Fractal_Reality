"""Can "one energy, self-limiting" produce the graph? Tests of each step, with predictions frozen first.

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. Record: plans/graph_from_self_limitation_2026_11_04.md
A first run crashed when a site lost every relation, so the isolated-site handling was fixed.
The predictions below were not changed. Parts edge, closure and holdout came after the first round, as marked below.

Needs numpy and scipy. Run: python graph_from_self_limitation_v1.py OUTDIR [part ...]
Parts: threshold matrix cap mix families edge closure holdout. All data are synthetic; nothing here is a measurement.

SETUP. n sites, symmetric weights w_ij >= 0, zero diagonal, started from the complete graph with small
random noise. Two budgets. GLOBAL: one total shared by all (a part holds a piece of the 1). SITE: every
row sums to 1 (each part is the whole 1, the corpus's "not a piece of it, but the whole thing").
Each step: w' = w^(1-eta) * f^eta, then renormalize to the budget.
Rules for f. gamma selects how energy is shared among modes, E_k ~ lambda_k^-gamma, and e_ij is the energy
in edge ij: gamma=1 equal energy per mode (e_ij = w_ij R_ij, Foster's theorem gives sum = n-1),
gamma=1/2 ground-state fluctuations, gamma=0 equal amplitude per mode (e_ij = 2 w_ij, plain self-reinforcement).
f = e^beta. The closure rule uses f = (P^2)^beta. The mixed rule uses f = e^(beta(1-theta)) (P^2)^(beta theta).

PREDICTIONS, WRITTEN BEFORE ANY RUN OF THIS SCRIPT.
P1. The complete graph is a fixed point for every rule (symmetry) and loses stability only near beta = 1
    (per-step amplification about beta(1 - O(1/n))).
P2. GLOBAL + gamma=0 + beta>1 collapses onto very few edges and disconnects.
P3. SITE + gamma=0 + beta>1 ends in disjoint pairs and odd cycles (Birkhoff and Katz), never connected for n>3.
P4. GLOBAL + gamma=1 + beta>1 ends in a connected spanning tree, m = n-1, in all runs.
P5. SITE + gamma=1 + beta>1 ends connected in all runs, mean degree at most 2.2, with Hamiltonian rings
    in the majority of runs at n<=64, and diameter growing at least as n^0.5.
    Failure of P5 means the closed line is a static theorem only, not something the dynamics reach.
P6. A weak bridge has e ~ w^(1-gamma), so it survives only if beta(1-gamma) < 1. Sparse and connected together
    therefore need 1 < beta < 1/(1-gamma): empty for gamma=0, (1,2) for gamma=1/2, (1,inf) for gamma=1.
    So gamma=1/2 stays connected at beta=1.5 and disconnects at beta=3.
P7. SITE + gamma=1 with each relation capped at 1/k, k>=3: the end state is expander-like, indistinguishable
    from a random k-regular graph (lambda_2 roughly constant in n, diameter about log n, clustering near zero).
    Energy reinforcement favors long shortcuts, so locality is NOT produced above degree 2.
P8. Closure rule alone gives disjoint clusters (wholes with no greater whole). Mixing closure with energy
    produces no d>=2 lattice; at best chains of clusters, one-dimensional at large scale.
P9. Families: ring and tori pass every test. Sierpinski gasket passes interior and growth tests but has
    walk dimension near 2.32 and spectral gaps at all scales. Hierarchical hypercube has gaps at all scales.
    Random regular graphs, rings glued at random, and the complete graph fail the interior test.

SECOND ROUND. Written after the first round's results and before these parts ran. Post hoc in choice of question.
First-round outcome that prompted them: P5 failed (no rings beyond n=16, diameter ~ n^0.27); at gamma=1/2, beta=1.5
diameter grew near n^0.74; and the strict closure rule kills any edge with no shared neighbour.
Q1. (part edge) Near the disconnection edge at gamma=1/2, as beta rises toward 2, mean degree falls toward 2 and the
    diameter exponent rises toward 1, with Hamiltonian rings appearing at n>=32 for beta>=1.8.
Q2. (part closure) With soft closure P + P^2 and strict closure P^2, and theta in (0, 1/2), clustering rises and the graph
    departs from random regular, with larger diameter and smaller lambda_2.
Q3. (part holdout) Exponents fitted at n<=256 do not hold at n=1024: a log-n fit predicts the diameter better than a
    power-law fit, so this is a clustered small world, not a finite-dimensional geometry.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json, sys, time
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path

ETA = 0.5
SUPPORT = 1e-5


def start(n, noise, rng):
    g = rng.normal(0, 1, (n, n))
    g = (g + g.T) / np.sqrt(2)
    w = np.exp(noise * g)
    np.fill_diagonal(w, 0)
    return w / (n - 1)


def sinkhorn(w, iters=200, tol=1e-11):
    d = np.ones(len(w))
    live = w.sum(1) > 0  # a site with no relations left stays isolated
    for _ in range(iters):
        s = w @ d
        d[live] = np.sqrt(d[live] / np.maximum(s[live], 1e-280))
        d = np.minimum(d, 1e100)
        if np.max(np.abs((d * (w @ d) - 1)[live]), initial=0.0) < tol:
            break
    return np.nan_to_num(w * np.outer(d, d), nan=0.0, posinf=0.0)


def normalize(w, budget, cap=None):
    if budget == "global":
        return w * (len(w) / 2) / (w.sum() / 2)
    if cap is None:
        return sinkhorn(w)
    for _ in range(60):
        w = sinkhorn(np.minimum(w, cap), iters=20)
        if w.max() <= cap * (1 + 1e-7):
            break
    return w


def edge_energy(w, gamma):
    L = np.diag(w.sum(1)) - w
    vals, vecs = np.linalg.eigh(L)
    vals = np.maximum(vals[1:], 1e-12)
    vecs = vecs[:, 1:]
    C = (vecs * vals ** (-gamma)) @ vecs.T
    D = np.diag(C)
    return w * (D[:, None] + D[None, :] - 2 * C)


def closure(w, soft=False):
    P2 = w @ w
    if soft:
        P2 = P2 + w
    np.fill_diagonal(P2, 0)
    return P2


def step(w, budget, gamma, beta, theta=0.0, cap=None, eta=ETA, soft=False):
    logf = np.zeros_like(w)
    mask = w > 0
    if theta < 1:
        logf[mask] += beta * (1 - theta) * np.log(np.maximum(edge_energy(w, gamma)[mask], 1e-300))
    if theta > 0:
        logf[mask] += beta * theta * np.log(np.maximum(closure(w, soft)[mask], 1e-300))
    new = np.zeros_like(w)
    new[mask] = np.exp((1 - eta) * np.log(w[mask]) + eta * logf[mask])
    new = normalize(new, budget, cap)
    new[new < 1e-12] = 0
    return (new + new.T) / 2


def describe(w):
    n = len(w)
    A = (w > SUPPORT).astype(int)
    np.fill_diagonal(A, 0)
    deg = A.sum(1)
    m = int(A.sum() // 2)
    sp = csr_matrix(A)
    ncomp, labels = connected_components(sp, directed=False)
    sizes = sorted(Counter(labels.tolist()).values(), reverse=True)
    big = np.argmax(np.bincount(labels))
    idx = np.flatnonzero(labels == big)
    dist = shortest_path(sp[idx][:, idx], unweighted=True, directed=False)
    tri = np.trace(A @ A @ A) / 6
    trip = (deg * (deg - 1) / 2).sum()
    s = w.sum(1)
    inv = np.where(s > 0, 1 / np.sqrt(np.where(s > 0, s, 1)), 0.0)
    K = np.eye(n) - w * np.outer(inv, inv)
    lam = np.linalg.eigvalsh(K)
    edge_w = w[np.triu_indices(n, 1)]
    edge_w = edge_w[edge_w > SUPPORT]
    comp_kinds = Counter()
    for c in range(ncomp):
        members = np.flatnonzero(labels == c)
        d = deg[members]
        size = len(members)
        if size == 1:
            comp_kinds["single"] += 1
        elif size == 2:
            comp_kinds["pair"] += 1
        elif np.all(d == 2):
            comp_kinds["odd_cycle" if size % 2 else "even_cycle"] += 1
        elif A[members][:, members].sum() // 2 == size - 1:
            comp_kinds["tree"] += 1
        else:
            comp_kinds["other"] += 1
    return dict(n=n, m=m, components=int(ncomp), sizes=sizes[:6], kinds=dict(comp_kinds),
                mean_degree=float(deg.mean()), max_degree=int(deg.max()), diameter=float(dist.max()),
                mean_distance=float(dist[np.triu_indices(len(idx), 1)].mean()) if len(idx) > 1 else 0.0,
                clustering=float(3 * tri / trip) if trip else 0.0, lambda2=float(lam[1]),
                ring=bool(ncomp == 1 and np.all(deg == 2)), tree=bool(ncomp == 1 and m == n - 1),
                min_w=float(edge_w.min()) if len(edge_w) else 0.0, max_w=float(edge_w.max()) if len(edge_w) else 0.0)


def evolve(job):
    budget, gamma, beta, theta, cap, n, seed, maxit, noise = job
    rng = np.random.default_rng(abs(hash((n, seed, round(beta * 100), round(gamma * 10), budget == "site", round(theta * 100), round((cap or 0) * 1000)))) % (2 ** 32))
    w = normalize(start(n, noise, rng), budget, cap)
    it = 0
    converged = False
    for it in range(1, maxit + 1):
        new = step(w, budget, gamma, beta, theta, cap)
        if it % 10 == 0:
            on = (new > SUPPORT) | (w > SUPPORT)
            if on.any():
                delta = np.abs(new[on] - w[on]) / np.maximum(w[on], SUPPORT)
                if delta.max() < 1e-7:
                    w = new
                    converged = True
                    break
        w = new
    out = describe(w)
    out.update(budget=budget, gamma=gamma, beta=beta, theta=theta, cap=cap, seed=seed, iters=it, converged=converged)
    return out


def evolve2(job):
    """Second-round runs: as evolve, with soft closure allowed, plus geometry metrics on the largest component."""
    budget, gamma, beta, theta, cap, n, seed, maxit, soft = job
    rng = np.random.default_rng([n, seed, int(beta * 1000), int(gamma * 100), int(theta * 1000), int((cap or 0) * 1000), int(soft)])
    w = normalize(start(n, 0.05, rng), budget, cap)
    it = 0
    converged = False
    for it in range(1, maxit + 1):
        new = step(w, budget, gamma, beta, theta, cap, soft=soft)
        if it % 10 == 0:
            on = (new > SUPPORT) | (w > SUPPORT)
            if on.any():
                delta = np.abs(new[on] - w[on]) / np.maximum(w[on], SUPPORT)
                if delta.max() < 1e-7:
                    w = new
                    converged = True
                    break
        w = new
    out = describe(w)
    A = w * (w > SUPPORT)
    ncomp, labels = connected_components(csr_matrix(A), directed=False)
    big = np.flatnonzero(labels == np.argmax(np.bincount(labels)))
    out["largest"] = int(len(big))
    if len(big) >= 8:
        fm = family_metrics(A[np.ix_(big, big)], seed=seed)
        out.update({"big_" + k: fm[k] for k in ("diameter", "lambda2", "conductance", "d_growth", "d_spectral", "interior")})
    out.update(gamma=gamma, beta=beta, theta=theta, cap=cap, seed=seed, iters=it, converged=converged, soft=soft)
    return out


# ---------- Part: threshold ----------
def threshold_job(job):
    budget, gamma, beta, n = job
    rng = np.random.default_rng(99)
    w = normalize(start(n, 1e-3, rng), budget)
    rates = []
    def spread(x):
        return np.log(x[np.triu_indices(n, 1)]).std()
    s = spread(w)
    for _ in range(12):
        w = step(w, budget, gamma, beta)
        t = spread(w)
        rates.append(t / s)
        s = t
    f = float(np.mean(rates[-6:]))
    return dict(budget=budget, gamma=gamma, beta=beta, n=n, amplification=2 * f - 1)


# ---------- Part: families ----------
def adj_ring(n):
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = 1
    return A


def adj_torus(L, d):
    n = L ** d
    A = np.zeros((n, n))
    for i in range(n):
        coords = [(i // L ** k) % L for k in range(d)]
        for k in range(d):
            c = list(coords)
            c[k] = (c[k] + 1) % L
            j = sum(v * L ** t for t, v in enumerate(c))
            A[i, j] = A[j, i] = 1
    return A


def adj_gasket(level):
    pts = {(0, 0): 0, (1, 0): 1, (0, 1): 2}
    tris = [((0, 0), (1, 0), (0, 1))]
    for _ in range(level):
        new = []
        for a, b, c in tris:
            two = lambda p: (2 * p[0], 2 * p[1])
            mid = lambda p, q: (p[0] + q[0], p[1] + q[1])
            A_, B_, C_ = two(a), two(b), two(c)
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new += [(A_, ab, ca), (ab, B_, bc), (ca, bc, C_)]
        tris = new
    pts = {}
    for t in tris:
        for p in t:
            pts.setdefault(p, len(pts))
    A = np.zeros((len(pts), len(pts)))
    for a, b, c in tris:
        for p, q in ((a, b), (b, c), (c, a)):
            A[pts[p], pts[q]] = A[pts[q], pts[p]] = 1
    return A


def adj_hypercube(d, r):
    n = 2 ** d
    a = np.array([r ** l for l in range(d)])
    a /= a.sum()
    A = np.zeros((n, n))
    for i in range(n):
        for l in range(d):
            A[i, i ^ (1 << l)] = a[l]
    return A


def adj_random_regular(n, k, rng):
    while True:
        stubs = np.repeat(np.arange(n), k)
        rng.shuffle(stubs)
        A = np.zeros((n, n))
        ok = True
        for a, b in zip(stubs[::2], stubs[1::2]):
            if a == b or A[a, b]:
                ok = False
                break
            A[a, b] = A[b, a] = 1
        if ok:
            return A
        # repair by rejection only at small k; fall back to switching
        if k <= 4:
            continue


def adj_glued_rings(L, mode, rng):
    n = L * L
    A = np.zeros((n, n))
    for ring in range(L):
        for s in range(L):
            a = ring * L + s
            b = ring * L + (s + 1) % L
            A[a, b] = A[b, a] = 1
    for ring in range(L):
        nxt = (ring + 1) % L
        perm = np.arange(L) if mode == "aligned" else rng.permutation(L)
        for s in range(L):
            a = ring * L + s
            b = nxt * L + perm[s]
            A[a, b] = A[b, a] = 1
    return A


def family_metrics(A, seed=0):
    n = len(A)
    rng = np.random.default_rng(seed)
    S = (A > 0).astype(int)
    s = A.sum(1)
    K = np.eye(n) - A / np.sqrt(np.outer(s, s))
    lam, vec = np.linalg.eigh(K)
    lam = np.maximum(lam, 0)
    sp = csr_matrix(S)
    src = rng.choice(n, size=min(30, n), replace=False)
    dist = shortest_path(sp, unweighted=True, directed=False, indices=src)
    diam = dist.max()
    balls = np.array([[(row <= r).sum() for r in range(int(diam) + 1)] for row in dist]).mean(0)
    keep = [r for r in range(1, int(diam) + 1) if balls[r] <= n / 4 and r >= 2]
    df = float(np.polyfit(np.log(keep), np.log(balls[keep]), 1)[0]) if len(keep) >= 3 else float("nan")
    # interior fraction of a half-volume ball
    fr = []
    for row in dist:
        r = max(r for r in range(int(diam) + 1) if (row <= r).sum() <= n / 2) if (row <= 0).sum() <= n / 2 else 0
        inside = row <= r
        out_links = (S[inside][:, ~inside].sum(1) > 0).sum()
        fr.append(1 - out_links / max(inside.sum(), 1))
    # best sweep cut along the Fiedler vector
    f = vec[:, 1] / np.sqrt(np.maximum(s, 1e-300))
    order = np.argsort(f)
    inS = np.zeros(n, bool)
    vol = s.sum()
    cut = 0.0
    volS = 0.0
    best = 1.0
    for i in order[:-1]:
        cut += A[i][~inS].sum() - A[i][inS].sum()
        inS[i] = True
        volS += s[i]
        best = min(best, cut / min(volS, vol - volS))
    # spectral dimension from continuous-time return probability
    tmax = 0.25 / max(lam[1], 1e-12)
    tmax = min(tmax, 1e7)
    ts = np.geomspace(3.0, max(tmax, 30.0), 24)
    p = np.array([np.exp(-lam * t).mean() for t in ts])
    ds = float(-2 * np.polyfit(np.log(ts), np.log(p), 1)[0])
    # persistent spectral gaps at low energy: largest ratio of successive distinct levels above the first few
    distinct = [lam[1]]
    for v in lam[2:]:
        if v > distinct[-1] * (1 + 1e-6):
            distinct.append(v)
    distinct = np.array(distinct)
    low = distinct[(distinct > 0) & (distinct < 0.25)]
    tail = low[3:] if len(low) > 5 else low
    gap = float((tail[1:] / tail[:-1]).max()) if len(tail) > 1 else float("nan")
    return dict(n=n, mean_degree=float(S.sum(1).mean()), diameter=float(diam), lambda2=float(lam[1]), conductance=float(best),
                d_growth=df, d_spectral=ds, d_walk=2 * df / ds if ds > 0 else float("nan"),
                interior=float(np.mean(fr)), largest_low_gap_ratio=gap, distinct_levels=int(len(distinct)))


def family_job(spec):
    name, builder, args = spec
    rng = np.random.default_rng(7)
    if builder == "ring": A = adj_ring(*args)
    elif builder == "torus": A = adj_torus(*args)
    elif builder == "gasket": A = adj_gasket(*args)
    elif builder == "hyper": A = adj_hypercube(*args)
    elif builder == "regular": A = adj_random_regular(args[0], args[1], rng)
    elif builder == "complete": A = np.ones((args[0], args[0])) - np.eye(args[0])
    elif builder == "glued": A = adj_glued_rings(args[0], args[1], rng)
    out = family_metrics(A)
    out["family"] = name
    return out


def exponent(ns, ys):
    ns, ys = np.array(ns, float), np.array(ys, float)
    good = ys > 0
    return float(np.polyfit(np.log(ns[good]), np.log(ys[good]), 1)[0]) if good.sum() >= 2 else float("nan")


def run(pool, fn, jobs, label):
    t = time.time()
    out = list(pool.imap_unordered(fn, jobs, chunksize=1))
    print(f"[{label}] {len(out)} jobs in {time.time() - t:.0f}s", flush=True)
    return out


def main():
    outdir = sys.argv[1]
    parts = sys.argv[2:] or ["threshold", "matrix", "cap", "mix", "families"]
    os.makedirs(outdir, exist_ok=True)
    results = {}
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        if "threshold" in parts:
            jobs = [(b, g, be, n) for b in ("global", "site") for g in (0.0, 0.5, 1.0)
                    for be in (0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.5) for n in (16, 64)]
            res = run(pool, threshold_job, jobs, "threshold")
            results["threshold"] = res
            print("\nP1. Amplification per step at the complete graph (above 1 = unstable)")
            for b in ("global", "site"):
                for g in (0.0, 0.5, 1.0):
                    for n in (16, 64):
                        row = sorted([r for r in res if r["budget"] == b and r["gamma"] == g and r["n"] == n], key=lambda r: r["beta"])
                        print(f"  {b:6} gamma={g} n={n:3}: " + " ".join(f"{r['beta']}:{r['amplification']:.3f}" for r in row))
        if "matrix" in parts:
            jobs = []
            for b in ("global", "site"):
                for g in (0.0, 0.5, 1.0):
                    for be in (0.8, 1.2, 1.5, 2.0, 3.0, 5.0):
                        for n in (16, 32, 64, 128):
                            for seed in range(8):
                                jobs.append((b, g, be, 0.0, None, n, seed, 1500, 0.05))
            # a larger size and odd sizes for the two central cases
            for b in ("global", "site"):
                for seed in range(8):
                    jobs.append((b, 1.0, 2.0, 0.0, None, 256, seed, 1500, 0.05))
                    for n in (15, 33, 65):
                        jobs.append((b, 1.0, 2.0, 0.0, None, n, seed, 1500, 0.05))
                    jobs.append((b, 1.0, 2.0, 0.0, None, 64, seed + 100, 1500, 1.0))  # large initial noise
            res = run(pool, evolve, jobs, "matrix")
            results["matrix"] = res
            print("\nP2-P6. Budget x rule x beta x n: connected fraction, rings, trees, mean degree, max degree, diameter, kinds")
            groups = defaultdict(list)
            for r in res:
                groups[(r["budget"], r["gamma"], r["beta"], r["n"])].append(r)
            for key in sorted(groups):
                g = groups[key]
                kinds = Counter()
                for r in g:
                    kinds.update(r["kinds"])
                print(f"  {key[0]:6} gamma={key[1]} beta={key[2]} n={key[3]:3}: conn {np.mean([r['components'] == 1 for r in g]):.2f} "
                      f"ring {np.mean([r['ring'] for r in g]):.2f} tree {np.mean([r['tree'] for r in g]):.2f} "
                      f"deg {np.mean([r['mean_degree'] for r in g]):.2f} max {np.mean([r['max_degree'] for r in g]):.1f} "
                      f"diam {np.mean([r['diameter'] for r in g]):.1f} conv {np.mean([r['converged'] for r in g]):.2f} kinds {dict(kinds)}")
        if "cap" in parts:
            jobs = [("site", 1.0, 2.0, 0.0, 1 / k, n, seed, 800, 0.05) for k in (2, 3, 4, 6) for n in (32, 64, 128, 256) for seed in range(6)]
            res = run(pool, evolve, jobs, "cap")
            results["cap"] = res
            print("\nP7. Each relation capped at 1/k, site budget, gamma=1, beta=2, against random k-regular")
            rng = np.random.default_rng(5)
            for k in (2, 3, 4, 6):
                ns, dm, lm = [], [], []
                for n in (32, 64, 128, 256):
                    g = [r for r in res if abs(r["cap"] - 1 / k) < 1e-9 and r["n"] == n]
                    ns.append(n); dm.append(np.mean([r["diameter"] for r in g])); lm.append(np.mean([r["lambda2"] for r in g]))
                    extra = ""
                    if k > 2 and (n * k) % 2 == 0:
                        null = [family_metrics(adj_random_regular(n, k, rng)) for _ in range(3)]
                        extra = f" | random regular: diam {np.mean([x['diameter'] for x in null]):.1f} lam2 {np.mean([x['lambda2'] for x in null]):.4f}"
                    print(f"  k={k} n={n:3}: conn {np.mean([r['components'] == 1 for r in g]):.2f} deg {np.mean([r['mean_degree'] for r in g]):.2f} "
                          f"maxw {np.mean([r['max_w'] for r in g]):.3f} diam {dm[-1]:.1f} lam2 {lm[-1]:.4f} clust {np.mean([r['clustering'] for r in g]):.3f} conv {np.mean([r['converged'] for r in g]):.2f}{extra}")
                print(f"     k={k}: diameter ~ n^{exponent(ns, dm):.2f}, lambda2 ~ n^{exponent(ns, lm):.2f}")
        if "mix" in parts:
            jobs = [("site", 1.0, 2.0, th, cap, n, seed, 800, 0.05)
                    for th in (0.0, 0.25, 0.5, 0.75, 1.0) for cap in (None, 0.25) for n in (32, 64, 128, 256) for seed in range(6)]
            res = run(pool, evolve, jobs, "mix")
            results["mix"] = res
            print("\nP8. Closure mixed with energy. theta=0 energy only, theta=1 closure only")
            for cap in (None, 0.25):
                for th in (0.0, 0.25, 0.5, 0.75, 1.0):
                    ns, dm, lm = [], [], []
                    for n in (32, 64, 128, 256):
                        g = [r for r in res if r["theta"] == th and r["cap"] == cap and r["n"] == n]
                        kinds = Counter()
                        for r in g:
                            kinds.update(r["kinds"])
                        ns.append(n); dm.append(np.mean([r["diameter"] for r in g])); lm.append(np.mean([r["lambda2"] for r in g]))
                        print(f"  cap={cap} theta={th} n={n:3}: conn {np.mean([r['components'] == 1 for r in g]):.2f} comps {np.mean([r['components'] for r in g]):.1f} "
                              f"deg {np.mean([r['mean_degree'] for r in g]):.2f} diam {dm[-1]:.1f} lam2 {lm[-1]:.5f} clust {np.mean([r['clustering'] for r in g]):.3f} kinds {dict(kinds)}")
                    print(f"     cap={cap} theta={th}: diameter ~ n^{exponent(ns, dm):.2f}, lambda2 ~ n^{exponent(ns, lm):.2f}")
        if "families" in parts:
            specs = []
            for n in (64, 256, 1024, 2048): specs.append(("ring", "ring", (n,)))
            for L in (8, 16, 32, 45): specs.append(("torus 2D", "torus", (L, 2)))
            for L in (4, 6, 10, 13): specs.append(("torus 3D", "torus", (L, 3)))
            for lv in (3, 4, 5, 6, 7): specs.append(("gasket", "gasket", (lv,)))
            for d in (6, 8, 10, 11): specs.append(("hierarchical cube r=1/4", "hyper", (d, 0.25)))
            for d in (6, 8, 10, 11): specs.append(("hierarchical cube r=1/2", "hyper", (d, 0.5)))
            for n in (64, 256, 1024, 2048): specs.append(("random 3-regular", "regular", (n, 3)))
            for n in (64, 256, 1024): specs.append(("complete", "complete", (n,)))
            for L in (8, 16, 32, 45): specs.append(("rings aligned", "glued", (L, "aligned")))
            for L in (8, 16, 32, 45): specs.append(("rings random glue", "glued", (L, "random")))
            res = run(pool, family_job, specs, "families")
            results["families"] = res
            print("\nP9. Families at per-site budget")
            for fam in dict.fromkeys(s[0] for s in specs):
                g = sorted([r for r in res if r["family"] == fam], key=lambda r: r["n"])
                ns = [r["n"] for r in g]
                top = g[-1]
                print(f"  {fam:24} n={top['n']:5} deg {top['mean_degree']:5.2f} d_growth {top['d_growth']:5.2f} d_spectral {top['d_spectral']:5.2f} d_walk {top['d_walk']:5.2f} "
                      f"interior {top['interior']:.3f} conductance {top['conductance']:.4f} low-gap {top['largest_low_gap_ratio']:.2f} levels {top['distinct_levels']:5d} "
                      f"| lam2~n^{exponent(ns, [r['lambda2'] for r in g]):.2f} cond~n^{exponent(ns, [r['conductance'] for r in g]):.2f} diam~n^{exponent(ns, [r['diameter'] for r in g]):.2f} "
                      f"interior by n {[round(r['interior'], 2) for r in g]}")
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        if "edge" in parts:
            sizes = (32, 64, 128, 256, 512)
            betas = (1.3, 1.5, 1.7, 1.8, 1.9, 1.95)
            jobs = [("site", 0.5, b, 0.0, None, n, s, 2000, False) for b in betas for n in sizes for s in range(6)]
            res = run(pool, evolve2, jobs, "edge")
            results["edge"] = res
            print("\nQ1. gamma=1/2, site budget, near the disconnection edge beta=2")
            for b in betas:
                ns, dm = [], []
                for n in sizes:
                    g = [r for r in res if r["beta"] == b and r["n"] == n]
                    ns.append(n); dm.append(np.mean([r["diameter"] for r in g]))
                    print(f"  beta={b} n={n:3}: conn {np.mean([r['components'] == 1 for r in g]):.2f} ring {np.mean([r['ring'] for r in g]):.2f} deg {np.mean([r['mean_degree'] for r in g]):.3f} "
                          f"max {np.mean([r['max_degree'] for r in g]):.1f} diam {dm[-1]:.1f} lam2 {np.mean([r['lambda2'] for r in g]):.5f} largest {np.mean([r['largest'] for r in g]):.0f} conv {np.mean([r['converged'] for r in g]):.2f}")
                print(f"     beta={b}: diameter ~ n^{exponent(ns, dm):.2f}")
        if "closure" in parts:
            thetas = (0.1, 0.2, 0.3, 0.4)
            sizes = (64, 128, 256)
            jobs = [("site", 1.0, 2.0, th, cap, n, s, 800, soft) for th in thetas for cap in (None, 0.25) for soft in (False, True) for n in sizes for s in range(6)]
            res = run(pool, evolve2, jobs, "closure")
            results["closure"] = res
            print("\nQ2. Energy mixed with closure, site budget, gamma=1, beta=2")
            rng = np.random.default_rng(6)
            null = {n: [family_metrics(adj_random_regular(n, 4, rng)) for _ in range(3)] for n in sizes}
            for n in sizes:
                print(f"  random 4-regular n={n}: diam {np.mean([x['diameter'] for x in null[n]]):.1f} lam2 {np.mean([x['lambda2'] for x in null[n]]):.4f} interior {np.mean([x['interior'] for x in null[n]]):.3f}")
            for soft in (False, True):
                for cap in (None, 0.25):
                    for th in thetas:
                        ns, dm, lm = [], [], []
                        for n in sizes:
                            g = [r for r in res if r["theta"] == th and r["cap"] == cap and r["soft"] == soft and r["n"] == n]
                            ns.append(n); dm.append(np.mean([r.get("big_diameter", 0) for r in g])); lm.append(np.mean([r.get("big_lambda2", 0) for r in g]))
                            print(f"  soft={soft} cap={cap} theta={th} n={n:3}: conn {np.mean([r['components'] == 1 for r in g]):.2f} largest {np.mean([r['largest'] for r in g]):.0f} deg {np.mean([r['mean_degree'] for r in g]):.2f} "
                                  f"clust {np.mean([r['clustering'] for r in g]):.3f} diam {dm[-1]:.1f} lam2 {lm[-1]:.5f} growth {np.nanmean([r.get('big_d_growth', np.nan) for r in g]):.2f} interior {np.nanmean([r.get('big_interior', np.nan) for r in g]):.3f} conv {np.mean([r['converged'] for r in g]):.2f}")
                        print(f"     soft={soft} cap={cap} theta={th}: diameter ~ n^{exponent(ns, dm):.2f}, lambda2 ~ n^{exponent(ns, lm):.2f}")
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        if "holdout" in parts:
            # The two strict-closure settings with the largest diameters and connected largest pieces at n<=256.
            configs = [(0.4, None), (0.4, 0.25), (0.3, None)]
            sizes = (64, 128, 256, 512, 1024)
            jobs = [("site", 1.0, 2.0, th, cap, n, s, 800, False) for th, cap in configs for n in sizes for s in range(4)]
            res = run(pool, evolve2, jobs, "holdout")
            results["holdout"] = res
            print("\nQ3. Fit diameter on n<=256, predict n=512 and 1024: power law against log n")
            for th, cap in configs:
                rows = []
                for n in sizes:
                    g = [r for r in res if r["theta"] == th and r["cap"] == cap and r["n"] == n]
                    rows.append((n, np.mean([r["largest"] for r in g]), np.mean([r.get("big_diameter", 0) for r in g]), np.mean([r.get("big_lambda2", 0) for r in g]),
                                 np.nanmean([r.get("big_d_growth", np.nan) for r in g]), np.mean([r.get("big_interior", 0) for r in g]), np.mean([r["clustering"] for r in g]),
                                 np.mean([r["mean_degree"] for r in g]), np.mean([r["converged"] for r in g]), np.mean([r["components"] for r in g])))
                    x = rows[-1]
                    print(f"  theta={th} cap={cap} n={n:4}: largest {x[1]:.0f} comps {x[9]:.1f} deg {x[7]:.2f} clust {x[6]:.3f} diam {x[2]:.1f} lam2 {x[3]:.5f} growth {x[4]:.2f} interior {x[5]:.3f} conv {x[8]:.2f}")
                m = np.array(rows)
                train = m[:3]
                a, b = np.polyfit(np.log(train[:, 1]), np.log(train[:, 2]), 1)
                c, d = np.polyfit(np.log(train[:, 1]), train[:, 2], 1)
                for row in m[3:]:
                    print(f"     largest {row[1]:.0f}: actual diam {row[2]:.1f}; power fit (exponent {a:.2f}) predicts {np.exp(b) * row[1] ** a:.1f}; log fit predicts {c * np.log(row[1]) + d:.1f}")
            rng = np.random.default_rng(8)
            for n in (64, 256, 1024):
                x = family_metrics(adj_random_regular(n, 4, rng))
                print(f"  random 4-regular n={n}: diam {x['diameter']:.1f} lam2 {x['lambda2']:.5f} growth {x['d_growth']:.2f} interior {x['interior']:.3f}")
    with open(os.path.join(outdir, "graph_from_self_limitation_" + "_".join(parts) + ".json"), "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    main()
