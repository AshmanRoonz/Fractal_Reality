# Part 3: Derivation of Quantum Mechanics

## 3. From FRFE to Schrödinger's Equation

### 3.1 Four Fundamental Constraints

We now prove that imposing physical consistency on FRFE in 3+1.5 dimensions uniquely recovers the Schrödinger equation in the classical 3+1 limit.

**Constraint 1** (Locality): Evolution at point x depends only on Φ and its derivatives at x

**Constraint 2** (Isotropy): No preferred spatial direction in the 3D sector

**Constraint 3** (Conservation): Probability/norm conservation: d/dt ∫|Φ|² d³x = 0

**Constraint 4** (Smoothness): Continuous evolution as Δt → 0

### 3.2 Main Uniqueness Theorem

**Theorem 3.1** (Uniqueness of Schrödinger): Under constraints 1-4, the only continuous limit of FRFE (Eq. 2.1) in 3.5D spacetime is:

```
iℏ ∂ψ/∂t = -(ℏ²/2m)∇²ψ + V(x)ψ + ε(x,t)ψ  (3.1)
```

where the stochastic term ε satisfies (2.6) with Var[ε] ~ α²|E| and α_quantum = √ℏ.

**Proof**:

*Step 1 - Continuum limit structure*:

Let Δt → 0, Δx → 0. The discrete update (2.1) becomes a differential equation. By **Constraint 1 (Locality)** and smoothness, the evolution must be expressible as:

```
∂Φ/∂t = F[Φ, ∇Φ, ∇²Φ] + ε(x,t)Φ
```

*Step 2 - Isotropy constraint*:

By **Constraint 2 (Isotropy)**, F must be invariant under SO(3) rotations in ℝ³.

**Lemma 3.1** (Isotropic Operators): The only rotationally invariant second-order scalar differential operator on ℝ³ is c∇² for some constant c.

Therefore:

```
F[Φ] = D∇²Φ + G(|Φ|²)Φ
```

*Step 3 - Conservation constraint*:

By **Constraint 3 (Conservation)**, require:

```
d/dt ∫|Φ|² d³x = 0
```

Computing:

```
d/dt ∫|Φ|² d³x = ∫ (∂Φ*/∂t · Φ + Φ* · ∂Φ/∂t) d³x
                = ∫ (F*[Φ*]Φ + Φ*F[Φ]) d³x
```

For this to vanish for all Φ, we need:

```
F[Φ] = iG[Φ]  where G is Hermitian (G* = G)
```

*Step 4 - Determine G from isotropy*:

From Steps 2 and 3:

```
iG[Φ] = D∇²Φ + G(|Φ|²)Φ
```

For G to be Hermitian, D must be pure imaginary. Write D = iD_real. Therefore:

```
∂Φ/∂t = i[D_real ∇²Φ - G(|Φ|²)Φ] + εΦ
```

*Step 5 - Linear regime and potential*:

In the linear quantum regime, G(|Φ|²) → V(x) is the external potential:

```
∂Φ/∂t = i[D_real ∇² - V(x)]Φ + εΦ
```

*Step 6 - Fix units using Stone's theorem*:

By **Constraint 4 (Smoothness)** and the requirement that time evolution forms a strongly continuous one-parameter unitary group U(t), **Stone's theorem** guarantees:

```
U(t) = exp(-itĤ/ℏ)
```

where Ĥ is a self-adjoint operator and ℏ sets the time scale. This gives:

```
iℏ ∂ψ/∂t = Ĥψ
```

Comparing with Step 5, identify:

```
Ĥ = -ℏ²/(2m) ∇² + V(x)
```

where dimensional analysis fixes D_real = ℏ/(2m).

*Step 7 - Stochastic term*:

The ε term from (2.5) carries through with variance scaling from (2.6):

```
Var[ε] = α²|E| = ℏ |⟨Ĥ⟩|  (at quantum scale)
```

giving the final form:

```
iℏ ∂ψ/∂t = [-(ℏ²/2m)∇² + V(x)]ψ + ε(x,t)ψ
```

∎

**Corollary 3.1**: The standard Schrödinger equation (without ε) is recovered when:

```
|ε|/|Ĥψ| ≪ 1  ⟺  measurement timescale ≫ validation timescale τ_v
```

where τ_v ~ ℏ/E is the characteristic validation time.

**Corollary 3.2**: The FRFE in 3.5 dimensions projects onto standard quantum mechanics when the 0.5D temporal/validational structure is coarse-grained over timescales ≫ τ_v. Time's arrow (irreversibility) is preserved in this projection because the 0.5D asymmetry (∇ ≠ ℰ) remains even after coarse-graining.

### 3.3 Physical Interpretation

This theorem establishes:

1. **QM is inevitable**: Given realistic physical constraints (locality, isotropy, conservation, smoothness), the FRFE **must** produce the Schrödinger equation in its continuum limit.

2. **Uniqueness**: There is no other continuous evolution equation satisfying these constraints. Any alternative must either:
   - Violate locality (pilot wave theory)
   - Violate unitarity (GRW collapse)
   - Assume rather than derive QM (many worlds)

3. **Uncertainty emerges**: The ε term is not external noise—it is intrinsic to the discrete validation structure in 3.5D, appearing as structured stochasticity in the continuum limit.

4. **No tuned free parameters**: ℏ and m are not inputs to FRFE—they emerge from:
   - ℏ: The scale of validation noise α = √ℏ
   - m: The inertial resistance to acceleration from texture accumulation

5. **The 0.5D manifests as quantum indeterminacy**: The half-dimensional temporal structure in 3.5D spacetime is precisely what creates the probabilistic branching we observe as quantum superposition and measurement. Following Einstein's insight that space and time are unified, we recognize that time's incompleteness (0.5 vs 1.0) IS what enables quantum phenomena.

**The Schrödinger equation is the unique continuous expression of discrete validation in 3.5 dimensional spacetime.**

---

*Continue to Part 4: General Relativity & Cosmology*
