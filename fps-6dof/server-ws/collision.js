// ============================================================================
// LAST SHIP SAILING ; Level Geometry & Collision System
// SDF-based collision for 6DOF space combat
// ============================================================================

'use strict';

const { Vec3 } = require('./shared');

// ============================================================================
// MAP DATA & CONSTANTS
// ============================================================================

const SU = 150; // Scale unit for level geometry

const MAP_DATA = {
  circumpunct: {
    name: 'The Circumpunct',
    rooms: [
      { id: 'center', team: null, x: 0, y: 0, z: 0, r: SU * 3.5 },
      { id: 'spawn_a', team: 'A', x: -SU * 9, y: 0, z: -SU * 4, r: SU * 2.5 },
      { id: 'spawn_b', team: 'B', x: SU * 9, y: 0, z: -SU * 4, r: SU * 2.5 },
      { id: 'ready_a', team: null, x: -SU * 5, y: 0, z: SU * 7, r: SU * 2.5 },
      { id: 'ready_b', team: null, x: SU * 5, y: 0, z: SU * 7, r: SU * 2.5 },
    ],
    tunnels: [
      { path: [{x:-SU*9,y:0,z:-SU*4},{x:-SU*7,y:0,z:SU*2},{x:-SU*3,y:0,z:SU*3},{x:0,y:0,z:0}]},
      { path: [{x:SU*9,y:0,z:-SU*4},{x:SU*7,y:0,z:SU*2},{x:SU*3,y:0,z:SU*3},{x:0,y:0,z:0}]},
      { path: [{x:-SU*9,y:0,z:-SU*4},{x:-SU*5,y:0,z:SU*7}]},
      { path: [{x:SU*9,y:0,z:-SU*4},{x:SU*5,y:0,z:SU*7}]},
      { path: [{x:-SU*5,y:SU*1.2,z:SU*7},{x:SU*5,y:SU*1.2,z:SU*7}]},
      { path: [{x:-SU*5,y:-SU*1.2,z:SU*7},{x:SU*5,y:-SU*1.2,z:SU*7}]},
      { path: [{x:-SU*5,y:0,z:SU*7},{x:0,y:0,z:0}]},
      { path: [{x:SU*5,y:0,z:SU*7},{x:0,y:0,z:0}]},
    ]
  },
  hourglass: {
    name: 'The Nexus',
    rooms: [
      { id: 'center', team: null, x: 0, y: 0, z: 0, r: SU * 2.5 },
      { id: 'spawn_a', team: 'A', x: 0, y: 0, z: -SU * 8, r: SU * 2.2 },
      { id: 'ne', team: null, x: SU * 7, y: SU * 2, z: -SU * 4, r: SU * 1.8 },
      { id: 'se', team: null, x: SU * 7, y: -SU * 2, z: SU * 4, r: SU * 1.8 },
      { id: 'spawn_b', team: 'B', x: 0, y: 0, z: SU * 8, r: SU * 2.2 },
      { id: 'sw', team: null, x: -SU * 7, y: -SU * 2, z: SU * 4, r: SU * 1.8 },
      { id: 'nw', team: null, x: -SU * 7, y: SU * 2, z: -SU * 4, r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{x:0,y:0,z:-SU*8},{x:SU*7,y:SU*2,z:-SU*4}]},
      { path: [{x:SU*7,y:SU*2,z:-SU*4},{x:SU*7,y:-SU*2,z:SU*4}]},
      { path: [{x:SU*7,y:-SU*2,z:SU*4},{x:0,y:0,z:SU*8}]},
      { path: [{x:0,y:0,z:SU*8},{x:-SU*7,y:-SU*2,z:SU*4}]},
      { path: [{x:-SU*7,y:-SU*2,z:SU*4},{x:-SU*7,y:SU*2,z:-SU*4}]},
      { path: [{x:-SU*7,y:SU*2,z:-SU*4},{x:0,y:0,z:-SU*8}]},
      { path: [{x:0,y:0,z:-SU*8},{x:0,y:0,z:0}]},
      { path: [{x:SU*7,y:SU*2,z:-SU*4},{x:0,y:0,z:0}]},
      { path: [{x:SU*7,y:-SU*2,z:SU*4},{x:0,y:0,z:0}]},
      { path: [{x:0,y:0,z:SU*8},{x:0,y:0,z:0}]},
      { path: [{x:-SU*7,y:-SU*2,z:SU*4},{x:0,y:0,z:0}]},
      { path: [{x:-SU*7,y:SU*2,z:-SU*4},{x:0,y:0,z:0}]},
    ]
  },
};

// ============================================================================
// SDF PRIMITIVE FUNCTIONS (using raw coordinates, not Vec3 for speed)
// ============================================================================

function sdSphere(px, py, pz, cx, cy, cz, r) {
  const dx = px - cx, dy = py - cy, dz = pz - cz;
  return Math.sqrt(dx*dx + dy*dy + dz*dz) - r;
}

function sdCylinder(px, py, pz, ax, ay, az, bx, by, bz, r) {
  const bax = bx - ax, bay = by - ay, baz = bz - az;
  const pax = px - ax, pay = py - ay, paz = pz - az;
  const baLen2 = bax*bax + bay*bay + baz*baz;

  if (baLen2 < 0.001) return sdSphere(px, py, pz, ax, ay, az, r);

  const t = Math.max(0, Math.min(1, (pax*bax + pay*bay + paz*baz) / baLen2));
  const cx2 = ax + bax*t, cy2 = ay + bay*t, cz2 = az + baz*t;
  const dx = px - cx2, dy = py - cy2, dz = pz - cz2;
  const perpDist = Math.sqrt(dx*dx + dy*dy + dz*dz);
  const baLen = Math.sqrt(baLen2);
  const axialFromMid = Math.abs(t - 0.5) * baLen;
  const halfLen = baLen * 0.5;
  const dAxial = axialFromMid - halfLen;
  const dPerp = perpDist - r;

  if (dPerp > 0 && dAxial > 0) {
    return Math.sqrt(dPerp*dPerp + dAxial*dAxial);
  }
  return Math.max(dPerp, dAxial);
}

// Smooth minimum (polynomial interpolation)
function sdfSmin(a, b, k) {
  if (k <= 0.001) return Math.min(a, b);
  const h = Math.max(0, Math.min(1, 0.5 + 0.5 * (b - a) / k));
  return b * (1 - h) + a * h - k * h * (1 - h);
}

// Hard minimum (used between tunnel segments)
function sdfHmin(a, b) {
  return Math.min(a, b);
}

// ============================================================================
// SIGNED DISTANCE FIELD (SDF) EVALUATION
// ============================================================================

function worldSDF(px, py, pz, levelData) {
  if (!levelData || !levelData.spheres) return 10000;

  let dist = 10000;
  const smoothK = levelData.smoothK || 45;

  // Blend all spheres (rooms) with smooth min
  for (const sphere of levelData.spheres) {
    const sd = sdSphere(px, py, pz, sphere.cx, sphere.cy, sphere.cz, sphere.r);
    dist = sdfSmin(dist, sd, smoothK);
  }

  // Blend all cylinders (tunnels) with smooth min
  for (const cyl of levelData.cylinders) {
    const sd = sdCylinder(px, py, pz, cyl.ax, cyl.ay, cyl.az, cyl.bx, cyl.by, cyl.bz, cyl.r);
    dist = sdfSmin(dist, sd, smoothK);
  }

  return dist;
}

function sdfNormal(px, py, pz, levelData) {
  const eps = 2.0;
  const dx = worldSDF(px + eps, py, pz, levelData) - worldSDF(px - eps, py, pz, levelData);
  const dy = worldSDF(px, py + eps, pz, levelData) - worldSDF(px, py - eps, pz, levelData);
  const dz = worldSDF(px, py, pz + eps, levelData) - worldSDF(px, py, pz - eps, levelData);

  const normal = new Vec3(dx, dy, dz);
  normal.normalize();
  return normal;
}

// ============================================================================
// RAYCAST (SDF Sphere Tracing)
// ============================================================================

function sdfRaycast(ox, oy, oz, dx, dy, dz, maxDist, levelData) {
  let t = 4.0; // Start at 4 units from ray origin
  const maxSteps = 80;
  const minStep = 8.0;
  let lastDist = 0;

  for (let step = 0; step < maxSteps && t < maxDist; step++) {
    const px = ox + dx * t;
    const py = oy + dy * t;
    const pz = oz + dz * t;

    const dist = worldSDF(px, py, pz, levelData);

    // Hit wall (SDF crosses from negative to positive)
    if (dist >= 0) {
      return t;
    }

    // Step forward along ray
    const stepSize = Math.max(minStep, -dist * 0.8);
    t += stepSize;
    lastDist = dist;
  }

  return maxDist; // No hit within maxDist
}

// ============================================================================
// COLLISION RESOLUTION
// ============================================================================

// Constants for collision
const CONTAIN_RANGE = 1.0; // Multiplier on radius for containment zone
const CONTAIN_STRENGTH = 12000; // Force strength for containment
const UNSTICK_RANGE = 1.2; // Distance to trigger unsticking

function resolveCollision(pos, vel, radius, levelData) {
  if (!levelData || !levelData.spheres) return;

  const sdfVal = worldSDF(pos.x, pos.y, pos.z, levelData);
  const margin = -sdfVal; // Positive margin means inside; negative means outside

  // Phase 1: CONTAINMENT - Push inward if outside or near wall
  if (margin < radius * CONTAIN_RANGE) {
    const normal = sdfNormal(pos.x, pos.y, pos.z, levelData);

    if (margin < 0) {
      // Outside level: hard push inward
      const push = normal.clone().multiplyScalar((0.1 - margin) * CONTAIN_STRENGTH);
      vel.add(push.multiplyScalar(1.0 / 60.0)); // Assume ~60Hz integration
      pos.add(normal.clone().multiplyScalar(-margin * 1.1));
    } else if (margin < radius * 0.8) {
      // Very close to wall: hard clamp + wall sliding
      const push = normal.clone().multiplyScalar((radius * 0.8 - margin) * CONTAIN_STRENGTH);
      vel.add(push.multiplyScalar(1.0 / 60.0));

      // Strip velocity component into wall (wall sliding)
      const velDotNormal = vel.dot(normal);
      if (velDotNormal < 0) {
        vel.add(normal.clone().multiplyScalar(-velDotNormal * 0.5));
      }
    } else {
      // Progressive containment force
      const alpha = 1.0 - (margin / (radius * CONTAIN_RANGE));
      const force = alpha * alpha * CONTAIN_STRENGTH;
      const push = normal.clone().multiplyScalar(force);
      vel.add(push.multiplyScalar(1.0 / 60.0));
    }
  }

  // Phase 2: UNSTICK - If near wall and nearly stationary, nudge toward nearest room
  if (margin < UNSTICK_RANGE * radius && vel.length() < 50) {
    if (levelData.rooms && levelData.rooms.length > 0) {
      // Find nearest room center
      let nearestRoom = levelData.rooms[0];
      let nearestDist = pos.distanceTo(nearestRoom.center);

      for (const room of levelData.rooms) {
        const dist = pos.distanceTo(room.center);
        if (dist < nearestDist) {
          nearestDist = dist;
          nearestRoom = room;
        }
      }

      // Nudge toward room center
      const nudgeDir = new Vec3(nearestRoom.center.x, nearestRoom.center.y, nearestRoom.center.z);
      nudgeDir.sub(pos).normalize();
      vel.add(nudgeDir.multiplyScalar(100));
    }
  }
}

// ============================================================================
// SHIP-TO-SHIP COLLISION
// ============================================================================

function resolveShipShipCollisions(entities, dt) {
  const damages = []; // Array of { targetId, damage }
  const REPULSION_RANGE_MULT = 2.2;
  const REPULSION_STRENGTH = 10000;
  const IMPULSE_DAMPING = 0.6;
  const RAM_DAMAGE_THRESHOLD = 80; // Minimum impact speed for ram damage
  const RAM_DAMAGE_BASE = 500;

  for (let i = 0; i < entities.length; i++) {
    for (let j = i + 1; j < entities.length; j++) {
      const a = entities[i];
      const b = entities[j];

      if (!a.pos || !b.pos || !a.radius || !b.radius) continue;

      const dx = b.pos.x - a.pos.x;
      const dy = b.pos.y - a.pos.y;
      const dz = b.pos.z - a.pos.z;
      const distSq = dx*dx + dy*dy + dz*dz;
      const combinedRadius = a.radius + b.radius;
      const repulsionRange = combinedRadius * REPULSION_RANGE_MULT;
      const repulsionRangeSq = repulsionRange * repulsionRange;

      if (distSq > repulsionRangeSq) continue; // Too far

      const dist = Math.sqrt(distSq);
      if (dist < 0.001) continue; // Coincident

      const normalX = dx / dist;
      const normalY = dy / dist;
      const normalZ = dz / dist;

      // Repulsion force (scales with proximity)
      const overlap = combinedRadius - dist;
      if (overlap > 0) {
        // Hard overlap: push apart
        const pushMag = (overlap + 10) * REPULSION_STRENGTH;
        const pushX = normalX * pushMag;
        const pushY = normalY * pushMag;
        const pushZ = normalZ * pushMag;

        a.vel.x -= pushX * dt / 60;
        a.vel.y -= pushY * dt / 60;
        a.vel.z -= pushZ * dt / 60;

        b.vel.x += pushX * dt / 60;
        b.vel.y += pushY * dt / 60;
        b.vel.z += pushZ * dt / 60;

        // Velocity impulse (reflect with damping)
        const relVelX = b.vel.x - a.vel.x;
        const relVelY = b.vel.y - a.vel.y;
        const relVelZ = b.vel.z - a.vel.z;
        const relVelDotNormal = relVelX * normalX + relVelY * normalY + relVelZ * normalZ;

        if (relVelDotNormal < 0) {
          const impulseX = normalX * relVelDotNormal * IMPULSE_DAMPING;
          const impulseY = normalY * relVelDotNormal * IMPULSE_DAMPING;
          const impulseZ = normalZ * relVelDotNormal * IMPULSE_DAMPING;

          a.vel.x += impulseX;
          a.vel.y += impulseY;
          a.vel.z += impulseZ;

          b.vel.x -= impulseX;
          b.vel.y -= impulseY;
          b.vel.z -= impulseZ;

          // Check for ram damage
          const impactSpeed = Math.abs(relVelDotNormal);
          if (impactSpeed > RAM_DAMAGE_THRESHOLD) {
            const ramDamage = Math.floor(RAM_DAMAGE_BASE + impactSpeed * 3);
            damages.push({ targetId: b.id, damage: ramDamage });
            damages.push({ targetId: a.id, damage: ramDamage });
          }
        }
      }
    }
  }

  return damages;
}

// ============================================================================
// LEVEL DATA CONSTRUCTION
// ============================================================================

function buildLevelData(mapKey) {
  const mapDef = MAP_DATA[mapKey];
  if (!mapDef) {
    console.warn(`Map not found: ${mapKey}, using circumpunct`);
    return buildLevelData('circumpunct');
  }

  const levelData = {
    mapKey,
    mapName: mapDef.name,
    spheres: [],
    cylinders: [],
    smoothK: 45,
    rooms: [],
  };

  // Add spheres from room definitions
  for (const room of mapDef.rooms) {
    const sphere = {
      cx: room.x, cy: room.y, cz: room.z, r: room.r,
    };
    levelData.spheres.push(sphere);

    // Store room centers for reference
    levelData.rooms.push({
      id: room.id, team: room.team,
      center: new Vec3(room.x, room.y, room.z),
      radius: room.r,
    });
  }

  // Add cylinders from tunnel definitions
  const tunnelRadius = SU * 2.0; // Tunnel radius
  for (const tunnel of mapDef.tunnels) {
    const path = tunnel.path;
    for (let i = 0; i < path.length - 1; i++) {
      const a = path[i];
      const b = path[i + 1];
      const cyl = {
        ax: a.x, ay: a.y, az: a.z,
        bx: b.x, by: b.y, bz: b.z,
        r: tunnelRadius,
      };
      levelData.cylinders.push(cyl);
    }
  }

  return levelData;
}

// ============================================================================
// SPAWN POINT FINDER
// ============================================================================

function getValidSpawnPoint(levelData, teamTag) {
  if (!levelData || !levelData.rooms) {
    // Fallback
    return new Vec3(
      (Math.random() - 0.5) * 2000,
      (Math.random() - 0.5) * 500,
      (Math.random() - 0.5) * 2000
    );
  }

  // Find team spawn rooms
  const spawnRooms = levelData.rooms.filter(room => room.team === teamTag);
  if (spawnRooms.length === 0) {
    // Fallback to any room
    const anyRoom = levelData.rooms[Math.floor(Math.random() * levelData.rooms.length)];
    const angle = Math.random() * Math.PI * 2;
    const radius = Math.random() * (anyRoom.radius * 0.5);
    return new Vec3(
      anyRoom.center.x + Math.cos(angle) * radius,
      anyRoom.center.y + (Math.random() - 0.5) * 100,
      anyRoom.center.z + Math.sin(angle) * radius
    );
  }

  // Pick a random spawn room
  const room = spawnRooms[Math.floor(Math.random() * spawnRooms.length)];

  // Pick a random point inside the room
  const angle = Math.random() * Math.PI * 2;
  const elevation = (Math.random() - 0.5) * Math.PI;
  const radius = Math.random() * (room.radius * 0.6);

  return new Vec3(
    room.center.x + Math.cos(angle) * Math.cos(elevation) * radius,
    room.center.y + Math.sin(elevation) * radius,
    room.center.z + Math.sin(angle) * Math.cos(elevation) * radius
  );
}

// ============================================================================
// PROCEDURAL MAP GENERATOR
// ============================================================================

function generateProceduralMap(seed = Math.random()) {
  // Simple seeded random
  const rng = () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };

  const map = { rooms: [], tunnels: [] };
  const numRooms = 5 + Math.floor(rng() * 3); // 5-7 rooms

  // Generate room centers using random placement
  const rooms = [];
  for (let i = 0; i < numRooms; i++) {
    const angle = (i / numRooms) * Math.PI * 2 + rng() * 0.3;
    const dist = SU * (4 + rng() * 6);
    rooms.push({
      id: `room_${i}`,
      team: i === 0 ? 'A' : i === 1 ? 'B' : null,
      x: Math.cos(angle) * dist,
      y: (rng() - 0.5) * SU * 2,
      z: Math.sin(angle) * dist,
      r: SU * (1.5 + rng() * 1.5),
    });
  }

  // Connect with Minimum Spanning Tree-ish approach
  const connected = new Set([0]);
  const edges = [];

  while (connected.size < rooms.length) {
    let best = null;
    let bestDist = Infinity;

    for (const i of connected) {
      for (let j = 0; j < rooms.length; j++) {
        if (connected.has(j)) continue;
        const dx = rooms[j].x - rooms[i].x;
        const dy = rooms[j].y - rooms[i].y;
        const dz = rooms[j].z - rooms[i].z;
        const d = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (d < bestDist) {
          bestDist = d;
          best = [i, j];
        }
      }
    }

    if (best) {
      edges.push(best);
      connected.add(best[1]);
    }
  }

  // Ensure each room has 2+ connections
  for (let i = 0; i < rooms.length; i++) {
    const connections = edges.filter(e => e[0] === i || e[1] === i).length;
    if (connections < 2 && i < rooms.length - 1) {
      edges.push([i, i + 1]);
    }
  }

  // Convert edges to tunnels
  for (const [i, j] of edges) {
    const ri = rooms[i];
    const rj = rooms[j];
    map.tunnels.push({
      path: [
        { x: ri.x, y: ri.y, z: ri.z },
        { x: rj.x, y: rj.y, z: rj.z },
      ],
    });
  }

  map.rooms = rooms;
  return map;
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // SDF functions
  sdSphere,
  sdCylinder,
  sdfSmin,
  sdfHmin,
  worldSDF,
  sdfNormal,
  sdfRaycast,

  // Collision resolution
  resolveCollision,
  resolveShipShipCollisions,

  // Level data
  buildLevelData,
  getValidSpawnPoint,
  generateProceduralMap,

  // Constants & data
  MAP_DATA,
  SU,
};
