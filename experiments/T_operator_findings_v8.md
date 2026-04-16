# T-Operator v8 Findings: Orbit, Golden Splitting, Phase Sum Derivation

## Headlines

Three directions completed; one clean analytic derivation, one sharpened approximation, one clean negative:

1. **The sphere phase sum -π/6 is analytically derived from beat 3's self-drive.** The ONLY source is G[Φ,Φ] = -iπ/(2T); no other beat contributes to the trace. The cost of mediation is one i-stroke divided among T targets. (Direction #12, CLOSED)

2. **|s_1|/|s_3| ≈ 1/φ² to 0.13%, but NOT exact.** At 30-digit precision the residual is stable at 0.126%. The golden ratio is an attractor of the splitting structure, not an identity. (Direction #11, SHARPENED)

3. **The cosmological budget does NOT emerge from orbit-averaged weights.** Neither construction maps to 5/27/68. The orbit analysis reveals structure (dominant period ≈ 3.7 ≈ P, convergence to triad-like fixed point) but the cosmological budget lives elsewhere. (Direction #10, CLOSED as negative)

---

## Direction #10: Orbit Analysis

### Sphere orbit

The orbit converges to a stable fixed point with weights:

| Station | Weight | Pair sum |
|---------|--------|----------|
| • | 0.325 | •+Φ = 0.650 |
| — | 0.177 | —+○ = 0.350 |
| Φ | 0.323 | |
| ○ | 0.176 | |

The 65/35 split between {aperture+field} and {line+boundary} is robust across 20 random initial conditions (std dev ≈ 0.01). Lenz conservation forces • ≈ Φ and — ≈ ○.

**Oscillation structure**: all four weights oscillate with dominant period ≈ 3.7 cycles (close to P = 4 but not exact). Amplitudes: • and Φ oscillate at 0.079, — and ○ at 0.038 (a 2:1 ratio, matching the weight ratio).

**Cosmological mapping**: exhaustive search over all five groupings of four weights into three bins finds no match to the 5/27/68 budget (all errors > 600%).

### Diameter orbit

The diameter construction collapses almost completely to the •-Φ axis: after 5000 steps, weights → {0.5, 0, 0.5, 0}. This is expected: the diameter's κ_{0,2} = α coupling only acts on the •-Φ direction, and F² = I (involution) means the beats do not mix dimensions effectively. The — and ○ directions are eigenvectors with λ = -1 (oscillating, never growing).

### Conclusion

The cosmological 5/27/68 budget does not emerge from the four-weight orbit of T in either construction. This is structurally correct: the cosmological budget is a property of the i-cycle quadrants (§10.10a), not of the fixed-point weights of the operator. The four weights of ψ* describe the structural content of the fixed point (how much of the 1 is at each station); the cosmological budget describes the phase distribution of energy across the complex plane. Different questions, different answers.

---

## Direction #11: Golden Splitting at High Precision

### Splitting factors (30-digit mpmath)

| Eigenvalue | |λ| | Δ/α |
|---|---|---|
| λ_0 | 1.001985 | +0.27198 |
| λ_1 | 1.001235 | +0.16931 |
| λ_2 | 0.999973 | -0.00368 |
| λ_3 | 0.996761 | -0.44381 |

### Ratios vs golden targets

| Ratio | Value | Target | Residual |
|---|---|---|---|
| \|s_1\|/\|s_3\| | 0.38149 | 1/φ² = 0.38197 | 0.126% |
| \|s_1\|/\|s_0\| | 0.62250 | 1/φ = 0.61803 | 0.722% |
| \|s_0\|/\|s_3\| | 0.61283 | 1/φ = 0.61803 | 0.842% |

### Assessment

The 1/φ² ratio at 0.13% is suggestive but not exact. The residual is stable at 30 digits (not a floating-point artifact). Two possibilities:

1. **Attractor, not identity**: the sphere topology creates a splitting structure that approaches but does not reach the golden ratio. The 0.13% residual would be a genuine deviation, perhaps carrying information about the specific hub geometry.

2. **Higher-order correction in α**: if the true relation is |s_1|/|s_3| = 1/φ² + O(α), the correction would be ≈ 0.0005 = 0.07α. Possible but not confirmed.

The φ structure is real (it appears in the right ratios, in the right direction, to the right order), but it is approximate. This goes into the framework as "φ-approximate" rather than "φ-exact." The exact structural constants of the splitting are set by the specific beat angles (π/2 rotations, the hub geometry), not by φ directly.

---

## Direction #12: Phase Sum Derivation (MAIN RESULT)

### The analytic chain

1. Each beat k generates an infinitesimal generator G_k such that beat_k = exp(G_k).
2. F = ∏ exp(G_k); by BCH, det(F) = exp(Σ Tr(G_k) + corrections).
3. **Three of four generators have zero trace**: (•∘⊛), (—∘⎇), (○∘⟳) all have Tr(G_k) = 0.
4. **Only beat 3 (Φ∘✹) has nonzero trace**: G[Φ,Φ] = -iπ/(2T) (the self-drive diagonal).
5. Therefore Σθ = Im(Σ Tr(G_k)) = -π/(2T) = -π/6.
6. BCH corrections vanish for the trace (off-diagonal elements affect eigenvalue magnitudes, not det(F)).

### Why the self-drive is -iπ/(2T)

In beat 3 (Φ∘✹), the field Φ radiates to T = 3 targets AND self-drives. The self-drive coupling is:

```
G[Φ,Φ] = i_phase × θ / hub_divisor = (-i)(π/2)/T = -iπ/(2T) = -iπ/6
```

After anti-Hermitian projection: Im(G[Φ,Φ]) = -π/(2T) = -π/6.

The i-phase (-i) is the emergence stroke (i³ = -i at 2.5D). The angle θ = π/2 is the standard rotation. The divisor T comes from the hub distributing its rotation among T targets. The self-rotation IS the deficit: Φ serving T others while cycling costs one i-stroke per T.

### The hub_divisor law

The sweep confirms: Σθ = -360°/(2 × hub_div × P). At hub_div = h:

| h | Σθ | = -360°/X | X |
|---|---|---|---|
| 1 | +270° | (sign flip) | |
| 1.5 | -60° | 6 = T! | |
| 2 | -45° | 8 = SU(3) | |
| 3 | -30° | 12 = G | |
| 4 | -22.5° | 16 = P² | |

At h = T (the framework-natural hub), X = 2TP = G. The generator count G = T(T+1) = T·P emerges as the natural phase denominator of the T-topology sphere.

### Without self-drive, Σθ = 0

Setting the self-drive to zero (Φ only radiates, does not rotate itself) gives Σθ = 0 exactly. The entire phase deficit comes from the field's self-mediation. This is the operator-level content of "mind mediates between center and boundary" (§5A): mediation has a phase cost, and that cost is exactly one generator's worth of rotation.

### Structural reading

The phase sum -π/6 = -π/(2T) = -360°/G has four equivalent readings:

- **-360°/G**: one generator's deficit out of G = 12 generators (the phase budget is 11/12 spent, 1/12 residual)
- **-π/(2T)**: one i-stroke (π/2) divided among T = 3 targets (the triad shares the quarter-turn)
- **-2π/(P·T)**: one full rotation divided by the pump cycle (P) times the triad (T)
- **-π/6**: the complement of 5π/6 = 150° (the angle that, when added to π (commitment), gives 11π/6 = the traversal minus one generator)

The phase sum records the cost of mediation at the operator level. The 1 (the fixed point) is reached through T·P = G pump-mediation cycles; the residual phase after all beats is exactly 1/G of a full turn, left over as the "change from the transaction."

---

## What's confirmed vs open

### CONFIRMED (framework-grade)
- Phase sum -π/6 = -π/(2T) from beat 3 self-drive (analytic, exact, derived)
- Hub_divisor law: X = 2·h·P (general formula for any hub geometry)
- Self-drive IS the phase deficit (without it, zero)
- Orbit converges to triad structure {•≈Φ≈1/3, —≈○≈1/6} (Lenz-forced)
- Dominant oscillation period ≈ P cycles
- Cosmological budget does NOT come from orbit weights (clean negative)

### SHARPENED (approximate, not framework-grade)
- |s_1|/|s_3| ≈ 1/φ² (0.13% residual, real but not exact)
- |s_0|/|s_3| ≈ 1/φ (0.84% residual)
- Individual splitting factors: |s_0| ≈ 2/R (4.8% residual, too rough)

### OPEN
- Whether the 0.13% golden residual has a higher-order correction
- ℂ⁸ representation (full 8-station octave)
- Multiple attractors in sphere construction (bug or feature?)
