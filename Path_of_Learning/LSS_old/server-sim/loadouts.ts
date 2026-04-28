/*
  LSS server-sim ; loadouts + chassis (v8.4)

  Pure-data port of LOADOUTS + CHASSIS from the original LSS frontend.
  Chassis stats drive movement (accel, max speed, dashes), survivability
  (HP, shield), and weapon-class baseline. Loadout adds the specific
  weapon profile + ability list.

  v8.4 uses chassis + weapon stats; abilities are listed but not yet
  implemented in tick() (v8.5+ ports them one loadout at a time).
*/

export interface ChassisStats {
  name: string;
  maxHealth: number;
  maxShield: number;
  shieldRegenRate: number;
  shieldRegenDelay: number;
  flightSpeed: number;       // top-speed cap (units/s)
  acceleration: number;       // units/s^2
  maxDashes: number;
  dashSpeed: number;
  dashDuration: number;
  dashCooldown: number;
  hullLength: number;
  mass: number;
}

export interface WeaponStats {
  name: string;
  mode: 'hitscan' | 'projectile' | 'spread';
  damage: number;
  fireRate: number;          // seconds between shots
  clipSize: number;
  range: number;
  splash: number;
  projSpeed: number;
  pellets: number;
  spinup: number;
  spread?: number;
}

export interface AbilityDef {
  name: string;
  cooldown: number;
  duration: number;
  desc: string;
  type: 'offensive' | 'defensive' | 'utility';
  dmg?: number;
}

export interface LoadoutDef {
  name: string;             // 'VORTEX', 'PYRO', etc.
  className: string;        // human-readable subtitle
  chassis: ChassisKey;
  weapon: WeaponStats;
  abilities: AbilityDef[];   // up to 3
  core: { name: string; desc: string; duration: number; damage: number; cooldown: number };
}

export type ChassisKey = 'FRIGATE' | 'CORVETTE' | 'DREADNOUGHT';
export type LoadoutKey = 'VORTEX' | 'PYRO' | 'PUNCTURE' | 'SLAYER' | 'TRACKER' | 'BLASTER' | 'SYPHON';

export const CHASSIS: Record<ChassisKey, ChassisStats> = {
  FRIGATE: {
    name: 'Frigate', maxHealth: 7500, maxShield: 2500,
    shieldRegenRate: 200, shieldRegenDelay: 5,
    flightSpeed: 800, acceleration: 1800,
    maxDashes: 3, dashSpeed: 1500, dashDuration: 0.4, dashCooldown: 4,
    hullLength: 80, mass: 5000,
  },
  CORVETTE: {
    name: 'Corvette', maxHealth: 10000, maxShield: 3500,
    shieldRegenRate: 175, shieldRegenDelay: 6,
    flightSpeed: 600, acceleration: 1400,
    maxDashes: 2, dashSpeed: 1200, dashDuration: 0.5, dashCooldown: 5,
    hullLength: 100, mass: 8000,
  },
  DREADNOUGHT: {
    name: 'Dreadnought', maxHealth: 12500, maxShield: 5000,
    shieldRegenRate: 150, shieldRegenDelay: 8,
    flightSpeed: 420, acceleration: 900,
    maxDashes: 1, dashSpeed: 850, dashDuration: 0.6, dashCooldown: 7,
    hullLength: 140, mass: 15000,
  },
};

export const LOADOUTS: Record<LoadoutKey, LoadoutDef> = {
  VORTEX: {
    name: 'VORTEX', className: 'Corvette MkII', chassis: 'CORVETTE',
    weapon: { name: 'Splitter Rifle', mode: 'hitscan', damage: 380, fireRate: 0.25, clipSize: 30, range: 3000, splash: 0, projSpeed: 0, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Laser Shot', cooldown: 10, duration: 0.5, desc: 'Massive beam: 2400 damage', type: 'offensive', dmg: 2400 },
      { name: 'Vortex Shield', cooldown: 0, duration: 999, desc: 'Hold to absorb and return projectiles', type: 'defensive' },
      { name: 'Trip Wire', cooldown: 12, duration: 12, desc: 'Proximity mines on contact', type: 'utility' },
    ],
    core: { name: 'Laser Core', desc: 'Continuous high-power laser', duration: 4, damage: 12000, cooldown: 60 },
  },
  PYRO: {
    name: 'PYRO', className: 'Dreadnought Incinerator', chassis: 'DREADNOUGHT',
    weapon: { name: 'T-203 Thermite', mode: 'projectile', damage: 900, fireRate: 1.2, clipSize: 12, range: 2500, splash: 300, projSpeed: 600, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Firewall', cooldown: 10, duration: 6, desc: 'Fire line: 400 DPS', type: 'offensive', dmg: 2400 },
      { name: 'Thermal Shield', cooldown: 0, duration: 5, desc: 'Hold up to 5s; blocks attacks', type: 'defensive' },
      { name: 'Incendiary Trap', cooldown: 15, duration: 10, desc: 'Area denial fire', type: 'utility' },
    ],
    core: { name: 'Flame Core', desc: 'Massive AoE incendiary', duration: 2, damage: 9000, cooldown: 60 },
  },
  PUNCTURE: {
    name: 'PUNCTURE', className: 'Frigate Starcaster', chassis: 'FRIGATE',
    weapon: { name: 'Plasma Railgun', mode: 'hitscan', damage: 1000, fireRate: 1.5, clipSize: 6, range: 4500, splash: 50, projSpeed: 0, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Cluster Missile', cooldown: 8, duration: 0.3, desc: 'Impact 800 + 500 DPS for 5s', type: 'offensive', dmg: 3300 },
      { name: 'Afterburner', cooldown: 10, duration: 3, desc: 'Speed boost', type: 'defensive' },
      { name: 'Tether Trap', cooldown: 12, duration: 4, desc: 'Slow and root enemies', type: 'utility' },
    ],
    core: { name: 'Afterburner Core', desc: 'Speed boost + rocket barrage', duration: 5, damage: 7000, cooldown: 60 },
  },
  SLAYER: {
    name: 'SLAYER', className: 'Frigate Blade', chassis: 'FRIGATE',
    weapon: { name: 'Leadwall', mode: 'spread', damage: 200, fireRate: 0.85, clipSize: 4, range: 900, splash: 0, projSpeed: 350, pellets: 8, spinup: 0 },
    abilities: [
      { name: 'Arc Wave', cooldown: 8, duration: 0.1, desc: 'Electric proj: 2000 damage', type: 'offensive', dmg: 2000 },
      { name: 'Sword Block', cooldown: 0, duration: 999, desc: 'Block 70% incoming', type: 'defensive' },
      { name: 'Phase Dash', cooldown: 6, duration: 0.2, desc: 'Teleport dash', type: 'utility' },
    ],
    core: { name: 'Sword Core', desc: 'Empowered melee + arc waves', duration: 5, damage: 9000, cooldown: 60 },
  },
  TRACKER: {
    name: 'TRACKER', className: 'Corvette Tracker', chassis: 'CORVETTE',
    weapon: { name: '40mm Tracker', mode: 'projectile', damage: 660, fireRate: 0.6, clipSize: 20, range: 3500, splash: 0, projSpeed: 900, pellets: 1, spinup: 0 },
    abilities: [
      { name: 'Tracker Rockets', cooldown: 6, duration: 0.5, desc: 'Lock-on rockets', type: 'offensive', dmg: 5000 },
      { name: 'Particle Wall', cooldown: 14, duration: 0.1, desc: 'One-way shield', type: 'defensive' },
      { name: 'Sonar Lock', cooldown: 12, duration: 8, desc: 'Reveal + partial lock', type: 'utility' },
    ],
    core: { name: 'Salvo Core', desc: 'Massive missile barrage', duration: 3, damage: 11000, cooldown: 60 },
  },
  BLASTER: {
    name: 'BLASTER', className: 'Dreadnought Siege', chassis: 'DREADNOUGHT',
    weapon: { name: 'Predator Cannon', mode: 'hitscan', damage: 85, fireRate: 0.05, clipSize: 150, range: 1500, splash: 0, projSpeed: 0, pellets: 1, spinup: 1.2, spread: 0.04 },
    abilities: [
      { name: 'Power Shot', cooldown: 8, duration: 0.1, desc: 'High-power: 3200 damage', type: 'offensive', dmg: 3200 },
      { name: 'Gun Shield', cooldown: 0, duration: 999, desc: 'Frontal shield', type: 'defensive' },
      { name: 'Mode Switch', cooldown: 2, duration: 999, desc: 'Close/long range', type: 'utility' },
    ],
    core: { name: 'Smart Core', desc: 'Auto-aim + unlimited ammo', duration: 10, damage: 10000, cooldown: 60 },
  },
  SYPHON: {
    name: 'SYPHON', className: 'Corvette Sovereign', chassis: 'CORVETTE',
    weapon: { name: 'XO-16 Chaingun', mode: 'hitscan', damage: 240, fireRate: 0.09, clipSize: 40, range: 3000, splash: 0, projSpeed: 0, pellets: 1, spinup: 0.4 },
    abilities: [
      { name: 'Rocket Salvo', cooldown: 6, duration: 0.3, desc: '5 rockets', type: 'offensive', dmg: 3500 },
      { name: 'Energy Siphon', cooldown: 8, duration: 2, desc: 'Drain shields: 800 heal', type: 'defensive' },
      { name: 'Rearm', cooldown: 12, duration: 0.1, desc: 'Reset cooldowns', type: 'utility' },
    ],
    core: { name: 'Upgrade Core', desc: '3 tiers of permanent upgrades', duration: 12, damage: 3000, cooldown: 60 },
  },
};

export const LOADOUT_KEYS: LoadoutKey[] = ['VORTEX', 'PYRO', 'PUNCTURE', 'SLAYER', 'TRACKER', 'BLASTER', 'SYPHON'];
export const DEFAULT_LOADOUT: LoadoutKey = 'TRACKER';

export function getLoadout(key: string | null | undefined): LoadoutDef {
  if (key && (key in LOADOUTS)) return LOADOUTS[key as LoadoutKey];
  return LOADOUTS[DEFAULT_LOADOUT];
}

export function getChassis(key: string | null | undefined): ChassisStats {
  if (key && (key in CHASSIS)) return CHASSIS[key as ChassisKey];
  return CHASSIS.CORVETTE;
}
