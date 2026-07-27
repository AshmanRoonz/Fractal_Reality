"""Crossover budgets on a finite-order stochastic source: testing dH_k = dR_k(n).

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Builds the testbed Ashman specified (binary Markov
  of known order K with declining coefficients, so every H_k is exactly
  computable) and tests three predictions: an interior k*(n) that migrates
  toward K, the occupancy learning tax against the crude one, and the
  crossover budget n_{k->k+1}.

Companion findings: pole_gap_crossover_findings_v1.md
Run: py -3.11 experiments/pole_gap_crossover_v1.py   (~8 min)
"""
"""Test the crossover-budget prediction on a finite-order stochastic source.

Source: binary Markov of true order K,
    P(Y=1 | y_{t-K+1..t}) = sigma(b + sum_j a_j (2 y_{t-j+1} - 1)),  a_j declining.

Everything about it is exactly computable: the stationary distribution over
2^K states, hence H_k for every k (and H_k = H_K exactly for k >= K).

Predictions under test (Ashman, 2026-07-27):
  A. an INTERIOR k*(n) exists and migrates upward toward K as n grows
  B. the occupancy tax R_k^occ(n) = (1/2n) sum_{c visited} log2 N_c(n)
     predicts realized loss better than the crude S_k log n / n
  C. the crossover budget n_{k->k+1} solving  dH_k = dR_k(n)  predicts where
     depth k+1 actually overtakes depth k
"""
import math, random

K = 12                      # true order of the source
NSTATES = 1 << K
N = 600_000
KS = list(range(1, 17))
CPS = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000, 590_000]

# declining coefficients: recent bits matter more, all K matter somewhat
A = [1.15 * (0.72 ** j) for j in range(K)]
B = 0.10


def p1_from_state(s):
    """P(Y=1 | state), state packed with the MOST RECENT bit in position 0."""
    z = B
    for j in range(K):
        bit = (s >> j) & 1
        z += A[j] * (2*bit - 1)
    return 1.0 / (1.0 + math.exp(-z))


print(f"source: binary Markov, true order K = {K}, {NSTATES} states")
PS = [p1_from_state(s) for s in range(NSTATES)]
print(f"  p range [{min(PS):.4f}, {max(PS):.4f}]")

# ---- exact stationary distribution (power iteration) ----
pi = [1.0/NSTATES]*NSTATES
MASK = NSTATES - 1
for it in range(20000):
    nxt = [0.0]*NSTATES
    for s in range(NSTATES):
        w = pi[s]
        if w == 0.0:
            continue
        p = PS[s]
        # new state: shift older bits up, put new bit at position 0
        base = (s << 1) & MASK
        nxt[base] += w * (1-p)          # new bit 0
        nxt[base | 1] += w * p          # new bit 1
    d = sum(abs(nxt[i]-pi[i]) for i in range(NSTATES))
    pi = nxt
    if d < 1e-14:
        break
print(f"  stationary converged in {it+1} iters (L1 delta {d:.2e})")


def H_exact(k):
    """H(Y_{t+1} | last k bits), exact from the stationary distribution."""
    if k >= K:
        k = K
    m = (1 << k) - 1
    wc = [0.0]*(1 << k)
    w1 = [0.0]*(1 << k)
    for s in range(NSTATES):
        c = s & m
        wc[c] += pi[s]
        w1[c] += pi[s]*PS[s]
    H = 0.0
    for c in range(1 << k):
        if wc[c] <= 0:
            continue
        q = w1[c]/wc[c]
        if 0 < q < 1:
            H -= wc[c]*(q*math.log2(q) + (1-q)*math.log2(1-q))
    return H


Hs = {k: H_exact(k) for k in KS}
print("\nexact structural entropy H_k (bits/symbol):")
for k in KS:
    tag = "  <- true order" if k == K else ""
    print(f"  k={k:>2}  H={Hs[k]:.6f}{tag}")

# ---- generate the sequence ----
rng = random.Random(30)
state = rng.getrandbits(K)
bits = []
for _ in range(N):
    p = PS[state]
    b = 1 if rng.random() < p else 0
    bits.append(b)
    state = ((state << 1) & MASK) | b


def run(k, cps):
    """Prequential KT at depth k. Returns {n: (realized loss, occupancy tax)}."""
    counts = {}
    ctx = 0
    m = (1 << k) - 1
    cum = 0.0
    scored = 0
    seen = 0
    want = set(cps)
    out = {}
    for i, b in enumerate(bits):
        if i >= k:
            cell = counts.get(ctx)
            if cell is None:
                cell = [0, 0]; counts[ctx] = cell
            tot = cell[0] + cell[1]
            p1 = (cell[1] + 0.5)/(tot + 1)
            p = p1 if b else 1 - p1
            cum += -math.log2(max(p, 1e-12))
            scored += 1
            cell[b] += 1
            if scored in want:
                tax = 0.0
                for c in counts.values():
                    nc = c[0] + c[1]
                    if nc > 0:
                        tax += math.log2(nc)
                out[scored] = (cum/scored, tax/(2*scored), len(counts))
        ctx = ((ctx << 1) & m) | b if k else 0
    return out


print(f"\nrunning {len(KS)} depths over {N:,} symbols...")
res = {k: run(k, CPS) for k in KS}

print("\n(A) k*(n): does an INTERIOR optimum appear and migrate toward K?")
print(f"{'n':>9}{'emp k*':>8}{'L(k*)':>10}{'pred k* (occ)':>15}{'pred k* (crude)':>17}")
for n in CPS:
    emp = min(KS, key=lambda k: res[k][n][0])
    pocc = min(KS, key=lambda k: Hs[k] + res[k][n][1])
    pcrude = min(KS, key=lambda k: Hs[k] + res[k][n][2]*math.log2(n)/(2*n))
    print(f"{n:>9,}{emp:>8}{res[emp][n][0]:>10.4f}{pocc:>15}{pcrude:>17}")

print("\n(B) tax model accuracy at n = 100,000 (realized vs H_k + tax):")
print(f"{'k':>4}{'realized':>11}{'H_k+occ':>11}{'err(occ)':>11}"
      f"{'H_k+crude':>12}{'err(crude)':>12}")
n = 100_000
eo = ec = 0.0
for k in KS:
    L, occ, S = res[k][n]
    po = Hs[k] + occ
    pc = Hs[k] + S*math.log2(n)/(2*n)
    eo += abs(po-L); ec += abs(pc-L)
    print(f"{k:>4}{L:>11.4f}{po:>11.4f}{po-L:>11.4f}{pc:>12.4f}{pc-L:>12.4f}")
print(f"  mean |err| occupancy {eo/len(KS):.4f}   crude {ec/len(KS):.4f}")

print("\n(C) crossover budget n_{k->k+1}: predicted vs observed")
print(f"{'k->k+1':>9}{'dH_k':>10}{'observed n':>13}{'predicted n':>14}")
FINE = [1_000, 2_000, 3_000, 5_000, 8_000, 10_000, 20_000, 30_000,
        50_000, 80_000, 100_000, 200_000, 300_000, 450_000, 590_000]
res2 = {k: run(k, FINE) for k in KS}
for k in KS[:-1]:
    dH = Hs[k] - Hs[k+1]
    if dH <= 1e-9:
        continue
    obs = None
    for n in FINE:
        if res2[k+1][n][0] < res2[k][n][0]:
            obs = n; break
    pred = None
    for n in FINE:
        dR = res2[k+1][n][1] - res2[k][n][1]
        if dH > dR:
            pred = n; break
    print(f"{k:>4}->{k+1:<4}{dH:>10.5f}"
          f"{(f'{obs:,}' if obs else '>590k'):>13}"
          f"{(f'{pred:,}' if pred else '>590k'):>14}")
