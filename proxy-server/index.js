const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware to log token usage
app.use((req, res, next) => {
    const token = req.headers['authorization'] || 'No Token';
    const logEntry = `${new Date().toISOString()} - Token: ${token} - Path: ${req.path}\n`;

    // Log to a file
    const logFilePath = path.join(__dirname, 'token-usage.log');
    fs.appendFileSync(logFilePath, logEntry);

    next();
});

// Proxy configuration
const services = {
    '/phi2': 'http://localhost:8000', // Replace with actual phi2 server URL
    '/rwkv': 'http://localhost:8001', // Replace with actual rwkv server URL
};

Object.keys(services).forEach((route) => {
    app.use(route, createProxyMiddleware({
        target: services[route],
        changeOrigin: true,
        pathRewrite: (path) => path.replace(route, ''),
    }));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Proxy server is running on http://localhost:${PORT}`);
});
