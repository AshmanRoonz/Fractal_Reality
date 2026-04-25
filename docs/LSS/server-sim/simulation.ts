/*
  LSS server-sim ; gameplay core (v8.9)
  +  SDF-based collision: replaces binary pointInLevel containment with a
     graded signed distance (rooms blended via smooth-min, tunnels hard-min'd
     against rooms). Resolver has three bands: outside (hard inward push),
     touching wall (clamp + bounce), and clear (no-op). Smooth at room-tunnel
     joins; no more discontinuity at the room sphere boundary.
  +  respawnAllPlayers() called on map rotation so peers don't land outside.
  +  ability framework: per-slot cooldowns + active timers, dispatched per loadout.
  +  SLAYER Phase Dash (instant forward teleport).
  +  PUNCTURE Afterburner (timed speed boost).
  +  hit and kill events in snapshot for shooter-credited markers.
  +  loadouts + chassis stats applied per-player.
  +  full match state machine: select <-> warmup -> playing -> roundEnd.
  +  set-loadout / switch-team / set-ready actions.
  +  added Bot type with chase-and-shoot AI; bots fill 3v3 when humans short.
  +  added Projectile type, fire input handling, damage, death, respawn.
  +  bots find nearest enemy, face them, fire on alignment.
  +  kill/death tracking on Player and Bot; credited via projectile owner.

  Pure JS, no DOM, no Three.js. The same module would run identically in
  Node, Bun, or a browser. The server imports it and runs tick() at 64 Hz;
  clients import nothing from here in v8.0 (they just render received
  state). v8.x can later use this same module for client-side prediction.

  Design:
    - State is a plain object (the substrate). JSON-serializable.
    - tick(state, inputs, dt) advances state in place.
    - Inputs are per-peer; server collects each peer's latest input each
      frame. Clients send inputs at their render rate; server consumes the
      most recent set.

  v8.0 scope: player movement + AABB collision + bounds clamping. No bots,
  no projectiles, no abilities, no damage. Verifies that two browsers can
  see each other moving in one authoritative arena.
*/

import type { Level, Vec3, AABB, Room, Tunnel } from './level.ts';
import { pointInLevel, worldSDFAt, sdfNormal } from './level.ts';
import { LOADOUTS, CHASSIS, getLoadout, getChassis, LOADOUT_KEYS, DEFAULT_LOADOUT, type LoadoutKey, type ChassisKey } from './loadouts.ts';

// ---- Types ----

export const TEAM_A = 2;
export const TEAM_B = 3;

export interface PlayerInput {
  forward: number;   // -1..1, W/S
  right:   number;   // -1..1, D/A
  up:      number;   // -1..1, Space/Ctrl (vertical thrust)
  yaw:     number;   // radians ; absolute mouse-driven heading
  pitch:   number;   // radians ; clamped to ±π/2 elsewhere
  fire:    boolean;
  // v8.8: ability key edges (true on the frame the key was pressed).
  // 0 = Q (offensive slot), 1 = E (defensive slot), 2 = F (utility slot), 3 = V (core).
  abilityPress: number | null;
  tick?:   number;
}

export interface Player {
  id: number;
  peerId: string;
  team: number;
  loadoutKey: string | null;
  alive: boolean;
  ready: boolean;              // true once player has clicked READY in lobby
  position: Vec3;
  velocity: Vec3;
  yaw: number;
  pitch: number;
  health: number;
  maxHealth: number;
  shield: number;
  maxShield: number;
  fireTimer: number;
  prevFire: boolean;
  deathTime: number;
  kills: number;
  deaths: number;
  // v8.4: chassis-derived stats (set on commitLoadout)
  accel: number;
  maxSpeed: number;
  weaponDamage: number;
  weaponFireRate: number;
  // v8.8: ability state (3 abilities + 1 core, indexed 0..3)
  abilityCooldowns: number[];      // seconds remaining per slot
  abilityActive: boolean[];        // true while a duration ability is up
  abilityTimers: number[];         // remaining duration if active
  // PUNCTURE Afterburner: speed multiplier while active.
  afterburnerMult: number;
}

export interface Bot {
  id: number;
  team: number;
  loadoutKey: string;
  alive: boolean;
  position: Vec3;
  velocity: Vec3;
  yaw: number;
  pitch: number;
  health: number;
  maxHealth: number;
  shield: number;
  maxShield: number;
  fireTimer: number;
  deathTime: number;
  kills: number;
  deaths: number;
  // chassis-derived
  accel: number;
  maxSpeed: number;
  weaponDamage: number;
  weaponFireRate: number;
  // AI state ; not part of the wire snapshot.
  aiTarget: Vec3 | null;
  aiTimer: number;
  aiTargetType: 'player' | 'bot' | null;
  aiTargetId: number | null;
}

export interface Projectile {
  id: number;
  ownerType: 'player' | 'bot';
  ownerId: number;          // entity id of firing player or bot
  ownerTeam: number;        // for friendly-fire prevention
  position: Vec3;
  velocity: Vec3;
  damage: number;
  age: number;
  lifetime: number;
  color: number;            // packed 0xRRGGBB hint for the client
}

export interface Match {
  state: 'select' | 'warmup' | 'playing' | 'roundEnd';
  warmupTimer: number;
  roundTimer: number;
  scoreA: number;
  scoreB: number;
  currentRound: number;
  selectedMap: string;
  seed: number;
}

export interface SimState {
  tick: number;
  time: number;
  match: Match;
  players: Map<string, Player>;   // keyed by peerId for fast lookup
  bots: Map<number, Bot>;         // keyed by id
  projectiles: Map<number, Projectile>;
  events: SimEvent[];               // cleared after each broadcast
  level: Level;
  nextEntityId: number;
}

// v8.6: hit/kill events surfaced to clients so they can play markers.
export interface SimEvent {
  type: 'hit' | 'kill';
  shooterType: 'player' | 'bot';
  shooterId: number;
  shooterPeerId?: string;
  targetType: 'player' | 'bot';
  targetId: number;
  targetPeerId?: string;
  damage: number;
  time: number;
}

// ---- Tunables ----

const PLAYER_RADIUS = 60;          // collision sphere radius
const ACCEL = 1500;                 // units / s^2
const MAX_SPEED = 600;              // units / s
const DAMPING = 4;                  // velocity decay per second when no input
const ROUND_TIME = 180;
const WARMUP_TIME = 10;
const TEAM_SIZE = 3;
const BOT_AI_RETARGET_INTERVAL = 4.0;   // seconds between AI target picks
const BOT_TARGET_REACH_DIST = 200;       // pick new target when within this much

// v8.2: combat tunables
const FIRE_RATE = 0.18;         // seconds between shots (~5.5 shots/sec)
const PROJ_SPEED = 1800;        // units / s
const PROJ_LIFETIME = 3.0;      // seconds
const PROJ_DAMAGE = 250;        // hp per hit
const PLAYER_HIT_RADIUS = 80;   // sphere radius for projectile-vs-ship hit
const RESPAWN_DELAY = 5.0;      // seconds dead before respawn

// v8.3: bot AI tunables
const BOT_FIRE_RATE = 0.30;        // bots fire slower than players
const BOT_SIGHT_RANGE = 2500;       // max distance to acquire targets
const BOT_OPTIMAL_RANGE = 900;      // ideal stand-off distance
const BOT_FIRE_DOT_THRESHOLD = 0.97; // alignment required before firing
const BOT_RETARGET_INTERVAL = 1.5;  // seconds between target re-evaluation
const BOT_DAMAGE_MULT = 0.6;        // bot projectiles do 60% damage

// ---- Initial state ----

export function createSim(level: Level): SimState {
  return {
    tick: 0,
    time: 0,
    match: {
      state: 'select',
      warmupTimer: 0,
      roundTimer: 0,
      scoreA: 0,
      scoreB: 0,
      currentRound: 1,
      selectedMap: level.name,
      seed: 0,
    },
    players: new Map(),
    bots: new Map(),
    projectiles: new Map(),
    events: [],
    level,
    nextEntityId: 1,
  };
}

export function addPlayer(state: SimState, peerId: string, team: number): Player {
  const spawnPool = team === TEAM_B ? state.level.spawnB : state.level.spawnA;
  const sp = spawnPool[Math.floor(Math.random() * spawnPool.length)];
  // Default chassis = CORVETTE until the player picks a loadout in the lobby.
  const ch = CHASSIS.CORVETTE;
  const player: Player = {
    id: state.nextEntityId++,
    peerId,
    team,
    loadoutKey: null,
    alive: true,
    ready: false,
    position: { x: sp.x, y: sp.y, z: sp.z },
    velocity: { x: 0, y: 0, z: 0 },
    yaw: 0, pitch: 0,
    health: ch.maxHealth,
    maxHealth: ch.maxHealth,
    shield: ch.maxShield,
    maxShield: ch.maxShield,
    fireTimer: 0,
    prevFire: false,
    deathTime: 0,
    kills: 0,
    deaths: 0,
    accel: ch.acceleration,
    maxSpeed: ch.flightSpeed,
    weaponDamage: 250,
    weaponFireRate: 0.18,
    abilityCooldowns: [0, 0, 0, 0],
    abilityActive: [false, false, false, false],
    abilityTimers: [0, 0, 0, 0],
    afterburnerMult: 1.0,
  };
  state.players.set(peerId, player);
  return player;
}

export function removePlayer(state: SimState, peerId: string): void {
  state.players.delete(peerId);
}

// v8.4: apply chassis + weapon stats to a player when they pick a loadout.
// Resets HP/shield to the chassis max so changes between rounds give them
// a fresh ship; the lobby UI reflects this.
export function applyPlayerLoadout(player: Player, loadoutKey: string | null): void {
  const ld = getLoadout(loadoutKey);
  const ch = getChassis(ld.chassis);
  player.loadoutKey = ld.name;
  player.maxHealth = ch.maxHealth;
  player.health = ch.maxHealth;
  player.maxShield = ch.maxShield;
  player.shield = ch.maxShield;
  player.accel = ch.acceleration;
  player.maxSpeed = ch.flightSpeed;
  player.weaponDamage = ld.weapon.damage;
  player.weaponFireRate = ld.weapon.fireRate;
  // Reset combat timers so a fresh-loadout player isn't mid-cooldown.
  player.fireTimer = 0;
  player.prevFire = false;
  // v8.8: reset ability state on loadout change.
  for (let i = 0; i < 4; i++) {
    player.abilityCooldowns[i] = 0;
    player.abilityActive[i] = false;
    player.abilityTimers[i] = 0;
  }
  player.afterburnerMult = 1.0;
}

// v8.4: switch a player to the other team. No-op if destination is full.
export function switchPlayerTeam(state: SimState, player: Player): boolean {
  const dest = player.team === TEAM_A ? TEAM_B : TEAM_A;
  let count = 0;
  for (const p of state.players.values()) {
    if (p !== player && p.team === dest) count++;
  }
  if (count >= TEAM_SIZE) return false;
  player.team = dest;
  return true;
}

// Assign default loadout to any player who hasn't picked one. Useful when
// the match starts with someone who didn't engage the lobby.
export function ensurePlayerHasLoadout(player: Player): void {
  if (!player.loadoutKey) applyPlayerLoadout(player, DEFAULT_LOADOUT);
}

// v8.8.1: reposition + reset every player at the start of a new match. Use
// the level's CURRENT spawn pool so they land inside the new envelope. Also
// resets HP/shield to chassis max so they start the round at full strength.
export function respawnAllPlayers(state: SimState): void {
  for (const p of state.players.values()) {
    _respawnPlayer(p, state.level);
  }
}

// ---- Bot lifecycle ----

const _BOT_LOADOUTS_A = ['PUNCTURE', 'BLASTER', 'SYPHON'];
const _BOT_LOADOUTS_B = ['PYRO', 'SLAYER', 'TRACKER'];

function _humanCount(state: SimState, team: number): number {
  let n = 0;
  for (const p of state.players.values()) {
    if (p.team === team) n++;
  }
  return n;
}

export function spawnBotsToFillTeams(state: SimState): void {
  const aHumans = _humanCount(state, TEAM_A);
  const bHumans = _humanCount(state, TEAM_B);
  const needA = Math.max(0, TEAM_SIZE - aHumans);
  const needB = Math.max(0, TEAM_SIZE - bHumans);
  // Friendly bots
  for (let i = 0; i < needA; i++) {
    spawnBot(state, TEAM_A, _BOT_LOADOUTS_A[i % _BOT_LOADOUTS_A.length]);
  }
  // Enemy bots
  for (let i = 0; i < needB; i++) {
    spawnBot(state, TEAM_B, _BOT_LOADOUTS_B[i % _BOT_LOADOUTS_B.length]);
  }
}

export function spawnBot(state: SimState, team: number, loadoutKey: string): Bot {
  const spawnPool = team === TEAM_B ? state.level.spawnB : state.level.spawnA;
  const sp = spawnPool[Math.floor(Math.random() * spawnPool.length)];
  const id = state.nextEntityId++;
  const ld = getLoadout(loadoutKey);
  const ch = getChassis(ld.chassis);
  const bot: Bot = {
    id, team, loadoutKey,
    alive: true,
    position: { x: sp.x + (Math.random() - 0.5) * 100, y: sp.y, z: sp.z + (Math.random() - 0.5) * 100 },
    velocity: { x: 0, y: 0, z: 0 },
    yaw: 0, pitch: 0,
    health: ch.maxHealth, maxHealth: ch.maxHealth,
    shield: ch.maxShield, maxShield: ch.maxShield,
    fireTimer: 0,
    deathTime: 0,
    kills: 0,
    deaths: 0,
    accel: ch.acceleration * 0.85,        // bots a bit slower than humans
    maxSpeed: ch.flightSpeed * 0.85,
    weaponDamage: ld.weapon.damage,
    weaponFireRate: ld.weapon.fireRate,
    aiTarget: null, aiTimer: 0,
    aiTargetType: null, aiTargetId: null,
  };
  state.bots.set(id, bot);
  return bot;
}

export function clearAllBots(state: SimState): void {
  state.bots.clear();
}

// v8.3: chase-and-shoot AI. Bot finds the nearest live enemy, flies toward
// optimal stand-off range, faces target, fires when aligned.

function _findNearestEnemy(bot: Bot, state: SimState): { type: 'player' | 'bot'; id: number; pos: Vec3; alive: boolean } | null {
  let best: { type: 'player' | 'bot'; id: number; pos: Vec3; alive: boolean } | null = null;
  let bestDist = BOT_SIGHT_RANGE;
  for (const p of state.players.values()) {
    if (!p.alive) continue;
    if (p.team === bot.team) continue;
    const dx = p.position.x - bot.position.x;
    const dy = p.position.y - bot.position.y;
    const dz = p.position.z - bot.position.z;
    const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (d < bestDist) { best = { type: 'player', id: p.id, pos: p.position, alive: true }; bestDist = d; }
  }
  for (const b of state.bots.values()) {
    if (!b.alive) continue;
    if (b.team === bot.team) continue;
    if (b.id === bot.id) continue;
    const dx = b.position.x - bot.position.x;
    const dy = b.position.y - bot.position.y;
    const dz = b.position.z - bot.position.z;
    const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (d < bestDist) { best = { type: 'bot', id: b.id, pos: b.position, alive: true }; bestDist = d; }
  }
  return best;
}

function _tickBotAI(bot: Bot, state: SimState, dt: number): void {
  if (!bot.alive) return;
  bot.aiTimer -= dt;

  // Periodically re-evaluate target.
  if (bot.aiTimer <= 0) {
    const target = _findNearestEnemy(bot, state);
    if (target) {
      bot.aiTargetType = target.type;
      bot.aiTargetId = target.id;
    } else {
      bot.aiTargetType = null;
      bot.aiTargetId = null;
    }
    bot.aiTimer = BOT_RETARGET_INTERVAL;
  }

  // Resolve target position from id (in case it moved or died).
  let targetPos: Vec3 | null = null;
  let targetAlive = false;
  if (bot.aiTargetType === 'player' && bot.aiTargetId != null) {
    for (const p of state.players.values()) {
      if (p.id === bot.aiTargetId) { targetPos = p.position; targetAlive = p.alive; break; }
    }
  } else if (bot.aiTargetType === 'bot' && bot.aiTargetId != null) {
    const b = state.bots.get(bot.aiTargetId);
    if (b) { targetPos = b.position; targetAlive = b.alive; }
  }

  // No target: drift to a stop.
  if (!targetPos || !targetAlive) {
    const damp = Math.exp(-DAMPING * dt);
    bot.velocity.x *= damp; bot.velocity.y *= damp; bot.velocity.z *= damp;
    return;
  }

  // Face target.
  const tx = targetPos.x - bot.position.x;
  const ty = targetPos.y - bot.position.y;
  const tz = targetPos.z - bot.position.z;
  const dist = Math.sqrt(tx * tx + ty * ty + tz * tz);
  if (dist < 0.01) return;
  const tnx = tx / dist, tny = ty / dist, tnz = tz / dist;
  bot.yaw = Math.atan2(-tnx, -tnz);
  bot.pitch = Math.atan2(tny, Math.sqrt(tnx * tnx + tnz * tnz));

  // Steering: approach if far, retreat if too close, hold otherwise.
  const accel = bot.accel;
  let steerX = 0, steerY = 0, steerZ = 0;
  if (dist > BOT_OPTIMAL_RANGE * 1.2) {
    // Approach
    steerX = tnx; steerY = tny; steerZ = tnz;
  } else if (dist < BOT_OPTIMAL_RANGE * 0.6) {
    // Retreat
    steerX = -tnx; steerY = -tny; steerZ = -tnz;
  } else {
    // Strafe orthogonally so we're not a sitting duck.
    // Right vector relative to facing target: cross(up, facing).
    steerX = -tnz;
    steerY = 0;
    steerZ = tnx;
    // Pseudo-random side: vary by id so two bots don't strafe the same way.
    if ((bot.id & 1) === 0) { steerX = -steerX; steerZ = -steerZ; }
  }
  bot.velocity.x += steerX * accel * dt;
  bot.velocity.y += steerY * accel * dt;
  bot.velocity.z += steerZ * accel * dt;

  // Clamp speed
  const speed = Math.sqrt(bot.velocity.x ** 2 + bot.velocity.y ** 2 + bot.velocity.z ** 2);
  if (speed > bot.maxSpeed) {
    const k = bot.maxSpeed / speed;
    bot.velocity.x *= k; bot.velocity.y *= k; bot.velocity.z *= k;
  }

  // Fire if aligned. Bots only fire when a match is in playing state.
  if (state.match.state !== 'playing') return;
  if (bot.fireTimer > 0) return;
  // Compare current facing (from yaw/pitch) to direction-to-target.
  const facing = _facingDir(bot.yaw, bot.pitch);
  const dot = facing.x * tnx + facing.y * tny + facing.z * tnz;
  if (dot >= BOT_FIRE_DOT_THRESHOLD) {
    const origin = {
      x: bot.position.x + facing.x * 80,
      y: bot.position.y + 30 + facing.y * 80,
      z: bot.position.z + facing.z * 80,
    };
    const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, facing);
    proj.damage = bot.weaponDamage * BOT_DAMAGE_MULT;
    bot.fireTimer = Math.max(BOT_FIRE_RATE, bot.weaponFireRate * 1.6);
  }
}

// ---- Projectiles + combat (v8.2) ----

function _spawnProjectile(state: SimState, ownerType: 'player' | 'bot', ownerId: number, ownerTeam: number, origin: Vec3, dir: Vec3): Projectile {
  const id = state.nextEntityId++;
  const proj: Projectile = {
    id, ownerType, ownerId, ownerTeam,
    position: { x: origin.x, y: origin.y, z: origin.z },
    velocity: { x: dir.x * PROJ_SPEED, y: dir.y * PROJ_SPEED, z: dir.z * PROJ_SPEED },
    damage: PROJ_DAMAGE,
    age: 0,
    lifetime: PROJ_LIFETIME,
    color: ownerTeam === TEAM_B ? 0x66ff66 : 0xff6666,
  };
  state.projectiles.set(id, proj);
  return proj;
}

// Compute facing direction from yaw + pitch (matching the camera convention
// in the thin client: yaw=0 looks toward -Z, +yaw turns counter-clockwise
// when viewed from above).
function _facingDir(yaw: number, pitch: number): Vec3 {
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const cp = Math.cos(pitch), sp = Math.sin(pitch);
  return { x: -sy * cp, y: sp, z: -cy * cp };
}

// Sphere vs AABB intersection test for projectile-vs-wall (cheap).
function _projectileHitsBox(p: Projectile, box: AABB): boolean {
  const cx = Math.max(box.min.x, Math.min(p.position.x, box.max.x));
  const cy = Math.max(box.min.y, Math.min(p.position.y, box.max.y));
  const cz = Math.max(box.min.z, Math.min(p.position.z, box.max.z));
  const dx = p.position.x - cx, dy = p.position.y - cy, dz = p.position.z - cz;
  return (dx * dx + dy * dy + dz * dz) < 16 * 16; // small projectile radius
}

function _projectileHitsEntity(p: Projectile, pos: Vec3, hitR: number): boolean {
  const dx = p.position.x - pos.x;
  const dy = p.position.y - pos.y;
  const dz = p.position.z - pos.z;
  return (dx * dx + dy * dy + dz * dz) < hitR * hitR;
}

function _killEntity(ent: { alive: boolean; deathTime: number; velocity: Vec3; deaths: number }, time: number): void {
  ent.alive = false;
  ent.deathTime = time;
  ent.velocity.x = 0; ent.velocity.y = 0; ent.velocity.z = 0;
  ent.deaths = (ent.deaths || 0) + 1;
}

// Lookup a killer by ownerType+ownerId and credit a kill.
function _creditKill(state: SimState, ownerType: 'player' | 'bot', ownerId: number): void {
  if (ownerType === 'player') {
    for (const p of state.players.values()) {
      if (p.id === ownerId) { p.kills = (p.kills || 0) + 1; return; }
    }
  } else {
    const b = state.bots.get(ownerId);
    if (b) b.kills = (b.kills || 0) + 1;
  }
}

function _respawnPlayer(player: Player, level: Level): void {
  const pool = player.team === TEAM_B ? level.spawnB : level.spawnA;
  const sp = pool[Math.floor(Math.random() * pool.length)];
  player.position.x = sp.x; player.position.y = sp.y; player.position.z = sp.z;
  player.velocity.x = 0; player.velocity.y = 0; player.velocity.z = 0;
  player.health = player.maxHealth;
  player.shield = player.maxShield;
  player.alive = true;
  player.fireTimer = 0;
}

function _respawnBot(bot: Bot, level: Level): void {
  const pool = bot.team === TEAM_B ? level.spawnB : level.spawnA;
  const sp = pool[Math.floor(Math.random() * pool.length)];
  bot.position.x = sp.x + (Math.random() - 0.5) * 100;
  bot.position.y = sp.y;
  bot.position.z = sp.z + (Math.random() - 0.5) * 100;
  bot.velocity.x = 0; bot.velocity.y = 0; bot.velocity.z = 0;
  bot.health = bot.maxHealth;
  bot.shield = bot.maxShield;
  bot.alive = true;
  bot.aiTarget = null; bot.aiTimer = 0;
}


function _recordHit(state: SimState, p: Projectile, target: Player | Bot, killed: boolean): void {
  const isPlayerTarget = (target as Player).peerId !== undefined;
  // Lookup shooter peerId for clean attribution.
  let shooterPeerId: string | undefined;
  if (p.ownerType === 'player') {
    for (const pl of state.players.values()) {
      if (pl.id === p.ownerId) { shooterPeerId = pl.peerId; break; }
    }
  }
  state.events.push({
    type: killed ? 'kill' : 'hit',
    shooterType: p.ownerType,
    shooterId: p.ownerId,
    shooterPeerId,
    targetType: isPlayerTarget ? 'player' : 'bot',
    targetId: (target as any).id,
    targetPeerId: isPlayerTarget ? (target as Player).peerId : undefined,
    damage: p.damage,
    time: state.time,
  });
}

function _tickProjectiles(state: SimState, dt: number): void {
  const dead: number[] = [];
  for (const p of state.projectiles.values()) {
    p.age += dt;
    if (p.age >= p.lifetime) { dead.push(p.id); continue; }
    p.position.x += p.velocity.x * dt;
    p.position.y += p.velocity.y * dt;
    p.position.z += p.velocity.z * dt;

    // Wall hit? v8.7: projectile dies if it leaves the room+tunnel envelope.
    let hit = false;
    if (!pointInLevel(p.position, state.level)) {
      hit = true;
    } else {
      for (let i = 0; i < state.level.obstacles.length; i++) {
        if (_projectileHitsBox(p, state.level.obstacles[i])) { hit = true; break; }
      }
    }
    if (hit) { dead.push(p.id); continue; }

    // Player hit? Skip own-team (no friendly fire).
    let consumed = false;
    for (const player of state.players.values()) {
      if (!player.alive) continue;
      if (player.team === p.ownerTeam) continue;
      if (player.id === p.ownerId) continue;
      if (_projectileHitsEntity(p, player.position, PLAYER_HIT_RADIUS)) {
        player.health -= p.damage;
        const killed = player.health <= 0;
        if (killed) {
          player.health = 0;
          _killEntity(player, state.time);
          _creditKill(state, p.ownerType, p.ownerId);
        }
        _recordHit(state, p, player, killed);
        consumed = true; break;
      }
    }
    if (consumed) { dead.push(p.id); continue; }

    // Bot hit?
    for (const bot of state.bots.values()) {
      if (!bot.alive) continue;
      if (bot.team === p.ownerTeam) continue;
      if (bot.id === p.ownerId) continue;
      if (_projectileHitsEntity(p, bot.position, PLAYER_HIT_RADIUS)) {
        bot.health -= p.damage;
        const killed = bot.health <= 0;
        if (killed) {
          bot.health = 0;
          _killEntity(bot, state.time);
          _creditKill(state, p.ownerType, p.ownerId);
        }
        _recordHit(state, p, bot, killed);
        consumed = true; break;
      }
    }
    if (consumed) { dead.push(p.id); continue; }
  }
  for (const id of dead) state.projectiles.delete(id);
}

// ---- Abilities (v8.8) ----

// Per-loadout cooldown table keyed by slot (0..3 = Q,E,F,V).
const ABILITY_COOLDOWNS: Record<string, number[]> = {
  VORTEX:   [10, 0,  12, 60],
  PYRO:     [10, 0,  15, 60],
  PUNCTURE: [ 8, 10, 12, 60],
  SLAYER:   [ 8, 0,   6, 60],
  TRACKER:  [ 6, 14, 12, 60],
  BLASTER:  [ 8, 0,   2, 60],
  SYPHON:   [ 6, 8,  12, 60],
};

const ABILITY_DURATIONS: Record<string, number[]> = {
  VORTEX:   [0.5, 999, 12, 4],
  PYRO:     [6,   5,   10, 2],
  PUNCTURE: [0.3, 3,   4,  5],
  SLAYER:   [0.1, 999, 0.2, 5],
  TRACKER:  [0.5, 0.1, 8,  3],
  BLASTER:  [0.1, 999, 999, 10],
  SYPHON:   [0.3, 2,   0.1, 12],
};

// Try to activate ability `slot` for `player`. Honors per-loadout cooldown.
// Returns true if activated. v8.8 implements SLAYER Phase Dash (slot 2) and
// PUNCTURE Afterburner (slot 1); other loadouts/slots no-op for now.
function _activatePlayerAbility(player: Player, slot: number): boolean {
  if (slot < 0 || slot > 3) return false;
  if (player.abilityCooldowns[slot] > 0) return false;
  if (!player.alive) return false;
  const lk = player.loadoutKey || '';
  const cdTable = ABILITY_COOLDOWNS[lk];
  const durTable = ABILITY_DURATIONS[lk];
  if (!cdTable || !durTable) return false;

  // Dispatch by loadout + slot.
  if (lk === 'SLAYER' && slot === 2) {
    // Phase Dash: instant forward teleport along facing direction.
    const dir = _facingDir(player.yaw, player.pitch);
    const DASH_DIST = 700;
    player.position.x += dir.x * DASH_DIST;
    player.position.y += dir.y * DASH_DIST;
    player.position.z += dir.z * DASH_DIST;
    // Velocity is preserved so you keep momentum after the dash.
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PUNCTURE' && slot === 1) {
    // Afterburner: speed multiplier for the duration.
    player.afterburnerMult = 2.0;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // Unimplemented: still consume the cooldown so the HUD reflects a press
  // (avoids spam during testing). Comment out if undesired.
  // For v8.8 leave unimplemented as no-op; HUD shows it as ready until a
  // server-side handler is added in v8.9+.
  return false;
}

// Tick ability cooldowns + timers for a player.
function _tickPlayerAbilities(player: Player, dt: number): void {
  for (let i = 0; i < 4; i++) {
    if (player.abilityCooldowns[i] > 0) {
      player.abilityCooldowns[i] = Math.max(0, player.abilityCooldowns[i] - dt);
    }
    if (player.abilityActive[i]) {
      player.abilityTimers[i] -= dt;
      if (player.abilityTimers[i] <= 0) {
        player.abilityActive[i] = false;
        player.abilityTimers[i] = 0;
        _onAbilityExpire(player, i);
      }
    }
  }
}

function _onAbilityExpire(player: Player, slot: number): void {
  const lk = player.loadoutKey || '';
  if (lk === 'PUNCTURE' && slot === 1) {
    player.afterburnerMult = 1.0;
  }
  // (SLAYER Phase Dash is instantaneous; no expire side-effect.)
}

// ---- Tick ----

const NO_INPUT: PlayerInput = { forward: 0, right: 0, up: 0, yaw: 0, pitch: 0, fire: false, abilityPress: null };

export function tick(state: SimState, inputs: Map<string, PlayerInput>, dt: number): void {
  state.tick++;
  state.time += dt;

  // 1) Apply inputs to each player
  // v8.4: gameplay-affecting inputs only fire during 'warmup' (movement only,
  // no firing) and 'playing'. In 'select' (lobby) and 'roundEnd' players are
  // frozen so inputs don't ghost-fire bullets through the scoreboard.
  const inGameplay = state.match.state === 'warmup' || state.match.state === 'playing';
  const canFire = state.match.state === 'playing';
  for (const player of state.players.values()) {
    const input = inputs.get(player.peerId) || NO_INPUT;

    if (!inGameplay) {
      // Lobby / round-end: keep player frozen at last position so the
      // scoreboard / lobby UI shows the right thing. Apply orientation so
      // the client's camera stays oriented during the wait.
      player.velocity.x = 0; player.velocity.y = 0; player.velocity.z = 0;
      player.yaw = input.yaw;
      player.pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, input.pitch));
      player.prevFire = !!input.fire;
      continue;
    }

    if (!player.alive) {
      if (state.time - player.deathTime >= RESPAWN_DELAY) {
        _respawnPlayer(player, state.level);
      } else {
        player.yaw = input.yaw;
        player.pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, input.pitch));
        player.prevFire = !!input.fire;
        continue;
      }
    }

    player.yaw = input.yaw;
    player.pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, input.pitch));

    player.fireTimer = Math.max(0, player.fireTimer - dt);
    if (canFire && input.fire && !player.prevFire && player.fireTimer <= 0) {
      const dir = _facingDir(player.yaw, player.pitch);
      const origin = {
        x: player.position.x + dir.x * 80,
        y: player.position.y + 30 + dir.y * 80,
        z: player.position.z + dir.z * 80,
      };
      const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, dir);
      proj.damage = player.weaponDamage;
      player.fireTimer = player.weaponFireRate;
    }
    player.prevFire = !!input.fire;

    // v8.8: ability activation + tick. Only during 'playing' to avoid
    // spurious activations during warmup.
    _tickPlayerAbilities(player, dt);
    if (canFire && input.abilityPress != null) {
      _activatePlayerAbility(player, input.abilityPress | 0);
    }

    // Build local-axis movement. forward = -Z when facing yaw=0; right = +X.
    const cy = Math.cos(player.yaw), sy = Math.sin(player.yaw);
    // Forward vector (yaw only; pitch is for aim, not movement, in this game)
    const forwardX = -sy, forwardZ = -cy;
    const rightX = cy, rightZ = -sy;

    const intentX = forwardX * input.forward + rightX * input.right;
    const intentZ = forwardZ * input.forward + rightZ * input.right;
    const intentY = input.up;

    // Normalize 2D-plane intent so diagonal movement isn't faster.
    const planeMag = Math.sqrt(intentX * intentX + intentZ * intentZ);
    const nx = planeMag > 0 ? intentX / planeMag : 0;
    const nz = planeMag > 0 ? intentZ / planeMag : 0;
    const planeIntent = Math.min(1, planeMag);

    // Accelerate toward intent (chassis-driven)
    const tdt = player.accel * dt;
    player.velocity.x += nx * planeIntent * tdt;
    player.velocity.z += nz * planeIntent * tdt;
    player.velocity.y += intentY * tdt;

    // Damping when no input (or partial input)
    const dampFactor = Math.exp(-DAMPING * dt);
    if (planeMag < 0.01) { player.velocity.x *= dampFactor; player.velocity.z *= dampFactor; }
    if (Math.abs(input.up) < 0.01) { player.velocity.y *= dampFactor; }

    // Clamp to chassis max speed
    const sx = player.velocity.x, sy2 = player.velocity.y, sz = player.velocity.z;
    const speed = Math.sqrt(sx * sx + sy2 * sy2 + sz * sz);
    const effectiveMax = player.maxSpeed * player.afterburnerMult;
    if (speed > effectiveMax) {
      const k = effectiveMax / speed;
      player.velocity.x *= k; player.velocity.y *= k; player.velocity.z *= k;
    }
  }

  // 2) Integrate positions and resolve collision
  for (const player of state.players.values()) {
    if (!player.alive) continue;
    const stepX = player.velocity.x * dt;
    const stepY = player.velocity.y * dt;
    const stepZ = player.velocity.z * dt;
    player.position.x += stepX;
    player.position.y += stepY;
    player.position.z += stepZ;
    resolveCollision(player, state.level);
  }

  // 3) Bot AI + integration
  for (const bot of state.bots.values()) {
    if (!bot.alive) {
      if (state.time - bot.deathTime >= RESPAWN_DELAY) {
        _respawnBot(bot, state.level);
      }
      continue;
    }
    bot.fireTimer = Math.max(0, bot.fireTimer - dt);
    _tickBotAI(bot, state, dt);
    bot.position.x += bot.velocity.x * dt;
    bot.position.y += bot.velocity.y * dt;
    bot.position.z += bot.velocity.z * dt;
    _resolveBotCollision(bot, state.level);
  }

  // 3b) Projectile motion + collision + damage
  _tickProjectiles(state, dt);

  // 4) Match state machine
  if (state.match.state === 'select') {
    // Lobby ; main.ts decides when to transition to 'warmup' (when all
    // ready). The simulation just holds.
  } else if (state.match.state === 'warmup') {
    state.match.warmupTimer = Math.max(0, state.match.warmupTimer - dt);
    if (state.match.warmupTimer <= 0) {
      state.match.state = 'playing';
      state.match.roundTimer = ROUND_TIME;
    }
  } else if (state.match.state === 'playing') {
    state.match.roundTimer = Math.max(0, state.match.roundTimer - dt);
    if (state.match.roundTimer <= 0) {
      state.match.state = 'roundEnd';
      // Reuse warmupTimer as the linger countdown.
      state.match.warmupTimer = ROUND_END_LINGER;
    }
  } else if (state.match.state === 'roundEnd') {
    state.match.warmupTimer = Math.max(0, state.match.warmupTimer - dt);
    if (state.match.warmupTimer <= 0) {
      state.match.state = 'select';
      state.match.currentRound++;
      // Clear ready on every player so they have to commit again.
      for (const p of state.players.values()) p.ready = false;
    }
  }
}

const ROUND_END_LINGER = 6;

// v8.9: SDF-based containment. Replaces the old binary pointInLevel check
// with a graded distance read; resolver has three bands depending on how
// close the entity is to the wall:
//
//   margin < 0          : entity is OUTSIDE the level. Hard inward push,
//                         strip outward velocity component (1.5x bounce).
//   0 <= margin < r     : entity is TOUCHING the wall. Clamp position so
//                         the collision sphere sits flush against the wall,
//                         strip outward velocity (1.05x bounce).
//   margin >= r         : entity has clearance; no-op.
//
// `margin` is `-worldSDF(p)` (positive when inside; equals signed depth from
// the wall). The inward normal is `-sdfNormal(p)`. Smooth at room-tunnel
// joints because worldSDF blends rooms and tunnels with sdfSmin.
//
// Scratch vector reused across calls so the hot path allocates nothing.
const _rcN: Vec3 = { x: 0, y: 0, z: 0 };

function _resolveSDF(pos: Vec3, vel: Vec3, radius: number, level: Level): void {
  const sdf = worldSDFAt(pos.x, pos.y, pos.z, level);
  const margin = -sdf;
  if (margin >= radius) return; // clear: nothing to do

  // sdfNormal points OUTWARD (toward higher SDF = toward wall and beyond).
  // We push INWARD, so we use the negation. Compute once, share between the
  // position correction and velocity bounce.
  sdfNormal(pos, level, _rcN);
  const nInX = -_rcN.x, nInY = -_rcN.y, nInZ = -_rcN.z;

  if (margin < 0) {
    // Outside the level. Hard push back inside; the +4 keeps us a touch
    // clear of the surface so the next tick doesn't re-trigger.
    const push = -margin + radius + 4;
    pos.x += nInX * push;
    pos.y += nInY * push;
    pos.z += nInZ * push;
    // vel.dot(inwardNormal) < 0 means velocity is heading further outward
    // (against the inward normal); strip that component with a small bounce.
    const vn = vel.x * nInX + vel.y * nInY + vel.z * nInZ;
    if (vn < 0) {
      vel.x -= nInX * vn * 1.5;
      vel.y -= nInY * vn * 1.5;
      vel.z -= nInZ * vn * 1.5;
    }
  } else {
    // Touching wall. Clamp so the collision sphere is just clear; bounce
    // the velocity component into the wall.
    const push = radius - margin + 2;
    pos.x += nInX * push;
    pos.y += nInY * push;
    pos.z += nInZ * push;
    const vn = vel.x * nInX + vel.y * nInY + vel.z * nInZ;
    if (vn < 0) {
      vel.x -= nInX * vn * 1.05;
      vel.y -= nInY * vn * 1.05;
      vel.z -= nInZ * vn * 1.05;
    }
  }
}

// AABB obstacle bumpers (used by both player and bot resolvers).
function _resolveAABBs(pos: Vec3, vel: Vec3, radius: number, obstacles: AABB[]): void {
  for (let i = 0; i < obstacles.length; i++) {
    const box = obstacles[i];
    const cx = Math.max(box.min.x, Math.min(pos.x, box.max.x));
    const cy = Math.max(box.min.y, Math.min(pos.y, box.max.y));
    const cz = Math.max(box.min.z, Math.min(pos.z, box.max.z));
    const dx = pos.x - cx, dy = pos.y - cy, dz = pos.z - cz;
    const d2 = dx * dx + dy * dy + dz * dz;
    if (d2 >= radius * radius) continue;
    const d = Math.sqrt(Math.max(d2, 0.0001));
    const push = (radius - d) / d;
    pos.x += dx * push;
    pos.y += dy * push;
    pos.z += dz * push;
    const vDotN = vel.x * dx + vel.y * dy + vel.z * dz;
    if (vDotN < 0) {
      const n2 = (dx * dx + dy * dy + dz * dz) || 1;
      const k = vDotN / n2;
      vel.x -= dx * k;
      vel.y -= dy * k;
      vel.z -= dz * k;
    }
  }
}

function resolveCollision(player: Player, level: Level): void {
  _resolveSDF(player.position, player.velocity, PLAYER_RADIUS, level);
  _resolveAABBs(player.position, player.velocity, PLAYER_RADIUS, level.obstacles);
}

function _resolveBotCollision(bot: Bot, level: Level): void {
  const r = PLAYER_RADIUS * 0.9;
  _resolveSDF(bot.position, bot.velocity, r, level);
  _resolveAABBs(bot.position, bot.velocity, r, level.obstacles);
}

// ---- Snapshot for the wire ----

export function snapshot(state: SimState) {
  // Plain objects only; no Maps. Each player record is small.
  const players: any[] = [];
  for (const p of state.players.values()) {
    players.push({
      id: p.id,
      peerId: p.peerId,
      team: p.team,
      loadoutKey: p.loadoutKey,
      alive: p.alive,
      position: { x: round1(p.position.x), y: round1(p.position.y), z: round1(p.position.z) },
      velocity: { x: round1(p.velocity.x), y: round1(p.velocity.y), z: round1(p.velocity.z) },
      yaw: round3(p.yaw),
      pitch: round3(p.pitch),
      health: p.health,
      maxHealth: p.maxHealth,
      shield: p.shield,
      maxShield: p.maxShield,
      ready: p.ready,
      kills: p.kills,
      deaths: p.deaths,
      abilityCooldowns: p.abilityCooldowns.slice(),
      abilityActive: p.abilityActive.slice(),
    });
  }
  // Bots: same shape as players except no peerId.
  const bots: any[] = [];
  for (const b of state.bots.values()) {
    bots.push({
      id: b.id,
      team: b.team,
      loadoutKey: b.loadoutKey,
      alive: b.alive,
      position: { x: round1(b.position.x), y: round1(b.position.y), z: round1(b.position.z) },
      velocity: { x: round1(b.velocity.x), y: round1(b.velocity.y), z: round1(b.velocity.z) },
      yaw: round3(b.yaw),
      pitch: round3(b.pitch),
      health: b.health,
      maxHealth: b.maxHealth,
      shield: b.shield,
      maxShield: b.maxShield,
      kills: b.kills,
      deaths: b.deaths,
    });
  }
  const projectiles: any[] = [];
  for (const p of state.projectiles.values()) {
    projectiles.push({
      id: p.id,
      ownerType: p.ownerType,
      ownerId: p.ownerId,
      ownerTeam: p.ownerTeam,
      position: { x: round1(p.position.x), y: round1(p.position.y), z: round1(p.position.z) },
      velocity: { x: round1(p.velocity.x), y: round1(p.velocity.y), z: round1(p.velocity.z) },
      color: p.color,
      age: round3(p.age),
      lifetime: p.lifetime,
    });
  }
  // v8.6: drain accumulated events into the snapshot. Clients use these
  // to play hit/kill markers; we clear them server-side so they only fire
  // once per event regardless of broadcast cadence.
  const events = state.events.slice();
  state.events.length = 0;
  return {
    tick: state.tick,
    time: round3(state.time),
    match: state.match,
    players,
    bots,
    projectiles,
    events,
  };
}

function round1(n: number) { return Math.round(n * 10) / 10; }
function round3(n: number) { return Math.round(n * 1000) / 1000; }

// Bring the match into 'select' state, used after roundEnd or on server boot.
export function resetMatch(state: SimState): void {
  state.match.state = 'select';
  state.match.warmupTimer = 0;
  state.match.roundTimer = 0;
  state.match.scoreA = 0;
  state.match.scoreB = 0;
  state.match.currentRound = 1;
}

// Begin the warmup phase. Server calls this when all peers are ready.
export function startMatch(state: SimState, seed: number, mapKey: string): void {
  state.match.state = 'warmup';
  state.match.warmupTimer = WARMUP_TIME;
  state.match.roundTimer = ROUND_TIME;
  state.match.seed = seed;
  state.match.selectedMap = mapKey;
  state.match.scoreA = 0;
  state.match.scoreB = 0;
  state.match.currentRound = 1;
}
