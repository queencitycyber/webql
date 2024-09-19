// vulnerable_webapp.js - Vulnerable Express.js Application

const express = require('express');
const mysql = require('mysql');
const crypto = require('crypto');
const fs = require('fs');
const app = express();

app.use(express.json());

// Vulnerable database connection (hardcoded credentials)
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'password123',
  database: 'vulnerable_db'
});

// XSS Vulnerability
app.get('/xss', (req, res) => {
  const userInput = req.query.input;
  res.send(`<div>${userInput}</div>`);  // XSS vulnerability
});

// SQL Injection Vulnerability
app.get('/users', (req, res) => {
  const userId = req.query.id;
  const query = `SELECT * FROM users WHERE id = ${userId}`;  // SQL Injection vulnerability
  connection.query(query, (error, results) => {
    if (error) throw error;
    res.json(results);
  });
});

// Weak Cryptography
app.post('/encrypt', (req, res) => {
  const { data } = req.body;
  const cipher = crypto.createCipher('aes-128-ecb', 'secretkey');  // Weak encryption
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  res.json({ encrypted });
});

// Path Traversal Vulnerability
app.get('/file', (req, res) => {
  const fileName = req.query.name;
  fs.readFile('/var/www/files/' + fileName, (err, data) => {  // Path traversal vulnerability
    if (err) {
      res.status(404).send('File not found');
    } else {
      res.send(data);
    }
  });
});

// Command Injection Vulnerability
app.get('/ping', (req, res) => {
  const host = req.query.host;
  const { exec } = require('child_process');
  exec(`ping -c 4 ${host}`, (error, stdout, stderr) => {  // Command injection vulnerability
    if (error) {
      res.status(500).send(error.message);
      return;
    }
    res.send(stdout);
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

module.exports = app;  // For testing purposes