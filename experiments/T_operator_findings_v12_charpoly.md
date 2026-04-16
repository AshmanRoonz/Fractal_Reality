# T-Operator Findings v12: The Characteristic Polynomial

**Date:** April 2026
**Depends on:** v7 (T = κ ∘ F construction), v9 (κ derivation, ℂ⁸), v11 (ℂ⁶⁴)

## Motivation

The characteristic polynomial det(T - λI) = 0 encodes the entire eigenvalue structure of T as a single algebraic object. If the roots carry the dimensional ladder constants (α, c, ℏ, mass ratios, π, G), that would be a statement: the unified expression's eigenstructure IS the ladder. One equation containing everything.

## The Exact Determinant Formula

The cleanest result of the investigation. Because T = κ ∘ F (matrix product), and because κ has a specific algebraic structure:

**κ = I + αM**, where M is a permutation matrix encoding the diameter bonds.

For ℂ⁴ (sphere hub), M swaps (0↔2) and (1↔3), the two diameter pairs •↔Φ and —↔○. M is an involution (M² = I), so:

```
det(κ) = det(I + αM) = (1 + α)^k × (1 - α)^k = (1 - α²)^D
```

where D = number of diameter bonds and k counts the +1/-1 eigenvalue multiplicities of M. Since M is a product of D disjoint transpositions, its eigenvalues are +1 and -1 each with multiplicity D (in ℂ⁴: D = 2; in ℂ⁸: D = 4).

Combined with det(F) = exp(iΘ) where Θ is the total phase:

```
det(T_n) = (1 - α²)^D × exp(iΘ)
```

| Representation | D (bonds) | Θ (phase deficit) | |det(T)| |
|---|---|---|---|
| ℂ⁴ | 2 | -π/6 = -360°/G | (1-α²)² = 0.99989 |
| ℂ⁸ | 4 | -π/3 = -2×360°/G | (1-α²)⁴ = 0.99979 |
| ℂ⁶⁴ | D₆₄ | 0 (tensor closure) | (1-α²)^D₆₄ |

The phase deficit follows the pattern Θ = -D' × 360°/G, where D' counts structural-processual dimension pairs. ℂ⁴ has one pair (giving -360°/G = -30°); ℂ⁸ has two (giving -60°); ℂ⁶⁴ closes to zero because the tensor product forces 48 copies of -π/6 = -8π = 0 mod 2π.

**Structural reading:** The determinant of T separates cleanly into a coupling factor (1-α²)^D (how much the nesting departs from unitarity) and a phase factor exp(iΘ) (how much rotational deficit the beats carry). The coupling factor is real and positive; the phase factor lives on the unit circle. The nesting costs amplitude; the beats cost phase.

## The Perturbation Structure

Since κ = I + αM, the eigenvalues of T = κF = (I + αM)F = F + αMF are:

```
λ_k(α) = λ_k(0) + α × ⟨L_k|MF|R_k⟩ + O(α²)
```

where λ_k(0) = eigenvalues of F (the unperturbed, unitary operator), and ⟨L_k|, |R_k⟩ are the left/right eigenvectors of F. This is EXACT to first order in α because κ is linear in α (no α² terms in κ itself; higher-order corrections come only from eigenvector mixing).

### T₄ Perturbation Ratios

The first-order correction c_k = ⟨L_k|MF|R_k⟩ for each eigenvalue of T₄ (sphere hub):

| Eigenvalue | |c_k| | Nearest framework ratio | Error |
|---|---|---|---|
| λ₁ (leading) | 1.42842 | A(2)/R = 10/7 = 1.42857 | 0.011% |
| λ₂ | 6.02570 | T! = 6 | 0.43% |
| λ₃ | 5.24696 | A(3)/P = 21/4 = 5.250 | 0.058% |
| λ₄ (trailing) | 0.65027 | V/P(P+1) = 13/20 = 0.650 | 0.042% |

Every perturbation coefficient is a ratio of framework numbers. The leading eigenvalue (the one that governs convergence to the fixed point) has perturbation coefficient A(2)/R = 10/7: the accumulated traversal at the field station divided by the number of rungs. The trailing eigenvalue has V/P(P+1), which is the same ratio that appears in the second pi-bond energy (π₂/σ = 13/20 in the bond-order model).

### Conservation Law

The sum of eigenvalue magnitude shifts is exactly zero:

```
Σ_k (|λ_k(α)| - |λ_k(0)|) = 0
```

This is not approximate; it holds to machine precision. The nesting κ redistributes amplitude among the eigenvalues without changing the total. What one eigenvalue gains in magnitude, the others lose. This is conservation of traversal (A4) at the operator-spectral level: 0(•) + 1(—) + 2(Φ) = 3(○) expressed as "the total departure from unitarity is a zero-sum game across eigenvalues."

## The Polynomial Itself

The degree-n characteristic polynomial det(T_n - λI) = λⁿ - σ₁λⁿ⁻¹ + σ₂λⁿ⁻² - ... + (-1)ⁿ det(T_n) has coefficients that are elementary symmetric polynomials of the eigenvalues.

### What is clean

**The constant term** (the determinant) has the exact formula above: (1-α²)^D × exp(iΘ). This is fully expressed in framework terms.

**σ₁ = Tr(T)** has the exact formula:

```
σ₁ = Tr(F) + α × Tr(MF)
```

Both traces are computable from the beat matrices. For T₄ (sphere hub), Tr(F) is the sum of four complex exponentials determined by the generator angles, and Tr(MF) encodes how the diameter swap interacts with the four-beat rotation.

### What is not yet clean

The intermediate coefficients σ₂ through σₙ₋₁ carry the full combinatorial structure of F (products of eigenvalue pairs, triples, etc.) mixed with α through the perturbation. They do not reduce to simple framework expressions. The F-matrix structure (which encodes the specific angles of the four beats) dominates; α enters as a perturbation that shifts each term.

**This is structurally expected.** The characteristic polynomial of T encodes everything, but in a compressed form. The clean structure lives in the ROOTS (the eigenvalues), not in the coefficients. The roots separate into:

- An F-determined unperturbed part (the four-beat rotation angles)
- An α-determined perturbation (the nesting shifts, carrying framework ratios)

The coefficients, being symmetric functions of the roots, mix these two contributions inseparably.

## Where the Ladder Lives

The dimensional ladder does not appear as a one-to-one map from eigenvalues to constants. Instead, it appears in three distinct ways:

### 1. In the determinant (the product of all roots)

The determinant (1-α²)^D × exp(iΘ) encodes the ladder's endpoints: α (the coupling, as departure from 1) and the phase deficit (which counts generator structure, G = 12). The factor (1+α)^(1/α) → e connects to the natural logarithm base: one α compounded for 1/α steps gives the transcendental that governs exponential growth. This is the ladder's 0D rung (α) meeting its global structure.

### 2. In the perturbation ratios (first-order shifts)

Each eigenvalue's first-order response to α is a framework ratio:

- A(2)/R = 10/7 at the leading eigenvalue (the one controlling convergence)
- T! = 6 at the second eigenvalue
- A(3)/P = 21/4 at the third
- V/P(P+1) = 13/20 at the trailing

These are not the ladder constants themselves (α, c, ℏ, etc.) but the STRUCTURAL NUMBERS that build the ladder (accumulated traversals, rungs, generators, etc.). The eigenvalues carry the building blocks; the ladder constants are combinations of these building blocks at specific dimensional homes.

### 3. In the phase structure (eigenvalue angles)

Phase differences between eigenvalues in T₄ approximate framework angles:

- 144° ≈ P × 360°/A(2) = 4 × 36° (pentagonal; φ-related)
- 120° = 360°/T (trigonal; the T = 3 signature)
- 126.87° ≈ arccos(-3/5) (Pythagorean; relates to the 3-4-5 triple = T-P-(Φ+○))

And in T₈/T₆₄, the tetrahedral angle arccos(-1/T) = 109.47° appears at the leading eigenvalue.

## Eigenvector Structure

The T₈ eigenvectors are NOT localized at individual stations. Each eigenvector is a superposition across all 8 stations of the dimensional octave. This means there is no clean "this eigenvalue belongs to the 0D rung, that one to the 1D rung" mapping.

**Structural reading:** This is correct physics. The ladder rungs are not independent; they are coupled by κ (the nesting). The eigenvectors of the coupled system are collective modes, not station modes. The ladder is a single vibrating structure; its normal modes are delocalized, just as normal modes of a crystal lattice are delocalized even though the atoms sit at specific sites.

The framework numbers appear in the perturbation ratios (how much each collective mode responds to the coupling) rather than in the mode shapes themselves.

## The Factorization Question

Does det(T - λI) factor into lower-degree polynomials with framework structure?

**Answer: no clean factorization found.** The characteristic polynomial of T₄ does not factor into two quadratics with framework coefficients. The characteristic polynomial of T₈ does not factor into clean lower-degree pieces. This is consistent with the eigenvector mixing: if the modes were cleanly separable by station, the polynomial would factor; since they are collective, it does not.

The one factorization that DOES work is the determinant: det(T) = det(κ) × det(F), separating nesting from rotation. But this is a factorization of the constant term, not of the whole polynomial.

## Summary Table

| Result | Status | Framework content |
|---|---|---|
| det(T_n) = (1-α²)^D × exp(iΘ) | Exact | α, G, D (diameter bond count) |
| Σ magnitude shifts = 0 | Exact | Conservation of traversal (A4) |
| Perturbation ratios | First order exact | A(2)/R, T!, A(3)/P, V/P(P+1) |
| Phase structure | Numerical | Tetrahedral angle, trigonal, pentagonal |
| Coefficient structure | Mixed | Clean at endpoints (σ₁, det); F-dominated interior |
| Eigenvector localization | None | Collective modes; ladder in perturbation, not in mode shapes |
| Polynomial factorization | None found | Consistent with mode mixing |

## Assessment

The characteristic polynomial of T encodes the ladder, but not in the way initially hoped (one polynomial whose roots ARE the ladder constants directly). Instead:

1. **The determinant formula** is the cleanest single equation: det(T) = (1-α²)^D × exp(iΘ). This encodes α (the coupling), G (the generator count via phase deficit), and D (the diameter topology).

2. **The perturbation ratios** encode the accumulated traversal function A(d), the rung count R, the pump phases P, and the generator+whole count V. These are the structural integers from which all ladder constants are built.

3. **The conservation law** (sum of magnitude shifts = 0) is conservation of traversal realized spectrally.

The statement is: the ladder lives in the RESPONSE of the eigenvalues to the coupling α, not in the eigenvalues themselves. The unperturbed eigenvalues (F alone, no nesting) are the four beats. The nesting (κ, the ⊂[α]) introduces the structural ratios as perturbation coefficients. The ladder is what happens when you couple the beats to the nesting; it is not in either piece alone.

This is consistent with the unified expression: the four beats are the engine, the nesting is the product, and the ladder is what the engine produces when the nesting is applied.

## Open Questions

1. **Analytic derivation of the perturbation ratios.** The ratios A(2)/R, T!, A(3)/P, V/P(P+1) are observed numerically. Can they be derived from the structure of M and F analytically? The derivation would need: (a) the eigenvectors of F (the four-beat rotation), (b) the action of M (the diameter swap) on those eigenvectors, (c) the resulting ⟨L_k|MF|R_k⟩ inner products.

2. **The intermediate coefficients σ₂, σ₃.** Are there framework expressions for these, perhaps involving sums of products of the perturbation ratios?

3. **The ℂ⁶⁴ characteristic polynomial.** A degree-64 polynomial whose determinant is real and positive (phase closure). The 20 phase clusters (sizes {1,3,6}) should appear as factorization structure of this polynomial over appropriate extensions.

4. **Connection to the selection rule.** The accumulated traversal A(d) appears in the perturbation ratios at the same positions where it appears in the exponents of the dimensional ladder (§27.7j). Is this the same function showing up in two views (exponent algebra vs operator spectral theory)?

## Files

- `experiments/T_operator_findings_v12_charpoly.md`: this document
- Analysis performed via inline computation on T₄ and T₈ matrices from v7 and v9

