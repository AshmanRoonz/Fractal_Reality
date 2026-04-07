/**
 * Lobby - Manages all active matches
 * Creates matches, stores them, lists them, and cleans up.
 */

const Match = require('./match');

class Lobby {
  constructor() {
    this.matches = new Map(); // matchId -> Match instance
  }

  /**
   * Create a new match with given options
   * @param {Object} options: { name, map, maxPlayers, botFill, password }
   * @returns {Object} match info with joinCode
   */
  createMatch(options) {
    const matchId = this.generateMatchId();
    const joinCode = this.generateJoinCode();

    const match = new Match({
      id: matchId,
      name: options.name,
      map: options.map,
      maxPlayers: options.maxPlayers,
      botFill: options.botFill,
      password: options.password,
      joinCode,
    });

    this.matches.set(matchId, match);

    console.log(`[Lobby] Created match ${matchId}: "${options.name}" (${options.map}, max ${options.maxPlayers})`);

    return {
      id: matchId,
      name: match.name,
      map: match.map,
      maxPlayers: match.maxPlayers,
      state: match.state,
      botFill: match.botFill,
      joinCode,
    };
  }

  /**
   * Get match instance by ID
   * @param {string} matchId
   * @returns {Match|null}
   */
  getMatch(matchId) {
    return this.matches.get(matchId) || null;
  }

  /**
   * List all public matches (not password-protected or recently played)
   * @returns {Array<Object>}
   */
  listMatches() {
    const list = [];
    for (const match of this.matches.values()) {
      if (!match.password) { // only public matches
        list.push({
          id: match.id,
          name: match.name,
          map: match.map,
          players: match.players.size,
          maxPlayers: match.maxPlayers,
          state: match.state,
          botFill: match.botFill,
        });
      }
    }
    return list;
  }

  /**
   * Remove match from lobby (cleanup)
   * @param {string} matchId
   */
  removeMatch(matchId) {
    this.matches.delete(matchId);
    console.log(`[Lobby] Removed match ${matchId}`);
  }

  /**
   * Generate a unique match ID
   * @returns {string}
   */
  generateMatchId() {
    return `match_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
  }

  /**
   * Generate a shareable 6-char alphanumeric join code
   * @returns {string}
   */
  generateJoinCode() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  }
}

module.exports = Lobby;
