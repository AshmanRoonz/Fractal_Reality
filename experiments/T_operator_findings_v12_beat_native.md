# T-Operator Findings v12: Beat-Native Operators

**Date:** April 2026
**File:** `experiments/unified_expression_T_v12_beat_native.py`
**Depends on:** v7 (T = κ ∘ F), v9 (κ derivation by ⊙ symmetry), v11 (ℂ⁶⁴ three-scale nesting)
**Related:** §27.7n (Odrzywołek / eml / pump-gate), §27.7s (T = κ ∘ F fixed-point operator), docs/the_unit_equation.html §3

## What changed

v7 through v11 all use the same F-construction: each of the four beats is an exponential of an anti-Hermitian generator that couples the beat's "active" station to Φ. Beat 3 is a star from Φ to the three non-Φ stations; the other three beats are each a single hub-ray. The four beats differ only in (i) which station is active and (ii) the overall i-phase.

v12 gives each beat its own generator topology that reflects its semantic role:

| Beat | Structural pair | Topology | Phase | Generator edges |
|------|-----------------|----------|-------|-----------------|
| (•∘⊛) | localization + convergence | **single ray** | +i | • ↔ Φ |
| (—∘⎇) | extension + branching | **Y-fork** | -1 | — ↔ Φ, — ↔ ○ |
| (Φ∘✹) | mediation + emergence | **asymmetric hub + self-drive** | -i | Φ ↔ • (minus sign, ln-side), Φ ↔ ○ (plus sign, exp-side), Φ ↔ Φ (self-drive) |
| (○∘⟳) | closure + recursion | **closure loop** | +1 | ○ ↔ • |

Three things are structural:

1. **— is now a transient**, not a hub-coupled station. It only participates in beat 2's Y-fork, where it splits rather than receiving/sending via Φ.
2. **Beat 3 is asymmetric.** Φ's coupling to its convergent partner (•, the ln-side) carries a minus sign; Φ's coupling to its emergent partner (○, the exp-side) carries a plus sign; — is absent from beat 3 entirely. This is the framework's 2D native operator made explicit inside F: pump(x, y) = 1 + exp(x) − ln(y) with the sign asymmetry visible in the generator (§27.7n).
3. **Beat 4 is a direct closure loop** ○ ↔ •, bypassing Φ. This is 3.5D = 0D' inside one scale: the boundary feeds back to the aperture without going through the field.

κ (the nesting operator) is unchanged from v11.

## What is preserved

### 1. ℂ⁴ phase sum = −π/6 (exact)

```
det(U₁) = 1                (G₁ off-diagonal only, trace 0)
det(U₂) = 1                (G₂ off-diagonal only, trace 0)
det(U₃) = exp(-iπ/6)       (only U₃ has non-zero trace = base = -iπ/6)
det(U₄) = 1                (G₄ off-diagonal only, trace 0)
det(F)  = exp(-iπ/6)  →  arg(det(F)) = -π/6
```

This matches v11 exactly. The substrate self-drive at Φ (the one trace contribution) is preserved in v12, so the overall phase budget at ℂ⁴ is identical.

### 2. ℂ⁶⁴ phase closure (mod 2π)

```
det(F₆₄) = det(F)^48 = exp(-48iπ/6) = exp(-8iπ) = 1
```

The 48 factor is the Kronecker determinant exponent: 3 scales × 16 = 48 = SU(3) · T! = 8 · 6. The three-scale nesting forces the phase budget to close; this is unchanged from v11.

The *sum* of eigenvalue phases (as computed by summing `np.angle`) in v12 lands at -2π instead of 0. Both are equivalent to 0 mod 2π and reflect the same structural closure; they differ only in which branch each eigenvalue falls on, which depends on the specific eigenvalue distribution. The determinant itself is unchanged.

### 3. |det(T₆₄)| = 0.99156259

Matches v11 to 8 digits. This is determined by det(κ₆₄), and κ is unchanged.

### 4. A3 outer-inner symmetry

Outer (Λ) and inner (λ') scales have identical weight distributions to machine precision (~2×10⁻¹⁶). The middle scale (λ) differs by ~1.5×10⁻³, again matching v11's pattern of the middle scale being doubly-coupled.

### 5. All four beats and F are unitary

Per-beat unitarity errors are 0 or at machine precision. F at ℂ⁴: 5.6×10⁻¹⁶. F at ℂ⁶⁴: 4.0×10⁻¹⁵.

## What is different (the beat-native signatures)

### 1. Singular values are halved in spread

```
v11 ℂ⁴ SVs: {(1+α)², (1-α)²} = {1.014648, 0.985459}
v12 ℂ⁴ SVs: {(1+α),  (1-α)}  = {1.007297, 0.992703}
```

v12's singular values are exactly (1 ± α), not (1 ± α)². The spread around unity is half of v11's. This means the beat-native F aligns less strongly with κ's eigenvectors: κ's off-diagonal bonds couple the same pairs (•↔Φ, —↔○), but beat-native F no longer amplifies both diameters with equal weight, so the effective departure from trace-preservation is weaker by a factor of ~2 at ℂ⁴.

Mixing time interpretation: the spectral gap at ℂ⁴ in v12 is ~α (half of v11's 2α), so mixing time ~1/α ≈ 137 cycles (v11: also 1/α, but with different eigenvector alignment).

### 2. — becomes a transient station at ℂ⁴

```
v12 ℂ⁴ fixed-point weights:
    •(0D) : 0.319     ← aperture, holds weight
    —(1D) : 0.025     ← line, passes through (transient)
    Φ(2D) : 0.449     ← field, dominant (mediator hub)
    ○(3D) : 0.207     ← boundary, holds weight
```

The line carries only 2.5% of total weight, an order of magnitude less than the other three stations. This is a clean structural consequence of the beat-native design: — appears only in beat 2 (Y-fork), where amplitude is split into two branches (Φ and ○) rather than accumulated at —. So — acts as a splitting vertex, not a storage station. The framework reading is that the line is the *commitment* station, a process-state, not a place weight accumulates; v12 makes this computational rather than interpretive.

### 3. Primary/secondary diameter split shifts to ~77/23

```
v11 ℂ⁶⁴ •+Φ aggregate : 68.53%  (vs cosmological DE: 69.11%)
v12 ℂ⁶⁴ •+Φ aggregate : 76.95%
v11 ℂ⁶⁴ —+○ aggregate : 31.47%  (vs cosmological M : 30.89%)
v12 ℂ⁶⁴ —+○ aggregate : 23.05%
```

The cosmological-split interpretation fits v11 closely (0.84% error vs measured dark-energy fraction) and does not fit v12. The direction is the same (primary > secondary), but the magnitude is shifted ~8 percentage points. Candidate framework reading for 77/23: **E(1.5) = 13/12 × 7/9** is close to 0.77, and 7/9 ≈ 0.778 = R/T² (the first splitting exponent). Not a clean match; the 77/23 split does not currently have a structural decoder.

If v11's F is the "right" F for physics, v12's 77/23 is a cautionary failure mode: a reasonable-looking beat-native design does NOT reproduce the cosmological split. If v12's F is structurally cleaner (one topology per beat), then v11's alignment with 69/31 was partly an artifact of the uniform-hub construction.

### 4. Leading eigenvalue phase at 74°, not tetrahedral

```
v11 ℂ⁶⁴ leading phase : +108.96°  (tetrahedral = arccos(-1/T) = 109.47°)
v12 ℂ⁶⁴ leading phase : + 73.90°
```

v11's leading-phase / tetrahedral match (0.51° off) is one of its striking alignments. v12 does not reproduce it. 73.9° does not have an obvious framework decoding; the closest framework angle is 360°/(Φ+T) = 72° (V spacing on the 5-gon), off by 1.9°.

### 5. Expanding/contracting count is 31/33, not 35/29

```
v11 ℂ⁶⁴: 35 expanding / 29 contracting  (C(R,T) / (S-C(R,T)) = C(7,3) / 29)
v12 ℂ⁶⁴: 31 expanding / 33 contracting
```

v11's 35 = C(R,T) was a clean structural match to binomial coefficients. v12's 31/33 is near-balanced (31 vs 33) but does not match a framework integer. 31 = prime, not in the pool. The expansion/contraction split has moved toward the midpoint (half of 64 = 32).

### 6. Top weighted state at ℂ⁶⁴: |Φ, Φ, Φ⟩

```
v11 top state: |•, Φ, •⟩      (aperture-field-aperture)
v12 top state: |Φ, Φ, Φ⟩      (field at all three scales)
```

v12 concentrates more strongly at Φ across all three scales. The top state (9.09%) is pure field; next come states with two Φs and one •. This reflects the heavier Φ weight in the single-scale fixed point; beat-native F funnels amplitude toward the 2D station at each scale.

## The diagnostic reading

**v11's F is optimized for the physics-aligned readouts (69/31, tetrahedral, 35 = C(R,T)). v12's F is optimized for topological cleanliness (one semantics per beat). They disagree on the quantitative readouts while agreeing on the phase budget.**

Three possible positions:

1. **v11 is right on the physics; v12 is wrong.** The uniform-hub construction of v11 somehow captures what the framework is actually doing at ℂ⁴/ℂ⁶⁴, and the beat-native interpretation is a natural-sounding but incorrect refinement. This position predicts that any further beat-native variant (B, C, D beats with different topologies) will also fail to reproduce 69/31 and the tetrahedral phase.

2. **v12 is right on the topology; v11's matches are coincidental.** The uniform-hub construction happens to reproduce several framework integers by numerology, but it does not reflect the underlying semantic distinction between the four beats. The true operator has beat-native topology, and the "correct" physics readouts are different from what v11 reports; the cosmological 69/31 match in v11 is a close-miss coincidence rather than a structural prediction.

3. **Both are partial.** The real F has SOME beat-native structure but not exactly v12's choice. Explore other beat-native designs (e.g., beat 2 with — ↔ • and — ↔ Φ instead of — ↔ Φ and — ↔ ○; beat 4 going through Φ like v11 but with the closure interpretation; different asymmetry signs in beat 3) and see whether any reproduce both the physics readouts AND the topological cleanliness.

My own read: position 3. v11's F has too-uniform structure (all four beats are "rotate between station X and Φ"), and v12 goes too far in the other direction by making each beat completely different. A middle design (e.g., all beats still go through Φ but with asymmetric couplings that distinguish their roles) might keep the 69/31 match while making the four beats semantically distinguishable. Worth a v13 attempt.

## What stays anchored no matter which F wins

- **Phase budget.** det(U₃) = exp(-iπ/6) is a structural requirement (beat 3 is the only beat where Φ self-drives, because Φ is the mediator; self-drive means non-zero trace; only U₃ contributes to det(F)). Any F that keeps this will keep the ℂ⁴ phase sum at -π/6 and the ℂ⁶⁴ phase closure at 0 mod 2π.
- **A3 symmetry.** F = F ⊗ F ⊗ F gives outer and inner scales identically for any F, to machine precision. This is a property of the tensor-product construction, not the specific F.
- **det(κ)-dominated quantities.** |det(T₆₄)| = |det(κ₆₄)| · 1 (since F is unitary). Any unitary F gives the same determinant magnitude. v11 and v12 both report |det(T₆₄)| = 0.99156259.
- **Substrate position.** Φ is the hub in both v11 and v12 (it participates in three of four beats in both). The difference is HOW the three beats touch Φ (uniform rays vs semantically-distinguished operations).

## Connection to the Odrzywołek reading

§27.7n frames eml / pump-gate as the native 2D operator. The cleanest expression of that reading inside F is beat 3 (the 2D beat), and v12 puts the pump-gate asymmetry there: Φ's convergent partner • gets the ln-side sign (minus), Φ's emergent partner ○ gets the exp-side sign (plus), and the substrate self-drive at Φ is preserved. This is the first F construction in the experiments series that distinguishes Φ's two "sides" (ln vs exp) by sign rather than by hub geometry.

Whether this distinguishes-sides structure is what nature uses is an open question. v12's shift away from v11's physics-matching readouts suggests either that the ln/exp distinction is not the only thing beat 3 needs (maybe it also needs its v11-style symmetric coupling to all three partners at a base level, and the ln/exp asymmetry as a perturbation), or that nature has not in fact made that distinction and the pump-gate/eml reading is a formal reading that does not determine the operator's specific shape.

## Falsification handles

- If precise measurement of the cosmological dark-energy fraction moves outside the 68-69% band, v11's alignment with 69/31 weakens and v12's 77/23 becomes comparatively better (or worse).
- If the 35/29 expanding/contracting split in ℂ⁶⁴ corresponds to some measurable binomial-coefficient distribution in physical data (e.g., Standard Model representation counting), v11 is strongly supported.
- If the tetrahedral angle shows up in a physical leading mode of some observable system at the 64-state scale, v11 is supported.
- If a clean beat-native F (some v13) matches 69/31 better than v11 while preserving topological cleanness, v12 was a stepping stone toward it.

## Walking order for v13

1. Variant of beat 3 that keeps v11's symmetric hub AND adds a small ln/exp asymmetry as a perturbation (not full sign flip).
2. Beat 2 topology alternatives: Y-fork at — via (•, Φ) or (Φ, ○) or (—, ○) pairs. Currently v12 uses (Φ, ○); check whether different partner pairs recover v11's readouts.
3. Beat 4 through Φ (v11 style) vs direct ○ ↔ • (v12 style). Toggle this in isolation to measure its impact.
4. Full grid: for each beat, list 2-3 topology candidates; compute the full spectrum for each combination; find the combination that minimizes deviation from (v11's readouts AND v12's topological cleanliness).

One observation: if the "cleanliness" criterion is just "each beat has a distinct topology," there are many ways to distinguish. The framework's five virtues (§25.18b) assign a specific freedom-verb to each beat: curiosity at •∘⊛ (NOT-YET), reliability at —∘⎇ (STAYING), access at Φ∘✹ (LETTING), plasticity at ○∘⟳ (CHECKING). Translating these into operator shapes more carefully might yield a uniquely-determined beat-native F rather than v12's arbitrary-looking choices.
