# T-Operator Findings v13: The Perturbation Structure

**Date:** April 2026
**Depends on:** v7 (T = kappa F construction), v9 (kappa derivation, both diameters), v12 (characteristic polynomial)
**Supersedes:** v12 perturbation ratio claims (which used incorrect values from a lost computation)

## The Clean Analytical Chain

### Step 1: The Perturbation Decomposition (Exact)

T = kappa F = (I + alpha M) F = F + alpha MF

where F is unitary (the four beats) and M is the diameter swap permutation (Hermitian, M^2 = I, Tr(M) = 0).

The first-order eigenvalue shift is:

```
lambda_k(alpha) = lambda_k(0) + alpha * c_k + O(alpha^2)
```

where c_k = <L_k|MF|R_k> is the perturbation coefficient in the biorthogonal eigenbasis of F.

### Step 2: c_k = lambda_k * m_kk (Exact)

Since F|R_k> = lambda_k|R_k>:

```
c_k = <L_k|MF|R_k> = <L_k|M(lambda_k|R_k>) = lambda_k * <L_k|M|R_k> = lambda_k * m_kk
```

where m_kk = <R_k|M|R_k> is the Rayleigh quotient of M in the kth eigenstate of F.

### Step 3: m_kk is Real (Exact)

M is Hermitian (real symmetric), and for unitary F the left eigenvectors are the conjugate transposes of the right eigenvectors. So m_kk = R_k^dagger M R_k is a Rayleigh quotient of a Hermitian operator, which is always real.

**Consequence:** |c_k| = |m_kk| (since |lambda_k| = 1 for unitary F). The perturbation coefficient magnitude equals the Rayleigh quotient magnitude. The perturbation DIRECTION is along the unperturbed eigenvalue (radially outward if m_kk > 0, inward if m_kk < 0).

### Step 4: The Conservation Law (Exact)

```
sum_k m_kk = Tr(M) = 0
```

This is the trace of M in the F eigenbasis, which equals Tr(M) in any basis. M is a derangement (fixed-point-free permutation), so its trace is zero.

**Physical meaning:** The nesting kappa redistributes amplitude among the eigenvalues without changing the total. What the expanding eigenvalue gains, the contracting eigenvalues lose, exactly. This is conservation of traversal (A4) at the operator-spectral level.

### Step 5: The Magnitude Shift Conservation (Exact at First Order)

The first-order magnitude shift of eigenvalue k is:

```
(|lambda_k(alpha)| - 1) / alpha = Re(c_k * conj(lambda_k)) = Re(lambda_k * m_kk * conj(lambda_k)) = m_kk
```

(since |lambda_k|^2 = 1 and m_kk is real). So the magnitude shift divided by alpha IS m_kk. The conservation law sum(m_kk) = 0 means the sum of all magnitude shifts is zero at first order.

Verified numerically: the sum of Re(c_k * conj(lambda_k)) = 0.0000000000 (machine precision).

## The Integer Ratio Pattern

### T4 (Sphere Hub, Both Diameters)

The four m_kk values, sorted by magnitude:

| Eigenstate | m_kk | Phase of F eigenvalue | Framework integer | Error |
|---|---|---|---|---|
| Most contracting | -0.21307 | -108.4 deg | -A(3) = -21 | 0.070% |
| Mid contracting | -0.05047 | -90.3 deg | -(Phi+O) = -5 | 0.448% |
| Least contracting | -0.04057 | +132.4 deg | -P = -4 | 0.025% |
| Expanding | +0.30411 | +36.3 deg | +T*A(2) = +30 | 0.022% |

Normalization constant C = 0.01014 maps between the m_kk values and their integer counterparts.

The identification of framework integers:

- **A(3) = 21**: the accumulated traversal at boundary closure
- **Phi+O = 5**: sum of field and boundary dimensions (the phi-residual, T^2 - T - 1)
- **P = 4**: pump phases (T+1)
- **T*A(2) = 30**: triad times field traversal

### The Conservation Identity

```
A(3) + (Phi+O) + P = T * A(2)
21  +    5     + 4 = 3 * 10
          30       =   30
```

The expanding eigenvalue's integer weight exactly equals the sum of all contracting weights. This is not a numerical accident; it is forced by Tr(M) = 0 combined with the integer ratio hypothesis.

### A Sixth Route to T = 3

The conservation identity, expressed as a constraint on T:

```
T * A(2) = A(T) + (Phi + O) + P
10T = T(2T+1) + (2+T) + (T+1)
10T = 2T^2 + 3T + 3
2T^2 - 7T + 3 = 0
```

**Discriminant:** 49 - 24 = 25 = (Phi+O)^2 = 5^2

**Solutions:** T = (7 +/- 5) / 4 = 3 or 1/2

**Unique positive integer: T = 3.**

The solution formula reads in framework terms:

```
T = (R +/- (Phi+O)) / (2*Phi) = (7 +/- 5) / 4
```

This is the sixth independent route to T = 3, and the first derived from the T-operator's spectral structure. It uses A(d), Phi, O, P, and R; no previous route uses all of these simultaneously.

| Route | Equation | Source |
|---|---|---|
| 1 | R = 2T+1 | Rung definition |
| 2 | T^(T-2) = T | Compositional mediator (D5) |
| 3 | (Phi+P)/2 = T | Balanced wobble (biology) |
| 4 | R > Phi+T AND R/(R-4) > 2 | Nuclear single-intruder |
| 5 | A'(T/2) = R | W-V decomposition |
| **6** | **T*A(2) = A(T) + (Phi+O) + P** | **Operator perturbation conservation** |

## T8: Exact Doubling

The T8 representation (8 stations, 4 diameter bonds) produces EXACTLY doubled m_kk values: each T4 eigenvalue appears twice with identical perturbation coefficient. This is forced by the construction: structural and processual stations have identical coupling topology (same hub architecture), so the 8D eigenstates come in degenerate pairs.

```
T8 m values: (-21, -21, -5, -5, -4, -4, +30, +30) * C
```

The conservation identity holds at double strength: 2*(21+5+4) = 2*30. The expanding/contracting count is 2/6.

## Structural Symmetry of F Eigenstates

A clean symmetry emerged from the F eigenvector analysis. In every eigenstate of F (sphere hub):

```
|R_k[dot]|^2 = |R_k[Phi]|^2     (dot-Phi diameter: equal Born weights)
|R_k[line]|^2 = |R_k[circle]|^2  (line-circle diameter: equal Born weights)
```

The F eigenstates respect the diameter pairing in magnitude (but not phase). This means the "how much each station contributes" is identical across each diameter pair; only the phase coherence differs.

The m_kk value for each eigenstate is then:

```
m_kk = 2*p_k^2 * cos(delta_k) + 2*q_k^2 * cos(epsilon_k)
```

where p_k^2 = |R_k[dot]|^2 = |R_k[Phi]|^2, q_k^2 = |R_k[line]|^2 = |R_k[circle]|^2, and delta_k, epsilon_k are the phase differences across each diameter.

### Beat 0 Is Exactly Block-Diagonal

When F is analyzed in the M-eigenbasis (symmetric/antisymmetric subspaces under diameter swap), beat 0 (the aperture convergence, dot-to-Phi) is exactly block-diagonal: it preserves the M-subspace decomposition perfectly. Beats 1 and 3 (line and circle) mix the subspaces maximally. Beat 2 (field) mixes partially.

This is structurally meaningful: the aperture beat respects the diameter symmetry because it acts on one diameter pair (dot-Phi). The other beats break this symmetry by coupling the cross-diameter stations.

## What the Integers Mean

The perturbation coefficient m_kk measures "how much does eigenstate k respond to the diameter coupling?" The four integers assign this response:

- **30 (expanding):** The eigenstate most aligned with the symmetric (+1) subspace of M. It gets amplified by the nesting. Its weight T*A(2) encodes the triad's reach through the field.
- **21 (most contracting):** The eigenstate most aligned with the antisymmetric (-1) subspace. It gets maximally suppressed. Its weight A(3) is the full boundary traversal; the mode that carries the boundary's information contracts the fastest.
- **5 (mid contracting):** Weight Phi+O, the sum of field and boundary dimensions. A mode that encodes the higher-dimensional structure.
- **4 (least contracting):** Weight P, the pump cycle count. The mode closest to neutral (smallest |m_kk|) is the one carrying the pump's phase structure.

The conservation identity 21 + 5 + 4 = 30 says: the total contracting response equals the expanding response. What the nesting amplifies at one eigenvalue, it exactly suppresses across the other three. The total amplitude is conserved.

## Connection to the Dimensional Ladder

The accumulated traversal function A(d) appears in the perturbation ratios at the SAME positions where it appears in the exponents of the dimensional ladder (Section 27.7j). The ratio m_expanding / m_most_contracting = 30/21 = 10/7 = A(2)/R, which is the field-traversal-to-rungs ratio that also appears in the selection rule for exponents.

This suggests a deeper connection: the selection rule for physical constants (which determines where on the ladder each constant lives) and the perturbation structure of the T-operator (which determines how the unified expression responds to coupling) are manifestations of the same mathematical object: the accumulated traversal function A(d) evaluated at framework stations.

## Corrections to v12

The v12 findings document reported perturbation ratios (A(2)/R, T!, A(3)/P, V/P(P+1)) attributed to absolute |c_k| values from a computation in a previous session. This was incorrect; those values were RATIOS between m_kk values, and the fourth ratio should be P/(Phi+O) = 4/5, not V/P(P+1) = 13/20.

The corrected picture: the perturbation structure is an INTEGER PATTERN m_kk ~ (-A(3), -(Phi+O), -P, T*A(2)), not individual framework-ratio magnitudes. The ratios between these integers reproduce all the matches reported in v12, with the correct identifications.

## Open Questions

1. **Analytic derivation of the integer pattern.** Why does the specific beat structure of F (four generators with i-phases at theta = pi/2, Phi as hub) combined with M (diameter swaps) produce m_kk proportional to (-21, -5, -4, +30)? This would require analytic expressions for the F eigenvectors.

2. **The normalization constant.** C ~ 0.01014. Is this a framework number? C^2 * 1382 ~ 1/R (0.55% error), but the identification is not clean enough to be confident.

3. **Why Phi+O = 5 appears as a single integer.** In the framework, Phi (2) and O (3) are distinct dimensions. Their sum (the phi-residual, T^2-T-1) appears as a single contracting weight. What structural property of the F eigenstates forces the field and boundary dimensions to contribute as a unit?

4. **The approximate nature of the integer ratios.** The ratios are not exact (errors 0.02-0.45%). Are there alpha-dependent corrections that make them exact? Or are they truly approximate, reflecting the numerical (not analytic) nature of the beat construction?

## Files

- `experiments/T_operator_findings_v13_perturbation.md`: this document
- Analysis performed on T4 (v7) and T8 (v9) operators
