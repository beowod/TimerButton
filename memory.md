# Project Memory - Motel Room Timer

## Business Context
- Application for motel operators to track room rental time
- Each room has an independent timer (stopwatch-style)
- Operators need to quickly see which rooms are occupied and for how long
- The room layout on screen must match the physical motel layout
- Timer correctness is critical - must survive crashes, reboots, power loss

## Environment
- Platform: Windows 10 (10.0.26200)
- Python: 3.12.10 (installed via winget)
- tkinter: Built-in with Python 3.12
- sqlite3: Built-in with Python 3.12
- Package manager: winget available
- Git: 2.52.0 (no repo initialized yet)

## Constraints
- Fully local, no cloud dependency
- Low resource usage (CPU and memory)
- Must persist state locally using SQLite
- Timer elapsed time computed from timestamps, never from RAM counters alone
- 43 rooms total arranged in a specific 11x4 grid layout
- Room layout has one null gap at position [0][0]

## Room Layout
- 11 rows x 4 columns grid
- Rooms: 1-6, 9-25, 28-38, 45-55 (43 rooms total)
- One null placeholder at top-left corner
- Layout must be rendered dynamically from config, not hardcoded

## Known Assumptions
- Single operator machine (no multi-user concurrency)
- Local timezone display is acceptable for the UI
- UTC storage for all persisted timestamps
- SQLite WAL mode provides adequate crash resilience
- Room numbers are fixed and do not change at runtime

## Implementation Facts
- [2026-04-03] Project initialized, Python 3.12 installed via winget
- [2026-04-03] Stack chosen: Python 3.12 + tkinter + SQLite
- [2026-04-03] Core implementation complete: models, persistence, UI, tests
- [2026-04-03] 33 tests passing, all lint clean
- [2026-04-03] Room 14 and 50 do not exist in the layout (43 rooms, not 45)
- [2026-04-03] Empty __init__.py files trigger W391 - ignored in setup.cfg
- [2026-04-03] Scripts created for: setup, deps, dev, testing, packaging, doctor
- [2026-04-03] Added 3-hour timer limit with blinking overdue alert
- [2026-04-03] Added CSV export to history dialog (default filename = current datetime)
- [2026-04-03] TIMER_LIMIT_SECONDS in config.py is the single knob for testing lower limits
- [2026-04-03] 37 tests passing after new features

## Operational Caveats
- Python WindowsApps stub may interfere - use full path or refresh PATH
- SQLite DB stored in `data/timerbutton.db` relative to app root
- WAL mode requires that DB directory is writable
- Auto-reset of finished rooms happens after 3 seconds
- Stop timer requires confirmation dialog to prevent accidental stops
- PATH must be refreshed after Python install: restart terminal or use $env:Path refresh

## Unresolved Questions
- None currently

## Lessons Learned
- [2026-04-03] winget Python install does not immediately update current shell PATH
- [2026-04-03] flake8 W391 triggered on empty files even when content is empty string
- [2026-04-03] Room layout has gaps: rooms 7,8,14,26,27,39-44,50 do not exist
