"""First real data for "A Theory of Wholeness". Predictions frozen in plans/real_data_predictions_2026_11_05.md before any file was downloaded.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial.
Results: R1 to R6 passed; R4 narrowly, with intervals starting at +.04 and +.06. R7 not run: D3 has no fusion score. Post hoc: corners +.30, +.04, -.04, -.37 at median splits, interaction +.008, and fusion plus cutoff explain 7% of well-being. E1: fusion with regulation difficulty +.35 controlling I-position; with I-position -.02 controlling regulation.

Needs numpy, pandas, pyreadstat. Raw files are not in the repository; pass their folder.
Run: python -I wholeness_real_data_v1.py DATADIR [posthoc]
DATADIR holds d1/x/ECR-data-1March2018/data.csv and d2/WBsokmencurun.sav.

SCORING, fixed after reading labels and codebooks and before computing any relation between constructs.
D1 (ECR). Five-point items, the codebook says -1 for missed and the file uses 0, so anything outside 1 to 5 is missing, and only people answering every item are kept. Odd items are avoidance and even items anxiety; Q3, 15, 19, 25, 27, 29, 31, 33, 35 and Q22 are reversed, confirmed against the wording. In a corner, high means above the median or above the scale midpoint 3, and low means at or below it.
D2 (DSI-R, Turkish 20 items). In the file EC + ER + IP + F equals the labelled differentiation total in all 351 rows. A higher DSI-R total is published as more differentiated, so all four stored subscales must run toward differentiation. So fusion = -F and cutoff = -EC. I did not retrieve the Turkish scoring manual, so this rests on that arithmetic and the published direction of the total.
D3. Dropped for R7, not analysed. Its items carry no labels, and the instrument's own validation (Gallego and colleagues, 2023) reports only two factors, reactivity and cutoff, so there is no fusion score to test.
R6 reads "after fusion + cutoff" as both entered separately. The version with only their sum is printed as well.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import pyreadstat

B = 2000
sys.stdout.reconfigure(encoding="utf-8")


def z(s):
    return (s - s.mean()) / s.std(ddof=1)


def alpha(M):
    k = M.shape[1]
    return float(k / (k - 1) * (1 - M.var(axis=0, ddof=1).sum() / M.sum(axis=1).var(ddof=1)))


def ci(v):
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def r1(path):
    df = pd.read_csv(path, sep=None, engine="python")
    q = [f"Q{i}" for i in range(1, 37)]
    X = df[q].where((df[q] >= 1) & (df[q] <= 5))
    keep = X.notna().all(axis=1)
    X = X[keep].copy()
    for i in (3, 15, 19, 25, 27, 29, 31, 33, 35, 22):
        X[f"Q{i}"] = 6 - X[f"Q{i}"]
    av = X[[f"Q{i}" for i in range(1, 37, 2)]]
    an = X[[f"Q{i}" for i in range(2, 37, 2)]]
    A, V = an.mean(axis=1).values, av.mean(axis=1).values
    r = float(np.corrcoef(A, V)[0, 1])
    rng = np.random.default_rng(1)
    boots = [np.corrcoef(A[idx], V[idx])[0, 1] for idx in (rng.integers(0, len(A), len(A)) for _ in range(500))]

    def corners(ta, tv):
        return dict(secure=float(((A <= ta) & (V <= tv)).mean()), anxious=float(((A > ta) & (V <= tv)).mean()), avoidant=float(((A <= ta) & (V > tv)).mean()), both=float(((A > ta) & (V > tv)).mean()))

    med = corners(np.median(A), np.median(V))
    mid = corners(3, 3)
    print(f"R1. {len(df)} rows, {len(A)} complete. alpha anxiety {alpha(an.values):.3f}, avoidance {alpha(av.values):.3f}. Means {A.mean():.2f}, {V.mean():.2f}")
    print(f"  r(anxiety, avoidance) {r:+.3f}, CI {ci(boots)[0]:+.3f} to {ci(boots)[1]:+.3f}")
    print("  Corners at the median:", {k: round(v, 3) for k, v in med.items()})
    print("  Corners at the midpoint:", {k: round(v, 3) for k, v in mid.items()})
    ok = -.1 <= r <= .4 and min(med.values()) >= .10 and min(mid.values()) >= .05
    bad = abs(r) > .5 or min(med.values()) < .05 or min(mid.values()) < .05
    print("  R1", "PASS" if ok else ("FAIL" if bad else "NEITHER"))
    return dict(n=len(A), r=r, med=med, mid=mid, verdict="PASS" if ok else ("FAIL" if bad else "NEITHER"))


def fit_r2(y, X):
    Xc = np.c_[np.ones(len(y)), X]
    b, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    res = y - Xc @ b
    return b, 1 - res.var() / y.var()


def partial(a, b, c):
    ra = a - np.polyval(np.polyfit(c, a, 1), c)
    rb = b - np.polyval(np.polyfit(c, b, 1), c)
    return float(np.corrcoef(ra, rb)[0, 1])


def d2(path):
    df, _ = pyreadstat.read_sav(path)
    Fu, Cu = (-df.F).values.astype(float), (-df.EC).values.astype(float)
    wb = ((z(df.FS) + z(df.SPANEB)) / 2).values
    wb = wb / wb.std(ddof=1)
    n = len(df)
    rng = np.random.default_rng(2)
    idxs = [rng.integers(0, n, n) for _ in range(B)]
    out = {}

    r = float(np.corrcoef(Fu, Cu)[0, 1])
    rb = [np.corrcoef(Fu[i], Cu[i])[0, 1] for i in idxs]
    hh = float(((Fu > np.median(Fu)) & (Cu > np.median(Cu))).mean())
    v = "PASS" if (r >= -.1 and hh >= .15) else ("FAIL" if r <= -.3 else "NEITHER")
    print(f"R2. n {n}. r(fusion, cutoff) {r:+.3f}, CI {ci(rb)[0]:+.3f} to {ci(rb)[1]:+.3f}; high-high share at medians {hh:.3f}. {v}")
    print(f"  Scores as stored: F mean {df.F.mean():.1f}, EC mean {df.EC.mean():.1f}; r(fusion, well-being) {np.corrcoef(Fu, wb)[0, 1]:+.3f}; r(cutoff, well-being) {np.corrcoef(Cu, wb)[0, 1]:+.3f}")
    out["R2"] = dict(r=r, ci=ci(rb), hh=hh, verdict=v)

    def tert(x):
        a, b = np.percentile(x, 100 / 3), np.percentile(x, 200 / 3)
        return np.where(x <= a, 0, np.where(x > b, 2, 1))

    tf, tc = tert(Fu), tert(Cu)
    names = ("low", "mid", "high")
    cell = lambda f, c: (tf == f) & (tc == c)
    print("  Well-being by tertile cell, SD units; rows fusion, columns cutoff; n in brackets")
    means = np.zeros((3, 3))
    for f in range(3):
        for c in range(3):
            means[f, c] = wb[cell(f, c)].mean() if cell(f, c).any() else np.nan
        print(f"    fusion {names[f]:4s}: " + "  ".join(f"{means[f, c]:+.2f} [{int(cell(f, c).sum())}]" for c in range(3)))

    def boot_diff(a, b):
        v_ = []
        for i in idxs:
            ta, tb = tf[i], tc[i]
            w = wb[i]
            xa, xb = w[(ta == a[0]) & (tb == a[1])], w[(ta == b[0]) & (tb == b[1])]
            v_.append(xa.mean() - xb.mean() if len(xa) and len(xb) else np.nan)
        v_ = np.array(v_)
        return float(np.nanpercentile(v_, 2.5)), float(np.nanpercentile(v_, 97.5))

    best = np.unravel_index(np.nanargmax(means), means.shape)
    d = float(means[0, 0] - means[1, 1])
    c_ = boot_diff((0, 0), (1, 1))
    if best == (0, 0):
        v = "PASS" if d >= .3 and c_[0] > 0 else "NEITHER"
    else:
        cc = boot_diff(best, (0, 0))
        v = "FAIL" if cc[0] > 0 else "NEITHER"
        print(f"  Best cell is fusion {names[best[0]]}, cutoff {names[best[1]]}; above low-low by {means[best] - means[0, 0]:+.2f}, CI {cc[0]:+.2f} to {cc[1]:+.2f}")
    print(f"R3. Low-low minus middle {d:+.2f} SD, CI {c_[0]:+.2f} to {c_[1]:+.2f}. {v}")
    out["R3"] = dict(means=means.tolist(), d=d, ci=c_, best=[int(best[0]), int(best[1])], verdict=v)

    corners = {"low-low": (0, 0), "fusion only": (2, 0), "cutoff only": (0, 2), "both": (2, 2)}
    print("R4. Corners: " + ", ".join(f"{k} {means[v_]:+.2f}" for k, v_ in corners.items()))
    d1, d2_ = float(means[0, 2] - means[2, 2]), float(means[2, 0] - means[2, 2])
    c1, c2 = boot_diff((0, 2), (2, 2)), boot_diff((2, 0), (2, 2))
    print(f"  Cutoff only minus both {d1:+.2f}, CI {c1[0]:+.2f} to {c1[1]:+.2f}; fusion only minus both {d2_:+.2f}, CI {c2[0]:+.2f} to {c2[1]:+.2f}")
    low = min(corners, key=lambda k: means[corners[k]])
    if low == "both":
        v = "PASS" if d1 >= .2 and d2_ >= .2 else "NEITHER"
    else:
        cc = boot_diff((2, 2), corners[low])
        v = "FAIL" if cc[0] > 0 else "NEITHER"
        print(f"  Lowest corner is {low}; both minus it {means[2, 2] - means[corners[low]]:+.2f}, CI {cc[0]:+.2f} to {cc[1]:+.2f}")
    print(f"  R4 {v}")
    out["R4"] = dict(d1=d1, d2=d2_, c1=c1, c2=c2, lowest=low, verdict=v)

    zF, zC = z(pd.Series(Fu)).values, z(pd.Series(Cu)).values
    X = np.c_[zF, zC]
    b, R2 = fit_r2(wb, X)
    bs = np.array([fit_r2(wb[i], X[i])[0][1:] for i in idxs])
    cF, cC = ci(bs[:, 0]), ci(bs[:, 1])
    ok = (cF[0] > 0 or cF[1] < 0) and (cC[0] > 0 or cC[1] < 0)
    print(f"R5. Model R2 {R2:.3f}. Fusion beta {b[1]:+.3f}, CI {cF[0]:+.3f} to {cF[1]:+.3f}; cutoff beta {b[2]:+.3f}, CI {cC[0]:+.3f} to {cC[1]:+.3f}. {'PASS' if ok else 'FAIL'}")
    out["R5"] = dict(R2=R2, fusion=[float(b[1]), cF], cutoff=[float(b[2]), cC], verdict="PASS" if ok else "FAIL")

    dd = Cu - Fu
    ad = np.abs(dd - dd.mean())
    base = fit_r2(wb, X)[1]
    full = fit_r2(wb, np.c_[X, ad])[1]
    sbase = fit_r2(wb, (Fu + Cu)[:, None])[1]
    sfull = fit_r2(wb, np.c_[Fu + Cu, ad])[1]
    add = full - base
    v = "PASS" if add <= .02 else ("FAIL" if add > .05 else "NEITHER")
    print(f"R6. |d| adds {add:.4f} of R2 after both; {sfull - sbase:.4f} after their sum alone. {v}")
    out["R6"] = dict(add=add, add_sum=sfull - sbase, verdict=v)

    pip = partial(Fu, df.IP.values.astype(float), df.DERS16total.values.astype(float))
    pder = partial(Fu, df.DERS16total.values.astype(float), df.IP.values.astype(float))
    print(f"E1. Fusion with I-position, controlling emotion-regulation difficulty {pip:+.3f}; fusion with emotion-regulation difficulty, controlling I-position {pder:+.3f}. Plain: {np.corrcoef(Fu, df.IP)[0, 1]:+.3f}, {np.corrcoef(Fu, df.DERS16total)[0, 1]:+.3f}")
    out["E1"] = dict(p_ip=pip, p_ders=pder)
    return out


def posthoc(path):
    """Not frozen. Run after seeing R1 to R6, to check how much the passes depend on small cells."""
    df, _ = pyreadstat.read_sav(path)
    Fu, Cu = (-df.F).values.astype(float), (-df.EC).values.astype(float)
    wb = ((z(df.FS) + z(df.SPANEB)) / 2).values
    wb = wb / wb.std(ddof=1)
    n = len(df)
    rng = np.random.default_rng(3)
    idxs = [rng.integers(0, n, n) for _ in range(B)]
    hf, hc = Fu > np.median(Fu), Cu > np.median(Cu)
    lab = {"neither": (~hf) & (~hc), "fusion only": hf & (~hc), "cutoff only": (~hf) & hc, "both": hf & hc}
    print("POST HOC. Median-split corners, larger cells than the tertile grid")
    for k, m in lab.items():
        print(f"  {k}: {wb[m].mean():+.2f} SD, n {int(m.sum())}")

    def diff(a, b):
        v = []
        for i in idxs:
            w = wb[i]
            v.append(w[lab[a][i]].mean() - w[lab[b][i]].mean())
        return float(np.mean(v)), ci(v)

    for a, b in (("neither", "both"), ("neither", "fusion only"), ("neither", "cutoff only"), ("fusion only", "both"), ("cutoff only", "both")):
        m, c = diff(a, b)
        print(f"  {a} minus {b}: {m:+.2f}, CI {c[0]:+.2f} to {c[1]:+.2f}")
    zF, zC = z(pd.Series(Fu)).values, z(pd.Series(Cu)).values
    X = np.c_[zF, zC, zF * zC]
    b, R = fit_r2(wb, X)
    bs = np.array([fit_r2(wb[i], X[i])[0][1:] for i in idxs])
    print(f"  Interaction fusion by cutoff: beta {b[3]:+.3f}, CI {ci(bs[:, 2])[0]:+.3f} to {ci(bs[:, 2])[1]:+.3f}; model R2 {R:.3f}")
    for name, y in (("Flourishing", z(df.FS).values), ("SPANE balance", z(df.SPANEB).values)):
        bb, RR = fit_r2(y, np.c_[zF, zC])
        print(f"  {name} alone: fusion {bb[1]:+.3f}, cutoff {bb[2]:+.3f}, R2 {RR:.3f}")
    for name, col in (("I-position", "IP"), ("reactivity", "ER")):
        print(f"  r(fusion, {name} as stored) {np.corrcoef(Fu, df[col])[0, 1]:+.3f}; r(cutoff, same) {np.corrcoef(Cu, df[col])[0, 1]:+.3f}")
    print(f"  r(fusion, regulation difficulty) {np.corrcoef(Fu, df.DERS16total)[0, 1]:+.3f}; r(cutoff, same) {np.corrcoef(Cu, df.DERS16total)[0, 1]:+.3f}; r(fusion, self-control) {np.corrcoef(Fu, df.BSCStotal)[0, 1]:+.3f}; r(cutoff, self-control) {np.corrcoef(Cu, df.BSCStotal)[0, 1]:+.3f}")


def main():
    root = sys.argv[1]
    if "posthoc" in sys.argv[2:]:
        posthoc(os.path.join(root, "d2", "WBsokmencurun.sav"))
        return
    res = dict(R1=r1(os.path.join(root, "d1", "x", "ECR-data-1March2018", "data.csv")))
    res.update(d2(os.path.join(root, "d2", "WBsokmencurun.sav")))
    print("R7. Dropped: no fusion score in D3.")
    json.dump(res, open(os.path.join(root, "results.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
