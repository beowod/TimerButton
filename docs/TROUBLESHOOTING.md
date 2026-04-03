# Troubleshooting

## Application Won't Start

### "Python was not found"
- Python is not installed or not in PATH
- Run: `winget install Python.Python.3.12`
- Restart your terminal after installation

### "No module named tkinter"
- tkinter should be included with Python 3.12
- Reinstall Python ensuring "tcl/tk" is selected in the installer

### "No module named src"
- Run the app from the project root directory
- Use: `python src\main.py` (not `cd src && python main.py`)

## Database Issues

### "database is locked"
- Another instance of the app may be running
- Close all instances and restart
- If persistent, delete `data\timerbutton.db-wal` and `data\timerbutton.db-shm`

### Data appears missing after restart
- Check that `data\timerbutton.db` exists
- The app creates it automatically on first launch
- If it was deleted, history is lost but the app will work with a fresh database

## Timer Issues

### Timer shows wrong elapsed time
- This should not happen. Elapsed time is computed from timestamps.
- If it does, check system clock accuracy
- All timestamps are stored in UTC

### Room stuck in a state
- If a room appears stuck, right-click for options
- For a "finished" room that won't reset, left-click it
- If truly stuck, restart the application - states are recovered from DB

## Display Issues

### Buttons too small/large
- The app adapts to window size
- Resize the window to adjust
- Room buttons scale with the grid layout

### Colors look different
- Colors are defined in `src\config.py`
- Modify the COLORS dictionary to change them

## Running Diagnostics

```powershell
powershell -ExecutionPolicy Bypass -File scripts\doctor.ps1
```

This checks Python, tkinter, sqlite3, and development tools.
