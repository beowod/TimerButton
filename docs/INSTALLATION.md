# Installation Guide

## Prerequisites

- Windows 10 or later
- Internet connection (for initial setup only)

## Quick Install

1. Open PowerShell as Administrator
2. Run the setup script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup-new-machine.ps1
   ```

## Manual Install

1. Install Python 3.12+:
   ```powershell
   winget install Python.Python.3.12
   ```

2. Restart your terminal to refresh PATH

3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   python -m pip install -r requirements-dev.txt
   ```

4. Verify installation:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\doctor.ps1
   ```

## Running the Application

```powershell
python src\main.py
```

The database will be created automatically at `data\timerbutton.db` on first launch.

## Building a Standalone Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package-app.ps1
```

The executable will be at `dist\MotelRoomTimer.exe`.
