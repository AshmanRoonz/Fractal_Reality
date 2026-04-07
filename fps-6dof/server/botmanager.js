/**
 * BotManager - AI bot backfill for multiplayer matches
 * Manages bot creation, removal, and AI decision-making.
 */

const { LOADOUTS } = require('../shared/constants');

class BotManager {
  constructor(match) {
    this.match = match;
    this.bots = new Map(); // botId -> player data
    this.botCounter = 0;
  }

  /**
   * Fill bots up to maxPlayers per team
   */
  fillBots() {
    const targetPerTeam = Math.floor(this.match.maxPlayers / 2);

    // Count current players per team
    let teamACount = 0, teamBCount = 0;
    for (const p of this.match.players.values()) {
      if (p.team === 'A') teamACount++;
      else teamBCount++;
    }

    // Fill team A
    while (teamACount < targetPerTeam) {
      this.createBot('A');
      teamACount++;
    }

    // Fill team B
    while (teamBCount < targetPerTeam) {
      this.createBot('B');
      teamBCount++;
    }
  }

  /**
   * Create a new bot player
   */
  createBot(team) {
    const botId = `bot_${++this.botCounter}`;
    const loadoutKey = this.randomLoadout();

    const player = {
      id: botId,
      ws: null, // bots have no websocket
      team,
      loadout: loadoutKey,
      state: this.match.createPlayerEntity(team, loadoutKey),
      ready: true, // bots are always ready
      connected: true,
      isBot: true,
    };

    this.match.players.set(botId, player);
    this.bots.set(botId, player);

    console.log(`[BotManager] Created bot ${botId} (${loadoutKey}) on team ${team}`);

    // Notify all players of the new bot
    this.match.broadcastToAll({
      type: 'player_joined',
      playerId: botId,
      team,
      playerCount: this.match.players.size,
    });
  }

  /**
   * Remove all bots from the match
   */
  removeBots() {
    const botIds = Array.from(this.bots.keys());
    for (const botId of botIds) {
      this.match.players.delete(botId);
      this.bots.delete(botId);

      this.match.broadcastToAll({
        type: 'player_left',
        playerId: botId,
        playerCount: this.match.players.size,
      });

      console.log(`[BotManager] Removed bot ${botId}`);
    }
  }

  /**
   * AI tick: generate input for all bots
   */
  tickBots(dt) {
    for (const bot of this.bots.values()) {
      this.generateBotInput(bot, dt);
    }
  }

  /**
   * Generate bot AI input
   * Phase 1 simplified: pick nearest enemy, turn toward them, fly toward them, fire
   */
  generateBotInput(bot, dt) {
    const e = bot.state;
    if (e.dead) return;

    // Initialize input
    if (!e.input) {
      e.input = {
        fwd: 0, back: 0, left: 0, right: 0, up: 0, down: 0,
        pitch: 0, yaw: 0, roll: 0,
        fire: false, reload: false,
        ability1: false, ability2: false, ability3: false, core: false,
      };
    }

    // Find nearest enemy
    let nearestEnemy = null;
    let nearestDist = Infinity;

    for (const other of this.match.players.values()) {
      if (other.team === bot.team || other.state.dead) continue;

      const dx = other.state.pos.x - e.pos.x;
      const dy = other.state.pos.y - e.pos.y;
      const dz = other.state.pos.z - e.pos.z;
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (dist < nearestDist) {
        nearestDist = dist;
        nearestEnemy = other;
      }
    }

    // Default: cruise forward and look around
    e.input.fwd = 0.5;
    e.input.pitch = 0;
    e.input.yaw = 0;
    e.input.fire = false;

    // If we see an enemy, pursue and attack
    if (nearestEnemy && nearestDist < 3000) {
      const targetPos = nearestEnemy.state.pos;

      // Calculate direction to target
      const dx = targetPos.x - e.pos.x;
      const dy = targetPos.y - e.pos.y;
      const dz = targetPos.z - e.pos.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

      // Forward vector (current orientation)
      const forward = {
        x: 2 * (e.quat.x * e.quat.z + e.quat.w * e.quat.y),
        y: 2 * (e.quat.y * e.quat.z - e.quat.w * e.quat.x),
        z: 1 - 2 * (e.quat.x * e.quat.x + e.quat.y * e.quat.y),
      };

      // Right vector
      const right = {
        x: 1 - 2 * (e.quat.y * e.quat.y + e.quat.z * e.quat.z),
        y: 2 * (e.quat.x * e.quat.y + e.quat.w * e.quat.z),
        z: 2 * (e.quat.x * e.quat.z - e.quat.w * e.quat.y),
      };

      // Up vector
      const up = {
        x: 2 * (e.quat.x * e.quat.y - e.quat.w * e.quat.z),
        y: 1 - 2 * (e.quat.x * e.quat.x + e.quat.z * e.quat.z),
        z: 2 * (e.quat.y * e.quat.z + e.quat.w * e.quat.x),
      };

      // Compute yaw and pitch to target
      const forwardDot = (dx * forward.x + dy * forward.y + dz * forward.z) / distance;
      const rightDot = (dx * right.x + dy * right.y + dz * right.z) / distance;
      const upDot = (dy * up.y) / distance;

      // Simple PID-like control
      const yawError = -rightDot * 0.1; // Negative because positive yaw is left
      const pitchError = upDot * 0.1;

      e.input.yaw = Math.max(-1, Math.min(1, yawError));
      e.input.pitch = Math.max(-1, Math.min(1, pitchError));

      // Move toward target
      e.input.fwd = Math.max(0.3, Math.min(1, (distance - 500) / 1000));

      // Fire if facing the target roughly
      if (forwardDot > 0.7) {
        e.input.fire = true;
      }

      // Reload if out of ammo
      if (e.clipAmmo === 0) {
        e.input.reload = true;
      }
    } else {
      // Random exploration when no enemy in sight
      if (Math.random() < 0.02) {
        e.input.yaw = (Math.random() - 0.5) * 0.5;
        e.input.pitch = (Math.random() - 0.5) * 0.5;
      }
    }
  }

  /**
   * Pick a random loadout
   */
  randomLoadout() {
    const keys = Object.keys(LOADOUTS);
    return keys[Math.floor(Math.random() * keys.length)];
  }
}

module.exports = BotManager;
