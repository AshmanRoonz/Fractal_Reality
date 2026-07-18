# T-Operator Findings v16: Bloch Sectors of the Staggered Ring

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `unified_expression_T_v16_bloch_sectors.py`
Context: v14's F4 (parity double-cover probe null; Bloch-sector test proposed); the canon adjudication (`docs/the_staggered_octave.html` §8, which tagged the −i holonomy to the whole-tone reading); v15's correction that no weight-based observable can see i-chirality and that a chirality test requires a phase-sensitive observable. This experiment is that instrument.

## The question

Does the parity double cover have operator-level content, and does i's chirality have any observable at all? v14's period-2 weight probe was null. The sharper instrument: make the ring operator exactly translation-invariant (beat-synchronous composition: each beat is exp of the summed generators over all octaves), decompose into 7×7 Bloch blocks T(q), and look at the spectrum as a function of momentum around the octave ring, including the antiperiodic sector q = π and the full band monodromy.

## Findings, graded

**F1 (instrument validated).** The beat-synchronous ring commutes with the 7-node octave shift to 3.5e-15 and its spectrum equals the union of Bloch-block spectra to 4.3e-15: the decomposition is exact, not approximate. Convention honesty: the beat-synchronous operator differs from v14's octave-sequential one substantially in operator norm (relative distance 0.90), but the conserved quantity agrees (departure from trace preservation 0.68α vs 0.79α, both inside v14's F1 band 0.60-0.79α): composition convention moves details, not the conservation result.

**F2 (grade A−; the headline): the fixed point ascends. The leading mode carries momentum, its weights stay octave-uniform, and the direction of circulation is set by i's chirality.** The leading modulus does NOT sit at q = 0: it peaks at q* ≈ 0.3621π per octave (|λ| = 1.00496 there vs 1.00392 at q = 0), and q* is α-independent across a 16× coupling sweep (0.3624 → 0.3607 for α × 0.25 to α × 4), so it is a property of the four-beat geometry F, not of κ. Because the leading state is a Bloch mode, its per-octave weight distribution is EXACTLY uniform; the modulation lives entirely in phase, which advances by q* ≈ 65° per octave. So there is no A3 violation (every octave carries identical weight; scale self-similarity holds to machine precision on the ring) and simultaneously no octave-uniform fixed point: the 1 circulates around the scale ring as a traveling wave, each octave the same in magnitude and rotated in phase. This also explains the prior nulls: v14/v15 probed weights, and weights are exactly blind to this structure (v15's correction, now with its constructive completion). Controls: conjugating the stroke phases (i → −i) flips q* to 2π − q* exactly (1.6379π vs 0.3621π): the circulation direction is the i-chirality observable v15 said must exist. Reversing beat order does NOT flip the direction (q* = 0.4345π, same sign): direction is carried by chirality, magnitude by composition order; order and chirality now have separate observables (order → weight pooling, v15; chirality → circulation sense, v16). Convention robustness: the octave-sequential (v14) ring's leading eigenvector is also momentum-carrying (94.8% of its weight at nonzero momentum, dominant sector q = 4π/3 ≡ −2π/3), so "the fixed point is not octave-uniform in phase" is convention-robust, though the preferred momentum value is not. Open: identify q* ≈ 0.3621π analytically from the beat geometry (θ = π/2, hub π/6); no pool identification is claimed and none was found at the 1% level; log the number, resist decorating it.

**F3 (grade B): the antiperiodic sector is the softest. A double-cover-flavored near-degeneracy sits exactly where v14 proposed to look.** The modulus gap between the top two modes, by sector: 0.12α at q = 0, 0.32α at q = π/2, 0.31α at q = 3π/2, and **0.058α at q = π**: the antiperiodic sector's gap is 2× smaller than periodic and 5× smaller than the quarter-turn sectors, and the ratio is stable in α (0.0577-0.0604 across 16×). Two modes nearly co-lead at exactly antiperiodic momentum. This is the double-cover-shaped spectral feature the v14 instrument could not resolve: present, modest, and stable; a softness of the antiperiodic sector rather than a mode. It does not close at finite α (no exact degeneracy).

**F4 (clean null): no band braiding in the canon octave.** Tracking all seven bands continuously around the Brillouin circle (2801 points, endpoint residual 2e-15): the monodromy permutation is the identity, all per-band phase windings are 0, and the minimum band separation over the zone is 0.117 (no exceptional-point proximity). The canon octave's band topology is trivial: no intrinsic double cover in the bands. This is CONSISTENT with the adjudication: canon carries no holonomy; the double-cover content belongs to the whole-tone reading.

**F5 (exact): the whole-tone −i holonomy is a closure obstruction, i.e. spin-structure-like flux on the ring.** A uniform (coordinate-anchored) stroke field on a ring of n octaves has floor(7n/2) strokes per loop and closes iff that count ≡ 0 mod 4, i.e. iff n ≡ 0 mod 8. Otherwise the field is frustrated by a flux that walks the i-cycle as n walks 2, 4, 6, 0 (mod 8): **−i, −1, +i, +1**. The parity double cover (n = 2) carries exactly the −i holonomy computed in `staggered_octave_findings_v2.md`, now realized as a ring flux: a field that returns to itself geometrically after the loop but not in phase, the defining shape of a spin structure. The canon field (four strokes per octave) closes on every ring, consistent with canon having no holonomy to carry.

## What the i-thread now says

The question was whether i's structure has content beyond bookkeeping. Answer, at the operator level: yes, three ways, each in the register the adjudication predicted. (1) i's chirality has a genuine observable: the direction the fixed point circulates around the scale ring (F2); it took a phase-sensitive instrument to see because weights are provably blind to it. (2) The double cover shows up in canon only as a softness of the antiperiodic sector (F3), not as a mode or a band topology (F4): canon sings a closed octave. (3) The full −i holonomy is real but lives exactly where the adjudication put it: in the whole-tone reading, as a closure obstruction with spin-structure shape (F5). Framework reading (interpretive, not proven): "time is scale" (§4.11) acquires an operator face; ascending one octave rotates the fixed point's phase by a fixed geometric angle, and the arrow of that rotation is i's arrow.

## Open

- Identify q* ≈ 0.3621π analytically from the beat geometry.
- Whether F3's soft antiperiodic sector connects to a physical measurable (the falsifiable version §8.4 still lacks).
- A whole-tone OPERATOR (strokes anchored to coordinate parity, unit cell 8 octaves = 56 nodes per the flux arithmetic) to see whether the −i flux produces the band braiding that canon lacks.

## Revision history

- 2026-07-18 v1.0: initial (Bloch instrument exact; momentum-carrying chiral fixed point with uniform weights; soft antiperiodic sector; no band braiding in canon; whole-tone flux table exact).
