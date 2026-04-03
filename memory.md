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
- [2026-04-03] Project initialized, Python 3.12 installed
- [2026-04-03] Stack chosen: Python + tkinter + SQLite

## Operational Caveats
- Python WindowsApps stub may interfere - use full path if needed
- SQLite DB stored in `data/timerbutton.db` relative to app root
- WAL mode requires that DB directory is writable

## Unresolved Questions
- None currently

## Lessons Learned
- (will be updated during implementation)
