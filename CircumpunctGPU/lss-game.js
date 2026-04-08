// ================================================================
// Last Ship Sailing: Game Logic
// Phase 1: Core flight + 6DOF movement
//
// Pure JavaScript game state. No rendering calls.
// Interfaces with CircumpunctGPU through the node buffer.
// ================================================================

const LSS = {
  // --- Constants ---
  ARENA_SIZE: 25000,
  TICK_RATE: 60,
  MAX_PLAYERS: 12,
  TEAM_A_COLOR: [1.0, 0.27, 0.27],  // red
  TEAM_B_COLOR: [0.27, 0.73, 0.27],  // green

  // Ship class definitions
  CLASSES: {
    ION:       { chassis: 'corvette',    hp: 2800, shield: 800,  speed: 280, accel: 420, name: 'ION' },
    SCORCH:    { chassis: 'dreadnought', hp: 4200, shield: 0,    speed: 180, accel: 260, name: 'SCORCH' },
    NORTHSTAR: { chassis: 'frigate',     hp: 2200, shield: 600,  speed: 340, accel: 520, name: 'NORTHSTAR' },
    RONIN:     { chassis: 'frigate',     hp: 2500, shield: 400,  speed: 320, accel: 480, name: 'RONIN' },
    TONE:      { chassis: 'corvette',    hp: 3000, shield: 600,  speed: 260, accel: 380, name: 'TONE' },
    LEGION:    { chassis: 'dreadnought', hp: 4500, shield: 0,    speed: 160, accel: 220, name: 'LEGION' },
    MONARCH:   { chassis: 'corvette',    hp: 3200, shield: 500,  speed: 250, accel: 360, name: 'MONARCH' },
  },

  // Chassis dimensions (CircNode hierarchy scale factors)
  CHASSIS: {
    frigate:     { hullW: 16, hullH: 8,  hullL: 40, baseScale: 40 },
    corvette:    { hullW: 22, hullH: 12, hullL: 36, baseScale: 50 },
    dreadnought: { hullW: 30, hullH: 16, hullL: 50, baseScale: 65 },
  },
};

// ================================================================
// QUATERNION MATH (6DOF requires quaternions, not Euler angles)
// ================================================================
const Quat = {
  identity() { return [0, 0, 0, 1]; },

  fromAxisAngle(axis, angle) {
    const ha = angle * 0.5;
    const s = Math.sin(ha);
    return [axis[0]*s, axis[1]*s, axis[2]*s, Math.cos(ha)];
  },

  multiply(a, b) {
    return [
      a[3]*b[0] + a[0]*b[3] + a[1]*b[2] - a[2]*b[1],
      a[3]*b[1] - a[0]*b[2] + a[1]*b[3] + a[2]*b[0],
      a[3]*b[2] + a[0]*b[1] - a[1]*b[0] + a[2]*b[3],
      a[3]*b[3] - a[0]*b[0] - a[1]*b[1] - a[2]*b[2],
    ];
  },

  normalize(q) {
    const l = Math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
    return l > 0 ? [q[0]/l, q[1]/l, q[2]/l, q[3]/l] : [0, 0, 0, 1];
  },

  rotateVec(q, v) {
    const [qx, qy, qz, qw] = q;
    const [vx, vy, vz] = v;
    // q * v * q^-1 (for unit quaternion, q^-1 = conjugate)
    const tx = 2 * (qy*vz - qz*vy);
    const ty = 2 * (qz*vx - qx*vz);
    const tz = 2 * (qx*vy - qy*vx);
    return [
      vx + qw*tx + qy*tz - qz*ty,
      vy + qw*ty + qz*tx - qx*tz,
      vz + qw*tz + qx*ty - qy*tx,
    ];
  },

  forward(q) { return Quat.rotateVec(q, [0, 0, -1]); },
  right(q)   { return Quat.rotateVec(q, [1, 0, 0]); },
  up(q)      { return Quat.rotateVec(q, [0, 1, 0]); },

  toMat4(q) {
    const [x, y, z, w] = q;
    const x2 = x+x, y2 = y+y, z2 = z+z;
    const xx = x*x2, xy = x*y2, xz = x*z2;
    const yy = y*y2, yz = y*z2, zz = z*z2;
    const wx = w*x2, wy = w*y2, wz = w*z2;
    return new Float32Array([
      1-yy-zz, xy+wz,   xz-wy,   0,
      xy-wz,   1-xx-zz, yz+wx,   0,
      xz+wy,   yz-wx,   1-xx-yy, 0,
      0,        0,        0,        1,
    ]);
  },
};

// ================================================================
// Vec3 helpers
// ================================================================
const Vec3 = {
  add(a, b) { return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]; },
  sub(a, b) { return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]; },
  scale(v, s) { return [v[0]*s, v[1]*s, v[2]*s]; },
  length(v) { return Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]); },
  normalize(v) {
    const l = Vec3.length(v);
    return l > 0 ? [v[0]/l, v[1]/l, v[2]/l] : [0, 0, 0];
  },
  dot(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; },
  lerp(a, b, t) { return [a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t]; },
};

// ================================================================
// INPUT SYSTEM (6DOF)
// ================================================================
class InputSystem {
  constructor() {
    this.keys = {};
    this.mouseDX = 0;
    this.mouseDY = 0;
    this.mouseButtons = {};
    this.locked = false;

    document.addEventListener('keydown', e => { this.keys[e.code] = true; });
    document.addEventListener('keyup', e => { this.keys[e.code] = false; });
    document.addEventListener('mousemove', e => {
      if (!this.locked) return;
      this.mouseDX += e.movementX;
      this.mouseDY += e.movementY;
    });
    document.addEventListener('mousedown', e => { this.mouseButtons[e.button] = true; });
    document.addEventListener('mouseup', e => { this.mouseButtons[e.button] = false; });
  }

  requestLock(canvas) {
    canvas.addEventListener('click', () => {
      canvas.requestPointerLock();
    });
    document.addEventListener('pointerlockchange', () => {
      this.locked = !!document.pointerLockElement;
    });
  }

  consumeMouse() {
    const dx = this.mouseDX;
    const dy = this.mouseDY;
    this.mouseDX = 0;
    this.mouseDY = 0;
    return { dx, dy };
  }

  key(code) { return !!this.keys[code]; }
  mouse(button) { return !!this.mouseButtons[button]; }
}

// ================================================================
// PLAYER ENTITY
// ================================================================
class Player {
  constructor(shipClass = 'NORTHSTAR', team = 0) {
    const cls = LSS.CLASSES[shipClass];
    const chassis = LSS.CHASSIS[cls.chassis];

    this.shipClass = shipClass;
    this.team = team;
    this.chassisType = cls.chassis;

    // Health
    this.health = cls.hp;
    this.maxHealth = cls.hp;
    this.shield = cls.shield;
    this.maxShield = cls.shield;
    this.alive = true;

    // Transform (6DOF)
    this.position = [0, 0, 0];
    this.rotation = Quat.identity();
    this.velocity = [0, 0, 0];

    // Movement params
    this.maxSpeed = cls.speed;
    this.accel = cls.accel;
    this.friction = 0.92;
    this.pitchSpeed = 2.5;
    this.yawSpeed = 2.5;
    this.rollSpeed = 3.0;

    // Combat
    this.isFiring = false;
    this.fireTimer = 0;
    this.muzzleFlashTimer = 0;

    // Abilities
    this.abilityCooldowns = [0, 0, 0];
    this.abilityActive = [false, false, false];
    this.coreMeter = 0;

    // CircNode indices (set by renderer)
    this.rootNodeIdx = -1;
    this.childNodeIndices = [];

    // Ship visual scale
    this.baseScale = chassis.baseScale;
  }

  update(dt, input) {
    if (!this.alive) return;

    // --- ROTATION (mouse + keyboard roll) ---
    const mouse = input.consumeMouse();
    const sensitivity = 0.002;

    // Pitch (mouse Y)
    if (mouse.dy !== 0) {
      const pitchQ = Quat.fromAxisAngle(
        Quat.right(this.rotation),
        -mouse.dy * sensitivity * this.pitchSpeed
      );
      this.rotation = Quat.normalize(Quat.multiply(pitchQ, this.rotation));
    }

    // Yaw (mouse X)
    if (mouse.dx !== 0) {
      const yawQ = Quat.fromAxisAngle(
        Quat.up(this.rotation),
        -mouse.dx * sensitivity * this.yawSpeed
      );
      this.rotation = Quat.normalize(Quat.multiply(yawQ, this.rotation));
    }

    // Roll (Q/E)
    let rollInput = 0;
    if (input.key('KeyQ')) rollInput -= 1;
    if (input.key('KeyE')) rollInput += 1;
    if (rollInput !== 0) {
      const rollQ = Quat.fromAxisAngle(
        Quat.forward(this.rotation),
        rollInput * dt * this.rollSpeed
      );
      this.rotation = Quat.normalize(Quat.multiply(rollQ, this.rotation));
    }

    // --- TRANSLATION (6DOF thrust) ---
    const fwd = Quat.forward(this.rotation);
    const right = Quat.right(this.rotation);
    const up = Quat.up(this.rotation);

    let thrustDir = [0, 0, 0];
    if (input.key('KeyW')) thrustDir = Vec3.add(thrustDir, fwd);
    if (input.key('KeyS')) thrustDir = Vec3.add(thrustDir, Vec3.scale(fwd, -1));
    if (input.key('KeyD')) thrustDir = Vec3.add(thrustDir, right);
    if (input.key('KeyA')) thrustDir = Vec3.add(thrustDir, Vec3.scale(right, -1));
    if (input.key('Space')) thrustDir = Vec3.add(thrustDir, up);
    if (input.key('ControlLeft') || input.key('ShiftLeft')) {
      thrustDir = Vec3.add(thrustDir, Vec3.scale(up, -1));
    }

    // Shift for boost
    const boost = input.key('ShiftLeft') ? 1.5 : 1.0;

    if (Vec3.length(thrustDir) > 0.01) {
      thrustDir = Vec3.normalize(thrustDir);
      this.velocity = Vec3.add(
        this.velocity,
        Vec3.scale(thrustDir, this.accel * boost * dt)
      );
    }

    // Speed cap
    const speed = Vec3.length(this.velocity);
    if (speed > this.maxSpeed * boost) {
      this.velocity = Vec3.scale(
        Vec3.normalize(this.velocity),
        this.maxSpeed * boost
      );
    }

    // Friction
    this.velocity = Vec3.scale(this.velocity, Math.pow(this.friction, dt * 60));

    // Apply velocity
    this.position = Vec3.add(this.position, Vec3.scale(this.velocity, dt));

    // Arena boundary (soft bounce)
    const half = LSS.ARENA_SIZE * 0.5;
    for (let i = 0; i < 3; i++) {
      if (Math.abs(this.position[i]) > half) {
        this.position[i] = Math.sign(this.position[i]) * half;
        this.velocity[i] *= -0.5;
      }
    }

    // --- FIRING ---
    this.isFiring = input.mouse(0);
    this.fireTimer -= dt;
    this.muzzleFlashTimer = Math.max(0, this.muzzleFlashTimer - dt);

    // Ability cooldowns
    for (let i = 0; i < 3; i++) {
      this.abilityCooldowns[i] = Math.max(0, this.abilityCooldowns[i] - dt);
    }

    // Core meter builds over time
    this.coreMeter = Math.min(100, this.coreMeter + dt * 2);
  }

  // Get the current speed as fraction of max
  get speedFraction() {
    return Vec3.length(this.velocity) / this.maxSpeed;
  }
}

// ================================================================
// GAME STATE
// ================================================================
class GameState {
  constructor() {
    this.player = null;
    this.entities = [];   // all ships (player + bots)
    this.projectiles = [];
    this.particles = [];
    this.time = 0;
    this.roundTimer = 300; // 5 minute rounds
    this.scores = [0, 0];
    this.paused = false;
  }

  init(shipClass) {
    this.player = new Player(shipClass, 0);
    this.player.position = [0, 200, 500];
    this.entities = [this.player];
  }

  update(dt, input) {
    if (this.paused) return;
    this.time += dt;
    this.roundTimer -= dt;

    // Update player
    this.player.update(dt, input);

    // Update other entities
    for (let i = 1; i < this.entities.length; i++) {
      // Bot AI would go here
    }

    // Update projectiles
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const p = this.projectiles[i];
      p.position = Vec3.add(p.position, Vec3.scale(p.velocity, dt));
      p.life -= dt;
      if (p.life <= 0) {
        this.projectiles.splice(i, 1);
      }
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.position = Vec3.add(p.position, Vec3.scale(p.velocity, dt));
      p.life -= dt;
      p.velocity = Vec3.scale(p.velocity, 0.98);
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }
}

// ================================================================
// EXPORT
// ================================================================
if (typeof window !== 'undefined') {
  window.LSS = LSS;
  window.Quat = Quat;
  window.Vec3 = Vec3;
  window.InputSystem = InputSystem;
  window.Player = Player;
  window.GameState = GameState;
}
