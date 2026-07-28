"""Projection x architecture: does the architecture ranking depend on the projection?

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. First attempt at the projection sweep. Produces an
  apparent ranking flip that the design CANNOT support: the fixed-order arm is
  oracle-selected, its optimum is pinned at the tested maximum depth, and there
  is one seed. Kept as the harness plus a specification of what a valid version
  needs. See companion findings.

Companion findings: pole_gap_projection_arch_findings_v1.md
Run: py -3.11 experiments/pole_gap_projection_arch_v1.py   (~6 min)
"""
"""Does the architecture ranking change when the projection changes?

One substrate (Rule 30, ring 15). Five projections of the SAME state.
Two observer architectures: fixed-order KT (must commit to one depth) and
CTW (mixes all bounded-depth tree models).

The question is not "does CTW win" -- it should, that is the 1995 theorem.
The question is whether the SIZE and ORDERING of its advantage depends on
how the substrate is presented to the observer.
"""
import math

W, CENTER = 15, 7
N = 80_000
D = 20                      # CTW max depth, and max fixed order
KS = list(range(1, D+1))
CPS = [5_000, 20_000, 79_000]
LN2 = math.log(2.0)


def rows(n):
    row = [0]*W; row[CENTER] = 1
    out = []
    for _ in range(n):
        out.append(row[:])
        nxt = [0]*W
        for i in range(W):
            l, c, r = row[(i-1) % W], row[i], row[(i+1) % W]
            nxt[i] = l ^ (c | r)
        row = nxt
    return out


R = rows(N)
PROJ = {
    "center cell":        lambda x: x[CENTER],
    "majority of 3":      lambda x: 1 if (x[6]+x[7]+x[8]) >= 2 else 0,
    "parity of 3":        lambda x: x[6] ^ x[7] ^ x[8],
    "two separated":      lambda x: x[3] ^ x[11],
    "block density>3":    lambda x: 1 if sum(x[4:11]) > 3 else 0,
}
STREAMS = {name: [f(x) for x in R] for name, f in PROJ.items()}


def fixed_order(bits, k, cps):
    counts = {}; ctx = 0; m = (1 << k) - 1
    cum = 0.0; scored = 0; want = set(cps); out = {}
    for i, b in enumerate(bits):
        if i >= k:
            cell = counts.get(ctx)
            if cell is None:
                cell = [0, 0]; counts[ctx] = cell
            p1 = (cell[1]+0.5)/(cell[0]+cell[1]+1)
            cum += -math.log2(max(p1 if b else 1-p1, 1e-15))
            scored += 1; cell[b] += 1
            if scored in want:
                out[scored] = cum/scored
        ctx = ((ctx << 1) & m) | b
    return out


def logaddexp(a, b):
    if a < b:
        a, b = b, a
    return a + math.log1p(math.exp(b-a)) if b > a-700 else a


def ctw(bits, depth, cps):
    """Binary CTW. Nodes keyed by (length, context-int), most recent bit low.

    node = [n0, n1, logPkt, logPw].  Unvisited subtree has logPw = 0.
    """
    nodes = {}
    cum = 0.0; scored = 0; want = set(cps); out = {}
    hist = 0
    LOGHALF = math.log(0.5)

    def get(key):
        nd = nodes.get(key)
        if nd is None:
            nd = [0, 0, 0.0, 0.0]; nodes[key] = nd
        return nd

    for i, b in enumerate(bits):
        if i >= depth:
            # path: root (len 0) .. leaf (len depth)
            path = []
            for d in range(depth+1):
                key = (d, hist & ((1 << d) - 1)) if d else (0, 0)
                path.append((key, get(key)))
            # hypothesis probabilities
            lp = [0.0, 0.0]
            for v in (0, 1):
                up = None
                for d in range(depth, -1, -1):
                    key, nd = path[d]
                    n0, n1, lkt, lw = nd
                    tot = n0 + n1
                    cnt = n1 if v else n0
                    lkt2 = lkt + math.log((cnt + 0.5)/(tot + 1.0))
                    if d == depth:
                        lw2 = lkt2
                    else:
                        # children of this node at depth d+1: the one on the
                        # path (updated) and its sibling (stored)
                        childbit = (hist >> d) & 1
                        sibkey = (d+1, (hist & ((1 << d) - 1)) |
                                  ((1 - childbit) << d))
                        sib = nodes.get(sibkey)
                        lsib = sib[3] if sib else 0.0
                        lw2 = LOGHALF + logaddexp(lkt2, up + lsib)
                    up = lw2
                lp[v] = up
            root_before = path[0][1][3]
            p1 = math.exp(lp[1] - logaddexp(lp[0], lp[1]))
            p = p1 if b else 1 - p1
            cum += -math.log2(max(p, 1e-15))
            scored += 1
            if scored in want:
                out[scored] = cum/scored
            # commit
            up = None
            for d in range(depth, -1, -1):
                key, nd = path[d]
                n0, n1, lkt, lw = nd
                tot = n0 + n1
                cnt = n1 if b else n0
                nd[2] = lkt + math.log((cnt + 0.5)/(tot + 1.0))
                nd[b] += 1
                if d == depth:
                    nd[3] = nd[2]
                else:
                    childbit = (hist >> d) & 1
                    sibkey = (d+1, (hist & ((1 << d) - 1)) |
                              ((1 - childbit) << d))
                    sib = nodes.get(sibkey)
                    lsib = sib[3] if sib else 0.0
                    nd[3] = LOGHALF + logaddexp(nd[2], up + lsib)
                up = nd[3]
        hist = ((hist << 1) | b) & ((1 << depth) - 1)
    return out, len(nodes)


# sanity: CTW probabilities must normalise, and it must beat a bad fixed depth
print("sanity check on a biased coin stream...")
import random
rng = random.Random(1)
toy = [1 if rng.random() < 0.8 else 0 for _ in range(5000)]
o, nn = ctw(toy, 6, [4_000])
print(f"  CTW on iid p=0.8: {o[4000]:.4f} bits/sym (true H = "
      f"{-(0.8*math.log2(0.8)+0.2*math.log2(0.2)):.4f})\n")

print(f"{'projection':<18}{'n':>8}{'best k':>8}{'F_fixed':>10}"
      f"{'CTW':>10}{'CTW-fixed':>11}")
print("-"*67)
summary = {}
for name, bits in STREAMS.items():
    fo = {k: fixed_order(bits, k, CPS) for k in KS}
    cw, nn = ctw(bits, D, CPS)
    for n in CPS:
        bk = min(KS, key=lambda k: fo[k][n])
        ff = fo[bk][n]; cc = cw[n]
        summary[(name, n)] = (bk, ff, cc)
        print(f"{name:<18}{n:>8,}{bk:>8}{ff:>10.4f}{cc:>10.4f}{cc-ff:>11.4f}")
    print()

print("THE QUESTION: does the architecture ranking change with projection?")
n = 79_000
adv = sorted(((summary[(nm, n)][2] - summary[(nm, n)][1], nm)
              for nm in STREAMS), key=lambda t: t[0])
for d, nm in adv:
    verdict = "CTW better" if d < 0 else "fixed better"
    print(f"  {nm:<18} CTW-fixed = {d:+.4f}  ({verdict})")
