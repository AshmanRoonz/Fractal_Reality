# T-Operator Findings v14: Origin of the Integer Pattern

**Date:** April 2026
**Depends on:** v7 (T = κ∘F construction), v9 (κ derivation), v12 (characteristic polynomial), v13 (perturbation integers)
**Answers:** v13 Open Question 1: "Why does the specific beat structure of F combined with M produce m_kk proportional to (-21, -5, -4, +30)?"

## Summary

The perturbation coefficients m_kk are **approximate**, not exact, framework integers. Their near-integer character originates from three structural facts:

1. **The trace formulas Tr(MF^n) decompose into sub-traces whose coefficients are exact framework integers** (T, V, √V, G) over framework denominators (T², T²V, TV).

2. **The hub angle θ = π/(2T) sits within 0.007% of the angle that minimizes deviation from integers**, making the Vandermonde inversion produce near-integer ratios.

3. **The integer set (-21, -5, -4, +30) is unique**: at θ = π/6, it is 2300× better than any competing integer triple, and the conservation identity 21+5+4 = 30 is forced by Tr(M) = 0.

## The F Decomposition

### Beat 2 spectral structure

The Phi beat (B2) is the only beat with non-trivial internal structure. Its generator is Gah₂ = -i(π/6)J_ext, where J_ext is the star graph adjacency matrix (three spokes 0,1,3 connected to hub 2) plus a self-loop at hub 2. The spectral decomposition of J_ext:

| Eigenvalue | Multiplicity | Eigenvector structure |
|---|---|---|
| 0 | 2 | span of {0,1,3} subspace orthogonal to (1,1,1) |
| (1+√V)/2 ≈ 2.303 | 1 | (1, 1, (1+√V)/2, 1) |
| (1-√V)/2 ≈ -1.303 | 1 | (1, 1, (1-√V)/2, 1) |

where V = 4T+1 = 13 (generators+whole). The irrational √V = √13 is the sole source of transcendental structure in the entire operator.

### Projectors

Three orthogonal projectors, all with exact algebraic entries:

**P₀ (rank 2, null space):**
```
3·P₀[i,j] = 2δ_{ij} - 1     for i,j ∈ {0,1,3}
P₀[i,j] = 0                   when i = 2 or j = 2
```

**P₊ (rank 1, eigenvalue (1+√V)/2):**
```
P₊[i,j] = v₊[i]·v₊[j] / ((V+√V)/2)
v₊ = (1, 1, (1+√V)/2, 1)
```
Off-diagonals involving station 2: P₊[i,2] = √V/V = 1/√V. Diagonal P₊[2,2] = (V+√V)/(2V).

**P₋ (rank 1, eigenvalue (1-√V)/2):**
Same structure with √V → -√V.

### The three-matrix decomposition

```
B₂ = P₀ + ω₊P₊ + ω₋P₋
```

where ω₊ = exp(-iπ(1+√V)/G) and ω₋ = exp(-iπ(1-√V)/G). Note: G = 12 (generators) appears in the phase denominators.

Key identities:
- ω₊·ω₋ = exp(-iπ/6) = exp(-iπ/(2T)) (the phase deficit per ℂ⁴ pump cycle)
- ω₊ + ω₋ = 2cos(σ)·exp(-iπ/G) where σ = π√V/G

### F decomposition

Since D = B₁·B₀ (a monomial matrix) and B₃ (a rotation in the {2,3} plane) are both exact:

```
F = B₃·B₂·D = F₀ + ω₊·F_p + ω₋·F_m
```

where F₀ = B₃·P₀·D (rank 2), F_p = B₃·P₊·D (rank 1), F_m = B₃·P₋·D (rank 1).

## The Trace Formulas

### Tr(MF): first-order (known from previous session)

```
Tr(MF) = (i-1)/T + ω₊·[(2V+√V) + i(V-√V)]/(TV) + ω₋·[(2V-√V) + i(V+√V)]/(TV)
```

Every coefficient is a framework integer: T = 3, V = 13, √V = √13. Denominator = TV = 39.

### Tr(MF²): second-order decomposition

F² has nine cross-terms from the decomposition F = F₀ + ω₊F_p + ω₋F_m. Grouping by powers of ω₊, ω₋:

| Term | Coefficient | Exact value |
|---|---|---|
| Tr(M·F₀²) | 1 | (-2 + 4i) / T² |
| Tr(M·F_p²) | ω₊² | (20 + 10√V + i(-31 + 7√V)) / (T²V) |
| Tr(M·F_m²) | ω₋² | (20 - 10√V + i(-31 - 7√V)) / (T²V) |
| Tr(M·(F₀F_p + F_pF₀)) | ω₊ | (-V - 5√V + i(-V + 7√V)) / (T²V) |
| Tr(M·(F₀F_m + F_mF₀)) | ω₋ | (-V + 5√V + i(-V - 7√V)) / (T²V) |
| Tr(M·(F_pF_m + F_mF_p)) | ω₊ω₋ = e^{-iπ/6} | (4 + 12i) / (TV) |

**Every sub-trace is an exact algebraic expression with integer coefficients over framework denominators.** The denominators are T² = 9, T²V = 117, and TV = 39. The √V = √13 terms respect conjugation symmetry: replacing √V → -√V exchanges the P₊ and P₋ contributions.

### Integer coefficient inventory

The integers appearing in the Tr(MF²) numerators:

| Integer | Framework identity | Where it appears |
|---|---|---|
| 2, 4 | Φ, P | Tr(M·F₀²) |
| 20 | P(P+1) = Φ·A(2) | Fp², Fm² real part |
| 10 | A(2) | Fp², Fm² √V coefficient |
| 31 | T·A(2)+1 | Fp², Fm² imaginary part |
| 7 | R | Fp², Fm² imaginary √V coefficient |
| 13 | V | Cross-terms |
| 5 | Φ+○ | Cross-terms √V coefficient |
| 12 | G | FpFm+FmFp imaginary part |

The integers are built from the same set that appears in the m_kk ratios: T, P, R, V, G, A(2), Φ+○.

## The Parametric Picture

### Hub angle determines the ratios

The hub angle θ (physical value π/6 = π/(2T)) parameterizes the F matrix through ω± = exp(-iθ·λ±). The m_kk ratios (normalized so the expanding eigenvalue gives 30) vary continuously with θ.

| θ/π | Ratios | Nearest integers | Max deviation |
|---|---|---|---|
| ~0 | (-30, 0, 0, 30) | (-30, 0, 0, 30) | ~0 |
| 0.10 | (-45.0, -1.4, 16.4, 30) | (-45, -1, 16, 30) | 0.40 |
| **1/6** | **(-21.0, -5.0, -4.0, 30)** | **(-21, -5, -4, 30)** | **0.021** |
| 0.25 | (-33.1, -2.1, 5.1, 30) | (-33, -2, 5, 30) | 0.12 |
| 0.35 | (-28.1, -1.0, -0.8, 30) | (-28, -1, -1, 30) | 0.16 |
| 0.45 | (-27.9, -7.1, 5.1, 30) | (-28, -7, 5, 30) | 0.14 |

**The physical angle θ = π/6 gives the smallest deviation from integers by a wide margin** (0.021 vs 0.12+ for all other angles tested). The deviation function has a sharp minimum near π/6.

### The true optimum

The exact minimum of the deviation function sits at θ_opt ≈ π/6 × (1 + 7.15×10⁻⁵), a fractional shift of 0.007% from the physical angle. At this optimum, the residuals drop from 0.021 to 0.003 (about 86× smaller). Even at the optimum, the ratios are NOT exact integers:

```
At θ_opt:  -20.999, -4.999, -4.003, 30.000
```

**The m_kk ratios are transcendental functions of π and √13 that have no exact integer value at any real angle.** The physical angle π/(2T) is simply very close to the critical point.

### Uniqueness of the integer set

At θ = π/6, the integer set (-21, -5, -4, 30) has a sum-of-squared-deviations of 0.00083. The next-best integer set (-22, -4, -4, 30) has deviation 1.92, a ratio of 2300×. The physical integer set is overwhelming in its dominance.

## The Structural Chain

Why are the m_kk near framework integers? The chain has five links:

**Link 1: Star graph topology → √V eigenvalues.** The star graph J_ext (3 spokes + hub + self-loop; T determines the number of spokes) has characteristic polynomial giving eigenvalues 0(×2), (1±√V)/2 where V = 4T+1 = 13. The irrational √V = √13 enters here and nowhere else.

**Link 2: Projectors carry T and V.** The three spectral projectors P₀, P₊, P₋ have entries that are rational functions of T, V, √V. The denominators norm± = (V±√V)/2 and the 1/T factor from P₀ propagate into every F-dependent quantity.

**Link 3: Traces inherit integer structure.** The sub-traces Tr(M·F_a·F_b) for a,b ∈ {0,p,m} have exact algebraic forms with numerators built from framework integers (T, V, R, G, P, A(2), Φ+○) and denominators T², T²V, TV. This is forced: the matrix entries are rational multiples of {1, i, √V, i√V} at each step, and M (the diameter swap) is a permutation, so the traces are sums of such entries.

**Link 4: Hub angle π/(2T) ≈ extremum.** The hub angle θ = π/(2T) nearly minimizes the deviation of m_kk from the integer set (-21, -5, -4, +30). The fractional difference between π/(2T) and the true optimum is 7.15×10⁻⁵. This near-coincidence is the unexplained link; it may be a deep structural property of the interplay between T and V, or it may be a numerical near-miss.

**Link 5: Vandermonde inversion → near integers.** The m_kk are obtained from the Tr(MF^n) via Vandermonde inversion using the four eigenvalues of F. The eigenvalues are transcendental functions of σ = π√V/G, so the inversion produces transcendental m_kk values. But because the input traces have integer coefficients and the hub angle is near an extremum, the output m_kk are near integers.

## The Conservation Identity Revisited

The identity 21 + 5 + 4 = 30, equivalently 2T²-7T+3 = 0 giving T = 3, is EXACT. It is forced by Tr(M) = 0 combined with the approximate integer identification. The exactness of the sum (not the individual terms) comes from the trace identity, which holds at all θ. Only the partition of 30 into (21, 5, 4) is approximate; the sum 30 = 30 is exact.

The sixth route to T = 3 (from v13) remains valid as a structural constraint: **if** the m_kk are framework integers, **then** 2T²-7T+3 = 0 forces T = 3. The slight non-integrality of the m_kk weakens this from "proves T = 3" to "is consistent with T = 3 being the unique positive integer solution."

## Corrections to v13

1. **v13 listed the integer ratios as "0.02-0.45% accurate."** This is correct for three of the four values. The ratio -P = -4 is the most accurate (0.025%), -(Φ+○) = -5 the least (0.45%). The residual structure is: the two largest values (-A(3) and T·A(2)) have matched residuals of opposite sign (~0.02 each, summing to ~0.04), and the intermediate value -(Φ+○) absorbs the remaining deviation.

2. **The normalization constant C.** v13 noted C ≈ 0.01014 and C²×1382 ≈ 1/R (0.55% error). This is now understood as a consequence of sum(m_kk²) ≈ 0.142 ≈ 1/R, which follows from the trace identity ||M||²_F = 4 with 96.4% of the Frobenius norm in the off-diagonal part of M in the F eigenbasis. The identification 1/R is approximate; the exact value of sum(m_kk²) is a transcendental function of σ.

3. **The question "Why Φ+○ = 5 appears as a single integer" (v13 Open Question 3).** 5 = Φ+○ appears because it is a coefficient in the Tr(MF²) sub-traces (the cross-term √V coefficient). The field and boundary dimensions contribute as a unit because they enter through the same projector structure (P₊ and P₋ each involve vp[2] = (1±√V)/2, and the traces involve products that generate Φ+○ = T²-T-1 = V-SU(3) as a natural combination).

## What Remains Open

1. **Link 4 is unexplained.** Why does θ = π/(2T) nearly coincide with the minimum of the integer-deviation function? The fractional shift 7.15×10⁻⁵ is not obviously a framework ratio. This could be a numerical near-miss, or it could reflect a deeper constraint (perhaps from the conservation identity or from the phase sum).

2. **Analytic form of individual m_kk.** The m_kk can in principle be expressed as explicit functions of σ = π√V/G via the Vandermonde inversion of the closed-form traces. This would require solving the quartic characteristic polynomial of F symbolically, which is feasible but algebraically dense.

3. **The approximate nature itself.** The m_kk are NOT exact integers at any θ. Whether there is a perturbative correction (perhaps involving α or higher-order terms) that makes them exact is unknown.

## Files

- `experiments/T_operator_findings_v14_integer_origin.md`: this document
- Analysis performed via inline computation using the projector decomposition of B₂
