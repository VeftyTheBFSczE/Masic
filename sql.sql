CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT,
  qr_code TEXT
);

CREATE TABLE coffee_log (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  amount INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  description TEXT,
  status TEXT,
  user_id TEXT
);