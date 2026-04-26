# LSS Server-Sim Port Plan

Created: 2026-04-26
Last updated: 2026-04-26
Version: 0.2

The plan for finishing the thin-client + server-authoritative port of Last Ship Sailing.

This document is the canonical reference for what's done, what's left, what order to do it in, and what each port involves. Update it as work lands.

## Architecture commitment

We're building a **thin-client + server-authoritative** version of LSS:

- **Server** (`server-sim/`): authoritative simulation in TypeScript, runs on Bun. Owns all gameplay state (positions, HP, projectiles, hits, abilities, match state, bot AI). Sends 64Hz snapshots to clients.
- **Client** (`last_ship_sailing_sim.html`): thin client built from scratch. Renders snapshots; sends inputs. No local sim.

Why this path: code we control, anti-cheat by construction, swappable client (mobile/console possible later), server can run in any language. The trade-off is more upfront work than a P2P or relay model. Estimated remaining ~4000-5000 lines across server and client. The user is committed to this path.

## Files

- `last_ship_sailing.html` ; the original LSS, untouched, used as the source for porting features.
- `last_ship_sailing_sim.html` ; the thin client we're building. Currently at v8.16.
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
- Match state machine: select / warmup / playing / roundEnd
- Hit/kill events with position + shooter
- Fire events for networked audio
- 4 abilities: SLAYER Phase Dash, PUNCTURE Afterburner, TRACKER kit (Q/E/F/V; simplified ; no homing/lock/walls/remote-guidance)

Not done:
- 24 remaining abilities (full kits for VORTEX, PYRO, BLASTER, SYPHON; remaining for PUNCTURE, SLAYER)
- Reload + clip ammo system
- Spinup mechanic (BLASTER)
- BLASTER mode switch (close/long)
- Doomed state + tremor
- Spawn protection
- Score tracking + round-win conditions
- Match-end transition
- Destructibles (cluster obstacles, debris)
- World effects (firewalls, trip wires, tethers, traps, gas)
- Stasis fields
- Lock-on system (TRACKER homing)
- Particle Wall as deployable entity (currently a buff)
- Salvo Core remote-guided missiles
- Friendly fire toggle (currently no FF)
- Spawn protection invulnerability window

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

Not done:
- Particles for almost everything (impact sparks, explosions, shield hits, debris, electric arcs, fire trails, organic flora)
- Kill feed (text rolling at top)
- Damage indicator (red flash from direction of attacker)
- Damage vignette (red ring at low HP)
- Doomed flash (HUD pulse)
- Camera shake (on hits, explosions, dashes)
- Tremor effect (low-HP wobble)
- Spawn protection visual (translucent bubble)
- Reload UI (timer bar)
- Spinup UI (charge indicator)
- Ammo display (clip count)
- Speed arc HUD layer
- Ammo arc HUD layer
- Ability cooldown rings on Q/E/F/V slots
- Per-chassis health segment counts (3/5/7)
- Round-start countdown overlay
- ROUND OVER banner
- VICTORY banner with winner color
- Match-end scoreboard with damage/kills/streaks
- Settings panel + persistence
- Gamepad input + remap
- Match-stats screen
- Teammates strip (lobby)

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

The bedrock first, then combat depth, then polish.

**Phase 1 ; foundation:** #1 (score), #2 (round/match banners), #3 (reload), #5 (doomed), #6 (spawn protection). Without these, the match flow doesn't really work. ~600 lines total.

**Phase 2 ; combat feel:** #7 (particles), #8 (camera shake / damage indicator), #9 (kill feed), #10 (HUD layers). Makes hits and damage feel right. ~800 lines total.

**Phase 3 ; world effects framework:** #15. Foundation for the rest of the abilities. ~350 lines.

**Phase 4 ; ability kits:** #11, #12, #13, #14, #18, #19. One chassis at a time, each ~250-450 lines. ~2000 lines total. Each chassis is a self-contained batch.

**Phase 5 ; stasis + destructibles + spinup/modes:** #4, #16, #17. ~700 lines total.

**Phase 6 ; input + polish:** #20 (gamepad), #21 (match-end scoreboard). ~500 lines total.

## Estimates

| Phase | Lines | Sessions (rough) |
|---|---|---|
| 1 | 600 | 1 |
| 2 | 800 | 1-2 |
| 3 | 350 | 1 |
| 4 | 2000 | 3-5 |
| 5 | 700 | 1 |
| 6 | 500 | 1 |
| **Total** | **~5000** | **8-11** |

## Risks

- **Edge-case porting bugs.** Each LSS feature has hidden flags and side-effects we'll discover as we go. Mitigate by porting one item at a time and testing.
- **Snapshot bandwidth growth.** As we add worldEffects, destructibles, particle data, snapshot size grows. We may need delta encoding eventually. Not a near-term issue.
- **Visual fidelity drift.** Our particle / shader work may not match LSS's exactly. Acceptable; close-enough is fine.
- **Per-chassis stat tuning.** LSS values are fine-tuned over many iterations; ours are copies. Should be OK but might feel different in practice.

## Out of scope (for this port)

- Multi-region servers
- Matchmaking / ranked / leaderboards
- Cosmetics / unlocks
- Tutorial mode
- Multi-language UI

These can be added later but aren't part of "feature parity with LSS."

## Revision history

- 2026-04-26 v0.1: initial plan written.
