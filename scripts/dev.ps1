# Run the application in dev mode
# Run: powershell -ExecutionPolicy Bypass -File scripts\dev.ps1

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Starting Motel Room Timer..." -ForegroundColor Cyan
python src\main.py
