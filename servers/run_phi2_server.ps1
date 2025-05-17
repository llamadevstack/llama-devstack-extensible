Write-Host "Activating Python 3.11 virtual environment and running phi2_server.py..."

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python servers\phi2_server.py
