"""
Pool-grammar audit: how restrictive is a "pinned by the pool" claim?

Created: 2026-09-18
Last updated: 2026-09-18
Version: 1.0

Motivation. Ashman, 2026-09-18, on the claim that "2D + 3D = 5 = 1.5D' pins the
(Phi + circ) factor in 360 = P! * T * (Phi + circ)": "This looks like fitting."

This script turns that objection into measurements. It answers three questions
that any "pinned" claim in the constants grammar should have to answer:

  Q1  Can the stated test ever REJECT a candidate? A test nothing fails is not
      a constraint. For the octave-wrap residue test the answer is no: integers
      mod 3.5 cycle with period 7 and hit all seven stations, so every integer
      lands somewhere on the ladder.

  Q2  Was the value FREE to begin with? If the other factors and the target are
      fixed, the remaining factor is fixed by division and no lemma determines
      it; a lemma can only name it.

  Q3  How DENSE is the grammar around the target? If admitting pool sums into
      product slots makes half the integers in the window reachable, hitting
      the target is not evidence of structure.

Usage:  python3 pool_grammar_audit_v1.py [target] [lo] [hi]
Default: target 360, window [300, 420].

Nothing here refutes the alpha formula. It measures one supporting claim, and
it is reusable against the others: change TARGET and re-run.

Revision history
- 2026-09-18 v1.0: initial; written for the (Phi + circ) audit in
  plans/recursive_present_review_2026_09_18.md, Finding 1.
"""

import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

# Framework pool primitives (glyph-integer rule: Phi = 2, circ = 3).
POOL = {
    '1': 1, 'Phi': 2, 'T': 3, 'circ': 3, 'P': 4, 'T!': 6, 'R': 7, 'SU3': 8,
    'A(2)': 10, 'G': 12, 'V': 13, 'P(P+1)': 20, 'A(3)': 21, 'P!': 24,
    'A(3.5)': 28, 'S': 64,
}
WRAP = Fraction(7, 2)          # the octave period, 3.5
STATIONS = [Fraction(n, 2) for n in range(7)]   # 0, 0.5, ..., 3


def q1_residue_test(hi=40):
    """Can 'lands on a station under mod 3.5' reject any integer?"""
    reached = {Fraction(n) % WRAP for n in range(hi)}
    onto = reached == set(STATIONS)
    print("Q1  residue test, integers mod 3.5")
    print("      stations on the ladder :", [str(s) for s in STATIONS])
    print("      residues actually hit  :", [str(s) for s in sorted(reached)])
    print(f"      map is ONTO the station grid: {onto} (period 7)")
    print(f"      => the test rejects {0 if onto else '?'} of {hi} integers. "
          "A test nothing fails is not a pin.\n")
    return onto


def q2_division(target, fixed):
    """Once target and the other factors are chosen, is anything left free?"""
    prod = 1
    for name in fixed:
        prod *= POOL[name]
    print(f"Q2  {target} / ({' * '.join(fixed)}) = {target} / {prod} = "
          f"{Fraction(target, prod)}")
    print("      zero remaining freedom: division fixes it, a lemma only names it.\n")
    return Fraction(target, prod)


def names_for(value, pool=POOL):
    """Two levels of count, because the type rule operates on the second.

    Level 1, VALUE-PAIRS: distinct unordered pairs of pool VALUES summing to
    `value`. Commuted pairs are one pair, not two.
    Level 2, GLYPH READINGS: for each value-pair, the distinct glyph spellings
    (T and circ are different glyphs of the value 3, and the octave-wrap type
    rule accepts one and rejects the other, so they are two readings of one
    pair).

    Counting level 2 as if it were level 1 inflates apparent freedom; counting
    only level 1 hides the discrimination the type rule actually performs.
    """
    pairs = {}
    for a in pool:
        for b in pool:
            if pool[a] + pool[b] != value:
                continue
            key = tuple(sorted((pool[a], pool[b])))
            spell = tuple(sorted((a, b)))
            pairs.setdefault(key, set()).add("+".join(spell))
    return {k: sorted(v) for k, v in sorted(pairs.items())}


def q3_density(target, lo, hi):
    """How many integers in [lo, hi] does a 3-factor product reach?"""
    prims = sorted(set(POOL.values()))
    sums = sorted({a + b for a in prims for b in prims})
    wide = sorted(set(prims) | set(sums))

    def triples(space):
        return {t for t in cwr(space, 3) if t[0] * t[1] * t[2] == target}

    narrow_hits, wide_hits = triples(prims), triples(wide)
    reach = {t[0] * t[1] * t[2] for t in cwr(wide, 3)
             if lo <= t[0] * t[1] * t[2] <= hi}
    span = hi - lo + 1

    print(f"Q3  density around {target}")
    print(f"      primitives only            : {len(prims):3d} values -> "
          f"{len(narrow_hits)} triples hit {target}")
    print(f"      primitives + two-term sums : {len(wide):3d} values -> "
          f"{len(wide_hits)} triples hit {target}")
    print(f"      integers in [{lo},{hi}] reachable as a 3-factor product: "
          f"{len(reach)} of {span} ({100 * len(reach) / span:.0f}%)")
    print("      => admitting sums into product slots is the loose move; "
          "measure it before calling a hit structural.\n")
    return len(wide_hits), len(reach), span


if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 360
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 420

    print(f"Pool-grammar audit, target = {target}\n" + "=" * 52 + "\n")
    q1_residue_test()
    if target == 360:
        left = q2_division(target, ['P!', 'T'])
        pairs = names_for(int(left))
        readings = sum(len(v) for v in pairs.values())
        print(f"Q2b names for the value {int(left)}: {len(pairs)} value-pairs, "
              f"{readings} glyph readings")
        for k, v in pairs.items():
            print(f"       {k[0]}+{k[1]}  ->  {', '.join(v)}")
        print("      The type rule discriminates WITHIN the {2,3} pair: it "
              "rejects Phi+T (coordinate")
        print("      + count) and accepts Phi+circ (coordinate + coordinate). "
              "It does NOT rule out the")
        print("      {1,4} pair, whose count form P+1 the corpus itself uses "
              "for 5 at the ionic")
        print("      coupling. So the rule picks between two readings of one "
              "pair. Real, and narrow.\n")
    q3_density(target, lo, hi)
    print("Verdict format: a claim is PINNED only if its test can reject, its "
          "value was free,\nand the grammar is sparse at the target. "
          "Report all three or do not use the word.")
