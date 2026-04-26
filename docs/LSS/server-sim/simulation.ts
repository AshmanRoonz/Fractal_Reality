/*
  LSS server-sim ; gameplay core (v8.30)
  +  v8.30 (destructibles): cluster obstacles spawned in non-spawn rooms at
     round start. Server-tracked HP; projectiles deduct + are consumed on
     contact. Cleared between rounds.
  +  v8.29 (stasis fields): pickup-style worldEffects spawned at round start;
     player contact triggers 3s stasis (immobilized + shield recharge).
     LSS line 12251-12305 (visual), 12442-12470 (logic).
  +  v8.28 (BLASTER spinup + mode switch): player.spinupTimer + spunUp gates
     fire for chassis with weapon.spinup > 0 (LSS line 8085-8090). Mode
     switch ability now sets blasterSwitchTimer + queues blasterPendingMode;
     stats swap on lockout expiry per LSS line 9863-9877.
  +  v8.23-v8.27 (remaining ability kits, simplified):
     SLAYER:  Arc Wave, Sword Block (passive damage reduction), Sword Core.
     VORTEX:  Laser Shot, Vortex Shield (passive), Trip Wire, Laser Core.
     PYRO:    Firewall, Thermal Shield (passive), Incendiary Trap, Flame Core.
     BLASTER: Power Shot, Gun Shield (passive), Mode Switch (placeholder),
              Smart Core.
     SYPHON:  Rocket Salvo, Energy Siphon (drain shield + heal + slow),
              Rearm (reset ability cooldowns), Upgrade Core (stacked buffs).
     All 28 chassis abilities now have server-side dispatch. Each marked
     // SIMPLIFIED: with LSS line citation; the homing/wall-collision/
     remote-guidance behaviors come back as we deepen ports later.
  +  v8.22 (PUNCTURE remaining): Cluster Missile (Q), Tether Trap (F using
     world-effects framework), Afterburner Core (V) ported from LSS lines
     8615-8623, 8890-8902, 9020-9055.
  +  v8.21 (world-effects framework): SimState gains worldEffects map;
     _tickWorldEffects handles area damage (line, sphere), area slow,
     trip-wire detonation. Snapshot ships them. Foundation for the rest of
     the ability kits.
  +  v8.18 (Phase 1 foundation, ported from LSS):
     - Round-win conditions (LSS line 9947-9973): count alive per team each
       tick during 'playing'; one team at 0 alive ends the round and awards
       score to the other. Tie on time-out goes to team A.
     - matchEnd state (LSS line 9977-9988): when scoreA or scoreB hits 4
       (ROUNDS_TO_WIN), transition to matchEnd, linger for 10s, then reset
       to select with scores cleared.
     - 'round_end' and 'match_end' SimEvents emitted on state transitions
       so the client can show ROUND OVER / VICTORY banners.
     - Doomed state (LSS line 4388): set when health drops below 30% of
       maxHealth; cleared on respawn. Surfaced in snapshot.
     - Spawn protection (LSS line 4365): 3 seconds of damage immunity on
       spawn so spawn-killers can't insta-delete fresh ships. Surfaced in
       snapshot for client to render a shield bubble.
     - Reload + clip ammo (LSS line 8094-8121): each weapon has a clip;
       firing decrements; auto-reloads at 2s when empty. Surfaced in snapshot.
  +  v8.16 (TRACKER ability kit, simplified):
     - Slot 0 (Q) Tracker Rockets: 5-missile spread, 1000 dmg, no homing
       (LSS line 8633 has the full lock/homing system).
     - Slot 1 (E) Particle Wall: 5s damage immunity buff (LSS line 8780
       deploys a worldEffect mesh with HP).
     - Slot 2 (F) Sonar Lock: emits a 'sonar_lock' event with enemy IDs in
       a 2000u forward cone for client highlight + ping audio (LSS line 8904
       builds per-target lock stacks 0..3).
     - Slot 3 (V) Salvo Core: 3s of 0.5x fire interval + 1.5x damage on
       regular fire (LSS line 9044 spawns remote-guided missiles steered by
       the player's crosshair every frame).
     Each tagged // SIMPLIFIED: with LSS line refs for future deepening.
  +  v8.15 (combat correctness, ported from LSS):
     - Shield-first damage. _applyDamage now drains shield before health
       (LSS Bot.takeDamage line 4364, applyPlayerDamage line 7723). Was
       applying the full hit straight to health.
     - Auto-fire while held. Removed the `!player.prevFire` rising-edge
       gate; condition is now `input.fire && player.fireTimer <= 0` to
       match LSS's main fire loop (line 8097). Held trigger now fires at
       the weapon's fireRate cadence; sound and projectile spawn line up.
  +  v8.14 (audio polish): SimEvent gains a 'fire' type emitted on every
     projectile spawn (player + bot). hit/kill events now carry a `position`
     for 3D spatial audio on the client.
  +  9 LSS maps ported verbatim (hourglass, spine, infinity, tower, cross,
     arc, octahedron, pentagon, gyre). SU=150 to match LSS's tuning. Levels
     carry palette + sdfSmoothK on the wire so the client meshes the same
     SDF the server collides against.
  +  SDF-based collision (v8.9): replaces binary pointInLevel containment with
     a graded signed distance (rooms blended via smooth-min, tunnels hard-min'd
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
  // v8.33: manual reload edge (R key on client). One-shot per send; server
  // triggers reload if clip isn't full and not already reloading.
  reload?: boolean;
  // v8.44: dash edge (Shift on client). One-shot per send; server consumes
  // a dash charge and applies the dash burst (LSS line 9898-9914).
  dash?:   boolean;
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
  // v8.32: damage credited on hit. Used by the match-end scoreboard.
  damageDealt: number;
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
  // v8.28: spinup mechanic (LSS line 8085-8090). For chassis whose weapon
  // has spinup > 0 (BLASTER 1.2s, SYPHON 0.4s), trigger held charges the
  // spinupTimer; fire is gated on spunUp. Released trigger drains at 2x rate.
  spinupTimer: number;
  spunUp: boolean;
  // v8.28: BLASTER mode switch (LSS line 8927). Toggled by the slot-2
  // ability press; 1s lockout (`blasterSwitchTimer`) before stats actually
  // swap. blasterPendingMode holds the queued target during the lockout.
  blasterMode: 'close' | 'long';
  blasterPendingMode: 'close' | 'long';
  blasterSwitchTimer: number;
  // v8.29: stasis state (LSS line 1115-1116, 12442-12470). Set when player
  // touches a stasis_pickup; locks velocity to 0, recharges shield over the
  // duration. Cleared when stasisTimer expires. Client renders vignette +
  // immobilization UI while inStasis.
  inStasis: boolean;
  stasisTimer: number;
  stasisDuration: number;
  // v8.18: doomed state (LSS line 4388, 7732). Set when health drops below
  // DOOMED_HEALTH_PCT of maxHealth; client uses it for HUD red flash + audio
  // tremor. Cleared on respawn.
  doomed: boolean;
  // v8.18: spawn protection (LSS line ~7554, SPAWN_PROTECTION_TIME). Counts
  // down from 3.0 on spawn; while >0, _applyDamage skips this player so spawn-
  // killers can't insta-delete a fresh ship. Client renders a shimmer bubble.
  spawnProtection: number;
  // v8.18: reload + clip ammo (LSS line 8094-8121). Each weapon has a clip
  // size; firing decrements clipAmmo; empty triggers reload over 2s.
  clipAmmo: number;
  maxClip: number;
  reloading: boolean;
  reloadTimer: number;
  // v8.16: TRACKER abilities.
  // Particle Wall (slot 1) is simplified to a 5s damage-immunity buff
  // instead of a deployed shield entity. >0 means incoming damage is fully
  // absorbed. SIMPLIFIED: LSS line 8780-8806 deploys a worldEffect with HP.
  damageImmuneTimer: number;
  // Salvo Core (slot 3) gives 3s of doubled fire rate and 1.5x damage.
  // SIMPLIFIED: LSS line 9044-9054 spawns remote-guided missiles steered by
  // the player's crosshair each frame. Here we just buff the regular fire.
  coreFireRateMult: number;
  coreDamageMult: number;
  // v8.44: universal dash system (LSS line 9898-9914 + 7916-7932). Every
  // chassis gets `maxDashes` charges (Frigate 3 / Corvette 2 / Dreadnought 1)
  // that consume on Shift press. Charges regenerate one at a time over
  // `dashCooldown` seconds. While dashActive, max-speed cap rises to
  // chassis.dashSpeed for dashDuration seconds.
  dashCharges: number;
  maxDashes: number;
  dashSpeed: number;
  dashDuration: number;
  dashCooldown: number;
  dashActive: boolean;
  dashTimer: number;
  dashCooldownTimer: number;
  prevDash: boolean;            // for rising-edge detection
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
  damageDealt: number;
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
  // v8.54: NA5 ; bot ability scheduling. Per-slot cooldown timers (bot's
  // perspective; throttles re-attempts after a successful or rejected use).
  // We don't read player.abilityCooldowns directly because bots have their
  // own ability state (similar shape but separate fields).
  abilityCooldowns: number[];
  abilityActive: boolean[];
  abilityTimers: number[];
  // Persistent buffs that bot abilities can grant (mirror of Player fields).
  afterburnerMult: number;
  damageImmuneTimer: number;
  coreFireRateMult: number;
  coreDamageMult: number;
  // Defensive trigger memory: bot tries defensive/utility abilities more
  // eagerly when recently damaged.
  lastDamageTime: number;
  // v8.54: per-bot ability cooldown bias so different bots don't synchronize.
  abilityScheduleJitter: number;
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
  // v8.40: NA10 ; projectile penetration. pierceCount is how many additional
  // entity hits this projectile survives before being consumed (0 = standard
  // single-hit; PUNCTURE rail rounds get pierceCount > 0). wallPierce lets
  // arc-wave-style projectiles pass through level geometry. piercedIds tracks
  // entities already hit by this projectile so it doesn't multi-tick the same
  // target.
  pierceCount?: number;
  wallPierce?: boolean;
  piercedIds?: number[];
}

// v8.21: world effects (firewalls, trip wires, tethers, traps, deployable
// shields, etc.). Generic enough to back most LSS abilities without per-
// kind server-side state. Each effect carries type-specific params in
// `data`, common fields here (position, ownerId, ownerTeam, hp, timer).
//
// Server runs the tick (timer decrement, hp removal, area-of-effect damage
// to enemies in range). Snapshot ships the array; client builds meshes per
// type and disposes on absence.
export interface WorldEffect {
  id: number;
  type: 'firewall' | 'trip_wire' | 'tether' | 'incendiary' | 'particle_wall' | 'gas' | 'stasis_pickup' | 'destructible';
  ownerType: 'player' | 'bot';
  ownerId: number;
  ownerTeam: number;
  position: Vec3;
  // Type-specific orientation/extent (radius, line-direction, etc.).
  // Read by the appropriate per-type tick + the client.
  data: any;
  hp: number;
  maxHp: number;
  timer: number;          // seconds remaining; <= 0 → cleanup
  spawnedAt: number;
}

export interface Match {
  state: 'select' | 'warmup' | 'playing' | 'roundEnd' | 'matchEnd';
  warmupTimer: number;
  roundTimer: number;
  // v8.18: matchEndTimer drives the post-victory scoreboard linger.
  matchEndTimer: number;
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
  // v8.21: world effects (firewalls, trip wires, particle walls, etc.).
  // Keyed by effect id; effect lifetimes and area damage are owned here.
  worldEffects: Map<number, WorldEffect>;
  events: SimEvent[];               // cleared after each broadcast
  level: Level;
  nextEntityId: number;
}

// v8.6: hit/kill events surfaced to clients so they can play markers.
export interface SimEvent {
  type: 'hit' | 'kill' | 'fire' | 'beam'; // v8.51: beam for hitscan visuals
  shooterType: 'player' | 'bot';
  shooterId: number;
  shooterPeerId?: string;
  shooterTeam?: number;
  // 'fire' carries the shooter's loadout (so client picks the right SFX)
  // and position (so client positions the sound in 3D). 'hit'/'kill' keep
  // the existing shape; targetType/targetId are absent on 'fire'.
  loadoutKey?: string;
  position?: Vec3;
  targetType?: 'player' | 'bot';
  targetId?: number;
  targetPeerId?: string;
  damage?: number;
  time: number;
}

// ---- Tunables ----

const PLAYER_RADIUS = 60;          // collision sphere radius (FALLBACK ONLY; per-chassis radius via _hullRadius)

// v8.43: NA7 ; per-chassis hull radius. LSS uses chassis.hullLength * 0.5
// (range 40-70 across the three chassis classes). Used for both collision
// (against walls + obstacles) and projectile-vs-ship hit detection. Falls
// back to PLAYER_RADIUS / PLAYER_HIT_RADIUS for entities without loadout.
function _hullRadius(ent: Player | Bot): number {
  const ld = (ent as any).loadoutKey ? LOADOUTS[(ent as any).loadoutKey as LoadoutKey] : null;
  if (!ld) return PLAYER_RADIUS;
  const ch = CHASSIS[ld.chassis];
  if (!ch) return PLAYER_RADIUS;
  return ch.hullLength * 0.5;
}
function _hitRadius(ent: Player | Bot): number {
  // Hit radius is hull radius + small forgiveness margin (LSS uses 1.33x).
  return _hullRadius(ent) * 1.33;
}
const ACCEL = 1500;                 // units / s^2
const MAX_SPEED = 600;              // units / s
const DAMPING = 4;                  // velocity decay per second when no input
const ROUND_TIME = 180;
const WARMUP_TIME = 10;
// v8.18: best-of-7 match (LSS line 964: ROUNDS_TO_WIN: 4). Whichever team
// hits 4 wins the match; on match end, scoreboard lingers for MATCH_END_LINGER
// seconds before the lobby reopens.
const ROUNDS_TO_WIN = 4;
const MATCH_END_LINGER = 10;
const ROUND_END_LINGER_LSS = 5; // (was 6 in our v8.7; LSS uses 5 at line 9966)
// v8.18: spawn protection grace period (LSS line ~7554, value LSS.SPAWN_PROTECTION).
const SPAWN_PROTECTION_TIME = 3.0;
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
      matchEndTimer: 0,
      scoreA: 0,
      scoreB: 0,
      currentRound: 1,
      selectedMap: level.name,
      seed: 0,
    },
    players: new Map(),
    bots: new Map(),
    projectiles: new Map(),
    worldEffects: new Map(),
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
    damageDealt: 0,
    accel: ch.acceleration,
    maxSpeed: ch.flightSpeed,
    weaponDamage: 250,
    weaponFireRate: 0.18,
    abilityCooldowns: [0, 0, 0, 0],
    abilityActive: [false, false, false, false],
    abilityTimers: [0, 0, 0, 0],
    afterburnerMult: 1.0,
    doomed: false,
    spawnProtection: SPAWN_PROTECTION_TIME,
    clipAmmo: 0,
    maxClip: 0,
    reloading: false,
    reloadTimer: 0,
    spinupTimer: 0,
    spunUp: false,
    blasterMode: 'close',
    blasterPendingMode: 'close',
    blasterSwitchTimer: 0,
    inStasis: false,
    stasisTimer: 0,
    stasisDuration: 3,
    damageImmuneTimer: 0,
    coreFireRateMult: 1.0,
    coreDamageMult: 1.0,
    // v8.44: dash defaults; per-chassis values set in applyPlayerLoadout.
    dashCharges: ch.maxDashes,
    maxDashes: ch.maxDashes,
    dashSpeed: ch.dashSpeed,
    dashDuration: ch.dashDuration,
    dashCooldown: ch.dashCooldown,
    dashActive: false,
    dashTimer: 0,
    dashCooldownTimer: 0,
    prevDash: false,
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
  player.damageImmuneTimer = 0;
  player.coreFireRateMult = 1.0;
  player.coreDamageMult = 1.0;
  // v8.18: clip ammo from weapon stats; reload state cleared.
  player.clipAmmo = ld.weapon.clipSize;
  player.maxClip = ld.weapon.clipSize;
  player.reloading = false;
  player.reloadTimer = 0;
  player.doomed = false;
  player.spawnProtection = SPAWN_PROTECTION_TIME;
  // v8.44: dash stats from chassis. Charges refilled to max on loadout swap.
  player.maxDashes = ch.maxDashes;
  player.dashSpeed = ch.dashSpeed;
  player.dashDuration = ch.dashDuration;
  player.dashCooldown = ch.dashCooldown;
  player.dashCharges = ch.maxDashes;
  player.dashActive = false;
  player.dashTimer = 0;
  player.dashCooldownTimer = 0;
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
    _respawnPlayer(p, state, state.level);
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
    damageDealt: 0,
    accel: ch.acceleration * 0.85,        // bots a bit slower than humans
    maxSpeed: ch.flightSpeed * 0.85,
    weaponDamage: ld.weapon.damage,
    weaponFireRate: ld.weapon.fireRate,
    aiTarget: null, aiTimer: 0,
    aiTargetType: null, aiTargetId: null,
    // v8.54: NA5 ; ability scheduling fields.
    abilityCooldowns: [0, 0, 0, 0],
    abilityActive: [false, false, false, false],
    abilityTimers: [0, 0, 0, 0],
    afterburnerMult: 1.0,
    damageImmuneTimer: 0,
    coreFireRateMult: 1.0,
    coreDamageMult: 1.0,
    lastDamageTime: -999,
    abilityScheduleJitter: Math.random() * 2.0,
  };
  state.bots.set(id, bot);
  return bot;
}

export function clearAllBots(state: SimState): void {
  state.bots.clear();
}

// v8.54: NA5 ; bot ability scheduler + dispatch. Picks a slot to use based
// on situation (recently-damaged + low HP → defensive; target in range →
// offensive; HP healthy + target visible → core); calls dispatcher to
// actually invoke. Bots only use what's wired here ; some abilities (utility
// slot 2) are skipped because their LSS heuristics are situational and not
// worth modeling for bot AI yet.
function _tryBotAbility(bot: Bot, state: SimState, distToTarget: number): void {
  const lk = bot.loadoutKey;
  const cdTable = ABILITY_COOLDOWNS[lk];
  if (!cdTable) return;
  // Add small jitter so two same-loadout bots don't synchronize button presses.
  const minDelay = 0.5 + bot.abilityScheduleJitter;
  if ((state.time + bot.abilityScheduleJitter) < minDelay) return;
  const hpFrac = bot.health / bot.maxHealth;
  const recentlyHit = (state.time - bot.lastDamageTime) < 2.0;

  // Defensive (slot 1) ; high priority when threatened.
  if (bot.abilityCooldowns[1] <= 0 && !bot.abilityActive[1]
      && (hpFrac < 0.5 || recentlyHit)) {
    if (_activateBotAbility(state, bot, 1)) return;
  }
  // Offensive (slot 0) ; main combat ability.
  if (bot.abilityCooldowns[0] <= 0 && !bot.abilityActive[0]
      && distToTarget < 2500) {
    if (_activateBotAbility(state, bot, 0)) return;
  }
  // Core (slot 3) ; emergency / aggressive moment.
  if (bot.abilityCooldowns[3] <= 0 && !bot.abilityActive[3]
      && hpFrac > 0.3 && distToTarget < 3000) {
    if (_activateBotAbility(state, bot, 3)) return;
  }
  // Utility (slot 2) is skipped for bots; LSS heuristics for trip wires /
  // traps / sonar-lock are situational and don't model cleanly without LOS
  // and ground-tracking infrastructure.
}

// Per-loadout bot-side ability implementation. Mirrors the player dispatcher
// in spirit but fires the same projectile types or applies the same buffs.
// Returns true if dispatched.
function _activateBotAbility(state: SimState, bot: Bot, slot: number): boolean {
  const lk = bot.loadoutKey;
  const cdTable = ABILITY_COOLDOWNS[lk];
  const durTable = ABILITY_DURATIONS[lk];
  if (!cdTable || !durTable) return false;

  // Resolve target position. Used by some abilities to aim non-fire effects.
  let targetPos: Vec3 | null = null;
  if (bot.aiTargetType === 'player' && bot.aiTargetId != null) {
    for (const p of state.players.values()) {
      if (p.id === bot.aiTargetId) { targetPos = p.position; break; }
    }
  } else if (bot.aiTargetType === 'bot' && bot.aiTargetId != null) {
    const b = state.bots.get(bot.aiTargetId);
    if (b) targetPos = b.position;
  }
  // For most abilities we just need facing + origin.
  const facing = _facingDir(bot.yaw, bot.pitch);
  const origin: Vec3 = {
    x: bot.position.x + facing.x * 80,
    y: bot.position.y + 30 + facing.y * 80,
    z: bot.position.z + facing.z * 80,
  };

  let dispatched = false;

  if (lk === 'VORTEX' && slot === 0) {
    _hitscanFire(state, 'bot', bot.id, bot.team, origin, facing, 2400, 3000, false);
    dispatched = true;
  } else if (lk === 'VORTEX' && slot === 1) {
    // Vortex Shield ; reduces damage via _applyDamage check on abilityActive[1].
    dispatched = true;
  } else if (lk === 'VORTEX' && slot === 3) {
    bot.coreDamageMult = 3.0;
    dispatched = true;
  } else if (lk === 'PYRO' && slot === 0) {
    // Firewall in front of bot.
    const wallPos: Vec3 = { x: bot.position.x + facing.x * 200, y: bot.position.y, z: bot.position.z + facing.z * 200 };
    _spawnWorldEffect(state, 'firewall', 'bot', bot.id, bot.team, wallPos,
      { width: 600, height: 200, dps: 400, dirX: facing.x, dirZ: facing.z, color: 0xff7733 }, durTable[0] || 6, 999);
    dispatched = true;
  } else if (lk === 'PYRO' && slot === 1) {
    dispatched = true;
  } else if (lk === 'PYRO' && slot === 3) {
    // Flame Core ; massive AoE at bot's position.
    _spawnWorldEffect(state, 'incendiary', 'bot', bot.id, bot.team, bot.position,
      { radius: 800, dps: 4500 }, durTable[3] || 2, 999);
    dispatched = true;
  } else if (lk === 'PUNCTURE' && slot === 0) {
    // Cluster Missile (single fast projectile; no burst zone for bots).
    const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, facing);
    proj.damage = 800;
    proj.velocity.x = facing.x * 1500;
    proj.velocity.y = facing.y * 1500;
    proj.velocity.z = facing.z * 1500;
    proj.lifetime = 3.0;
    proj.color = 0xffaa44;
    dispatched = true;
  } else if (lk === 'PUNCTURE' && slot === 1) {
    bot.afterburnerMult = 2.0;
    dispatched = true;
  } else if (lk === 'PUNCTURE' && slot === 3) {
    bot.afterburnerMult = 2.5;
    bot.coreDamageMult = 1.5;
    dispatched = true;
  } else if (lk === 'SLAYER' && slot === 0) {
    // Arc Wave (short range wide projectile; wallPierce so it threads tunnels).
    const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, facing);
    proj.damage = 1200;
    proj.velocity.x = facing.x * 800;
    proj.velocity.y = facing.y * 800;
    proj.velocity.z = facing.z * 800;
    proj.wallPierce = true;
    proj.lifetime = 1.5;
    proj.color = 0xffeeaa;
    dispatched = true;
  } else if (lk === 'SLAYER' && slot === 1) {
    dispatched = true;
  } else if (lk === 'SLAYER' && slot === 3) {
    bot.coreDamageMult = 2.5;
    dispatched = true;
  } else if (lk === 'TRACKER' && slot === 0) {
    // Tracker Rockets ; 3-shot fan instead of homing salvo (simpler).
    for (let i = -1; i <= 1; i++) {
      const angOff = i * 0.1;
      const cy = Math.cos(bot.yaw + angOff), sy2 = Math.sin(bot.yaw + angOff);
      const dir = { x: -sy2, y: facing.y, z: -cy };
      const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, dir);
      proj.damage = 600;
      proj.velocity.x = dir.x * 1200;
      proj.velocity.y = dir.y * 1200;
      proj.velocity.z = dir.z * 1200;
      proj.lifetime = 2.5;
      proj.color = 0x88ddaa;
    }
    dispatched = true;
  } else if (lk === 'TRACKER' && slot === 1) {
    bot.damageImmuneTimer = durTable[1] || 5;
    dispatched = true;
  } else if (lk === 'TRACKER' && slot === 3) {
    bot.coreFireRateMult = 2.0;
    bot.coreDamageMult = 1.5;
    dispatched = true;
  } else if (lk === 'BLASTER' && slot === 0) {
    // Power Shot ; single big-damage projectile.
    const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, facing);
    proj.damage = 3000;
    proj.velocity.x = facing.x * 2500;
    proj.velocity.y = facing.y * 2500;
    proj.velocity.z = facing.z * 2500;
    proj.lifetime = 1.5;
    proj.color = 0xffdd44;
    dispatched = true;
  } else if (lk === 'BLASTER' && slot === 1) {
    dispatched = true;
  } else if (lk === 'BLASTER' && slot === 3) {
    bot.coreFireRateMult = 1.5;
    bot.coreDamageMult = 1.2;
    dispatched = true;
  } else if (lk === 'SYPHON' && slot === 0) {
    // Rocket Salvo ; 5-shot tight spread.
    for (let i = 0; i < 5; i++) {
      const angOff = (i - 2) * 0.04;
      const cy = Math.cos(bot.yaw + angOff), sy2 = Math.sin(bot.yaw + angOff);
      const dir = { x: -sy2, y: facing.y, z: -cy };
      const proj = _spawnProjectile(state, 'bot', bot.id, bot.team, origin, dir);
      proj.damage = 700;
      proj.velocity.x = dir.x * 1400;
      proj.velocity.y = dir.y * 1400;
      proj.velocity.z = dir.z * 1400;
      proj.lifetime = 2.5;
      proj.color = 0xcc77ff;
    }
    dispatched = true;
  } else if (lk === 'SYPHON' && slot === 1) {
    // Energy Siphon ; cheap hitscan that drains.
    _hitscanFire(state, 'bot', bot.id, bot.team, origin, facing, 1500, 2500, false);
    dispatched = true;
  } else if (lk === 'SYPHON' && slot === 3) {
    bot.coreDamageMult = 1.5;
    dispatched = true;
  }

  if (!dispatched) return false;
  bot.abilityCooldowns[slot] = cdTable[slot];
  if (durTable[slot] > 0) {
    bot.abilityActive[slot] = true;
    bot.abilityTimers[slot] = durTable[slot];
  }
  return true;
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

  // v8.56: NA6 ; cheap obstacle avoidance. Sample SDF 200u ahead of intended
  // direction; if outside the level (i.e. would hit wall), nudge sideways
  // until clearer. Prevents bots from grinding wall corners in tunnels.
  {
    const lookAhead = 250;
    const probeX = bot.position.x + steerX * lookAhead;
    const probeY = bot.position.y + steerY * lookAhead;
    const probeZ = bot.position.z + steerZ * lookAhead;
    if (!pointInLevel({ x: probeX, y: probeY, z: probeZ }, state.level)) {
      // Try perpendicular candidates (left-strafe + right-strafe) and pick
      // the one with cleaner forward path. Use cross product with up vector.
      const altLX = -steerZ, altLY = steerY, altLZ = steerX;     // left
      const altRX =  steerZ, altRY = steerY, altRZ = -steerX;    // right
      const probeL = pointInLevel({
        x: bot.position.x + altLX * lookAhead,
        y: bot.position.y + altLY * lookAhead,
        z: bot.position.z + altLZ * lookAhead,
      }, state.level);
      const probeR = pointInLevel({
        x: bot.position.x + altRX * lookAhead,
        y: bot.position.y + altRY * lookAhead,
        z: bot.position.z + altRZ * lookAhead,
      }, state.level);
      if (probeL && !probeR)      { steerX = altLX; steerY = altLY; steerZ = altLZ; }
      else if (probeR && !probeL) { steerX = altRX; steerY = altRY; steerZ = altRZ; }
      else if (probeL && probeR) {
        // Both clear ; deterministic pick by bot id so neighbors don't oscillate.
        if ((bot.id & 1) === 0) { steerX = altLX; steerY = altLY; steerZ = altLZ; }
        else                    { steerX = altRX; steerY = altRY; steerZ = altRZ; }
      }
      // Both blocked: keep original; SDF push-out resolves whatever happens.
    }
  }

  // v8.56: NA6 ; projectile dodge. If an enemy projectile is heading toward us
  // within ~1s impact, sidestep perpendicular to its velocity. Cheap O(P)
  // scan; we only check projectiles within a forward cone.
  {
    const dodgeR2 = 1500 * 1500; // only consider projectiles within 1500u
    let dodgeX = 0, dodgeZ = 0, dodgeFound = false;
    for (const proj of state.projectiles.values()) {
      if (proj.ownerTeam === bot.team) continue;
      const px = bot.position.x - proj.position.x;
      const py = bot.position.y - proj.position.y;
      const pz = bot.position.z - proj.position.z;
      const distP2 = px * px + py * py + pz * pz;
      if (distP2 > dodgeR2) continue;
      const pvx = proj.velocity.x, pvy = proj.velocity.y, pvz = proj.velocity.z;
      const pvLen2 = pvx * pvx + pvy * pvy + pvz * pvz;
      if (pvLen2 < 100) continue;
      // Closing velocity ; dot of (bot - proj) and projectile velocity sign.
      // If projectile moving toward us, (proj.pos + t*vel) approaches bot.
      // Compute t of closest approach; if t < 1.0 and miss distance < 250 → dodge.
      const dotPv = -(px * pvx + py * pvy + pz * pvz); // > 0 means proj heading toward bot
      if (dotPv <= 0) continue;
      const tClose = dotPv / pvLen2;
      if (tClose > 1.0 || tClose < 0.05) continue;
      const cx = proj.position.x + pvx * tClose;
      const cy = proj.position.y + pvy * tClose;
      const cz = proj.position.z + pvz * tClose;
      const mx = cx - bot.position.x, my = cy - bot.position.y, mz = cz - bot.position.z;
      const missD2 = mx * mx + my * my + mz * mz;
      if (missD2 > 250 * 250) continue;
      // Dodge perpendicular to projectile velocity (in horizontal plane).
      const pvLen = Math.sqrt(pvLen2);
      const npvx = pvx / pvLen, npvz = pvz / pvLen;
      // Perpendicular = (-z, +x).
      dodgeX += -npvz;
      dodgeZ +=  npvx;
      dodgeFound = true;
    }
    if (dodgeFound) {
      const dLen = Math.sqrt(dodgeX * dodgeX + dodgeZ * dodgeZ) || 1;
      // Blend dodge into existing steer (60% dodge, 40% original).
      steerX = (dodgeX / dLen) * 0.6 + steerX * 0.4;
      steerZ = (dodgeZ / dLen) * 0.6 + steerZ * 0.4;
    }
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

  // v8.54: NA5 ; tick bot ability cooldowns/active timers + try to use them.
  // Done before fire so an offensive ability press in this tick still goes
  // through. State machine is independent from the player ability system but
  // dispatches to similar effect (projectile spawns, world effect spawns,
  // self-buff timers).
  if (state.match.state === 'playing') {
    for (let i = 0; i < 4; i++) {
      if (bot.abilityCooldowns[i] > 0) bot.abilityCooldowns[i] = Math.max(0, bot.abilityCooldowns[i] - dt);
      if (bot.abilityActive[i]) {
        bot.abilityTimers[i] -= dt;
        if (bot.abilityTimers[i] <= 0) {
          bot.abilityActive[i] = false;
          bot.abilityTimers[i] = 0;
          // Clear duration buffs that map to this slot.
          if (i === 1 && bot.afterburnerMult !== 1.0) bot.afterburnerMult = 1.0;
          if (i === 3) { bot.coreFireRateMult = 1.0; bot.coreDamageMult = 1.0; }
        }
      }
    }
    // Tick damageImmuneTimer (TRACKER particle wall).
    if (bot.damageImmuneTimer > 0) bot.damageImmuneTimer = Math.max(0, bot.damageImmuneTimer - dt);
    _tryBotAbility(bot, state, dist);
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
    // v8.54: NA5 ; bot core damage / fire-rate buffs apply to regular fire.
    proj.damage = bot.weaponDamage * BOT_DAMAGE_MULT * (bot.coreDamageMult || 1.0);
    const baseFr = Math.max(BOT_FIRE_RATE, bot.weaponFireRate * 1.6);
    bot.fireTimer = baseFr / (bot.coreFireRateMult || 1.0);
    state.events.push({
      type: 'fire',
      shooterType: 'bot',
      shooterId: bot.id,
      shooterTeam: bot.team,
      loadoutKey: bot.loadoutKey,
      position: { x: origin.x, y: origin.y, z: origin.z },
      time: state.time,
    });
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

// v8.38: NA11. Anti-spawn-camp spawn picker. Score each candidate spawn by
// MIN distance to any living enemy (higher = better) and MIN distance to any
// teammate (higher = better but weighted less so we don't isolate spawns).
// Returns the highest-scoring spawn with a small randomization tie-breaker
// so identical-score spawns don't always pick the same one.
function _pickSafeSpawn(state: SimState, team: number, level: Level): { x: number; y: number; z: number } {
  const pool = team === TEAM_B ? level.spawnB : level.spawnA;
  if (pool.length <= 1) return pool[0];
  let bestScore = -Infinity;
  let best = pool[0];
  for (const sp of pool) {
    let minEnemyDist2 = Infinity;
    let minAllyDist2 = Infinity;
    // Compare against living players + bots.
    for (const p of state.players.values()) {
      if (!p.alive) continue;
      const dx = p.position.x - sp.x;
      const dy = p.position.y - sp.y;
      const dz = p.position.z - sp.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      if (p.team === team) { if (d2 < minAllyDist2) minAllyDist2 = d2; }
      else                 { if (d2 < minEnemyDist2) minEnemyDist2 = d2; }
    }
    for (const b of state.bots.values()) {
      if (!b.alive) continue;
      const dx = b.position.x - sp.x;
      const dy = b.position.y - sp.y;
      const dz = b.position.z - sp.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      if (b.team === team) { if (d2 < minAllyDist2) minAllyDist2 = d2; }
      else                 { if (d2 < minEnemyDist2) minEnemyDist2 = d2; }
    }
    // Score: enemy distance dominates (weight 1.0); ally distance has small
    // bonus (weight 0.25) to spread teammates apart but not too aggressively.
    // Square-root for more linear distance feel.
    const enemyScore = (minEnemyDist2 === Infinity ? 1e9 : Math.sqrt(minEnemyDist2));
    const allyScore  = (minAllyDist2  === Infinity ? 1e6 : Math.sqrt(minAllyDist2));
    const score = enemyScore + 0.25 * allyScore + Math.random() * 50; // 50u jitter
    if (score > bestScore) { bestScore = score; best = sp; }
  }
  return best;
}

function _respawnPlayer(player: Player, state: SimState, level: Level): void {
  const sp = _pickSafeSpawn(state, player.team, level);
  player.position.x = sp.x; player.position.y = sp.y; player.position.z = sp.z;
  player.velocity.x = 0; player.velocity.y = 0; player.velocity.z = 0;
  player.health = player.maxHealth;
  player.shield = player.maxShield;
  player.alive = true;
  player.fireTimer = 0;
  // v8.18: reset doomed + spawn protection on respawn (LSS line 7554, 7733).
  player.doomed = false;
  player.spawnProtection = SPAWN_PROTECTION_TIME;
  // Refill clip on respawn so a fresh ship doesn't spawn empty.
  player.clipAmmo = player.maxClip;
  player.reloading = false;
  player.reloadTimer = 0;
  // v8.44: refill dash charges on respawn (LSS line 7774, 8836).
  player.dashCharges = player.maxDashes;
  player.dashActive = false;
  player.dashTimer = 0;
  player.dashCooldownTimer = 0;
}

function _respawnBot(bot: Bot, state: SimState, level: Level): void {
  const sp = _pickSafeSpawn(state, bot.team, level);
  bot.position.x = sp.x + (Math.random() - 0.5) * 100;
  bot.position.y = sp.y;
  bot.position.z = sp.z + (Math.random() - 0.5) * 100;
  bot.velocity.x = 0; bot.velocity.y = 0; bot.velocity.z = 0;
  bot.health = bot.maxHealth;
  bot.shield = bot.maxShield;
  bot.alive = true;
  bot.aiTarget = null; bot.aiTimer = 0;
}


// v8.15: shield-first damage application. Ported verbatim from LSS's
// takeDamage (Bot at line 4364, Player at line 7723):
//   if (shield > 0):
//     if (amount <= shield):  shield -= amount;        // fully absorbed
//     else:                   amount -= shield; shield = 0;  // overflow
//   health -= amount;
// The previous version applied p.damage straight to health, skipping the
// shield entirely; v8.15 fixes that. Returns true if the target died.
function _applyDamage(target: Player | Bot, amount: number, state?: SimState): boolean {
  if (!target.alive) return false;
  // v8.54: NA5 ; bot defensive trigger memory.
  const tBot = target as Bot;
  if (tBot.lastDamageTime !== undefined && state) {
    tBot.lastDamageTime = state.time;
  }
  // v8.18: spawn protection (LSS line 4365). Fresh-spawned ships are
  // invulnerable for SPAWN_PROTECTION_TIME seconds so spawn-killers can't
  // delete them before they get oriented. Bots don't have it currently;
  // could add later.
  if ((target as Player).spawnProtection && (target as Player).spawnProtection > 0) {
    return false;
  }
  // v8.16: TRACKER Particle Wall (simplified) damage immunity.
  // SIMPLIFIED: full LSS implementation has the wall as a separate entity
  // that takes hits and is destroyed by Arc Wave; here the buff is on the
  // player directly.
  if ((target as Player).damageImmuneTimer && (target as Player).damageImmuneTimer > 0) {
    return false; // fully absorbed; HP and shield untouched
  }
  // v8.23-v8.24: held defensive shields (Sword Block / Vortex Shield) act
  // as flat damage reductions while slot 1 is active.
  //   SLAYER Sword Block:    0.30 mult (LSS line 7633-7637)
  //   VORTEX Vortex Shield:  0.30 mult (LSS line 9091-9118)
  // If their respective core is also active, the reduction is stronger.
  // v8.54: NA5 ; bots also have abilityActive[1] for these chassis now.
  const tp = target as Player | Bot;
  if (tp.abilityActive && tp.abilityActive[1]) {
    if (tp.loadoutKey === 'SLAYER') {
      amount *= tp.abilityActive[3] ? 0.15 : 0.30;
    } else if (tp.loadoutKey === 'VORTEX') {
      amount *= tp.abilityActive[3] ? 0.20 : 0.35;
    } else if (tp.loadoutKey === 'PYRO') {
      // Thermal Shield (LSS line 8772-8780). Stronger reduction; full LSS
      // version drains a power pool while held but we don't model that yet.
      amount *= 0.25;
    } else if (tp.loadoutKey === 'BLASTER') {
      // Gun Shield (LSS line 8762-8767). LSS uses a directional HP-based
      // shield; simplified to a damage multiplier here.
      amount *= 0.40;
    }
  }
  if (target.shield > 0) {
    if (amount <= target.shield) {
      target.shield -= amount;
      return false;
    } else {
      amount -= target.shield;
      target.shield = 0;
    }
  }
  target.health -= amount;
  // v8.18: doomed flag (LSS line 4388). Once we drop below 30% HP, set the
  // doomed bit so the client can drive its red-flash + tremor visuals from
  // it. Cleared on respawn.
  const DOOMED_PCT = 0.30;
  if ((target as Player).peerId !== undefined) {
    const p = target as Player;
    if (!p.doomed && p.health > 0 && p.health / p.maxHealth <= DOOMED_PCT) {
      p.doomed = true;
    }
  }
  if (target.health <= 0) {
    target.health = 0;
    return true;
  }
  return false;
}

// v8.39: NA8. Knockback impulse applied to the target on a non-fatal hit.
// Direction is the projectile's normalized velocity vector (so the target is
// pushed AWAY from the shooter along the projectile's trajectory). Magnitude
// scales with damage; capped so single shots don't punt ships across the map.
// Heavier weapons (rockets, cluster missiles) naturally produce larger pushes
// because they carry more damage per hit. Adds to existing velocity rather
// than replacing it (so a ship boosting toward you keeps its momentum and
// just gets nudged off course).
const KNOCKBACK_PER_DAMAGE = 0.40;       // velocity units per damage point
const KNOCKBACK_MAX_PER_HIT = 280;       // hard cap on a single impulse
function _applyKnockback(target: Player | Bot, p: Projectile): void {
  const vx = p.velocity.x, vy = p.velocity.y, vz = p.velocity.z;
  const speed = Math.sqrt(vx * vx + vy * vy + vz * vz);
  if (speed < 1) return;
  const nx = vx / speed, ny = vy / speed, nz = vz / speed;
  let mag = p.damage * KNOCKBACK_PER_DAMAGE;
  if (mag > KNOCKBACK_MAX_PER_HIT) mag = KNOCKBACK_MAX_PER_HIT;
  target.velocity.x += nx * mag;
  target.velocity.y += ny * mag;
  target.velocity.z += nz * mag;
}

// v8.35: NA38. Caller passes pre-hit shield so we can deterministically
// tag whether shield absorbed any of this hit and whether it broke. LSS
// at line 14913-14915 uses `if (shieldBefore > 0)` for damage_shield and
// `if (shieldAfter <= 0 && shieldBefore < amount + 0.001)` for damage.
// Client previously approximated from snapshot shield; now uses these tags.
function _recordHit(
  state: SimState,
  p: Projectile,
  target: Player | Bot,
  killed: boolean,
  shieldBefore: number = 0,
): void {
  const isPlayerTarget = (target as Player).peerId !== undefined;
  // Lookup shooter peerId for clean attribution. Also credit damage.
  let shooterPeerId: string | undefined;
  if (p.ownerType === 'player') {
    for (const pl of state.players.values()) {
      if (pl.id === p.ownerId) {
        shooterPeerId = pl.peerId;
        pl.damageDealt = (pl.damageDealt || 0) + p.damage;
        break;
      }
    }
  } else if (p.ownerType === 'bot') {
    const b = state.bots.get(p.ownerId);
    if (b) b.damageDealt = (b.damageDealt || 0) + p.damage;
  }
  // v8.35: shield tagging. Compute from pre-hit shield + post-hit shield.
  const shieldAfter = target.shield;
  const absorbedByShield = shieldBefore > 0;
  const brokeShield = shieldBefore > 0 && shieldAfter <= 0;
  state.events.push({
    type: killed ? 'kill' : 'hit',
    shooterType: p.ownerType,
    shooterId: p.ownerId,
    shooterPeerId,
    targetType: isPlayerTarget ? 'player' : 'bot',
    targetId: (target as any).id,
    targetPeerId: isPlayerTarget ? (target as Player).peerId : undefined,
    damage: p.damage,
    absorbedByShield,
    brokeShield,
    // v8.14: target position so the client can position the hit/kill SFX
    // in 3D via PannerNode. Cheap (one Vec3 copy) and lets the listener
    // tell where the hit happened by ear.
    position: { x: target.position.x, y: target.position.y, z: target.position.z },
    time: state.time,
  });
}

// v8.51: NA4 ; hitscan / raycast path. Used for instant beams (VORTEX laser,
// BLASTER smart-core, sniper-style abilities). Ray-marches the level SDF in
// fixed steps until either a wall blocks the beam or an entity sphere is
// hit. Returns the first hit (player/bot/wall) along with hit position +
// distance. Spawns a `beam` event so the client can render a flash/streak.
//
// Caller signature mirrors a fire: shooterTeam excludes own-team hits;
// shooterId+shooterType for kill attribution; damage applied at the hit
// point; range caps the beam length; wallPierce skips wall blocking.
type HitscanResult = {
  hitType: 'player' | 'bot' | 'wall' | 'none';
  hitId?: number;
  hitPosition: Vec3;
  distance: number;
};
function _hitscanFire(
  state: SimState,
  shooterType: 'player' | 'bot',
  shooterId: number,
  shooterTeam: number,
  origin: Vec3,
  dir: Vec3,
  damage: number,
  range: number,
  wallPierce: boolean = false,
): HitscanResult {
  // Normalize direction.
  const len = Math.sqrt(dir.x * dir.x + dir.y * dir.y + dir.z * dir.z) || 1;
  const dx = dir.x / len, dy = dir.y / len, dz = dir.z / len;
  // March in 30u steps (a typical projectile moves ~5-10u per tick at 64Hz,
  // so 30u is fine-grained enough to not skip thin walls or hulls).
  const STEP = 30;
  let bestHitDist = range;
  let bestHitType: 'player' | 'bot' | 'wall' | 'none' = 'none';
  let bestHitId: number | undefined;
  let bestHitPos: Vec3 = { x: origin.x + dx * range, y: origin.y + dy * range, z: origin.z + dz * range };

  // 1) Sphere-vs-line check against players + bots first; pick the nearest.
  // We use the standard ray-vs-sphere closed-form with t in [0, range].
  const checkSphere = (cx: number, cy: number, cz: number, r: number, hitType: 'player' | 'bot', id: number) => {
    // Vector from origin to center.
    const ox = cx - origin.x, oy = cy - origin.y, oz = cz - origin.z;
    // Project onto ray.
    const tProj = ox * dx + oy * dy + oz * dz;
    if (tProj < 0 || tProj > bestHitDist) return; // behind shooter or beyond best.
    // Closest point on ray.
    const cpx = origin.x + dx * tProj;
    const cpy = origin.y + dy * tProj;
    const cpz = origin.z + dz * tProj;
    const dxc = cx - cpx, dyc = cy - cpy, dzc = cz - cpz;
    const d2 = dxc * dxc + dyc * dyc + dzc * dzc;
    if (d2 > r * r) return;
    // Compute actual entry point along ray (tProj minus how far inside sphere
    // the closest point sits).
    const back = Math.sqrt(r * r - d2);
    const tEntry = Math.max(0, tProj - back);
    if (tEntry < bestHitDist) {
      bestHitDist = tEntry;
      bestHitType = hitType;
      bestHitId = id;
      bestHitPos = { x: origin.x + dx * tEntry, y: origin.y + dy * tEntry, z: origin.z + dz * tEntry };
    }
  };
  for (const p of state.players.values()) {
    if (!p.alive) continue;
    if (p.team === shooterTeam) continue;
    if (p.id === shooterId && shooterType === 'player') continue;
    checkSphere(p.position.x, p.position.y, p.position.z, _hitRadius(p), 'player', p.id);
  }
  for (const b of state.bots.values()) {
    if (!b.alive) continue;
    if (b.team === shooterTeam) continue;
    if (b.id === shooterId && shooterType === 'bot') continue;
    checkSphere(b.position.x, b.position.y, b.position.z, _hitRadius(b), 'bot', b.id);
  }

  // 2) March the ray; stop on wall (unless wallPierce). Check wall hit only
  // up to bestHitDist so a wall behind a closer entity doesn't override.
  if (!wallPierce) {
    let t = STEP;
    while (t < bestHitDist) {
      const sx = origin.x + dx * t;
      const sy = origin.y + dy * t;
      const sz = origin.z + dz * t;
      if (!pointInLevel({ x: sx, y: sy, z: sz }, state.level)) {
        // Wall blocks. Only override if closer than current best entity hit.
        if (t < bestHitDist) {
          bestHitDist = t;
          bestHitType = 'wall';
          bestHitId = undefined;
          bestHitPos = { x: sx, y: sy, z: sz };
        }
        break;
      }
      t += STEP;
    }
  }

  // 3) Apply damage if entity hit + emit event for client beam render.
  if (bestHitType === 'player' || bestHitType === 'bot') {
    const target: Player | Bot | undefined = bestHitType === 'player'
      ? state.players.get(_findPeerByEntityId(state, bestHitId!) || '')
      : state.bots.get(bestHitId!);
    if (target && target.alive) {
      const shieldBefore = target.shield;
      const killed = _applyDamage(target, damage, state);
      // Build a synthetic projectile-like object so _recordHit can attribute
      // properly + tag shield-vs-hull. Knockback applied directly along ray dir.
      const syntheticProj: Projectile = {
        id: -1, ownerType: shooterType, ownerId: shooterId, ownerTeam: shooterTeam,
        position: { x: bestHitPos.x, y: bestHitPos.y, z: bestHitPos.z },
        velocity: { x: dx * 1000, y: dy * 1000, z: dz * 1000 },
        damage, age: 0, lifetime: 0, color: 0xffffff,
      };
      if (killed) {
        _killEntity(target, state.time);
        _creditKill(state, shooterType, shooterId);
      } else {
        const isProtected = (target as Player).peerId !== undefined
          && ((target as Player).spawnProtection || 0) > 0;
        if (!isProtected) _applyKnockback(target, syntheticProj);
      }
      _recordHit(state, syntheticProj, target, killed, shieldBefore);
    }
  }

  // Emit beam event regardless of hit so the client can render the visual.
  state.events.push({
    type: 'beam',
    shooterType, shooterId, shooterTeam,
    origin: { x: origin.x, y: origin.y, z: origin.z },
    end: bestHitPos,
    distance: bestHitDist,
    hit: bestHitType !== 'none',
    time: state.time,
  } as any);

  return { hitType: bestHitType, hitId: bestHitId, hitPosition: bestHitPos, distance: bestHitDist };
}

// Helper: find player peerId by entity id (for hitscan target lookup).
function _findPeerByEntityId(state: SimState, id: number): string | null {
  for (const [peerId, p] of state.players) {
    if (p.id === id) return peerId;
  }
  return null;
}

// v8.55: NA9 ; shared splash damage helper. Used by explosions, cluster
// impacts, rocket detonations, smart-core blasts. Applies damage to every
// alive enemy entity within `radius` of `center`, with linear falloff from
// `damage` at center to 0 at radius. Optionally also damages owner team
// (LSS doesn't FF; opt-in for self-damage scenarios). `excludeId/Type`
// skips a specific entity (typically the projectile owner so a self-fired
// rocket doesn't friendly-blast you on contact).
function _applySplashDamage(
  state: SimState,
  center: Vec3,
  radius: number,
  damage: number,
  ownerTeam: number,
  options?: {
    friendlyFire?: boolean;
    excludeType?: 'player' | 'bot';
    excludeId?: number;
    falloff?: 'linear' | 'flat';
  }
): void {
  const opts = options || {};
  const r2 = radius * radius;
  const apply = (ent: Player | Bot, type: 'player' | 'bot') => {
    if (!ent.alive) return;
    if (!opts.friendlyFire && ent.team === ownerTeam) return;
    if (opts.excludeType === type && opts.excludeId === (ent as any).id) return;
    const dx = ent.position.x - center.x;
    const dy = ent.position.y - center.y;
    const dz = ent.position.z - center.z;
    const d2 = dx * dx + dy * dy + dz * dz;
    if (d2 >= r2) return;
    let dmg = damage;
    if (opts.falloff !== 'flat') {
      const d = Math.sqrt(d2);
      dmg = damage * (1 - d / radius);
    }
    if (dmg > 0) _applyDamage(ent, dmg, state);
  };
  for (const p of state.players.values()) apply(p, 'player');
  for (const b of state.bots.values()) apply(b, 'bot');
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
    // v8.40: NA10 ; wallPierce skips the wall check (arc-wave style).
    let hit = false;
    if (!p.wallPierce) {
      if (!pointInLevel(p.position, state.level)) {
        hit = true;
      } else {
        for (let i = 0; i < state.level.obstacles.length; i++) {
          if (_projectileHitsBox(p, state.level.obstacles[i])) { hit = true; break; }
        }
      }
    }
    if (hit) { dead.push(p.id); continue; }

    // v8.30: destructible obstacles. Projectiles deduct HP on contact and
    // are consumed; on HP<=0, the worldEffect cleans up next tick.
    let hitDestructible = false;
    for (const eff of state.worldEffects.values()) {
      if (eff.type !== 'destructible' || eff.hp <= 0) continue;
      const r = ((eff.data && eff.data.scale) || 60) * 0.7; // collision radius
      const dx = p.position.x - eff.position.x;
      const dy = p.position.y - eff.position.y;
      const dz = p.position.z - eff.position.z;
      if (dx*dx + dy*dy + dz*dz < r*r) {
        eff.hp -= p.damage;
        hitDestructible = true;
        break;
      }
    }
    if (hitDestructible) { dead.push(p.id); continue; }

    // Player hit? Skip own-team (no friendly fire).
    // v8.40: NA10 ; pierce. consumed flips true when the projectile is used up.
    // For pierceCount > 0 each entity hit decrements the counter; same target
    // can't be hit twice (piercedIds memo).
    let consumed = false;
    for (const player of state.players.values()) {
      if (!player.alive) continue;
      if (player.team === p.ownerTeam) continue;
      if (player.id === p.ownerId) continue;
      if (p.piercedIds && p.piercedIds.indexOf(player.id) >= 0) continue;
      if (_projectileHitsEntity(p, player.position, _hitRadius(player))) {
        // v8.35: snapshot shield BEFORE damage so _recordHit can tag the event
        // deterministically (NA38; LSS line 14913-14915).
        const shieldBefore = player.shield;
        const killed = _applyDamage(player, p.damage, state);
        // v8.39: NA8. Knockback impulse on hit. Direction from projectile
        // velocity (normalized); magnitude scales with damage. No knockback
        // while in spawn protection or stasis (those override movement).
        if (!killed && !player.spawnProtection && !player.inStasis) {
          _applyKnockback(player, p);
        }
        if (killed) {
          _killEntity(player, state.time);
          _creditKill(state, p.ownerType, p.ownerId);
        }
        _recordHit(state, p, player, killed, shieldBefore);
        // v8.40: NA10 ; pierce check.
        if (p.pierceCount && p.pierceCount > 0) {
          p.pierceCount--;
          if (!p.piercedIds) p.piercedIds = [];
          p.piercedIds.push(player.id);
          // Don't consume; keep flying. Only one hit per tick to avoid double-
          // hitting clustered enemies in the same frame.
        } else {
          consumed = true;
        }
        break;
      }
    }
    if (consumed) { dead.push(p.id); continue; }

    // Bot hit?
    for (const bot of state.bots.values()) {
      if (!bot.alive) continue;
      if (bot.team === p.ownerTeam) continue;
      if (bot.id === p.ownerId) continue;
      if (p.piercedIds && p.piercedIds.indexOf(bot.id) >= 0) continue;
      if (_projectileHitsEntity(p, bot.position, _hitRadius(bot))) {
        // v8.35: snapshot shield BEFORE damage (NA38).
        const shieldBefore = bot.shield;
        const killed = _applyDamage(bot, p.damage, state);
        // v8.39: NA8. Knockback on bots too.
        if (!killed) _applyKnockback(bot, p);
        if (killed) {
          _killEntity(bot, state.time);
          _creditKill(state, p.ownerType, p.ownerId);
        }
        _recordHit(state, p, bot, killed, shieldBefore);
        // v8.40: NA10 ; pierce check.
        if (p.pierceCount && p.pierceCount > 0) {
          p.pierceCount--;
          if (!p.piercedIds) p.piercedIds = [];
          p.piercedIds.push(bot.id);
        } else {
          consumed = true;
        }
        break;
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
// PUNCTURE Afterburner (slot 1); v8.16 adds the TRACKER kit (slots 0-3).
// `state` is needed by abilities that spawn projectiles (Tracker Rockets) or
// emit events (Sonar Lock); pure player-state buffs (Phase Dash, Afterburner)
// don't read it.
function _activatePlayerAbility(state: SimState, player: Player, slot: number): boolean {
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

  // ---- SYPHON kit (v8.27) ----

  if (lk === 'SYPHON' && slot === 0) {
    // Rocket Salvo (LSS line 8672-8680): 5 rockets in spread, 700 damage each.
    const dir = _facingDir(player.yaw, player.pitch);
    for (let i = 0; i < 5; i++) {
      const sx = (Math.random() - 0.5) * 0.18;
      const sy = (Math.random() - 0.5) * 0.18;
      const dx = dir.x + sx, dy = dir.y + sy, dz = dir.z;
      const mag = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;
      const ndx = dx / mag, ndy = dy / mag, ndz = dz / mag;
      const origin = {
        x: player.position.x + ndx * 80,
        y: player.position.y + 30 + ndy * 80,
        z: player.position.z + ndz * 80,
      };
      const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, { x: ndx, y: ndy, z: ndz });
      proj.damage = 700;
      proj.velocity.x = ndx * 800;
      proj.velocity.y = ndy * 800;
      proj.velocity.z = ndz * 800;
      proj.lifetime = 1.5;
      proj.color = 0xff4400;
    }
    state.events.push({
      type: 'fire',
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      loadoutKey: 'SYPHON',
      position: { x: player.position.x, y: player.position.y, z: player.position.z },
      time: state.time,
    });
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'SYPHON' && slot === 1) {
    // Energy Siphon (LSS line 8687-8755): drain nearest enemy's shield, heal
    // self by 800. Range 1500u, cone dot >= 0.5.
    const dir = _facingDir(player.yaw, player.pitch);
    let bestTarget: Player | Bot | null = null;
    let bestDist = Infinity;
    const all: Array<Player | Bot> = [...state.players.values(), ...state.bots.values()];
    for (const t of all) {
      if (!t.alive || t.team === player.team) continue;
      if ((t as Player).peerId === player.peerId) continue;
      const dx = t.position.x - player.position.x;
      const dy = t.position.y - player.position.y;
      const dz = t.position.z - player.position.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
      if (dist > 1500) continue;
      const inv = 1 / (dist || 1);
      const dot = dir.x * dx * inv + dir.y * dy * inv + dir.z * dz * inv;
      if (dot < 0.5) continue;
      if (dist < bestDist) { bestDist = dist; bestTarget = t; }
    }
    if (bestTarget) {
      const drain = Math.min(bestTarget.shield || 0, 800);
      bestTarget.shield = Math.max(0, (bestTarget.shield || 0) - drain);
      // Slow the target a bit (LSS does this too).
      bestTarget.velocity.x *= 0.4;
      bestTarget.velocity.y *= 0.4;
      bestTarget.velocity.z *= 0.4;
      // Heal self.
      player.shield = Math.min(player.maxShield, player.shield + 800);
    }
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'SYPHON' && slot === 2) {
    // Rearm (LSS line 8932): reset all ability cooldowns.
    for (let i = 0; i < 4; i++) {
      if (i !== slot) player.abilityCooldowns[i] = 0;
    }
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'SYPHON' && slot === 3) {
    // Upgrade Core (LSS line 9059-9082): permanent tier upgrades.
    // SIMPLIFIED: LSS has 3 tiers (Arc Rounds, Maelstrom, XO-16 Accelerator)
    // each granting different buffs. Ours stacks all-of-the-above for the
    // duration: bigger clip, +500 max shield, +25% damage, faster fire.
    player.maxClip = Math.max(player.maxClip, 50);
    player.clipAmmo = Math.min(player.clipAmmo + 10, player.maxClip);
    player.maxShield = player.maxShield + 500;
    player.shield = Math.min(player.maxShield, player.shield + 500);
    player.coreFireRateMult = 0.7;
    player.coreDamageMult = 1.25;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- BLASTER kit (v8.26) ----

  if (lk === 'BLASTER' && slot === 0) {
    // Power Shot (LSS line 8630-8670): high-damage charged hitscan.
    // SIMPLIFIED: LSS has a 1s charge phase before firing. Ours fires
    // instantly on press. Damage: 3200 (the charged-shot value from LSS).
    const dir = _facingDir(player.yaw, player.pitch);
    const origin = {
      x: player.position.x + dir.x * 80,
      y: player.position.y + 30 + dir.y * 80,
      z: player.position.z + dir.z * 80,
    };
    const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, dir);
    proj.damage = 3200;
    proj.velocity.x = dir.x * 4500;
    proj.velocity.y = dir.y * 4500;
    proj.velocity.z = dir.z * 4500;
    proj.lifetime = 0.5;
    proj.color = 0xff8844;
    state.events.push({
      type: 'fire',
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      loadoutKey: 'BLASTER',
      position: { x: origin.x, y: origin.y, z: origin.z },
      time: state.time,
    });
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'BLASTER' && slot === 1) {
    // Gun Shield (LSS line 8762-8767): frontal HP-based shield.
    // SIMPLIFIED: ours acts as a 0.4 damage multiplier while active (since
    // we don't model directional shields). Stronger than the held shields
    // because it's a one-shot panic button (not held-only).
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'BLASTER' && slot === 2) {
    // Mode Switch (LSS line 8927-8931): real implementation in v8.28. Sets
    // a 1s lockout; on expiry the weapon stats swap (close/long). Per-tick
    // logic in the player update path applies the swap.
    player.blasterSwitchTimer = 1.0;
    player.blasterPendingMode = (player.blasterMode === 'close') ? 'long' : 'close';
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'BLASTER' && slot === 3) {
    // Smart Core (LSS line 9522-9540): 8s of auto-aim + +20% damage.
    // SIMPLIFIED: ours just buffs the regular weapon (no auto-aim because
    // that needs server-side targeting that we'd add later). Buffs are
    // strong to match LSS's intent.
    player.coreFireRateMult = 0.5;
    player.coreDamageMult = 1.5;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- PYRO kit (v8.25) ----

  if (lk === 'PYRO' && slot === 0) {
    // Firewall (LSS line 8800-8870): line of fire 1500u long, 100u wide,
    // 400 DPS, 6s duration. _tickAreaDamageLine handles damage application.
    const dir = _facingDir(player.yaw, player.pitch);
    const start = {
      x: player.position.x + dir.x * 100,
      y: player.position.y + dir.y * 100,
      z: player.position.z + dir.z * 100,
    };
    _spawnWorldEffect(state, 'firewall', 'player', player.id, player.team, start,
      { dirX: dir.x, dirY: dir.y, dirZ: dir.z, length: 1500, width: 100, dps: 400 }, 1, 6);
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PYRO' && slot === 1) {
    // Thermal Shield (LSS line 8772-8780): held shield, damage reduction.
    // SIMPLIFIED: LSS has a power pool that drains while active and burns
    // close enemies. Ours is just a damage reducer for now.
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PYRO' && slot === 2) {
    // Incendiary Trap (LSS line 8870-8902): drop a sphere of fire 250u
    // ahead. _tickAreaDamageSphere handles damage.
    const dir = _facingDir(player.yaw, player.pitch);
    const trapPos = {
      x: player.position.x + dir.x * 250,
      y: player.position.y + dir.y * 250,
      z: player.position.z + dir.z * 250,
    };
    _spawnWorldEffect(state, 'incendiary', 'player', player.id, player.team, trapPos,
      { radius: 350, dps: 450 }, 1, 10);
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PYRO' && slot === 3) {
    // Flame Core (LSS line 9020-9050): 2s of massive AoE.
    // SIMPLIFIED: spawn a big incendiary at player position that lasts 2s.
    const flamePos = {
      x: player.position.x, y: player.position.y, z: player.position.z,
    };
    _spawnWorldEffect(state, 'incendiary', 'player', player.id, player.team, flamePos,
      { radius: 700, dps: 1500 }, 1, 2);
    player.coreFireRateMult = 0.6;
    player.coreDamageMult = 1.5;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- VORTEX kit (v8.24) ----

  if (lk === 'VORTEX' && slot === 0) {
    // Laser Shot (LSS line 8550-8600): instant hitscan beam with 2400
    // damage along the player's aim line.
    // v8.51: NA4 ; now uses real hitscan path. Walls block; first entity
    // hit takes the full 2400. The 'beam' event drives the client visual.
    const dir = _facingDir(player.yaw, player.pitch);
    const origin = {
      x: player.position.x + dir.x * 80,
      y: player.position.y + 30 + dir.y * 80,
      z: player.position.z + dir.z * 80,
    };
    _hitscanFire(state, 'player', player.id, player.team, origin, dir, 2400, 3000, false);
    state.events.push({
      type: 'fire',
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      loadoutKey: 'VORTEX',
      position: { x: origin.x, y: origin.y, z: origin.z },
      time: state.time,
    });
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'VORTEX' && slot === 1) {
    // Vortex Shield (LSS line 9091-9118): held shield, damage reduction.
    // Same shape as Sword Block; _applyDamage handles VORTEX too via the
    // generic loadout/active check below.
    // SIMPLIFIED: LSS reflects projectiles back; ours just dampens damage.
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'VORTEX' && slot === 2) {
    // Trip Wire (LSS line 8845-8870): drop a proximity mine 200u ahead.
    // _tickTripWire handles enemy contact + burst damage.
    const dir = _facingDir(player.yaw, player.pitch);
    const trapPos = {
      x: player.position.x + dir.x * 200,
      y: player.position.y + dir.y * 200,
      z: player.position.z + dir.z * 200,
    };
    _spawnWorldEffect(state, 'trip_wire', 'player', player.id, player.team, trapPos,
      { radius: 120, damage: 1200 }, 1, 12);
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'VORTEX' && slot === 3) {
    // Laser Core (LSS line 8995-9008): 4s of continuous high-power beam.
    // SIMPLIFIED: LSS spawns the beam every frame during duration; we
    // just buff regular fire by 0.4x interval (2.5x faster) and 2x damage
    // for the duration so the splitter rifle melts everything.
    player.coreFireRateMult = 0.4;
    player.coreDamageMult = 2.0;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- SLAYER remaining (v8.23) ----

  if (lk === 'SLAYER' && slot === 0) {
    // Arc Wave (LSS line 8624-8631): high-damage electric projectile.
    // Damage is 2000 normally, 3000 if Sword Core is active.
    // SIMPLIFIED: LSS sets isArcWave on the projectile to apply slow on hit
    // and to destroy walls/Gun Shields it passes near. Here we just deal
    // burst damage; the wall-destroy interaction will land when those
    // worldEffects exist for SLAYER to clash with.
    const coreOn = !!player.abilityActive[3];
    const dir = _facingDir(player.yaw, player.pitch);
    const origin = {
      x: player.position.x + dir.x * 80,
      y: player.position.y + 30 + dir.y * 80,
      z: player.position.z + dir.z * 80,
    };
    const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, dir);
    proj.damage = coreOn ? 3000 : 2000;
    proj.velocity.x = dir.x * 800;
    proj.velocity.y = dir.y * 800;
    proj.velocity.z = dir.z * 800;
    proj.lifetime = 1.5;
    proj.color = 0x44aaff;
    state.events.push({
      type: 'fire',
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      loadoutKey: 'SLAYER',
      position: { x: origin.x, y: origin.y, z: origin.z },
      time: state.time,
    });
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'SLAYER' && slot === 1) {
    // Sword Block (LSS line 7633-7637): hold-to-block; the actual damage
    // reduction is applied in _applyDamage when slot 1 is active. Here we
    // just turn the active flag on; LSS treats it as a held state with
    // duration 999 (effectively until cooldown ends or player toggles).
    // SIMPLIFIED: LSS gates "can't shoot" while blocking; ours doesn't
    // (might add later if balance demands).
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'SLAYER' && slot === 3) {
    // Sword Core (LSS line 9008-9020): 5s of empowered melee + arc waves.
    // SIMPLIFIED: LSS spawns periodic arc waves during the duration; ours
    // just buffs Arc Wave damage (read in slot 0) and the regular weapon
    // by 1.5x for the duration.
    player.coreFireRateMult = 0.7;
    player.coreDamageMult = 1.5;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- PUNCTURE remaining (v8.22) ----

  if (lk === 'PUNCTURE' && slot === 0) {
    // Cluster Missile (LSS line 8615-8623): single high-damage projectile.
    // SIMPLIFIED: LSS spawns a sustained 5s damage zone on impact; ours
    // just hits hard. Will be deepened when destructibles/zones land.
    const dir = _facingDir(player.yaw, player.pitch);
    const origin = {
      x: player.position.x + dir.x * 80,
      y: player.position.y + 30 + dir.y * 80,
      z: player.position.z + dir.z * 80,
    };
    const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, dir);
    proj.damage = 800;
    proj.velocity.x = dir.x * 1000;
    proj.velocity.y = dir.y * 1000;
    proj.velocity.z = dir.z * 1000;
    proj.lifetime = 1.5;
    proj.color = 0xff6600;
    state.events.push({
      type: 'fire',
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      loadoutKey: 'PUNCTURE',
      position: { x: origin.x, y: origin.y, z: origin.z },
      time: state.time,
    });
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PUNCTURE' && slot === 2) {
    // Tether Trap (LSS line 8890-8902): spawns a tether worldEffect 300u
    // ahead of the player. Slows enemies in radius. _tickAreaSlow handles it.
    const dir = _facingDir(player.yaw, player.pitch);
    const trapPos = {
      x: player.position.x + dir.x * 300,
      y: player.position.y + dir.y * 300,
      z: player.position.z + dir.z * 300,
    };
    _spawnWorldEffect(state, 'tether', 'player', player.id, player.team, trapPos,
      { radius: 250, slowMult: 0.4 }, 1, 15);
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'PUNCTURE' && slot === 3) {
    // Afterburner Core: 5s of speed boost + rocket barrage at start.
    // SIMPLIFIED: LSS line 9020-9055 has the rocket barrage spawn over the
    // duration; we fire 8 rockets at activation then leave the speed boost
    // running for the duration.
    player.afterburnerMult = 2.5;
    player.coreFireRateMult = 0.6;
    player.coreDamageMult = 1.3;
    const dir = _facingDir(player.yaw, player.pitch);
    for (let i = 0; i < 8; i++) {
      const sx = (Math.random() - 0.5) * 0.25;
      const sy = (Math.random() - 0.5) * 0.25;
      const dx = dir.x + sx, dy = dir.y + sy, dz = dir.z;
      const mag = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;
      const ndx = dx / mag, ndy = dy / mag, ndz = dz / mag;
      const origin = {
        x: player.position.x + ndx * 80,
        y: player.position.y + 30 + ndy * 80,
        z: player.position.z + ndz * 80,
      };
      const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, { x: ndx, y: ndy, z: ndz });
      proj.damage = 700;
      proj.velocity.x = ndx * 800;
      proj.velocity.y = ndy * 800;
      proj.velocity.z = ndz * 800;
      proj.lifetime = 1.2;
      proj.color = 0xff7733;
    }
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  // ---- TRACKER kit (v8.16, simplified) ----

  if (lk === 'TRACKER' && slot === 0) {
    // Tracker Rockets: 5 missiles in a forward spread.
    // SIMPLIFIED: LSS line 8633-8665 has a 3-stack lock system fed by Sonar
    // Lock; locked targets receive homing missiles. Here we fire 5 unguided
    // missiles in a tight spread regardless of lock state. Damage 1000 each
    // (matches LSS), velocity 900 units/s, lifetime 1.0s.
    const dir = _facingDir(player.yaw, player.pitch);
    for (let i = 0; i < 5; i++) {
      const sx = (Math.random() - 0.5) * 0.20;
      const sy = (Math.random() - 0.5) * 0.20;
      const dx = dir.x + sx, dy = dir.y + sy, dz = dir.z;
      const mag = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;
      const ndx = dx / mag, ndy = dy / mag, ndz = dz / mag;
      const origin = {
        x: player.position.x + ndx * 80,
        y: player.position.y + 30 + ndy * 80,
        z: player.position.z + ndz * 80,
      };
      const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, { x: ndx, y: ndy, z: ndz });
      // Override defaults: tracker missiles hit hard and live a touch longer.
      proj.damage = 1000;
      proj.velocity.x = ndx * 900;
      proj.velocity.y = ndy * 900;
      proj.velocity.z = ndz * 900;
      proj.lifetime = 1.0;
      proj.color = 0xffaa00;
      // Emit a fire event so the client plays the salvo sound spatially.
      state.events.push({
        type: 'fire',
        shooterType: 'player',
        shooterId: player.id,
        shooterPeerId: player.peerId,
        shooterTeam: player.team,
        loadoutKey: 'TRACKER',
        position: { x: origin.x, y: origin.y, z: origin.z },
        time: state.time,
      });
    }
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'TRACKER' && slot === 1) {
    // Particle Wall (simplified): 5s damage immunity buff.
    // SIMPLIFIED: LSS line 8780-8806 spawns a 400x300 plane mesh in front of
    // the player as a worldEffect with 5000 HP that absorbs incoming hits.
    // Here we just flag the player as damage-immune for the duration; the
    // client can read player.damageImmuneTimer to render a shield bubble.
    player.damageImmuneTimer = 5;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'TRACKER' && slot === 2) {
    // Sonar Lock (simplified): emit a 'sonar_lock' event with the IDs of all
    // enemies in a 2000u forward cone. Client plays sonar pings + highlights
    // those enemies for the duration. Doesn't actually build lock stacks for
    // Tracker Rockets in this simplified version (rockets fire unguided).
    // SIMPLIFIED: LSS line 8904-8926 increments player.trackerLocks per hit
    // and gates Tracker Rockets behind a 3-stack lock requirement.
    const dir = _facingDir(player.yaw, player.pitch);
    const SONAR_RANGE = 2000;
    const SONAR_DOT = 0.3;
    const lockedIds: number[] = [];
    for (const bot of state.bots.values()) {
      if (!bot.alive || bot.team === player.team) continue;
      const dx = bot.position.x - player.position.x;
      const dy = bot.position.y - player.position.y;
      const dz = bot.position.z - player.position.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
      if (dist > SONAR_RANGE) continue;
      const inv = 1 / (dist || 1);
      const dot = dir.x * dx * inv + dir.y * dy * inv + dir.z * dz * inv;
      if (dot < SONAR_DOT) continue;
      lockedIds.push(bot.id);
    }
    for (const other of state.players.values()) {
      if (!other.alive || other.team === player.team || other.id === player.id) continue;
      const dx = other.position.x - player.position.x;
      const dy = other.position.y - player.position.y;
      const dz = other.position.z - player.position.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
      if (dist > SONAR_RANGE) continue;
      const inv = 1 / (dist || 1);
      const dot = dir.x * dx * inv + dir.y * dy * inv + dir.z * dz * inv;
      if (dot < SONAR_DOT) continue;
      lockedIds.push(other.id);
    }
    state.events.push({
      type: 'sonar_lock' as any, // SimEvent's type union widened informally; client switches on it
      shooterType: 'player',
      shooterId: player.id,
      shooterPeerId: player.peerId,
      shooterTeam: player.team,
      position: { x: player.position.x, y: player.position.y, z: player.position.z },
      time: state.time,
      // ad-hoc payload field: target IDs to highlight client-side
      // (TS sees `any` here so this compiles; client reads ev.targetIds)
      targetId: lockedIds.length > 0 ? lockedIds[0] : 0,
    });
    // Stash the full id list on the event so client can render all of them.
    (state.events[state.events.length - 1] as any).targetIds = lockedIds;
    player.abilityCooldowns[slot] = cdTable[slot];
    player.abilityActive[slot] = true;
    player.abilityTimers[slot] = durTable[slot];
    return true;
  }

  if (lk === 'TRACKER' && slot === 3) {
    // Salvo Core (simplified): 3s of doubled fire rate + 1.5x damage.
    // SIMPLIFIED: LSS line 9044-9054 + 9511-9521 spawns remote-guided missiles
    // that steer toward the player's crosshair every frame. Here we just
    // enable rapid + heavy regular fire for the duration; player still has to
    // hold the trigger.
    player.coreFireRateMult = 0.5;   // half the fire interval = 2x rate
    player.coreDamageMult = 1.5;
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
  // v8.16: tick simplified TRACKER buffs.
  if (player.damageImmuneTimer > 0) {
    player.damageImmuneTimer = Math.max(0, player.damageImmuneTimer - dt);
  }
  // v8.18: spawn protection + reload tick.
  if (player.spawnProtection > 0) {
    player.spawnProtection = Math.max(0, player.spawnProtection - dt);
  }
  if (player.reloading) {
    player.reloadTimer = Math.max(0, player.reloadTimer - dt);
    if (player.reloadTimer <= 0) {
      player.clipAmmo = player.maxClip;
      player.reloading = false;
    }
  }
  // v8.29: stasis tick. While inStasis, player is immobilized and shield
  // recharges over the duration (LSS line 12442-12470).
  if (player.inStasis) {
    player.stasisTimer = Math.max(0, player.stasisTimer - dt);
    const recharge = player.maxShield / Math.max(0.1, player.stasisDuration);
    player.shield = Math.min(player.maxShield, player.shield + recharge * dt);
    player.velocity.x = 0; player.velocity.y = 0; player.velocity.z = 0;
    if (player.stasisTimer <= 0) player.inStasis = false;
  }
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

// v8.21: world-effect helpers ; spawn, tick, area damage.
function _spawnWorldEffect(
  state: SimState,
  type: WorldEffect['type'],
  ownerType: 'player' | 'bot',
  ownerId: number,
  ownerTeam: number,
  position: Vec3,
  data: any,
  hp: number,
  duration: number,
): WorldEffect {
  const id = state.nextEntityId++;
  const eff: WorldEffect = {
    id, type, ownerType, ownerId, ownerTeam,
    position: { x: position.x, y: position.y, z: position.z },
    data: data || {},
    hp, maxHp: hp,
    timer: duration,
    spawnedAt: state.time,
  };
  state.worldEffects.set(id, eff);
  return eff;
}

function _tickWorldEffects(state: SimState, dt: number): void {
  if (state.worldEffects.size === 0) return;
  const toRemove: number[] = [];
  for (const eff of state.worldEffects.values()) {
    eff.timer -= dt;
    if (eff.timer <= 0 || eff.hp <= 0) {
      toRemove.push(eff.id);
      continue;
    }
    // Per-type area-of-effect ticking. Each branch is small and
    // self-contained so individual abilities can be ported incrementally.
    if (eff.type === 'firewall') {
      // Linear fire: data = {dirX, dirY, dirZ, length, width}. Damages
      // enemy entities within `width` of the line for `dps * dt` per tick.
      _tickAreaDamageLine(state, eff, dt);
    }
    else if (eff.type === 'incendiary' || eff.type === 'gas') {
      // Spherical hazard: data = {radius, dps}. Damages enemies inside.
      _tickAreaDamageSphere(state, eff, dt);
    }
    else if (eff.type === 'tether') {
      // Slows enemies inside its radius. data = {radius, slowMult}.
      _tickAreaSlow(state, eff, dt);
    }
    else if (eff.type === 'trip_wire') {
      // Proximity mines: detonate on enemy contact, dealing burst damage
      // and removing self.
      _tickTripWire(state, eff);
    }
    else if (eff.type === 'stasis_pickup') {
      // v8.29: pickup that traps the first player to touch it (LSS line
      // 12251, 12442-12470). On contact: set the player's stasis state and
      // remove the pickup from the world.
      _tickStasisPickup(state, eff);
    }
    // particle_wall is hp-driven (handled by projectile collision pass);
    // no per-tick logic.
  }
  for (const id of toRemove) state.worldEffects.delete(id);
}

function _tickStasisPickup(state: SimState, eff: WorldEffect): void {
  const radius = (eff.data && eff.data.radius) || 120;
  const r2 = radius * radius;
  for (const p of state.players.values()) {
    if (!p.alive || p.inStasis) continue;
    const dx = p.position.x - eff.position.x;
    const dy = p.position.y - eff.position.y;
    const dz = p.position.z - eff.position.z;
    if (dx * dx + dy * dy + dz * dz < r2) {
      p.inStasis = true;
      p.stasisTimer = p.stasisDuration;
      p.velocity.x = 0; p.velocity.y = 0; p.velocity.z = 0;
      eff.timer = 0;     // mark for cleanup
      eff.hp = 0;
      return;
    }
  }
}

// v8.47: NA12. Seeded PRNG (mulberry32). Used for round-deterministic
// placement so every connected client agrees on where destructibles +
// stasis fields spawn given the same match.seed. Server is authoritative;
// this just makes the math reproducible for replays + cross-checking.
function _seededRng(seed: number): () => number {
  let t = (seed | 0) || 1;
  return function () {
    t = (t + 0x6D2B79F5) | 0;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

// v8.30: destructible obstacles (LSS line 7383+, ClusterObstacle). Each is
// a world entity with HP that blocks/absorbs projectiles. Spawned at round
// start in non-spawn rooms.
function _spawnDestructiblesForRound(state: SimState): void {
  const level = state.level;
  if (!level || !level.rooms || level.rooms.length === 0) return;
  const candidates = level.rooms.filter(r => r.team !== 'A' && r.team !== 'B');
  // v8.47: NA12 ; seed RNG from match.seed for deterministic placement.
  // Mix in currentRound so each round in a match gets a fresh layout.
  const rng = _seededRng(state.match.seed ^ (state.match.currentRound * 0x9E3779B9));
  for (const room of candidates) {
    // 2-3 obstacles per room, placed at deterministic offsets within the sphere.
    const count = 2 + Math.floor(rng() * 2);
    for (let i = 0; i < count; i++) {
      const off = room.radius * (0.3 + rng() * 0.4);
      const ang = rng() * Math.PI * 2;
      const phi = (rng() - 0.5) * Math.PI * 0.5;
      const pos: Vec3 = {
        x: room.center.x + Math.cos(ang) * Math.cos(phi) * off,
        y: room.center.y + Math.sin(phi) * off,
        z: room.center.z + Math.sin(ang) * Math.cos(phi) * off,
      };
      const scale = 60 + rng() * 40;
      const shapeIdx = Math.floor(rng() * 4); // 0..3: dia/cross/wedge/box
      _spawnWorldEffect(state, 'destructible', 'player', 0, 0, pos,
        { scale, shape: shapeIdx, color: 0x99aabb }, 1500, 999);
    }
  }
}

// v8.29: spawn 3 stasis pickups at random map positions when a round starts.
// SIMPLIFIED: LSS spawns batches periodically over the round (line 12379-12386);
// ours spawns once at round start.
function _spawnStasisFieldsForRound(state: SimState): void {
  const level = state.level;
  if (!level || !level.rooms || level.rooms.length === 0) return;
  // v8.47: NA12 ; deterministic placement from match.seed + currentRound.
  // Different mix-in than destructibles so they don't share patterns.
  const rng = _seededRng(state.match.seed ^ (state.match.currentRound * 0x85EBCA6B));
  // Pick 3 distinct non-spawn rooms; place a pickup at each room center
  // (offset slightly so they aren't in the dead center).
  const candidates = level.rooms.filter(r => r.team !== 'A' && r.team !== 'B');
  const pool = candidates.length >= 3 ? candidates : level.rooms;
  for (let i = 0; i < 3 && pool.length > 0; i++) {
    const r = pool[Math.floor(rng() * pool.length)];
    const off = r.radius * 0.4;
    const ang = rng() * Math.PI * 2;
    const pos: Vec3 = {
      x: r.center.x + Math.cos(ang) * off,
      y: r.center.y + (rng() - 0.5) * 60,
      z: r.center.z + Math.sin(ang) * off,
    };
    _spawnWorldEffect(state, 'stasis_pickup', 'player', 0, 0, pos,
      { radius: 120 }, 1, 999); // 999s timer = lasts the round
  }
}

function _tickAreaDamageLine(state: SimState, eff: WorldEffect, dt: number): void {
  const d = eff.data || {};
  const dx = d.dirX || 0, dy = d.dirY || 0, dz = d.dirZ || -1;
  const len = d.length || 1500;
  const width = d.width || 100;
  const dps = d.dps || 400;
  // Project each enemy onto the line; damage if within width.
  const all: Array<Player | Bot> = [...state.players.values(), ...state.bots.values()];
  for (const t of all) {
    if (!t.alive || t.team === eff.ownerTeam) continue;
    const px = t.position.x - eff.position.x;
    const py = t.position.y - eff.position.y;
    const pz = t.position.z - eff.position.z;
    const dot = Math.max(0, Math.min(len, px * dx + py * dy + pz * dz));
    const cx = dx * dot, cy = dy * dot, cz = dz * dot;
    const ex = px - cx, ey = py - cy, ez = pz - cz;
    const dist2 = ex * ex + ey * ey + ez * ez;
    if (dist2 < width * width) _applyDamage(t, dps * dt, state);
  }
}

function _tickAreaDamageSphere(state: SimState, eff: WorldEffect, dt: number): void {
  const d = eff.data || {};
  const radius = d.radius || 300;
  const dps = d.dps || 200;
  const r2 = radius * radius;
  const all: Array<Player | Bot> = [...state.players.values(), ...state.bots.values()];
  for (const t of all) {
    if (!t.alive || t.team === eff.ownerTeam) continue;
    const dx = t.position.x - eff.position.x;
    const dy = t.position.y - eff.position.y;
    const dz = t.position.z - eff.position.z;
    if (dx * dx + dy * dy + dz * dz < r2) _applyDamage(t, dps * dt, state);
  }
}

function _tickAreaSlow(state: SimState, eff: WorldEffect, dt: number): void {
  const d = eff.data || {};
  const radius = d.radius || 250;
  const r2 = radius * radius;
  // We damp velocity per tick instead of tracking a status effect; cheap
  // approximation of LSS's tetherSlowTimer system. Owner's team is unaffected.
  const all: Array<Player | Bot> = [...state.players.values(), ...state.bots.values()];
  for (const t of all) {
    if (!t.alive || t.team === eff.ownerTeam) continue;
    const dx = t.position.x - eff.position.x;
    const dy = t.position.y - eff.position.y;
    const dz = t.position.z - eff.position.z;
    if (dx * dx + dy * dy + dz * dz < r2) {
      const k = Math.exp(-2 * dt); // ~50% slowdown per second of contact
      t.velocity.x *= k; t.velocity.y *= k; t.velocity.z *= k;
    }
  }
}

function _tickTripWire(state: SimState, eff: WorldEffect): void {
  const d = eff.data || {};
  const radius = d.radius || 120;
  const burst = d.damage || 800;
  const r2 = radius * radius;
  const all: Array<Player | Bot> = [...state.players.values(), ...state.bots.values()];
  for (const t of all) {
    if (!t.alive || t.team === eff.ownerTeam) continue;
    const dx = t.position.x - eff.position.x;
    const dy = t.position.y - eff.position.y;
    const dz = t.position.z - eff.position.z;
    if (dx * dx + dy * dy + dz * dz < r2) {
      _applyDamage(t, burst, state);
      eff.timer = 0;       // detonate (cleanup next tick)
      eff.hp = 0;
      return;
    }
  }
}

function _onAbilityExpire(player: Player, slot: number): void {
  const lk = player.loadoutKey || '';
  if (lk === 'PUNCTURE' && slot === 1) {
    player.afterburnerMult = 1.0;
  }
  // v8.22: Afterburner Core expiry resets all the buffs it stacked.
  if (lk === 'PUNCTURE' && slot === 3) {
    player.afterburnerMult = 1.0;
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // v8.23: SLAYER Sword Core expiry.
  if (lk === 'SLAYER' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // v8.24: VORTEX Laser Core expiry.
  if (lk === 'VORTEX' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // v8.25: PYRO Flame Core expiry.
  if (lk === 'PYRO' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // v8.26: BLASTER Smart Core expiry.
  if (lk === 'BLASTER' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // v8.27: SYPHON Upgrade Core expiry. Reset the buffs we stacked.
  if (lk === 'SYPHON' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
    // Note: maxClip/maxShield buffs aren't reset here; LSS treats them as
    // permanent within a match. A future round-reset path can clear them
    // when applyPlayerLoadout is called between rounds.
  }
  // v8.16: TRACKER ability expiry.
  if (lk === 'TRACKER' && slot === 1) {
    player.damageImmuneTimer = 0;
  }
  if (lk === 'TRACKER' && slot === 3) {
    player.coreFireRateMult = 1.0;
    player.coreDamageMult = 1.0;
  }
  // (SLAYER Phase Dash is instantaneous; Tracker Rockets and Sonar Lock
  // don't carry persistent buffs, so no expire side-effect for slots 0/2.)
}

// ---- Tick ----

const NO_INPUT: PlayerInput = { forward: 0, right: 0, up: 0, yaw: 0, pitch: 0, fire: false, abilityPress: null, reload: false, dash: false };

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
        _respawnPlayer(player, state, state.level);
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
    // v8.28: spinup tick (LSS line 8085-8090). For chassis whose weapon has
    // spinup > 0, trigger held charges the timer; release drains at 2x rate.
    // Fire path gates on spunUp. Mirror table because we don't carry the
    // full weapon spec on Player.
    const _SPINUP = { BLASTER: 1.2, SYPHON: 0.4 };
    const spinupNeeded = (_SPINUP as any)[player.loadoutKey || ''] || 0;
    if (spinupNeeded > 0) {
      if (input.fire) {
        player.spinupTimer = Math.min(spinupNeeded, player.spinupTimer + dt);
        if (player.spinupTimer >= spinupNeeded) player.spunUp = true;
      } else {
        player.spinupTimer = Math.max(0, player.spinupTimer - dt * 2);
        if (player.spinupTimer <= 0.001) player.spunUp = false;
      }
    } else {
      player.spunUp = true; // weapons without spinup are always ready
    }
    // v8.28: BLASTER mode-switch lockout tick (LSS line 9855-9877). During
    // the 1s lockout, fire is blocked. On expiry, weapon stats swap based
    // on blasterPendingMode.
    if (player.blasterSwitchTimer > 0) {
      player.blasterSwitchTimer = Math.max(0, player.blasterSwitchTimer - dt);
      if (player.blasterSwitchTimer <= 0 && player.blasterPendingMode !== player.blasterMode) {
        player.blasterMode = player.blasterPendingMode;
        // Apply mode-specific stats (LSS line 9863-9877).
        const ammoPct = player.maxClip > 0 ? player.clipAmmo / player.maxClip : 1;
        if (player.blasterMode === 'close') {
          player.weaponFireRate = 0.05;
          player.weaponDamage = 85;
          player.maxClip = 150;
          player.clipAmmo = Math.round(ammoPct * 150);
        } else {
          player.weaponFireRate = 0.08;
          player.weaponDamage = 100;
          player.maxClip = 100;
          player.clipAmmo = Math.round(ammoPct * 100);
        }
      }
    }
    // v8.15: full-auto firing (matches LSS line 8097: `if (firing && fireTimer <= 0)`).
    // The `!player.prevFire` rising-edge gate forced single-shot behavior;
    // for chainguns and most weapons, holding the trigger should fire at the
    // weapon's fireRate cadence. Semi-auto behavior is captured by the
    // weapon's fireRate alone (a 1.5s railgun naturally feels semi).
    // v8.18: gate fire on having ammo + not currently reloading.
    // v8.28: also gate on spunUp + not in mode-switch lockout.
    if (canFire && input.fire && player.fireTimer <= 0
        && !player.reloading && player.clipAmmo > 0
        && player.spunUp && player.blasterSwitchTimer <= 0) {
      const dir = _facingDir(player.yaw, player.pitch);
      const origin = {
        x: player.position.x + dir.x * 80,
        y: player.position.y + 30 + dir.y * 80,
        z: player.position.z + dir.z * 80,
      };
      const proj = _spawnProjectile(state, 'player', player.id, player.team, origin, dir);
      // v8.16: TRACKER Salvo Core (simplified) buffs damage and fire rate
      // for its 3-second duration. coreDamageMult/coreFireRateMult default
      // to 1.0 outside the core window so this is a no-op normally.
      proj.damage = player.weaponDamage * player.coreDamageMult;
      player.fireTimer = player.weaponFireRate * player.coreFireRateMult;
      // v8.18: decrement clip; auto-reload when empty (LSS line 8104-8107).
      // Weapons with clipSize >= 999 (Smart Core etc.) skip the decrement.
      if (player.maxClip > 0 && player.maxClip < 999) {
        player.clipAmmo = Math.max(0, player.clipAmmo - 1);
        if (player.clipAmmo <= 0) {
          player.reloading = true;
          player.reloadTimer = 2.0; // LSS line 8120
        }
      }
      state.events.push({
        type: 'fire',
        shooterType: 'player',
        shooterId: player.id,
        shooterPeerId: player.peerId,
        shooterTeam: player.team,
        loadoutKey: player.loadoutKey || undefined,
        position: { x: origin.x, y: origin.y, z: origin.z },
        time: state.time,
      });
    }
    player.prevFire = !!input.fire;

    // v8.8: ability activation + tick. Only during 'playing' to avoid
    // spurious activations during warmup.
    _tickPlayerAbilities(player, dt);
    if (canFire && input.abilityPress != null) {
      _activatePlayerAbility(state, player, input.abilityPress | 0);
    }
    // v8.33: manual reload (LSS line 8111-8114). Triggers a reload if clip
    // isn't full + not already reloading + not an infinite-clip weapon.
    if (canFire && input.reload && !player.reloading
        && player.clipAmmo < player.maxClip && player.maxClip < 999) {
      player.reloading = true;
      player.reloadTimer = 2.0;
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

    // v8.44: dash burst (LSS line 9898-9914). Rising-edge press while not
    // already dashing AND with a charge available AND match is playing
    // (not warmup; LSS line 9902 explicitly blocks dash before launch).
    // Direction = current velocity if moving; else forward facing. Velocity
    // is REPLACED with dashDir * dashSpeed for the burst (LSS line 9908).
    const dashEdge = !!input.dash && !player.prevDash;
    if (dashEdge && !player.dashActive && player.dashCharges > 0
        && state.match.state === 'playing') {
      let ddx = player.velocity.x, ddy = player.velocity.y, ddz = player.velocity.z;
      const dvLen = Math.sqrt(ddx * ddx + ddy * ddy + ddz * ddz);
      if (dvLen < 10) {
        // No movement; use facing direction (yaw + pitch).
        const fd = _facingDir(player.yaw, player.pitch);
        ddx = fd.x; ddy = fd.y; ddz = fd.z;
      } else {
        ddx /= dvLen; ddy /= dvLen; ddz /= dvLen;
      }
      player.velocity.x = ddx * player.dashSpeed;
      player.velocity.y = ddy * player.dashSpeed;
      player.velocity.z = ddz * player.dashSpeed;
      player.dashActive = true;
      player.dashTimer = player.dashDuration;
      player.dashCharges--;
      // Re-arm cooldown timer when consuming a charge.
      if (player.dashCooldownTimer <= 0) player.dashCooldownTimer = player.dashCooldown;
    }
    player.prevDash = !!input.dash;

    // v8.44: dash duration tick (LSS line 7916-7923).
    if (player.dashActive) {
      player.dashTimer -= dt;
      if (player.dashTimer <= 0) player.dashActive = false;
    }
    // v8.44: dash charge regen (LSS line 7925-7932). Cooldown regenerates
    // one charge at a time; re-arms after each regen until charges full.
    if (player.dashCooldownTimer > 0) {
      player.dashCooldownTimer -= dt;
      if (player.dashCooldownTimer <= 0 && player.dashCharges < player.maxDashes) {
        player.dashCharges++;
        if (player.dashCharges < player.maxDashes) player.dashCooldownTimer = player.dashCooldown;
      }
    }

    // Clamp to chassis max speed.
    // v8.44: max speed cap is dashSpeed during dash, else flight speed × afterburner mult.
    const sx = player.velocity.x, sy2 = player.velocity.y, sz = player.velocity.z;
    const speed = Math.sqrt(sx * sx + sy2 * sy2 + sz * sz);
    const effectiveMax = player.dashActive
      ? player.dashSpeed
      : (player.maxSpeed * player.afterburnerMult);
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
        _respawnBot(bot, state, state.level);
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

  // 3a) v8.45: NA1 ; player-vs-player + player-vs-bot collision. Run AFTER
  // both groups have integrated + done wall collision so the per-pair push
  // doesn't fight the SDF resolver. O(n²) but n is small (≤12 entities).
  // Mass weighting from chassis.mass via _entityMass; lighter ships bounce
  // off heavier ones more. Spawn-protected ships are intangible (push others
  // out of the way without taking the hit themselves).
  _resolveEntityCollisions(state);

  // 3b) Projectile motion + collision + damage
  _tickProjectiles(state, dt);
  _tickWorldEffects(state, dt);

  // 4) Match state machine
  // v8.18: ports LSS line 9918-10003 (updateRoundSystem). Round ends when
  // one team is fully wiped (alive count = 0) or the round timer expires.
  // Tie on time-out goes to team A by LSS convention. After ROUNDS_TO_WIN
  // round wins, transition to matchEnd; otherwise back to select for next
  // ship pick.
  if (state.match.state === 'select') {
    // Lobby ; main.ts decides when to transition to 'warmup' (when all
    // ready). The simulation just holds.
  } else if (state.match.state === 'warmup') {
    state.match.warmupTimer = Math.max(0, state.match.warmupTimer - dt);
    if (state.match.warmupTimer <= 0) {
      state.match.state = 'playing';
      state.match.roundTimer = ROUND_TIME;
      // v8.29: spawn stasis field pickups when the round actually starts.
      _spawnStasisFieldsForRound(state);
      // v8.30: spawn destructibles in non-spawn rooms.
      _spawnDestructiblesForRound(state);
    }
  } else if (state.match.state === 'playing') {
    state.match.roundTimer = Math.max(0, state.match.roundTimer - dt);

    // Count alive entities per team (players + bots).
    let aliveA = 0, aliveB = 0;
    for (const p of state.players.values()) {
      if (!p.alive) continue;
      if (p.team === TEAM_A) aliveA++;
      else if (p.team === TEAM_B) aliveB++;
    }
    for (const b of state.bots.values()) {
      if (!b.alive) continue;
      if (b.team === TEAM_A) aliveA++;
      else if (b.team === TEAM_B) aliveB++;
    }

    // LSS line 9961-9973: end the round when a team is wiped or time runs out.
    let winner: 'A' | 'B' | null = null;
    if (aliveB === 0 && aliveA > 0) winner = 'A';
    else if (aliveA === 0 && aliveB > 0) winner = 'B';
    else if (state.match.roundTimer <= 0) winner = 'A'; // tie goes to A (LSS convention)
    if (winner) {
      if (winner === 'A') state.match.scoreA++;
      else state.match.scoreB++;
      state.match.state = 'roundEnd';
      state.match.warmupTimer = ROUND_END_LINGER_LSS;
      state.events.push({
        type: 'round_end' as any,
        shooterType: 'player',
        shooterId: 0,
        time: state.time,
        // ad-hoc: which team won this round and the new score
        // (cast as any for the SimEvent union; client switches on type)
      } as any);
      const ev = state.events[state.events.length - 1] as any;
      ev.winner = winner;
      ev.scoreA = state.match.scoreA;
      ev.scoreB = state.match.scoreB;
    }
  } else if (state.match.state === 'roundEnd') {
    state.match.warmupTimer = Math.max(0, state.match.warmupTimer - dt);
    if (state.match.warmupTimer <= 0) {
      // LSS line 9977-10001: matchEnd if either team hit ROUNDS_TO_WIN; else
      // back to select for next pick.
      if (state.match.scoreA >= ROUNDS_TO_WIN || state.match.scoreB >= ROUNDS_TO_WIN) {
        state.match.state = 'matchEnd';
        state.match.matchEndTimer = MATCH_END_LINGER;
        state.events.push({
          type: 'match_end' as any,
          shooterType: 'player',
          shooterId: 0,
          time: state.time,
        } as any);
        const ev = state.events[state.events.length - 1] as any;
        ev.winner = state.match.scoreA >= ROUNDS_TO_WIN ? 'A' : 'B';
        ev.scoreA = state.match.scoreA;
        ev.scoreB = state.match.scoreB;
      } else {
        state.match.state = 'select';
        state.match.currentRound++;
        // Clear ready on every player so they have to commit again.
        for (const p of state.players.values()) {
          p.ready = false;
          // v8.29: clear stasis carryover between rounds.
          p.inStasis = false;
          p.stasisTimer = 0;
        }
        // v8.29-v8.30: drop stasis pickups + destructibles left over from
        // the previous round so the next round respawns clean.
        for (const [id, eff] of [...state.worldEffects.entries()]) {
          if (eff.type === 'stasis_pickup' || eff.type === 'destructible') {
            state.worldEffects.delete(id);
          }
        }
      }
    }
  } else if (state.match.state === 'matchEnd') {
    state.match.matchEndTimer = Math.max(0, state.match.matchEndTimer - dt);
    if (state.match.matchEndTimer <= 0) {
      // Reset scores + round counter, return to lobby for a fresh series.
      // LSS line 10075-10084: also clears per-player stats so the new match
      // starts clean.
      state.match.scoreA = 0;
      state.match.scoreB = 0;
      state.match.currentRound = 1;
      state.match.state = 'select';
      for (const p of state.players.values()) {
        p.ready = false;
        p.kills = 0;
        p.deaths = 0;
        p.damageDealt = 0;
      }
      for (const b of state.bots.values()) {
        b.kills = 0;
        b.deaths = 0;
        b.damageDealt = 0;
      }
    }
  }
}

const ROUND_END_LINGER = ROUND_END_LINGER_LSS;

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
  // v8.43: NA7 ; per-chassis hull radius for wall + obstacle collision.
  const r = _hullRadius(player);
  _resolveSDF(player.position, player.velocity, r, level);
  _resolveAABBs(player.position, player.velocity, r, level.obstacles);
}

function _resolveBotCollision(bot: Bot, level: Level): void {
  // v8.43: NA7 ; bots use the same per-chassis radius (no longer 0.9x).
  const r = _hullRadius(bot);
  _resolveSDF(bot.position, bot.velocity, r, level);
  _resolveAABBs(bot.position, bot.velocity, r, level.obstacles);
}

// v8.45: NA1. Per-chassis mass for collision response (heavier ships push
// lighter ones harder). Defaults to 8000 (Corvette) when no loadout.
function _entityMass(ent: Player | Bot): number {
  const lk = (ent as any).loadoutKey;
  if (!lk) return 8000;
  const ld = LOADOUTS[lk as LoadoutKey];
  if (!ld) return 8000;
  const ch = CHASSIS[ld.chassis];
  return ch ? ch.mass : 8000;
}

// v8.45: NA1. Player-vs-player + player-vs-bot collision. Sphere-vs-sphere
// overlap → mass-weighted position separation along contact normal +
// reflective velocity component along the normal so they bounce apart
// instead of grinding through each other. Spawn-protected entities are
// intangible: they push others out of the way without absorbing the
// momentum themselves. O(n²) but typically ≤ 12 alive entities.
function _resolveEntityCollisions(state: SimState): void {
  // Collect all alive entities (players + bots) into one list for uniform
  // pair iteration.
  const ents: Array<Player | Bot> = [];
  for (const p of state.players.values()) {
    if (p.alive) ents.push(p);
  }
  for (const b of state.bots.values()) {
    if (b.alive) ents.push(b);
  }
  for (let i = 0; i < ents.length; i++) {
    const a = ents[i];
    const ra = _hullRadius(a);
    const ma = _entityMass(a);
    const aProtected = (a as any).spawnProtection && (a as any).spawnProtection > 0;
    for (let j = i + 1; j < ents.length; j++) {
      const b = ents[j];
      const rb = _hullRadius(b);
      const dx = b.position.x - a.position.x;
      const dy = b.position.y - a.position.y;
      const dz = b.position.z - a.position.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      const minD = ra + rb;
      if (d2 >= minD * minD) continue; // no overlap
      const d = Math.sqrt(d2) || 0.001;
      // Contact normal pointing from a → b.
      const nx = dx / d, ny = dy / d, nz = dz / d;
      const overlap = minD - d;
      const mb = _entityMass(b);
      const bProtected = (b as any).spawnProtection && (b as any).spawnProtection > 0;
      // Position separation. Spawn-protected entities don't move; the other
      // takes the full push.
      let pushA: number, pushB: number;
      if (aProtected && bProtected) { pushA = pushB = overlap * 0.5; }
      else if (aProtected)          { pushA = 0;            pushB = overlap; }
      else if (bProtected)          { pushA = overlap;      pushB = 0; }
      else {
        // Mass-weighted: lighter entity moves more.
        pushA = overlap * (mb / (ma + mb));
        pushB = overlap * (ma / (ma + mb));
      }
      a.position.x -= nx * pushA;
      a.position.y -= ny * pushA;
      a.position.z -= nz * pushA;
      b.position.x += nx * pushB;
      b.position.y += ny * pushB;
      b.position.z += nz * pushB;
      // Velocity exchange: only the components along the normal swap with
      // mass-weighted elastic-ish response (coefficient 0.5; lossy, prevents
      // perpetual bouncing). Skip if either is spawn-protected.
      if (aProtected || bProtected) continue;
      const va_n = a.velocity.x * nx + a.velocity.y * ny + a.velocity.z * nz;
      const vb_n = b.velocity.x * nx + b.velocity.y * ny + b.velocity.z * nz;
      const relVel = vb_n - va_n;
      if (relVel < 0) {
        // Already separating; let them continue.
        continue;
      }
      const e = 0.5; // restitution
      // v8.50: rename from `j` to `impulseJ` to avoid shadowing the for-loop
      // counter `j` at block scope (block-scoped const created TDZ for the
      // whole loop body).
      const impulseJ = -(1 + e) * relVel / (1 / ma + 1 / mb);
      const impulseA = impulseJ / ma;
      const impulseB = impulseJ / mb;
      a.velocity.x -= nx * impulseA;
      a.velocity.y -= ny * impulseA;
      a.velocity.z -= nz * impulseA;
      b.velocity.x += nx * impulseB;
      b.velocity.y += ny * impulseB;
      b.velocity.z += nz * impulseB;
    }
  }
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
      damageDealt: Math.round(p.damageDealt || 0),
      abilityCooldowns: p.abilityCooldowns.slice(),
      abilityActive: p.abilityActive.slice(),
      // v8.28: spinup + mode-switch state for HUD.
      spinupTimer: round3(p.spinupTimer),
      spunUp: p.spunUp,
      blasterMode: p.blasterMode,
      blasterSwitchTimer: round3(p.blasterSwitchTimer),
      // v8.29: stasis state for client visuals.
      inStasis: p.inStasis,
      stasisTimer: round3(p.stasisTimer),
      stasisDuration: p.stasisDuration,
      // v8.16: simplified TRACKER buffs surfaced for HUD/visual feedback.
      damageImmuneTimer: round3(p.damageImmuneTimer),
      coreActive: p.coreFireRateMult !== 1.0 || p.coreDamageMult !== 1.0,
      // v8.18: foundation fields for client visuals.
      doomed: p.doomed,
      spawnProtection: round3(p.spawnProtection),
      clipAmmo: p.clipAmmo,
      maxClip: p.maxClip,
      reloading: p.reloading,
      reloadTimer: round3(p.reloadTimer),
      // v8.42: NA17 ; deathTime so client can compute respawn countdown.
      deathTime: round3(p.deathTime),
      // v8.44: dash state for HUD pip rendering + visuals.
      dashCharges: p.dashCharges,
      maxDashes: p.maxDashes,
      dashActive: p.dashActive,
      dashCooldownTimer: round3(p.dashCooldownTimer),
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
  // v8.21: world effects.
  const worldEffects: any[] = [];
  for (const e of state.worldEffects.values()) {
    worldEffects.push({
      id: e.id,
      type: e.type,
      ownerType: e.ownerType,
      ownerId: e.ownerId,
      ownerTeam: e.ownerTeam,
      position: { x: round1(e.position.x), y: round1(e.position.y), z: round1(e.position.z) },
      data: e.data,
      hp: round1(e.hp),
      maxHp: e.maxHp,
      timer: round3(e.timer),
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
    worldEffects,
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
