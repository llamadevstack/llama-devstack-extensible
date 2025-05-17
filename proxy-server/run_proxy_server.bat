@echo off
:: Batch file to start the proxy server
cd /d "%~dp0"
cd proxy-server
node index.js
