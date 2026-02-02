# PowerShell setup script for Plant Care Agent
$ErrorActionPreference = "Stop"

$VENV_DIR = "venv"

Write-Host "Setting up virtual environment and installing dependencies..." -ForegroundColor Cyan

# 1. Create venv if it doesn't exist
if (-not (Test-Path $VENV_DIR)) {
  Write-Host "Creating virtual environment in ./$VENV_DIR" -ForegroundColor Yellow
  python -m venv $VENV_DIR
}
else {
  Write-Host "Virtual environment already exists at ./$VENV_DIR" -ForegroundColor Green
}

# 2. Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$VENV_DIR\Scripts\Activate.ps1"

# 3. Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 4. Install requirements
if (Test-Path "requirements.txt") {
  Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
  pip install -r requirements.txt
}
else {
  Write-Host "requirements.txt not found. Installing Streamlit directly..." -ForegroundColor Yellow
  pip install streamlit
}

Write-Host "Setup complete." -ForegroundColor Green

Write-Host ""
Write-Host "To start the app, run:" -ForegroundColor Cyan
Write-Host "  streamlit run plant_agent_streamlit.py"
