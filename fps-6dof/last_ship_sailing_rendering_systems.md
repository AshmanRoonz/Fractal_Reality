# Last Ship Sailing: Three.js Rendering Systems Analysis

## Overview
The rendering pipeline in `last_ship_sailing.html` uses Three.js with a custom post-processing layer, SDF-based level geometry generation via marching cubes, and a circumpunct ring HUD rendered on a separate canvas overlay.

---

## 1. SCENE SETUP & CORE OBJECTS

### Lines 1324-1342: Basic Scene/Camera/Renderer
```
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(90, window.innerWidth / window.innerHeight, 1, 25000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
```

**Key Settings:**
- **FOV:** 90 degrees (wide for 6DOF combat)
- **Near/Far Planes:** 1 to 25,000 units
- **Pixel Ratio:** Capped at 2 for performance
- **Clear Color:** `0x0a0520` (dark purple-black space theme)
- **Output Encoding:** `sRGBEncoding` (vivid colors)
- **Scene Fog:** `THREE.FogExp2(0x0a0520, 0.000015)` — light fog; low density to keep indoor walls visible

---

## 2. POST-PROCESSING PIPELINE (Lines 1343-1510)

### Architecture
Custom fullscreen quad-based post-FX with NO external library. Bloom + vignette + chromatic aberration (on damage).

### Render Targets
```javascript
postFX.rtScene       // Main scene renders here (full resolution)
postFX.rtBright      // Bright pixel extraction (half resolution)
postFX.rtBlurH       // Horizontal blur pass
postFX.rtBlurV       // Vertical blur pass
postFX.quadGeo       // Shared PlaneGeometry(2, 2)
postFX.quadCamera    // OrthographicCamera(-1, 1, 1, -1, 0, 1)
```

### Shader Materials
1. **Brightness Extraction** (lines 1375-1388)
   - Extracts pixels > 0.7 brightness using luminance formula
   - `fragmentShader`: Threshold comparison with color passthrough

2. **Gaussian Blur** (lines 1391-1418)
   - Separable blur (horizontal + vertical)
   - 9-tap kernel with standard deviation weights
   - Uniforms: `tDiffuse`, `direction` (1,0 or 0,1), `resolution`

3. **Composite/Final Pass** (lines 1421-1462)
   - **Chromatic Aberration:** Driven by `chromAb` uniform (set by damage indicator intensity)
     - RGB channels offset by distance from center
     - Formula: `abAmount = chromAb * dist * 0.02`
   - **Bloom:** Additive blend of blurred bright pixels
   - **Vignette:** Radial falloff using `smoothstep(vignetteSize, vignetteSize + 0.55, dist * 1.4)`
   - **Film Grain:** Subtle per-frame noise `(fract(sin(...)) - 0.5) * 0.03`
   - **Uniforms:** `tScene`, `tBloom`, `bloomStrength` (0.45), `vignetteIntensity` (0.35), `vignetteSize` (0.45), `chromAb` (damage-driven), `time`

### Rendering Function
**`renderPostFX()` (lines 1470-1510)**
1. Render main scene to `rtScene`
2. Extract bright pixels to `rtBright`
3. Blur horizontally to `rtBlurH`
4. Blur vertically to `rtBlurV`
5. Composite all layers to screen

---

## 3. LIGHTING (Lines 1512-1527)

### Static Lights
```javascript
ambientLight = THREE.AmbientLight(0x445577, 0.8)        // Bright, flat cartoon look
dirLight = THREE.DirectionalLight(0xffeedd, 1.2)       // Key light (warm), position (1000, 3000, 1500)
dirLight2 = THREE.DirectionalLight(0x8888ff, 0.4)      // Fill light (cool blue, from below)
pointLight = THREE.PointLight(0x6699ff, 0.5, range=12000) // Position (0, 500, 0)
hemiLight = THREE.HemisphereLight(0x6688cc, 0x224466, 0.6) // Sky/ground split
```

**Approach:** Cartoon/toon style with high-contrast edges, minimal shadows. Heavy reliance on ambient + directional for flat aesthetic.

### Dynamic Lights
- **Engine glow flashes:** Additive blended materials on ship meshes
- **Explosion lights:** Updated in `updateDynamicLights()` (called each frame in gameLoop)
- **No shadow maps** (too expensive for fast-paced 6DOF)

---

## 4. STARFIELD (Lines 1531-1556)

**Type:** Three.js Points geometry with per-vertex color

**Generation:**
- 4000 stars randomly placed in ±10000 unit cube
- Color palette: 6 predefined color variations (warm yellows, cool blues, pink)
- Size: 5 pixels per star
- Material: `THREE.PointsMaterial` with `vertexColors: true`, `opacity: 0.9`

**No animation** (static for performance)

---

## 5. ARENA BOUNDARY GRID (Lines 1558-1580)

**Type:** Line segments grid

**Construction:**
- 3 axes, 2 planes per axis (±face), 500 unit grid spacing
- Material: `THREE.LineBasicMaterial(0x112244, opacity=0.15)`
- Subtle visual boundary aid; kept very faint

---

## 6. LEVEL GEOMETRY: SDF + MARCHING CUBES

### Approach (Lines 8114-8220+)
**Function:** `buildRoomGraphLevel(level)`

**SDF Types:**
1. **Sphere (Room):** `sdSphere(px, py, pz, cx, cy, cz, r)`
2. **Cylinder (Tunnel):** `sdCylinder(px, py, pz, ax, ay, az, bx, by, bz, r)` — endpoint-based capsule
3. **Smooth Union:** `sdfSmin(a, b, k)` with k=45 radians

**Data Storage (lines 8148-8155):**
```javascript
game.levelSpheres  = [{cx, cy, cz, r}, ...]         // Rooms
game.levelCylinders = [{ax, ay, az, bx, by, bz, r}, ...] // Tunnels
game.sdfRoomData = rooms                             // Original level data
```

### Marching Cubes
**Worker or Sync (lines 1589+):**
- If Web Worker available: async generation in parallel
- Fallback: synchronous (blocks frame; shown in map-gen-hud)

**Tables (line 8216-8218):**
- `mcEdgeTable` (256 entries): edge configuration for each cube corner pattern
- `mcTriTable`: Precomputed triangle list for each configuration
- `mcEdgeVerts`: 12 edges of a cube

**Mesh Generation (lines 8220+):**
- Creates `THREE.BufferGeometry` with computed vertex normals
- Material: Custom shader (wall shader)

### Wall Shader (Lines 8226-8263+)

**Vertex Shader (`sdfVertSrc`):**
- Transforms position to world space
- Computes normal direction
- Calculates AO from normal (upward normals = 1.0, others darker)
- Passes to fragment

**Fragment Shader (`sdfFragSrc`):**
- Receives up to 8 room centers/colors (uniform arrays)
- Perlin noise + hash-based wall vein animation
- Color interpolation based on proximity to nearest room
- Time-driven vein animation for visual interest
- Emissive accents on panel seams

**Key Uniforms:**
- `time`: For vein animation (set each frame: `game.levelMaterial.uniforms.time.value = game.time`)
- `roomCenters[8]`, `roomColorsU[8]`, `roomRadii[8]`
- `roomCount`: Number of rooms

---

## 7. SHIP RENDERING

### Ship Mesh Creation
**Function:** `createShipMesh(chassisData, teamColor)` (lines 2056-2263)

**Output:** `THREE.Group` containing:
- Multiple composite parts (hull, wings, engines, cockpit, armor, turrets)
- Part meshes with outlines (EdgesGeometry for hard edges)
- Shield bubble (SphereGeometry, transparent cyan, initially opacity=0)
- Engine glow meshes (CircleGeometry with AdditiveBlending)
- Thruster meshes (small circles with cyan additive blend)
- Panel glow meshes (for seam accents)

**Chassis Types:**
1. **Frigate:** Sleek, pointed nose, twin engines, swept wings
2. **Corvette:** Balanced, boxy, single large engine, maneuvering thrusters
3. **Dreadnought:** Massive, layered armor, multiple engine banks

**Materials:**
```javascript
hullMat = THREE.MeshPhongMaterial({ color: teamColor, specular: 0x444444, shininess: 60 })
darkMat = THREE.MeshPhongMaterial({ color: 0x222233, specular: 0x222222, shininess: 40 })
accentMat = THREE.MeshPhongMaterial({ color: offsetHSL(...), specular: 0x666666, shininess: 80 })
cockpitMat = THREE.MeshPhongMaterial({ color: 0x1a3355, specular: 0x88bbff, shininess: 120, emissive: 0x0a1a33, emissiveIntensity: 0.4 })
engineGlowMat = THREE.MeshBasicMaterial({ color: teamColor, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending })
thrusterMat = THREE.MeshBasicMaterial({ color: 0x44ddff, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending })
outlineMat = THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 })
```

**userData Storage:**
```javascript
group.userData = {
  engineMesh: glow_mesh,
  shieldMesh: shield,
  engineGlows: [glow1, glow2, ...],
  barrelMeshes: [barrel1, barrel2, ...],
  panelGlowMat,
  engineGlowMat
}
```

### Ship Animation
**Function:** `animateShipMesh(mesh, speed, maxSpeed, isFiring, dt)` (lines 2267-2306)

**Engine Glow Animation:**
- Opacity: `baseOp = 0.3 + t * 0.6` (t = speed/maxSpeed)
- Pulse: `sin(time * 12) * 0.08 * t` (added to opacity)
- Scale: `baseScale = 0.6 + t * 0.8`, then `flicker = 1 + sin(time * 18) * 0.05 * t`

**Barrel Recoil (when firing):**
- Trigger: `barrel.userData.recoil = 1.0`
- Decay: `recoil -= dt * 8` per frame
- Position offset: `originalZ + recoil * 3` (kicks back)
- Flash: Emissive color = 0xff8800 if `recoil > 0.5`, else 0x000000
- Emissive intensity driven by recoil value

---

## 8. PROJECTILES

### Projectile Class (Lines 2784-2983+)
**Constructor:** `new Projectile(origin, velocity, damage, splash, owner, color)`

**Rendering:**
- **Mesh:** `THREE.Mesh(SphereGeometry(3, 6, 4), THREE.MeshBasicMaterial({color}))`
- **Trail:** `THREE.Line(BufferGeometry, LineBasicMaterial)` with 2 position points
  - Updated each frame: `positions[0..2]` = prev position, `positions[3..5]` = current position
  - Attribute marked dirty: `geometry.attributes.position.needsUpdate = true`

**Special Effects:**
- **Arc Wave:** Lightning bolts spawned forward
  - Function: `spawnLightningBolt(start, end, color, width, intensity, lifetime)`
  - Random wall arcs (30% chance per frame)
  - Spark particles: 2 per frame at projectile position

- **Cluster Projectiles:** Spawn children on impact via `spawnClusterChildren()`

- **Fire Source:** Ignites gas clouds via `igniteNearbyGas(position, radius)`

**Tracking (Homing Missiles):**
- Close range (<800 units): aggressive tracking, loose FOV (-0.3)
- Mid range (800-3000): moderate tracking, threshold 0.2
- Far range (>3000): gentle, tight FOV (0.5)
- Turn rate: Lerp toward target direction at rate 5.0/3.0/1.5

**Salvo Core Remote Guidance:**
- Steers toward player's camera crosshair (aim point)
- Aggressive turn rate: 6.0 * dt

**Physics:**
- Velocity-based movement: `position += velocity * dt`
- Wall collision raycast: `raycastLevel(prevPos, moveDir, moveDist + 5)`
- Bounce behavior: velocity reflection off normal, energy loss (0.5-0.75 multiplier)
- Splash damage on explode: `splashDamage()` within radius
- Impact sparks: `spawnImpactSparks(hitPoint, count)`

---

## 9. CAMERA

### First-Person Camera (Player)
**Function:** `updatePlayerMovement(dt)` (lines 4218-4400+)

**Mouse Look:**
```javascript
if (input.locked) {
  player.euler.y -= input.mouseDX * input.sensitivity;
  player.euler.x -= input.mouseDY * input.sensitivity;
}
player.euler.x = Math.max(-π*0.45, Math.min(π*0.45, player.euler.x))  // ±81 degrees pitch
camera.quaternion.setFromEuler(player.euler);
camera.position.copy(player.position);
```

**Direction Vectors (derived each frame):**
```javascript
forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
up = new THREE.Vector3(0, 1, 0);  // World up, not camera-relative
```

**Gamepad Look (curve applied in `pollGamepad()`):**
```javascript
player.euler.y -= input.gpLookX * input.gpLookSensitivity * dt;
player.euler.x -= input.gpLookY * input.gpLookSensitivity * dt;
```

### Death Cam (Third Person)
**Object:** `deathCam` (lines 9502+)

**Fields:**
- `active`: Boolean flag
- `target`: Player's position at death
- `angle`: Orbit angle (incremented each frame)
- `radius`: Distance from target (based on ship size)
- `height`: Y offset above target

**Update** `updateDeathCam(dt)` (lines 9518-9524):
```javascript
deathCam.angle += dt * 0.4;  // Slow orbit
camX = target.x + cos(angle) * radius;
camY = target.y + height;
camZ = target.z + sin(angle) * radius;
camera.position.set(camX, camY, camZ);
camera.lookAt(deathCam.target);
```

**Activation:** `activateDeathCam()` (line 9510)
- Called when `playerDie()` triggered
- Sets `deathCam.active = true`, copies player position, initializes orbit

---

## 10. HUD RENDERING

### Circumpunct Ring HUD (Canvas Overlay)
**Canvas:** `<canvas id="circumpunct-hud"></canvas>` (line 309)

**Function:** `drawCircumpunctHUD()` (lines 6211-6450+)

**DPI Handling:**
```javascript
const dpr = window.devicePixelRatio || 1;
hudCanvas.width = W * dpr;
hudCanvas.height = H * dpr;
hudCanvas.style.width = W + 'px';
hudCanvas.style.height = H + 'px';
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
```

**Layers (concentric rings, bottom-to-top):**

1. **Layer 0: Center Crosshair (lines 6252-6282)**
   - Legion close-range: Circle (22px radius)
   - All others: Standard + crosshair
   - Center dot (3.5px)
   - Crosshair arms: 28px length, 10px gap

2. **Layer 1: Health Ring (lines 6304-6363)**
   - Inner radius: 150px
   - Arc: 7 o'clock to 5 o'clock (bottom half)
   - Segmented by `player.chassis.healthSegments` (e.g., 4-6 segments)
   - Segment gaps: 0.04 radians
   - Color: Green (healthy) → Amber (60%) → Red (<30%) → Flash red (doomed)
   - Brighter inner edge highlight
   - Boundary ticks between segments
   - Health value text below ring

3. **Layer 2: Shield Ring (lines 6365-6400)**
   - Outer radius: 190px
   - Arc: 11 o'clock to 1 o'clock (top half)
   - Thinner than health (5px linewidth)
   - Color: Cyan
   - Tick marks: 10% intervals (major every 50%)
   - No text overlay

4. **Layer 3: Speed Arc (lines 6402+)**
   - Left side of screen
   - Scales with velocity

5. **Layer 4: Core Meter (lines ~6450+)**
   - Right side
   - Scales with `player.coreMeter / 100`

6. **Layer 5: Threat/Lock Indicators**
   - Enemy TONE lock warning (DOM element, positioned absolutely)
   - Pips showing lock count (0-3)
   - Color: Orange (locking) → Red (full lock)
   - Animation: Pulse at full lock

### Ability HUD (DOM Elements)
**Function:** `updateAbilityHUD()` (lines 7229-7267)

**Elements:** 4 slots (Q, E, F, V for abilities) displayed bottom-center

**Slot Update (per ability):**
- Class: `ability-slot` + state (`ready`, `on-cooldown`, `active-now`)
- Cooldown bar: width = `(1 - cd/maxCd) * 100%`
- Cooldown text: Shows seconds remaining or ability-specific values
  - Gun Shield: Shows HP
  - Thermal Shield: Shows HP
  - ION abilities: Override bar to show energy %

### Minimap
**Function:** `updateMinimap()` (lines 7079-7173)

**Canvas:** `<canvas id="minimap">` 150x150px, top-left

**Elements:**
- Background: Semi-transparent dark
- Tunnel cylinders: Lines
- Room spheres: Filled circles with stroke
- Player: White square, with white direction line
- Bots: Colored squares (red/green by team)
- Doomed indicator: Red circle around bot
- Stasis fields: Cyan pulsing diamonds
- Map label: Bottom center

**Scaling:** Auto-fit to level geometry extent

### HUD Update Loop
**Function:** `updateHUD()` (lines 7018-7075)

Called once per frame in `gameLoop()`:
1. Draw circumpunct ring HUD
2. Update core meter DOM element
3. Update doomed warning visibility + vignette
4. Update enemy lock-on warning + pips
5. Update round timer/score display
6. Update ability bar

---

## 11. GAME LOOP & RENDERING SEQUENCE

**Function:** `gameLoop(timestamp)` (lines 8681-8786)

**Frame Timing:**
```javascript
game.deltaTime = Math.min(0.05, (timestamp - game.lastTime) / 1000);  // Cap at 50ms
game.lastTime = timestamp;
game.time += game.deltaTime;
```

**Update Sequence (if not paused/dead):**
1. Update level shader time: `levelMaterial.uniforms.time.value = game.time`
2. Poll gamepad
3. Update player movement + weapon
4. Update abilities + round system
5. Update all bots (entity.update(dt) + ship mesh animation)
6. Resolve ship-ship collisions
7. Update projectiles (alive check, cleanup dead)
8. Update dynamic objects, organics, particles, effects
9. Update screen shake, damage indicators
10. Update HUD (calls `drawCircumpunctHUD()`)
11. Update minimap
12. Update enemy health bars (DOM)
13. Apply screen shake to camera (if not in death cam)
14. **`renderPostFX()`** — Main render call

**Frame Rate:** Uncapped (requestAnimationFrame)

---

## 12. SCREEN EFFECTS

### Screen Shake
**Variable:** `game.shakeOffset = {x, y}`

**Application (line 8773):**
```javascript
camera.position.x += game.shakeOffset.x;
camera.position.y += game.shakeOffset.y;
```

**Driven by:** Damage, explosions, weapon fire

### Damage Indicators
**Variable:** `game.damageIndicators = {top, bottom, left, right}`

**Usage:** Drives chromatic aberration in composite shader
```javascript
postFX.compositeMat.uniforms.chromAb.value = damageMax * 3.0;
```

**Update:** Called in `updateDamageIndicators(dt)`

---

## 13. KEY FILE LOCATIONS & FUNCTION SIGNATURES

| System | Function/Variable | Line(s) | Purpose |
|--------|------------------|---------|---------|
| **Scene Setup** | scene, camera, renderer | 1324-1341 | Core THREE.js objects |
| **Post-FX** | postFX object | 1347-1510 | Bloom, vignette, CA pipeline |
| **Lights** | ambientLight, dirLight, etc. | 1513-1527 | Static toon-style lighting |
| **Starfield** | createStarfield() | 1531-1556 | 4000 colored point stars |
| **Level Geometry** | buildRoomGraphLevel(level) | 8114-8300+ | SDF rooms + tunnels → marching cubes |
| **Level Shader** | sdfVertSrc, sdfFragSrc | 8226-8263+ | Wall material with vein animation |
| **Ship Creation** | createShipMesh(chassis, color) | 2056-2263 | Composite ship model builder |
| **Ship Animation** | animateShipMesh(mesh, speed, dt) | 2267-2306 | Engine glow + barrel recoil |
| **Projectile** | class Projectile | 2784-2983+ | Sphere mesh + trail line, physics |
| **Player Movement** | updatePlayerMovement(dt) | 4218-4400+ | Camera control, input, collision |
| **Death Cam** | updateDeathCam(dt), activateDeathCam() | 9518-9524, 9510-9514 | Third-person orbital view |
| **Circumpunct HUD** | drawCircumpunctHUD() | 6211-6450+ | Canvas-based health/shield rings |
| **Ability HUD** | updateAbilityHUD() | 7229-7267 | DOM-based cooldown bars |
| **Minimap** | updateMinimap() | 7079-7173 | Canvas radar overlay |
| **Main Render** | renderPostFX() | 1470-1510 | Bloom + composite to screen |
| **Game Loop** | gameLoop(timestamp) | 8681-8786 | Update all systems, call renderPostFX |

---

## 14. NOTES FOR MULTIPLAYER CLIENT PORT

### Critical Rendering Patterns
1. **SDF Level Generation:** Async marching cubes worker; fallback to sync. Geometry needs to be updated per round.
2. **Ship Models:** Built from reusable `createShipMesh()` function; store all state in `userData`.
3. **Projectiles:** Simple sphere + trail; handle via per-entity tracking in projectile list.
4. **HUD:** Split between canvas (circumpunct) + DOM (abilities, kill feed). Both driven by player state.
5. **Post-FX:** Shader passes are resolution-aware; maintain same pipeline for consistency.

### Performance Considerations
- No shadow maps (too expensive)
- Vertex colors instead of textures for starfield
- Additive blending for dynamic lights (cheap)
- Canvas-based HUD avoids WebGL state thrashing
- Marching cubes run in worker to avoid frame drops

### Camera Notes
- First-person tied to Euler angles (yaw/pitch)
- Death cam uses orbit calculations (no camera parenting)
- Input sensitivity customizable per control type (mouse vs gamepad curve)

---

## 15. SHADER SUMMARY

### Wall Shader (Fragment)
- **Input:** World position, normal, room proximity data
- **Output:** Color with vein animation + ambient occlusion
- **Key Technique:** Perlin noise-based procedural veins; hash-based variation
- **Performance:** Fast enough to run on 8+ room configurations

### Post-FX Shaders
1. **Brightness Extraction:** Simple luminance threshold
2. **Gaussian Blur:** Standard 9-tap separable
3. **Composite:** Chromatic aberration, bloom blend, vignette, film grain

All shaders use `varying` for ES2 compatibility (no compute shaders).

---

## APPENDIX: Important Constants

```javascript
game.sdfSmoothK = 45              // Smooth union parameter (radians equivalent)
postFX.brightMat.uniforms.threshold.value = 0.7  // Bloom threshold
postFX.compositeMat.uniforms.bloomStrength = 0.45
postFX.compositeMat.uniforms.vignetteIntensity = 0.35
postFX.compositeMat.uniforms.vignetteSize = 0.45
scene.fog.density = 0.000015
renderer.pixelRatio = Math.min(window.devicePixelRatio, 2)
ARENA_SIZE = ~5000                // Boundary grid extent
animateShipMesh speed threshold = t = speed / maxSpeed
```

