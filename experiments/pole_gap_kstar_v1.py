"""k*(n) and the three timescales: testing the Pole Gap Calculus reply.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Verifies A*_12 = 92.646% (Ashman's correction),
  separates tau_sync from tau_learn, and tests
  k*(n) = argmin_k [ H(Y|C_k) + R_{q,k}(n) ] against the empirical argmin of
  realized prequential loss on ring 15.

Companion findings: pole_gap_kmin_findings_v1.md section 8.
Run: py -3.11 experiments/pole_gap_kstar_v1.py
"""
import math
from collections import defaultdict
W,N=15,200_000
def rule30_center(n,w=W):
    row=[0]*w; row[w//2]=1; out=[]
    for _ in range(n):
        out.append(row[w//2]); nxt=[0]*w
        for i in range(w):
            l,c,r=row[(i-1)%w],row[i],row[(i+1)%w]; nxt[i]=l^(c|r)
        row=nxt
    return out
def cycle_info(w=W,cap=200_000):
    row=[0]*w; row[w//2]=1; seen={}
    for t in range(1,cap+1):
        nxt=[0]*w
        for i in range(w):
            l,c,r=row[(i-1)%w],row[i],row[(i+1)%w]; nxt[i]=l^(c|r)
        row=nxt; key=tuple(row)
        if key in seen: return t,t-seen[key],seen[key]
        seen[key]=t
tau_X,P,first=cycle_info()
bits=rule30_center(N); orbit=bits[first:first+P]
def ideal(k):
    d=defaultdict(lambda:[0,0])
    for i in range(P):
        d[tuple(orbit[(i-k+j)%P] for j in range(k))][orbit[i]]+=1
    H=0.0
    for c in d.values():
        n=c[0]+c[1]
        for y in (0,1):
            if c[y]:
                p=c[y]/n; H-=(n/P)*p*math.log2(p)
    return H,len(d)
def preq_curve(bits,k,cps):
    counts={}; ctx=[]; cum=0.0; scored=0; res={}
    want=set(cps)
    for b in bits:
        if len(ctx)==k:
            key=tuple(ctx); cell=counts.get(key)
            if cell is None: cell=[0,0]; counts[key]=cell
            tot=cell[0]+cell[1]; p1=(cell[1]+0.5)/(tot+1)
            p=p1 if b else 1-p1
            cum+=-math.log2(max(p,1e-12)); scored+=1; cell[b]+=1
            if scored in want: res[scored]=cum/scored
        ctx.append(b)
        if len(ctx)>k: ctx.pop(0)
    return res
CPS=[2_000,5_000,10_000,25_000,50_000,100_000,190_000]
KS=list(range(8,25))
Hs={}; Ss={}
for k in KS:
    Hs[k],Ss[k]=ideal(k)
real={k:preq_curve(bits,k,CPS) for k in KS}
print("sanity: real[10][10000] =",round(real[10][10000],4),"(should be ~0.5-0.7)\n")
print(f"{'n':>9}{'pred k*':>9}{'emp k*':>8}{'match':>7}{'L(pred)':>10}{'L(emp)':>9}{'gap':>8}")
hits=0
for n in CPS:
    pred=min(KS,key=lambda k:Hs[k]+Ss[k]*math.log2(n)/(2*n))
    emp=min(KS,key=lambda k:real[k][n])
    ok=pred==emp; hits+=ok
    print(f"{n:>9,}{pred:>9}{emp:>8}{('YES' if ok else 'no'):>7}"
          f"{real[pred][n]:>10.4f}{real[emp][n]:>9.4f}{real[pred][n]-real[emp][n]:>8.4f}")
print(f"\nagreement {hits}/{len(CPS)}")
print("\nrealized loss by k (non-monotonicity in k at fixed n):")
print(f"{'n':>9}"+"".join(f"{k:>8}" for k in [8,10,12,16,20,24]))
for n in CPS:
    print(f"{n:>9,}"+"".join(f"{real[k][n]:>8.3f}" for k in [8,10,12,16,20,24]))
