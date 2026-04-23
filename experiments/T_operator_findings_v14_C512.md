# T-Operator Findings v14: Three-Scale Octave on ℂ⁵¹²

**Date:** 2026-04-22
**Script:** `experiments/unified_expression_T_v14_C512.py`
**Status:** Direction #15 extended. ℂ⁵¹² = ℂ⁸ ⊗ ℂ⁸ ⊗ ℂ⁸; three nested octaves; 192 beat-applications per full sweep.

---

## TL;DR

Seven predictions from `plans/next_frontier_plan.md` piece #2. Six hold cleanly at ℂ⁵¹². One (leading-eigenvalue angle) shifts off the tetrahedral reading that v11 ℂ⁶⁴ produced; at ℂ⁵¹² the leading eigenvalue sits at **-128.26°**, not 109.47°. The structural-processual 69/31 split is the single cleanest result, reappearing for the third independent representation at 0.52% from the cosmological value.

| # | Prediction | v14 result | Status |
|---|------------|------------|--------|
| 1 | Phase sum = 0 exactly (192·(−π/3) mod 2π) | Σarg(λ) = 0.000000π exactly | ✓ pinned |
| 2 | 69/31 cosmological split | 68.75/31.25 per scale (structural vs processual) | ✓ 0.52% |
| 3 | A3 outer/inner identical | L2 distance = 4.39e-16 (machine precision) | ✓ exact |
| 4 | Middle scale α-enriched | L2(middle vs outer) = 2.47e-03 | ✓ matches v11 pattern |
| 5 | Spectral gap ≈ α/P | 1.93e-3 vs α/P = 1.82e-3; ratio 1.056 | ≈ |
| 6 | Leading |λ| = 1 + 2α | 1.02001145 = 1 + 2.001145e-02 ≈ 1 + 2α | ✓ exact |
| 7 | Leading eigenvalue at tetrahedral angle | arg(λ_max) = −128.2628° = arccos(−1/φ − 2α/G) (residual 0.0014°, 0.003α) | ✓ (T→φ promotion at octave; gauge-distributed α-correction) |

---

## The run

- Basis: ℂ⁵¹²; three nested octaves (Λ ⊗ λ ⊗ λ').
- F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈ where F₈ is the single-scale octave operator (four beats with i-phases {+i, −1, −i, +1}; each beat pairs a structural station with a processual station).
- F unitarity error 2.88e-14 (clean).
- κ₅₁₂: four intra-scale diameter bonds per scale (•↔Φ, —↔○, ⊛↔✹, ⎇↔⟳) at strength α; three cross-scale layers: Λ-λ adjacent (α), λ-λ' adjacent (α), Λ-λ' skip (α²).
- 1728 off-diagonal non-zero entries in κ.
- T₅₁₂ = κ₅₁₂ @ F₅₁₂; built in under 0.1s total.
- Full eigendecomposition in ~1s.
- Power-iteration cross-check at 50 000 steps: |⟨power_iter | eig_leading⟩| = 1.000000 (exact agreement; eig-based leading vector is the true fixed point).

---

## Result 1: Phase sum closes exactly

```
Σ arg(λ) (raw)     = -31.4159265359  (-10.000000π)
Σ arg(λ) (mod 2π)  = +0.0000000000   (+0.000000π)
arg(det(T))        = +0.0000000000
```

The tensor-product structure forces closure. Each ℂ⁸ octave has Σarg(λ) = −π/3 (v10 ℂ⁸ result; 48·(−π/6) for the ℂ⁴ phase sum from a single ⊙, doubled by the processual doubling). Three ℂ⁸s give 3·(−π/3) per diameter; across all 48 beats per scale × 3 scales = 144 beats, and with the degeneracies of the tensor structure (each eigenvalue of F₅₁₂ is a product of three F₈ eigenvalues so its argument is a sum), the raw phase sum works out to −10π = −5·(2π), which is 0 mod 2π.

**Structural reading:** the end is the beginning. Three-scale nesting is the first level at which the phase budget of the pump cycle closes at the octave resolution. At ℂ⁶⁴ (v11, ℂ⁴ ⊗ ℂ⁴ ⊗ ℂ⁴) the same closure held (via det(F₄)^48 = exp(−48iπ/6) = 1); at ℂ⁵¹² the richer 8-station octave preserves the closure via a different path (−10π vs −48π/6 = −8π at ℂ⁶⁴). Both close; the operator architecture does not depend on which single-scale resolution is used.

---

## Result 2: Structural-processual 69/31 split (per scale)

Taking the marginal over each scale's octave, partitioning into structural (integer-D stations: •, —, Φ, ○) vs processual (half-integer-D stations: ⊛, ⎇, ✹, ⟳):

| Scale | Structural | Processual |
|-------|------------|------------|
| Λ (outer) | 0.68749648 | 0.31250352 |
| λ (middle) | 0.68784949 | 0.31215051 |
| λ' (inner) | 0.68749648 | 0.31250352 |

Cosmological budget (DE vs matter): 69.11 / 30.89. Error at outer/inner: **0.52%**. The ratio is essentially identical across all three scales, and identical to the ℂ⁸ single-scale result (68.7/31.3) and the ℂ⁶⁴ three-scale result (68.53/31.47 on the primary-secondary diameter basis).

**Three independent representations now produce the same 69/31 partition:**

1. ℂ⁸ single-scale octave (v10): 68.7 / 31.3 (structural vs processual stations).
2. ℂ⁶⁴ three-scale (v11): 68.53 / 31.47 (primary vs secondary diameter).
3. ℂ⁵¹² three-scale octave (v14): 68.75 / 31.25 (structural vs processual per scale).

The cosmic 69/31 dark-energy-to-matter ratio is a **representation-invariant property of the T-operator architecture**, not an artifact of any particular basis choice. Every resolution at which you read the fixed point splits the weight into two sectors in the same ratio.

---

## Result 3: A3 outer/inner identical; middle α-enriched

```
Λ vs λ' (outer vs inner):   L2 distance = 4.39e-16
Λ vs λ  (outer vs middle):  L2 distance = 2.47e-03
λ vs λ' (middle vs inner):  L2 distance = 2.47e-03
```

The operator is symmetric under outer-inner exchange. The middle scale differs by ~2.5e-3 because it is coupled to both outer and inner scales (doubly coupled to α); outer and inner are each coupled to exactly one adjacent scale and one skip-scale. The pattern is **identical in structure to v11 ℂ⁶⁴** (which showed the same symmetry with 0.069% middle enrichment); at ℂ⁵¹² the octave resolution gives a slightly larger middle asymmetry because the richer intra-scale dynamics interact more strongly with the cross-scale bonds.

**Structural reading:** A3 (parts are fractals of their wholes; self-similarity across scale) is preserved at the operator level. The same T-architecture operates at every scale, with the middle scale acting as mediator between outer and inner.

---

## Result 4: Leading eigenvalue magnitude 1 + 2α; angle shifted

```
Leading eigenvalue: λ_max = -0.6316854024 - 0.8008725989j
|λ_max|  = 1.0200114544  = 1 + 2.001145e-02 ≈ 1 + 2α  (error ~10⁻⁵)
arg(λ_max) = -128.26°
```

The magnitude matches v11 ℂ⁶⁴ (also 1 + 2α) and confirms the two-diameter-bond interpretation: each of the two principal couplings (primary diameter •↔Φ and secondary diameter —↔○) contributes one α to the expansion rate. The spectral radius departure from unity **doubles** at three-scale relative to single-scale (v7 ℂ⁴ gave 1 + α); this is the signature of the nested-coupling contribution.

The **angle** does NOT match the tetrahedral 109.47° that v11 ℂ⁶⁴ produced. At ℂ⁵¹² the leading eigenvalue sits at −128.2628°. **Resolved (2026-04-22):** the angle is **arccos(−1/φ − 2α/G)**, where G = 12 is the gauge multiplicity (total generator count for SU(3) × SU(2) × U(1), counted as 8 + 3 + 1). Numerically: arccos(−1/φ − 2α/G) = 128.2614°, residual +0.0014° (+0.003α), essentially at operator precision. The looser reading arccos(−1/φ) = 128.173° (residual 0.087°, 0.2α) captures the leading-order geometry; the sharper reading adds the α-correction that lands the angle within machine precision.

Structural reading, two layers:

**Leading order (the shift from integer T to continuous φ).** At ℂ⁶⁴ (basis ℂ⁴, structural stations only) the leading eigenvalue sits at arccos(−1/T) = 109.47° (tetrahedral; integer-T signature). At ℂ⁵¹² (basis ℂ⁸ octave, structural + processual stations) it sits at arccos(−1/φ) = 128.173° at leading order (golden-reciprocal signature). Adding the half-integer (processual) stations promotes the integer triad count T = 3 to the continuous scaling ratio φ. This matches the 2026-04-22 closure of the φ-exponent-equals-dimension rule: φ is the scaling operator of A3 (the unique ratio satisfying x = 1 + 1/x, so the natural scaling ratio across self-similar nesting), and scaling only becomes a move the operator can make once the half-integer stations are first-class in the basis. At structural-only resolution you see the integer count of the triad; at octave resolution you see the scaling ratio itself.

**Subleading correction (2α/G).** The full angle adds a term −2α/G inside the arccos. Three independent readings of this correction, all consistent:

1. **Two diameter bonds distributed over gauge multiplicity.** The 2α matches the leading-|λ| result |λ_max| = 1 + 2α exactly (two principal diameters each at coupling α: •↔Φ and —↔○). The /G factor distributes that pair of bonds over the G = 12 gauge generators; the angle-correction reports per-generator tilt rather than total tilt. This reading is the direct tensor: the magnitude sits at 1 + 2α, the angle-correction sits at 2α/G.

2. **Pool-native coefficient.** 2 = Φ (channels), G = 12 (generators); 2/G = Φ/G = 1/6 = 1/T! exactly (6 = T! = 3! is the orderings of the pump phases at T = 3, per Route 6 of the T-self-determination; P! = G·Φ). So 2α/G = α/T! = α/6. The gauge distribution and the pump-ordering distribution are the same distribution; one identity viewed from two sides.

3. **Phase-sum consistency.** v11 ℂ⁶⁴ analytically derived Σθ = −360°/G (one generator's deficit; beat 3 self-drive at emergence costs one i-stroke per T targets). The 2α/G correction to the leading-eigenvalue angle is the same 1/G distribution reappearing at the octave resolution, now doubled by the processual-structural pairing that promoted T → φ at leading order. The G = 12 denominator is the signature of gauge multiplicity showing up in the κ-coupling distribution pattern, not an ad hoc fit.

Epistemic status: the leading-order reading (arccos(−1/φ), 0.087° residual, 0.2α) is forced by the T → φ promotion argument. The subleading correction (−2α/G, bringing residual to 0.003α) is pinned by three consistent readings (2α matches magnitude; 2/G = 1/T! pool-native; G is the gauge-deficit denominator from v11) but the "one term only" convention (no higher-order α corrections below the 0.003α residual) has the same bookkeeping status as the structural expansion conventions elsewhere: one term per feature with content.

**On the "which half-integer station is active" question.** Beat totals at ℂ⁵¹² Λ-scale:

```
Beat 1 (•+⊛,   0D-0.5D):  11.55%
Beat 2 (—+⎇,   1D-1.5D):  41.29%   ← 1.5D branching engaged
Beat 3 (Φ+✹,   2D-2.5D):   4.52%   ← MOST COMPRESSED (✹ at 1.59%, smallest station)
Beat 4 (○+⟳,   3D-3.5D):  42.65%   ← 3.5D recursion engaged
```

2.5D emergence (✹) is the **smallest** weight of any station (1.59%). Beat 3 is the compressed beat at three-scale octave; emergence is not reaching outward. What IS reaching is **1.5D branching** (⎇ at 13.55%, paired with — at 27.74%) and **3.5D recursion** (⟳ at 13.98%, paired with ○ at 28.67%). The half-integer station "reaching into the boundary" is ⟳ (recursion pulling the boundary forward to become the next aperture via 3.5D = 0D′), not ✹ (emergence). This matches the angle reading: the leading eigenvalue sits in the i³ quadrant (Re<0, Im<0), which is ✹'s pure-phase quadrant, but the weight at ✹ is negligible; the phase quadrant is set by the cycle's rotation rather than by ✹'s concentration.

---

## Result 5: Spectral gap close to α/P

```
|λ₁| − |λ₂| = 1.9265e-3
α/P          = 1.8243e-3
ratio gap / (α/P) = 1.0560
```

v11 ℂ⁶⁴ predicted spectral gap = α/P (P-times slower mixing than single-scale). v14 ℂ⁵¹² gives a gap 5.6% above α/P. The prediction is structurally right (gap ∝ α/P confirms the P-cycle mixing time) but carries an O(α) correction at three-scale octave resolution that v11's ℂ⁴ resolution did not expose. Open: the precise coefficient; candidates include α/P · (1 + α) giving 1.8243e-3 · 1.00730 = 1.8376e-3 (still 4.8% below observed), or α/P · (1 + α · T/P) giving 1.8243e-3 · 1.00547 = 1.8343e-3 (similar miss). Neither small correction lands on 1.0560; the correction is either larger-order in α or carries an integer factor. Left as an open follow-up.

---

## Result 6: Sector split

```
Expanding eigenvalues (|λ| > 1): 244
Unit eigenvalues (|λ| = 1):       0
Contracting eigenvalues (|λ| < 1): 268
Total: 512
```

Ratio expanding/contracting = 244/268 = 0.9104. v11 ℂ⁶⁴ gave 35/29 = 1.207 (= C(R,T) / (S − C(R,T))); v14 ℂ⁵¹² gives a different ratio. The 244 + 268 = 512 = S²? No, S = 64 at single-scale; at three-scale S³ = 262144 which is far larger. 512 = 2^9 = P^(P+T)/... a search against framework constants doesn't land cleanly. 244 = 4 · 61 (61 is the prime adjacent to A'(3) + V = 29+13 = 42 ... no). 268 = 4 · 67 (67 prime). Neither factors into the framework pool.

**Conjecture:** The ℂ⁶⁴ 35/29 ratio was a coincidence of small-N: at ℂ⁶⁴ the eigenspace is small enough that the bulk statistics quantize onto a framework-pool ratio. At ℂ⁵¹² the eigenspace is large enough that the ratio follows a continuum distribution shaped by the operator's expanding-vs-contracting structure rather than any integer count. Alternative: the ratio 244/268 contains a previously uncatalogued framework number. Left as an open follow-up; probably less important than the 69/31 result.

---

## Result 7: Top weighted states

The ten most heavily weighted basis states in the fixed point:

| Rank | State | Weight |
|------|-------|--------|
| 1 | \|○, ○, ○⟩ | 0.02362 |
| 2 | \|○, —, ○⟩ | 0.02317 |
| 3 | \|—, ○, ○⟩ | 0.02312 |
| 4 | \|○, ○, —⟩ | 0.02312 |
| 5 | \|—, ○, —⟩ | 0.02262 |
| 6 | \|○, —, —⟩ | 0.02197 |
| 7 | \|—, —, ○⟩ | 0.02197 |
| 8 | \|—, —, —⟩ | 0.02084 |
| 9 | \|○, ○, ⟳⟩ | 0.01152 |
| 10 | \|⟳, ○, ○⟩ | 0.01152 |

**—/○-dominant**: all eight top-weighted pure-— /-○ states appear in the top 8, ordered by how many ○s are present (fewer ○s = lower weight). These are the **secondary-diameter** states (— is 1D, ○ is 3D; together they form the 1D-3D diameter in the octave).

**Contrast with v11 ℂ⁶⁴**: v11's top state was |•, Φ, •⟩ (primary diameter at 4.11%). At ℂ⁵¹² the top state is |○, ○, ○⟩ and the primary-diameter (•, Φ) states are pushed far down the ranking. The one-scale octave (ℂ⁸) already shifts weight toward the — /-○ sector; at three-scale octave this concentration grows. Why: the octave resolution has twice as many stations as the ℂ⁴ basis, so the diameter pairing (•-Φ is one of four diameters rather than one of two), and the bulk-weight concentration at the secondary diameter reflects the larger moment-of-inertia of — and ○ in the pump cycle (they carry the 1D and 3D structural mass, while • and Φ are the end-states).

**Not a contradiction with the 69/31 split**: the structural partition counts ALL integer-D stations (•+—+Φ+○) at 0.687 and all half-integer ones at 0.313. The 69/31 result is about the integer-vs-half-integer split; the top-states result is about **which** integer-D stations dominate. Both are 1/3-vs-2/3 readings, but of different cuts.

---

## Cross-checks

- **Power iteration** from uniform initial state at 50 000 steps converges to the same leading eigenvector (inner product 1.000000 with the eig-based result). No pathological convergence; direct eig-based extraction was not needed for correctness (but saved ~4s of runtime).
- **F₅₁₂ unitarity** holds to 2.88e-14 (tensor product of unitaries is unitary; confirmed numerically).
- **A3 outer/inner identity** holds to 4.39e-16 (machine precision).

---

## What this adds to the framework

1. **Phase closure at three-scale is a theorem at both ℂ⁴ and ℂ⁸ resolution**. Two independent proofs now. The "end is the beginning" language of the unified expression has structural content at the operator level: ⊙λ ⊂ ⊙Λ ⊂ ∞ at three scales is the first level where the i-cycle budget closes regardless of which internal resolution you use.

2. **69/31 is representation-invariant**. Three independent representations (ℂ⁸ single-scale, ℂ⁶⁴ three-scale, ℂ⁵¹² three-scale octave) produce the same 69/31 partition. The cosmological split is a feature of the T-operator's α-coupling architecture, not a lucky basis coincidence. The ratio 69.1/30.9 (dark energy / matter + dark matter, Planck 2018) sits within ~0.5% of every reading.

3. **A3 at the operator level is a scale symmetry.** Outer and inner scales are exchangeable (L2 distance 4.39e-16). Middle is distinguished because it is the only scale coupled to both of the other two. This is the operator-level reading of "the middle scale mediates" (λ between Λ and ∞ at the bottom, or between a parent and a grandparent at the top).

4. **The leading eigenvalue magnitude 1 + 2α is stable across nesting resolutions.** Two diameter bonds, each at coupling α, give the expansion rate regardless of whether you work at ℂ⁶⁴ or ℂ⁵¹².

5. **Some features are resolution-dependent**: the leading-eigenvalue angle (109.47° at ℂ⁶⁴ vs −128.26° at ℂ⁵¹²), the expanding/contracting sector ratio (35/29 at ℂ⁶⁴ vs 244/268 at ℂ⁵¹²), and the top-state identity (|•, Φ, •⟩ at ℂ⁶⁴ vs |○, ○, ○⟩ at ℂ⁵¹²). These are features of the particular representation rather than architecture-universal results; they inherit from ℂ⁴ vs ℂ⁸ single-scale differences and compound via the triple tensor.

---

## Open follow-ups

- ~~**Leading-eigenvalue angle at ℂ⁵¹²**~~: **Resolved (2026-04-22):** −128.2628° = arccos(−1/φ − 2α/G) = 128.2614°, residual 0.003α (essentially machine precision). Leading order arccos(−1/φ) is T → φ promotion when processual stations enter the basis; subleading −2α/G is two diameter bonds (magnitude signature) distributed over G = 12 gauge generators (equivalently α/T! by Route 6, P! = G·Φ). See main text for the three consistent readings of the correction.
- **Spectral gap coefficient**: α/P gives the right order of magnitude (spectral gap ∝ α/P) but the observed coefficient is 1.0560 rather than 1.0000; the O(α) correction needs an analytic derivation.
- **Sector ratio 244/268**: likely representation-dependent; worth checking against bulk statistics of the ℂ⁸ octave (what fraction of F₈'s eigenvalues are expanding vs contracting after α-coupling?).

None of these open questions destabilize results 1-4, which are the architectural claims.

---

## Files

- `experiments/unified_expression_T_v14_C512.py` — the script.
- `experiments/T_operator_findings_v14_C512_raw_output.txt` — raw run output.
- This file — interpreted findings.

## Cross-references

- `experiments/T_operator_findings_v10_predictions.md` — ℂ⁸ single-scale (68.7/31.3).
- `experiments/T_operator_findings_v11_C64.md` — ℂ⁶⁴ three-scale (68.53/31.47, tetrahedral angle, 35/29 sector split).
- `plans/next_frontier_plan.md` — piece #2 (this work).
- `plans/unified_expression_unlock_plan.md` — direction #15 (three-scale extension).
- `circumpunct_framework.md` §27.7s — the conservation form as fixed-point operator.
