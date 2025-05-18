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

    const logEntry = `${new Date().toISOString()} - Token: ${inputText} - Path: ${req.path} - Input Tokens: ${inputTokens}`;

    // Also log to the terminal
    console.log(logEntry);

    // Intercept response to count output tokens
    const originalSend = res.send;
    res.send = function (body) {
        console.log('Intercepted response body:', body);

        let outputText = '';
        // Parse the body if it's a JSON string
        if (typeof body === 'string') {
            try {
                const parsedBody = JSON.parse(body);
                console.log('Parsed response body:', parsedBody);
                outputText = parsedBody?.choices?.map(c => c.text).join(' ') || '';
            } catch (e) {
                console.error('Failed to parse response body as JSON:', e);
            }
        } else if (body?.choices) {
            // Extract 'text' from 'choices' if body is already parsed
            console.log('Response body is already parsed:', body);
            outputText = body.choices.map(c => c.text).join(' ');
        }

        const outputTokens = outputText ? encoding.encode(outputText).length : 0;
        const outputLogEntry = `${new Date().toISOString()} - Path: ${req.path} - Output Tokens: ${outputTokens}`;

        // Log output tokens
        console.log(outputLogEntry);

        return originalSend.call(this, body);
    };

    next();
});

// Add middleware to ensure the request body is forwarded correctly
app.use((req, res, next) => {
    if (req.body) {
        req.headers['content-type'] = 'application/json';
        req.rawBody = JSON.stringify(req.body);
    }
    next();
});

// Ensure the request body is forwarded correctly in the proxy
app.use('/', createProxyMiddleware({
    target: `http://127.0.0.1:${TARGET_PORT}`,
    changeOrigin: true,
    onProxyReq: (proxyReq, req) => {
        // Log the method, headers, and body of the request being forwarded
        // console.log(`Forwarding request: ${req.method} ${req.url}`);
        // console.log('Headers:', req.headers);
        if (req.body) {
            // console.log('Body:', req.body);
            const bodyData = JSON.stringify(req.body);

            // Write body data to the proxied request
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
        }

        // Forward the original HTTP method
        proxyReq.method = req.method;
    },
    // Update onProxyRes to handle streamed responses and count tokens after completion
    onProxyRes: (proxyRes, req, res) => {
        let responseBody = '';

        // Forward the streamed data to the client
        proxyRes.on('data', (chunk) => {
            responseBody += chunk;
            res.write(chunk); // Stream the chunk to the client
        });

        proxyRes.on('end', () => {
            res.end(); // End the response stream

            try {
                // Check if responseBody is valid JSON
                if (responseBody.trim().startsWith('{') && responseBody.trim().endsWith('}')) {
                    const parsedBody = JSON.parse(responseBody);
                    let outputText = '';

                    // Check for 'text' in 'choices'
                    if (parsedBody?.choices) {
                        outputText = parsedBody.choices.map(c => c.text || c.message?.content).join(' ') || '';
                    }

                    const outputTokens = outputText ? encoding.encode(outputText).length : 0;
                    const outputLogEntry = `${new Date().toISOString()} - Path: ${req.path} - Output Tokens: ${outputTokens}`;

                    // Log output tokens
                    console.log(outputLogEntry);
                } else {
                    console.warn('Response body is not valid JSON:', responseBody);
                }
            } catch (e) {
                console.error('Failed to parse response body as JSON:', e);
            }
        });

        proxyRes.on('error', (err) => {
            console.error('Error in proxy response:', err);
            res.end(); // Ensure the response ends on error
        });
    }
}));


// Start the server
app.listen(PORT, () => {
    console.log(`Proxy server is running on http://127.0.0.1:${PORT}, forwarding to http://127.0.0.1:${TARGET_PORT}`);
    console.log(`Access token usage logs at http://127.0.0.1:${PORT}/logs`);
});
