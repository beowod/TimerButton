# Package the application as a standalone .exe
# Run: powershell -ExecutionPolicy Bypass -File scripts\package-app.ps1

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Packaging Motel Room Timer..." -ForegroundColor Cyan

python -m PyInstaller --onefile --windowed --name MotelRoomTimer --add-data "src;src" src\main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Package created: dist\MotelRoomTimer.exe" -ForegroundColor Green
} else {
    Write-Host "Packaging failed." -ForegroundColor Red
}
