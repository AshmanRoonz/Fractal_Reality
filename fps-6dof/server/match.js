/**
 * Match - Core game match and authoritative simulation
 * Manages player state, physics, combat, rounds, and game state broadcast.
 */

const { LSS, CHASSIS, LOADOUTS } = require('../shared/constants');
const MAPS = require('../shared/maps');
const BotManager = require('./botmanager');

class Match {
  constructor(options) {
    this.id = options.id;
    this.name = options.name;
    this.map = options.map;
    this.maxPlayers = options.maxPlayers;
    this.botFill = options.botFill;
    this.password = options.password;
    this.joinCode = options.joinCode;

    // State machine: 'lobby' -> 'loadout' -> 'warmup' -> 'playing' -> 'roundEnd' -> loop or 'matchEnd'
    this.state = 'lobby';
    this.stateTimer = 0;

    // Players: playerId -> { id, ws, team, loadout, state (entity), ready, connected }
    this.players = new Map();

    // Round and match tracking
    this.round = 0;
    this.teamAScore = 0;
    this.teamBScore = 0;

    // Game configuration
    this.mapData = MAPS.getMap(this.map);

    // Bot manager (if enabled)
    this.botManager = this.botFill ? new BotManager(this) : null;
  }

  /**
   * Add a player to the match
   * @param {string} playerId
   * @param {WebSocket} ws
   */
  addPlayer(playerId, ws) {
    if (this.players.size >= this.maxPlayers) {
      throw new Error('Match is full');
    }

    // Assign to team with fewer players
    let teamASize = 0, teamBSize = 0;
    for (const p of this.players.values()) {
      if (p.team === LSS.TEAM_A) teamASize++;
      else if (p.team === LSS.TEAM_B) teamBSize++;
    }

    const team = teamASize <= teamBSize ? LSS.TEAM_A : LSS.TEAM_B;

    // Initialize player entity
    const entity = this.createPlayerEntity(team);

    const player = {
      id: playerId,
      ws,
      team,
      loadout: null, // selected during loadout phase
      state: entity,
      ready: false,
      connected: true,
    };

    this.players.set(playerId, player);

    // Send welcome message with current state
    ws.send(JSON.stringify({
      type: 'match_join_ok',
      matchId: this.id,
      playerId,
      team,
      currentState: this.state,
      mapData: this.mapData,
      gameTime: this.stateTimer,
    }));

    // Notify all other players of the new player
    this.broadcastToAll({
      type: 'player_joined',
      playerId,
      team,
      playerCount: this.players.size,
    });

    console.log(`[Match ${this.id}] Player ${playerId} added to team ${team}. Total: ${this.players.size}/${this.maxPlayers}`);

    // Transition from lobby to loadout when first player joins
    if (this.state === 'lobby') {
      this.state = 'loadout';
      this.broadcastToAll({
        type: 'state_change',
        newState: 'loadout',
      });
    }
  }

  /**
   * Remove a player from the match
   * @param {string} playerId
   */
  removePlayer(playerId) {
    const player = this.players.get(playerId);
    if (!player) return;

    this.players.delete(playerId);
    player.connected = false;

    // Rebalance teams if needed
    if (this.state === 'playing' || this.state === 'roundEnd') {
      // Player was in an active round; they're now gone
    }

    // Notify others
    this.broadcastToAll({
      type: 'player_left',
      playerId,
      playerCount: this.players.size,
    });

    console.log(`[Match ${this.id}] Player ${playerId} removed. Remaining: ${this.players.size}`);

    // If all players left, match cleanup is handled by the server (via empty match detection)
  }

  /**
   * Handle player input
   * @param {string} playerId
   * @param {Object} input: { fwd, back, left, right, up, down, pitch, yaw, roll, fire, reload, ability1, ability2, ability3, core }
   */
  handleInput(playerId, input) {
    const player = this.players.get(playerId);
    if (!player || !player.state) return;

    // Rate limit: only process input during active rounds
    if (this.state !== 'playing' && this.state !== 'warmup') return;

    // Accept client format: movement: {x, y, z}, rotation: {pitch, yaw}
    // Convert to the fwd/back/left/right/up/down format used by physics
    const clamp1 = (v) => Math.max(-1, Math.min(1, v || 0));
    const mv = input.movement || {};
    const rot = input.rotation || {};

    // movement.z > 0 = forward, movement.x > 0 = right, movement.y > 0 = up
    const mz = clamp1(mv.z);
    const mx = clamp1(mv.x);
    const my = clamp1(mv.y);

    player.state.input = {
      fwd: mz > 0 ? mz : 0,
      back: mz < 0 ? -mz : 0,
      right: mx > 0 ? mx : 0,
      left: mx < 0 ? -mx : 0,
      up: my > 0 ? my : 0,
      down: my < 0 ? -my : 0,
      pitch: clamp1(rot.pitch),
      yaw: clamp1(rot.yaw),
      roll: 0,
      fire: Boolean(input.fire),
      reload: Boolean(input.reload),
      ability1: Boolean(input.ability === 'q'),
      ability2: Boolean(input.ability === 'e'),
      ability3: Boolean(input.ability === 'f'),
      core: Boolean(input.ability === 'core'),
      dash: Boolean(input.dash),
    };
  }

  /**
   * Handle loadout selection
   * @param {string} playerId
   * @param {string} loadoutKey
   */
  handleLoadoutSelect(playerId, loadoutKey) {
    const player = this.players.get(playerId);
    if (!player) return;

    if (!LOADOUTS[loadoutKey]) {
      player.ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid loadout',
      }));
      return;
    }

    player.loadout = loadoutKey;
    player.state = this.createPlayerEntity(player.team, loadoutKey);
    player.ready = false; // Reset ready status on loadout change

    // Notify all players
    this.broadcastToAll({
      type: 'loadout_selected',
      playerId,
      loadout: loadoutKey,
    });
  }

  /**
   * Mark player as ready
   * @param {string} playerId
   */
  handleReady(playerId) {
    const player = this.players.get(playerId);
    if (!player) return;

    if (!player.loadout) {
      player.ws.send(JSON.stringify({
        type: 'error',
        message: 'Select a loadout first',
      }));
      return;
    }

    player.ready = true;

    this.broadcastToAll({
      type: 'player_ready',
      playerId,
    });

    // Check if all players are ready
    this.checkAllReady();
  }

  /**
   * Check if all players are ready; if so, start the match
   */
  checkAllReady() {
    if (this.state !== 'loadout') return;

    // Need at least 1 player to start (allows solo testing; bots fill the rest)
    if (this.players.size < 1) return;

    for (const player of this.players.values()) {
      if (!player.ready) return;
    }

    // All ready; transition to warmup
    this.state = 'warmup';
    this.stateTimer = 0;
    console.log(`[Match ${this.id}] All players ready; starting warmup`);

    this.broadcastToAll({
      type: 'state_change',
      newState: 'warmup',
      duration: LSS.WARMUP_TIME,
    });
  }

  /**
   * Tick: update game state (called at TICK_RATE)
   * @param {number} dt: delta time in seconds
   */
  tick(dt) {
    this.stateTimer += dt;

    switch (this.state) {
      case 'lobby':
      case 'loadout':
        // No gameplay updates
        break;

      case 'warmup':
        this.tickWarmup(dt);
        break;

      case 'playing':
        this.tickPlaying(dt);
        break;

      case 'roundEnd':
        this.tickRoundEnd(dt);
        break;

      case 'matchEnd':
        // Match ended; do not process further
        break;
    }
  }

  /**
   * Warmup phase: wait for round to begin
   */
  tickWarmup(dt) {
    if (this.stateTimer >= LSS.WARMUP_TIME) {
      this.state = 'playing';
      this.stateTimer = 0;
      this.round++;

      // Reset player state for the round
      for (const player of this.players.values()) {
        player.state = this.createPlayerEntity(player.team, player.loadout);
        player.state.spawnProtection = LSS.SPAWN_PROTECTION;
      }

      console.log(`[Match ${this.id}] Round ${this.round} started`);

      this.broadcastToAll({
        type: 'state_change',
        newState: 'playing',
        round: this.round,
        duration: LSS.ROUND_TIME,
      });
    }
  }

  /**
   * Playing phase: process inputs, physics, combat, check end conditions
   */
  tickPlaying(dt) {
    // Process inputs and update physics for each player
    for (const player of this.players.values()) {
      this.updatePlayerPhysics(player, dt);
      this.updatePlayerCombat(player, dt);
      this.updatePlayerAbilities(player, dt);
    }

    // Tick bots if enabled
    if (this.botManager) {
      this.botManager.tickBots(dt);
    }

    // Check round end conditions
    // Only count teams that actually have players (don't end round if a team is just empty)
    const teamAPlayers = Array.from(this.players.values()).filter(p => p.team === LSS.TEAM_A);
    const teamBPlayers = Array.from(this.players.values()).filter(p => p.team === LSS.TEAM_B);
    const teamAAlive = teamAPlayers.filter(p => !p.state.dead).length;
    const teamBAlive = teamBPlayers.filter(p => !p.state.dead).length;

    const allTeamADead = teamAPlayers.length > 0 && teamAAlive === 0;
    const allTeamBDead = teamBPlayers.length > 0 && teamBAlive === 0;
    const roundTimeExpired = this.stateTimer >= LSS.ROUND_TIME;

    // Only end round by elimination if BOTH teams have players
    if (teamAPlayers.length > 0 && teamBPlayers.length > 0 && (allTeamADead || allTeamBDead)) {
      this.endRound(allTeamADead, allTeamBDead);
    } else if (roundTimeExpired) {
      this.endRound(false, false);
    }
  }

  /**
   * Update player physics
   */
  updatePlayerPhysics(player, dt) {
    const e = player.state;
    if (e.dead) return;

    const loadoutData = LOADOUTS[player.loadout] || LOADOUTS.ION;
    const chassis = CHASSIS[loadoutData.chassis];

    // Initialize input if not set
    if (!e.input) {
      e.input = {
        fwd: 0, back: 0, left: 0, right: 0, up: 0, down: 0,
        pitch: 0, yaw: 0, roll: 0,
        fire: false, reload: false,
        ability1: false, ability2: false, ability3: false, core: false,
      };
    }

    const input = e.input;

    // Compute movement direction (local to ship orientation)
    const moveX = (input.right - input.left) * chassis.strafeSpeed;
    const moveY = (input.up - input.down) * chassis.verticalSpeed;
    const moveZ = -(input.fwd - input.back) * chassis.flightSpeed;

    // Convert quaternion to rotation matrix (simplified: use for forward/up/right vectors)
    const q = e.quat;
    const forward = {
      x: 2 * (q.x * q.z + q.w * q.y),
      y: 2 * (q.y * q.z - q.w * q.x),
      z: 1 - 2 * (q.x * q.x + q.y * q.y),
    };

    const up = {
      x: 2 * (q.x * q.y - q.w * q.z),
      y: 1 - 2 * (q.x * q.x + q.z * q.z),
      z: 2 * (q.y * q.z + q.w * q.x),
    };

    const right = {
      x: 1 - 2 * (q.y * q.y + q.z * q.z),
      y: 2 * (q.x * q.y + q.w * q.z),
      z: 2 * (q.x * q.z - q.w * q.y),
    };

    // Compute world-space acceleration
    const acc = {
      x: right.x * moveX + up.x * moveY + forward.x * moveZ,
      y: right.y * moveX + up.y * moveY + forward.y * moveZ,
      z: right.z * moveX + up.z * moveY + forward.z * moveZ,
    };

    // Apply acceleration
    e.vel.x += acc.x * dt;
    e.vel.y += acc.y * dt;
    e.vel.z += acc.z * dt;

    // Apply drag (exponential)
    const dragCoeff = 0.97;
    const dragFactor = Math.pow(dragCoeff, dt);
    e.vel.x *= dragFactor;
    e.vel.y *= dragFactor;
    e.vel.z *= dragFactor;

    // Speed cap
    const speed = Math.sqrt(e.vel.x * e.vel.x + e.vel.y * e.vel.y + e.vel.z * e.vel.z);
    const maxSpeed = chassis.flightSpeed * 1.5;
    if (speed > maxSpeed) {
      const scale = maxSpeed / speed;
      e.vel.x *= scale;
      e.vel.y *= scale;
      e.vel.z *= scale;
    }

    // Integrate position
    e.pos.x += e.vel.x * dt;
    e.pos.y += e.vel.y * dt;
    e.pos.z += e.vel.z * dt;

    // Rotation input
    const pitchRate = (input.pitch) * chassis.pitchRate * (Math.PI / 180);
    const yawRate = (input.yaw) * chassis.turnRate * (Math.PI / 180);
    const rollRate = (input.roll) * chassis.turnRate * (Math.PI / 180);

    e.angVel.x = pitchRate;
    e.angVel.y = yawRate;
    e.angVel.z = rollRate;

    // Integrate quaternion from angular velocity
    const angSpeed = Math.sqrt(
      e.angVel.x * e.angVel.x + e.angVel.y * e.angVel.y + e.angVel.z * e.angVel.z
    );
    if (angSpeed > 0) {
      const halfAngle = angSpeed * dt * 0.5;
      const s = Math.sin(halfAngle) / angSpeed;
      const deltaQuat = {
        x: e.angVel.x * s,
        y: e.angVel.y * s,
        z: e.angVel.z * s,
        w: Math.cos(halfAngle),
      };

      // Multiply: e.quat = deltaQuat * e.quat
      const q1 = deltaQuat;
      const q2 = e.quat;
      e.quat = {
        x: q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y,
        y: q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x,
        z: q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w,
        w: q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z,
      };

      // Normalize quaternion
      const len = Math.sqrt(
        e.quat.x * e.quat.x + e.quat.y * e.quat.y +
        e.quat.z * e.quat.z + e.quat.w * e.quat.w
      );
      e.quat.x /= len;
      e.quat.y /= len;
      e.quat.z /= len;
      e.quat.w /= len;
    }

    // Update spawn protection
    if (e.spawnProtection > 0) {
      e.spawnProtection -= dt;
    }

    // Shield regen
    if (e.health > 0) {
      if (e.shieldRegenTimer > 0) {
        e.shieldRegenTimer -= dt;
      } else {
        const shieldGain = chassis.shieldRegenRate * dt;
        e.shield = Math.min(e.maxShield, e.shield + shieldGain);
      }
    }

    // Doomed timer
    if (e.isDoomed) {
      e.doomedTimer -= dt;
      if (e.doomedTimer <= 0) {
        e.dead = true;
        e.health = 0;
        console.log(`[Match ${this.id}] Player ${player.id} auto-killed (doomed timeout)`);
      }
    }

    // Respawn logic (Phase 1: no respawns during round; simplified)
  }

  /**
   * Update player combat (weapons, fire, damage)
   */
  updatePlayerCombat(player, dt) {
    const e = player.state;
    if (e.dead) return;

    const loadout = LOADOUTS[player.loadout] || LOADOUTS.ION;
    const weapon = loadout.weapon;

    // Update fire cooldown
    if (e.fireCooldown > 0) {
      e.fireCooldown -= dt;
    }

    // Process fire input
    if (e.input.fire && e.fireCooldown <= 0 && e.clipAmmo > 0 && !e.reloading) {
      e.clipAmmo--;
      e.fireCooldown = weapon.fireRate;

      // Spawn projectile or hitscan
      if (weapon.type === 'hitscan') {
        this.fireHitscan(player);
      } else if (weapon.type === 'projectile') {
        this.fireProjectile(player);
      } else if (weapon.type === 'spread') {
        this.fireSpread(player);
      }
    }

    // Process reload input
    if (e.input.reload && !e.reloading && e.clipAmmo < weapon.clipSize) {
      e.reloading = true;
      e.reloadTimer = 2.0; // 2 second reload
    }

    if (e.reloading) {
      e.reloadTimer -= dt;
      if (e.reloadTimer <= 0) {
        e.clipAmmo = weapon.clipSize;
        e.reloading = false;
      }
    }
  }

  /**
   * Fire hitscan weapon
   */
  fireHitscan(player) {
    const loadout = LOADOUTS[player.loadout] || LOADOUTS.ION;
    const weapon = loadout.weapon;
    const e = player.state;

    const forward = {
      x: 2 * (e.quat.x * e.quat.z + e.quat.w * e.quat.y),
      y: 2 * (e.quat.y * e.quat.z - e.quat.w * e.quat.x),
      z: 1 - 2 * (e.quat.x * e.quat.x + e.quat.y * e.quat.y),
    };

    // Raycast: check all other players
    let closestDist = Infinity;
    let target = null;

    for (const other of this.players.values()) {
      if (other.id === player.id || other.state.dead) continue;

      const dx = other.state.pos.x - e.pos.x;
      const dy = other.state.pos.y - e.pos.y;
      const dz = other.state.pos.z - e.pos.z;

      // Simple sphere distance check
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
      const collRadius = CHASSIS[(LOADOUTS[other.loadout] || LOADOUTS.ION).chassis].collRadius;

      if (dist < weapon.range && dist < closestDist) {
        // Check if target is roughly in front (dot product with forward)
        const dot = (dx * forward.x + dy * forward.y + dz * forward.z) / dist;
        if (dot > 0.3) {
          closestDist = dist;
          target = other;
        }
      }
    }

    if (target) {
      this.applyDamage(player, target, weapon.damage);
    }
  }

  /**
   * Fire projectile weapon
   */
  fireProjectile(player) {
    const loadout = LOADOUTS[player.loadout] || LOADOUTS.ION;
    const weapon = loadout.weapon;
    const e = player.state;

    const forward = {
      x: 2 * (e.quat.x * e.quat.z + e.quat.w * e.quat.y),
      y: 2 * (e.quat.y * e.quat.z - e.quat.w * e.quat.x),
      z: 1 - 2 * (e.quat.x * e.quat.x + e.quat.y * e.quat.y),
    };

    // Store projectile (simplified: just track damage and check collision each tick)
    if (!e.projectiles) e.projectiles = [];

    e.projectiles.push({
      pos: { ...e.pos },
      vel: {
        x: forward.x * weapon.projectileSpeed,
        y: forward.y * weapon.projectileSpeed,
        z: forward.z * weapon.projectileSpeed,
      },
      damage: weapon.damage,
      lifetime: weapon.range / weapon.projectileSpeed,
      owner: player.id,
    });
  }

  /**
   * Fire spread weapon (multiple pellets)
   */
  fireSpread(player) {
    const loadout = LOADOUTS[player.loadout] || LOADOUTS.ION;
    const weapon = loadout.weapon;
    const e = player.state;

    const forward = {
      x: 2 * (e.quat.x * e.quat.z + e.quat.w * e.quat.y),
      y: 2 * (e.quat.y * e.quat.z - e.quat.w * e.quat.x),
      z: 1 - 2 * (e.quat.x * e.quat.x + e.quat.y * e.quat.y),
    };

    if (!e.projectiles) e.projectiles = [];

    const pellets = weapon.pellets || 8;
    for (let i = 0; i < pellets; i++) {
      // Add random spread to pellet direction
      const spreadAngle = (Math.random() - 0.5) * 0.3; // ~17 degrees
      const perpX = Math.random() - 0.5;
      const perpY = Math.random() - 0.5;
      const perpZ = Math.random() - 0.5;

      e.projectiles.push({
        pos: { ...e.pos },
        vel: {
          x: forward.x * weapon.projectileSpeed + perpX * weapon.projectileSpeed * spreadAngle,
          y: forward.y * weapon.projectileSpeed + perpY * weapon.projectileSpeed * spreadAngle,
          z: forward.z * weapon.projectileSpeed + perpZ * weapon.projectileSpeed * spreadAngle,
        },
        damage: weapon.damage,
        lifetime: weapon.range / weapon.projectileSpeed,
        owner: player.id,
      });
    }
  }

  /**
   * Apply damage to a target (server-authoritative)
   */
  applyDamage(attacker, target, damage) {
    const e = target.state;

    if (e.spawnProtection > 0) return; // Spawn protection
    if (e.dead) return;

    // Reduce shield first
    if (e.shield > 0) {
      const shieldDmg = Math.min(e.shield, damage);
      e.shield -= shieldDmg;
      const remainingDmg = damage - shieldDmg;

      if (remainingDmg > 0) {
        e.health -= remainingDmg;
      }

      // Reset shield regen timer
      const chassis = CHASSIS[(LOADOUTS[target.loadout] || LOADOUTS.ION).chassis];
      e.shieldRegenTimer = chassis.shieldRegenDelay;
    } else {
      e.health -= damage;
    }

    // Check for doomed state
    const doomed = e.health / e.maxHealth < LSS.DOOMED_HEALTH_PCT;
    if (doomed && !e.isDoomed) {
      e.isDoomed = true;
      e.doomedTimer = LSS.DOOMED_TIMER;
      console.log(`[Match ${this.id}] Player ${target.id} is DOOMED`);
      this.broadcastToAll({
        type: 'doomed',
        playerId: target.id,
      });
    }

    // Check for death
    if (e.health <= 0) {
      e.dead = true;
      e.health = 0;
      console.log(`[Match ${this.id}] Player ${target.id} killed by ${attacker.id}`);

      // Award kill
      attacker.state.kills = (attacker.state.kills || 0) + 1;

      this.broadcastToAll({
        type: 'player_killed',
        victim: target.id,
        attacker: attacker.id,
      });
    }
  }

  /**
   * Update abilities (cooldowns, effects)
   */
  updatePlayerAbilities(player, dt) {
    const e = player.state;

    // Update ability cooldowns
    for (let i = 0; i < 3; i++) {
      if (e.abilityCooldowns[i] > 0) {
        e.abilityCooldowns[i] -= dt;
      }
    }

    // Core cooldown
    if (e.coreTimer > 0) {
      e.coreTimer -= dt;
    }
  }

  /**
   * Round end phase: brief pause then start next round
   */
  tickRoundEnd(dt) {
    // Wait 5 seconds between rounds
    if (this.stateTimer >= 5) {
      // Start next round
      this.state = 'warmup';
      this.stateTimer = 0;

      this.broadcastToAll({
        type: 'state_change',
        newState: 'warmup',
        duration: LSS.WARMUP_TIME,
      });
    }
  }

  /**
   * End round logic
   */
  endRound(allTeamADead, allTeamBDead) {
    this.state = 'roundEnd';
    this.stateTimer = 0;

    let winnerTeam = null;
    if (allTeamADead) {
      winnerTeam = LSS.TEAM_B;
      this.teamBScore++;
    } else if (allTeamBDead) {
      winnerTeam = LSS.TEAM_A;
      this.teamAScore++;
    } else {
      // Timeout: team with more alive wins (or draw)
      const teamAAlive = Array.from(this.players.values()).filter(
        (p) => p.team === LSS.TEAM_A && !p.state.dead
      ).length;
      const teamBAlive = Array.from(this.players.values()).filter(
        (p) => p.team === LSS.TEAM_B && !p.state.dead
      ).length;

      if (teamAAlive > teamBAlive) {
        winnerTeam = LSS.TEAM_A;
        this.teamAScore++;
      } else if (teamBAlive > teamAAlive) {
        winnerTeam = LSS.TEAM_B;
        this.teamBScore++;
      }
    }

    console.log(
      `[Match ${this.id}] Round ${this.round} ended. Score: A=${this.teamAScore} B=${this.teamBScore}`
    );

    this.broadcastToAll({
      type: 'round_end',
      winnerTeam,
      scoreA: this.teamAScore,
      scoreB: this.teamBScore,
    });

    // Check if match is over
    if (this.teamAScore >= LSS.ROUNDS_TO_WIN || this.teamBScore >= LSS.ROUNDS_TO_WIN) {
      this.endMatch();
    }
  }

  /**
   * End match logic
   */
  endMatch() {
    this.state = 'matchEnd';

    const winner = this.teamAScore > this.teamBScore ? LSS.TEAM_A : LSS.TEAM_B;

    console.log(`[Match ${this.id}] Match ended. Winner: Team ${winner}`);

    this.broadcastToAll({
      type: 'match_end',
      winner,
      finalScoreA: this.teamAScore,
      finalScoreB: this.teamBScore,
    });
  }

  /**
   * Create a player entity (initial state)
   */
  createPlayerEntity(team, loadoutKey = null) {
    const chassis = CHASSIS[LOADOUTS[loadoutKey || 'ION'].chassis];

    // Pick a spawn point based on team
    const spawnRoom = team === LSS.TEAM_A ? 'spawn_a' : 'spawn_b';
    const spawnPos = this.getSpawnPosition(spawnRoom);

    // Compute quaternion that faces from spawn toward map center (0,0,0)
    const spawnQuat = this.lookAtQuaternion(spawnPos, { x: 0, y: 0, z: 0 });

    return {
      pos: spawnPos,
      vel: { x: 0, y: 0, z: 0 },
      quat: spawnQuat,
      angVel: { x: 0, y: 0, z: 0 },
      health: chassis.maxHealth,
      maxHealth: chassis.maxHealth,
      shield: chassis.maxShield,
      maxShield: chassis.maxShield,
      shieldRegenTimer: 0,
      shieldRegenDelay: chassis.shieldRegenDelay,
      shieldRegenRate: chassis.shieldRegenRate,
      dead: false,
      doomedTimer: 0,
      isDoomed: false,
      fireCooldown: 0,
      clipAmmo: LOADOUTS[loadoutKey || 'ION'].weapon.clipSize,
      reloading: false,
      reloadTimer: 0,
      abilityCooldowns: [0, 0, 0],
      coreMeter: 0,
      coreActive: false,
      coreTimer: 0,
      dashCharges: chassis.maxDashes,
      dashCooldownTimer: 0,
      dashActive: false,
      dashTimer: 0,
      spawnProtection: 0,
      input: null,
      projectiles: [],
      kills: 0,
    };
  }

  /**
   * Get spawn position for a team
   */
  getSpawnPosition(roomId) {
    const room = this.mapData.rooms.find((r) => r.id === roomId);
    if (!room) {
      return { x: 0, y: 0, z: 0 };
    }

    // Add some randomness within the room
    const offset = 100;
    return {
      x: room.x + (Math.random() - 0.5) * offset,
      y: room.y + (Math.random() - 0.5) * offset,
      z: room.z + (Math.random() - 0.5) * offset,
    };
  }

  /**
   * Compute a quaternion that makes an entity at 'from' look toward 'to'.
   * Uses the convention that forward is -Z (matching Three.js camera default).
   */
  lookAtQuaternion(from, to) {
    // Direction vector from 'from' to 'to'
    let dx = to.x - from.x;
    let dy = to.y - from.y;
    let dz = to.z - from.z;
    const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (len < 0.001) return { x: 0, y: 0, z: 0, w: 1 };
    dx /= len; dy /= len; dz /= len;

    // We want to rotate from forward (-Z = 0,0,-1) to the direction (dx,dy,dz)
    // Using axis-angle: axis = cross(forward, dir), angle = acos(dot(forward, dir))
    const fwd = { x: 0, y: 0, z: -1 };
    const dot = fwd.x * dx + fwd.y * dy + fwd.z * dz;

    // If looking almost exactly forward, return identity
    if (dot > 0.9999) return { x: 0, y: 0, z: 0, w: 1 };
    // If looking almost exactly backward, rotate 180 around Y
    if (dot < -0.9999) return { x: 0, y: 1, z: 0, w: 0 };

    // Cross product: fwd x dir
    const cx = fwd.y * dz - fwd.z * dy;
    const cy = fwd.z * dx - fwd.x * dz;
    const cz = fwd.x * dy - fwd.y * dx;

    // Quaternion from half-angle formula: q = (cross, 1 + dot), then normalize
    const qx = cx;
    const qy = cy;
    const qz = cz;
    const qw = 1 + dot;
    const qlen = Math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw);
    return { x: qx / qlen, y: qy / qlen, z: qz / qlen, w: qw / qlen };
  }

  /**
   * Broadcast serialized game state to all connected players
   */
  broadcastState() {
    const state = {
      type: 'game_state',
      matchId: this.id,
      gameTime: this.stateTimer,
      matchState: this.state,
      scoreA: this.teamAScore,
      scoreB: this.teamBScore,
      round: this.round,
      players: {},
    };

    // Serialize each player's entity state
    for (const [playerId, player] of this.players) {
      state.players[playerId] = {
        id: playerId,
        team: player.team,
        loadout: player.loadout,
        connected: player.connected,
        entity: {
          pos: player.state.pos,
          quat: player.state.quat,
          vel: player.state.vel,
          health: player.state.health,
          shield: player.state.shield,
          dead: player.state.dead,
          isDoomed: player.state.isDoomed,
          clipAmmo: player.state.clipAmmo,
          reloading: player.state.reloading,
          kills: player.state.kills || 0,
        },
      };
    }

    this.broadcastToAll(state);
  }

  /**
   * Broadcast a message to all connected players in the match
   */
  broadcastToAll(msg) {
    const data = JSON.stringify(msg);
    for (const player of this.players.values()) {
      if (player.connected && player.ws.readyState === 1) { // WebSocket.OPEN
        player.ws.send(data);
      }
    }
  }

  /**
   * Broadcast a message to one team only
   */
  broadcastToTeam(team, msg) {
    const data = JSON.stringify(msg);
    for (const player of this.players.values()) {
      if (player.team === team && player.connected && player.ws.readyState === 1) {
        player.ws.send(data);
      }
    }
  }
}

module.exports = Match;
