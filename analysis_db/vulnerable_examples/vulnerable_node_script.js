// vulnerable_node_script.js - Vulnerable Node.js Script

const fs = require('fs');
const crypto = require('crypto');
const { exec } = require('child_process');

// Unsafe deserialization
function deserializeUserData(data) {
  return JSON.parse(data);  // Potential prototype pollution
}

// Weak random number generation
function generateToken() {
  return Math.random().toString(36).substring(2, 15);  // Weak random token
}

// Path traversal
function readUserFile(fileName) {
  return fs.readFileSync(`./user_files/${fileName}`, 'utf8');  // Path traversal vulnerability
}

// Command injection
function runCommand(command) {
  exec(command, (error, stdout, stderr) => {  // Command injection vulnerability
    if (error) {
      console.error(`exec error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });
}

// Weak cryptography
function encryptData(data) {
  const cipher = crypto.createCipher('aes-128-ecb', 'secretkey');  // Weak encryption
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

// Usage of vulnerable functions
const userData = '{"username": "admin", "role": "user"}';
const deserializedData = deserializeUserData(userData);
console.log('Deserialized data:', deserializedData);

const token = generateToken();
console.log('Generated token:', token);

try {
  const fileContent = readUserFile('../config.json');  // Attempting path traversal
  console.log('File content:', fileContent);
} catch (error) {
  console.error('Error reading file:', error.message);
}

runCommand('ls -la ' + process.argv[2]);  // Potential command injection

const sensitiveData = 'password123';
const encryptedData = encryptData(sensitiveData);
console.log('Encrypted data:', encryptedData);

module.exports = {
  deserializeUserData,
  generateToken,
  readUserFile,
  runCommand,
  encryptData
};