// ============================================================================
// LAST SHIP SAILING ; Dedicated Server
// Run with: node index.js
// Clients connect via WebSocket to port 2567
// ============================================================================

'use strict';

const { Server } = require('colyseus');
const { WebSocketTransport } = require('@colyseus/ws-transport');
const express = require('express');
const http = require('http');
const path = require('path');
const fs = require('fs');
const { MatchRoom } = require('./MatchRoom');

const PORT = parseInt(process.env.PORT) || 2567;

// ---- Express app for static file serving ----
// Express routes are checked BEFORE Colyseus's catch-all status page

const app = express();

// Serve the MP client at root
app.get('/', (req, res) => {
  let filePath = path.join(__dirname, '..', 'last_ship_sailing_mp.html');
  if (!fs.existsSync(filePath)) {
    filePath = path.join(__dirname, '..', 'last_ship_sailing.html');
  }
  res.sendFile(filePath);
});

app.get('/index.html', (req, res) => {
  let filePath = path.join(__dirname, '..', 'last_ship_sailing_mp.html');
  if (!fs.existsSync(filePath)) {
    filePath = path.join(__dirname, '..', 'last_ship_sailing.html');
  }
  res.sendFile(filePath);
});

// Serve static files from the game directory (for any assets)
app.use(express.static(path.join(__dirname, '..')));

// ---- HTTP + Colyseus game server ----
// Wrap Express app in an http server, then patch matchmaking responses.
// Colyseus server 0.17 returns flat: {name, sessionId, roomId, processId}
// Colyseus client 0.16 expects nested: {room: {name, roomId, processId}, sessionId}

const httpServer = http.createServer(app);

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
