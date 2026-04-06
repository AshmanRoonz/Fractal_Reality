/**
 * FPS-6DOF Server
 * Server-authoritative multiplayer with 6 degrees of freedom physics.
 * WebSocket + Express. No engine, just math.
 */

const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

app.use(express.static(path.join(__dirname, 'public')));

// ─── CONFIG ───────────────────────────────────────────────────────
const TICK_RATE = 60;
const DT = 1 / TICK_RATE;
const ARENA = { x: 80, y: 60, z: 80 };          // half-extents
const THRUST = 40;
const TORQUE = 3.5;
const LINEAR_DRAG = 0.97;
const ANGULAR_DRAG = 0.93;
const PROJECTILE_SPEED = 120;
const PROJECTILE_LIFETIME = 3;                    // seconds
const FIRE_COOLDOWN = 0.15;                       // seconds
const MAX_HP = 100;
const PROJECTILE_DAMAGE = 15;
const RESPAWN_TIME = 3;

// ─── STATE ────────────────────────────────────────────────────────
const players = new Map();
const projectiles = [];
let nextProjectileId = 0;

function spawnPosition() {
  return {
    x: (Math.random() - 0.5) * ARENA.x,
    y: (Math.random() - 0.5) * ARENA.y,
    z: (Math.random() - 0.5) * ARENA.z
  };
}

function createPlayer(id) {
  const pos = spawnPosition();
  return {
    id,
    pos,
    vel: { x: 0, y: 0, z: 0 },
    quat: { x: 0, y: 0, z: 0, w: 1 },
    angVel: { x: 0, y: 0, z: 0 },
    input: { thrust: { x: 0, y: 0, z: 0 }, torque: { x: 0, y: 0, z: 0 }, fire: false },
    fireCooldown: 0,
    hp: MAX_HP,
    kills: 0,
    deaths: 0,
    dead: false,
    respawnTimer: 0,
    color: `hsl(${Math.random() * 360}, 80%, 60%)`
  };
}

// ─── QUATERNION MATH ──────────────────────────────────────────────
function quatMultiply(a, b) {
  return {
    x: a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
    y: a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
    z: a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
    w: a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z
  };
}

function quatNormalize(q) {
  const len = Math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w);
  if (len < 0.0001) return { x: 0, y: 0, z: 0, w: 1 };
  return { x: q.x / len, y: q.y / len, z: q.z / len, w: q.w / len };
}

function quatFromAngVel(av, dt) {
  const angle = Math.sqrt(av.x * av.x + av.y * av.y + av.z * av.z) * dt;
  if (angle < 0.00001) return { x: 0, y: 0, z: 0, w: 1 };
  const ha = angle / 2;
  const s = Math.sin(ha) / (angle / dt);
  return quatNormalize({
    x: av.x * s * dt / 2,
    y: av.y * s * dt / 2,
    z: av.z * s * dt / 2,
    w: Math.cos(ha)
  });
}

// Rotate a vector by a quaternion
function quatRotate(q, v) {
  const ix = q.w * v.x + q.y * v.z - q.z * v.y;
  const iy = q.w * v.y + q.z * v.x - q.x * v.z;
  const iz = q.w * v.z + q.x * v.y - q.y * v.x;
  const iw = -q.x * v.x - q.y * v.y - q.z * v.z;
  return {
    x: ix * q.w + iw * -q.x + iy * -q.z - iz * -q.y,
    y: iy * q.w + iw * -q.y + iz * -q.x - ix * -q.z,
    z: iz * q.w + iw * -q.z + ix * -q.y - iy * -q.x
  };
}

// ─── PHYSICS TICK ─────────────────────────────────────────────────
function tick() {
  // Update players
  for (const p of players.values()) {
    if (p.dead) {
      p.respawnTimer -= DT;
      if (p.respawnTimer <= 0) {
        p.dead = false;
        p.hp = MAX_HP;
        const sp = spawnPosition();
        p.pos = sp;
        p.vel = { x: 0, y: 0, z: 0 };
        p.angVel = { x: 0, y: 0, z: 0 };
        p.quat = { x: 0, y: 0, z: 0, w: 1 };
      }
      continue;
    }

    const inp = p.input;

    // Apply thrust in local space (convert to world)
    const localThrust = {
      x: inp.thrust.x * THRUST,
      y: inp.thrust.y * THRUST,
      z: inp.thrust.z * THRUST
    };
    const worldThrust = quatRotate(p.quat, localThrust);
    p.vel.x += worldThrust.x * DT;
    p.vel.y += worldThrust.y * DT;
    p.vel.z += worldThrust.z * DT;

    // Apply torque (local space angular acceleration)
    p.angVel.x += inp.torque.x * TORQUE * DT;
    p.angVel.y += inp.torque.y * TORQUE * DT;
    p.angVel.z += inp.torque.z * TORQUE * DT;

    // Drag
    p.vel.x *= LINEAR_DRAG;
    p.vel.y *= LINEAR_DRAG;
    p.vel.z *= LINEAR_DRAG;
    p.angVel.x *= ANGULAR_DRAG;
    p.angVel.y *= ANGULAR_DRAG;
    p.angVel.z *= ANGULAR_DRAG;

    // Integrate position
    p.pos.x += p.vel.x * DT;
    p.pos.y += p.vel.y * DT;
    p.pos.z += p.vel.z * DT;

    // Integrate rotation
    const dq = quatFromAngVel(p.angVel, DT);
    p.quat = quatNormalize(quatMultiply(dq, p.quat));

    // Arena bounds (bounce)
    ['x', 'y', 'z'].forEach((axis, i) => {
      const ext = [ARENA.x, ARENA.y, ARENA.z][i] / 2;
      if (p.pos[axis] > ext)  { p.pos[axis] = ext;  p.vel[axis] *= -0.5; }
      if (p.pos[axis] < -ext) { p.pos[axis] = -ext; p.vel[axis] *= -0.5; }
    });

    // Firing
    p.fireCooldown = Math.max(0, p.fireCooldown - DT);
    if (inp.fire && p.fireCooldown <= 0) {
      p.fireCooldown = FIRE_COOLDOWN;
      const forward = quatRotate(p.quat, { x: 0, y: 0, z: -1 });
      projectiles.push({
        id: nextProjectileId++,
        owner: p.id,
        pos: { x: p.pos.x + forward.x * 2, y: p.pos.y + forward.y * 2, z: p.pos.z + forward.z * 2 },
        vel: {
          x: forward.x * PROJECTILE_SPEED + p.vel.x,
          y: forward.y * PROJECTILE_SPEED + p.vel.y,
          z: forward.z * PROJECTILE_SPEED + p.vel.z
        },
        life: PROJECTILE_LIFETIME,
        color: p.color
      });
    }
  }

  // Update projectiles
  for (let i = projectiles.length - 1; i >= 0; i--) {
    const proj = projectiles[i];
    proj.pos.x += proj.vel.x * DT;
    proj.pos.y += proj.vel.y * DT;
    proj.pos.z += proj.vel.z * DT;
    proj.life -= DT;

    // Check bounds
    if (Math.abs(proj.pos.x) > ARENA.x / 2 ||
        Math.abs(proj.pos.y) > ARENA.y / 2 ||
        Math.abs(proj.pos.z) > ARENA.z / 2 ||
        proj.life <= 0) {
      projectiles.splice(i, 1);
      continue;
    }

    // Hit detection (sphere vs sphere, radius 1.5 for players, 0.3 for projectiles)
    for (const p of players.values()) {
      if (p.id === proj.owner || p.dead) continue;
      const dx = p.pos.x - proj.pos.x;
      const dy = p.pos.y - proj.pos.y;
      const dz = p.pos.z - proj.pos.z;
      const distSq = dx * dx + dy * dy + dz * dz;
      if (distSq < (1.5 + 0.3) ** 2) {
        // Hit!
        p.hp -= PROJECTILE_DAMAGE;
        projectiles.splice(i, 1);
        if (p.hp <= 0) {
          p.dead = true;
          p.respawnTimer = RESPAWN_TIME;
          p.deaths++;
          const shooter = players.get(proj.owner);
          if (shooter) shooter.kills++;
        }
        break;
      }
    }
  }

  // Broadcast state
  const state = {
    type: 'state',
    players: Array.from(players.values()).map(p => ({
      id: p.id,
      pos: p.pos,
      quat: p.quat,
      vel: p.vel,
      hp: p.hp,
      kills: p.kills,
      deaths: p.deaths,
      dead: p.dead,
      color: p.color
    })),
    projectiles: projectiles.map(pr => ({
      id: pr.id,
      pos: pr.pos,
      color: pr.color
    }))
  };

  const msg = JSON.stringify(state);
  wss.clients.forEach(client => {
    if (client.readyState === 1) client.send(msg);
  });
}

// ─── CONNECTIONS ──────────────────────────────────────────────────
let nextPlayerId = 1;

wss.on('connection', (ws) => {
  const id = 'p' + nextPlayerId++;
  const player = createPlayer(id);
  players.set(id, player);
  console.log(`${id} connected (${players.size} players)`);

  ws.send(JSON.stringify({ type: 'welcome', id, arena: ARENA }));

  ws.on('message', (raw) => {
    try {
      const msg = JSON.parse(raw);
      if (msg.type === 'input') {
        player.input = msg.input;
      }
    } catch(e) {}
  });

  ws.on('close', () => {
    players.delete(id);
    console.log(`${id} disconnected (${players.size} players)`);
  });
});

// ─── START ────────────────────────────────────────────────────────
setInterval(tick, 1000 / TICK_RATE);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`\n  6DOF FPS server running on http://localhost:${PORT}\n`);
  console.log(`  Open multiple tabs to test multiplayer.`);
  console.log(`  Gamepad: plug in and press any button to activate.\n`);
});
