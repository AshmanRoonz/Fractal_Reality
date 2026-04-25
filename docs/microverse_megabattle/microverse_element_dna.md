# Microverse Element DNA + Interaction Library
Created: 2026-04-25
Last updated: 2026-04-25
Version: 0.1

Minecraft-style design document for Microverse Megabattle's element library. Each element is a designed block-type with an explicit DNA (its • + — + Φ + ○ configuration) and specific behaviors. Interactions are pair-specific where chemistry calls for it, generic otherwise.

This document defines the world before the world is built. Implementation follows from this design, not the other way around.

## Design principles

**Each element is a designed identity, not a derivation.** We do not say "carbon = (Z_eff=4, valence=4, hyb=sp³)" and let formulas compute everything else. We say "carbon is the SKELETON. It chains. It rings. It forms tetrahedra. It binds tightly. Its color is teal because that's what carbon should look like." The framework-native inputs are present (every element does have its A, Z_eff, valence, hyb, LP) but they support the identity rather than substituting for it.

**Each element has a role.** Roles include: terminal (caps a chain), bridge (connects two), hub (centers a tetrahedron or octahedron), backbone (forms long chains/rings), catalyst (accelerates without being consumed), oxidizer (breaks bonds in others), inert (doesn't bond), energy-carrier (stores/releases on demand), template (biases neighbor configuration). An element may have a primary role plus secondary roles.

**Pair-specific interactions where chemistry has them; generic where it doesn't.** Real chemistry has specific reactions: H + O → water; Na + Cl → salt; C + 4H → methane. We name these. Where chemistry is generic (any two compatible-valence atoms can bond), the existing generic mechanism applies.

**State emerges from element + condition.** Matter states (solid / liquid / gas / plasma) aren't separate categories; they emerge from each element's bond-stiffness and the local heat/pressure. Carbon is solid below burning temperature; nitrogen is gas at room temp; mercury is liquid. Per-element stiffness/break thresholds determine the state band.

**Visuals signal DNA.** Each element renders distinctly enough that a player can identify it at a glance. Color is the first signal, but shape/animation/internal pattern reinforces. C looks like a teal sphere with a faint tetrahedral outline; N looks like a violet sphere with internal explosive shimmer; etc.

## DNA schema

Each element entry contains:

```
{
  symbol:       "C",                         // periodic table abbrev
  name:         "Carbon",                    // human-readable
  role:         "skeleton-hub",              // primary identity
  secondary:    ["templater", "ringer"],     // additional roles

  // Framework inputs (these stay; they support the identity)
  A:            12,                          // mass number = nucleon count
  Z_eff:        4,                           // effective nuclear charge
  valence:      4,                           // bond slot count
  hyb:          "sp3",                       // 1.0/1.5/2.0/2.5/3.0 station
  LP:           0,                           // lone pairs

  // Visual signature
  palette:      { base: 0x3aa8b5, emissive: 0x7fe8f6 },
  shape:        "tetrahedral-spike",         // surface pattern hint
  internalAnim: "lattice-pulse",             // interior motion style

  // Behavior
  behavior:     "binds-tightly",             // generic disposition
  preferredBondStiffness: 250,               // overrides default for this element's bonds
  preferredBreakStretch:  6.0,               // very persistent

  // Phase bands (heat ranges where each state happens)
  states: {
    solid:  { minHeat: 0,   maxHeat: 60  },
    liquid: { minHeat: 60,  maxHeat: 95  },
    gas:    { minHeat: 95,  maxHeat: 100 }
  },

  // Pair-specific interactions
  interactions: {
    "C":  { reaction: "chain-or-ring",  prob: 0.85 },
    "H":  { reaction: "saturate",       prob: 0.95 },
    "O":  { reaction: "form-CO2",       prob: 0.50 },
    "N":  { reaction: "form-CN-bond",   prob: 0.40 }
  }
}
```

The `interactions` table is sparse — only pair-specific behaviors are listed. Pairs not listed fall through to the generic bond-or-no-bond rule based on valence.

## Element library

### Terminals (valence 1)

```
H — Hydrogen
  role:    "terminal-light"
  A: 1, Zeff: 1, valence: 1, hyb: "sp", LP: 0
  palette: pale white-blue
  shape:   tiny smooth sphere
  behavior: "loose, ubiquitous, swappable"
  interactions:
    H  → "fuse-to-He"  (under high energy)
    O  → "saturate-as-water"
    N  → "saturate-as-ammonia"
    C  → "saturate-organic"
    F  → "form-HF"      (acidic)
    Cl → "form-HCl"     (acidic)

He — Helium (noble)
  role:    "noble-light"
  A: 4, Zeff: 2, valence: 0, hyb: "sp", LP: 0
  palette: pale blue
  shape:   smooth sphere, very dim
  behavior: "inert, drifts"
  interactions: NONE (does not bond)

Li — Lithium
  role:    "alkali-light"
  A: 7, Zeff: 1, valence: 1, hyb: "sp", LP: 0
  palette: silver-white
  shape:   small sphere, slight metallic sheen
  behavior: "reactive, gives up its electron readily"
  interactions:
    H  → "form-LiH"
    O  → "form-Li2O"
    F  → "form-LiF"   (intense)
    Cl → "form-LiCl"

F — Fluorine
  role:    "halogen-cutter"
  A: 19, Zeff: 9, valence: 1, hyb: "sp", LP: 3
  palette: pale yellow-green
  shape:   sharp small sphere with spiky shimmer
  behavior: "aggressive, breaks other bonds, wants electrons"
  interactions:
    EVERYTHING → "abstract-electron-from"  (cleaves nearby bonds)
    H  → "form-HF"
    Li → "form-LiF"
    Na → "form-NaF"

Cl — Chlorine
  role:    "halogen-cutter-medium"
  A: 35, Zeff: 11, valence: 1, hyb: "sp", LP: 3
  palette: yellow-green
  shape:   sharp small sphere
  behavior: "less aggressive than F, still corrosive"
  interactions:
    H  → "form-HCl"
    Na → "form-NaCl"   (salt crystal)
    K  → "form-KCl"
```

### Light bridges (valence 2)

```
Be — Beryllium
  role:    "structural-bridge-light"
  A: 9, Zeff: 3, valence: 2, hyb: "sp3", LP: 0
  palette: pale grey-blue
  shape:   small sphere with two visible bond facets
  behavior: "rigid, structural, predictable"
  interactions:
    O  → "form-BeO"
    F  → "form-BeF2"

O — Oxygen
  role:    "bridge-polar"
  A: 16, Zeff: 8, valence: 2, hyb: "sp3", LP: 2
  palette: red-orange
  shape:   sphere with two distinct bond facets at 104.5°
  behavior: "polar, water-forming, oxidizing"
  interactions:
    H  → "form-water"  (specific 104.5° angle, locks)
    H  → if 2H present → snap to H2O molecule
    C  → "oxidize-form-CO-or-CO2"
    O  → "form-O2"     (paramagnetic, reactive)
    N  → "form-NO-or-NO2"
    Si → "form-silica"

Mg — Magnesium
  role:    "alkaline-earth-bridge"
  A: 24, Zeff: 6, valence: 2, hyb: "sp2", LP: 1
  palette: amber-bronze
  shape:   sphere with three trigonal facets
  behavior: "moderately reactive, structural in plant cells"
  interactions:
    O  → "form-MgO"
    Cl → "form-MgCl2"

Na — Sodium
  role:    "alkali-bridge"  (technically valence 1 but plays as a bridge)
  A: 23, Zeff: 4, valence: 1, hyb: "sp", LP: 0
  palette: silver-white-pale
  shape:   small sphere with metallic shimmer
  behavior: "reactive, salt-forming"
  interactions:
    Cl → "form-NaCl"   (ionic crystal, table salt)
    F  → "form-NaF"
    O  → "form-Na2O"
```

### Tri-connects (valence 3)

```
B — Boron
  role:    "tri-bridge"
  A: 11, Zeff: 3, valence: 3, hyb: "sp2", LP: 0
  palette: yellow-amber
  shape:   sphere with three planar facets at 120°
  behavior: "trigonal, planar templates"
  interactions:
    H  → "form-BH3"
    O  → "form-B2O3"

Al — Aluminum
  role:    "structural-tri"
  A: 27, Zeff: 5, valence: 3, hyb: "sp2", LP: 0
  palette: light silver
  shape:   sphere with three angled facets
  behavior: "lightweight structural, oxide-passivated"
  interactions:
    O  → "form-Al2O3" (corundum lattice)
    Cl → "form-AlCl3"

N — Nitrogen (3-valence form)
  role:    "tri-pyramidal-hub"
  A: 14, Zeff: 5, valence: 3, hyb: "sp3", LP: 1
  palette: violet
  shape:   pyramidal sphere with 3 facets at 107°
  behavior: "energy-storing, can become explosive"
  interactions:
    H  → "form-NH3"
    H  → if 3H present → snap to ammonia
    N  → "form-N2-triple-bond"  (very stable, very energetic if broken)
    O  → "form-NOx"
```

### Tetrahedral hubs (valence 4)

```
C — Carbon
  role:    "skeleton-hub"
  secondary: ["templater", "ringer", "chainer"]
  A: 12, Zeff: 4, valence: 4, hyb: "sp3", LP: 0
  palette: teal cyan
  shape:   tetrahedral spike pattern on surface
  behavior: "binds-tightly, the basis of organic chemistry"
  interactions:
    C  → "chain-or-ring"   (templates ring at 6 atoms)
    H  → "saturate"
    O  → "form-CO2-or-CO"
    N  → "form-CN"
    Cl → "form-organic-chloride"
    F  → "form-organic-fluoride"

Si — Silicon
  role:    "crystal-skeleton"
  secondary: ["lattice-templater"]
  A: 28, Zeff: 6, valence: 4, hyb: "sp3", LP: 0
  palette: cool blue-grey
  shape:   crystalline cubic facet pattern
  behavior: "rigid, periodic, lattice-forming"
  interactions:
    Si → "lattice-grow" (cubic crystal templating)
    O  → "form-silica" (rigid 3D network)
    H  → "form-SiH4"
```

### High-valence (5-6)

```
P — Phosphorus
  role:    "energy-carrier"
  A: 31, Zeff: 7, valence: 5, hyb: "sp3d", LP: 0
  palette: orange-red glow
  shape:   sphere with internal pulsing energy core
  behavior: "stores energy in P-O bonds, releases on demand (ATP analog)"
  interactions:
    O  → "form-phosphate-PO4"  (3-D structure, energy-storage)
    H  → "form-PH3"
    P  → "form-P-P-P chain"

S — Sulfur
  role:    "polymer-cross-linker"
  A: 32, Zeff: 8, valence: 5, hyb: "sp3d", LP: 1
  palette: yellow
  shape:   sphere with sticky-looking surface pattern
  behavior: "chains and crosslinks, sticky"
  interactions:
    S  → "form-S-S-chain"  (polymer)
    H  → "form-H2S"        (smelly)
    O  → "form-SO2-or-SO3"

N — Nitrogen (6-valence super-hub form, framework-extension)
  role:    "octahedral-super-hub-explosive"
  A: 14, Zeff: 10, valence: 6, hyb: "sp3d2", LP: 0
  palette: deep violet
  shape:   octahedral facet pattern
  behavior: "very high energy, explosive"
  interactions:
    SAME AS N (3-valence) but with octahedral bonding capacity
```

### Noble gases (valence 0)

```
Ne — Neon
  role:    "noble-light"
  A: 20, Zeff: 10, valence: 0, hyb: "sp", LP: 4
  palette: pale orange-pink
  shape:   smooth dim sphere
  behavior: "inert, glows under high energy"

Ar — Argon
  role:    "noble-medium"
  A: 40 (extension), Zeff: 12, valence: 0, hyb: "sp", LP: 4
  palette: pale cyan
  shape:   smooth dim sphere
  behavior: "inert, common"
```

### Catalysts and exotics (framework-native, not strict periodic table)

```
M — Mediator
  role:    "catalyst"
  A: 24, Zeff: 6, valence: 2, hyb: "sp2", LP: 1
  palette: amber-warm
  shape:   sphere with rotating ring around equator
  behavior: "accelerates reactions in nearby atoms; not consumed"
  interactions:
    PROXIMITY-BASED: any pair within 30 units gets +50% reaction probability
    if M is also within 50 units of both

Λ — Lambda (template seed)
  role:    "template"
  A: 1 (placeholder), Zeff: 1, valence: 1, hyb: "sp", LP: 0
  palette: bright white-gold
  shape:   small star-like point
  behavior: "biases nearby atoms to copy the structure of recent bonds"
  (advanced; for v4.2+)
```

## Interaction registry

Generic rule (default): two atoms in proximity, valences allowing, may form a bond. Probability follows the existing station-compatibility + ionic-resonance + LP-suppression formulas.

**Pair-specific overrides** (hand-designed, take precedence over generic):

```
("H", "H")     → fusion attempt (high energy, low probability)
("H", "O")     → bond at 104.5°; if 2H exist near O, snap to water molecule
("H", "N")     → bond at 107°; if 3H exist near N, snap to ammonia
("H", "C")     → simple saturation bond
("H", "F")     → form HF, very stable
("H", "Cl")    → form HCl, stable
("C", "C")     → chain bias; 6 atoms in proximity → snap to benzene ring
("C", "O")     → bond; if 2 O near 1 C → snap to CO2 (linear)
("C", "N")     → form CN bond, can extend to nitrile
("C", "H4")    → if 4 H near 1 C → snap to methane (sp³)
("Si", "Si")   → crystal lattice templating; biases cubic angles
("Si", "O")    → silica (3D rigid network)
("Na", "Cl")   → ionic crystal (NaCl) — strong, low-energy bond
("Na", "F")    → ionic crystal (NaF) — even stronger
("Li", "F")    → ionic crystal (LiF) — strongest
("F", any)     → bond-cleaving aggressor: F atoms break nearby C-H, C-C, etc.
("Cl", any)    → similar to F but milder
("N", "N")     → triple bond on close approach (N2); breaking N2 releases huge energy
("N", "N", "N") → if 3 N close → metastable; on impact → explosion (N→2N + heat burst)
("O", "O")     → form O2 (paramagnetic, reactive)
("P", "O")     → phosphate cluster (energy-storage)
("S", "S")     → polymer chain
```

**Three-body specials** (when 3 atoms cluster):

```
("He", "He", "He") → triple-alpha → C  (high energy)
("H", "H", "O")    → snap to water (H2O)
("H", "H", "H", "N") → snap to ammonia (NH3)
("H", "H", "H", "H", "C") → snap to methane (CH4)
("C", "C", "C", "C", "C", "C") → snap to benzene ring
```

**Catalyst proximity** (when M is within 50 units of a reacting pair):

```
ALL reaction probabilities × 1.5
```

## State system

States are not visual variation; they are tools and weapons. Each state has explicit game purpose:

### Solid (the structural state)
Atoms in rigid lattice. Stiff bonds, very high break threshold. Doesn't deform much. **Role: ARMOR.** Blocks projectiles, absorbs damage by losing constituent bonds rather than transmitting force. Slowest to move. The HULL of every ship is solids. Carbon and silicon armor; ionic crystals (NaCl, LiF) make medium armor.

### Liquid (the flowing state)
Atoms bonded but flexibly; bonds form/break easily. Flows under forces, displaces other matter. **Role: FLOW + COOLANT.** Liquid water around hot weapon ports prevents ignition; liquid coolants regulate heat. Projectiles travel slower through liquid. Liquid pools can be displaced into shapes.

### Gas (the volatile state)
Atoms dispersed, no bonds, high kinetic motion. **Role: WEAPON / VOLATILE.** Combustible gases (H, CH4, NH3) ignite when local heat crosses threshold AND an oxidizer (O) is nearby; ignition releases huge heat burst that propagates → chain reaction. Tactical: ship leaks H gas → enemy ignites → BOOM. Hydrogen-rich ships are powerful but explosive.

### Plasma (the energetic state)
Atoms ionized, very high energy. **Role: HIGH-ENERGY WEAPON / PROCESS.** Plasma beams cut through armor (delivers heat that breaks bonds); conductive; short-lived (decays to gas/liquid as heat dissipates). Player weapons; high-energy reactions; fusion attempts.

### Combustion mechanic (the headline interaction)

```
Trigger: an atom in GAS state, with combustible flag (H, CH4, NH3),
         within proximity (~30 units) of an OXIDIZER (O atom in any state),
         experiences local heat > IGNITION_THRESHOLD.

Effect:  burst of heat at the gas atom's position; gas + oxidizer
         transformed to PRODUCTS (water for H+O, CO2 for CH4+O, etc).
         Heat burst propagates → ignites neighboring combustible gas →
         chain reaction. Each combustion event emits light + audio +
         kinetic burst.

Visual:  bright orange flash, expanding heat wave, flame trail.

Cooldown: combusted atoms (now products) drop their combustible flag;
          a region needs to re-fill with fuel before re-ignition.
```

Tactical implications:
- A ship with H gas tanks can be ignited by enemy fire if pierced
- Cooling systems matter (liquid water around H tanks prevents ignition)
- Fire suppressants: noble gases displace oxidizers, prevent combustion
- Plasma weapons fired through gas clouds chain-ignite them
- Defensive: dump O2 to oxidize enemy weapons; dump N2 to smother fires
- Offensive: light an H pocket near an enemy ship to chain-detonate

### Heat propagation

HEAT exists at two scales:
- **Global HEAT** (existing slider): ambient temperature of the soup, sets baseline kinetic noise
- **Local heat field**: per-region heat that builds at collision/combustion sites and decays exponentially. Implemented as a spatial grid or per-atom local-heat counter.

An atom's effective state is determined by `localHeat + globalHEAT` checked against its element's heat bands.

### Per-element state bands (heat ranges)

```
H:   liquid 0-1, gas 1+, plasma 100+   (almost always gas at room)
He:  liquid 0-0.5, gas 0.5+            (always gas)
Li:  solid 0-50, liquid 50-95, gas 95+
F:   liquid 0-1, gas 1+                (always gas, very reactive)
Cl:  liquid 0-20, gas 20+
Be:  solid 0-90, liquid 90-95, gas 95+
O:   liquid 5-30, gas 30+              (gas at room)
Mg:  solid 0-65, liquid 65-90, gas 90+
Na:  solid 0-25, liquid 25-50, gas 50+
B:   solid 0-90, liquid 90-95, gas 95+
Al:  solid 0-65, liquid 65-90, gas 90+
N:   liquid 0-5, gas 5+                (gas at room)
C:   solid 0-90, liquid 90-95, gas 95+ (very stable solid)
Si:  solid 0-80, liquid 80-95, gas 95+
P:   solid 0-30, liquid 30-50, gas 50+
S:   solid 0-30, liquid 30-50, gas 50+
Ne:  gas at all heats, plasma 100+
Ar:  gas at all heats, plasma 100+
```

A molecule's state is gated by its LOWEST-state constituent: a methane molecule (CH4) is gas-state because H is gas at room temp; once heated past 95, the C also goes gas, the molecule fully dissociates.

### Visual signatures per state

```
Solid:  full opacity (1.0), bright emissive, sharp surface pattern,
        slow rendering motion (atoms barely jitter)
Liquid: ~70% opacity, softer emissive, surface ripple animation,
        moderate flow motion
Gas:    ~30% opacity, dim emissive, fast wobble + drift,
        slight afterimage/motion blur
Plasma: 100%+ emissive (overdriven), lightning-arc flicker pattern,
        very fast motion, electric blue/white edge tint
```

You can identify state at a glance.

### Combustible flags (per element)

```
combustible: H, CH4 (assembled), NH3 (assembled), S
oxidizer:    O, F (extreme), Cl (mild), N (in some configs)
inert:       He, Ne, Ar (smother fires)
```

Combustion only fires when a combustible meets an oxidizer in gas state with sufficient heat. The product elements (water, CO2, etc.) are NOT combustible (they've already burned).

## Visual signatures per element

Each element renders distinctly:

```
H, He, Ne: small smooth dim spheres (terminal/noble character)
Li, Na, K: small spheres with metallic shimmer
F, Cl: small spheres with sharp/spiky surface pattern
Be, Mg, Al: medium spheres with planar facets
B: medium sphere with three trigonal markings
C: medium sphere with tetrahedral spike pattern
Si: medium sphere with crystalline cubic facets
N: medium sphere with violet pulsing core (energy-storing)
O: medium sphere with two distinct bond facets at 104.5°
P: medium sphere with internal energy pulse (orange glow)
S: medium sphere with sticky/wavy surface
M: medium sphere with rotating ring around equator
```

Implementation: extend the v2.6 ShaderMaterial to dispatch on element identifier, choosing a per-element shader path. The `hyb` station already gives us coarse pattern selection; we add per-element refinements.

## Game implications

What players can build:

```
Water (H2O): the medium of cellular life; cells made of H+O+C have water-rich shells
Methane (CH4): a fuel; small ships made primarily of CH4 are fast but fragile
Ammonia (NH3): an alternative solvent; ships made of NH3 are tougher than water-ships
Benzene rings (C6H6): rigid aromatic; structural component
ATP-like (ADP, ATP): P-O-P-O chains; energy-storage component
Silica (SiO2): glassy hard armor
Salt crystals (NaCl, LiF): ionic crystals; structural building blocks
Polymers (S chains): flexible, sticky; binding agents
```

Different ship classes from different compositions:

```
Carbon-class scout: lots of C + H; light, fast, fragile
Silicon-class diatom: lots of Si + O; heavy, armored, slow
Phosphorus-class burst: lots of P + O; energy-rich, can fire weapons
Nitrogen-class bomber: lots of N (volatile); damages enemies on death
Halogen-class cutter: F or Cl carriers; specialized weapons
```

## Implementation plan (when we build)

**v4.0:** Fork from v2_1.html. Add the DNA schema (extended ELEMENTS table with new fields). Add 5-10 pair-specific interactions to start (water, salt, methane, ammonia, benzene). Test that snap-to-molecule works for water and methane.

**v4.1:** Add the visual signatures (per-element shader paths). Atoms become identifiable at a glance.

**v4.2:** Add catalyst behavior (M element). Templating for Si crystal growth.

**v4.3:** Add LSS movement and player body composition tracking. Player can fly through and absorb atoms. HUD shows what they have.

**v4.4:** Game loop. Build a target structure to win. Or a simple combat loop.

## Open design questions

- How explicit should the snap-to-molecule mechanic be? When 2H + 1O cluster, do we INSTANTLY snap to water (rigid molecule that moves as one), or do we just lock the bond angles and let the result feel like water without a special snap-state?
- Should noble gases ever bond? In real chemistry they almost never do; in MMB they'd be inert decoration.
- Should certain elements have spawn restrictions? E.g., is Na placed in the soup at the start, or only as a fusion product from H + Mg?
- Does the player ⊙ have its own DNA, or is it composed entirely of absorbed atoms?
- How do we handle "blocks of blocks" — i.e., once water is formed, does it become a single ⊙ with H2O DNA, or stay as 3 atoms with locked angles?

Resolving these before v4.0 will make implementation cleaner.

## Revision history

- 2026-04-25 v0.1: initial draft. Element library, interaction registry, state system, visual signatures, game implications.
