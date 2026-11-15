"""Identity as a pattern rather than one bit: can a part change without merging? Predictions frozen before any site-level run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, following wholeness_reference_v1.py. The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte
Results: V2, V4, V5, V6, P6 passed; 9 of 14 missed. The central claim held: V5, change without joining, 100% of seeds. Misses, which stand as frozen:
V1: limits .459, .587, .668, .789 against .455, .634, .725, .863, and past s_u the blocks do not dissolve at G >= 3 (mean x^2 .94 to 1.0). After the fact: the uniform mode has gain G s (1-m^2), and reaching 1 fits within 2.5%, so the blocks jump to a shared uniform state.
V3: own vocabulary .336, .348, .367, .410 against .375, .45, .43, .435; above shared at every G, by 1.85, 1.33, 1.20, 1.07, so the 1.3 clause failed at G = 4.
P1: G = 1.9 still at .668 after 4 tau. P2: nothing formed at G = 3, 75% at G = 4, and the overlap statistics were contaminated by unsettled seeds. P3: thresholds 1.254 and 2.081 against .965 and 1.81, inf at G = 2.5 inside its grid; but after rewriting nothing of the old pattern remained.
P4: .161, .209, .269, .370 against .135, .195, .265, .370; exact at high gain, and G = 8 is only 10% below own vocabulary; at G = 2.5 and 3 the blocks merge rather than dissolve as I said. P5: at G = 4 the medians read .500 and .499, which looked right, and at G = 8 one pattern captured the other. A3 shows the G = 4 reading was the median of a two-sided outcome: per seed one pattern won whole there too. P7: .54 at s = .02, then noisy, reliably above .5 from s = .05.
B1: .254, .289, .304, .305, .285, .270 against .26 to .435; gain helps to beta about 16, then hurts.
After the follow-up: A1 and A4 passed, A2 and A3 missed. A1: G = 1.9 reached .003 by 20 tau; with a 12 tau push, thresholds 1.013 and 1.901 against .965 and 1.81. A2: with top gain 3 all seeds settled and different W0 gave |overlap| .09, but the same W0 gave .511 and .314, so noise helps pick the pattern. A3: no blending; capture in 100% of seeds up to s = .44, .94 and .78 at s = .50, with either block winning; so the third pattern I derived does not form. A4: .355, .365, .385, .395, rising, within 10% of the solver.
Totals: 7 of 18 passed, 11 missed.

Needs numpy. All data are synthetic.
Run: python -I wholeness_patterns_v1.py OUTDIR [solve vocab switch plastic budget after]
"solve" prints the mean-field numbers used below, and was run before the predictions were written. It simulates no sites.

WHY. In wholeness_reference_v1.py identity was one bit, so rewriting yourself meant joining the other block, and "still adapting" could not be tested. Here each block holds a pattern over its sites.

LAW. x' = -x + tanh(G[(1-s) W x + s C y]), two blocks of 64 sites, orthogonal balanced patterns (Walsh rows), W = (1/n) sum over stored patterns of xi xi^T, so each stored pattern has eigenvalue 1. C is the contact.

HAND DERIVATIONS.
(a) What contact can read. Uniform contact, C = (1/n) 1 1^T, reads only the other block's mean, and a balanced pattern has mean zero. So the pull is zero at any s. A pattern is lost only when the interior starves: m = tanh(G(1-s)m), which ends at s_u = 1 - 1/G, and both blocks dissolve instead of merging. Separation halves at s = 1 - atanh(m0/2)/(G m0/2): .455, .634, .725, .863 at G = 2, 3, 4, 8.
(b) Aligned contact, C = I, joins site i to site i. With orthogonal patterns half the sites agree and half disagree.
    Shared vocabulary (both blocks store both patterns). On the disagreeing half, xi_i xi_j + eta_i eta_j = 2 xi_i xi_j, and between the halves it is 0. So the halves decouple exactly, and the disagreeing half obeys the one-bit law. Merge = s_hold(G): .188, .266, .310, .386.
    Own vocabulary (each stores only its own). Then a = tanh(G((1-s)m + s a)), b = tanh(G((1-s)m - s b)), m = (a+b)/2. Agreeing sites support each other across blocks, so the interior still sees m, and it holds further. Separation fades, or a disagreeing pair commits to a shared sign once G s (1-b^2) >= 1. Solver: .375 (fade), .45, .43, .435 (pairs commit).
    Reading to test: what both can represent is where one can be pulled into the other.
(c) More stored patterns. Modes not excited stay at zero by orthogonality, so four stored patterns should change little.
(d) Changing without merging. A at xi1, B at xi2, push A along xi3 with input u. On the sites where xi1 and xi3 disagree the same reduction gives b = tanh(G b - u), so the threshold is the one-bit flip, u_c = |atanh(m*) - G m*|: .533 at G = 2, 2.147 at G = 4. After release A holds xi3, which is orthogonal to B's xi2. So it has changed and has not joined. Pushing back returns it, since xi1 is still stored.
    A pattern outside the vocabulary cannot be kept: W sends it to zero. So a fixed vocabulary can return but cannot learn.
(e) A self-writing interior. W' = (x x^T/n - W)/tau, tau >> 1, nobody stores anything. Rank one: W x = x <x^2>, so m = tanh(G m^3). Zero is always stable, and a self-sustaining state needs G above 2.017 (solver). So it needs a seed and enough gain.
    From a random symmetric W0 with top gain above 1, activity falls onto W0's leading modes, and Hebb locks them in. So a pattern can form with no input. The pattern is set by W0 and noise, and W0 fades.
(f) Self-writing under contact. Slowly, W tracks activity, so a = tanh(G((1-s)Q + s)a), b = tanh(G((1-s)Q - s)b), Q = (a^2+b^2)/2. As b falls Q falls, which lowers the interior's vote, a runaway. Limit: .135, .195, .265, .370 at G = 2.5, 3, 4, 8. At 2.5 and 3 a collapses too, so the blocks dissolve. At 4 and 8 a stays near 1.
    Above the limit, disagreeing pairs have gain (1-b^2) G((1-s)Q + s) on their shared mode, so each pair picks a shared sign by itself. The blocks should end as one new pattern: agreeing sites kept, the rest decided site by site. Overlap with each parent about .5. They become a third thing, not the one or the other.
    Erosion is slow, so between this limit and the fixed limit, time to merge should scale with tau.
(g) Self-writing under a push. a = tanh(G Q a + u), b = tanh(G Q b - u). The vote weakens as b falls, so a sustained push rewrites more easily than a fixed block allows: u_p .555, .965, 1.81 against u_c .905, 1.303, 2.147 at G = 2.5, 3, 4. After rewriting nothing of the old pattern is left. So it can learn but cannot return.
(h) Keep versus make. Two blocks with independent W0, aligned contact from the start. The shared mode's top gain is about G(s + (1-s) lambda0/sqrt 2), each block's alone about G(1-s) lambda0, which cross near s = .10 at G = 4. So they should form one pattern above about .10, while once formed they keep two up to .265.
(i) A law that is not a sigmoid and has non-negative weights. K assemblies, each with uniform positive weights; a block budget: x_i target = (n/K) softmax(beta h_i), h = (1-s) (mean of own assembly) + s (aligned site). Every block always has an active assembly, unlike the on-off law where an off block has nothing to push back with. So gain should help again. Solver, K = 4: .26, .31, .36, .39, .42, .435 at beta = 6, 8, 12, 16, 24, 32.

PREDICTIONS. Noise .02 and input spread .05 throughout unless stated. Merge is separation falling through half its value at s = 0.
V1. Uniform contact: merge within 5% of .455, .634, .725, .863, and at s_u + .05 mean x^2 is under .05: dissolved, not merged.
V2. Shared vocabulary, aligned: merge within 5% of .188, .266, .310, .386.
V3. Own vocabulary, aligned: merge within 10% of .375, .45, .43, .435, above shared at every G, and at least 1.3 times it at G = 2, 3, 4.
V4. Four stored patterns: shared within 15% of V2's values, own within 15% of V3's.
V5. Changing without merging. Shared vocabulary of 4. Threshold at s = 0 within 10% of u_c at G = 2 and 4. At u = 1.25 u_c, at s = .1 for both G and also s = .2 at G = 4, in at least 90% of seeds: after release A has overlap >= .8 with xi3 and |overlap| <= .2 with B's pattern, and B keeps overlap >= .8 with its own. Pushing back returns A to xi1 with overlap >= .8.
V6. Outside the vocabulary. G = 4, u = 3 u_c along an unstored pattern: after release |overlap| with it <= .2 in at least 90% of seeds.
P1. Self-writing, imprinted, no contact, after 4 tau: mean x^2 >= .5 at G = 2.2, 2.5, 3, 4, and <= .1 at G = 1.6, 1.9.
P2. Formation from noise, G = 3 and 4, top gain 1.5, no input, after 6 tau: mean x^2 >= .5 in at least 90% of seeds. Different W0: median |overlap| <= .25. Same W0, different noise: median |overlap| >= .5.
P3. Sustained push for 3 tau: threshold within 15% of .555, .965, 1.81, and below u_c. After rewriting and 3 tau more: overlap with the new pattern >= .8, |overlap| with the old <= .2.
P4. Self-writing under aligned contact, after 6 tau: merge within 15% of .135, .195, .265, .370, and at least 25% below V3's value at G = 3, 4, 8.
P5. Past the limit, 1.2 times it, G = 4 and 8, after 6 tau: separation under .1 of its start, mean x^2 >= .7, A's overlap with each parent between .35 and .65, and A and B overlap >= .9 with each other.
P6. G = 4, s = .33, time to merge at tau = 200 over tau = 50 between 2.5 and 6.
P7. G = 4, independent W0, contact from the start: the median overlap of A and B first reaches .5 at an s between .04 and .2, below P4's limit at G = 4.
B1. Budget law, K = 4: merge within 15% of the solver at each beta, rising at every step. The on-off law fell from .11 to .003.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Four of the misses look like things a small run can settle.
A1. P1 and P3 were time-limited, since near threshold the state passes slowly. G = 1.9 falls to mean x^2 <= .1 by 20 tau. With a 12 tau push, thresholds come within 10% of .965 and 1.81 at G = 3 and 4.
A2. P2 failed for want of a strong enough seed: to reach the self-sustaining branch, activity must clear m_u, about .63 at G = 3 and .52 at G = 4. With top gain 3, in at least 90% of seeds a pattern forms at G = 3 and 4. Counting only settled seeds: different W0 median |overlap| <= .25, same W0 >= .5.
A3. Two ways of merging. Past the fixed limit, W still votes for the old patterns while pairs commit, so one pattern should win whole (capture). Between the plastic and fixed limits, W follows activity and pairs decide alone, so a third pattern should form (blend). Per seed: capture means A's |overlap| with a parent >= .85; blend means both in .3 to .7.
    G = 4: blend in at least 70% of seeds at s = .30, .33; capture in at least 70% at s = .42, .50. G = 8: blend at s = .385; capture at s = .44, .50. Each block wins between 25% and 75% of captures.
A4. B1's fall at high beta comes from site-level competition driven by heterogeneity. With input spread and noise a tenth as large, merge is within 15% of the solver at beta = 12, 16, 24, 32 and rises at every step.
"""
import json
import os
import sys
import time
from math import atanh, sqrt, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

N = 64
A_ROWS = (1, 2, 4, 8)
B_ROWS = (16, 32, 7, 56)
GS = (2, 3, 4, 8)


def walsh(i):
    return np.array([(-1.0) ** bin(i & j).count("1") for j in range(N)])


def stored(rows):
    P = np.array([walsh(r) for r in rows])
    return P.T @ P / N


def s_hold(G):
    m = sqrt(1 - 1 / G)
    return .5 * (1 - atanh(m) / (G * m))


def flip_u(G):
    m = sqrt(1 - 1 / G)
    return abs(atanh(m) - G * m)


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


def bias(rng, seeds, spread=.05):
    xi = rng.normal(0, 1, (seeds, 2 * N))
    xi[:, :N] -= xi[:, :N].mean(1, keepdims=True)
    xi[:, N:] -= xi[:, N:].mean(1, keepdims=True)
    return spread * xi


# ---------- Fixed vocabularies ----------
CONFIG = {
    "own": (A_ROWS[:1], B_ROWS[:1], A_ROWS[0], B_ROWS[0], "aligned"),
    "shared": (A_ROWS[:2], A_ROWS[:2], A_ROWS[0], A_ROWS[1], "aligned"),
    "own4": (A_ROWS, B_ROWS, A_ROWS[0], B_ROWS[0], "aligned"),
    "shared4": (A_ROWS, A_ROWS, A_ROWS[0], A_ROWS[1], "aligned"),
    "uniform": (A_ROWS[:1], B_ROWS[:1], A_ROWS[0], B_ROWS[0], "uniform"),
}


def fixed_field(G, s, Wa, Wb, contact, b):
    def f(x, ua=0.0):
        xa, xb = x[:, :N], x[:, N:]
        if contact == "uniform":
            ca, cb = xb.mean(1, keepdims=True), xa.mean(1, keepdims=True)
        else:
            ca, cb = xb, xa
        ha = G * ((1 - s) * (xa @ Wa) + s * ca) + b[:, :N] + ua
        hb = G * ((1 - s) * (xb @ Wb) + s * cb) + b[:, N:]
        return -x + np.tanh(np.concatenate([ha, hb], 1))
    return f


def step_fixed(f, x, rng, ua=0.0, dt=.05, sigma=.02):
    k1 = f(x, ua)
    x = x + dt / 2 * (k1 + f(x + dt * k1, ua))
    return x + sigma * np.sqrt(dt) * rng.normal(0, 1, x.shape)


def vocab_job(job):
    name, G, s, seeds, T = job
    va, vb, pa, pb, contact = CONFIG[name]
    Wa, Wb = stored(va), stored(vb)
    rng = seed_of(len(name), G, s, pa, pb)
    b = bias(rng, seeds)
    xia, xib = walsh(pa), walsh(pb)
    x = np.tile(np.r_[xia, xib], (seeds, 1))
    f = fixed_field(G, s, Wa, Wb, contact, b)
    steps = int(T / .05)
    D, Q, cnt = 0.0, 0.0, 0
    for i in range(steps):
        x = step_fixed(f, x, rng)
        if i >= steps * 3 // 4 and i % 5 == 0:
            D = D + np.abs(x[:, :N] - x[:, N:]).mean(1) / 2
            Q = Q + (x ** 2).mean(1)
            cnt += 1
    return dict(name=name, G=G, s=s, D=float(np.median(D / cnt)), Q=float(np.median(Q / cnt)))


def part_vocab(outdir, pool):
    S = [0.0] + [round(.005 * i, 3) for i in range(1, 101)] + [round(.5 + .02 * i, 3) for i in range(1, 24)]
    jobs = [(name, G, s, 12, 200.0) for name in CONFIG for G in GS for s in S]
    t0 = time.time()
    res = []
    with open(os.path.join(outdir, "vocab.jsonl"), "w") as fh:
        for i, r in enumerate(pool.imap_unordered(vocab_job, jobs, chunksize=4)):
            res.append(r)
            fh.write(json.dumps(r) + "\n")
            if (i + 1) % 500 == 0:
                fh.flush()
                print(f"  vocab {i + 1}/{len(jobs)}, {time.time() - t0:.0f}s", flush=True)
    print(f"  vocab done, {time.time() - t0:.0f}s", flush=True)
    tab = {}
    for name in CONFIG:
        for G in GS:
            g = sorted([r for r in res if r["name"] == name and r["G"] == G], key=lambda r: r["s"])
            tab[(name, G)] = crossing([r["s"] for r in g], [r["D"] / g[0]["D"] for r in g])
    print("Merge by vocabulary, G = 2, 3, 4, 8")
    for name in CONFIG:
        print(f"  {name}: " + ", ".join(f"{tab[(name, G)]:.3f}" for G in GS))
    v1 = dict(zip(GS, (.455, .634, .725, .863)))
    v3 = dict(zip(GS, (.375, .45, .43, .435)))
    ok = all(within(tab[("uniform", G)], v1[G], .05) for G in GS)
    qs = []
    for G in GS:
        su = 1 - 1 / G
        g = min([r for r in res if r["name"] == "uniform" and r["G"] == G], key=lambda r: abs(r["s"] - su - .05))
        qs.append(round(g["Q"], 3))
    print(f"V1 {verdict(ok and all(q < .05 for q in qs))}: mean x^2 just past s_u {qs}")
    print(f"V2 {verdict(all(within(tab[('shared', G)], s_hold(G), .05) for G in GS))}: against {[round(s_hold(G), 3) for G in GS]}")
    a = all(within(tab[("own", G)], v3[G], .10) for G in GS)
    b_ = all(tab[("own", G)] > tab[("shared", G)] for G in GS)
    c = all(tab[("own", G)] >= 1.3 * tab[("shared", G)] for G in (2, 3, 4))
    print(f"V3 {verdict(a and b_ and c)}: within 10% {a}; above shared {b_}; 1.3 times at G 2, 3, 4 {c}; ratios {[round(tab[('own', G)] / tab[('shared', G)], 2) for G in GS]}")
    d = all(within(tab[("shared4", G)], tab[("shared", G)], .15) and within(tab[("own4", G)], tab[("own", G)], .15) for G in GS)
    print(f"V4 {verdict(d)}")


def switch_job(job):
    """A at xi1, B at xi2, in a shared vocabulary of 4. Push A along target, release, optionally push back."""
    G, s, u, target, back, seeds = job
    W = stored(A_ROWS)
    rng = seed_of(G, s, u, target, back)
    b = bias(rng, seeds)
    xi1, xi2 = walsh(A_ROWS[0]), walsh(A_ROWS[1])
    tgt = walsh(target)
    x = np.tile(np.r_[xi1, xi2], (seeds, 1))
    f = fixed_field(G, s, W, W, "aligned", b)
    for _ in range(int(60 / .05)):
        x = step_fixed(f, x, rng, u * tgt)
    for _ in range(int(140 / .05)):
        x = step_fixed(f, x, rng)
    ov = lambda p, a: (x[:, a * N:(a + 1) * N] @ p) / N
    out = dict(G=G, s=s, u=u, target=target, back=back, on_target=[float(v) for v in ov(tgt, 0)], on_b=[float(v) for v in ov(xi2, 0)], b_own=[float(v) for v in ov(xi2, 1)])
    if back:
        for _ in range(int(60 / .05)):
            x = step_fixed(f, x, rng, u * xi1)
        for _ in range(int(100 / .05)):
            x = step_fixed(f, x, rng)
        out["back_on"] = [float(v) for v in ov(xi1, 0)]
    return out


def part_switch(outdir, pool):
    xi3 = A_ROWS[2]
    fr = (.7, .8, .9, .95, 1.0, 1.05, 1.1, 1.2, 1.3, 1.5)
    jobs = [(G, 0.0, f * flip_u(G), xi3, False, 16) for G in (2, 4) for f in fr]
    jobs += [(2, .1, 1.25 * flip_u(2), xi3, True, 32), (4, .1, 1.25 * flip_u(4), xi3, True, 32), (4, .2, 1.25 * flip_u(4), xi3, True, 32)]
    jobs += [(4, .1, 3 * flip_u(4), B_ROWS[0], False, 32)]
    res = pool.map(switch_job, jobs)
    json.dump(res, open(os.path.join(outdir, "switch.json"), "w"))
    ok = True
    print("Changing without merging. Threshold at s = 0: fraction of seeds reaching the target, by u / u_c")
    for G in (2, 4):
        g = sorted([r for r in res if r["G"] == G and r["s"] == 0], key=lambda r: r["u"])
        fracs = [float(np.mean(np.array(r["on_target"]) >= .8)) for r in g]
        print(f"  G {G}, u_c {flip_u(G):.3f}: " + ", ".join(f"{r['u'] / flip_u(G):.2f}: {p:.2f}" for r, p in zip(g, fracs)))
        th = next((r["u"] for r, p in zip(g, fracs) if p >= .5), float("inf"))
        ok = ok and within(th, flip_u(G), .10)
    ok2 = True
    for r in [r for r in res if r["back"]]:
        t, o, bo, ba = (np.array(r[k]) for k in ("on_target", "on_b", "b_own", "back_on"))
        good = (t >= .8) & (np.abs(o) <= .2) & (bo >= .8)
        print(f"  G {r['G']}, s {r['s']}, u {r['u']:.3f}: changed without joining {good.mean():.2f}; medians on target {np.median(t):.3f}, on B's pattern {np.median(o):.3f}, B on its own {np.median(bo):.3f}; returned {np.mean(ba >= .8):.2f}, median {np.median(ba):.3f}")
        ok2 = ok2 and good.mean() >= .9 and np.mean(ba >= .8) >= .9
    print(f"V5 {verdict(ok and ok2)}: threshold {ok}; changed and returned {ok2}")
    r = [r for r in res if r["target"] == B_ROWS[0]][0]
    t = np.abs(np.array(r["on_target"]))
    print(f"V6 {verdict(np.mean(t <= .2) >= .9)}: fraction with |overlap| <= .2 {np.mean(t <= .2):.2f}; median {np.median(t):.3f}")


# ---------- Self-writing interiors ----------
def plastic_run(G, s, tau, T, seeds, rng, xa0=None, xb0=None, Wa0=None, Wb0=None, push=None, push_T=0.0, record=False, dt=.1, every=5, sigma=.02):
    b = bias(rng, seeds)
    x = np.zeros((seeds, 2 * N))
    x[:, :N] = xa0
    x[:, N:] = xb0
    Wa = np.array(Wa0, float)
    Wb = np.array(Wb0, float)
    rate = every * dt / tau
    amp = sigma * np.sqrt(dt)
    trace = []
    steps = int(T / dt)
    u = 0.0

    def f(y):
        ya, yb = y[:, :N], y[:, N:]
        ha = G * ((1 - s) * np.matmul(Wa, ya[..., None])[..., 0] + s * yb) + b[:, :N] + u
        hb = G * ((1 - s) * np.matmul(Wb, yb[..., None])[..., 0] + s * ya) + b[:, N:]
        return -y + np.tanh(np.concatenate([ha, hb], 1))

    for i in range(steps):
        u = push if (push is not None and i * dt < push_T) else 0.0
        k1 = f(x)
        x = x + dt / 2 * (k1 + f(x + dt * k1)) + amp * rng.normal(0, 1, x.shape)
        if i % every == 0:
            xa, xb = x[:, :N], x[:, N:]
            Wa += rate * (xa[:, :, None] * xa[:, None, :] / N - Wa)
            Wb += rate * (xb[:, :, None] * xb[:, None, :] / N - Wb)
        if record and i % 100 == 0:
            trace.append((i * dt, float(np.median(np.abs(x[:, :N] - x[:, N:]).mean(1) / 2))))
    return x, trace


def imprinted(p, seeds):
    return np.tile(p, (seeds, 1)), np.tile(np.outer(p, p) / N, (seeds, 1, 1))


def p1_job(job):
    G, tau = job
    seeds = 8
    rng = seed_of(G, tau, 1)
    xa, Wa = imprinted(walsh(1), seeds)
    xb, Wb = imprinted(walsh(16), seeds)
    x, _ = plastic_run(G, 0.0, tau, 4 * tau, seeds, rng, xa, xb, Wa, Wb)
    return dict(G=G, Q=float(np.median((x ** 2).mean(1))))


def random_W(rng, seeds, lam):
    W = np.zeros((seeds, N, N))
    for i in range(seeds):
        A = rng.normal(0, 1, (N, N))
        A = (A + A.T) / 2
        W[i] = lam * A / np.linalg.eigvalsh(A)[-1]
    return W


def overlaps_pairs(x):
    M = np.abs(x @ x.T) / N
    return M[np.triu_indices(len(x), 1)]


def p2_job(job):
    G, tau = job
    seeds = 16
    rng = seed_of(G, tau, 2)
    lam = 1.5 / G
    Wa, Wb = random_W(rng, seeds, lam), random_W(rng, seeds, lam)
    x, _ = plastic_run(G, 0.0, tau, 6 * tau, seeds, rng, rng.normal(0, .03, (seeds, N)), rng.normal(0, .03, (seeds, N)), Wa, Wb)
    xa = x[:, :N]
    Q = (xa ** 2).mean(1)
    Wsame = np.tile(Wa[0], (seeds, 1, 1))
    y, _ = plastic_run(G, 0.0, tau, 6 * tau, seeds, rng, rng.normal(0, .03, (seeds, N)), rng.normal(0, .03, (seeds, N)), Wsame, Wb)
    return dict(G=G, frac=float(np.mean(Q >= .5)), Q=float(np.median(Q)), diff=float(np.median(overlaps_pairs(xa))), same=float(np.median(overlaps_pairs(y[:, :N]))))


def p3_job(job):
    G, f_, u_p, tau = job
    seeds = 8
    rng = seed_of(G, f_, tau, 3)
    xi, zeta = walsh(1), walsh(2)
    xa, Wa = imprinted(xi, seeds)
    xb, Wb = imprinted(walsh(16), seeds)
    x, _ = plastic_run(G, 0.0, tau, 6 * tau, seeds, rng, xa, xb, Wa, Wb, push=f_ * u_p * zeta, push_T=3 * tau)
    a = x[:, :N]
    return dict(G=G, f=f_, u=f_ * u_p, new=[float(v) for v in a @ zeta / N], old=[float(v) for v in a @ xi / N])


def p4_job(job):
    G, s, tau = job
    seeds = 8
    rng = seed_of(G, s, tau, 4)
    xi, eta = walsh(1), walsh(16)
    xa, Wa = imprinted(xi, seeds)
    xb, Wb = imprinted(eta, seeds)
    x, _ = plastic_run(G, s, tau, 6 * tau, seeds, rng, xa, xb, Wa, Wb)
    a, b = x[:, :N], x[:, N:]
    return dict(G=G, s=s, D=float(np.median(np.abs(a - b).mean(1) / 2)), Q=float(np.median((x ** 2).mean(1))), a_xi=float(np.median(a @ xi / N)), a_eta=float(np.median(a @ eta / N)), ab=float(np.median((a * b).mean(1))))


def p6_job(job):
    G, s, tau = job
    seeds = 8
    rng = seed_of(G, s, tau, 6)
    xa, Wa = imprinted(walsh(1), seeds)
    xb, Wb = imprinted(walsh(16), seeds)
    _, tr = plastic_run(G, s, tau, 10 * tau, seeds, rng, xa, xb, Wa, Wb, record=True)
    d0 = tr[1][1]
    t = next((t_ for t_, d in tr if d < .5 * d0), float("inf"))
    return dict(tau=tau, t=t, d0=d0)


def p7_job(job):
    G, s, tau = job
    seeds = 16
    rng = seed_of(G, s, tau, 7)
    lam = 1.5 / G
    Wa, Wb = random_W(rng, seeds, lam), random_W(rng, seeds, lam)
    x, _ = plastic_run(G, s, tau, 6 * tau, seeds, rng, rng.normal(0, .03, (seeds, N)), rng.normal(0, .03, (seeds, N)), Wa, Wb)
    return dict(s=s, ab=float(np.median(np.abs((x[:, :N] * x[:, N:]).sum(1)) / np.maximum(np.sqrt((x[:, :N] ** 2).sum(1) * (x[:, N:] ** 2).sum(1)), 1e-9))), Q=float(np.median((x ** 2).mean(1))))


def part_plastic(outdir, pool):
    t0 = time.time()
    tau = 100.0
    r1 = pool.map(p1_job, [(G, tau) for G in (1.6, 1.9, 2.2, 2.5, 3, 4)])
    print("P1. Mean x^2 after 4 tau, imprinted, by G: " + ", ".join(f"{r['G']}: {r['Q']:.3f}" for r in r1))
    print(f"P1 {verdict(all(r['Q'] >= .5 for r in r1 if r['G'] >= 2.2) and all(r['Q'] <= .1 for r in r1 if r['G'] <= 1.9))}", flush=True)
    r2 = pool.map(p2_job, [(G, tau) for G in (3, 4)])
    for r in r2:
        print(f"  Formation G {r['G']}: settled {r['frac']:.2f}, mean x^2 {r['Q']:.3f}; different W0 median |overlap| {r['diff']:.3f}; same W0 {r['same']:.3f}")
    print(f"P2 {verdict(all(r['frac'] >= .9 and r['diff'] <= .25 and r['same'] >= .5 for r in r2))}", flush=True)
    up = {2.5: .555, 3: .965, 4: 1.81}
    uc = {G: flip_u(G) for G in up}
    fr = (.6, .7, .8, .85, .9, .95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.5)
    r3 = pool.map(p3_job, [(G, f_, up[G], tau) for G in up for f_ in fr])
    json.dump(r3, open(os.path.join(outdir, "plastic_push.json"), "w"))
    ok = True
    for G in up:
        g = sorted([r for r in r3 if r["G"] == G], key=lambda r: r["f"])
        fracs = [float(np.mean(np.array(r["new"]) >= .8)) for r in g]
        th = next((r["u"] for r, p in zip(g, fracs) if p >= .5), float("inf"))
        hit = next((r for r, p in zip(g, fracs) if p >= .5), None)
        old = float(np.median(np.abs(hit["old"]))) if hit else float("nan")
        new = float(np.median(hit["new"])) if hit else float("nan")
        print(f"  Push G {G}: threshold {th:.3f}, derived {up[G]}, fixed {uc[G]:.3f}; at threshold median on new {new:.3f}, |on old| {old:.3f}; " + ", ".join(f"{r['f']:.2f}: {p:.2f}" for r, p in zip(g, fracs)))
        ok = ok and within(th, up[G], .15) and th < uc[G] and new >= .8 and old <= .2
    print(f"P3 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    lim = {2.5: .135, 3: .195, 4: .265, 8: .37}
    own = {3: .45, 4: .43, 8: .435}
    S = [0.0] + [round(.02 * i, 3) for i in range(1, 31)]
    r4 = pool.map(p4_job, [(G, s, tau) for G in lim for s in S], chunksize=2)
    json.dump(r4, open(os.path.join(outdir, "plastic_contact.json"), "w"))
    tab = {}
    for G in lim:
        g = sorted([r for r in r4 if r["G"] == G], key=lambda r: r["s"])
        tab[G] = crossing([r["s"] for r in g], [r["D"] / g[0]["D"] for r in g])
        print(f"  Contact G {G}: merge {tab[G]:.3f}, derived {lim[G]}; " + " | ".join(f"{r['s']:.2f}: D {r['D'] / g[0]['D']:.2f} Q {r['Q']:.2f}" for r in g[::5]))
    print(f"P4 {verdict(all(within(tab[G], lim[G], .15) for G in lim) and all(tab[G] <= .75 * own[G] for G in own))}; {time.time() - t0:.0f}s", flush=True)
    r5 = pool.map(p4_job, [(G, round(1.2 * lim[G], 3), tau) for G in (4, 8)])
    ok = True
    for r, G in zip(r5, (4, 8)):
        base = [q for q in r4 if q["G"] == G and q["s"] == 0][0]["D"]
        print(f"  Past the limit, G {G}, s {r['s']}: D over start {r['D'] / base:.3f}; mean x^2 {r['Q']:.3f}; A on its parent {r['a_xi']:.3f}, A on the other parent {r['a_eta']:.3f}; A with B {r['ab']:.3f}")
        ok = ok and r["D"] / base < .1 and r["Q"] >= .7 and .35 <= r["a_xi"] <= .65 and .35 <= abs(r["a_eta"]) <= .65 and r["ab"] >= .9
    print(f"P5 {verdict(ok)}", flush=True)
    r6 = pool.map(p6_job, [(4, .33, t_) for t_ in (50.0, 100.0, 200.0)])
    print("P6. Time to merge by tau: " + ", ".join(f"{r['tau']:.0f}: {r['t']:.0f}" for r in r6))
    ratio = r6[2]["t"] / r6[0]["t"] if r6[0]["t"] > 0 else float("inf")
    print(f"P6 {verdict(2.5 <= ratio <= 6)}: ratio {ratio:.2f}", flush=True)
    S7 = [0, .01, .02, .03, .05, .07, .09, .11, .13, .15, .2, .25, .3]
    r7 = sorted(pool.map(p7_job, [(4, s, tau) for s in S7]), key=lambda r: r["s"])
    print("P7. Median overlap of A and B formed under contact, by s: " + ", ".join(f"{r['s']}: {r['ab']:.2f}" for r in r7))
    first = next((r["s"] for r in r7 if r["ab"] >= .5), float("inf"))
    print(f"P7 {verdict(.04 <= first <= .2 and first < tab[4])}: first at {first}; {time.time() - t0:.0f}s", flush=True)


# ---------- Budget law ----------
def budget_job(job):
    beta, s, seeds, T, K, *rest = job
    scale = rest[0] if rest else 1.0
    rng = seed_of(beta, s, K, 9)
    size = N // K
    asm = np.arange(N) // size
    x = np.zeros((seeds, 2 * N))
    x[:, :N][:, asm == 0] = 1.0
    x[:, N:][:, asm == 1] = 1.0
    b = rng.normal(0, .01 * scale, (seeds, 2 * N))
    dt = .02
    amp = .02 * scale * np.sqrt(dt)

    def amean(y):
        out = np.zeros_like(y)
        for k in range(K):
            out[:, asm == k] = y[:, asm == k].mean(1, keepdims=True)
        return out

    def target(h):
        h = h - h.max(1, keepdims=True)
        e = np.exp(beta * h)
        return N / K * e / e.sum(1, keepdims=True)

    def f(y):
        a_, b_ = y[:, :N], y[:, N:]
        ta = target((1 - s) * amean(a_) + s * b_ + b[:, :N])
        tb = target((1 - s) * amean(b_) + s * a_ + b[:, N:])
        return -y + np.concatenate([ta, tb], 1)

    steps = int(T / dt)
    D, cnt = 0.0, 0
    for i in range(steps):
        k1 = f(x)
        x = x + dt / 2 * (k1 + f(x + dt * k1)) + amp * rng.normal(0, 1, x.shape)
        if i >= steps * 3 // 4 and i % 10 == 0:
            D = D + np.abs(x[:, :N] - x[:, N:]).mean(1) / 2
            cnt += 1
    return dict(beta=beta, s=s, D=float(np.median(D / cnt)))


def part_budget(outdir, pool):
    t0 = time.time()
    B = (6, 8, 12, 16, 24, 32)
    pred = dict(zip(B, (.26, .31, .36, .39, .42, .435)))
    S = [0.0] + [round(.01 * i, 3) for i in range(1, 61)]
    res = pool.map(budget_job, [(b_, s, 12, 150.0, 4) for b_ in B for s in S], chunksize=4)
    json.dump(res, open(os.path.join(outdir, "budget.json"), "w"))
    tab = {}
    for b_ in B:
        g = sorted([r for r in res if r["beta"] == b_], key=lambda r: r["s"])
        tab[b_] = crossing([r["s"] for r in g], [r["D"] / g[0]["D"] for r in g])
    print("Budget law, K = 4: (beta, merge, solver) " + ", ".join(f"({b_}, {tab[b_]:.3f}, {pred[b_]})" for b_ in B) + f"; {time.time() - t0:.0f}s")
    ok = all(within(tab[b_], pred[b_], .15) for b_ in B) and all(tab[B[i]] < tab[B[i + 1]] for i in range(len(B) - 1))
    print(f"B1 {verdict(ok)}", flush=True)


def a1_q(job):
    G, tau = job
    seeds = 8
    rng = seed_of(G, tau, 11)
    xa, Wa = imprinted(walsh(1), seeds)
    xb, Wb = imprinted(walsh(16), seeds)
    x, _ = plastic_run(G, 0.0, tau, 20 * tau, seeds, rng, xa, xb, Wa, Wb)
    return float(np.median((x ** 2).mean(1)))


def a1_push(job):
    G, f_, u_p, tau = job
    seeds = 8
    rng = seed_of(G, f_, tau, 12)
    xi, zeta = walsh(1), walsh(2)
    xa, Wa = imprinted(xi, seeds)
    xb, Wb = imprinted(walsh(16), seeds)
    x, _ = plastic_run(G, 0.0, tau, 15 * tau, seeds, rng, xa, xb, Wa, Wb, push=f_ * u_p * zeta, push_T=12 * tau)
    return dict(G=G, f=f_, u=f_ * u_p, frac=float(np.mean(x[:, :N] @ zeta / N >= .8)))


def a2_job(job):
    G, gain, tau = job
    seeds = 16
    rng = seed_of(G, gain, tau, 13)
    lam = gain / G
    Wa, Wb = random_W(rng, seeds, lam), random_W(rng, seeds, lam)
    x, _ = plastic_run(G, 0.0, tau, 6 * tau, seeds, rng, rng.normal(0, .03, (seeds, N)), rng.normal(0, .03, (seeds, N)), Wa, Wb)
    xa = x[:, :N]
    ok = (xa ** 2).mean(1) >= .5
    y, _ = plastic_run(G, 0.0, tau, 6 * tau, seeds, rng, rng.normal(0, .03, (seeds, N)), rng.normal(0, .03, (seeds, N)), np.tile(Wa[0], (seeds, 1, 1)), Wb)
    ya = y[:, :N]
    oky = (ya ** 2).mean(1) >= .5
    return dict(G=G, frac=float(ok.mean()), diff=float(np.median(overlaps_pairs(xa[ok]))) if ok.sum() > 1 else float("nan"), frac_same=float(oky.mean()), same=float(np.median(overlaps_pairs(ya[oky]))) if oky.sum() > 1 else float("nan"))


def a3_job(job):
    G, s, tau = job
    seeds = 32
    rng = seed_of(G, s, tau, 14)
    xi, eta = walsh(1), walsh(16)
    xa, Wa = imprinted(xi, seeds)
    xb, Wb = imprinted(eta, seeds)
    x, _ = plastic_run(G, s, tau, 6 * tau, seeds, rng, xa, xb, Wa, Wb)
    a = x[:, :N]
    p, q = np.abs(a @ xi / N), np.abs(a @ eta / N)
    cap = (p >= .85) | (q >= .85)
    blend = (p >= .3) & (p <= .7) & (q >= .3) & (q <= .7)
    d = np.abs(x[:, :N] - x[:, N:]).mean(1) / 2
    return dict(G=G, s=s, cap=float(cap.mean()), blend=float(blend.mean()), a_wins=float((p >= .85).sum() / max(cap.sum(), 1)), merged=float(np.mean(d < .1)))


def part_after(outdir, pool):
    t0 = time.time()
    tau = 100.0
    q = pool.map(a1_q, [(1.9, tau)])[0]
    up = {3: .965, 4: 1.81}
    fr = (.8, .85, .9, .95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3)
    r = pool.map(a1_push, [(G, f_, up[G], tau) for G in up for f_ in fr])
    json.dump(r, open(os.path.join(outdir, "a1.json"), "w"))
    ok = q <= .1
    print(f"A1. G = 1.9 mean x^2 after 20 tau {q:.3f}")
    for G in up:
        g = sorted([x for x in r if x["G"] == G], key=lambda x: x["f"])
        th = next((x["u"] for x in g if x["frac"] >= .5), float("inf"))
        print(f"  12 tau push, G {G}: threshold {th:.3f}, derived {up[G]}, fixed {flip_u(G):.3f}; " + ", ".join(f"{x['f']:.2f}: {x['frac']:.2f}" for x in g))
        ok = ok and within(th, up[G], .10)
    print(f"A1 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    r = pool.map(a2_job, [(G, 3.0, tau) for G in (3, 4)])
    for x in r:
        print(f"  Seed gain 3, G {x['G']}: settled {x['frac']:.2f}; different W0 median |overlap| {x['diff']:.3f}; same W0, settled {x['frac_same']:.2f}, median |overlap| {x['same']:.3f}")
    print(f"A2 {verdict(all(x['frac'] >= .9 and x['diff'] <= .25 and x['same'] >= .5 for x in r))}; {time.time() - t0:.0f}s", flush=True)
    jobs = [(4, .30, tau), (4, .33, tau), (4, .42, tau), (4, .50, tau), (8, .385, tau), (8, .44, tau), (8, .50, tau)]
    r = pool.map(a3_job, jobs)
    json.dump(r, open(os.path.join(outdir, "a3.json"), "w"))
    ok = True
    for x in r:
        fast = (x["G"], x["s"]) in ((4, .42), (4, .50), (8, .44), (8, .50))
        print(f"  G {x['G']}, s {x['s']}: merged {x['merged']:.2f}; capture {x['cap']:.2f}; blend {x['blend']:.2f}; A wins {x['a_wins']:.2f} of captures")
        ok = ok and (x["cap"] >= .7 and .25 <= x["a_wins"] <= .75 if fast else x["blend"] >= .7)
    print(f"A3 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    B = (12, 16, 24, 32)
    pred = dict(zip(B, (.36, .39, .42, .435)))
    S = [0.0] + [round(.01 * i, 3) for i in range(1, 61)]
    res = pool.map(budget_job, [(b_, s_, 12, 150.0, 4, .1) for b_ in B for s_ in S], chunksize=4)
    tab = {}
    for b_ in B:
        g = sorted([x for x in res if x["beta"] == b_], key=lambda x: x["s"])
        tab[b_] = crossing([x["s"] for x in g], [x["D"] / g[0]["D"] for x in g])
    print("A4. Budget law, a tenth of the spread and noise: (beta, merge, solver) " + ", ".join(f"({b_}, {tab[b_]:.3f}, {pred[b_]})" for b_ in B))
    print(f"A4 {verdict(all(within(tab[b_], pred[b_], .15) for b_ in B) and all(tab[B[i]] < tab[B[i + 1]] for i in range(len(B) - 1)))}; {time.time() - t0:.0f}s", flush=True)


def part_solve():
    def m0(G):
        m = 1.0
        for _ in range(5000):
            m = tanh(G * m)
        return m

    def own(G):
        a = b = start = m0(G)
        for s in np.arange(.005, .95, .005):
            for _ in range(20000):
                m = (a + b) / 2
                a, b = tanh(G * ((1 - s) * m + s * a)), tanh(G * ((1 - s) * m - s * b))
            if b / start < .5:
                return round(float(s), 3), "fade"
            if G * s * (1 - b * b) >= 1:
                return round(float(s), 3), "pairs commit"
        return None, None

    def rank_one(G):
        m = 1.0
        for _ in range(20000):
            m = tanh(G * m ** 3)
        return m

    def plastic(G):
        a = b = start = rank_one(G)
        for s in np.arange(.005, .95, .005):
            for _ in range(40000):
                Q = (a * a + b * b) / 2
                a, b = tanh(G * ((1 - s) * Q + s) * a), tanh(G * ((1 - s) * Q - s) * b)
            if b / start < .5:
                return round(float(s), 3), round(a, 3)
        return None, None

    def push(G):
        a = b = rank_one(G)
        last = 0.0
        for u in np.arange(.005, 4, .005):
            for _ in range(40000):
                Q = (a * a + b * b) / 2
                a, b = tanh(G * Q * a + u), tanh(G * Q * b - u)
            if b <= 0:
                return round(float(last), 3)
            last = u
        return None

    print("G, s_hold, s_u, own vocabulary")
    for G in GS:
        print(G, round(s_hold(G), 3), round(1 - 1 / G, 3), own(G))
    print("plastic: G, limit, a there; fixed flip; plastic push")
    for G in (2.5, 3, 4):
        print(G, plastic(G), round(flip_u(G), 3), push(G))


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    parts = sys.argv[2:] or ["vocab", "switch", "budget", "plastic"]
    with Pool(8, maxtasksperchild=200) as pool:
        for p in parts:
            if p == "solve":
                part_solve()
            elif p == "vocab":
                part_vocab(outdir, pool)
            elif p == "switch":
                part_switch(outdir, pool)
            elif p == "plastic":
                part_plastic(outdir, pool)
            elif p == "budget":
                part_budget(outdir, pool)
            elif p == "after":
                part_after(outdir, pool)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
