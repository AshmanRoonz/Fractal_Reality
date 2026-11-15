"""Does cohesion buy distinctness outside the family it was tested on? Predictions frozen before any run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after an outside review of "A Theory of Wholeness" (https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte).
Results: F1, F2, F3, F5, F6, F7, F8, F11, F12, F13, F14 passed. F4 missed one clause: 10.7% against a 10% limit at G = 1.5, where the jump lies between grid points .10 and .12 and s_hold = .1198; every other clause held. F9 missed: right direction, 12% and 7% against 15%, and not graded by h. F10 missed: rings tear as predicted, but complete interiors tear too, and no interior merged at any realised share. Its second clause printed True only because inf <= inf; the numbers show it false, and the code now requires a finite crossing.
After the follow-up: P1, P2, P5 passed. P3 missed: door sites pass through a low magnitude near s = .15 to .19, then commit together at one shared sign above .9, so they do not stay neutral; the other sites do stay above half. P4 missed: blocks hold through 4 doors at G = 2 and 5 at G of 3 to 8, not by 1 - 1/G. Totals: 14 of 19 passed, 5 missed.
Seen in the F6 table and not predicted: in the on-off law h does matter at high gain (merge .013, .018, .020, .025 from ring k=1 to complete at G = 4), and at G = 8 rings k=1 and 2 lose the off state with no contact, under noise .02. So "mixing speed does not buy distinctness" has that exception.

Needs numpy and scipy. All data are synthetic.
Run: python -I wholeness_reference_v1.py OUTDIR [family noise doors release form listen grid:PATH_TO_OLD_RUN_DIR after]

WHY. The review objected that "cohesion does not buy distinctness" is narrower than its wording, since in symmetric Kuramoto networks the internal forces cancel when you compute a group's mean velocity.
That is right, and it is more general than Kuramoto. Everything tested so far has an interior force that depends only on differences between sites.

HAND DERIVATIONS BEFORE ANY RUN.
(a) The invariance lemma. Let the interior force on site i be f_i(x) = sum_j W_ij g(x_j - x_i), with W symmetric and g odd. Then sum_i f_i = 0, for any x, any W, any strength.
    So the group's mean has no interior term at all. In words: an interior that only cares how its parts differ has no opinion about where the whole group sits. Diffusion and Kuramoto are both this.
    H1 in wholeness_theory_v1.py therefore tested close to an identity. Its reach is exactly this family. Note also what it says about strength: raising coupling here only strengthens the pull across, so the merge point falls as 1/G.
(b) Where the lemma fails. Take x_i' = -x_i + F(G sum_j W_ij x_j), where W has row sums 1 and F saturates. Each site has a leak and a limit. The interior force no longer vanishes on the collective move.
    With two blocks and outward share s, the state (m, -m) has m = tanh(G(1-2s)m). It exists while G(1-2s) > 1, so it needs gain above 1 and a limiter, and nobody supplies its value or its sign: history picks the sign.
    That is a reference the interior makes for itself.
    It is lost earlier than that, when the shared mode goes unstable: G(1-m^2) = 1. So m* = sqrt(1-1/G), and s_hold(G) = (1/2)(1 - atanh(m*)/(G m*)).
    Values: G 1.25 .070, 1.5 .120, 2 .188, 3 .266, 4 .310, 8 .387, 16 .433. As G grows, s_hold approaches 1/2: a part stays itself while most of its relating lands inside.
    So here strength helps, the opposite sign from (a). The loss is a jump, not a fade.
(c) Mixing speed is not gain. The uniform vector is an eigenvector of W whatever the interior topology, so the gap h should not enter s_hold at low noise. So "cohesion" is at least two things: how fast differences die (h) and how strongly the interior feeds itself (G).
(d) Gain is not enough. With x_i' = -x_i + hill(G sum_j W_ij x_j), states are on and off. An off block has no interior activity to push back with, and the pull on it scales with G, so the merge point should FALL with G. So the rule is not "non-invariant laws reward gain". It is: gain helps when the interior's own activity opposes the pull.
(e) Linear leak without a limit. x_i' = -x_i + G W x + u r, G < 1. Separation over its own value at s = 0 is (1-G)/(1-G(1-2s)), so s_merge = (1-G)/(2G), falling with G, though absolute separation rises with G. With u gone it decays at every s, even s = 0. No self-made reference.
(f) Keep versus make. From a small random start the shared mode grows at G-1 and the opposed mode at G(1-2s)-1, so the opposed mode loses by a factor exp(-2Gs t) before saturation. Opposed states should form only at s well below s_hold.
(g) Listening. About (m, -m), with a = 1-m^2 and input u on block 1: self gain = (a/2)(1/(1-aG) + 1/(1-aG(1-2s))), cross gain = (a/2)(1/(1-aG) - 1/(1-aG(1-2s))). Cross gain diverges at s_hold, so a part listens most just before it stops being itself.
    To flip block 1 at s = 0 takes u = |atanh(m*) - G m*|: .533 at G = 2, 2.147 at G = 4.
    Limit of this law: identity here is one bit, so rewriting yourself means joining the other block. A law with a space of identities needs patterns, which this script does not test.
(h) Price. Force balance says any reference must cancel a pull proportional to s, so squared counter-force goes as s^2 whatever the law. The earlier "1.2 s^2" is this, not a discovery. Leak power, mean x^2, is a different cost: largest at s = 0, falling with s. So this law pays to exist rather than to connect.
(i) The plane's -.003. a depends on s = b + x and c on the ratio b/x. Under swapping b and x, a is unchanged and c goes to about 1 - c. The grid was swap-symmetric, so the rank correlation had to come out near zero whatever the relation. The right claim is that (s, b/x) are independent coordinates, not that a sample is uncorrelated.

PREDICTIONS.
F1 (diffusion). Merge = H/(2G) within 10% at H = 1, range across interiors under 5%.
F2 (oscillators). G times merge within 15% of .346 at every G, complete interior; range across interiors under 15% at G >= 2.
F3 (leaky). Merge = (1-G)/(2G) within 10%, range across interiors under 5%. Absolute separation at s = .1 rises with G.
F4 (limit law, the main test). Complete interior: merge within 10% of s_hold(G) at every G; rising with G at every step; above .4 at G = 16; below .5 everywhere. Spearman(merge, G) >= .9 across all interiors and G.
    If this passes, "cohesion does not buy distinctness" is false as stated.
F5 (gap at low noise). In the limit law at G >= 2, merge varies by under 15% across ring k=1 to complete, though h varies eightfold. So mixing speed still does not buy distinctness here, while gain does.
F6 (on-off law). Merge falls with G from 1.5 to 8, and at G = 8 is under half its value at G = 1.5.
F7 (release, breaks my own row in "What would break it"). Identical frequencies and no reference, starting from a difference, retained separation at s >= .01 is under .5 in diffusion and oscillators; in the leaky law it is under .5 even at s = 0; in the limit law it stays above .5 up to s_hold within 10%.
F8 (keep versus make). Limit law, complete, random start, no pulses: P(opposed) >= .35 at s <= .005; falls below .25 at s_form under half of s_hold, at G = 2, 4, 8.
F9 (noise can bring the gap back). Limit law, sigma .2: ring k=1 loses half of complete's own s = 0 separation at an s at least 15% below complete's, at G = 2 and 4.
F10 (doors). Limit law, 4 of 12 doors. Ring k=1 at G = 2 and 4: door separation falls through .5 at a realised s at least 20% below the other sites'. Complete at G = 2: within 10% of each other. At G = 2 the merge differs by at least 15% between ring k=1 and complete, direction not predicted.
F11 (listening). Self and cross gains within 10% of (g). Cross gain rises at every step in s, and at .95 s_hold exceeds 5 times its value at .1 s_hold.
F12 (flip). Flip input at s = 0 within 10% of (g), falling at every step in s, under 15% of the s = 0 value at .95 s_hold.
F13 (price). Leak power falls with s at every step up to .95 s_hold. Squared pull rises at every step.
F14 (grid). On the old belonging grid, Spearman(a, c) is below -.3 for b > x and above +.3 for x > b, cancelling to near zero on the whole grid.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. F4's miss looks like grid spacing, F5's zero range is limited by the same spacing, and F10 surprised me: door sites lose their separation and the rest of the block holds, whatever the interior.
Hand argument for that. Door sites of the two blocks lock at about zero, not at the other block's sign, so the other sites keep gain of about G(1 - d/n) while doors weigh in their inputs. So the block should survive if d/n < 1 - 1/G. And each door site's budget is one: as it spends more outward it spends less inward, so at very large contact the rest of the block is left to itself with full gain G.
P1. Fine grid, limit law, complete: merge within 5% of s_hold at every G.
P2. Fine grid, limit law: range across the four interiors under 5% at G >= 2.
P3. At 4 doors, G = 2, complete and ring k=1: where door separation has fallen below half its start, mean door activity magnitude is under .3, and the other sites stay above half at every realised share.
P4. Limit law, complete, d of 12 doors, d = 1 to 11. The other sites stay above half their start at every contact when d/12 < 1 - 1/G, and fall below it at some contact when d/12 >= 1 - 1/G + 1/12. Right within one door at G = 2, 3, 4, 8.
P5. Limit law, complete, G = 2, d = 7 and 8: the other sites fall below half at some contact and are back above half at the largest contact.
"""
import json
import os
import sys
import time
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.stats import spearmanr

N = 12
SEEDS = 16
DT = .05
LAW_ID = dict(diffuse=1, kuramoto=2, leaky=3, limit=4, onoff=5)
S_GRID = [0, .005, .01, .015, .02, .03, .04, .05, .06, .07, .08, .09, .10, .12, .14, .16, .18, .19, .2, .22, .24, .26, .28, .3, .32, .34, .36, .38, .4, .42, .44, .46, .48, .5, .6, .7, .8, .9]
GAINS = dict(diffuse=(1, 2, 4, 8), kuramoto=(1, 2, 4, 8), leaky=(.5, .7, .8, .9), limit=(1.25, 1.5, 2, 3, 4, 8, 16), onoff=(1, 1.5, 2, 4, 8))
REF = dict(diffuse=1.0, kuramoto=.4, leaky=.1, limit=0.0, onoff=0.0)
TOPS = (1, 2, 3, 6)
NAME = {1: "ring k=1", 2: "ring k=2", 3: "ring k=3", 6: "complete"}


def s_hold(G):
    m = np.sqrt(1 - 1 / G)
    return .5 * (1 - np.arctanh(m) / (G * m))


def ring_lattice(n, k):
    if k >= n // 2:
        A = np.ones((n, n)) - np.eye(n)
    else:
        A = np.zeros((n, n))
        for d in range(1, k + 1):
            A += np.roll(np.eye(n), d, 1) + np.roll(np.eye(n), -d, 1)
    return A / A.sum(1, keepdims=True)


def network(k, s, doors=0, n=N):
    inner = ring_lattice(n, k)
    W = np.zeros((2 * n, 2 * n))
    if not doors:
        W[:n, :n] = W[n:, n:] = inner * (1 - s)
        W[:n, n:] = W[n:, :n] = s / n
        return W, float(s), np.arange(n)
    D = np.arange(0, n, n // doors)[:doors]
    W[:n, :n] = W[n:, n:] = inner
    for a_ in D:
        for b_ in D:
            W[a_, n + b_] = W[n + b_, a_] = s * n / (doors * doors)
    d = np.ones(2 * n)
    for _ in range(400):
        d = np.sqrt(d / np.maximum(W @ d, 1e-280))
    W = W * np.outer(d, d)
    W = (W + W.T) / 2
    return W, float(W[:n, n:].sum() / n), D


def hill(y, theta=.5):
    y = np.maximum(y, 0)
    y4 = y ** 4
    return y4 / (theta ** 4 + y4)


def crossing(xs, ys, level):
    """First x where y falls through level, interpolated. inf if it never does; 0 if it starts below."""
    if ys[0] < level:
        return 0.0
    for i in range(len(xs) - 1):
        if ys[i] >= level > ys[i + 1]:
            return float(xs[i] + (ys[i] - level) * (xs[i + 1] - xs[i]) / (ys[i] - ys[i + 1]))
    return float("inf")


def rate_field(law, W, G, ref, sign, bias):
    if law == "diffuse":
        return lambda x: G * (x @ W - x) + bias + ref * (sign - x)
    if law == "leaky":
        return lambda x: -x + G * (x @ W) + bias + ref * sign
    if law == "limit":
        return lambda x: -x + np.tanh(G * (x @ W) + bias + ref * sign)
    if law == "onoff":
        return lambda x: -x + hill(G * (x @ W) + bias)
    raise ValueError(law)


def sim(job):
    """One cell. release=True removes the reference and starts from a difference."""
    law, G, k, s, doors, sigma, spread, release, seeds, T = job
    n = N
    W, s_real, D = network(k, s, doors)
    rng = np.random.default_rng([LAW_ID[law], int(G * 100), k, int(s * 10000), doors, int(sigma * 100), int(release)])
    sign = np.r_[np.ones(n), -np.ones(n)]
    xi = rng.normal(0, 1, (seeds, 2 * n))
    xi[:, :n] -= xi[:, :n].mean(1, keepdims=True)
    xi[:, n:] -= xi[:, n:].mean(1, keepdims=True)
    bias = spread * xi
    steps = int(T / DT)
    burn = int(steps * .75)
    nd = np.setdiff1d(np.arange(n), D)
    ref = 0.0 if release else REF[law]
    if law == "kuramoto":
        om = ref * sign + bias
        th = sign * (1.0 if release else 0.0) + rng.normal(0, .1, (seeds, 2 * n))

        def f(t_):
            d_ = t_[:, None, :] - t_[:, :, None]
            return om + G * (W[None] * np.sin(d_)).sum(2)

        start = None
        phi, cnt = 0.0, 0
        for i in range(steps):
            k1 = f(th)
            th = th + DT / 2 * (k1 + f(th + DT * k1))
            if i >= burn:
                if start is None:
                    start = th.copy()
                if i % 5 == 0:
                    z = np.exp(1j * th)
                    phi = phi + np.abs(np.angle(z[:, :n].mean(1) * np.conj(z[:, n:].mean(1))))
                    cnt += 1
        if release:
            sep = float(np.median(phi / cnt) / 2.0)
            return dict(law=law, G=G, k=k, s=s_real, target=s, doors=doors, sigma=sigma, release=release, sep=sep, door=sep, rest=sep)
        rate = (th - start) / ((steps - burn) * DT)
        sep = (rate[:, :n].mean(1) - rate[:, n:].mean(1)) / (2 * ref)
        return dict(law=law, G=G, k=k, s=s_real, target=s, doors=doors, sigma=sigma, release=release, sep=float(np.median(np.abs(sep))), door=0.0, rest=0.0)
    field = rate_field(law, W, G, ref, sign, bias)
    if law == "onoff":
        x = np.r_[np.ones(n), np.zeros(n)] * np.ones((seeds, 2 * n))
    elif law == "leaky" and not release:
        x = sign * ref / (1 - G) * np.ones((seeds, 2 * n))
    elif law == "leaky":
        x = sign * 1.0 * np.ones((seeds, 2 * n))
    else:
        x = sign * 1.0 * np.ones((seeds, 2 * n))
    tot, door, rest, cnt, dabs = 0.0, 0.0, 0.0, 0, 0.0
    amp = sigma * np.sqrt(DT)
    for i in range(steps):
        k1 = field(x)
        x = x + DT / 2 * (k1 + field(x + DT * k1))
        if sigma:
            x = x + amp * rng.normal(0, 1, x.shape)
        if i >= burn and i % 5 == 0:
            tot = tot + np.abs(x[:, :n].mean(1) - x[:, n:].mean(1))
            door = door + np.abs(x[:, D].mean(1) - x[:, n + D].mean(1))
            dabs = dabs + np.abs(x[:, D]).mean(1)
            if len(nd):
                rest = rest + np.abs(x[:, nd].mean(1) - x[:, n + nd].mean(1))
            cnt += 1
    start_sep = 1.0 if law == "onoff" else 2.0
    return dict(law=law, G=G, k=k, s=s_real, target=s, doors=doors, sigma=sigma, release=release, sep=float(np.median(tot / cnt)), door=float(np.median(door / cnt)), rest=float(np.median(rest / cnt)) if len(nd) else 0.0, start=start_sep, door_abs=float(np.median(dabs / cnt)))


def run_jobs(pool, jobs, path, label):
    t0 = time.time()
    out = []
    with open(path, "w") as fh:
        for i, r in enumerate(pool.imap_unordered(sim, jobs, chunksize=2)):
            out.append(r)
            fh.write(json.dumps(r) + "\n")
            if (i + 1) % 200 == 0:
                fh.flush()
                print(f"  {label} {i + 1}/{len(jobs)}, {time.time() - t0:.0f}s", flush=True)
    print(f"  {label} done, {len(jobs)} cells, {time.time() - t0:.0f}s", flush=True)
    return out


def verdict(ok):
    return "PASS" if ok else "MISS"


def merge_table(res, law, sigma=.02):
    """merge[(G, k)] from separation over its own value at s = 0."""
    out, base = {}, {}
    for G in GAINS[law]:
        for k in TOPS:
            g = sorted([r for r in res if r["law"] == law and r["G"] == G and r["k"] == k and r["sigma"] == sigma and not r["doors"]], key=lambda r: r["s"])
            if not g:
                continue
            b = g[0]["sep"]
            base[(G, k)] = b
            out[(G, k)] = crossing([r["s"] for r in g], [r["sep"] / max(b, 1e-12) for r in g], .5)
    return out, base


def part_family(outdir, pool):
    jobs = [(law, G, k, s, 0, .02, .05, False, SEEDS, 300.0) for law in GAINS for G in GAINS[law] for k in TOPS for s in S_GRID]
    res = run_jobs(pool, jobs, os.path.join(outdir, "family.jsonl"), "family")
    for law in GAINS:
        m, b = merge_table(res, law)
        print(f"{law}: merge by G (rows) and interior (columns {[NAME[k] for k in TOPS]}); separation at s = 0 in brackets for complete")
        for G in GAINS[law]:
            print(f"  G {G}: " + ", ".join(f"{m[(G, k)]:.3f}" for k in TOPS) + f" [{b[(G, 6)]:.3f}]")
    m, _ = merge_table(res, "diffuse")
    rg = max((max(m[(G, k)] for k in TOPS) - min(m[(G, k)] for k in TOPS)) / min(m[(G, k)] for k in TOPS) for G in GAINS["diffuse"])
    err = max(abs(m[(G, 6)] - 1 / (2 * G)) / (1 / (2 * G)) for G in GAINS["diffuse"])
    print(f"F1 {verdict(err < .10 and rg < .05)}: worst error against H/(2G) {err:.3f}; worst range across interiors {rg:.3f}")
    m, _ = merge_table(res, "kuramoto")
    err = max(abs(G * m[(G, 6)] - .346) / .346 for G in GAINS["kuramoto"])
    rg = max((max(m[(G, k)] for k in TOPS) - min(m[(G, k)] for k in TOPS)) / min(m[(G, k)] for k in TOPS) for G in GAINS["kuramoto"] if G >= 2)
    print(f"F2 {verdict(err < .15 and rg < .15)}: G times merge {[round(G * m[(G, 6)], 3) for G in GAINS['kuramoto']]}; worst error {err:.3f}; worst range across interiors at G >= 2 {rg:.3f}")
    m, _ = merge_table(res, "leaky")
    err = max(abs(m[(G, 6)] - (1 - G) / (2 * G)) / ((1 - G) / (2 * G)) for G in GAINS["leaky"])
    rg = max((max(m[(G, k)] for k in TOPS) - min(m[(G, k)] for k in TOPS)) / min(m[(G, k)] for k in TOPS) for G in GAINS["leaky"])
    ab = [[r for r in res if r["law"] == "leaky" and r["G"] == G and r["k"] == 6 and r["target"] == .1][0]["sep"] for G in GAINS["leaky"]]
    print(f"F3 {verdict(err < .10 and rg < .05 and all(ab[i] < ab[i + 1] for i in range(len(ab) - 1)))}: worst error {err:.3f}; range {rg:.3f}; absolute separation at s = .1 by G {[round(v, 3) for v in ab]}")
    m, _ = merge_table(res, "limit")
    Gs = GAINS["limit"]
    line = [(G, round(m[(G, 6)], 3), round(s_hold(G), 3)) for G in Gs]
    err = max(abs(m[(G, 6)] - s_hold(G)) / s_hold(G) for G in Gs)
    rising = all(m[(Gs[i], 6)] < m[(Gs[i + 1], 6)] for i in range(len(Gs) - 1))
    allm = [(G, m[(G, k)]) for G in Gs for k in TOPS]
    rho = spearmanr([a for a, _ in allm], [b for _, b in allm]).statistic
    print(f"F4 {verdict(err < .10 and rising and m[(16, 6)] > .4 and m[(16, 6)] < .5 and rho >= .9)}: (G, merge, s_hold) {line}; worst error {err:.3f}; Spearman(merge, G) {rho:.3f}")
    rg = {G: (max(m[(G, k)] for k in TOPS) - min(m[(G, k)] for k in TOPS)) / min(m[(G, k)] for k in TOPS) for G in Gs if G >= 2}
    print(f"F5 {verdict(max(rg.values()) < .15)}: range across interiors by G {[(G, round(v, 3)) for G, v in rg.items()]}")
    m, _ = merge_table(res, "onoff")
    Gs = GAINS["onoff"]
    fall = [m[(G, 6)] for G in Gs if G >= 1.5]
    print(f"F6 {verdict(all(fall[i] > fall[i + 1] for i in range(len(fall) - 1)) and m[(8, 6)] < .5 * m[(1.5, 6)])}: merge by G, complete {[(G, round(m[(G, 6)], 3)) for G in Gs]}")


def part_release(outdir, pool):
    S = [0, .005, .01, .02, .05, .1, .15, .2, .25, .3, .35, .4, .45]
    Gs = dict(diffuse=(2,), kuramoto=(2,), leaky=(.8,), limit=(2, 4, 8), onoff=(1.5,))
    jobs = [(law, G, 6, s, 0, .02, 0.0, True, SEEDS, 300.0) for law in Gs for G in Gs[law] for s in S]
    res = run_jobs(pool, jobs, os.path.join(outdir, "release.jsonl"), "release")
    json.dump(res, open(os.path.join(outdir, "release.json"), "w"))
    print("Release: identical sites, no reference, starting from a difference. Retained separation, by s")
    table = {}
    for law in Gs:
        for G in Gs[law]:
            g = sorted([r for r in res if r["law"] == law and r["G"] == G], key=lambda r: r["s"])
            start = g[0].get("start", 1.0) if law != "kuramoto" else 1.0
            vals = [r["sep"] / start for r in g]
            table[(law, G)] = (g, vals)
            print(f"  {law} G {G}: " + ", ".join(f"{r['s']:.3f}: {v:.3f}" for r, v in zip(g, vals)))
    pick = lambda law, G, lo: max(v for r, v in zip(*table[(law, G)]) if r["s"] >= lo)
    a = pick("diffuse", 2, .01) < .5
    b = pick("kuramoto", 2, .01) < .5
    c = table[("leaky", .8)][1][0] < .5
    lim = []
    for G in (2, 4, 8):
        g, vals = table[("limit", G)]
        last = max((r["s"] for r, v in zip(g, vals) if v > .5), default=0.0)
        nxt = min((r["s"] for r, v in zip(g, vals) if v <= .5), default=float("inf"))
        lim.append((G, last, nxt, round(s_hold(G), 3)))
    d = all(l <= s * 1.1 and n >= s * .9 for _, l, n, s in lim)
    print(f"F7 {verdict(a and b and c and d)}: diffusion {a}, oscillators {b}, leaky {c}, limit {d}; limit law (G, last s held, next s, s_hold) {lim}")


def form_job(job):
    G, s, seeds, T = job
    W, _, _ = network(6, s)
    n = N
    rng = np.random.default_rng([int(G * 100), int(s * 10000)])
    x = rng.normal(0, .03, (seeds, 2 * n))
    amp = .02 * np.sqrt(DT)
    for _ in range(int(T / DT)):
        f1 = -x + np.tanh(G * (x @ W))
        y = x + DT * f1
        x = x + DT / 2 * (f1 - y + np.tanh(G * (y @ W))) + amp * rng.normal(0, 1, x.shape)
    m1, m2 = x[:, :n].mean(1), x[:, n:].mean(1)
    opp = (m1 * m2 < 0) & (np.abs(m1) > .2) & (np.abs(m2) > .2)
    return dict(G=G, s=s, p=float(opp.mean()))


def part_form(outdir, pool):
    S = [0, .002, .005, .01, .02, .03, .04, .05, .06, .08, .1, .12, .15, .18, .2, .25, .3]
    res = pool.map(form_job, [(G, s, 256, 150.0) for G in (2, 4, 8) for s in S])
    json.dump(res, open(os.path.join(outdir, "form.json"), "w"))
    ok = True
    print("Keep versus make: chance the blocks settle opposed, from a small random start, by s")
    for G in (2, 4, 8):
        g = sorted([r for r in res if r["G"] == G], key=lambda r: r["s"])
        xs, ps = [r["s"] for r in g], [r["p"] for r in g]
        sf = crossing(xs, ps, .25)
        early = min(p for x_, p in zip(xs, ps) if x_ <= .005)
        ok = ok and early >= .35 and sf < .5 * s_hold(G)
        print(f"  G {G}: " + ", ".join(f"{x_:.3f}: {p:.2f}" for x_, p in zip(xs, ps)) + f"; s_form {sf:.3f}; s_hold {s_hold(G):.3f}; ratio {sf / s_hold(G):.2f}")
    print(f"F8 {verdict(ok)}")


def part_noise(outdir, pool):
    jobs = [("limit", G, k, s, 0, .2, .05, False, SEEDS, 300.0) for G in (2, 4) for k in TOPS for s in S_GRID]
    res = run_jobs(pool, jobs, os.path.join(outdir, "noise.jsonl"), "noise")
    ok = True
    print("F9. Limit law, sigma .2. Absolute separation falling through half of complete's own value at s = 0, by interior; separation at s = 0 in brackets")
    for G in (2, 4):
        base = sorted([r for r in res if r["G"] == G and r["k"] == 6], key=lambda r: r["s"])[0]["sep"]
        vals = {}
        for k in TOPS:
            g = sorted([r for r in res if r["G"] == G and r["k"] == k], key=lambda r: r["s"])
            vals[k] = crossing([r["s"] for r in g], [r["sep"] / base for r in g], .5)
            print(f"  G {G}, {NAME[k]}: {vals[k]:.3f} [{g[0]['sep']:.3f}]")
        ok = ok and vals[1] <= .85 * vals[6]
    print(f"F9 {verdict(ok)}")


def part_doors(outdir, pool):
    S = [.02, .05, .08, .1, .12, .15, .18, .2, .25, .3, .35, .4, .5, .6, .7, .85, 1, 1.25, 1.5, 2, 3, 5, 8]
    jobs = [("limit", G, k, s, 4, .02, .05, False, SEEDS, 300.0) for G in (2, 4) for k in TOPS for s in S]
    res = run_jobs(pool, jobs, os.path.join(outdir, "doors.jsonl"), "doors")
    print("F10. Limit law, 4 of 12 doors. By interior: realised s where doors and other sites fall through half their start, and whole-block merge")
    tab = {}
    for G in (2, 4):
        for k in TOPS:
            g = sorted([r for r in res if r["G"] == G and r["k"] == k], key=lambda r: r["s"])
            xs = [r["s"] for r in g]
            d0, r0, s0 = g[0]["door"], g[0]["rest"], g[0]["sep"]
            d_ = crossing(xs, [r["door"] / d0 for r in g], .5)
            r_ = crossing(xs, [r["rest"] / r0 for r in g], .5)
            m_ = crossing(xs, [r["sep"] / s0 for r in g], .5)
            tab[(G, k)] = (d_, r_, m_)
            print(f"  G {G}, {NAME[k]}: doors {d_:.3f}, other sites {r_:.3f}, merge {m_:.3f}; start {d0:.2f} {r0:.2f}")
    a = all(tab[(G, 1)][0] <= .8 * tab[(G, 1)][1] for G in (2, 4))
    b = np.isfinite(tab[(2, 6)][1]) and abs(tab[(2, 6)][0] - tab[(2, 6)][1]) <= .1 * tab[(2, 6)][1]
    c = np.isfinite(tab[(2, 1)][2]) and np.isfinite(tab[(2, 6)][2]) and abs(tab[(2, 1)][2] - tab[(2, 6)][2]) >= .15 * min(tab[(2, 1)][2], tab[(2, 6)][2])
    print(f"F10 {verdict(a and b and c)}: ring tears {a}; complete does not at G = 2 {b}; merge differs at G = 2 {c}")


def settle(G, s, u1=0.0, x=None, T=800.0):
    """Mean-field-free deterministic run on the complete interior, identical sites. Returns block means and the state."""
    W, _, _ = network(6, s)
    n = N
    if x is None:
        x = np.r_[np.ones(n), -np.ones(n)]
    u = np.r_[np.full(n, u1), np.zeros(n)]
    dt = .05
    for _ in range(int(T / dt)):
        f1 = -x + np.tanh(G * (W @ x) + u)
        y = x + dt * f1
        x = x + dt / 2 * (f1 - y + np.tanh(G * (W @ y) + u))
    return x[:n].mean(), x[n:].mean(), x


def listen_job(job):
    G, frac = job
    s = frac * s_hold(G)
    m1, m2, x0 = settle(G, s)
    e = .002
    a1, a2, _ = settle(G, s, e, x0.copy(), 400.0)
    b1, b2, _ = settle(G, s, -e, x0.copy(), 400.0)
    self_g, cross = (a1 - b1) / (2 * e), (a2 - b2) / (2 * e)
    m = (m1 - m2) / 2
    a = 1 - m ** 2
    sg, ag = 1 / (1 - a * G), 1 / (1 - a * G * (1 - 2 * s))
    lo, hi = 0.0, 4.0
    for _ in range(14):
        mid = (lo + hi) / 2
        f1, _, _ = settle(G, s, -mid, x0.copy(), 400.0)
        if f1 < 0:
            hi = mid
        else:
            lo = mid
    return dict(G=G, frac=frac, s=s, m=float(m), self_g=float(self_g), cross=float(cross), self_a=float(a * .5 * (sg + ag)), cross_a=float(a * .5 * (sg - ag)), flip=float(hi), leak=float((x0 ** 2).mean()), pull=float((G * s * m) ** 2))


def part_listen(outdir, pool):
    fr = [0, .1, .3, .5, .7, .85, .95]
    res = pool.map(listen_job, [(G, f) for G in (2, 4) for f in fr])
    json.dump(res, open(os.path.join(outdir, "listen.json"), "w"))
    ok11, ok12, ok13 = True, True, True
    print("Listening. By fraction of s_hold: m; self gain (analytic); cross gain (analytic); flip input; leak power; squared pull")
    for G in (2, 4):
        g = sorted([r for r in res if r["G"] == G], key=lambda r: r["frac"])
        for r in g:
            print(f"  G {G}, {r['frac']:.2f}: m {r['m']:.3f}; self {r['self_g']:.3f} ({r['self_a']:.3f}); cross {r['cross']:.3f} ({r['cross_a']:.3f}); flip {r['flip']:.3f}; leak {r['leak']:.3f}; pull {r['pull']:.4f}")
        h = g[1:]
        ok11 = ok11 and all(abs(r["self_g"] - r["self_a"]) <= .1 * r["self_a"] and abs(r["cross"] - r["cross_a"]) <= .1 * r["cross_a"] for r in h)
        ok11 = ok11 and all(h[i]["cross"] < h[i + 1]["cross"] for i in range(len(h) - 1)) and h[-1]["cross"] > 5 * h[0]["cross"]
        want = {2: .533, 4: 2.147}[G]
        ok12 = ok12 and abs(g[0]["flip"] - want) <= .1 * want and all(g[i]["flip"] > g[i + 1]["flip"] for i in range(len(g) - 1)) and g[-1]["flip"] < .15 * g[0]["flip"]
        ok13 = ok13 and all(g[i]["leak"] > g[i + 1]["leak"] for i in range(len(g) - 1)) and all(g[i]["pull"] < g[i + 1]["pull"] for i in range(len(g) - 1))
    print(f"F11 {verdict(ok11)}; F12 {verdict(ok12)}; F13 {verdict(ok13)}")


def part_grid(path):
    b = [r for r in json.load(open(os.path.join(path, "belonging.json"))) if r["seed"] == 1]
    rho = lambda g, x_, y_: spearmanr([r[x_] for r in g], [r[y_] for r in g]).statistic
    hi = [r for r in b if r["b"] > r["x"]]
    lo = [r for r in b if r["x"] > r["b"]]
    print(f"Whole grid, {len(b)} cells: Spearman(a, c) {rho(b, 'a', 'c'):+.3f}; direct {rho(b, 'a_true', 'c_true'):+.3f}")
    print(f"b > x, {len(hi)} cells: {rho(hi, 'a', 'c'):+.3f}; direct {rho(hi, 'a_true', 'c_true'):+.3f}")
    print(f"x > b, {len(lo)} cells: {rho(lo, 'a', 'c'):+.3f}; direct {rho(lo, 'a_true', 'c_true'):+.3f}")
    print(f"F14 {verdict(rho(hi, 'a', 'c') < -.3 and rho(lo, 'a', 'c') > .3)}")


def part_after(outdir, pool):
    Gs = GAINS["limit"]
    fine = [("limit", G, k, float(f * s_hold(G)), 0, .02, .05, False, SEEDS, 300.0) for G in Gs for k in TOPS for f in np.r_[0, np.arange(.7, 1.16, .02)]]
    res = run_jobs(pool, fine, os.path.join(outdir, "fine.jsonl"), "fine")
    tab = {}
    for G in Gs:
        for k in TOPS:
            g = sorted([r for r in res if r["G"] == G and r["k"] == k], key=lambda r: r["s"])
            tab[(G, k)] = crossing([r["s"] for r in g], [r["sep"] / g[0]["sep"] for r in g], .5)
    print("Fine grid, limit law. Merge by interior, s_hold, error for complete")
    for G in Gs:
        print(f"  G {G}: " + ", ".join(f"{tab[(G, k)]:.4f}" for k in TOPS) + f"; s_hold {s_hold(G):.4f}; error {abs(tab[(G, 6)] - s_hold(G)) / s_hold(G):.3f}")
    print(f"P1 {verdict(all(abs(tab[(G, 6)] - s_hold(G)) <= .05 * s_hold(G) for G in Gs))}")
    rg = {G: (max(tab[(G, k)] for k in TOPS) - min(tab[(G, k)] for k in TOPS)) / min(tab[(G, k)] for k in TOPS) for G in Gs if G >= 2}
    print(f"P2 {verdict(max(rg.values()) < .05)}: range across interiors {[(G, round(v, 3)) for G, v in rg.items()]}")
    T_ = [.02, .05, .08, .1, .12, .15, .18, .2, .25, .3, .35, .4, .5, .6, .7, .85, 1, 1.25, 1.5, 2, 3, 5, 8, 20, 50]
    jobs = [("limit", 2, 1, s, 4, .02, .05, False, SEEDS, 300.0) for s in T_]
    jobs += [("limit", G, 6, s, d, .02, .05, False, SEEDS, 300.0) for G in (2, 3, 4, 8) for d in range(1, 12) for s in T_]
    res = run_jobs(pool, jobs, os.path.join(outdir, "doors_count.jsonl"), "doors count")
    ok3 = True
    print("P3. 4 doors, G = 2: realised s, door separation over start, mean door magnitude, other sites over start")
    for k in (1, 6):
        g = sorted([r for r in res if r["k"] == k and r["G"] == 2 and r["doors"] == 4], key=lambda r: r["s"])
        d0, r0 = g[0]["door"], g[0]["rest"]
        print(f"  {NAME[k]}: " + " | ".join(f"{r['s']:.3f}: {r['door'] / d0:.2f} {r['door_abs']:.2f} {r['rest'] / r0:.2f}" for r in g[::3]))
        ok3 = ok3 and all(r["door_abs"] < .3 for r in g if r["door"] / d0 < .5) and all(r["rest"] / r0 > .5 for r in g)
    print(f"P3 {verdict(ok3)}")
    ok4, ok5 = True, True
    print("P4. Lowest other-site separation over its start, by doors d; rule says holds if d/12 < 1 - 1/G, lost if d/12 >= 1 - 1/G + 1/12")
    for G in (2, 3, 4, 8):
        held, line = {}, []
        for d in range(1, 12):
            g = sorted([r for r in res if r["k"] == 6 and r["G"] == G and r["doors"] == d], key=lambda r: r["target"])
            base = g[0]["rest"]
            low = min(r["rest"] / base for r in g)
            held[d] = low > .5
            line.append(f"{d}: {low:.2f}")
            if G == 2 and d in (7, 8):
                print(f"    G 2, d {d}: other sites over start by realised s " + " | ".join(f"{r['s']:.3f}: {r['rest'] / base:.2f}" for r in g[::3]))
                ok5 = ok5 and low < .5 and g[-1]["rest"] / base > .5
        thr_hold = max((d for d in held if d / 12 < 1 - 1 / G), default=0)
        thr_lost = min((d for d in held if d / 12 >= 1 - 1 / G + 1 / 12), default=99)
        obs = min((d for d in held if not held[d]), default=99)
        ok4 = ok4 and (obs >= thr_hold) and (obs <= thr_lost + 1 or thr_lost == 99)
        print(f"  G {G}: " + ", ".join(line) + f"; first lost at d = {obs}; rule holds through {thr_hold}, lost from {thr_lost}")
    print(f"P4 {verdict(ok4)}; P5 {verdict(ok5)}")


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    parts = sys.argv[2:] or ["family", "release", "form", "noise", "doors", "listen"]
    with Pool(8, maxtasksperchild=200) as pool:
        for p in parts:
            if p == "family":
                part_family(outdir, pool)
            elif p == "release":
                part_release(outdir, pool)
            elif p == "form":
                part_form(outdir, pool)
            elif p == "noise":
                part_noise(outdir, pool)
            elif p == "doors":
                part_doors(outdir, pool)
            elif p == "listen":
                part_listen(outdir, pool)
            elif p.startswith("grid:"):
                part_grid(p[5:])
            elif p == "after":
                part_after(outdir, pool)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
