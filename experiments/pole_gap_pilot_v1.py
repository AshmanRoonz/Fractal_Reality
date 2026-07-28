"""Matched-pair pilot harness. NOT A VALID RUN -- see companion findings.

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. Two attempts, three defects, no usable primary
  endpoint. Committed as a harness with its faults documented, not as a result.
  Known defects, all UNFIXED here: (1) the row generator supplies
  PILOT_N+BURN+2 rows so scoring can never reach the n=50,000 endpoint;
  (2) stats() returns the sentinel (0.0, 1.0, 0.0) when no context clears
  MINCOUNT, and those sentinels were consumed as measurements by the pair
  selector; (3) the pair selector has no minimum-dV requirement, so it will
  happily pair two sentinels. Fix all three before rerunning.

Companion findings: pole_gap_pilot_findings_v1.md
"""
"""Registered pilot: matched-pair test of V_pi against CTW advantage.

TWO-STREAM observers: context from O_t = pi(X_t), target Y_{t+1} = centre cell.
Both observers are validated by requiring that, when ctx = s[:-1] and
tgt = s[1:], they reproduce the single-stream results already checked against
brute-force tree enumeration.
"""
import numpy as np, math

CAL_W, CAL_SEEDS, CAL_N = 101, [11, 12], 20_000
PILOT_W, PILOT_SEEDS, PILOT_N = [127, 173], [201, 202, 203, 204], 50_000
CPS = [10_000, 20_000, 35_000, 50_000]
D_CAP, EPS, MINCOUNT, BURN = 16, 0.02, 20, 400
LOGHALF = math.log(0.5)


def evolve(W, n, seed):
    r = np.random.default_rng(seed).integers(0, 2, W, dtype=np.uint8)
    out = np.empty((n, W), dtype=np.uint8)
    for t in range(n):
        out[t] = r
        L = np.roll(r, 1); R = np.roll(r, -1)
        r = (L ^ (r | R)).astype(np.uint8)
    return out


def build_bank(W):
    c = W // 2; B = []
    cl = lambda ix: [i % W for i in ix]
    for r in (3, 5, 7, 9):
        B.append((f"maj{r}", cl(range(c-r//2, c+r//2+1)), "thr", r//2+1))
    for r in (5, 7, 9, 11):
        for th in (r//2, r//2+1):
            B.append((f"den{r}>{th}", cl(range(c-r//2, c+r//2+1)), "thr", th+1))
    for d in (2, 3, 4, 5):
        B.append((f"majsep{d}", cl([c-d, c, c+d]), "thr", 2))
    for off in (0, 2, 4, 6):
        B.append((f"blk7off{off}", cl(range(c-3+off, c+4+off)), "thr", 4))
    for r in (3, 5, 7, 9):
        B.append((f"xor{r}", cl(range(c-r//2, c+r//2+1)), "xor", 0))
    for d in (2, 3, 5, 7):
        B.append((f"xor2d{d}", cl([c, c+d]), "xor", 0))
    for d in (2, 3, 4, 5):
        B.append((f"xor3d{d}", cl([c-d, c, c+d]), "xor", 0))
    for s in (2, 3, 4, 5):
        B.append((f"stride{s}", cl(range(c-6, c+7, s)), "xor", 0))
    for d in (1, 2, 4, 8):
        B.append((f"diff{d}", cl([c, c+d]), "xor", 0))
    return B


def project(rows, spec):
    _, idx, kind, thr = spec
    sub = rows[:, idx]
    if kind == "xor":
        return np.bitwise_xor.reduce(sub, axis=1).astype(np.uint8)
    return (sub.sum(axis=1) >= thr).astype(np.uint8)


def stats(O, Y, D=12):
    n = len(O)-1
    o = O[:n].astype(np.int64); y = Y[1:n+1].astype(np.int64)
    ctx = np.zeros(n, dtype=np.int64); T = []
    for d in range(D+1):
        if d:
            prev = np.zeros(n, dtype=np.int64); prev[d:] = o[:n-d]
            ctx = ctx + (prev << (d-1))
        T.append(np.bincount((ctx[D:] << 1) | y[D:], minlength=1 << (d+1)))
    deep = T[D]; tot = deep.sum()
    ells, ws, H = [], [], 0.0
    for c in range(1 << D):
        n0, n1 = deep[c << 1], deep[(c << 1)+1]; m = n0+n1
        if m < MINCOUNT:
            continue
        pD = (n1+0.5)/(m+1.0)
        H += (m/tot)*(-(pD*math.log2(pD)+(1-pD)*math.log2(1-pD)) if 0 < pD < 1 else 0)
        ell = D
        for d in range(D+1):
            pc = c & ((1 << d)-1) if d else 0
            t = T[d]; a, b = t[pc << 1], t[(pc << 1)+1]
            if a+b >= MINCOUNT and abs((b+0.5)/(a+b+1.0)-pD) < EPS:
                ell = d; break
        ells.append(ell); ws.append(m/tot)
    if not ells:
        return 0.0, 1.0, 0.0
    s = sum(ws); ws = [w/s for w in ws]
    lb = sum(w*l for w, l in zip(ws, ells))
    return sum(w*(l-lb)**2 for w, l in zip(ws, ells)), H, lb


def logaddexp(a, b):
    if a < b:
        a, b = b, a
    return a + math.log1p(math.exp(b-a)) if b > a-700 else a


def ctw2(ctxs, tgts, depth, cps):
    """CTW with context from ctxs and predicted symbol from tgts."""
    nodes = {}; cum = 0.0; scored = 0; want = set(cps); out = {}; hist = 0
    def get(k):
        nd = nodes.get(k)
        if nd is None:
            nd = [0, 0, 0.0, 0.0]; nodes[k] = nd
        return nd
    for i in range(len(tgts)):
        b = int(tgts[i])
        if i >= depth:
            path = [(get((d, hist & ((1 << d)-1)) if d else (0, 0))) for d in range(depth+1)]
            lp = [0.0, 0.0]
            for v in (0, 1):
                up = None
                for d in range(depth, -1, -1):
                    nd = path[d]; n0, n1, lkt = nd[0], nd[1], nd[2]
                    cnt = n1 if v else n0
                    lkt2 = lkt + math.log((cnt+0.5)/(n0+n1+1.0))
                    if d == depth:
                        lw2 = lkt2
                    else:
                        cb = (hist >> d) & 1
                        sib = nodes.get((d+1, (hist & ((1 << d)-1)) | ((1-cb) << d)))
                        lw2 = LOGHALF + logaddexp(lkt2, up + (sib[3] if sib else 0.0))
                    up = lw2
                lp[v] = up
            p1 = math.exp(lp[1] - logaddexp(lp[0], lp[1]))
            cum += -math.log2(max(p1 if b else 1-p1, 1e-300)); scored += 1
            if scored in want:
                out[scored] = cum/scored
            up = None
            for d in range(depth, -1, -1):
                nd = path[d]; n0, n1 = nd[0], nd[1]
                cnt = n1 if b else n0
                nd[2] = nd[2] + math.log((cnt+0.5)/(n0+n1+1.0)); nd[b] += 1
                if d == depth:
                    nd[3] = nd[2]
                else:
                    cb = (hist >> d) & 1
                    sib = nodes.get((d+1, (hist & ((1 << d)-1)) | ((1-cb) << d)))
                    nd[3] = LOGHALF + logaddexp(nd[2], up + (sib[3] if sib else 0.0))
                up = nd[3]
        if depth:
            hist = ((hist << 1) | int(ctxs[i])) & ((1 << depth)-1)
    return out


def fo_mix2(ctxs, tgts, D, cps):
    """Prequential Bayesian mixture over fixed orders 0..D, uniform prior."""
    tabs = [dict() for _ in range(D+1)]; logQ = [0.0]*(D+1)
    cum = 0.0; scored = 0; want = set(cps); out = {}; hist = 0
    for i in range(len(tgts)):
        b = int(tgts[i])
        if i >= D:
            ps = []
            for k in range(D+1):
                c = hist & ((1 << k)-1) if k else 0
                cell = tabs[k].get(c)
                if cell is None:
                    cell = [0, 0]; tabs[k][c] = cell
                ps.append((cell[1]+0.5)/(cell[0]+cell[1]+1.0))
            mx = max(logQ); wts = [math.exp(q-mx) for q in logQ]; s = sum(wts)
            p1 = sum(w*p for w, p in zip(wts, ps))/s
            cum += -math.log2(max(p1 if b else 1-p1, 1e-300)); scored += 1
            if scored in want:
                out[scored] = cum/scored
            for k in range(D+1):
                c = hist & ((1 << k)-1) if k else 0
                logQ[k] += math.log(ps[k] if b else 1-ps[k]); tabs[k][c][b] += 1
        hist = ((hist << 1) | int(ctxs[i])) & ((1 << D)-1)
    return out


# ---- validation of the two-stream forms against the single-stream case ----
_s = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1]*40
_ctx, _tgt = _s[:-1], _s[1:]
_a = ctw2(_ctx, _tgt, 0, [len(_tgt)])[len(_tgt)]
_cnt = [0, 0]; _c = 0.0
for _b in _tgt:
    _p = (_cnt[1]+0.5)/(_cnt[0]+_cnt[1]+1); _c += -math.log2(_p if _b else 1-_p); _cnt[_b] += 1
assert abs(_a - _c/len(_tgt)) < 1e-12, "ctw2 depth-0 != KT"
_f = fo_mix2(_ctx, _tgt, 0, [len(_tgt)])[len(_tgt)]
assert abs(_f - _c/len(_tgt)) < 1e-12, "fo_mix2 depth-0 != KT"
print("two-stream observers: depth-0 identity checks PASS\n")

# ---------------- PHASE A ----------------
print(f"PHASE A calibration: W={CAL_W}, seeds={CAL_SEEDS}, n={CAL_N:,}")
bank = build_bank(CAL_W)
_r0 = evolve(CAL_W, 3000+BURN, CAL_SEEDS[0])[BURN:]
_seen = {}; _dedup = []
for _sp in bank:
    _key = project(_r0, _sp).tobytes()
    if _key in _seen:
        continue
    _seen[_key] = _sp[0]; _dedup.append(_sp)
print(f"  bank {len(bank)} -> {len(_dedup)} after removing functional duplicates")
bank = _dedup
cal = {}
for sd in CAL_SEEDS:
    rows = evolve(CAL_W, CAL_N+BURN, sd)[BURN:]; Y = rows[:, CAL_W//2]
    for sp in bank:
        cal.setdefault(sp[0], []).append(stats(project(rows, sp), Y))
prof = {k: tuple(np.mean([x[i] for x in v]) for i in range(3)) for k, v in cal.items()}

cands = []
for a in prof:
    for b in prof:
        if a >= b:
            continue
        Va, Ha, La = prof[a]; Vb, Hb, Lb = prof[b]
        if abs(Ha-Hb) < 0.02 and abs(La-Lb) < 1.0:
            cands.append((abs(Va-Vb), a, b))
cands.sort(reverse=True)
pairs, used = [], set()
for dv, a, b in cands:
    if a in used or b in used or len(pairs) == 4:
        continue
    hi, lo = (a, b) if prof[a][0] > prof[b][0] else (b, a)
    pairs.append((hi, lo, dv)); used |= {a, b}
print(f"  {len(cands)} candidate pairs, selected {len(pairs)}")
for hi, lo, dv in pairs:
    print(f"    {hi:<12} V={prof[hi][0]:6.2f} H={prof[hi][1]:.4f}  vs  "
          f"{lo:<12} V={prof[lo][0]:6.2f} H={prof[lo][1]:.4f}   dV={dv:5.2f}")
if len(pairs) < 4:
    raise SystemExit("insufficient matched pairs")

# ---------------- PHASE B ----------------
sel = [p[0] for p in pairs] + [p[1] for p in pairs]
tot = len(sel)*len(PILOT_W)*len(PILOT_SEEDS)*PILOT_N
print(f"\nPHASE B pilot: widths {PILOT_W}, seeds {PILOT_SEEDS}, n={PILOT_N:,}")
print(f"  {tot:,} symbol-steps per observer\n")
A = {}
for W in PILOT_W:
    bk = {s[0]: s for s in build_bank(W)}
    for sd in PILOT_SEEDS:
        rows = evolve(W, PILOT_N+BURN+2, sd)[BURN:]
        Yc = rows[:, W//2]
        for nm in sel:
            O = project(rows, bk[nm])
            m = min(len(O)-1, PILOT_N + D_CAP)
            ctxs = O[:m]; tgts = Yc[1:m+1]
            lc = ctw2(ctxs, tgts, D_CAP, CPS)
            lf = fo_mix2(ctxs, tgts, D_CAP, CPS)
            for n in CPS:
                if n in lc and n in lf:
                    A.setdefault((nm, n), []).append(lf[n]-lc[n])
        print(f"    W={W} seed={sd} done", flush=True)

print(f"\n{'pair (high - low V)':<30}" + "".join(f"{n//1000:>9}k" for n in CPS))
Db = {n: [] for n in CPS}
for hi, lo, dv in pairs:
    row = f"{hi[:13]:<14}-{lo[:13]:<15}"
    for n in CPS:
        d = np.mean(A.get((hi, n), [np.nan])) - np.mean(A.get((lo, n), [np.nan]))
        Db[n].append(d); row += f"{d:>10.4f}"
    print(row)
print(f"\n{'MEAN D-bar':<30}" + "".join(f"{np.mean(Db[n]):>10.4f}" for n in CPS))
print(f"{'pairs positive / 4':<30}"
      + "".join(f"{sum(1 for x in Db[n] if x>0):>10d}" for n in CPS))
n = CPS[-1]; arr = np.array(Db[n])
se = arr.std(ddof=1)/math.sqrt(len(arr))
print(f"\nPRIMARY ENDPOINT n={n:,}:  D-bar = {arr.mean():+.4f} +/- {1.96*se:.4f} (95%)")
print(f"  interval excludes zero: {abs(arr.mean()) > 1.96*se}")
print(f"  positive at preceding checkpoint: {np.mean(Db[CPS[-2]]) > 0}")
print(f"  pairs positive: {sum(1 for x in arr if x>0)}/4")
