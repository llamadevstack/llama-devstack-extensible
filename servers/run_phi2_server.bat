@echo off
SETLOCAL

:: Check if PowerShell is available
where powershell >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PowerShell is required to run this script.
    pause
    exit /b 1
)

:: Run the PowerShell script to start the server
powershell -ExecutionPolicy Bypass -File "servers\run_phi2_server.ps1"

ENDLOCAL
