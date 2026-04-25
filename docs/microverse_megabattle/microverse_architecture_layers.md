# Microverse Architecture: Dimensional Layers + MUD Substrate
Created: 2026-04-25
Last updated: 2026-04-25
Version: 1.0

**Status: v5.0 spec, committed.** The substrate refactor begins in `v5.html`. v4.html remains the last build of the previous architecture (single-tier 3D mesh per atom).

Architectural design for v5.0+. Reorganizes the engine around the framework's dimensional ladder, treating the game state as MUD-style data at the cheap layers (0D + 1D) and rendering as pluggable projections at the higher layers (2D + 3D). Each entity processes at the lowest layer sufficient for what's happening to it right now; expensive higher-layer work runs only when needed.

This document supersedes parts of the T=3 architecture (`v3.0+ WorldEngine / PerceptionEngine / SubstrateEngine`) by being more granular and specific. The previous T=3 split was three coarse modules; this is four ladder-aligned layers.

## Core principle

**The game state is the truth; rendering is one projection of it.** What the world IS (entity positions, connections, properties, descriptions) belongs to the substrate. How the world is SEEN (3D mesh, 2D map, text description, audio map) is a separate layer that consumes the substrate and produces output for one observer.

This is the standard model-view separation, taken to the framework's depth: there isn't ONE rendering. There are MANY POSSIBLE rendering projections, each appropriate to a different observer or device. The substrate doesn't know which views exist; views subscribe to substrate state.

A MUD does this implicitly: it has only the substrate (text data) and one rendering (text output). What we're proposing is generalizing the same architecture: the substrate stays MUD-cheap; multiple renderings (text, 2D map, 3D scene, VR, sonar) can attach.

## Framework grounding

The framework's dimensional ladder gives us four natural processing layers:

- **0D (•)** — points: entity positions and orientations
- **1D (—)** — lines: connections, edges, target-locks, threads, bonds
- **2D (Φ)** — surfaces: planes, navigation meshes, screen projections, UI
- **3D (○)** — volumes: meshes, physics bodies, spatialized audio

Each higher layer is BUILT FROM the lower (A3 self-similar nesting):
- A 1D edge connects two 0D points
- A 2D face is bounded by 1D edges
- A 3D solid is bounded by 2D faces

So the engine can store data at the lowest sufficient layer and INFLATE up the layers only when a view needs the higher representation.

## The four engine layers

### Layer 0D — Soul / Position

Every entity has:
- 3D position (a Vector3)
- 3D orientation (an Euler or Quaternion)
- An element/type identifier
- A current state value (active / inert / etc.)

That's it. This is the absolute minimum to know the entity exists and where it is.

**Cost per entity per frame:** ~10 floats. Trivial. Can support tens of thousands of entities.

**Operations supported:**
- "Where am I"
- "What direction am I facing"
- "What kind of entity am I"
- Spatial queries (broad-phase, range queries via grid bins)

**Update rate:** every frame for active entities; every N frames for distant ones.

### Layer 1D — Connection / Line

Each entity has (in addition to 0D state):
- A list of CONNECTIONS to other entities (bonds, target-locks, threads, awareness)
- Each connection has: target entity ID, type (bond/target/thread), weight/strength, optional metadata

The connections form a sparse graph. Most entities have few connections (~3-12).

**Cost per entity per frame:** O(connections), typically ~50 floats. Cheap.

**Operations supported:**
- "Who am I bonded to"
- "Who am I aiming at"
- "Who is in my awareness range"
- Path traversal in the entity graph
- Network sync (lines between entities are first-class data)

**Update rate:** when connections change (form/break) + every N frames for force calculations.

### Layer 2D — Plane / Surface

For entities active in a 2D context (player on a map, UI, screen-space rendering):
- Their projected position on the relevant plane
- Their 2D bounding box (for screen-space culling, UI hit-testing)
- Their distance to current 2D camera (for LOD)

This layer is RENDERED FROM the 0D + 1D data. Entities don't store 2D state permanently; views compute it as needed.

**Cost per entity per visible frame:** ~20 floats + projection math. Moderate.

**Operations supported:**
- "Where on the screen does this entity appear"
- "Is this entity visible to the current 2D view"
- "How big is it on screen"
- 2D pathfinding
- HUD / minimap rendering

**Update rate:** per-frame for visible entities only.

### Layer 3D — Volume / Interaction

For entities active in 3D physics or 3D rendering:
- A 3D mesh / shader assignment
- A physics body (collision shape, mass, velocity, momentum)
- 3D collision response
- Per-vertex animation if needed

This is the EXPENSIVE layer. Most entities should NEVER need it. Only those in active 3D interaction (close to player, in physics range, on screen with full mesh detail).

**Cost per entity per frame:** ~kilobytes of state + physics integration + mesh draw calls. Expensive.

**Operations supported:**
- Full 3D physics (collision, force, integration)
- Mesh rendering with shaders
- Spatialized 3D audio
- Volumetric particle effects
- Direct 3D interaction (combat, manipulation)

**Update rate:** per-frame only for entities in active 3D context.

## Per-entity layer escalation

Each entity has an `activeLayer` value (0, 1, 2, 3). Engine logic determines this each frame:

```
activeLayer = max(
  needsView0D(entity),  // always true
  needsView1D(entity),  // if any other entity is connected to it OR has it in awareness range
  needsView2D(entity),  // if visible in any active 2D view
  needsView3D(entity)   // if in active 3D interaction range of any player
)
```

The entity is processed at its `activeLayer` for that frame. Higher-layer processing is skipped if not needed.

For MMB at 1000-atom soup with one player:
- The 980 atoms far from the player run only 0D (position update) + 1D (occasional bond check). ~5 microseconds per atom per frame.
- The 15 atoms near the player run 2D (visible in their HUD/2D map). ~50 microseconds.
- The 5 atoms in active interaction (touching player, fusing, etc.) run 3D physics. ~500 microseconds.

Total: ~5,000 + 750 + 2,500 = ~8 ms/frame. Plenty of headroom for 60fps.

Compare to running everything at 3D: ~500,000 microseconds = 500ms/frame. 2fps. Unplayable.

## The MUD substrate as a first-class artifact

The 0D + 1D data IS the game world. It can be:

- **Serialized to text**: each entity describable as "Carbon atom #1234 at (12, 5, -3), bonded to H#1235 and O#1236, at heat 18, gas state."
- **Saved/loaded**: just write the entity graph to disk; load anywhere.
- **Sync'd over network**: tiny payload (positions + connections + state).
- **Multi-mode shared**: one player runs the 3D view, another runs the text view, both see the same underlying world.

A standalone "world inspector" tool could read the MUD data and produce text descriptions, 2D maps, statistical analyses, network diagrams, all without re-running the simulation.

## Pluggable view system

Each VIEW is a module that:
- Subscribes to the MUD substrate
- Filters which entities it's interested in (frustum cull, range cull, type cull)
- For each selected entity, projects from MUD data to the view's representation
- Renders/outputs

Built-in views:

### Text view (MUD classic)
For each entity in the player's awareness range, generate a text description. Output to console / chat / overlay panel. "There is a Carbon atom 12 units northeast, bonded to a Hydrogen at heat 23."

### 2D map view (top-down)
Project all entities to a top-down 2D map. Render as colored dots with bond-lines. Useful for navigation, strategic overview, spectating. Cheap.

### 3D scene view (current MMB)
Three.js renderer. Per-entity mesh + material. Bond electrons, fusion events, lighting. Expensive but gorgeous. Only renders entities in 3D interaction range.

### Audio view
Spatialized stereo / surround based on entity positions and types. Element frequencies as v2.1 already had. Could include a "sonar" mode for blind play.

### VR view
Same 3D rendering but to stereo headset. Same MUD substrate; different camera and viewport.

### Replay view
Captures MUD substrate snapshots. Replays them into any of the above views. Same data, time-shifted.

### Statistical view
No rendering; produces dashboards: how many atoms of each type, fusion rate, average bond order, heat distribution, etc. Useful for testing, analytics, streaming overlays.

Players choose their view(s); games can support multiple simultaneous views per player (3D primary + minimap secondary + text log).

## Multi-modal multiplayer

This architecture enables MIXED-MODE multiplayer where different players run different views into the same shared MUD world:

- Player A is a 3D combatant: full mesh rendering, plays the action game.
- Player B is a 2D scout: top-down map view, plays a strategic game.
- Player C is a MUD player: text-only, plays an exploration / RP game.
- Player D is a spectator: replay / statistical view, watches.

All four are in the same world. Player A sees player B as a moving entity in 3D; player B sees player A as a dot on the map; player C reads "Player A is approaching from the southwest, type: 3D combatant, heading 45°."

Network sync transmits MUD substrate updates only. Bandwidth is low. Each player's local engine renders into their chosen view.

Latency tolerance is per-view: text/MUD is tolerant of seconds of latency; 2D is tolerant of 100ms; 3D combat needs <50ms. The substrate sync rate adjusts per player based on which view they need.

## Skeleton-of-the-next: building UP through layers

When a 2D view needs to render an entity, it asks: "Where on the screen does this 0D position project?"

When a 3D view needs to render an entity, it asks: "Stretch a mesh across the 1D bonds, then enclose it in a 3D volume."

The construction is always upward from MUD substrate to view-specific representation. The reverse direction never needs to happen: views never modify substrate state directly. Player input modifies substrate; substrate updates; views observe and project.

This is one-way data flow, model-view-isolated.

## Efficiency analysis (worked example)

Scenario: 1,000 atom soup, 4 players, mixed views (2 in 3D, 1 in 2D map, 1 in text MUD).

**At 60fps:**

- Substrate update: 0D + 1D for all 1,000 atoms = ~10ms
- Player A (3D, sees ~50 atoms in active range): 3D processing for 50 atoms = ~25ms
- Player B (3D, sees ~50 atoms): another ~25ms (parallelizable on GPU)
- Player C (2D map, sees ~200 atoms): 2D projection + render = ~5ms
- Player D (text MUD, sees ~30 atoms): text generation = ~1ms

Per-player budget: ~16.7ms (60fps). Players A/B fit (substrate + their 3D work). Players C/D have tons of headroom.

Network: substrate delta sync at ~100 atom-updates per second per player. Tiny.

Compare to traditional architecture (everything 3D for everyone): 1,000 atoms × 4 players = 4,000 3D-entity updates per frame. At 0.5ms per entity, that's 2 seconds per frame. Unplayable.

The architecture buys us 100x throughput by not over-processing.

## Player operates 0D-2D; 3D is emergent

A foundational asymmetry: **the player never directly controls the 3D layer.** Player input always operates at the low-dimensional layers (0D position/orientation, 1D aim/target/connection, 2D movement direction). The 3D body, its physics, its collision with other 3D bodies, its rendering — all of that is the SIMULATION'S work, run autonomously from the player's lower-dimensional intentions.

Every FPS game does this implicitly: WASD updates a 2D directional intent; mouse movement updates a 0D orientation and 1D aim; click commits a 1D action. The simulation translates these to 3D character physics, projectile trajectories, mesh animation, audio. The player never reaches in and grabs the 3D mesh.

Framework reading: the • aperture ACTS; the ○ boundary is what HAPPENS. Action originates at the aperture; consequence manifests at the boundary. The player IS the aperture; their 3D body is the consequence.

Architectural implications:

**Input layer is always low-dimensional.** Player input never touches 3D state directly. It updates 0D-2D intent on the player's entity. Simulation then propagates those intentions to 3D consequences.

**3D is the "consensus reality."** When two players collide in 3D, neither directly controls the collision; the simulation owns it. This is why multiplayer works without arbitration battles: the 3D layer falls out of everyone's lower-dimensional inputs deterministically (or with light server reconciliation). Nobody fights over the 3D state.

**Network sync is dimensional.** Sync 0D-2D INTENTS (player position, orientation, aim, movement direction) — tiny payload, low latency, ~10-50 bytes per player per tick. Each peer computes 3D consequences locally from the same intents. Disagreements get reconciled periodically via authoritative state.

**Perception is the reverse path.** Player sees the 3D world via 2D screen projection (rendering), 1D awareness threads (attention to specific objects), 0D fovea (focus point). Foveated rendering exploits this: render expensively only at 0D focus + 1D awareness, cheaply at 2D periphery, cheaper still in the wireframe substrate.

The complete loop:

```
Player input  (0D-2D, cheap, low-bandwidth)
   ↓
Substrate     (0D + 1D state; sparse connection graph)
   ↓ via simulation
3D world      (3D, emergent; all bodies + physics interaction)
   ↓ via rendering
Perception    (foveated 3D → 2D screen → 1D awareness threads → 0D focus)
   ↑
Player input  (loop closes)
```

Three observations:

1. The expensive layers (3D simulation, full rendering) live INSIDE the loop, not at its endpoints. The endpoints (player intent, player perception) are cheap.

2. The architecture is dimensionally efficient by construction: cheap things stay cheap because they're at low dimensions; expensive things only run when low-dimensional work demands them.

3. Multi-modal multiplayer (one player in 3D, another in 2D map, another in text MUD) is naturally supported because every player only TOUCHES the low-dimensional substrate. Their views are independent and can vary in fidelity without affecting the substrate's truth.

This is also why MUDs work: they have only 0D-1D-2D loops. Players input intents; the world's text-described state updates; players read text descriptions. No 3D layer is ever needed for the gameplay to be coherent. Adding a 3D layer is just adding one more rendering option, not a fundamental change in the loop's structure.

## 0D-1D is the always-broadcast substrate; 2D is the first shared interaction layer

All layers are sync'd to all observers — there's no "private" data in the substrate. The framework treats reality as observable. What VARIES across layers is what the layer DOES, not who can see it.

| Layer | Always-on? | What it is | First "shared" in what sense |
|-------|-----------|------------|------------------------------|
| 0D | YES | Every entity's position + orientation. Always broadcast. | Already shared, but it's just being. |
| 1D | YES | Every entity's connection graph (bonds, target-locks, awareness threads). Always broadcast. | Already shared, but it's just relating. |
| 2D | on-demand | Shared field of mediation. Where MOVEMENT and INTERACTION between entities happen. | First MEDIATION layer — Φ is by definition between things. |
| 3D | on-demand | Shared volumetric physics. Where bodies collide and physics resolves. | First COLLISION layer — ○ boundaries meet ○ boundaries. |

So 0D-1D is the always-on substrate that every observer can read. 2D is the first layer where mediation happens (Φ is by framework definition the field between ⊙s). 3D is where physical bodies collide. The "first SHARED" character of 2D is about MEDIATION, not about visibility — visibility was already universal at 0D-1D.

Architectural consequences:

**The substrate IS shared truth.** Every observer can read every entity's 0D position and 1D connections. This is the cheap data that flows freely. Network sync at the substrate level is broadcast, not negotiated.

**2D is where players ENTER each other's worlds.** Two entities at the same 2D position are co-present in a shared field. The field is the place where their ⊙s overlap; their actions there affect each other. This is "mediation" in the framework's sense.

**3D is where bodies collide.** Two entities at the same 3D position can't both occupy it — physics resolves. This is the first layer where SHARED PHYSICAL CONSEQUENCE exists. 3D resolution happens deterministically from 2D inputs (position, velocity); no observer "owns" the resolution.

**Network sync is uniform, not asymmetric.** All layers' state can be broadcast; what varies is FREQUENCY and METHOD. 0D-1D state is broadcast at substrate-tick rate (high). 2D state at interaction-tick rate (lower). 3D state at physics-tick rate (lowest, on collision events). All are public; the bandwidth tradeoff is per-layer.

**0D-1D feeds into 2D, which feeds into 3D.** The substrate provides the inputs for 2D mediation; 2D mediation provides the inputs for 3D collision. The vertical data flow is one-way upward through the layers.

**Multi-modal alignment.** All players — whether 3D, 2D map, or text MUD — share the same 0D-1D substrate. Different views project the substrate differently: text players read the entity descriptions; 2D map players see the connection graph; 3D players see the inflated mesh+physics. The truth is the substrate; views are projections.

**No player owns the 3D resolution.** Two players whose 3D bodies would collide are resolved by deterministic physics from their shared 2D state. Both clients compute the same 3D state from the same substrate. Server (or designated peer) only arbitrates when clients disagree.

**This explains why MUDs and 3D games have the same wire-level multiplayer logic.** A MUD broadcasts the substrate ("Alice is in the kitchen, holding the sword"). A 3D FPS broadcasts the substrate (Alice.position, Alice.holding). The wire data is the same shape; only the local rendering pipeline differs.

## Wireframe as the natural substrate visualization

The 0D + 1D substrate IS wireframe by construction: points (entities) and lines (connections). A wireframe rendering of the substrate isn't a stylistic choice; it's the raw data made visible. Anything ELSE we render is layered ON TOP of that wireframe.

This gives us:

- **A free debug view.** A wireframe mode shows the substrate directly: every entity as a dot, every connection as a line. Use for testing, network analysis, profiling, gameplay overview.
- **A natural low-fidelity tier.** When an entity is far away or at the periphery of view, render it as wireframe (one or two pixels per entity, zero shader cost). It's still THERE in the game; just not full 3D.
- **A consistent visual hierarchy.** All scales of view start from wireframe and add fidelity inward. The wireframe is the truth; higher fidelity is decoration.
- **A tiny network sync.** Wireframe data IS the substrate data. To sync the world to a remote client, send the wireframe. They can render at whatever fidelity they like locally.

For MMB this means: we already have most of the wireframe (bonds-as-lines, atom positions). Make it RENDERABLE as a primary view. Higher-fidelity views (3D meshes, shaders) are additions over the wireframe base.

## Foveated rendering: gaze-focal layer escalation

Per-entity layer escalation as defined earlier escalates by ENTITY DISTANCE to player. Foveated rendering escalates by SCREEN-SPACE distance to the gaze focal point. The two compound.

Human vision works this way: the fovea (~5° of visual field at the center of gaze) has dense color receptors and high spatial resolution. The periphery has fewer color receptors and lower resolution but is great at motion detection. The brain fills in the gaps.

VR headsets exploit this with foveated rendering: render the gaze-tracked center at full resolution, falling off to lower resolution at the periphery. Massive GPU savings (often 2-4×) with no perceived loss because peripheral detail isn't perceived anyway.

Apply the same to the engine's per-entity layer:

- **Tier 3 (full 3D)**: entities within ~10° of gaze AND in active interaction range. Full mesh, shader, nucleon cloud, lighting.
- **Tier 2 (simplified 3D)**: entities within ~25° of gaze (camera FOV center). Sphere with basic material. No nucleons, no shader effects.
- **Tier 1 (sprite)**: entities at the screen edge but within camera FOV. Single billboard sprite, color only.
- **Tier 0 (wireframe / off-screen)**: entities outside camera FOV or far away. Wireframe line if connected to a visible entity; otherwise invisible (substrate only).

The escalation rule combines distance and gaze:

```
tier = min(
  distanceTier(entity, player),      // 0..3 by world distance
  gazeTier(entity, gazeFocus)        // 0..3 by screen-space angle to gaze
)
```

A close entity at the periphery gets the same tier as a distant entity at the center. Both deserve modest fidelity; neither deserves full 3D.

For MMB at 1000-atom soup with one player:
- Tier 3 (~5 atoms in active interaction at center of gaze): full treatment
- Tier 2 (~30 atoms in mid-screen near range): simple sphere
- Tier 1 (~100 atoms at screen edges or mid-distance): sprite billboard
- Tier 0 (~865 atoms off-screen or very far): wireframe / not rendered

Total render cost: ~5× tier-3 + ~30× tier-2 + ~100× tier-1 + 0× tier-0 ≈ ~1ms vs the ~15ms it would take to do all 1000 at tier 3.

Compounds with the layer escalation: a tier-0 entity also stays at substrate-layer 1D processing. Tier-3 entities are the only ones running full 3D physics. Tier-1 entities run minimal physics.

## Combined: substrate-wireframe + foveated render

The complete picture:

```
SUBSTRATE (always-on, cheap):
  ├─ 0D: positions, orientations, types, states
  └─ 1D: connections, bonds, awareness graph

VIEW (per observer, foveated):
  ├─ Tier 0: wireframe (just connection lines + dots)
  ├─ Tier 1: sprite billboards (small visible markers)
  ├─ Tier 2: simplified 3D (spheres, basic materials)
  └─ Tier 3: full 3D (mesh, shaders, nucleons, particle effects)
  
  Tier assigned per entity based on:
    - World distance to player
    - Screen-space angle to gaze focus
```

Each view's render cost is dominated by tier-3 entities (the few in the gaze-focal interaction range). Tier-1 and tier-0 entities cost nearly nothing. The same architecture supports thousands of entities at 60fps where naive rendering would manage tens.

For VR specifically: tier 3 gets even tighter (~3° fovea), tier 2 falls off quickly. The architecture is VR-ready out of the box.

## Implementation roadmap

**v5.0**: Refactor MMB substrate to MUD-data first.
- Strip particles[] entries to 0D + 1D minimum (position, orientation, element, state, connections list)
- All 3D mesh / material / shader state lives in a separate "view-state" object owned by the 3D view
- The 3D view subscribes to substrate, lazily creates view-state for entities in 3D range
- Substrate update logic stops touching view-state directly

**v5.1**: Add per-entity layer escalation.
- Each entity tracks its activeLayer
- Engine update loop processes at activeLayer
- Far entities run cheap; near entities run expensive

**v5.2**: Add the 2D map view.
- Top-down map of all entities
- Renders to a corner panel
- Demonstrates pluggable view architecture

**v5.3**: Add the text view.
- Side panel with scrolling text descriptions of entities in player's awareness range
- "You see a Carbon atom 12 units NE, bonded to H, gas state, heat 23."
- Optional MUD-style commands (`look`, `who`, `where`, `examine`)

**v5.4**: Multi-mode multiplayer prep.
- Network protocol carries substrate deltas only
- Each connected client picks its own view(s)
- Initial test: two browser windows, same world, different views

**v5.5**: VR view via WebXR.
- Same 3D rendering but stereo
- Same substrate
- VR observer is just another view subscriber

**v5.6+**: All the game features (weapons, AI, combat, win conditions) build on top of this clean architecture.

## Open design questions

1. **Substrate representation: object graph or columnar arrays?** Object graph is easier to reason about; columnar is faster for bulk operations (Entity-Component-System pattern). The framework doesn't dictate; performance does.

2. **Connection types: one list per entity (heterogeneous) or separate lists (homogeneous)?** Heterogeneous is cleaner; homogeneous is faster (no type-dispatching per element).

3. **View update frequency: per-frame, on-demand, or push from substrate?** Push (substrate fires events when state changes; views react) is most efficient but more complex than polling.

4. **Networking: full state every tick, or deltas only?** Deltas with periodic full state for resync. Standard practice.

5. **Save/load: substrate snapshot or replay log?** Snapshot is simpler. Replay log is tiny and rewindable. Both possible.

6. **Multi-view conflicts: if player A is in 3D and player B is in 2D, what does B see when A fires a weapon?** Probably: B sees a notification ("Player A fired at C") + a visible animated dot on the 2D map. The substrate event ("weapon fired") is broadcast; each view renders it appropriately.

7. **Authority: which player's machine is authoritative for substrate state?** Standard answer: a server (or one designated peer in P2P) holds the canonical substrate; clients sync from it. Or full P2P with eventual consistency for non-conflicting state.

## Connection to other design docs

- `circumpunct_particle_taxonomy.md` (v0.1, 2026-04-24): defines what each ⊙ is at every rung of the ladder. The substrate represents these properties.
- `microverse_element_dna.md` (v0.1, 2026-04-25): defines the specific element library + interaction registry. Substrate stores element identity; behavior table is queried by views or substrate-update logic.
- This doc (v0.1, 2026-04-25): defines HOW the engine processes that data efficiently, in dimensional layers, with pluggable views.

The three docs together cover: WHAT entities are (taxonomy), WHICH entities exist (DNA library), and HOW to compute/render them (this doc).

## Revision history

- 2026-04-25 v1.0: committed as v5.0 build spec. Added 0D-1D-always-broadcast clarification (2D is first MEDIATION layer, not first PUBLIC layer; visibility was already universal at substrate). Player-operates-0D-2D asymmetry section added. Wireframe-as-substrate section. Foveated-rendering tiers spelled out. Roadmap v5.0 → v5.6 stable.
- 2026-04-25 v0.1: initial draft. Four-layer architecture, MUD substrate, pluggable views, multi-modal multiplayer, efficiency analysis, implementation roadmap.
