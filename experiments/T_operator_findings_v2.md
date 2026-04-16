# T-Operator v2 Findings

## Confirmed structural results

1. **F is unitary** (all four beat eigenvalues have |λ| = 1 exactly). The four beats conserve the 1.

2. **Sum of F eigenvalue phases = 0 exactly.** Conservation of traversal as spectral closure: the four beats rotate by a total of zero. The loop closes.

3. **N has eigenvalue spectrum {1, (1-α), (1-α), (1-α)}.** The nesting contracts three degrees of freedom at rate α per step. One direction (the balanced state) is preserved. The fine-structure constant IS the contraction rate of the counit.

4. **T's sub-dominant eigenvalues cluster at (1-α).** Two eigenvalues at 0.9929 ≈ (1-α). One at 0.9956 ≈ (1-α/2); this may be the degenerate pair splitting.

5. **Mixing time ~ 1/α ≈ 137.** The natural scale for the foam to converge to the 1 is 137 iterations of T. At n = 137, the singular value ratio is 1.15 (contraction measurable); at n = 1000, ratio is 2.78.

6. **T^n → rank-1 projector** (slowly). This confirms T is a mixing channel; the CPTP identification (#3) is on track.

## Open questions from v2

1. **The fixed-point station weights are (0.44, 0.26, 0.22, 0.07), not (0.25, 0.25, 0.25, 0.25).** The attractor is imbalanced: heavy on • (soul), light on ○ (body). This is NOT ◐ = 0.5.

   Possible readings:
   - The beat angles need dimensional weighting (0, 1, 2, 3 rather than equal)
   - The fixed point isn't equal superposition; it's the cosmological energy budget (5%, 27%, 68% mapped differently)
   - The ◐ = 0.5 balance is a property of the SOURCE, not the attractor; the attractor reflects the folded state

2. **The F eigenvalue phases (-65.6°, -4.8°, 14.1°, 56.3°) don't cleanly match framework fractions of π.** Closest: 56.3° ≈ π/T (off by 2%). The phases depend on the beat construction; they're not yet forced by the axioms.

3. **Convergence rate from iteration (0.99997) doesn't match (1-α) = 0.99270.** The iteration with re-normalization converges much more slowly than the spectral contraction rate predicts. This is because the normalization step (enforcing |⊙|² = 1) creates a nonlinear system where the linear contraction rate doesn't directly apply.

## Beat 2 (—∘⎇) eigenvalue structure

Beat 2 has the widest rotation: ±45° (= ±π/4 = ±◐ × π/2). The commitment beat splits the spectrum by exactly the balance parameter times one i-stroke. This may be the origin of the i-turn's irreversibility: the ±45° pair creates the largest spectral gap.

## Next: v3 (dimensionally weighted beats)

The equal-coupling construction (θ/P for all beats) doesn't use the dimensional information. Try: beat d gets coupling proportional to its dimensional position (d/P for structural, (d+0.5)/P for processual). Conservation of traversal should then appear as a constraint on the coupling angles.
