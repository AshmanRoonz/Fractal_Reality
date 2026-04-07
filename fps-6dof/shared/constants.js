/**
 * LSS (Last Ship Sailing) - Game Constants
 * Shared between Node.js server and browser client.
 * Used for: match rules, chassis specs, loadout definitions.
 */

const SU = 150; // Ship Unit: Dreadnought hull + margin

const LSS = {
  MAX_PLAYERS_PER_MATCH: 10,  // 5v5
  TEAM_A: 'A',
  TEAM_B: 'B',
  ROUND_TIME: 180,            // seconds per round
  WARMUP_TIME: 5,             // seconds before match starts
  ROUNDS_TO_WIN: 4,           // first to 4 rounds wins
  SPAWN_PROTECTION: 3,        // seconds of invulnerability after spawn
  DOOMED_HEALTH_PCT: 0.15,    // health threshold for doomed state
  DOOMED_TIMER: 10,           // seconds until auto-kill when doomed
  TICK_RATE: 60,              // server game loop: 60 Hz
  NET_SEND_RATE: 20,          // state broadcast: 20 Hz (0.05s per frame)
  SU: SU,
};

const CHASSIS = {
  FRIGATE: {
    name: 'FRIGATE',
    maxHealth: 7500,
    maxShield: 2500,
    shieldRegenRate: 200,      // per second
    shieldRegenDelay: 5,       // seconds before regen starts
    flightSpeed: 450,          // forward
    strafeSpeed: 350,          // left/right
    verticalSpeed: 300,        // up/down
    acceleration: 1200,
    deceleration: 800,
    turnRate: 180,             // degrees/sec (yaw)
    pitchRate: 120,            // degrees/sec (pitch)
    maxDashes: 3,
    dashSpeed: 900,
    dashDuration: 0.4,
    dashCooldown: 4,
    hullWidth: 60,
    hullHeight: 25,
    hullLength: 80,
    mass: 5000,
    collRadius: 50,            // collision radius in game units
  },

  CORVETTE: {
    name: 'CORVETTE',
    maxHealth: 10000,
    maxShield: 3500,
    shieldRegenRate: 175,
    shieldRegenDelay: 6,
    flightSpeed: 350,
    strafeSpeed: 280,
    verticalSpeed: 250,
    acceleration: 800,
    deceleration: 600,
    turnRate: 140,
    pitchRate: 100,
    maxDashes: 2,
    dashSpeed: 750,
    dashDuration: 0.5,
    dashCooldown: 5,
    hullWidth: 80,
    hullHeight: 30,
    hullLength: 100,
    mass: 8000,
    collRadius: 65,
  },

  DREADNOUGHT: {
    name: 'DREADNOUGHT',
    maxHealth: 12500,
    maxShield: 5000,
    shieldRegenRate: 150,
    shieldRegenDelay: 8,
    flightSpeed: 250,
    strafeSpeed: 180,
    verticalSpeed: 160,
    acceleration: 500,
    deceleration: 400,
    turnRate: 100,
    pitchRate: 70,
    maxDashes: 1,
    dashSpeed: 550,
    dashDuration: 0.6,
    dashCooldown: 7,
    hullWidth: 110,
    hullHeight: 45,
    hullLength: 140,
    mass: 15000,
    collRadius: 90,
  },
};

const LOADOUTS = {
  ION: {
    name: 'ION',
    chassis: 'FRIGATE',
    weapon: {
      name: 'Splitter Rifle',
      type: 'hitscan',
      damage: 380,
      fireRate: 0.25,          // seconds between shots
      clipSize: 30,
      range: 3000,
    },
    abilities: [
      {
        name: 'Laser Shot',
        cooldown: 10,
        damage: 2400,
      },
      {
        name: 'Vortex Shield',
        cooldown: 0,            // activated, not cooldown-based
        holdable: true,
      },
      {
        name: 'Trip Wire',
        cooldown: 12,
        duration: 12,
      },
    ],
    core: {
      name: 'Laser Core',
      duration: 4,
      damage: 12000,
    },
  },

  SCORCH: {
    name: 'SCORCH',
    chassis: 'DREADNOUGHT',
    weapon: {
      name: 'T-203 Thermite',
      type: 'projectile',
      damage: 900,
      fireRate: 1.2,
      clipSize: 12,
      range: 2500,
      splashRadius: 300,
      projectileSpeed: 600,
    },
    abilities: [
      {
        name: 'Firewall',
        cooldown: 10,
        duration: 6,
        damage: 2400,
      },
      {
        name: 'Thermal Shield',
        cooldown: 0,
        holdable: true,
      },
      {
        name: 'Incendiary Trap',
        cooldown: 15,
        duration: 10,
      },
    ],
    core: {
      name: 'Flame Core',
      duration: 2,
      damage: 9000,
    },
  },

  NORTHSTAR: {
    name: 'NORTHSTAR',
    chassis: 'FRIGATE',
    weapon: {
      name: 'Plasma Railgun',
      type: 'hitscan',
      damage: 1000,
      fireRate: 1.5,
      clipSize: 6,
      range: 4500,
      splashRadius: 50,
    },
    abilities: [
      {
        name: 'Cluster Missile',
        cooldown: 8,
        duration: 0.3,
        damage: 3300,
      },
      {
        name: 'Afterburner',
        cooldown: 10,
        duration: 3,
      },
      {
        name: 'Tether Trap',
        cooldown: 12,
        duration: 4,
      },
    ],
    core: {
      name: 'Afterburner Core',
      duration: 5,
      damage: 7000,
    },
  },

  RONIN: {
    name: 'RONIN',
    chassis: 'FRIGATE',
    weapon: {
      name: 'Leadwall',
      type: 'spread',
      damage: 200,
      fireRate: 0.85,
      clipSize: 4,
      range: 900,
      projectileSpeed: 350,
      pellets: 8,
    },
    abilities: [
      {
        name: 'Arc Wave',
        cooldown: 8,
        damage: 2000,
      },
      {
        name: 'Sword Block',
        cooldown: 0,
        holdable: true,
        blockPercent: 0.70,
        coreBlockPercent: 0.85,
      },
      {
        name: 'Phase Dash',
        cooldown: 6,
        duration: 0.2,
      },
    ],
    core: {
      name: 'Sword Core',
      duration: 5,
      damage: 9000,
    },
  },

  TONE: {
    name: 'TONE',
    chassis: 'CORVETTE',
    weapon: {
      name: '40mm Tracker',
      type: 'projectile',
      damage: 660,
      fireRate: 0.6,
      clipSize: 20,
      range: 3500,
      projectileSpeed: 900,
    },
    abilities: [
      {
        name: 'Tracker Rockets',
        cooldown: 6,
        duration: 0.5,
        damage: 5000,
      },
      {
        name: 'Particle Wall',
        cooldown: 14,
        shieldHealth: 5000,
        duration: 10,
      },
      {
        name: 'Sonar Lock',
        cooldown: 12,
        duration: 8,
      },
    ],
    core: {
      name: 'Salvo Core',
      duration: 3,
      damage: 11000,
    },
  },

  LEGION: {
    name: 'LEGION',
    chassis: 'DREADNOUGHT',
    weapon: {
      name: 'Predator Cannon',
      type: 'hitscan',
      damage: 85,
      fireRate: 0.05,          // very slow fire rate, high RPM
      clipSize: 150,
      range: 1500,
      spinupTime: 1.2,
      spread: 0.04,
    },
    abilities: [
      {
        name: 'Power Shot',
        cooldown: 8,
        damage: 3200,
      },
      {
        name: 'Gun Shield',
        cooldown: 0,
        holdable: true,
        shieldHealth: 5000,
      },
      {
        name: 'Mode Switch',
        cooldown: 2,
      },
    ],
    core: {
      name: 'Smart Core',
      duration: 10,
      damage: 10000,
    },
  },

  MONARCH: {
    name: 'MONARCH',
    chassis: 'CORVETTE',
    weapon: {
      name: 'XO-16 Chaingun',
      type: 'hitscan',
      damage: 240,
      fireRate: 0.09,
      clipSize: 40,
      range: 3000,
      spinupTime: 0.4,
    },
    abilities: [
      {
        name: 'Rocket Salvo',
        cooldown: 6,
        duration: 0.3,
        damage: 3500,
      },
      {
        name: 'Energy Siphon',
        cooldown: 8,
        duration: 2,
        heal: 800,
      },
      {
        name: 'Rearm',
        cooldown: 12,
      },
    ],
    core: {
      name: 'Upgrade Core',
      duration: 12,
      damage: 3000,
      upgradeTiers: 3,
    },
  },
};

// Dual-environment export: CommonJS for Node, globalThis for browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LSS, CHASSIS, LOADOUTS, SU };
} else {
  window.LSS_SHARED = { LSS, CHASSIS, LOADOUTS, SU };
}
