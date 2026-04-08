'use strict';

const { LSS, CHASSIS, LOADOUTS, Vec3, Quat, getForward, getRight, getUp } = require('./shared');
const {
  worldSDF, sdfNormal, sdfRaycast, resolveCollision, resolveShipShipCollisions,
  buildLevelData, getValidSpawnPoint
} = require('./collision');

// ============================================================================
// PLAYER STATE (server-side internal)
// ============================================================================

class ServerPlayer {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.ws = null; // WebSocket connection

    // Loadout
    this.loadoutKey = null;
    this.loadout = null;
    this.chassis = null;

    // Position & movement
    this.pos = new Vec3();
    this.vel = new Vec3();
    this.quat = new Quat();
    this.input = {
      moveX: 0, moveY: 0, moveZ: 0, fire: false, altFire: false, reload: false,
    };

    // Health & damage
    this.maxHealth = 0;
    this.health = 0;
    this.maxShield = 0;
    this.shield = 0;
    this.shieldRegenTimer = 0;
    this.doomed = false;
    this.doomTimer = 0;
    this.spawnProtection = 0;

    // Combat
    this.team = null;
    this.alive = false;
    this.kills = 0;
    this.deaths = 0;
    this.damageDealt = 0;

    // Weapon
    this.clipAmmo = 0;
    this.maxClip = 0;
    this.reloading = false;
    this.reloadTimer = 0;
    this.fireTimer = 0;
    this.isFiring = false;
    this.spunUp = false;
    this.spinupTimer = 0;

    // Abilities
    this.abilityCooldowns = [0, 0, 0];
    this.abilityActive = [false, false, false];
    this.abilityTimers = [0, 0, 0];

    // Loadout-specific state
    this.gunShieldHP = 0;
    this.gunShieldTimer = 0;
    this.thermalShieldHP = 0;
    this.vortexStored = 0;
    this.phaseInvuln = false;
    this.phaseInvulnTimer = 0;
    this.afterburnerActive = false;
    this.afterburnerSpeedMult = 1.0;
    this.ionEnergy = 0;
    this.railgunCharge = 0;
    this.monarchDmgMult = 1.0;
    this.legionMode = 'close';
    this.legionSwitchTimer = 0;

    // Dash
    this.dashCharges = 0;
    this.dashActive = false;
    this.dashTimer = 0;
    this.dashCooldownTimer = 0;

    // Core ability
    this.coreMeter = 0;
    this.coreActive = false;
    this.coreTimer = 0;
  }
}

// ============================================================================
// BOT STATE (simplified)
// ============================================================================

class ServerBot {
  constructor(id, loadoutKey, team) {
    this.id = id;
    this.loadoutKey = loadoutKey;
    this.loadout = LOADOUTS[loadoutKey];
    this.chassis = CHASSIS[this.loadout.chassis];
    this.team = team;

    this.pos = new Vec3();
    this.vel = new Vec3();
    this.targetDir = new Vec3(0, 0, -1);

    this.health = this.chassis.maxHealth;
    this.maxHealth = this.chassis.maxHealth;
    this.shield = this.chassis.maxShield;
    this.maxShield = this.chassis.maxShield;
    this.alive = true;

    this.doomed = false;
    this.doomTimer = 0;
    this.isFiring = false;

    this.coreMeter = 0;

    // AI
    this.aiTimer = 1;
    this.aiTarget = null;
    this.aiWanderDir = new Vec3(0, 0, 1);
    this.aiRetreating = false;
    this.aiStrafeTimer = 1;
    this.aiStrafe = false;
    this.aiStrafeDir = 1;
    this.aiRangePreference = this.getLoadoutRangePreference();
    this.fireTimer = 0;
    this.arcSlowTimer = 0;
    this.spawnProtection = 0;
  }

  getLoadoutRangePreference() {
    switch (this.loadoutKey) {
      case 'NORTHSTAR': return 3500;
      case 'LEGION': return 1500;
      case 'TONE': return 3500;
      case 'RONIN': return 900;
      default: return 2000;
    }
  }
}

// ============================================================================
// PROJECTILE STATE
// ============================================================================

class ServerProjectile {
  constructor(id, origin, velocity, damage, splash, ownerId, weaponType) {
    this.id = id;
    this.pos = origin.clone();
    this.vel = velocity.clone();
    this.damage = damage;
    this.splash = splash;
    this.ownerId = ownerId;
    this.weaponType = weaponType;
    this.lifetime = 10;
    this.age = 0;
    this.alive = true;
    this.isFireSource = false;
  }
}

// ============================================================================
// GAME ROOM (main logic)
// ============================================================================

class GameRoom {
  constructor() {
    this.players = new Map(); // ws -> ServerPlayer
    this.playersBySessionId = new Map(); // sessionId -> ServerPlayer
    this.bots = new Map(); // id -> ServerBot
    this.projectiles = new Map(); // id -> ServerProjectile

    this.gameState = 'lobby'; // 'lobby', 'warmup', 'playing', 'round_end', 'match_end'
    this.roundTimer = LSS.ROUND_TIME;
    this.warmupTimer = LSS.WARMUP_TIME;
    this.scoreA = 0;
    this.scoreB = 0;
    this.currentRound = 1;
    this.roundEndTimer = 3;
    this.gameTime = 0;

    this.levelData = buildLevelData('circumpunct');
    this.stateSyncCounter = 0;
    this.projIdCounter = 0;

    // Game loop
    const dtMs = 1000 / LSS.TICK_RATE;
    this.gameLoopInterval = setInterval(() => this.tick(dtMs / 1000), dtMs);
  }

  tick(dt) {
    this.gameTime += dt;

    // Movement
    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive || !sp.chassis) continue;
      this.updatePlayerMovement(sp, dt);
    }
    for (const bot of this.bots.values()) {
      if (!bot.alive) continue;
      this.updateBotAI(bot, dt);
    }

    // Collision with level
    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive || !sp.chassis) continue;
      const shipRadius = sp.chassis.hullLength * 0.5;
      resolveCollision(sp.pos, sp.vel, shipRadius, this.levelData);
    }
    for (const bot of this.bots.values()) {
      if (!bot.alive) continue;
      const shipRadius = bot.chassis.hullLength * 0.5;
      resolveCollision(bot.pos, bot.vel, shipRadius, this.levelData);
    }

    // Weapon updates
    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive || !sp.loadout) continue;
      this.updatePlayerWeapon(sp, dt);
    }

    // Abilities
    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive) continue;
      this.updatePlayerAbilities(sp, dt);
    }

    // Ship-to-ship collisions
    const allEntities = [
      ...Array.from(this.playersBySessionId.values()),
      ...Array.from(this.bots.values())
    ];
    const ramDamages = resolveShipShipCollisions(allEntities, dt);
    for (const dmgEvent of ramDamages) {
      const target = this.playersBySessionId.get(dmgEvent.targetId) || this.bots.get(dmgEvent.targetId);
      if (target) this.applyDamage(target, dmgEvent.damage, null);
    }

    // Projectiles
    for (const [id, proj] of this.projectiles) {
      this.updateProjectile(proj, dt);
      if (!proj.alive) this.projectiles.delete(id);
    }

    // Doom timers
    for (const sp of this.playersBySessionId.values()) {
      if (sp.alive) this.updatePlayerDoom(sp, dt);
    }
    for (const bot of this.bots.values()) {
      if (bot.alive) this.updateBotDoom(bot, dt);
    }

    // Round system
    this.updateRoundSystem(dt);

    // Broadcast state (every other tick = 33 Hz)
    if (this.stateSyncCounter % 2 === 0) {
      this.broadcastState();
    }
    this.stateSyncCounter++;
  }

  // ========================================================================
  // MOVEMENT
  // ========================================================================

  updatePlayerMovement(sp, dt) {
    if (sp.dashActive) {
      sp.dashTimer -= dt;
      if (sp.dashTimer <= 0) sp.dashActive = false;
    }

    if (sp.dashCooldownTimer > 0) {
      sp.dashCooldownTimer -= dt;
      if (sp.dashCooldownTimer <= 0 && sp.dashCharges < sp.chassis.maxDashes) {
        sp.dashCharges++;
        if (sp.dashCharges < sp.chassis.maxDashes) sp.dashCooldownTimer = sp.chassis.dashCooldown;
      }
    }

    const ch = sp.chassis;
    const forward = getForward(sp.quat);
    const right = getRight(sp.quat);
    const up = getUp(sp.quat);

    // Build movement vector
    const moveDir = new Vec3();
    if (sp.input.moveY > 0.1) moveDir.add(forward.clone().multiplyScalar(ch.flightSpeed));
    if (sp.input.moveY < -0.1) moveDir.add(forward.clone().multiplyScalar(-ch.flightSpeed * 0.6));
    if (sp.input.moveX < -0.1) moveDir.add(right.clone().multiplyScalar(-ch.strafeSpeed));
    if (sp.input.moveX > 0.1) moveDir.add(right.clone().multiplyScalar(ch.strafeSpeed));
    if (sp.input.moveZ > 0.1) moveDir.add(up.clone().multiplyScalar(ch.verticalSpeed));
    if (sp.input.moveZ < -0.1) moveDir.add(up.clone().multiplyScalar(-ch.verticalSpeed));

    if (sp.afterburnerActive) moveDir.multiplyScalar(sp.afterburnerSpeedMult);

    // Accelerate
    if (moveDir.length() > 0) {
      const accelDir = moveDir.clone().normalize();
      const accelMag = Math.min(moveDir.length(), ch.acceleration * dt);
      if (accelMag > 0.01) sp.vel.add(accelDir.normalize().multiplyScalar(accelMag));
    }

    // Deceleration when no input
    if (moveDir.length() < 0.1) {
      const speed = sp.vel.length();
      if (speed > 1) {
        const decel = Math.min(speed, ch.deceleration * dt);
        sp.vel.multiplyScalar(1 - decel / Math.max(speed, 1));
      }
    }

    // Max speed cap
    const maxSpeed = ch.flightSpeed * 1.5;
    if (sp.vel.length() > maxSpeed) {
      sp.vel.normalize().multiplyScalar(maxSpeed);
    }

    // Apply drag
    sp.vel.multiplyScalar(1 - 0.02 * dt);

    // Soft boundary
    const soft = LSS.ARENA_SIZE * 0.8;
    for (const axis of ['x', 'y', 'z']) {
      if (sp.pos[axis] > soft) sp.vel[axis] -= (sp.pos[axis] - soft) * 0.5 * dt;
      if (sp.pos[axis] < -soft) sp.vel[axis] += (-soft - sp.pos[axis]) * 0.5 * dt;
    }

    // Integrate
    sp.pos.add(sp.vel.clone().multiplyScalar(dt));
  }

  // ========================================================================
  // WEAPON SYSTEM
  // ========================================================================

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
    }

    // Block fire if holding defensive ability
    if (sp.abilityActive[1] && sp.loadout.abilities[1]) {
      const defName = sp.loadout.abilities[1].name;
      if (['Vortex Shield', 'Sword Block', 'Thermal Shield'].includes(defName)) return;
    }

    // Spinup
    const firing = sp.input.fire && !sp.reloading;
    if (w.spinup > 0 && firing) {
      if (!sp.spunUp) {
        sp.spinupTimer += dt;
        if (sp.spinupTimer >= w.spinup) sp.spunUp = true;
      }
    } else {
      sp.spunUp = false;
      sp.spinupTimer = 0;
    }

    // Legion mode switch cooldown
    if (sp.legionSwitchTimer > 0) { sp.legionSwitchTimer -= dt; }

    // Fire weapon
    if (firing && sp.fireTimer <= 0) {
      const smartCore = sp.coreActive && sp.loadout.core.name === 'Smart Core';

      if (!smartCore && sp.clipAmmo <= 0) { this.startReload(sp); return; }

      this.fireWeapon(sp);
      if (!smartCore) sp.clipAmmo--;
      sp.fireTimer = w.fireRate;
      sp.spunUp = false;
      sp.spinupTimer = 0;

      if (!smartCore && sp.clipAmmo <= 0 && w.clipSize < 999) this.startReload(sp);
    }

    // Fire timer
    if (sp.fireTimer > 0) sp.fireTimer -= dt;
    sp.isFiring = firing && sp.fireTimer <= 0.1;

    // Reload on input
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

    // Broadcast fire event
    this.broadcast('fire', {
      sid: sp.sessionId,
      mode: w.mode,
      px: origin.x, py: origin.y, pz: origin.z,
      dx: forward.x, dy: forward.y, dz: forward.z,
      weaponType: w.name,
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

    // Raycast to find wall distance
    const wallDist = sdfRaycast(origin.x, origin.y, origin.z, aimDir.x, aimDir.y, aimDir.z, w.range, this.levelData);
    const effectiveRange = Math.min(w.range, wallDist);

    let bestTarget = null, bestDist = effectiveRange;

    // Check players
    for (const [sid, other] of this.playersBySessionId) {
      if (sid === sp.sessionId || !other.alive || other.team === sp.team) continue;
      const hit = this.rayVsEntity(origin, aimDir, other.pos, other.chassis.hullLength * 0.7, bestDist);
      if (hit !== null && hit < bestDist) { bestTarget = other; bestDist = hit; }
    }

    // Check bots
    for (const bot of this.bots.values()) {
      if (!bot.alive || bot.team === sp.team) continue;
      const hit = this.rayVsEntity(origin, aimDir, bot.pos, bot.chassis.hullLength * 0.7, bestDist);
      if (hit !== null && hit < bestDist) { bestTarget = bot; bestDist = hit; }
    }

    if (bestTarget) {
      const rangeFalloff = 0.7 + 0.3 * Math.max(0, 1 - bestDist / effectiveRange);
      let finalDmg = w.damage * rangeFalloff;

      if (sp.monarchDmgMult > 1) finalDmg *= sp.monarchDmgMult;

      this.applyDamage(bestTarget, finalDmg, sp);
    }
  }

  fireProjectile(sp, origin, dir, w) {
    const id = 'proj_' + (this.projIdCounter++);
    const vel = dir.clone().multiplyScalar(w.projSpeed);
    const proj = new ServerProjectile(id, origin, vel, w.damage, w.splash, sp.sessionId, w.name);
    this.projectiles.set(id, proj);
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

      for (const other of this.playersBySessionId.values()) {
        if (other.sessionId === sp.sessionId || !other.alive || other.team === sp.team) continue;
        const hit = this.rayVsEntity(origin, spreadDir, other.pos, other.chassis.hullLength * 1.2, bestDist);
        if (hit !== null && hit < bestDist) { bestTarget = other; bestDist = hit; }
      }
      for (const bot of this.bots.values()) {
        if (!bot.alive || bot.team === sp.team) continue;
        const hit = this.rayVsEntity(origin, spreadDir, bot.pos, bot.chassis.hullLength * 1.2, bestDist);
        if (hit !== null && hit < bestDist) { bestTarget = bot; bestDist = hit; }
      }

      if (bestTarget) {
        const rangeFalloff = Math.max(0.3, 1 - (bestDist / w.range) * 0.7);
        let finalDmg = w.damage * rangeFalloff;
        if (sp.monarchDmgMult > 1) finalDmg *= sp.monarchDmgMult;
        this.applyDamage(bestTarget, finalDmg, sp);
        break;
      }
    }
  }

  rayVsEntity(origin, dir, entityPos, radius, maxDist) {
    const toEntity = entityPos.clone().sub(origin);
    const proj = toEntity.dot(dir);
    if (proj < 0 || proj > maxDist) return null;
    const closest = origin.clone().add(dir.clone().multiplyScalar(proj));
    const dist = closest.distanceTo(entityPos);
    if (dist < radius) return proj;
    return null;
  }

  // ========================================================================
  // DAMAGE & DEATH
  // ========================================================================

  applyDamage(target, amount, attacker) {
    if (target.spawnProtection > 0) return;
    if (target.phaseInvuln) return;

    // Defensive abilities
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

    // Track stats
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

    let killerName = 'Unknown';
    if (attacker) {
      if (attacker.sessionId) {
        killerName = attacker.sessionId.substring(0, 8);
        attacker.kills = (attacker.kills || 0) + 1;
      } else if (attacker.id) {
        killerName = attacker.loadoutKey || attacker.id;
      }
    }

    let victimName = 'Unknown';
    if (target.sessionId) {
      victimName = target.sessionId.substring(0, 8);
      target.deaths = (target.deaths || 0) + 1;
    } else if (target.id) {
      victimName = target.loadoutKey || target.id;
    }

    this.broadcast('death', {
      victimSid: target.sessionId || target.id,
      victimName,
      killerName,
      px: target.pos.x, py: target.pos.y, pz: target.pos.z,
    });

    // Respawn after delay (players only)
    if (target.sessionId) {
      setTimeout(() => {
        const sp = this.playersBySessionId.get(target.sessionId);
        if (sp && this.gameState === 'playing') {
          this.respawnPlayer(sp);
        }
      }, 5000);
    }
  }

  // ========================================================================
  // ABILITIES
  // ========================================================================

  updatePlayerAbilities(sp, dt) {
    for (let i = 0; i < 3; i++) {
      if (sp.abilityCooldowns[i] > 0) sp.abilityCooldowns[i] = Math.max(0, sp.abilityCooldowns[i] - dt);
      if (sp.abilityActive[i] && sp.abilityTimers[i] < 999) {
        sp.abilityTimers[i] -= dt;
        if (sp.abilityTimers[i] <= 0) sp.abilityActive[i] = false;
      }
    }

    if (sp.coreActive) {
      sp.coreTimer -= dt;
      if (sp.coreTimer <= 0) sp.coreActive = false;
    }

    if (sp.phaseInvuln) {
      sp.phaseInvulnTimer -= dt;
      if (sp.phaseInvulnTimer <= 0) sp.phaseInvuln = false;
    }

    if (sp.afterburnerActive && !sp.abilityActive[1]) {
      sp.afterburnerActive = false;
      sp.afterburnerSpeedMult = 1.0;
    }

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

    switch (ability.name) {
      case 'Afterburner':
        sp.afterburnerActive = true;
        sp.afterburnerSpeedMult = 1.8;
        break;
      case 'Phase Dash':
        sp.phaseInvuln = true;
        sp.phaseInvulnTimer = 0.3;
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
        break;
      case 'Rearm':
        for (let i = 0; i < 3; i++) {
          if (i !== index) sp.abilityCooldowns[i] = 0;
        }
        break;
      case 'Laser Shot': {
        const dir = getForward(sp.quat);
        this.fireHitscan(sp, sp.pos.clone(), dir, { ...sp.loadout.weapon, damage: 2400, range: 3000, spread: 0 });
        break;
      }
      case 'Arc Wave': {
        const dir2 = getForward(sp.quat);
        const id = 'proj_' + (this.projIdCounter++);
        const vel = dir2.clone().multiplyScalar(600);
        const proj = new ServerProjectile(id, sp.pos.clone(), vel, 2000, 200, sp.sessionId, 'Arc Wave');
        this.projectiles.set(id, proj);
        break;
      }
      case 'Power Shot': {
        const dir3 = getForward(sp.quat);
        this.fireHitscan(sp, sp.pos.clone(), dir3, { ...sp.loadout.weapon, damage: 3200, range: 2000, spread: 0 });
        break;
      }
    }

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

  // ========================================================================
  // DOOM TIMER
  // ========================================================================

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

  // ========================================================================
  // BOT AI
  // ========================================================================

  updateBotAI(bot, dt) {
    bot.spawnProtection = Math.max(0, bot.spawnProtection - dt);

    bot.aiTimer -= dt;
    if (bot.aiTimer <= 0) {
      bot.aiTimer = 1 + Math.random() * 2;
      bot.aiTarget = this.findBotTarget(bot);
      bot.aiWanderDir = new Vec3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();
    }

    bot.aiStrafeTimer -= dt;
    if (bot.aiStrafeTimer <= 0) {
      bot.aiStrafe = Math.random() < 0.5;
      bot.aiStrafeDir = Math.random() < 0.5 ? 1 : -1;
      bot.aiStrafeTimer = 1 + Math.random() * 2;
    }

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

    const s = LSS.ARENA_SIZE * 0.9;
    bot.pos.clampScalar(-s, s);

    if (bot.doomed && !bot.aiRetreating) bot.aiRetreating = true;

    bot.fireTimer -= dt;
    if (bot.fireTimer <= 0 && !bot.aiRetreating && this.gameState === 'playing') {
      const target = this.findClosestEnemy(bot);
      if (target) {
        const toTarget = target.pos.clone().sub(bot.pos);
        const dist = toTarget.length();
        if (dist < bot.loadout.weapon.range) {
          const dot = toTarget.clone().normalize().dot(bot.targetDir);
          if (dot > 0.7 && dist <= bot.aiRangePreference * 1.3) {
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
    let bestDist = Infinity;
    let bestPos = null;

    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive || sp.team === bot.team) continue;
      const dist = bot.pos.distanceTo(sp.pos);
      if (dist < bestDist) { bestDist = dist; bestPos = sp.pos.clone(); }
    }

    for (const other of this.bots.values()) {
      if (other.id === bot.id || !other.alive || other.team === bot.team) continue;
      const dist = bot.pos.distanceTo(other.pos);
      if (dist < bestDist) { bestDist = dist; bestPos = other.pos.clone(); }
    }

    return bestPos;
  }

  findClosestEnemy(bot) {
    let bestDist = Infinity;
    let bestTarget = null;

    for (const sp of this.playersBySessionId.values()) {
      if (!sp.alive || sp.team === bot.team) continue;
      const dist = bot.pos.distanceTo(sp.pos);
      if (dist < bestDist) { bestDist = dist; bestTarget = sp; }
    }

    for (const other of this.bots.values()) {
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

    const dist = bot.pos.distanceTo(target.pos);
    const hitChance = Math.max(0.3, 1 - dist / (w.range * 1.5));

    if (Math.random() < hitChance) {
      let dmg = w.damage;
      if (w.mode === 'spread') dmg *= w.pellets * 0.4;
      const rangeFalloff = 0.7 + 0.3 * Math.max(0, 1 - dist / w.range);
      dmg *= rangeFalloff;
      this.applyDamage(target, dmg, bot);
    }

    this.broadcast('fire', {
      sid: bot.id,
      mode: w.mode,
      px: origin.x, py: origin.y, pz: origin.z,
      dx: dir.x, dy: dir.y, dz: dir.z,
      weaponType: w.name,
    });
  }

  // ========================================================================
  // PROJECTILES
  // ========================================================================

  updateProjectile(proj, dt) {
    proj.age += dt;
    if (proj.age > proj.lifetime) { proj.alive = false; return; }

    proj.pos.add(proj.vel.clone().multiplyScalar(dt));

    const hitRadius = proj.splash > 0 ? proj.splash : 30;

    // Check players
    for (const sp of this.playersBySessionId.values()) {
      if (sp.sessionId === proj.ownerId || !sp.alive || !sp.chassis) continue;
      if (proj.pos.distanceTo(sp.pos) < sp.chassis.hullLength * 0.7 + hitRadius) {
        const owner = this.playersBySessionId.get(proj.ownerId);
        this.applyDamage(sp, proj.damage, owner || null);
        this.broadcast('impact', { px: proj.pos.x, py: proj.pos.y, pz: proj.pos.z, size: proj.splash });
        proj.alive = false;
        return;
      }
    }

    // Check bots
    for (const bot of this.bots.values()) {
      if (bot.id === proj.ownerId || !bot.alive) continue;
      const ownerBot = this.bots.get(proj.ownerId);
      if (ownerBot && ownerBot.team === bot.team) continue;
      const ownerPlayer = this.playersBySessionId.get(proj.ownerId);
      if (ownerPlayer && ownerPlayer.team === bot.team) continue;

      if (proj.pos.distanceTo(bot.pos) < bot.chassis.hullLength * 0.7 + hitRadius) {
        const attacker = this.playersBySessionId.get(proj.ownerId) || this.bots.get(proj.ownerId) || null;
        this.applyDamage(bot, proj.damage, attacker);
        this.broadcast('impact', { px: proj.pos.x, py: proj.pos.y, pz: proj.pos.z, size: proj.splash });
        proj.alive = false;
        return;
      }
    }

    // Arena boundary
    const s = LSS.ARENA_SIZE;
    if (Math.abs(proj.pos.x) > s || Math.abs(proj.pos.y) > s || Math.abs(proj.pos.z) > s) {
      proj.alive = false;
    }
  }

  // ========================================================================
  // ROUND SYSTEM
  // ========================================================================

  updateRoundSystem(dt) {
    if (this.gameState === 'warmup') {
      this.warmupTimer -= dt;
      if (this.warmupTimer <= 0) {
        this.startRound();
      }
    } else if (this.gameState === 'playing') {
      this.roundTimer -= dt;

      let aliveA = 0, aliveB = 0;
      for (const sp of this.playersBySessionId.values()) {
        if (sp.alive) {
          if (sp.team === LSS.TEAM_FLEET_A) aliveA++;
          else if (sp.team === LSS.TEAM_FLEET_B) aliveB++;
        }
      }
      for (const bot of this.bots.values()) {
        if (bot.alive) {
          if (bot.team === LSS.TEAM_FLEET_A) aliveA++;
          else if (bot.team === LSS.TEAM_FLEET_B) aliveB++;
        }
      }

      if (aliveB === 0) this.endRound(LSS.TEAM_FLEET_A);
      else if (aliveA === 0) this.endRound(LSS.TEAM_FLEET_B);
      else if (this.roundTimer <= 0) this.endRound(null);
    } else if (this.gameState === 'round_end') {
      this.roundEndTimer -= dt;
      if (this.roundEndTimer <= 0) this.nextRound();
    }
  }

  startWarmup() {
    this.gameState = 'warmup';
    this.warmupTimer = LSS.WARMUP_TIME;
    this.broadcast('round_start', { round: this.currentRound, mapKey: 'circumpunct' });
  }

  startRound() {
    this.gameState = 'playing';
    this.roundTimer = LSS.ROUND_TIME;
    this.broadcast('round_start', { round: this.currentRound, mapKey: 'circumpunct' });
  }

  endRound(winnerTeam) {
    this.gameState = 'round_end';
    if (winnerTeam === LSS.TEAM_FLEET_A) this.scoreA++;
    else if (winnerTeam === LSS.TEAM_FLEET_B) this.scoreB++;

    const winner = winnerTeam === LSS.TEAM_FLEET_A ? 'Team A' : winnerTeam === LSS.TEAM_FLEET_B ? 'Team B' : 'Draw';
    this.broadcast('round_end', {
      winner,
      scoreA: this.scoreA,
      scoreB: this.scoreB,
    });

    this.roundEndTimer = 3;
  }

  nextRound() {
    if (this.scoreA >= LSS.ROUNDS_TO_WIN || this.scoreB >= LSS.ROUNDS_TO_WIN) {
      this.gameState = 'match_end';
      const winner = this.scoreA >= LSS.ROUNDS_TO_WIN ? 'Team A' : 'Team B';
      this.broadcast('match_end', { winner, scoreA: this.scoreA, scoreB: this.scoreB });
      return;
    }

    this.currentRound++;
    for (const sp of this.playersBySessionId.values()) {
      if (sp.loadoutKey) this.respawnPlayer(sp);
    }

    this.clearBots();
    this.spawnBots();
    this.startWarmup();
  }

  respawnPlayer(sp) {
    const teamTag = sp.team === LSS.TEAM_FLEET_A ? 'A' : 'B';
    sp.pos = getValidSpawnPoint(this.levelData, teamTag);
    sp.vel.set(0, 0, 0);
    sp.quat.set(0, 0, 0, 1);
    sp.health = sp.maxHealth;
    sp.shield = sp.maxShield;
    sp.shieldRegenTimer = 0;
    sp.alive = true;
    sp.doomed = false;
    sp.doomTimer = 0;
    sp.spawnProtection = LSS.SPAWN_PROTECTION;
    sp.clipAmmo = sp.maxClip;
    sp.reloading = false;
    sp.reloadTimer = 0;
    sp.fireTimer = 0;
    sp.dashCharges = sp.chassis.maxDashes;
    sp.dashActive = false;
    sp.dashTimer = 0;
    sp.dashCooldownTimer = 0;
    sp.coreMeter = 0;
  }

  spawnBots() {
    const botsPerTeam = 2;
    for (let t = 0; t < 2; t++) {
      const team = t === 0 ? LSS.TEAM_FLEET_A : LSS.TEAM_FLEET_B;
      const teamTag = t === 0 ? 'A' : 'B';

      for (let i = 0; i < botsPerTeam; i++) {
        const loadoutKeys = ['ION', 'SCORCH', 'NORTHSTAR', 'RONIN', 'TONE', 'LEGION', 'MONARCH'];
        const loadoutKey = loadoutKeys[Math.floor(Math.random() * loadoutKeys.length)];
        const botId = 'bot_' + Math.random().toString(36).substr(2, 9);
        const bot = new ServerBot(botId, loadoutKey, team);
        bot.pos = getValidSpawnPoint(this.levelData, teamTag);
        bot.health = bot.maxHealth;
        bot.shield = bot.maxShield;
        this.bots.set(botId, bot);
      }
    }
  }

  clearBots() {
    this.bots.clear();
  }

  // ========================================================================
  // STATE SYNC
  // ========================================================================

  broadcastState() {
    const players = {};
    for (const sp of this.playersBySessionId.values()) {
      players[sp.sessionId] = {
        sid: sp.sessionId, loadoutKey: sp.loadoutKey || '', team: sp.team,
        px: sp.pos.x, py: sp.pos.y, pz: sp.pos.z,
        vx: sp.vel.x, vy: sp.vel.y, vz: sp.vel.z,
        qx: sp.quat.x, qy: sp.quat.y, qz: sp.quat.z, qw: sp.quat.w,
        health: sp.health, maxHealth: sp.maxHealth,
        shield: sp.shield, maxShield: sp.maxShield,
        coreMeter: sp.coreMeter, alive: sp.alive,
        doomed: sp.doomed, doomTimer: sp.doomTimer,
        spawnProtection: sp.spawnProtection,
        clipAmmo: sp.clipAmmo, reloading: sp.reloading, isFiring: sp.isFiring,
        abilityCd0: sp.abilityCooldowns[0], abilityCd1: sp.abilityCooldowns[1], abilityCd2: sp.abilityCooldowns[2],
        abilityActive0: sp.abilityActive[0], abilityActive1: sp.abilityActive[1], abilityActive2: sp.abilityActive[2],
        coreActive: sp.coreActive, coreTimer: sp.coreTimer,
        dashCharges: sp.dashCharges, dashActive: sp.dashActive,
        kills: sp.kills, deaths: sp.deaths, damageDealt: sp.damageDealt,
      };
    }

    const bots = {};
    for (const bot of this.bots.values()) {
      const td = bot.targetDir;
      const len = Math.sqrt(td.x * td.x + td.y * td.y + td.z * td.z) || 1;
      const fx = td.x / len, fy = td.y / len, fz = td.z / len;
      const yaw = Math.atan2(-fx, -fz);
      const pitch = Math.asin(Math.max(-1, Math.min(1, fy)));
      const q = new Quat().setFromEuler(pitch, yaw, 0);
      bots[bot.id] = {
        id: bot.id, loadoutKey: bot.loadoutKey, team: bot.team,
        px: bot.pos.x, py: bot.pos.y, pz: bot.pos.z,
        vx: bot.vel.x, vy: bot.vel.y, vz: bot.vel.z,
        qx: q.x, qy: q.y, qz: q.z, qw: q.w,
        health: bot.health, maxHealth: bot.maxHealth,
        shield: bot.shield, maxShield: bot.maxShield,
        alive: bot.alive, doomed: bot.doomed, doomTimer: bot.doomTimer,
        isFiring: bot.isFiring, coreMeter: bot.coreMeter,
      };
    }

    const msg = {
      type: 'state_sync',
      gameState: this.gameState,
      roundTimer: this.roundTimer,
      warmupTimer: this.warmupTimer,
      scoreA: this.scoreA,
      scoreB: this.scoreB,
      currentRound: this.currentRound,
      serverTime: this.gameTime,
      players, bots,
    };

    this.broadcast(null, msg);
  }

  broadcast(type, data) {
    const msg = type ? { type, ...data } : data;
    const json = JSON.stringify(msg);
    for (const sp of this.playersBySessionId.values()) {
      if (sp.ws && sp.ws.readyState === 1) {
        sp.ws.send(json);
      }
    }
  }

  onPlayerJoin(ws, sessionId) {
    const sp = new ServerPlayer(sessionId);
    sp.ws = ws;
    this.players.set(ws, sp);
    this.playersBySessionId.set(sessionId, sp);

    ws.send(JSON.stringify({ type: 'welcome', sessionId }));
  }

  onPlayerMessage(ws, data) {
    const sp = this.players.get(ws);
    if (!sp) return;

    const msg = typeof data === 'string' ? JSON.parse(data) : data;

    switch (msg.type) {
      case 'select_loadout': {
        const loadoutKey = msg.loadoutKey;
        if (!LOADOUTS[loadoutKey]) return;

        sp.loadoutKey = loadoutKey;
        sp.loadout = LOADOUTS[loadoutKey];
        sp.chassis = CHASSIS[sp.loadout.chassis];
        sp.team = Math.random() < 0.5 ? LSS.TEAM_FLEET_A : LSS.TEAM_FLEET_B;
        sp.maxHealth = sp.chassis.maxHealth;
        sp.health = sp.maxHealth;
        sp.maxShield = sp.chassis.maxShield;
        sp.shield = sp.maxShield;
        sp.maxClip = sp.loadout.weapon.clipSize;
        sp.clipAmmo = sp.maxClip;

        const readyCount = Array.from(this.playersBySessionId.values()).filter(p => p.loadoutKey).length;
        if (readyCount >= 1 && this.gameState === 'lobby') {
          this.startWarmup();
        }

        this.respawnPlayer(sp);
        break;
      }
      case 'input': {
        if (!sp.alive) break;
        sp.input.moveX = msg.mx || 0;
        sp.input.moveY = msg.my || 0;
        sp.input.moveZ = msg.mz || 0;
        sp.input.fire = msg.fire || false;
        sp.input.altFire = msg.alt || false;
        sp.input.reload = msg.reload || false;

        if (msg.qx !== undefined) {
          sp.quat.set(msg.qx, msg.qy, msg.qz, msg.qw);
        }
        break;
      }
      case 'dash': {
        if (sp) this.performDash(sp);
        break;
      }
      case 'ability': {
        if (sp) this.activateAbility(sp, msg.index);
        break;
      }
      case 'core': {
        if (sp) this.activateCore(sp);
        break;
      }
    }
  }

  onPlayerLeave(ws) {
    const sp = this.players.get(ws);
    if (sp) {
      this.players.delete(ws);
      this.playersBySessionId.delete(sp.sessionId);
    }
  }

  shutdown() {
    clearInterval(this.gameLoopInterval);
  }
}

module.exports = { GameRoom, ServerPlayer, ServerBot, ServerProjectile };
