Write-Host "Activating Python 3.11 virtual environment and running nvidia_code_reasoning_server.py..."

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python servers\nvidia_code_reasoning_server.py
