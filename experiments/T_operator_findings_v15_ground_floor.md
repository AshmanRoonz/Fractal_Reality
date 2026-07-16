# T-Operator Findings v15: The Ground Floor

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0

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

**H3. There IS a real skin effect, but only under reversed (descending) beat order, and it is order-set, not chirality-set.** Direction controls (G3, G5):

- Ascending beat order (canonical; octave 0's beats act first): dome, floor share ≈ top share. No skin.
- Descending beat order (octave n−1 first): true exponential edge-localization at the bottom, decay length 0.64 octaves, bottom octave 0.79 of the weight. A clean non-Hermitian skin effect.
- i-stroke chirality (conjugating the i-phase cycle): NO effect on the floor in either order. The nonreciprocity is carried by the temporal order in which the pump lays down octaves, not by the sign of the i-cycle.

Reading: the pump has a direction (the framework's arrow of time, i² = −1 irreversibility), and applying it in its canonical ascending sense produces a bulk standing wave, while applying it against its sense dams the 1 at the floor. The skin effect is the operator's way of saying the pump order is physical; it is not a statement about a privileged scale, but about a privileged direction.

**H4. All-mode skin diagnostics confirm the picture.** For the ascending chain at n = 10: mode centers of mass distribute 0.07 / 0.86 / 0.07 across bottom/middle/top thirds (modes cluster in the MIDDLE, not at an edge), mean COM 0.49 (unbiased), mean participation 0.454 vs the ring's 0.623. The participation drop is the open-boundary standing-wave signature (nodes at the ends reduce participation), not edge-pileup: a true skin effect would push COMs to one third, and they do not. The descending operator is where the COMs would pile; that regime is the skin phase.

## What changes upstream

v14's F5 is superseded: the open-chain localization is a finite-size dome edge at small n, not a structural ground floor, and the foam-floor reading is withdrawn for the canonical operator. The genuine content that survives: (1) the canonical staggered operator has no privileged scale (A3 holds dynamically, a positive result), and (2) the pump order is physical, isolable as a skin transition when the beats are applied against their canonical sense.

## Conventions (not results)

Beat order and i-chirality are the two controls; everything else matches v14 (per-octave ℂ⁸ blocks, θ = π/2, per-octave diameter κ at α, tonic sharing by node identification). Octave windows in G4-G6 use non-overlapping 7-node windows (each tonic assigned to the octave it opens) to avoid double-counting shared nodes; the G1 leading-profile uses the v14 8-node windows, so bottom/top shares there are not directly comparable to G4's (the qualitative dome is identical under both).

## Revision history

- 2026-07-16 v1.0: initial; foam-floor reading retired for the canonical operator; skin effect isolated to reversed beat order.
