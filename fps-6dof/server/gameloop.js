/**
 * GameLoop - Main game loop running at TICK_RATE (60Hz)
 * Calls tick on all active matches, broadcasts state at NET_SEND_RATE (20Hz).
 */

const { LSS } = require('../shared/constants');

class GameLoop {
  constructor() {
    this.running = false;
    this.intervalId = null;
    this.lobby = null;
    this.lastTime = null;
    this.tickCount = 0;
  }

  /**
   * Start the game loop
   * @param {Lobby} lobby
   */
  start(lobby) {
    this.lobby = lobby;
    this.running = true;
    this.lastTime = Date.now();
    this.tickCount = 0;

    const tickInterval = 1000 / LSS.TICK_RATE; // ~16.67ms for 60Hz

    this.intervalId = setInterval(() => {
      this.tick();
    }, tickInterval);

    console.log(`[GameLoop] Started at ${LSS.TICK_RATE}Hz (${tickInterval.toFixed(2)}ms per tick)`);
  }

  /**
   * Stop the game loop
   */
  stop() {
    this.running = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    console.log('[GameLoop] Stopped');
  }

  /**
   * Main loop tick
   */
  tick() {
    const now = Date.now();
    const dt = (now - this.lastTime) / 1000; // convert to seconds
    this.lastTime = now;

    const startTime = performance.now();

    // Tick all active matches
    for (const match of this.lobby.matches.values()) {
      match.tick(dt);
    }

    // Broadcast state every NET_SEND_RATE (20Hz); i.e., every 3rd tick at 60Hz
    const broadcastInterval = Math.floor(LSS.TICK_RATE / LSS.NET_SEND_RATE);
    if ((this.tickCount % broadcastInterval) === 0) {
      for (const match of this.lobby.matches.values()) {
        match.broadcastState();
      }
    }

    this.tickCount++;

    // Performance monitoring
    const elapsed = performance.now() - startTime;
    if (elapsed > 16) {
      // Warn if tick takes longer than one frame at 60Hz
      console.warn(
        `[GameLoop] Slow tick: ${elapsed.toFixed(2)}ms (should be < 16.67ms)`
      );
    }
  }
}

module.exports = GameLoop;
