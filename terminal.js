// terminal.js
const io = require('socket.io-client');
const socket = io('http://localhost:3000');

socket.on('update', (data) => {
  console.clear();
  console.log('Coffee Consumption Overview:');
  data.coffeeLog.forEach(log => {
    console.log(`${log.user_id} drank ${log.amount} coffee(s)`);
  });
});

socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});