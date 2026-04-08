# Last Ship Sailing on CircumpunctGPU: Architecture Map

## The Principle

Every entity in the game is a CircNode. Ships, projectiles, arena walls, particles,
stasis fields: all circumpuncts at different scales, with different balance parameters,
at different phases of the pump cycle.

The game logic (physics, abilities, networking, AI) stays as JavaScript.
The rendering backend changes from Three.js to CircumpunctGPU.
The HUD stays as Canvas 2D (already circumpunct-native).

---

## System Mapping

### 1. Ships as CircNode Hierarchies

Original: THREE.Group with child meshes (cone, box, cylinder) + Phong materials + edge outlines.

CircumpunctGPU: Each ship is a root CircNode with children for components.
The ship class determines the hierarchy shape:

```
Frigate (NORTHSTAR, RONIN):
  root ⊙ (scale=40, d=3, balance=0.6)  // sleek, boundary-biased
    nose ⊙ (scale=12, d=2)
    hull ⊙ (scale=20, d=3)
    wing_L ⊙ (scale=15, d=2)
    wing_R ⊙ (scale=15, d=2)
    engine ⊙ (scale=8, d=1, phase=pump)  // 1D: line/thrust

Corvette (ION, TONE, MONARCH):
  root ⊙ (scale=50, d=3, balance=0.5)  // balanced
    hull ⊙ (scale=25, d=3)
    bridge ⊙ (scale=10, d=2)
    shoulder_L ⊙ (scale=12, d=3)
    shoulder_R ⊙ (scale=12, d=3)
    barrel ⊙ (scale=8, d=1)
    engine ⊙ (scale=10, d=1, phase=pump)

Dreadnought (SCORCH, LEGION):
  root ⊙ (scale=65, d=3, balance=0.4)  // heavy, more boundary
    core ⊙ (scale=35, d=3)
    armor_top ⊙ (scale=30, d=3)
    keel ⊙ (scale=25, d=3)
    engine_L ⊙ (scale=12, d=1, phase=pump)
    engine_R ⊙ (scale=12, d=1, phase=pump)
```

At distance, the ship collapses to a single point (0D).
At medium range, you see the outline (1D edges).
At close range, full surfaces (2D) and volume (3D).
The dimensional ladder IS the LOD system.

### 2. Arena as Root Circumpunct

Original: Marching cubes SDF mesh + boundary grid + fog.

CircumpunctGPU: The arena IS the outermost ⊙.
  - Arena boundary (the ○) = the root CircNode at scale=25000
  - Rooms = child CircNodes carved into the field
  - Corridors = connections between room nodes
  - Level geometry = SDF evaluated in compute shader
  - Fog = the field (Phi) at low visibility

The marching cubes worker stays as-is (CPU side), but outputs
directly to a WebGPU vertex buffer instead of Three.js geometry.

### 3. Projectiles and Particles

Original: Lines (tracers), points (particles), transient point lights.

CircumpunctGPU: Projectiles are CircNodes at small scale.
  - Tracer: d=1 (line), moving fast, short life
  - Bullet: d=0 (point), high speed
  - Missile: d=2 (surface), tracking target
  - Explosion: rapidly increasing d from 0 to 3 (expanding boundary)

Particles managed in a compute-pass ring buffer:
  - Compute pass updates position, velocity, life
  - Dead particles recycled via atomic counter
  - Rendered as d=0 (point sprites)

### 4. Lighting

Original: Ambient + 3 directional + point + hemisphere + transient weapon flashes.

CircumpunctGPU: Light IS convergence. Every aperture (dot) emits.
  - The sun: a distant CircNode with high convergence weight
  - Weapon flash: a temporary CircNode with high phase speed (fast pump, bright convergence phase)
  - Engine glow: CircNode at d=1 with phase locked to speed

In the fragment shader, lighting is computed from nearby apertures
in the CircNode buffer (read in the render pass).

### 5. Post-Processing

Original: 4-pass bloom (extract brights, blur H, blur V, composite) + vignette + chromatic aberration.

CircumpunctGPU: Compute passes.
  - Pass 1: render scene to texture
  - Pass 2 (compute): extract bright pixels (threshold 0.7)
  - Pass 3 (compute): separable Gaussian blur (9-tap)
  - Pass 4: composite render pass (scene + bloom + vignette + aberration)

Chromatic aberration strength driven by `player.damageIndicator`.
Vignette from framework: alpha falls off as (V-1)/V from center.

### 6. HUD

Original: Canvas 2D with 9 concentric ring layers. Already circumpunct.

STAYS AS-IS. The Canvas 2D HUD is overlaid on the WebGPU canvas.
No port needed; it's already the best implementation.

### 7. Networking

Original: P2P via Trystero (WebTorrent), 20Hz broadcast, hit consensus.

STAYS AS-IS. Pure JavaScript, no rendering dependency.

### 8. AI Bots

Original: Line-of-sight, memory decay, squad targeting, nav via corridor points.

STAYS AS-IS. Pure JavaScript. Bot ship entities are just CircNodes
that the AI system moves.

### 9. Audio

Original: Web Audio API with positional audio.

STAYS AS-IS. No rendering dependency.

---

## Compute Pass Schedule (Per Frame)

```
1. PUMP PASS (compute)
   - Update all CircNodes: phase, convergence/emergence, breathing
   - Ships, projectiles, particles, stasis fields: all updated

2. GAME LOGIC (CPU)
   - Physics: velocity, collision (raycast against SDF)
   - Input: 6DOF controls
   - Abilities: cooldowns, activation, effects
   - AI: bot decisions, navigation
   - Networking: receive/send state
   - Spawn/despawn entities (write to CircNode buffer)

3. LOD PASS (compute)
   - Evaluate every CircNode against camera
   - Choose representation: 0D/1D/2D/3D
   - Write visible instances to draw buffer
   - Set indirect draw args

4. RENDER PASS
   - Clear framebuffer
   - Draw level geometry (marching cubes mesh, separate pipeline)
   - Draw CircNode instances (billboards with dimensional SDF)
   - Draw weapon effects (tracers, flashes)

5. POST-PROCESS PASSES (compute + render)
   - Bright extraction (compute)
   - Blur (compute, 2 passes)
   - Composite (render: scene + bloom + vignette + aberration)

6. HUD (CPU)
   - Canvas 2D: draw circumpunct rings
   - Composite over WebGPU output
```

---

## New Pipelines Needed (beyond current CircumpunctGPU)

1. **Level geometry pipeline**: Vertex buffer from marching cubes, custom wall shader (procedural texturing), standard rasterization.

2. **Tracer/line pipeline**: Line rendering for weapon traces. Could be thin billboard quads or actual line primitives.

3. **Post-process compute**: Bloom extraction, blur, composite.

4. **Dynamic lighting in fragment shader**: Read nearby CircNodes as light sources.

5. **SDF collision in compute**: Raycast against level SDF for physics.

---

## File Structure

```
CircumpunctGPU/
  circumpunct-gpu.js        // Core library (exists)
  lss-game.js               // Game logic (physics, abilities, AI, networking)
  lss-ships.js              // Ship class definitions and CircNode hierarchies
  lss-level.js              // Level generation (marching cubes worker)
  lss-hud.js                // Circumpunct HUD (Canvas 2D)
  lss-audio.js              // Audio system
  lss-net.js                // Networking (Trystero P2P)
  lss-postfx.js             // Post-processing compute passes
  last_ship_sailing.html    // Entry point
```

---

## Build Order

Phase 1: Core flight
  - 6DOF movement and camera
  - Empty arena (boundary CircNode only)
  - Ship rendered as CircNode hierarchy
  - Basic controls (WASD + mouse)

Phase 2: Combat
  - Weapon fire (tracers, projectiles)
  - Hit detection (raycast)
  - Damage, health, death/respawn
  - Muzzle flash (transient CircNode lights)

Phase 3: Arena
  - Procedural level generation
  - Marching cubes mesh rendering
  - Collision against SDF
  - Fog

Phase 4: Ships and abilities
  - All 7 ship classes as CircNode hierarchies
  - Ship selection screen
  - Ability system (Q/E/F + core)
  - Class-specific weapons

Phase 5: AI
  - Bot spawning and navigation
  - Combat AI
  - Squad behavior

Phase 6: Polish
  - Post-processing (bloom, aberration, vignette)
  - Circumpunct HUD
  - Particles (sparks, explosions)
  - Audio
  - Stasis fields

Phase 7: Networking
  - P2P connection
  - State broadcast
  - Hit consensus
