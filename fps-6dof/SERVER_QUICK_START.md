# Last Ship Sailing Server: Quick Start Guide

## Installation

```bash
cd fps-6dof
npm install
```

## Running the Server

```bash
npm start
```

The server will listen on `http://localhost:3000` and WebSocket at `ws://localhost:3000/ws`.

## API Quick Reference

### Create a Match

```bash
curl -X POST http://localhost:3000/api/matches \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deathmatch Arena",
    "map": "circumpunct",
    "maxPlayers": 10,
    "botFill": false
  }'
```

Response:
```json
{
  "id": "match_1712464800000_abc1234",
  "name": "Deathmatch Arena",
  "map": "circumpunct",
  "maxPlayers": 10,
  "state": "lobby",
  "botFill": false,
  "joinCode": "A7K2M9"
}
```

### List Public Matches

```bash
curl http://localhost:3000/api/matches
```

### Get Match Details

```bash
curl http://localhost:3000/api/matches/match_1712464800000_abc1234
```

## WebSocket Messages

### Client Sends: Join a Match

```javascript
ws.send(JSON.stringify({
  type: 'join_match',
  matchId: 'match_1712464800000_abc1234'
}));
```

### Client Sends: Player Input

```javascript
ws.send(JSON.stringify({
  type: 'input',
  input: {
    fwd: 1.0,      // range [-1, 1]
    back: 0.0,
    left: 0.0,
    right: 0.0,
    up: 0.5,       // hold space to go up
    down: 0.0,
    pitch: -0.2,   // look up/down
    yaw: 0.3,      // look left/right
    roll: 0.0,
    fire: true,
    reload: false,
    ability1: false,
    ability2: false,
    ability3: false,
    core: false
  }
}));
```

### Client Sends: Select Loadout

```javascript
ws.send(JSON.stringify({
  type: 'loadout_select',
  loadoutKey: 'ION'  // or: SCORCH, NORTHSTAR, RONIN, TONE, LEGION, MONARCH
}));
```

### Client Sends: Mark Ready

```javascript
ws.send(JSON.stringify({
  type: 'ready'
}));
```

### Server Sends: Game State (Every ~50ms)

```javascript
{
  type: 'game_state',
  matchId: 'match_...',
  gameTime: 23.45,
  matchState: 'playing',  // lobby, loadout, warmup, playing, roundEnd, matchEnd
  scoreA: 1,
  scoreB: 0,
  round: 1,
  players: {
    'player_1': {
      id: 'player_1',
      team: 'A',
      loadout: 'ION',
      connected: true,
      entity: {
        pos: {x: 100.5, y: 50.2, z: -200.3},
        quat: {x: 0, y: 0.707, z: 0, w: 0.707},
        vel: {x: 50, y: 0, z: 0},
        health: 7500,
        shield: 2500,
        dead: false,
        isDoomed: false,
        clipAmmo: 30,
        reloading: false,
        kills: 2
      }
    },
    // ... other players ...
  }
}
```

### Server Sends: State Change

```javascript
{
  type: 'state_change',
  newState: 'warmup',  // or playing, roundEnd, etc.
  duration: 5,         // seconds until next state
  round: 1
}
```

### Server Sends: Kill Notification

```javascript
{
  type: 'player_killed',
  victim: 'player_1',
  attacker: 'player_2'
}
```

### Server Sends: Round End

```javascript
{
  type: 'round_end',
  winnerTeam: 'A',
  scoreA: 2,
  scoreB: 1
}
```

### Server Sends: Match End

```javascript
{
  type: 'match_end',
  winner: 'A',
  finalScoreA: 4,
  finalScoreB: 2
}
```

## Loadout Roster

| Loadout   | Chassis      | Weapon           | Type       | Damage |
|-----------|--------------|------------------|------------|--------|
| ION       | FRIGATE      | Splitter Rifle   | hitscan    | 380    |
| SCORCH    | DREADNOUGHT  | T-203 Thermite   | projectile | 900    |
| NORTHSTAR | FRIGATE      | Plasma Railgun   | hitscan    | 1000   |
| RONIN     | FRIGATE      | Leadwall         | spread     | 200x8  |
| TONE      | CORVETTE     | 40mm Tracker     | projectile | 660    |
| LEGION    | DREADNOUGHT  | Predator Cannon  | hitscan    | 85     |
| MONARCH   | CORVETTE     | XO-16 Chaingun   | hitscan    | 240    |

## Chassis Stats

| Chassis      | Health | Shield | Regen Rate | Flight Speed | Collide Radius |
|--------------|--------|--------|------------|--------------|----------------|
| FRIGATE      | 7500   | 2500   | 200/s      | 450          | 50             |
| CORVETTE     | 10000  | 3500   | 175/s      | 350          | 65             |
| DREADNOUGHT  | 12500  | 5000   | 150/s      | 250          | 90             |

## Match Configuration

| Setting         | Default | Range     | Notes                              |
|-----------------|---------|-----------|-----|
| MAX_PLAYERS     | 10      | 2-10      | Balanced: 5v5                      |
| ROUND_TIME      | 180     | seconds   | Time limit per round               |
| WARMUP_TIME     | 5       | seconds   | Countdown before round starts      |
| ROUNDS_TO_WIN   | 4       | matches   | First team to win 4 rounds wins    |
| SPAWN_PROTECT   | 3       | seconds   | Invulnerability after spawn        |
| DOOMED_HEALTH   | 15%     | percent   | Health threshold for doomed state  |
| DOOMED_TIMER    | 10      | seconds   | Time until auto-kill when doomed   |
| TICK_RATE       | 60      | Hz        | Server game loop                   |
| NET_SEND_RATE   | 20      | Hz        | State broadcast frequency          |

## Common Debugging

### Server Won't Start

- Check Node version: `node --version` (need 14+)
- Check dependencies: `npm install`
- Check port: `netstat -an | grep 3000` (make sure 3000 is free)

### Players Can't Connect

- Firewall: allow port 3000 (or set `PORT` env var)
- WebSocket path: ensure client connects to `/ws` endpoint
- Check console logs: server prints connection attempts

### Physics Feels Wrong

- Adjust TICK_RATE in gameloop.js (60 Hz is stable baseline)
- Adjust DRAG coefficients in match.js (0.97 for linear, 0.93 for angular)
- Check quaternion normalization after rotation (done every tick)

### Bot AI Broken

- Check botmanager.js logic for nearest enemy search
- Verify bot loadout exists in shared/constants.js
- Bots need 3000+ unit visibility range to engage

## Environment Variables

```bash
PORT=8000 npm start      # Listen on port 8000 instead of 3000
```

## File Reference

- **server/index.js** - Main entry point; HTTP/WebSocket server
- **server/lobby.js** - Match creation and management
- **server/match.js** - Core game simulation (physics, combat, rounds)
- **server/gameloop.js** - 60 Hz main loop and state broadcasting
- **server/botmanager.js** - AI bot creation and control
- **shared/constants.js** - Game rules, chassis, loadouts
- **shared/maps.js** - Map definitions (Circumpunct, Nexus, Procedural)

## Architecture

```
HTTP Server (Express)
  └─ REST API (match discovery)
  └─ Static files (client/)

WebSocket Server (ws)
  └─ PlayerA
  └─ PlayerB
  └─ ...

GameLoop (60 Hz)
  └─ Match 1
  │   ├─ Physics update
  │   ├─ Combat processing
  │   └─ State broadcast (20 Hz)
  └─ Match 2
      ├─ Physics update
      ├─ Combat processing
      └─ State broadcast (20 Hz)
```

## Phase 1 Limitations

- No SDF (Signed Distance Field) collision with environment
- Abilities defined but not implemented (cooldowns only)
- No advanced bot AI (no pathfinding or tactical decisions)
- Simple raycast/sphere collision detection (no complex geometry)
- No chat persistence or spectator mode
- No replay system

These features are planned for Phase 2 and Phase 3.
