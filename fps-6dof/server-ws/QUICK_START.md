# Quick Start

## Install & Run

```bash
cd server-ws
npm install
npm start
```

Server starts on `ws://localhost:2567` (WebSocket) and `http://localhost:2567/` (HTTP static).

## Architecture at a Glance

```
index.js (63 lines)
  ├─ Express server
  ├─ WebSocket handler (connection, message, close)
  └─ GameRoom singleton

game.js (1495 lines of game logic)
  ├─ GameRoom (tick loop, game state, message routing)
  ├─ ServerPlayer (position, health, weapons, abilities)
  ├─ ServerBot (AI, same combat state as player)
  └─ ServerProjectile (lifetime, collision)

shared.js (234 lines, exact copy from Colyseus)
  ├─ LSS constants
  ├─ CHASSIS (3 types)
  ├─ LOADOUTS (7 ships)
  ├─ Vec3 & Quat math
  └─ Helper functions

collision.js (534 lines, exact copy from Colyseus)
  ├─ SDF collision (level geometry)
  ├─ Ship-to-ship collision
  └─ Level data builder
```

## Game Loop (66 Hz)

1. Player movement + input handling
2. Bot AI
3. Level collision (SDF)
4. Weapon updates & firing
5. Abilities
6. Ship-to-ship collisions (ram damage)
7. Projectiles
8. Doom timers
9. Round management
10. **State broadcast (every 2 ticks = 33 Hz)**

## Message Flow

**Player connects:**
```
Client ──connect──> Server
Server ──{type: 'welcome', sessionId}──> Client
```

**Player selects loadout:**
```
Client ──{type: 'select_loadout', loadoutKey: 'ION'}──> Server
Server ──checks readyCount, starts warmup if ≥1 player ready
Server ──{type: 'round_start', round, mapKey}──> All players
Server ──{type: 'state_sync', ...}──> All (every 33 Hz)
```

**Player fires:**
```
Client ──{type: 'input', fire: true}──> Server (every tick)
Server ──fireWeapon()──> raycast/projectile check
Server ──{type: 'fire', ...}──> All (broadcast VFX)
Server ──{type: 'impact', ...} [if hit]──> All
```

**Player takes damage:**
```
Server ──applyDamage()──> shield → health → doomed → death
Server ──{type: 'death', victimName, killerName, ...}──> All
Server ──5s delay──> respawnPlayer()
```

**State broadcast (every 33 Hz):**
```
{
  type: 'state_sync',
  gameState: 'playing',
  roundTimer: 150.5,
  warmupTimer: 0,
  scoreA: 2, scoreB: 1,
  currentRound: 4,
  serverTime: 45.2,
  players: {
    's0_abc123': {
      sid, loadoutKey, team,
      px, py, pz, vx, vy, vz, qx, qy, qz, qw,
      health, maxHealth, shield, maxShield,
      alive, doomed, doomTimer,
      clipAmmo, reloading, isFiring,
      abilityCd0-2, abilityActive0-2,
      coreActive, coreTimer,
      dashCharges, dashActive,
      kills, deaths, damageDealt
    }
  },
  bots: {
    'bot_xyz789': { id, loadoutKey, team, px, py, pz, ... }
  }
}
```

## Loadouts (7 Total)

| Name | Chassis | Weapon | Abilities |
|------|---------|--------|-----------|
| ION | Corvette | Splitter Rifle (hitscan) | Laser Shot, Vortex Shield, Trip Wire |
| SCORCH | Dreadnought | T-203 Thermite (projectile) | Firewall, Thermal Shield, Incendiary Trap |
| NORTHSTAR | Frigate | Plasma Railgun (hitscan) | Cluster Missile, Afterburner, Tether Trap |
| RONIN | Frigate | Leadwall (spread) | Arc Wave, Sword Block, Phase Dash |
| TONE | Corvette | 40mm Tracker (projectile) | Tracker Rockets, Particle Wall, Sonar Lock |
| LEGION | Dreadnought | Predator Cannon (hitscan) | Power Shot, Gun Shield, Mode Switch |
| MONARCH | Corvette | XO-16 Chaingun (hitscan) | Rocket Salvo, Energy Siphon, Rearm |

## Abilities

Each loadout has:
- **Ability 0**: Offensive (cooldown)
- **Ability 1**: Defensive (often toggle)
- **Ability 2**: Utility
- **Core**: Ultimate (100 core meter = ready)

Example: ION
- Ability 0 (Laser Shot): 10s cooldown, instant 2400 damage beam
- Ability 1 (Vortex Shield): Hold to absorb projectiles
- Ability 2 (Trip Wire): 12s cooldown, proximity mines
- Core (Laser Core): 4s continuous beam, 60s cooldown

## Combat Mechanics

**Health & Shield:**
- Shield absorbs damage first
- Regenerates after 5-8s delay (loadout-dependent)
- When shield breaks, damage goes to health

**Doomed State:**
- Triggered at 15% health
- 10s timer before automatic death
- Broadcasts "doomed" status to all players

**Damage Reduction:**
- Defensive abilities reduce incoming damage
- Sword Block: 30% (70% at Sword Core)
- Gun Shield: Absorbs up to 5000 damage
- Thermal Shield: Absorbs up to 3000 damage
- Vortex Shield: Absorbs and stores projectiles

**Core Meter:**
- Gains 1 point per 100 damage dealt
- Max 100 points
- Core abilities cost 100 (immediate reset after activation)
- Duration varies: 2-12 seconds per core

**Spawn Protection:**
- 3 seconds of invulnerability after respawn
- Cannot deal or take damage

**Dash System:**
- Frigate: 3 charges, 900 m/s, 0.4s duration, 4s cooldown
- Corvette: 2 charges, 750 m/s, 0.5s duration, 5s cooldown
- Dreadnought: 1 charge, 550 m/s, 0.6s duration, 7s cooldown

## Game States

```
lobby
  ↓ (1st player selects loadout)
warmup (5 seconds)
  ↓
playing (180 seconds or team wipe)
  ↓ (Team eliminated OR timer expires)
round_end (3 seconds)
  ↓
[repeat until someone wins 4 rounds]
  ↓
match_end
```

## Physics

- No gravity
- 2% drag per second
- Arena size: 25,000 units per axis
- Soft boundary at 80% (gentle push inward)
- Ship-to-ship repulsion (configurable range multiplier 2.2×)
- Ram damage: 500 base + 3× impact speed

## SDF Level Geometry

**Rooms** (spheres):
- Center: r=525 units
- Spawn A/B: r=375 units
- Ready A/B: r=375 units

**Tunnels** (capsules): radius=300 units connecting rooms

Smooth blending between shapes using Cubic Hermite interpolation (smoothK=45).

## Bot Behavior

Bots spawn 2 per team (4 total). They:
- Select target every 1-3 seconds
- Wander randomly when no target
- Move toward target, strafe occasionally
- Fire when aligned (dot product > 0.7) and in range
- Retreat when doomed (move away from enemies)
- Build core meter naturally (1.5 points/sec)
- Have different range preferences per loadout:
  - NORTHSTAR/TONE: 3500 units
  - LEGION: 1500 units
  - RONIN: 900 units
  - Others: 2000 units

## Performance

- Server tick: 66 Hz (15.15 ms per frame)
- State broadcast: 33 Hz (every 2 ticks)
- Supports 12 players + 4 bots
- Network: Full state sync JSON (efficient for 16 entities)
- CPU: < 10 ms per tick on modern hardware

## Extending the Server

**Add a new ship:**
1. Add to LOADOUTS in shared.js (copy existing, modify)
2. Add to CHASSIS if new type needed
3. Adjust weapon damage, ability cooldowns as desired
4. Client auto-detects via loadout list

**Tweak balance:**
- Weapon damage: shared.js LOADOUTS[key].weapon.damage
- Ability cooldowns: shared.js LOADOUTS[key].abilities[i].cooldown
- Chassis stats: shared.js CHASSIS.CORVETTE, etc.
- Bot accuracy: game.js updateBotAI hitChance formula

**Add map:**
1. Define in collision.js MAP_DATA
2. Call buildLevelData('newMapKey')
3. Update startWarmup message

**Change difficulty:**
- Bot fire rate: game.js botFireAtTarget fireTimer multiplier
- Bot accuracy: hitChance = Math.max(0.3, 1 - dist / ...)
- Bot targeting: findBotTarget, findClosestEnemy

---

Built with the Circumpunct Framework: aperture (•) through field (Φ) to boundary (○).
