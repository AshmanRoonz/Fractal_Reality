# T-Operator Findings v17: The Tonic Discriminant

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0

Companion code: `unified_expression_T_v17_tonic_discriminant.py`
Framework context: §27.7t (staggered octave), §27.7o (α and retention), §4.11 (time is scale), v14 (chain, F1), v15 (dome), v16b (F1′, F1″).

## The question

v16b raised a decision the corpus cannot currently answer:

- **§27.7t** says adjacent octaves **share** exactly one station. 3.5D = 0D′. One node. v14 built this.
- **§27.7o** says κ₀,₀ = α is the aperture-to-aperture **bond**, and that α's smallness is what lets a part retain identity: *"if α were order 1, A3 would collapse."*

Sharing a node is κ = ∞, which the corpus names the Inflation Lie. v16b measured the consequence: a formed ⊙ dissolves to the 1/n baseline in ten steps, and α never enters.

v17 builds the rival geometry and prices the swap. **Geometry A**: 7n+1 nodes, tonic welded (v14). **Geometry B**: 8n nodes, each octave's ⟳ and the next octave's • distinct, joined only by a κ bond at α.

## A bug I caught, and it matters

The first version of `retention()` evolved under **F alone**. Geometry B's blocks are *disjoint* in F (all of B's cross-octave coupling lives in κ), so B scored a perfect **1.0000 at every step by construction** while A leaked through its welded node. That is a rigged comparison, not a result. It is recorded here because it would have produced a spectacular false positive for option 1: "α-bonding gives perfect retention!" It does not. Everything below evolves under T = κ ∘ F.

## Findings, graded

**F1 (grade A): α buys a lifetime, not permanence. The end state does not discriminate; the timescale does by ~100x.**

| step | A shared | B split |
|---|---|---|
| 0 | 1.0000 | 1.0000 |
| 10 | **0.1035** | 0.9997 |
| 100 | 0.3982 | 0.9862 |
| 300 | 0.1361 | 0.8923 |
| 1000 | 0.2487 | **0.5171** |
| 3000 | 0.2713 | 0.2747 |
| 30000 | 0.2700 | 0.2148 |

Both converge to **the same dome** (0.270 and 0.215 are their attractors' peak octave shares, not the 0.125 delocalization floor). Neither geometry preserves ⊙λ forever. What changes is how long it holds: A is gone by step 10; B holds past step 300 and half-decays around step 1000, the same order as 1/α = 137.

This is a reading of §27.7o that the corpus does not currently state and might want to: **α does not prevent dissolution. α sets the part's lifespan.** Under that reading the claim survives with its meaning sharpened, and it costs nothing the framework was not already committed to; A2 says a self-limitation that is not maintained collapses, and things do in fact dissolve. Ten pump cycles, however, is not a lifespan. It is the part never existing.

**F2 (grade A, the price): splitting breaks v14's grade-A conservation result.**

| n_oct | A shared (×α) | B split (×α) |
|---|---|---|
| 1 | 0.6446 | 0.6446 |
| 4 | 0.6032 | 0.9820 |
| 8 | 0.7293 | 1.0378 |
| **n=1 → 8** | **+13.1%** | **+61.0%** |

v14's F1 was that tonic-sharing conserves the 1 across unbounded nesting: departure stays flat where tensor nesting compounds. That was the experiment's main positive result. Splitting the tonic costs one κ bond per octave boundary, and κ is exactly where trace preservation departs, so B's departure grows with scale count. **A conserves the 1 but its parts never live. B's parts live but the 1 leaks as you nest.** That is a real dilemma, it is sharp, and it is yours.

**F3 (pre-registered prediction FAILED, and it retracts something I said): the dome is not the weld.**

I predicted B would localize and that v15's dome was an artifact of welding every octave together. Wrong. Normalized IPR: **A = 0.466, B = 0.479.** B is if anything marginally *more* delocalized. Both attractors are the same centered dome:

- A per-octave: [0.016, 0.079, 0.194, **0.278**, 0.270, 0.178, 0.067, 0.013]
- B per-octave: [0.027, 0.093, 0.168, **0.216**, 0.215, 0.165, 0.091, 0.026]

**This retracts the warning at the end of v16b's session note** that "if every tonic is an Inflation point, v15's dome is not an emergent discovery; it is what fusing every adjacent octave was always going to produce." It is not. The dome survives the geometry swap intact. v15's finding stands, and v14's F1 needs no re-reading on those grounds either (though F2 above bears on it directly).

**F4 (the real gap, and it is bigger than the tonic): the chain has no scale parameter.**

Why is the dome robust? Because every octave is an **identical block**, so all octaves are exactly degenerate, and degenerate levels hybridize completely under *any* nonzero coupling, however weak. The dome is a degeneracy effect. α cannot buy localization at any strength; it can only buy time.

But real nesting is not degenerate. A cell and an organism are not the same object at the same rate. **λ is the framework's own name and it is absent from the model.** §4.11 says time IS scale, which means octaves at different scales should run at different clock rates. Detuning them (octave k's engine running at rate (1+δ)^k) lifts the degeneracy, and A's retention at step 40 rises with it:

| detuning δ | A home share @40 | B home share @40 |
|---|---|---|
| 0.00 | 0.1285 | 0.9976 |
| 0.05 | 0.2451 | 0.9995 |
| 0.15 | **0.4775** | 0.9998 |
| 0.35 | 0.4882 | 0.9998 |
| 0.62 | 0.4250 | 0.9997 |

A's retention nearly quadruples from a 15% clock difference between neighbouring octaves. This is a stronger effect on A than the entire shared/split question, and it costs no κ bonds, so it does not touch v14's F1.

## The decision, with numbers attached

| | A: tonic shared (v14) | B: tonic α-bonded |
|---|---|---|
| ⊙λ lifetime | ~10 steps | ~1000 steps (**100×**) |
| conservation of the 1 across n | +13% (**F1 holds**) | +61% (**F1 breaks**) |
| attractor | dome | dome (no gain) |
| α does work? | no (θ/T = 71.8α swamps it) | yes, sets lifespan |

Three ways this can go, and only you can pick:

1. **Split (option 1).** α does the job §27.7o assigns it, parts get a hundredfold lifespan, and you pay by giving up v14's conservation result across scale count. You would need a story for why the 1 leaks as you nest, or a reason the departure growth is acceptable.
2. **Keep the weld, add λ.** The detuning result says most of A's retention problem is degeneracy, not geometry, and scale differentiation is framework-native (§4.11) and free of κ cost. This does not resolve the shared-vs-bonded contradiction; it makes it less urgent by removing its worst symptom.
3. **Both are answering the wrong question.** The chain is a *lineage*, one octave per level, and the real structure branches: ⊙Λ contains many ⊙λ. Sibling ⊙s sharing one parent tonic would all be welded to each other, which forces the bond reading on grounds that have nothing to do with retention. That argument is cleaner than anything measured here and it did not need an operator.

My read, offered as a read and not a verdict: **the tonic question is real but F4 is bigger.** The corpus is named for a scale parameter the model does not contain. Until octaves differ, every result on this chain is a statement about a degenerate lattice, and degeneracy is doing work that is being attributed to geometry.

## Construction choices (conventions, not results)

Both geometries use v9's ℂ⁸ block per octave, identical engine, ascending beat product. B's per-octave κ matches A's (four diameter bonds at α); B adds one tonic bond per boundary at g_tonic = α (sweepable). The formed ⊙ is the leading eigenvector of T on an isolated single octave, identical for both geometries, so the comparison is the same boat in two seas. Detuning is implemented as a fractional matrix power of each beat, which preserves the engine and changes only its rate.

## Revision history

- 2026-07-16 v1.0: initial. F-only retention bug caught and recorded. F1: α buys lifetime not permanence, 100× timescale, same end state. F2: splitting costs v14's F1 (+61% vs +13%). F3: pre-registered prediction failed; dome is not the weld; retracts v16b's session warning about v15. F4: the chain has no scale parameter, degeneracy explains the dome, detuning nearly quadruples A's retention. Decision put to Ashman with three options priced.
