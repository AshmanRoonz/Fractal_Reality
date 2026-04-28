/*
  Last Ship Sailing ; local-host server (v7.3)
  Created: 2026-04-25
  Last updated: 2026-04-25
  Version: 7.3

  WebSocket relay + static file server + match-state authority. Runs on Bun.
  Single-room model: every connected client is in the same match.

  v7.3 (this version) adds match-state authority on top of the v7.0 relay.
  Server is now the canonical source of truth for: state ('select' / 'warmup'
  / 'playing' / 'roundEnd'), seed (32-bit int generated when match starts),
  selectedMap (string key), warmupTimer (seconds), roundTimer (seconds),
  currentRound, scoreA, scoreB. Clients consume `{type: 'match-state', ...}`
  broadcasts and mirror the fields into local game.* . Clients no longer
  elect a host for match purposes; they still elect one for bot ownership
  separately.

  Wire summary:
    Server -> client:
      {type: 'hello', myPeerId, peers}                        on connect
      {type: 'match-state', payload: {state, seed, ...}}      on transition
      {type: 'peer-join',  peerId}                            on join
      {type: 'peer-leave', peerId}                            on leave
      {type: 'forward', from, payload: {action, payload}}     relay
    Client -> server:
      {action: 'ready', payload: {ready, team, loadoutKey}}   to set status
      {action: 'mapVote', payload: {mapKey}}                  optional
      {action: <other>, payload: ...}                         relayed

  Run:
    cd docs/LSS && bun run server/main.ts
*/

import os from 'node:os';
import path from 'node:path';
import type { ServerWebSocket } from 'bun';

type ClientData = { peerId: string };
type Client = ServerWebSocket<ClientData>;

const PORT = Number(process.env.PORT) || 8080;
const HOSTNAME = process.env.HOSTNAME || '0.0.0.0';

const WEB_ROOT = path.resolve(import.meta.dir, '..');

const clients = new Map<string, Client>();
let nextPeerId = 1;

// ---- v7.3: server-authoritative match state ----
const ROUND_TIME = 180;
const WARMUP_TIME = 10;
const ROUND_END_LINGER = 6;   // seconds shown on scoreboard before reset
const TICK_HZ = 4;            // 4 Hz is plenty for state transitions
const BROADCAST_TICK_INTERVAL = 1.0; // re-broadcast match-state once a second for resync

// v7.3.1: state names match the client's existing strings. The lobby /
// ship-pick phase is 'select' on both sides. (v7.3 used 'lobby' on the
// server side, which mismatched the client's gameplay-loop early-return
// `game.state === 'select'` and let broadcastPlayerState run pre-commit
// against a null player.position.)
type MatchPhase = 'select' | 'warmup' | 'playing' | 'roundEnd';

interface MatchState {
  state: MatchPhase;
  seed: number;
  selectedMap: string;
  warmupTimer: number;
  roundTimer: number;
  currentRound: number;
  scoreA: number;
  scoreB: number;
}

interface PeerInfo {
  ready: boolean;
  team: number | null;
  loadoutKey: string | null;
  mapVote: string | null;
}

const matchState: MatchState = {
  state: 'select',
  seed: 0,
  selectedMap: 'hourglass',
  warmupTimer: 0,
  roundTimer: 0,
  currentRound: 1,
  scoreA: 0,
  scoreB: 0,
};

const peerInfo = new Map<string, PeerInfo>();
let lastBroadcastAt = 0;

function genPeerId(): string {
  const id = (nextPeerId++).toString(36).padStart(4, '0');
  return 'p' + id;
}

function broadcast(obj: unknown, except?: Client) {
  const msg = JSON.stringify(obj);
  for (const client of clients.values()) {
    if (client === except) continue;
    try { client.send(msg); } catch { /* dropped */ }
  }
}

function broadcastMatchState() {
  broadcast({ type: 'match-state', payload: matchState });
  lastBroadcastAt = Date.now() / 1000;
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

function allPeersReady(): boolean {
  if (peerInfo.size === 0) return false;
  for (const info of peerInfo.values()) {
    if (!info.ready) return false;
  }
  return true;
}

// Tally map votes; pick the most-voted, ties broken alphabetically.
function pickMapFromVotes(): string {
  const tally = new Map<string, number>();
  for (const info of peerInfo.values()) {
    if (info.mapVote) tally.set(info.mapVote, (tally.get(info.mapVote) || 0) + 1);
  }
  if (tally.size === 0) return matchState.selectedMap; // keep current
  let best: string | null = null;
  let bestN = -1;
  for (const [k, n] of tally) {
    if (n > bestN || (n === bestN && best != null && k < best)) {
      best = k;
      bestN = n;
    }
  }
  return best || matchState.selectedMap;
}

function startMatch() {
  matchState.state = 'warmup';
  matchState.warmupTimer = WARMUP_TIME;
  matchState.roundTimer = ROUND_TIME;
  matchState.seed = (Math.random() * 0xFFFFFFFF) | 0;
  matchState.selectedMap = pickMapFromVotes();
  matchState.scoreA = 0;
  matchState.scoreB = 0;
  matchState.currentRound = 1;
  console.log('[match] LOBBY -> WARMUP  seed=' + matchState.seed
    + ' map=' + matchState.selectedMap + ' peers=' + peerInfo.size);
  broadcastMatchState();
}

function endRound() {
  matchState.state = 'roundEnd';
  matchState.roundTimer = 0;
  console.log('[match] PLAYING -> ROUND_END');
  broadcastMatchState();
}

function resetToLobby() {
  matchState.state = 'select';
  matchState.warmupTimer = 0;
  matchState.roundTimer = 0;
  // Reset every peer's ready flag so they have to commit again.
  for (const info of peerInfo.values()) info.ready = false;
  console.log('[match] -> LOBBY  (peers reset to not-ready)');
  broadcastMatchState();
}

let lastTickMs = Date.now();
setInterval(() => {
  const now = Date.now();
  const dt = (now - lastTickMs) / 1000;
  lastTickMs = now;

  if (matchState.state === 'select') {
    if (allPeersReady() && peerInfo.size > 0) {
      startMatch();
    }
  } else if (matchState.state === 'warmup') {
    matchState.warmupTimer = Math.max(0, matchState.warmupTimer - dt);
    if (matchState.warmupTimer <= 0) {
      matchState.state = 'playing';
      console.log('[match] WARMUP -> PLAYING');
      broadcastMatchState();
    }
  } else if (matchState.state === 'playing') {
    matchState.roundTimer = Math.max(0, matchState.roundTimer - dt);
    if (matchState.roundTimer <= 0) {
      endRound();
    }
  } else if (matchState.state === 'roundEnd') {
    matchState.warmupTimer -= dt; // reuse warmupTimer as the linger countdown
    if (matchState.warmupTimer <= -ROUND_END_LINGER) {
      resetToLobby();
    }
  }

  // Periodic re-broadcast so late-joiners and out-of-sync clients catch up.
  const sec = now / 1000;
  if (sec - lastBroadcastAt > BROADCAST_TICK_INTERVAL) {
    broadcastMatchState();
  }
}, Math.round(1000 / TICK_HZ));

// MIME types
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
    urlPath = '/last_ship_sailing_lh.html';
  }
  const decoded = decodeURIComponent(urlPath);
  const rel = decoded.replace(/^\/+/, '').replace(/\\/g, '/');
  const abs = path.resolve(WEB_ROOT, rel);
  if (!abs.startsWith(WEB_ROOT)) return null;
  return abs;
}

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
      return new Response(JSON.stringify({
        ok: true,
        clients: clients.size,
        match: matchState,
        peers: Array.from(peerInfo.entries()).map(([id, p]) => ({ id, ...p })),
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
    const headers: Record<string, string> = {
      'cache-control': 'no-cache',
    };
    if (MIME[ext]) headers['content-type'] = MIME[ext];
    return new Response(file, { headers });
  },

  websocket: {
    open(ws) {
      const peerId = ws.data.peerId;
      const peers = [...clients.keys()];
      peerInfo.set(peerId, { ready: false, team: null, loadoutKey: null, mapVote: null });
      ws.send(JSON.stringify({ type: 'hello', myPeerId: peerId, peers }));
      ws.send(JSON.stringify({ type: 'match-state', payload: matchState }));
      broadcast({ type: 'peer-join', peerId }, ws);
      clients.set(peerId, ws);
      console.log('[connect]   ' + peerId + '  (clients: ' + clients.size + ')');
    },

    message(ws, message) {
      const peerId = ws.data.peerId;
      let data: any;
      try {
        data = typeof message === 'string'
          ? JSON.parse(message)
          : JSON.parse(new TextDecoder().decode(message));
      } catch (e) {
        console.error('[parse-err] ' + peerId + ': ' + (e as Error).message);
        return;
      }

      // v7.3: server-consumed actions don't get relayed.
      if (data && data.action === 'ready') {
        const info = peerInfo.get(peerId);
        if (info) {
          info.ready = !!(data.payload && data.payload.ready);
          if (data.payload && typeof data.payload.team === 'number') info.team = data.payload.team;
          if (data.payload && typeof data.payload.loadoutKey === 'string') info.loadoutKey = data.payload.loadoutKey;
        }
        return;
      }
      if (data && data.action === 'mapVote') {
        const info = peerInfo.get(peerId);
        if (info && data.payload && typeof data.payload.mapKey === 'string') {
          info.mapVote = data.payload.mapKey;
        }
        return;
      }
      if (data && data.action === 'leaveMatch') {
        // Allow a peer to gracefully bail out of a round (returns them to lobby).
        const info = peerInfo.get(peerId);
        if (info) info.ready = false;
        return;
      }

      // Everything else: relay to other peers, wrapped with sender id.
      const wrapped = JSON.stringify({ type: 'forward', from: peerId, payload: data });
      for (const client of clients.values()) {
        if (client === ws) continue;
        try { client.send(wrapped); } catch { /* drop */ }
      }
    },

    close(ws, code, reason) {
      const peerId = ws.data.peerId;
      clients.delete(peerId);
      peerInfo.delete(peerId);
      broadcast({ type: 'peer-leave', peerId });
      console.log('[disconnect] ' + peerId + '  (clients: ' + clients.size + ')'
        + (reason ? '  reason: ' + reason : ''));
      // If everyone left during a match, snap back to lobby.
      if (clients.size === 0 && matchState.state !== 'select') {
        resetToLobby();
      }
    },
  },
});

console.log('');
console.log('===========================================');
console.log('  Last Ship Sailing ; local server (v7.3)');
console.log('===========================================');
console.log('  Same machine:  http://localhost:' + server.port);
console.log('  LAN devices:   http://' + getLanIp() + ':' + server.port);
console.log('  Health check:  http://localhost:' + server.port + '/health');
console.log('  WebSocket:     ws://localhost:' + server.port + '/socket');
console.log('===========================================');
console.log('  Match authority: server (lobby/warmup/playing/roundEnd)');
console.log('  Press Ctrl+C to stop.');
console.log('');
