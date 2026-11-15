"""Tests behind "A Theory of Wholeness". Predictions frozen before any run of this script.

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte
Results: B1 to B4, H1, H3, H4, H5, H7, D1, D2 passed. H2 inconclusive, since its threshold was never crossed, though the ordering held. H6 missed: thin parts do not tear first; all four structures merge, then lose their doors alike.
The first launch failed on a negative seed before any test ran. The predictions below stand as frozen.

Needs numpy, scipy, and wholeness_plane_criterion_v1.py beside it. All data are synthetic.
Run: python -I wholeness_theory_v1.py OUTDIR [belonging depth holding doors], in that order, since doors reads what the first and third saved

WHY. The day's records and the physics series agree that a part stays itself only while what holds it outruns what connects it. Three things stop that being a theory:
(1) The plane's c is blind to bridge strength, so a nearly severed network reads as health. (2) "Holding" mixes two things that may have different causes.
(3) Everything measured so far is diffusive, so the h claim has never faced a nonlinear system.

HAND DERIVATIONS BEFORE ANY RUN.
(a) Belonging. Let a part have outward share s = b + x, where b lands among its peers and x passes beyond them. Then a = A(S) = r/(r + s), with r = (1-s)h, depends on how MUCH leaves.
    c = r_peer/(r_peer + x), with r_peer the rate at which the part's mass mixes across its peers, depends on WHERE it goes. With s fixed, b and x can trade: c changes and a does not.
    So belonging need not cost holding if outward flow is redirected rather than increased. The clock in c is the leak out of the peer set, which needs no whole above, only that there be a beyond.
    c is the peer set's own A, read one level up: (c, a) is one function at two adjacent scales. With no beyond at all, c has no clock and is undefined.
    Four corners, three rates: h >> b >> x integration; h >> x >> b severance; b >> h, x absorption; x >> h, b anomie.
(b) Staying one against staying distinct. Rigid blocks of Kuramoto oscillators with mean frequencies +W and -W, total coupling K, outward share s, order parameter R:
    the phase difference obeys d(phi)/dt = 2W - 2 K s R^2 sin(phi). So the blocks merge at s_m = W/(K R^2). Internal structure enters only through R. Near R = 1 the merge point does not depend on h at all.
    This disagrees in form with the capacity law s* = h/(1+h), which is diffusive. Internal coherence itself should fail where K(1-s)h falls below the frequency spread, which does depend on h.
    So: cohesion buys staying one. It does not buy staying distinct. Self-reference does: pinning each block to its own rotating reference with strength H resists the pull, as in Experiment 14's H/(H + 2b).
(c) Depth. With level shares in ratio r, the outward load on a part with K levels above it is S_K = r + ... + r^K = (r/(1-r))(1 - r^K), which saturates: the corpus's candidate form d_n = d_inf(1 - rho^n), with rho = r.
    Mass still reaches every level, so depth does not sever. It costs time: the time to reach level K grows as (1/r)^K.

PREDICTIONS.
B1 (severance is reached continuously). Fixed x = 1e-3, b falling from 1e-1 to 1e-6, complete parts: new c falls from above .9 to below .1, a stays above .9, the old c stays at 1.000.
B2 (all four corners, in the direct measures). On the b, x grid with both part types and both contact types, each quadrant of (a_true, c_true) at .5 holds at least 5% of cells. |Spearman(a, c)| < .3 for the formulas. The old record: rho -.742, 1 cell in the low-low corner.
B3 (the formulas track the dynamics). Spearman(c, c_true) >= .9, higher than the old c. Spearman(a, a_true) >= .8. Old figures: .707 and .748.
B4 (redirecting). With total outward share fixed at s = .05, complete parts, moving flow from x to b raises c_true by at least .5 while a_true moves by under .1.
H1 (cohesion does not buy distinctness). Spread .05, no self-reference: where R >= .9 at the lowest s, the merge point varies by under 15% across ring k=1, 2, 3 and complete, though s* = h/(1+h) varies by more than 4 times.
H2 (cohesion buys oneness). Spread .4, no self-reference: the s at which R falls below .7 rises with h across the four topologies (a topology that never falls counts as highest).
H3 (self-reference buys distinctness). Spread .05: the merge point rises with H at every step, and at H = 1 is at least 1.5 times its value at H = 0.
H4 (it has a price). The smallest H that keeps block separation at or above .9 rises with s, and effort at fixed H rises with s up to the merge point.
H5 (cohesion still does not help). At H >= .5, the merge point of ring k=1 and complete differ by under 20%.
D1 (depth saturates). Product of K_2, L = 10, r = .25 and .4: A on true blocks stays within .05 of its saturated value for K >= 3 at r = .25 and K >= 6 at r = .4, while the product of the A's along the chain falls below .5.
D2 (depth costs time). Time for a block of size 2^j to lose 1 - 1/e of its starting mass grows per level by 1/r, within 15%, in the bulk.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. H1 passed, but all-pairs bridging pulls on every site directly and so bypasses the interior. In a real whole connection arrives through doors.
H6 (doors). Pull only through 4 of 12 sites, evenly spaced, spread .05, H = 0. Complete blocks merge whole near .173, with R at or above .9 up to the merge point. Ring k=1 tears: R falls below .9 at a lower outward share than its separation falls below .5.
    So cohesion decides HOW a part is lost, whole or torn, even if not how much connection it takes. h matters through doors in a way it did not through all pairs.
    Note: a first grid never reached the merge point, because the site budget caps the realised share, so the targets were widened before scoring. With 6 doors, ring k=1 passed zero outward share: all its doors sit on one side of an even ring (doors lemma).
H7 (a narrower range). Spearman(c, c_true) and Spearman(a, a_true) stay at or above .7 on cells with c, and separately a, between .2 and .8, since the full grid's wide range makes rank agreement easy.
"""
import importlib.util
import json
import os
import sys
import time
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("wholeness_plane_criterion_v1", os.path.join(HERE, "wholeness_plane_criterion_v1.py"))
WP = importlib.util.module_from_spec(_s)
sys.modules["wholeness_plane_criterion_v1"] = WP
_s.loader.exec_module(WP)


# ---------- Belonging ----------
def build(kind, contact, b, x, rng, m=8, p=4, q=4, doors=2, noise=.2):
    """Parts of m sites, p parts in a peer set, q peer sets. Shares b to peers and x beyond, then noise and the site budget."""
    n = m * p * q
    A = np.zeros((n, n))
    inner = np.ones((m, m)) - np.eye(m) if kind == "complete" else np.roll(np.eye(m), 1, 1) + np.roll(np.eye(m), -1, 1)
    inner = inner / inner.sum(1, keepdims=True) * max(1 - b - x, 1e-6)
    part = np.arange(n) // m
    peer = np.arange(n) // (m * p)
    for u in range(m * p * q // m):
        A[np.ix_(np.arange(u * m, (u + 1) * m), np.arange(u * m, (u + 1) * m))] = inner
    door = np.arange(n) % m < (m if contact == "all" else doors)
    for i in range(n):
        if not door[i]:
            continue
        for j in range(i + 1, n):
            if not door[j] or part[i] == part[j]:
                continue
            frac = m / doors if contact != "all" else 1.0  # door sites carry the part's whole outward share
            w = b / (m * (p - 1)) if peer[i] == peer[j] else x / (m * p * (q - 1))
            A[i, j] = A[j, i] = w * frac * frac
    if noise:
        g = rng.normal(0, noise, (n, n))
        g = (g + g.T) / np.sqrt(2)
        A = A * np.exp(g)
    d = np.ones(n)
    for _ in range(300):
        d = np.sqrt(d / np.maximum(A @ d, 1e-280))
    A = A * np.outer(d, d)
    return (A + A.T) / 2, m, p, q


def belong(W, m, p, q, u=0):
    """a, new c, old c for part u, against direct measures from the heat kernel."""
    n = len(W)
    s = W.sum(1)
    S = list(range(u * m, (u + 1) * m))
    P0 = (u // p) * p
    P = list(range(P0 * m, (P0 + p) * m))
    parts = [list(range(k * m, (k + 1) * m)) for k in range(P0, P0 + p)]
    a = WP.autonomy_part(W, s, S)
    vol = np.array([s[g].sum() for g in parts])
    Q = WP.quotient(W, parts)
    L = (np.diag(Q.sum(1)) - Q) / np.sqrt(np.outer(vol, vol))
    r_peer = float(np.sort(np.linalg.eigvalsh(L))[1])
    out_P = max(0.0, 1 - W[np.ix_(P, P)].sum() / s[P].sum())
    c = r_peer / (r_peer + out_P) if r_peer + out_P > 0 else float("nan")
    c_old = min(1.0, WP.norm_gap(Q))
    lam, V, _, inv = WP.spectrum(W)
    sq = np.sqrt(s)
    ts = np.geomspace(1e-2, 1e8, 240)
    coef = np.exp(-np.outer(ts, lam))

    def plateau(p0, law):
        c0 = V.T @ (p0 / sq)
        best = 1e9
        for row in coef:
            q_ = sq * (V @ (row * c0))
            best = min(best, .5 * np.abs(q_ - law).sum())
        return 1 - best

    law_S = np.zeros(n); law_S[S] = s[S] / s[S].sum()
    law_P = np.zeros(n); law_P[P] = s[P] / s[P].sum()
    p_site = np.zeros(n); p_site[S[0]] = 1.0
    a_true = (plateau(p_site, law_S) - 1 / m) / (1 - 1 / m)
    p_part = law_S.copy()
    c_true = (plateau(p_part, law_P) - 1 / p) / (1 - 1 / p)
    return dict(a=float(a), c=float(c), c_old=float(c_old), a_true=float(a_true), c_true=float(c_true), h=float(WP.norm_gap(W[np.ix_(S, S)])), out=float(1 - W[np.ix_(S, S)].sum() / s[S].sum()), out_P=float(out_P), r_peer=r_peer)


def belong_job(job):
    kind, contact, b, x, seed = job
    rng = np.random.default_rng([abs(seed), int(1e6 * b), int(1e6 * x), kind == "ring", contact == "all"])
    W, m, p, q = build(kind, contact, b, x, rng, noise=(.2 if seed >= 0 else 0.0))
    out = belong(W, m, p, q)
    out.update(kind=kind, contact=contact, b=b, x=x, seed=seed)
    return out


def part_belonging(outdir, pool):
    grid = list(np.geomspace(1e-5, .6, 9))
    jobs = [(k, c, b, x, 1) for k in ("complete", "ring") for c in ("all", "doors") for b in grid for x in grid if b + x < .95]
    jobs += [("complete", "all", b, 1e-3, -1) for b in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)]
    jobs += [("complete", "all", f * .05, (1 - f) * .05, -1) for f in (.999, .9, .7, .5, .3, .1, .01, .001)]
    res = pool.map(belong_job, jobs, chunksize=8)
    json.dump(res, open(os.path.join(outdir, "belonging.json"), "w"))
    g = [r for r in res if r["seed"] == 1]
    print("B1. Fixed x = 1e-3, b falling, complete parts, no noise")
    for r in [r for r in res if r["seed"] == -1 and r["x"] == 1e-3]:
        print(f"  b {r['b']:.0e}: a {r['a']:.3f}, new c {r['c']:.3f}, old c {r['c_old']:.3f}; direct a {r['a_true']:.3f}, direct c {r['c_true']:.3f}")
    A, C, CO, AT, CT = (np.array([r[k] for r in g]) for k in ("a", "c", "c_old", "a_true", "c_true"))
    print(f"B2. {len(g)} cells. Formula quadrants at .5: HH {((A > .5) & (C > .5)).sum()}, a high c low {((A > .5) & (C <= .5)).sum()}, a low c high {((A <= .5) & (C > .5)).sum()}, LL {((A <= .5) & (C <= .5)).sum()}; Spearman(a, c) {spearmanr(A, C).statistic:+.3f}; with old c {spearmanr(A, CO).statistic:+.3f}")
    print(f"    Direct quadrants: HH {((AT > .5) & (CT > .5)).mean():.3f}, a high c low {((AT > .5) & (CT <= .5)).mean():.3f}, a low c high {((AT <= .5) & (CT > .5)).mean():.3f}, LL {((AT <= .5) & (CT <= .5)).mean():.3f}; Spearman(a_true, c_true) {spearmanr(AT, CT).statistic:+.3f}")
    print(f"B3. Spearman(c, c_true) {spearmanr(C, CT).statistic:.3f}; old c {spearmanr(CO, CT).statistic:.3f}; Spearman(a, a_true) {spearmanr(A, AT).statistic:.3f}")
    for k in ("complete", "ring"):
        for ct in ("all", "doors"):
            h = [r for r in g if r["kind"] == k and r["contact"] == ct]
            print(f"    {k}, {ct}: Spearman(c, c_true) {spearmanr([r['c'] for r in h], [r['c_true'] for r in h]).statistic:.3f}; Spearman(a, a_true) {spearmanr([r['a'] for r in h], [r['a_true'] for r in h]).statistic:.3f}; mean h {np.mean([r['h'] for r in h]):.3f}")
    print("B4. Total outward share .05, moving flow from beyond to peers, complete parts, no noise")
    for r in [r for r in res if r["seed"] == -1 and r["x"] != 1e-3]:
        print(f"  b {r['b']:.5f}, x {r['x']:.5f}: a {r['a']:.3f}, c {r['c']:.3f}; direct a {r['a_true']:.3f}, direct c {r['c_true']:.3f}")


# ---------- Holding ----------
def ring_lattice(n, k):
    if k >= n // 2:
        A = np.ones((n, n)) - np.eye(n)
    else:
        A = np.zeros((n, n))
        for d in range(1, k + 1):
            A += np.roll(np.eye(n), d, 1) + np.roll(np.eye(n), -d, 1)
    return A / A.sum(1, keepdims=True)


def holding_job(job):
    k, s, H, spread, seeds, K, Om = job
    n = 12
    inner = ring_lattice(n, k)
    W = np.zeros((2 * n, 2 * n))
    W[:n, :n] = W[n:, n:] = inner * (1 - s)
    W[:n, n:] = W[n:, :n] = s / n
    rng = np.random.default_rng([k, int(s * 1000), int(H * 100), int(spread * 100)])
    xi = rng.normal(0, 1, (seeds, 2 * n))
    xi[:, :n] -= xi[:, :n].mean(1, keepdims=True)
    xi[:, n:] -= xi[:, n:].mean(1, keepdims=True)
    sign = np.r_[np.ones(n), -np.ones(n)]
    omega = Om * sign + spread * xi
    th = rng.normal(0, .1, (seeds, 2 * n))
    dt, T = .05, 400.0
    steps = int(T / dt)

    def f(th_, t):
        d = th_[:, None, :] - th_[:, :, None]
        out = omega + K * (W[None] * np.sin(d)).sum(2)
        if H:
            out = out + H * np.sin(Om * sign * t - th_)
        return out

    R, adv, eff, cnt = 0.0, 0.0, 0.0, 0
    burn = steps // 2
    start_mean = None
    for i in range(steps):
        t = i * dt
        k1 = f(th, t)
        k2 = f(th + dt * k1, t + dt)
        new = th + dt / 2 * (k1 + k2)
        if i >= burn:
            if start_mean is None:
                start_mean = th.copy()
            if i % 5 == 0:
                z = np.exp(1j * th)
                R = R + (np.abs(z[:, :n].mean(1)) + np.abs(z[:, n:].mean(1))) / 2
                if H:
                    eff = eff + ((H * np.sin(Om * sign * t - th)) ** 2).mean(1)
                cnt += 1
        th = new
    elapsed = (steps - burn) * dt
    rate = (th - start_mean) / elapsed
    sep = (rate[:, :n].mean(1) - rate[:, n:].mean(1)) / (2 * Om)
    return dict(k=k, s=s, H=H, spread=spread, R=float(np.median(R / cnt)), sep=float(np.median(np.abs(sep))), effort=float(np.median(eff / cnt)) if H else 0.0)


def crossing(xs, ys, level, above=True):
    """First x where y falls through level, interpolated. inf if it never does; 0 if it starts below."""
    if (ys[0] < level) if above else False:
        return 0.0
    for i in range(len(xs) - 1):
        if ys[i] >= level > ys[i + 1]:
            return float(xs[i] + (ys[i] - level) * (xs[i + 1] - xs[i]) / (ys[i] - ys[i + 1]))
    return float("inf")


def part_holding(outdir, pool):
    K, Om, seeds = 2.0, .4, 24
    S = [.02, .05, .08, .11, .14, .17, .2, .23, .26, .3, .35, .4, .5, .6, .7, .8]
    Hs = [0, .2, .5, 1, 2]
    tops = [1, 2, 3, 6]
    jobs = [(k, s, H, sp, seeds, K, Om) for k in tops for s in S for H in Hs for sp in (.05, .4)]
    t0 = time.time()
    res = []
    for i, r in enumerate(pool.imap_unordered(holding_job, jobs, chunksize=2)):
        res.append(r)
        if (i + 1) % 80 == 0:
            print(f"  holding {i + 1}/{len(jobs)}, {time.time() - t0:.0f}s", flush=True)
    json.dump(res, open(os.path.join(outdir, "holding.json"), "w"))
    get = lambda k, H, sp: sorted([r for r in res if r["k"] == k and r["H"] == H and r["spread"] == sp], key=lambda r: r["s"])
    name = {1: "ring k=1", 2: "ring k=2", 3: "ring k=3", 6: "complete"}
    print("Internal gap h and the capacity law's s* = h/(1+h), against the predicted merge point W/K =", Om / K)
    hs = {}
    for k in tops:
        h = WP.norm_gap(ring_lattice(12, k))
        hs[k] = h
        print(f"  {name[k]}: h {h:.3f}, s* {h / (1 + h):.3f}")
    print("H1. Spread .05, H = 0: merge point (separation falls through .5), and R at the lowest s")
    m0 = {}
    for k in tops:
        g = get(k, 0, .05)
        m0[k] = crossing([r["s"] for r in g], [r["sep"] for r in g], .5)
        print(f"  {name[k]}: merge {m0[k]:.3f}; R at lowest s {g[0]['R']:.3f}; R at merge region {[round(r['R'], 3) for r in g if .14 <= r['s'] <= .26]}")
    print("H2. Spread .4, H = 0: s where R falls below .7, and the merge point")
    for k in tops:
        g = get(k, 0, .4)
        print(f"  {name[k]}: R falls at {crossing([r['s'] for r in g], [r['R'] for r in g], .7):.3f}; merge {crossing([r['s'] for r in g], [r['sep'] for r in g], .5):.3f}; R by s {[round(r['R'], 2) for r in g[::3]]}")
    print("H3, H5. Spread .05: merge point by H")
    for k in tops:
        line = []
        for H in Hs:
            g = get(k, H, .05)
            line.append(crossing([r["s"] for r in g], [r["sep"] for r in g], .5))
        print(f"  {name[k]}: " + ", ".join(f"H={H}: {v:.3f}" for H, v in zip(Hs, line)))
    print("H4. Spread .05, complete: the price. Smallest H keeping separation at .9 or above, by s; then effort by s at H = 1")
    for s in S:
        ok = [H for H in Hs if [r for r in get(6, H, .05) if r["s"] == s][0]["sep"] >= .9]
        e = [r for r in get(6, 1, .05) if r["s"] == s][0]
        print(f"  s {s:.2f}: smallest H {min(ok) if ok else 'none in range'}; at H=1 effort {e['effort']:.4f}, separation {e['sep']:.3f}")


def doors_job(job):
    k, s_target, doors, seeds, K, Om, spread = job
    n = 12
    inner = ring_lattice(n, k)
    D = np.arange(0, n, n // doors)[:doors]
    W = np.zeros((2 * n, 2 * n))
    W[:n, :n] = W[n:, n:] = inner
    for a_ in D:
        for b_ in D:
            W[a_, n + b_] = W[n + b_, a_] = s_target * n / (doors * doors)
    d = np.ones(2 * n)
    for _ in range(400):
        d = np.sqrt(d / np.maximum(W @ d, 1e-280))
    W = W * np.outer(d, d)
    W = (W + W.T) / 2
    s_real = W[:n, n:].sum() / n
    rng = np.random.default_rng([k, int(s_target * 1000), doors])
    xi = rng.normal(0, 1, (seeds, 2 * n))
    xi[:, :n] -= xi[:, :n].mean(1, keepdims=True)
    xi[:, n:] -= xi[:, n:].mean(1, keepdims=True)
    sign = np.r_[np.ones(n), -np.ones(n)]
    omega = Om * sign + spread * xi
    th = rng.normal(0, .1, (seeds, 2 * n))
    dt, T = .05, 400.0
    steps = int(T / dt)

    def f(th_):
        d_ = th_[:, None, :] - th_[:, :, None]
        return omega + K * (W[None] * np.sin(d_)).sum(2)

    R, cnt, burn, start_mean = 0.0, 0, steps // 2, None
    door_rate = None
    for i in range(steps):
        k1 = f(th)
        new = th + dt / 2 * (k1 + f(th + dt * k1))
        if i >= burn:
            if start_mean is None:
                start_mean = th.copy()
            if i % 5 == 0:
                z = np.exp(1j * th)
                R = R + (np.abs(z[:, :n].mean(1)) + np.abs(z[:, n:].mean(1))) / 2
                cnt += 1
        th = new
    rate = (th - start_mean) / ((steps - burn) * dt)
    sep = (rate[:, :n].mean(1) - rate[:, n:].mean(1)) / (2 * Om)
    nd = np.setdiff1d(np.arange(n), D)
    door_sep = (rate[:, D].mean(1) - rate[:, n + D].mean(1)) / (2 * Om)
    rest_sep = (rate[:, nd].mean(1) - rate[:, n + nd].mean(1)) / (2 * Om)
    return dict(k=k, s=float(s_real), doors=doors, R=float(np.median(R / cnt)), sep=float(np.median(np.abs(sep))), door_sep=float(np.median(np.abs(door_sep))), rest_sep=float(np.median(np.abs(rest_sep))))


def part_doors(outdir, pool):
    K, Om, seeds = 2.0, .4, 24
    S = [.05, .1, .15, .2, .25, .3, .35, .4, .5, .6, .7, .85, 1, 1.25, 1.5, 2, 3, 5, 8]  # targets; the site budget caps what is realised
    jobs = [(k, s, 4, seeds, K, Om, .05) for k in (1, 2, 3, 6) for s in S]
    res = pool.map(doors_job, jobs, chunksize=2)
    json.dump(res, open(os.path.join(outdir, "doors.json"), "w"))
    name = {1: "ring k=1", 2: "ring k=2", 3: "ring k=3", 6: "complete"}
    print("H6. Pull through doors only, spread .05, H = 0. Separation falls through .5; R falls through .9; then by realised outward share s: R, separation, door sites' separation, other sites' separation")
    for d in (4,):
        for k in (1, 2, 3, 6):
            g = sorted([r for r in res if r["k"] == k and r["doors"] == d], key=lambda r: r["s"])
            xs = [r["s"] for r in g]
            print(f"  {d} doors, {name[k]}: merge {crossing(xs, [r['sep'] for r in g], .5):.3f}; R below .9 at {crossing(xs, [r['R'] for r in g], .9):.3f}")
            print("     " + " | ".join(f"{r['s']:.3f}: {r['R']:.2f} {r['sep']:.2f} {r['door_sep']:.2f} {r['rest_sep']:.2f}" for r in g[2::2]))
    print("H7. On a narrower range")
    b = json.load(open(os.path.join(outdir, "belonging.json")))
    g = [r for r in b if r["seed"] == 1]
    m1 = [r for r in g if .2 < r["c"] < .8]
    m2 = [r for r in g if .2 < r["a"] < .8]
    print(f"  c in (.2, .8): {len(m1)} cells, Spearman(c, c_true) {spearmanr([r['c'] for r in m1], [r['c_true'] for r in m1]).statistic:.3f}")
    print(f"  a in (.2, .8): {len(m2)} cells, Spearman(a, a_true) {spearmanr([r['a'] for r in m2], [r['a_true'] for r in m2]).statistic:.3f}")
    print("Spread .4 by H, merge point, from the holding run")
    h = json.load(open(os.path.join(outdir, "holding.json")))
    for k in (1, 2, 3, 6):
        line = []
        for H in (0, .2, .5, 1, 2):
            q = sorted([r for r in h if r["k"] == k and r["H"] == H and r["spread"] == .4], key=lambda r: r["s"])
            line.append(f"H={H}: {crossing([r['s'] for r in q], [r['sep'] for r in q], .5):.3f}, lowest R {min(r['R'] for r in q):.2f}")
        print(f"  {name[k]}: " + "; ".join(line))


# ---------- Depth ----------
def part_depth(outdir):
    print("D1, D2. Products of K_2, L = 10. A on true blocks by K levels above; running product of A; escape time to 1/e of the block's excess")
    for r in (.25, .4):
        L = 10
        n = 2 ** L
        tau = r ** np.arange(L)
        tau = tau / tau.sum()
        W = np.zeros((n, n))
        for l in range(L):
            for i in range(n):
                W[i, i ^ (1 << l)] = tau[l]
        s = W.sum(1)
        lam, V, _, inv = WP.spectrum(W)
        sq = np.sqrt(s)
        ts = np.geomspace(1e-2, 1e9, 500)
        rows = []
        for j in range(1, L):
            S = list(range(2 ** j))
            A = WP.autonomy_part(W, s, S)
            law = np.zeros(n); law[S] = 1 / len(S)
            c0 = V.T @ (law / sq)
            floor = len(S) / n
            stay = np.array([(sq * (V @ (np.exp(-lam * t) * c0)))[S].sum() for t in ts])
            x = (stay - floor) / (1 - floor)
            tesc = float(ts[np.argmax(x < np.exp(-1))]) if (x < np.exp(-1)).any() else float("inf")
            rows.append(dict(size=2 ** j, K=L - j, A=float(A), t=tesc))
        rows = rows[::-1]
        prod = 1.0
        sat = 2 / (2 + r / (1 - r))
        print(f"  r = {r}, saturated A = {sat:.4f}")
        for x_ in rows:
            prod *= x_["A"]
            print(f"    K {x_['K']}, size {x_['size']}: A {x_['A']:.4f}; product so far {prod:.4f}; escape time {x_['t']:.2f}")
        tt = [x_["t"] for x_ in rows[::-1]]
        ratios = [tt[i + 1] / tt[i] for i in range(len(tt) - 1)]
        print(f"    escape time ratio per level upward: {[round(v, 3) for v in ratios]}; 1/r = {1 / r:.2f}")


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    parts = sys.argv[2:] or ["belonging", "depth", "holding"]
    with Pool(8, maxtasksperchild=50) as pool:
        for p in parts:
            if p == "belonging":
                part_belonging(outdir, pool)
            elif p == "holding":
                part_holding(outdir, pool)
            elif p == "depth":
                part_depth(outdir)
            elif p == "doors":
                part_doors(outdir, pool)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
