# Last Ship Sailing WebSocket Server

Raw WebSocket game server for Last Ship Sailing: 6DOF zero-gravity ship combat. Built with Express + `ws` (no Colyseus).

## Installation

```bash
cd server-ws
npm install
npm start
```

Server runs on `ws://localhost:2567` (or configured PORT). HTTP server serves the client at `http://localhost:2567/`.

## Architecture

### Files

- **index.js** (1.8 KB): Express app + WebSocket server. Handles connections, routes messages to GameRoom.
- **game.js** (39 KB): Complete GameRoom class with all game logic (1495 lines from MatchRoom.js ported).
- **shared.js** (12 KB): LSS constants, CHASSIS, LOADOUTS, Vec3, Quat classes. Copied from original.
- **collision.js** (18 KB): SDF collision system. Copied from original (framework-agnostic).
- **package.json**: Dependencies: `ws` (8.16.0), `express` (4.18.2).

### Game Loop

- **Tick Rate**: 66 Hz (1000/66 ≈ 15.15 ms per tick)
- **Broadcast Rate**: 33 Hz (every 2 ticks)
- Loop order:
  1. Player movement
  2. Bot AI
  3. Level collision (SDF)
  4. Weapon updates
  5. Abilities
  6. Ship-to-ship collision
  7. Projectiles
  8. Doom timers
  9. Round system
  10. State broadcast

### Data Structures

**ServerPlayer**
- Position, velocity, quaternion (rotation)
- Health, shield, damage mechanics
- Weapon state (ammo, reload, fire timer)
- Abilities (cooldowns, active state, timers)
- Loadout-specific state (Ion energy, railgun charge, etc.)
- Dash system, core meter, spawn protection

**ServerBot**
- Same combat state as ServerPlayer
- AI: target selection, movement, strafe, fire decision
- Range preference per loadout

**ServerProjectile**
- Position, velocity, damage, splash radius
- Lifetime, collision tracking
- Owner tracking (for friendly-fire logic)

### Game States

1. **lobby** - Awaiting first player loadout selection
2. **warmup** - 5s countdown before round start
3. **playing** - Active combat, round timer ticking
4. **round_end** - 3s delay, displaying winner
5. **match_end** - Best-of match complete

Round win conditions:
- All enemy team dead
- Round timer expires (draw)
- Match won at 4 rounds first

### Message Protocol

**Client → Server**

```json
{type: 'select_loadout', loadoutKey: 'ION'}
{type: 'input', mx, my, mz, fire, alt, reload, qx, qy, qz, qw}
{type: 'dash'}
{type: 'ability', index: 0}
{type: 'core'}
```

**Server → Client (Broadcast)**

```json
{type: 'state_sync', gameState, roundTimer, warmupTimer, scoreA, scoreB, currentRound, serverTime, players, bots}
{type: 'fire', sid, px, py, pz, dx, dy, dz, weaponType}
{type: 'death', victimSid, victimName, killerName, px, py, pz}
{type: 'impact', px, py, pz, size}
{type: 'ability', sid, index, name}
{type: 'core', sid, name}
{type: 'round_start', round, mapKey}
{type: 'round_end', winner, scoreA, scoreB}
{type: 'match_end', winner, scoreA, scoreB}
{type: 'welcome', sessionId}
```

### Features Ported from Colyseus

✓ All 7 loadouts (ION, SCORCH, NORTHSTAR, RONIN, TONE, LEGION, MONARCH)
✓ All 3 chassis types (Frigate, Corvette, Dreadnought)
✓ Weapon systems: hitscan, projectile, spread
✓ All abilities with cooldowns
✓ Core abilities (ultimate abilities)
✓ Dash system with charge management
✓ Shield regen with delay
✓ Damage mechanics: shields, health, abilities-as-damage-reduction
✓ Doomed state (15% health threshold, 10s timer)
✓ Spawn protection
✓ Kill tracking, damage dealt
✓ BOT AI: target selection, movement, strafe, fire decisions, retreat when doomed
✓ Projectile physics: lifetime, collision, splash radius
✓ Friendly-fire logic
✓ Round system: warmup, playing, round_end, match_end
✓ Level geometry: SDF-based collision, room + tunnel system
✓ Arena boundaries with soft containment

### Loadout Details

| Loadout | Chassis | Weapon | Abilities |
|---------|---------|--------|-----------|
| ION | Corvette | Splitter Rifle (hitscan) | Laser Shot, Vortex Shield, Trip Wire |
| SCORCH | Dreadnought | T-203 Thermite (projectile) | Firewall, Thermal Shield, Incendiary Trap |
| NORTHSTAR | Frigate | Plasma Railgun (hitscan) | Cluster Missile, Afterburner, Tether Trap |
| RONIN | Frigate | Leadwall (spread) | Arc Wave, Sword Block, Phase Dash |
| TONE | Corvette | 40mm Tracker (projectile) | Tracker Rockets, Particle Wall, Sonar Lock |
| LEGION | Dreadnought | Predator Cannon (hitscan) | Power Shot, Gun Shield, Mode Switch |
| MONARCH | Corvette | XO-16 Chaingun (hitscan) | Rocket Salvo, Energy Siphon, Rearm |

### Ability System

Each loadout has 3 abilities + 1 core ability:
- **Ability 0**: Offensive cooldown-based
- **Ability 1**: Defensive (often hold-to-activate)
- **Ability 2**: Utility
- **Core**: Ultimate ability (requires 100 core meter, gained from damage dealt)

Core meter fills at 1 point per 100 damage dealt.

### Physics

- No gravity (LSS.GRAVITY = 0)
- Drag: 2% per second
- Max speeds enforced per chassis
- Soft arena boundary at 80% of ARENA_SIZE
- SDF collision with level geometry
- Ship-to-ship repulsion (no overlap allowed)
- Ram damage: 500 base + 3× impact speed

### Collision System

**Level Collision** (SDF)
- Signed Distance Fields for level geometry
- Smooth blending of rooms (spheres) and tunnels (cylinders)
- Raycast for hitscan range limiting
- Soft containment inside boundaries
- Unsticking near walls

**Ship-to-Ship**
- Repulsion force scales with overlap
- Velocity impulse with damping
- Ram damage threshold: 80 m/s

### How to Extend

1. **Add new loadouts**: Edit `LOADOUTS` in shared.js
2. **Adjust weapon stats**: Modify weapon properties
3. **Tweak balance**: Edit damage, cooldowns, cooldowns, speeds
4. **Add map**: buildLevelData() uses MAP_DATA from collision.js
5. **Bot difficulty**: Adjust fireTimer, hitChance, rangePreference in updateBotAI()
6. **UI/VFX**: All events broadcast as messages; client handles rendering

### Performance Notes

- 66 Hz server tick is ideal for 60 FPS client (1.1 ms headroom)
- State broadcasts at 33 Hz (every other tick)
- Each tick < 10 ms on modern hardware with 12 players + 4 bots
- Projectile collision is O(n) per projectile; limit projectile count for large servers

### Known Limitations

- Single map (Circumpunct) hardcoded
- No user persistence (no database)
- No authentication
- Bots are not as sophisticated as full MatchRoom (simplified fire logic)
- No voice chat or team chat
- Arena boundaries are soft, not hard walls (can exceed slightly)

---

Built with the Circumpunct Framework mindset: constraint hierarchies from aperture through field to boundary.
