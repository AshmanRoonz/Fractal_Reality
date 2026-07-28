"""CTW validation suite: brute-force enumeration check before use.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Run before building anything further on the CTW
  arm, per Ashman's caution that a 0.005-bit interaction is small enough for a
  boundary-condition error to manufacture. All four tests pass to machine
  precision, including exact agreement with explicit enumeration over all 26
  permitted depth-3 context trees.

Run: py -3.11 experiments/pole_gap_ctw_validation_v1.py   (seconds)
"""
"""Validate the CTW implementation before anything is built on it.

Tests (Ashman's list):
  1. depth-0 CTW must equal ordinary KT exactly
  2. on short sequences, CTW must equal BRUTE-FORCE enumeration over every
     permitted context tree, weighted by the CTW prior
  3. the sequential mixture must normalise: P(0) + P(1) = 1 at every step
  4. the tree prior itself must sum to 1 over all permitted trees
"""
import math, itertools, random

LN2 = math.log(2.0)
LGH = math.lgamma(0.5)


def logaddexp(a, b):
    if a < b:
        a, b = b, a
    return a + math.log1p(math.exp(b-a)) if b > a-700 else a


def log_pkt_block(n0, n1):
    """log P_KT(n0,n1) = log[ B(n0+.5,n1+.5)/B(.5,.5) ], natural log."""
    return (math.lgamma(n0+0.5) + math.lgamma(n1+0.5)
            - math.lgamma(n0+n1+1.0) - 2*LGH)


# ---------------- the implementation under test (verbatim from the run) ------
def ctw(bits, depth, cps, want_norm=False):
    nodes = {}
    cum = 0.0; scored = 0; want = set(cps); out = {}
    hist = 0
    LOGHALF = math.log(0.5)
    worst_norm = 0.0

    def get(key):
        nd = nodes.get(key)
        if nd is None:
            nd = [0, 0, 0.0, 0.0]; nodes[key] = nd
        return nd

    for i, b in enumerate(bits):
        if i >= depth:
            path = []
            for d in range(depth+1):
                key = (d, hist & ((1 << d) - 1)) if d else (0, 0)
                path.append((key, get(key)))
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
                        childbit = (hist >> d) & 1
                        sibkey = (d+1, (hist & ((1 << d) - 1)) |
                                  ((1 - childbit) << d))
                        sib = nodes.get(sibkey)
                        lsib = sib[3] if sib else 0.0
                        lw2 = LOGHALF + logaddexp(lkt2, up + lsib)
                    up = lw2
                lp[v] = up
            tot_lp = logaddexp(lp[0], lp[1])
            root_before = path[0][1][3]
            worst_norm = max(worst_norm, abs(math.exp(tot_lp - root_before) - 1.0))
            p1 = math.exp(lp[1] - tot_lp)
            p = p1 if b else 1 - p1
            cum += -math.log2(max(p, 1e-300))
            scored += 1
            if scored in want:
                out[scored] = cum/scored
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
        hist = ((hist << 1) | b) & ((1 << depth) - 1) if depth else 0
    return out, cum, scored, worst_norm


def plain_kt(bits, k):
    counts = {}; ctx = 0; m = (1 << k) - 1
    cum = 0.0; scored = 0
    for i, b in enumerate(bits):
        if i >= k:
            cell = counts.get(ctx)
            if cell is None:
                cell = [0, 0]; counts[ctx] = cell
            p1 = (cell[1]+0.5)/(cell[0]+cell[1]+1)
            cum += -math.log2(p1 if b else 1-p1)
            scored += 1; cell[b] += 1
        ctx = ((ctx << 1) & m) | b if k else 0
    return cum, scored


# ---------------- brute force over all permitted trees ----------------------
def all_trees(d):
    """Complete binary trees of depth <= d. Leaf = None; internal = (T0,T1)."""
    if d == 0:
        return [None]
    sub = all_trees(d-1)
    out = [None]
    for a in sub:
        for b in sub:
            out.append((a, b))
    return out


def tree_logweight(T, depth_left, D):
    """log of (1/2)^(#internal + #leaves at depth < D)."""
    if T is None:
        return math.log(0.5) if depth_left > 0 else 0.0
    return (math.log(0.5) + tree_logweight(T[0], depth_left-1, D)
            + tree_logweight(T[1], depth_left-1, D))


def leaf_of(T, ctxbits):
    """Walk the tree by successive bits (most recent first); return leaf id."""
    path = ()
    node = T
    i = 0
    while node is not None:
        b = ctxbits[i]
        path = path + (b,)
        node = node[b]
        i += 1
    return path


def brute_force(bits, D):
    """log2 Q_CTW over scored symbols, by explicit enumeration."""
    trees = all_trees(D)
    total_w = 0.0
    terms = []
    for T in trees:
        lw = tree_logweight(T, D, D)
        leaves = {}
        for i in range(D, len(bits)):
            ctxbits = [bits[i-1-j] for j in range(D)]   # most recent first
            lid = leaf_of(T, ctxbits)
            c = leaves.setdefault(lid, [0, 0])
            c[bits[i]] += 1
        lq = sum(log_pkt_block(c[0], c[1]) for c in leaves.values())
        terms.append(lw + lq)
        total_w += math.exp(lw)
    acc = terms[0]
    for t in terms[1:]:
        acc = logaddexp(acc, t)
    return acc/LN2 * -1.0, total_w, len(trees)


rng = random.Random(7)
print("TEST 4: does the tree prior sum to 1?")
for D in (1, 2, 3):
    _, tw, nt = brute_force([0, 1]*8, D)
    print(f"  D={D}: {nt:>3} trees, prior mass = {tw:.12f}")

print("\nTEST 1: depth-0 CTW == ordinary KT (order 0)?")
seq = [rng.randint(0, 1) for _ in range(200)]
_, c_ctw, s1, _ = ctw(seq, 0, [])
c_kt, s2 = plain_kt(seq, 0)
print(f"  CTW {c_ctw:.10f} bits over {s1} symbols")
print(f"  KT  {c_kt:.10f} bits over {s2} symbols")
print(f"  |diff| = {abs(c_ctw-c_kt):.2e}  -> {'PASS' if abs(c_ctw-c_kt) < 1e-9 else 'FAIL'}")

print("\nTEST 3: sequential normalisation P(0)+P(1)=1")
seq2 = [rng.randint(0, 1) for _ in range(400)]
for D in (1, 2, 3, 6):
    _, _, _, wn = ctw(seq2, D, [], want_norm=True)
    print(f"  D={D}: worst |P(0)+P(1)-1| = {wn:.2e}"
          f"  -> {'PASS' if wn < 1e-9 else 'FAIL'}")

print("\nTEST 2: CTW == brute-force enumeration over all permitted trees")
for D in (1, 2, 3):
    for trial in range(3):
        s = [rng.randint(0, 1) for _ in range(14)]
        _, cum, sc, _ = ctw(s, D, [])
        bf, _, nt = brute_force(s, D)
        ok = abs(cum - bf) < 1e-9
        print(f"  D={D} trial{trial}: CTW {cum:.10f}  brute {bf:.10f}"
              f"  |d|={abs(cum-bf):.2e}  {'PASS' if ok else '*** FAIL ***'}")
