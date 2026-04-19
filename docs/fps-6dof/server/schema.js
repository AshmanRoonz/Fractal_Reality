// ============================================================================
// LAST SHIP SAILING ; Colyseus State Schema
// Defines the authoritative game state that auto-syncs to all clients
// ============================================================================

'use strict';

const { Schema, MapSchema, ArraySchema, type } = require('@colyseus/schema');

// --- Per-player state (synced to all clients) ---

class PlayerState extends Schema {}
type("string")(PlayerState.prototype, "sessionId");
type("string")(PlayerState.prototype, "name");
type("string")(PlayerState.prototype, "loadoutKey");   // ION, SCORCH, etc.
type("uint8")(PlayerState.prototype, "team");           // 2 = Fleet A, 3 = Fleet B

// Position
type("float32")(PlayerState.prototype, "px");
type("float32")(PlayerState.prototype, "py");
type("float32")(PlayerState.prototype, "pz");

// Velocity (for client-side interpolation and projectile inheritance)
type("float32")(PlayerState.prototype, "vx");
type("float32")(PlayerState.prototype, "vy");
type("float32")(PlayerState.prototype, "vz");

// Rotation (quaternion)
type("float32")(PlayerState.prototype, "qx");
type("float32")(PlayerState.prototype, "qy");
type("float32")(PlayerState.prototype, "qz");
type("float32")(PlayerState.prototype, "qw");

// Combat state
type("float32")(PlayerState.prototype, "health");
type("float32")(PlayerState.prototype, "maxHealth");
type("float32")(PlayerState.prototype, "shield");
type("float32")(PlayerState.prototype, "maxShield");
type("float32")(PlayerState.prototype, "coreMeter");
type("boolean")(PlayerState.prototype, "alive");
type("boolean")(PlayerState.prototype, "doomed");
type("float32")(PlayerState.prototype, "doomTimer");
type("float32")(PlayerState.prototype, "spawnProtection");

// Weapon state
type("uint8")(PlayerState.prototype, "clipAmmo");
type("boolean")(PlayerState.prototype, "reloading");
type("boolean")(PlayerState.prototype, "isFiring");

// Abilities (cooldowns synced so clients can show HUD)
type("float32")(PlayerState.prototype, "abilityCd0");
type("float32")(PlayerState.prototype, "abilityCd1");
type("float32")(PlayerState.prototype, "abilityCd2");
type("boolean")(PlayerState.prototype, "abilityActive0");
type("boolean")(PlayerState.prototype, "abilityActive1");
type("boolean")(PlayerState.prototype, "abilityActive2");
type("boolean")(PlayerState.prototype, "coreActive");
type("float32")(PlayerState.prototype, "coreTimer");

// Dash
type("uint8")(PlayerState.prototype, "dashCharges");
type("boolean")(PlayerState.prototype, "dashActive");

// Stats
type("uint16")(PlayerState.prototype, "kills");
type("uint16")(PlayerState.prototype, "deaths");
type("float32")(PlayerState.prototype, "damageDealt");


// --- Projectile state (synced for visual rendering on clients) ---

class ProjectileState extends Schema {}
type("string")(ProjectileState.prototype, "id");
type("string")(ProjectileState.prototype, "owner");     // sessionId of shooter
type("float32")(ProjectileState.prototype, "px");
type("float32")(ProjectileState.prototype, "py");
type("float32")(ProjectileState.prototype, "pz");
type("float32")(ProjectileState.prototype, "vx");
type("float32")(ProjectileState.prototype, "vy");
type("float32")(ProjectileState.prototype, "vz");
type("float32")(ProjectileState.prototype, "damage");
type("float32")(ProjectileState.prototype, "splash");
type("boolean")(ProjectileState.prototype, "tracking");
type("string")(ProjectileState.prototype, "trackTargetId");
type("string")(ProjectileState.prototype, "weaponType");  // for visual effects


// --- Bot state (same as player but server-controlled) ---

class BotState extends Schema {}
type("string")(BotState.prototype, "id");
type("string")(BotState.prototype, "loadoutKey");
type("uint8")(BotState.prototype, "team");

type("float32")(BotState.prototype, "px");
type("float32")(BotState.prototype, "py");
type("float32")(BotState.prototype, "pz");
type("float32")(BotState.prototype, "vx");
type("float32")(BotState.prototype, "vy");
type("float32")(BotState.prototype, "vz");
type("float32")(BotState.prototype, "qx");
type("float32")(BotState.prototype, "qy");
type("float32")(BotState.prototype, "qz");
type("float32")(BotState.prototype, "qw");

type("float32")(BotState.prototype, "health");
type("float32")(BotState.prototype, "maxHealth");
type("float32")(BotState.prototype, "shield");
type("float32")(BotState.prototype, "maxShield");
type("boolean")(BotState.prototype, "alive");
type("boolean")(BotState.prototype, "doomed");
type("float32")(BotState.prototype, "doomTimer");
type("boolean")(BotState.prototype, "isFiring");
type("float32")(BotState.prototype, "coreMeter");


// --- World effect state (firewalls, tethers, particle walls, etc.) ---

class WorldEffectState extends Schema {}
type("string")(WorldEffectState.prototype, "id");
type("string")(WorldEffectState.prototype, "type");     // firewall, particle_wall, trip_wire, etc.
type("string")(WorldEffectState.prototype, "owner");    // sessionId or bot id
type("float32")(WorldEffectState.prototype, "px");
type("float32")(WorldEffectState.prototype, "py");
type("float32")(WorldEffectState.prototype, "pz");
type("float32")(WorldEffectState.prototype, "dx");      // direction x
type("float32")(WorldEffectState.prototype, "dy");
type("float32")(WorldEffectState.prototype, "dz");
type("float32")(WorldEffectState.prototype, "hp");
type("float32")(WorldEffectState.prototype, "timer");


// --- Kill feed entry ---

class KillEntry extends Schema {}
type("string")(KillEntry.prototype, "killer");
type("string")(KillEntry.prototype, "victim");
type("string")(KillEntry.prototype, "weapon");
type("float32")(KillEntry.prototype, "time");


// --- Match state (the root schema) ---

class MatchState extends Schema {
  constructor() {
    super();
    this.players = new MapSchema();
    this.bots = new MapSchema();
    this.projectiles = new MapSchema();
    this.worldEffects = new MapSchema();
    this.killFeed = new ArraySchema();

    this.gameState = 'lobby';   // lobby, warmup, playing, roundEnd, matchEnd
    this.roundTimer = 0;
    this.warmupTimer = 0;
    this.scoreA = 0;
    this.scoreB = 0;
    this.currentRound = 1;
    this.serverTime = 0;
  }
}

type({ map: PlayerState })(MatchState.prototype, "players");
type({ map: BotState })(MatchState.prototype, "bots");
type({ map: ProjectileState })(MatchState.prototype, "projectiles");
type({ map: WorldEffectState })(MatchState.prototype, "worldEffects");
type({ array: KillEntry })(MatchState.prototype, "killFeed");

type("string")(MatchState.prototype, "gameState");
type("float32")(MatchState.prototype, "roundTimer");
type("float32")(MatchState.prototype, "warmupTimer");
type("uint8")(MatchState.prototype, "scoreA");
type("uint8")(MatchState.prototype, "scoreB");
type("uint8")(MatchState.prototype, "currentRound");
type("float32")(MatchState.prototype, "serverTime");


module.exports = {
  PlayerState,
  ProjectileState,
  BotState,
  WorldEffectState,
  KillEntry,
  MatchState,
};
