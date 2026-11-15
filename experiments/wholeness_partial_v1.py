"""Partial change: does a block keep a changed part, restore it, or lose it? Predictions frozen before any site-level run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, following wholeness_growth_v1.py. The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte
Results: D1, D2, D3, D5, D6, D7, D8, D10, D11 passed; D4, D9, D12, D13 missed. D1: difference 4.4e-16. D3: all 16 limits within 3% of the solver. D5: cost ratio 1.145, while c = .5 restored in every seed. D6: first kept .68 to .74 at G = 3, 4 for k = 1, 2, 4. D8: T_step .70, .70, .75, total 4.29 times; 1 step never reached it, inverted in every seed.
Misses, which stand as frozen: D4: member limits up to 11% below the solver at G = 2, 4.5% below at G = 4. D9: blend stayed in 56% at G = 2.5. D12: at s = .4, k = 4, changed members stayed in every seed. D13: d = 6, k = 3 joined .38 against the bar of .5.
After the follow-up: E2, E3 passed; E1, E4, E5 missed. E1: quiet member limits within 3% of the solver at all 16 cells, so D4's gap is site noise, but content n = 1 differed from member by up to 6%, since member runs hold 4 flipped traits per seed where n = 1 holds one replica; I missed that when writing the clause. E2: at s = .4, k = 4 changed members returned in every seed with frozen weights and tau_w = 200, and stayed in every seed at tau_w = 20. So how fast the ties follow decides it. E3: the bar was wrong: weight to holders equals the share (.365 against .365, .279 against .286, .245 against .250), so held means joined, in 24 of 24 seeds at d = 4, 22 and 21 of 24 at d = 6. E4: blend at G = 2.25 stayed .62, needing .75; 1.00 at G = 2.5 and 0 at G = 2, so the limit is near G = 2.2. E5: 180 of 212. The sign matches at every length except the two beside the threshold: at T = .70, W_uc at release is +.007 and 97% were kept. After the fact: b takes a few time units to relax, W_uc keeps falling meanwhile, so the deciding crossing comes just after release.
Totals: 18 frozen, 11 passed, 7 missed. Limit: the blocks in D10 and D11 have no outward share (weight inside 1.000), so they test a change with nothing pulling from beyond.

Needs numpy. All data are synthetic.
Run: python -I wholeness_partial_v1.py OUTDIR [solve gauge content members push self gradual vocab seeded space]
"solve" prints the mean-field numbers used below, and was run before the predictions were written. It simulates no sites.

WHY. The doc's untested reading: a trait block fits Ashman's 2026-08-08 group, since its centre is a divisible list and one trait can change while the block persists, and a stored pattern should restore a partial change, which is closer to something that cannot be divided. Here that gets its test. Change part of what a block is, let go, and see whether the part stays changed (kept), goes back (restored), or takes the rest with it (inverted).

HAND DERIVATIONS.
(a) One stored pattern is a one-trait block. With W = xi xi^T / n and y_i = xi_i x_i, the law x' = -x + tanh(G W x) becomes y' = -y + tanh(G mean(y)), because tanh is odd. So a stored pattern restoring a few flipped sites is exactly a uniform block pulling a few deviant members back. Restoration here is consensus and nothing more.
(b) A dial between list and pattern. d traits, n members who follow their trait's mean, and an interior vote across traits: x_ik' = -x_ik + tanh(G[(1-c) mean_i(x_k) + c vote]), vote = mean_k(mean_i(x_k)), code taken as all +1 by (a). c = 0: traits independent, 2^d codes. c = 1: one stored pattern, 2 codes. With a share f of traits flipped: a = tanh(G[(1-c)a + c q]), b = tanh(G[(1-c)b - c q]), q = (1-f)a - f b. The flipped traits stay flipped only if b survives, which gives a limit c_keep(G, f).
(c) The same equation for members. Flip a share f of members in a block with own hold, x_i' = -x_i + tanh(G[(1-s)x_i + s mean(x)]). Relabel members as traits and s as c: it is (b) with the words swapped. So s_keep = c_keep, and it starts near s_hold(G) as f goes to 0 and rises with f. So "does a block keep a changed part" is "does a part hold against the rest", the theory's own law one level down. A block that restores every partial change is a block whose parts have no hold.
(d) A push costs about the same whether or not it sticks. Flipping a trait while the vote still stands needs u_push = G c q + u_c(G(1-c)). The two terms trade, so c only raises it a little: 2.147, 2.196, 2.250, 2.311, 2.458 at c = 0, .1, .2, .3, .5, G = 4, f = 2/16. Coupling decides what happens after release, not how hard the push is.
(e) A self-writing interior. W' = (x x^T / n - W) / tau. My first derivation was static: at release, the changed sites hear (1-f) W_uc a + f W_cc b, so they are restored above one gain, kept below another, and silenced in a window between. The mean-field run of "solve" refuted that before any site ran: there is no window. The sign of W_uc amplifies itself, since a small W_uc gives a small b of the same sign and W_uc then tracks a b, with gain G(1-f) above 1. So the outcome is decided when the old link W_uc crosses zero: W_uc(T) = 2 exp(-T/tau) - 1, T* = tau ln 2 = .693 tau, whatever the size of the change. Solver, first T / tau kept: G 3: .71, .70, .72 at f = 1/16, 2/16, 4/16; G 4: .70, .69, .67; G 8: .69, .67, .58, and .44 at 6/16.
(f) Too large a push tips everything. Pushing only the changing sites, the unchanged ones hear (1-f)a - f, and past a tipping share they follow the push and the whole pattern inverts, in any push length. Solver: inverted at 6/16 and 8/16 for G = 3, 4, at 8/16 for G = 8. The same should hold with W frozen, since this happens before W has time to move.
(g) Gradual against abrupt. Half the sites can't be changed in one step, by (f). In steps, each step needs about T*. Solver at G = 4, T_step / tau: never in 1 step; .70, .70, .70 in 2, 4, 8 steps. So total push grows with the number of steps, and each site pays about T* either way.
(h) A vocabulary is not one thing either. Fixed W with several stored patterns has blends as attractors: the state sign(xi1 + xi2 + xi3) has m = (1/4)tanh(3 G m) + (1/4)tanh(G m), near .5 on each. From memory (Amit, Gutfreund and Sompolinsky, 1985) this stays stable for 1/G below about .46, so G above about 2.17. So a stored vocabulary of 3 or more also keeps some partial states.
(i) A list can replace everything. Trait blocks flip one trait at a time with no vote against them, and members move together so weights do not change. So all 16 traits can be replaced with the same members and the same relations. This is the plain form of the 2026-08-08 line that identity survives total material turnover, in a toy where nothing is a centre.
(j) Changing can mean joining. With d traits and N sites, a given code is already held with probability about 1 - exp(-N / 2^d): near 1 at d = 4, .86 at d = 6, and near 0 at d = 16 with 8 seeded blocks. Landing on a held code gives q = 1 with its holders, so the weights join them. Earlier I scored H7 "change without joining" against one chosen other block, so it could not see this.
Reading to test, not a result. If (a) and (c) hold, keeping or restoring a partial change measures how much hold the parts have. It is a dial, not a kind, and a person can drop a goal and persist too. So I expect this test to weaken my reading that restoring is closer to an indivisible centre.

PREDICTIONS. Noise .02 and input spread .05 throughout. Kept: the changed part reads >= .5 in its new sign and the rest >= .5 in its old sign. Restored: the changed part reads <= -.5 and the rest >= .5. Inverted: the rest reads <= -.5. A limit is where the fraction of seeds kept falls through .5.
D1. Gauge. Same noise relabelled: a stored pattern and a uniform one-trait block agree within 1e-9, f = 1/4, G = 4.
D2. Ends of the dial. n = d = 16. c = 0: kept in at least 90% of seeds. c = 1: restored in at least 90%. G = 2, 3, 4, 8; k = 1, 2, 4, 6 of 16.
D3. Content limit. Within 10% of G 2: .175, .188, .221, .270. G 3: .260, .279, .326, .395. G 4: .311, .334, .390, .469. G 8: .402, .431, .502, .603, at k = 1, 2, 4, 6.
D4. Member limit. The same numbers within 10%, and within 5% of D3's measured limits.
D5. Push cost. G = 4, k = 2. Threshold within 10% of 2.147, 2.196, 2.250, 2.311, 2.458 at c = 0, .1, .2, .3, .5, and the last over the first at most 1.2. At 1.25 times the derived value: kept in at least 75% of seeds at c = 0, .1, .2, .3, restored in at least 90% at c = .5.
D6. Self-writing. tau = 100, u = 1.25 G. First T / tau kept within 15% of G 3: .71, .70, .72. G 4: .70, .69, .67. G 8: .69, .67, .58, and .44 at k = 6. Not silenced: the changed part reads between -.5 and .5 in at least half the seeds only within .05 tau of that threshold.
D7. Tipping. Inverted in at least 90% of seeds at every push length from .05 tau, at k = 6, 8 for G = 3, 4 and k = 8 for G = 8. With W frozen, G = 4: inverted at k = 6, restored at k = 4.
D8. Gradual. G = 4, half the sites in total. First T_step / tau reaching the target in at least half the seeds within 15% of .70 in 2, 4 and 8 steps. In 1 step no seed reaches it at any length tried. Total push at 8 steps over 2 steps between 3 and 5.
D9. Vocabulary. Fixed W, 4 stored patterns. A random f = 1/4 flip from xi1 returns, overlap >= .8, in at least 90% of seeds at G = 3, 4, 8. The blend of three stays, each of the three between .35 and .65, in at least 90% at G = 2.5, 3, 4, 8, and at G = 2 falls to one pattern, overlap >= .8, in at least 75%.
D10. Content change with free weights. 128 sites, 8 seeded blocks of 16, d = 16, G = 4, s = .2, kappa = 16. Push all members of one block on k = 1, 4, 8 traits at 1.25 u_c, in at least 90% of seeds: changed traits >= .8 in the new sign, the rest >= .8 in the old, members with each other >= .9, weight inside the block >= .9, the other blocks on their own codes >= .8.
D11. All replaced. Same cell, all 16 traits one at a time: final overlap with the old code <= -.8, members with each other >= .9, weight inside the block >= .9, in at least 90% of seeds.
D12. Members with free weights. Change k = 1, 4, 6 of a block's 16 members on half the traits, at once. Limits from the solver with no self in the mean, G = 4: .292, .365, .44 (k = 2: .313). s = .2: changed members stay changed in at least 90% of seeds at every k, with median weight to the unchanged members <= .1. s = .4: return in at least 75% at k = 1 and 4; stay in at least 75% at k = 6. Unchanged members stay on the code, >= .8, in every run.
D13. Small identity space. Grown blocks, G = 4, s = .2, kappa = 16, largest block, k traits pushed at 1.25 u_c. d = 4, k = 1: code already held in at least 90% of seeds, and joined, at least .25 of the block's weight to those holders, in at least 75%. d = 6, k = 1 and 3: held in .7 or more, joined in at least 50%. Where the code was free, joined in none. Seeded d = 16, k = 1: joined in none.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: D1, D2, D3, D5, D6, D7, D8, D10, D11 passed; D4, D9, D12, D13 missed. D4: member limits ran below content limits, up to 11% below the solver at G = 2. D9: at G = 2.5 the blend stayed in only 56% of seeds. D12: at s = .4, k = 4, changed members stayed in every seed, above the frozen-weight limit .365. D13: at d = 6, k = 3 joined read .38, with a median weight to holders of .245.
E1. D4's gap is site noise. Content averages each trait over 16 members, so its bias and noise shrink; a member has only itself. With n = 1 the content law is the member law, so its limit is within 3% of the member limit at every G and k. With spread and noise a tenth as large, member limits come within 3% of the solver.
E2. D12's miss is a race. Near the limit the return is slow, and free weights leave at tau_w = 20 before it ends. s = .4, k = 4: with frozen weights changed members return in at least 90% of seeds; with tau_w = 200, in at least 75%. s = .4, k = 6, frozen: stay in at least 75%, since .44 is above .4.
E3. D13's .25 was the wrong bar. A block of n sites joining h holders gives them a share near h / (h + n - 1), and with few holders that is under .25. Among seeds where the code was held, weight to holders reaches at least half that share in at least 75%, at d = 4, k = 1 and d = 6, k = 1 and 3.
E4. D9's miss at G = 2.5 is noise near the limit. With spread and noise a tenth as large the blend stays in at least 90% at G = 2.5 and at least 75% at G = 2.25, and falls at G = 2 in at least 75%.
E5. The mechanism of (e). G = 4, k = 2, T / tau = .6, .65, .68, .7, .72, .75, .8, 32 seeds each. Kept or restored matches the sign of W_uc at release in at least 90% of seeds that end in either: negative means kept, positive means restored.
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

DT = .05
SIGMA = .02
SPREAD = .05
TAU = 100.0
KS = (1, 2, 4, 6)


def s_hold(G):
    m = sqrt(1 - 1 / G)
    return .5 * (1 - atanh(m) / (G * m))


def flip_u(G):
    if G <= 1:
        return 0.0
    m = sqrt(1 - 1 / G)
    return abs(atanh(m) - G * m)


def seed_of(*v):
    return np.random.default_rng([abs(int(round(a * 1000))) for a in v])


def within(x, y, tol):
    return bool(np.isfinite(x) and abs(x - y) <= tol * y)


def verdict(ok):
    return "PASS" if ok else "MISS"


def walsh(i, n=64):
    return np.array([(-1.0) ** bin(i & j).count("1") for j in range(n)])


# ---------- Mean-field numbers, no sites ----------
def keep_mf(G, c, f, T=800.0, dt=.02):
    a = b = 1.0
    for _ in range(int(T / dt)):
        q = (1 - f) * a - f * b
        a, b = a + dt * (-a + tanh(G * ((1 - c) * a + c * q))), b + dt * (-b + tanh(G * ((1 - c) * b - c * q)))
    return a, b


def c_keep(G, f):
    lo, hi = 0.0, 1.0
    for _ in range(12):
        mid = (lo + hi) / 2
        a, b = keep_mf(G, mid, f)
        if a >= .5 and b >= .5:
            lo = mid
        else:
            hi = mid
    return lo


def u_push(G, c, f):
    a0 = 1.0
    for _ in range(4000):
        a0 = tanh(G * a0)
    Gp = G * (1 - c)
    ms = sqrt(1 - 1 / Gp) if Gp > 1 else 0.0
    q = (1 - f) * a0 + f * ms
    return G * c * q + flip_u(Gp)


def m_plastic(G):
    m = 1.0
    for _ in range(40000):
        m = tanh(G * m ** 3)
    return m


def self_mf(G, f, Ts, tau=TAU, dt=.2, rest=8.0):
    """Two classes in the pattern's gauge, unchanged a and changed b, with W_uu, W_uc, W_cc. Vectorised over push lengths."""
    Ts = np.asarray(Ts, float)
    m0 = m_plastic(G)
    a, b = np.full(Ts.shape, m0), np.full(Ts.shape, m0)
    uu, uc, cc = np.full(Ts.shape, m0 * m0), np.full(Ts.shape, m0 * m0), np.full(Ts.shape, m0 * m0)
    u = 1.25 * G
    tmax = Ts.max() + rest * tau
    for i in range(int(tmax / dt)):
        t = i * dt
        on = t < Ts
        ha = G * ((1 - f) * uu * a + f * uc * b)
        hb = G * ((1 - f) * uc * a + f * cc * b) - u * on
        da = -a + np.tanh(ha)
        db = -b + np.tanh(hb)
        duu, duc, dcc = (a * a - uu) / tau, (a * b - uc) / tau, (b * b - cc) / tau
        a, b = a + dt * da, b + dt * db
        uu, uc, cc = uu + dt * duu, uc + dt * duc, cc + dt * dcc
    return a, b


def self_edges(G, f):
    Ts = np.arange(.01, 3.0, .01) * TAU
    a, b = self_mf(G, f, Ts)
    kept = (b <= -.5) & (a >= .5)
    restored = (b >= .5) & (a >= .5)
    last_rest = float(Ts[restored].max() / TAU) if restored.any() else 0.0
    first_keep = float(Ts[kept].min() / TAU) if kept.any() else float("inf")
    return last_rest, first_keep


def gradual_mf(G, steps, T_step, tau=TAU, rest_tau=2.0, end_tau=6.0, dt=.25):
    """steps equal classes changed one after another, half the sites in total. True if all are kept."""
    n = steps + 1
    fr = np.r_[.5, np.full(steps, .5 / steps)]
    m0 = m_plastic(G)
    x = np.full(n, m0)
    W = np.full((n, n), m0 * m0)
    u = 1.25 * G

    def advance(T, on, x, W):
        for _ in range(int(T / dt)):
            h = G * (W @ (fr * x))
            if on is not None:
                h[on] -= u
            x2 = x + dt * (-x + np.tanh(h))
            W = W + dt * (np.outer(x, x) - W) / tau
            x = x2
        return x, W

    for k in range(steps):
        x, W = advance(T_step, k + 1, x, W)
        x, W = advance(rest_tau * tau, None, x, W)
    x, W = advance(end_tau * tau, None, x, W)
    return bool(x[0] >= .5 and (x[1:] <= -.5).all())


def gradual_edge(job):
    G, steps = job
    for Tr in np.arange(.05, 3.0, .05):
        if gradual_mf(G, steps, Tr * TAU):
            return G, steps, round(float(Tr), 2)
    return G, steps, float("inf")


def mix_m(G):
    m = .5
    for _ in range(20000):
        m = .25 * tanh(3 * G * m) + .25 * tanh(G * m)
    return m


def part_solve(pool):
    t0 = time.time()
    print("Keep limit c_keep(G, f) = s_keep(G, f); G, s_hold, then f = 1/16, 2/16, 4/16, 6/16")
    for G in (2, 3, 4, 8):
        print(f"  {G}, {s_hold(G):.3f}: " + ", ".join(f"{c_keep(G, k / 16):.3f}" for k in KS), flush=True)
    print("Push threshold at G = 4, f = 2/16, by c: " + ", ".join(f"{c}: {u_push(4, c, 2 / 16):.3f}" for c in (0, .1, .2, .3, .5)))
    print("Self-writing, u = 1.25 G, tau 100. G, f: last T/tau restored, first T/tau kept")
    for G in (3, 4, 8):
        for k in (1, 2, 4, 6, 8):
            lr, fk = self_edges(G, k / 16)
            print(f"  {G}, {k}/16: {lr:.2f}, {fk:.2f}", flush=True)
    print("Gradual: smallest T_step / tau that keeps all steps; total push = steps x T_step")
    res = pool.map(gradual_edge, [(G, st) for G in (3, 4, 8) for st in (1, 2, 4, 8)])
    for G, st, tr in res:
        print(f"  G {G}, {st} steps: T_step {tr}, total {st * tr:.2f}")
    print("Three-blend overlap by G: " + ", ".join(f"{G}: {mix_m(G):.3f}" for G in (2, 2.5, 3, 4, 8)))
    print(f"{time.time() - t0:.0f}s")


# ---------- Site-level runs ----------
def heun(f, x, rng, dt=DT, sigma=SIGMA):
    k1 = f(x)
    return x + dt / 2 * (k1 + f(x + dt * k1)) + sigma * np.sqrt(dt) * rng.normal(0, 1, x.shape)


def crossing(xs, ys, level=.5):
    if ys[0] < level:
        return 0.0
    for i in range(len(xs) - 1):
        if ys[i] >= level > ys[i + 1]:
            return float(xs[i] + (ys[i] - level) * (xs[i + 1] - xs[i]) / (ys[i] - ys[i + 1]))
    return float("inf")


def outcomes(ch, rest):
    kept = (ch >= .5) & (rest >= .5)
    restored = (ch <= -.5) & (rest >= .5)
    silent = (np.abs(ch) < .5) & (rest >= .5)
    inverted = rest <= -.5
    return dict(kept=float(kept.mean()), restored=float(restored.mean()), silent=float(silent.mean()), inverted=float(inverted.mean()), ch=float(np.median(ch)), rest=float(np.median(rest)))


def part_gauge():
    n, G = 64, 4
    xi = walsh(1)
    rng = seed_of(1)
    b = SPREAD * rng.normal(0, 1, n)
    y = np.ones(n)
    y[:16] = -1
    x = xi * y
    W = np.outer(xi, xi) / n
    fx = lambda v: -v + np.tanh(G * (W @ v) + xi * b)
    fy = lambda v: -v + np.tanh(G * v.mean() + b)
    worst = 0.0
    amp = SIGMA * np.sqrt(DT)
    for _ in range(4000):
        z = rng.normal(0, 1, n)
        k = fx(x)
        x = x + DT / 2 * (k + fx(x + DT * k)) + amp * xi * z
        k = fy(y)
        y = y + DT / 2 * (k + fy(y + DT * k)) + amp * z
        worst = max(worst, float(np.abs(x - xi * y).max()))
    print(f"D1 {verdict(worst <= 1e-9)}: largest difference {worst:.2e}; ended restored {bool(y.mean() > .9)}")


C_GRID = [round(.01 * i, 2) for i in range(71)] + [.75, .8, .85, .9, .95, 1.0]


def content_job(job):
    G, c, k = job
    S, n, d = 12, 16, 16
    rng = seed_of(G, c, k, 21)
    b = SPREAD * rng.normal(0, 1, (S, n, d))
    x = np.ones((S, n, d))
    x[:, :, :k] = -1

    def f(y):
        ybar = y.mean(1, keepdims=True)
        return -y + np.tanh(G * ((1 - c) * ybar + c * ybar.mean(2, keepdims=True)) + b)

    for _ in range(int(150 / DT)):
        x = heun(f, x, rng)
    r = outcomes(-x[:, :, :k].mean((1, 2)), x[:, :, k:].mean((1, 2)))
    r.update(G=G, c=c, k=k)
    return r


def members_job(job):
    G, s, k = job
    S, n, d = 12, 16, 8
    rng = seed_of(G, s, k, 22)
    b = SPREAD * rng.normal(0, 1, (S, n, d))
    x = np.ones((S, n, d))
    x[:, :k, :d // 2] = -1

    def f(y):
        return -y + np.tanh(G * ((1 - s) * y + s * y.mean(1, keepdims=True)) + b)

    for _ in range(int(150 / DT)):
        x = heun(f, x, rng)
    r = outcomes(-x[:, :k, :d // 2].mean((1, 2)), x[:, k:, :d // 2].mean((1, 2)))
    r.update(G=G, c=s, k=k)
    return r


D3 = {2: (.175, .188, .221, .270), 3: (.260, .279, .326, .395), 4: (.311, .334, .390, .469), 8: (.402, .431, .502, .603)}


def limits(res):
    tab = {}
    for G in D3:
        for k in KS:
            g = sorted([r for r in res if r["G"] == G and r["k"] == k], key=lambda r: r["c"])
            tab[(G, k)] = crossing([r["c"] for r in g], [r["kept"] for r in g])
    return tab


def part_content(outdir, pool):
    t0 = time.time()
    res = pool.map(content_job, [(G, c, k) for G in D3 for k in KS for c in C_GRID], chunksize=8)
    json.dump(res, open(os.path.join(outdir, "content.json"), "w"))
    tab = limits(res)
    ok_ends = all(r["kept"] >= .9 for r in res if r["c"] == 0) and all(r["restored"] >= .9 for r in res if r["c"] == 1.0)
    print(f"D2 {verdict(ok_ends)}: c = 0 kept {min(r['kept'] for r in res if r['c'] == 0):.2f} or more; c = 1 restored {min(r['restored'] for r in res if r['c'] == 1.0):.2f} or more")
    ok = True
    for G in D3:
        print(f"  Content limit G {G}: " + ", ".join(f"{tab[(G, k)]:.3f} ({p})" for k, p in zip(KS, D3[G])))
        ok = ok and all(within(tab[(G, k)], p, .10) for k, p in zip(KS, D3[G]))
    print(f"D3 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)


def part_members(outdir, pool):
    t0 = time.time()
    res = pool.map(members_job, [(G, c, k) for G in D3 for k in KS for c in C_GRID], chunksize=8)
    json.dump(res, open(os.path.join(outdir, "members.json"), "w"))
    tm = limits(res)
    tab = limits(json.load(open(os.path.join(outdir, "content.json"))))
    ok = True
    for G in D3:
        print(f"  Member limit G {G}: " + ", ".join(f"{tm[(G, k)]:.3f} ({p}; content {tab[(G, k)]:.3f})" for k, p in zip(KS, D3[G])))
        ok = ok and all(within(tm[(G, k)], p, .10) and within(tm[(G, k)], tab[(G, k)], .05) for k, p in zip(KS, D3[G]))
    print(f"D4 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)


def push_job(job):
    G, c, k, fac = job
    S, n, d = 12, 16, 16
    rng = seed_of(G, c, k, fac, 23)
    b = SPREAD * rng.normal(0, 1, (S, n, d))
    x = np.ones((S, n, d))
    u0 = fac * u_push(G, c, k / d)
    u = np.zeros((S, n, d))
    u[:, :, :k] = -u0

    def field(y, v):
        ybar = y.mean(1, keepdims=True)
        return -y + np.tanh(G * ((1 - c) * ybar + c * ybar.mean(2, keepdims=True)) + b + v)

    for _ in range(int(60 / DT)):
        x = heun(lambda y: field(y, u), x, rng)
    end = -x[:, :, :k].mean((1, 2))
    for _ in range(int(100 / DT)):
        x = heun(lambda y: field(y, 0.0), x, rng)
    r = outcomes(-x[:, :, :k].mean((1, 2)), x[:, :, k:].mean((1, 2)))
    r.update(c=c, fac=fac, u=u0, moved=float((end >= .5).mean()))
    return r


def part_push(outdir, pool):
    t0 = time.time()
    C = (0, .1, .2, .3, .5)
    F = (.8, .85, .9, .95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25)
    res = pool.map(push_job, [(4, c, 2, fac) for c in C for fac in F])
    json.dump(res, open(os.path.join(outdir, "push.json"), "w"))
    th, ok = {}, True
    for c in C:
        g = sorted([r for r in res if r["c"] == c], key=lambda r: r["fac"])
        th[c] = next((r["u"] for r in g if r["moved"] >= .5), float("inf"))
        top = g[-1]
        print(f"  c {c}: threshold {th[c]:.3f}, derived {u_push(4, c, 2 / 16):.3f}; at 1.25 kept {top['kept']:.2f}, restored {top['restored']:.2f}, inverted {top['inverted']:.2f}; moved by factor " + ", ".join(f"{r['fac']}: {r['moved']:.2f}" for r in g))
        ok = ok and within(th[c], u_push(4, c, 2 / 16), .10)
        ok = ok and (top["restored"] >= .9 if c == .5 else top["kept"] >= .75)
    ok = ok and th[.5] / th[0] <= 1.2
    print(f"D5 {verdict(ok)}: cost ratio {th[.5] / th[0]:.3f}; {time.time() - t0:.0f}s", flush=True)


def plastic(G, x, W, rng, b, T, u=None, frozen=False, tau=TAU, dt=.1, every=5):
    n = x.shape[1]
    amp = SIGMA * np.sqrt(dt)
    rate = every * dt / tau
    extra = 0.0 if u is None else u

    def f(y):
        return -y + np.tanh(G * np.matmul(W, y[..., None])[..., 0] + b + extra)

    for i in range(int(T / dt)):
        k1 = f(x)
        x = x + dt / 2 * (k1 + f(x + dt * k1)) + amp * rng.normal(0, 1, x.shape)
        if not frozen and i % every == 0:
            W = W + rate * (x[:, :, None] * x[:, None, :] / n - W)
    return x, W


def self_job(job):
    G, k, Tr, frozen = job
    S, n = 8, 64
    rng = seed_of(G, k, Tr, frozen, 24)
    p = walsh(1)
    b = SPREAD * rng.normal(0, 1, (S, n))
    x = np.tile(p, (S, 1))
    W = np.tile(np.outer(p, p) / n, (S, 1, 1))
    x, W = plastic(G, x, W, rng, b, TAU, frozen=frozen)
    mask = np.zeros((S, n), bool)
    for i in range(S):
        mask[i, rng.permutation(n)[:k * n // 16]] = True
    u = -1.25 * G * p * mask
    x, W = plastic(G, x, W, rng, b, Tr * TAU, u=u, frozen=frozen)
    x, W = plastic(G, x, W, rng, b, 8 * TAU, frozen=frozen)
    y = x * p
    ch = np.array([-y[i, mask[i]].mean() for i in range(S)])
    rest = np.array([y[i, ~mask[i]].mean() for i in range(S)])
    r = outcomes(ch, rest)
    r.update(G=G, k=k, T=Tr, frozen=frozen)
    return r


T_GRID = (.05, .2, .4, .5, .55, .6, .62, .64, .66, .68, .7, .72, .74, .76, .8, .85, .9, 1.0, 1.25, 1.5, 2.0)
D6 = {(3, 1): .71, (3, 2): .70, (3, 4): .72, (4, 1): .70, (4, 2): .69, (4, 4): .67, (8, 1): .69, (8, 2): .67, (8, 4): .58, (8, 6): .44}


def part_self(outdir, pool):
    t0 = time.time()
    jobs = [(G, k, Tr, False) for G in (3, 4, 8) for k in (1, 2, 4, 6, 8) for Tr in T_GRID]
    jobs += [(4, k, Tr, True) for k in (4, 6) for Tr in (.05, .2, .7, 2.0)]
    res = pool.map(self_job, jobs, chunksize=2)
    json.dump(res, open(os.path.join(outdir, "self.json"), "w"))
    ok, ok_silent = True, True
    for (G, k), p in D6.items():
        g = sorted([r for r in res if r["G"] == G and r["k"] == k and not r["frozen"]], key=lambda r: r["T"])
        th = next((r["T"] for r in g if r["kept"] >= .5), float("inf"))
        sil = [r["T"] for r in g if r["silent"] >= .5]
        print(f"  G {G}, k {k}: first kept {th}, derived {p}; silent at {sil}; " + " ".join(f"{r['T']}:{'K' if r['kept'] >= .5 else 'R' if r['restored'] >= .5 else 'I' if r['inverted'] >= .5 else 'S' if r['silent'] >= .5 else '?'}" for r in g))
        ok = ok and within(th, p, .15)
        ok_silent = ok_silent and all(abs(t - th) <= .05 for t in sil)
    print(f"D6 {verdict(ok and ok_silent)}: thresholds {ok}; silent only near them {ok_silent}; {time.time() - t0:.0f}s", flush=True)
    ok = True
    for G, k in ((3, 6), (3, 8), (4, 6), (4, 8), (8, 8)):
        g = [r for r in res if r["G"] == G and r["k"] == k and not r["frozen"]]
        print(f"  Tipping G {G}, k {k}: inverted, lowest over lengths {min(r['inverted'] for r in g):.2f}")
        ok = ok and min(r["inverted"] for r in g) >= .9
    g6 = [r for r in res if r["frozen"] and r["k"] == 6]
    g4 = [r for r in res if r["frozen"] and r["k"] == 4]
    print(f"  Frozen W, G 4: k 6 inverted, lowest {min(r['inverted'] for r in g6):.2f}; k 4 restored, lowest {min(r['restored'] for r in g4):.2f}")
    ok = ok and min(r["inverted"] for r in g6) >= .9 and min(r["restored"] for r in g4) >= .9
    print(f"D7 {verdict(ok)}", flush=True)


def gradual_job(job):
    G, steps, Tr = job
    S, n = 8, 64
    rng = seed_of(G, steps, Tr, 25)
    p = walsh(1)
    b = SPREAD * rng.normal(0, 1, (S, n))
    x = np.tile(p, (S, 1))
    W = np.tile(np.outer(p, p) / n, (S, 1, 1))
    x, W = plastic(G, x, W, rng, b, TAU)
    sets = [rng.permutation(n)[:n // 2] for _ in range(S)]
    size = n // 2 // steps
    for st in range(steps):
        mask = np.zeros((S, n), bool)
        for i in range(S):
            mask[i, sets[i][st * size:(st + 1) * size]] = True
        x, W = plastic(G, x, W, rng, b, Tr * TAU, u=-1.25 * G * p * mask)
        x, W = plastic(G, x, W, rng, b, 2 * TAU)
    x, W = plastic(G, x, W, rng, b, 6 * TAU)
    y = x * p
    ok = np.zeros(S, bool)
    inv = np.zeros(S, bool)
    for i in range(S):
        ch = -y[i, sets[i]]
        rest_idx = np.setdiff1d(np.arange(n), sets[i])
        by = [ch[st * size:(st + 1) * size].mean() for st in range(steps)]
        ok[i] = min(by) >= .5 and y[i, rest_idx].mean() >= .5
        inv[i] = y[i, rest_idx].mean() <= -.5
    return dict(G=G, steps=steps, T=Tr, reached=float(ok.mean()), inverted=float(inv.mean()))


def part_gradual(outdir, pool):
    t0 = time.time()
    Ts = (.05, .2, .5, .6, .65, .7, .75, .8, .9, 1.0, 1.2, 1.5, 2.0)
    res = pool.map(gradual_job, [(4, st, Tr) for st in (1, 2, 4, 8) for Tr in Ts])
    json.dump(res, open(os.path.join(outdir, "gradual.json"), "w"))
    th, ok = {}, True
    for st in (1, 2, 4, 8):
        g = sorted([r for r in res if r["steps"] == st], key=lambda r: r["T"])
        th[st] = next((r["T"] for r in g if r["reached"] >= .5), float("inf"))
        print(f"  {st} steps: first reached at T_step {th[st]}; total {st * th[st]:.2f}; " + " ".join(f"{r['T']}:{r['reached']:.2f}" for r in g) + f"; inverted at most {max(r['inverted'] for r in g):.2f}")
        if st == 1:
            ok = ok and max(r["reached"] for r in g) == 0
        else:
            ok = ok and within(th[st], .70, .15)
    ratio = 8 * th[8] / (2 * th[2]) if np.isfinite(th[2]) and np.isfinite(th[8]) else float("nan")
    ok = ok and 3 <= ratio <= 5
    print(f"D8 {verdict(ok)}: total push, 8 steps over 2, {ratio:.2f}; {time.time() - t0:.0f}s", flush=True)


def vocab_job(job):
    G, mode = job
    S, n = 32, 64
    rng = seed_of(G, len(mode), 26)
    P = np.array([walsh(r) for r in (1, 2, 4, 8)])
    W = P.T @ P / n
    b = SPREAD * rng.normal(0, 1, (S, n))
    if mode == "flip":
        x = np.tile(P[0], (S, 1))
        for i in range(S):
            x[i, rng.permutation(n)[:n // 4]] *= -1
    else:
        x = np.tile(np.sign(P[0] + P[1] + P[2]), (S, 1))

    def f(y):
        return -y + np.tanh(G * y @ W + b)

    for _ in range(int(200 / DT)):
        x = heun(f, x, rng)
    ov = x @ P.T / n
    return dict(G=G, mode=mode, ov=ov.tolist())


def part_vocab(outdir, pool):
    res = pool.map(vocab_job, [(G, m) for G in (2, 2.5, 3, 4, 8) for m in ("flip", "blend")])
    json.dump(res, open(os.path.join(outdir, "vocab.json"), "w"))
    ok = True
    for r in res:
        ov = np.array(r["ov"])
        if r["mode"] == "flip":
            back = float(np.mean(ov[:, 0] >= .8))
            print(f"  G {r['G']}, one quarter flipped: returned {back:.2f}; median on xi1 {np.median(ov[:, 0]):.3f}")
            if r["G"] in (3, 4, 8):
                ok = ok and back >= .9
        else:
            stay = float(np.mean(((ov[:, :3] >= .35) & (ov[:, :3] <= .65)).all(1)))
            one = float(np.mean((np.abs(ov) >= .8).any(1)))
            print(f"  G {r['G']}, blend of three: stayed {stay:.2f}; fell to one pattern {one:.2f}; median overlaps {np.round(np.median(ov, 0), 3).tolist()}")
            if r["G"] == 2:
                ok = ok and one >= .75
            else:
                ok = ok and stay >= .9
    print(f"D9 {verdict(ok)}", flush=True)


# ---------- Blocks with free weights ----------
NS = 128
EVERY = 10
TAU_W = 20.0


def kernel(x, kappa, scale):
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


def evolve(x, pi, G, s, kappa, T, rng, b, u=None, scale=None, dt=.1):
    amp = SIGMA * np.sqrt(dt)
    if scale is None:
        scale = np.ones(len(x))
    extra = 0.0 if u is None else u

    def f(y):
        return -y + np.tanh(G * ((1 - s) * y + s * (pi @ y)) + b + extra)

    for i in range(int(T / dt)):
        k1 = f(x)
        x = x + dt / 2 * (k1 + f(x + dt * k1)) + amp * rng.normal(0, 1, x.shape)
        if i % EVERY == 0:
            target, scale = kernel(x, kappa, scale)
            pi = pi + min(1.0, EVERY * dt / TAU_W) * (target - pi)
    return x, pi, scale


def seeded(s, seed, kappa=16, d=16, B=8, G=4):
    rng = seed_of(G, s, kappa, seed, 31)
    codes = rng.choice([-1.0, 1.0], (B, d))
    lab = np.repeat(np.arange(B), NS // B)
    x = codes[lab].copy()
    b = SPREAD * rng.normal(0, 1, (NS, d))
    pi, scale = kernel(x, kappa, np.ones(NS))
    x, pi, scale = evolve(x, pi, G, s, kappa, 100.0, rng, b, scale=scale)
    return x, pi, b, rng, scale, codes, lab


def block_read(x, pi, A, code, codes, lab):
    d = x.shape[1]
    qq = x[A] @ x[A].T / d
    iu = np.triu_indices(len(A), 1)
    others = [float(np.mean(x[lab == j] @ codes[j] / d)) for j in range(1, len(codes))]
    return dict(together=float(np.median(qq[iu])), inside=float(pi[np.ix_(A, A)].sum(1).mean()), others=min(others), on_old=float(np.mean(x[A] @ code / d)))


def content_seed_job(job):
    seed, k = job
    G, s, kappa = 4, .2, 16
    x, pi, b, rng, scale, codes, lab = seeded(s, seed)
    A = np.nonzero(lab == 0)[0]
    code = codes[0]
    tr = rng.permutation(16)[:k]
    u = np.zeros_like(x)
    u[np.ix_(A, tr)] = -1.25 * flip_u(G) * code[tr]
    x, pi, scale = evolve(x, pi, G, s, kappa, 60.0, rng, b, u=u, scale=scale)
    x, pi, scale = evolve(x, pi, G, s, kappa, 140.0, rng, b, scale=scale)
    r = block_read(x, pi, A, code, codes, lab)
    rest = np.setdiff1d(np.arange(16), tr)
    r.update(seed=seed, k=k, ch=float(-(x[np.ix_(A, tr)] * code[tr]).mean()), rest=float((x[np.ix_(A, rest)] * code[rest]).mean()))
    return r


def all_seed_job(seed):
    G, s, kappa = 4, .2, 16
    x, pi, b, rng, scale, codes, lab = seeded(s, seed)
    A = np.nonzero(lab == 0)[0]
    code = codes[0]
    for t in rng.permutation(16):
        u = np.zeros_like(x)
        u[A, t] = -1.25 * flip_u(G) * code[t]
        x, pi, scale = evolve(x, pi, G, s, kappa, 60.0, rng, b, u=u, scale=scale)
        x, pi, scale = evolve(x, pi, G, s, kappa, 40.0, rng, b, scale=scale)
    r = block_read(x, pi, A, code, codes, lab)
    r.update(seed=seed)
    return r


def member_seed_job(job):
    s, k, seed = job
    G, kappa = 4, 16
    x, pi, b, rng, scale, codes, lab = seeded(s, seed)
    A = np.nonzero(lab == 0)[0]
    code = codes[0]
    ch_m, rest_m = A[:k], A[k:]
    tr = rng.permutation(16)[:8]
    x[np.ix_(ch_m, tr)] *= -1
    x, pi, scale = evolve(x, pi, G, s, kappa, 200.0, rng, b, scale=scale)
    return dict(s=s, k=k, seed=seed, ch=float(-(x[np.ix_(ch_m, tr)] * code[tr]).mean()), rest=float((x[rest_m] @ code / 16).mean()), to_rest=float(pi[np.ix_(ch_m, rest_m)].sum(1).mean()))


def part_seeded(outdir, pool):
    t0 = time.time()
    r1 = pool.map(content_seed_job, [(seed, k) for k in (1, 4, 8) for seed in range(16)])
    json.dump(r1, open(os.path.join(outdir, "seed_content.json"), "w"))
    ok = True
    for k in (1, 4, 8):
        g = [r for r in r1 if r["k"] == k]
        good = [r["ch"] >= .8 and r["rest"] >= .8 and r["together"] >= .9 and r["inside"] >= .9 and r["others"] >= .8 for r in g]
        print(f"  k {k}: all conditions {np.mean(good):.2f}; changed {np.median([r['ch'] for r in g]):.3f}; rest {np.median([r['rest'] for r in g]):.3f}; together {np.median([r['together'] for r in g]):.3f}; inside {np.median([r['inside'] for r in g]):.3f}; others {np.median([r['others'] for r in g]):.3f}")
        ok = ok and np.mean(good) >= .9
    print(f"D10 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    r2 = pool.map(all_seed_job, range(16))
    json.dump(r2, open(os.path.join(outdir, "seed_all.json"), "w"))
    good = [r["on_old"] <= -.8 and r["together"] >= .9 and r["inside"] >= .9 for r in r2]
    print(f"D11 {verdict(np.mean(good) >= .9)}: all conditions {np.mean(good):.2f}; overlap with the old code {np.median([r['on_old'] for r in r2]):.3f}; together {np.median([r['together'] for r in r2]):.3f}; inside {np.median([r['inside'] for r in r2]):.3f}; others {np.median([r['others'] for r in r2]):.3f}; {time.time() - t0:.0f}s", flush=True)
    r3 = pool.map(member_seed_job, [(s, k, seed) for s in (.2, .4) for k in (1, 4, 6) for seed in range(16)])
    json.dump(r3, open(os.path.join(outdir, "seed_members.json"), "w"))
    ok = True
    for s in (.2, .4):
        for k in (1, 4, 6):
            g = [r for r in r3 if r["s"] == s and r["k"] == k]
            stay = float(np.mean([r["ch"] >= .5 for r in g]))
            back = float(np.mean([r["ch"] <= -.5 for r in g]))
            rest = min(r["rest"] for r in g)
            to = float(np.median([r["to_rest"] for r in g]))
            print(f"  s {s}, k {k}: stayed {stay:.2f}; returned {back:.2f}; unchanged members on the code, lowest {rest:.3f}; weight to them {to:.3f}")
            ok = ok and rest >= .8
            if s == .2:
                ok = ok and stay >= .9 and to <= .1
            elif k == 6:
                ok = ok and stay >= .75
            else:
                ok = ok and back >= .75
    print(f"D12 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)


def groups(x):
    d = x.shape[1]
    adj = x @ x.T / d >= .8
    seen = np.zeros(len(x), bool)
    out = []
    for i in range(len(x)):
        if seen[i]:
            continue
        stack, comp = [i], []
        seen[i] = True
        while stack:
            a = stack.pop()
            comp.append(a)
            for j in np.nonzero(adj[a] & ~seen)[0]:
                seen[j] = True
                stack.append(int(j))
        out.append(comp)
    return [g for g in out if len(g) >= 2]


def space_job(job):
    d, k, seed = job
    G, s, kappa = 4, .2, 16
    rng = seed_of(G, d, s, kappa, seed, 32)
    x = rng.choice([-1.0, 1.0], (NS, d))
    b = SPREAD * rng.normal(0, 1, (NS, d))
    pi = (np.ones((NS, NS)) - np.eye(NS)) / (NS - 1)
    x, pi, scale = evolve(x, pi, G, s, kappa, 400.0, rng, b)
    bl = [g for g in groups(x) if len(g) >= 3]
    if not bl:
        return dict(d=d, k=k, seed=seed, ok=False)
    A = np.array(max(bl, key=len))
    code = np.sign(x[A].mean(0))
    tr = rng.permutation(d)[:k]
    new = code.copy()
    new[tr] *= -1
    out_mask = np.ones(NS, bool)
    out_mask[A] = False
    held = int((x[out_mask] @ new / d >= .9).sum())
    u = np.zeros_like(x)
    u[np.ix_(A, tr)] = 1.25 * flip_u(G) * new[tr]
    x, pi, scale = evolve(x, pi, G, s, kappa, 60.0, rng, b, u=u, scale=scale)
    x, pi, scale = evolve(x, pi, G, s, kappa, 140.0, rng, b, scale=scale)
    holders = np.nonzero(out_mask & (x @ new / d >= .9))[0]
    weight = float(pi[np.ix_(A, holders)].sum(1).mean()) if len(holders) else 0.0
    return dict(d=d, k=k, seed=seed, ok=True, size=len(A), held=held > 0, weight=weight, joined=weight >= .25, on_new=float(np.mean(x[A] @ new / d)))


def seeded_join_job(seed):
    G, s, kappa = 4, .2, 16
    x, pi, b, rng, scale, codes, lab = seeded(s, seed)
    A = np.nonzero(lab == 0)[0]
    code = codes[0]
    t = rng.integers(16)
    u = np.zeros_like(x)
    u[A, t] = -1.25 * flip_u(G) * code[t]
    x, pi, scale = evolve(x, pi, G, s, kappa, 60.0, rng, b, u=u, scale=scale)
    x, pi, scale = evolve(x, pi, G, s, kappa, 140.0, rng, b, scale=scale)
    new = code.copy()
    new[t] *= -1
    holders = np.nonzero((lab != 0) & (x @ new / 16 >= .9))[0]
    return dict(seed=seed, weight=float(pi[np.ix_(A, holders)].sum(1).mean()) if len(holders) else 0.0)


def part_space(outdir, pool):
    t0 = time.time()
    cells = ((4, 1), (6, 1), (6, 3))
    res = pool.map(space_job, [(d, k, seed) for d, k in cells for seed in range(24)])
    json.dump(res, open(os.path.join(outdir, "space.json"), "w"))
    ok = True
    for d, k in cells:
        g = [r for r in res if r["d"] == d and r["k"] == k and r["ok"]]
        held = float(np.mean([r["held"] for r in g]))
        joined = float(np.mean([r["joined"] for r in g]))
        free = [r for r in g if not r["held"]]
        jf = float(np.mean([r["joined"] for r in free])) if free else 0.0
        w = float(np.median([r["weight"] for r in g if r["held"]])) if any(r["held"] for r in g) else 0.0
        print(f"  d {d}, k {k}: {len(g)} seeds, median size {np.median([r['size'] for r in g]):.0f}; code held {held:.2f}; joined {joined:.2f}; joined where free {jf:.2f} of {len(free)}; weight to holders where held {w:.3f}; on new code {np.median([r['on_new'] for r in g]):.3f}")
        if d == 4:
            ok = ok and held >= .9 and joined >= .75
        else:
            ok = ok and held >= .7 and joined >= .5
        ok = ok and jf == 0
    r2 = pool.map(seeded_join_job, range(16))
    worst = max(r["weight"] for r in r2)
    print(f"  Seeded d 16, k 1: largest weight to holders {worst:.4f}")
    ok = ok and worst < .25
    print(f"D13 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)


# ---------- Added after the results above ----------
def e1_job(job):
    kind, G, c, k, scale = job
    S = 12
    rng = seed_of(G, c, k, scale, len(kind), 41)
    if kind == "content1":
        n, d = 1, 16
        x = np.ones((S, n, d))
        x[:, :, :k] = -1
        idx_ch, idx_rest = (slice(None), slice(None), slice(None, k)), (slice(None), slice(None), slice(k, None))
    else:
        n, d = 16, 8
        x = np.ones((S, n, d))
        x[:, :k, :d // 2] = -1
        idx_ch, idx_rest = (slice(None), slice(None, k), slice(None, d // 2)), (slice(None), slice(k, None), slice(None, d // 2))
    b = scale * SPREAD * rng.normal(0, 1, (S, n, d))

    def f_content(y):
        ybar = y.mean(1, keepdims=True)
        return -y + np.tanh(G * ((1 - c) * ybar + c * ybar.mean(2, keepdims=True)) + b)

    def f_member(y):
        return -y + np.tanh(G * ((1 - c) * y + c * y.mean(1, keepdims=True)) + b)

    f = f_content if kind == "content1" else f_member
    for _ in range(int(150 / DT)):
        x = heun(f, x, rng, sigma=scale * SIGMA)
    r = outcomes(-x[idx_ch].mean((1, 2)), x[idx_rest].mean((1, 2)))
    r.update(kind=kind, G=G, c=c, k=k, scale=scale)
    return r


def evolve_tw(x, pi, G, s, kappa, T, rng, b, tau_w, scale=None, dt=.1):
    """tau_w None freezes the weights."""
    amp = SIGMA * np.sqrt(dt)
    if scale is None:
        scale = np.ones(len(x))

    def f(y):
        return -y + np.tanh(G * ((1 - s) * y + s * (pi @ y)) + b)

    for i in range(int(T / dt)):
        k1 = f(x)
        x = x + dt / 2 * (k1 + f(x + dt * k1)) + amp * rng.normal(0, 1, x.shape)
        if tau_w is not None and i % EVERY == 0:
            target, scale = kernel(x, kappa, scale)
            pi = pi + min(1.0, EVERY * dt / tau_w) * (target - pi)
    return x, pi


def e2_job(job):
    k, tau_w, seed = job
    G, s, kappa = 4, .4, 16
    x, pi, b, rng, scale, codes, lab = seeded(s, seed)
    A = np.nonzero(lab == 0)[0]
    code = codes[0]
    ch_m = A[:k]
    tr = rng.permutation(16)[:8]
    x[np.ix_(ch_m, tr)] *= -1
    x, pi = evolve_tw(x, pi, G, s, kappa, 200.0, rng, b, tau_w, scale=scale)
    return dict(k=k, tau_w=tau_w, seed=seed, ch=float(-(x[np.ix_(ch_m, tr)] * code[tr]).mean()))


def e3_job(job):
    d, k, seed = job
    G, s, kappa = 4, .2, 16
    rng = seed_of(G, d, s, kappa, seed, 32)
    x = rng.choice([-1.0, 1.0], (NS, d))
    b = SPREAD * rng.normal(0, 1, (NS, d))
    pi = (np.ones((NS, NS)) - np.eye(NS)) / (NS - 1)
    x, pi, scale = evolve(x, pi, G, s, kappa, 400.0, rng, b)
    bl = [g for g in groups(x) if len(g) >= 3]
    if not bl:
        return dict(d=d, k=k, seed=seed, ok=False)
    A = np.array(max(bl, key=len))
    code = np.sign(x[A].mean(0))
    tr = rng.permutation(d)[:k]
    new = code.copy()
    new[tr] *= -1
    out_mask = np.ones(NS, bool)
    out_mask[A] = False
    u = np.zeros_like(x)
    u[np.ix_(A, tr)] = 1.25 * flip_u(G) * new[tr]
    x, pi, scale = evolve(x, pi, G, s, kappa, 60.0, rng, b, u=u, scale=scale)
    x, pi, scale = evolve(x, pi, G, s, kappa, 140.0, rng, b, scale=scale)
    holders = np.nonzero(out_mask & (x @ new / d >= .9))[0]
    h, n = len(holders), len(A)
    weight = float(pi[np.ix_(A, holders)].sum(1).mean()) if h else 0.0
    return dict(d=d, k=k, seed=seed, ok=True, n=n, h=h, weight=weight, share=h / (h + n - 1) if h else 0.0)


def e4_job(job):
    G, scale = job
    S, n = 32, 64
    rng = seed_of(G, scale, 44)
    P = np.array([walsh(r) for r in (1, 2, 4, 8)])
    W = P.T @ P / n
    b = scale * SPREAD * rng.normal(0, 1, (S, n))
    x = np.tile(np.sign(P[0] + P[1] + P[2]), (S, 1))

    def f(y):
        return -y + np.tanh(G * y @ W + b)

    for _ in range(int(200 / DT)):
        x = heun(f, x, rng, sigma=scale * SIGMA)
    ov = x @ P.T / n
    return dict(G=G, stay=float(((ov[:, :3] >= .35) & (ov[:, :3] <= .65)).all(1).mean()), one=float((np.abs(ov) >= .8).any(1).mean()))


def e5_job(job):
    G, k, Tr = job
    S, n = 32, 64
    rng = seed_of(G, k, Tr, 45)
    p = walsh(1)
    b = SPREAD * rng.normal(0, 1, (S, n))
    x = np.tile(p, (S, 1))
    W = np.tile(np.outer(p, p) / n, (S, 1, 1))
    x, W = plastic(G, x, W, rng, b, TAU)
    mask = np.zeros((S, n), bool)
    for i in range(S):
        mask[i, rng.permutation(n)[:k * n // 16]] = True
    x, W = plastic(G, x, W, rng, b, Tr * TAU, u=-1.25 * G * p * mask)
    gauge = W * n * p[None, :, None] * p[None, None, :]
    uc = np.array([gauge[i][np.ix_(mask[i], ~mask[i])].mean() for i in range(S)])
    x, W = plastic(G, x, W, rng, b, 8 * TAU)
    y = x * p
    ch = np.array([-y[i, mask[i]].mean() for i in range(S)])
    rest = np.array([y[i, ~mask[i]].mean() for i in range(S)])
    return dict(T=Tr, uc=uc.tolist(), ch=ch.tolist(), rest=rest.tolist())


def part_after(outdir, pool):
    t0 = time.time()
    jobs = [("content1", G, c, k, 1.0) for G in D3 for k in KS for c in C_GRID]
    jobs += [("member", G, c, k, .1) for G in D3 for k in KS for c in C_GRID]
    res = pool.map(e1_job, jobs, chunksize=8)
    json.dump(res, open(os.path.join(outdir, "e1.json"), "w"))
    members = limits(json.load(open(os.path.join(outdir, "members.json"))))
    c1 = limits([r for r in res if r["kind"] == "content1"])
    quiet = limits([r for r in res if r["kind"] == "member"])
    ok = True
    for G in D3:
        print(f"  G {G}: " + ", ".join(f"content n=1 {c1[(G, k)]:.3f}, member {members[(G, k)]:.3f}, quiet member {quiet[(G, k)]:.3f}, solver {p}" for k, p in zip(KS, D3[G])))
        ok = ok and all(within(c1[(G, k)], members[(G, k)], .03) and within(quiet[(G, k)], p, .03) for k, p in zip(KS, D3[G]))
    print(f"E1 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    r2 = pool.map(e2_job, [(k, tw, seed) for k, tw in ((4, None), (4, 200.0), (4, 20.0), (6, None)) for seed in range(16)])
    json.dump(r2, open(os.path.join(outdir, "e2.json"), "w"))
    tab = {}
    for k, tw in ((4, None), (4, 200.0), (4, 20.0), (6, None)):
        g = [r for r in r2 if r["k"] == k and r["tau_w"] == tw]
        tab[(k, tw)] = (float(np.mean([r["ch"] <= -.5 for r in g])), float(np.mean([r["ch"] >= .5 for r in g])))
        print(f"  s .4, k {k}, tau_w {tw}: returned {tab[(k, tw)][0]:.2f}; stayed {tab[(k, tw)][1]:.2f}")
    print(f"E2 {verdict(tab[(4, None)][0] >= .9 and tab[(4, 200.0)][0] >= .75 and tab[(6, None)][1] >= .75)}; {time.time() - t0:.0f}s", flush=True)
    cells = ((4, 1), (6, 1), (6, 3))
    r3 = pool.map(e3_job, [(d, k, seed) for d, k in cells for seed in range(24)])
    json.dump(r3, open(os.path.join(outdir, "e3.json"), "w"))
    ok = True
    for d, k in cells:
        g = [r for r in r3 if r["d"] == d and r["k"] == k and r["ok"] and r["h"] > 0]
        frac = float(np.mean([r["weight"] >= .5 * r["share"] for r in g]))
        print(f"  d {d}, k {k}: {len(g)} held seeds; median holders {np.median([r['h'] for r in g]):.0f}, block {np.median([r['n'] for r in g]):.0f}; weight {np.median([r['weight'] for r in g]):.3f}, share {np.median([r['share'] for r in g]):.3f}; reached half the share {frac:.2f}")
        ok = ok and frac >= .75
    print(f"E3 {verdict(ok)}; {time.time() - t0:.0f}s", flush=True)
    r4 = pool.map(e4_job, [(G, .1) for G in (2, 2.25, 2.5)])
    for r in r4:
        print(f"  Quiet blend, G {r['G']}: stayed {r['stay']:.2f}; fell to one {r['one']:.2f}")
    by = {r["G"]: r for r in r4}
    print(f"E4 {verdict(by[2.5]['stay'] >= .9 and by[2.25]['stay'] >= .75 and by[2]['one'] >= .75)}", flush=True)
    r5 = pool.map(e5_job, [(4, 2, Tr) for Tr in (.6, .65, .68, .7, .72, .75, .8)])
    json.dump(r5, open(os.path.join(outdir, "e5.json"), "w"))
    hit, tot = 0, 0
    for r in r5:
        uc, ch, rest = (np.array(r[k_]) for k_ in ("uc", "ch", "rest"))
        decided = (rest >= .5) & (np.abs(ch) >= .5)
        match = ((uc < 0) == (ch >= .5)) & decided
        hit += int(match.sum())
        tot += int(decided.sum())
        print(f"  T {r['T']}: W_uc at release, median {np.median(uc):+.3f}; kept {np.mean(ch >= .5):.2f}; restored {np.mean(ch <= -.5):.2f}; sign matches {match.sum()} of {decided.sum()}")
    print(f"E5 {verdict(tot > 0 and hit / tot >= .9)}: {hit} of {tot}; {time.time() - t0:.0f}s", flush=True)


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    parts = sys.argv[2:]
    with Pool(8, maxtasksperchild=200) as pool:
        for p in parts:
            if p == "solve":
                part_solve(pool)
            elif p == "gauge":
                part_gauge()
            elif p == "content":
                part_content(outdir, pool)
            elif p == "members":
                part_members(outdir, pool)
            elif p == "push":
                part_push(outdir, pool)
            elif p == "self":
                part_self(outdir, pool)
            elif p == "gradual":
                part_gradual(outdir, pool)
            elif p == "vocab":
                part_vocab(outdir, pool)
            elif p == "seeded":
                part_seeded(outdir, pool)
            elif p == "space":
                part_space(outdir, pool)
            elif p == "after":
                part_after(outdir, pool)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
