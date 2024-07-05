import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';
import express from 'express';
import path from 'path';
import connectToMongoDB from './db/connectToMongoDB.js';
import authRoutes from './routes/auth.routes.js';
import friendshipRoutes from './routes/friendship.routes.js';
import groupRoutes from './routes/group.routes.js';
import groupMessageRoutes from './routes/groupMessage.routes.js';
import messageRoutes from './routes/message.routes.js';
import userRoutes from './routes/user.routes.js';
import { app, server } from './socket/socket.js';

const __dirname = path.resolve();

dotenv.config();
const PORT = process.env.PORT || 5000;

app.use(express.json()); // middleware, to parse incoming request with JSON payloads (req.body)
app.use(cookieParser()); // middleware, to parse incoming request with cookies (req.cookies)

app.use('/api/auth', authRoutes); // middleware
app.use('/api/messages', messageRoutes); // middleware
app.use('/api/users', userRoutes); // middleware
app.use('/api/groups', groupRoutes); // middleware
app.use('/api/group-messages', groupMessageRoutes); // middleware
app.use('/api/friend-list', friendshipRoutes); // middleware
app.use(express.static(path.join(__dirname, '/frontend/dist'))); // middleware

app.get('/', (req, res) => {
  // root route http://localhost:5000/
  res.send('Hai World');
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'dist', 'index.html'));
});

server.listen(PORT, () => {
  connectToMongoDB();
  console.log(`Server is running on port ${PORT}`);
});
