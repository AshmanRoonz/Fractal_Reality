# Last Ship Sailing: Multiplayer Server Architecture

## Overview

The server implements a fully authoritative 6DOF multiplayer game with tick-based simulation, WebSocket communication, and bot backfill. It runs at 60 Hz game loop with state broadcast at 20 Hz.

## File Structure

### `/server/index.js` (Main Entry Point)
- Express HTTP server with WebSocket support
- REST API endpoints for match creation and discovery
- WebSocket connection management and message routing
- Player ID generation
- Graceful shutdown handling

**Key Endpoints:**
- `GET /api/matches` : List all public matches
- `POST /api/matches` : Create a new match
- `GET /api/matches/:id` : Get match details
- `WS /ws` : WebSocket endpoint for game communication

### `/server/lobby.js` (Match Management)
- Manages all active matches
- Creates matches with unique IDs and join codes
- Provides match lookup and listing (public only)
- Handles match cleanup after 60 seconds of emptiness

### `/server/match.js` (Core Game Simulation)
**State Machine:** `lobby` -> `loadout` -> `warmup` -> `playing` -> `roundEnd` -> loop or `matchEnd`

**Key Responsibilities:**
- Player management (add/remove, team balancing)
- Entity physics (position, velocity, quaternion rotation)
- Combat system (hitscan, projectile, spread weapons; damage calculation)
- Round management (spawn protection, respawn, kill tracking)
- Game state broadcasting to all connected clients

**Physics Model:**
- Position integration with velocity and acceleration
- Quaternion-based 6DOF rotation
- Local-to-world space conversion via forward/right/up vectors
- Exponential drag with speed caps per chassis
- Projectile collision detection (sphere-based)

**Combat Pipeline:**
1. Input validation and rate limiting
2. Weapon fire (hitscan raycast, projectile spawning, spread pellets)
3. Collision detection (sphere radius per chassis)
4. Damage application (shield first, then health)
5. Status checks (spawn protection, doomed state, death)
6. Kill tracking and round end conditions

**Entity State Structure:**
```javascript
{
  pos: {x, y, z},
  vel: {x, y, z},
  quat: {x, y, z, w},          // orientation quaternion
  angVel: {x, y, z},
  health, maxHealth, shield, maxShield,
  shieldRegenTimer, shieldRegenDelay, shieldRegenRate,
  dead, doomedTimer, isDoomed,
  fireCooldown, clipAmmo, reloading, reloadTimer,
  abilityCooldowns: [0, 0, 0],
  coreMeter, coreActive, coreTimer,
  dashCharges, dashCooldownTimer,
  spawnProtection,
  input: { fwd, back, left, right, up, down, pitch, yaw, roll, fire, reload, ability1, ability2, ability3, core },
  projectiles: [],
  kills
}
```

### `/server/gameloop.js` (Main Loop)
- Runs at 60 Hz (TICK_RATE)
- Calls `tick(dt)` on all active matches
- Broadcasts state at 20 Hz (NET_SEND_RATE)
- Performance monitoring (warns if tick > 16ms)

**Timing:**
- Game tick: ~16.67 ms per frame at 60 Hz
- State broadcast: every 3rd tick (50 ms between broadcasts)
- dt computed from actual wall-clock time

### `/server/botmanager.js` (AI Bot Backfill)
- Creates and manages AI-controlled players
- Fills teams up to `maxPlayers / 2` per team if `botFill: true`
- Simple AI (Phase 1): nearest enemy pursuit, rotation toward target, fire when facing

**Bot AI Logic:**
- Pick nearest enemy within 3000 units
- Rotate (pitch/yaw) to face target using PID-like control
- Thrust toward target (distance-based speed scaling)
- Fire when facing enemy (dot product > 0.7)
- Auto-reload when out of ammo
- Random exploration when no enemy in sight

## Game Flow

### 1. Player Connection
- WebSocket connects to `/ws`
- Server assigns unique player ID
- Client sends `join_match` with match ID
- Server adds player to team with fewer players
- Welcome message includes map data and current game state

### 2. Loadout Selection (Loadout Phase)
- Players select from 7 available loadouts
- Each loadout defines chassis, weapon, and abilities
- Server validates loadout exists
- Player entity state created from loadout specs

### 3. Ready Up (Still Loadout Phase)
- Player marks ready after selecting loadout
- Server checks if all players ready and minimum threshold met
- Transition to `warmup` phase

### 4. Warmup Phase
- 5 second countdown
- No gameplay updates
- Players can move around to prepare
- At end, transition to `playing`

### 5. Playing Phase
- Round timer starts (180 seconds default)
- Server processes physics and combat each tick
- Input from clients is validated and applied
- Damage is calculated server-side (authoritative)
- Projectiles tracked and collisions checked
- Shield regen ticks if no damage taken for delay period
- Round ends when: all of one team dead, or timer expires

### 6. Round End Phase
- Winner determined
- Score updated
- Broadcast to all players
- If match score reached threshold (4 rounds), match ends
- Otherwise, return to `warmup` for next round

### 7. Match End
- Match state set to `matchEnd`
- No further gameplay updates
- Players notified of final winner and scores

## Input Handling

**Input Message Format:**
```javascript
{
  type: 'input',
  input: {
    fwd, back, left, right, up, down,    // range [-1, 1]
    pitch, yaw, roll,                     // range [-1, 1]
    fire, reload,                         // boolean
    ability1, ability2, ability3, core   // boolean
  }
}
```

**Rate Limiting:** Input is only processed during `playing` and `warmup` phases. All values are clamped to [-1, 1] range.

## Message Types (WebSocket)

**Server to Client:**
- `connect_ack`: Initial connection confirmation with player ID
- `match_join_ok`: Player successfully joined match
- `player_joined`: Another player joined (broadcast)
- `player_left`: Player disconnected (broadcast)
- `loadout_selected`: Player chose a loadout (broadcast)
- `player_ready`: Player marked ready (broadcast)
- `state_change`: Phase transition (phase, duration)
- `game_state`: Full game state snapshot (20 Hz)
- `doomed`: Player entered doomed state (countdown to death)
- `player_killed`: Kill notification (victim, attacker)
- `round_end`: Round ended (winner team, score)
- `match_end`: Match ended (winner team, final scores)
- `chat`: Chat message from player
- `error`: Error message

**Client to Server:**
- `join_match`: Join a match (matchId)
- `leave_match`: Leave current match
- `input`: Send player input
- `loadout_select`: Choose a loadout (loadoutKey)
- `ready`: Mark player ready
- `chat`: Send chat message

## Physics Details

### Movement
- Local thrust direction converted to world space via quaternion rotation
- Separate max speeds for forward (flightSpeed), strafe (strafeSpeed), vertical (verticalSpeed)
- Acceleration applied over time, then drag applied (exponential: vel *= 0.97^dt)
- Global speed cap at 1.5x flightSpeed

### Rotation
- Angular velocity driven by input pitch/yaw/roll rates
- Quaternion integrated from angular velocity using half-angle formula
- Quaternion normalized after each integration step

### Collision
- No SDF (Signed Distance Field) collision in Phase 1
- Projectiles use ray/sphere intersection
- Hitscan uses ray/sphere casting from player forward direction

## Combat Details

### Weapon Types
1. **Hitscan**: Instant damage, raycast in forward direction, hits closest target
2. **Projectile**: Spawned entity, lifetime-based, sphere collision check
3. **Spread**: Multiple projectiles (pellets) with random spread angle

### Damage Pipeline
1. Shields reduce first (before health)
2. Any overflow damage goes to health
3. Shield regeneration paused for `shieldRegenDelay` seconds after hit
4. Health below 15% triggers doomed state (10 second countdown to auto-kill)

### Status Effects
- **Spawn Protection**: 3 seconds of invulnerability after respawn
- **Doomed**: Health below 15%; auto-killed after 10 seconds if not healed
- **Shield Regen**: Passive regeneration at `shieldRegenRate` per second after delay

## Team Management

Teams are auto-balanced: when a player joins, they're assigned to the team with fewer players. Bot fill ensures each team has `maxPlayers / 2` players if `botFill: true`.

## Logging

The server logs:
- Player connections and disconnections
- Match creation and removal
- Round and match progression
- Bot creation and removal
- Performance warnings (slow ticks)
- Errors and edge cases

## Performance Notes

- Tick rate: 60 Hz (16.67 ms per frame)
- State broadcast: 20 Hz (every 3rd tick)
- Per-match overhead: minimal; mostly player physics and combat
- Scales to ~5-10 concurrent matches before noticeable slowdown (depends on machine)
- No SDF collision detection yet (Phase 2 feature)

## Future Extensions

1. **Phase 2**: Add SDF (Signed Distance Field) collision for environment
2. **Phase 2**: Implement abilities and core meter mechanics
3. **Phase 3**: Advanced bot AI (pathfinding, ability usage, team tactics)
4. **Phase 3**: Matchmaking and ranking
5. **Phase 3**: Spectator mode and replays
