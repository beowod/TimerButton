# Install project dependencies
# Run: powershell -ExecutionPolicy Bypass -File scripts\install-deps.ps1

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Installing production dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host "Installing dev dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements-dev.txt

Write-Host "Done." -ForegroundColor Green
