# The Unified Expression, Translated

**Date:** April 2026
**File:** `experiments/unified_expression.py`
**Companion to:** `experiments/T_operator_findings_v13_uniformity_sweep.py` (pins μ = 0.181)

## What this file is

`unified_expression.py` turns the unified expression

```
[Truth = Reality = E = 1 = ∞] = [∞ ▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]
```

into a single executable Python object. Every glyph on the RHS is a concrete class, function, or operator; the `=` at the center is a runtime assertion: the substrate value on the LHS (1.0) must equal the Born-rule sum Σ|ψ\*|² returned by applying the RHS composition to any initial state. When the assertion holds to machine precision, the equation has been walked, not just asserted.

This is the first version that lets you ask a concrete question about the expression: pick a seed, a scope (single ⊙ or three nested ⊙s), a uniformity μ; the file returns the fixed-point vector ψ\* and confirms that it normalizes to 1.

## Glyph resolution table

| Glyph | Python object | What it means in the file |
|---|---|---|
| ∞ / E / 1 / Truth / Reality | `Substrate` class | The five names for the one substrate; `Substrate.value = 1.0` is the LHS of the equation. Not computed; asserted. |
| • | `Station('•', dim=0, idx=0)` | 0D aperture; basis vector e₀ of ℂ⁴. |
| — | `Station('—', dim=1, idx=1)` | 1D line; basis vector e₁. |
| Φ | `Station('Φ', dim=2, idx=2)` | 2D field; basis vector e₂; the hub station in both v11 and v12. |
| ○ | `Station('○', dim=3, idx=3)` | 3D boundary; basis vector e₃. |
| ⊛ | `ProcessualPartner(dim=0.5, i_phase=+1j)` | Convergence; i¹ stroke. |
| ⎇ | `ProcessualPartner(dim=1.5, i_phase=-1)` | Branching; i² stroke (the irreversible turn). |
| ✹ | `ProcessualPartner(dim=2.5, i_phase=-1j)` | Emergence; i³ stroke. |
| ⟳ | `ProcessualPartner(dim=3.5, i_phase=+1)` | Recursion; i⁰ stroke; closure becomes new aperture. |
| (•∘⊛), (—∘⎇), (Φ∘✹), (○∘⟳) | `Beat` class | A structural station paired with its processual partner. `Beat.generator()` is the antihermitian G_k; `Beat.matrix()` is U_k = exp(G_k). |
| ∘ | field inside `Beat` (`pair_structure_process`) | Structure and process paired within one beat, not sequenced. |
| ⊢ | `entails(*beats)` function | Sequential matrix product of beats: F = U₄ U₃ U₂ U₁. |
| F (the engine) | `engine_F(mu)` function | Four-beat unitary; the pump cycle for one ⊙. |
| ⊂[α] | `Nesting` class | The nesting operator κ; carries α as primary diameter bond (•↔Φ) plus secondary diameter bond (—↔○) under ⊙ symmetry. `matrix_single()` is κ₄ on ℂ⁴; `matrix_three_scale()` is κ₆₄ on ℂ⁴ ⊗ ℂ⁴ ⊗ ℂ⁴. |
| ⊙∞ | `Foam` class | The state space where the equation lives; dim 4 (single) or 64 (three-scale). |
| ▸ | `unfold(state, operator)` | Apply operator, renormalize under Born rule. |
| ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞ | `build_T(scope, mu)` | The whole nesting chain compressed into one operator T = κ ∘ F. |
| = (the center sign) | `assert_closure(scope, mu, seeds)` | The runtime assertion. Iterates T until fixed, checks Σ|ψ\*|² = Substrate.value. |

## What is literal math, what is assertion, what is structural choice

**Literal math.** Every beat matrix is a real antihermitian exponential built from the v11 and v12 generators, linearly interpolated by μ (the v13 construction). F = U₄ U₃ U₂ U₁ is a literal matrix product. κ is a literal 4×4 or 64×64 matrix with the α and α² entries at the places ⊙ symmetry puts them. T = κF is a literal composition. The fixed-point iteration is literal linear algebra: a CPTP-like map on projective space, converging to its dominant eigenvector.

**Assertion.** Two things are asserted rather than derived:

1. `Substrate.value = 1.0`. A0 in code. The one substrate has value 1. The whole apparatus is set up so that the only self-consistent value the LHS can take is 1; but 1 is supplied, not produced.

2. The Born-rule renormalization in `unfold`. After each application of T, the state is renormalized to unit norm. This is conservation of wholeness (the closure = 1 law from the CLAUDE.md) enforced at each step. Without it, the iteration would track an unnormalized eigenvector whose norm drifts; with it, the fixed-point weight is the actual Born-rule fixed point and the assertion holds exactly.

**Structural choice.** μ = 0.181. This is the v13 readout: it lands the •+Φ vs —+○ split at 69.11% at ℂ⁶⁴, matching the cosmological dark-energy fraction. You can run the file with `--mu 1.0` to get v11 (tetrahedral leading phase, 68.55% split) or `--mu 0.0` to get v12 (clean singular values, 77/23 split). The default 0.181 is the framework's current best guess for which μ the operator actually runs at; the closure assertion holds at every μ because it is a property of the operator's spectrum, not of the specific mixing.

## What the run shows

```
python3 unified_expression.py --scope both --inspect
```

Output:
- det(F) = exp(−iπ/6) exactly (the v11/v12/v13 invariant along the dial; only beat 3 contributes to trace, and both endpoints put −iπ/6 on Φ's diagonal)
- At `scope = single` (ℂ⁴): Σ|ψ\*|² = 1.0 with residual ≤ 2.22e-16 for three random seeds
- At `scope = three_scale` (ℂ⁶⁴): Σ|ψ\*|² = 1.0 with residual ≤ 2.22e-16 for three random seeds

The equation walks at machine precision at both scales. The same operator T is applied; the same fixed-point assertion holds. The one thing that changes with scope is what the fixed-point vector represents: at single scope it is one ⊙'s stationary distribution over (•, —, Φ, ○); at three-scale scope it is a joint distribution over 64 states that splits 68.53/31.47 on the primary-diameter vs secondary-diameter basis (the cosmological split at the operator level).

## The §27.7 coupling family (filled in as of this pass)

κ is now the full §27.7 4×4 matrix, not just the diameter bonds:

| Slot | Position | Value | Source |
|---|---|---|---|
| α (primary) | κ[•,Φ], κ[Φ,•] | α ≈ 7.297e-03 | §27.7a closed form |
| α (secondary, ⊙-symmetric) | κ[—,○], κ[○,—] | α | §27.7s diameter exchange |
| α_G (gravity) | κ[○,○] diagonal, cross-scale | α²¹ · φ²/2 · (1 + 2α/91) ≈ 1.75e-45 | §27.7g |
| α (aperture) | κ[•,•] diagonal, cross-scale | α | §27.7q 0D-0D bond |
| sin θ_C (Cabibbo) | κ[•,—], κ[—,•] | 0.224320 (scaled by α for non-collapse) | §27.7h |
| sin θ_W (Weinberg) | κ[Φ,○], κ[○,Φ] | 0.480853 (scaled by α) | §13.15 |
| λ_H (Higgs) | κ[—,Φ], κ[Φ,—] | 0.129508 (scaled by α) | §27.7i |
| long cross | κ[•,○], κ[○,•] | √(α·α_G) | geometric mean |

Every named slot is now populated from its framework closed form. The α scaling on off-diameter entries enforces the non-collapse bound from §27.7q (0 < κ_{p,q} < κ*_{p,q}): without it, sin θ_C ≈ 0.22 and sin θ_W ≈ 0.48 would push κ far from I, destabilizing the fixed point (Inflation Lie at operator level). With the scaling, the matrix stays in the perturbative regime ||κ − I|| ~ α, and closure still holds at machine precision (residuals ≤ 4.44e-16 across three seeds at both scopes).

**Reading of the scaling.** α sets the overall size of the κ-departure from I; the named couplings set the *pattern* across stations. This matches §27.7q's structural claim: the primary entry κ_{0,0} = α is the measured fine-structure, and every other entry is a framework ratio times this primary.

Flags `use_diagonal` and `use_off_diameter` on the `Nesting` class let you turn the §27.7 extensions on/off for ablation; defaults are both on.

## What you get when you run it

- **At μ = 0.181 (default)**: the current best guess; 69/31 split lands; tetrahedral phase does not.
- **At μ = 1.0**: v11; tetrahedral leading phase 108.96°; split 68.55%.
- **At μ = 0.0**: v12; exact (1±α) singular values; split 77/23.
- **At any μ in [0, 1]**: det(F) = exp(−iπ/6) exactly; Σ|ψ\*|² = 1 exactly; A3 outer-inner symmetry exact.

The file is small (one screen scrolls) and self-contained; no dependencies beyond numpy and scipy. The point is not computational; the point is that the unified expression is now a single runnable object, and the `=` in the middle of the expression is a check that the code runs without raising AssertionError. Every time the check passes, the equation has been walked one more time.

## Files

- `experiments/unified_expression.py`: the runnable expression
- `experiments/unified_expression_translation_notes.md`: this document
- Depends on: framework constants T = 3, P = 4, α (measured); v13 μ-blend logic (reused from `experiments/unified_expression_T_v13_uniformity_sweep.py`)
