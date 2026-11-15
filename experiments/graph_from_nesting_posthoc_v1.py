"""Post hoc checks on graph_from_nesting_v1.py. Everything here was thought of AFTER seeing its results; predictions below were frozen before THIS script ran.

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. Record: plans/graph_from_nesting_2026_11_04.md
The predictions below stand as frozen. P1 and P2 passed. P3 missed at b=6 and P4 missed at beta=1.2; the record scores them.
The gaps part was added after P3 missed, to check the diagnosis: combination modes make the gap factor 1 - S_K, not 1 - r.

Needs numpy, scipy, and graph_from_nesting_v1.py with its two neighbours beside it.
Run: python graph_from_nesting_posthoc_v1.py NEST_OUTDIR [shapes finite holds longT tally]
A further part, gaps, is listed below P4. NEST_OUTDIR must hold the output of graph_from_nesting_v1.py; tally reads it. All data are synthetic.

WHY EACH CHECK EXISTS, AND WHAT I PREDICT.
P1 (shapes). N2's means passed, but blocks of up to 71 sites appeared, some of even size. Pair_up does not record shape.
   Fractional perfect matchings have pairs and odd cycles as their extreme points, so I expect long odd cycles.
   Prediction: pairs and odd cycles are at least 99% of blocks at every m; the rest are patterns unsettled at the 300-step limit.
P2 (finite). N4 missed: slow-mode crossings sat 20 to 37% above r*. r* assumes an infinite tower, but the towers tested had only
   K = 2 or 4 levels above the block. The finite form is q = r + r^2 + ... + r^K. It gives .742, .823, .758, .618 against measured
   A=1/2 crossings .741, .823, .759, .618. That match is close to arithmetic, since A is computed from outward share and block gap,
   so it is not evidence. The dynamical measure is the slow-mode crossing, which the finite form misses by at most 11% on those four.
   Prediction, on towers not yet seen: slow-mode crossing within 15% of the finite-form root in every new case, including the deep b=2
   towers (K >= 6), whose root is close to r* = 2/3.
P3 (holds). Mean field from (d) with q = b/(b-1) and level ratio r = b^(-2/3), the ratio that gives d_s = 3 under 2 ln b / ln(1/r):
   a = (1-r) q / (q + sum_{k=1..K} r^k). Prediction for WP.plane on products of K_b at that r: no accepted level for b = 2, 3, 4;
   at most one for b = 5; all L-1 interior levels for b >= 6. So levels that hold as wholes and d_s = 3 need blocks of at least 6.
P4 (longT). Most large runs had not converged at T=150, and gamma=1, beta=1.2 was the one FREE case above the N9 ceiling.
   Same seeds and blocks, T=600. Prediction at n=1024: beta=2 moves d_s by under .15 and diameter by under 15%, so the main result
   is not a transient. beta=1.2 falls below mean degree 4 and d_s 2.5, so its 2.7 is mostly a transient.

GAPS (added after P3 missed, so post hoc throughout). A product of K_b has modes that are nontrivial on several levels at once, with
eigenvalue q (t_a + t_b + ...). So the gap under the block with K levels above it is 1 - S_K, with S_K = r + ... + r^K, not 1 - r.
Corrected: a_K = (1 - S_K) q / (q + S_K), which exceeds 1/2 if and only if S_K < q / (2q + 1). In a deep tower this reads r < q / (3q + 1).
Check: the level count this gives against the plane's own count on every product row already measured.
"""
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("graph_from_nesting_v1", os.path.join(HERE, "graph_from_nesting_v1.py"))
N = importlib.util.module_from_spec(_s)
sys.modules["graph_from_nesting_v1"] = N
_s.loader.exec_module(N)
SUPPORT = N.SUPPORT


# ---------- P1 ----------
def shapes_job(job):
    m, beta0, noise, seed = job
    rng = np.random.default_rng([m, int(beta0 * 100), int(noise * 1000), seed, 5])
    Q, groups = N.pair_up(m, beta0, noise, rng)
    c = Counter()
    biggest_other = 0
    deg_other = 0
    for g in groups:
        k = len(g)
        if k == 1:
            c["single"] += 1
        elif k == 2:
            c["pair"] += 1
        else:
            d = (Q[np.ix_(g, g)] > SUPPORT).sum(1)
            if d.max() == 2 and d.min() == 2:
                c["odd cycle" if k % 2 else "even cycle"] += 1
            else:
                c["other odd size" if k % 2 else "other even size"] += 1
                biggest_other = max(biggest_other, k)
                deg_other = max(deg_other, int(d.max()))
    return dict(m=m, beta0=beta0, noise=noise, seed=seed, counts=dict(c), blocks=len(groups), biggest_other=biggest_other, deg_other=deg_other)


def part_shapes(outdir, pool):
    jobs = [(m, b, .05, s) for m in (64, 256, 1024) for b in (1.2, 2.0, 3.0) for s in range(8)] + [(2048, 2.0, .05, s) for s in range(4)]
    res = N.run_jobs(pool, shapes_job, jobs, outdir, "posthoc_shapes")
    print("P1. Block shapes, by m. Share of all blocks, then pairs plus odd cycles")
    for m in (64, 256, 1024, 2048):
        c = Counter()
        for r in res:
            if r["m"] == m:
                c.update(r["counts"])
        tot = sum(c.values())
        good = (c["pair"] + c["odd cycle"]) / tot
        print(f"  m={m}: {dict(c)}; pairs plus odd cycles {good:.4f}; largest non-cycle {max(r['biggest_other'] for r in res if r['m'] == m)}, its max degree {max(r['deg_other'] for r in res if r['m'] == m)}")


# ---------- P2 ----------
def finite_root(q, K):
    if K < q:
        return float("nan")
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if sum(mid ** k for k in range(1, K + 1)) < q:
            lo = mid
        else:
            hi = mid
    return lo


def part_finite(outdir, pool):
    cases = [(2, "complete", 10, 1), (2, "complete", 10, 2), (2, "complete", 10, 3), (2, "complete", 10, 5), (2, "complete", 10, 6),
             (3, "complete", 6, 0), (3, "complete", 6, 1), (3, "complete", 6, 2), (4, "complete", 5, 0), (4, "complete", 5, 1),
             (4, "ring", 5, 0), (4, "ring", 5, 1), (5, "complete", 4, 0), (5, "complete", 4, 1)]
    rs = [round(x, 3) for x in np.arange(.30, .97, .02)]
    jobs = [(b, p, L, lv, r) for b, p, L, lv in cases for r in rs]
    res = N.run_jobs(pool, N.capacity_job, jobs, outdir, "posthoc_finite", ordered=True)
    print("P2. Slow-mode crossing against the finite-tower root q = r + ... + r^K, on towers not used before")
    i = 0
    ok = 0
    n = 0
    for b, p, L, lv in cases:
        rows = res[i:i + len(rs)]
        i += len(rs)
        K = L - 1 - lv
        q = 1.0 if p == "ring" else b / (b - 1)
        root = finite_root(q, K)
        rstar = q / (1 + q)
        rr = np.array([x["r"] for x in rows])
        ratio = np.array([x["r_mix"] / x["r_esc"] if x["r_esc"] and x["r_esc"] > 0 else np.nan for x in rows])
        cd = float("nan")
        for j in range(len(rr) - 1):
            if np.isfinite(ratio[j]) and np.isfinite(ratio[j + 1]) and (ratio[j] - 1) * (ratio[j + 1] - 1) <= 0:
                cd = float(rr[j] + (1 - ratio[j]) * (rr[j + 1] - rr[j]) / (ratio[j + 1] - ratio[j]))
                break
        err = cd / root - 1
        n += 1
        ok += abs(err) <= .15
        print(f"  b={b} {p} L={L} level={lv} K={K}: finite root {root:.3f}, infinite r* {rstar:.3f}, slow-mode crossing {cd:.3f}; against finite {100 * err:+.1f}%, against infinite {100 * (cd / rstar - 1):+.1f}%")
    print(f"  within 15% of the finite root: {ok} of {n}")


# ---------- P3 ----------
def holds_job(job):
    b, L = job
    r = b ** (-2 / 3)
    out = N.geom(N.product(b, L, r), 1, do_plane=True)
    q = b / (b - 1)
    pred = [round((1 - r) * q / (q + sum(r ** k for k in range(1, K + 1))), 3) for K in range(1, L)]
    return dict(b=b, L=L, r=r, n=b ** L, levels=out.get("levels"), level_ac=out.get("level_ac"), best_ac=out.get("best_ac"), ds_weyl=out.get("ds_weyl"), d_spectral=out.get("d_spectral"), pred_a=pred)


def part_holds(outdir, pool):
    res = N.run_jobs(pool, holds_job, [(2, 10), (3, 6), (4, 5), (5, 4), (6, 4), (7, 3), (8, 3)], outdir, "posthoc_holds", ordered=True)
    print("P3. Products of K_b at r = b^(-2/3), the ratio aimed at d_s = 3. Interior levels are L-1")
    for x in res:
        print(f"  b={x['b']} L={x['L']} n={x['n']} r={x['r']:.3f}: accepted {x['levels']} of {x['L'] - 1}; (k,a,c) {[(k, round(a, 3), round(c, 3)) for k, a, c in (x['level_ac'] or [])]}; mean-field a by K {x['pred_a']}; d_s weyl {x['ds_weyl']:.2f}, ret {x['d_spectral']:.2f}")


# ---------- P4 ----------
def part_longT(outdir, pool):
    jobs = [("free", 1.0, be, .3, 0, 2.0, .05, n, s, 600) for be in (2.0, 1.2) for n in (256, 512, 1024) for s in range(4)]
    res = N.run_jobs(pool, N.grow_job, jobs, outdir, "posthoc_longT")
    base = [json.loads(x) for x in open(os.path.join(outdir, "grow.jsonl"))]
    print("P4. Same seeds, T=150 against T=600")
    for be in (2.0, 1.2):
        for n in (256, 512, 1024):
            for tag, rows in (("T=150", [x for x in base if x["mode"] == "free" and x["gamma"] == 1.0 and x["beta"] == be and x["t0"] == .3 and x["beta0"] == 2.0 and x["n"] == n and x["seed"] < 4]),
                              ("T=600", [x for x in res if x["beta"] == be and x["n"] == n])):
                f = lambda k: float(np.nanmean([x[k] for x in rows]))
                print(f"  beta={be} n={n} {tag}: conn {np.mean([x['connected'] for x in rows]):.2f} deg {f('mean_degree'):.2f} diam {f('diameter'):.1f} d_s weyl {f('ds_weyl'):.2f} ret {f('d_spectral'):.2f} growth {f('d_growth'):.2f} lam2 {f('lambda2'):.2e} conv {np.mean([x['top_conv'] for x in rows]):.2f}")


# ---------- Gaps ----------
def a_K(b, r, K):
    q = b / (b - 1)
    S = sum(r ** k for k in range(1, K + 1))
    return (1 - S) * q / (q + S)


def part_gaps(outdir):
    print("GAPS. The plane's gap factor and a on true blocks, against 1 - S_K and the corrected a_K")
    for b, L in ((5, 4), (6, 4), (7, 3), (8, 3)):
        r = b ** (-2 / 3)
        rows, _ = N.WP.level_table(N.product(b, L, r))
        by_k = {x["k"]: x for x in rows}
        for K in range(1, L):
            k = b ** K
            x = by_k.get(k)
            print(f"  b={b} L={L} r={r:.3f} K={K}, k={k}: plane g {x['g'] if x else float('nan'):.3f}, 1-S_K {1 - sum(r ** j for j in range(1, K + 1)):.3f}; plane a {x['a'] if x else float('nan'):.3f}, a_K {a_K(b, r, K):.3f}")
    st = [json.loads(x) for x in open(os.path.join(outdir, "static.jsonl"))]
    st = [x for x in st if x["kind"] == "product" and x.get("levels") is not None]
    st += [json.loads(x) | {"kind": "product"} for x in open(os.path.join(outdir, "posthoc_holds.jsonl"))]
    right = 0
    print("  Level counts, corrected form against the plane; the plane only examines its six largest gaps, so counts are capped at 6")
    for x in st:
        pred = sum(a_K(x["b"], x["r"], K) > .5 for K in range(1, x["L"]))
        ties = [K for K in range(1, x["L"]) if abs(a_K(x["b"], x["r"], K) - .5) < 1e-6]
        ok = min(pred, 6) == x["levels"] or bool(ties)
        right += ok
        print(f"    b={x['b']} L={x['L']} r={x['r']:.3f}: corrected {pred}, plane {x['levels']}" + (" (exact tie at a = 1/2)" if ties else "") + ("" if ok else "  MISS"))
    print(f"  agree: {right} of {len(st)}")
    print("  Largest d_s with every level held in a deep tower, r = q/(3q+1), d_s = 2 ln b / ln(1/r):")
    for b in (2, 3, 4, 5, 6, 7, 8, 9, 16):
        q = b / (b - 1)
        rc = q / (3 * q + 1)
        print(f"    b={b}: r {rc:.3f}, d_s {2 * np.log(b) / np.log(1 / rc):.2f}")


# ---------- Tally of the frozen predictions from saved output ----------
def part_tally(outdir):
    res = json.load(open(os.path.join(outdir, "formula.json")))
    inside, miss = 0, []
    for g in (.5, 1., 1.5, 2.):
        for be in (1.2, 1.5, 2., 3.):
            if 1 - be * (1 - g) <= 0:
                continue
            pred = 2 * (1 / be - 1 + g)
            for b in (2, 3, 4):
                x = [y for y in res if y["gamma"] == g and y["beta"] == be and y["b"] == b and y["seed"] == 0][0]
                e = x["ds_from_r"] / pred - 1 if x["ds_from_r"] and np.isfinite(x["ds_from_r"]) else float("nan")
                inside += abs(e) <= .10
                if not abs(e) <= .10:
                    miss.append((g, be, b, round(100 * e, 1)))
    print(f"N3: within 10%: {inside} of {inside + len(miss)}; misses (gamma, beta, b, %): {miss}")
    st = [json.loads(x) for x in open(os.path.join(outdir, "static.jsonl"))]
    h = [x for x in st if x["kind"] in ("product", "spread") and x["r"] <= .6]
    bad = []
    for x in h:
        pred = 2 * np.log(x["b"]) / np.log(1 / x["r"])
        ew, er = x["ds_weyl"] / pred - 1, x["d_spectral"] / pred - 1
        if abs(ew) > .10:
            bad.append((x["kind"], x["b"], x["L"], x["r"], round(100 * ew, 1), round(100 * er, 1)))
    print(f"N5 d_s: within 10% on the Weyl fit: {len(h) - len(bad)} of {len(h)}; misses (kind, b, L, r, weyl %, ret %): {bad}")
    m5 = [x for x in h if x["r"] <= .5]
    print(f"N5 midpoint >= .8 for r <= .5: {sum(x['midpoint'] >= .8 for x in m5)} of {len(m5)}; product only {sum(x['midpoint'] >= .8 for x in m5 if x['kind'] == 'product')} of {sum(x['kind'] == 'product' for x in m5)}")
    print(f"N5 hop diameter <= L+1: {sum(x['diameter'] <= x['L'] + 1 for x in st if x['kind'] == 'product')} of {sum(x['kind'] == 'product' for x in st)}")
    de = [json.loads(x) for x in open(os.path.join(outdir, "dense.jsonl"))]
    keys = sorted({(x["b"], x["L"], x["gamma"], x["beta"]) for x in de})
    a, d_ = 0, 0
    print("N6, and end-state d_s against the symmetric formula 2(1/beta - 1 + gamma):")
    for k in keys:
        g = [x for x in de if (x["b"], x["L"], x["gamma"], x["beta"]) == k]
        f = float(np.mean([x["spread1"] / x["spread0"] for x in g]))
        dg = float(np.mean([x["mean_degree"] for x in g]))
        ds = float(np.nanmean([x["ds_weyl"] for x in g]))
        pred = 2 * (1 / k[3] - 1 + k[2])
        a += f >= 10
        d_ += dg < k[1] / 2
        print(f"  b={k[0]} L={k[1]} gamma={k[2]} beta={k[3]}: spread grows x{f:.1f}; degree {dg:.2f} against L/2 = {k[1] / 2}; d_s {ds:.2f}, symmetric {pred:.2f}, ratio {ds / pred:.2f}; converged {np.mean([x['converged'] for x in g]):.2f}")
    print(f"  spread at least x10: {a} of {len(keys)}; degree under L/2: {d_} of {len(keys)}")
    rows = [json.loads(x) for x in open(os.path.join(outdir, "grow.jsonl"))]
    base = [json.loads(x) for x in open(os.path.join(outdir, "baseline.jsonl"))]
    sizes = (32, 64, 128, 256, 512, 1024)
    sib = [x for x in rows if x["mode"] == "free" and x["gamma"] == 1.0 and x["beta"] == 2.0]
    main = [x for x in sib if x["t0"] == .3 and x["beta0"] == 2.0]
    print("N7 main config, diameter by seed at n=1024:", [x["diameter"] for x in main if x["n"] == 1024], "; at 512:", [x["diameter"] for x in main if x["n"] == 512])
    print("N7 pooled over the four gamma=1, beta=2 configurations (post hoc):", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in (N.holdout(sib, sizes) or {}).items()})
    print("Per n, pooled: n diameter lam2 growth d_s_weyl d_s_ret; baseline beside it")
    for n in sizes:
        f = lambda rs, k: float(np.nanmean([x[k] for x in rs if x["n"] == n and k in x and x[k] is not None]))
        print(f"  n={n}: nested {f(sib, 'diameter'):.1f} {f(sib, 'lambda2'):.2e} {f(sib, 'd_growth'):.2f} {f(sib, 'ds_weyl'):.2f} {f(sib, 'd_spectral'):.2f} | baseline {f(base, 'diameter'):.1f} {f(base, 'lambda2'):.2e} {f(base, 'd_growth'):.2f} {f(base, 'ds_weyl'):.2f} {f(base, 'd_spectral'):.2f}")
    def slope(rs, k, a_=256, b_=1024):
        va = np.nanmean([x[k] for x in rs if x["n"] == a_])
        vb = np.nanmean([x[k] for x in rs if x["n"] == b_])
        return float(np.log(vb / va) / np.log(b_ / a_))
    print("Slopes from n=256 to 1024 (log-log), with the largest-n readings. Config: diameter, lam2; d_s weyl, ret, deg")
    print(f"  baseline: diam {slope(base, 'diameter'):.2f}, lam2 {slope(base, 'lambda2'):.2f}")
    cfgs = sorted({(x["mode"], x["gamma"], x["beta"], x["t0"], x["r"], x["beta0"]) for x in rows})
    for c in cfgs:
        g = [x for x in rows if (x["mode"], x["gamma"], x["beta"], x["t0"], x["r"], x["beta0"]) == c]
        big = [x for x in g if x["n"] == 1024]
        if not any(x.get("connected") for x in big):
            print(f"  {c}: disconnected at n=1024 in every run")
            continue
        kap = []
        lv = defaultdict(list)
        for x in big:
            for t in x["table"]:
                lv[t["level"]].append(t["edges_per_site"])
        v = [np.mean(lv[l]) for l in sorted(lv)]
        if len(v) >= 6:
            kap = float(-np.polyfit(np.arange(2, 7), np.log2(np.maximum(v[2:7], 1e-9)), 1)[0])
        print(f"  {c}: diam {slope(g, 'diameter'):.2f}, lam2 {slope(g, 'lambda2'):.2f}; d_s {np.nanmean([x['ds_weyl'] for x in big]):.2f}, {np.nanmean([x['d_spectral'] for x in big]):.2f}; deg {np.nanmean([x['mean_degree'] for x in big]):.2f}; kappa over levels 2 to 6 {kap if kap else float('nan'):.2f}")


def main():
    outdir = sys.argv[1]
    parts = sys.argv[2:] or ["shapes", "finite", "holds", "longT", "tally"]
    with Pool(16) as pool:
        for p in parts:
            if p == "shapes":
                part_shapes(outdir, pool)
            elif p == "finite":
                part_finite(outdir, pool)
            elif p == "holds":
                part_holds(outdir, pool)
            elif p == "longT":
                part_longT(outdir, pool)
            elif p == "gaps":
                part_gaps(outdir)
            elif p == "tally":
                part_tally(outdir)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
