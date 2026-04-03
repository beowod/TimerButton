# Motel Room Timer

Local desktop application for motel room time tracking using stopwatch-like timers.

## Quick Start

```powershell
# Install dependencies
python -m pip install -r requirements-dev.txt

# Run the app
python src\main.py

# Run tests
python -m pytest tests/ -v
```

## Features

- Visual room map matching the physical motel layout (43 rooms)
- Independent timer per room with start/pause/resume/stop
- Color-coded room states (green=available, red=active, orange=paused, blue=finished)
- Crash-resilient: timers survive app close, reboot, and power loss
- Elapsed time reconstructed from persisted timestamps (SQLite)
- Session history with timestamps and elapsed times
- Single-click operation for fast workflow

## Room Controls

| Action | Gesture |
|--------|---------|
| Start timer | Left-click green room |
| Stop timer | Left-click red room (with confirmation) |
| Pause timer | Right-click red room |
| Resume timer | Left-click orange room |
| Reset finished | Left-click blue room (or auto-resets after 3s) |

## Stack

- Python 3.12 + tkinter (GUI)
- SQLite with WAL mode (persistence)
- pytest (testing)

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Setup New Machine](docs/SETUP_NEW_MACHINE.md)
- [User Manual](docs/USER_MANUAL.md)
- [Operations Guide](docs/OPERATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Testing Guide](docs/TESTING.md)
