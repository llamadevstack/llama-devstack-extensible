Write-Host "Activating Python 3.11 virtual environment and running rwkv_server.py..."

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python servers\rwkv_server.py
