"""Blocks that grow instead of being given. Predictions frozen before any run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, following wholeness_patterns_v1.py. The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte
Results: G1 and G12 passed. G8 passed only vacuously, on one block. G2 missed narrowly: 316 of 320 alone, the rest at G = 2, s = .15, kappa = 64. G3 missed: above s_div all 56 runs reached one, as predicted, but 170 of 560 high-kappa runs reached one too. The cause is my derivation: partners start uniform, so consensus outruns selection, and the upper edge stayed near s_div at kappa = 0 for every kappa.
G4, G5, G7, G9, G10, G11 missed because I set them at s = .7, which is above that edge: there was one block, so nothing to test. That was a design error from the same mistake, and those predictions were never really tried. G6 missed its s = .7 clause; at s = .2 it held exactly (2, 4, 8, 16 blocks in every seed).
After the follow-up: H2, H4, H5, H6, H7, H8 passed; H1 and H3 missed. H1: the band held on G = 3 and 8 except 62% against 75% at G = 8, 1.2 s_hold. H3: selection first holds blocks at kappa = 16 to s = .9, but kappa = 8 reaches one at s = .9 and kappa = 4 reaches one from s = .7, so the formula for this edge is rough. H5: 15 or 16 blocks from noise in all 16 seeds at d = 4. H6: merge .303. H7: threshold 1.00 to 1.05 of u_c. H8: blend 72%, capture 28%, about the 25% chance gives with 3 disagreeing traits.
Totals: 20 frozen; 8 real passes, G8 vacuous, 11 missed. G5, G7, G9, G10, G11 were never really tried and were retried as H2, H6, H7, H8.

Needs numpy. All data are synthetic.
Run: python -I wholeness_growth_v1.py OUTDIR [phase size space small forced push after]

WHY. Every earlier test drew its blocks by hand. Here nothing marks a block: N = 128 sites, all alike, each holding d traits, connected to everyone at the start. If blocks appear they must be read off the result.

LAW. x_i' = -x_i + tanh(G[(1-s) x_i + s sum_j pi_ij x_j]) + noise, for each of d traits. A site keeps 1-s of its budget at home and spends s on others. pi has zero diagonal and row sums 1. Where the budget goes follows similarity, slowly: pi' = (K - pi)/tau, K the doubly scaled kernel exp(kappa q_ij), q_ij = x_i.x_j/d.
So s is how much leaves and kappa is where it goes, the two things the theory separates. Close prior art, from memory: Axelrod's culture model (1997), bounded-confidence opinion models (Deffuant 2000; Hegselmann and Krause 2002), and coevolving networks (Holme and Newman 2006). Expect this behaviour to be known in outline.

A BLOCK is read off the result, not assumed. Sites join if q_ij >= .8, and connected groups of 2 or more are blocks. Separately, the count of eigenvalues above .5 in the symmetrised pi reads them from the relations alone.
Regimes per run: dissolved (mean x^2 < .1); one (largest group >= 90% of sites); alone (<= 10% of sites in blocks); blocks (2 or more blocks, >= 50% of sites in them, largest < 90%); otherwise mixed.

HAND DERIVATIONS.
(a) Below s_hold nothing can move. A trait flips only if the pull beats the site's own hold, and the most the others can pull is all opposed, which is the one-bit pair. So below s_hold(G) (.188 at G = 2, .310 at G = 4) traits are frozen at their starting values. With many possible codes nobody is alike, so every site stays alone at any kappa.
(b) Consensus. With partners chosen by similarity, a partner agrees on each trait on average by t = tanh(kappa/d), which adds to a site's own hold: m = tanh(G((1-s) + s t)m). The shared mode goes unstable when G(1-m^2) = 1, so m* = sqrt(1-1/G), and with g* = atanh(m*)/m*, s_div = (1 - g*/G)/(1 - t).
    kappa = 0: .377 at G = 2, .620 at G = 4. kappa = 2, d = 16: .430 and .708. Past t = g*/G it never happens: kappa_c = 11.7 at G = 2, 6.4 at G = 4.
(c) Corners. Low s: alone, the severance corner. High s with low kappa: one, the absorption corner. High s with high kappa: blocks, integration. G < 1: nothing holds at all, anomie.
(d) Block size. A site's effective partner count at the start is N_eff = N cosh(kappa/d)^(2d) / cosh(2 kappa/d)^d: at N = 128, d = 16, about 19 at kappa = 6, 5.8 at 8, 1.75 at 10, under 1 beyond. Once a group shares a code, q = 1 dominates its kernel and it stops looking outside. So block size should be set near the start, near max(2, N_eff).
(e) Identity space. Blocks cannot outnumber distinct codes, 2^d. When 2^d << N, identical codes exist by chance and blocks form by weights alone, even below s_hold where nothing moves.
(f) Grown blocks should behave like given ones. Inside a block, row sums are about 1, so forced contact t leaves disagreeing traits under m = tanh(G(1-2t)m): merge at s_hold(G). A push on all members has the one-bit threshold u_c: 2.147 at G = 4.
(g) Merging here should blend, not capture. Traits are independent, so nothing votes across them. Each disagreeing trait picks a sign alone, and the merged code overlaps each parent by about .5 in each single run. Stored patterns captured, because their interior voted as one. So capture or blend should depend on whether identity is one coupled thing or a list of independent traits.
(h) Differentiate first. From a small random start, the shared mode grows at G-1 and a site's own at G(1-s)-1. With N = 128 the shared mode has a head start deficit of ln sqrt N and loses by exp(G s t). Forming diversity needs s under about .3 at G = 4, about the same as s_hold, so mobility and diversity barely overlap. So from an undifferentiated start blocks should mostly fail at d = 16, while they grow from committed sites.

PREDICTIONS. Committed random start, noise .02, input spread .05, tau = 20, T = 400, d = 16 unless stated. Every statement is per run, with fractions over seeds.
G1. Anomie. G = .8: dissolved at every s and kappa.
G2. Severance. d = 16: alone at every kappa for s <= .25 at G = 4, and s <= .15 at G = 2.
G3. Absorption. One, at s >= 1.15 s_div, for kappa = 0 and 2, at G = 2 and 4. No seed reaches one at kappa >= 8 at G = 4, or kappa >= 12 at G = 2.
G4. Integration. G = 4, kappa = 8, s = .6, .7, .8, .9: blocks in at least 75% of seeds.
G5. Size. G = 4, s = .7: median block size within a factor of 3 of max(2, N_eff) at kappa = 6, 8, 10, 12, 16, and falling or level as kappa rises.
G6. Identity space. G = 4, kappa = 16: block count never above 2^d. For d = 1, 2, 3, 4 it equals 2^d in at least 75% of seeds, at s = .2 and at s = .7.
G7. Relations match states. G = 4, s = .7, kappa = 8, 10, 12: eigenvalue count within 25% of block count, median over seeds.
G8. Fast inside, slow beyond, unassigned. Same cells: median outward share of a block <= .2 and median A = (1-s_b)h/((1-s_b)h + s_b) >= .5.
G9. Forced contact. G = 4, s = .7, kappa = 8, two grown blocks, weights frozen: median merge within 10% of .310.
G10. Change without joining. Same cells, weights free: threshold within 10% of 2.147. At 1.25 times it, in at least 90% of seeds: members on the new code >= .8, members with each other >= .9, the other block on its own code >= .8, and the two blocks' overlap <= .5.
G11. Blend. Same cells, forced contact at t = .465, weights frozen: disagreeing separation under .1 in at least 90% of seeds; in at least 60%, overlap with each parent lies between .3 and .7; in at most 20% it is >= .85 with either parent.
G12. Differentiate first. G = 4, kappa = 8, small random start: blocks in under 25% of seeds at every s from .1 to .8.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: with partners starting uniform, blocks appear only in a band, s_hold(G) to about 2 s_hold(G). In that band at d = 16 they are nearly all pairs, and at high kappa their outward share is zero. Blocks of useful size came from small identity spaces.
H1. The band, on gains not yet run. G = 3 and 8, kappa = 32, d = 16: alone at s <= .85 s_hold; one at s >= 2.3 s_hold; blocks in at least 75% of seeds at s = 1.2 s_hold and 1.7 s_hold.
H2. Pairs, then severed. G = 3, s = .4, d = 16, kappa = 10, 12, 16, 32: median block size <= 3; eigenvalue count within 25% of block count; A >= .5. Median outward share >= .1 at kappa = 10 and <= .01 at kappa = 32: so selecting harder ends in pairs cut off from everything else.
H3. Selection first moves the upper edge, which is what my derivation of kappa_c assumed. Partners start at the kernel instead of uniform, G = 4, s = .7, .8, .9. At kappa = 8 and 16 no run reaches one, and blocks in at least 75% of seeds at kappa = 16. At kappa = 4, where s_div = .82, one at s = .9 and not at s = .7.
H4. Faster selection does the same, less completely. Uniform start, G = 4, kappa = 16, s = .7: one in under 50% of seeds at tau = 1, against every seed at tau = 20.
H5. Nothing given but the law. Small random start, G = 4, s = .2, kappa = 16, d = 4: blocks in at least 75% of seeds, at least 8 of them. At d = 16 G12 found none.
H6. Grown blocks merge like given ones. G = 4, s = .2, kappa = 16, d = 6, two grown blocks of 3 or more, weights frozen: median merge within 10% of .310.
H7. They change without joining. Same cells, weights free: threshold within 10% of 2.147. At 1.25 times it, in at least 75% of seeds: members on the new code >= .8, members with each other >= .9, the other block on its own code >= .8, and overlap between the blocks <= .5.
H8. Merging blends. Same cells, forced contact at t = .465: merged in at least 90% of seeds; overlap with each parent between .3 and .7 in at least 50%; >= .85 with a parent in at most 40%, since about 3 disagreeing traits go one way by chance about a quarter of the time. Stored patterns were captured in 78% to 100%.
"""
import json
import os
import sys
import time
from math import atanh, cosh, log, sqrt, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

N = 128
DT = .1
EVERY = 10
TAU = 20.0
SG = [.05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .6, .7, .8, .9]
KG = [0, 2, 4, 6, 8, 10, 12, 16, 32, 64]


def s_hold(G):
    m = sqrt(1 - 1 / G)
    return .5 * (1 - atanh(m) / (G * m))


def flip_u(G):
    m = sqrt(1 - 1 / G)
    return abs(atanh(m) - G * m)


def s_div(G, kappa, d=16):
    m = sqrt(1 - 1 / G)
    return (1 - atanh(m) / (m * G)) / (1 - tanh(kappa / d))


def n_eff(kappa, d=16):
    return N * cosh(kappa / d) ** (2 * d) / cosh(2 * kappa / d) ** d


def crossing(xs, ys, level=.5):
    if ys[0] < level:
        return 0.0
    for i in range(len(xs) - 1):
        if ys[i] >= level > ys[i + 1]:
            return float(xs[i] + (ys[i] - level) * (xs[i + 1] - xs[i]) / (ys[i] - ys[i + 1]))
    return float("inf")


def within(x, y, tol):
    return bool(np.isfinite(x) and abs(x - y) <= tol * y)


def verdict(ok):
    return "PASS" if ok else "MISS"


def seed_of(*v):
    return np.random.default_rng([abs(int(round(a * 1000))) for a in v])


def kernel(x, kappa, scale):
    """Target pi from similarity: symmetric scaling, then row sums 1 so the budget holds exactly."""
    d = x.shape[1]
    q = x @ x.T / d
    K = np.exp(kappa * (q - 1))
    np.fill_diagonal(K, 0)
    K = np.maximum(K, 1e-280)
    np.fill_diagonal(K, 0)
    for _ in range(8):
        scale = np.sqrt(scale / np.maximum(K @ scale, 1e-280))
    P = K * np.outer(scale, scale)
    return P / np.maximum(P.sum(1, keepdims=True), 1e-280), scale


def evolve(x, pi, G, s, kappa, T, rng, bias, u=None, plastic=True, sigma=.02, W_fixed=None, scale=None, tau=TAU):
    """W_fixed, if given, replaces (1-s) I + s pi and freezes the weights."""
    steps = int(T / DT)
    amp = sigma * np.sqrt(DT)
    if scale is None:
        scale = np.ones(len(x))
    extra = 0.0 if u is None else u

    def f(y):
        if W_fixed is not None:
            return -y + np.tanh(G * (W_fixed @ y) + bias + extra)
        return -y + np.tanh(G * ((1 - s) * y + s * (pi @ y)) + bias + extra)

    for i in range(steps):
        k1 = f(x)
        x = x + DT / 2 * (k1 + f(x + DT * k1)) + amp * rng.normal(0, 1, x.shape)
        if plastic and W_fixed is None and i % EVERY == 0:
            target, scale = kernel(x, kappa, scale)
            pi = pi + min(1.0, EVERY * DT / tau) * (target - pi)
    return x, pi, scale


def start_state(d, rng, how):
    if how == "committed":
        return rng.choice([-1.0, 1.0], (N, d))
    return rng.normal(0, .03, (N, d))


def grow(G, d, s, kappa, seed, how="committed", T=400.0, first="uniform", tau=TAU):
    rng = seed_of(G, d, s, kappa, seed, how == "small")
    x = start_state(d, rng, how)
    bias = .05 * rng.normal(0, 1, (N, d))
    pi = (np.ones((N, N)) - np.eye(N)) / (N - 1)
    if first == "kernel":
        pi, _ = kernel(x, kappa, np.ones(N))
    x, pi, scale = evolve(x, pi, G, s, kappa, T, rng, bias, tau=tau)
    return x, pi, bias, rng, scale


def groups(x):
    d = x.shape[1]
    q = x @ x.T / d
    adj = q >= .8
    seen = np.zeros(N, bool)
    out = []
    for i in range(N):
        if seen[i]:
            continue
        stack, comp = [i], []
        seen[i] = True
        while stack:
            a = stack.pop()
            comp.append(a)
            for b in np.nonzero(adj[a] & ~seen)[0]:
                seen[b] = True
                stack.append(int(b))
        out.append(comp)
    return [g for g in out if len(g) >= 2]


def read(x, pi):
    Q = float((x ** 2).mean())
    bl = groups(x) if Q >= .1 else []
    sizes = sorted((len(g) for g in bl), reverse=True)
    frac = sum(sizes) / N
    largest = (sizes[0] / N) if sizes else 0.0
    if Q < .1:
        regime = "dissolved"
    elif largest >= .9:
        regime = "one"
    elif frac <= .1:
        regime = "alone"
    elif len(bl) >= 2 and frac >= .5:
        regime = "blocks"
    else:
        regime = "mixed"
    sym = (pi + pi.T) / 2
    ev = int((np.linalg.eigvalsh(sym) > .5).sum())
    sb, A = [], []
    for g in bl:
        idx = np.array(g)
        M = pi[np.ix_(idx, idx)]
        out_ = float(max(0.0, 1 - M.sum(1).mean()))
        Ms = (M + M.T) / 2
        dg = Ms.sum(1)
        if dg.min() <= 0:
            continue
        L = np.eye(len(g)) - Ms / np.sqrt(np.outer(dg, dg))
        h = float(np.sort(np.linalg.eigvalsh(L))[1])
        sb.append(out_)
        A.append((1 - out_) * h / ((1 - out_) * h + out_) if (1 - out_) * h + out_ > 0 else 0.0)
    return dict(Q=Q, n=len(bl), frac=frac, largest=largest, regime=regime, size=float(np.median(sizes)) if sizes else 0.0, ev=ev, sb=float(np.median(sb)) if sb else float("nan"), A=float(np.median(A)) if A else float("nan"))


def grow_job(job):
    G, d, s, kappa, seed, how = job
    x, pi, _, _, _ = grow(G, d, s, kappa, seed, how)
    r = read(x, pi)
    r.update(G=G, d=d, s=s, kappa=kappa, seed=seed, how=how)
    return r


def run(pool, jobs, path, label):
    t0 = time.time()
    res = []
    with open(path, "w") as fh:
        for i, r in enumerate(pool.imap_unordered(grow_job, jobs, chunksize=2)):
            res.append(r)
            fh.write(json.dumps(r) + "\n")
            if (i + 1) % 200 == 0:
                fh.flush()
                print(f"  {label} {i + 1}/{len(jobs)}, {time.time() - t0:.0f}s", flush=True)
    print(f"  {label} done, {len(jobs)} runs, {time.time() - t0:.0f}s", flush=True)
    return res


def after_job(job):
    G, d, s, kappa, seed, how, first, tau = job
    x, pi, _, _, _ = grow(G, d, s, kappa, seed, how, first=first, tau=tau)
    r = read(x, pi)
    r.update(G=G, d=d, s=s, kappa=kappa, seed=seed, how=how, first=first, tau=tau)
    return r


def forced_d(job):
    G, s, kappa, seed, d = job
    x, pi, bias, rng, _ = grow(G, d, s, kappa, seed)
    pair = pick_pair(x)
    if pair is None:
        return dict(seed=seed, ok=False)
    A, B = np.array(pair[0]), np.array(pair[1])
    ca, cb = np.sign(x[A].mean(0)), np.sign(x[B].mean(0))
    dis = ca != cb
    W0 = (1 - s) * np.eye(N) + s * pi

    def with_contact(t):
        W = W0.copy()
        W[A] *= (1 - t)
        W[B] *= (1 - t)
        W[np.ix_(A, B)] += t / len(B)
        W[np.ix_(B, A)] += t / len(A)
        return W

    def sep(y):
        return float(np.abs(y[A][:, dis].mean(0) - y[B][:, dis].mean(0)).mean() / 2)

    T_ = [0, .05, .1, .15, .2, .22, .24, .26, .28, .3, .32, .34, .36, .38, .4, .45, .5, .6]
    ys = []
    for t in T_:
        y, _, _ = evolve(x.copy(), pi, G, s, kappa, 100.0, seed_of(seed, t, 5), bias, plastic=False, W_fixed=with_contact(t))
        ys.append(sep(y))
    merge = crossing(T_, [v / max(ys[0], 1e-9) for v in ys])
    y, _, _ = evolve(x.copy(), pi, G, s, kappa, 150.0, seed_of(seed, 7), bias, plastic=False, W_fixed=with_contact(.465))
    ma = y[A].mean(0)
    return dict(seed=seed, ok=True, sizes=[len(A), len(B)], q=float((ca * cb).mean()), n_dis=int(dis.sum()), merge=merge, sep=sep(y) / max(ys[0], 1e-9), on_a=float(ma @ ca / d), on_b=float(ma @ cb / d))


def push_d(job):
    G, s, kappa, seed, f_, d = job
    x, pi, bias, rng, scale = grow(G, d, s, kappa, seed)
    pair = pick_pair(x)
    if pair is None:
        return dict(seed=seed, f=f_, ok=False)
    A, B = (pair[0], pair[1]) if len(pair[0]) >= len(pair[1]) else (pair[1], pair[0])
    A, B = np.array(A), np.array(B)
    ca, cb = np.sign(x[A].mean(0)), np.sign(x[B].mean(0))
    r2 = seed_of(seed, f_, 9)
    zeta = -ca.copy()
    flip = r2.permutation(d)[:d // 2]
    zeta[flip] = ca[flip]
    u = np.zeros((N, d))
    u[A] = f_ * flip_u(G) * zeta
    y, pi2, scale = evolve(x.copy(), pi.copy(), G, s, kappa, 60.0, r2, bias, u=u, scale=scale)
    y, pi2, scale = evolve(y, pi2, G, s, kappa, 140.0, r2, bias, scale=scale)
    qq = y[A] @ y[A].T / d
    iu = np.triu_indices(len(A), 1)
    return dict(seed=seed, f=f_, ok=True, on_new=float(np.median(y[A] @ zeta / d)), together=float(np.median(qq[iu])), other=float(np.median(y[B] @ cb / d)), between=float(abs(y[A].mean(0) @ y[B].mean(0)) / d))


def part_after(outdir, pool):
    t0 = time.time()
    jobs = []
    for G in (3, 8):
        sh = s_hold(G)
        for f_ in (.5, .85, 1.2, 1.7, 2.3, 2.5):
            s_ = round(f_ * sh, 3)
            if s_ < 1:
                jobs += [(G, 16, s_, 32, seed, "committed", "uniform", TAU) for seed in range(8)]
    jobs += [(3, 16, .4, k, seed, "committed", "uniform", TAU) for k in (10, 12, 16, 32) for seed in range(8)]
    jobs += [(4, 16, s_, k, seed, "committed", "kernel", TAU) for s_ in (.7, .8, .9) for k in (4, 8, 16) for seed in range(8)]
    jobs += [(4, 16, .7, 16, seed, "committed", "uniform", t_) for t_ in (1.0, 5.0) for seed in range(8)]
    jobs += [(4, 4, .2, 16, seed, "small", "uniform", TAU) for seed in range(16)]
    res = pool.map(after_job, jobs, chunksize=2)
    with open(os.path.join(outdir, "after.jsonl"), "w") as fh:
        for r in res:
            fh.write(json.dumps(r) + "\n")
    print(f"  {len(jobs)} runs, {time.time() - t0:.0f}s", flush=True)
    ok = True
    for G in (3, 8):
        sh = s_hold(G)
        g = [r for r in res if r["G"] == G and r["d"] == 16 and r["kappa"] == 32 and r["first"] == "uniform" and not (G == 3 and r["s"] == .4)]
        line = []
        for s_ in sorted(set(r["s"] for r in g)):
            h = [r for r in g if r["s"] == s_]
            fr = {k: float(np.mean([r["regime"] == k for r in h])) for k in ("alone", "blocks", "one", "mixed")}
            line.append(f"{s_ / sh:.2f}: a {fr['alone']:.2f} B {fr['blocks']:.2f} 1 {fr['one']:.2f}")
            if s_ <= .85 * sh + 1e-3:
                ok = ok and fr["alone"] == 1
            if s_ >= 2.3 * sh - 1e-3:
                ok = ok and fr["one"] == 1
            if abs(s_ / sh - 1.2) < .01 or abs(s_ / sh - 1.7) < .01:
                ok = ok and fr["blocks"] >= .75
        print(f"  G {G}, s_hold {sh:.3f}, by s / s_hold: " + " | ".join(line))
    print(f"H1 {verdict(ok)}")
    g2 = [r for r in res if r["G"] == 3 and r["s"] == .4 and r["kappa"] in (10, 12, 16, 32)]
    ok = True
    for k in (10, 12, 16, 32):
        h = [r for r in g2 if r["kappa"] == k and r["seed"] < 8]
        size, nb, ev = np.median([r["size"] for r in h]), np.median([r["n"] for r in h]), np.median([r["ev"] for r in h])
        sb, A = np.nanmedian([r["sb"] for r in h]), np.nanmedian([r["A"] for r in h])
        print(f"  G 3, s .4, kappa {k}: size {size:.1f}; blocks {nb:.0f}; eigenvalues {ev:.0f}; outward {sb:.3f}; A {A:.3f}; regime blocks {np.mean([r['regime'] == 'blocks' for r in h]):.2f}")
        ok = ok and size <= 3 and within(ev, nb, .25) and A >= .5
        if k == 10:
            ok = ok and sb >= .1
        if k == 32:
            ok = ok and sb <= .01
    print(f"H2 {verdict(ok)}")
    g3 = [r for r in res if r["first"] == "kernel"]
    for k in (4, 8, 16):
        print(f"  Selection first, kappa {k}: " + " | ".join(f"s {s_}: one {np.mean([r['regime'] == 'one' for r in g3 if r['kappa'] == k and r['s'] == s_]):.2f}, blocks {np.mean([r['regime'] == 'blocks' for r in g3 if r['kappa'] == k and r['s'] == s_]):.2f}, size {np.median([r['size'] for r in g3 if r['kappa'] == k and r['s'] == s_]):.1f}" for s_ in (.7, .8, .9)))
    a = not any(r["regime"] == "one" for r in g3 if r["kappa"] in (8, 16))
    b = all(np.mean([r["regime"] == "blocks" for r in g3 if r["kappa"] == 16 and r["s"] == s_]) >= .75 for s_ in (.7, .8, .9))
    c = np.mean([r["regime"] == "one" for r in g3 if r["kappa"] == 4 and r["s"] == .9]) >= .75 and np.mean([r["regime"] == "one" for r in g3 if r["kappa"] == 4 and r["s"] == .7]) <= .25
    print(f"H3 {verdict(a and b and c)}: no one at kappa 8, 16 {a}; blocks at 16 {b}; kappa 4 edge {c}")
    g4 = [r for r in res if r["first"] == "uniform" and r["tau"] != TAU]
    print("  Faster selection, s .7, kappa 16: " + " | ".join(f"tau {t_}: one {np.mean([r['regime'] == 'one' for r in g4 if r['tau'] == t_]):.2f}, blocks {np.mean([r['regime'] == 'blocks' for r in g4 if r['tau'] == t_]):.2f}" for t_ in (1.0, 5.0)))
    print(f"H4 {verdict(np.mean([r['regime'] == 'one' for r in g4 if r['tau'] == 1.0]) < .5)}")
    g5 = [r for r in res if r["how"] == "small"]
    print(f"  Nothing given, d 4: blocks regime {np.mean([r['regime'] == 'blocks' for r in g5]):.2f}; counts {[r['n'] for r in g5]}; in blocks {np.median([r['frac'] for r in g5]):.2f}; largest {np.median([r['largest'] for r in g5]):.2f}; size {np.median([r['size'] for r in g5]):.1f}")
    print(f"H5 {verdict(np.mean([r['regime'] == 'blocks' and r['n'] >= 8 for r in g5]) >= .75)}; {time.time() - t0:.0f}s", flush=True)
    r6 = pool.map(forced_d, [(4, .2, 16, seed, 6) for seed in range(32)])
    json.dump(r6, open(os.path.join(outdir, "forced_d.json"), "w"))
    g = [r for r in r6 if r["ok"]]
    print(f"  Forced contact, d 6: {len(g)} of {len(r6)} seeds; sizes {[r['sizes'] for r in g][:6]}; disagreeing traits median {np.median([r['n_dis'] for r in g]):.0f}; parent overlap median {np.median([r['q'] for r in g]):.3f}")
    m = float(np.median([r["merge"] for r in g]))
    print(f"H6 {verdict(within(m, s_hold(4), .10))}: median merge {m:.3f}; per seed {[round(r['merge'], 3) for r in g][:12]}")
    merged = np.mean([r["sep"] < .1 for r in g])
    blend = np.mean([(.3 <= abs(r["on_a"]) <= .7) and (.3 <= abs(r["on_b"]) <= .7) for r in g])
    cap = np.mean([abs(r["on_a"]) >= .85 or abs(r["on_b"]) >= .85 for r in g])
    print(f"H8 {verdict(merged >= .9 and blend >= .5 and cap <= .4)}: merged {merged:.2f}; blend {blend:.2f}; capture {cap:.2f}; per seed {[(round(r['on_a'], 2), round(r['on_b'], 2)) for r in g][:12]}; {time.time() - t0:.0f}s", flush=True)
    fr = (.7, .8, .9, .95, 1.0, 1.05, 1.1, 1.25)
    r7 = pool.map(push_d, [(4, .2, 16, seed, f_, 6) for seed in range(12) for f_ in fr], chunksize=2)
    json.dump(r7, open(os.path.join(outdir, "push_d.json"), "w"))
    line, th = [], float("inf")
    for f_ in fr:
        g = [r for r in r7 if r["f"] == f_ and r["ok"]]
        p = float(np.mean([r["on_new"] >= .8 for r in g]))
        line.append(f"{f_:.2f}: {p:.2f}")
        if p >= .5 and not np.isfinite(th):
            th = f_ * flip_u(4)
    g = [r for r in r7 if r["f"] == 1.25 and r["ok"]]
    good = [r["on_new"] >= .8 and r["together"] >= .9 and r["other"] >= .8 and r["between"] <= .5 for r in g]
    print(f"  Push, d 6, by u / u_c: {', '.join(line)}; threshold {th:.3f}. At 1.25, {len(g)} seeds: on new {np.median([r['on_new'] for r in g]):.3f}; together {np.median([r['together'] for r in g]):.3f}; other on own {np.median([r['other'] for r in g]):.3f}; between {np.median([r['between'] for r in g]):.3f}; all four {np.mean(good):.2f}")
    print(f"H7 {verdict(within(th, flip_u(4), .10) and np.mean(good) >= .75)}; {time.time() - t0:.0f}s", flush=True)


def part_phase(outdir, pool):
    jobs = [(G, 16, s, k, seed, "committed") for G in (2, 4) for s in SG for k in KG for seed in range(4)]
    jobs += [(.8, 16, s, k, 0, "committed") for s in (.1, .5, .9) for k in (0, 8, 64)]
    res = run(pool, jobs, os.path.join(outdir, "phase.jsonl"), "phase")
    letter = dict(dissolved=".", one="1", alone="a", blocks="B", mixed="~")
    for G in (2, 4):
        print(f"G = {G}, d = 16. Commonest regime; rows s, columns kappa {KG}; a alone, 1 one, B blocks, ~ mixed")
        for s in SG:
            row = []
            for k in KG:
                v = [r["regime"] for r in res if r["G"] == G and r["s"] == s and r["kappa"] == k]
                row.append(letter[max(set(v), key=v.count)])
            print(f"  s {s:.2f}: " + " ".join(row))
    g = [r for r in res if r["G"] == .8]
    print(f"G1 {verdict(all(r['regime'] == 'dissolved' for r in g))}: mean x^2 up to {max(r['Q'] for r in g):.3f}")
    bad = [r for r in res if (r["G"] == 4 and r["s"] <= .25) or (r["G"] == 2 and r["s"] <= .15)]
    print(f"G2 {verdict(all(r['regime'] == 'alone' for r in bad))}: {sum(r['regime'] == 'alone' for r in bad)} of {len(bad)} alone; largest fraction in blocks {max(r['frac'] for r in bad):.3f}")
    a = [r for r in res if r["G"] in (2, 4) and r["kappa"] in (0, 2) and r["s"] >= 1.15 * s_div(r["G"], r["kappa"])]
    b = [r for r in res if (r["G"] == 4 and r["kappa"] >= 8) or (r["G"] == 2 and r["kappa"] >= 12)]
    print(f"G3 {verdict(all(r['regime'] == 'one' for r in a) and not any(r['regime'] == 'one' for r in b))}: above s_div {sum(r['regime'] == 'one' for r in a)} of {len(a)} one; high kappa {sum(r['regime'] == 'one' for r in b)} of {len(b)} one")
    c = [r for r in res if r["G"] == 4 and r["kappa"] == 8 and r["s"] in (.6, .7, .8, .9)]
    by = {s: np.mean([r["regime"] == "blocks" for r in c if r["s"] == s]) for s in (.6, .7, .8, .9)}
    print(f"G4 {verdict(all(v >= .75 for v in by.values()))}: {by}")


def part_size(outdir, pool):
    K = (6, 8, 10, 12, 16)
    res = run(pool, [(4, 16, .7, k, seed, "committed") for k in K for seed in range(8)], os.path.join(outdir, "size.jsonl"), "size")
    med = {k: float(np.median([r["size"] for r in res if r["kappa"] == k])) for k in K}
    pred = {k: max(2.0, n_eff(k)) for k in K}
    print("By kappa: median block size, predicted, blocks, eigenvalue count, outward share, A, regime count")
    for k in K:
        g = [r for r in res if r["kappa"] == k]
        print(f"  {k}: size {med[k]:.1f}, predicted {pred[k]:.1f}; blocks {np.median([r['n'] for r in g]):.0f}; eigenvalues {np.median([r['ev'] for r in g]):.0f}; outward {np.nanmedian([r['sb'] for r in g]):.3f}; A {np.nanmedian([r['A'] for r in g]):.3f}; regime blocks {np.mean([r['regime'] == 'blocks' for r in g]):.2f}")
    ok = all(pred[k] / 3 <= med[k] <= pred[k] * 3 for k in K) and all(med[K[i]] >= med[K[i + 1]] for i in range(len(K) - 1))
    print(f"G5 {verdict(ok)}")
    ok7, ok8 = True, True
    for k in (8, 10, 12):
        g = [r for r in res if r["kappa"] == k]
        nb, ev = np.median([r["n"] for r in g]), np.median([r["ev"] for r in g])
        ok7 = ok7 and within(ev, nb, .25)
        ok8 = ok8 and np.nanmedian([r["sb"] for r in g]) <= .2 and np.nanmedian([r["A"] for r in g]) >= .5
    print(f"G7 {verdict(ok7)}; G8 {verdict(ok8)}")


def part_space(outdir, pool):
    D = (1, 2, 3, 4, 6, 8, 12, 16)
    res = run(pool, [(4, d, s, 16, seed, "committed") for d in D for s in (.2, .7) for seed in range(8)], os.path.join(outdir, "space.jsonl"), "space")
    ok = True
    for s in (.2, .7):
        print(f"s = {s}. By d: median blocks, median size, fraction of sites in blocks, 2^d")
        for d in D:
            g = [r for r in res if r["d"] == d and r["s"] == s]
            print(f"  d {d}: blocks {np.median([r['n'] for r in g]):.0f}; size {np.median([r['size'] for r in g]):.1f}; in blocks {np.median([r['frac'] for r in g]):.2f}; 2^d {2 ** d}; equal {np.mean([r['n'] == 2 ** d for r in g]):.2f}")
            ok = ok and all(r["n"] <= 2 ** d for r in g)
            if d <= 4:
                ok = ok and np.mean([r["n"] == 2 ** d for r in g]) >= .75
    print(f"G6 {verdict(ok)}")


def part_small(outdir, pool):
    S = (.1, .2, .3, .4, .5, .6, .7, .8)
    res = run(pool, [(4, 16, s, 8, seed, "small") for s in S for seed in range(8)], os.path.join(outdir, "small.jsonl"), "small")
    ok = True
    print("Small start. By s: fraction of seeds in each regime")
    for s in S:
        g = [r for r in res if r["s"] == s]
        fr = {k: float(np.mean([r["regime"] == k for r in g])) for k in ("alone", "one", "blocks", "mixed", "dissolved")}
        print(f"  {s}: {fr}; median blocks {np.median([r['n'] for r in g]):.0f}")
        ok = ok and fr["blocks"] < .25
    print(f"G12 {verdict(ok)}")


def pick_pair(x):
    bl = [g for g in groups(x) if len(g) >= 3]
    if len(bl) < 2:
        return None
    bl = sorted(bl, key=len, reverse=True)[:8]
    best, pair = 9.0, None
    for i in range(len(bl)):
        for j in range(i + 1, len(bl)):
            q = abs(float((np.sign(x[bl[i]].mean(0)) * np.sign(x[bl[j]].mean(0))).mean()))
            if q < best:
                best, pair = q, (bl[i], bl[j])
    return pair


def forced_job(job):
    G, s, kappa, seed = job
    x, pi, bias, rng, _ = grow(G, 16, s, kappa, seed)
    pair = pick_pair(x)
    if pair is None:
        return dict(seed=seed, ok=False)
    A, B = np.array(pair[0]), np.array(pair[1])
    ca, cb = np.sign(x[A].mean(0)), np.sign(x[B].mean(0))
    dis = ca != cb
    W0 = (1 - s) * np.eye(N) + s * pi

    def with_contact(t):
        W = W0.copy()
        W[A] *= (1 - t)
        W[B] *= (1 - t)
        W[np.ix_(A, B)] += t / len(B)
        W[np.ix_(B, A)] += t / len(A)
        return W

    def sep(y):
        return float(np.abs(y[A][:, dis].mean(0) - y[B][:, dis].mean(0)).mean() / 2)

    T_ = [0, .05, .1, .15, .2, .22, .24, .26, .28, .3, .32, .34, .36, .38, .4, .45, .5, .6]
    ys = []
    for t in T_:
        r2 = seed_of(seed, t, 5)
        y, _, _ = evolve(x.copy(), pi, G, s, kappa, 100.0, r2, bias, plastic=False, W_fixed=with_contact(t))
        ys.append(sep(y))
    merge = crossing(T_, [v / max(ys[0], 1e-9) for v in ys])
    y, _, _ = evolve(x.copy(), pi, G, s, kappa, 150.0, seed_of(seed, 7), bias, plastic=False, W_fixed=with_contact(.465))
    ma = y[A].mean(0)
    return dict(seed=seed, ok=True, sizes=[len(A), len(B)], q=float((ca * cb).mean()), merge=merge, sep=sep(y) / max(ys[0], 1e-9), on_a=float(ma @ ca / 16), on_b=float(ma @ cb / 16))


def part_forced(outdir, pool):
    res = pool.map(forced_job, [(4, .7, 8, seed) for seed in range(16)])
    json.dump(res, open(os.path.join(outdir, "forced.json"), "w"))
    g = [r for r in res if r["ok"]]
    print(f"Forced contact: {len(g)} of {len(res)} seeds had two blocks of 3 or more; sizes {[r['sizes'] for r in g][:6]}; parent overlap median {np.median([r['q'] for r in g]):.3f}")
    m = float(np.median([r["merge"] for r in g]))
    print(f"G9 {verdict(within(m, s_hold(4), .10))}: median merge {m:.3f}, s_hold {s_hold(4):.3f}; per seed {[round(r['merge'], 3) for r in g]}")
    merged = np.mean([r["sep"] < .1 for r in g])
    blend = np.mean([(.3 <= abs(r["on_a"]) <= .7) and (.3 <= abs(r["on_b"]) <= .7) for r in g])
    cap = np.mean([abs(r["on_a"]) >= .85 or abs(r["on_b"]) >= .85 for r in g])
    print(f"G11 {verdict(merged >= .9 and blend >= .6 and cap <= .2)}: merged {merged:.2f}; blend {blend:.2f}; capture {cap:.2f}; per seed {[(round(r['on_a'], 2), round(r['on_b'], 2)) for r in g]}")


def push_job(job):
    G, s, kappa, seed, f_ = job
    x, pi, bias, rng, scale = grow(G, 16, s, kappa, seed)
    pair = pick_pair(x)
    if pair is None:
        return dict(seed=seed, f=f_, ok=False)
    A, B = (pair[0], pair[1]) if len(pair[0]) >= len(pair[1]) else (pair[1], pair[0])
    A, B = np.array(A), np.array(B)
    ca, cb = np.sign(x[A].mean(0)), np.sign(x[B].mean(0))
    r2 = seed_of(seed, f_, 9)
    zeta = r2.choice([-1.0, 1.0], 16)
    u = np.zeros((N, 16))
    u[A] = f_ * flip_u(G) * zeta
    y, pi2, scale = evolve(x.copy(), pi.copy(), G, s, kappa, 60.0, r2, bias, u=u, scale=scale)
    y, pi2, scale = evolve(y, pi2, G, s, kappa, 140.0, r2, bias, scale=scale)
    qq = y[A] @ y[A].T / 16
    iu = np.triu_indices(len(A), 1)
    return dict(seed=seed, f=f_, ok=True, on_new=float(np.median(y[A] @ zeta / 16)), together=float(np.median(qq[iu])), other=float(np.median(y[B] @ cb / 16)), between=float(abs(y[A].mean(0) @ y[B].mean(0)) / 16), start_q=float(abs(ca @ zeta) / 16))


def part_push(outdir, pool):
    fr = (.7, .8, .9, .95, 1.0, 1.05, 1.1, 1.25)
    res = pool.map(push_job, [(4, .7, 8, seed, f_) for seed in range(12) for f_ in fr], chunksize=2)
    json.dump(res, open(os.path.join(outdir, "push.json"), "w"))
    ok_th = False
    line = []
    th = float("inf")
    for f_ in fr:
        g = [r for r in res if r["f"] == f_ and r["ok"]]
        p = float(np.mean([r["on_new"] >= .8 for r in g]))
        line.append(f"{f_:.2f}: {p:.2f}")
        if p >= .5 and not np.isfinite(th):
            th = f_ * flip_u(4)
    print(f"Push on a grown block, by u / u_c: {', '.join(line)}; threshold {th:.3f}, u_c {flip_u(4):.3f}")
    g = [r for r in res if r["f"] == 1.25 and r["ok"]]
    good = [r["on_new"] >= .8 and r["together"] >= .9 and r["other"] >= .8 and r["between"] <= .5 for r in g]
    print(f"  At 1.25 u_c, {len(g)} seeds: on new {np.median([r['on_new'] for r in g]):.3f}; members together {np.median([r['together'] for r in g]):.3f}; other block on its own {np.median([r['other'] for r in g]):.3f}; between {np.median([r['between'] for r in g]):.3f}; all four {np.mean(good):.2f}")
    print(f"G10 {verdict(within(th, flip_u(4), .10) and np.mean(good) >= .9)}")


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    parts = sys.argv[2:] or ["phase", "size", "space", "small", "forced", "push"]
    with Pool(8, maxtasksperchild=200) as pool:
        for p in parts:
            if p == "phase":
                part_phase(outdir, pool)
            elif p == "size":
                part_size(outdir, pool)
            elif p == "space":
                part_space(outdir, pool)
            elif p == "small":
                part_small(outdir, pool)
            elif p == "forced":
                part_forced(outdir, pool)
            elif p == "push":
                part_push(outdir, pool)
            elif p == "after":
                part_after(outdir, pool)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
