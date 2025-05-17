const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');
const path = require('path');
const tiktoken = require('tiktoken'); // Example tokenizer library

const app = express();
const PORT = 3000;
const TARGET_PORT = 8000;

// Initialize the tokenizer
const encoding = tiktoken.get_encoding('cl100k_base');

// Middleware to log token usage
app.use(express.json()); // Ensure JSON body parsing
app.use((req, res, next) => {
    const token = req.headers['authorization'] || 'No Token';

    const inputText = req.body?.messages?.map(m => m.content).join(' ') || req.body?.prompt || ''; // Check for 'content' in 'messages' or 'prompt'
    const inputTokens = inputText ? encoding.encode(inputText).length : 0; // Count input tokens if text exists

    const logEntry = `${new Date().toISOString()} - Token: ${token} - Path: ${req.path} - Input Tokens: ${inputTokens}`;

    // Also log to the terminal
    console.log(logEntry);

    // Intercept response to count output tokens
    const originalSend = res.send;
    res.send = function (body) {
        const outputText = typeof body === 'string' ? body : JSON.stringify(body);
        const outputTokens = encoding.encode(outputText).length; // Count output tokens

        const outputLogEntry = `${new Date().toISOString()} - Path: ${req.path} - Output Tokens: ${outputTokens}`;

        // Log output tokens
        console.log(outputLogEntry);

        return originalSend.call(this, body);
    };

    next();
});

// Endpoint to retrieve token usage logs
app.get('/logs', (req, res) => {
    res.status(404).send('No logs available.');
});

// Proxy all other requests to port 8000
app.use('/', createProxyMiddleware({
    target: `http://127.0.0.1:${TARGET_PORT}`,
    changeOrigin: true
}));

// Start the server
app.listen(PORT, () => {
    console.log(`Proxy server is running on http://127.0.0.1:${PORT}, forwarding to http://127.0.0.1:${TARGET_PORT}`);
    console.log(`Access token usage logs at http://127.0.0.1:${PORT}/logs`);
});
