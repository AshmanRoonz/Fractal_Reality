# T-Operator Findings v13: Uniformity Sweep (v12 → v11)

**Date:** April 2026
**File:** `experiments/unified_expression_T_v13_uniformity_sweep.py`
**Depends on:** v11 (uniform hub, physics match), v12 (beat-native, clean singular values)

## The question

v11 has uniformly-coupled beat generators that produce the cosmological 69/31 split, the tetrahedral 109° leading-eigenvalue phase, and the C(R,T) = 35 expanding/contracting count at ℂ⁶⁴; but its ℂ⁴ singular values fit (1±α)² rather than the structurally clean (1±α). v12 has beat-native generators that give exact (1±α) singular values but lose the 69/31 split (reads 77/23), the tetrahedral phase (reads 74°), and the C(R,T) expanding count (reads 31/33).

v13 asks: can a single interpolation dial between the two constructions move all four readouts simultaneously, and if so, does one value of the dial hit all the targets or do they separate?

## Construction

For each beat k ∈ {1, 2, 3, 4}, define the generator blend:

```
G_k(μ) = (1 − μ) · G_v12,k  +  μ · G_v11,k
U_k(μ) = expm( antiherm( G_k(μ) ) )
F(μ)   = U_4(μ) U_3(μ) U_2(μ) U_1(μ)
```

μ = 0 reproduces v12 exactly; μ = 1 reproduces v11 exactly. κ is unchanged (diameter bonds at strength α).

**Phase budget invariance along the dial.** Only beat 3 contributes to trace, and both v11 and v12 put G[Φ, Φ] = −iπ/6 on the Φ diagonal. Linear interpolation preserves that diagonal entry, so for every μ:

```
Tr(G_3(μ)) = −iπ/6   ⇒   det(U_3(μ)) = exp(−iπ/6)
det(F(μ)) = exp(−iπ/6)
det(F_64(μ)) = det(F(μ))^48 = 1
```

The total ℂ⁶⁴ phase sum is zero for every μ. Confirmed numerically: |ps64 mod 2π| ≤ 6e-15 across the sweep.

**A3 symmetry invariance.** κ is unchanged and F(μ) = F(μ) ⊗ F(μ) ⊗ F(μ) is structurally symmetric between the outer and inner scales for every μ. Confirmed: ||Λ weights − λ' weights|| ≤ 1e-15 across the sweep.

## Coarse sweep (μ ∈ {0.0, 0.1, ..., 1.0})

| μ | |λ|max (ℂ⁴) | expanding | lead° | •+Φ % | A3 dist |
|---|---|---|---|---|---|
| 0.00 (v12) | 1.00328 | 31 | +73.90 | 76.95 | 5.3e-16 |
| 0.10 | 1.00353 | 33 | +65.42 | 71.80 | 4.5e-16 |
| 0.20 | 1.00344 | 35 | +56.89 | 68.60 | 3.4e-16 |
| 0.30 | 1.00316 | 35 | +49.35 | 66.59 | 1.3e-16 |
| 0.40 | 1.00276 | 34 | +43.25 | 65.28 | 4.9e-16 |
| 0.50 | 1.00230 | 35 | +38.75 | 64.42 | 7.4e-16 |
| 0.60 | 1.00179 | 35 | +35.83 | 59.05 | 1.1e-15 |
| 0.70 | 1.00126 | 36 | +34.39 | 50.34 | 7.6e-16 |
| 0.80 | 1.00140 | 36 | +67.92 | 54.30 | 5.0e-16 |
| 0.90 | 1.00177 | 35 | +85.83 | 62.46 | 3.9e-16 |
| 1.00 (v11) | 1.00220 | 35 | +108.96 | 68.55 | 1.1e-16 |

Phase sum (ℂ⁶⁴, mod 2π) stays within machine precision across every row.

## Fine sweep in μ ∈ [0.10, 0.30]

| μ | exp | lead° | •+Φ % |
|---|---|---|---|
| 0.130 | 35 | +62.80 | 70.68 |
| 0.150 | 35 | +61.08 | 70.01 |
| 0.170 | 35 | +59.38 | 69.41 |
| 0.180 | 35 | +58.54 | 69.13 |
| 0.181* | 35 | +58.45 | 69.11 |
| 0.190 | 35 | +57.71 | 68.86 |
| 0.200 | 35 | +56.89 | 68.60 |
| 0.220 | 35 | +55.28 | 68.13 |
| 0.250 | 35 | +52.96 | 67.49 |
| 0.280 | 35 | +50.75 | 66.93 |
| 0.300 | 35 | +49.35 | 66.59 |

**μ* ≈ 0.181** lands •+Φ = 69.11% (the measured dark-energy fraction) to the reported precision. The C(R,T) = 35 expanding count is stable across μ ∈ [0.13, 0.30], comfortably covering μ*.

## Fine sweep in μ ∈ [0.90, 1.00]

| μ | exp | lead° | •+Φ % |
|---|---|---|---|
| 0.900 | 35 | +85.83 | 62.47 |
| 0.950 | 35 | +96.87 | 65.80 |
| 0.970 | 35 | +101.59 | 66.97 |
| 0.990 | 35 | +106.47 | 68.05 |
| 1.000 | 35 | +108.96 | 68.55 |

The leading phase rises toward 109.47° as μ → 1 but does not reach it within [0, 1]. Linear extrapolation of the μ = 0.99 → 1.00 segment (slope ~2.49°/0.01μ) places the tetrahedral crossing at μ ≈ 1.002, just outside the dial range. At exact v11 (μ = 1.00) the leading phase is 108.96°, 0.51° short of the tetrahedral angle; this 0.51° gap is a property of the operator at the v11 endpoint, not something the blend can fix.

## Three targets, three μ values

| Target | Value | μ that hits it |
|---|---|---|
| •+Φ = 69.11% (cosmological DE fraction) | 69.11% | **0.181** |
| expanding = C(R, T) = 35 | 35 | stable across [0.13, 0.30] (includes 0.181) |
| leading phase = arccos(−1/T) = 109.47° | 109.47° | not reached; nearest is 108.96° at μ = 1.00 |

The cosmological split and the combinatorial expanding-count are co-located at μ ≈ 0.181, which is far from v11 and reachable with only a small amount of uniform-hub mixing into the beat-native skeleton. The tetrahedral leading-eigenvalue phase is a separate phenomenon that lives only at the v11 extreme.

## Reading of the result

**The beat-native construction needs only ~18% uniform-hub mixing to land the cosmological split.** That is not a lot. Structurally, it says the primary-diameter enrichment is mostly carried by the beat-native topology (beat 3's asymmetric Φ↔• and Φ↔○ couplings, beat 4's closure loop, beat 2's Y-fork), and a small global homogeneity term is enough to tune the fine balance from 77% down to 69%.

**The C(R, T) expanding count is structurally robust across most of the dial.** It sits at 35 for μ ∈ [0.13, 0.30] and from μ ≈ 0.50 onward almost continuously (with brief excursions to 34 or 36 at isolated points, consistent with eigenvalues crossing the |λ| = 1 circle near μ-boundaries). This suggests C(R, T) is a combinatorial consequence of the 64-dimensional structure with α-coupled nesting, not a delicate feature of the uniform hub.

**The tetrahedral leading phase is a v11-only signature.** Across μ ∈ [0, 0.9] the leading phase stays below 90° and is not approaching 109° monotonically; the climb to 109° happens in the last 10% of the dial. There is also a discontinuity between μ = 0.7 and μ = 0.8 (phase jumps from 34° to 68°), indicating the leading mode swaps identity as the uniform-hub mixing becomes dominant. The tetrahedral match at v11 is the specific phase of whichever mode wins the magnitude competition at μ = 1; at μ ≈ 0.181 a different mode leads, with phase ~58°.

## Interpretation options

**Position (1): μ ≈ 0.181 is the correct operator.** The cosmological split and the C(R,T) expanding count are both carried at this μ with the cleanest beat-native skeleton. The tetrahedral leading-phase match in v11 is a coincidence of the uniform-hub construction at μ = 1; the real operator lives near μ = 0.18 and does not carry the tetrahedral signature as its leading phase. The framework reads this as: the primary-diameter enrichment and the combinatorial eigenvalue split are fundamental; the molecular-geometry angle lives elsewhere in the system (in bond-angle predictions at the molecular scale, not in the leading eigenvalue of T₆₄).

**Position (2): μ = 1 is correct and v13's intermediate μ is an accident.** The tetrahedral leading phase is the deeper signature because it ties the 64-state operator directly to the observer-triad (arccos(−1/T) = 109.47° is T = 3 made geometric). The beat-native skeleton is structurally cleaner for the ℂ⁴ singular values but structurally incomplete for the three-scale leading mode. Accept the (1±α)² singular values as the cost of carrying the tetrahedral phase.

**Position (3): no single μ is correct; the framework needs two independent couplings.** The 69/31 split and the tetrahedral phase are separate physics that require separate tuning. A v14 construction would give beat 3 two independent couplings (one for the primary-diameter enrichment, one for the tetrahedral leading mode) and show that both targets can be hit simultaneously only with two-dimensional parameter freedom, not one.

**Currently preferred:** position (1). The 0.51° gap between v11's leading phase (108.96°) and the tetrahedral target (109.47°) was already not an exact match; it was a "close match," which is what reviewers would call a fit, not a derivation. The 69.11% cosmological target is met at μ = 0.181 to the 0.02-point level, which is a much tighter hit. If forced to choose one signature for the leading eigenvalue to carry, the cosmological split is the stronger claim.

## What to take to v14

1. **Pin μ = 0.181 as the default operator** and report v11 (μ = 1) as a limiting case for comparison. Rename the master construction as `T_v13[μ = 0.181]` rather than treating v12 or v11 as canonical.

2. **Rebuild the ℂ⁸ single-scale and ℂ⁵¹² three-scale octaves with the μ = 0.181 mixing.** Check whether the v10 "68.7/31.3 structural vs processual" split persists and whether the ℂ⁵¹² phase closure still holds (should, by the same tensor-product argument that works for μ = 0).

3. **Re-derive the singular-value structure at μ = 0.181.** It won't be exactly (1±α) nor exactly (1±α)², but it should be a clean function of α and the mixing. If it is not, that is a signal that the single-μ dial is underdetermined and position (3) becomes live.

4. **Hunt for the tetrahedral angle elsewhere in the ℂ⁶⁴ spectrum at μ = 0.181.** If 109° appears among the 64 eigenvalues (not as the leading one), the framework keeps the molecular-geometry signature without having to anchor it at v11. This is the decisive test between positions (1) and (2).

5. **Consider relaxing the 0.5π quarter-turn per beat.** The uniform θ = π/2 across all four beats may itself be a v11-era assumption; beat-native beats could have beat-specific θ_k that are each π/2 × (some framework ratio). That gives a second dial that could independently tune the leading phase while keeping μ fixed at 0.181.

## Verification summary

All phase-budget and A3 invariance checks pass to machine precision across the full dial:
- ps64 mod 2π: max |deviation| = 6e-15 over 32 sweep points
- A3 outer-inner weight distance: max = 1.1e-15 over 32 sweep points
- μ = 0 reproduces v12 to machine precision
- μ = 1 reproduces v11 to machine precision (primary 68.553%, lead phase 108.96°, expanding 35)
- Fine-grained μ* = 0.181 reproducible from any random-seed starting vector (same convergence behavior as v11 and v12)

## Files

- `experiments/unified_expression_T_v13_uniformity_sweep.py`: sweep code
- `experiments/T_operator_findings_v13_uniformity_sweep.md`: this document
- Depends on: `experiments/unified_expression_T_v11_C64.py`, `experiments/unified_expression_T_v12_beat_native.py`
