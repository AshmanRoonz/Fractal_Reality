// ============================================================================
// LAST SHIP SAILING ; Client Network Adapter (Colyseus)
// Drop-in replacement for the trystero P2P mesh layer.
// Include this via <script> before the main game code, or inline it.
//
// Exposes the same `net` interface the game already uses, plus
// Colyseus-specific connection logic.
// ============================================================================

'use strict';

// --- Colyseus Client ---
// Loaded from CDN in the HTML: <script src="https://unpkg.com/colyseus.js@0.15/dist/colyseus.js"></script>
// Provides global `Colyseus` object.

const colyseusNet = {
  client: null,
  room: null,
  sessionId: null,
  connected: false,

  // State listeners (called by game code)
  onPlayerAdd: null,    // (playerState, sessionId) => {}
  onPlayerRemove: null, // (sessionId) => {}
  onPlayerChange: null, // (playerState, sessionId) => {}
  onBotAdd: null,
  onBotRemove: null,
  onBotChange: null,
  onProjectileAdd: null,
  onProjectileRemove: null,
  onStateChange: null,  // (state) => {}

  // Message listeners
  onHit: null,          // (data) => {}
  onFire: null,         // (data) => {}
  onDeath: null,        // (data) => {}
  onImpact: null,       // (data) => {}
  onAbility: null,      // (data) => {}
  onCore: null,         // (data) => {}
  onRoundStart: null,
  onRoundEnd: null,
  onMatchEnd: null,
};

async function connectToServer(serverUrl, playerName) {
  try {
    colyseusNet.client = new Colyseus.Client(serverUrl);
    colyseusNet.room = await colyseusNet.client.joinOrCreate('match', { name: playerName });
    colyseusNet.sessionId = colyseusNet.room.sessionId;
    colyseusNet.connected = true;

    console.log('[LSS Net] Connected to server. Session:', colyseusNet.sessionId);

    const room = colyseusNet.room;

    // --- State change listeners ---

    // Players
    room.state.players.onAdd((player, sessionId) => {
      console.log('[LSS Net] Player added:', sessionId);
      if (colyseusNet.onPlayerAdd) colyseusNet.onPlayerAdd(player, sessionId);

      player.onChange(() => {
        if (colyseusNet.onPlayerChange) colyseusNet.onPlayerChange(player, sessionId);
      });
    });

    room.state.players.onRemove((player, sessionId) => {
      console.log('[LSS Net] Player removed:', sessionId);
      if (colyseusNet.onPlayerRemove) colyseusNet.onPlayerRemove(sessionId);
    });

    // Bots
    room.state.bots.onAdd((bot, id) => {
      if (colyseusNet.onBotAdd) colyseusNet.onBotAdd(bot, id);
      bot.onChange(() => {
        if (colyseusNet.onBotChange) colyseusNet.onBotChange(bot, id);
      });
    });

    room.state.bots.onRemove((bot, id) => {
      if (colyseusNet.onBotRemove) colyseusNet.onBotRemove(id);
    });

    // Projectiles
    room.state.projectiles.onAdd((proj, id) => {
      if (colyseusNet.onProjectileAdd) colyseusNet.onProjectileAdd(proj, id);
    });

    room.state.projectiles.onRemove((proj, id) => {
      if (colyseusNet.onProjectileRemove) colyseusNet.onProjectileRemove(id);
    });

    // General state change
    room.state.onChange(() => {
      if (colyseusNet.onStateChange) colyseusNet.onStateChange(room.state);
    });

    // --- Message listeners ---

    room.onMessage('hit', (data) => {
      if (colyseusNet.onHit) colyseusNet.onHit(data);
    });

    room.onMessage('fire', (data) => {
      if (colyseusNet.onFire) colyseusNet.onFire(data);
    });

    room.onMessage('death', (data) => {
      if (colyseusNet.onDeath) colyseusNet.onDeath(data);
    });

    room.onMessage('impact', (data) => {
      if (colyseusNet.onImpact) colyseusNet.onImpact(data);
    });

    room.onMessage('ability', (data) => {
      if (colyseusNet.onAbility) colyseusNet.onAbility(data);
    });

    room.onMessage('core', (data) => {
      if (colyseusNet.onCore) colyseusNet.onCore(data);
    });

    room.onMessage('round_start', (data) => {
      if (colyseusNet.onRoundStart) colyseusNet.onRoundStart(data);
    });

    room.onMessage('round_end', (data) => {
      if (colyseusNet.onRoundEnd) colyseusNet.onRoundEnd(data);
    });

    room.onMessage('match_end', (data) => {
      if (colyseusNet.onMatchEnd) colyseusNet.onMatchEnd(data);
    });

    // --- Room lifecycle ---

    room.onLeave((code) => {
      console.log('[LSS Net] Disconnected. Code:', code);
      colyseusNet.connected = false;
    });

    room.onError((code, message) => {
      console.error('[LSS Net] Error:', code, message);
    });

    return true;
  } catch (err) {
    console.error('[LSS Net] Connection failed:', err);
    return false;
  }
}

// --- Send functions (client -> server) ---

function sendInput(inputData) {
  if (!colyseusNet.room) return;
  colyseusNet.room.send('input', inputData);
}

function sendSelectLoadout(loadoutKey) {
  if (!colyseusNet.room) return;
  colyseusNet.room.send('select_loadout', { loadoutKey });
}

function sendDash() {
  if (!colyseusNet.room) return;
  colyseusNet.room.send('dash', {});
}

function sendAbility(index) {
  if (!colyseusNet.room) return;
  colyseusNet.room.send('ability', { index });
}

function sendCore() {
  if (!colyseusNet.room) return;
  colyseusNet.room.send('core', {});
}

// --- Input broadcast (called each frame from game loop) ---
// Sends the current input state to the server at a reduced rate

let inputSendAccum = 0;
const INPUT_SEND_HZ = 30; // send input 30 times per second

function broadcastInput(dt, inputState, cameraQuat) {
  inputSendAccum += dt;
  if (inputSendAccum < 1 / INPUT_SEND_HZ) return;
  inputSendAccum = 0;

  if (!colyseusNet.room) return;

  // Pack input compactly
  const data = {
    mx: inputState.moveX,   // -1 to 1
    my: inputState.moveY,   // -1 to 1
    mz: inputState.moveZ,   // -1 to 1
    fire: inputState.fire,
    alt: inputState.altFire,
    reload: inputState.reload,
    // Camera quaternion (server needs this for movement direction)
    qx: Math.round(cameraQuat.x * 1000) / 1000,
    qy: Math.round(cameraQuat.y * 1000) / 1000,
    qz: Math.round(cameraQuat.z * 1000) / 1000,
    qw: Math.round(cameraQuat.w * 1000) / 1000,
  };

  colyseusNet.room.send('input', data);
}
