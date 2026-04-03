# Setting Up on a New Machine

## From Scratch

1. Clone or copy the project folder to the new machine
2. Open PowerShell
3. Navigate to the project folder:
   ```powershell
   cd C:\path\to\TimerButton
   ```
4. Run the setup script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup-new-machine.ps1
   ```
5. Verify with doctor script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\doctor.ps1
   ```
6. Run the application:
   ```powershell
   python src\main.py
   ```

## Migrating Data

To transfer timer history from another machine:
1. Copy `data\timerbutton.db` from the old machine
2. Place it in the `data\` folder on the new machine
3. Start the application - all history and active timers will be restored

## Using the Standalone Executable

If a packaged `.exe` is available:
1. Copy `MotelRoomTimer.exe` to the new machine
2. Double-click to run - no Python installation needed
3. Data is stored alongside the executable in `data\`
