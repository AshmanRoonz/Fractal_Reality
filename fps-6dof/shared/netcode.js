/**
 * LSS (Last Ship Sailing) - Networking Code
 * Shared between Node.js server and browser client.
 * Message type definitions and serialization helpers for bandwidth optimization.
 */

// Message Types: string constants for all protocol messages

const MSG_TYPE = {
  // Client to Server
  CLIENT_JOIN: 'CLIENT_JOIN',
  CLIENT_LEAVE: 'CLIENT_LEAVE',
  CLIENT_INPUT: 'CLIENT_INPUT',
  CLIENT_LOADOUT_SELECT: 'CLIENT_LOADOUT_SELECT',
  CLIENT_READY: 'CLIENT_READY',

  // Server to Client
  SERVER_WELCOME: 'SERVER_WELCOME',
  SERVER_LOBBY_STATE: 'SERVER_LOBBY_STATE',
  SERVER_MATCH_START: 'SERVER_MATCH_START',
  SERVER_GAME_STATE: 'SERVER_GAME_STATE',
  SERVER_PLAYER_JOINED: 'SERVER_PLAYER_JOINED',
  SERVER_PLAYER_LEFT: 'SERVER_PLAYER_LEFT',
  SERVER_ROUND_START: 'SERVER_ROUND_START',
  SERVER_ROUND_END: 'SERVER_ROUND_END',
  SERVER_MATCH_END: 'SERVER_MATCH_END',
  SERVER_KILL_EVENT: 'SERVER_KILL_EVENT',
  SERVER_DAMAGE_EVENT: 'SERVER_DAMAGE_EVENT',
  SERVER_ABILITY_EVENT: 'SERVER_ABILITY_EVENT',
  SERVER_CHAT: 'SERVER_CHAT',
};

// Input Schema
// Represents player input for a single network tick
const INPUT_SCHEMA = {
  type: 'string',                 // MSG_TYPE.CLIENT_INPUT
  tick: 'number',                 // Game tick number
  movement: { x: 'number', y: 'number', z: 'number' },  // [-1, 1] each
  rotation: { pitch: 'number', yaw: 'number' },         // radians
  fire: 'boolean',                // Weapon fire
  ability: 'number|null',         // Ability index (0-2) or null
  dash: 'boolean',                // Dash command
};

// GameState Schema
// Complete snapshot of game state for client
const GAMESTATE_SCHEMA = {
  type: 'string',                 // MSG_TYPE.SERVER_GAME_STATE
  tick: 'number',
  timestamp: 'number',            // Seconds since round start
  players: [
    {
      id: 'string',
      pos: { x: 'number', y: 'number', z: 'number' },
      quat: { x: 'number', y: 'number', z: 'number', w: 'number' },
      vel: { x: 'number', y: 'number', z: 'number' },
      health: 'number',
      shield: 'number',
      team: 'string',              // 'A' or 'B'
      loadout: 'string',           // Loadout name (ION, SCORCH, etc.)
      dead: 'boolean',
      dashActive: 'boolean',
      coreActive: 'boolean',
      abilityStates: [             // 3 abilities
        {
          cooldownRemaining: 'number',
          duration: 'number',       // Currently active duration
          active: 'boolean',
        },
      ],
    },
  ],
  projectiles: [
    {
      id: 'string',
      pos: { x: 'number', y: 'number', z: 'number' },
      vel: { x: 'number', y: 'number', z: 'number' },
      type: 'string',              // Weapon type or effect
      owner: 'string',             // Owner player ID
    },
  ],
  effects: [
    {
      type: 'string',              // Effect name
      pos: { x: 'number', y: 'number', z: 'number' },
      data: 'object',              // Effect-specific data
    },
  ],
};

/**
 * packInput(input): serializes input to compact array format
 * Reduces bandwidth by using typed arrays instead of JSON
 *
 * Output format (20 values):
 * [0] tick (uint32)
 * [1] movement.x (float16 ~ int16 * 100)
 * [2] movement.y
 * [3] movement.z
 * [4] rotation.pitch (float16)
 * [5] rotation.yaw (float16)
 * [6] fire (uint8: 0|1)
 * [7] ability (int8: -1 = null, 0-2 = ability index)
 * [8] dash (uint8: 0|1)
 */
function packInput(input) {
  return [
    input.tick,
    Math.round(input.movement.x * 100),
    Math.round(input.movement.y * 100),
    Math.round(input.movement.z * 100),
    input.rotation.pitch,
    input.rotation.yaw,
    input.fire ? 1 : 0,
    input.ability !== null ? input.ability : -1,
    input.dash ? 1 : 0,
  ];
}

/**
 * unpackInput(data): deserializes input from packed array
 */
function unpackInput(data) {
  return {
    type: MSG_TYPE.CLIENT_INPUT,
    tick: data[0],
    movement: {
      x: data[1] / 100,
      y: data[2] / 100,
      z: data[3] / 100,
    },
    rotation: {
      pitch: data[4],
      yaw: data[5],
    },
    fire: data[6] === 1,
    ability: data[7] === -1 ? null : data[7],
    dash: data[8] === 1,
  };
}

/**
 * packVector(v): packs position { x, y, z } into 3 int16s
 * Scale: multiply by 10 for 0.1 unit precision (range: ±3276.7 units)
 */
function packVector(v) {
  return [
    Math.round(v.x * 10),
    Math.round(v.y * 10),
    Math.round(v.z * 10),
  ];
}

/**
 * unpackVector(data): unpacks 3-element int16 array back to vector
 */
function unpackVector(data) {
  return {
    x: data[0] / 10,
    y: data[1] / 10,
    z: data[2] / 10,
  };
}

/**
 * packQuaternion(q): packs { x, y, z, w } into 4 int16s
 * Scale: multiply by 10000 (range: ±3.276)
 */
function packQuaternion(q) {
  return [
    Math.round(q.x * 10000),
    Math.round(q.y * 10000),
    Math.round(q.z * 10000),
    Math.round(q.w * 10000),
  ];
}

/**
 * unpackQuaternion(data): unpacks 4-element int16 array back to quaternion
 */
function unpackQuaternion(data) {
  return {
    x: data[0] / 10000,
    y: data[1] / 10000,
    z: data[2] / 10000,
    w: data[3] / 10000,
  };
}

/**
 * packGameState(state): serializes game state to compact format
 * Players and projectiles use packed vectors and quaternions.
 * This is a reference implementation; production code may compress further.
 */
function packGameState(state) {
  const packedPlayers = state.players.map(player => ({
    id: player.id,
    pos: packVector(player.pos),
    quat: packQuaternion(player.quat),
    vel: packVector(player.vel),
    health: Math.round(player.health),
    shield: Math.round(player.shield),
    team: player.team,
    loadout: player.loadout,
    dead: player.dead ? 1 : 0,
    dashActive: player.dashActive ? 1 : 0,
    coreActive: player.coreActive ? 1 : 0,
    abilityStates: player.abilityStates.map(ability => ({
      cooldownRemaining: Math.round(ability.cooldownRemaining * 10),
      duration: Math.round(ability.duration * 10),
      active: ability.active ? 1 : 0,
    })),
  }));

  const packedProjectiles = state.projectiles.map(proj => ({
    id: proj.id,
    pos: packVector(proj.pos),
    vel: packVector(proj.vel),
    type: proj.type,
    owner: proj.owner,
  }));

  return {
    type: state.type,
    tick: state.tick,
    timestamp: state.timestamp,
    players: packedPlayers,
    projectiles: packedProjectiles,
    effects: state.effects,
  };
}

/**
 * unpackGameState(packed): deserializes game state from packed format
 */
function unpackGameState(packed) {
  const players = packed.players.map(player => ({
    id: player.id,
    pos: unpackVector(player.pos),
    quat: unpackQuaternion(player.quat),
    vel: unpackVector(player.vel),
    health: player.health,
    shield: player.shield,
    team: player.team,
    loadout: player.loadout,
    dead: player.dead === 1,
    dashActive: player.dashActive === 1,
    coreActive: player.coreActive === 1,
    abilityStates: player.abilityStates.map(ability => ({
      cooldownRemaining: ability.cooldownRemaining / 10,
      duration: ability.duration / 10,
      active: ability.active === 1,
    })),
  }));

  const projectiles = packed.projectiles.map(proj => ({
    id: proj.id,
    pos: unpackVector(proj.pos),
    vel: unpackVector(proj.vel),
    type: proj.type,
    owner: proj.owner,
  }));

  return {
    type: packed.type,
    tick: packed.tick,
    timestamp: packed.timestamp,
    players,
    projectiles,
    effects: packed.effects,
  };
}

/**
 * validateInput(input): returns true if input object is valid
 * Used by server to reject malformed client packets
 */
function validateInput(input) {
  if (!input || typeof input !== 'object') return false;
  if (typeof input.tick !== 'number') return false;
  if (!input.movement || typeof input.movement.x !== 'number') return false;
  if (!input.rotation || typeof input.rotation.pitch !== 'number') return false;
  if (typeof input.fire !== 'boolean') return false;
  if (input.ability !== null && (typeof input.ability !== 'number' || input.ability < 0 || input.ability > 2)) return false;
  if (typeof input.dash !== 'boolean') return false;

  // Clamp movement to [-1, 1] range
  if (Math.abs(input.movement.x) > 1 || Math.abs(input.movement.y) > 1 || Math.abs(input.movement.z) > 1) {
    return false;
  }

  return true;
}

/**
 * validateGameState(state): returns true if game state is valid
 */
function validateGameState(state) {
  if (!state || typeof state !== 'object') return false;
  if (state.type !== MSG_TYPE.SERVER_GAME_STATE) return false;
  if (typeof state.tick !== 'number') return false;
  if (typeof state.timestamp !== 'number') return false;
  if (!Array.isArray(state.players)) return false;
  if (!Array.isArray(state.projectiles)) return false;
  if (!Array.isArray(state.effects)) return false;

  // Validate each player
  for (const player of state.players) {
    if (typeof player.id !== 'string') return false;
    if (typeof player.health !== 'number' || player.health < 0) return false;
    if (typeof player.shield !== 'number' || player.shield < 0) return false;
    if (!['A', 'B'].includes(player.team)) return false;
  }

  return true;
}

// Dual-environment export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    MSG_TYPE,
    INPUT_SCHEMA,
    GAMESTATE_SCHEMA,
    packInput,
    unpackInput,
    packVector,
    unpackVector,
    packQuaternion,
    unpackQuaternion,
    packGameState,
    unpackGameState,
    validateInput,
    validateGameState,
  };
} else {
  window.LSS_SHARED = window.LSS_SHARED || {};
  Object.assign(window.LSS_SHARED, {
    MSG_TYPE,
    INPUT_SCHEMA,
    GAMESTATE_SCHEMA,
    packInput,
    unpackInput,
    packVector,
    unpackVector,
    packQuaternion,
    unpackQuaternion,
    packGameState,
    unpackGameState,
    validateInput,
    validateGameState,
  });
}
