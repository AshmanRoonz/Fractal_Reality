"""Pole gap transfer experiment v1: Yao's next-bit/distinguisher equivalence as a pole-gap law.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Imported from the claude.ai chat session (emergence-files.zip,
  original name transfer.py); code body unchanged from the chat version except this header.
  Numbers re-verified locally the same day (py -3.11).

Companion findings: pole_gap_transfer_findings_v1.md
Run: py -3.11 experiments/pole_gap_transfer_v1.py
"""
import numpy as np, math
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# TRANSFER UNDER TEST (T1): Yao's next-bit/distinguisher
# equivalence, moved from cryptography to arbitrary projected
# processes. Claim: within an observer class (order-k statistics),
#   per-step prediction deficit  <=>  k-block distinguishability,
# linked by the chain rule  KL(P_k||U_k) = sum of per-step deficits
# and Pinsker  TV <= sqrt(KL_bits * ln2 / 2).
# Predictions: (1) bound holds on every stream, crypto or physics;
# (2) the two alarms NEVER fire separately; (3) consistency audits
# our own earlier entropy-rate estimate for Rule 30.
# ─────────────────────────────────────────────────────────────

N = 300_000

def rule30_center(n, W=101):
    row = np.zeros(W, np.uint8); row[W//2] = 1
    out = np.empty(n, np.uint8)
    for t in range(n):
        out[t] = row[W//2]
        L = np.roll(row,1); R = np.roll(row,-1)
        row = (L ^ (row | R)).astype(np.uint8)
    return out

def lfsr_bits(n, nbits=8, taps=(8,6,5,4), state=0b10011010):
    out = np.empty(n, np.uint8)
    for t in range(n):
        out[t] = state & 1
        fb = 0
        for tp in taps: fb ^= (state >> (tp-1)) & 1
        state = (state >> 1) | (fb << (nbits-1))
    return out

def markov_bits(n, p_stay, seed=7):
    rng = np.random.default_rng(seed)
    out = np.empty(n, np.uint8); b = 0
    r = rng.random(n)
    for t in range(n):
        out[t] = b
        if r[t] >= p_stay: b = 1-b
    return out

def logistic_bits(n, r=3.8, x0=0.3141592):
    x = x0
    for _ in range(1000): x = r*x*(1-x)
    out = np.empty(n, np.uint8)
    for t in range(n):
        x = r*x*(1-x); out[t] = 1 if x > 0.5 else 0
    return out

def coin_bits(n, seed=3):
    return np.random.default_rng(seed).integers(0,2,n,dtype=np.uint8)

def kt_prequential(bits, k):
    """⊙'s honest ledger: price before reveal, pay log-loss."""
    counts = defaultdict(lambda: [0,0]); ctx = []
    loss = 0.0; scored = 0; hits = 0
    for b in bits:
        b = int(b)
        if len(ctx) == k:
            c = counts[tuple(ctx)]
            t = c[0] + c[1]
            p1 = (c[1] + 0.5) / (t + 1)
            p  = p1 if b else 1 - p1
            loss += -math.log2(max(p, 1e-12)); scored += 1
            hits += ((1 if p1 > 0.5 else 0) == b)
            c[b] += 1
        ctx.append(b)
        if len(ctx) > k: ctx.pop(0)
    return loss/scored, hits/scored

def block_stats(bits, k):
    """k-block empirical distribution vs uniform: KL(bits), TV, chi2/df."""
    n = len(bits) - k + 1
    idx = np.zeros(n, dtype=np.int64)
    for j in range(k):
        idx = (idx << 1) | bits[j:j+n].astype(np.int64)
    cnt = np.bincount(idx, minlength=1<<k).astype(float)
    tot = cnt.sum(); p = cnt/tot; u = 1.0/(1<<k)
    nz = p > 0
    KL = float(np.sum(p[nz]*np.log2(p[nz]/u)))          # = k - H(P_k), chain rule
    TV = 0.5*float(np.abs(p-u).sum())
    chi2df = float(((cnt-tot*u)**2/(tot*u)).sum()) / ((1<<k)-1)
    return KL, TV, chi2df

K = 12
streams = [
    ("fair coin (control)",  coin_bits(N)),
    ("Rule 30 center (phys)",rule30_center(N)),
    ("logistic r=3.8 (chaos)",logistic_bits(N)),
    ("Markov p=0.55 (stat)", markov_bits(N,0.55)),
    ("LFSR-8 (weak crypto)", lfsr_bits(N)),
]

print(f"{'stream':<24}{'KT H(b|ctx12)':>14}{'acc%':>8}{'KL12':>9}{'TVbound':>9}{'TVmeas':>9}{'chi2/df':>9}  coupling")
print("-"*96)
for name, bits in streams:
    H, acc = kt_prequential(bits, K)
    KL, TV, c2 = block_stats(bits, K)
    tv_bound = math.sqrt(KL*math.log(2)/2)
    pred_fires = acc > 0.515 or H < 0.97
    dist_fires = c2 > 1.35            # chi2/df well above 1 => distinguisher alarm
    couple = ("BOTH fire" if pred_fires and dist_fires else
              "NEITHER"   if not pred_fires and not dist_fires else
              "*** DECOUPLED — TRANSFER FALSIFIED ***")
    ok = "OK " if TV <= tv_bound + 1e-9 else "VIOLATED"
    print(f"{name:<24}{H:>14.4f}{acc*100:>8.2f}{KL:>9.4f}{tv_bound:>9.4f}{TV:>9.4f}{c2:>9.2f}  {couple} | Pinsker {ok}")

# ─────────────────────────────────────────────────────────────
# AUDIT: the transfer's consistency requirement vs our session-1
# claim that Rule 30's center column has entropy rate ≈ 0.863.
# If the per-step deficit were really 0.137, chain rule forces
# KL12 ≈ 12×0.137 ≈ 1.65 bits and the chi-square must scream.
# ─────────────────────────────────────────────────────────────
print()
bits = rule30_center(200_000)   # replicate session-1 conditions
def block_H(bits, m):
    n = len(bits)-m+1
    idx = np.zeros(n, dtype=np.int64)
    for j in range(m):
        idx = (idx << 1) | bits[j:j+n].astype(np.int64)
    cnt = np.bincount(idx); cnt = cnt[cnt>0].astype(float)
    p = cnt/cnt.sum()
    raw = -float(np.sum(p*np.log2(p)))
    mm  = raw + (len(cnt)-1)/(2*n*math.log(2))   # Miller–Madow correction
    return raw, mm, len(cnt)/(1<<m)
r16, m16, cov16 = block_H(bits,16); r15, m15, cov15 = block_H(bits,15)
Hkt16, acc16 = kt_prequential(bits, 16)
KL12b, TV12b, c2b = block_stats(bits, 12)
print("Rule 30 entropy-rate audit (200k samples, as in session 1):")
print(f"  naive plug-in  H(16)-H(15)      = {r16-r15:.4f} bits/step   (block coverage at m=16: {cov16*100:.1f}%)")
print(f"  Miller-Madow   H(16)-H(15)      = {m16-m15:.4f} bits/step")
print(f"  KT prequential H(b|ctx16)       = {Hkt16:.4f} bits/step   (acc {acc16*100:.2f}%)")
print(f"  chain-rule check: KL12 = {KL12b:.4f} bits  -> implied avg deficit {KL12b/12:.5f} bits/step")
print(f"  if session-1 rate 0.863 were the class-relative gap, KL12 would be ~1.65 bits; chi2/df = {c2b:.2f} says otherwise")

# ─────────────────────────────────────────────────────────────
# EXPORTED COROLLARY (crypto -> experimental physics):
# sample complexity of DETECTING hidden determinism scales as
# 1/deficit. G-statistic = 2n·KL_nats crosses threshold at
# n* ≈ const / deficit. Test on Markov chains of varying subtlety.
# ─────────────────────────────────────────────────────────────
print()
print("Sample-complexity corollary (detection step n* vs 1/deficit):")
print(f"{'p_stay':>8}{'deficit(bits/step)':>20}{'n* detected':>13}{'n* × deficit':>14}")
for p in (0.51, 0.55, 0.60):
    bitsM = markov_bits(N, p, seed=11)
    dH = 1 + (p*math.log2(p) + (1-p)*math.log2(1-p))   # 1 - H_b(p)
    # scan: G-test on 1-step transitions over growing prefix
    nstar = None
    trans = np.zeros((2,2))
    prev = int(bitsM[0])
    for t in range(1, N):
        b = int(bitsM[t]); trans[prev][b] += 1; prev = b
        if t % 50 == 0 and t > 200:
            tot = trans.sum()
            row = trans.sum(1, keepdims=True); col = trans.sum(0, keepdims=True)
            exp = row*col/tot
            with np.errstate(divide='ignore', invalid='ignore'):
                G = 2.0*np.nansum(np.where(trans>0, trans*np.log(trans/exp), 0))
            if G > 10.83:   # p ~ 0.001, df=1
                nstar = t; break
    print(f"{p:>8.2f}{dH:>20.6f}{(nstar if nstar else -1):>13}{(nstar*dH if nstar else float('nan')):>14.1f}")
