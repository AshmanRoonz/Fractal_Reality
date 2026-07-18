# Staggered-Octave Findings v2: Phase Times Chroma, Octave Counts, the Generation Gap

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `staggered_octave_v2_phase_octaves.py`
Context: the three next steps queued by `staggered_octave_z7_findings_v1.md`; framework §27.7t; wrap lemma §8.

## The questions

v1 queued three follow-ups: (1) whether the i-phase cycle and the chroma group act as independent generators (the ℤ₂₈ question); (2) whether the corpus's cross-scale exponents are whole numbers of octaves; (3) whether the tau-muon base-exponent gap 241/420 pins to a pool identity or discards as numerology.

## E1 result: the convention fork is real, and its three branches have state groups of order R, P·R, and SU(3)·R. Adjudication is Ashman's; the consequences of each choice are now computed.

The corpus contains three inequivalent phrasings of where the i-strokes anchor. Built explicitly on the half-step lattice with numerical minimal-period detection:

- **CANON (residue-anchored; the stroke table).** Strokes fire at processual residue classes; four per octave; i⁴ = 1 at each tonic. Verified: phase is then a function of residue alone, so phase and chroma are COMMENSURATE; the joint state group is just ℤ₇ (order R) and no larger object arises. Price paid: the stroke spacing is not uniform. The spacing pattern is [1, 1, 1, 0.5]D repeating; the two strokes straddling each tonic are only 0.5D apart because the tonic is shared. This is the dynamical face of "completion and new beginning are one event": the pump accelerates through the tonic. The average stroke rate is 8/7 = SU(3)/R quarter-turns per dimension.
- **UNIFORM (coordinate-anchored).** One stroke per dimension (every half-integer coordinate). Uniform spacing, but the phase no longer closes per octave (3.5 strokes per octave on average). Joint state period: exactly 56 half-steps = 28D = 8 octaves; the state group is ℤ₅₆ ≅ ℤ₈ × ℤ₇, order SU(3)·R = 56, the Λ exponent. The computed holonomy: one winding of the parity double cover (two octaves, 7D) multiplies phase by exactly −i; four windings (8 octaves, 28D) restore. Under this convention the double cover of §8.4 is PHASE-CHARGED, which is a sharper spin-½-shaped statement than the bare parity alternation: a structure that returns to itself geometrically after one winding but needs four windings to return in phase. Flagged as convention-dependent; interpretation open.
- **I2D (the literal "i^(2d)" label that appears in the corpus).** One quarter-turn per half-step. Joint period 28 half-steps = 14D = 4 octaves; state group ℤ₂₈ ≅ ℤ₄ × ℤ₇, order P·R = A(3.5) = 28. Demonstrated: this label does NOT reproduce the canon stroke table (at d = 1.5 it gives i³ where the table says i²). The corpus phrase "i^(2d)" is loose; it names a third convention, not the table.

So the answer to "do phase and chroma act independently" is: under canon, no (order R); under the two uniform anchorings, yes, with joint cyclic groups of order 28 = P·R or 56 = SU(3)·R. All three orders are pool-native, which is either a pleasing consistency or a warning that the pool is dense enough to decorate any outcome; both readings are noted. **Decision queued for Ashman:** whether the stroke table (canon) is definitional, in which case the "i^(2d)" phrasing in the corpus should be corrected to avoid naming a different convention, or whether the uniform anchoring has independent standing, in which case the −i double-cover holonomy and the ℤ₅₆ state group become live framework objects.

## E2 result: the conjecture holds exactly on the corpus. Hierarchy exponents are octave-integral; local exponents are not; 13 for 13.

One octave is R half-steps = 3.5D, so e is octave-integral iff e/3.5 ∈ ℤ. Classification of every α-step exponent in the corpus:

- **Hierarchy (cross-scale) exponents, all octave-integral:** G's 21 → **6 = T! octaves**; Λ's 56 → **16 = P² octaves**; M_Pl/m_e's 21/2 → **3 = T octaves** (the Planck hierarchy is exactly T octaves); the octave exponent sum 84 → **24 = P! octaves**; the frame product 28 → **8 = SU(3) octaves**; Pascal level 3's 126 → **36 = (T!)² octaves**.
- **Station-local exponents, none octave-integral:** the mass-ratio bases 13/12, 58/35, 3/2; the emergence exponent 56/39; the Cabibbo base 1/2; the W base 95/39.

The mechanism is R-divisibility (an exponent divisible by R spans whole octaves), so the conjecture reduces to: R divides cross-scale exponents and does not divide local ones. Stated as the octave-integrality conjecture: **exponents that couple across scales complete whole octaves; exponents that act within a station do not.** This gives the recurring factor R in cross-scale formulas a structural job (R half-steps IS one octave) where before it was a factorization observation.

Boundary of validity, found honestly: the abstract Pascal-diagonal continuation C(R+m, m+2) is divisible by 7 for m = 0..4 (octave counts 6, 16, 36, 72, 132), FAILS at m = 5, 6 (C(12,7) = 792 and C(13,8) = 1287; Lucas: no base-7 carry), and resumes at m = 7, 8. So octave-integrality of the diagonal is Lucas-patterned, not a law; the corpus-used levels (m ≤ 3) all sit inside the first unbroken run. If the framework ever assigns physical content to level 5, the conjecture as stated would be falsified there or would need the Lucas refinement; this is a genuine forward falsification handle.

## E3 result: the generation gap is exactly P/R + 1/lcm(1..R). Grade C+; leaning pin as a flagged identity.

Exact facts, all asserted in code: the gen-2 to gen-3 base-exponent gap is 58/35 − 13/12 = 241/420; the denominator 420 = lcm(1, ..., R) = P(P+1)·A(3); P/R = 240/420; so **gap = P/R + 1/lcm(1..R), exactly one lattice step above P/R** on the lattice the base-exponent denominators force. The pool-fraction search confirms P/R is the closest simple pool ratio to the gap (next candidate 7/12 is 4× farther). Null quantification: the window [1/2, 2/3] contains 70 lattice points; landing within one step of P/R has null probability about 3/70 ≈ 4%. Suggestive, not conclusive. If pinned, the reading would be: one generation of ascent advances the base exponent by P rungs per R (a pump-cycle's worth per octave), plus a single quantum of the ladder's common denominator; the 1/420 term would need its own derivation before the identity is more than bookkeeping. Grade C+.

## Status

- E1: computed on all three branches; convention adjudication queued (canon table vs "i^(2d)" wording; whether ℤ₅₆ and the −i holonomy are live objects).
- E2: conjecture confirmed 13/13 on the corpus; Lucas boundary at Pascal m = 5 logged as a falsification handle; candidate for a §27.7t addendum after countersign.
- E3: exact identity logged at C+; needs a derivation of the 1/420 term to graduate.

## Revision history

- 2026-07-18 v1.0: initial (three-branch convention fork with state groups R/PR/SU(3)R and the −i double-cover holonomy; octave-integrality 13/13 with Lucas boundary; generation gap = P/R + 1/lcm(1..R) at C+).
