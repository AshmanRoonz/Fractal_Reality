"""Aligned difficulty audit, with an alignment oracle on the entropy function.

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. The retraction notice in
  pole_gap_vpi_precondition_findings_v1.md corrected the partial-mass weighting
  but computed its corrected ranges on the still-misaligned contexts of defect
  4. This recomputes them on the intended conditioning (O_t included) and
  checks the entropy function against an alignment oracle first: with
  Y_{t+1} = O_t, aligned depth-1 H must be ~0 and misaligned ~1.

Result: the overlap retraction survives alignment; the claim that all
projections are nearly maximally unpredictable does not.

Run: py -3.11 experiments/pole_gap_aligned_audit_v1.py
"""
"""Aligned difficulty audit. The retraction's own corrected ranges were still
computed on misaligned contexts (O_{t-1} onward, never O_t).

Invariant first: an alignment oracle applied to the ENTROPY function, not only
to the observers. If Y_{t+1} = O_t exactly, an aligned depth-1 conditional
entropy must be ~0 and a misaligned one must be ~1.
"""
import numpy as np, math

D, MINCOUNT = 12, 20


def h2(p):
    return 0.0 if p <= 0 or p >= 1 else -(p*math.log2(p)+(1-p)*math.log2(1-p))


def contexts(O, Y, D, aligned):
    """Return (counts array indexed ctx*2+y, n_used).

    aligned=True : ctx bits are O_t, O_{t-1}, ..., O_{t-D+1}   (includes now)
    aligned=False: ctx bits are O_{t-1}, ..., O_{t-D}          (the old bug)
    """
    n = len(O)-1
    o = O[:n].astype(np.int64); y = Y[1:n+1].astype(np.int64)
    ctx = np.zeros(n, dtype=np.int64)
    lags = range(0, D) if aligned else range(1, D+1)
    for j, d in enumerate(lags):
        prev = np.zeros(n, dtype=np.int64)
        if d:
            prev[d:] = o[:n-d]
        else:
            prev[:] = o
        ctx = ctx + (prev << j)
    s = slice(D, n)
    return np.bincount((ctx[s] << 1) | y[s], minlength=1 << (D+1))


def measures(cnt):
    n0 = cnt[0::2].astype(float); n1 = cnt[1::2].astype(float)
    m = n0+n1; tot = m.sum()
    if tot == 0:
        return (float("nan"),)*4
    p = np.where(m > 0, (n1+0.5)/(m+1.0), 0.5)
    hs = np.array([h2(x) for x in p])
    qual = m >= MINCOUNT; occ = m > 0
    rho = float(m[qual].sum()/tot)
    H_rep = float((m[qual]/tot*hs[qual]).sum())
    H_qual = H_rep/rho if rho > 0 else float("nan")
    H_all = float((m[occ]/tot*hs[occ]).sum())
    return rho, H_rep, H_qual, H_all


# ---- INVARIANT: alignment oracle on the entropy function ----
rng = np.random.default_rng(3)
Otoy = rng.integers(0, 2, 40_000, dtype=np.uint8)
Ytoy = np.empty(len(Otoy)+1, dtype=np.uint8)
Ytoy[0] = 0
Ytoy[1:] = Otoy                      # Y_{t+1} = O_t exactly
for al in (True, False):
    c = contexts(Otoy, Ytoy, 1, al)
    _, _, hq, ha = measures(c)
    print(f"  oracle aligned={al!s:<5} H_qualified={hq:.4f}  H_all={ha:.4f}")
print("  -> aligned must be ~0, misaligned ~1\n")


def evolve(W, n, seed):
    r = np.random.default_rng(seed).integers(0, 2, W, dtype=np.uint8)
    out = np.empty((n, W), dtype=np.uint8)
    for t in range(n):
        out[t] = r
        L = np.roll(r, 1); R = np.roll(r, -1)
        r = (L ^ (r | R)).astype(np.uint8)
    return out


def bank(W):
    c = W//2; B = []
    cl = lambda ix: [i % W for i in ix]
    for r in (3, 5, 7, 9):
        B.append(("agg", f"maj{r}", cl(range(c-r//2, c+r//2+1)), "thr", r//2+1))
    for r in (5, 7, 9, 11):
        for th in (r//2, r//2+1):
            B.append(("agg", f"den{r}>{th}", cl(range(c-r//2, c+r//2+1)), "thr", th+1))
    for r in (3, 5, 7, 9):
        B.append(("alg", f"xor{r}", cl(range(c-r//2, c+r//2+1)), "xor", 0))
    for d in (2, 3, 5, 7):
        B.append(("alg", f"xor2d{d}", cl([c, c+d]), "xor", 0))
    return B


def project(rows, spec):
    _, _, idx, kind, thr = spec
    sub = rows[:, idx]
    if kind == "xor":
        return np.bitwise_xor.reduce(sub, axis=1).astype(np.uint8)
    return (sub.sum(axis=1) >= thr).astype(np.uint8)


rows = evolve(101, 60_400, 11)[400:]
Y = rows[:, 50]
print(f"{'fam':<5}{'projection':<12}{'rho':>7}{'H_qual(mis)':>13}"
      f"{'H_qual(ALIGNED)':>17}{'H_all(ALIGNED)':>16}")
store = {}
seen = set()
for spec in bank(101):
    O = project(rows, spec)
    k = O.tobytes()
    if k in seen:
        continue
    seen.add(k)
    _, _, hq_mis, _ = measures(contexts(O, Y, D, False))
    rho, _, hq_al, ha_al = measures(contexts(O, Y, D, True))
    store.setdefault(spec[0], []).append((spec[1], hq_al, ha_al))
    print(f"{spec[0]:<5}{spec[1]:<12}{rho:>7.3f}{hq_mis:>13.4f}"
          f"{hq_al:>17.4f}{ha_al:>16.4f}")

print("\nALIGNED family ranges (the intended task):")
for fam in ("agg", "alg"):
    q = [r[1] for r in store[fam]]; a = [r[2] for r in store[fam]]
    print(f"  {fam}: H_qualified [{min(q):.3f},{max(q):.3f}]   "
          f"H_all_occupied [{min(a):.3f},{max(a):.3f}]")
qa = [r[1] for r in store["agg"]]; qb = [r[1] for r in store["alg"]]
lo, hi = max(min(qa), min(qb)), min(max(qa), max(qb))
print(f"  overlap on H_qualified: "
      f"{'EMPTY' if lo >= hi else f'[{lo:.3f},{hi:.3f}]'}")
print(f"\n  spread within algebraic: {max(qb)-min(qb):.3f} bits"
      f"  -> 'all nearly maximally unpredictable' is "
      f"{'SUPPORTED' if max(qb)-min(qb) < 0.1 else 'UNSUPPORTED'}")
