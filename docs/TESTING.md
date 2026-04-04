# Testing Guide

## Running Tests

```powershell
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Single test file
python -m pytest tests/test_timer.py -v

# Single test
python -m pytest tests/test_timer.py::test_active_timer_elapsed -v
```

## Test Coverage

| Module           | What's Tested                                          |
|------------------|--------------------------------------------------------|
| test_config.py   | Room layout dimensions, positions, room count          |
| test_state.py    | State machine transitions, valid/invalid transitions   |
| test_timer.py    | Elapsed time computation, formatting, all event combos |
| test_csv_export.py | CSV export content, default filename format           |
| test_persistence.py | DB creation, CRUD, session lifecycle, crash recovery |

## Testing with a Lower Timer Limit

To test the blinking overdue alert without waiting 3 hours, edit `src/config.py`:

```python
TIMER_LIMIT_SECONDS = 10  # 10 seconds for quick testing
```

Start the app, click a room, and after 10 seconds it will start blinking.
Remember to restore the value to `3 * 60 * 60` after testing.

## Key Test Scenarios

### Timer Reconstruction (test_timer.py)
- Active timer: elapsed = now - start
- Paused timer: elapsed = pause_time - start_time
- Resume after pause: elapsed = active_periods_sum
- Multiple pause/resume cycles
- Stopped timer with final elapsed

### Crash Recovery (test_persistence.py::test_recovery_after_restart)
- Creates room with active timer and events
- Closes database (simulates crash)
- Opens new database connection
- Verifies room state, session, events all recovered
- Verifies elapsed time computed correctly from recovered data

### Room Layout (test_config.py)
- 11 rows x 4 columns
- Exactly 1 null position
- 43 unique room numbers
- Specific room positions match specification

## Linting

```powershell
python -m flake8 src/ tests/
```

## Running Everything

```powershell
powershell -ExecutionPolicy Bypass -File scripts\test-all.ps1
```
