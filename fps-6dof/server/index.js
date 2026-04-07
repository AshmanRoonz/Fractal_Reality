/**
 * Last Ship Sailing - Multiplayer Server Main Entry Point
 *
 * Manages HTTP server, WebSocket connections, and Match lifecycle.
 * REST API for match discovery and creation.
 * WebSocket routing for real-time game communication.
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const crypto = require('crypto');

const Lobby = require('./lobby');
const Match = require('./match');
const GameLoop = require('./gameloop');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws' });

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../client')));

// State management
const lobby = new Lobby();
const gameLoop = new GameLoop();
let playerCounter = 0;

// Generate unique player ID
function generatePlayerId() {
  return `player_${++playerCounter}`;
}

// REST API endpoints

// GET /api/matches: list all public matches
app.get('/api/matches', (req, res) => {
  const matches = lobby.listMatches();
  res.json(matches);
});

// POST /api/matches: create a new match
app.post('/api/matches', (req, res) => {
  const { name, map, maxPlayers, botFill, password } = req.body;

  // Validate input
  if (!name || !map) {
    return res.status(400).json({ error: 'name and map required' });
  }

  const max = Math.max(2, Math.min(10, maxPlayers || 10));
  const opts = {
    name,
    map,
    maxPlayers: max,
    botFill: botFill || false,
    password: password || null,
  };

  try {
    const matchInfo = lobby.createMatch(opts);
    res.status(201).json(matchInfo);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/matches/:id: get match details
app.get('/api/matches/:id', (req, res) => {
  const match = lobby.getMatch(req.params.id);
  if (!match) {
    return res.status(404).json({ error: 'match not found' });
  }

  res.json({
    id: match.id,
    name: match.name,
    map: match.map,
    players: match.players.size,
    maxPlayers: match.maxPlayers,
    state: match.state,
    botFill: match.botFill,
    joinCode: match.joinCode,
  });
});

// WebSocket connection handling
wss.on('connection', (ws) => {
  const playerId = generatePlayerId();
  let currentMatchId = null;

  console.log(`[WS] Player connected: ${playerId}`);

  // Send initial player ID
  ws.send(JSON.stringify({
    type: 'connect_ack',
    playerId,
  }));

  // Message handler
  ws.on('message', (rawData) => {
    try {
      const msg = JSON.parse(rawData);
      handleMessage(playerId, currentMatchId, msg, ws);
    } catch (err) {
      console.error(`[WS] Parse error for ${playerId}:`, err.message);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format',
      }));
    }
  });

  // Error handler
  ws.on('error', (err) => {
    console.error(`[WS] Error for ${playerId}:`, err.message);
  });

  // Disconnect handler
  ws.on('close', () => {
    console.log(`[WS] Player disconnected: ${playerId}`);
    if (currentMatchId) {
      const match = lobby.getMatch(currentMatchId);
      if (match) {
        match.removePlayer(playerId);
        if (match.players.size === 0) {
          setTimeout(() => {
            if (match.players.size === 0) {
              lobby.removeMatch(currentMatchId);
              console.log(`[Lobby] Removed empty match: ${currentMatchId}`);
            }
          }, 60000);
        }
      }
    }
  });

  function handleMessage(pId, mId, msg, wsConnection) {
    switch (msg.type) {
      case 'join_match':
        handleJoinMatch(pId, msg, wsConnection);
        currentMatchId = msg.matchId;
        break;

      case 'leave_match':
        if (currentMatchId) {
          const match = lobby.getMatch(currentMatchId);
          if (match) {
            match.removePlayer(pId);
          }
          currentMatchId = null;
        }
        break;

      case 'input':
        if (currentMatchId) {
          const match = lobby.getMatch(currentMatchId);
          if (match) {
            match.handleInput(pId, msg);
          }
        }
        break;

      case 'loadout_select':
        if (currentMatchId) {
          const match = lobby.getMatch(currentMatchId);
          if (match) {
            match.handleLoadoutSelect(pId, msg.loadoutKey);
          }
        }
        break;

      case 'ready':
        if (currentMatchId) {
          const match = lobby.getMatch(currentMatchId);
          if (match) {
            match.handleReady(pId);
          }
        }
        break;

      case 'chat':
        if (currentMatchId) {
          const match = lobby.getMatch(currentMatchId);
          if (match) {
            match.broadcastToAll({
              type: 'chat',
              playerId: pId,
              message: msg.message,
              timestamp: Date.now(),
            });
          }
        }
        break;

      default:
        console.warn(`[WS] Unknown message type: ${msg.type}`);
    }
  }

  function handleJoinMatch(pId, msg, wsConnection) {
    const { matchId } = msg;
    const match = lobby.getMatch(matchId);

    if (!match) {
      wsConnection.send(JSON.stringify({
        type: 'error',
        message: 'Match not found',
      }));
      return;
    }

    // Add player to match
    try {
      match.addPlayer(pId, wsConnection);
      console.log(`[Match ${matchId}] Player ${pId} joined`);
    } catch (err) {
      wsConnection.send(JSON.stringify({
        type: 'error',
        message: err.message,
      }));
    }
  }
});

// Start game loop
gameLoop.start(lobby);

// HTTP server listen
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`[Server] Listening on port ${PORT}`);
  console.log(`[Server] WebSocket endpoint: ws://localhost:${PORT}/ws`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Server] SIGTERM received; shutting down gracefully');
  gameLoop.stop();
  server.close(() => {
    console.log('[Server] Server closed');
    process.exit(0);
  });
});
