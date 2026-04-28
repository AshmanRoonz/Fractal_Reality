# LSS Server-Sim Port Plan

Created: 2026-04-26
Last updated: 2026-04-26
Version: 1.3

The plan for finishing the thin-client + server-authoritative port of Last Ship Sailing.

This document is the canonical reference for what's done, what's left, what order to do it in, and what each port involves. Update it as work lands.

## Architecture commitment

We're building a **thin-client + server-authoritative** version of LSS:

- **Server** (`server-sim/`): authoritative simulation in TypeScript, runs on Bun. Owns all gameplay state (positions, HP, projectiles, hits, abilities, match state, bot AI). Sends 64Hz snapshots to clients.
- **Client** (`last_ship_sailing_sim.html`): thin client built from scratch. Renders snapshots; sends inputs. No local sim.

Why this path: code we control, anti-cheat by construction, swappable client (mobile/console possible later), server can run in any language. The trade-off is more upfront work than a P2P or relay model. Estimated remaining ~4000-5000 lines across server and client. The user is committed to this path.

## Files

- **`last_ship_sailing.html` ; the original LSS, the canonical source we are porting from.** Untouched. Every feature claim, every behavior detail, every audio recipe, every tuning value should be cross-checked against this file by line number before being declared "done." When in doubt about how something should behave, **read LSS first**. Each numbered plan item below cites LSS line ranges, and every "LSS reference:" tag should resolve to actual code in this file. If a behavior is missing from LSS, it is a [PROPOSED] addition and should be flagged as such, not assumed.
- `last_ship_sailing_sim.html` ; the thin client we're building. Currently at v8.57.
- `server-sim/main.ts`, `simulation.ts`, `level.ts`, `loadouts.ts` ; the server.
- Backups preserved: `last_ship_sailing_sim_v8.15_thinclient_backup.html`, `last_ship_sailing_sim_v8.16_lssfork_broken.html`, `last_ship_sailing_sim_v8.17_lssfork_phaseA.html` (the LSS-fork experiment, abandoned).

## Status snapshot

### Server (simulation.ts)

Done:
- 64Hz tick + state broadcast
- 9 LSS maps (hourglass, spine, infinity, tower, cross, arc, octahedron, pentagon, gyre) ported as data
- SDF collision (smooth-min blended room/tunnel union)
- Player movement with chassis stats from loadouts
- Bot AI (chase + shoot)
- Projectile motion + hit detection
- Shield-first damage (LSS line 4364, 7723)
- Auto-fire while held (LSS line 8097)
- Match state machine: select / warmup / playing / roundEnd / matchEnd
- Round-win counting (LSS line 9947-9973), tie-on-time-out → A
- ROUNDS_TO_WIN = 4 (best-of-7); matchEnd → 10s linger → reset
- round_end + match_end events emitted on transitions
- Hit/kill events with position + shooter
- Fire events for networked audio
- Doomed flag (LSS line 4388, 30% threshold)
- Spawn protection (3s grace, LSS line 4365)
- Reload + clip ammo (LSS line 8094-8121, 2s reload)
- World effects framework (firewall, trip_wire, tether, incendiary, gas, particle_wall) with area-damage / area-slow / proximity-detonation handlers
- All 28 abilities have server-side dispatch (every chassis Q/E/F/V); marked // SIMPLIFIED: where depth is missing

Done (added in v8.28-v8.30):
- BLASTER spinup mechanic (charges before fire)
- BLASTER mode switch actual stat swap (close/long with 1s lockout)
- Stasis fields (immobilization + shield recharge pickups)
- Destructibles (cluster obstacles + debris with HP)

Not done:
- Full ability fidelity (see "Second sweep" S1-S7 below)
- Tremor (low-HP audio/visual wobble)
- Lock-on system depth (TRACKER homing per-tick steering)
- Particle Wall as deployable entity (currently a buff)
- Salvo Core remote-guided missiles
- Friendly fire toggle (currently no FF)
- Player-vs-player collision (ships pass through each other)
- Hitscan/raycast path (all weapons are sphere-vs-projectile)
- Bot ability use (bots only chase + shoot; never use Q/E/F/V)
- Bot dodging / strafing
- Bot pathfinding (currently steer direct + SDF push-out; breaks in tunnels)
- Anti-spawn-camp spawn selection (currently random pool)
- Per-chassis hull collision radius (PLAYER_RADIUS = 60 flat)
- Per-chassis spawn-protection scaling (flat 3s)
- Knockback impulses on damage
- Splash/radius damage as a generic system
- Projectile penetration
- Match seed actually used for deterministic obstacle placement
- Reconnection on WS drop (server-side resume of player slot)
- Snapshot delta encoding

### Client (last_ship_sailing_sim.html)

Done:
- WebSocket connection + lobby UI
- Snapshot consumer (player/bots/projectiles)
- Marching cubes wall mesh from server level data
- Procedural audio module (reverb chain, phi-cascade ambient, ~10 sound recipes)
- Spatial audio (PannerNode, listener tracking, environment probe)
- Circular HUD rings (health segmented arc + shield arc)
- Per-ship health bars (HTML overlay above each ship)
- Ship GLBs + cockpit frame
- Hit/kill marker flashes
- Networked fire SFX (other players' shots play spatially)
- Sonar ping audio (TRACKER F)
- Sonar highlight rings on enemies (TRACKER F)
- Shield bubble visual (TRACKER E)
- Lobby with 7 loadout cards + team switch + ready
- Cockpit frame swaps with loadout

Done (added in v8.18-v8.27):
- Particle pool (impact sparks, shield shimmer, explosions) triggered by snap events
- Kill feed (HTML overlay, top-right, 5-entry rolling, 5s fade)
- Damage indicator (4 directional SVG arrows, lights up by attacker quadrant)
- Doomed vignette (red full-screen pulse below 30% HP)
- Camera shake (own hits + nearby explosions, exponential decay)
- Spawn protection bubble (cyan-white sphere around fresh-spawned ships)
- Reload UI (orange bar with progress fill)
- Ammo display (current/max, color-coded empty)
- Speed arc + ammo arc (left/right of crosshair)
- Per-chassis health segment counts (3/5/7 from chassis lookup)
- Cinematic banner (ROUND OVER with score, VICTORY/DEFEAT with team color)
- World-effect renderers (planes for walls, boxes for firewalls, spheres for area effects, octahedrons for trip wires)

Done (added in v8.28-v8.34):
- Spinup UI (BLASTER chaingun charge indicator)
- 3-2-1 launch countdown overlay (cinematic transitions)
- FIGHT! banner on warmup → playing
- Match-end scoreboard with kills/deaths/damage per player
- Gamepad input (sticks, buttons, triggers, deadzone, sensitivity, persistence)
- Reload key (R) for manual reload
- Round-start audio fanfare
- Stasis pickup visuals + immobilization UI
- Destructible cluster meshes + debris

Not done:
- Damage vignette layered with doomed (red ring scaling with health %)
- Tremor effect (low-HP audio wobble)
- Settings panel UI for gamepad bindings + sensitivity (config exists; no UI)
- Mid-match scoreboard (Tab key) showing per-player stats
- Teammates strip in lobby (shows other connected peers' selected ships)
- Per-ability unique audio recipes (dash, ability, core, etc. ; we have generic fire only)
- Per-ability unique visuals (beam meshes for lasers, lightning bolts, fire trails, etc.)
- Lock-on indicator (rings showing 1/2/3 stacks for TRACKER)
- Snapshot interpolation (currently renders raw last-received snapshot; stepped at 64Hz)
- Client-side prediction (every input round-trips before player sees ship move)
- Reconnection on WebSocket drop
- Ping / lag display
- Loading screen between maps
- Death cam (look at killer)
- Respawn timer countdown overlay
- Per-weapon-mode crosshair variants
- FOV change on boost
- Camera shake from own firing (only have hit-shake)
- Banking/roll on yaw (visual)
- Engine pitch shift with speed (currently constant)
- Audio Doppler (PannerNode supports it; not configured)
- Audio occlusion through walls (sound bleeds through walls at full volume)

## Remaining work, in priority order

Each item below has:
- **What it is**
- **LSS reference** (line ranges to port from)
- **Server scope** / **Client scope** (estimated lines)
- **Dependencies**

### 1. Score tracking + round-win conditions [SERVER]

Foundation for match flow. Without this, rounds never end.

- LSS reference: `updateRoundSystem` line 9919-10063
- Server: count alive players per team each tick; when one team is at 0, increment scoreA/scoreB and transition to `roundEnd`. After 3 wins, transition to `matchEnd`. Reset on next round.
- Client: render scores in HUD (top center, fleet a/b labels) ; mostly already wired, just needs to read snap.match.scoreA/scoreB.
- Server: ~80 lines. Client: ~20 lines.
- Dependencies: none.

### 2. Round-end + match-end visuals [CLIENT]

LSS shows banners at state transitions: ROUND 1 / FIGHT / ROUND OVER / VICTORY.

- LSS reference: `Overlays.countdown`, `Overlays.banner` ~line 10072-10090, 10112, 10131
- Client: detect state transitions in snap.match.state edges; trigger banner animation. CSS already provides the elements.
- Client: ~80 lines.
- Dependencies: #1.

### 3. Reload + clipAmmo system [SERVER + CLIENT]

Each weapon has a clip; runs out, reloads after 2s.

- LSS reference: `startReload` line 8117, `updateWeapon` line 8094
- Server: track player.clipAmmo, player.maxClip, player.reloading, player.reloadTimer. Decrement on fire, trigger reload when empty or on R key, refill after timer.
- Client: render reload bar, show ammo count in HUD.
- Server: ~60 lines. Client: ~40 lines.
- Dependencies: none.

### 4. Spinup + mode switch (BLASTER) [SERVER + CLIENT]

BLASTER chaingun has a spinup time before firing; close/long mode switch.

- LSS reference: line 8085-8090 (spinup), line 8927-8931 (mode switch).
- Server: track player.spinupTimer, player.spunUp; gate fire on spunUp; toggle close/long mode via ability slot 2.
- Client: render spinup indicator, mode label.
- Server: ~40 lines. Client: ~30 lines.
- Dependencies: none.

### 5. Doomed state + tremor [SERVER + CLIENT]

Below 30% HP, ship enters doomed state. HUD pulses red, audio gets a tremor.

- LSS reference: line 4388, 7732, 14175, etc.
- Server: track player.doomed, set when hp/maxHp < 0.3; clear on respawn.
- Client: doomed flag triggers HUD red flash, audio tremor (~5Hz gain wobble).
- Server: ~20 lines. Client: ~50 lines.
- Dependencies: none.

### 6. Spawn protection [SERVER + CLIENT]

3-second invulnerability window after spawn so you don't get spawn-killed.

- LSS reference: `LSS.SPAWN_PROTECTION = 3.0`, line 4365 (ignore damage), line 7554 (set on respawn)
- Server: player.spawnProtection timer; _applyDamage checks and short-circuits while > 0.
- Client: render protection bubble (translucent shimmer) while active.
- Server: ~20 lines. Client: ~30 lines.
- Dependencies: none.

### 7. Particles batch 1: combat impacts [CLIENT]

Sparks on projectile hit, shield hit shimmer, explosion on kill.

- LSS reference: `spawnExplosion`, `spawnShieldHit`, `spawnImpactSparks` line 5400-5500ish, `updateParticles` line 6228+
- Client: particle pool with shared geometry; spawn helpers triggered from snap events.
- Client: ~250 lines. Server: 0.
- Dependencies: none.

### 8. Camera shake + damage indicator + vignette [CLIENT]

Camera shake on hits, red directional flash from attacker, red vignette at low HP.

- LSS reference: `addScreenShake`, `showDamageIndicator`, the damage-indicator SVG elements at top of file
- Client: shake offset applied to camera transform; SVG damage indicator triggered from hit events with direction; vignette opacity from health %.
- Client: ~150 lines.
- Dependencies: server already sends hit events with shooter position.

### 9. Kill feed [CLIENT]

Top-right rolling list of "X killed Y with Z" entries.

- LSS reference: `addKillFeed` line ~7747
- Client: HTML overlay, push entries on snap.events kill, fade after 5s.
- Client: ~80 lines. Server: needs to add shooter loadoutKey to kill events (~5 lines).
- Dependencies: #1 (events shape).

### 10. Remaining HUD layers [CLIENT]

Speed arc, ammo arc, ability cooldown rings, doomed flash, per-chassis health segment counts.

- LSS reference: line 10355-10650 in the canvas HUD draw function
- Client: extend our `_circHud.draw()` with these layers; pull values from snap.
- Client: ~250 lines.
- Dependencies: #3 (ammo), #5 (doomed).

### 11. Abilities: PUNCTURE remaining [SERVER + CLIENT]

3 abilities: Cluster Missile (Q), Tether Trap (F), Afterburner Core (V).

- LSS reference: line 8580-8629 (cluster), line 8870-8902 (tether), line 9020-9055 (cores)
- Server: cluster missile = special projectile that splits on impact; tether = world effect that slows enemies; afterburner core = 5s of speed boost + rocket barrage spawn.
- Client: visuals for cluster split, tether tendril mesh, core particle effect.
- Server: ~150 lines. Client: ~100 lines.
- Dependencies: #15 (world effects framework) for tether.

### 12. Abilities: SLAYER remaining [SERVER + CLIENT]

3 abilities: Arc Wave (Q), Sword Block (E), Sword Core (V).

- LSS reference: line 8528-8580 (arc wave), line 4368 (sword block in takeDamage), line 9008-9020 (sword core)
- Server: arc wave = projectile that destroys walls on contact; sword block = passive 70% damage reduction in `_applyDamage`; sword core = 5s of melee + arc waves.
- Client: arc wave visual, sword glow effect, core particle ring.
- Server: ~100 lines. Client: ~80 lines.
- Dependencies: none for arc wave/block; #15 for full sword core (impact zones).

### 13. Abilities: VORTEX kit [SERVER + CLIENT]

4 abilities: Laser Shot (Q), Vortex Shield (E), Trip Wire (F), Laser Core (V).

- LSS reference: line 8550-8600 (laser shot), line 9091-9118 (vortex shield), line 8845-8870 (trip wire), line 8995-9008 (laser core)
- Server: laser shot = instant beam dealing 2400 damage; vortex shield = held shield that reflects projectiles; trip wire = proximity mines; laser core = 4s continuous beam.
- Client: laser beam mesh, shield bubble, mine entities, core beam mesh.
- Server: ~200 lines. Client: ~150 lines.
- Dependencies: #15 for trip wire.

### 14. Abilities: PYRO kit [SERVER + CLIENT]

4 abilities: Firewall (Q), Thermal Shield (E), Incendiary Trap (F), Flame Core (V).

- LSS reference: line 8800-8870 (firewall), line 8772-8780 (thermal), line 8870-8900 (trap), line 9020-9050 (flame core)
- Server: firewall = line of fire dealing 400 DPS for 6s; thermal shield = held shield with power pool that burns nearby; incendiary trap = proximity area-fire; flame core = 2s of massive AoE.
- Client: firewall flame mesh, thermal shield haze, trap area visual, core fire effect.
- Server: ~250 lines. Client: ~200 lines.
- Dependencies: #15 for firewall/trap as world effects.

### 15. World effects framework [SERVER + CLIENT]

Generic system for world entities (firewalls, trip wires, tethers, traps, gas clouds, particle walls).

- LSS reference: `game.worldEffects` ~line 8800, various effect handlers
- Server: SimState gains worldEffects array; each entry has type, position, geometry, hp, timer, owner. Tick decrements timers, removes expired. Snapshot includes them.
- Client: render loop walks worldEffects, creates/disposes meshes per type.
- Server: ~150 lines. Client: ~200 lines.
- Dependencies: foundational for #11, #13, #14, #16, #17.

### 16. Stasis fields [SERVER + CLIENT]

Special ability that immobilizes the player and recharges shield.

- LSS reference: line 12442-12470
- Server: track player.inStasis, stasisTimer; immobilize player; tick shield recharge.
- Client: stasis charging visual, immobilization UI, vignette.
- Server: ~80 lines. Client: ~120 lines.
- Dependencies: #15.

### 17. Destructibles (cluster obstacles + debris) [SERVER + CLIENT]

Map-spawned destructible obstacles you can shoot for cover.

- LSS reference: `ClusterObstacle` line 7383+, `spawnDynamicObjects` line 7556
- Server: SimState.dynamicObjects array; cluster obstacles with HP; on destroy, spawn debris with drift physics. Projectile collision against them.
- Client: render cluster mesh (5-10 child shapes), debris physics mirror.
- Server: ~250 lines. Client: ~250 lines.
- Dependencies: #15 (uses similar framework).

### 18. Abilities: BLASTER kit [SERVER + CLIENT]

4 abilities: Power Shot (Q), Gun Shield (E), Mode Switch (F), Smart Core (V).

- LSS reference: line 8630-8670 (power shot), line 8762-8767 (gun shield), line 8927-8931 (mode), line 9522-9540 (smart core)
- Server: power shot = 1s charge then high-damage hitscan; gun shield = frontal absorber with HP; smart core = auto-aim rapid fire.
- Client: power shot charge bar, gun shield mesh, smart core auto-aim indicator.
- Server: ~180 lines. Client: ~120 lines.
- Dependencies: #4 (mode switch).

### 19. Abilities: SYPHON kit [SERVER + CLIENT]

4 abilities: Rocket Salvo (Q), Energy Siphon (E), Rearm (F), Upgrade Core (V).

- LSS reference: line 8672-8680 (rocket salvo), line 8687-8755 (siphon), line 8932 (rearm), line 9059-9082 (upgrade core)
- Server: rocket salvo = 5 missile burst; energy siphon = lightning beam that drains shields and heals; rearm = reset all cooldowns; upgrade core = 3 tiers of permanent buffs.
- Client: rocket trails, lightning bolt mesh, rearm flash, upgrade UI.
- Server: ~200 lines. Client: ~180 lines.
- Dependencies: none.

### 20. Gamepad input + settings [CLIENT]

Stick mapping, button bindings, deadzone config, persistence.

- LSS reference: `pollGamepad` line 13800ish, `LSS.gamepad` mapping, settings panel HTML
- Client: gamepad polling each frame; map sticks/buttons to input fields; settings panel with bindings + sensitivity + deadzone; localStorage persistence.
- Client: ~350 lines.
- Dependencies: none (independent of all gameplay work).

### 21. Cinematic match-end scoreboard [CLIENT]

End-of-match summary with kills, deaths, damage dealt, ability uses.

- LSS reference: scoreboard rendering ~line 11000+
- Client: HTML scoreboard overlay; pulls from snap on matchEnd state.
- Server: extend snapshot with damageDealt per player (~10 lines).
- Client: ~150 lines.
- Dependencies: #1, #2.

## Recommended order

The bedrock first, then combat depth, then polish. Phases 1-6 below all shipped through v8.18-v8.34. Phase 7 (non-ability gaps) and Phase 8 (second-sweep ability depth) are what's left.

**Phase 1 ; foundation:** #1 (score), #2 (round/match banners), #3 (reload), #5 (doomed), #6 (spawn protection). Without these, the match flow doesn't really work. ~600 lines total. **DONE v8.18.**

**Phase 2 ; combat feel:** #7 (particles), #8 (camera shake / damage indicator), #9 (kill feed), #10 (HUD layers). Makes hits and damage feel right. ~800 lines total. **DONE v8.19-v8.20.**

**Phase 3 ; world effects framework:** #15. Foundation for the rest of the abilities. ~350 lines. **DONE v8.21.**

**Phase 4 ; ability kits:** #11, #12, #13, #14, #18, #19. One chassis at a time, each ~250-450 lines. ~2000 lines total. **DONE (first-pass) v8.22-v8.27.**

**Phase 5 ; stasis + destructibles + spinup/modes:** #4, #16, #17. ~700 lines total. **DONE v8.28-v8.30.**

**Phase 6 ; input + polish:** #20 (gamepad), #21 (match-end scoreboard). ~500 lines total. **DONE v8.31-v8.33** (gamepad fire-stuck fix v8.34).

**Phase 7 ; non-ability gaps (physics, networking, bot AI, polish):** see "Non-ability gaps" section below. ~1500-2000 lines.

**Phase 8 ; second-sweep ability depth:** see "Second sweep" section below. ~2500-3000 lines.

**Phase 9 ; third-sweep balance & polish:** see "Third sweep" section below. ~500-1000 lines.

## Estimates

| Phase | Lines | Sessions (rough) | Status |
|---|---|---|---|
| 1 ; foundation | 600 | 1 | DONE v8.18 |
| 2 ; combat feel | 800 | 1-2 | DONE v8.19-v8.20 |
| 3 ; world effects framework | 350 | 1 | DONE v8.21 |
| 4 ; ability kits (first pass) | 2000 | 3-5 | DONE v8.22-v8.27 |
| 5 ; stasis + destructibles + spinup/modes | 700 | 1 | DONE v8.28-v8.30 |
| 6 ; input + polish | 500 | 1 | DONE v8.31-v8.34 |
| 7 ; non-ability gaps | ~2300 | 6-9 | TODO (see Non-ability gaps section) |
| 8 ; second-sweep ability depth | ~3000 | 6-8 | TODO (see Second sweep section) |
| 9 ; third-sweep balance & polish | ~800 | 2-3 | TODO (see Third sweep section) |
| **Total remaining** | **~6100** | **14-20** | |
| **Total project** | **~11050** | **22-31** | |

## Risks

- **Edge-case porting bugs.** Each LSS feature has hidden flags and side-effects we'll discover as we go. Mitigate by porting one item at a time and testing.
- **Snapshot bandwidth growth.** As we add worldEffects, destructibles, particle data, snapshot size grows. We may need delta encoding eventually. Not a near-term issue.
- **Visual fidelity drift.** Our particle / shader work may not match LSS's exactly. Acceptable; close-enough is fine.
- **Per-chassis stat tuning.** LSS values are fine-tuned over many iterations; ours are copies. Should be OK but might feel different in practice.

## Visual identity per chassis and ability

The eight effects in `effects_demo.html` are the visual vocabulary; this section maps each one to specific weapons and abilities so we don't ad-hoc the look as we wire them in. Items marked [USER] were specified by Ashman; items marked [PROPOSED] are gap-fills awaiting confirmation.

### Main weapons

| Chassis | Effect | Notes |
|---|---|---|
| VORTEX | Emissive + Bloom | [USER] cyan/blue energy bolts; the canonical "looks expensive" weapon |
| PYRO | Emissive + Bloom (fiery) | [USER] orange/red palette, same effect, hotter colors and softer falloff |
| TRACKER | Fresnel Rim | [USER] 40mm shells ; rim-lit projectile geometry |
| SLAYER | Particle Burst | [USER] shotgun-style; tight spread cone of additive points per shot |
| BLASTER | Emissive + Bloom (yellow) | [PROPOSED] chaingun bolts; low-saturation yellow, higher fire rate so density does the work |
| SYPHON | Emissive + Bloom (purple) | [PROPOSED] energy rounds; deep purple/magenta to differentiate from VORTEX cyan |
| PUNCTURE | Tube Ribbon Trail (short tail) | [PROPOSED] kinetic darts with a brief contrail; reads as "long thin thing moving fast" |

### Shields (the universal shield bubble + per-chassis variants)

| Use | Effect | Notes |
|---|---|---|
| Universal shield (every ship's basic shield) | Energy Shield | [USER] the hex-cell fresnel sphere; impact pulse on hit |
| VORTEX Vortex-Shield (E) | Energy Shield (half-shell) | [USER] frontal hemisphere only, blue palette; reflects projectiles |
| PYRO Thermal-Shield (E) | Energy Shield (half-shell, fiery) | [USER] frontal hemisphere, orange/red palette; burns enemies in contact range |
| BLASTER Gun-Shield (E) | Hologram Scanlines | [USER] flat panel in front of player, scanline grid |
| TRACKER Particle Wall (F) | Hologram Scanlines | [USER] deployable plane separate from the player |
| Spawn protection | Energy Shield (white-cyan) | [PROPOSED] universal shield with a brighter, calmer palette to read as "untouchable" |

### Beams and core abilities

| Use | Effect | Notes |
|---|---|---|
| VORTEX Laser-Shot (Q) | Volumetric Beam | [USER] standard-thickness instant beam |
| VORTEX Laser-Core (V) | Volumetric Beam (very thick) | [USER] same effect, much wider radius, longer duration |
| SLAYER Sword-Core (V) | Volumetric Beam (red, sword-shaped) | [PROPOSED] thicker than VORTEX laser-shot, shorter range, melee-coded color |
| BLASTER Smart-Core (V) | Volumetric Beam (yellow, brief) | [PROPOSED] auto-aimed flickering beam, briefer than VORTEX |
| Boosters / engine thrust (all chassis) | Volumetric Beam (short) | [USER] short beams from engine ports per chassis; on while moving forward, brighter on afterburner; **new feature, see NA27** |

### Lightning and electric

| Use | Effect | Notes |
|---|---|---|
| SLAYER Arc-Wave (Q) | Lightning Bolt (thick, short) | [USER] big chunky electric arc, short range |
| SYPHON Energy-Siphon (E) | Lightning Bolt (thin, long) | [USER] thin flickering chain, long range, drains over time |
| Stasis-field tendrils | Lightning Bolt (subtle, ambient) | [PROPOSED] continuous low-intensity arcs while stasis is active |

### Unspecified abilities (waiting on direction)

These chassis abilities don't yet have a visual identity locked in. Working list of proposals:

- **VORTEX Trip-Wire (F):** small octahedron mine + Hologram Scanlines panel face; arms on detection
- **PYRO Firewall (Q):** Particle Burst (sustained, fire palette) along a line; stays for duration
- **PYRO Incendiary Trap (F):** Particle Burst on detonation + brief Tube Ribbon trail to target
- **PYRO Flame-Core (V):** Particle Burst (massive, expanding sphere)
- **PUNCTURE Cluster-Missile (Q):** Tube Ribbon Trail in flight, Particle Burst on impact, sustained Lightning Bolt-like burn arcs in the impact zone
- **PUNCTURE Tether-Trap (F):** Lightning Bolt (thin, between mine and rooted target)
- **PUNCTURE Afterburner-Core (V):** Volumetric Beam (engine plume, intensified) + Tube Ribbon Trail
- **SLAYER Sword-Block (E):** Energy Shield (red, half-shell) facing forward
- **TRACKER Sonar-Lock (Q):** Hologram Scanlines (rings on enemies showing 1/2/3 stack count)
- **TRACKER Tracker-Rockets:** Tube Ribbon Trail per missile + small Bloom tip
- **TRACKER Salvo-Core (V):** N Tube Ribbon Trails fanning out + Hologram Scanlines target reticle on aim point
- **BLASTER Power-Shot (Q):** Bloom (huge, charged) + Particle Burst on launch
- **BLASTER Mode-Switch (F):** Hologram Scanlines transition flash
- **SYPHON Rocket-Salvo (Q):** Tube Ribbon Trail per rocket + Bloom tip
- **SYPHON Rearm (F):** Bloom flash (gold) + Hologram Scanlines ring around player
- **SYPHON Upgrade-Core (V):** Energy Shield-like aura (gold, persistent) + tier-up flash per stack

### Palette per chassis

For consistency across abilities, each chassis gets a primary color used across all its effects:

| Chassis | Primary | Accent | Reads as |
|---|---|---|---|
| VORTEX | cyan #44ccff | white #ffffff | high-tech energy |
| PYRO | orange #ff7733 | hot yellow #ffcc44 | heat, plasma, fire |
| TRACKER | green #66ff99 | white | clinical, scanner |
| SLAYER | red #ff4444 | gold #ffcc66 | aggressive melee |
| BLASTER | yellow #ffdd44 | gold #ff9933 | industrial, heavy |
| SYPHON | purple #cc66ff | electric blue #88ccff | exotic, vampiric |
| PUNCTURE | white #eeeeff | cyan-grey #aaccdd | clean kinetic |

## Non-ability gaps

The first pass built every ability and every match-flow piece structurally, but a lot of the systems they sit on top of are missing or shallow. This section catalogs every gap that isn't an ability behavior. Items marked **CRITICAL** change how the game fundamentally feels; items marked **POLISH** are quality-of-life. Each item has a rough estimate and dependencies.

### NA1. Player-vs-player collision [SERVER] **CRITICAL**

Ships currently pass through each other and through bots. No ramming, no body-blocking, no physical fight clutter.

- Server: in the integration step (after position update, before SDF resolve), do an O(n²) sphere-vs-sphere pass across all alive players + bots. Push apart along the contact normal with mass-weighted impulses; chassis hullLength × 0.5 sets the radius. Keep it simple ; no rotational physics, just position separation + velocity reflection along normal.
- LSS reference: `resolvePlayerCollisions` ~line 4900-4950.
- Server: ~80 lines. Client: 0 (positions arrive in snapshot).
- Dependencies: per-chassis hull radius (NA7).

### NA2. Snapshot interpolation on the client [CLIENT] **CRITICAL** (if WAN play)

Currently the client renders the last received snapshot raw, so movement arrives in 64Hz steps. Interpolation tweens between two recent snapshots to make motion smooth.

- Client: keep a 2-3 snapshot ring buffer with arrival timestamps. Render at `now - INTERP_DELAY` (typically 100-150ms) with linear lerp on positions and slerp/lerp on yaw/pitch. Bot/projectile positions get the same treatment. Local player position is special-cased (rendered from server's authoritative state but with input-applied predicted offset; see NA3).
- LSS reference: doesn't have this (LSS is local sim); look at any standard Quake-style netcode writeup.
- Client: ~150 lines.
- Dependencies: none.

### NA3. Client-side prediction for local player [CLIENT] **CRITICAL** (if WAN play)

Every input currently round-trips before you see your ship move. Under 50ms RTT it's fine; under 150ms it's unplayable.

- Client: maintain a local mirror of the player's velocity/position/yaw/pitch. Apply input each frame to the local mirror. When a server snapshot arrives, reconcile: if local position deviates from server's by > threshold, snap (or smoothly correct over ~5 frames). Keep an input sequence number so the server can echo back which inputs are confirmed.
- LSS reference: doesn't have this.
- Client: ~200 lines. Server: needs to echo input sequence number in snapshots (~10 lines).
- Dependencies: NA2 (interpolation; prediction sits on top of it).

### NA4. Hitscan / raycast path [SERVER] **CRITICAL** for proper lasers

All weapons are projectile + sphere overlap right now. VORTEX laser is a fast projectile pretending to be a beam. Real beams need a raycast path.

- Server: add a `_hitscanFire(state, shooter, dir, damage, range)` helper that ray-marches the SDF + casts against player/bot spheres + AABBs/destructibles. Returns first hit and applies damage. Used by VORTEX laser, smart-core auto-aim variants, sniper-style abilities.
- LSS reference: `hitscanFire` line ~5100.
- Server: ~80 lines. Client: needs a beam mesh visual (~50 lines per beam type, can share).
- Dependencies: none.

### NA5. Bot ability use [SERVER] **CRITICAL**

Bots only chase + shoot. They never use Q/E/F/V. Half their kit is invisible to the player.

- Server: extend `_tickBotAI` with an ability scheduler. Each bot has a per-slot cooldown bias and a heuristic per ability kind: aggressive abilities fire when an enemy is in line of sight at appropriate range; defensive abilities fire when health < 50% or recently damaged; utility abilities fire opportunistically. Per-loadout list of which slots map to which heuristic.
- LSS reference: `botUseAbility` ~line 6400-6600.
- Server: ~250 lines.
- Dependencies: none, but layers on top of every ability so do it after second sweep (S1-S7).

### NA6. Bot pathfinding + dodging [SERVER] **POLISH**

Bots steer direct toward target and rely on SDF push-out for walls. In tunnels they get stuck at wall corners; in fights they don't dodge.

- Server: cheap pathfinding ; cast 3-5 rays around the bot's intended direction; if direct path is blocked, pick the clearest alternative within ±60°. Dodging: when an enemy projectile is incoming within ~1s impact, sidestep perpendicular to its velocity.
- LSS reference: `botSteer` + `botDodge` ~line 6200-6400.
- Server: ~150 lines.
- Dependencies: none.

### NA7. Per-chassis hull radius + spawn protection [SERVER] **POLISH**

PLAYER_RADIUS = 60 is constant; LSS uses chassis.hullLength × 0.5 (range 40-70). Spawn protection is flat 3s; could scale with chassis (frigate 2s, dreadnought 4s).

- Server: replace PLAYER_RADIUS constant with `_hullRadius(player)` lookup; use it in collision + hit detection. Same for spawn protection ; lookup per-chassis from loadouts.ts.
- Server: ~30 lines.
- Dependencies: NA1 uses this.

### NA8. Knockback impulses [SERVER] **POLISH**

Heavy hits should push the target. Currently damage is purely numeric ; positions don't shift on impact.

- Server: in `_applyDamage`, if the hit is from a projectile with a known velocity vector, apply an impulse to the target's velocity proportional to damage and weapon mass. Some abilities specifically generate big knockback (Power Shot, Cluster Missile core).
- LSS reference: `applyKnockback` ~line 7800.
- Server: ~40 lines.
- Dependencies: none.

### NA9. Splash / radius damage as a system [SERVER] **POLISH**

Some abilities hand-roll their own AoE; there's no shared `_applySplashDamage(state, center, radius, damageFalloff, source)` helper. Cluster missile, rockets, explosions all reinvent it.

- Server: extract the shared helper. Used by cluster missile, salvo missiles, flame core, sword core, smart core, any explosion event.
- Server: ~50 lines. Refactors ~5 callsites.
- Dependencies: none.

### NA10. Projectile penetration [SERVER] **POLISH**

PUNCTURE chassis name implies it; not modeled. Some weapons should pass through one player and continue, or pass through walls (Arc Wave does the latter).

- Server: projectile gets `pierceCount` and `wallPierce: boolean`. On hit, if `pierceCount > 0`, decrement and continue instead of removing.
- Server: ~30 lines (mostly in `_tickProjectiles`).
- Dependencies: none.

### NA11. Anti-spawn-camp logic [SERVER] **POLISH**

Currently random pool from team's spawn array. Players can stack on the same spawn point or spawn next to enemies.

- Server: when picking a spawn, score each candidate by minimum distance to any enemy and to any teammate; pick highest score. Add small randomization so it isn't deterministic.
- LSS reference: `pickSpawnPoint` ~line 7500.
- Server: ~40 lines.
- Dependencies: none.

### NA12. Match seed used for deterministic obstacle placement [SERVER] **POLISH**

Server picks `Math.random() * 0xFFFFFFFF` as match seed but doesn't use it. LSS uses it so all clients get the same destructible/world-effect placement.

- Server: implement a tiny seeded PRNG (mulberry32, ~10 lines), thread the seed through `_spawnDestructiblesForRound` and `_spawnStasisFieldsForRound`. Snapshot includes the seed so any tooling can replay.
- Server: ~30 lines.
- Dependencies: none.

### NA13. Reconnection on WS drop [SERVER + CLIENT] **POLISH**

WS drops kick the player. They have to refresh and re-pick loadout.

- Server: keep player slot for ~30s after disconnect (mark stale); if same peerId reconnects with same session token, restore loadout + position + score. Otherwise drop after timeout.
- Client: detect WS close; auto-reconnect with backoff; re-send loadout on reconnect. Show "reconnecting..." overlay.
- Server: ~80 lines. Client: ~80 lines.
- Dependencies: none.

### NA14. Audio Doppler + occlusion [CLIENT] **POLISH**

PannerNode supports Doppler but isn't configured. Sounds also bleed through walls at full volume.

- Client: set PannerNode `dopplerFactor` to 0.3 and feed source velocity each frame. For occlusion: cast SDF ray from listener to source; if blocked, multiply gain by 0.3 and lowpass-filter the sound (cheap occlusion ; not perfect but big improvement).
- Client: ~80 lines.
- Dependencies: none.

### NA15. Engine pitch shift with speed [CLIENT] **POLISH**

Engine sound is constant. Should rise with speed (standard space-shooter feel).

- Client: in the engine audio recipe, set oscillator/source pitch from `speed / maxSpeed` mapped to a 0.7-1.4 multiplier. Update each frame.
- Client: ~20 lines.
- Dependencies: none.

### NA16. Camera + visual feedback for movement [CLIENT] **POLISH**

Several small visuals missing: FOV opens on boost; camera shakes when firing your own weapon; ship banks visually when yawing or strafing.

- Client: `targetFov = baseFov + (afterburnerActive ? 8 : 0)`; lerp current FOV toward it. Camera shake on own fire = small randomized offset for ~50ms scaled by weapon power. Banking = roll the cockpit/ship mesh by yawRate × 0.3 + strafeIntent × 0.2, capped at ~25°.
- Client: ~80 lines.
- Dependencies: none.

### NA17. Death cam + respawn timer overlay [CLIENT] **POLISH**

When you die, camera should track the killer for the respawn delay; overlay shows "Respawn in 3s".

- Client: on snap.events kill (where you're the victim), camera target switches to the shooter's position for the respawn delay. Big text overlay shows the countdown.
- Client: ~80 lines.
- Dependencies: none.

### NA18. Per-weapon-mode crosshair variants [CLIENT] **POLISH**

Currently single crosshair. Different weapons should look different (BLASTER long-mode = tight reticle, close-mode = wider; rockets = lock-on box, etc.).

- Client: crosshair is a small SVG element; per-loadout overrides set in a lookup table. Spinup on BLASTER = ring filling.
- Client: ~50 lines.
- Dependencies: NA21 below partly overlaps.

### NA19. Mid-match Tab scoreboard [CLIENT] **POLISH**

Press Tab to see live kills/deaths/damage scoreboard during play (already shipped end-of-match scoreboard in v8.32).

- Client: reuse the v8.32 scoreboard component; show on Tab keydown, hide on keyup.
- Client: ~40 lines.
- Dependencies: v8.32 shipped.

### NA20. Lobby teammates strip [CLIENT] **POLISH**

Lobby should show other connected players' selected ships.

- Client: render a row of mini cards for each peer, showing their loadout and ready state. Updates on snapshot.
- Client: ~80 lines.
- Dependencies: none.

### NA21. Full settings menu [CLIENT] **POLISH** (expanded scope)

A real settings menu accessible from lobby AND mid-match (Esc-pause). Currently nothing exists; gamepad config is in code only, audio is fixed, no exit or quit-to-main-menu paths.

Sections to include:
- **Gamepad:** per-binding remap (click button slot, press to capture), sliders for stick sensitivity, deadzone, invert-Y, trigger threshold; reset-to-defaults button
- **Keyboard + mouse:** rebindable WASD/space/ctrl/Q/E/F/V/R; mouse sensitivity; invert-Y option
- **Audio:** master volume, music volume, SFX volume, voice/announcer volume, mute-on-tab-out toggle; per-bus sliders feed into the existing audio bus chain
- **Graphics:** quality preset (low/med/high), bloom on/off, particle density (25/50/100%), shadow toggle (when shadows added), FOV slider, V-sync toggle
- **Match:** exit current match (return to lobby), quit server (drop connection, go back to a "main menu" landing page or just disconnect with a confirm dialog)
- **Persistence:** all settings save to localStorage under `lss_settings_v1`; load on boot

Spawned UI structure:
- Esc opens a translucent overlay over the canvas; in lobby it opens directly (no game running underneath)
- Tab navigation between sections (left rail or top tabs)
- Each setting is a row: label, control, optional reset-to-default
- Bottom buttons: Apply, Cancel, Defaults

Currently NA20 (lobby teammates strip) and NA21 are independent UI items that could share a component library; bundling them is reasonable.

- Client: ~500 lines (panel structure + 5 sections + persistence + apply/cancel logic).
- Dependencies: none for the panel itself; some sections wait on dependent systems (graphics quality preset needs the bloom + particle + shadow systems to exist; audio sliders need the bus chain refactored from per-recipe to per-bus).

### NA22. Loading screen between maps [CLIENT] **POLISH**

Map switch currently stutters as the marching cubes mesh rebuilds. Should show a brief overlay.

- Client: on `level` message receipt, show full-screen overlay; rebuild mesh; remove overlay when first state snapshot arrives for new level.
- Client: ~30 lines.
- Dependencies: none.

### NA23. Ping / lag indicator [CLIENT] **POLISH**

No visibility into connection quality.

- Client: server sends `ping` reply to `ping` request; client measures RTT, shows in HUD corner.
- Server: ~10 lines. Client: ~30 lines.
- Dependencies: none.

### NA24. Damage vignette layered with doomed [CLIENT] **POLISH**

Doomed pulses red below 30% HP. Want a continuous red ring overlay scaling with HP% so the player feels gradual damage, not just the doomed cliff.

- Client: HUD overlay with red border whose opacity = `1 - hp/maxHp` clamped above 30%. Compounds with doomed pulse below 30%.
- Client: ~30 lines.
- Dependencies: none.

### NA25. Tremor effect [CLIENT] **POLISH**

LSS adds a 5Hz audio gain wobble + slight camera shake when doomed.

- Client: while doomed, multiply audio bus gain by `0.85 + 0.15·sin(2π·5·t)` and add small camera offset on the same wave.
- Client: ~30 lines.
- Dependencies: NA17 (death cam) doesn't conflict.

### NA28. Minimap [CLIENT] **POLISH** (new feature)

Top-down (or top-iso) view of the current map showing teammates, enemies (within sensor range), projectiles-of-interest (rockets, cluster missiles), world effects (firewalls, traps, stasis pickups), destructibles. No minimap currently exists; players have no spatial awareness beyond what they can see through the cockpit.

Approach options:
- **Top-down 2D Canvas overlay (recommended):** sample the SDF along a horizontal slice through the player's Y position into a static contour at room load; render player + entity dots on top; cheap, ~200 lines
- **Real-time mini render** (second Three.js camera looking down at the scene): nicer-looking but expensive (extra render pass, full geometry); only worth it if the 2D version doesn't read well

Features:
- Player at center, facing up (rotates with player yaw); or fixed-north with player as a pointing arrow
- Teammates as small triangles in team color
- Enemies within sensor range (300u? per-chassis variant?) as red dots
- Projectiles classified as "interesting" (rockets, cluster missiles) as moving dots with trails
- World effects color-coded (firewall = orange, trap = yellow, stasis-pickup = green, particle wall = blue)
- Destructibles as small grey squares; fade as their HP drops
- Zoom toggle (close / mid / far) bound to a key
- Translucent panel in a corner of the HUD, sized for readability without dominating

- Client: ~200-300 lines (Canvas 2D overlay version).
- Dependencies: none. Reads from snapshot directly.

### NA27. Engine boosters / thrust visualization [CLIENT] **POLISH** (new feature)

Ships currently have no visible engine thrust. Boosters add short volumetric beams from each chassis's engine ports, lit while moving forward and intensified during afterburner. Critical for movement feel ; right now the speed feedback is only the speed-arc HUD number, with no spatial/visual cue.

- Client: per-chassis engine port positions defined in a lookup table (manually authored from each ship's GLB; 1-4 ports per chassis). On each frame, for each port, render a short Volumetric Beam pointing backward (relative to ship orientation) with length = `baseLen + speed/maxSpeed * extraLen`, brightness scaling with speed and afterburner status. Beams use the chassis's primary palette color (see Visual identity table).
- Tied to the camera/movement polish work: pairs naturally with NA16 (FOV opens on boost) and NA15 (engine pitch shifts with speed) for a coherent "going fast" feel.
- LSS reference: doesn't have proper boosters in the LSS source either; this is a new feature.
- Client: ~120 lines (lookup table + per-port beam pool + per-frame update).
- Dependencies: Volumetric Beam shader (from effects_demo.html); per-chassis palette table.

### NA38. Server-tagged shield-vs-hull hit SFX [SERVER + CLIENT] **POLISH** (port from LSS)

LSS plays distinct sounds: `damage_shield` (crystalline crack) when shield absorbed any of the hit, `damage` (dissonance) when armor took the overflow (LSS line 14913-14915). The client recipes already exist (`damage_shield`, `damage_hull`); the wire-up at `last_ship_sailing_sim.html` line 2682 currently *approximates* shield vs hull by reading the snapshot's `shield` value, with an in-code comment admitting "Server doesn't tag shield vs hull so we approximate from current shield value." This misfires on shield-breaking hits and on multi-hit frames.

The clean fix is server-side tagging:

- Server: `_applyDamage` knows the pre-hit shield, post-hit shield, and damage amount. Emit two booleans on the `hit` event: `absorbedByShield: boolean` (true if any of the hit landed on shield), `brokeShield: boolean` (true if the shield was reduced to zero by this hit). LSS line 14913-14915 selects sounds with the same logic.
- Client: at `last_ship_sailing_sim.html` line 2682, replace the snapshot-based guess with `ev.absorbedByShield ? 'damage_shield' : 'damage_hull'`. Add a third path for `brokeShield` to play a distinct "shield breaking" sound (LSS doesn't separate this currently but it's an obvious upgrade; ~10 extra lines).
- Server: ~10 lines. Client: ~5 lines (tag-driven) + optional ~30 lines for the new shield-break recipe.
- Dependencies: none.
- LSS reference: `playerTakeDamage` wrapper at line 14906-14916.

### NA29. Map preview thumbnails in lobby [CLIENT + ASSETS] **POLISH** (new feature)

Lobby currently shows loadout cards but no visual cue for which map you'll be playing on. Pre-rendered thumbnails (or a tiny live preview render) on the lobby panel.

- Either: pre-render a screenshot of each map (top-iso angle) once and ship as PNGs in `docs/LSS/assets/maps/`; or use the same minimap-style top-down Canvas 2D contour render at small size in lobby
- Show current/upcoming map name + thumbnail on the lobby panel
- Bonus: tiny rotation animation or shimmer to make it feel alive
- Client: ~80 lines (just the renderer or `<img>` swap on map change). Assets: ~9 PNGs at ~50 KB each.
- Dependencies: NA28 (minimap) shares the contour-rendering code if we go the dynamic route.

### NA30. Lobby tooltips for chassis [CLIENT] **POLISH** (new feature)

Hovering a chassis card in the lobby shows a tooltip with: chassis role description (e.g. "fast skirmisher; lock-on missiles + sonar utility"), each ability slot's name and a one-sentence summary, base health/shield/speed numbers. Currently nothing explains what each chassis does until you commit to one.

- Client: tooltip component (CSS popover keyed off hover); per-chassis content sourced from a new `CHASSIS_TOOLTIPS` table in the loadouts module (or read from the server's loadouts.ts and shipped over the wire on connect)
- Tooltip should also show on focus for keyboard navigation
- Client: ~120 lines (component + content table + styles).
- Dependencies: none.

### NA31. Per-map music tracks [CLIENT + ASSETS] **POLISH** (new feature)

We have a procedural ambient pad (phi-cascade) but no actual music. Each of the 9 maps could have a dedicated low-key track or stem set that fades in during warmup, intensifies during combat, and ducks for important audio.

- Either: ship MP3/OGG tracks (simplest; needs licensing or original composition); or extend the procedural audio module with longer-form generative tracks per map (in keeping with the existing procedural philosophy)
- Per-map theme + a "menu/lobby" theme; smooth crossfade between them
- Volume controlled by the music slider in NA21
- Client: ~80 lines for the music manager (load/play/crossfade/volume); plus content (~9 tracks; original procedural variants ~200 lines each).
- Dependencies: NA21 (audio bus + music slider).

### NA32. Spectator mode [SERVER + CLIENT] **POLISH** (new feature)

A player can connect as a spectator: not assigned to a team, no ship, watches matches in progress with a free-fly camera or by following players. Useful for: dev/streaming, late joiners waiting for next round, competitive viewing.

- Server: spectator role; player joins with `?spectator=1` URL param or via a lobby toggle; counted separately from team rosters; doesn't affect alive-counting or match-end conditions
- Client: alternate input scheme (free-fly WASD + mouse-look, or follow-player with Tab to cycle); HUD strips out personal HUD (no health/ammo) and shows team scores + a "spectating: PLAYER_NAME" overlay; can spectate alive or dead, switch targets freely
- Dropping spectator role and joining lobby works mid-match (you become a queued player for next round)
- Server: ~80 lines (role tracking + snapshot filtering). Client: ~250 lines (mode + HUD + free-fly cam + target cycling).
- Dependencies: none.

### NA33. Practice / tutorial mode [SERVER + CLIENT] **POLISH** (new feature; was previously out of scope)

Offline single-player mode for learning. Drops you into a sandbox map with bots configurable per-team; lets you test loadouts, abilities, weapons against passive or aggressive targets without affecting score or other players.

- Server: practice game mode flag; bots use simplified scripted behaviors (stand still, patrol, dodge, fight back); scoring disabled; round timer disabled or per-objective
- Client: dedicated "Practice" entry in the main menu (parallel to "Play"); in-mode UI for adjusting bot count/behavior + map; on-screen ability prompts that pulse for unused slots ("press Q to fire ability"); first-time player walkthrough overlay covering: movement, firing, ability use, reload, abilities (~6 bite-sized prompts dismissable each)
- Lighter-weight version: just a "training match" with all bots and no humans, no special UI; deeper version adds the tutorial prompts
- Server: ~150 lines (mode flag + simplified bot behaviors + scoring suppressor). Client: ~300 lines (mode UI + prompts + walkthrough overlay).
- Dependencies: NA5 (bot ability use) for varied bot behaviors; NA21 (settings menu) for the entry point.

### NA34. Text chat [SERVER + CLIENT] **POLISH** (new feature)

Per-team text chat during match (Tab + T or just T to open), all-chat in lobby/match-end. No DMs.

- Server: chat message routing (team-only during match, all-chat in lobby/scoreboard states); rate-limit per peer; basic profanity filter optional
- Client: chat overlay (bottom-left during play; centered in lobby); enter to send; persists last ~5 messages with fade
- Server: ~80 lines. Client: ~120 lines.
- Dependencies: none.

### NA35. Voice chat [SERVER + CLIENT] **DEFER**

Push-to-talk team voice. Significantly more complex than text chat (WebRTC peer connections or a media server) and needs moderation infrastructure.

- Either: WebRTC mesh between teammates (server brokers signaling, peers do P2P audio; cheap server-side, harder NAT/firewall traversal); or media server like mediasoup (server handles routing; more reliable, more infra cost)
- Client: PTT key, mic permission flow, per-peer volume sliders, mute-self/mute-other UI
- Server: WebRTC signaling endpoints OR full media server integration
- Server: ~300 lines (signaling) or external infra. Client: ~400 lines (WebRTC setup + audio routing + UI).
- Dependencies: NA21 (volume sliders), NA34 (chat structure useful for mute UI).
- **Defer.** Text chat first (NA34); voice is a major undertaking with privacy/moderation implications.

### NA36. Replay / kill-cam saves [SERVER + CLIENT] **DEFER**

Record matches as snapshot streams; play them back at variable speed, with full camera control. Killcam = replay last 3-5 seconds from killer's POV after a death.

- Server: optional snapshot recording mode (write all snapshots to a file or buffer keyed off match ID); for kill-cam, keep a rolling buffer of the last few seconds in memory and snapshot a chunk on each kill event
- Client: replay player UI (timeline scrubber, speed control, free-fly camera, follow-player toggle); kill-cam triggered on death with a 3-second rewind from killer's POV before the respawn timer
- Storage: replays are large (~2-5 MB per match at JSON; ~500 KB binary). Kill-cam buffer is ~500 KB in memory.
- Server: ~200 lines (recording + replay endpoints) + storage decisions. Client: ~400 lines (player UI + kill-cam overlay).
- Dependencies: NA26 (delta encoding makes recordings small enough to keep many).
- **Defer.** Nice to have, big lift, low priority before the core gameplay is polished.

### NA37. Persistent player identity [SERVER + CLIENT] **DEFER**

Player names that persist across sessions, optional clan tags, basic profile (favorite chassis, stats over time). Currently every connection gets a fresh anonymous peerId.

- Server: identity store (sqlite or even a JSON file); accounts via simple username+passphrase or magic link or anonymous-token cookies; name + clan tag fields; stats accumulate per peerId
- Client: name entry on first connect (saved to localStorage); display in lobby + scoreboard + kill feed
- Privacy: explicit "no email required" path; tokens are local-only unless user opts in
- Server: ~250 lines (identity routes + storage + token validation). Client: ~150 lines (name UI + token storage).
- Dependencies: none, but pairs with NA34 (text chat needs names).
- **Defer.** Anonymous peerId is fine for the LAN/early-stage period; revisit when going public or adding ranked.

### NA26. Snapshot delta encoding + binary wire format [SERVER + CLIENT] **POLISH** (defer until needed)

Current snapshot is full JSON every broadcast. At 64Hz with 6+ players + projectiles + world effects, this is roughly 50-100 KB/s per client. Fine for now; would matter past ~10 concurrent players or on cellular.

- Server: per-client baseline snapshot; only send fields that changed. Optionally pack as MessagePack or a custom binary layout.
- Server: ~150 lines. Client: ~100 lines.
- Dependencies: none. Defer.

### Estimates by priority

| Priority | Items | Lines | Sessions |
|---|---|---|---|
| CRITICAL | NA1, NA2, NA3, NA4, NA5 | ~760 | 2-3 |
| POLISH (gameplay) | NA6, NA7, NA8, NA9, NA10, NA11, NA12 | ~370 | 1-2 |
| POLISH (UX) | NA13-NA25, NA27-NA34, NA38 | ~2325 | 6-8 |
| Defer | NA26, NA35, NA36, NA37 | ~1100 | 3-4 (when picked up) |
| **Subtotal (active scope)** | | ~3455 | 9-13 |
| **Subtotal (incl. deferred)** | | **~4555** | **12-17** |

If LAN-only play is the target, NA2/NA3 can drop from CRITICAL to POLISH. The other three CRITICAL items (player-vs-player collision, hitscan, bot abilities) are gameplay holes regardless of network.

## Second sweep ; ability depth

The first sweep (v8.18-v8.27) shipped structural ability dispatch; every Q/E/F/V press fires, cooldowns tick, projectiles spawn, basic buffs apply. Many things got `// SIMPLIFIED:` markers in the code. The second sweep restores the depth those markers point at.

### S1. TRACKER depth [SERVER + CLIENT]

- **Lock-on system:** `player.trackerLocks` map (botId → 0/1/2/3) populated by Sonar Lock cone-cast. Persists between activations until used or target dies.
- **Tracker Rockets homing:** when fully-locked targets exist, fire 5 missiles per target with `homingTargetId`; per-tick steering correction in `_tickProjectiles`. Partial locks preserved on misfire.
- **Particle Wall as deployable:** spawn a particle_wall worldEffect in front of player with 5000 HP, 10s timer. Projectiles passing within wall plane deduct HP; wall destroyed at 0.
- **Salvo Core remote-guidance:** during the 3s window, spawn 1 missile per (dt × 10) chance with `salvoGuided` flag; per-tick steers each toward player's current crosshair aim point. Requires player.aim to ship in input.
- **Visuals:** 1/2/3 lock indicator rings above enemies; missile contrails; particle wall translucent plane.
- **Audio:** missile launch swoosh per rocket (have generic salvo); lock acquisition tone per stack.
- LSS refs: 8633-8665 (rockets), 8780-8806 (wall), 8904-8926 (sonar), 9044-9054 + 9511-9521 (core).
- Estimate: ~250 server, ~200 client.

### S2. PUNCTURE depth [SERVER + CLIENT]

- **Cluster Missile sustained zone:** on impact, spawn a 5s incendiary worldEffect at hit point with 500 DPS over 3-second cluster duration (LSS line 8619-8621 `clusterDmg=500, clusterDuration=5`).
- **Tether Trap rooting:** in addition to slow, immobilize first enemy that enters for 4 seconds (LSS rootDuration). Reset velocity to zero per tick during root window.
- **Afterburner Core ongoing barrage:** spawn 1 rocket per ~0.4s during the 5s duration (currently a single 8-rocket burst at activation).
- **Visuals:** cluster impact splash, tether tendrils between mine and rooted enemy, afterburner blue flame trail.
- LSS refs: 8615-8623, 8890-8902, 9020-9055.
- Estimate: ~150 server, ~150 client.

### S3. SLAYER depth [SERVER + CLIENT]

- **Sword Block fire-lock:** while slot 1 is active, gate the regular fire path so player can't shoot (LSS comment "can't shoot"). Currently no restriction.
- **Arc Wave wall destruction:** Arc Wave projectile destroys Particle Walls and Gun Shield worldEffects on contact (LSS line 8807).
- **Arc Wave slow-on-hit:** apply a 1-second slow status (velocity damp) to hit targets.
- **Sword Core periodic arc waves:** spawn an arc-wave projectile every 0.5s during the 5s duration, in addition to buffing damage.
- **Visuals:** arc wave electric trail, sword block aura, sword core ring.
- LSS refs: 4368 (block), 8624-8631 (arc wave), 9008-9020 (core).
- Estimate: ~100 server, ~100 client.

### S4. VORTEX depth [SERVER + CLIENT]

- **Vortex Shield projectile reflection:** while held, projectiles within reflection cone are bounced back at original speed but with shooter's team flipped to player's team (so the bounced shot can hit the original shooter). Currently shield just reduces damage.
- **Trip Wire as cluster:** drop 3-5 mines in a small spread (LSS spawns multiple), not a single one.
- **Laser Core continuous beam:** spawn a continuous beam projectile/worldEffect for the 4s duration that deals 200 DPS to anything in line (rather than buffing regular fire).
- **Visuals:** shield bubble with rainbow shimmer; visible beam mesh.
- **Audio:** vortex shield hum (loop); laser beam tone.
- LSS refs: 9091-9118 (shield), 8845-8870 (trip wire), 8995-9008 (core).
- Estimate: ~150 server, ~150 client.

### S5. PYRO depth [SERVER + CLIENT]

- **Thermal Shield power pool:** drain `player.thermalShieldHP` (max 2500) while held; out-of-pool forces drop. Pool regenerates over 10s out of use. (LSS line 1187, 7656-7677.)
- **Thermal Shield burn-on-touch:** while held, deal 200 DPS to enemies within 250u of player.
- **Firewall persistent flame visual:** sprite-sheet flame instead of solid box; ember layer below.
- **Incendiary Trap delayed arm:** 1s arming delay before damage starts.
- **Flame Core wave:** AoE expands over the 2s duration (radius growing from 200 → 800) instead of static sphere.
- **Visuals:** flame sprites, smoke, fire trails, distortion shader.
- **Audio:** thermal hum, flame whoosh, ignite ping.
- LSS refs: 8800-8870 (firewall), 8772-8780 (thermal), 8870-8902 (trap), 9020-9050 (core).
- Estimate: ~250 server, ~250 client.

### S6. BLASTER depth [SERVER + CLIENT]

- **Spinup mechanic:** `player.spinupTimer`, `player.spunUp`. While trigger held, spinupTimer increases by dt; once it reaches `weapon.spinup` (1.2s for BLASTER), `spunUp=true` and fire is unlocked. Released trigger drains spinup at 2x rate. Gates fire path on `spunUp` for chassis with `weapon.spinup > 0`.
- **Mode Switch actual stat swap:** `player.blasterMode` ('close' | 'long') with two weapon stat profiles. Close = high spread, fast fire, short range; Long = tight spread, slower fire, long range. 1s transition lockout (`player.blasterSwitchTimer`).
- **Power Shot 1s charge:** activation starts a charge timer; fire only on completion. Cancellable by death or stasis.
- **Gun Shield directional + HP-based:** directional cone in front of player, 2500 HP that absorbs incoming damage, can be destroyed by Arc Wave.
- **Smart Core auto-aim:** during 8s duration, server picks nearest enemy and auto-aims fire at them; +20% damage.
- **Visuals:** charge bar, mode-switch transition, gun shield mesh, smart core target lock indicator.
- LSS refs: 8085-8090 (spinup), 8927-8931 (mode), 8630-8670 (power shot), 8762-8767 (gun shield), 9522-9540 (smart core).
- Estimate: ~200 server, ~150 client.

### S7. SYPHON depth [SERVER + CLIENT]

- **Energy Siphon arc-slow timer:** drained enemies get `arcSlowTimer = 2.0`; per-tick velocity damping while > 0.
- **Upgrade Core 3 tiers:** Tier 1 (Arc Rounds: +50% vs shields, +10 ammo), Tier 2 (Maelstrom: +500 maxShield, faster cooldowns), Tier 3 (XO-16 Accelerator: +25% damage, faster fire). Currently stacks all three.
- **Rearm visual + audio flash:** brief golden ring + ascending tone on press.
- **Visuals:** lightning bolt mesh from player to siphoned target (with branching), drain particles, upgrade aura per tier.
- **Audio:** electric zap (siphon), rearm chime, tier-up tone.
- LSS refs: 8672-8680 (salvo), 8687-8755 (siphon), 8932 (rearm), 9059-9082 (core).
- Estimate: ~150 server, ~200 client.

### S8. Cross-ability interactions [SERVER]

- **Arc Wave destroys Particle Wall + Gun Shield** (LSS line 4732-4733).
- **Energy Siphon vs Vortex Shield:** if target has Vortex Shield active, siphon is blocked (or reflects?). Decide and implement.
- **Doomed-state ability lockout:** some abilities should be unavailable when doomed (LSS doesn't do this exactly, but it's a sensible balance lever).
- **Ability press during reload / stasis / death:** standardize the gating so unintended presses don't fire.
- Estimate: ~100 server.

## Third sweep ; balance & polish

After abilities have proper depth, this is the polish that makes it feel like LSS:

- **Stat tuning** ; damage, fireRate, cooldowns, durations against LSS values. Currently we use LSS values, but the simplified behaviors mean things feel different. Pass to re-tune.
- **Spawn protection scaling per chassis** ; LSS uses 3s flat; could tune per chassis (Frigates faster respawn, Dreadnoughts longer protection).
- **Friendly fire toggle** ; currently no FF. Add config flag.
- **Anti-camping spawn logic** ; currently random pool. Choose spawn farthest from current enemies.
- **Ammo scaling for cores** ; some cores grant infinite ammo (LSS Smart Core); we don't model "infinite" yet.
- **Visual polish per ability:** dynamic lights from explosions/lasers/electric, screen-space fire haze, ability VFX intensity.
- **Audio polish per ability:** unique recipes for dash, ability, core, death, reload, mode-switch, charge, lock-acquired.
- **Cinematic transitions:** 3-2-1 launch countdown, FIGHT banner on warmup→playing, ROUND OVER banner with score breakdown, VICTORY/DEFEAT with team color (current banners are minimal).
- **Mid-match scoreboard (Tab):** kills/deaths/damage/streaks per player.
- **Match-end scoreboard:** detailed per-player stats with kill streaks + best ability + most damage.
- **Per-loadout fireRate-aware audio throttle:** currently `_LOADOUT_AUDIO` table mirrors LSS but spinup/mode-switch will need updates.
- **Reconnection on WS drop:** automatically reconnect, reapply loadout, rejoin lobby.
- **Ping display + lag indicator** for the player.
- **Map-load spinner** between rounds (currently stutters on map switch).

## Things missed in the first pass (smaller items)

These are gaps I noticed while shipping that didn't fit any major category:

- **Reload key (R):** LSS supports manual reload in addition to auto. Currently auto-only.
- **Cockpit frame swap on loadout change:** loadout change should swap the cockpit PNG; currently might stick with the first one picked.
- **Lobby teammates strip:** LSS has a strip showing other connected players' selected ships.
- **Per-loadout ammo arc max:** ammo arc uses generic max; should read player.maxClip.
- **Round-start audio cue:** `round_start` recipe exists but not all transition paths trigger it.
- **Bot loadout balance:** server picks bot loadouts in a fixed order; might want randomization.
- **Per-loadout hullLength for collision sphere:** PLAYER_RADIUS=60 is constant; LSS uses chassis.hullLength * 0.5 (40-70 range).
- **Bot fire spread per weapon:** all bots use same fire spread; LSS varies by weapon.mode.
- **Spawn protection skip on respawn-without-kill:** if player respawns from a round transition (not a kill), skip the protection? (LSS gives it always; probably fine.)
- **Server tick rate mismatch with LSS:** LSS originally targeted 60Hz; we run 64Hz. Probably fine but worth noting.
- **Snapshot field name `worldEffects` vs LSS's `world_effects`:** harmless but inconsistent if anything ever bridges.
- **Match seed handling:** server picks `Math.random() * 0xFFFFFFFF` as seed but doesn't use it for anything yet. LSS uses the seed for deterministic obstacle placement; we don't have obstacles yet.
- **Spawn-camp prevention:** currently random pool from team's spawnA/spawnB. LSS prefers spawns far from current enemies.

## Out of scope (for this port)

- Multi-region servers
- Matchmaking / ranked / leaderboards (depends on NA37 persistent identity)
- Cosmetics / unlocks
- Multi-language UI / localization
- Mobile touch controls
- Achievements / badges

(Tutorial mode is no longer out of scope; see NA33. Voice chat, replay/kill-cam, and persistent identity are in-scope but **deferred** ; see NA35-NA37.)

These can be added later but aren't part of "feature parity with LSS."

## Revision history

- 2026-04-26 v1.3: shipped NA21 full settings menu (v8.57). Esc opens overlay with 5 tabs (Gamepad / Mouse-Keys / Audio / Graphics / Match); live-editable sliders + checkboxes + click-to-rebind for gamepad buttons; localStorage persistence under `lss_settings_v1`; boot-time apply so saved settings take effect immediately. Audio module gained per-bus volume scalars and mute-on-tab-out. Graphics tab includes FOV slider, particle density, camera shake scale, minimap/ping toggles. Match tab has Return-to-Lobby + Quit-Server actions. Status: 25 non-ability gaps closed. Remaining: NA2/NA3 (snapshot interpolation + client-side prediction; only matters for WAN), NA13 reconnection, NA14 audio Doppler/occlusion, NA29-NA34 (lobby thumbs/tooltips/music/spectator/practice/text-chat). PLAN at v1.3.
- 2026-04-26 v1.2: shipped NA5 bot ability use (v8.54), NA9 splash damage helper (v8.55), NA6 bot pathfinding + dodging (v8.56). Bots now use offensive/defensive/core abilities per loadout (VORTEX hitscan + laser core damage buff, PYRO firewall + flame core AoE, PUNCTURE cluster missile + afterburner, SLAYER arc wave + sword core, TRACKER 3-shot rocket fan + particle wall + salvo core, BLASTER power shot + smart core, SYPHON 5-rocket salvo + siphon hitscan + upgrade core); held-shield damage reduction now applies to bots; bot regular fire scales with coreDamageMult/coreFireRateMult. _applySplashDamage helper added with linear/flat falloff + friendly-fire opt-in. Bots probe 250u ahead via SDF and pick perpendicular alternatives at blocked walls; projectile dodge scans enemy projectiles within 1500u and sidesteps perpendicular to incoming. Status: 24 non-ability gaps closed cumulatively. Remaining critical: NA2/NA3 (snapshot interpolation + client-side prediction). Remaining polish: NA13 reconnection, NA14 audio Doppler/occlusion, NA21 settings menu, NA29-NA34. PLAN at v1.3.
- 2026-04-26 v1.1: shipped NA4 hitscan path + beam visuals (v8.51), NA27 engine boosters (v8.52), NA28 minimap (v8.53). Discovered NA20 lobby teammates strip already shipped (left/right team panels show each peer's loadout + ready state, just different layout from LSS's bottom strip). Status: 4 more non-ability gaps closed. Cumulative: 21 non-ability gaps closed across v8.35-v8.53. VORTEX Laser-Shot now uses real hitscan (walls block, beam visual fades over 150ms). Booster trails attached to all ships (per-chassis palette, length+opacity scale with speed). Minimap top-left shows rooms, tunnels, world effects, allies, enemies (in sensor range), self. Remaining critical: NA2/NA3 (snapshot interpolation + client-side prediction), NA5 (bot ability use). Remaining polish: NA6 bot pathfinding, NA9 splash damage system, NA13 reconnection, NA14 audio Doppler/occlusion, NA21 settings menu, NA29-NA34. PLAN at v1.2.
- 2026-04-26 v1.0: shipped NA1 player-vs-player collision (v8.45), NA16 finish: banking + own-fire shake (v8.46), NA12 match seed deterministic placement (v8.47), NA18 per-chassis crosshair variants (v8.48), NA23 ping indicator (v8.49). Discovered NA19 mid-match Tab scoreboard was already shipped (Tab keybind + #scoreboard overlay live since earlier work; just not previously documented). Status: 5 more non-ability gaps closed. Cumulative: 17 non-ability gaps closed across v8.35-v8.49 (NA7, NA8, NA10, NA11, NA12, NA15, NA16, NA17, NA18, NA19, NA22, NA23, NA24, NA25, NA38, NA1, plus universal dash). Remaining critical: NA2/NA3 (snapshot interpolation + client-side prediction), NA4 (hitscan path), NA5 (bot ability use). Remaining polish: NA6 bot pathfinding, NA9 splash damage system, NA13 reconnection, NA14 audio Doppler/occlusion, NA20 lobby teammates strip, NA21 settings menu, NA27 boosters, NA28 minimap, NA29-NA34. PLAN promoted to v1.0.
- 2026-04-26 v0.9: shipped v8.44 universal dash system ; ports LSS line 9898-9914 (dash function) + 7916-7932 (dash duration tick + charge regen). Per-chassis charges (Frigate 3 / Corvette 2 / Dreadnought 1) consumed on Shift, dash burst in current movement (or facing) direction at chassis.dashSpeed for dashDuration, charges regen one at a time over dashCooldown. Server: PlayerInput.dash; Player.dashCharges/maxDashes/dashSpeed/dashDuration/dashCooldown/dashActive/dashTimer/dashCooldownTimer; per-tick edge detection + duration tick + cooldown regen + max-speed cap during dash + refill on respawn; gated to playing state. Snapshot ships dashCharges + maxDashes + dashActive. Client: Shift keybind, gamepad A button, pendingDash one-shot, dash pip HUD bottom-left (full = available, charging glow = leading regen pip). SLAYER Phase Dash (slot 2 ability, instant teleport 700u) kept separate as a stronger ability-on-cooldown variant. Adds the missing universal dash gap.
- 2026-04-26 v0.8: shipped NA38 (v8.35), NA22 (v8.36), NA24 + NA25 (v8.37), NA11 (v8.38), NA8 (v8.39), NA10 (v8.40), NA16 partial: FOV-on-boost (v8.41), NA17 death cam + respawn timer (v8.42), NA7 per-chassis hull radius (v8.43). Discovered NA15 (engine pitch shift with speed) was already implemented as `_audio.setEngineSpeed(speed/maxSpeed)` at client line 3375 ; pre-existing, just not previously documented as done. Status: 10 non-ability gaps closed in this batch, ~700 lines added across server + client. Remaining critical: NA1 (player-vs-player collision), NA2/NA3 (snapshot interpolation + client-side prediction; gate on whether WAN play is the target), NA4 (hitscan path), NA5 (bot ability use). Remaining polish: NA6 bot pathfinding, NA9 splash damage system, NA12 match seed used, NA13 reconnection, NA14 audio Doppler/occlusion, NA16 banking + own-fire shake (FOV done), NA18 crosshair variants, NA19 mid-match Tab scoreboard, NA20 lobby teammates strip, NA21 settings menu, NA23 ping indicator, NA27 boosters, NA28 minimap, NA29-NA34 (lobby thumbs, tooltips, music, spectator, practice, text chat). Deferred: NA26, NA35, NA36, NA37.
- 2026-04-26 v0.7: added NA38 (server-tagged shield-vs-hull hit SFX) ; LSS at line 14913-14915 plays distinct sounds (`damage_shield` crystalline crack vs `damage` dissonance); our client recipes exist but the wire-up at line 2682 of last_ship_sailing_sim.html approximates from snapshot shield value instead of using server tagging. Fix is server emits `absorbedByShield` + optional `brokeShield` on hit events; client picks recipe deterministically. Made the "LSS is the canonical source" rule explicit in the Files section header (every feature claim cross-checked against LSS line numbers before claiming "done").
- 2026-04-26 v0.6: added NA29 (lobby map preview thumbnails), NA30 (lobby chassis tooltips), NA31 (per-map music tracks), NA32 (spectator mode), NA33 (practice/tutorial mode; moved out of "Out of scope"), NA34 (text chat), NA35 (voice chat; deferred), NA36 (replay / kill-cam saves; deferred), NA37 (persistent player identity; deferred). Refreshed Out of scope to reflect the moves. Estimates table now distinguishes active scope (~3410 lines) from deferred (~1100 lines).
- 2026-04-26 v0.5: expanded NA21 from "gamepad settings UI" to a full settings menu (gamepad, keyboard+mouse, audio, graphics, match: exit/quit-to-main; persistent in localStorage; accessible from lobby and Esc-pause). Added NA28 (minimap) as a new feature gap (top-down Canvas 2D overlay with teammates, enemies-in-sensor, key projectiles, world effects, destructibles).
- 2026-04-26 v0.4: added Visual identity per chassis and ability section mapping the eight effects in `effects_demo.html` to specific weapons/abilities; locked Ashman's [USER] mappings (VORTEX/PYRO bloom, TRACKER fresnel, SLAYER particle burst, VORTEX beams, all-ship energy shields with VORTEX/PYRO half-shell variants, BLASTER gun-shield + TRACKER particle-wall as hologram, SLAYER + SYPHON lightning thick/thin variants, boosters as short volumetric beams). Filled remaining ability gaps as [PROPOSED]. Added per-chassis primary palette table. Added NA27 (engine boosters / thrust visualization) as a new feature gap pairing with NA15/NA16 for movement feel.
- 2026-04-26 v0.3: added Non-ability gaps section (NA1-NA26: physics, networking, bot AI, audio, HUD, polish) ; the gaps the first six phases didn't address. Updated server + client status to reflect v8.28-v8.34 (BLASTER spinup, stasis, destructibles, gamepad, match-end scoreboard, cinematics, reload key, gamepad fire-stuck fix). Refreshed Estimates table with three remaining phases (7: non-ability gaps, 8: second sweep, 9: third sweep). Project is ~45% complete by line estimate.
- 2026-04-26 v0.2: added Second sweep (S1-S8), Third sweep (balance/polish), Things missed in first pass. Updated server + client status to reflect v8.18-v8.27. Document is the source of truth for what's done; reflects the simplified-first / depth-second strategy.
- 2026-04-26 v0.1: initial plan written.
