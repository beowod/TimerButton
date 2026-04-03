# Verify the machine is ready for development
# Run: powershell -ExecutionPolicy Bypass -File scripts\doctor.ps1

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== Environment Doctor ===" -ForegroundColor Cyan
$allGood = $true

# Python
try {
    $pyVer = python --version 2>&1
    Write-Host "[OK] $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Python not found" -ForegroundColor Red
    $allGood = $false
}

# tkinter
try {
    python -c "import tkinter; print('[OK] tkinter available')" 2>&1
} catch {
    Write-Host "[FAIL] tkinter not available" -ForegroundColor Red
    $allGood = $false
}

# sqlite3
try {
    python -c "import sqlite3; print('[OK] sqlite3 available')" 2>&1
} catch {
    Write-Host "[FAIL] sqlite3 not available" -ForegroundColor Red
    $allGood = $false
}

# pytest
try {
    python -c "import pytest; print('[OK] pytest ' + pytest.__version__)" 2>&1
} catch {
    Write-Host "[WARN] pytest not installed - run: pip install -r requirements-dev.txt" -ForegroundColor Yellow
}

# Git
try {
    $gitVer = git --version 2>&1
    Write-Host "[OK] $gitVer" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Git not found" -ForegroundColor Yellow
}

if ($allGood) {
    Write-Host "`n=== All checks passed ===" -ForegroundColor Green
} else {
    Write-Host "`n=== Some checks failed ===" -ForegroundColor Red
}
