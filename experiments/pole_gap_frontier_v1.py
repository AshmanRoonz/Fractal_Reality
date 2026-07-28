"""Exact KT regret tax and a slope test of the usable-integration frontier.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Confirms the exact-regret accounting identity to
  machine precision; the slope test of dk*/d(ln n) = 1/(alpha+beta) is a NULL
  (underpowered, not a falsification). See companion findings.

Companion findings: pole_gap_frontier_findings_v1.md
Run: py -3.11 experiments/pole_gap_frontier_v1.py   (~10 min)
"""
"""Exact KT regret tax, and a slope test of the usable-integration frontier.

Two things under test.

(1) EXACT ACCOUNTING. With r_KT(n0,n1) = -log2 Q_KT - N h2(n1/N) summed over
    contexts, the sequential-to-block identity of KT forces
        realized_loss_per_symbol == Hhat_k + R_k^KT(n)
    exactly, where Hhat_k is the empirical plug-in conditional entropy.
    So predicting H_k + R^KT leaves a residual of exactly (H_k - Hhat_k),
    the plug-in entropy bias -- the same estimator pathology that section 4
    of the transfer experiment caught in the corpus's Rule 30 number.
    Checked to machine precision, and against Miller-Madow.

(2) THE SLOPE. Ashman's law for exponential gain and exponential cost:
        k*(n) = (gamma*ln n - ln l(n)) / (alpha + beta) + O(1)
    so  dk*/d(ln n) = 1/(alpha + beta), with beta = ln 2 for a fully
    populated binary fixed-order observer. Three sources with different
    coefficient decay give three different alpha, hence three different
    predicted slopes. That is the falsifiable content.
"""
import math, random

K = 10
NSTATES = 1 << K
MASK = NSTATES - 1
N = 250_000
KS = list(range(1, 11))
CPS = [1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000, 128_000, 249_000]
LN2 = math.log(2.0)
LGH = math.lgamma(0.5)


def h2(p):
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p*math.log2(p) + (1-p)*math.log2(1-p))


def kt_regret(n0, n1):
    """-log2 Q_KT(n0,n1) - N*h2(n1/N). Exactly 1 bit for a singleton."""
    Nc = n0 + n1
    negLogQ = -(math.lgamma(n0+0.5) + math.lgamma(n1+0.5)
                - math.lgamma(Nc+1.0) - 2*LGH)/LN2
    return negLogQ - Nc*h2(n1/Nc)


def build(decay, b=0.10, amp=1.15):
    A = [amp * (decay ** j) for j in range(K)]
    PS = [0.0]*NSTATES
    for s in range(NSTATES):
        z = b
        for j in range(K):
            z += A[j] * (2*((s >> j) & 1) - 1)
        PS[s] = 1.0/(1.0 + math.exp(-z))
    pi = [1.0/NSTATES]*NSTATES
    for _ in range(30000):
        nxt = [0.0]*NSTATES
        for s in range(NSTATES):
            w = pi[s]
            if w:
                p = PS[s]; base = (s << 1) & MASK
                nxt[base] += w*(1-p); nxt[base | 1] += w*p
        d = sum(abs(nxt[i]-pi[i]) for i in range(NSTATES))
        pi = nxt
        if d < 1e-15:
            break
    return PS, pi


def H_exact(PS, pi, k):
    k = min(k, K)
    m = (1 << k) - 1
    wc = [0.0]*(1 << k); w1 = [0.0]*(1 << k)
    for s in range(NSTATES):
        c = s & m
        wc[c] += pi[s]; w1[c] += pi[s]*PS[s]
    H = 0.0
    for c in range(1 << k):
        if wc[c] > 0:
            H += wc[c]*h2(w1[c]/wc[c])
    return H


def gen(PS, n, seed):
    rng = random.Random(seed)
    st = rng.getrandbits(K)
    out = []
    for _ in range(n):
        b = 1 if rng.random() < PS[st] else 0
        out.append(b); st = ((st << 1) & MASK) | b
    return out


def run(bits, k, cps):
    counts = {}; ctx = 0; m = (1 << k) - 1
    cum = 0.0; scored = 0; want = set(cps); out = {}
    for i, b in enumerate(bits):
        if i >= k:
            cell = counts.get(ctx)
            if cell is None:
                cell = [0, 0]; counts[ctx] = cell
            tot = cell[0]+cell[1]
            p1 = (cell[1]+0.5)/(tot+1)
            cum += -math.log2(max(p1 if b else 1-p1, 1e-12))
            scored += 1; cell[b] += 1
            if scored in want:
                reg = 0.0; Hh = 0.0; both = 0
                for c in counts.values():
                    n0, n1 = c
                    Nc = n0+n1
                    reg += kt_regret(n0, n1)
                    Hh += Nc*h2(n1/Nc)
                    if n0 and n1:
                        both += 1
                out[scored] = (cum/scored, reg/scored, Hh/scored,
                               len(counts), both)
        ctx = ((ctx << 1) & m) | b if k else 0
    return out


for decay in (0.55, 0.70, 0.85):
    PS, pi = build(decay)
    Hs = {k: H_exact(PS, pi, k) for k in KS}
    dH = [Hs[k]-Hs[k+1] for k in KS[:-1]]
    # fit alpha from the exponential decay of dH over its usable range
    pts = [(k, d) for k, d in zip(KS[:-1], dH) if d > 1e-7]
    if len(pts) >= 3:
        xs = [p[0] for p in pts]; ys = [math.log(p[1]) for p in pts]
        mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
        alpha = -sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs)
    else:
        alpha = float('nan')
    beta = LN2
    print(f"\n{'='*74}\nsource decay {decay}:  H_1={Hs[1]:.5f} .. H_10={Hs[10]:.5f}")
    print(f"  dH_k = " + " ".join(f"{d:.5f}" for d in dH[:6]))
    print(f"  fitted alpha = {alpha:.4f}   beta = ln2 = {beta:.4f}"
          f"   predicted slope 1/(a+b) = {1/(alpha+beta):.4f}")

    bits = gen(PS, N, seed=int(decay*1000))
    res = {k: run(bits, k, CPS) for k in KS}

    # (1) exact accounting check on the deepest observer
    k = 8
    L, R, Hh, S, both = res[k][128_000]
    ident = abs(L - (Hh + R))
    mm = both/(2*128_000*LN2)
    print(f"  identity check k=8,n=128k:  |L - (Hhat + R_KT)| = {ident:.2e}")
    print(f"    residual H_k - Hhat = {Hs[k]-Hh:+.6f}   "
          f"Miller-Madow estimate = {mm:+.6f}")

    print(f"  {'n':>8}{'k*':>5}{'L(k*)':>9}{'pred k* (KT)':>14}")
    ks = []
    for n in CPS:
        emp = min(KS, key=lambda kk: res[kk][n][0])
        pk = min(KS, key=lambda kk: Hs[kk] + res[kk][n][1])
        ks.append((math.log(n), emp))
        print(f"  {n:>8,}{emp:>5}{res[emp][n][0]:>9.4f}{pk:>14}")
    mx = sum(p[0] for p in ks)/len(ks); my = sum(p[1] for p in ks)/len(ks)
    den = sum((x-mx)**2 for x, _ in ks)
    slope = sum((x-mx)*(y-my) for x, y in ks)/den
    print(f"  MEASURED slope dk*/d(ln n) = {slope:.4f}"
          f"   PREDICTED = {1/(alpha+beta):.4f}"
          f"   ratio = {slope*(alpha+beta):.3f}")
