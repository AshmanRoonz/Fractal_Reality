# Last Ship Sailing, Godot Port: Take-Over Plan

Written after reading every GDScript in `godot/scripts/` and surveying the web build. This is the read-and-plan pass; no code has been changed yet.

## 1. What's here, script by script

| File | Lines | Role | Verdict |
|---|---|---|---|
| `game_data.gd` | 473 | Data layer: chassis, loadouts, ships, map definition, signatures, input map | Solid. Clean `RefCounted` with static methods. The one place to edit when content changes. |
| `main.gd` | 875 | Match director: env build, spawn, round state machine, projectile physics, ability effects, hit detection, tracer routing | Fragile by volume. Logic is correct; the problem is that six concerns live in one file. |
| `player_ship.gd` | 599 | First-person ship controller: movement, camera, abilities, loadout cycling, state timers, Monarch/Legion upgrades | Fragile by duplication. Shares ~90% of its body with `enemy_ship.gd`. |
| `enemy_ship.gd` | 510 | AI ship controller: same state machine as player plus orbit/retreat/advance AI and per-loadout decision switch | Fragile by duplication. Every bug fix has to be written twice. |
| `arena_map.gd` | 496 | SDF-based Nexus geometry: chamber spheres, tunnel capsules, `contains_point`, `constrain_point`, `raycast_wall`, navigation waypoints, spawn points | Solid. Self-contained and already exercised every physics tick by both ship scripts. |
| `ship_visuals.gd` | 431 | GLB importer with procedural box-hull fallback, engine plumes (GPUParticles3D), shield mesh, muzzle flash particles and light | Solid. The import pipeline (bbox + scale-to-length + face flip) is careful; fallback hull is per-chassis. |
| `tracer_pool.gd` | 86 | GPU-instanced tracer segments via `MultiMeshInstance3D` with per-instance color alpha for lifetime fade | Solid. Exactly the right pattern for this effect. |
| `hud.gd` | 21 | Trivial `CanvasLayer` wrapper around `HUDOverlay` | Thin shim. Fine, but provides no value a direct parent wouldn't. |
| `hud_overlay.gd` | 540 | The entire presentation layer: circumpunct reticle, health/shield/ammo arcs, minimap, cockpit guns, enemy markers, round banner, corner panels | Works, but brittle. One 540-line `_draw()` call with no component boundaries. Adding scoreboard / kill feed / post-round card will be painful without a pass. |
| `target_drone.gd` | 121 | `StaticBody3D` target dummy from the pre-round-loop sandbox era | **Dead code.** `main.gd` spawns three `EnemyShip` instances now; `TargetDrone` is never instantiated. Safe to delete. |

Two quick counts for context:
- Abilities in the data layer: 21 total across seven loadouts.
- Abilities with explicit effect implementations in `main.gd`: 13. The other eight (`vortex_shield`, `thermal_shield`, `afterburner`, `sword_block`, `phase_dash`, `gun_shield`, `mode_switch`, `rearm`) are handled ship-side via state timers; that is correct by design, not a gap.
- Cores: 7 total. Three projectile-emitting cores (`laser_core`, `flame_core`, `salvo_core`) live in `main.gd`; four state-buff cores (`afterburner_core`, `sword_core`, `smart_core`, `upgrade_core`) live ship-side. Same pattern as abilities.

## 2. Dependency graph

```
project.godot
  ↳ Main.tscn
      ↳ main.gd
          ├─ game_data.gd
          ├─ arena_map.gd
          ├─ player_ship.gd ───── ship_visuals.gd ─── game_data.gd
          │                                        └─ (arena_map.gd)
          ├─ enemy_ship.gd  ──── ship_visuals.gd
          │       └─ player_ship.gd (for TEAM constants only)
          ├─ hud.gd
          │       └─ hud_overlay.gd ── game_data.gd, player_ship.gd, arena_map.gd
          └─ tracer_pool.gd

  (not instantiated by anyone: target_drone.gd)
```

The only awkward edge is `enemy_ship.gd` preloading `player_ship.gd` just to read team constants. A `BaseShip` (see §4.1) cleans that up.

## 3. Validation status

- Linux headless run with `--quit-after 2`: project parses, no script errors surfaced.
- Windows Vulkan run (from `render-run.log`): real render, NVIDIA RTX 5050 Laptop GPU. Non-fatal warnings only (unrecognized gamepad mapping fields, CA cert lookup).
- Combat slice (`combat-run.log`): ships spawn, round timer advances, hits and abilities fire, round end and match end trigger.

The foundation is not mock. The scripts compile, load their GLBs, run their SDFs, and play a round.

## 4. Ordered next steps

Priority is ordered so each step unlocks the next and falsifiable checkpoints exist at every step.

### 4.1 Extract `BaseShip` (deduplication pass)

**Why first.** `player_ship.gd` and `enemy_ship.gd` share the state-timer map, Monarch upgrade logic, Legion mode toggle, damage application, clip/reload, ability cooldown arrays, core meter rules, and boundary clamping. Every gameplay change has to be written twice today. Do this before adding anything new.

**What moves.** Create `scripts/base_ship.gd` as `class_name BaseShip extends Node3D`. Pull in: chassis/loadout storage, health/shield state, dash charges, state timers dict, ability cooldown array, core meter, `apply_damage`, `_apply_monarch_upgrade`, `_toggle_legion_mode`, `is_state_active`, `get_forward`, boundary clamping via `ArenaMap`. Keep `player_ship.gd` for: camera hierarchy, mouse look, input polling, FOV/shake/recoil feedback. Keep `enemy_ship.gd` for: AI decision loop, navigation target picking, per-loadout `_run_combat_decisions` switch, `_should_use_core`, core-meter regen rule.

**Falsifiable checkpoint.** After extraction, `player_ship.gd` + `enemy_ship.gd` combined should be ~60% of the current line count, with zero duplicated method bodies. The refactor is wrong if either subclass still contains full copies of shared functions.

**Risk.** Low. Pure refactor; no behavior change. Regress by running the combat slice and confirming same damage numbers, same ability behavior, same round pacing.

### 4.2 Split ability effects and projectiles into dedicated resources/nodes

**Why second.** `main.gd` is 875 lines because it owns the fire router, the projectile integrator, and every ability effect implementation. Adding new content or rebalancing existing content requires editing this monolith. A `Projectile` base class and an `AbilityEffect` dispatcher lets `main.gd` become a thin orchestrator.

**What moves.** Create `scripts/projectiles/projectile.gd` with a common interface (position, velocity, lifetime, damage, owner team, on-hit callback). Subclass for `BulletProjectile`, `HomingMissile`, `ArcWave`, `ClusterMissile`, `TetherTrap`, etc. Each projectile owns its own `MeshInstance3D` and its own ticking; `main.gd` just calls `add_child` on a spawn. Create `scripts/abilities/ability_effect.gd` as a dispatcher: `AbilityEffect.trigger(ability_id, emitter, loadout_data, world_ctx)`. Move the ability switch block into a lookup table over small effect scripts.

**Falsifiable checkpoint.** Adding a new ability should require: one new file in `scripts/abilities/`, one entry in `game_data.gd`. Zero edits to `main.gd`. If `main.gd` has to change, the dispatcher is in the wrong place.

**Risk.** Medium. Projectile node classes are a real behavior boundary; watch for ordering bugs (who ticks when, who resolves hits when).

### 4.3 Port one additional map

**Why third.** The web build has The Nexus and nothing else in Godot yet. Porting a second map is the cheapest way to validate that `arena_map.gd`'s SDF approach generalizes without the current geometry being hard-coded into the script. If adding a map requires editing `arena_map.gd`, the map format is wrong.

**What moves.** Move room/tunnel definitions out of inline dictionaries in `main.gd`'s map dict and into standalone `.tres` resources that `arena_map.gd` consumes. Pick one web-build map (Rift or Ember, whichever is simplest in geometry) and port it as a second `.tres`.

**Falsifiable checkpoint.** The second map loads, spawns, and the AI navigates it without any change to `arena_map.gd` itself. If the AI gets stuck or the ships clip walls, the SDF primitive set needs more shapes (boxes, half-spaces); add them to `arena_map.gd` and retry.

**Risk.** Low-medium. The SDF primitive set is currently spheres + capsules. Complex geometry might need boxes or implicit-CSG additions.

### 4.4 Port audio

**Why fourth.** No audio in Godot yet. Every combat test feels dead. With a real `BaseShip` (step 1) and real ability classes (step 2), wiring audio is a clean add: a bus layout in project settings, `AudioStreamPlayer3D` attachments on ships/projectiles, bus routing per category (engine, weapon, impact, ability, core, UI).

**What moves.** `godot/audio/` with subdirs matching web-build categories. A small `SoundBank` resource for per-loadout lookups (ion fires laser; scorch fires flame). Ship engines pitch-shifted by speed ratio. Weapon audio on `primary_fired`. Impact SFX on hit.

**Falsifiable checkpoint.** Blindfold the screen. Firing, reloading, dashing, ability activation, core activation, hits, and shield-break should each be identifiable by sound alone.

**Risk.** Low. Godot's bus system is clean; the main work is asset sourcing / porting from the web build.

### 4.5 Scoreboard, kill feed, post-round presentation

**Why fifth.** `hud_overlay.gd` is a 540-line `_draw()` today. Before stacking more UI on it, split it into components: `ReticleLayer`, `MinimapLayer`, `RoundBannerLayer`, `EnemyMarkerLayer`, `CockpitGunsLayer`. Then add `ScoreboardLayer` (Tab-held overlay) and `KillFeedLayer` (scrolling top-right) and `PostRoundCard` (spawns on `round_ended`).

**What moves.** Each layer becomes its own `Control` with its own `_draw()`. `HUDOverlay` becomes a coordinator that owns the layer list and passes state down. The giant `_draw` disappears; each layer is 50-100 lines.

**Falsifiable checkpoint.** Every HUD element can be individually disabled by toggling one layer's `visible`. Currently this is impossible without ripping pieces out of `_draw`.

**Risk.** Low. Pure UI refactor.

### 4.6 Netcode decision (the big deliberate step)

**Why last.** Only makes sense once 4.1-4.5 are done. Netcode on fragile systems produces fragile multiplayer. The web build uses a WebRTC-mesh client-authority model with 64-byte state packets and foveated refresh; that model has specific assumptions (everyone is a client, trust-but-verify hit voting) that must be decided, not ported by reflex.

**What to decide first.**
- ENet (simpler, server-authority) vs WebRTC (browser-compatible, P2P) vs Steam sockets (matchmaking built in).
- Client authority with consensus voting (web build's approach) vs server-authority snapshot interpolation (standard FPS approach).
- Snapshot rate, prediction/rollback, who-resolves-hits.

**What moves.** A separate `network/` directory. `Ship` nodes grow a `is_network_authority` flag (Godot's multiplayer API term). Input gets split into local-apply-immediately vs send-to-authority. Projectiles become network-owned; authority spawns, peers simulate.

**Falsifiable checkpoint.** Two Godot instances on LAN sync player positions within 100ms of each other, no desync > 3m after 30 seconds of uninterrupted play. One client quitting does not freeze the other.

**Risk.** High. Every netcode implementation has edge cases. Accept this step will take weeks, not days.

## 5. Smaller tasks that can slot in anywhere

- **Delete `target_drone.gd`.** Dead code. Five-minute task; do it whenever.
- **Promote `hud.gd` to a real class or delete it.** It's a 21-line passthrough. Either add value (owns scoreboard/kill feed orchestration) or remove the indirection.
- **Break the `enemy_ship.gd` → `player_ship.gd` preload.** Currently only used for `TEAM_PLAYER` / `TEAM_ENEMY` constants; move those to `game_data.gd`. One-line fix; removes the cross-subclass dependency.
- **Document the signals in `main.gd`.** `primary_fired`, `ability_triggered`, `core_triggered` are the fire router entry points. A header comment in `main.gd` listing all signals and their payloads would save any future reader an hour.

## 6. Non-goals for this pass

- Redesign the circumpunct reticle. It's working and on-brand; leave it alone.
- Change the SDF approach. It's doing what it needs to; only revisit if step 4.3 reveals a shape primitive gap.
- Rewrite the ability system from scratch. Step 4.2 is a refactor, not a rewrite; existing behavior stays identical.
- Touch the web build. Migration target is Godot; the web build is the reference, not a place to fix things.

## 7. Execution order summary

1. Extract `BaseShip`.
2. Split ability effects and projectiles.
3. Port a second map.
4. Port audio.
5. Componentize the HUD; add scoreboard, kill feed, post-round card.
6. Decide and implement netcode.

Steps 1-2 are refactors (no new features); they pay for themselves by making steps 3-6 cheap. Steps 3-5 are content + polish. Step 6 is the real multiplayer decision.

## 8. Open questions for Ashman

Before starting any code:

- **Which map to port second in step 4.3?** The web build has several; I'll pick whichever you say feels most different from The Nexus (so the generalization test is real).
- **Audio sources for step 4.4?** Reuse web build assets, or commission/source new?
- **Netcode preference for step 6?** You have a working WebRTC mesh in the web version. Do you want to carry that pattern to Godot, or rethink for native multiplayer?
- **Priority tension.** If you want visible progress fast, steps 4.3 and 4.4 give the biggest "this feels real" returns. If you want structural debt paid down first, 4.1 and 4.2 are the right order. I recommend the structural order (1 → 2 → 3 → 4 → 5 → 6), but the ordering is yours to set.
