"""What does the coherence dividend Omega = I(A;B|M) actually measure?

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.1
History:
- 2026-07-28 v1.1: RETRACTED the v1.0 conclusion. v1.0 concluded from two
  extreme cases that Omega "is a redundancy measure running opposite to
  synergy." That is scope inflation: a relationship asserted from n = 2.
  Ashman's counterexample refutes it (case 5 below). Also renamed the proxy
  column: I(Y;A,B) - max{I(Y;A),I(Y;B)} equals S + min{U_A,U_B} under a PID
  decomposition, not S, so it is now labelled joint_beyond_best_single and
  case 6 exhibits a run where it is positive with zero synergy.
- 2026-07-28 v1.0: initial. Established (correctly) that Omega is not synergy.
  Its further conclusion is retracted; see above.

CURRENT POSITION. Omega = I(A;B|M) measures dependence between the parts and
nothing more. It is not synergy. It is also not redundancy, for a structural
reason: redundancy and synergy are target-relative and I(A;B|M) names no
target. "Information in neither part alone" is the synergistic term S of
I(Y;A,B|M) = R + U_A + U_B + S, which requires a named target and a chosen
PID measure.

Run: py -3.11 experiments/pole_gap_omega_synergy_v1.py
"""
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


# Each case: (joint, A-coords, B-coords, Y-coords)
cases = {}

j = {}
for a, b in itertools.product((0, 1), repeat=2):
    j[(a, b, a ^ b)] = 0.25
cases["1 synergistic (Y = A xor B)"] = (j, (0,), (1,), (2,))

j = {(a, a, a): 0.5 for a in (0, 1)}
cases["2 redundant (A = B = Y)"] = (j, (0,), (1,), (2,))

j = {k: 0.125 for k in itertools.product((0, 1), repeat=3)}
cases["3 independent, Y unrelated"] = (j, (0,), (1,), (2,))

j = {}
for a, b in itertools.product((0, 1), repeat=2):
    j[(a, b, a)] = 0.25
cases["4 unique to A (Y = A)"] = (j, (0,), (1,), (2,))

# 5. Ashman's counterexample: dependence AND synergy both maximal.
#    C,U,V independent fair bits; A=(C,U), B=(C,V), Y=U xor V.
j = {}
for c, u, v in itertools.product((0, 1), repeat=3):
    j[(c, u, v, u ^ v)] = 0.125
cases["5 shared C, synergistic U xor V"] = (j, (0, 1), (0, 2), (3,))

# 6. Both parts carry UNIQUE information, and no joint-only capacity.
#    Y = (Y1,Y2) independent fair bits; A = Y1, B = Y2.
#    The proxy is positive here because it picks up min{U_A,U_B}.
#
#    NOTE: S = 0 here is a STRUCTURAL claim about the construction, not a
#    computed quantity. This file implements no PID measure, and no single
#    PID synergy measure is universally accepted, so any numerical synergy
#    claim would have to name its decomposition. In case 6, A supplies Y1
#    and B supplies Y2 and neither contribution requires combining the
#    sources, which is why the joint-only term is zero by construction.
j = {}
for y1, y2 in itertools.product((0, 1), repeat=2):
    j[(y1, y2, y1, y2)] = 0.25
cases["6 unique to BOTH, no synergy"] = (j, (0,), (1,), (2, 3))

print(f"{'case':<32}{'Omega=I(A;B)':>14}{'I(Y;A)':>9}{'I(Y;B)':>9}"
      f"{'I(Y;A,B)':>11}{'joint_beyond_best':>19}")
print("-"*94)
for name, (j, A, B, Y) in cases.items():
    om = MI(j, A, B)
    iya = MI(j, Y, A); iyb = MI(j, Y, B); iyab = MI(j, Y, A+B)
    proxy = iyab - max(iya, iyb)        # = S + min{U_A,U_B}, NOT S
    print(f"{name:<32}{om:>14.3f}{iya:>9.3f}{iyb:>9.3f}{iyab:>11.3f}"
          f"{proxy:>19.3f}")

print("""
RETRACTED (v1.0 conclusion): "Omega is maximal where synergy is zero and zero
where synergy is maximal, so it is a redundancy measure running the wrong way."
Cases 1 and 2 alone suggested that; case 5 refutes it.

CURRENT:
  case 5  I(A;B) = 1 AND joint-beyond-best = 1. Dependence and synergy are
          both maximal, so they are not opposites. The shared bit C is simply
          irrelevant to the synergistic target.
  case 6  joint-beyond-best = 1 with no joint-only capacity: Y1 and Y2 are
          independent and each part carries only its own. The column equals
          S + min{U_A,U_B}, which is why it is not labelled synergy.

  SCOPE OF THIS FILE: no PID measure is computed here, and none is universally
  agreed on. The columns above are all mutual informations. Where S is said to
  be zero (cases 4 and 6) that is structural, read off the construction, not
  output from a decomposition. Any numerical synergy claim must name its PID.

  Omega measures dependence between the parts, full stop. It is not synergy
  and it is not redundancy: redundancy and synergy are target-relative, and
  I(A;B) names no target at all. Whole-only capacity is the S term of a PID,
  which needs a named target and a chosen decomposition.
""")
