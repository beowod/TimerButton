# Setup script for new Windows machine
# Run: powershell -ExecutionPolicy Bypass -File scripts\setup-new-machine.ps1

Write-Host "=== Motel Room Timer - New Machine Setup ===" -ForegroundColor Cyan

# Check for winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: winget not found. Install App Installer from Microsoft Store." -ForegroundColor Red
    exit 1
}

# Install Python 3.12
Write-Host "Installing Python 3.12..." -ForegroundColor Yellow
winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python installation failed." -ForegroundColor Red
    exit 1
}

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Python installed: $(python --version)" -ForegroundColor Green

# Install dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

Write-Host "=== Setup complete! ===" -ForegroundColor Cyan
Write-Host "Run the app: python src\main.py" -ForegroundColor Green
Write-Host "Run tests:   python -m pytest tests\ -v" -ForegroundColor Green
