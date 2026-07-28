"""Instrument Pole Gap: A_T(C) = H(C(Z) | T(Z)) computed on a real failure.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Measures the residual ambiguity of the live page's
  threshold indicator about the claim it was labelled with, against a marker
  from the same data that resolves the claim exactly. Also demonstrates that
  A_T(C) depends on the prior over conditions and is therefore not an intrinsic
  property of an indicator.

See plans/pole_gap_boundary.md section 2a.
Run: py -3.11 experiments/pole_gap_indicator_ambiguity_v1.py
"""
import math
# ring-15 k-sweep, measured (pole_gap_kmin_findings_v1.md)
DATA = [  # k, H(Y|C_k), FOUND light fired, S_k
 (8,0.8636,0,254),(9,0.6676,0,488),(10,0.4499,0,782),(11,0.2902,0,1036),
 (12,0.1569,1,1219),(13,0.0910,1,1323),(14,0.0418,1,1386),(15,0.0239,1,1416),
 (16,0.0143,1,1433),(17,0.0096,1,1443),(18,0.0027,1,1450),(19,0.0027,1,1452),
 (20,0.0014,1,1454),(21,0.0,1,1455),(22,0.0,1,1455),(23,0.0,1,1455),(24,0.0,1,1455)]
P=1455
def h2(p): return 0.0 if p<=0 or p>=1 else -(p*math.log2(p)+(1-p)*math.log2(1-p))
def A(rows, ind):
    """H(C | T) with C = [H_k == 0], T = ind(row), uniform over rows."""
    groups={}
    for k,H,fired,S in rows:
        groups.setdefault(ind(k,H,fired,S),[]).append(1 if H==0.0 else 0)
    tot=len(rows); a=0.0
    for g,cs in groups.items():
        a += (len(cs)/tot)*h2(sum(cs)/len(cs))
    return a
full=DATA
print("claim C = 'the floor is found', i.e. H(Y|C_k) = 0\n")
print("indicator T = the page's threshold light (EMA < 0.3 sustained):")
for lo,hi,label in ((8,24,"k in 8..24"),(10,22,"k in 10..22"),(12,24,"k in 12..24")):
    rows=[r for r in full if lo<=r[0]<=hi]
    print(f"  prior {label:<12} A_T(C) = {A(rows, lambda k,H,f,S: f):.4f} bits")
print("\nindicator T' = (S_k == period), a less destructive marker:")
for lo,hi,label in ((8,24,"k in 8..24"),(10,22,"k in 10..22"),(12,24,"k in 12..24")):
    rows=[r for r in full if lo<=r[0]<=hi]
    print(f"  prior {label:<12} A_T(C) = {A(rows, lambda k,H,f,S: S==P):.4f} bits")
