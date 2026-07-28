"""Does the coherence dividend measure synergy or redundancy?

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. Ashman corrected the gloss of Omega = I(A;B|M) as
  "information in neither part alone"; that is synergy, and MI does not
  measure it. This checks the stronger claim: on the canonical cases Omega is
  maximal where synergy is zero and zero where synergy is maximal, so it is a
  redundancy measure running opposite to the phenomenon D5 names.

Run: py -3.11 experiments/pole_gap_omega_synergy_v1.py
"""
"""Does the coherence dividend measure 'information in neither part alone'?
Ashman says no: it measures shared dependence. Check whether it is worse than
that -- whether it is ANTI-correlated with synergy on the canonical cases."""
import itertools, math
def H(dist):
    return -sum(p*math.log2(p) for p in dist.values() if p > 0)
def marg(joint, idx):
    d = {}
    for k, p in joint.items():
        kk = tuple(k[i] for i in idx)
        d[kk] = d.get(kk, 0.0) + p
    return d
def MI(joint, ia, ib):
    return H(marg(joint, ia)) + H(marg(joint, ib)) - H(marg(joint, ia+ib))

print(f"{'case':<34}{'Omega=I(A;B)':>14}{'I(Y;A)':>9}{'I(Y;B)':>9}{'I(Y;A,B)':>11}{'synergy':>10}")
cases = {}
# 1. synergistic: A,B independent fair bits, Y = A xor B
j = {}
for a, b in itertools.product((0,1), repeat=2):
    j[(a, b, a ^ b)] = 0.25
cases["synergistic (Y = A xor B)"] = j
# 2. redundant: A = B fair bit, Y = A
j = {}
for a in (0,1):
    j[(a, a, a)] = 0.5
cases["redundant (A = B = Y)"] = j
# 3. independent-irrelevant
j = {}
for a, b, y in itertools.product((0,1), repeat=3):
    j[(a, b, y)] = 0.125
cases["independent, Y unrelated"] = j
# 4. unique to A
j = {}
for a, b in itertools.product((0,1), repeat=2):
    j[(a, b, a)] = 0.25
cases["unique to A (Y = A)"] = j

for name, j in cases.items():
    om = MI(j, (0,), (1,))
    iya = MI(j, (2,), (0,)); iyb = MI(j, (2,), (1,)); iyab = MI(j, (2,), (0,1))
    syn = iyab - max(iya, iyb)   # crude synergy proxy: joint beyond best single
    print(f"{name:<34}{om:>14.3f}{iya:>9.3f}{iyb:>9.3f}{iyab:>11.3f}{syn:>10.3f}")
print("\nOmega is MAXIMAL where synergy is zero (redundant) and ZERO where")
print("synergy is maximal (xor). On the canonical cases it runs the wrong way.")
