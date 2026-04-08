// ============================================================================
// LAST SHIP SAILING ; Dedicated Server
// Run with: node index.js
// Clients connect via WebSocket to port 2567
// ============================================================================

'use strict';

const { Server } = require('colyseus');
const { WebSocketTransport } = require('@colyseus/ws-transport');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { MatchRoom } = require('./MatchRoom');

const PORT = parseInt(process.env.PORT) || 2567;

// ---- Simple static file server for the game client ----
// Serves the HTML file so players only need the server URL

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

const httpServer = http.createServer((req, res) => {
  // Skip Colyseus internal routes (matchmake, etc.)
  if (req.url.startsWith('/matchmake') || req.url.startsWith('/colyseus')) {
    // Colyseus handles these; do nothing (transport will respond)
    return;
  }

  // Serve the client HTML at root
  let filePath;
  if (req.url === '/' || req.url === '/index.html') {
    // Serve the multiplayer client version
    filePath = path.join(__dirname, '..', 'last_ship_sailing_mp.html');
    if (!fs.existsSync(filePath)) {
      // Fallback to original
      filePath = path.join(__dirname, '..', 'last_ship_sailing.html');
    }
  } else {
    // Serve static files from parent directory (sanitize path)
    const safePath = path.normalize(req.url).replace(/^(\.\.[\/\\])+/, '');
    filePath = path.join(__dirname, '..', safePath);
  }

  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (!res.headersSent) {
        res.writeHead(404);
        res.end('Not found');
      }
      return;
    }
    if (!res.headersSent) {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

// ---- Colyseus game server ----

const gameServer = new Server({
  transport: new WebSocketTransport({ server: httpServer }),
});

// Register the match room type
gameServer.define('match', MatchRoom);

// Start listening
gameServer.listen(PORT).then(() => {
  console.log('');
  console.log('  ╔══════════════════════════════════════════╗');
  console.log('  ║     LAST SHIP SAILING ; Dedicated Server ║');
  console.log('  ╠══════════════════════════════════════════╣');
  console.log(`  ║  Listening on port ${PORT}                  ║`);
  console.log(`  ║  Local:  http://localhost:${PORT}            ║`);
  console.log('  ║                                          ║');
  console.log('  ║  To expose publicly (free):              ║');
  console.log('  ║  npx cloudflared tunnel \\                ║');
  console.log(`  ║    --url http://localhost:${PORT}            ║`);
  console.log('  ║                                          ║');
  console.log('  ║  Share the tunnel URL with players.      ║');
  console.log('  ╚══════════════════════════════════════════╝');
  console.log('');
});
