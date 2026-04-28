/*
  LSS server-sim ; level data (v8.10)

  Levels are room-graph: a set of rooms (spheres) connected by tunnels
  (cylinders). Pure data; the server uses these for collision (player must
  stay inside the union of all rooms+tunnels), the client renders them via
  marching cubes on the same SDF the server uses for collision, so visuals
  and physics agree.

  v8.10:
   - Map definitions ported verbatim from last_ship_sailing.html
     (hourglass, spine, infinity, tower, cross, arc, octahedron, pentagon,
     gyre); 9 maps replacing the 3 hand-rederived ones.
   - Tunnels are now multi-waypoint paths in MapDef; flattened to single-
     segment Tunnels at build time (the runtime form). Lets us author
     curved corridors (arc, gyre) and figure-8s.
   - Level carries displayName, description, palette (8 hex colors for the
     wall shader), and sdfSmoothK on the wire so the client meshes the
     same SDF the server collides against.
   - SU back to LSS's 150 to preserve their chassis-speed-vs-room-size
     tuning. (Was 700 in v8.7-v8.9; maps were 4.67x larger than designed.)

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
  displayName: string;
  description: string;
  palette: number[];        // 8 hex colors driving the wall shader's per-zone tint
  bounds: AABB;
  rooms: Room[];
  tunnels: Tunnel[];        // already split into segments at build time
  obstacles: AABB[];
  spawnA: Vec3[];
  spawnB: Vec3[];
  sdfSmoothK: number;       // smooth-min radius; client uses this when meshing
}

// LSS uses SU = 150; we keep that to preserve LSS's chassis-speed-to-room-size
// tuning. Every room/tunnel coordinate in MAP_DEFS is a multiple of SU, so to
// rescale the whole world you change this one number. Note: PLAYER_RADIUS in
// simulation.ts is in absolute units, not SU-relative; if you change SU you
// probably want to keep player size proportional.
const SU = 150;
const TUNNEL_R = SU * 1.2;  // default tunnel radius (LSS default for hand-crafted maps)

interface MapDef {
  name: string;             // key (hourglass, spine, ...)
  displayName: string;
  description: string;
  palette: number[];
  rooms: { id: string; team: 'A' | 'B' | null; x: number; y: number; z: number; r: number }[];
  // Each tunnel is a path of waypoints; consecutive pairs become one cylinder
  // segment. Lets us author curved corridors (arc, gyre) and figure-8s without
  // contorting the data model.
  tunnels: { path: { x: number; y: number; z: number }[]; r?: number }[];
  obstacles?: AABB[];
}

// ---- Map definitions (ported verbatim from last_ship_sailing.html, Apr 2026) ----
//
// Nine maps; each one a hand-authored room + tunnel graph. The wall mesh is
// procedural (marching cubes from the SDF) but the topology is fixed so each
// map plays the way it was designed.

const MAP_DEFS: Record<string, MapDef> = {
  hourglass: {
    name: 'hourglass',
    displayName: 'The Nexus',
    description: 'Ring layout. Six chambers. Every room connects to two others; no dead ends.',
    palette: [0x4a3818, 0x2a1840, 0x1a2848, 0x18283a, 0x202848, 0x1a2840, 0x18203a, 0x1c2848],
    rooms: [
      { id: 'center',  team: null, x: 0,        y: 0,        z: 0,        r: SU * 2.5 },
      { id: 'spawn_a', team: 'A',  x: 0,        y: 0,        z: -SU * 8,  r: SU * 2.2 },
      { id: 'ne',      team: null, x:  SU * 7,  y:  SU * 2,  z: -SU * 4,  r: SU * 1.8 },
      { id: 'se',      team: null, x:  SU * 7,  y: -SU * 2,  z:  SU * 4,  r: SU * 1.8 },
      { id: 'spawn_b', team: 'B',  x: 0,        y: 0,        z:  SU * 8,  r: SU * 2.2 },
      { id: 'sw',      team: null, x: -SU * 7,  y: -SU * 2,  z:  SU * 4,  r: SU * 1.8 },
      { id: 'nw',      team: null, x: -SU * 7,  y:  SU * 2,  z: -SU * 4,  r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{ x: 0, y: 0, z: -SU * 8 }, { x:  SU * 7, y:  SU * 2, z: -SU * 4 }] },
      { path: [{ x:  SU * 7, y:  SU * 2, z: -SU * 4 }, { x:  SU * 7, y: -SU * 2, z:  SU * 4 }] },
      { path: [{ x:  SU * 7, y: -SU * 2, z:  SU * 4 }, { x: 0, y: 0, z:  SU * 8 }] },
      { path: [{ x: 0, y: 0, z:  SU * 8 }, { x: -SU * 7, y: -SU * 2, z:  SU * 4 }] },
      { path: [{ x: -SU * 7, y: -SU * 2, z:  SU * 4 }, { x: -SU * 7, y:  SU * 2, z: -SU * 4 }] },
      { path: [{ x: -SU * 7, y:  SU * 2, z: -SU * 4 }, { x: 0, y: 0, z: -SU * 8 }] },
      { path: [{ x: 0, y: 0, z: -SU * 8 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x:  SU * 7, y:  SU * 2, z: -SU * 4 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x:  SU * 7, y: -SU * 2, z:  SU * 4 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: 0, y: 0, z:  SU * 8 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: -SU * 7, y: -SU * 2, z:  SU * 4 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: -SU * 7, y:  SU * 2, z: -SU * 4 }, { x: 0, y: 0, z: 0 }] },
    ],
  },

  spine: {
    name: 'spine',
    displayName: 'The Spine',
    description: 'Long axis with parallel bypasses. Center is the killing line; flank through the arcs.',
    palette: [0x1c1818, 0x281a1a, 0x2a1c1c, 0x381616, 0x281818, 0x202020, 0x301818, 0x401818],
    rooms: [
      { id: 'spawn_a',   team: 'A',  x: 0,        y: 0,        z: -SU * 9, r: SU * 2.2 },
      { id: 'mid_a',     team: null, x: 0,        y: 0,        z: -SU * 4, r: SU * 2.0 },
      { id: 'center',    team: null, x: 0,        y: 0,        z:  0,      r: SU * 2.5 },
      { id: 'mid_b',     team: null, x: 0,        y: 0,        z:  SU * 4, r: SU * 2.0 },
      { id: 'spawn_b',   team: 'B',  x: 0,        y: 0,        z:  SU * 9, r: SU * 2.2 },
      { id: 'north_arc', team: null, x:  SU * 5,  y:  SU * 2,  z:  0,      r: SU * 1.8 },
      { id: 'south_arc', team: null, x: -SU * 5,  y: -SU * 2,  z:  0,      r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{ x: 0, y: 0, z: -SU * 9 }, { x: 0, y: 0, z: -SU * 4 }] },
      { path: [{ x: 0, y: 0, z: -SU * 4 }, { x: 0, y: 0, z:  0 }] },
      { path: [{ x: 0, y: 0, z:  0 },      { x: 0, y: 0, z:  SU * 4 }] },
      { path: [{ x: 0, y: 0, z:  SU * 4 }, { x: 0, y: 0, z:  SU * 9 }] },
      { path: [{ x: 0, y: 0, z: -SU * 4 }, { x:  SU * 5, y:  SU * 2, z: 0 }] },
      { path: [{ x:  SU * 5, y:  SU * 2, z: 0 }, { x: 0, y: 0, z:  SU * 4 }] },
      { path: [{ x: 0, y: 0, z: -SU * 4 }, { x: -SU * 5, y: -SU * 2, z: 0 }] },
      { path: [{ x: -SU * 5, y: -SU * 2, z: 0 }, { x: 0, y: 0, z:  SU * 4 }] },
    ],
  },

  infinity: {
    name: 'infinity',
    displayName: 'The Infinity',
    description: 'Two rings joined at a pinch. Hold the center, halve the map.',
    palette: [0x103838, 0x14383a, 0x12303a, 0x4a2818, 0x381038, 0x3a1438, 0x381432, 0x183838],
    rooms: [
      { id: 'spawn_a', team: 'A',  x: -SU * 8, y:  0,       z:  0,       r: SU * 2.2 },
      { id: 'left_n',  team: null, x: -SU * 4, y:  SU * 2,  z: -SU * 4,  r: SU * 1.8 },
      { id: 'left_s',  team: null, x: -SU * 4, y: -SU * 2,  z:  SU * 4,  r: SU * 1.8 },
      { id: 'center',  team: null, x:  0,      y:  0,       z:  0,       r: SU * 2.5 },
      { id: 'right_n', team: null, x:  SU * 4, y: -SU * 2,  z: -SU * 4,  r: SU * 1.8 },
      { id: 'right_s', team: null, x:  SU * 4, y:  SU * 2,  z:  SU * 4,  r: SU * 1.8 },
      { id: 'spawn_b', team: 'B',  x:  SU * 8, y:  0,       z:  0,       r: SU * 2.2 },
    ],
    tunnels: [
      { path: [{ x: -SU * 8, y: 0, z: 0 },              { x: -SU * 4, y:  SU * 2, z: -SU * 4 }] },
      { path: [{ x: -SU * 4, y:  SU * 2, z: -SU * 4 },  { x:  0,      y: 0,       z:  0 }] },
      { path: [{ x:  0,      y: 0,       z:  0 },       { x: -SU * 4, y: -SU * 2, z:  SU * 4 }] },
      { path: [{ x: -SU * 4, y: -SU * 2, z:  SU * 4 },  { x: -SU * 8, y: 0,       z:  0 }] },
      { path: [{ x:  SU * 8, y: 0, z: 0 },              { x:  SU * 4, y: -SU * 2, z: -SU * 4 }] },
      { path: [{ x:  SU * 4, y: -SU * 2, z: -SU * 4 },  { x:  0,      y: 0,       z:  0 }] },
      { path: [{ x:  0,      y: 0,       z:  0 },       { x:  SU * 4, y:  SU * 2, z:  SU * 4 }] },
      { path: [{ x:  SU * 4, y:  SU * 2, z:  SU * 4 },  { x:  SU * 8, y: 0,       z:  0 }] },
    ],
  },

  tower: {
    name: 'tower',
    displayName: 'The Tower',
    description: 'Vertical stack. Two layers between the spawns. Watch your six in three dimensions.',
    palette: [0x281848, 0x201840, 0x282040, 0x303030, 0x382818, 0x402818, 0x481810, 0x3a2010],
    rooms: [
      { id: 'spawn_a',  team: 'A',  x:  0,       y:  SU * 8, z:  0,       r: SU * 2.2 },
      { id: 'mid_hi_e', team: null, x:  SU * 4,  y:  SU * 4, z:  SU * 2,  r: SU * 1.8 },
      { id: 'mid_hi_w', team: null, x: -SU * 4,  y:  SU * 4, z: -SU * 2,  r: SU * 1.8 },
      { id: 'center',   team: null, x:  0,       y:  0,      z:  0,       r: SU * 2.5 },
      { id: 'mid_lo_e', team: null, x:  SU * 4,  y: -SU * 4, z: -SU * 2,  r: SU * 1.8 },
      { id: 'mid_lo_w', team: null, x: -SU * 4,  y: -SU * 4, z:  SU * 2,  r: SU * 1.8 },
      { id: 'spawn_b',  team: 'B',  x:  0,       y: -SU * 8, z:  0,       r: SU * 2.2 },
    ],
    tunnels: [
      { path: [{ x:  0, y:  SU * 8, z: 0 }, { x:  SU * 4, y:  SU * 4, z:  SU * 2 }] },
      { path: [{ x:  0, y:  SU * 8, z: 0 }, { x: -SU * 4, y:  SU * 4, z: -SU * 2 }] },
      { path: [{ x:  SU * 4, y:  SU * 4, z:  SU * 2 }, { x: -SU * 4, y:  SU * 4, z: -SU * 2 }] },
      { path: [{ x:  SU * 4, y:  SU * 4, z:  SU * 2 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: -SU * 4, y:  SU * 4, z: -SU * 2 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: 0, y: 0, z: 0 }, { x:  SU * 4, y: -SU * 4, z: -SU * 2 }] },
      { path: [{ x: 0, y: 0, z: 0 }, { x: -SU * 4, y: -SU * 4, z:  SU * 2 }] },
      { path: [{ x:  SU * 4, y: -SU * 4, z: -SU * 2 }, { x: -SU * 4, y: -SU * 4, z:  SU * 2 }] },
      { path: [{ x:  SU * 4, y: -SU * 4, z: -SU * 2 }, { x: 0, y: -SU * 8, z: 0 }] },
      { path: [{ x: -SU * 4, y: -SU * 4, z:  SU * 2 }, { x: 0, y: -SU * 8, z: 0 }] },
    ],
  },

  cross: {
    name: 'cross',
    displayName: 'The Cross',
    description: 'Compact crucible. Four arms cut by diagonals; nowhere to hide.',
    palette: [0x4a2818, 0x401818, 0x381818, 0x401010, 0x381010, 0x4a2010, 0x4a2010, 0x382010],
    rooms: [
      { id: 'center',  team: null, x:  0,       y:  0,       z:  0,       r: SU * 2.5 },
      { id: 'arm_n',   team: null, x:  0,       y:  SU * 1,  z: -SU * 4,  r: SU * 1.8 },
      { id: 'arm_s',   team: null, x:  0,       y: -SU * 1,  z:  SU * 4,  r: SU * 1.8 },
      { id: 'arm_e',   team: null, x:  SU * 4,  y:  0,       z:  0,       r: SU * 1.8 },
      { id: 'arm_w',   team: null, x: -SU * 4,  y:  0,       z:  0,       r: SU * 1.8 },
      { id: 'spawn_a', team: 'A',  x:  0,       y:  SU * 2,  z: -SU * 8,  r: SU * 2.2 },
      { id: 'spawn_b', team: 'B',  x:  0,       y: -SU * 2,  z:  SU * 8,  r: SU * 2.2 },
    ],
    tunnels: [
      { path: [{ x: 0, y: 0, z: 0 }, { x: 0, y:  SU * 1, z: -SU * 4 }] },
      { path: [{ x: 0, y: 0, z: 0 }, { x: 0, y: -SU * 1, z:  SU * 4 }] },
      { path: [{ x: 0, y: 0, z: 0 }, { x:  SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y: 0, z: 0 }, { x: -SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y:  SU * 1, z: -SU * 4 }, { x:  SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y:  SU * 1, z: -SU * 4 }, { x: -SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y: -SU * 1, z:  SU * 4 }, { x:  SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y: -SU * 1, z:  SU * 4 }, { x: -SU * 4, y: 0, z: 0 }] },
      { path: [{ x: 0, y:  SU * 1, z: -SU * 4 }, { x: 0, y:  SU * 2, z: -SU * 8 }] },
      { path: [{ x: 0, y: -SU * 1, z:  SU * 4 }, { x: 0, y: -SU * 2, z:  SU * 8 }] },
    ],
  },

  arc: {
    name: 'arc',
    displayName: 'The Arc',
    description: 'Curved approach with shortcuts over the top. Flank or get flanked.',
    palette: [0x101838, 0x182040, 0x282040, 0x481830, 0x382040, 0x282040, 0x182040, 0x101838],
    rooms: [
      { id: 'spawn_a', team: 'A',  x: -SU * 8, y:  0,      z:  SU * 3, r: SU * 2.2 },
      { id: 'arc_1',   team: null, x: -SU * 6, y:  SU * 1, z: -SU * 3, r: SU * 1.8 },
      { id: 'arc_2',   team: null, x: -SU * 3, y:  SU * 2, z: -SU * 6, r: SU * 1.8 },
      { id: 'arc_3',   team: null, x:  0,      y:  SU * 3, z: -SU * 7, r: SU * 2.0 },
      { id: 'arc_4',   team: null, x:  SU * 3, y:  SU * 2, z: -SU * 6, r: SU * 1.8 },
      { id: 'arc_5',   team: null, x:  SU * 6, y:  SU * 1, z: -SU * 3, r: SU * 1.8 },
      { id: 'spawn_b', team: 'B',  x:  SU * 8, y:  0,      z:  SU * 3, r: SU * 2.2 },
    ],
    tunnels: [
      { path: [{ x: -SU * 8, y: 0,      z:  SU * 3 }, { x: -SU * 6, y:  SU * 1, z: -SU * 3 }] },
      { path: [{ x: -SU * 6, y:  SU * 1, z: -SU * 3 }, { x: -SU * 3, y:  SU * 2, z: -SU * 6 }] },
      { path: [{ x: -SU * 3, y:  SU * 2, z: -SU * 6 }, { x:  0,      y:  SU * 3, z: -SU * 7 }] },
      { path: [{ x:  0,      y:  SU * 3, z: -SU * 7 }, { x:  SU * 3, y:  SU * 2, z: -SU * 6 }] },
      { path: [{ x:  SU * 3, y:  SU * 2, z: -SU * 6 }, { x:  SU * 6, y:  SU * 1, z: -SU * 3 }] },
      { path: [{ x:  SU * 6, y:  SU * 1, z: -SU * 3 }, { x:  SU * 8, y: 0,       z:  SU * 3 }] },
      { path: [{ x: -SU * 6, y:  SU * 1, z: -SU * 3 }, { x:  0,      y:  SU * 3, z: -SU * 7 }] },
      { path: [{ x:  0,      y:  SU * 3, z: -SU * 7 }, { x:  SU * 6, y:  SU * 1, z: -SU * 3 }] },
      { path: [{ x: -SU * 3, y:  SU * 2, z: -SU * 6 }, { x:  SU * 3, y:  SU * 2, z: -SU * 6 }] },
    ],
  },

  octahedron: {
    name: 'octahedron',
    displayName: 'The Octahedron',
    description: 'Bipyramid. Two apex spawns, four equator rooms, a central hub. Vertical and lateral, no camp.',
    palette: [0x4a3818, 0x1a2848, 0x1c2a50, 0x1a2848, 0x1c2a50, 0x1a2848, 0x1c2a50, 0x202848],
    rooms: [
      { id: 'center',  team: null, x: 0,        y: 0,        z: 0,        r: SU * 2.5 },
      { id: 'spawn_a', team: 'A',  x: 0,        y:  SU * 8,  z: 0,        r: SU * 2.2 },
      { id: 'spawn_b', team: 'B',  x: 0,        y: -SU * 8,  z: 0,        r: SU * 2.2 },
      { id: 'eq_n',    team: null, x: 0,        y: 0,        z: -SU * 6,  r: SU * 1.8 },
      { id: 'eq_e',    team: null, x:  SU * 6,  y: 0,        z: 0,        r: SU * 1.8 },
      { id: 'eq_s',    team: null, x: 0,        y: 0,        z:  SU * 6,  r: SU * 1.8 },
      { id: 'eq_w',    team: null, x: -SU * 6,  y: 0,        z: 0,        r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{ x: 0, y:  SU * 8, z: 0 }, { x: 0,        y: 0, z: -SU * 6 }] },
      { path: [{ x: 0, y:  SU * 8, z: 0 }, { x:  SU * 6,  y: 0, z: 0 }] },
      { path: [{ x: 0, y:  SU * 8, z: 0 }, { x: 0,        y: 0, z:  SU * 6 }] },
      { path: [{ x: 0, y:  SU * 8, z: 0 }, { x: -SU * 6,  y: 0, z: 0 }] },
      { path: [{ x: 0, y: -SU * 8, z: 0 }, { x: 0,        y: 0, z: -SU * 6 }] },
      { path: [{ x: 0, y: -SU * 8, z: 0 }, { x:  SU * 6,  y: 0, z: 0 }] },
      { path: [{ x: 0, y: -SU * 8, z: 0 }, { x: 0,        y: 0, z:  SU * 6 }] },
      { path: [{ x: 0, y: -SU * 8, z: 0 }, { x: -SU * 6,  y: 0, z: 0 }] },
      { path: [{ x: 0,        y: 0, z: -SU * 6 }, { x:  SU * 6,  y: 0, z: 0 }] },
      { path: [{ x:  SU * 6,  y: 0, z: 0 },        { x: 0,        y: 0, z:  SU * 6 }] },
      { path: [{ x: 0,        y: 0, z:  SU * 6 }, { x: -SU * 6,  y: 0, z: 0 }] },
      { path: [{ x: -SU * 6,  y: 0, z: 0 },        { x: 0,        y: 0, z: -SU * 6 }] },
      { path: [{ x: 0, y:  SU * 8, z: 0 }, { x: 0, y: 0, z: 0 }] },
      { path: [{ x: 0, y: 0,       z: 0 }, { x: 0, y: -SU * 8, z: 0 }] },
    ],
  },

  pentagon: {
    name: 'pentagon',
    displayName: 'The Pentagon',
    description: 'Pentagonal bipyramid. Two apex spawns, five ring rooms, no hub. Every path crosses the ring.',
    palette: [0x4a2a10, 0x3a2818, 0x4a3820, 0x3a2810, 0x4a2a18, 0x4a3820, 0x3a2818, 0x4a2a10],
    rooms: [
      { id: 'spawn_a', team: 'A',  x: 0,             y:  SU * 7,  z: 0,             r: SU * 2.2 },
      { id: 'spawn_b', team: 'B',  x: 0,             y: -SU * 7,  z: 0,             r: SU * 2.2 },
      { id: 'p0',      team: null, x:  SU *  6.000,  y: 0,        z:  SU *  0.000,  r: SU * 1.8 },
      { id: 'p1',      team: null, x:  SU *  1.854,  y: 0,        z:  SU *  5.706,  r: SU * 1.8 },
      { id: 'p2',      team: null, x: -SU *  4.854,  y: 0,        z:  SU *  3.527,  r: SU * 1.8 },
      { id: 'p3',      team: null, x: -SU *  4.854,  y: 0,        z: -SU *  3.527,  r: SU * 1.8 },
      { id: 'p4',      team: null, x:  SU *  1.854,  y: 0,        z: -SU *  5.706,  r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{ x: 0, y:  SU * 7, z: 0 }, { x:  SU * 6.000, y: 0, z:  SU * 0.000 }] },
      { path: [{ x: 0, y:  SU * 7, z: 0 }, { x:  SU * 1.854, y: 0, z:  SU * 5.706 }] },
      { path: [{ x: 0, y:  SU * 7, z: 0 }, { x: -SU * 4.854, y: 0, z:  SU * 3.527 }] },
      { path: [{ x: 0, y:  SU * 7, z: 0 }, { x: -SU * 4.854, y: 0, z: -SU * 3.527 }] },
      { path: [{ x: 0, y:  SU * 7, z: 0 }, { x:  SU * 1.854, y: 0, z: -SU * 5.706 }] },
      { path: [{ x: 0, y: -SU * 7, z: 0 }, { x:  SU * 6.000, y: 0, z:  SU * 0.000 }] },
      { path: [{ x: 0, y: -SU * 7, z: 0 }, { x:  SU * 1.854, y: 0, z:  SU * 5.706 }] },
      { path: [{ x: 0, y: -SU * 7, z: 0 }, { x: -SU * 4.854, y: 0, z:  SU * 3.527 }] },
      { path: [{ x: 0, y: -SU * 7, z: 0 }, { x: -SU * 4.854, y: 0, z: -SU * 3.527 }] },
      { path: [{ x: 0, y: -SU * 7, z: 0 }, { x:  SU * 1.854, y: 0, z: -SU * 5.706 }] },
      { path: [{ x:  SU * 6.000, y: 0, z:  SU * 0.000 }, { x:  SU * 1.854, y: 0, z:  SU * 5.706 }] },
      { path: [{ x:  SU * 1.854, y: 0, z:  SU * 5.706 }, { x: -SU * 4.854, y: 0, z:  SU * 3.527 }] },
      { path: [{ x: -SU * 4.854, y: 0, z:  SU * 3.527 }, { x: -SU * 4.854, y: 0, z: -SU * 3.527 }] },
      { path: [{ x: -SU * 4.854, y: 0, z: -SU * 3.527 }, { x:  SU * 1.854, y: 0, z: -SU * 5.706 }] },
      { path: [{ x:  SU * 1.854, y: 0, z: -SU * 5.706 }, { x:  SU * 6.000, y: 0, z:  SU * 0.000 }] },
    ],
  },

  gyre: {
    name: 'gyre',
    displayName: 'The Gyre',
    description: 'Helix. Spawns at the poles, five spiral rooms climbing Y. Long main path with chord shortcuts.',
    palette: [0x2a1848, 0x1a2848, 0x301848, 0x183848, 0x281a48, 0x183048, 0x2a1848, 0x1a2a48],
    rooms: [
      { id: 'spawn_a', team: 'A',  x: 0,             y: -SU * 7,  z: 0,             r: SU * 2.2 },
      { id: 'spawn_b', team: 'B',  x: 0,             y:  SU * 7,  z: 0,             r: SU * 2.2 },
      { id: 'g1',      team: null, x:  SU *  5.000,  y: -SU * 4,  z:  SU *  0.000,  r: SU * 1.8 },
      { id: 'g2',      team: null, x:  SU *  1.545,  y: -SU * 2,  z:  SU *  4.755,  r: SU * 1.8 },
      { id: 'g3',      team: null, x: -SU *  4.045,  y: 0,        z:  SU *  2.939,  r: SU * 2.0 },
      { id: 'g4',      team: null, x: -SU *  4.045,  y:  SU * 2,  z: -SU *  2.939,  r: SU * 1.8 },
      { id: 'g5',      team: null, x:  SU *  1.545,  y:  SU * 4,  z: -SU *  4.755,  r: SU * 1.8 },
    ],
    tunnels: [
      { path: [{ x: 0,             y: -SU * 7, z: 0 },            { x:  SU * 5.000, y: -SU * 4, z:  SU * 0.000 }] },
      { path: [{ x:  SU * 5.000,   y: -SU * 4, z:  SU * 0.000 },  { x:  SU * 1.545, y: -SU * 2, z:  SU * 4.755 }] },
      { path: [{ x:  SU * 1.545,   y: -SU * 2, z:  SU * 4.755 },  { x: -SU * 4.045, y: 0,       z:  SU * 2.939 }] },
      { path: [{ x: -SU * 4.045,   y: 0,       z:  SU * 2.939 },  { x: -SU * 4.045, y:  SU * 2, z: -SU * 2.939 }] },
      { path: [{ x: -SU * 4.045,   y:  SU * 2, z: -SU * 2.939 },  { x:  SU * 1.545, y:  SU * 4, z: -SU * 4.755 }] },
      { path: [{ x:  SU * 1.545,   y:  SU * 4, z: -SU * 4.755 },  { x: 0,           y:  SU * 7, z: 0 }] },
      { path: [{ x: 0,             y: -SU * 7, z: 0 },            { x: -SU * 4.045, y: 0,       z:  SU * 2.939 }] },
      { path: [{ x: -SU * 4.045,   y: 0,       z:  SU * 2.939 },  { x: 0,           y:  SU * 7, z: 0 }] },
      { path: [{ x:  SU * 5.000,   y: -SU * 4, z:  SU * 0.000 },  { x: -SU * 4.045, y:  SU * 2, z: -SU * 2.939 }] },
      { path: [{ x:  SU * 1.545,   y: -SU * 2, z:  SU * 4.755 },  { x:  SU * 1.545, y:  SU * 4, z: -SU * 4.755 }] },
    ],
  },
};

export const MAP_KEYS = Object.keys(MAP_DEFS);

export function buildLevel(mapKey?: string): Level {
  const key = (mapKey && MAP_DEFS[mapKey]) ? mapKey : 'hourglass';
  return _buildLevelFromDef(MAP_DEFS[key]);
}

function _buildLevelFromDef(def: MapDef): Level {
  const rooms: Room[] = def.rooms.map(r => ({
    id: r.id, team: r.team,
    center: { x: r.x, y: r.y, z: r.z },
    radius: r.r,
  }));

  // Each tunnel is a path of N waypoints; expand to N-1 cylinder segments.
  // The SDF and the marching cubes worker both treat tunnels as flat lists
  // of cylinder segments, so paths are an authoring convenience that gets
  // flattened here.
  const tunnels: Tunnel[] = [];
  for (const t of def.tunnels) {
    const r = t.r != null ? t.r : TUNNEL_R;
    for (let i = 0; i < t.path.length - 1; i++) {
      const a = t.path[i], b = t.path[i + 1];
      const dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z;
      if (dx * dx + dy * dy + dz * dz < 100) continue; // skip near-zero segments
      tunnels.push({
        a: { x: a.x, y: a.y, z: a.z },
        b: { x: b.x, y: b.y, z: b.z },
        radius: r,
      });
    }
  }

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
    displayName: def.displayName,
    description: def.description,
    palette: def.palette.slice(),
    bounds, rooms, tunnels,
    obstacles: def.obstacles || [],
    spawnA, spawnB,
    sdfSmoothK: SDF_SMOOTH_K,
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
// Smooth-min radius. Match LSS exactly (45 with SU=150). Bigger k = softer
// blend (more rounded junctions); smaller k = sharper. Travels on the wire
// as level.sdfSmoothK so the client's marching cubes pass agrees with the
// server's collision SDF; if they diverge, players see one wall but collide
// with another.
const SDF_SMOOTH_K = 45;

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
