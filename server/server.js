const express = require('express');
const https = require('https');
const fs = require('fs');
const WebSocket = require('ws');
const kurento = require('kurento-client');
const path = require('path');

const app = express();
const server = https.createServer({
  cert: fs.readFileSync('/etc/letsencrypt/live/i11b204.p.ssafy.io/fullchain.pem'),
  key: fs.readFileSync('/etc/letsencrypt/live/i11b204.p.ssafy.io/privkey.pem')
}, app);

const wss = new WebSocket.Server({ noServer: true });

const ws_uri = 'ws://i11b204.p.ssafy.io:8888/kurento';

kurento(ws_uri, (error, kurentoClient) => {
  if (error) return console.error('Kurento connection error:', error);

  kurentoClient.create('MediaPipeline', (error, pipeline) => {
    if (error) return console.error('MediaPipeline error:', error);

    pipeline.create('WebRtcEndpoint', (error, webRtcEndpoint) => {
      if (error) return console.error('WebRtcEndpoint error:', error);

      console.log('WebRtcEndpoint created successfully');
    });
  });
});

let idCounter = 0;
const users = {};

const getImageForPosition = (x, y) => {
  if (x === 0 && y === 0) return 'default';
  if (x >= 0 && y >= 0) return 'soldier';
  if (x < 0 && y > 0) return 'art';
  if (x <= 0 && y <= 0) return 'steel';
  if (x > 0 && y < 0) return 'butler';
};

wss.on('connection', (ws, req) => {
  const userId = idCounter++;
  const position = { x: Math.random() * 2 - 1, y: Math.random() * 2 - 1 };
  const userImage = getImageForPosition(position.x, position.y);
  users[userId] = { id: userId, ws: ws, position: position, image: userImage };
  console.log(`User connected: ${userId}`);
  ws.send(JSON.stringify({ type: 'assign_id', position: position, id: userId, image: userImage }));

  const otherUsers = Object.values(users).filter(user => user.id !== userId);
  ws.send(JSON.stringify({ type: 'all_users', users: otherUsers.map(user => ({ id: user.id, position: user.position, image: user.image })) }));

  ws.on('message', async (message) => {
    const data = JSON.parse(message);
    console.log(`Received message from user ${userId}:`, data);
    switch (data.type) {
      case 'move':
        handleMove(userId, data.position);
        break;
      case 'offer':
        console.log(`Received offer from user ${userId}`);
        break;
      case 'candidate':
        console.log(`Received candidate from user ${userId}`);
        break;
      case 'disconnect':
        handleDisconnect(userId);
        break;
    }
  });

  ws.on('close', () => {
    console.log(`User disconnected: ${userId}`);
    handleDisconnect(userId);
  });
});

function handleMove(userId, position) {
  users[userId].position = position;
  broadcast({ users: Object.values(users).filter(user => user.id !== userId).map(user => ({ id: user.id, position: user.position, image: user.image })) });

  const nearbyUsers = getNearbyUsers(userId, 0.2);
  if (nearbyUsers.length > 0) {
    console.log(`User ${userId} is near users:`, nearbyUsers.map(u => u.id));
  }
}

function handleDisconnect(userId) {
  delete users[userId];
  broadcast({ type: 'disconnect', id: userId });
}

function getNearbyUsers(userId, distance) {
  const currentUser = users[userId];
  return Object.values(users).filter(user => {
    if (user.id === userId) return false;
    const dx = user.position.x - currentUser.position.x;
    const dy = user.position.y - currentUser.position.y;
    return Math.sqrt(dx * dx + dy * dy) <= distance;
  });
}

function broadcast(message) {
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

app.use(express.static(path.join(__dirname, 'build')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

server.listen(5001, () => {
  console.log('Server is running on port 5001');
});
