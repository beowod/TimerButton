# Run all tests with coverage
# Run: powershell -ExecutionPolicy Bypass -File scripts\test-all.ps1

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Running tests..." -ForegroundColor Cyan
python -m pytest tests/ -v --cov=src --cov-report=term-missing

Write-Host ""
Write-Host "Running lint..." -ForegroundColor Cyan
python -m flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__

Write-Host ""
Write-Host "Done." -ForegroundColor Green
