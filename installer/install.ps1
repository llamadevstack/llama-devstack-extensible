Write-Host "Setting up llama-devstack environment using Python 3.11..."

# Define Python 3.11 path
$python311 = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe"

# Check if Python 3.11 exists
if (-Not (Test-Path $python311)) {
    Write-Host "Python 3.11 not found at $python311"
    Write-Host "Please install Python 3.11 from https://www.python.org/downloads/release/python-31110/"
    exit 1
}

# Create virtual environment using Python 3.11
& "$python311" -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

# Install PyTorch CPU version
Write-Host "Installing PyTorch (CPU-only)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
Write-Host "Installing remaining packages from pythonrequirements.txt..."
pip install -r installer\pythonrequirements.txt

# Run patch to fix torch.load weights_only issue
.\installer\patch.ps1

Write-Host "llama-devstack setup complete using Python 3.11. You can now run any of the servers in /servers"