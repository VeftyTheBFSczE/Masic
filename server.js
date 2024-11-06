// server.js
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const db = new sqlite3.Database(':memory:');

db.serialize(() => {
  db.run("CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT, qr_code TEXT)");
  db.run("CREATE TABLE coffee_log (id TEXT PRIMARY KEY, user_id TEXT, amount INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)");
  db.run("CREATE TABLE tasks (id TEXT PRIMARY KEY, description TEXT, status TEXT, user_id TEXT)");
});

io.on('connection', (socket) => {
  db.all("SELECT * FROM coffee_log", [], (err, coffeeLog) => {
    if (err) {
      throw err;
    }
    db.all("SELECT * FROM tasks", [], (err, tasks) => {
      if (err) {
        throw err;
      }
      socket.emit('update', { coffeeLog, tasks });
    });
  });

  socket.on('logCoffee', (data) => {
    const id = uuidv4();
    db.run("INSERT INTO coffee_log (id, user_id, amount) VALUES (?, ?, ?)", [id, data.user, data.amount], (err) => {
      if (err) {
        return console.error(err.message);
      }
      db.all("SELECT * FROM coffee_log", [], (err, coffeeLog) => {
        if (err) {
          throw err;
        }
        io.emit('update', { coffeeLog, tasks: [] });
      });
    });
  });

  socket.on('addTask', (data) => {
    const id = uuidv4();
    db.run("INSERT INTO tasks (id, description, status, user_id) VALUES (?, ?, ?, ?)", [id, data.description, 'pending', data.user], (err) => {
      if (err) {
        return console.error(err.message);
      }
      db.all("SELECT * FROM tasks", [], (err, tasks) => {
        if (err) {
          throw err;
        }
        io.emit('update', { coffeeLog: [], tasks });
      });
    });
  });

  socket.on('completeTask', (data) => {
    db.run("UPDATE tasks SET status = ? WHERE id = ?", ['completed', data.id], (err) => {
      if (err) {
        return console.error(err.message);
      }
      db.all("SELECT * FROM tasks", [], (err, tasks) => {
        if (err) {
          throw err;
        }
        io.emit('update', { coffeeLog: [], tasks });
      });
    });
  });
});

server.listen(3000, () => {
  console.log('Server is running on port 3000');
});