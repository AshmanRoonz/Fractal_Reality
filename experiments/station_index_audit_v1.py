"""
Station-index audit: does the ladder need half-dimensions?

Created: 2026-09-19
Last updated: 2026-09-19
Version: 1.0

Motivation. Ashman, 2026-09-19: "There aren't half dimensions. Structure has
dimensionality. Process I don't think does."

The August 2026 audit (plans/half_integer_stations_audit_2026_08_19.md,
Finding 4) listed what deleting the half-step lattice would cost. That audit
answered a DELETION proposal. The present claim deletes nothing; it says the
coordinate has the wrong TYPE. So this script tests the substitution

    n = 2d,  structures at even n (carrying a dimension),
             processes at odd n  (carrying an index and a phase, no dimension)

against that load list, item by item. Result: five of six items survive, three
of them in simpler form; the sixth (c at "0.5D") genuinely breaks, and its
rationale was weak independently.

Run:  python3 station_index_audit_v1.py

Revision history
- 2026-09-19 v1.0: initial; written for
  plans/process_has_no_dimension_2026_09_19.md, Finding 3.
"""

from fractions import Fraction as F

print("Substitution under test:  n = 2d.  Structures at even n, processes at odd n.")
print("Processes get an index and a phase; they do NOT get a d.\n")

# --- load-list item 3: A(d) at 'half arguments' ---
A  = lambda d: d*(2*d+1)
print("A(d) = d(2d+1) at d = n/2   vs   T_n = n(n+1)/2")
ok = True
for n in range(8):
    d = F(n,2); a = A(d); t = F(n*(n+1),2)
    ok &= (a == t)
    kind = "structure" if n%2==0 else "process  "
    print(f"  n={n} {kind}  d={str(d):>3}  A(d)={str(a):>2}  T_n={str(t):>2}  {'=' if a==t else 'X'}")
print(f"  => A(n/2) == T_n for all n: {ok}.  'Half arguments' are an artifact of writing n/2.\n")

# --- G's exponent 21 ---
half_sum = sum(F(n,2) for n in range(7))
print(f"G exponent, corpus form : (0+0.5+1+1.5+2+2.5+3) x 2 channels = {half_sum} x 2 = {half_sum*2}")
print(f"G exponent, integer form: sum of n for n=0..6            = {sum(range(7))} = T_6 = {F(6*7,2)}")
print("  => the 'x2 channels' factor exactly undoes the /2 in d=n/2. It may be bookkeeping, not physics.\n")

# --- load-list item 1 and 2: the residue group and the wrap ---
print("Residue group: mod 3.5 on d   vs   mod 7 on n")
cls_d, cls_n = {}, {}
for n in range(0, 35):
    cls_d.setdefault(F(n,2) % F(7,2), []).append(n)
    cls_n.setdefault(n % 7, []).append(n)
same = [sorted(v) for v in cls_d.values()] == [sorted(v) for v in cls_n.values()]
print(f"  classes under mod 3.5 on d : {len(cls_d)}")
print(f"  classes under mod 7  on n  : {len(cls_n)}")
print(f"  partitions identical: {same}   => same group, Z_7. R = 7 survives.")
print("  wrap: d + 3.5 = d'  becomes  n + 7 = n'.")
print("  single-period lemma: a second return at n=8 makes 8-7=1 a period -> ladder collapses.")
print("  (the disputed '4D' is n=8; the argument is cleaner on integers)\n")

# --- load-list item 6: the C^8 partition ---
struct = [n for n in range(8) if n%2==0]; proc = [n for n in range(8) if n%2]
print(f"C^8 partition: structural = even n {struct}, processual = odd n {proc}")
print("  => identical partition to integer-vs-half-integer. 69/31 split untouched.\n")

# --- what genuinely breaks ---
print("GENUINELY BROKEN: c at '0.5D'.")
print("  corpus rationale: 'the square root comes from c living at 0.5D,")
print("  the half-dimension step from 0D energy to 0.5D speed.'")
print("  On the integer index c sits at n=1 and there is no half-step to point at.")
print("  A square root is not half a dimension; that rationale needed replacing anyway.")
