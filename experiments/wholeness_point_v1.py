"""Point of convergence: what does a centre do that a list cannot? Predictions frozen before any site-level run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after Ashman answered the open decision in the doc: "an indivisible centre, a soul... what it does? it's a point of convergence... is a list a point of convergence? no it is not." The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte

Results: Z2 to Z10 passed; Z1 missed on one clause. Z1: difference 0; threshold 1.377 against 1.303 at eps = 10, G = 3, 5.7% with a 5% bar; first kept at T = 7.40 and 28.00 against 7.93 and 28.73. Z3: all 48 cells as derived in every seed. Z7: within 4%. Z8: at G = 4 flip threshold 2.142, 1.433, .671, .284, .114, .044. Z10: 27 and 23 blocks with count 0, 28 of 28 with count 1 at beta = 2, read 47.55 times the mean, 26 with count 0 under Sinkhorn.
After the follow-up: E1 to E4 passed. E1: 1.307 and 2.148 in a run of 600, so Z1's miss was run length. E2: centre held alone in 22 of 22 blocks without emptying; with emptying in 0 of 21, own share .009, count 1 in every block. E3: limits within .02. E4: .25, .30, .38.
Totals: 14 frozen, 13 passed, 1 missed. Most of these are close to algebra, and Z10 and E2 grow only under laws I chose. No real system was measured, and a node is assumed indivisible.

Needs numpy. All data are synthetic.
Run: python -I wholeness_point_v1.py OUTDIR [solve same partial clamp divide remove alone share budget drop grow e1 e2 e3 e4]
"solve" prints the mean-field numbers used below, and was run before the predictions were written. It simulates no sites.

WHY. Ashman's answer closes a gap I left. Canon already has the terms: "The point cannot be divided, because it has no extension to divide" (framework section 4.8a); "a barycentre, which is a geometric point and not an aperture" (plans/shared_wholeness_and_groups_2026_08_08.md, Finding 3); "an attractor region is not an aperture" (same, Finding 1); "its only variable is how open it is" (CLAUDE.md). So here a centre is a place flows really pass through, and the question is what that does which a list's mean does not.

HAND DERIVATIONS.
(a) A mean acts as a point until something is cut. A list: x_i' = -x_i + tanh(G mean(x)). A point: h' = (-h + mean(x)) / eps, x_i' = -x_i + tanh(G h). The steady states agree at every eps, and at eps -> 0 the two are one map. So my earlier laws already held a centre's shadow, the mean, which is the barycentre. No intact test of them could see the difference, partial change included. Saying "the centre is not in these models" was half right: the barycentre was in them, the aperture was not.
(b) A list's mean divides, a point does not. Every subset of a list has a mean and is a list. A subset of parts without the point has no ties at all. So cutting gives as many wholes as pieces for a list, and at most one for a point. CAUTION: that the point itself cannot be split is assumed here, a node is removed whole. It is not derived.
(c) Clamping one node. A node clamped opposite is a share s read against: x = tanh(G[(1-s)x - s]). That holds only for s < s_flip(G). For k occupants of a centre s = 1/k; for a list of n, s = 1/(n-1); for one part of a point, s = 1/n. So count the nodes that both follow the whole and can move it. A long list: none. A point: one. Occupants: k, but only while k < k_min(G) = 7, 5, 4, 3 at G = 2, 3, 4, 8; above that, none. So "several" has to be few, and a large centre region is a list again. A small list has every member in that position.
(d) A centre with an interior. h' = (-h + (1-a) mean(x) + a tanh(G h)) / eps. It holds alone only for a > 1/G. It stops following the parts at a_star(G) = .841, .757, .708, .623. So: a < 1/G, a point, no life apart from its whole; between, a chair, follows and also stands alone; above, a leader, moves the whole and does not follow. Clamps alone cannot tell a point from a chair. Only cutting the centre away can.
(e) Losing the point. Parts read a share c through it and 1 - c directly. Lose it and the gain is G(1 - c), so a list remains only for c < c_star = 1 - 1/G. A group can outlive a centre it mostly did not read through.
(f) Influence, with no cutting. Shift what others read from node j by u. Near consensus, with A = G sech^2, the mean moves by A u / (n(1 - A)) for a part and A s c u / (k (1 - A)) for one of k centres, with own share 1 - s. So a centre's share of influence is s c / (k (1 + s c)), whatever G and n, and a list member's is 1 / n. This reads a centre even where parts hold too well for a clamp to move them. From memory, this is DeGroot's 1974 social power, the left eigenvector.
(g) What makes one point one. Without something shared, one node with d channels is d nodes under one label. So I add A0 as an assumption: one energy through the point, and since energy goes as amplitude squared, ||h||_2 <= 1. Then x = tanh(G / sqrt(d)), and the gain a trait reads, G / ||x||, falls toward 1 as d grows, under L1 too. So the more a point carries, the dimmer each thing and the less it takes to change any one. A list holds every trait at full strength. Solver flip u, L2: G 2: .533, .393, .134, .047, .016, .006; G 4: 2.147, 1.435, .668, .285, .113, .043 at d = 1, 2, 4, 8, 16, 32. This is the one intact difference, and it rests wholly on the assumed budget.
(h) Dropping a goal, the level I mixed up. A person's goal is content through the point; a group's goal is what occupies its centre. So partial change moved content, and my objection "a person can drop a goal too" compared two different levels. Drop one of d through one budget: it goes, and the others brighten, tanh(G / sqrt(d)) to tanh(G / sqrt(d - 1)). Drop one occupant of d: it goes, the rest do not move. Remove the point: all go at once. Remove one occupant: one goes. No single removal ends a group.
(i) What growth could grow. The growth law's Sinkhorn step forces equal in-strength, so it could not grow a centre. Reading alike sites only gives no asymmetry. Let i read j as exp(kappa q_ij) in_j^beta: the uniform state moves as (beta - 1) / tau, so stable below beta = 1, and above it a power map leaves one winner. So a centre should grow only if ties seek reach, a law I am choosing.
(j) Cost, a theorem, not run. Every pair within two steps with the fewest ties: a connected graph needs n - 1, and the only tree of diameter 2 or less is the star. From memory, Jackson and Wolinsky 1996 have stars as efficient at middle tie costs, complete graphs when cheap, empty when dear.
What may fail. Z1, Z4, Z5, Z6, Z9 follow nearly by construction, so they show the mathematics can express the distinction and nothing more. Z2, Z3, Z7, Z8, Z10 can miss. None of this shows that any real thing has such a point.

PREDICTIONS. Noise .02 and input spread .05 unless stated, n = 64 parts unless stated.
Z1. Same law while intact. Same noise, eps -> 0: difference <= 1e-9 through a push. Long-push flip threshold at eps = 1, 10 within 5% of u_c, G = 3, 4. G = 4, u = 1.25 G: first push length kept within 20% of eps ln 2 + 1, eps = 10, 40.
Z2. Partial change cannot see the point. Vote through a point, eps -> 0 and eps = 1. Limits within 5% of the solver: G 3: .260, .326; G 4: .311, .390 at k = 1, 4.
Z3. Count of nodes that follow and can move, clamp length 120, at least 75% of 8 seeds. G 3: list 2, 3, 5, 6, 64: 2, 3, 5, 0, 0. Point 3, 4, 5, 64: 4, 5, 1, 1. Occupants 2, 3, 4, 5, 8: 2, 3, 4, 0, 0. G 4: lists 2, 3, 0, 0, 0; points 4, 1, 1, 1; occupants 2, 3, 0, 0, 0. G 8: lists 2, 3, 0, 0, 0; points 1, 1, 1, 1; occupants 2, 0, 0, 0, 0. Chair, a midway from 1/G to a_star: 1. Leader, a midway from a_star to 1: 0.
Z4. Pieces holding, G = 3. Reading who remain: list into 2: 2; into 8: 8; point into 2: 1; into 8: 1; 2 occupants on one side each: 2; on the same side: 1. Ties kept unscaled: list into 2: 2; into 4: 0; point into 2: 1; into 4: 0.
Z5. Losing the point. Last c holding within .03 of .50, .67, .75, .875 at G = 2, 3, 4, 8. c = 1, G = 3: reading under .1. One of 2 or 3 occupants removed: at least .8. One part removed: change at most .02.
Z6. Thresholds. Holds alone from a within .03 of 1/G. Stops following from a within .03 of a_star.
Z7. Influence. G = 2, 3, 4. Centre share within 5% of: point s = 1: .500; s = .4: .286; s = .2: .167; 2 occupants s = .4: .143 each; c = .5, s = .4: .167. List: 1/64. G = 4, s = .2: with the point clamped opposite the parts still read >= .5.
Z8. Budget. G = 2, 4, L2 and L1, d = 1 to 32: amplitude within 3% of the solver, wherever the gain read is at least 1.05, since noise may carry weaker cells; without a budget within 3% of rest(G) at every d. Flip threshold under L2 within 10% of the numbers in (g), or within .03.
Z9. Drop. n = 32, d = 8, G = 4. One budget: others .888 to .905 within 3%, dropped under .1; point removed: every trait under .1. One occupant per goal: others move at most .01, dropped under .1.
Z10. Growth. 128 sites, d = 3, G = 4, s = .4, kappa = 16, tau = 20, 12 seeds, blocks of 8 or more, frozen ties, count as in Z3, at least 75% of blocks. Alike only, row budget: 0. beta = .5: 0. beta = 2: 1. beta = 2 with Sinkhorn: 0.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: Z2 to Z10 passed; Z1 missed on one clause: flip threshold 1.377 against 1.303 at eps = 10, G = 3, which is 5.7% with a 5% bar. Nearly everything passing means these tests mostly check my algebra, so these follow-ups go after what is weakest.
E1. Z1's miss is the length of the run. Near the threshold the flip is slow and the point lags, and that run lasted 120. With a run of 600, eps = 10, G = 3, 4: within 3% of u_c.
E2. What grew in Z10 is a chair, not a point. All sites there keep own share .6 and G .6 = 2.4 > 1, so the grown centre holds alone. I did not see that when I froze Z10. Add a law of my own, emptying: a site read by more than its share gives up its own hold, own_i = .6 / (1 + max(0, in_i - 1)). Then beta = 2: without emptying the centre holds alone in at least 90% of blocks; with emptying in at most 25%, and the count stays 1 in at least 75%. This shows what a law would have to do, and nothing shows that such a law holds.
E3. Openness, the aperture's one variable in canon. The point passes beta_o mean(x). The whole ends only below (1/G - 1 + c) / c. c = 1: .50, .333, .25, .125 at G = 2, 3, 4, 8. c = .9: .444, .259, .167, .028. All within .03. c = .5, G = 4: holds with the aperture shut, since the peers carry it.
E4. A healthy whole may not be movable by its point. Clamp the point opposite, parts read a share c through it and the rest from each other: the parts turn only for c at or above s_flip(G) = .243, .292, .377 at G = 3, 4, 8, within .03. So the count in Z3 is a reading of the absorption corner, and only the share in Z7 still reads the centre below that.
"""
import json
import os
import sys
import time
from math import atanh, exp, log, sqrt, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

DT = .05
SIGMA = .02
SPREAD = .05
GS = (2.0, 3.0, 4.0, 8.0)
FAST = 1e-9


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
    return bool(np.isfinite(x) and abs(x - y) <= tol * abs(y))


def verdict(ok):
    return "PASS" if ok else "MISS"


def rest(G):
    m = 1.0
    for _ in range(20000):
        m = tanh(G * m)
    return m


# ---------- Mean-field numbers, no sites ----------
def holds_against(G, s):
    """Does a block hold while a share s of what it reads is clamped opposite? x = tanh(G[(1-s)x - s])."""
    Gp = G * (1 - s)
    return Gp > 1 and G * s < flip_u(Gp)


def s_flip(G):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if holds_against(G, mid):
            lo = mid
        else:
            hi = mid
    return lo


def k_min(G):
    k = 1
    while not holds_against(G, 1 / k):
        k += 1
    return k


def expected_both(G, kind, n, k=0):
    """Nodes that both follow the whole and can move it, a = 0."""
    km = k_min(G)
    if kind == "list":
        return n if (n - 1) < km else 0
    return (k if k < km else 0) + (n if n < km else 0)


def a_star(G):
    """Largest own hold a at which a centre still follows when every part is clamped opposite: h = -(1-a) + a tanh(G h)."""
    def stays(a):
        h = 1.0
        for _ in range(8000):
            h += .05 * (-h - (1 - a) + a * tanh(G * h))
        return h > 0
    lo, hi = 0.0, 1.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if stays(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def norm_of(x1, x2, d, p):
    if p == 2:
        return max(1.0, sqrt(x1 * x1 + (d - 1) * x2 * x2))
    return max(1.0, abs(x1) + (d - 1) * abs(x2))


def budget_rest(G, d, p=2):
    x = 1.0
    for _ in range(20000):
        z = norm_of(x, x, d, p)
        x += .05 * (-x + tanh(G * x / z))
    return x


def budget_flip(G, d, p=2, T=300.0):
    """Push one trait of d through one budget: smallest u that turns it."""
    def turns(u):
        x1 = x2 = budget_rest(G, d, p)
        for _ in range(int(T / .05)):
            z = norm_of(x1, x2, d, p)
            x1, x2 = x1 + .05 * (-x1 + tanh(G * x1 / z - u)), x2 + .05 * (-x2 + tanh(G * x2 / z))
        return x1 < 0
    lo, hi = 0.0, 8.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if turns(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


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


def solve():
    print("s_hold, s_flip, k_min, a_star, 1/G, c_star")
    for G in GS:
        print(f"  G {G:g}: s_hold {s_hold(G):.3f}; s_flip {s_flip(G):.3f}; k_min {k_min(G)}; a_star {a_star(G):.3f}; 1/G {1/G:.3f}; c_star {1-1/G:.3f}; u_c {flip_u(G):.3f}")
    print("Nodes that follow and can move")
    for G in (3.0, 4.0, 8.0):
        row = [f"list {n}: {expected_both(G,'list',n)}" for n in (2, 3, 5, 6, 64)]
        row += [f"point {n}: {expected_both(G,'c',n,1)}" for n in (3, 4, 5, 64)]
        row += [f"{k} occupants: {expected_both(G,'c',64,k)}" for k in (2, 3, 4, 5, 8)]
        print(f"  G {G:g}: " + "; ".join(row))
    print("Share of influence, largest node: list 1/n; centre s c / (k (1 + s c))")
    print("Budget, L2 then L1: amplitude, formula, flip u, gain read by a trait")
    for G in (2.0, 4.0):
        for p in (2, 1):
            cells = []
            for d in (1, 2, 4, 8, 16, 32):
                x = budget_rest(G, d, p)
                z = norm_of(x, x, d, p)
                form = tanh(G / sqrt(d)) if p == 2 else tanh(G / d)
                cells.append(f"d {d}: {x:.3f} ({form:.3f}), u {budget_flip(G,d,p):.3f}, gain {G/z:.2f}")
            print(f"  G {G:g}, L{p}: " + "; ".join(cells))
    print("Partial change, solver limits")
    for G in (3.0, 4.0):
        print(f"  G {G:g}: k 1 {c_keep(G,1/16):.3f}; k 4 {c_keep(G,4/16):.3f}")


# ---------- The law ----------
def run(W, y0, G, T, relay=None, a=0.0, eps=FAST, pin=None, pinv=-1.0, shift=None, sigma=SIGMA, rng=None):
    """y' = -y + tanh(G W y) for members. A relay has no state of its own at a = 0: y' = (-y + (1-a) W y + a tanh(G y)) / eps. Relays update first and carry no noise. y is (batch, N)."""
    y = y0.copy()
    WT = W.T
    f = 1 - exp(-DT / eps)
    has_rel = relay is not None and relay.any()
    for _ in range(int(T / DT)):
        if pin is not None:
            y[pin] = pinv
        if has_rel:
            rd = (y if shift is None else y + shift) @ WT
            tg = (1 - a) * rd + a * np.tanh(G * y)
            y[:, relay] += f * (tg[:, relay] - y[:, relay])
            if pin is not None:
                y[pin] = pinv
        rd = (y if shift is None else y + shift) @ WT
        dy = DT * (-y + np.tanh(G * rd))
        if sigma:
            dy += sqrt(DT) * sigma * rng.standard_normal(y.shape)
        if has_rel:
            dy[:, relay] = 0
        y += dy
    if pin is not None:
        y[pin] = pinv
    return y


def w_list(n, s=1.0):
    W = s * (1 - np.eye(n)) / (n - 1) + (1 - s) * np.eye(n)
    return W, np.zeros(n, bool)


def w_centres(n, k=1, s=1.0, c=1.0):
    N = n + k
    W = np.zeros((N, N))
    for i in range(n):
        W[i, i] = 1 - s
        if c < 1:
            W[i, :n] += s * (1 - c) / (n - 1)
            W[i, i] -= s * (1 - c) / (n - 1)
        W[i, n:] = s * c / k
    W[n:, :n] = 1 / n
    rel = np.zeros(N, bool)
    rel[n:] = True
    return W, rel


def start(N, B, m, rng, spread=SPREAD):
    return m + spread * rng.standard_normal((B, N))


def fingerprint(W, rel, a, G, n, rng, T=120.0):
    """For each node class: Out, clamping it opposite turns the rest of the parts; In, clamping all others opposite turns it."""
    N = W.shape[0]
    m = rest(G)
    parts = np.arange(n)
    centres = np.arange(n, N)
    sample = rng.choice(n, size=min(n, 6), replace=False)
    nodes = np.r_[sample, centres].astype(int)
    B = len(nodes)
    eps = FAST if a == 0 else 1.0
    pin = np.zeros((B, N), bool)
    pin[np.arange(B), nodes] = True
    y = run(W, start(N, B, m, rng), G, T, rel, a, eps, pin, rng=rng)
    out = []
    for b, j in enumerate(nodes):
        keep = parts[parts != j]
        out.append(y[b, keep].mean() <= -.5)
    pin2 = ~pin
    y2 = run(W, start(N, B, m, rng), G, T, rel, a, eps, pin2, rng=rng)
    inn = y2[np.arange(B), nodes] <= -.5
    out = np.array(out)
    both = out & inn
    np_s = len(sample)
    count = int(both[np_s:].sum()) + int(round(n * both[:np_s].mean()))
    return count, bool(out[np_s:].all()) if N > n else None, bool(inn[np_s:].all()) if N > n else None, float(out[:np_s].mean()), float(inn[:np_s].mean())


def job_same(_o):
    """Z1."""
    # Identity with the same noise.
    n, G = 64, 3.0
    rng1, rng2 = seed_of(1, 1), seed_of(1, 1)
    m = rest(G)
    x1 = m + SPREAD * rng1.standard_normal(n)
    x2 = x1.copy()
    rng2.standard_normal(n)
    h = x2.mean()
    worst = 0.0
    u = np.zeros(n)
    u[:40] = 1.25 * G
    for t in range(4000):
        on = u if 1000 <= t < 1400 else 0
        h = x2.mean()
        z1, z2 = rng1.standard_normal(n), rng2.standard_normal(n)
        x1 = x1 + DT * (-x1 + np.tanh(G * x1.mean() - on)) + sqrt(DT) * SIGMA * z1
        x2 = x2 + DT * (-x2 + np.tanh(G * h - on)) + sqrt(DT) * SIGMA * z2
        worst = max(worst, float(np.abs(x1 - x2).max()))
    print(f"  Mean against point, same noise: largest difference {worst:.2e}")
    ok_a = worst <= 1e-9
    # Long-push threshold at any speed of the point.
    res = []
    ok_b = True
    for G in (3.0, 4.0):
        for eps in (1.0, 10.0):
            lo, hi = 0.0, 2 * G
            for _ in range(9):
                mid = (lo + hi) / 2
                rng = seed_of(2, G, eps, mid)
                W, rel = w_centres(64)
                push = np.zeros((4, 65))
                y = start(65, 4, rest(G), rng)
                f = 1 - exp(-DT / eps)
                for _t in range(int(max(120, 8 * eps) / DT)):
                    y[:, 64] += f * (y[:, :64].mean(1) - y[:, 64])
                    y[:, :64] += DT * (-y[:, :64] + np.tanh(G * y[:, 64:65] - mid)) + sqrt(DT) * SIGMA * rng.standard_normal((4, 64))
                if np.median(y[:, 64]) <= -.5:
                    hi = mid
                else:
                    lo = mid
            th = (lo + hi) / 2
            res.append((G, eps, th))
            ok_b &= within(th, flip_u(G), .05)
            print(f"  G {G:g}, speed {eps:g}: threshold {th:.3f}, u_c {flip_u(G):.3f}")
    # Time for a push to stick.
    ok_c = True
    for eps in (10.0, 40.0):
        G = 4.0
        first = float("inf")
        for T in np.arange(.2, 1.6, .02) * eps:
            rng = seed_of(3, eps, T)
            y = start(65, 8, rest(G), rng)
            f = 1 - exp(-DT / eps)
            for t in range(int((T + 6 * eps + 40) / DT)):
                u = 1.25 * G if t * DT < T else 0
                y[:, 64] += f * (y[:, :64].mean(1) - y[:, 64])
                y[:, :64] += DT * (-y[:, :64] + np.tanh(G * y[:, 64:65] - u)) + sqrt(DT) * SIGMA * rng.standard_normal((8, 64))
            if np.mean(y[:, 64] <= -.5) >= .5:
                first = float(T)
                break
        pred = eps * log(2) + 1
        ok_c &= within(first, pred, .2)
        print(f"  Speed {eps:g}: first kept at T = {first:.2f}, derived {pred:.2f}")
    return ok_a and ok_b and ok_c


def partial_limit(G, k, eps, seeds=8):
    n, d = 16, 16
    c0 = c_keep(G, k / 16)
    cs = np.arange(c0 - .08, c0 + .08, .01)
    B = len(cs) * seeds
    cc = np.repeat(cs, seeds)[:, None]
    rng = seed_of(4, G, k, eps)
    sg = np.ones(d)
    sg[:k] = -1
    m = rest(G)
    x = m * sg[None, None, :] + SPREAD * rng.standard_normal((B, n, d))
    v = x.mean((1, 2))
    f = 1 - exp(-DT / eps)
    for _ in range(int(150 / DT)):
        mk = x.mean(1)
        v = v + f * (mk.mean(1) - v)
        fld = G * ((1 - cc) * mk + cc * v[:, None])
        x = x + DT * (-x + np.tanh(fld[:, None, :])) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
    mk = x.mean(1)
    kept = (mk[:, :k].max(1) <= -.5) & (mk[:, k:].min(1) >= .5)
    fr = kept.reshape(len(cs), seeds).mean(1)
    idx = np.where(fr < .5)[0]
    return float(cs[idx[0]]) if len(idx) else float(cs[-1]), c0


def job_partial(_o):
    """Z2."""
    ok = True
    for G in (3.0, 4.0):
        for k in (1, 4):
            for eps in (FAST, 1.0):
                lim, c0 = partial_limit(G, k, eps)
                ok &= within(lim, c0, .05)
                print(f"  G {G:g}, k {k}, speed {eps:g}: limit {lim:.3f}, solver {c0:.3f}")
    return ok


def job_clamp(_o):
    """Z3, and Z6's table entries."""
    n_seeds = 8
    ok = True
    table = []
    for G in (3.0, 4.0, 8.0):
        rows = []
        for n in (2, 3, 5, 6, 64):
            rows.append((f"list {n}", *w_list(n), 0.0, n, expected_both(G, "list", n)))
        for n in (3, 4, 5, 64):
            rows.append((f"point {n}", *w_centres(n), 0.0, n, expected_both(G, "c", n, 1)))
        for k in (2, 3, 4, 5, 8):
            rows.append((f"{k} occupants", *w_centres(64, k), 0.0, 64, expected_both(G, "c", 64, k)))
        ast = a_star(G)
        chair = (1 / G + ast) / 2
        leader = (ast + 1) / 2
        rows.append((f"chair a {chair:.2f}", *w_centres(64), chair, 64, 1))
        rows.append((f"leader a {leader:.2f}", *w_centres(64), leader, 64, 0))
        for lab, W, rel, a, n, want in rows:
            hits = []
            cnts = []
            for s in range(n_seeds):
                rng = seed_of(5, G, s, len(lab), n, a)
                c = fingerprint(W, rel, a, G, n, rng)
                cnts.append(c[0])
                hits.append(c[0] == want)
            fr = float(np.mean(hits))
            ok &= fr >= .75
            table.append((G, lab, want, int(np.median(cnts)), fr))
            print(f"  G {G:g}, {lab}: predicted {want}; median {int(np.median(cnts))}; seeds matching {fr:.2f}")
    return ok, table


def piece_run(W, rel, G, assign, renorm, rng, T=80.0, B=4):
    N = W.shape[0]
    Wc = W * (assign[:, None] == assign[None, :])
    if renorm:
        rs = W.sum(1)
        cs = Wc.sum(1)
        Wc = Wc * np.where(cs > 0, rs / np.maximum(cs, 1e-12), 0)[:, None]
    return run(Wc, start(N, B, rest(G), rng), G, T, rel, rng=rng)


def count_pieces(y, n, assign):
    res = []
    for b in range(y.shape[0]):
        c = 0
        for p in np.unique(assign[:n]):
            if abs(y[b, :n][assign[:n] == p].mean()) >= .5:
                c += 1
        res.append(c)
    return int(np.median(res))


def job_divide(_o):
    """Z4."""
    ok = True
    n = 64
    G = 3.0
    rng = seed_of(6, 1)
    def asg(pieces, centres=()):
        a = np.repeat(np.arange(pieces), n // pieces)
        return np.r_[a, np.array(centres, int)]
    cells = [
        ("list, 2, reads who remain", *w_list(n), asg(2), True, 2),
        ("list, 8, reads who remain", *w_list(n), asg(8), True, 8),
        ("list, 2, ties kept", *w_list(n), asg(2), False, 2),
        ("list, 4, ties kept", *w_list(n), asg(4), False, 0),
        ("point, 2, reads who remain", *w_centres(n), asg(2, (0,)), True, 1),
        ("point, 8, reads who remain", *w_centres(n), asg(8, (0,)), True, 1),
        ("point, 2, ties kept", *w_centres(n), asg(2, (0,)), False, 1),
        ("point, 4, ties kept", *w_centres(n), asg(4, (0,)), False, 0),
        ("2 occupants, one side each", *w_centres(n, 2), asg(2, (0, 1)), True, 2),
        ("2 occupants, same side", *w_centres(n, 2), asg(2, (0, 0)), True, 1),
    ]
    for lab, W, rel, a, ren, want in cells:
        y = piece_run(W, rel, G, a, ren, rng)
        got = count_pieces(y, n, a)
        ok &= got == want
        print(f"  {lab}: predicted {want}; pieces holding {got}")
    return ok


def job_remove(_o):
    """Z5."""
    ok = True
    n = 64
    for G in GS:
        cs = np.arange(0, 1.0001, .02)
        B = len(cs)
        rng = seed_of(7, G)
        x = start(n, B, rest(G), rng)
        cc = cs[:, None]
        for _ in range(int(1000 / DT)):
            r = (x.sum(1, keepdims=True) - x) / (n - 1)
            x = x + DT * (-x + np.tanh(G * (1 - cc) * r)) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
        held = np.abs(x.mean(1)) >= .1
        lim = float(cs[held].max()) if held.any() else 0.0
        ok &= abs(lim - (1 - 1 / G)) <= .03
        print(f"  G {G:g}: last share through the point that survives its loss {lim:.2f}; derived {1-1/G:.2f}")
    # Ends at c = 1; occupants survive; one part is nothing.
    G = 3.0
    rng = seed_of(7, 99)
    W, rel = w_centres(n)
    W2 = W.copy()
    W2[:, n] = 0
    y = run(W2, start(n + 1, 4, rest(G), rng), G, 60, rel, rng=rng)
    end = float(np.abs(y[:, :n].mean(1)).max())
    ok &= end < .1
    print(f"  Point removed, c = 1: largest reading {end:.3f}")
    for k in (2, 3):
        Wk, relk = w_centres(n, k - 1)
        y = run(Wk, start(n + k - 1, 4, rest(G), rng), G, 60, relk, rng=rng)
        v = float(np.abs(y[:, :n].mean(1)).min())
        ok &= v >= .8
        print(f"  One of {k} occupants removed: lowest reading {v:.3f}")
    Wp, relp = w_centres(n - 1)
    y = run(Wp, start(n, 4, rest(G), rng), G, 60, relp, rng=rng)
    v = abs(float(np.abs(y[:, :n - 1].mean(1)).min()) - rest(G))
    ok &= v <= .02
    print(f"  One part removed: change {v:.4f}")
    return ok


def job_alone(_o):
    """Z6."""
    ok = True
    for G in GS:
        As = np.arange(0, 1.0001, .01)
        # Alone: no parts at all.
        h = np.ones_like(As)
        for _ in range(int(4000 / DT)):
            h = h + DT * (-h + As * np.tanh(G * h))
        lim1 = float(As[h >= .05].min()) if (h >= .05).any() else 1.0
        # Parts all clamped opposite.
        h = np.ones_like(As) * rest(G)
        for _ in range(int(4000 / DT)):
            h = h + DT * (-h - (1 - As) + As * np.tanh(G * h))
        lim2 = float(As[h > 0].min()) if (h > 0).any() else 1.0
        ast = a_star(G)
        ok &= abs(lim1 - 1 / G) <= .03 and abs(lim2 - ast) <= .03
        print(f"  G {G:g}: holds alone from a = {lim1:.2f} (1/G {1/G:.2f}); stops following from a = {lim2:.2f} (a_star {ast:.2f})")
    return ok


def job_share(_o):
    """Z7: read-level nudge, no noise. Also Z7's clamp clause."""
    ok = True
    n = 64
    u = .02
    def shares(W, rel, G):
        N = W.shape[0]
        m = rest(G)
        y0 = np.full((1, N), m)
        base = run(W, y0, G, 200, rel, sigma=0.0)
        centres = np.arange(n, N)
        nodes = np.r_[0, centres].astype(int)
        B = len(nodes)
        sh = np.zeros((B, N))
        sh[np.arange(B), nodes] = u
        y = run(W, np.repeat(base, B, 0), G, 200, rel, shift=sh, sigma=0.0)
        d = (y[:, :n] - base[:, :n]).mean(1)
        tot = n * d[0] + d[1:].sum()
        return d / tot
    for G in (2.0, 3.0, 4.0):
        for lab, build, want in [
            ("list s 1", lambda: w_list(n, 1.0), None),
            ("list s .4", lambda: w_list(n, .4), None),
            ("point s 1", lambda: w_centres(n, 1, 1.0, 1.0), 1 / 2),
            ("point s .4", lambda: w_centres(n, 1, .4, 1.0), .4 / 1.4),
            ("point s .2", lambda: w_centres(n, 1, .2, 1.0), .2 / 1.2),
            ("2 occupants s .4", lambda: w_centres(n, 2, .4, 1.0), .4 / 1.4 / 2),
            ("point c .5 s .4", lambda: w_centres(n, 1, .4, .5), .2 / 1.2),
        ]:
            W, rel = build()
            s = shares(W, rel, G)
            if want is None:
                top = float(s.max())
                good = within(top, 1 / n, .05)
                print(f"  G {G:g}, {lab}: part share {top:.4f}, 1/n {1/n:.4f}")
            else:
                top = float(s[1:].max())
                good = within(top, want, .05)
                print(f"  G {G:g}, {lab}: centre share {top:.3f}, derived {want:.3f}; one part {float(s[0]):.4f}")
            ok &= good
    # A clamp cannot see it, a share can.
    G, s0 = 4.0, .2
    W, rel = w_centres(n, 1, s0, 1.0)
    rng = seed_of(8, 1)
    N = n + 1
    pin = np.zeros((4, N), bool)
    pin[:, n] = True
    y = run(W, start(N, 4, rest(G), rng), G, 60, rel, pin=pin, rng=rng)
    v = float(y[:, :n].mean())
    ok &= v >= .5
    print(f"  G 4, s .2: parts read {v:.3f} with the point clamped opposite")
    return ok


def budget_step(x, G, cap, drop=None, off=False, p=2, u=None, rng=None):
    m = x.mean(1)
    if drop is not None:
        m = m.copy()
        m[:, drop] = 0
    if off:
        h = np.zeros_like(m)
    elif cap:
        z = np.sqrt((m * m).sum(1, keepdims=True)) if p == 2 else np.abs(m).sum(1, keepdims=True)
        h = m / np.maximum(z, 1.0)
    else:
        h = m
    fld = G * h
    if u is not None:
        fld = fld - u
    x = x + DT * (-x + np.tanh(fld[:, None, :])) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
    return x


def job_budget(_o):
    """Z8."""
    ok = True
    n = 32
    for G in (2.0, 4.0):
        for p in (2, 1):
            for d in (1, 2, 4, 8, 16, 32):
                rng = seed_of(9, G, p, d)
                x = budget_rest(G, d, p) + SPREAD * rng.standard_normal((4, n, d))
                for _ in range(int(200 / DT)):
                    x = budget_step(x, G, True, p=p, rng=rng)
                a = float(x.mean((0, 1, 2)))
                pa = budget_rest(G, d, p)
                if G / norm_of(pa, pa, d, p) >= 1.05:
                    ok &= within(a, pa, .03)
                x2 = rest(G) + SPREAD * rng.standard_normal((4, n, d))
                for _ in range(int(100 / DT)):
                    x2 = budget_step(x2, G, False, rng=rng)
                a2 = float(x2.mean())
                ok &= within(a2, rest(G), .03)
                print(f"  G {G:g}, L{p}, d {d}: through one budget {a:.3f} (derived {pa:.3f}); no budget {a2:.3f}")
    # Flip threshold.
    for G in (2.0, 4.0):
        for d in (1, 2, 4, 8, 16, 32):
            lo, hi = 0.0, 6.0
            pred = budget_flip(G, d)
            am = budget_rest(G, d)
            for _ in range(10):
                mid = (lo + hi) / 2
                rng = seed_of(10, G, d, mid)
                x = am + SPREAD * rng.standard_normal((4, n, d))
                u = np.zeros((4, d))
                u[:, 0] = mid
                for _t in range(int(300 / DT)):
                    x = budget_step(x, G, True, u=u, rng=rng)
                if np.median(x[:, :, 0].mean(1)) < 0:
                    hi = mid
                else:
                    lo = mid
            th = (lo + hi) / 2
            good = (abs(th - pred) <= max(.1 * pred, .03))
            ok &= good
            print(f"  G {G:g}, d {d}: flip threshold {th:.3f}; derived {pred:.3f}; without a budget {flip_u(G):.3f}")
    return ok


def job_drop(_o):
    """Z9."""
    ok = True
    n, d, G = 32, 8, 4.0
    rng = seed_of(11, 1)
    base = SPREAD * rng.standard_normal((4, n, d))
    # One point, one budget.
    x = budget_rest(G, d) + base
    for _ in range(int(100 / DT)):
        x = budget_step(x, G, True, rng=rng)
    before = float(x[:, :, 1:].mean())
    y = x.copy()
    for _ in range(int(100 / DT)):
        y = budget_step(y, G, True, drop=0, rng=rng)
    after = float(y[:, :, 1:].mean())
    dropped = float(np.abs(y[:, :, 0].mean(1)).max())
    pa, pb = tanh(G / sqrt(d)), tanh(G / sqrt(d - 1))
    good = within(before, pa, .03) and within(after, pb, .03) and dropped <= .1
    ok &= good
    print(f"  One budget: others {before:.3f} to {after:.3f}, derived {pa:.3f} to {pb:.3f}; dropped trait {dropped:.3f}")
    z = x.copy()
    for _ in range(int(60 / DT)):
        z = budget_step(z, G, True, off=True, rng=rng)
    gone = float(np.abs(z.mean(1)).max())
    ok &= gone <= .1
    print(f"  Point removed: largest trait reading {gone:.3f}")
    # d occupants, one for each goal.
    x = rest(G) + base
    for _ in range(int(100 / DT)):
        x = budget_step(x, G, False, rng=rng)
    before = float(x[:, :, 1:].mean())
    y = x.copy()
    for _ in range(int(100 / DT)):
        y = budget_step(y, G, False, drop=0, rng=rng)
    after = float(y[:, :, 1:].mean())
    dropped = float(np.abs(y[:, :, 0].mean(1)).max())
    good = abs(after - before) <= .01 and dropped <= .1
    ok &= good
    print(f"  One occupant per goal: others {before:.3f} to {after:.3f}; dropped trait {dropped:.3f}")
    return ok


def grow_one(job):
    seed, beta, sink = job
    rng = seed_of(12, seed, beta, sink)
    N, d, G, s, kappa, tau = 128, 3, 4.0, .4, 16.0, 20.0
    x = .05 * rng.standard_normal((N, d))
    pi = (1 - np.eye(N)) / (N - 1)
    for _ in range(int(600 / DT)):
        w = (pi + pi.T) / 2
        R = w / np.maximum(w.sum(1, keepdims=True), 1e-12)
        x = x + DT * (-x + np.tanh(G * ((1 - s) * x + s * R @ x))) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
        q = x @ x.T / d
        inn = pi.sum(0)
        t = np.exp(kappa * q) * (inn + 1e-3) ** beta
        np.fill_diagonal(t, 0)
        t = t / t.sum(1, keepdims=True)
        if sink:
            for _k in range(8):
                t = t / t.sum(1, keepdims=True)
                t = t / t.sum(0, keepdims=True)
            t = t / t.sum(1, keepdims=True)
        pi = pi + DT * (t - pi) / tau
    w = (pi + pi.T) / 2
    R = w / np.maximum(w.sum(1, keepdims=True), 1e-12)
    code = np.sign(x)
    keys = {}
    for i in range(N):
        keys.setdefault(tuple(code[i]), []).append(i)
    out = []
    for key, mem in keys.items():
        if len(mem) < 8:
            continue
        mem = np.array(mem)
        W = R[np.ix_(mem, mem)]
        W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
        nb = len(mem)
        Wb = (1 - s) * np.eye(nb) + s * W
        m = rest(G)
        pin = np.eye(nb, dtype=bool)
        y = run(Wb, np.full((nb, nb), m), G, 40, pin=pin, sigma=0.0)
        moved = np.array([np.delete(y[b], b).mean() <= -.5 for b in range(nb)])
        y2 = run(Wb, np.full((nb, nb), m), G, 40, pin=~pin, sigma=0.0)
        follows = y2[np.arange(nb), np.arange(nb)] <= -.5
        ins = pi[np.ix_(mem, mem)].sum(0)
        out.append((nb, int((moved & follows).sum()), float(ins.max() / ins.mean())))
    return seed, out


def job_grow(_o):
    """Z10."""
    ok = True
    arms = [("reads alike only, row budget", 0.0, False, 0), ("reach exponent .5", .5, False, 0), ("reach exponent 2", 2.0, False, 1), ("reach exponent 2, Sinkhorn", 2.0, True, 0)]
    with Pool(8) as p:
        for lab, beta, sink, want in arms:
            res = p.map(grow_one, [(s, beta, sink) for s in range(12)])
            blocks = [b for _s, o in res for b in o]
            sizes = [b[0] for b in blocks]
            cnt = [b[1] for b in blocks]
            rat = [b[2] for b in blocks]
            fr = float(np.mean([c == want for c in cnt])) if cnt else 0.0
            ok &= fr >= .75
            print(f"  {lab}: {len(blocks)} blocks, median size {int(np.median(sizes)) if sizes else 0}; predicted {want}; matching {fr:.2f}; counts {sorted(set(cnt))}; largest read over mean, median {float(np.median(rat)) if rat else 0:.2f}")
    return ok


def job_e1(_o):
    ok = True
    for G in (3.0, 4.0):
        eps = 10.0
        lo, hi = 0.0, 2 * G
        for _ in range(9):
            mid = (lo + hi) / 2
            rng = seed_of(21, G, eps, mid)
            y = start(65, 4, rest(G), rng)
            f = 1 - exp(-DT / eps)
            for _t in range(int(600 / DT)):
                y[:, 64] += f * (y[:, :64].mean(1) - y[:, 64])
                y[:, :64] += DT * (-y[:, :64] + np.tanh(G * y[:, 64:65] - mid)) + sqrt(DT) * SIGMA * rng.standard_normal((4, 64))
            if np.median(y[:, 64]) <= -.5:
                hi = mid
            else:
                lo = mid
        th = (lo + hi) / 2
        ok &= within(th, flip_u(G), .03)
        print(f"  G {G:g}, speed 10, run 600: threshold {th:.3f}, u_c {flip_u(G):.3f}")
    return ok


def grow_empty(job):
    seed, beta, empty = job
    rng = seed_of(22, seed, beta, empty)
    N, d, G, s, kappa, tau = 128, 3, 4.0, .4, 16.0, 20.0
    x = .05 * rng.standard_normal((N, d))
    pi = (1 - np.eye(N)) / (N - 1)
    own = np.full(N, 1 - s)
    for _ in range(int(600 / DT)):
        w = (pi + pi.T) / 2
        R = w / np.maximum(w.sum(1, keepdims=True), 1e-12)
        inn = pi.sum(0)
        if empty:
            own = (1 - s) / (1 + np.maximum(0, inn - 1))
        x = x + DT * (-x + np.tanh(G * (own[:, None] * x + (1 - own[:, None]) * (R @ x)))) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
        q = x @ x.T / d
        t = np.exp(kappa * q) * (inn + 1e-3) ** beta
        np.fill_diagonal(t, 0)
        t = t / t.sum(1, keepdims=True)
        pi = pi + DT * (t - pi) / tau
    w = (pi + pi.T) / 2
    R = w / np.maximum(w.sum(1, keepdims=True), 1e-12)
    inn = pi.sum(0)
    if empty:
        own = (1 - s) / (1 + np.maximum(0, inn - 1))
    code = np.sign(x)
    keys = {}
    for i in range(N):
        keys.setdefault(tuple(code[i]), []).append(i)
    out = []
    for key, mem in keys.items():
        if len(mem) < 8:
            continue
        mem = np.array(mem)
        W = R[np.ix_(mem, mem)]
        W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
        nb = len(mem)
        ow = own[mem]
        Wb = np.diag(ow) + (1 - ow)[:, None] * W
        m = rest(G)
        pin = np.eye(nb, dtype=bool)
        y = run(Wb, np.full((nb, nb), m), G, 40, pin=pin, sigma=0.0)
        moved = np.array([np.delete(y[b], b).mean() <= -.5 for b in range(nb)])
        y2 = run(Wb, np.full((nb, nb), m), G, 40, pin=~pin, sigma=0.0)
        follows = y2[np.arange(nb), np.arange(nb)] <= -.5
        both = moved & follows
        hub = int(np.argmax(pi[np.ix_(mem, mem)].sum(0)))
        h = 1.0
        for _t in range(int(400 / DT)):
            h += DT * (-h + tanh(G * ow[hub] * h))
        out.append((nb, int(both.sum()), h >= .5, float(ow[hub])))
    return seed, out


def job_e2(_o):
    ok = True
    with Pool(8) as p:
        for lab, empty, lo, hi, want_count in [("reach 2, no emptying", False, .9, 1.0, None), ("reach 2, emptying", True, 0.0, .25, 1)]:
            res = p.map(grow_empty, [(sd, 2.0, empty) for sd in range(12)])
            blocks = [b for _s, o in res for b in o]
            alone = float(np.mean([b[2] for b in blocks]))
            cnt = float(np.mean([b[1] == 1 for b in blocks]))
            ok &= lo <= alone <= hi
            if want_count is not None:
                ok &= cnt >= .75
            print(f"  {lab}: {len(blocks)} blocks, median size {int(np.median([b[0] for b in blocks]))}; count 1 in {cnt:.2f}; centre holds alone in {alone:.2f}; median own share of the centre {float(np.median([b[3] for b in blocks])):.3f}")
    return ok


def job_e3(_o):
    ok = True
    n = 64
    for c in (1.0, .9):
        for G in GS:
            bs = np.arange(0, 1.0001, .01)
            rng = seed_of(23, c, G)
            x = start(n, len(bs), rest(G), rng)
            b = bs[:, None]
            for _ in range(int(1000 / DT)):
                mn = x.mean(1, keepdims=True)
                r = (n * mn - x) / (n - 1)
                x = x + DT * (-x + np.tanh(G * ((1 - c) * r + c * b * mn))) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
            held = np.abs(x.mean(1)) >= .1
            lim = float(bs[held].min()) if held.any() else 1.0
            want = (1 / G - 1 + c) / c
            ok &= abs(lim - want) <= .03
            print(f"  c {c:g}, G {G:g}: holds from openness {lim:.2f}; derived {want:.3f}")
    G, c = 4.0, .5
    rng = seed_of(23, 99)
    x = start(n, 4, rest(G), rng)
    for _ in range(int(200 / DT)):
        mn = x.mean(1, keepdims=True)
        r = (n * mn - x) / (n - 1)
        x = x + DT * (-x + np.tanh(G * (1 - c) * r)) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
    v = float(np.abs(x.mean(1)).min())
    ok &= v >= .5
    print(f"  c .5, G 4, aperture shut: lowest reading {v:.3f}")
    return ok


def job_e4(_o):
    ok = True
    n = 64
    for G in (3.0, 4.0, 8.0):
        cs = np.arange(.05, .7, .01)
        rng = seed_of(24, G)
        x = start(n, len(cs), rest(G), rng)
        cc = cs[:, None]
        for _ in range(int(120 / DT)):
            r = (x.sum(1, keepdims=True) - x) / (n - 1)
            x = x + DT * (-x + np.tanh(G * ((1 - cc) * r - cc))) + sqrt(DT) * SIGMA * rng.standard_normal(x.shape)
        turned = x.mean(1) <= -.5
        lim = float(cs[turned].min()) if turned.any() else float("inf")
        ok &= abs(lim - s_flip(G)) <= .03
        print(f"  G {G:g}: the point turns the parts from c = {lim:.2f}; s_flip {s_flip(G):.3f}")
    return ok


JOBS = {"same": ("Z1", job_same), "partial": ("Z2", job_partial), "clamp": ("Z3", job_clamp), "divide": ("Z4", job_divide), "remove": ("Z5", job_remove), "alone": ("Z6", job_alone), "share": ("Z7", job_share), "budget": ("Z8", job_budget), "drop": ("Z9", job_drop), "grow": ("Z10", job_grow), "e1": ("E1", job_e1), "e2": ("E2", job_e2), "e3": ("E3", job_e3), "e4": ("E4", job_e4)}


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    which = sys.argv[2:] or list(JOBS)
    res = {}
    for w in which:
        if w == "solve":
            solve()
            continue
        name, fn = JOBS[w]
        t0 = time.time()
        r = fn(None)
        ok = r[0] if isinstance(r, tuple) else r
        res[name] = bool(ok)
        print(f"{name} {verdict(ok)}; {time.time()-t0:.0f}s", flush=True)
    with open(os.path.join(outdir, "results_" + "_".join(which) + ".json"), "w") as f:
        json.dump(res, f)
