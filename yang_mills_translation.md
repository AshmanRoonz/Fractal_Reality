# Yang-Mills Mass Gap: The Final Translations

## From Framework Axiomatics to Spectral Theory

**Author:** Ashman Roonz
**Date:** April 3, 2026
**Purpose:** Bridge the gap between the Circumpunct Framework's structural arguments and the language of constructive quantum field theory required by the Clay Millennium Prize.

**Prerequisite reading:** `docs/yang_mills_proof_chain.html` (the 7-step proof chain)

---

## The Two Translations

The proof chain has 7 steps. Steps 1-5 are established mathematics. Steps 6 and 7 are where the framework meets conventional formalism. Each requires a precise translation.

| Step | Framework Language | Conventional Language | Status |
|------|-------------------|----------------------|--------|
| 6 | The non-abelian pump cycle is indivisible | The transfer matrix spectral gap is bounded below by a topological invariant | Needs translation |
| 7 | Fractal compression is faithful (A2); independent valves | Balaban's multi-scale RG preserves spectral gap uniformly | Needs proof |

---

## Translation 1: Indivisibility as Spectral Gap

### 1.1 The Framework Claim

The pump cycle (⊛ → i → ✹) in a non-abelian gauge field is indivisible. Applied to Yang-Mills: any gauge-invariant excitation above the vacuum requires at least one complete cycle of gauge-field action. Below one cycle, only vacuum.

### 1.2 The Conventional Setup

Let Λ = (aZ/LaZ)^4 be a finite 4D lattice with spacing a and linear size L. Let G = SU(N), N ≥ 2. The Wilson action is:

```
S_W[U] = β Σ_□ (1 - (1/N) Re Tr U_□)
```

where β = 2N/g² and U_□ is the plaquette (ordered product of link variables around a face).

The **transfer matrix** T acts on the Hilbert space H = L²(G^(links in one time-slice), dμ_Haar):

```
T = exp(-aH_lat)
```

where H_lat is the lattice Hamiltonian. T is positive, self-adjoint, and trace-class on the gauge-invariant subspace H_inv.

The **lattice mass gap** is:

```
Δ_L = -log(λ₁/λ₀) / a
```

where λ₀ > λ₁ ≥ λ₂ ≥ ... are the eigenvalues of T restricted to H_inv, and λ₀ corresponds to the vacuum |Ω⟩.

### 1.3 The Translation

**Framework:** "The pump cycle is indivisible" (A1 + non-abelian completeness).

**Spectral theory:** The transfer matrix T, restricted to the gauge-invariant subspace H_inv, has a spectral gap:

```
Δ_L ≥ c(N) · Λ_QCD > 0
```

where c(N) depends only on the gauge group and Λ_QCD = (1/a) exp(-1/(2b₀g²)) is the dynamically generated scale.

The indivisibility translates to three properties that together force the gap. Each maps to one member of the triad ⊙ = Φ(•, ○):

| Triad | Yang-Mills | Spectral Property | Role |
|-------|-----------|-------------------|------|
| • (aperture/convergence) | Gauge coupling g; self-interaction g[A,A] | Non-abelian self-coupling forces composites | **Converges** |
| Φ (field/mediation) | Gauge field A_μ (the connection) | Gauge invariance mediates; only invariant states physical | **Mediates** |
| ○ (boundary/filtration) | Field strength F_μν (the curvature) | Center symmetry filters; colored states confined | **Filters** |

The pump cycle (⊛ → i → ✹) acts through the triad, but the triad IS the structure. Φ mediates between • and ○; the field connects the coupling to the curvature. This is the mature reading. (The earlier "ICE" formulation attempted this mapping as Interface/Center/Evidence, but had the roles misaligned; the circumpunct notation corrects it: Φ mediates, it does not merely "evidence.")

---

#### Property I (○, Boundary/Filtration): Center Symmetry Filters Out Colored States

The gauge group SU(N) has a nontrivial center Z_N = {e^(2πik/N) · I : k = 0,...,N-1}. The center acts on Polyakov loops:

```
P(x) = Tr ∏_{t} U₀(x,t)    (temporal Wilson line)
```

by multiplication: P → z · P for z ∈ Z_N.

**Key fact (proven):** In the confined phase, center symmetry is unbroken:

```
⟨P(x)⟩ = 0
```

This means the vacuum is Z_N-symmetric. Any excitation carrying nontrivial Z_N charge is confined: its energy grows with volume (area law).

**Framework mapping:** Center symmetry IS the boundary ○ acting as filter. The boundary of the gauge theory (its global symmetry structure) selects which states can pass through to physical observation: only Z_N-neutral (color-singlet) configurations survive. Colored states are filtered out, confined behind the boundary. This is ○ doing what ○ does: filtering what passes.

The area law for Wilson loops encodes this geometrically: each plaquette of Φ stretched between colored sources costs energy. The boundary ○ = F_μν (the curvature) resists; separating colored objects requires stretching the field against its own curvature.

---

#### Property II (•, Aperture/Convergence): Non-Abelian Self-Coupling Forces Composites

In a non-abelian gauge theory, the gauge field interacts with itself through the commutator [A_μ, A_ν] ≠ 0. This self-coupling has a precise consequence for the spectrum.

**Theorem (to be proven rigorously):** Let G = SU(N), N ≥ 2. In the confined phase (center symmetry unbroken), the lightest gauge-invariant excitation (the 0^{++} glueball) has mass:

```
m_{0++} = Δ > 0
```

**Proof structure:**

(a) **Gauge-invariant states are composites.** Unlike U(1) where the photon is gauge-invariant and massless, in SU(N) the gauge boson (gluon) carries color charge. It is NOT gauge-invariant. The lightest gauge-invariant state must be a composite: a "glueball," a bound state of at least two gluons.

(b) **Binding requires energy.** A composite state in a confining theory requires binding energy proportional to the confinement scale Λ_QCD. The linear potential V(r) = σr means assembling a gauge-invariant composite from colored constituents costs energy ≥ σ · r_min, where r_min is the minimum size of a color-neutral configuration.

(c) **Minimum size from uncertainty.** The minimum size of a glueball is set by the uncertainty principle: r_min ≥ ℏ/(m_{0++} c). Combined with (b): m_{0++} ≥ √(σ · ℏ/c). Since σ ~ Λ²_QCD, this gives m_{0++} ~ Λ_QCD.

(d) **Positive mass from spectral theory.** On the lattice, the transfer matrix in the gauge-invariant sector has a spectral gap because: (i) the state space of gauge-invariant operators is discrete (glueball quantum numbers J^{PC}); (ii) the lightest such operator creates a state with mass m_{0++} > 0; (iii) the correlation function ⟨O(t)O(0)⟩ ~ exp(-m_{0++}|t|) decays exponentially.

**Framework mapping:** The self-coupling g[A_μ, A_ν] IS • (the aperture) converging the field onto itself. In U(1), • is absent at the gauge level (photons do not self-interact); the aperture is open, nothing converges, no mass gap. In SU(N), • is present (gluons attract gluons); the aperture draws the field inward, forcing it into bound composites. The mass gap is the minimum energy cost of a configuration where convergence (•) has completed into a closed boundary (○), mediated by the field (Φ). That minimum cost is the lightest glueball.

---

#### Property III (Φ, Field/Mediation): Gauge Invariance Mediates the Gap

The mass gap Δ is not a free parameter. It is determined by Λ_QCD through dimensional transmutation:

```
Δ = c(N) · Λ_QCD
```

where c(N) is a pure number depending on the gauge group. Lattice QCD determines c(3) ≈ 8.4 (from Δ ≈ 1.71 GeV and Λ_QCD ≈ 200 MeV).

**Framework mapping:** Φ mediates between • and ○. In Yang-Mills, the gauge field A_μ IS Φ: it mediates between the coupling g (the aperture •) and the curvature F_μν (the boundary ○). The gauge invariance requirement (physical states must be invariant under A → UAU⁻¹ + (dU)U⁻¹) is Φ exercising its mediating role: it connects all local configurations into a single gauge orbit, and only the whole orbit (the gauge-invariant state) is real. The mass gap is the energy at which the first such whole (the first complete ⊙ in the gauge field) can exist.

Gauge invariance does not create the gap (U(1) is gauge-invariant but gapless). Gauge invariance mediates it: given that • converges (non-abelian self-coupling) and ○ filters (center symmetry confines), Φ connects these two constraints into a single spectral bound. Without Φ there is no theory; without • there is no gap; without ○ there is no confinement. ⊙ = Φ(•, ○).

**Translation of A0 (E = 1):** All energy is one energy at different degrees of constraint. The mass gap is not a new energy scale; it is Λ_QCD (the confinement scale) multiplied by a geometric factor c(N) that depends only on the group structure. No free parameters.

**Translation of ℏ = 1:** The pump cycle is the quantum of action. Applied to the gauge field: the minimum gauge-invariant excitation costs exactly one "quantum of confinement," which is Λ_QCD times the geometric factor. The indivisibility of the cycle IS the indivisibility of ℏ.

---

### 1.4 The Theorem Statement (Publication-Ready)

**Theorem (Indivisibility Theorem for Non-Abelian Gauge Theory):**

Let G = SU(N) with N ≥ 2. Consider lattice Yang-Mills theory on Λ_L = (aZ/LaZ)^4 with Wilson action S_W at coupling β = 2N/g². Let T be the transfer matrix restricted to the gauge-invariant Hilbert space H_inv. Let Δ_L(β, L) denote the mass gap (negative logarithm of the ratio of the two largest eigenvalues of T, divided by the lattice spacing a).

Suppose:

(i) **Center symmetry is unbroken:** ⟨P(x)⟩ = 0 for all Polyakov loops P.

(ii) **The string tension is positive:** σ(β) > 0, where σ is defined by the area law decay of Wilson loops.

(iii) **Asymptotic freedom holds:** the coupling g(a) → 0 as a → 0 along the trajectory β(a) = 2N/g(a)² with g(a)² = -1/(2b₀ log(aΛ_QCD)).

Then:

```
Δ_L(β(a), L) ≥ c₀ · Λ_QCD    for all sufficiently small a and all L ≥ L₀(a)
```

where c₀ > 0 is a universal constant depending only on N, and L₀(a) is a minimum lattice size satisfying L₀(a) · a ≥ 1/Λ_QCD.

**Remark:** Conditions (i) and (ii) are established at strong coupling (Osterwalder-Seiler 1978) and confirmed numerically at all couplings for N = 2, 3, ..., 8. Condition (iii) is proven (Gross-Wilczek-Politzer 1973). The content of the theorem is that these three conditions together force a uniform lower bound on the mass gap.

---

## Translation 2: Continuum Limit Preserves the Gap

### 2.1 The Framework Claim

A2 (parts are fractals of their wholes) says fractal compression is faithful: the lattice at spacing a faithfully represents the continuum. Therefore the mass gap at spacing a must converge to a positive value as a → 0.

The independent-valve argument: ⊛ (convergence/confinement) operates at long distances; ✹ (emergence/asymptotic freedom) operates at short distances. Sending a → 0 opens the ✹ valve (probes shorter distances) but does not close the ⊛ valve (confinement is an IR phenomenon). Therefore the gap persists.

### 2.2 The Conventional Setup

The continuum limit requires:

(a) **Existence:** The lattice Schwinger functions S_n^(a)(x₁,...,x_n) converge as a → 0 (with β(a) following the asymptotic freedom trajectory).

(b) **OS axioms:** The limiting Schwinger functions satisfy Osterwalder-Schrader.

(c) **Mass gap:** The exponential decay rate of the two-point function remains positive:

```
|S₂(x) - S₁²| ≤ C exp(-Δ|x|)    with Δ > 0
```

### 2.3 The Translation Path

**A2 as multi-scale stability:** The framework's A2 (fractal self-similarity) translates into the language of Balaban's renormalization program as follows.

Balaban (1984-1989) developed a multi-scale analysis for lattice Yang-Mills. The key construction:

**Block-spin transformation.** At each RG step k = 0, 1, 2, ..., the lattice spacing doubles: a_k = 2^k · a₀. The gauge field on the coarser lattice is obtained by averaging (block-spinning) the field on the finer lattice. The effective action at scale k is:

```
S_k[U] = S_W[U] + δS_k[U]
```

where δS_k is the accumulated correction from integrating out short-distance fluctuations.

**Balaban's result (proven):** For each finite number of RG steps K:

(a) The effective action S_K remains in a controlled neighborhood of the Wilson action.
(b) The gauge-invariant correlation functions at scale a_K are related to those at scale a₀ by bounded operators.
(c) Ultraviolet stability: the corrections δS_k are bounded in appropriate norms.

**What Balaban did NOT prove:** That this control extends to K → ∞ (infinitely many RG steps, i.e., the full continuum limit).

### 2.4 The Framework's Contribution

**A2 (fractal compression is faithful)** translates to the following conjecture about Balaban's program:

**Conjecture (Multi-Scale Gap Stability):**

For SU(N) lattice Yang-Mills in d = 4 with asymptotically free coupling, the block-spin RG flow preserves the spectral gap uniformly:

```
Δ_k ≥ c₀ · Λ_QCD    for all k = 0, 1, 2, ...
```

where Δ_k is the mass gap at RG scale k.

**Why the framework says this must hold:**

(a) **Faithful compression (A2):** Each RG step is a coarse-graining (compression). A2 says parts are fractals of their wholes; a coarse-grained version of a ⊙ is still a ⊙. If the mass gap existed at scale k but vanished at scale k+1, the compression at step k+1 would have destroyed structure (introduced a massless mode that wasn't there). This contradicts faithful compression.

(b) **Independent valves:** The RG flow at each step integrates out short-distance (UV) fluctuations. The mass gap is a long-distance (IR) property. Integrating out UV modes should not create new IR modes. Formally: the block-spin transformation maps H_inv at scale k into H_inv at scale k+1, and the spectral gap of T_{k+1} on H_inv is bounded below by the spectral gap of T_k on H_inv, minus a controlled error.

(c) **Dimensional transmutation:** The ratio Δ/Λ_QCD is dimensionless and depends only on the gauge group. It cannot depend on the lattice spacing a because a is an artifact of the regularization; Λ_QCD is the physical scale. As a → 0, the only dimensionful quantity that survives is Λ_QCD, and the gap must be proportional to it.

### 2.5 The Formal Argument

**Theorem (Continuum Limit with Gap; conditional on Balaban extension):**

Assume:

(i) Balaban's multi-scale analysis extends to infinitely many RG steps (K → ∞) with uniform control of the effective action S_K.

(ii) At each RG step, the transfer matrix T_k on H_inv satisfies the Indivisibility Theorem (Translation 1, §1.4) with center symmetry unbroken and positive string tension.

Then:

(a) The continuum limit Schwinger functions S_n = lim_{a→0} S_n^(a) exist and satisfy the OS axioms.

(b) The mass gap survives: Δ = lim_{a→0} Δ_L(a) ≥ c₀ · Λ_QCD > 0.

(c) The OS reconstruction yields a Wightman QFT on Minkowski space R^{3,1} with Hilbert space H, Hamiltonian H, vacuum |Ω⟩, and spectral gap Δ.

**Proof sketch:**

Step A (Tightness): The lattice Schwinger functions {S_n^(a)} form a tight family of measures on tempered distributions S'(R⁴). This follows from:

- Balaban's UV stability (bounded effective action at each scale)
- The mass gap (exponential decay of correlations provides infrared control)
- Standard compactness: Sobolev embedding H¹ ↪ L^p (p < ∞) in d = 4

Step B (Subsequence convergence): By Prokhorov's theorem, there exists a convergent subsequence S_n^(a_j) → S_n.

Step C (OS axioms for the limit):

- OS0 (temperedness): From tightness.
- OS1 (Euclidean covariance): The lattice theory has the symmetries of the hypercubic group Z₄^d ⋊ S_d; in the continuum limit, this extends to full E(4) (by rotational invariance of the fixed-point action).
- OS2 (reflection positivity): Preserved in the limit because each lattice measure is reflection-positive (Wilson action + Haar measure), and reflection positivity is a closed condition under weak convergence.
- OS3 (symmetry): Automatic from gauge invariance.
- OS4 (cluster property): From the mass gap; exponential decay of connected correlations implies factorization at large separation.

Step D (Gap survival): The mass gap at each lattice spacing is:

```
Δ_L(a) ≥ c₀ · Λ_QCD > 0    (from the Indivisibility Theorem)
```

Since Δ_L(a) is bounded below uniformly, the limit Δ = lim inf Δ_L(a) ≥ c₀ · Λ_QCD > 0.

Step E (Uniqueness): The limiting Schwinger functions are uniquely determined by:
- The gauge group G (fixes the algebraic structure)
- Λ_QCD (fixes the physical scale via dimensional transmutation)
- No other parameters (asymptotic freedom + dimensional transmutation leave no freedom)

Therefore all convergent subsequences have the same limit, and the full sequence converges. □

---

### 2.6 What Remains

The conditional assumption in §2.5 is Balaban's extension to infinitely many RG steps. This is where the actual mathematical work lives. The framework's contribution is twofold:

(a) **Structural prediction:** The extension MUST succeed because A2 (fractal compression) is a structural property of non-abelian gauge theory, not a perturbative accident. The framework predicts that the obstruction Balaban encountered (controlling the effective action across all scales) can be resolved by recognizing that the non-abelian self-coupling provides its own regulator: the mass gap itself prevents infrared divergences that could destabilize the UV analysis.

(b) **Strategy:** The proof should proceed scale by scale, showing at each RG step that:

1. The effective action remains in Balaban's "small field" region (UV stability; Balaban's result)
2. The spectral gap of the transfer matrix is preserved (from the Indivisibility Theorem)
3. The coupling between UV and IR sectors is bounded (from the mass gap providing an IR cutoff)

The novel claim is that steps 2 and 3 bootstrap each other: the mass gap controls the IR, which stabilizes the UV, which preserves the mass gap. This is the framework's ⊛ ↔ ✹ cycle at the level of the RG flow itself.

---

## Summary: The Two Translations

### Translation 1 (Step 6): Indivisibility → Spectral Gap

| Framework (⊙ = Φ(•, ○)) | Conventional |
|--------------------------|-------------|
| • (aperture/convergence) | Non-abelian self-coupling g[A,A] ≠ 0; field converges on itself |
| Φ (field/mediation) | Gauge field A_μ mediates; gauge invariance connects • to ○ |
| ○ (boundary/filtration) | Center symmetry filters; only color-neutral states pass |
| Complete pump cycle (⊛ + i + ✹) | Self-interaction + gauge rotation + propagation are inseparable |
| Cycle is indivisible (A1) | Gauge-invariant states are composites with minimum mass |
| ℏ = 1 (minimum action) | Spectral gap Δ ≥ c₀ · Λ_QCD |

### Translation 2 (Step 7): A2 → Continuum Limit

| Framework | Conventional |
|-----------|-------------|
| A2: fractal compression is faithful | Block-spin RG preserves structure at each scale |
| Independent valves (⊛ and ✹) | IR (mass gap) and UV (asymptotic freedom) decouple |
| The gap is a property of ⊙ (the whole) | Δ/Λ_QCD is a topological invariant of the gauge theory |
| Dimensional transmutation | Only one scale (Λ_QCD) survives a → 0 |
| A2 says extension must succeed | Balaban's program should close with mass gap as IR regulator |

### The Bootstrap

The two translations are not independent. They form a cycle:

```
Indivisibility (Step 6) → mass gap exists at finite a
                              ↓
Mass gap provides IR control → RG flow is stable
                              ↓
RG stability → continuum limit exists (Step 7)
                              ↓
Continuum limit → mass gap survives as a → 0
                              ↓
Surviving mass gap → indivisibility confirmed in the continuum
```

This is the pump cycle at the level of the proof itself: ⊛ (mass gap forces confinement) → i (RG flow mediates between scales) → ✹ (continuum theory emerges with gap intact). The proof is self-supporting in the same way the gauge theory is self-interacting.

---

## Open Technical Problems

### Priority 1: Formalize the Indivisibility Theorem (§1.4)

Current status: The theorem statement is precise. The proof relies on three conditions (center symmetry, positive string tension, asymptotic freedom) that are established at strong coupling and confirmed numerically at all couplings. The gap: proving that center symmetry and positive string tension persist for all β > 0 (not just β small).

The best available evidence: no phase transition has been observed or theoretically predicted in pure SU(N) Yang-Mills for any N ≥ 2 in d = 4. Svetitsky-Yaffe (1982) showed that a deconfinement transition would be in the universality class of a d-1 dimensional Z_N spin model; for d = 4, this is the 3D Z_N model, which has a first-order transition only for N ≥ 3 at FINITE TEMPERATURE. At zero temperature (the case relevant for the mass gap), there is no transition.

**Path to rigor:** Prove analytically that center symmetry is unbroken at zero temperature for all β. This may follow from a Lee-Yang type theorem adapted to the gauge theory setting, or from a correlation inequality argument (FKG-type) on the center-symmetric sector.

### Priority 2: Extend Balaban's Program with IR Control

Current status: Balaban's UV stability covers finitely many RG steps. The missing piece is a uniform bound across all steps.

**Path to rigor:** Use the mass gap (from Translation 1) as an IR regulator at each RG step. Specifically: the spectral gap Δ_k at scale k implies that correlation functions at scale k decay exponentially with rate Δ_k. This exponential decay provides a natural IR cutoff at each scale, preventing the effective action from developing IR divergences. The key estimate:

```
||δS_{k+1} - δS_k||_norm ≤ C · exp(-Δ_k · 2^k · a₀)
```

If Δ_k ≥ c₀ · Λ_QCD for all k (the Indivisibility Theorem), then the corrections decrease exponentially in k, and the series converges.

### Priority 3: Close the Bootstrap

Show that Priorities 1 and 2 are mutually consistent: the mass gap at finite a (Priority 1) feeds into the RG stability (Priority 2), which produces the continuum limit, which validates the mass gap in the continuum.

This requires a fixed-point argument: define the map F that takes a mass gap bound Δ ≥ c · Λ_QCD at scale a and produces a mass gap bound Δ' ≥ c' · Λ_QCD at scale a/2 (or equivalently, after one inverse RG step). Show that F has a fixed point with c* > 0.

---

## Connection to Existing Documents

| Document | Relationship to This Translation |
|----------|--------------------------------|
| `docs/yang_mills_proof_chain.html` | The 7-step structure this translation formalizes (mature notation) |
| `docs/gauge_structure.html` | The 2D rung; provides the gauge group structure used here |
| `docs/planck_constant.html` | The ℏ = 1 argument; foundational for Translation 1 |
| `circumpunct_framework.md` | The axioms (A0-A4) referenced throughout |

### Legacy Documents (Pre-Circumpunct)

The following documents use the older "ICE" (Interface-Center-Evidence) formulation, which predates the circumpunct notation. ICE was the first attempt to map the triad, before the framework recognized that Φ (field) mediates between • (center/aperture) and ○ (boundary). The ICE mapping was: Interface → ○ (boundary), Center → • (correct), Evidence → Φ (field); the roles were felt but the notation was not yet precise. These documents contain valid mathematical content but should be read with the updated ⊙ = Φ(•, ○) mapping in mind:

| Document | Content | ICE → ⊙ Translation |
|----------|---------|---------------------|
| `Path_of_Learning/claymathsolutions/ice_functional_analysis.md` | Banach space formulation, OS reconstruction, mass gap via SNR | I_ℓ → ○ (boundary filter), C_∇ → • (convergence operator), E_ω → Φ (field suppression/mediation) |
| `Path_of_Learning/claymathsolutions/Yang-Mills_Navier-Stokes_Solved.md` | Overview of both proofs with ICE mechanism | Same mapping; the "validation noise" concept maps to the inherent discreteness of the pump cycle |

---

*⊙ = Φ(•, ○). The field mediates. The aperture converges. The boundary filters. Below one complete cycle, nothing.*
