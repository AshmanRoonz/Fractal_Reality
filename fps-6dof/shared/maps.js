/**
 * LSS (Last Ship Sailing) - Map Definitions
 * Shared between Node.js server and browser client.
 * Includes handcrafted maps and procedural generation.
 */

const SU = 150; // Ship Unit

// Handcrafted map: Circumpunct
// Central arena with 4 satellite rooms (2 spawns, 2 ready zones) connected via curved tunnels.
const CIRCUMPUNCT_MAP = {
  key: 'circumpunct',
  name: 'Circumpunct',
  description: 'Symmetrical arena with central nexus and four satellite chambers.',
  procedural: false,
  rooms: [
    {
      id: 'center',
      name: 'Central Nexus',
      x: 0,
      y: 0,
      z: 0,
      radius: SU * 3.5,
      type: 'combat',
    },
    {
      id: 'spawn_a',
      name: 'Spawn Alpha',
      x: -SU * 9,
      y: 0,
      z: -SU * 4,
      radius: SU * 2.5,
      type: 'spawn',
      team: 'A',
    },
    {
      id: 'spawn_b',
      name: 'Spawn Bravo',
      x: SU * 9,
      y: 0,
      z: -SU * 4,
      radius: SU * 2.5,
      type: 'spawn',
      team: 'B',
    },
    {
      id: 'ready_a',
      name: 'Ready Room Alpha',
      x: -SU * 5,
      y: 0,
      z: SU * 7,
      radius: SU * 2.5,
      type: 'ready',
      team: 'A',
    },
    {
      id: 'ready_b',
      name: 'Ready Room Bravo',
      x: SU * 5,
      y: 0,
      z: SU * 7,
      radius: SU * 2.5,
      type: 'ready',
      team: 'B',
    },
  ],
  tunnels: [
    // From spawn_a to center (curved path)
    {
      id: 'tunnel_spawn_a_center_0',
      from: 'spawn_a',
      to: 'center',
      radius: SU * 2.0,
      points: [
        { x: -SU * 9, y: 0, z: -SU * 4 },
        { x: -SU * 6, y: SU * 1.5, z: -SU * 2 },
        { x: -SU * 3, y: 0, z: -SU * 0.5 },
        { x: 0, y: 0, z: 0 },
      ],
    },
    // From spawn_b to center (curved path)
    {
      id: 'tunnel_spawn_b_center_0',
      from: 'spawn_b',
      to: 'center',
      radius: SU * 2.0,
      points: [
        { x: SU * 9, y: 0, z: -SU * 4 },
        { x: SU * 6, y: SU * 1.5, z: -SU * 2 },
        { x: SU * 3, y: 0, z: -SU * 0.5 },
        { x: 0, y: 0, z: 0 },
      ],
    },
    // From center to ready_a
    {
      id: 'tunnel_center_ready_a_0',
      from: 'center',
      to: 'ready_a',
      radius: SU * 1.8,
      points: [
        { x: 0, y: 0, z: 0 },
        { x: -SU * 2, y: SU * 2, z: SU * 4 },
        { x: -SU * 5, y: 0, z: SU * 7 },
      ],
    },
    // From center to ready_b
    {
      id: 'tunnel_center_ready_b_0',
      from: 'center',
      to: 'ready_b',
      radius: SU * 1.8,
      points: [
        { x: 0, y: 0, z: 0 },
        { x: SU * 2, y: SU * 2, z: SU * 4 },
        { x: SU * 5, y: 0, z: SU * 7 },
      ],
    },
    // Direct path: ready_a to ready_b
    {
      id: 'tunnel_ready_a_ready_b_0',
      from: 'ready_a',
      to: 'ready_b',
      radius: SU * 1.6,
      points: [
        { x: -SU * 5, y: 0, z: SU * 7 },
        { x: 0, y: SU * 1, z: SU * 7.5 },
        { x: SU * 5, y: 0, z: SU * 7 },
      ],
    },
  ],
};

// Handcrafted map: Nexus / Hourglass
// Hexagonal ring of 6 rooms plus central hub. Spawn rooms at poles.
const NEXUS_MAP = {
  key: 'hourglass',
  name: 'Nexus',
  description: 'Hexagonal ring arena with central hub and polar spawn chambers.',
  procedural: false,
  rooms: [
    {
      id: 'center',
      name: 'Central Hub',
      x: 0,
      y: 0,
      z: 0,
      radius: SU * 2.5,
      type: 'combat',
    },
    {
      id: 'spawn_a',
      name: 'Spawn Alpha',
      x: 0,
      y: 0,
      z: -SU * 8,
      radius: SU * 2.2,
      type: 'spawn',
      team: 'A',
    },
    {
      id: 'spawn_b',
      name: 'Spawn Bravo',
      x: 0,
      y: 0,
      z: SU * 8,
      radius: SU * 2.2,
      type: 'spawn',
      team: 'B',
    },
    // 6 hexagon rooms around the ring (60 degree intervals on circle r=SU*7)
    {
      id: 'ne_upper',
      name: 'Northeast Chamber',
      x: SU * 7 * Math.cos(Math.PI / 6),
      y: SU * 2,
      z: -SU * 7 * Math.sin(Math.PI / 6),
      radius: SU * 1.8,
      type: 'combat',
    },
    {
      id: 'se_upper',
      name: 'Southeast Chamber',
      x: SU * 7 * Math.cos(-Math.PI / 6),
      y: -SU * 2,
      z: -SU * 7 * Math.sin(-Math.PI / 6),
      radius: SU * 1.8,
      type: 'combat',
    },
    {
      id: 'se_lower',
      name: 'South Chamber',
      x: SU * 7,
      y: -SU * 2,
      z: SU * 4,
      radius: SU * 1.8,
      type: 'combat',
    },
    {
      id: 'sw_lower',
      name: 'Southwest Chamber',
      x: -SU * 7,
      y: -SU * 2,
      z: SU * 4,
      radius: SU * 1.8,
      type: 'combat',
    },
    {
      id: 'nw_upper',
      name: 'Northwest Chamber',
      x: -SU * 7 * Math.cos(Math.PI / 6),
      y: SU * 2,
      z: -SU * 7 * Math.sin(Math.PI / 6),
      radius: SU * 1.8,
      type: 'combat',
    },
    {
      id: 'nw_lower',
      name: 'North Chamber',
      x: -SU * 7,
      y: SU * 2,
      z: -SU * 4,
      radius: SU * 1.8,
      type: 'combat',
    },
  ],
  tunnels: [
    // Spokes from center to each hex room (6 spokes)
    { id: 'spoke_center_ne', from: 'center', to: 'ne_upper', radius: SU * 1.5 },
    { id: 'spoke_center_se_u', from: 'center', to: 'se_upper', radius: SU * 1.5 },
    { id: 'spoke_center_se_l', from: 'center', to: 'se_lower', radius: SU * 1.5 },
    { id: 'spoke_center_sw', from: 'center', to: 'sw_lower', radius: SU * 1.5 },
    { id: 'spoke_center_nw_l', from: 'center', to: 'nw_lower', radius: SU * 1.5 },
    { id: 'spoke_center_nw_u', from: 'center', to: 'nw_upper', radius: SU * 1.5 },

    // Ring connections (outer hex perimeter)
    { id: 'ring_ne_se_u', from: 'ne_upper', to: 'se_upper', radius: SU * 1.4 },
    { id: 'ring_se_u_se_l', from: 'se_upper', to: 'se_lower', radius: SU * 1.4 },
    { id: 'ring_se_l_sw', from: 'se_lower', to: 'sw_lower', radius: SU * 1.4 },
    { id: 'ring_sw_nw_l', from: 'sw_lower', to: 'nw_lower', radius: SU * 1.4 },
    { id: 'ring_nw_l_nw_u', from: 'nw_lower', to: 'nw_upper', radius: SU * 1.4 },
    { id: 'ring_nw_u_ne', from: 'nw_upper', to: 'ne_upper', radius: SU * 1.4 },

    // Spawn to center (polar axis)
    { id: 'tunnel_spawn_a_center', from: 'spawn_a', to: 'center', radius: SU * 2.0 },
    { id: 'tunnel_spawn_b_center', from: 'spawn_b', to: 'center', radius: SU * 2.0 },
  ],
};

// Procedural map flag and generator
const PROCEDURAL_MAP = {
  key: 'procedural',
  name: 'Deep Random',
  description: 'Procedurally generated. New layout every match.',
  procedural: true,
};

/**
 * generateProceduralMap(): creates a new procedural map
 * Returns a MAP_DATA object suitable for play.
 *
 * Layout:
 * - 5-7 rooms total
 * - Spawn rooms on opposite sides (z: ±(SU*8 + random*SU*3))
 * - 1-3 neutral combat rooms scattered between
 * - MST connectivity (Prim's algorithm)
 * - Additional edges until every room has 2+ connections
 * - 1-2 random loop edges for emergent alternate routes
 * - Tunnels with variable radius (SU*1.5 to SU*2)
 * - Long tunnels (>SU*8) get curved midpoints
 */
function generateProceduralMap(seed) {
  // Seeded RNG for reproducibility (optional; server can pass seed)
  const rng = seed !== undefined ? seededRandom(seed) : Math.random;

  const roomCount = 5 + Math.floor(rng() * 3); // 5-7 rooms
  const rooms = [];
  const roomIds = [];

  // Spawn rooms (poles)
  const spawnAZ = -(SU * 8 + rng() * SU * 3);
  const spawnBZ = SU * 8 + rng() * SU * 3;

  rooms.push({
    id: 'spawn_a',
    name: 'Spawn Alpha',
    x: (rng() - 0.5) * SU,
    y: (rng() - 0.5) * SU * 0.5,
    z: spawnAZ,
    radius: SU * 2.2,
    type: 'spawn',
    team: 'A',
  });
  roomIds.push('spawn_a');

  rooms.push({
    id: 'spawn_b',
    name: 'Spawn Bravo',
    x: (rng() - 0.5) * SU,
    y: (rng() - 0.5) * SU * 0.5,
    z: spawnBZ,
    radius: SU * 2.2,
    type: 'spawn',
    team: 'B',
  });
  roomIds.push('spawn_b');

  // Combat/neutral rooms scattered between spawns
  for (let i = 2; i < roomCount; i++) {
    rooms.push({
      id: `room_${i}`,
      name: `Chamber ${String.fromCharCode(67 + i - 2)}`, // C, D, E, ...
      x: (rng() - 0.5) * SU * 12,
      y: (rng() - 0.5) * SU * 4,
      z: (rng() - 0.5) * SU * 12,
      radius: SU * (1.5 + rng() * 1.0),
      type: 'combat',
    });
    roomIds.push(`room_${i}`);
  }

  // Build MST (Prim's algorithm) for connectivity
  const edges = [];
  const inMST = new Set(['spawn_a']);
  const outMST = new Set(roomIds.slice(1));

  while (outMST.size > 0) {
    let bestEdge = null;
    let bestDist = Infinity;

    for (const u of inMST) {
      for (const v of outMST) {
        const uRoom = rooms.find(r => r.id === u);
        const vRoom = rooms.find(r => r.id === v);
        const dx = uRoom.x - vRoom.x;
        const dy = uRoom.y - vRoom.y;
        const dz = uRoom.z - vRoom.z;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < bestDist) {
          bestDist = dist;
          bestEdge = [u, v];
        }
      }
    }

    if (bestEdge) {
      edges.push(bestEdge);
      inMST.add(bestEdge[1]);
      outMST.delete(bestEdge[1]);
    }
  }

  // Add edges until every room has 2+ connections
  let edgeSet = new Set(edges.map(e => JSON.stringify([e[0], e[1]])));
  const degree = {};
  roomIds.forEach(id => (degree[id] = 0));
  edges.forEach(([u, v]) => {
    degree[u]++;
    degree[v]++;
  });

  for (const id of roomIds) {
    if (degree[id] < 2) {
      for (const otherId of roomIds) {
        if (id !== otherId && degree[otherId] < 3) {
          const key = JSON.stringify([id, otherId].sort());
          if (!edgeSet.has(key)) {
            edges.push([id, otherId]);
            edgeSet.add(key);
            degree[id]++;
            degree[otherId]++;
            if (degree[id] >= 2) break;
          }
        }
      }
    }
  }

  // Add 1-2 random loop edges for alternate routes
  const loopCount = rng() < 0.5 ? 1 : 2;
  for (let i = 0; i < loopCount; i++) {
    const u = roomIds[Math.floor(rng() * roomIds.length)];
    const v = roomIds[Math.floor(rng() * roomIds.length)];
    if (u !== v) {
      const key = JSON.stringify([u, v].sort());
      if (!edgeSet.has(key)) {
        edges.push([u, v]);
        edgeSet.add(key);
      }
    }
  }

  // Build tunnels from edges
  const tunnels = [];
  let tunnelIdx = 0;

  for (const [fromId, toId] of edges) {
    const fromRoom = rooms.find(r => r.id === fromId);
    const toRoom = rooms.find(r => r.id === toId);
    const dx = toRoom.x - fromRoom.x;
    const dy = toRoom.y - fromRoom.y;
    const dz = toRoom.z - fromRoom.z;
    const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

    const tunnelRadius = SU * (1.5 + rng() * 0.5); // Variable width

    const tunnel = {
      id: `tunnel_${tunnelIdx++}`,
      from: fromId,
      to: toId,
      radius: tunnelRadius,
      points: [
        { x: fromRoom.x, y: fromRoom.y, z: fromRoom.z },
      ],
    };

    // Add curved midpoint for long tunnels
    if (distance > SU * 8) {
      const midX = (fromRoom.x + toRoom.x) / 2 + (rng() - 0.5) * SU * 2;
      const midY = (fromRoom.y + toRoom.y) / 2 + (rng() - 0.5) * SU;
      const midZ = (fromRoom.z + toRoom.z) / 2 + (rng() - 0.5) * SU * 2;
      tunnel.points.push({ x: midX, y: midY, z: midZ });
    }

    tunnel.points.push({ x: toRoom.x, y: toRoom.y, z: toRoom.z });
    tunnels.push(tunnel);
  }

  return {
    key: 'procedural_' + seed,
    name: 'Deep Random',
    description: 'Procedurally generated arena.',
    procedural: true,
    rooms,
    tunnels,
  };
}

/**
 * seededRandom(seed): simple seeded RNG
 * Returns a function that generates deterministic pseudo-random [0,1) values.
 */
function seededRandom(seed) {
  return function() {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
}

const MAP_DATA = {
  'circumpunct': CIRCUMPUNCT_MAP,
  'hourglass': NEXUS_MAP,
  'procedural': PROCEDURAL_MAP,
};

/**
 * getMap(key): retrieve a map by key; generate procedural if needed
 */
function getMap(key) {
  if (MAP_DATA[key]) {
    return MAP_DATA[key];
  }
  if (key === 'procedural' || key.startsWith('procedural_')) {
    const seed = key.startsWith('procedural_') ? parseInt(key.split('_')[1]) : Date.now();
    return generateProceduralMap(seed);
  }
  return CIRCUMPUNCT_MAP; // default fallback
}

// Dual-environment export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SU,
    MAP_DATA,
    CIRCUMPUNCT_MAP,
    NEXUS_MAP,
    PROCEDURAL_MAP,
    generateProceduralMap,
    getMap,
  };
} else {
  window.LSS_SHARED = window.LSS_SHARED || {};
  Object.assign(window.LSS_SHARED, {
    SU,
    MAP_DATA,
    CIRCUMPUNCT_MAP,
    NEXUS_MAP,
    PROCEDURAL_MAP,
    generateProceduralMap,
    getMap,
  });
}
