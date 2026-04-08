// ============================================================================
// LAST SHIP SAILING ; Authoritative Game Server Room
// Colyseus Room that owns all game state and runs the simulation tick
// ============================================================================

'use strict';

const { Room } = require('colyseus');
const {
  MatchState, PlayerState, BotState, ProjectileState,
  WorldEffectState, KillEntry,
} = require('./schema');
const { LSS, CHASSIS, LOADOUTS, Vec3, Quat, getForward, getRight } = require('./shared');
const {
  worldSDF, sdfNormal, sdfRaycast,
  resolveCollision, resolveShipShipCollisions,
  buildLevelData, getValidSpawnPoint,
} = require('./collision');

// ------------------------------------------------------------------
// Internal (non-synced) state for simulation
// ------------------------------------------------------------------

class ServerPlayer {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.loadoutKey = null;
    this.loadout = null;
    this.chassis = null;
    this.team = 0;
    this.pos = new Vec3();
    this.vel = new Vec3();
    this.quat = new Quat();
    this.health = 0;
    this.maxHealth = 0;
    this.shield = 0;
    this.maxShield = 0;
    this.alive = false;
    this.doomed = false;
    this.doomTimer = 0;
    this.spawnProtection = 0;
    this.coreMeter = 0;
    this.coreActive = false;
    this.coreTimer = 0;

    // Weapon
    this.clipAmmo = 0;
    this.maxClip = 0;
    this.fireTimer = 0;
    this.reloading = false;
    this.reloadTimer = 0;
    this.spinupTimer = 0;
    this.spunUp = false;
    this.isFiring = false;

    // Abilities
    this.abilityCooldowns = [0, 0, 0];
    this.abilityActive = [false, false, false];
    this.abilityTimers = [0, 0, 0];

    // Dash
    this.dashCharges = 0;
    this.dashCooldownTimer = 0;
    this.dashActive = false;
    this.dashTimer = 0;

    // Stats
    this.kills = 0;
    this.deaths = 0;
    this.damageDealt = 0;

    // Input buffer (latest from client)
    this.input = {
      moveX: 0, moveY: 0, moveZ: 0, // -1 to 1 normalized
      lookPitch: 0, lookYaw: 0,       // euler angles from client
      fire: false,
      altFire: false,
      dash: false,
      reload: false,
      ability: [false, false, false],
      core: false,
      qx: 0, qy: 0, qz: 0, qw: 1,   // client camera quaternion
    };

    // Loadout-specific state
    this.ionEnergy = 0;
    this.ionMaxEnergy = 1000;
    this.ionAdsActive = false;
    this.railgunCharge = 0;
    this.vortexStored = 0;
    this.afterburnerActive = false;
    this.afterburnerSpeedMult = 1.0;
    this.gunShieldHP = 0;
    this.gunShieldTimer = 0;
    this.thermalShieldHP = 0;
    this.legionMode = 'close';
    this.legionSwitchTimer = 0;
    this.monarchDmgMult = 1;
    this.monarchArcRounds = false;
    this.monarchUpgradeTier = 0;
    this.phaseInvuln = false;
    this.phaseInvulnTimer = 0;

    // TONE lock tracking
    this.toneLocks = {}; // targetId -> lock count
  }
}

class ServerBot {
  constructor(id, loadoutKey, team) {
    this.id = id;
    this.loadoutKey = loadoutKey;
    this.loadout = LOADOUTS[loadoutKey];
    this.chassis = CHASSIS[this.loadout.chassis];
    this.team = team;
    this.pos = new Vec3(
      (Math.random() - 0.5) * 3000,
      (Math.random() - 0.5) * 1000,
      (Math.random() - 0.5) * 3000
    );
    this.vel = new Vec3();
    this.targetDir = new Vec3(0, 0, -1);
    this.health = this.chassis.maxHealth;
    this.maxHealth = this.chassis.maxHealth;
    this.shield = this.chassis.maxShield;
    this.maxShield = this.chassis.maxShield;
    this.alive = true;
    this.doomed = false;
    this.doomTimer = 0;
    this.spawnProtection = LSS.SPAWN_PROTECTION;
    this.coreMeter = 0;
    this.isFiring = false;
    this.fireTimer = 0;

    // AI state
    this.aiTarget = null;
    this.aiTimer = 0;
    this.aiWanderDir = new Vec3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();
    this.aiRole = Math.random() < 0.33 ? 'flank' : 'engage';
    this.aiRangePreference = this.getLoadoutRangePreference();
    this.aiRetreating = false;
    this.aiStrafe = false;
    this.aiStrafeTimer = 0;
    this.aiStrafeDir = Math.random() < 0.5 ? 1 : -1;
    this.arcSlowTimer = 0;
  }

  getLoadoutRangePreference() {
    switch (this.loadoutKey) {
      case 'SCORCH': return 500;
      case 'RONIN': return 500;
      case 'NORTHSTAR': return 1500;
      case 'TONE': return 1200;
      case 'LEGION': return 1000;
      case 'MONARCH': return 800;
      case 'ION': return 1000;
      default: return 800;
    }
  }
}

class ServerProjectile {
  constructor(id, origin, velocity, damage, splash, ownerId, weaponType) {
    this.id = id;
    this.pos = origin.clone();
    this.vel = velocity.clone();
    this.damage = damage;
    this.splash = splash;
    this.ownerId = ownerId;
    this.weaponType = weaponType || '';
    this.alive = true;
    this.lifetime = 5;
    this.age = 0;
    this.tracking = false;
    this.trackTargetId = null;
    this.isFireSource = false;
    this.isArcWave = false;
  }
}

// ------------------------------------------------------------------
// MatchRoom
// ------------------------------------------------------------------

class MatchRoom extends Room {

  onCreate(options) {
    this.setState(new MatchState());

    // Internal simulation state (not synced directly; pushed to schema each tick)
    this.serverPlayers = new Map();  // sessionId -> ServerPlayer
    this.serverBots = new Map();     // id -> ServerBot
    this.serverProjectiles = new Map(); // id -> ServerProjectile
    this.projIdCounter = 0;
    this.botIdCounter = 0;
    this.gameTime = 0;

    // Level geometry and collision
    this.levelData = buildLevelData('circumpunct');

    // Max clients
    this.maxClients = LSS.MAX_PLAYERS;

    // Set simulation interval (server tick) and state patch rate
    this.setSimulationInterval((dt) => this.serverTick(dt), 1000 / LSS.TICK_RATE);
    this.setPatchRate(1000 / LSS.TICK_RATE); // sync state patches at same rate as tick

    // ---- Message handlers ----

    // Client selects a loadout
    this.onMessage('select_loadout', (client, data) => {
      const sp = this.serverPlayers.get(client.sessionId);
      if (!sp) return;
      const loadoutKey = data.loadoutKey;
      if (!LOADOUTS[loadoutKey]) return;

      sp.loadoutKey = loadoutKey;
      sp.loadout = LOADOUTS[loadoutKey];
      sp.chassis = CHASSIS[sp.loadout.chassis];

      // Assign team (balance teams)
      const countA = [...this.serverPlayers.values()].filter(p => p.team === LSS.TEAM_FLEET_A).length;
      const countB = [...this.serverPlayers.values()].filter(p => p.team === LSS.TEAM_FLEET_B).length;
      sp.team = countA <= countB ? LSS.TEAM_FLEET_A : LSS.TEAM_FLEET_B;

      this.respawnPlayer(sp);
      this.syncPlayerToSchema(sp);

      // If enough players have selected, transition to warmup
      const readyCount = [...this.serverPlayers.values()].filter(p => p.loadoutKey).length;
      if (readyCount >= 1 && this.state.gameState === 'lobby') {
        this.startWarmup();
      }
    });

    // Client sends input each frame (or at reduced rate)
    this.onMessage('input', (client, data) => {
      const sp = this.serverPlayers.get(client.sessionId);
      if (!sp) return;
      // Overwrite input buffer
      sp.input.moveX = data.mx || 0;
      sp.input.moveY = data.my || 0;
      sp.input.moveZ = data.mz || 0;
      sp.input.fire = !!data.fire;
      sp.input.altFire = !!data.alt;
      sp.input.dash = !!data.dash;
      sp.input.reload = !!data.reload;
      sp.input.ability = [!!data.a0, !!data.a1, !!data.a2];
      sp.input.core = !!data.core;
      // Camera quaternion (client sends their look direction)
      if (data.qx !== undefined) {
        sp.input.qx = data.qx;
        sp.input.qy = data.qy;
        sp.input.qz = data.qz;
        sp.input.qw = data.qw;
      }
    });

    // Client requests dash (edge-triggered on client, sent once)
    this.onMessage('dash', (client) => {
      const sp = this.serverPlayers.get(client.sessionId);
      if (sp) this.performDash(sp);
    });

    // Client activates ability (edge-triggered)
    this.onMessage('ability', (client, data) => {
      const sp = this.serverPlayers.get(client.sessionId);
      if (sp) this.activateAbility(sp, data.index);
    });

    // Client activates core
    this.onMessage('core', (client) => {
      const sp = this.serverPlayers.get(client.sessionId);
      if (sp) this.activateCore(sp);
    });

    console.log('[MatchRoom] Created. Waiting for players...');
  }

  onJoin(client, options) {
    console.log(`[MatchRoom] ${client.sessionId} joined.`);

    const sp = new ServerPlayer(client.sessionId);
    this.serverPlayers.set(client.sessionId, sp);

    // Create synced schema
    const ps = new PlayerState();
    ps.sessionId = client.sessionId;
    ps.name = options.name || 'Player';
    ps.alive = false;
    ps.health = 0;
    ps.maxHealth = 0;
    ps.shield = 0;
    ps.maxShield = 0;
    ps.qw = 1;
    this.state.players.set(client.sessionId, ps);
  }

  onLeave(client, consented) {
    console.log(`[MatchRoom] ${client.sessionId} left.`);
    this.serverPlayers.delete(client.sessionId);
    this.state.players.delete(client.sessionId);
  }

  onDispose() {
    console.log('[MatchRoom] Disposed.');
  }

  // ------------------------------------------------------------------
  // GAME FLOW
  // ------------------------------------------------------------------

  startWarmup() {
    this.state.gameState = 'warmup';
    this.state.warmupTimer = LSS.WARMUP_TIME;
    this.spawnBots();
  }

  startRound() {
    this.state.gameState = 'playing';
    this.state.roundTimer = LSS.ROUND_TIME;
    this.broadcast('round_start', {});
  }

  endRound(winnerTeam) {
    if (winnerTeam === LSS.TEAM_FLEET_A) this.state.scoreA++;
    else this.state.scoreB++;
    this.state.gameState = 'roundEnd';
    this.roundEndTimer = 5;
    this.broadcast('round_end', { winner: winnerTeam, scoreA: this.state.scoreA, scoreB: this.state.scoreB });
  }

  nextRound() {
    if (this.state.scoreA >= LSS.ROUNDS_TO_WIN || this.state.scoreB >= LSS.ROUNDS_TO_WIN) {
      this.state.gameState = 'matchEnd';
      this.broadcast('match_end', { winner: this.state.scoreA >= LSS.ROUNDS_TO_WIN ? 'A' : 'B' });
      return;
    }
    this.state.currentRound++;

    // Optional: rotate to different map every 2 rounds
    const mapKeys = ['circumpunct', 'hourglass'];
    const mapIndex = (this.state.currentRound - 1) % mapKeys.length;
    this.levelData = buildLevelData(mapKeys[mapIndex]);

    // Respawn everyone
    for (const sp of this.serverPlayers.values()) {
      if (sp.loadoutKey) this.respawnPlayer(sp);
    }

    // Respawn bots
    this.clearBots();
    this.spawnBots();

    // Clear projectiles
    this.serverProjectiles.clear();
    this.state.projectiles.clear();

    // Clear world effects
    this.state.worldEffects.clear();

    this.state.gameState = 'warmup';
    this.state.warmupTimer = LSS.WARMUP_TIME;
  }

  // ------------------------------------------------------------------
  // SPAWN
  // ------------------------------------------------------------------

  respawnPlayer(sp) {
    const ch = sp.chassis;
    sp.health = ch.maxHealth;
    sp.maxHealth = ch.maxHealth;
    sp.shield = ch.maxShield;
    sp.maxShield = ch.maxShield;
    sp.alive = true;
    sp.doomed = false;
    sp.doomTimer = 0;
    sp.spawnProtection = LSS.SPAWN_PROTECTION;
    sp.coreMeter = 0;
    sp.coreActive = false;
    sp.coreTimer = 0;
    sp.clipAmmo = sp.loadout.weapon.clipSize;
    sp.maxClip = sp.loadout.weapon.clipSize;
    sp.fireTimer = 0;
    sp.reloading = false;
    sp.reloadTimer = 0;
    sp.spinupTimer = 0;
    sp.spunUp = false;
    sp.isFiring = false;
    sp.abilityCooldowns = [0, 0, 0];
    sp.abilityActive = [false, false, false];
    sp.abilityTimers = [0, 0, 0];
    sp.dashCharges = ch.maxDashes;
    sp.dashCooldownTimer = 0;
    sp.dashActive = false;
    sp.dashTimer = 0;
    sp.vel.set(0, 0, 0);
    sp.ionEnergy = sp.ionMaxEnergy;

    // Spawn position using team-aware spawn function
    const teamTag = sp.team === LSS.TEAM_FLEET_A ? 'A' : 'B';
    const spawnPos = getValidSpawnPoint(this.levelData, teamTag);
    sp.pos.copy(spawnPos);
  }

  spawnBots() {
    // Spawn 3 bots per team (adjustable)
    const botsPerTeam = 3;
    const loadoutKeys = Object.keys(LOADOUTS);

    for (let t = 0; t < 2; t++) {
      const team = t === 0 ? LSS.TEAM_FLEET_A : LSS.TEAM_FLEET_B;
      const teamTag = team === LSS.TEAM_FLEET_A ? 'A' : 'B';
      for (let i = 0; i < botsPerTeam; i++) {
        const id = 'bot_' + (this.botIdCounter++);
        const loadoutKey = loadoutKeys[Math.floor(Math.random() * loadoutKeys.length)];
        const bot = new ServerBot(id, loadoutKey, team);

        // Position bots using team-aware spawn function
        const spawnPos = getValidSpawnPoint(this.levelData, teamTag);
        bot.pos.copy(spawnPos);

        this.serverBots.set(id, bot);

        // Create synced schema
        const bs = new BotState();
        bs.id = id;
        bs.loadoutKey = loadoutKey;
        bs.team = team;
        bs.health = bot.health;
        bs.maxHealth = bot.maxHealth;
        bs.shield = bot.shield;
        bs.maxShield = bot.maxShield;
        bs.alive = true;
        bs.doomed = false;
        bs.qw = 1;
        this.state.bots.set(id, bs);
      }
    }
  }

  clearBots() {
    this.serverBots.clear();
    this.state.bots.clear();
  }

  // ------------------------------------------------------------------
  // SERVER TICK (runs at LSS.TICK_RATE Hz)
  // ------------------------------------------------------------------

  serverTick(dtMs) {
    const dt = dtMs / 1000;
    this.gameTime += dt;
    this.state.serverTime = this.gameTime;

    // ---- Round system ----
    this.updateRoundSystem(dt);

    if (this.state.gameState !== 'playing' && this.state.gameState !== 'warmup') {
      // Still sync player positions even outside gameplay (lobby, etc.)
      this.syncAllToSchema();
      return;
    }

    // ---- Update all players ----
    for (const sp of this.serverPlayers.values()) {
      if (!sp.alive || !sp.chassis) continue;
      this.updatePlayerMovement(sp, dt);
      this.updatePlayerWeapon(sp, dt);
      this.updatePlayerAbilities(sp, dt);
      this.updatePlayerDoom(sp, dt);
    }

    // ---- Update all bots ----
    for (const bot of this.serverBots.values()) {
      if (!bot.alive) continue;
      this.updateBotAI(bot, dt);
      this.updateBotDoom(bot, dt);
    }

    // ---- Level collision resolution ----
    for (const sp of this.serverPlayers.values()) {
      if (!sp.alive || !sp.chassis) continue;
      const shipRadius = sp.chassis.hullLength * 0.4;
      resolveCollision(sp.pos, sp.vel, shipRadius, this.levelData);
    }

    for (const bot of this.serverBots.values()) {
      if (!bot.alive) continue;
      const shipRadius = bot.chassis.hullLength * 0.5;
      resolveCollision(bot.pos, bot.vel, shipRadius, this.levelData);
    }

    // ---- Ship-to-ship collision resolution ----
    const allEntities = [];
    for (const sp of this.serverPlayers.values()) {
      if (sp.alive && sp.chassis) {
        allEntities.push({
          id: sp.sessionId,
          pos: sp.pos,
          vel: sp.vel,
          radius: sp.chassis.hullLength * 0.4,
          health: sp.health,
          shield: sp.shield,
          dashActive: sp.dashActive,
        });
      }
    }
    for (const bot of this.serverBots.values()) {
      if (bot.alive) {
        allEntities.push({
          id: bot.id,
          pos: bot.pos,
          vel: bot.vel,
          radius: bot.chassis.hullLength * 0.5,
          health: bot.health,
          shield: bot.shield,
          dashActive: false,
        });
      }
    }

    const ramDamages = resolveShipShipCollisions(allEntities, dt);
    for (const dmgEvent of ramDamages) {
      const target = this.serverPlayers.get(dmgEvent.targetId) || this.serverBots.get(dmgEvent.targetId);
      if (target) this.applyDamage(target, dmgEvent.damage, null);
    }

    // ---- Update projectiles ----
    for (const [id, proj] of this.serverProjectiles) {
      this.updateProjectile(proj, dt);
      if (!proj.alive) {
        this.serverProjectiles.delete(id);
        this.state.projectiles.delete(id);
      }
    }

    // ---- Sync all internal state to Colyseus schema ----
    this.syncAllToSchema();
  }

  // ------------------------------------------------------------------
  // ROUND SYSTEM
  // ------------------------------------------------------------------

  updateRoundSystem(dt) {
    if (this.state.gameState === 'warmup') {
      this.state.warmupTimer -= dt;
      if (this.state.warmupTimer <= 0) {
        this.startRound();
      }
    } else if (this.state.gameState === 'playing') {
      this.state.roundTimer -= dt;

      // Count alive entities per team
      let aliveA = 0, aliveB = 0;
      for (const sp of this.serverPlayers.values()) {
        if (sp.alive) {
          if (sp.team === LSS.TEAM_FLEET_A) aliveA++;
          else aliveB++;
        }
      }
      for (const bot of this.serverBots.values()) {
        if (bot.alive) {
          if (bot.team === LSS.TEAM_FLEET_A) aliveA++;
          else aliveB++;
        }
      }

      if (aliveB === 0) this.endRound(LSS.TEAM_FLEET_A);
      else if (aliveA === 0) this.endRound(LSS.TEAM_FLEET_B);
      else if (this.state.roundTimer <= 0) this.endRound(LSS.TEAM_FLEET_A); // timeout: Fleet A wins
    } else if (this.state.gameState === 'roundEnd') {
      this.roundEndTimer -= dt;
      if (this.roundEndTimer <= 0) this.nextRound();
    }
  }

  // ------------------------------------------------------------------
  // PLAYER MOVEMENT (server authoritative)
  // ------------------------------------------------------------------

  updatePlayerMovement(sp, dt) {
    if (sp.dashActive) {
      sp.dashTimer -= dt;
      if (sp.dashTimer <= 0) sp.dashActive = false;
    }

    // Dash cooldown regen
    if (sp.dashCooldownTimer > 0) {
      sp.dashCooldownTimer -= dt;
      if (sp.dashCooldownTimer <= 0 && sp.dashCharges < sp.chassis.maxDashes) {
        sp.dashCharges++;
        if (sp.dashCharges < sp.chassis.maxDashes) sp.dashCooldownTimer = sp.chassis.dashCooldown;
      }
    }

    sp.spawnProtection = Math.max(0, sp.spawnProtection - dt);

    // Apply camera quaternion from client input
    sp.quat.set(sp.input.qx, sp.input.qy, sp.input.qz, sp.input.qw);

    const ch = sp.chassis;
    const forward = getForward(sp.quat);
    const right = getRight(sp.quat);
    const up = new Vec3(0, 1, 0);

    // Build desired velocity from input
    const moveDir = new Vec3();
    if (sp.input.moveY > 0.1) moveDir.add(forward.clone().multiplyScalar(ch.flightSpeed));
    if (sp.input.moveY < -0.1) moveDir.add(forward.clone().multiplyScalar(-ch.flightSpeed * 0.6));
    if (sp.input.moveX < -0.1) moveDir.add(right.clone().multiplyScalar(-ch.strafeSpeed));
    if (sp.input.moveX > 0.1) moveDir.add(right.clone().multiplyScalar(ch.strafeSpeed));
    if (sp.input.moveZ > 0.1) moveDir.add(up.clone().multiplyScalar(ch.verticalSpeed));
    if (sp.input.moveZ < -0.1) moveDir.add(up.clone().multiplyScalar(-ch.verticalSpeed));

    // Afterburner boost
    if (sp.afterburnerActive) moveDir.multiplyScalar(sp.afterburnerSpeedMult);

    // Acceleration toward desired velocity
    if (moveDir.length() > 0) {
      const accelDir = moveDir.clone().sub(sp.vel);
      const accelMag = Math.min(accelDir.length(), ch.acceleration * dt);
      if (accelMag > 0.01) sp.vel.add(accelDir.normalize().multiplyScalar(accelMag));
    } else {
      const speed = sp.vel.length();
      if (speed > 1) {
        const drag = Math.min(speed, ch.deceleration * dt);
        sp.vel.sub(sp.vel.clone().normalize().multiplyScalar(drag));
      } else {
        sp.vel.set(0, 0, 0);
      }
    }

    // Speed cap
    const maxSpeed = sp.dashActive ? ch.dashSpeed : (sp.afterburnerActive ? 600 : ch.flightSpeed);
    if (sp.vel.length() > maxSpeed) {
      sp.vel.normalize().multiplyScalar(maxSpeed);
    }

    // Apply velocity
    sp.pos.add(sp.vel.clone().multiplyScalar(dt));

    // Arena boundary (soft push + hard clamp)
    const soft = LSS.ARENA_SIZE * 0.8;
    const hard = LSS.ARENA_SIZE * 0.9;
    for (const axis of ['x', 'y', 'z']) {
      if (sp.pos[axis] > soft) sp.vel[axis] -= (sp.pos[axis] - soft) * 0.5 * dt;
      else if (sp.pos[axis] < -soft) sp.vel[axis] -= (sp.pos[axis] + soft) * 0.5 * dt;
      sp.pos[axis] = Math.max(-hard, Math.min(hard, sp.pos[axis]));
    }
  }

  // ------------------------------------------------------------------
  // PLAYER WEAPON
  // ------------------------------------------------------------------

  updatePlayerWeapon(sp, dt) {
    if (!sp.alive || !sp.loadout) return;
    const w = sp.loadout.weapon;

    // Reload
    if (sp.reloading) {
      sp.reloadTimer -= dt;
      if (sp.reloadTimer <= 0) {
        sp.clipAmmo = sp.maxClip;
        sp.reloading = false;
      }
      return;
    }

    // Hold defensive blocks shooting
    if (sp.abilityActive[1] && sp.loadout.abilities[1]) {
      const defName = sp.loadout.abilities[1].name;
      if (['Vortex Shield', 'Sword Block', 'Thermal Shield'].includes(defName)) return;
    }

    // Spinup
    let firing = sp.input.fire;
    if (w.spinup > 0 && firing) {
      if (!sp.spunUp) {
        sp.spinupTimer += dt;
        if (sp.spinupTimer >= w.spinup) sp.spunUp = true;
        return;
      }
    } else if (w.spinup > 0) {
      sp.spinupTimer = Math.max(0, sp.spinupTimer - dt * 2);
      sp.spunUp = false;
    }

    sp.fireTimer -= dt;
    if (sp.legionSwitchTimer > 0) { sp.legionSwitchTimer -= dt; firing = false; }

    if (firing && sp.fireTimer <= 0) {
      const smartCore = sp.coreActive && sp.loadoutKey === 'LEGION';
      if (!smartCore && sp.clipAmmo <= 0) { this.startReload(sp); return; }

      this.fireWeapon(sp);
      sp.isFiring = true;
      sp.fireTimer = w.fireRate;
      if (!smartCore) {
        sp.clipAmmo--;
        if (sp.clipAmmo <= 0 && w.clipSize < 999) this.startReload(sp);
      }
    } else {
      sp.isFiring = false;
    }

    // Manual reload
    if (sp.input.reload && sp.clipAmmo < sp.maxClip && !sp.reloading && w.clipSize < 999) {
      this.startReload(sp);
    }
  }

  startReload(sp) {
    if (sp.loadout.weapon.clipSize >= 999) return;
    sp.reloading = true;
    sp.reloadTimer = 2.0;
  }

  fireWeapon(sp) {
    const w = sp.loadout.weapon;
    const origin = sp.pos.clone();
    const forward = getForward(sp.quat);

    if (w.mode === 'hitscan') {
      this.fireHitscan(sp, origin, forward, w);
    } else if (w.mode === 'projectile') {
      this.fireProjectile(sp, origin, forward, w);
    } else if (w.mode === 'spread') {
      this.fireSpread(sp, origin, forward, w);
    }

    // Broadcast fire event for client-side VFX
    this.broadcast('fire', {
      sid: sp.sessionId,
      mode: w.mode,
      ox: origin.x, oy: origin.y, oz: origin.z,
      dx: forward.x, dy: forward.y, dz: forward.z,
    });
  }

  fireHitscan(sp, origin, dir, w) {
    let aimDir = dir.clone();
    if (w.spread && w.spread > 0) {
      aimDir.x += (Math.random() - 0.5) * w.spread;
      aimDir.y += (Math.random() - 0.5) * w.spread;
      aimDir.z += (Math.random() - 0.5) * w.spread;
      aimDir.normalize();
    }

    // Check level geometry raycast to limit hitscan range
    const wallDist = sdfRaycast(origin.x, origin.y, origin.z, aimDir.x, aimDir.y, aimDir.z, w.range, this.levelData);
    const effectiveRange = Math.min(w.range, wallDist);

    // Find closest hit (players + bots, excluding friendly)
    let bestTarget = null, bestDist = effectiveRange;

    // Check other players
    for (const [sid, other] of this.serverPlayers) {
      if (sid === sp.sessionId || !other.alive || other.team === sp.team) continue;
      const hit = this.rayVsEntity(origin, aimDir, other.pos, other.chassis.hullLength * 0.7, bestDist);
      if (hit !== null && hit < bestDist) { bestTarget = { type: 'player', ref: other }; bestDist = hit; }
    }

    // Check bots
    for (const bot of this.serverBots.values()) {
      if (!bot.alive || bot.team === sp.team) continue;
      const hit = this.rayVsEntity(origin, aimDir, bot.pos, bot.chassis.hullLength * 0.7, bestDist);
      if (hit !== null && hit < bestDist) { bestTarget = { type: 'bot', ref: bot }; bestDist = hit; }
    }

    if (bestTarget) {
      const rangeFalloff = 0.7 + 0.3 * Math.max(0, 1 - bestDist / effectiveRange);
      let finalDmg = w.damage * rangeFalloff;

      // ION ADS bonus
      if (sp.loadoutKey === 'ION' && sp.input.altFire && sp.ionEnergy > 0) finalDmg *= 1.75;
      // Northstar charge
      if (sp.loadoutKey === 'NORTHSTAR' && sp.railgunCharge > 0) {
        finalDmg *= 1.0 + sp.railgunCharge * 3.0;
        sp.railgunCharge = 0;
      }
      // Monarch damage mult
      if (sp.monarchDmgMult > 1) finalDmg *= sp.monarchDmgMult;

      this.applyDamage(bestTarget.ref, finalDmg, sp);

      // Hit confirmation to shooter
      this.clients.forEach(c => {
        if (c.sessionId === sp.sessionId) c.send('hit', { targetId: bestTarget.ref.id || bestTarget.ref.sessionId });
      });
    }
  }

  fireProjectile(sp, origin, dir, w) {
    const id = 'proj_' + (this.projIdCounter++);
    const vel = dir.clone().multiplyScalar(w.projSpeed);
    const proj = new ServerProjectile(id, origin, vel, w.damage, w.splash, sp.sessionId, w.name);
    if (sp.loadoutKey === 'SCORCH') proj.isFireSource = true;
    this.serverProjectiles.set(id, proj);

    const ps = new ProjectileState();
    ps.id = id;
    ps.owner = sp.sessionId;
    ps.px = origin.x; ps.py = origin.y; ps.pz = origin.z;
    ps.vx = vel.x; ps.vy = vel.y; ps.vz = vel.z;
    ps.damage = w.damage;
    ps.splash = w.splash;
    ps.weaponType = w.name;
    this.state.projectiles.set(id, ps);
  }

  fireSpread(sp, origin, dir, w) {
    for (let i = 0; i < w.pellets; i++) {
      const spreadAngle = 0.08;
      const pitch = (Math.random() - 0.5) * spreadAngle;
      const heading = (Math.random() - 0.5) * spreadAngle;
      const spreadDir = dir.clone();
      spreadDir.x += pitch; spreadDir.y += heading;
      spreadDir.normalize();

      let bestTarget = null, bestDist = w.range;

      for (const [sid, other] of this.serverPlayers) {
        if (sid === sp.sessionId || !other.alive || other.team === sp.team) continue;
        const hit = this.rayVsEntity(origin, spreadDir, other.pos, other.chassis.hullLength * 1.2, bestDist);
        if (hit !== null && hit < bestDist) { bestTarget = { type: 'player', ref: other }; bestDist = hit; }
      }
      for (const bot of this.serverBots.values()) {
        if (!bot.alive || bot.team === sp.team) continue;
        const hit = this.rayVsEntity(origin, spreadDir, bot.pos, bot.chassis.hullLength * 1.2, bestDist);
        if (hit !== null && hit < bestDist) { bestTarget = { type: 'bot', ref: bot }; bestDist = hit; }
      }

      if (bestTarget) {
        const rangeFalloff = Math.max(0.3, 1 - (bestDist / w.range) * 0.7);
        let finalDmg = w.damage * rangeFalloff;
        if (sp.monarchDmgMult > 1) finalDmg *= sp.monarchDmgMult;
        this.applyDamage(bestTarget.ref, finalDmg, sp);

        this.clients.forEach(c => {
          if (c.sessionId === sp.sessionId) c.send('hit', { targetId: bestTarget.ref.id || bestTarget.ref.sessionId });
        });
        break; // one pellet per target max per frame
      }
    }
  }

  // Simple ray vs sphere test
  rayVsEntity(origin, dir, entityPos, radius, maxDist) {
    const toEntity = entityPos.clone().sub(origin);
    const proj = toEntity.dot(dir);
    if (proj < 0 || proj > maxDist) return null;
    const closest = origin.clone().add(dir.clone().multiplyScalar(proj));
    const dist = closest.distanceTo(entityPos);
    if (dist < radius) return proj;
    return null;
  }

  // ------------------------------------------------------------------
  // DAMAGE
  // ------------------------------------------------------------------

  applyDamage(target, amount, attacker) {
    if (target.spawnProtection > 0) return;
    if (target.phaseInvuln) return;

    // Defensive ability reductions
    if (target.abilityActive && target.abilityActive[1] && target.loadout) {
      const defName = target.loadout.abilities[1].name;
      if (defName === 'Sword Block') {
        const swordCore = target.coreActive && target.loadout.core.name === 'Sword Core';
        amount *= swordCore ? 0.15 : 0.30;
      }
      if (defName === 'Gun Shield' && target.gunShieldHP > 0) {
        const absorbed = Math.min(amount, target.gunShieldHP);
        target.gunShieldHP -= absorbed;
        amount -= absorbed;
        if (target.gunShieldHP <= 0) {
          target.abilityActive[1] = false;
          target.abilityCooldowns[1] = 15;
        }
        if (amount <= 0) return;
      }
      if (defName === 'Thermal Shield' && target.thermalShieldHP > 0) {
        const absorbed = Math.min(amount, target.thermalShieldHP);
        target.thermalShieldHP -= absorbed;
        amount -= absorbed;
        if (target.thermalShieldHP <= 0) {
          target.abilityActive[1] = false;
          target.abilityCooldowns[1] = 12;
        }
        if (amount <= 0) return;
      }
      if (defName === 'Vortex Shield') {
        const stored = Math.min(amount, 500 - (target.vortexStored || 0));
        target.vortexStored = (target.vortexStored || 0) + stored;
        amount -= stored;
        if (amount <= 0) return;
      }
    }

    // Shield absorbs first
    if (target.shield > 0) {
      if (amount <= target.shield) { target.shield -= amount; return; }
      amount -= target.shield;
      target.shield = 0;
    }

    target.health -= amount;

    // Track attacker stats
    if (attacker && attacker.damageDealt !== undefined) {
      attacker.damageDealt += amount;
      attacker.coreMeter = Math.min(100, attacker.coreMeter + amount / 100);
    }

    // Doomed state
    if (!target.doomed && target.health > 0 && target.health / target.maxHealth <= LSS.DOOMED_HEALTH_PCT) {
      target.doomed = true;
      target.doomTimer = LSS.DOOMED_TIMER;
    }

    // Death
    if (target.health <= 0) {
      this.entityDie(target, attacker);
    }
  }

  entityDie(target, attacker) {
    target.health = 0;
    target.alive = false;

    // Identify attacker for kill feed
    let killerName = 'Unknown';
    if (attacker) {
      if (attacker.sessionId) {
        const ps = this.state.players.get(attacker.sessionId);
        killerName = ps ? (ps.name || attacker.sessionId) : attacker.sessionId;
        attacker.kills = (attacker.kills || 0) + 1;
      } else if (attacker.id) {
        killerName = attacker.loadoutKey || attacker.id;
      }
    }

    let victimName = 'Unknown';
    if (target.sessionId) {
      const ps = this.state.players.get(target.sessionId);
      victimName = ps ? (ps.name || target.sessionId) : target.sessionId;
      target.deaths = (target.deaths || 0) + 1;
    } else if (target.id) {
      victimName = target.loadoutKey || target.id;
    }

    // Kill feed entry
    const ke = new KillEntry();
    ke.killer = killerName;
    ke.victim = victimName;
    ke.weapon = attacker && attacker.loadout ? attacker.loadout.weapon.name : '';
    ke.time = this.gameTime;
    this.state.killFeed.push(ke);
    // Trim old kill feed
    while (this.state.killFeed.length > 10) this.state.killFeed.shift();

    // Broadcast death event for VFX
    const px = target.pos ? target.pos.x : 0;
    const py = target.pos ? target.pos.y : 0;
    const pz = target.pos ? target.pos.z : 0;
    this.broadcast('death', {
      id: target.sessionId || target.id,
      px, py, pz,
      killer: attacker ? (attacker.sessionId || attacker.id) : null,
    });

    // Respawn after delay (players only)
    if (target.sessionId) {
      this.clock.setTimeout(() => {
        const sp = this.serverPlayers.get(target.sessionId);
        if (sp && this.state.gameState === 'playing') {
          this.respawnPlayer(sp);
          this.syncPlayerToSchema(sp);
        }
      }, 5000);
    }
  }

  // ------------------------------------------------------------------
  // PLAYER ABILITIES (simplified; full ability logic can be expanded)
  // ------------------------------------------------------------------

  updatePlayerAbilities(sp, dt) {
    for (let i = 0; i < 3; i++) {
      if (sp.abilityCooldowns[i] > 0) sp.abilityCooldowns[i] = Math.max(0, sp.abilityCooldowns[i] - dt);
      if (sp.abilityActive[i] && sp.abilityTimers[i] < 999) {
        sp.abilityTimers[i] -= dt;
        if (sp.abilityTimers[i] <= 0) sp.abilityActive[i] = false;
      }
    }

    // Core timer
    if (sp.coreActive) {
      sp.coreTimer -= dt;
      if (sp.coreTimer <= 0) {
        sp.coreActive = false;
      }
    }

    // Phase dash invuln
    if (sp.phaseInvuln) {
      sp.phaseInvulnTimer -= dt;
      if (sp.phaseInvulnTimer <= 0) sp.phaseInvuln = false;
    }

    // Afterburner deactivation when ability times out
    if (sp.afterburnerActive && !sp.abilityActive[1]) {
      sp.afterburnerActive = false;
      sp.afterburnerSpeedMult = 1.0;
    }

    // Legion mode switch timer
    if (sp.legionSwitchTimer > 0) sp.legionSwitchTimer -= dt;
  }

  activateAbility(sp, index) {
    if (!sp.alive || !sp.loadout || index < 0 || index > 2) return;
    const ability = sp.loadout.abilities[index];
    if (!ability) return;
    if (sp.abilityCooldowns[index] > 0) return;

    sp.abilityActive[index] = true;
    sp.abilityTimers[index] = ability.duration;
    if (ability.cooldown > 0) sp.abilityCooldowns[index] = ability.cooldown;

    // Specific ability effects
    switch (ability.name) {
      case 'Afterburner':
        sp.afterburnerActive = true;
        sp.afterburnerSpeedMult = 1.8;
        break;
      case 'Phase Dash':
        sp.phaseInvuln = true;
        sp.phaseInvulnTimer = 0.3;
        // Teleport forward
        const fwd = getForward(sp.quat);
        sp.pos.add(fwd.multiplyScalar(400));
        sp.vel.copy(fwd.multiplyScalar(sp.chassis.dashSpeed));
        break;
      case 'Gun Shield':
        sp.gunShieldHP = 5000;
        sp.gunShieldTimer = 10;
        break;
      case 'Thermal Shield':
        sp.thermalShieldHP = 3000;
        break;
      case 'Mode Switch':
        sp.legionMode = sp.legionMode === 'close' ? 'long' : 'close';
        sp.legionSwitchTimer = 0.8;
        // Adjust weapon spread for mode
        // (client-visible; server uses the current loadout spread)
        break;
      case 'Rearm':
        // Reset other ability cooldowns
        for (let i = 0; i < 3; i++) {
          if (i !== index) sp.abilityCooldowns[i] = 0;
        }
        break;
      case 'Laser Shot': {
        // Instant hitscan beam, 2400 damage
        const dir = getForward(sp.quat);
        this.fireHitscan(sp, sp.pos.clone(), dir, { ...sp.loadout.weapon, damage: 2400, range: 3000, spread: 0 });
        break;
      }
      case 'Arc Wave': {
        // Fire arc wave projectile
        const dir2 = getForward(sp.quat);
        const id = 'proj_' + (this.projIdCounter++);
        const vel = dir2.clone().multiplyScalar(600);
        const proj = new ServerProjectile(id, sp.pos.clone(), vel, 2000, 200, sp.sessionId, 'Arc Wave');
        proj.isArcWave = true;
        this.serverProjectiles.set(id, proj);
        const ps = new ProjectileState();
        ps.id = id; ps.owner = sp.sessionId;
        ps.px = sp.pos.x; ps.py = sp.pos.y; ps.pz = sp.pos.z;
        ps.vx = vel.x; ps.vy = vel.y; ps.vz = vel.z;
        ps.damage = 2000; ps.splash = 200; ps.weaponType = 'Arc Wave';
        this.state.projectiles.set(id, ps);
        break;
      }
      case 'Power Shot': {
        const dir3 = getForward(sp.quat);
        this.fireHitscan(sp, sp.pos.clone(), dir3, { ...sp.loadout.weapon, damage: 3200, range: 2000, spread: 0 });
        break;
      }
    }

    // Broadcast ability activation for client VFX
    this.broadcast('ability', {
      sid: sp.sessionId,
      index,
      name: ability.name,
    });
  }

  activateCore(sp) {
    if (!sp.alive || sp.coreMeter < 100 || sp.coreActive) return;
    sp.coreActive = true;
    sp.coreMeter = 0;
    sp.coreTimer = sp.loadout.core.duration;
    this.broadcast('core', { sid: sp.sessionId, name: sp.loadout.core.name });
  }

  performDash(sp) {
    if (!sp.alive || !sp.chassis || sp.dashCharges <= 0 || sp.dashActive) return;
    const fwd = getForward(sp.quat);
    sp.vel.copy(fwd.multiplyScalar(sp.chassis.dashSpeed));
    sp.dashActive = true;
    sp.dashTimer = sp.chassis.dashDuration;
    sp.dashCharges--;
    if (sp.dashCooldownTimer <= 0) sp.dashCooldownTimer = sp.chassis.dashCooldown;
  }

  // ------------------------------------------------------------------
  // DOOM TIMER
  // ------------------------------------------------------------------

  updatePlayerDoom(sp, dt) {
    if (sp.doomed && sp.alive) {
      sp.doomTimer -= dt;
      if (sp.doomTimer <= 0) this.entityDie(sp, null);
    }
  }

  updateBotDoom(bot, dt) {
    if (bot.doomed && bot.alive) {
      bot.doomTimer -= dt;
      if (bot.doomTimer <= 0) this.entityDie(bot, null);
    }
  }

  // ------------------------------------------------------------------
  // BOT AI (simplified server-side version)
  // ------------------------------------------------------------------

  updateBotAI(bot, dt) {
    bot.spawnProtection = Math.max(0, bot.spawnProtection - dt);

    // AI target selection
    bot.aiTimer -= dt;
    if (bot.aiTimer <= 0) {
      bot.aiTimer = 1 + Math.random() * 2;
      bot.aiTarget = this.findBotTarget(bot);
      bot.aiWanderDir = new Vec3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();
    }

    // Strafe timer
    bot.aiStrafeTimer -= dt;
    if (bot.aiStrafeTimer <= 0) {
      bot.aiStrafe = Math.random() < 0.5;
      bot.aiStrafeDir = Math.random() < 0.5 ? 1 : -1;
      bot.aiStrafeTimer = 1 + Math.random() * 2;
    }

    // Movement
    let moveDir = bot.aiWanderDir.clone();
    if (bot.aiTarget) {
      const toTarget = bot.aiTarget.clone().sub(bot.pos);
      const dist = toTarget.length();
      if (bot.aiRetreating) {
        moveDir = bot.pos.clone().sub(bot.aiTarget).normalize();
      } else if (dist > 100) {
        moveDir = toTarget.normalize();
      }
    }

    bot.targetDir.lerp(moveDir, dt * 2);
    bot.targetDir.normalize();

    const accelMult = bot.arcSlowTimer > 0 ? 0.3 : 1.0;
    bot.arcSlowTimer = Math.max(0, bot.arcSlowTimer - dt);

    const accel = bot.targetDir.clone().multiplyScalar(bot.chassis.acceleration * dt * accelMult);
    bot.vel.add(accel);

    const speed = bot.vel.length();
    const maxSpd = bot.arcSlowTimer > 0 ? bot.chassis.flightSpeed * 0.3 : bot.chassis.flightSpeed;
    if (speed > maxSpd) bot.vel.multiplyScalar(maxSpd / speed);
    bot.vel.multiplyScalar(1 - bot.chassis.deceleration * dt / Math.max(speed, 1));

    bot.pos.add(bot.vel.clone().multiplyScalar(dt));

    // Boundary clamp
    const s = LSS.ARENA_SIZE * 0.9;
    bot.pos.clampScalar(-s, s);

    // Retreat when doomed
    if (bot.doomed && !bot.aiRetreating) bot.aiRetreating = true;

    // Fire at targets
    bot.fireTimer -= dt;
    if (bot.fireTimer <= 0 && !bot.aiRetreating && this.state.gameState === 'playing') {
      const target = this.findClosestEnemy(bot);
      if (target) {
        const toTarget = target.pos.clone().sub(bot.pos);
        const dist = toTarget.length();
        if (dist < bot.loadout.weapon.range) {
          const dot = toTarget.clone().normalize().dot(bot.targetDir);
          if (dot > 0.7 && dist <= bot.aiRangePreference * 1.3) {
            // Bot fires (simplified hitscan/projectile)
            this.botFireAtTarget(bot, target);
            bot.fireTimer = bot.loadout.weapon.fireRate * (1 + Math.random() * 0.5);
            bot.isFiring = true;
          }
        }
      }
    }

    bot.coreMeter = Math.min(100, bot.coreMeter + dt * 1.5);
  }

  findBotTarget(bot) {
    // Find nearest enemy (player or bot)
    let bestDist = Infinity;
    let bestPos = null;

    for (const sp of this.serverPlayers.values()) {
      if (!sp.alive || sp.team === bot.team) continue;
      const dist = bot.pos.distanceTo(sp.pos);
      if (dist < bestDist) { bestDist = dist; bestPos = sp.pos.clone(); }
    }

    for (const other of this.serverBots.values()) {
      if (other.id === bot.id || !other.alive || other.team === bot.team) continue;
      const dist = bot.pos.distanceTo(other.pos);
      if (dist < bestDist) { bestDist = dist; bestPos = other.pos.clone(); }
    }

    return bestPos;
  }

  findClosestEnemy(bot) {
    let bestDist = Infinity;
    let bestTarget = null;

    for (const sp of this.serverPlayers.values()) {
      if (!sp.alive || sp.team === bot.team) continue;
      const dist = bot.pos.distanceTo(sp.pos);
      if (dist < bestDist) { bestDist = dist; bestTarget = sp; }
    }

    for (const other of this.serverBots.values()) {
      if (other.id === bot.id || !other.alive || other.team === bot.team) continue;
      const dist = bot.pos.distanceTo(other.pos);
      if (dist < bestDist) { bestDist = dist; bestTarget = other; }
    }

    return bestTarget;
  }

  botFireAtTarget(bot, target) {
    const w = bot.loadout.weapon;
    const origin = bot.pos.clone();
    const dir = target.pos.clone().sub(origin).normalize();

    // Simplified: bots use hitscan-style hit check regardless of weapon mode
    // (avoids having to simulate slow projectiles for bots on server)
    const dist = bot.pos.distanceTo(target.pos);
    const hitChance = Math.max(0.3, 1 - dist / (w.range * 1.5));

    if (Math.random() < hitChance) {
      let dmg = w.damage;
      if (w.mode === 'spread') dmg *= w.pellets * 0.4; // average pellet hit ratio
      const rangeFalloff = 0.7 + 0.3 * Math.max(0, 1 - dist / w.range);
      dmg *= rangeFalloff;
      this.applyDamage(target, dmg, bot);
    }

    // Broadcast bot fire for client VFX
    this.broadcast('fire', {
      sid: bot.id,
      mode: w.mode,
      ox: origin.x, oy: origin.y, oz: origin.z,
      dx: dir.x, dy: dir.y, dz: dir.z,
    });
  }

  // ------------------------------------------------------------------
  // PROJECTILE UPDATE
  // ------------------------------------------------------------------

  updateProjectile(proj, dt) {
    proj.age += dt;
    if (proj.age > proj.lifetime) { proj.alive = false; return; }

    // Tracking (homing missiles)
    if (proj.tracking && proj.trackTargetId) {
      const target = this.serverPlayers.get(proj.trackTargetId) || this.serverBots.get(proj.trackTargetId);
      if (target && target.alive) {
        const toTarget = target.pos.clone().sub(proj.pos);
        const dist = toTarget.length();
        const speed = proj.vel.length();
        const curDir = proj.vel.clone().normalize();
        const toTargetDir = toTarget.normalize();
        const turnRate = dist < 800 ? 5.0 : (dist < 3000 ? 3.0 : 1.5);
        proj.vel.lerp(toTargetDir.multiplyScalar(speed), turnRate * dt);
        proj.vel.normalize().multiplyScalar(speed);
      }
    }

    proj.pos.add(proj.vel.clone().multiplyScalar(dt));

    // Check collision with entities
    const hitRadius = proj.splash > 0 ? proj.splash : 30;

    // Check players
    for (const [sid, sp] of this.serverPlayers) {
      if (sid === proj.ownerId || !sp.alive || !sp.chassis) continue;
      if (proj.pos.distanceTo(sp.pos) < sp.chassis.hullLength * 0.7 + hitRadius) {
        this.applyDamage(sp, proj.damage, this.serverPlayers.get(proj.ownerId) || null);
        this.broadcast('impact', { px: proj.pos.x, py: proj.pos.y, pz: proj.pos.z, splash: proj.splash });
        proj.alive = false;
        return;
      }
    }

    // Check bots
    for (const bot of this.serverBots.values()) {
      if (bot.id === proj.ownerId || !bot.alive) continue;
      // Don't hit friendly bots if owner is a bot
      const ownerBot = this.serverBots.get(proj.ownerId);
      if (ownerBot && ownerBot.team === bot.team) continue;
      // Don't hit friendly bots if owner is a player
      const ownerPlayer = this.serverPlayers.get(proj.ownerId);
      if (ownerPlayer && ownerPlayer.team === bot.team) continue;

      if (proj.pos.distanceTo(bot.pos) < bot.chassis.hullLength * 0.7 + hitRadius) {
        const attacker = this.serverPlayers.get(proj.ownerId) || this.serverBots.get(proj.ownerId) || null;
        this.applyDamage(bot, proj.damage, attacker);
        this.broadcast('impact', { px: proj.pos.x, py: proj.pos.y, pz: proj.pos.z, splash: proj.splash });
        proj.alive = false;
        return;
      }
    }

    // Arena boundary kill
    const s = LSS.ARENA_SIZE;
    if (Math.abs(proj.pos.x) > s || Math.abs(proj.pos.y) > s || Math.abs(proj.pos.z) > s) {
      proj.alive = false;
    }

    // Update synced state
    const ps = this.state.projectiles.get(proj.id);
    if (ps) {
      ps.px = proj.pos.x; ps.py = proj.pos.y; ps.pz = proj.pos.z;
      ps.vx = proj.vel.x; ps.vy = proj.vel.y; ps.vz = proj.vel.z;
    }
  }

  // ------------------------------------------------------------------
  // SYNC internal state -> Colyseus schema (called each tick)
  // ------------------------------------------------------------------

  syncAllToSchema() {
    for (const sp of this.serverPlayers.values()) {
      this.syncPlayerToSchema(sp);
    }
    for (const bot of this.serverBots.values()) {
      this.syncBotToSchema(bot);
    }
  }

  syncPlayerToSchema(sp) {
    const ps = this.state.players.get(sp.sessionId);
    if (!ps) return;

    ps.loadoutKey = sp.loadoutKey || '';
    ps.team = sp.team;
    ps.px = sp.pos.x; ps.py = sp.pos.y; ps.pz = sp.pos.z;
    ps.vx = sp.vel.x; ps.vy = sp.vel.y; ps.vz = sp.vel.z;
    ps.qx = sp.quat.x; ps.qy = sp.quat.y; ps.qz = sp.quat.z; ps.qw = sp.quat.w;
    ps.health = sp.health;
    ps.maxHealth = sp.maxHealth;
    ps.shield = sp.shield;
    ps.maxShield = sp.maxShield;
    ps.coreMeter = sp.coreMeter;
    ps.alive = sp.alive;
    ps.doomed = sp.doomed;
    ps.doomTimer = sp.doomTimer;
    ps.spawnProtection = sp.spawnProtection;
    ps.clipAmmo = sp.clipAmmo;
    ps.reloading = sp.reloading;
    ps.isFiring = sp.isFiring;
    ps.abilityCd0 = sp.abilityCooldowns[0];
    ps.abilityCd1 = sp.abilityCooldowns[1];
    ps.abilityCd2 = sp.abilityCooldowns[2];
    ps.abilityActive0 = sp.abilityActive[0];
    ps.abilityActive1 = sp.abilityActive[1];
    ps.abilityActive2 = sp.abilityActive[2];
    ps.coreActive = sp.coreActive;
    ps.coreTimer = sp.coreTimer;
    ps.dashCharges = sp.dashCharges;
    ps.dashActive = sp.dashActive;
    ps.kills = sp.kills;
    ps.deaths = sp.deaths;
    ps.damageDealt = sp.damageDealt;
  }

  syncBotToSchema(bot) {
    const bs = this.state.bots.get(bot.id);
    if (!bs) return;

    bs.px = bot.pos.x; bs.py = bot.pos.y; bs.pz = bot.pos.z;
    bs.vx = bot.vel.x; bs.vy = bot.vel.y; bs.vz = bot.vel.z;

    // Compute quaternion from targetDir for rendering
    // (simplified: look-at from +Z to targetDir)
    const fwd = bot.targetDir.clone().normalize();
    // Simple forward-to-quaternion (yaw + pitch only)
    const yaw = Math.atan2(-fwd.x, -fwd.z);
    const pitch = Math.asin(Math.max(-1, Math.min(1, fwd.y)));
    const q = new Quat().setFromEuler(pitch, yaw, 0);
    bs.qx = q.x; bs.qy = q.y; bs.qz = q.z; bs.qw = q.w;

    bs.health = bot.health;
    bs.maxHealth = bot.maxHealth;
    bs.shield = bot.shield;
    bs.maxShield = bot.maxShield;
    bs.alive = bot.alive;
    bs.doomed = bot.doomed;
    bs.doomTimer = bot.doomTimer;
    bs.isFiring = bot.isFiring;
    bs.coreMeter = bot.coreMeter;
  }
}

module.exports = { MatchRoom };
