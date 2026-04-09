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

// Raw SDF evaluation (used only during grid pre-computation)
function worldSDFRaw(px, py, pz, levelData) {
  if (!levelData || !levelData.spheres) return 10000;
  let dist = 10000;
  const smoothK = levelData.smoothK || 45;
  for (const sphere of levelData.spheres) {
    const sd = sdSphere(px, py, pz, sphere.cx, sphere.cy, sphere.cz, sphere.r);
    dist = sdfSmin(dist, sd, smoothK);
  }
  for (const cyl of levelData.cylinders) {
    const sd = sdCylinder(px, py, pz, cyl.ax, cyl.ay, cyl.az, cyl.bx, cyl.by, cyl.bz, cyl.r);
    dist = sdfSmin(dist, sd, smoothK);
  }
  return dist;
}

// Pre-computed SDF grid: one Float32Array lookup replaces 17 distance calcs
const SDF_CELL = 20; // Grid cell size in world units
const SDF_PAD = 250; // Padding around geometry bounds

let sdfGrid = null;   // Float32Array
let sdfNX = 0, sdfNY = 0, sdfNZ = 0;
let sdfMinX = 0, sdfMinY = 0, sdfMinZ = 0;

function buildSDFGrid(levelData) {
  // Find bounds of all geometry
  let bMinX = Infinity, bMinY = Infinity, bMinZ = Infinity;
  let bMaxX = -Infinity, bMaxY = -Infinity, bMaxZ = -Infinity;
  for (const s of levelData.spheres) {
    bMinX = Math.min(bMinX, s.cx - s.r); bMaxX = Math.max(bMaxX, s.cx + s.r);
    bMinY = Math.min(bMinY, s.cy - s.r); bMaxY = Math.max(bMaxY, s.cy + s.r);
    bMinZ = Math.min(bMinZ, s.cz - s.r); bMaxZ = Math.max(bMaxZ, s.cz + s.r);
  }
  for (const c of levelData.cylinders) {
    for (const p of [{x:c.ax,y:c.ay,z:c.az},{x:c.bx,y:c.by,z:c.bz}]) {
      bMinX = Math.min(bMinX, p.x - c.r); bMaxX = Math.max(bMaxX, p.x + c.r);
      bMinY = Math.min(bMinY, p.y - c.r); bMaxY = Math.max(bMaxY, p.y + c.r);
      bMinZ = Math.min(bMinZ, p.z - c.r); bMaxZ = Math.max(bMaxZ, p.z + c.r);
    }
  }

  sdfMinX = bMinX - SDF_PAD;
  sdfMinY = bMinY - SDF_PAD;
  sdfMinZ = bMinZ - SDF_PAD;
  sdfNX = Math.ceil((bMaxX + SDF_PAD - sdfMinX) / SDF_CELL) + 1;
  sdfNY = Math.ceil((bMaxY + SDF_PAD - sdfMinY) / SDF_CELL) + 1;
  sdfNZ = Math.ceil((bMaxZ + SDF_PAD - sdfMinZ) / SDF_CELL) + 1;

  sdfGrid = new Float32Array(sdfNX * sdfNY * sdfNZ);

  console.log(`[SDF Grid] ${sdfNX}x${sdfNY}x${sdfNZ} = ${sdfGrid.length} cells (${(sdfGrid.length * 4 / 1024 / 1024).toFixed(1)} MB)`);

  const t0 = Date.now();
  for (let iz = 0; iz < sdfNZ; iz++) {
    const pz = sdfMinZ + iz * SDF_CELL;
    for (let iy = 0; iy < sdfNY; iy++) {
      const py = sdfMinY + iy * SDF_CELL;
      for (let ix = 0; ix < sdfNX; ix++) {
        const px = sdfMinX + ix * SDF_CELL;
        sdfGrid[ix + iy * sdfNX + iz * sdfNX * sdfNY] = worldSDFRaw(px, py, pz, levelData);
      }
    }
  }
  console.log(`[SDF Grid] Built in ${Date.now() - t0}ms`);
}

// Trilinear interpolation from the pre-computed grid
function worldSDF(px, py, pz, levelData) {
  if (!sdfGrid) return worldSDFRaw(px, py, pz, levelData);

  // Convert world coords to grid coords
  const gx = (px - sdfMinX) / SDF_CELL;
  const gy = (py - sdfMinY) / SDF_CELL;
  const gz = (pz - sdfMinZ) / SDF_CELL;

  // Clamp to grid bounds
  const ix = Math.max(0, Math.min(sdfNX - 2, Math.floor(gx)));
  const iy = Math.max(0, Math.min(sdfNY - 2, Math.floor(gy)));
  const iz = Math.max(0, Math.min(sdfNZ - 2, Math.floor(gz)));

  const fx = gx - ix, fy = gy - iy, fz = gz - iz;
  const fx1 = 1 - fx, fy1 = 1 - fy, fz1 = 1 - fz;

  const idx = ix + iy * sdfNX + iz * sdfNX * sdfNY;
  const sX = 1, sY = sdfNX, sZ = sdfNX * sdfNY;

  // 8-point trilinear interpolation
  return (
    sdfGrid[idx]             * fx1 * fy1 * fz1 +
    sdfGrid[idx + sX]        * fx  * fy1 * fz1 +
    sdfGrid[idx + sY]        * fx1 * fy  * fz1 +
    sdfGrid[idx + sX + sY]   * fx  * fy  * fz1 +
    sdfGrid[idx + sZ]        * fx1 * fy1 * fz  +
    sdfGrid[idx + sX + sZ]   * fx  * fy1 * fz  +
    sdfGrid[idx + sY + sZ]   * fx1 * fy  * fz  +
    sdfGrid[idx + sX+sY+sZ]  * fx  * fy  * fz
  );
}

// Normal from grid: central differences on the grid (6 lookups instead of 102 primitive evals)
function sdfNormal(px, py, pz, levelData) {
  const eps = SDF_CELL * 0.6;
  const dx = worldSDF(px + eps, py, pz, levelData) - worldSDF(px - eps, py, pz, levelData);
  const dy = worldSDF(px, py + eps, pz, levelData) - worldSDF(px, py - eps, pz, levelData);
  const dz = worldSDF(px, py, pz + eps, levelData) - worldSDF(px, py, pz - eps, levelData);
  const len = Math.sqrt(dx*dx + dy*dy + dz*dz);
  if (len < 0.0001) return new Vec3(0, 1, 0);
  return new Vec3(dx / len, dy / len, dz / len);
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
// COLLISION RESOLUTION (matches client exactly)
// ============================================================================

const CONTAIN_STRENGTH = 12000;

function resolveCollision(pos, vel, radius, levelData) {
  if (!levelData || !levelData.spheres) return;

  const sdfVal = worldSDF(pos.x, pos.y, pos.z, levelData);
  // sdfVal < 0 means inside (negative = inside the union of shapes)
  // margin = -sdfVal: positive means inside, negative means outside
  const margin = -sdfVal;

  const CONTAIN_RANGE_R = radius * 2.5;

  if (margin < CONTAIN_RANGE_R) {
    // NEGATE the SDF normal to get INWARD normal (pointing into room, away from walls)
    // This matches the client's convention: sdfNormal(...).negate()
    const rawNormal = sdfNormal(pos.x, pos.y, pos.z, levelData);
    const normal = new Vec3(-rawNormal.x, -rawNormal.y, -rawNormal.z);

    if (margin < 0) {
      // Outside the level: hard push inside (matches client)
      pos.add(normal.clone().multiplyScalar(-margin + radius + 4));
      const vn = vel.dot(normal);
      if (vn < 0) vel.sub(normal.clone().multiplyScalar(vn * 1.5));
    } else if (margin < radius * 0.8) {
      // Very close to wall: hard clamp position + wall sliding (matches client)
      pos.add(normal.clone().multiplyScalar(radius * 0.8 - margin + 2));
      const vn = vel.dot(normal);
      if (vn < 0) vel.sub(normal.clone().multiplyScalar(vn * 1.05));
    } else {
      // Inside but near wall: progressive containment force (matches client)
      const ratio = 1 - (margin / CONTAIN_RANGE_R);
      const force = CONTAIN_STRENGTH * ratio * ratio;
      vel.add(normal.clone().multiplyScalar(force * (1.0 / 60.0)));
    }
  }

  // Unstick: if near wall and nearly stationary, nudge toward nearest room
  if (margin > 0 && margin < radius * 2.0 && vel.lengthSq() < 100) {
    if (levelData.rooms && levelData.rooms.length > 0) {
      let nearestRoom = levelData.rooms[0];
      let nearestDist = pos.distanceTo(nearestRoom.center);
      for (const room of levelData.rooms) {
        const dist = pos.distanceTo(room.center);
        if (dist < nearestDist) { nearestDist = dist; nearestRoom = room; }
      }
      const nudgeDir = new Vec3(
        nearestRoom.center.x - pos.x,
        nearestRoom.center.y - pos.y,
        nearestRoom.center.z - pos.z
      );
      if (nudgeDir.lengthSq() > 1) {
        nudgeDir.normalize();
        vel.add(nudgeDir.multiplyScalar(100));
      }
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
      levelData.cylinders.push({
        ax: a.x, ay: a.y, az: a.z,
        bx: b.x, by: b.y, bz: b.z,
        r: tunnelRadius,
      });
    }
  }

  // Pre-compute the SDF grid for fast lookups
  buildSDFGrid(levelData);

  return levelData;
}

// ============================================================================
// SPAWN POINTS
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

  const room = spawnRooms[Math.floor(Math.random() * spawnRooms.length)];
  const angle = Math.random() * Math.PI * 2;
  const r = Math.random() * (room.radius * 0.4);
  return new Vec3(
    room.center.x + Math.cos(angle) * r,
    room.center.y + (Math.random() - 0.5) * 80,
    room.center.z + Math.sin(angle) * r
  );
}

// ============================================================================
// PROCEDURAL MAP GENERATION (not used for circumpunct but kept for future)
// ============================================================================

function generateProceduralMap() {
  const numRooms = 5 + Math.floor(Math.random() * 4);
  const map = {
    name: 'Procedural Arena',
    rooms: [],
    tunnels: [],
    procedural: true,
  };

  // Generate rooms with minimum separation
  const minSep = SU * 5;
  for (let i = 0; i < numRooms; i++) {
    let x, y, z, valid;
    let attempts = 0;
    do {
      x = (Math.random() - 0.5) * SU * 18;
      y = (Math.random() - 0.5) * SU * 6;
      z = (Math.random() - 0.5) * SU * 18;
      valid = true;
      for (const r of map.rooms) {
        const dx = r.x - x, dy = r.y - y, dz = r.z - z;
        if (Math.sqrt(dx*dx + dy*dy + dz*dz) < minSep) { valid = false; break; }
      }
      attempts++;
    } while (!valid && attempts < 100);

    const team = i === 0 ? 'A' : (i === 1 ? 'B' : null);
    const r = SU * (1.5 + Math.random() * 1.5);
    map.rooms.push({ id: `room_${i}`, team, x, y, z, r });
  }

  // Connect rooms with MST
  const rooms = map.rooms;
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
