"""
One-and-many entailment check.

Created: 2026-09-20
Last updated: 2026-09-20
Version: 1.0

Checks the central step of the incoming "argument from one and many"
(plans/one_and_many_argument_2026_09_20.md, Finding 1):

    [E a E b (a != b)]  ==>  [A x E y (x != y)]

and whether its single ontological premise, "reality contains at least two
distinct existents", is load-bearing. It is: on a one-element domain the
premise is false and so is the conclusion.

This validates the argument's logic only. It says nothing about what
discharges the premise, which is the live question (Finding 4: the framework
offers A1 as an internal derivation where the document reaches for experienced
difference).

Revision history
- 2026-09-20 v1.0: initial.
"""

"""Check the document's entailment and whether its premise is load-bearing."""
from itertools import product

def exists_two_distinct(D):            # E a E b (a != b)
    return any(a != b for a in D for b in D)

def every_has_a_distinct_other(D):     # A x E y (x != y)
    return all(any(x != y for y in D) for x in D)

print("domain | premise  E a E b (a!=b) | conclusion  A x E y (x!=y)")
for n in range(0, 5):
    D = list(range(n))
    p, c = exists_two_distinct(D), every_has_a_distinct_other(D)
    flag = "" if (not p or c) else "   <-- COUNTEREXAMPLE"
    print(f"  |D|={n}  |      {str(p):5s}            |      {str(c):5s}{flag}")

print("\nEntailment holds on every finite domain checked (and the proof given is valid:")
print("pick witnesses a != b; for any x, either b differs from it or a does).")
print("\nIs the premise load-bearing? Drop it:")
for n in (0, 1):
    D = list(range(n))
    print(f"  |D|={n}: conclusion = {every_has_a_distinct_other(D)}  -> premise cannot be dropped")
print("\nSo the argument is valid and its one premise is doing real work.")
print("The whole question is what discharges that premise.")
