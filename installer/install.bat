@echo off
SETLOCAL


:: Check if PowerShell is available
where powershell >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PowerShell is required to run this installer.
    echo Please install PowerShell or run the installation steps manually.
    pause
    exit /b 1
)

:: Run the PowerShell install script
powershell -ExecutionPolicy Bypass -File "installer\install.ps1"

ENDLOCAL
