/*
  Last Ship Sailing ; local-host server (v7.0)
  Created: 2026-04-25
  Last updated: 2026-04-25
  Version: 7.0

  WebSocket relay + static file server. Runs on Bun. Single-room model:
  every connected client is in the same match. Server assigns a peer-id
  on connect, relays messages between clients, and emits peer-join /
  peer-leave events. Wire format mirrors what the v6_x frontend already
  speaks over Trystero ; the server is a pure relay for now (no game
  logic). v7.1+ will move match-state authority onto the server.

  Run:
    bun run server/main.ts
  or from the LSS folder:
    cd docs/LSS && bun run server/main.ts

  Then point browsers at:
    http://localhost:8080            (same machine)
    http://<your-LAN-IP>:8080        (other devices on your network)
*/

import os from 'node:os';
import path from 'node:path';
import type { ServerWebSocket } from 'bun';

type ClientData = { peerId: string };
type Client = ServerWebSocket<ClientData>;

const PORT = Number(process.env.PORT) || 8080;
const HOSTNAME = process.env.HOSTNAME || '0.0.0.0';

// docs/LSS/ ; the directory that contains the .html files and ships/.
const WEB_ROOT = path.resolve(import.meta.dir, '..');

const clients = new Map<string, Client>();
let nextPeerId = 1;

function genPeerId(): string {
  // Short, sortable; lowest peer-id wins host election in the frontend.
  const id = (nextPeerId++).toString(36).padStart(4, '0');
  return 'p' + id;
}

function broadcast(obj: unknown, except?: Client) {
  const msg = JSON.stringify(obj);
  for (const client of clients.values()) {
    if (client === except) continue;
    try { client.send(msg); } catch { /* dropped client; close handler will clean it up */ }
  }
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

// MIME types for the small set of file extensions the LSS frontend serves.
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
  // Default route serves the LH frontend.
  if (urlPath === '/' || urlPath === '/index.html') {
    urlPath = '/last_ship_sailing_lh.html';
  }
  const decoded = decodeURIComponent(urlPath);
  // Strip leading slash, prevent directory traversal.
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

    // WebSocket upgrade
    if (url.pathname === '/socket') {
      const peerId = genPeerId();
      const upgraded = server.upgrade(req, { data: { peerId } });
      if (upgraded) return undefined;
      return new Response('WebSocket upgrade failed', { status: 400 });
    }

    // Health check
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({
        ok: true,
        clients: clients.size,
        uptimeSeconds: Math.floor(process.uptime()),
      }), { headers: { 'content-type': 'application/json' } });
    }

    // Static files
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
      ws.send(JSON.stringify({ type: 'hello', myPeerId: peerId, peers }));
      broadcast({ type: 'peer-join', peerId }, ws);
      clients.set(peerId, ws);
      console.log('[connect]   ' + peerId + '  (clients: ' + clients.size + ')');
    },

    message(ws, message) {
      const peerId = ws.data.peerId;
      let payload: unknown;
      try {
        payload = typeof message === 'string'
          ? JSON.parse(message)
          : JSON.parse(new TextDecoder().decode(message));
      } catch (e) {
        console.error('[parse-err] ' + peerId + ': ' + (e as Error).message);
        return;
      }

      // Wrap with sender so the receiving frontend knows who it came from,
      // mirroring Trystero's (data, peerId) signature on its action handlers.
      const wrapped = JSON.stringify({ type: 'forward', from: peerId, payload });
      for (const client of clients.values()) {
        if (client === ws) continue;
        try { client.send(wrapped); } catch { /* drop */ }
      }
    },

    close(ws, code, reason) {
      const peerId = ws.data.peerId;
      clients.delete(peerId);
      broadcast({ type: 'peer-leave', peerId });
      console.log('[disconnect] ' + peerId + '  (clients: ' + clients.size + ')'
        + (reason ? '  reason: ' + reason : ''));
    },
  },
});

console.log('');
console.log('===========================================');
console.log('  Last Ship Sailing ; local server');
console.log('===========================================');
console.log('  Same machine:  http://localhost:' + server.port);
console.log('  LAN devices:   http://' + getLanIp() + ':' + server.port);
console.log('  Health check:  http://localhost:' + server.port + '/health');
console.log('  WebSocket:     ws://localhost:' + server.port + '/socket');
console.log('===========================================');
console.log('  Press Ctrl+C to stop.');
console.log('');
