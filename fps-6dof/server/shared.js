// ============================================================================
// LAST SHIP SAILING ; Shared constants and data
// Used by both server and client
// ============================================================================

'use strict';

const LSS = {
  MAX_PLAYERS: 12,
  TEAM_FLEET_A: 2,
  TEAM_FLEET_B: 3,
  ROUND_TIME: 180,
  WARMUP_TIME: 5,
  ROUNDS_TO_WIN: 4,
  SPAWN_PROTECTION: 3,
  DOOMED_HEALTH_PCT: 0.15,
  DOOMED_TIMER: 10,
  GRAVITY: 0,
  ARENA_SIZE: 25000,
  TICK_RATE: 20, // server tick rate (Hz); client renders at 60fps with interpolation
};

const CHASSIS = {
  FRIGATE: {
    name: 'Frigate', maxHealth: 7500, maxShield: 2500,
    shieldRegenRate: 200, shieldRegenDelay: 5,
    flightSpeed: 450, strafeSpeed: 350, verticalSpeed: 300,
    acceleration: 1200, deceleration: 800,
    turnRate: 180, pitchRate: 120,
    maxDashes: 3, dashSpeed: 900, dashDuration: 0.4, dashCooldown: 4,
    hullWidth: 60, hullHeight: 25, hullLength: 80, mass: 5000,
  },
  CORVETTE: {
    name: 'Corvette', maxHealth: 10000, maxShield: 3500,
    shieldRegenRate: 175, shieldRegenDelay: 6,
    flightSpeed: 350, strafeSpeed: 280, verticalSpeed: 250,
    acceleration: 800, deceleration: 600,
    turnRate: 140, pitchRate: 100,
    maxDashes: 2, dashSpeed: 750, dashDuration: 0.5, dashCooldown: 5,
    hullWidth: 80, hullHeight: 30, hullLength: 100, mass: 8000,
  },
  DREADNOUGHT: {
    name: 'Dreadnought', maxHealth: 12500, maxShield: 5000,
    shieldRegenRate: 150, shieldRegenDelay: 8,
    flightSpeed: 250, strafeSpeed: 180, verticalSpeed: 160,
    acceleration: 500, deceleration: 400,
    turnRate: 100, pitchRate: 70,
    maxDashes: 1, dashSpeed: 550, dashDuration: 0.6, dashCooldown: 7,
    hullWidth: 110, hullHeight: 45, hullLength: 140, mass: 15000,
  }
};

const LOADOUTS = {
  ION: {
    name: 'ION', className: 'Corvette MkII', chassis: 'CORVETTE',
    weapon: { name: 'Splitter Rifle', mode: 'hitscan', damage: 380, fireRate: 0.25, clipSize: 30, range: 3000, splash: 0, projSpeed: 0, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Laser Shot', cooldown: 10, duration: 0.5, desc: 'Massive beam: 2400 damage', type: 'offensive', dmg: 2400 },
      { name: 'Vortex Shield', cooldown: 0, duration: 999, desc: 'Hold to absorb and return projectiles', type: 'defensive' },
      { name: 'Trip Wire', cooldown: 12, duration: 12, desc: 'Proximity mines on contact', type: 'utility' },
    ],
    core: { name: 'Laser Core', desc: 'Continuous high-power laser', duration: 4, damage: 12000, cooldown: 60 },
  },
  SCORCH: {
    name: 'SCORCH', className: 'Dreadnought Incinerator', chassis: 'DREADNOUGHT',
    weapon: { name: 'T-203 Thermite', mode: 'projectile', damage: 900, fireRate: 1.2, clipSize: 12, range: 2500, splash: 300, projSpeed: 600, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Firewall', cooldown: 10, duration: 6, desc: 'Fire line: 400 DPS', type: 'offensive', dmg: 2400 },
      { name: 'Thermal Shield', cooldown: 0, duration: 999, desc: 'Hold to burn close enemies (drains shield HP)', type: 'defensive' },
      { name: 'Incendiary Trap', cooldown: 15, duration: 10, desc: 'Area denial fire', type: 'utility' },
    ],
    core: { name: 'Flame Core', desc: 'Massive AoE incendiary', duration: 2, damage: 9000, cooldown: 60 },
  },
  NORTHSTAR: {
    name: 'NORTHSTAR', className: 'Frigate Starcaster', chassis: 'FRIGATE',
    weapon: { name: 'Plasma Railgun', mode: 'hitscan', damage: 1000, fireRate: 1.5, clipSize: 6, range: 4500, splash: 50, projSpeed: 0, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Cluster Missile', cooldown: 8, duration: 0.3, desc: 'Impact 800 + 500 DPS for 5s', type: 'offensive', dmg: 3300 },
      { name: 'Afterburner', cooldown: 10, duration: 3, desc: 'Speed boost to 600', type: 'defensive' },
      { name: 'Tether Trap', cooldown: 12, duration: 4, desc: 'Slow and root enemies', type: 'utility' },
    ],
    core: { name: 'Afterburner Core', desc: 'Speed boost + rocket barrage', duration: 5, damage: 7000, cooldown: 60 },
  },
  RONIN: {
    name: 'RONIN', className: 'Frigate Blade', chassis: 'FRIGATE',
    weapon: { name: 'Leadwall', mode: 'spread', damage: 200, fireRate: 0.85, clipSize: 4, range: 900, splash: 0, projSpeed: 350, pellets: 8, spinup: 0 },
    abilities: [
      { name: 'Arc Wave', cooldown: 8, duration: 0.1, desc: 'Electric proj: 2000 damage', type: 'offensive', dmg: 2000 },
      { name: 'Sword Block', cooldown: 0, duration: 999, desc: 'Block 70% incoming (85% Sword Core)', type: 'defensive' },
      { name: 'Phase Dash', cooldown: 6, duration: 0.2, desc: 'Teleport dash', type: 'utility' },
    ],
    core: { name: 'Sword Core', desc: 'Empowered melee + arc waves', duration: 5, damage: 9000, cooldown: 60 },
  },
  TONE: {
    name: 'TONE', className: 'Corvette Tracker', chassis: 'CORVETTE',
    weapon: { name: '40mm Tracker', mode: 'projectile', damage: 660, fireRate: 0.6, clipSize: 20, range: 3500, splash: 0, projSpeed: 900, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Tracker Rockets', cooldown: 6, duration: 0.5, desc: 'Lock-on: 5 rockets (3 locks)', type: 'offensive', dmg: 5000 },
      { name: 'Particle Wall', cooldown: 14, duration: 0.1, desc: 'Deploy one-way shield (5000 HP, 10s)', type: 'defensive' },
      { name: 'Sonar Lock', cooldown: 12, duration: 8, desc: 'Reveal + partial lock (1 mark)', type: 'utility' },
    ],
    core: { name: 'Salvo Core', desc: 'Massive missile barrage', duration: 3, damage: 11000, cooldown: 60 },
  },
  LEGION: {
    name: 'LEGION', className: 'Dreadnought Siege', chassis: 'DREADNOUGHT',
    weapon: { name: 'Predator Cannon', mode: 'hitscan', damage: 85, fireRate: 0.05, clipSize: 150, range: 1500, splash: 0, projSpeed: 0, pellets: 1, spinup: 1.2, spread: 0.04 },
    abilities: [
      { name: 'Power Shot', cooldown: 8, duration: 0.1, desc: 'High-power: 3200 damage', type: 'offensive', dmg: 3200 },
      { name: 'Gun Shield', cooldown: 0, duration: 999, desc: 'Frontal shield (5000 HP, 10s)', type: 'defensive' },
      { name: 'Mode Switch', cooldown: 2, duration: 999, desc: 'Close/long range modes', type: 'utility' },
    ],
    core: { name: 'Smart Core', desc: 'Auto-aim + unlimited ammo', duration: 10, damage: 10000, cooldown: 60 },
  },
  MONARCH: {
    name: 'MONARCH', className: 'Corvette Sovereign', chassis: 'CORVETTE',
    weapon: { name: 'XO-16 Chaingun', mode: 'hitscan', damage: 240, fireRate: 0.09, clipSize: 40, range: 3000, splash: 0, projSpeed: 0, pellets: 1, spinup: 0.4 },
    abilities: [
      { name: 'Rocket Salvo', cooldown: 6, duration: 0.3, desc: '5 rockets (10 with Missile Racks)', type: 'offensive', dmg: 3500 },
      { name: 'Energy Siphon', cooldown: 8, duration: 2, desc: 'Drain shields: 800 heal', type: 'defensive' },
      { name: 'Rearm', cooldown: 12, duration: 0.1, desc: 'Reset ability cooldowns', type: 'utility' },
    ],
    core: { name: 'Upgrade Core', desc: '3 tiers of permanent upgrades', duration: 12, damage: 3000, cooldown: 60 },
  },
};

// Simple 3D vector math for server-side (no THREE.js dependency)
class Vec3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; }
  copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; }
  clone() { return new Vec3(this.x, this.y, this.z); }
  add(v) { this.x += v.x; this.y += v.y; this.z += v.z; return this; }
  sub(v) { this.x -= v.x; this.y -= v.y; this.z -= v.z; return this; }
  multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; return this; }
  length() { return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z); }
  lengthSq() { return this.x * this.x + this.y * this.y + this.z * this.z; }
  normalize() { const l = this.length(); if (l > 0) { this.x /= l; this.y /= l; this.z /= l; } return this; }
  dot(v) { return this.x * v.x + this.y * v.y + this.z * v.z; }
  cross(v) {
    const ax = this.x, ay = this.y, az = this.z;
    this.x = ay * v.z - az * v.y;
    this.y = az * v.x - ax * v.z;
    this.z = ax * v.y - ay * v.x;
    return this;
  }
  distanceTo(v) {
    const dx = this.x - v.x, dy = this.y - v.y, dz = this.z - v.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
  lerp(v, t) {
    this.x += (v.x - this.x) * t;
    this.y += (v.y - this.y) * t;
    this.z += (v.z - this.z) * t;
    return this;
  }
  clampScalar(min, max) {
    this.x = Math.max(min, Math.min(max, this.x));
    this.y = Math.max(min, Math.min(max, this.y));
    this.z = Math.max(min, Math.min(max, this.z));
    return this;
  }
  toJSON() { return { x: this.x, y: this.y, z: this.z }; }
  static fromJSON(j) { return new Vec3(j.x || 0, j.y || 0, j.z || 0); }
}

// Simple quaternion for server-side rotation
class Quat {
  constructor(x = 0, y = 0, z = 0, w = 1) { this.x = x; this.y = y; this.z = z; this.w = w; }
  clone() { return new Quat(this.x, this.y, this.z, this.w); }
  copy(q) { this.x = q.x; this.y = q.y; this.z = q.z; this.w = q.w; return this; }
  set(x, y, z, w) { this.x = x; this.y = y; this.z = z; this.w = w; return this; }

  setFromEuler(pitch, yaw, roll) {
    // YXZ order (matches THREE.js default for FPS)
    const c1 = Math.cos(yaw / 2), s1 = Math.sin(yaw / 2);
    const c2 = Math.cos(pitch / 2), s2 = Math.sin(pitch / 2);
    const c3 = Math.cos(roll / 2), s3 = Math.sin(roll / 2);
    this.x = s2 * c1 * c3 + c2 * s1 * s3;
    this.y = c2 * s1 * c3 - s2 * c1 * s3;
    this.z = c2 * c1 * s3 - s2 * s1 * c3;
    this.w = c2 * c1 * c3 + s2 * s1 * s3;
    return this;
  }

  // Apply quaternion to a Vec3
  applyToVec3(v) {
    const ix = this.w * v.x + this.y * v.z - this.z * v.y;
    const iy = this.w * v.y + this.z * v.x - this.x * v.z;
    const iz = this.w * v.z + this.x * v.y - this.y * v.x;
    const iw = -this.x * v.x - this.y * v.y - this.z * v.z;
    return new Vec3(
      ix * this.w + iw * -this.x + iy * -this.z - iz * -this.y,
      iy * this.w + iw * -this.y + iz * -this.x - ix * -this.z,
      iz * this.w + iw * -this.z + ix * -this.y - iy * -this.x
    );
  }

  slerp(q, t) {
    if (t === 0) return this;
    if (t === 1) return this.copy(q);
    let cosHalf = this.x * q.x + this.y * q.y + this.z * q.z + this.w * q.w;
    const qb = { x: q.x, y: q.y, z: q.z, w: q.w };
    if (cosHalf < 0) { qb.x = -q.x; qb.y = -q.y; qb.z = -q.z; qb.w = -q.w; cosHalf = -cosHalf; }
    if (cosHalf >= 1.0) return this;
    const sinHalf = Math.sqrt(1.0 - cosHalf * cosHalf);
    if (Math.abs(sinHalf) < 0.001) {
      this.x = 0.5 * (this.x + qb.x); this.y = 0.5 * (this.y + qb.y);
      this.z = 0.5 * (this.z + qb.z); this.w = 0.5 * (this.w + qb.w);
      return this;
    }
    const halfAngle = Math.atan2(sinHalf, cosHalf);
    const ra = Math.sin((1 - t) * halfAngle) / sinHalf;
    const rb = Math.sin(t * halfAngle) / sinHalf;
    this.x = this.x * ra + qb.x * rb; this.y = this.y * ra + qb.y * rb;
    this.z = this.z * ra + qb.z * rb; this.w = this.w * ra + qb.w * rb;
    return this;
  }

  toJSON() { return { x: this.x, y: this.y, z: this.z, w: this.w }; }
}

// Helper: get forward vector from quaternion
function getForward(quat) {
  return quat.applyToVec3(new Vec3(0, 0, -1));
}

function getRight(quat) {
  return quat.applyToVec3(new Vec3(1, 0, 0));
}

if (typeof module !== 'undefined') {
  module.exports = { LSS, CHASSIS, LOADOUTS, Vec3, Quat, getForward, getRight };
}
