"""Precondition check for the projection x architecture confirmatory run.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Tests failure mode 4 (do the families generate
  different V_pi?) and the difficulty-matching requirement, before the
  expensive confirmatory run. Result: V_pi separates decisively but the
  families do not overlap in difficulty at all, so the two-family contrast
  is unidentifiable. A within-family design is visible in the same data.

Companion findings: pole_gap_vpi_precondition_findings_v1.md
Run: py -3.11 experiments/pole_gap_vpi_precondition_v1.py   (~4 min)
"""
"""Precondition check for the projection x architecture experiment.

Failure mode 4 in the protocol: "projection families do not generate different
V_pi distributions." That one is cheap to test and it gates everything else,
so it goes first. No CTW, no architecture comparison, calibration data only.

Setup matches the protocol: observer sees O_t = pi_o(X_t), predicts
Y_{t+1} = centre cell at the next step. Two projections, one target.

V_pi = sum_c P(c) [ l(c) - lbar ]^2, where l(c) is the shortest suffix depth
whose predictive distribution is already within eps of the deepest estimate.
"""
import numpy as np
import math

W_LIST = [101, 151]
N = 60_000
BURN = 500
D = 12
EPS = 0.02
MINCOUNT = 20
rng = np.random.default_rng(30)


def evolve(W, n, seed):
    r = np.random.default_rng(seed).integers(0, 2, W, dtype=np.uint8)
    out = np.empty((n, W), dtype=np.uint8)
    for t in range(n):
        out[t] = r
        L = np.roll(r, 1); R = np.roll(r, -1)
        r = (L ^ (r | R)).astype(np.uint8)
    return out


# ---- prospective projection bank, built by rule before any results ----------
def build_bank(W):
    c = W // 2
    agg, alg = [], []

    def cells(idxs):
        return [(i) % W for i in idxs]

    # aggregating: majority of r consecutive
    for r in (3, 5, 7, 9):
        idx = cells(range(c-r//2, c+r//2+1))
        agg.append((f"maj{r}", idx, "thr", r//2 + 1))
    # aggregating: density over r with two thresholds
    for r in (5, 7, 9, 11):
        idx = cells(range(c-r//2, c+r//2+1))
        for th in (r//2, r//2 + 1):
            agg.append((f"den{r}>{th}", idx, "thr", th + 1))
    # aggregating: majority over separated triple
    for d in (2, 3, 4, 5):
        idx = cells([c-d, c, c+d])
        agg.append((f"majsep{d}", idx, "thr", 2))
    # aggregating: wide block count in upper half
    for off in (0, 2, 4, 6):
        idx = cells(range(c-3+off, c+4+off))
        agg.append((f"blk7off{off}", idx, "thr", 4))

    # algebraic: xor of r consecutive
    for r in (3, 5, 7, 9):
        idx = cells(range(c-r//2, c+r//2+1))
        alg.append((f"xor{r}", idx, "xor", 0))
    # algebraic: xor of two separated
    for d in (2, 3, 5, 7):
        alg.append((f"xor2d{d}", cells([c, c+d]), "xor", 0))
    # algebraic: xor of separated triple
    for d in (2, 3, 4, 5):
        alg.append((f"xor3d{d}", cells([c-d, c, c+d]), "xor", 0))
    # algebraic: mod-2 linear on strided masks
    for s in (2, 3, 4, 5):
        idx = cells(range(c-6, c+7, s))
        alg.append((f"stride{s}", idx, "xor", 0))
    # algebraic: local difference at lag d
    for d in (1, 2, 4, 8):
        alg.append((f"diff{d}", cells([c, c+d]), "xor", 0))

    return agg[:20], alg[:20]


def project(rows, spec):
    _, idx, kind, thr = spec
    sub = rows[:, idx]
    if kind == "xor":
        return np.bitwise_xor.reduce(sub, axis=1).astype(np.uint8)
    return (sub.sum(axis=1) >= thr).astype(np.uint8)


def context_stats(O, Y, D):
    """counts[d][ctx*2+y] over the calibration stream."""
    n = len(O) - 1
    o = O[:n].astype(np.int64)
    y = Y[1:n+1].astype(np.int64)
    ctx = np.zeros(n, dtype=np.int64)
    tables = []
    for d in range(D+1):
        if d > 0:
            prev = np.zeros(n, dtype=np.int64)
            prev[d:] = o[:n-d]
            ctx = ctx + (prev << (d-1))
        valid = slice(D, n)
        key = (ctx[valid] << 1) | y[valid]
        tables.append(np.bincount(key, minlength=(1 << (d+1))))
    return tables


def V_and_difficulty(O, Y, D):
    T = context_stats(O, Y, D)

    def p_at(d, c):
        t = T[d]
        i = c << 1
        n0, n1 = t[i], t[i+1]
        return (n1 + 0.5)/(n0 + n1 + 1.0), n0 + n1

    deep = T[D]
    tot = deep.sum()
    if tot == 0:
        return 0.0, 1.0, 0.5
    ells, weights = [], []
    H = 0.0
    for c in range(1 << D):
        n0, n1 = deep[c << 1], deep[(c << 1) + 1]
        m = n0 + n1
        if m < MINCOUNT:
            continue
        pD = (n1 + 0.5)/(m + 1.0)
        H += (m/tot)*(-(pD*math.log2(pD) + (1-pD)*math.log2(1-pD))
                      if 0 < pD < 1 else 0.0)
        ell = D
        for d in range(D+1):
            pc = c & ((1 << d) - 1) if d else 0
            pd, md = p_at(d, pc)
            if md >= MINCOUNT and abs(pd - pD) < EPS:
                ell = d
                break
        ells.append(ell); weights.append(m/tot)
    if not ells:
        return 0.0, 1.0, 0.5
    wsum = sum(weights)
    weights = [w/wsum for w in weights]
    lbar = sum(w*l for w, l in zip(weights, ells))
    V = sum(w*(l-lbar)**2 for w, l in zip(weights, ells))
    return V, H, lbar


print(f"calibration: rings {W_LIST}, n={N:,}, D={D}, eps={EPS}\n")
res = {"agg": [], "alg": []}
for W in W_LIST:
    rows = evolve(W, N + BURN, seed=W)[BURN:]
    Y = rows[:, W//2]
    agg, alg = build_bank(W)
    for fam, bank in (("agg", agg), ("alg", alg)):
        for spec in bank:
            O = project(rows, spec)
            V, H, lbar = V_and_difficulty(O, Y, D)
            res[fam].append((spec[0], W, V, H, lbar, O.mean()))

print(f"{'family':<6}{'proj':<12}{'W':>5}{'V_pi':>9}{'H':>8}{'lbar':>7}{'bal':>7}")
for fam in ("agg", "alg"):
    for name, W, V, H, lbar, bal in sorted(res[fam], key=lambda r: -r[2])[:8]:
        print(f"{fam:<6}{name:<12}{W:>5}{V:>9.3f}{H:>8.4f}{lbar:>7.2f}{bal:>7.3f}")
    print()


def summ(v):
    v = sorted(v)
    n = len(v)
    return (sum(v)/n, v[n//2], v[0], v[-1])


for fam in ("agg", "alg"):
    Vs = [r[2] for r in res[fam]]
    Hs = [r[3] for r in res[fam]]
    m, md, lo, hi = summ(Vs)
    hm, hmd, hlo, hhi = summ(Hs)
    print(f"{fam}: V_pi mean {m:.3f} median {md:.3f} range [{lo:.3f},{hi:.3f}]"
          f"  |  H mean {hm:.4f} range [{hlo:.4f},{hhi:.4f}]  n={len(Vs)}")

Va = [r[2] for r in res["agg"]]; Vb = [r[2] for r in res["alg"]]
# rank-sum separation (Mann-Whitney U), no scipy dependency
allv = sorted([(v, 0) for v in Va] + [(v, 1) for v in Vb])
ranks = {}
for i, (v, g) in enumerate(allv):
    ranks.setdefault(g, []).append(i+1)
Ra = sum(ranks[0]); na, nb = len(Va), len(Vb)
U = Ra - na*(na+1)/2
mu = na*nb/2; sd = math.sqrt(na*nb*(na+nb+1)/12)
z = (U-mu)/sd if sd else 0.0
print(f"\nV_pi separation between families: U={U:.0f}, z={z:+.2f}")
print("  -> families DO generate different V_pi" if abs(z) > 2 else
      "  -> NO reliable separation: precondition FAILS as designed")
print("\ndifficulty overlap (needed for matching):")
print(f"  agg H range [{min(r[3] for r in res['agg']):.4f},"
      f"{max(r[3] for r in res['agg']):.4f}]")
print(f"  alg H range [{min(r[3] for r in res['alg']):.4f},"
      f"{max(r[3] for r in res['alg']):.4f}]")

# ---- the decisive diagnostic: can V be identified apart from H? ----
def corr(xs, ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    if sx==0 or sy==0: return float("nan")
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy)

allV=[r[2] for r in res["agg"]+res["alg"]]
allH=[r[3] for r in res["agg"]+res["alg"]]
print(f"\ncorr(V_pi, H) pooled over all {len(allV)} projections = {corr(allV,allH):+.3f}")
for fam in ("agg","alg"):
    V=[r[2] for r in res[fam]]; H=[r[3] for r in res[fam]]
    print(f"  within {fam}: corr = {corr(V,H):+.3f}   "
          f"V range [{min(V):.2f},{max(V):.2f}]  H range [{min(H):.4f},{max(H):.4f}]")
lo=max(min(r[3] for r in res["agg"]), min(r[3] for r in res["alg"]))
hi=min(max(r[3] for r in res["agg"]), max(r[3] for r in res["alg"]))
print(f"\noverlapping H band across families: [{lo:.4f},{hi:.4f}]"
      f"  -> {'EMPTY, matching impossible' if lo>=hi else 'usable'}")
