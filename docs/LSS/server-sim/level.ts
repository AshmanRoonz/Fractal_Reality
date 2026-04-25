/*
  LSS server-sim ; level data (v8.9)

  Levels are room-graph: a set of rooms (spheres) connected by tunnels
  (cylinders). Pure data; the server uses these for collision (player must
  stay inside the union of all rooms+tunnels), the client renders them as
  inside-out wireframe shells. No Three.js dependency here.

  v8.9: SDF helpers ported from the LSS html. The world SDF blends rooms
  via smooth-min (sdfSmin) so room-room and room-tunnel junctions are
  graded, not binary; tunnels use hard-min between each other so parallel
  tunnels stay separate. sdfNormal gives the gradient (central differences)
  for collision response. Negative SDF = inside the playable union; positive
  SDF = outside (solid wall).
*/

export interface Vec3 { x: number; y: number; z: number; }
export interface AABB { min: Vec3; max: Vec3; }

export interface Room {
  id: string;
  team: 'A' | 'B' | null;
  center: Vec3;
  radius: number;
}

export interface Tunnel {
  a: Vec3;
  b: Vec3;
  radius: number;
}

export interface Level {
  name: string;
  bounds: AABB;
  rooms: Room[];
  tunnels: Tunnel[];
  obstacles: AABB[];
  spawnA: Vec3[];
  spawnB: Vec3[];
}

const SU = 700;

interface MapDef {
  name: string;
  rooms: { id: string; team: 'A' | 'B' | null; x: number; y: number; z: number; r: number }[];
  tunnels: { from: string; to: string; r?: number }[];
  obstacles?: AABB[];
}

const MAP_DEFS: Record<string, MapDef> = {
  hourglass: {
    name: 'hourglass',
    rooms: [
      { id: 'spawn_a', team: 'A', x: 0, y: 0, z: -SU * 4,   r: SU * 1.4 },
      { id: 'top',     team: null, x: 0, y: SU * 1.5, z: -SU * 1.5, r: SU * 1.0 },
      { id: 'center',  team: null, x: 0, y: 0, z: 0,        r: SU * 1.5 },
      { id: 'bottom',  team: null, x: 0, y: -SU * 1.5, z: SU * 1.5,  r: SU * 1.0 },
      { id: 'spawn_b', team: 'B', x: 0, y: 0, z: SU * 4,    r: SU * 1.4 },
    ],
    tunnels: [
      { from: 'spawn_a', to: 'top' },
      { from: 'spawn_a', to: 'center' },
      { from: 'top',     to: 'center' },
      { from: 'center',  to: 'bottom' },
      { from: 'bottom',  to: 'spawn_b' },
      { from: 'center',  to: 'spawn_b' },
    ],
  },

  nexus: {
    name: 'nexus',
    rooms: [
      { id: 'center',  team: null, x: 0,           y: 0,  z: 0,           r: SU * 1.6 },
      { id: 'spawn_a', team: 'A',  x: 0,           y: 0,  z: -SU * 5,     r: SU * 1.4 },
      { id: 'ne',      team: null, x:  SU * 4.3,    y: SU * 1.2, z: -SU * 2.5, r: SU * 1.1 },
      { id: 'se',      team: null, x:  SU * 4.3,    y: -SU * 1.2, z:  SU * 2.5, r: SU * 1.1 },
      { id: 'spawn_b', team: 'B',  x: 0,           y: 0,  z:  SU * 5,     r: SU * 1.4 },
      { id: 'sw',      team: null, x: -SU * 4.3,    y: -SU * 1.2, z:  SU * 2.5, r: SU * 1.1 },
      { id: 'nw',      team: null, x: -SU * 4.3,    y: SU * 1.2, z: -SU * 2.5, r: SU * 1.1 },
    ],
    tunnels: [
      { from: 'spawn_a', to: 'ne' },
      { from: 'ne',      to: 'se' },
      { from: 'se',      to: 'spawn_b' },
      { from: 'spawn_b', to: 'sw' },
      { from: 'sw',      to: 'nw' },
      { from: 'nw',      to: 'spawn_a' },
      { from: 'spawn_a', to: 'center' },
      { from: 'ne',      to: 'center' },
      { from: 'se',      to: 'center' },
      { from: 'spawn_b', to: 'center' },
      { from: 'sw',      to: 'center' },
      { from: 'nw',      to: 'center' },
    ],
  },

  cathedral: {
    name: 'cathedral',
    rooms: [
      { id: 'spawn_a', team: 'A', x: -SU * 5,     y: 0, z: 0,           r: SU * 1.4 },
      { id: 'apse_a',  team: null, x: -SU * 3,    y: SU * 1.2, z: 0,    r: SU * 1.0 },
      { id: 'nave_a',  team: null, x: -SU * 1.5,  y: 0, z: 0,            r: SU * 1.2 },
      { id: 'transept', team: null, x: 0,         y: SU * 0.6, z: 0,     r: SU * 1.6 },
      { id: 'side_n',   team: null, x: 0,         y: 0, z: -SU * 3,      r: SU * 1.0 },
      { id: 'side_s',   team: null, x: 0,         y: 0, z:  SU * 3,      r: SU * 1.0 },
      { id: 'nave_b',  team: null, x:  SU * 1.5,  y: 0, z: 0,            r: SU * 1.2 },
      { id: 'apse_b',  team: null, x:  SU * 3,    y: SU * 1.2, z: 0,    r: SU * 1.0 },
      { id: 'spawn_b', team: 'B', x:  SU * 5,     y: 0, z: 0,           r: SU * 1.4 },
    ],
    tunnels: [
      { from: 'spawn_a', to: 'apse_a' },
      { from: 'spawn_a', to: 'nave_a' },
      { from: 'apse_a',  to: 'nave_a' },
      { from: 'nave_a',  to: 'transept' },
      { from: 'transept', to: 'side_n' },
      { from: 'transept', to: 'side_s' },
      { from: 'transept', to: 'nave_b' },
      { from: 'nave_b',  to: 'apse_b' },
      { from: 'nave_b',  to: 'spawn_b' },
      { from: 'apse_b',  to: 'spawn_b' },
    ],
  },
};

export const MAP_KEYS = Object.keys(MAP_DEFS);

export function buildLevel(mapKey?: string): Level {
  const key = (mapKey && MAP_DEFS[mapKey]) ? mapKey : 'hourglass';
  return _buildLevelFromDef(MAP_DEFS[key]);
}

function _buildLevelFromDef(def: MapDef): Level {
  const TUNNEL_R = SU * 0.35;
  const rooms: Room[] = def.rooms.map(r => ({
    id: r.id, team: r.team,
    center: { x: r.x, y: r.y, z: r.z },
    radius: r.r,
  }));
  const roomById: Record<string, Room> = {};
  for (const r of rooms) roomById[r.id] = r;

  const tunnels: Tunnel[] = def.tunnels.map(t => {
    const a = roomById[t.from]; const b = roomById[t.to];
    return {
      a: { x: a.center.x, y: a.center.y, z: a.center.z },
      b: { x: b.center.x, y: b.center.y, z: b.center.z },
      radius: t.r != null ? t.r : TUNNEL_R,
    };
  });

  const spawnA: Vec3[] = [];
  const spawnB: Vec3[] = [];
  for (const r of rooms) {
    if (r.team !== 'A' && r.team !== 'B') continue;
    const target = r.team === 'A' ? spawnA : spawnB;
    for (let i = 0; i < 4; i++) {
      const ang = (i / 4) * Math.PI * 2;
      const off = r.radius * 0.55;
      target.push({
        x: r.center.x + Math.cos(ang) * off,
        y: r.center.y + (i % 2 === 0 ? 80 : -80),
        z: r.center.z + Math.sin(ang) * off,
      });
    }
  }
  if (spawnA.length === 0 && rooms.length > 0) spawnA.push(rooms[0].center);
  if (spawnB.length === 0 && rooms.length > 0) spawnB.push(rooms[rooms.length - 1].center);

  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  const expand = (p: Vec3, r: number) => {
    if (p.x - r < minX) minX = p.x - r;
    if (p.y - r < minY) minY = p.y - r;
    if (p.z - r < minZ) minZ = p.z - r;
    if (p.x + r > maxX) maxX = p.x + r;
    if (p.y + r > maxY) maxY = p.y + r;
    if (p.z + r > maxZ) maxZ = p.z + r;
  };
  for (const r of rooms) expand(r.center, r.radius);
  for (const t of tunnels) { expand(t.a, t.radius); expand(t.b, t.radius); }
  const M = 200;
  const bounds: AABB = {
    min: { x: minX - M, y: minY - M, z: minZ - M },
    max: { x: maxX + M, y: maxY + M, z: maxZ + M },
  };

  return {
    name: def.name,
    bounds, rooms, tunnels,
    obstacles: def.obstacles || [],
    spawnA, spawnB,
  };
}

export function pointInRoom(p: Vec3, r: Room): boolean {
  const dx = p.x - r.center.x, dy = p.y - r.center.y, dz = p.z - r.center.z;
  return (dx * dx + dy * dy + dz * dz) < r.radius * r.radius;
}

export function pointInTunnel(p: Vec3, t: Tunnel): boolean {
  const ax = t.b.x - t.a.x, ay = t.b.y - t.a.y, az = t.b.z - t.a.z;
  const len2 = ax * ax + ay * ay + az * az;
  if (len2 < 1e-6) return false;
  const px = p.x - t.a.x, py = p.y - t.a.y, pz = p.z - t.a.z;
  const dot = px * ax + py * ay + pz * az;
  const tParam = dot / len2;
  if (tParam < 0 || tParam > 1) return false;
  const closestX = t.a.x + ax * tParam;
  const closestY = t.a.y + ay * tParam;
  const closestZ = t.a.z + az * tParam;
  const dx = p.x - closestX, dy = p.y - closestY, dz = p.z - closestZ;
  return (dx * dx + dy * dy + dz * dz) < t.radius * t.radius;
}

export function pointInLevel(p: Vec3, level: Level): boolean {
  for (let i = 0; i < level.rooms.length; i++) if (pointInRoom(p, level.rooms[i])) return true;
  for (let i = 0; i < level.tunnels.length; i++) if (pointInTunnel(p, level.tunnels[i])) return true;
  return false;
}

// ---- SDF level system (v8.9, ported from LSS html) ----
//
// The world SDF is the signed distance to the boundary of the playable
// union. Negative inside (deeper = more negative); positive outside (further
// = more positive); zero on the wall. Rooms blend with each other and with
// tunnels via smooth-min so junctions are graded (no hard discontinuity at
// room edges). Tunnels are hard-min'd against each other so parallel tunnels
// stay separate (smooth-blending all tunnels would merge nearby parallels
// into a single fat tube).
//
// Smooth-min radius. LSS uses 45 with SU=150; we scale to our SU=700.
// Bigger k = softer blend (more rounded junctions); smaller k = sharper.
const SDF_SMOOTH_K = 200;

function sdSphere(px: number, py: number, pz: number, cx: number, cy: number, cz: number, r: number): number {
  const dx = px - cx, dy = py - cy, dz = pz - cz;
  return Math.sqrt(dx * dx + dy * dy + dz * dz) - r;
}

function sdCylinder(
  px: number, py: number, pz: number,
  ax: number, ay: number, az: number,
  bx: number, by: number, bz: number,
  r: number,
): number {
  const bax = bx - ax, bay = by - ay, baz = bz - az;
  const pax = px - ax, pay = py - ay, paz = pz - az;
  const baLen2 = bax * bax + bay * bay + baz * baz;
  if (baLen2 < 0.001) return sdSphere(px, py, pz, ax, ay, az, r);
  let t = (pax * bax + pay * bay + paz * baz) / baLen2;
  if (t < 0) t = 0; else if (t > 1) t = 1;
  const cx2 = ax + bax * t, cy2 = ay + bay * t, cz2 = az + baz * t;
  const dx = px - cx2, dy = py - cy2, dz = pz - cz2;
  const perpDist = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const baLen = Math.sqrt(baLen2);
  const axialFromMid = Math.abs(t - 0.5) * baLen;
  const halfLen = baLen * 0.5;
  const dAxial = axialFromMid - halfLen;
  const dPerp = perpDist - r;
  if (dPerp > 0 && dAxial > 0) return Math.sqrt(dPerp * dPerp + dAxial * dAxial);
  return Math.max(dPerp, dAxial);
}

function sdfSmin(a: number, b: number, k: number): number {
  if (k <= 0.001) return Math.min(a, b);
  let h = 0.5 + 0.5 * (b - a) / k;
  if (h < 0) h = 0; else if (h > 1) h = 1;
  return b * (1 - h) + a * h - k * h * (1 - h);
}

// World SDF on raw coords (zero allocation; the hot path).
// Negative = inside playable union; positive = solid wall. Rooms blend with
// each other (smin); each tunnel blends with the rooms (smin) but tunnels
// are unioned with each other via hard min so parallels stay separate.
export function worldSDFAt(px: number, py: number, pz: number, level: Level): number {
  const k = SDF_SMOOTH_K;
  let roomD = 99999;
  for (let i = 0; i < level.rooms.length; i++) {
    const r = level.rooms[i];
    roomD = sdfSmin(roomD, sdSphere(px, py, pz, r.center.x, r.center.y, r.center.z, r.radius), k);
  }
  let d = roomD;
  for (let i = 0; i < level.tunnels.length; i++) {
    const t = level.tunnels[i];
    const cd = sdCylinder(px, py, pz, t.a.x, t.a.y, t.a.z, t.b.x, t.b.y, t.b.z, t.radius);
    const blended = sdfSmin(roomD, cd, k);
    if (blended < d) d = blended;
  }
  return d;
}

// Convenience wrapper for callers holding a Vec3.
export function worldSDF(p: Vec3, level: Level): number {
  return worldSDFAt(p.x, p.y, p.z, level);
}

// SDF gradient via central differences. Points OUTWARD (toward higher SDF =
// toward the wall and beyond). Inward normal (used by the collision resolver
// to push the player back inside) is the negation. Writes into `out` if
// provided to avoid allocation in the hot collision loop.
export function sdfNormal(p: Vec3, level: Level, out?: Vec3): Vec3 {
  const e = 4.0; // central-differences step; ~0.6% of SU=700
  const px = p.x, py = p.y, pz = p.z;
  const nx = worldSDFAt(px + e, py, pz, level) - worldSDFAt(px - e, py, pz, level);
  const ny = worldSDFAt(px, py + e, pz, level) - worldSDFAt(px, py - e, pz, level);
  const nz = worldSDFAt(px, py, pz + e, level) - worldSDFAt(px, py, pz - e, level);
  const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
  if (out) {
    out.x = nx / len; out.y = ny / len; out.z = nz / len;
    return out;
  }
  return { x: nx / len, y: ny / len, z: nz / len };
}
