"""
staggered_octave_v2_phase_octaves.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. The three next steps queued by v1's findings:
    phase-chroma joint structure (convention fork computed on all branches),
    the octave-integrality audit of corpus exponents, and the tau-muon
    generation-gap check.

PHASE TIMES CHROMA, OCTAVE COUNTS, AND THE GENERATION GAP (v2)

v1 (staggered_octave_z7_dft_v1.py) established the chirp/tone duality on the
residue group Z7 and queued three follow-ups. This experiment takes them.

E1  PHASE-CHROMA JOINT STRUCTURE. The i-cycle (Z4) and the chroma group (Z7)
    may or may not act as independent generators; the answer depends on WHERE
    the i-strokes anchor, and the corpus contains three inequivalent
    phrasings. All three are computed here as explicit stroke sequences on
    the half-step lattice J = 0, 1, 2, ... (station J at continuation
    coordinate d = J/2; residue r = J mod 7; octave n = J div 7):

    CANON (residue-anchored; the stroke table): a stroke fires at every
      station whose RESIDUE class is processual (r in {1, 3, 5}, plus the
      tonic's recursion face at r = 0, J > 0). Four strokes per octave,
      i^4 = 1 at each tonic: "the phase closes each octave."
    UNIFORM (coordinate-anchored): a stroke fires at every half-integer
      COORDINATE (odd J), one quarter-turn per dimension. Uniform spacing,
      but phase no longer closes per octave (3.5 strokes per octave on
      average).
    I2D (the literal "i^(2d)" label that appears in the corpus): phase(d) =
      i^(2d), i.e. one quarter-turn per half-step. Note this label does NOT
      reproduce the stroke table (at d = 1.5 it gives i^3, the table says
      i^2); the mismatch is demonstrated below.

    For each convention the joint state (residue, phase) is built explicitly
    and its minimal period found numerically. Also computed: the canon
    stroke-spacing pattern (the tonic hiccup), the canon stroke rate per
    dimension, and the UNIFORM double-cover holonomy.

E2  OCTAVE-INTEGRALITY AUDIT. One octave is R = 7 half-steps = 3.5
    dimensions, so an exponent e is a whole number of octaves iff e/3.5 is
    an integer. Every alpha-step exponent in the corpus is classified.
    Conjecture from session 2026-07-18: hierarchy (cross-scale) exponents
    are octave-integral; station-local exponents (mass-ratio bases, mixing
    angles) are not. The Pascal-diagonal continuation C(R+m, m+2) is checked
    for divisibility by R to find where abstract octave-integrality breaks.

E3  THE GENERATION GAP. The tau and muon base exponents give the
    gen-2 -> gen-3 gap delta = 58/35 - 13/12 = 241/420. Facts checked
    exactly: 420 = lcm(1..R) = P(P+1)*A(3); 4/7 = P/R = 240/420; so
    delta = P/R + 1/lcm(1..R), exactly one lattice step above P/R on the
    denominator-forced lattice (1/420)Z. A pool-fraction search ranks P/R
    among all simple pool ratios near delta, and the lattice null is
    quantified honestly.

Interim glyph-integer rule respected throughout; no pool integer altered.
"""

import math
from fractions import Fraction

import numpy as np

R = 7
P = 4

# ======================================================================= E1

print("=" * 74)
print("E1  PHASE-CHROMA JOINT STRUCTURE: three stroke conventions, computed")
print("=" * 74)

N = 2000  # stations on the half-step lattice


def cum_strokes_canon(n):
    c = np.zeros(n, dtype=int)
    k = 0
    for J in range(n):
        r = J % R
        if r in (1, 3, 5) or (r == 0 and J > 0):
            k += 1
        c[J] = k
    return c


def cum_strokes_uniform(n):
    return np.array([(J + 1) // 2 for J in range(n)], dtype=int)


def minimal_period(states):
    n = len(states)
    for period in range(1, n // 2):
        if all(states[J + period] == states[J] for J in range(n - period)):
            return period
    return None


conventions = {
    "CANON  (residue-anchored)": cum_strokes_canon(N) % 4,
    "UNIFORM (coordinate-anchored)": cum_strokes_uniform(N) % 4,
    "I2D    (literal i^(2d) label)": np.arange(N) % 4,
}

pool_orders = {7: "R", 14: "Phi*R", 28: "P*R = A(3.5)", 56: "SU(3)*R (the Lambda exponent)"}

for name, phase in conventions.items():
    states = [(J % R, int(phase[J])) for J in range(N)]
    T_joint = minimal_period(states)
    tag = pool_orders.get(T_joint, "?")
    print(f"\n  {name}")
    print(f"    joint (residue, phase) minimal period: {T_joint} half-steps "
          f"= {T_joint/2}D = {T_joint/R} octaves   [order = {tag}]")

# canon: stroke spacings and rate
canon = cum_strokes_canon(N)
stroke_J = [J for J in range(1, N) if canon[J] > canon[J - 1]]
spacings_D = [(stroke_J[i + 1] - stroke_J[i]) / 2 for i in range(12)]
rate = canon[N - 1] / ((N - 1) / 2)
print(f"\n  CANON stroke spacings (D): {spacings_D}")
print(f"    the tonic hiccup: the strokes straddling each tonic are 0.5D "
      f"apart, not 1D")
print(f"    (completion and new beginning are one event, dynamically)")
print(f"    stroke rate: {rate:.6f} quarter-turns per D  ->  8/7 = SU(3)/R "
      f"= {8/7:.6f}")

# canon: phase is a function of residue alone
canon_phase_by_residue = {}
consistent = True
for J in range(N):
    r = J % R
    ph = int(canon[J] % 4)
    if r in canon_phase_by_residue and canon_phase_by_residue[r] != ph:
        consistent = False
    canon_phase_by_residue[r] = ph
print(f"    phase determined by residue alone: {consistent}   "
      f"(phase-chroma COMMENSURATE; no larger group)")

# uniform: double-cover holonomy
u = cum_strokes_uniform(N)
hol2 = (u[14] - u[0]) % 4   # strokes across two octaves = one parity period
print(f"\n  UNIFORM double-cover holonomy: strokes per 2 octaves (= parity "
      f"period 7D) = {u[14]-u[0]} -> i^{hol2} = -i")
print(f"    one winding of the parity double cover multiplies phase by -i; "
      f"four windings (8 octaves, 28D) restore.")

# i2d mismatch with the stroke table
print(f"\n  I2D vs stroke table at d = 1.5: i^(2d) = i^3, stroke table says "
      f"i^2  ->  the corpus label 'i^(2d)' is loose;")
print(f"    it names a third convention, not the canon table.")

# ======================================================================= E2

print()
print("=" * 74)
print("E2  OCTAVE-INTEGRALITY AUDIT (one octave = R half-steps = 3.5D)")
print("=" * 74)

EXPONENTS = [
    # (name, exponent, class)
    ("alpha (unit of the ladder)", Fraction(1), "hierarchy"),
    ("G exponent", Fraction(21), "hierarchy"),
    ("Lambda exponent", Fraction(56), "hierarchy"),
    ("M_Pl/m_e exponent", Fraction(21, 2), "hierarchy"),
    ("octave exponent sum", Fraction(84), "hierarchy"),
    ("frame product E(0.5)E(3.5)", Fraction(28), "hierarchy"),
    ("Pascal level 3 (SO(10))", Fraction(126), "hierarchy"),
    ("muon base 13/12", Fraction(13, 12), "local"),
    ("tau base 58/35", Fraction(58, 35), "local"),
    ("proton base 3/2", Fraction(3, 2), "local"),
    ("v/Lambda_QCD 56/39", Fraction(56, 39), "local"),
    ("Cabibbo base 1/2", Fraction(1, 2), "local"),
    ("W boson base 95/39", Fraction(95, 39), "local"),
]

OCT = Fraction(7, 2)
print(f"\n  {'exponent':38s} {'e/3.5':>10s}  octave-integral?")
for name, e, cls in EXPONENTS:
    q = e / OCT
    integral = q.denominator == 1
    mark = f"YES ({q})" if integral else "no"
    print(f"  {name:38s} {str(q):>10s}  {mark:12s} [{cls}]")

hier = [(n, e) for n, e, c in EXPONENTS if c == "hierarchy" and n != "alpha (unit of the ladder)"]
all_hier_integral = all((e / OCT).denominator == 1 for _, e in hier)
all_local_non = all((e / OCT).denominator != 1 for n, e, c in EXPONENTS if c == "local")
print(f"\n  Pattern: all hierarchy exponents octave-integral: {all_hier_integral}; "
      f"all local exponents non-integral: {all_local_non}")
print("  Octave counts read pool-native: 21 -> 6 = T!, 56 -> 16 = P^2, "
      "84 -> 24 = P!, 28 -> 8 = SU(3),")
print("  126 -> 36 = (T!)^2, 21/2 -> 3 = T (the Planck hierarchy is exactly "
      "T octaves).")

print("\n  Pascal-diagonal continuation C(R+m, m+2), divisibility by R:")
for m in range(9):
    val = math.comb(R + m, m + 2)
    div = val % R == 0
    note = f"octaves = {val // R * 2}" if div else "NOT divisible (Lucas: no base-7 carry)"
    print(f"    m={m}: C({R+m},{m+2}) = {val:6d}   7 | C: {div}   {note}")

# ======================================================================= E3

print()
print("=" * 74)
print("E3  THE GENERATION GAP: 58/35 - 13/12")
print("=" * 74)

gap = Fraction(58, 35) - Fraction(13, 12)
assert gap == Fraction(241, 420)
lcm17 = math.lcm(*range(1, R + 1))
assert lcm17 == 420
assert Fraction(P, R) == Fraction(240, 420)
assert gap - Fraction(P, R) == Fraction(1, 420)
assert 420 == P * (P + 1) * 21  # P(P+1) * A(3)

print(f"\n  gap = 58/35 - 13/12 = {gap}  (~{float(gap):.6f})")
print(f"  420 = lcm(1..R) = P(P+1)*A(3): confirmed")
print(f"  gap = P/R + 1/lcm(1..R)  EXACTLY  (P/R = 240/420, gap = 241/420)")
print(f"  i.e. one lattice step above P/R on the denominator-forced lattice "
      f"(1/420)Z")

# pool-fraction search: is P/R the closest simple pool ratio to the gap?
POOL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20, 21, 27, 28, 39, 56, 64]
cands = []
for a in POOL:
    for b in POOL:
        fr = Fraction(a, b)
        if Fraction(1, 3) < fr < Fraction(5, 6):
            cands.append((abs(float(fr - gap)), a, b, fr))
cands.sort()
seen = set()
print("\n  closest pool fractions a/b to the gap (deduplicated by value):")
shown = 0
for dist, a, b, fr in cands:
    if fr in seen:
        continue
    seen.add(fr)
    print(f"    {a:2d}/{b:2d} = {float(fr):.6f}   |diff| = {dist:.6f}   "
          f"complexity a+b = {a+b}")
    shown += 1
    if shown == 5:
        break

# honest lattice null
lo, hi = Fraction(1, 2), Fraction(2, 3)
n_lattice = int((hi - lo) * 420)
print(f"\n  Null consideration: the base-exponent denominators (12, 35) force "
      f"the gap onto (1/420)Z;")
print(f"  in the a-priori window [1/2, 2/3] there are {n_lattice} lattice "
      f"points. Landing within one step")
print(f"  of P/R has null probability ~ 3/{n_lattice} = "
      f"{3/n_lattice:.3f}. Suggestive, not conclusive: grade C+.")

print()
print("=" * 74)
print("SUMMARY")
print("=" * 74)
print("""
  E1: the convention fork is now three computed branches with pool-native
      state-group orders R, P*R, SU(3)*R (= 7, 28, 56). CANON keeps per-
      octave phase closure at the price of the tonic hiccup (0.5D stroke
      spacing across each tonic; rate 8/7 = SU(3)/R per D) and makes phase
      chroma-determined. UNIFORM makes the parity double cover carry
      holonomy -i (restores after 4 windings = 8 octaves = 28D). I2D is a
      third convention and does not reproduce the stroke table. Adjudication
      is Ashman's; the arithmetic consequences of each choice are now on
      the table.
  E2: hierarchy exponents are octave-integral (21, 56, 84, 28, 126, 21/2 ->
      6, 16, 24, 8, 36, 3 octaves); local exponents are not; the abstract
      Pascal continuation breaks octave-integrality at m = 5 (C(12,7) = 792),
      so the conjecture is about the corpus-used levels m <= 4.
  E3: gap(gen3 - gen2) = P/R + 1/lcm(1..R) exactly; P/R is the closest
      simple pool fraction; lattice null ~3%; grade C+ (pin or discard
      remains open, leaning pin-worthy as a flagged identity).
""")
