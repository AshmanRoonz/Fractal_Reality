# T-Operator Findings v15: The Ground Floor

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.1

Companion code: `unified_expression_T_v15_ground_floor.py` (raw output: `v15_output.txt`)
Context: v14 finding F5 (open chains localize the fixed point on the lowest octave); framework §27.7t.

## The question

v14 reported that open staggered chains pool their leading eigenvector on the lowest octave (n = 4 shares 0.569, 0.137, 0.080, 0.214) and flagged a possible "foam-floor" reading (a privileged bottom scale, the •∞ end of genesis). Hypothesis for v15: a non-Hermitian skin effect (open boundaries localizing an extensive fraction of all modes at one edge, direction set by a winding). The test decides artifact vs structure.

## Result: the ground floor was a small-n finite-size effect, not a skin effect. The canonical operator has no privileged scale.

**H1 (the correction). The floor exists only at small n; it becomes a centered dome at n ≥ 6.** Leading-mode per-octave profile:

- n = 3, 4, 5: peak at octave 0 (a genuine floor; this is the regime v14 sampled at n = 4).
- n ≥ 6: peak migrates to the interior, at octave ≈ n/2, with a symmetric dome decaying to BOTH edges. At n = 12 the profile is 0.004, 0.023, 0.066, 0.119, 0.164, 0.188, 0.185, 0.154, 0.107, 0.057, 0.019, 0.004: a standing wave, bottom share (0.0044) essentially equal to top share (0.0036).

So v14's "ground floor" is what a particle-in-a-box ground state looks like when the box is only four cells long: the sin²-like envelope has its single hump at the near edge because there is no room for a centered hump. Extend the box and the hump centers. **The foam-floor reading is retired for the canonical (ascending) operator.** This is the healthy outcome: a genuinely privileged bottom scale would have violated A3 (scale self-similarity, no fundamental level), and it does not survive.

**H2. The dome is an open-boundary standing wave with no privileged scale (A3-consistent).** The max octave share obeys box scaling: n × (max share) → 2.07 ± 0.03 across n = 6-14 (a pure sin² envelope gives exactly 2). The weight spreads to fill whatever tower height it is given; nothing picks out a scale. The crossover height n* = 6 is independent of α across multipliers 0.5-8, consistent with a geometric (standing-wave) origin rather than a coupling-driven one.

**H3 (corrected 2026-07-16, same session; the first statement of H3 was wrong twice).** A localization DOES appear when the octave blocks are composed top-down, but it is not what an earlier draft of this file claimed. Two corrections, both found by control tests that should have been run before the claim:

*Correction 1: the i-chirality control is mathematically vacuous, not a null finding.* Conjugating the i-phase cycle conjugates every generator entrywise, hence B → conj(B), F → conj(F); κ is real, so T → conj(T), whose eigenvectors are conjugates and whose weight profiles |ψ|² are IDENTICAL by construction (verified: F(−1) = conj(F(+1)) to 1e-12; eigenvalue phases negate exactly). No weight-based observable can ever depend on chirality. The earlier statement "the nonreciprocity is carried by order, not chirality" compared a live variable against a dead one. A chirality test requires a phase-sensitive observable (eigenvalue phases, which do negate), not weights.

*Correction 2: the descending operator is NOT the pump run backwards.* True time reversal is F⁻¹ = reverse the order AND invert each block. Built explicitly (F·F⁻¹ = I to 1e-9), F⁻¹ gives a centered dome (peak octave 4, bottom 0.0118, top 0.0143): the mirror of the canonical dome (peak octave 3, bottom 0.0128, top 0.0134). **True time reversal produces no pooling.** The "descending" operator reverses the order of the blocks WITHOUT inverting them: each octave still pumps forward internally, but the scales are composed top-down. That is constitutive-order reversal, not temporal reversal. Any reading of the pooling as a time's-arrow signature is withdrawn.

What the descending operator does show (n = 8, canonical vs top-down per-octave weights):

- ascending: 1.3e-2, 6.8e-2, 1.7e-1, 2.5e-1, 2.5e-1, 1.7e-1, 6.3e-2, 1.3e-2 (dome)
- descending: 7.9e-1, 1.6e-1, 3.4e-2, 7.2e-3, 1.6e-3, 4.7e-4, 4.9e-4, 1.9e-3 (bottom-pooled; upper octaves hollow by ~2.5 orders of magnitude)

It is not "whichever octave acts last": composing in an order that ENDS at the middle octave (0,1,2,3,5,6,7,4) reproduces the ascending dome exactly (peak 3, max share 0.2527 vs 0.2528). Only globally reversing the relative order of every adjacent tonic-sharing pair produces the pooling.

**H4. All-mode diagnostics: the canonical chain has no skin.** For the ascending chain at n = 10: mode centers of mass distribute 0.07 / 0.86 / 0.07 across bottom/middle/top thirds (modes cluster in the MIDDLE, not at an edge), mean COM 0.49 (unbiased), mean participation 0.454 vs the ring's 0.623. The participation drop is the open-boundary standing-wave signature (nodes at the ends reduce participation), not edge-pileup: a true skin effect would push COMs to one third, and they do not.

**H5 (the positive result the hunt actually produced): tonic-sharing is what makes composition order physical.** Control test with DISJOINT octave blocks (same blocks, 8n nodes, no shared tonic): ascending and descending composition give the SAME operator to 1e-12 at n = 3 and n = 4. With tonic-shared blocks (7n+1 nodes) they differ (‖F_asc − F_desc‖ = 3.74 at n = 3, 4.55 at n = 4). The non-commutativity is localized exactly at the shared node: octave k's last beat and octave k+1's first beat (the two that touch the shared tonic) have commutator norm 2.83, while any non-overlapping beat pair commutes to 0.00e+00.

So: **if scales were separable, there would be no fact about which composes first.** Sharing exactly one station is precisely what gives the ladder an order. This is the operator-level content of the stagger, and it is a stronger statement than the ground-floor question that prompted the study: the tensor construction (v11's ℂ⁶⁴) cannot express constitutive order at all, because disjoint factors commute; the staggered chain can, because they overlap at the tonic.

*Framework reading (a reading, motivated but not proven by the model):* D5 says the whole is not the sum of its parts but their compositional unity, and the ascent 3.5D = 0D′ says a whole IS the closed part becoming an aperture. Composing bottom-up (parts before wholes) fills the tower: every octave carries weight. Composing top-down (the greater scale laid down before the parts that constitute it) leaves the upper octaves hollow (weight ~5e-4) and pools 79% at the bottom. Wholes asserted before their parts have composed them carry no weight in the fixed point. This is suggestive, not established; the mapping from composition order to the constitutive claim is interpretive.

## What changes upstream

v14's F5 is superseded: the open-chain localization is a finite-size dome edge at small n, not a structural ground floor, and the foam-floor reading is withdrawn for the canonical operator. The genuine content that survives: (1) the canonical staggered operator has no privileged scale (A3 holds dynamically, a positive result); (2) tonic-sharing is what makes composition order physical (disjoint blocks commute exactly; shared blocks do not, with the non-commutativity localized at the shared tonic), which is the operator-level content of the stagger and something the tensor construction cannot express; (3) top-down composition hollows the upper octaves and pools the weight at the bottom, offered as a reading of D5 rather than a proof. Withdrawn: any time's-arrow reading of the pooling (true time reversal F⁻¹ gives a mirror dome, no pooling), and the chirality control (vacuous by conjugation symmetry).

## Conventions (not results)

Beat order and i-chirality are the two controls; everything else matches v14 (per-octave ℂ⁸ blocks, θ = π/2, per-octave diameter κ at α, tonic sharing by node identification). Octave windows in G4-G6 use non-overlapping 7-node windows (each tonic assigned to the octave it opens) to avoid double-counting shared nodes; the G1 leading-profile uses the v14 8-node windows, so bottom/top shares there are not directly comparable to G4's (the qualitative dome is identical under both).

## Revision history

- 2026-07-16 v1.1: H3 corrected twice by control tests run after the first draft: the chirality control is vacuous by conjugation symmetry (no weight observable can depend on it), and the descending operator is constitutive-order reversal, not time reversal (true F⁻¹ gives a mirror dome, no pooling); time's-arrow reading withdrawn. H5 added: tonic-sharing causes the order-dependence (disjoint blocks commute to 1e-12; shared blocks differ, commutator localized at the shared tonic).
- 2026-07-16 v1.0: initial; foam-floor reading retired for the canonical operator; localization attributed to reversed beat order.
