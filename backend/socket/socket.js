import cors from 'cors';
import express from 'express';
import http from 'http';
import { Server } from 'socket.io';

const app = express();

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: ['http://localhost:3000', 'https://chitchat-835v.onrender.com'],
    methods: ['GET', 'POST'],
  },
});

export const getReceiverSocketId = (receiverId) => {
  return userSocketMap[receiverId];
};

const userSocketMap = {};

io.on('connection', (socket) => {
  console.log('a user connected', socket.id);
  const userId = socket.handshake.query.userId;
  if (userId !== undefined) {
    userSocketMap[userId] = socket.id;
  }
  io.emit('getOnlineUsers', Object.keys(userSocketMap));
  // socket.on() digunakan untuk mendengarkan event tertentu. dapat digunakan untuk menerima data dari client dan mengirimkan data ke client

  // Handle user joining a group
  socket.on('joinGroup', (groupId) => {
    socket.join(groupId);
    console.log(`User joined group: ${groupId}`);
  });

  // Handle user leaving a group
  socket.on('leaveGroup', (groupId) => {
    socket.leave(groupId);
    console.log(`User left group: ${groupId}`);
  });

  socket.on('disconnect', () => {
    console.log('user disconnected', socket.id);
    delete userSocketMap[userId];
    io.emit('getOnlineUsers', Object.keys(userSocketMap));
  });
});

export { app, io, server };
