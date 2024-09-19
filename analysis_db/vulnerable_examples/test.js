// test.js - Multiple vulnerabilities

function unsafeEval(input) {
  eval(input);  // Arbitrary code execution vulnerability
}

function xssVulnerable(userInput) {
  document.write("<div>" + userInput + "</div>");  // XSS vulnerability
}

function sqlInjectionVulnerable(userId) {
  const query = "SELECT * FROM users WHERE id = " + userId;  // SQL Injection vulnerability
  // Execute query...
}

function insecureRandomNumber() {
  return Math.random();  // Weak random number generation
}

function pathTraversalVulnerable(fileName) {
  const fs = require('fs');
  fs.readFile('/home/user/' + fileName, (err, data) => {  // Path traversal vulnerability
      if (err) throw err;
      console.log(data);
  });
}

module.exports = {
  unsafeEval,
  xssVulnerable,
  sqlInjectionVulnerable,
  insecureRandomNumber,
  pathTraversalVulnerable
};