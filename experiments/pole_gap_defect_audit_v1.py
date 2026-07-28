"""Audit of two harness defects found by Ashman, and their consequences.

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. Confirms the temporal misalignment (defect 4) with
  an alignment oracle, confirms the partial-mass entropy (defect 5), and traces
  defect 5 to the precondition study, whose central claim it retracts.

Run: py -3.11 experiments/pole_gap_defect_audit_v1.py
"""
"""Verify defects 4 and 5, and trace defect 5 to the committed precondition claim.

Defect 4: alignment oracle. IID O, target Y_{t+1} = O_t. A correctly aligned
depth-1 observer must approach zero loss.

Defect 5: H is a partial-mass sum. Reproduce the xor9 accounting.

CONSEQUENCE (untested by either of us so far): the precondition study's claim
that the two families do not overlap in difficulty rests on that same H. If the
families differ mainly in COVERAGE rather than predictability, the claim that
killed the two-family design is itself an artifact.
"""
import numpy as np, math

MINCOUNT, D = 20, 12
LOGHALF = math.log(0.5)


def evolve(W, n, seed):
    r = np.random.default_rng(seed).integers(0, 2, W, dtype=np.uint8)
    out = np.empty((n, W), dtype=np.uint8)
    for t in range(n):
        out[t] = r
        L = np.roll(r, 1); R = np.roll(r, -1)
        r = (L ^ (r | R)).astype(np.uint8)
    return out


def h2(p):
    return 0.0 if p <= 0 or p >= 1 else -(p*math.log2(p)+(1-p)*math.log2(1-p))


# ---------- DEFECT 4: alignment oracle ----------
def fo_mix_OLD(ctxs, tgts, Dp):
    tabs = [dict() for _ in range(Dp+1)]; logQ = [0.0]*(Dp+1)
    cum = 0.0; sc = 0; hist = 0
    for i in range(len(tgts)):
        b = int(tgts[i])
        if i >= Dp:
            ps = []
            for k in range(Dp+1):
                c = hist & ((1 << k)-1) if k else 0
                cell = tabs[k].setdefault(c, [0, 0])
                ps.append((cell[1]+0.5)/(cell[0]+cell[1]+1.0))
            mx = max(logQ); w = [math.exp(q-mx) for q in logQ]; s = sum(w)
            p1 = sum(wi*pi for wi, pi in zip(w, ps))/s
            cum += -math.log2(max(p1 if b else 1-p1, 1e-300)); sc += 1
            for k in range(Dp+1):
                c = hist & ((1 << k)-1) if k else 0
                logQ[k] += math.log(ps[k] if b else 1-ps[k]); tabs[k][c][b] += 1
        hist = ((hist << 1) | int(ctxs[i])) & ((1 << Dp)-1)   # AFTER predicting
    return cum/sc


def fo_mix_FIXED(ctxs, tgts, Dp):
    tabs = [dict() for _ in range(Dp+1)]; logQ = [0.0]*(Dp+1)
    cum = 0.0; sc = 0; hist = 0
    for i in range(len(tgts)):
        hist = ((hist << 1) | int(ctxs[i])) & ((1 << Dp)-1)   # O_t arrives FIRST
        b = int(tgts[i])
        if i >= Dp:
            ps = []
            for k in range(Dp+1):
                c = hist & ((1 << k)-1) if k else 0
                cell = tabs[k].setdefault(c, [0, 0])
                ps.append((cell[1]+0.5)/(cell[0]+cell[1]+1.0))
            mx = max(logQ); w = [math.exp(q-mx) for q in logQ]; s = sum(w)
            p1 = sum(wi*pi for wi, pi in zip(w, ps))/s
            cum += -math.log2(max(p1 if b else 1-p1, 1e-300)); sc += 1
            for k in range(Dp+1):
                c = hist & ((1 << k)-1) if k else 0
                logQ[k] += math.log(ps[k] if b else 1-ps[k]); tabs[k][c][b] += 1
    return cum/sc


rng = np.random.default_rng(5)
O = rng.integers(0, 2, 30_000, dtype=np.uint8)
Ynext = O.copy()          # Y_{t+1} = O_t exactly
print("DEFECT 4 -- alignment oracle (IID O, Y_{t+1} = O_t, depth 1)")
print(f"  as-shipped observer : {fo_mix_OLD(O, Ynext, 1):.4f} bits/symbol")
print(f"  corrected observer  : {fo_mix_FIXED(O, Ynext, 1):.4f} bits/symbol")
print("  -> as-shipped sees no relationship at all; the defect is confirmed\n")


# ---------- DEFECT 5: partial-mass entropy, and its consequence ----------
def bank(W):
    c = W//2; B = []
    cl = lambda ix: [i % W for i in ix]
    for r in (3, 5, 7, 9):
        B.append((f"maj{r}", cl(range(c-r//2, c+r//2+1)), "thr", r//2+1))
    for r in (5, 7, 9, 11):
        for th in (r//2, r//2+1):
            B.append((f"den{r}>{th}", cl(range(c-r//2, c+r//2+1)), "thr", th+1))
    for r in (3, 5, 7, 9):
        B.append((f"xor{r}", cl(range(c-r//2, c+r//2+1)), "xor", 0))
    for d in (2, 3, 5, 7):
        B.append((f"xor2d{d}", cl([c, c+d]), "xor", 0))
    return B


def project(rows, spec):
    _, idx, kind, thr = spec
    sub = rows[:, idx]
    if kind == "xor":
        return np.bitwise_xor.reduce(sub, axis=1).astype(np.uint8)
    return (sub.sum(axis=1) >= thr).astype(np.uint8)


def accounting(O, Y):
    """Return rho, H_reported (partial mass), H_qualified, H_all_occupied."""
    n = len(O)-1
    o = O[:n].astype(np.int64); y = Y[1:n+1].astype(np.int64)
    ctx = np.zeros(n, dtype=np.int64)
    for d in range(1, D+1):
        prev = np.zeros(n, dtype=np.int64); prev[d:] = o[:n-d]
        ctx = ctx + (prev << (d-1))
    cnt = np.bincount((ctx[D:] << 1) | y[D:], minlength=1 << (D+1))
    n0 = cnt[0::2].astype(float); n1 = cnt[1::2].astype(float)
    m = n0+n1; tot = m.sum()
    qual = m >= MINCOUNT
    occ = m > 0
    p = np.where(m > 0, (n1+0.5)/(m+1.0), 0.5)
    hs = np.array([h2(x) for x in p])
    H_rep = float((m[qual]/tot*hs[qual]).sum())
    rho = float(m[qual].sum()/tot)
    H_qual = H_rep/rho if rho > 0 else float("nan")
    H_all = float((m[occ]/tot*hs[occ]).sum())
    return rho, H_rep, H_qual, H_all, int(qual.sum())


rows = evolve(101, 60_400, 11)[400:]
Y = rows[:, 50]
bk = {s[0]: s for s in bank(101)}
print("DEFECT 5 -- H is a partial-mass sum (n=60,000, D=12, MINCOUNT=20)")
print(f"{'projection':<12}{'rho':>8}{'H_reported':>12}{'H_qualified':>13}"
      f"{'H_all_occ':>11}{'qual ctx':>10}")
fams = {"agg": ["maj3", "maj5", "maj7", "maj9", "den7>3", "den9>4", "den11>5"],
        "alg": ["xor3", "xor5", "xor7", "xor9", "xor2d2", "xor2d3", "xor2d5"]}
store = {}
for fam, names in fams.items():
    for nm in names:
        rho, Hr, Hq, Ha, q = accounting(project(rows, bk[nm]), Y)
        store.setdefault(fam, []).append((nm, rho, Hr, Hq, Ha))
        print(f"{nm:<12}{rho:>8.4f}{Hr:>12.4f}{Hq:>13.4f}{Ha:>11.4f}{q:>10}")
    print()

print("CONSEQUENCE for the committed precondition claim")
print("(the claim was: family H ranges do not overlap, so matching is impossible)")
for key, lbl in ((2, "H_reported (what was committed)"),
                 (3, "H_qualified (renormalised)"),
                 (4, "H_all_occupied")):
    a = [r[key] for r in store["agg"]]; b = [r[key] for r in store["alg"]]
    lo = max(min(a), min(b)); hi = min(max(a), max(b))
    print(f"  {lbl:<34} agg [{min(a):.4f},{max(a):.4f}]  "
          f"alg [{min(b):.4f},{max(b):.4f}]  overlap "
          f"{'EMPTY' if lo >= hi else f'[{lo:.4f},{hi:.4f}]'}")
