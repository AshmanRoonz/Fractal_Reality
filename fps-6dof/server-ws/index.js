#!/usr/bin/env node

'use strict';

const express = require('express');
const { WebSocketServer } = require('ws');
const { createServer } = require('http');
const path = require('path');
const { GameRoom } = require('./game');

const PORT = process.env.PORT || 2567;
const HOST = process.env.HOST || '0.0.0.0';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Counter for session IDs
let sessionIdCounter = 0;

// Single game room
const gameRoom = new GameRoom();

// Serve static files
const clientPath = path.join(__dirname, '..', 'last_ship_sailing_mp.html');
app.get('/', (req, res) => {
  res.sendFile(clientPath);
});

// WebSocket connection handler
wss.on('connection', (ws) => {
  const sessionId = 's' + (sessionIdCounter++) + '_' + Math.random().toString(36).substr(2, 6);

  console.log(`Player connected: ${sessionId}`);

  // Notify game room
  gameRoom.onPlayerJoin(ws, sessionId);

  // Message handler
  ws.on('message', (data) => {
    try {
      gameRoom.onPlayerMessage(ws, data);
    } catch (err) {
      console.error('Message error:', err);
    }
  });

  // Error handler
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });

  // Close handler
  ws.on('close', () => {
    console.log(`Player disconnected: ${sessionId}`);
    gameRoom.onPlayerLeave(ws);
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  gameRoom.shutdown();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

// Start server
server.listen(PORT, HOST, () => {
  console.log(`Last Ship Sailing WebSocket Server running on ws://${HOST}:${PORT}`);
  console.log(`HTTP server on http://${HOST}:${PORT}/`);
});
