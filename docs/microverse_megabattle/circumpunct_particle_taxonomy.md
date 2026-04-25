# Circumpunct Particle Taxonomy
Created: 2026-04-24
Last updated: 2026-04-24
Version: 0.1

Single source of truth for what a ⊙ particle can be and how two or more ⊙s can interact, in MMB. Drives the engine; everything else is implementation. Organized by dimensional ladder rung (properties), then by interaction class.

The framework's claim: every ⊙ is the 1 self-limited at a specific configuration. The "configuration" is a value at each rung of the ladder. So properties belong at rungs, not in a flat list. Interactions are between values at the same rung (peer interactions: two •s, two Φs) or across rungs (cross-rung: a • probing a Φ, a ○ filtering a — passing through).

## Properties (organized by ladder rung)

### ∞ (substrate)

- **E_share**: the particle's share of the conserved 1. Always normalized to 1 in framework terms (it IS the 1 at its scale, A3); in MMB we use it as a scalar bookkeeping value (mass-energy budget).

### • (0D, aperture)

- **A** (mass number): nucleon count; cardinality of the inner ⊙ population
- **Z_eff** (effective nuclear charge): aperture coupling strength, drives EN
- **|•|** (aperture strength): scalar, derives from Z_eff and A; the framework's α at electron scale
- **spin**: intrinsic angular momentum at the aperture (1/2, 1, 3/2, …)
- **i_phase** (worldline phase): current position in the i-cycle (0, π/2, π, 3π/2)
- **position**: aperture's location in space (the ⊙'s center)
- **velocity**: aperture's drift through space (the line — that the • is currently tracing)

### ⊛ (0.5D, convergence)

- **convergence_rate**: how strongly this aperture pulls inward; gravitational tendency at this scale
- **convergence_affinity**: dictionary mapping other element types → relative attraction (some ⊙s pull harder on specific others; e.g., H is loose, O+H attracts strongly)
- **trigger_threshold**: how hard a stimulus has to be before convergence engages

### — (1D, line/extension)

- **frequency f₀·2^(d/T)**: natural ringing of the worldline (220Hz × octave step)
- **velocity** (lateral): drift speed; how fast — extends through 3-space (already covered above as •-velocity since they're paired in MMB; could split if needed)
- **lifetime / half-life**: how long this line persists before decay (∞ for stable nuclei; finite for unstable)
- **decay_mode**: alpha (eject He-4), beta (n → p + e), gamma (emit photon, no transmutation), spontaneous fission
- **commitment_strength**: how irreversibly the line holds its current trace (high for stable nuclei, low for unstable)

### ⎇ (1.5D, branching)

- **valence**: number of branches (bond slots) the line can split into
- **branching_geometry** (hyb): sp / sp² / sp³ / sp³d / sp³d² → angle target via arccos(−1/T)-family
- **branch_irreversibility**: once split, how hard to re-merge

### Φ (2D, field/mind)

- **station** (dimensional position): 1.0D / 1.5D / 2.0D / 2.5D / 3.0D (derives from hyb)
- **field_range**: distance over which this ⊙ mediates with others
- **field_type**: covalent / ionic / metallic / hydrogen-bond / van-der-Waals (different transmission modes)
- **polarity (ΔEN-driven)**: asymmetry of mediation; high polarity = directional field
- **lone_pairs LP**: non-bonding allocations of Φ; reduce sigma availability
- **catalytic_affinity**: which other ⊙s this one accelerates reactions in (without being consumed)
- **inhibitory_affinity**: which other ⊙s this one slows reactions in (noble-gas effect)
- **electronegativity EN** = Z_eff^(R/A(2))/n: how greedy this ⊙ is for shared electrons

### ✹ (2.5D, emergence)

- **emission_spectrum**: which colors/frequencies this ⊙ radiates when triggered
- **emission_threshold**: energy required before emission fires
- **emission_directionality**: isotropic / dipole / focused beam
- **photon_color**: tied to the bond/event that triggered emission

### ○ (3D, boundary/body)

- **boundary_radius**: physical size of the rendered sphere
- **boundary_stiffness**: how much it deforms under pressure
- **filter_passband**: which energies/atoms can cross it (sticky for halogens, transparent for noble gases)
- **boundary_geometry**: spherical / oblate / prolate (most ⊙s spherical at this scale)
- **charge_state**: ionization (neutral / +1 / -1 / etc.); changes filter behavior
- **phase_state**: gas / liquid / solid (depends on local kinetic energy and bond density)
- **damage_accumulator**: cumulative strain on the boundary; high damage = fragmentation risk

### ⟳ (3.5D, recursion)

- **reproduction_rate**: how often this ⊙'s closed boundary opens to spawn a new aperture (for cells, this is the cell-cycle rate; for nuclei, the radioactive decay rate)
- **fission_threshold**: energy at which the ⊙ splits into smaller ⊙s
- **daughter_products**: what it becomes when it decays / fissions / reproduces
- **legacy_mode**: whether the ⊙ "remembers" its parent (for tracking lineages)

### ⊙ (the whole)

- **class**: terminal (valence 1) / bridge (2) / hub (4) / super-hub (6)
- **family**: alkali / alkaline-earth / metalloid / nonmetal / halogen / noble (groups in periodic table)
- **stability**: magic-number? near-magic? fissile? metastable?
- **palette**: visual signature (hue/saturation/lightness derived from station + family)
- **audio_signature**: timbre (sine, triangle, sawtooth, square; element-family-coded)
- **name**: H, He, C, etc.

## Interactions

### Bonding (peer-rung at Φ)

- **Covalent bond**: shared electron pairs between two ⊙s; valence-driven; bond order can climb 1→2→3 (single→double→triple) following pi-ratio (R/T², V/P(P+1)) and D5 closure boost (T/Φ for triples with LP)
- **Ionic bond**: electron transfer (Δq=±1); ΔEN > threshold; lower energy than covalent; produces charged ⊙s with strong polarity
- **Hydrogen bond**: weak (~1/10 covalent strength) bond between H attached to electronegative atom and another electronegative atom; doesn't consume valence; geometric (linear-ish)
- **Metallic bond**: many-to-many electron sharing in a lattice; specific to certain elements (alkali/transition metals)
- **Van der Waals**: ultra-weak distance-only attraction; everywhere; mostly cosmetic

### Fusion (cross-scale at •)

- **Two-body fusion**: A_a + A_b → A_new; only stable A_new survive (FUSION_TABLE_BY_A); momentum conserved; energy threshold (Coulomb barrier proxy)
- **Three-body fusion**: He + He + He → C (triple-alpha); requires three-body proximity in time window; bypasses A=8 forbidden state
- **Catalyzed fusion**: when a third ⊙ is present (e.g., a catalyst element), fusion threshold drops for the other two

### Fission (cross-scale at •)

- **Spontaneous fission**: heavy unstable nucleus splits without external trigger; rate set by half-life
- **Induced fission**: collision/heat above threshold splits the nucleus; ejects daughter products + free atoms (analog: neutron-induced fission of U-235)
- **Alpha decay**: ⊙ ejects an He-4 sub-⊙ (a piece of its nucleon cloud); A→A−4, Z→Z−2
- **Beta decay**: a nucleon transmutes; A unchanged, Z±1; ⊙ becomes a different element

### Catalysis (cross-element at Φ)

- **Acceleration catalyst**: in proximity, certain ⊙ types lower the energy threshold for specific reactions in their neighbors
- **Inhibitor**: opposite; raises threshold; noble gases inhibit nearly everything
- **Templating**: a ⊙ recruits specific other ⊙s into a specific spatial arrangement (DNA → RNA → protein at chemical scale; crystal seeding at silicate scale)

### Absorption (cross-scale at ○ → •)

- **Phagocytosis**: large ⊙ engulfs small ⊙; small ⊙'s nucleons join large's nucleon cloud; identity of large preserved (different from fusion: phagocytosis is asymmetric, fusion is symmetric)
- **Photon absorption**: ⊙ absorbs an emitted ray, raising its excitation level
- **Atom capture**: one ⊙ binds a free smaller ⊙ as a part of its boundary structure (like a moon)

### Emission (peer at ✹)

- **Bond-event emission**: forming or breaking a bond emits a ray (color = blend of the two ⊙s' palettes)
- **Decay emission**: an unstable ⊙ emits a photon as it transitions to a lower-energy state
- **Radiation emission**: ⊙ at high excitation emits continuously
- **Stimulated emission**: incoming photon at matching frequency triggers the ⊙ to emit a coherent twin (laser principle)

### Repulsion (peer at ○)

- **Hard-core repulsion**: two ⊙s can't occupy the same space; boundary-against-boundary force
- **Coulomb repulsion**: like charges repel (positive ions repel each other)
- **Phase repulsion**: two solid ⊙s at low energy don't merge

### Resonance (peer at —)

- **Frequency-matched coupling**: two ⊙s with matching natural frequency exchange energy without contact (the framework's "transparent Φ"); audible as standing waves
- **Phase-locked coupling**: bonded ⊙s lock their i-phases over time; their amplitudes correlate
- **Parametric resonance**: a third ⊙ at the difference frequency can transfer energy between the two

### Transformation (cross-rung)

- **Excitation**: ⊙ absorbs energy, jumps to higher state (changes color, emission threshold lowers)
- **Relaxation**: excited ⊙ drops back to ground state, emits the difference as a photon
- **Phase transition**: ⊙ shifts gas → liquid → solid (or reverse) based on local KE; visual signature changes
- **Ionization**: ⊙ gains/loses electrons; charge state shifts; behavior changes
- **Isomerization**: ⊙ keeps same composition but rearranges its internal structure

### Tunneling (cross-rung at ○)

- **Quantum tunneling**: ⊙ passes through a boundary it shouldn't classically cross; rare, probability-based; relevant to fusion at low energy
- **Membrane diffusion**: ⊙ passes through a multi-⊙ boundary if its filter-pass matches

### Multi-body / Emergent (composite ⊙ at scale Λ)

- **Ring formation**: 3+ ⊙s in proximity snap into a closed cycle (benzene ring at C=6; ribose at C=5; cyclopentane; etc.)
- **Chain formation**: ⊙s of compatible valence string into linear chains (alkanes, polymers)
- **Lattice formation**: ⊙s of high valence with slow dynamics crystallize into 3D lattices (Si crystal, ice)
- **Cage formation**: ⊙s form hollow polyhedra (fullerene C60, viral capsids)
- **Membrane formation**: amphipathic ⊙s self-organize into bilayers (lipid membranes)
- **Aggregate ⊙ recognition**: when N ⊙s are bonded, they ARE a new ⊙ at scale Λ with its own boundary, frequency, and behavior (A3 made literal)

### Decay chains (cascading ⟳)

- **Sequential decay**: unstable ⊙ decays to another unstable ⊙ which decays again, until a stable end-state is reached (e.g., U-238 → ... → Pb-206)
- **Branching decay**: ⊙ has multiple possible decay modes with branching ratios

## How this maps to engine architecture

Each property is a field on the particle struct. Most are derivable from a small input vector (A, Z_eff, valence, hyb, LP) → all the rest. We already do this for some; we should extend to all.

Each interaction is a function (or a rule in a registry) that takes ⊙s as inputs, checks conditions, applies effects. Currently MMB has: covalent bonding (with bond order, ionic boost, LP suppression), fusion (two-body, momentum-conserved, stability-table-gated), photon emission (bond events). Missing: most everything else listed above.

Implementation priority (subjective; ordered by impact-per-effort):

1. **Three-body fusion** (triple-alpha) — fixes the He+He=Be-8-bounce bottleneck so carbon actually appears
2. **Aggregate ⊙ recognition** — makes molecules visually exist as wholes (A3 finally visible)
3. **Phase state** (gas/liquid/solid) — adds visible thermodynamics
4. **Catalysis & inhibition** — gives elements personalities (Mn, M, etc. become catalysts)
5. **Decay & half-life** — unstable elements actually transmute over time (heavy isotopes, beta decay)
6. **Templating / ring formation** — emergent organic chemistry
7. **Photon absorption / excitation states** — energy moves through the soup as photons, not just kinetic
8. **Phagocytosis** — sets up the cellular scale for v3.0

## Open questions

- Should "phase state" be a property of each ⊙ (each ⊙ is independently gas/liquid/solid based on its own KE) or of regions (the soup has temperature gradients)?
- Should decay use real half-lives (microseconds to billions of years) or game-time half-lives (seconds to minutes)?
- Should catalysis be hardcoded per element or driven by a κ-matrix lookup (the framework's cross-station coupling)?
- Should emission/absorption photons be tracked as discrete particles (with their own Vec3 trajectory) or as instant ray events?
- Should aggregate ⊙s have their own audio signature (a chord) or inherit from the constituent atoms?
- How much of this lands in v2.x vs needs a v3.0 architectural pass?

## Revision history
- 2026-04-24 v0.1: initial inventory; properties by ladder rung, interactions by class
