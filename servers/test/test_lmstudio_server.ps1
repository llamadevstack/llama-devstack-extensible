Write-Host "Activating Python 3.11 virtual environment and running test_lmstudio_server.py..."

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python servers\test\test_lmstudio_server.py
