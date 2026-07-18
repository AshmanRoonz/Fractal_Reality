# T-Operator Findings v18: The Whole-Tone Operator

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `unified_expression_T_v18_wholetone_operator.py`
Context: v16's open item (build the whole-tone operator, unit cell 8 octaves = 56 nodes, and see whether its −i flux produces the band braiding canon lacks); the canon adjudication (`docs/the_staggered_octave.html` §8).

## Result: no braiding on either side. The −i flux's spectral content is GAP-OPENING: the whole-tone field disconnects canon's sector-traversing spectral flow into isolated loops. The band structure reproduces, at the operator level, the musical phenomenology that adjudicated canon.

**F1 (instrument validated; the ℤ₅₆ cell is real).** Both operators share the identical beat geometry; only the stroke field differs (canon: 4 strokes per octave at processual residues; whole-tone: strokes at odd coordinates, ceil(J/2)). Folding check: the canon 56-cell's Bloch spectrum equals the union of the canon 7-cell's bands at the eight unfolded momenta to 6e-15. Symmetry check on a 112-node ring: canon commutes with both the 7-node and 56-node shifts (5e-15); the whole-tone operator breaks the octave shift hard (‖[T, U₇]‖ = 10.3) and keeps exactly the 8-octave shift (4e-15), precisely as the flux arithmetic (v16 E4, phases repeating only after 28 strokes) predicted. The whole-tone reading's true unit cell is 56 nodes: ℤ₅₆ realized in an operator, not just in counting.

**F2 (the hunt's verdict): no braiding anywhere, and the two monodromies differ in exactly the opposite way from the naive guess.** Tracking all 56 bands over the Brillouin circle by eigenvector-overlap assignment (grid-robust at 512/1024/2048 points, identical results):

- **Canon-56 (control): seven 8-cycles.** Each of canon's seven true bands flows by one momentum sector per zone loop and needs 8 loops to close: cycle order = folding multiplicity, with near-exact crossings at the sector intersections (minimum separation 9.1e-6) and det winding 0. This is the standard folded description of a genuinely 7-periodic system, and it is also a picture worth keeping: in the 8-octave frame, canon's bands ARE the helix, each band traversing all eight sectors before returning.
- **Whole-tone: fully trivial monodromy.** All 56 bands are isolated closed loops (56 fixed points, largest cycle 1), det winding 0.

**F3 (the positive finding): the −i flux opens gaps.** The minimum band separation jumps from 9.1e-6 (canon's protected sector crossings) to 5.05e-3 (whole-tone avoided crossings): a factor ~550. The whole-tone stroke field acts as a commensurate period-8-octave superlattice that gaps the crossings canon's octave-translation symmetry protects. So the spectral content of the −i holonomy is not braiding but DISCONNECTION: canon's spectrum is connected across sectors (a band must ascend through all eight octave-sectors before closing), while the whole-tone spectrum falls apart into closed loops at fixed height. Flagged as reading, but the consistency is striking: this is the diatonic/whole-tone phenomenology that adjudicated canon, reappearing in the operator's band topology: the scale with the leading tone ascends and resolves; the uniformly spaced scale drifts in place, going nowhere.

**F4: the whole-tone operator still conserves the 1, and chirality behaves.** Departure from |λ| = 1 stays O(α) (0.563α max over the zone, vs canon's 0.68α): the frustration does not break tonic-sharing's conservation (v14's F1 extends to the whole-tone field). The i-conjugation control mirrors the leading momentum exactly (0.4125π ↔ 1.5875π = 2π − 0.4125π).

## What the i-thread now says (v16 + v17 + v18)

i's operator-level content, complete as of this session: (1) chirality = the circulation direction of the ascending fixed point (v16 F2), with q* derived as an α-free Rayleigh argmax (v17) though not elementary; (2) the canon octave is topologically trivial in its own cell and CONNECTED in the folded frame: ascent is spectral flow (v16 F4 + v18 F2); (3) the whole-tone −i holonomy is a closure obstruction (v16 F5) whose spectral action is gap-opening: it cuts the ascent into closed loops (v18 F3). One sentence: canon climbs, whole-tone circles, and i's arrow picks the direction of the climb.

## Open

- Gap scaling: how does the 5.05e-3 avoided-crossing gap scale with a continuously tunable interpolation between the canon and whole-tone fields? (A crossover exponent would sharpen F3.)
- The §8.4 physical measurable remains open; F3 at least names the observable class to look for: gap structure at sector crossings, not mode content.

## Revision history

- 2026-07-18 v1.0: initial (ℤ₅₆ cell realized and validated; no braiding either side; canon = seven 8-cycles of folding flow, whole-tone = isolated loops; −i flux opens gaps ×550; conservation and chirality checks pass).
