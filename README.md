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
- **3-hour timer limit** with blinking alert when exceeded
- Color-coded room states (green=available, red=active, orange=paused, blue=finished)
- Crash-resilient: timers survive app close, reboot, and power loss
- Elapsed time reconstructed from persisted timestamps (SQLite)
- Session history with timestamps and elapsed times
- **CSV export** of session history (default filename = current date/time)
- Single-click operation for fast workflow

## Room Controls

| Action | Gesture |
|--------|---------|
| Start timer | Left-click green room |
| Stop timer | Left-click red room (with confirmation) |
| Pause timer | Right-click red room |
| Resume timer | Left-click orange room |
| Reset finished | Left-click blue room (or auto-resets after 3s) |

## Configuring the Timer Limit

Edit `src/config.py` and change `TIMER_LIMIT_SECONDS`:

```python
# Default: 3 hours
TIMER_LIMIT_SECONDS = 3 * 60 * 60

# For testing: 10 seconds
TIMER_LIMIT_SECONDS = 10
```

Restart the app after changing the value.

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
