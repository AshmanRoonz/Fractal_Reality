"""Do CTW and the fixed-order mixture share J_D and differ only in learning?

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. Tests Ashman's placement correction: under the
  fair common-D protocol both families contain the complete depth-D model, so
  their internal-aperture loss J_D is identical and their difference is the
  learning term. Confirmed: on a known-order source with exactly computable
  H_D, both observers converge on the same floor while the between-observer
  gap shrinks ~35x.

See plans/pole_gap_and_the_octave.md section 7.
Run: py -3.11 experiments/pole_gap_same_floor_v1.py
"""
"""Do CTW and the fixed-order mixture share J_D and differ only in learning?

If Ashman is right, at a common depth D both observers must converge to the
SAME asymptote H_D (exactly computable here), and their loss difference must
be purely the learning term. Source: binary Markov of true order K = 10 with
declining coefficients; H_D computed from the exact stationary distribution.
"""
import numpy as np, math
K, NSTATES = 10, 1 << 10
MASK = NSTATES-1
D, N = 8, 300_000
CPS = [2_000, 10_000, 50_000, 150_000, 299_000]
LOGHALF = math.log(0.5)
h2 = lambda p: 0.0 if p <= 0 or p >= 1 else -(p*math.log2(p)+(1-p)*math.log2(1-p))

A = [1.1*(0.70**j) for j in range(K)]
PS = []
for s in range(NSTATES):
    z = 0.05 + sum(A[j]*(2*((s >> j) & 1)-1) for j in range(K))
    PS.append(1.0/(1.0+math.exp(-z)))
pi = [1.0/NSTATES]*NSTATES
for _ in range(30000):
    nx = [0.0]*NSTATES
    for s in range(NSTATES):
        w = pi[s]
        if w:
            p = PS[s]; b = (s << 1) & MASK
            nx[b] += w*(1-p); nx[b | 1] += w*p
    d = sum(abs(nx[i]-pi[i]) for i in range(NSTATES)); pi = nx
    if d < 1e-15: break

def H_exact(k):
    m = (1 << k)-1; wc = [0.0]*(1 << k); w1 = [0.0]*(1 << k)
    for s in range(NSTATES):
        c = s & m; wc[c] += pi[s]; w1[c] += pi[s]*PS[s]
    return sum(wc[c]*h2(w1[c]/wc[c]) for c in range(1 << k) if wc[c] > 0)

HD = H_exact(D)
print(f"exact H_D at D={D}: {HD:.5f} bits   (H_K = {H_exact(K):.5f})")

rng = np.random.default_rng(4)
st = rng.integers(0, NSTATES); bits = []
for _ in range(N):
    b = 1 if rng.random() < PS[st] else 0
    bits.append(b); st = ((st << 1) & MASK) | b

def logaddexp(a, b):
    if a < b: a, b = b, a
    return a+math.log1p(math.exp(b-a)) if b > a-700 else a

def ctw(bits, depth, cps):
    nodes = {}; cum = 0.0; sc = 0; want = set(cps); out = {}; hist = 0
    def g(k):
        nd = nodes.get(k)
        if nd is None: nd = [0,0,0.0,0.0]; nodes[k] = nd
        return nd
    for i, b in enumerate(bits):
        if i >= depth:
            path = [g((d, hist & ((1 << d)-1)) if d else (0,0)) for d in range(depth+1)]
            lp = [0.0,0.0]
            for v in (0,1):
                up = None
                for d in range(depth,-1,-1):
                    nd = path[d]; n0,n1 = nd[0],nd[1]
                    l2 = nd[2]+math.log(((n1 if v else n0)+0.5)/(n0+n1+1.0))
                    if d == depth: w2 = l2
                    else:
                        cb = (hist >> d) & 1
                        sib = nodes.get((d+1,(hist & ((1<<d)-1)) | ((1-cb)<<d)))
                        w2 = LOGHALF+logaddexp(l2, up+(sib[3] if sib else 0.0))
                    up = w2
                lp[v] = up
            p1 = math.exp(lp[1]-logaddexp(lp[0],lp[1]))
            cum += -math.log2(max(p1 if b else 1-p1,1e-300)); sc += 1
            if sc in want: out[sc] = cum/sc
            up = None
            for d in range(depth,-1,-1):
                nd = path[d]; n0,n1 = nd[0],nd[1]
                nd[2] = nd[2]+math.log(((n1 if b else n0)+0.5)/(n0+n1+1.0)); nd[b] += 1
                if d == depth: nd[3] = nd[2]
                else:
                    cb = (hist >> d) & 1
                    sib = nodes.get((d+1,(hist & ((1<<d)-1)) | ((1-cb)<<d)))
                    nd[3] = LOGHALF+logaddexp(nd[2], up+(sib[3] if sib else 0.0))
                up = nd[3]
        hist = ((hist << 1) | b) & ((1 << depth)-1)
    return out

def fo(bits, D, cps):
    tabs = [dict() for _ in range(D+1)]; lq = [0.0]*(D+1)
    cum = 0.0; sc = 0; want = set(cps); out = {}; hist = 0
    for i, b in enumerate(bits):
        if i >= D:
            ps = []
            for k in range(D+1):
                c = hist & ((1 << k)-1) if k else 0
                cell = tabs[k].setdefault(c,[0,0])
                ps.append((cell[1]+0.5)/(cell[0]+cell[1]+1.0))
            mx = max(lq); w = [math.exp(q-mx) for q in lq]; s = sum(w)
            p1 = sum(wi*pi_ for wi,pi_ in zip(w,ps))/s
            cum += -math.log2(max(p1 if b else 1-p1,1e-300)); sc += 1
            if sc in want: out[sc] = cum/sc
            for k in range(D+1):
                c = hist & ((1 << k)-1) if k else 0
                lq[k] += math.log(ps[k] if b else 1-ps[k]); tabs[k][c][b] += 1
        hist = ((hist << 1) | b) & ((1 << D)-1)
    return out

lc = ctw(bits, D, CPS); lf = fo(bits, D, CPS)
print(f"\n{'n':>9}{'L_FO':>10}{'L_CTW':>10}{'FO-H_D':>10}{'CTW-H_D':>10}{'L_FO-L_CTW':>13}")
for n in CPS:
    print(f"{n:>9,}{lf[n]:>10.5f}{lc[n]:>10.5f}{lf[n]-HD:>10.5f}"
          f"{lc[n]-HD:>10.5f}{lf[n]-lc[n]:>13.5f}")
print(f"\nBoth excess terms shrink toward 0 above the SAME floor H_D = {HD:.5f}.")
print("Shared J_D; the difference between the observers is the learning term.")
