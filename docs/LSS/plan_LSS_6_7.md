# Plan: LSS v6.7 Graphics Upgrades

Created: 2026-04-26
Last updated: 2026-04-26
Version: 0.1

The roadmap for layering the next round of visual upgrades onto `last_ship_sailing_v6_7.html` (the mesh-P2P fork). The goal is to take the existing visual vocabulary (emissive bloom, volumetric beams, fresnel, hologram scanlines, lightning, fire, energy shield, particle burst) and reuse the same materials across more places so the world reads richer without writing new shaders.

## Visual vocabulary (existing materials and their canonical use)

This is the inventory of effects that already work in the game and the chassis / system each one is currently identified with. Every upgrade below reuses one of these materials in a new place, so the visual language stays coherent and we are not adding shader work, only spawning more instances.

| Material | Currently used by | Canonical use |
|---|---|---|
| Emissive bloom | Vortex main weapon, Pyro main weapon (with fire tint) | Bright glowing projectile or surface |
| Volumetric beam | Vortex laser-shot (thin), Vortex core (thick) | Light shaft / beam in air |
| Half-energy shield | Vortex shield, Pyro shield (fire tint) | Directional/partial shield surface |
| Full energy shield | "When you have shields" state, every chassis | Wraparound HP shield |
| Particle burst | Slayer main weapon | Shotgun-style spread of bright particles |
| Lightning bolt (thick) | Slayer arc-wave | Short, fat, electric arc |
| Lightning bolt (thin, longer) | Syphon arc-wave | Long thin electric arc |
| Fresnel | Tracker 40mm | Edge-glowing surface |
| Hologram scanlines | Tracker particle shield, Blaster gunshield | Translucent rasterized panel |
| Fire | Pyro variants | Flickering combustion particles |

These ten materials cover everything below. New variants are colour-tinted or scale-tweaked versions; no new shader programs.

## Roadmap (priority-ordered, cheapest big wins first)

1. Directional damage indicator (edge-of-screen vignette pulse from the hit direction)
2. Hitscan tracers (Slayer / Blaster / Syphon arc-wave reach the receiving peer's screen)
3. Engine thruster glow (always-on volumetric beam, chassis-tinted, scales with throttle)
4. Volumetric fog density per room (light spawn rooms, hazy fight rooms)
5. Damage-state ship visuals (cracks at 75%, scorches at 50%, arcing at "doomed" 30%, fire vent at <10%)
6. Stasis field upgrades (proximity tell, godray on consume)
7. Hit-cam micro-stutter on kills (3-frame freeze + bloom punch)
8. Spawn protection bubble (hologram scanline sphere, fades with the timer)
9. Pre-break stress on destructibles (cracks spider out, fresnel intensifies before breakApart)
10. Ability signatures (one per chassis ability, see below)
11. Dash boosters (short volumetric beam burst from each thruster on dash)
12. Sympathetic detonation chain (clusters near a popped one shudder visibly)
13. Hitscan / muzzle-flash variety per chassis
14. Post-processing polish (chromatic aberration on damage / dash, FOV punch on crits)
15. Framework-thematic flourishes (⊙ patterns, phi-spiral debris, HUD i-stroke pulse)

Items 1-4 together produce the largest perceived improvement for the smallest effort and are the recommended first sprint.

## Detailed upgrades

### 1. Directional damage indicator

Edge-of-screen vignette pulse on the side the shot came from. Currently the local player has no idea where they are being hit from in fast 3D combat; this is the difference between knowing you are being shot at and just dying confused.

Implementation: in `playerTakeDamage`, compute the direction from the attacker's position (or the projectile's incoming velocity) into player-local space, dot with the four screen-edge axes, and pulse a CSS / canvas vignette on the dominant edge. Use the existing damage-flash colour palette so it matches the rest of the HUD. Costs nothing per frame except the pulse animation.

### 2. Hitscan tracers

Slayer, Blaster, and the arc-waves currently resolve in one tick on the shooter; the receiving peer feels their HP drop without seeing where the shot came from. Add a `fire/tracer` mesh event carrying `{ox, oy, oz, ex, ey, ez, color, style}` so receivers render a brief line on their screen. (The mesh networking concept doc already names this.)

Per-chassis tracer style:

- Slayer: thick lightning-bolt material (matches its arc-wave aesthetic)
- Blaster: hologram scanline beam (matches its gunshield)
- Syphon: thin lightning-bolt (matches its arc-wave)
- Tracker hitscan (if any): fresnel beam

Plus muzzle-flash sprite at the shooter's position, so the receiver sees both ends of the shot.

### 3. Engine thruster glow

Always-on short volumetric beams from each thruster port, chassis-tinted, length scaling with throttle and dash state. The dash boosters the user mentioned (item 11) are the same effect at maximum scale.

Implementation: attach a `VolumetricBeam` instance to each chassis's thruster anchor point in the chassis mesh. Update length per tick from `player.velocity.length()` or input throttle. Cost: one beam per ship per thruster (typically 2-4 thrusters). Reuse the existing volumetric beam material from the Vortex laser-shot.

### 4. Volumetric fog density per room

Spawn rooms quiet (low fog), central fight rooms hazier (high fog) so muzzle flashes and explosions push through. Tunnels somewhere in between.

Implementation: per-room density value stored on the room data (already in MAP_DATA structure). Render a low-poly volumetric fog mesh inside each room sphere, density tinted by room type. The central energy ball already glows; let it cast volumetric shafts down each tunnel mouth using the same beam material.

### 5. Damage-state ship visuals

Layer cumulatively as HP drops:

- 75% HP: light cracks (decals on the chassis mesh, masked by HP threshold)
- 50% HP: dark scorches (additional decal layer)
- 30% HP ("doomed", existing threshold): electrical arcing across the hull (small lightning-bolt material, looped, animated along the chassis spine)
- <10% HP: small fire-particle stream venting from the chassis

Implementation: the damage decals are texture overlays toggled by HP threshold; the arcing uses the existing lightning material at small scale; the fire vent reuses the Pyro fire material at small scale. The `ship` model already supports material swaps; this is data-driven.

### 6. Stasis field upgrades

Stasis fields are the most fought-over objects in the round; they should look like prizes worth fighting for.

- Core sphere as a brighter volumetric beam pulse (scale up the inner glow)
- Rings spinning faster as a player gets close (proximity tells you you are about to grab it)
- Brief light-shaft / godray straight up when consumed, visible across the level (kill-confirmation feedback for the other player)

Implementation: add proximity check in `StasisField.update(dt)` against `player.position`; modulate ring rotation speed and core bloom intensity. In `enterStasis()`, after `field.destroy()`, spawn a tall thin volumetric beam at the field position with a 1.5s fade. Receivers also play this on `stasis_pickup` event so the consume is visible to all.

### 7. Hit-cam micro-stutter on kills

3-frame freeze-frame on a kill, bloom cranked, slight FOV punch. Sells the moment without disrupting flow.

Implementation: in the local kill detection (when a NetworkPlayer.die fires from broadcast death, or when any local kill resolves), schedule a 50ms render pause + bloom intensity multiplier. Restore on next frame. Costs a single frame budget hit.

### 8. Spawn protection bubble

While `player.spawnProtection > 0`, render a hologram-scanline sphere around the ship that fades opacity from full to zero over the protection window. Reuses the existing scanline material from the Tracker particle shield.

Implementation: toggle a child mesh on the player chassis based on `player.spawnProtection > 0`; opacity = `protection / SPAWN_PROTECTION_MAX`.

### 9. Pre-break stress on destructibles

Telegraph imminent destruction. Cracks spider out across the cluster as HP drops; fresnel intensifies on the children near death. The existing `breakApart` fires at HP=0 as before; this is just visual telegraph.

Implementation: in `ClusterObstacle.update(dt)`, compute the cluster's average child HP; when below 50%, animate crack-decal opacity scaling from 0 to 1; when below 25%, also scale the children's fresnel material intensity. No gameplay change; pure visual.

### 10. Ability signatures (per ability)

Each chassis has a Q/E/F ability that currently lacks visual identity. One bespoke effect per ability, all reusing existing materials:

| Ability | Visual |
|---|---|
| Phase Dash | Fading ghost-clone silhouette (motion-blur copy) at the takeoff point, alpha fades over 200ms |
| Sword Block | Brief edge-spark fresnel along the blade plane on a successful block |
| Cluster Missile | Pre-launch lock-on glow per missile (small bloom on the launcher tube) |
| Salvo Core / remote missiles | Thin tether-line from player to each in-flight missile (only visible to the owner; thin volumetric beam) |
| Tether (Syphon) | Visible chain or rope between player and target (currently invisible; ribbon mesh) |
| Particle Wall | Shimmering scanline field in mid-air, semi-transparent, hologram material |
| Trip Wire | Thin laser line you can see and dodge (thin volumetric beam) |
| Incendiary | Dripping flame remnants on the boundary surface for a few seconds after spawn (Pyro fire material at low scale) |
| Gas Cloud | Volumetric gas using the existing fire shader recolored green / sickly |
| Empowered melee | Aura buildup before the swing (energy-shield material around the weapon for the windup) |

### 11. Dash boosters

Short volumetric beam burst from each thruster port on dash; same material as the thruster glow (item 3) but at maximum scale and shorter duration. Visible to all peers via the per-tick state packet (`player.dashing` flag, broadcast).

Implementation: add `dashing` boolean to broadcast; on receive, NetworkPlayer renders the beam burst when the flag toggles to true.

### 12. Sympathetic detonation chain

When a cluster pops near another, the second one shudders / cracks visibly. Gives the world a chain-reaction feel without changing gameplay.

Implementation: in the `obj_destroy` mesh-event handler, after running `breakApart` on the target, iterate `game.clusters` for any within 200 units and bump their crack-decal opacity by 0.3, plus a small position-shake on the cluster's mesh. Pure visual; HP unaffected.

### 13. Hitscan / muzzle-flash variety per chassis

Each chassis already has a unique main-weapon style; the muzzle flash should match. Currently the muzzle flash is generic.

| Chassis | Muzzle flash style |
|---|---|
| Vortex | Small bloom puff |
| Pyro | Bloom puff + flame tongues (Pyro fire material at small scale) |
| Slayer | Particle burst (matches projectile) |
| Syphon | Thin lightning crackle |
| Tracker | Fresnel ring expansion |
| Blaster | Hologram scanline ring |
| Puncture | Sharp directional cone (small volumetric beam, short and wide) |

### 14. Post-processing polish

- Chromatic aberration on dash (intensity peaks at dash velocity, fades over 300ms)
- Chromatic aberration on damage (one-shot pulse on hit)
- Slight FOV punch on critical hits (5 degrees, 100ms)
- Tone-map spawn rooms cooler and central rooms hotter (gives the level a temperature gradient; tells you where action is from a glance)
- Bloom on the central energy ball cranked when a player gets close to it (proximity-modulated bloom intensity)

Implementation: Three.js post-processing pipeline. Chromatic aberration is a single shader pass; FOV punch is camera.fov modulation; tone mapping is per-room ambient light tinting on existing lights.

### 15. Framework-thematic flourishes

Optional, on-brand for the Circumpunct project. These are flavour, not gameplay.

- ⊙ glyph as a particle burst pattern when two players collide head-on (rare event; cost is low)
- Phi-spiral debris on cluster destruction (fragment scatter follows a golden-ratio spiral instead of pure random; requires the seeded debris scatter anyway, per the mesh doc's debris physics note)
- Faint ⊙ readout on the HUD that pulses on every i-stroke quarter-turn (heart of the gauge structure made visible to the player; ties the visual layer to the framework)
- Critical-hit flash specifically when a shot hits the small "convergence point" of a ship (the ⊙ aperture at the geometric centre of the chassis mesh)
- Death animation as the inverse of the four beats: the killed ship visibly cycles through ⟳ → ✹ → ⎇ → ⊛ as it explodes, each i-stroke a quarter-turn of the explosion expansion

These are sequenced last because they trade against gameplay legibility; opt in deliberately.

## Implementation ordering rationale

Items 1-4 are the "cheapest big wins" because:

- Each one is a single point of code change (one function modification or one new system)
- Each one is visible in every match, every round, by every player
- None of them require new shader work, only reuse of existing materials
- Together they make the world feel substantially more alive: you can see incoming fire (1, 2), see your own movement (3), and have a sense of place inside the level (4)

Items 5-9 build on the foundation: ship state, key-object readability, polish on big moments. Items 10-12 are gameplay-tied flourishes that need each chassis touched individually. Items 13-15 are pure polish.

## Mesh-sync implications

Several upgrades require new fields in the per-tick state packet or new event types in the mesh layer:

- Item 2 (hitscan tracers): new `fire/tracer` event type, per the mesh doc
- Item 11 (dash boosters): `dashing` boolean in per-tick state
- Item 6 (stasis field godray on consume): already covered; the existing `stasis_pickup` event is the trigger
- Item 7 (hit-cam micro-stutter): purely local; no mesh sync needed
- Item 12 (sympathetic detonation): purely local; the local `obj_destroy` handler triggers it

Plan to update `mesh_networking_concept.md` when item 2 lands to formalize the `fire/tracer` event format.

## Out of scope (not yet)

- Skybox / nebula background overhaul
- Per-chassis cockpit / first-person interior
- Replay system / killcam playback
- Spectator mode UI
- Photo mode

These are larger projects orthogonal to the visual-upgrade pass.

## Revision history

- 2026-04-26 v0.1: initial plan, 15 items prioritized; visual-vocabulary inventory of existing materials; mesh-sync implications noted
