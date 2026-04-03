# AGENTS.md - Motel Room Timer Application

## Project Overview
Local desktop application for motel room time tracking using stopwatch-like timers.
Built with Python 3.12 + tkinter + SQLite.

## Core Commands

- Run application: `python src/main.py`
- Run all tests: `python -m pytest tests/ -v`
- Run single test: `python -m pytest tests/<file>.py -v`
- Lint: `python -m flake8 src/ tests/`
- Type check: `python -m mypy src/`
- Package: `python -m PyInstaller scripts/timerbutton.spec`
- Install deps: `pip install -r requirements.txt`
- Install dev deps: `pip install -r requirements-dev.txt`

## Project Layout

```
TimerButton/
├── src/                  # Application source code
│   ├── main.py           # Entry point
│   ├── app.py            # Main application window
│   ├── models/           # Domain models (Room, Timer, Event)
│   ├── persistence/      # SQLite database layer
│   ├── ui/               # tkinter UI components
│   └── config.py         # Room layout and app configuration
├── tests/                # Test suite
├── scripts/              # Setup, build, and ops scripts
├── docs/                 # User and operator documentation
├── data/                 # Runtime data directory (SQLite DB, logs)
├── AGENTS.md             # This file
├── memory.md             # Persistent project memory
├── architecture.md       # System architecture
├── design.md             # UX/UI design
└── decisions.md          # ADR-style decision log
```

## Architecture Boundaries

- `src/models/` owns all domain logic. No UI imports allowed here.
- `src/persistence/` owns all database access. Models use it, UI does not directly.
- `src/ui/` owns all tkinter widgets. It reads models but never writes to DB directly.
- `src/config.py` is the single source of truth for room layout and app constants.

## Coding Standards

- Python 3.12+, type hints on all public functions
- PEP 8 style, max line length 100
- Use `pathlib.Path` for all file paths
- Use `datetime.datetime` with UTC for all timestamps
- Use `enum.Enum` for state machines
- No global mutable state outside the application class
- Docstrings on all public classes and methods
- Prefer composition over inheritance

## Testing Rules

- Tests live in `tests/` mirroring `src/` structure
- Use pytest with fixtures for DB setup/teardown
- Test persistence recovery: simulate app restart by closing and reopening DB
- Test timer reconstruction from persisted timestamps
- Test room layout matches required visual arrangement
- Mock time where needed using `unittest.mock.patch`

## Documentation Update Rules

- Update `memory.md` after any significant implementation fact or lesson
- Update `decisions.md` for every non-trivial technical choice
- Update `architecture.md` if module boundaries or data flow change
- Update `design.md` if UI behavior or visual states change

## Subagent Policy

- Subagents may be used for parallel implementation of independent modules
- Each subagent must read AGENTS.md before starting work
- Subagents must not modify documentation files without coordination
- Subagents report results; main agent integrates and validates

## Decision Policy

- Decide autonomously on implementation details
- Document every decision in decisions.md
- Ask user only for: unclear business rules, missing credentials, destructive actions
