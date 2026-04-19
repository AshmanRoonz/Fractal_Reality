# Bot AI Upgrade: Squad Tactics, Flanking, and Smart Combat

## Overview

The Bot class in `last_ship_sailing.html` has been upgraded with sophisticated squad coordination, flanking tactics, smart range-based combat, and corridor-based navigation. Bots now hunt collaboratively, apply tactical positioning, and respond intelligently to health states.

## What Changed

### File Modified
- `/sessions/vigilant-pensive-davinci/mnt/Fractal_Reality/fps-6dof/last_ship_sailing.html`
- Lines 1954-2271 (Bot class)

### Methods Enhanced
1. **Constructor** (lines 1990-2011): Added 12 new AI properties
2. **update()** (lines 2026-2164): Enhanced movement with flanking, strafing, retreat
3. **findTarget()** (lines 2166-2238): Squad coordination and memory fallback
4. **getLoadoutRangePreference()** (new, lines 2013-2024): Loadout-specific optimal distance

### New Method
- **navigateToEnemyTerritory()** (lines 2240-2271): Corridor-based navigation

## New AI Properties

```javascript
this.aiRole                // 'flank' or 'engage' (33% flankers)
this.aiLastKnownPlayer     // Position of last player sighting
this.aiLastKnownTime       // Timestamp of last player sighting
this.aiSharedTargetAge     // Age of squad's shared target data
this.aiStrafe              // Current strafe direction active
this.aiStrafeTimer         // Time until strafe direction changes
this.aiStrafeDir           // 1 (left) or -1 (right)
this.aiNavTarget           // Current navigation target
this.aiRangePreference     // Loadout-optimal engagement distance
this.aiRetreating          // True when health critical
this._tempVec3a, _tempVec3b // Reused vectors (performance)
```

## Feature Details

### 1. Squad Coordination (Lines 2181-2196)

Enemy bots share player position via `game.botSharedTarget`:
- When a bot has line of sight, it broadcasts player position
- Other bots navigate toward the shared target even without direct vision
- Shared target expires after 7 seconds (forces independent action)
- Enables 3-bot coordinated hunts

**Implementation:**
```javascript
if (this.team === LSS.TEAM_FLEET_B) {
  if (!game.botSharedTarget) game.botSharedTarget = {};
  game.botSharedTarget.pos = player.position.clone();
  game.botSharedTarget.time = game.time;
}
```

### 2. Flanking Tactics (Lines 2078-2087)

33% of bots assigned `aiRole = 'flank'`:
- Navigate 90 degrees perpendicular to player position
- Active at 300-3000 unit range
- Blend movement 60% toward flanking position
- Forces player to manage multi-angle threats

**Implementation:**
```javascript
if (this.aiRole === 'flank' && distToPlayer < 3000 && distToPlayer > 300) {
  const playerDir = toPlayer.normalize();
  const right = new THREE.Vector3(0, 1, 0).cross(playerDir).normalize();
  const flankOffset = right.multiplyScalar(600);
  const flankTarget = player.position.clone().add(flankOffset);
  const toFlank = this._tempVec3b.subVectors(flankTarget, this.position).normalize();
  moveDir.lerp(toFlank, 0.6);
  moveDir.normalize();
}
```

### 3. Combat Strafing (Lines 2056-2094)

All bots perform unpredictable lateral movement:
- Strafe direction changes every 1-3 seconds randomly
- Movement perpendicular to player direction
- Active within `range preference * 1.5` distance
- Disabled when doomed (allows cleanup)

**Implementation:**
```javascript
this.aiStrafeTimer -= dt;
if (this.aiStrafeTimer <= 0) {
  this.aiStrafe = Math.random() < 0.5;
  this.aiStrafeDir = Math.random() < 0.5 ? 1 : -1;
  this.aiStrafeTimer = 1 + Math.random() * 2;
}

if (this.aiStrafe && distToPlayer < this.aiRangePreference * 1.5 && !this.doomed) {
  const perpendicular = new THREE.Vector3(0, 1, 0).cross(toPlayer).normalize();
  moveDir.add(perpendicular.clone().multiplyScalar(this.aiStrafeDir * 0.5));
  moveDir.normalize();
}
```

### 4. Range Preference by Loadout (Lines 2013-2024)

Each loadout has optimal engagement distance:

| Loadout | Distance | Behavior |
|---------|----------|----------|
| SCORCH | 500 | Aggressive close-range assault |
| RONIN | 500 | Aggressive sword range |
| NORTHSTAR | 1500 | Defensive sniper standoff |
| TONE | 1200 | Balanced medium range |
| LEGION | 1000 | Suppressive minigun range |
| ION | 1000 | Medium energy-efficient |
| MONARCH | 800 | Versatile medium-close |

Bots only fire when within `range preference * 1.3`, preventing wasted ammo.

**Implementation:**
```javascript
const preferredDist = this.aiRangePreference;
const withinRange = distToPlayer <= preferredDist * 1.3;

if (dot > 0.7 && withinRange) {
  // Fire only if in optimal range window
}
```

### 5. Corridor Point Navigation (Lines 2240-2271)

When no target information, bots use level geometry:
- Greedy pathfinding through `game.corridorPoints`
- Scores points by distance and territory preference
- Prefers points in enemy territory (500 point discount)
- Ensures active movement toward objectives

**Implementation:**
```javascript
for (const nav of game.corridorPoints) {
  const distToNav = this._tempVec3a.set(nav.x, nav.y, nav.z).distanceTo(this.position);
  let score = distToNav;
  if (nav.team && nav.team !== goal) score -= 500;
  if (score < bestScore) {
    bestScore = score;
    bestNav = nav;
  }
}
```

### 6. Doomed Retreat Behavior (Lines 2043-2070)

When health critical:
- Bot sets `aiRetreating = true` immediately
- Moves away from player at maximum speed
- Stops firing attempts
- Strafing disabled (easy target)
- Allows skilled players to chase finishes

**Implementation:**
```javascript
if (this.doomed && !this.aiRetreating) {
  this.aiRetreating = true;
}

if (this.aiRetreating) {
  moveDir = this._tempVec3b.subVectors(this.position, player.position).normalize();
}

if (this.fireTimer <= 0 && game.state === 'playing' && !this.aiRetreating) {
  // Only fires when not retreating
}
```

### 7. Last Known Position Memory (Lines 2200-2212)

Three-tier fallback system:
1. **Direct LOS**: Current player position (perfect data)
2. **Squad memory**: Last seen via shared target (7 sec window)
3. **Own memory**: Personal last known position (5 sec window, with drift)
4. **Navigation**: Fallback to corridor pathfinding

Memory position drifts with time to simulate realistic forgetting:
```javascript
targetPos = this.aiLastKnownPlayer.clone().add(
  this._tempVec3b.set(
    (Math.random() - 0.5) * (memoryAge * 80),
    (Math.random() - 0.5) * (memoryAge * 40),
    (Math.random() - 0.5) * (memoryAge * 80)
  )
);
```

### 8. Friendly Bot Support (Lines 2221-2233)

TEAM_FLEET_A bots (allies):
- Maintain 200-400 unit randomized offset around player
- Use same flanking and strafing logic
- Follow player into combat
- Call `navigateToEnemyTerritory()` when player dies
- Provide support without blocking actions

## Performance Optimizations

1. **Reused Vector3 Objects**: `_tempVec3a` and `_tempVec3b` prevent per-frame allocations
2. **Shared Squad Target**: Single `game.botSharedTarget` object instead of per-bot storage
3. **Greedy Navigation**: O(n) simple search through corridor points (not A*)
4. **Timer-based Strafing**: Direction changes on timer, not per-frame randomness

No measurable performance impact expected on modern hardware.

## Preserved Systems

The following systems remain completely unchanged:
- SDF functions and spatial queries
- Shader rendering pipeline
- Marching cubes mesh generation
- Networking layer
- Weapon firing system and accuracy
- Level geometry and collision detection
- Particle effects and VFX
- Animation and mesh orientation

## Gameplay Impact

### Before Upgrade
- Bots wander randomly when not in combat
- Bots hunt only if they have direct line of sight
- All bots use identical tactics regardless of loadout
- Doomed bots continue fighting until death
- No spatial awareness or tactical positioning

### After Upgrade
- Bots actively patrol and navigate level geometry
- Squad coordinates attacks via shared target information
- Loadout-specific tactics (close vs distance preference)
- Flanking forces player to manage multiple angles
- Doomed bots retreat realistically, allowing finishes
- Combat strafing makes bots harder to hit
- Friendly bots provide meaningful support

### Result
3v1 gameplay becomes challenging and tactical, not trivial.

## Code Location Reference

| Feature | Lines | Method |
|---------|-------|--------|
| Constructor additions | 1990-2024 | `constructor()` |
| Range preference | 2013-2024 | `getLoadoutRangePreference()` |
| Retreat behavior | 2043-2044 | `update()` |
| Strafe management | 2056-2061 | `update()` |
| Flanking logic | 2078-2087 | `update()` |
| Combat strafing | 2090-2094 | `update()` |
| Firing with range check | 2142-2162 | `update()` |
| Squad coordination | 2181-2196 | `findTarget()` |
| Squad target check | 2243-2247 | `findTarget()` |
| Memory fallback | 2200-2212 | `findTarget()` |
| Friendly support | 2221-2233 | `findTarget()` |
| Navigation fallback | 2218-2236 | `findTarget()` |
| Corridor pathfinding | 2240-2271 | `navigateToEnemyTerritory()` |

## Testing Notes

Key behaviors to test in-game:

1. **Squad Coordination**: Hide from 1 bot while visible to another; others should hunt from shared intel
2. **Flanking**: Flank bots should approach from sides while engage bots push front
3. **Range Preference**: SCORCH should charge; NORTHSTAR should keep distance
4. **Strafing**: Bots should move unpredictably left/right during combat
5. **Doomed Retreat**: Low-health bots should flee and stop shooting
6. **Corridor Navigation**: Bots should move toward enemy spawn when unaware of player
7. **Friendly Support**: Ally bots should stay near player and follow into combat
8. **Memory Decay**: Bots should hunt player's last position for 5 seconds if LOS lost

## Future Enhancement Ideas

- Add formation movement (bots stay within X units of each other)
- Implement cover selection (prefer corridor points with obstructions)
- Add role-specific firing patterns (flankers suppress, engage bots push)
- Implement target priority (lowest health enemy first)
- Add bait tactics (flanker draws fire while engage bots push)
- Squad size scaling (more bots at high difficulty)
