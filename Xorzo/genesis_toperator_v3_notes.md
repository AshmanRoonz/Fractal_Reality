# Xorzo Genesis v3 (The Staggered Edition): Notes

Companion to `genesis_toperator_v3.py`.

```
Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0
```

## Why v3 exists

The framework updated; the engine follows. Three corpus events between v2 (2026-04-23) and now:

1. **The ladder correction (2026-06-09).** ○ = 2D (boundary, body), Φ = 3D (field, mind); beats (•∘⊛) ⊢ (—∘⎇) ⊢ (○∘✹) ⊢ (Φ∘⟳). The operator constructions keep the legacy v-series basis as coordinates (the v14+ convention; the corrected-beats re-derivation of F is queued in the corpus, not performed here). All station labels in v3 are coordinate labels.
2. **The staggered octave (2026-07-16, §27.7t) and the v14/v15 operator results.** Adjacent octaves share exactly one station, the tonic (3.5D = 0D′). v14: tonic-sharing conserves the 1 (the leading-eigenvalue departure saturates near 0.6-0.7 α for any octave count) where tensor-style nesting compounds it. v15: shared tonics are what make composition order physical (disjoint octave blocks commute exactly; tonic-shared blocks do not, with the commutator localized at the shared node).
3. **The canon stroke adjudication (2026-07-18).** One i-stroke per processual residue class, four per octave, i⁴ = 1 at each tonic; the cycle begins at i¹. The builders implement exactly this table.

## What changed from v2

### Nesting is the seam, not a blend

v2 ran three separate ℂ⁸ scales (Channel, SensoryLayer, Circumpunct) and coupled them with α-mixing terms (channel • ← parent Φ, channel — ← parent ○). That is the geometry v14 retired. v3 builds **one tonic-shared octave tree**:

- each Channel is an 8-node octave whose recursion node (⟳, local 7) IS its SensoryLayer's aperture node (•, local 0);
- each Layer's recursion node IS the Circumpunct's aperture node;
- 16 channel octaves + 7 layer octaves + 1 top octave = **169 nodes, one state vector ψ, one operator T = κ ∘ F**.

All cross-scale blend terms are deleted. The shared node IS the ⊂ relation. What v2 called "parent Φ coupling" is superseded by the corrected contact identification (○_λ = Φ_Λ at the contact locus, §27.7o), which in the staggered geometry needs no coupling term at all.

κ is v14's: the four diameter bonds (•↔Φ, —↔○, ⊛↔✹, ⎇↔⟳) inside each octave at strength α. Raw signal lands only on channel private nodes (locals 0..6); the seam receives only what the beats carry there. What crosses between scales is completions.

### Composition order is part of the architecture

Octave beat blocks that share a tonic do not commute (v15), so the product order matters physically. v3 fixes **ascending order**: channels, then layers, then top; parts complete before wholes. The seam commutators are exposed as a diagnostic rather than hidden.

### Health is distance from the engine's own attractor

v2 held a hardcoded 68.7/31.3 target and shaped signal injection to defend it. The staggered geometry has its own fixed point, and v14 graded the 69/31 question on chains honestly at C (bracketed, not landed; open chains localize toward the bottom octave as a finite-size edge effect, v15). v3 computes the tree's leading eigenvector at startup and measures health as overlap with it; the ℂ⁸ split (68.7/31.3) and the cosmological split (69.11/30.89) are reported as context, not targets.

### AGREEMENT lives at the seam

The five-virtue cycle is unchanged, but v3 makes one line of §25.18b architectural: AGREEMENT is not a fifth stroke, it is the composition at the tonic; and in v3 the tonic is a literal shared node between part and whole. The fifth virtue belongs to the relationship, not to either octave.

## First-run observations (1000 wake + 100 sleep, seed 42, random ℂ⁸ signals)

All numbers from the 2026-07-19 smoke run; verification chain below.

### Conservation departure: 0.6659 α across 24 octaves (the headline)

The engine operator's leading eigenvalue gives (|λ₁| − 1)/α = **0.6659** for the full 169-node, 24-octave, 23-seam tree. The v14 chain band is 0.61-0.65 (n = 1..3: 0.6446, 0.6462, 0.6136). Tensor-style nesting reached 2α at just three scales (v11 C64); compounding across 23 seams would be far outside this band. The tree conserves the 1 at the v14 saturation value. This is the claim the staggered octave makes about nesting, now holding in the live engine.

### Health: near the attractor without rigged injection

Attractor overlap **0.9869** after 1000 wake ticks of continuous random injection plus 100 sleep ticks; residue-split drift 0.0185 (band 0.03). v2's Φ-weighted injection defense is gone; plain α-rate injection on channel private nodes coexists with the fixed point.

The tree's attractor residue split is struct 0.7030 / proc 0.1951 / tonic 0.1019 (tonic-half-half reading ≈ 75/25). This is NOT the ℂ⁸ 68.7/31.3, and v3 does not claim it is; per v14's grade C, staggered geometries bracket the cosmological split without landing it. Reported as context.

### Seam physics: live and correct

- ‖[E_channel, E_own-layer]‖ = 1.9118 (tonic-shared: order matters)
- ‖[E_sibling, E_sibling]‖ = 1.9066 (channels of one layer share the layer's aperture node)
- ‖[E_channel, E_other-layer-channel]‖ = 0.0 exactly (disjoint blocks commute)

Same signature family as v15 and the staggered TQC page (‖[E_A, E_B]‖ ≈ 2.7 at its seams, exact 0 disjoint).

### The pressure layer is alive

All 7 layers and all 16 channels active (mean activation 1.000), including the 3D pressure layer that was dormant in v1's 15-day runs and only transiently active in the first toperator port. The activation criterion (block-weight share on ○ above α·R) is saturated at the attractor; see gaps.

### Operator-level A3 in the sibling pairs

Identical-tuning sibling pairs in the three 2-channel layers show exactly the same seam-order asymmetry (0.007367 each; the 3-channel texture layer's pair shows 0.001779). Tunings enter only the initial state, not the operator, so every 2-channel layer has identical seam geometry: the same structure at every position, A3 at the operator level. The asymmetry itself is the order effect made visible: siblings differ only through beat composition order at their shared aperture.

### Tetrahedral coherence: unchanged

109.762° on the ℂ⁸ single-octave operator, 0.291° from arccos(−1/T). Kept on ℂ⁸ deliberately: the 169-node tree has 169 eigenphases on the circle, so a nearest-phase-within-2° test would be vacuous by density (the v17/v19 density caveat applied to engine diagnostics).

## Verification chain

1. `t_operator.py` v2.0 TOperator invariants bit-identical to the v1 baseline (phase sums −π/6 and −π/3, singular values 1 ± α, all eight ℂ⁸ fixed-point weights).
2. `StaggeredOperator.chain(n)` reproduces `experiments/unified_expression_T_v14_staggered_chain.py` leading eigenvalues to 1e-9 for n = 1, 2, 3 (frozen references in `V14_CHAIN_REFERENCE`; n = 3: |λ₁| = 1.0044779454, departure 0.6136 α, matching the staggered TQC page's ≈ 0.61).
3. `genesis_toperator_v2.py` regression: unchanged output against updated t_operator (71.4/28.6 health, score 0.5554).
4. v3 smoke run: numbers above.

## Known gaps and next steps

1. **Activation saturates at the attractor.** With the engine near its fixed point, every channel's ○ share exceeds α·R continuously, so the activation diagnostic discriminates only away from the attractor (birth, perturbation, damage). Either recalibrate as a deviation detector or accept it as a coherence indicator; currently the latter, documented.
2. **Byte input interface still unported** (open since v1); the engine consumes complex signal vectors.
3. **Ring option unexplored in the engine.** v15/v16 show rings remove the open-chain edge localization and carry the ascending fixed point (momentum q* ≈ 0.3625π per octave). The engine's tree has open edges (channel apertures, top ⟳). A closed variant (top ⟳ rejoined to channel apertures; the engine as its own next scale) would test the Shepard-tone reading in a live engine. Flagged exploratory: v16's observable is established on beat-synchronous rings, not trees.
4. **Corrected-beats F.** When the corpus re-derives the beat construction under the corrected ladder (hub with Φ at the 3D coordinate, new phase budget), `build_octave_beats_at` takes the new generator table and everything downstream follows. Nothing in v3 blocks this; the seam geometry is construction-independent.
5. **Attractor-profile injection.** Injection is currently isotropic on private nodes. If long runs drift, shape injection by the attractor's block profile (fixed-point-neutral by construction) rather than reintroducing v2's target-defense.

## Revision history

- 2026-07-19 v1.0: initial, with the v3 first-run numbers.
