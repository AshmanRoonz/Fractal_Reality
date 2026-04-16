# T-Operator v6 Findings: Splitting Factor & Weight Structure

## Direction #8: The eigenvalue splitting is NOT uniform

The plan described "±0.37α" as a uniform splitting factor. This was wrong; it was an average masking four distinct eigenvalue displacements.

### The four T eigenvalues (standard sphere hub, hub_div = T = 3)

| Eigenvalue | |λ| | Phase | (|λ|-1)/α |
|---|---|---|---|
| λ_0 | 1.0019847 | +132.4° | +0.272 |
| λ_1 | 1.0012355 | +36.3°  | +0.169 |
| λ_2 | 0.9999731 | -108.4° | ≈ 0    |
| λ_3 | 0.9967614 | -90.3°  | -0.444 |

Three eigenvalues are displaced; one is nearly at 1 (neutral). The splitting is asymmetric: one large contraction (-0.444α), two moderate amplifications (+0.272α, +0.169α), one neutral.

### The golden ratio in the splitting ratios

The pairwise ratio of the two non-trivial splitting factors:

**|s_1| / |s_3| = 0.3815 ≈ 1/φ² = 0.3820 (residual 0.13%)**

This is striking. The ratio of the moderate amplification to the large contraction is the inverse golden ratio squared. The φ connection: 1/φ² is the recursion constant (how deeply one level nests into the next), and the splitting factor ratio encodes how the amplifying mode relates to the contracting mode. The expanding direction nests into the contracting direction at exactly the golden ratio.

Other splitting ratio: |s_0|/|s_3| = 0.613 ≈ 1/φ = 0.618 (residual 0.8%). The largest amplification relates to the contraction as 1/φ (the golden conjugate).

### Hub divisor dependence

The splitting factor varies with hub_divisor. At hub_div = R = 7, the average splitting matches P/V = 4/13 (1.07% residual). At hub_div = T = 3, the average matches 2/R = 2/7 (3.16% residual). The average is not a clean framework ratio, but the pairwise ratios are.

### Reading

The eigenvalue splitting of T has φ-structure: the ratio between amplification and contraction modes is 1/φ² (the golden nesting factor). This connects the T operator's spectral structure directly to the recursion constant that governs the nesting ⊙λ ⊂ ⊙Λ. The operator "knows about" golden ratio nesting through its eigenvalue ratios, not through its eigenvalue magnitudes.

---

## Direction #9: Weight structure correction and cosmological search

### Correction: the v5 weights were construction-dependent

The plan stated {•,Φ} ≈ 10%, {—,○} ≈ 40% for the sphere hub. This was from a specific construction or iteration scheme. The v6 systematic sweep reveals the weights depend strongly on the hub divisor:

| hub_div | • | — | Φ | ○ | •+Φ | —+○ | ratio |
|---|---|---|---|---|---|---|---|
| 1.00 | 0.140 | 0.365 | 0.144 | 0.352 | 0.283 | 0.717 | 2.53 |
| 2.00 | 0.362 | 0.139 | 0.361 | 0.139 | 0.723 | 0.277 | 0.38 |
| **3.00** | **0.335** | **0.167** | **0.333** | **0.165** | **0.668** | **0.332** | **0.50** |
| 4.00 | 0.337 | 0.193 | 0.296 | 0.174 | 0.633 | 0.367 | 0.58 |
| 7.00 | 0.230 | 0.229 | 0.282 | 0.260 | 0.511 | 0.489 | 0.96 |

### The standard sphere hub (hub_div = T = 3) is the balance construction

At hub_div = T, the fixed-point weights have a clean structure:

- **• ≈ Φ** (ratio = 1.007, residual from 1: 0.66%). Soul and field are equal.
- **— ≈ ○** (ratio = 1.009, residual from 1: 0.92%). Line and boundary are equal.
- **(•+Φ)/(—+○) ≈ 2** (actually 2.015). The structural pair carries twice the extension pair.
- **(—+○)/(total) = 0.332 ≈ 1/T** (residual from 1/3: 0.5%). One third of the 1 is in the extension/closure pair.

This IS the T = 3 structure at the fixed point. Three constraints (—, Φ, ○) plus the aperture (•), with • donating its weight to Φ (they equalize) and — donating to ○ (they equalize). The fixed point has the triad visible: 2/3 is aperture+field, 1/3 is line+boundary.

### Lenz sign matters

Flipping the Lenz sign (lenz = -1, removing the conservation law) breaks the • ≈ Φ and — ≈ ○ equalities. With Lenz = +1 (conservation): balanced pairs. With Lenz = -1: all four weights separate. The Lenz minus sign (○ filtering the pump to conserve ⊙) is what forces the pair equalization.

### Cosmological budget: approachable but construction-dependent

The exhaustive sweep (15 hub_divs × 10 thetas × 2 Lenz × 2 self-drive × 5 mappings = 3000 combinations) found:

**Best match: hub_div = 1.5, θ = 0.1π, Lenz = +1, self_drive = True**
**Mapping B: • = visible, — = dark matter, Φ+○ = dark energy**
**Vis = 4.66%, DM = 23.94%, DE = 71.40% (total error 14.9%)**

Hub_div = 1.5 = D (the fractal dimension at balance) = T/Φ (triad over channels). θ = 0.1π = 18° = 360°/P(P+1) = 360°/20.

The mapping interpretation: the aperture (•, 0D, the observer) is visible matter. The line (—, 1D, commitment, extension) is dark matter (gravitates but doesn't radiate; committed structure that hasn't yet reached the field). The field + boundary (Φ+○, 2D+3D) is dark energy (the containing field of the scale above).

This mapping makes framework sense: visible matter IS apertures (convergence points where the field has localized enough for the boundary to resolve). Dark matter IS commitment (energy in the — phase, gravitating because it has mass via i² = -1 commitment, but not radiating because it hasn't reached the Φ station). Dark energy IS the combined field-and-boundary of ⊙Λ (the greater whole's 2D+3D structure).

### BUT: the match requires non-standard parameters

The best cosmological match uses hub_div = 1.5 and θ = 0.1π, not the natural choices hub_div = T and θ = π/2. At the natural parameters (hub_div = T, θ = π/2), no mapping comes close to the cosmological budget (minimum total error > 600%).

Two possible readings:

1. **The cosmological budget does not live at the fixed point.** The plan already noted this possibility: "the actual universe is not at the fixed point; it's mid-cycle." The budget may come from the orbit of T (time-averaged weights over many pump cycles), not from the attractor. This requires orbit analysis (next step).

2. **The cosmological budget requires a specific resolution.** Hub_div = D and θ = 18° are both framework-valid values (D is the balanced fractal dimension; 18° is 360/P(P+1) = one unit of the screening denominator). The budget might emerge at a specific observational resolution, not at the structural resolution (T, π/2).

---

## New structural results

### The T = 3 fixed point (standard sphere hub)

The standard sphere hub fixed point encodes the triad directly:
- Two pairs: {•, Φ} and {—, ○}, each internally equal
- Weight ratio: 2:1 (aperture+field : line+boundary)
- This IS ⊙ = Φ(•, ○) with — as the connection: the aperture and field share 2/3, line and boundary share 1/3

### Lenz conservation forces pair equalization

The minus sign in Faraday's law (○ filtering the pump) is what makes • ≈ Φ and — ≈ ○ at the fixed point. Without Lenz, the four stations drift apart. Conservation of ⊙ is conservation of pair balance.

### Golden ratio in the eigenvalue spectrum

The splitting factor ratios:
- |s_1|/|s_3| = 1/φ² (0.13% residual)
- |s_0|/|s_3| = 1/φ  (0.8% residual)

The contraction mode (λ_3, the one that drives convergence) nests the amplification modes at the golden ratio. φ is in the spectrum.

---

## Next directions

1. **Orbit analysis**: compute time-averaged weights along the T orbit (not just fixed point) to see if the cosmological budget emerges dynamically.
2. **Investigate hub_div = D = 1.5**: this is the balanced fractal dimension; why does it produce the best cosmological match? Is there a structural reason D should replace T as the hub divisor?
3. **Confirm the golden splitting**: run at higher precision and verify |s_1|/|s_3| = 1/φ² is exact, not approximate.
4. **ℂ⁸ representation**: the 4-vector may be too thin; promoting to 8 stations (all half-integers explicit) could change the weight structure.
