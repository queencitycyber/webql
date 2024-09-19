// sql_injection.js - SQL Injection vulnerabilities

function getUserById(id) {
    const query = `SELECT * FROM users WHERE id = ${id}`;  // SQL Injection vulnerability
    // Execute query...
}

function searchUsers(name) {
    const query = "SELECT * FROM users WHERE name LIKE '%" + name + "%'";  // Another SQL Injection vulnerability
    // Execute query...
}

function updateUser(id, data) {
    const query = `UPDATE users SET ${data} WHERE id = ${id}`;  // SQL Injection in UPDATE statement
    // Execute query...
}

module.exports = {
    getUserById,
    searchUsers,
    updateUser
};