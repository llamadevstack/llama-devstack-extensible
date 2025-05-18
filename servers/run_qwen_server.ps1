Write-Host "Activating Python 3.11 virtual environment and running quen_server.py..."

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python servers\quen_server.py
