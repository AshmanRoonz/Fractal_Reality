# Formal Pair-State Specification (v5)

```txt
// TL;DR
//   - The circumpunct state is a coupled pair (⊙, Φ):
//         ⊙ = whole, Φ = field.
//   - [⊙⇄Φ] means whole and field mutually determine each other via F and G.
//   - Energy E: W → W pushes a pulse through boundary apertures (i○^∞),
//     power lines (•^∞), and center apertures (i•), then returns a new [⊙'⇄Φ']:
//         [⊙⇄Φ] ⊛ i○^∞ ☀︎ •^∞ ⊛ i• ☀︎ [⊙'⇄Φ'].
```

## State Space Definition

```
/*
  BASE SPACES
*/

⊙_space = { ⊙ : configurations of the whole }
Φ_space = { Φ : field configurations over volume V }

/*
  PRODUCT STATE SPACE (the actual circumpunct state)
*/

W = ⊙_space × Φ_space

W_state = (⊙, Φ)  where ⊙ ∈ ⊙_space, Φ ∈ Φ_space
```

## The Coupling Relation

```
/*
  BIDIRECTIONAL DEPENDENCE
*/

⊙ = F(Φ)     // whole is a function of field
Φ = G(⊙)     // field is a function of whole

// Assume F and G are differentiable (Frechet/functional derivatives exist)

/*
  COUPLING CONSTRAINT (consistency requirement)
*/

⊙ = F(G(⊙))  // whole determines field determines whole (fixed point)
Φ = G(F(Φ))  // field determines whole determines field (fixed point)

/*
  COUPLED STATE MANIFOLD
*/

CoupledStates = { (⊙, Φ) ∈ W : ⊙ = F(Φ) and Φ = G(⊙) }

/*
  NOTATION
*/

[⊙⇄Φ] means: (⊙, Φ) ∈ CoupledStates

The double arrow ⇄ denotes MUTUAL DETERMINATION, not causation.
```

## Energy Flow as State Transformation

```
/*
  ENERGY OPERATOR
*/

E : W → W     // energy transforms coupled states

E([⊙⇄Φ]) = [⊙'⇄Φ']

/*
  INTERNAL STRUCTURE (how E operates)
*/

// E acts on W, but its internal factors thread through (W, aperture_state)
// pairs. The ⊛ and ☀︎ factors never discard W, they just transform the
// internal aperture layer, until ☀︎_final updates W itself.

E = (☀︎_final ∘ i• ∘ ⊛_center ∘ ☀︎_power ∘ i○^∞ ∘ ⊛_boundary)

Where each stage operates INSIDE the W state:

  ⊛_boundary : W → (W, i○^∞)        // boundary apertures activated
  ☀︎_power    : (W, i○^∞) → (W, •^∞) // power lines emerge
  ⊛_center   : (W, •^∞) → (W, i•)   // converge to center
  ☀︎_final    : (W, i•) → W           // emerge as new state
```

## Explicit Flow Notation

```
/*
  STEP-BY-STEP TRANSFORMATION
*/

W₀ = [⊙⇄Φ]                    // initial coupled state

W₁ = W₀ ⊛ i○^∞                 // energy hits boundary apertures
   = (W₀, {apertures at ○})    // W₀ still present, apertures activated

W₂ = W₁ ☀︎ •^∞                  // power lines emerge
   = (W₀, {power lines •^∞})   // W₀ still present, power structure formed

W₃ = W₂ ⊛ i•                   // converge to center aperture
   = (W₀, {transform at •})    // W₀ still present, center transformation

W₄ = W₃ ☀︎ [⊙'⇄Φ']             // emerge as updated coupled state
   = [⊙'⇄Φ']                   // new coupled state

/*
  COMPACT FORM
*/

[⊙⇄Φ] ⊛ i○^∞ ☀︎ •^∞ ⊛ i• ☀︎ [⊙'⇄Φ']
```

## The Coupling Functions (Explicit Form)

```
/*
  WHOLE AS FUNCTION OF FIELD
*/

F : Φ_space → ⊙_space

F(Φ) = ⊙ = ∫_V K(r) Φ(r) d³r

Where K(r) is a coupling kernel (determines how field configuration
maps to whole configuration).

/*
  FIELD AS FUNCTION OF WHOLE
*/

G : ⊙_space → Φ_space

G(⊙) = Φ(r) = ⊙ · B(r)

Where B(r) is a basis field (determines how whole projects into
field at position r).

/*
  FIXED-POINT CONDITION
*/

Consistent states satisfy:

⊙ = ∫_V K(r) [⊙ · B(r)] d³r

This requires:

∫_V K(r) B(r) d³r = 1  (normalization condition)

Therefore: [⊙⇄Φ] states live on a constraint manifold in W.
```

## Type Signatures

```
/*
  CORE TYPES
*/

W         : Type                  // paired state space
⊙         : Component of W        // whole configuration
Φ         : Component of W        // field configuration
[⊙⇄Φ]    : Constrained W         // coupled states only

i○^∞      : Aperture config       // boundary aperture structure
•^∞       : Power structure       // emerged power lines
i•        : Center aperture       // center transformation point

/*
  OPERATOR SIGNATURES
*/

⊛_boundary : W → (W, i○^∞)
☀︎_power    : (W, i○^∞) → (W, •^∞)
⊛_center   : (W, •^∞) → (W, i•)
☀︎_final    : (W, i•) → W

E          : W → W                // composite energy operator
```

## Conservation Laws

```
/*
  WHOLE-FIELD ENERGY CONSERVATION
*/

For any energy flow E : W → W,

Energy(W) = Energy(E(W))

Where:

Energy(W) = Energy(⊙) + Energy(Φ)
          = ∫_⊙ ε_whole + ∫_V ε_field(Φ) d³r

The coupling ensures energy redistributes between ⊙ and Φ
but total remains constant:

dE_total/dt = 0

But individual components can exchange:

dE_⊙/dt = -dE_Φ/dt
```

## The Master Equation (Differential Form)

```
/*
  CONTINUOUS EVOLUTION
*/

d/dt [⊙⇄Φ] = E([⊙⇄Φ])

Expanded (using functional derivatives):

d⊙/dt = F'(Φ) · dΦ/dt
dΦ/dt = G'(⊙) · d⊙/dt

This is a coupled system of PDEs that describes how
the whole-field pair evolves continuously.

/*
  DISCRETE PULSE FORM
*/

[⊙⇄Φ]_next = E([⊙⇄Φ]_current)

For discrete energy inputs (photons, events, etc.)
```

## Example: Photon Absorption

```
/*
  INITIAL STATE
*/

W₀ = [⊙₀⇄Φ₀]  where Φ₀ = background field

/*
  PHOTON ENTERS AT FIELD
*/

Φ₀ → Φ₀ + δΦ_photon  (field perturbation)

/*
  FLOW THROUGH SYSTEM
*/

W₀ ⊛ i○^∞    // photon hits retinal boundary apertures
   ☀︎ •^∞     // generates neural power lines (action potentials)
   ⊛ i•      // converges to conscious center
   ☀︎ W₁      // emerges as updated state

W₁ = [⊙₁⇄Φ₁]  where:
  ⊙₁ = "I see red"       (updated whole - conscious state)
  Φ₁ = Φ₀ + neural_field (updated field - brain activity)

The coupling [⊙⇄Φ] ensures:
  - Seeing red (⊙₁) corresponds to specific neural activity (Φ₁)
  - Neural activity (Φ₁) manifests as seeing red (⊙₁)
```

## Summary: The Complete Mathematical Structure

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  STATE SPACE:        W = ⊙_space × Φ_space                    ║
║                                                                ║
║  COUPLING:           [⊙⇄Φ] = {(⊙,Φ) : ⊙=F(Φ), Φ=G(⊙)}       ║
║                                                                ║
║  ENERGY OPERATOR:    E : W → W                                ║
║                                                                ║
║  DECOMPOSITION:      E = ☀︎ ∘ i• ∘ ⊛ ∘ ☀︎ ∘ i○^∞ ∘ ⊛           ║
║                                                                ║
║  FLOW:               [⊙⇄Φ] ⊛ i○^∞ ☀︎ •^∞ ⊛ i• ☀︎ [⊙'⇄Φ']      ║
║                                                                ║
║  CONSERVATION:       Energy(W) = Energy(E(W))                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```
