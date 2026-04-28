/*
  LSS server-sim ; main entry (v8.18) ; round-win + match-end + reload

  Server-authoritative simulation. Bun WebSocket server. One simulation
  runs at 64 Hz; clients send inputs, receive state snapshots, render
  locally. No host election, no peer-to-peer, no Trystero.

  Run:
    bun run server-sim/main.ts

  Then point browsers at:
    http://localhost:8090
*/

import os from 'node:os';
import path from 'node:path';
import type { ServerWebSocket } from 'bun';

import {
  createSim, addPlayer, removePlayer, tick, snapshot, startMatch, resetMatch,
  spawnBotsToFillTeams, clearAllBots,
  applyPlayerLoadout, switchPlayerTeam, ensurePlayerHasLoadout,
  respawnAllPlayers,
  TEAM_A, TEAM_B,
  type PlayerInput, type SimState,
} from './simulation.ts';
import { LOADOUT_KEYS, LOADOUTS } from './loadouts.ts';
import { buildLevel, MAP_KEYS } from './level.ts';

type ClientData = { peerId: string };
type Client = ServerWebSocket<ClientData>;

const PORT = Number(process.env.PORT) || 8090;
const HOSTNAME = process.env.HOSTNAME || '0.0.0.0';
const TICK_HZ = 128;
const STATE_HZ = 64;            // v8.1: bumped from 64/32 to 128/64

const WEB_ROOT = path.resolve(import.meta.dir, '..');

const clients = new Map<string, Client>();
let nextPeerId = 1;

function genPeerId(): string {
  const id = (nextPeerId++).toString(36).padStart(4, '0');
  return 'p' + id;
}

// ---- Simulation state ----

// v8.7: server starts on first map; rotates each fresh-match.
let _mapIndex = 0;
let level = buildLevel(MAP_KEYS[_mapIndex]);
const sim: SimState = createSim(level);
const inputs = new Map<string, PlayerInput>();      // peerId -> latest input received

// Per-peer team-balance counter (alternate teams as players join).
let nextTeamCounter = 0;

function pickTeam(): number {
  const t = (nextTeamCounter % 2 === 0) ? TEAM_A : TEAM_B;
  nextTeamCounter++;
  return t;
}

// ---- Wire helpers ----

function send(client: Client, obj: unknown): void {
  try { client.send(JSON.stringify(obj)); } catch { /* dropped */ }
}

function broadcast(obj: unknown, except?: Client): void {
  const msg = JSON.stringify(obj);
  for (const c of clients.values()) {
    if (c === except) continue;
    try { c.send(msg); } catch { /* dropped */ }
  }
}

function broadcastState(): void {
  const snap = snapshot(sim);
  broadcast({ type: 'state', payload: snap });
}

// ---- Tick loop ----

function _allHumansReady(): boolean {
  if (sim.players.size === 0) return false;
  for (const p of sim.players.values()) {
    if (!p.ready) return false;
  }
  return true;
}

function _tickLoopExtras(): void {
  // Lobby -> Warmup transition.
  if (sim.match.state === 'select' && _allHumansReady()) {
    // v8.7: rotate to next map for variety.
    _mapIndex = (_mapIndex + 1) % MAP_KEYS.length;
    const newKey = MAP_KEYS[_mapIndex];
    sim.level = buildLevel(newKey);
    level = sim.level;
    for (const p of sim.players.values()) ensurePlayerHasLoadout(p);
    // v8.8.1: must reposition existing players to the new level's spawn
    // pool BEFORE startMatch ; otherwise they're outside the new envelope
    // and the collision pass pushes them around erratically.
    respawnAllPlayers(sim);
    startMatch(sim, (Math.random() * 0xFFFFFFFF) | 0, sim.level.name);
    clearAllBots(sim);
    spawnBotsToFillTeams(sim);
    // Push the new level data to every client so they rebuild meshes.
    const lvlMsg = JSON.stringify({ type: 'level', level: sim.level });
    for (const c of clients.values()) { try { c.send(lvlMsg); } catch { /* drop */ } }
    console.log('[match] all ready ; SELECT -> WARMUP  round=' + sim.match.currentRound + '  map=' + newKey + '  peers=' + sim.players.size);
    broadcast({ type: 'state', payload: snapshot(sim) });
  }
}

let lastTickMs = Date.now();
setInterval(() => {
  const now = Date.now();
  const dt = (now - lastTickMs) / 1000;
  lastTickMs = now;
  tick(sim, inputs, dt);
  _tickLoopExtras();
}, Math.round(1000 / TICK_HZ));

setInterval(broadcastState, Math.round(1000 / STATE_HZ));

// ---- Static file serving ----

const MIME: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.glb':  'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.wav':  'audio/wav',
  '.mp3':  'audio/mpeg',
  '.ogg':  'audio/ogg',
};

function resolveSafe(urlPath: string): string | null {
  if (urlPath === '/' || urlPath === '/index.html') {
    urlPath = '/last_ship_sailing_sim.html';
  }
  const decoded = decodeURIComponent(urlPath);
  const rel = decoded.replace(/^\/+/, '').replace(/\\/g, '/');
  const abs = path.resolve(WEB_ROOT, rel);
  if (!abs.startsWith(WEB_ROOT)) return null;
  return abs;
}

// ---- Bun server ----

const server = Bun.serve<ClientData>({
  port: PORT,
  hostname: HOSTNAME,
  async fetch(req, server) {
    const url = new URL(req.url);

    if (url.pathname === '/socket') {
      const peerId = genPeerId();
      const upgraded = server.upgrade(req, { data: { peerId } });
      if (upgraded) return undefined;
      return new Response('WebSocket upgrade failed', { status: 400 });
    }

    if (url.pathname === '/health') {
      const players: any[] = [];
      for (const p of sim.players.values()) {
        players.push({ peerId: p.peerId, team: p.team, position: p.position, health: p.health });
      }
      return new Response(JSON.stringify({
        ok: true,
        clients: clients.size,
        match: sim.match,
        players,
        bots: Array.from(sim.bots.values()).map(b => ({ id: b.id, team: b.team, loadoutKey: b.loadoutKey, position: b.position, health: b.health, alive: b.alive })),
        projectiles: sim.projectiles.size,
        tick: sim.tick,
        uptimeSeconds: Math.floor(process.uptime()),
      }), { headers: { 'content-type': 'application/json' } });
    }

    const abs = resolveSafe(url.pathname);
    if (!abs) return new Response('Bad request', { status: 400 });
    const file = Bun.file(abs);
    if (!(await file.exists())) {
      return new Response('Not found: ' + url.pathname, { status: 404 });
    }
    const ext = path.extname(abs).toLowerCase();
    const headers: Record<string, string> = { 'cache-control': 'no-cache' };
    if (MIME[ext]) headers['content-type'] = MIME[ext];
    return new Response(file, { headers });
  },

  websocket: {
    open(ws) {
      const peerId = ws.data.peerId;
      const team = pickTeam();
      const player = addPlayer(sim, peerId, team);
      clients.set(peerId, ws);
      // Send hello + level data so the client can set up its scene.
      send(ws, {
        type: 'hello',
        myPeerId: peerId,
        myEntityId: player.id,
        team: player.team,
        level,
        tickHz: TICK_HZ,
      });
      // Send an immediate state snapshot so the new client sees everyone.
      send(ws, { type: 'state', payload: snapshot(sim) });
      console.log('[connect]    ' + peerId + '  team=' + (team === TEAM_A ? 'A' : 'B') + '  (clients: ' + clients.size + ')');
      // v8.4: don't auto-start. Server is in 'select' state; player picks
      // loadout in the lobby and clicks ready, then once all peers are
      // ready the tickLoopExtras() helper transitions to 'warmup'.
      // For convenience send a fresh snapshot now so the client renders.
      broadcast({ type: 'state', payload: snapshot(sim) });
    },

    message(ws, message) {
      const peerId = ws.data.peerId;
      let data: any;
      try {
        data = typeof message === 'string'
          ? JSON.parse(message)
          : JSON.parse(new TextDecoder().decode(message));
      } catch { return; }

      if (data && data.type === 'input' && data.payload) {
        const p = data.payload;
        // v8.8: ability press is one-shot per frame. Client re-sends null
        // by default; only sets a slot index on the rising-edge frame.
        let abilityPress: number | null = null;
        if (typeof p.abilityPress === 'number' && p.abilityPress >= 0 && p.abilityPress <= 3) {
          abilityPress = p.abilityPress | 0;
        }
        const inp: PlayerInput = {
          forward: clamp(toNum(p.forward), -1, 1),
          right:   clamp(toNum(p.right),   -1, 1),
          up:      clamp(toNum(p.up),      -1, 1),
          yaw:     toNum(p.yaw),
          pitch:   clamp(toNum(p.pitch), -Math.PI / 2, Math.PI / 2),
          fire:    !!p.fire,
          abilityPress,
          reload:  !!p.reload,    // v8.33: manual R-key reload edge.
          dash:    !!p.dash,      // v8.44: dash key (Shift) edge.
          tick:    typeof p.tick === 'number' ? p.tick : undefined,
        };
        inputs.set(peerId, inp);
        return;
      }

      // v8.4 lobby actions ; only valid in 'select' state.
      if (data && data.type === 'set-loadout' && data.payload) {
        if (sim.match.state !== 'select') return;
        const player = sim.players.get(peerId);
        if (!player) return;
        const key = String(data.payload.loadoutKey || '');
        if (!LOADOUT_KEYS.includes(key as any)) return;
        applyPlayerLoadout(player, key);
        return;
      }
      if (data && data.type === 'switch-team') {
        if (sim.match.state !== 'select') return;
        const player = sim.players.get(peerId);
        if (!player) return;
        switchPlayerTeam(sim, player);
        return;
      }
      if (data && data.type === 'set-ready' && data.payload) {
        if (sim.match.state !== 'select') return;
        const player = sim.players.get(peerId);
        if (!player) return;
        player.ready = !!data.payload.ready;
        return;
      }

      // v8.49: NA23 ; ping/pong for client RTT measurement. Echo back the
      // client's `t` so they can compute round-trip time.
      if (data && data.type === 'ping') {
        send(ws, { type: 'pong', t: data.t });
        return;
      }
    },

    close(ws, code, reason) {
      const peerId = ws.data.peerId;
      clients.delete(peerId);
      removePlayer(sim, peerId);
      inputs.delete(peerId);
      broadcast({ type: 'peer-leave', peerId });
      console.log('[disconnect] ' + peerId + '  (clients: ' + clients.size + ')'
        + (reason ? '  reason: ' + reason : ''));
      // If everyone has left, reset the match.
      if (clients.size === 0) {
        resetMatch(sim);
        clearAllBots(sim);
        sim.projectiles.clear();
      }
    },
  },
});

// ---- Util ----

function toNum(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}
function clamp(n: number, lo: number, hi: number): number {
  return n < lo ? lo : n > hi ? hi : n;
}

function getLanIp(): string {
  const ifaces = os.networkInterfaces();
  for (const iface of Object.values(ifaces)) {
    if (!iface) continue;
    for (const addr of iface) {
      if (addr.family === 'IPv4' && !addr.internal) return addr.address;
    }
  }
  return 'localhost';
}

// ---- Boot banner ----

console.log('');
console.log('===========================================');
console.log('  Last Ship Sailing ; server-sim (v8.0)');
console.log('===========================================');
console.log('  Same machine:  http://localhost:' + server.port);
console.log('  LAN devices:   http://' + getLanIp() + ':' + server.port);
console.log('  Health check:  http://localhost:' + server.port + '/health');
console.log('  WebSocket:     ws://localhost:' + server.port + '/socket');
console.log('===========================================');
console.log('  Authoritative simulation: ' + TICK_HZ + ' Hz tick, ' + STATE_HZ + ' Hz broadcast');
console.log('  Players send inputs; server holds state.');
console.log('  Press Ctrl+C to stop.');
console.log('');
