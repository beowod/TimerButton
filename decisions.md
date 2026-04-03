# Decision Log - Motel Room Timer

## ADR-001: Application Stack Selection
**Date**: 2026-04-03
**Decision**: Python 3.12 + tkinter + SQLite
**Rationale**:
- Python is available on the target machine (installed via winget)
- tkinter is included with Python - zero external GUI dependency
- SQLite is included with Python - zero external database dependency
- The combination is extremely lightweight (low CPU/memory)
- Grid-based room layout maps perfectly to tkinter's grid geometry manager
- SQLite WAL mode provides crash resilience without complexity
- PyInstaller can produce a single .exe for distribution

**Alternatives Considered**:
| Alternative          | Why Rejected                                                |
|----------------------|-------------------------------------------------------------|
| Electron + JS        | Too heavy (~150MB+), excessive for simple timer app         |
| Tauri + Rust          | Requires Rust toolchain installation, overkill complexity   |
| C# WinForms/WPF      | .NET SDK not available, Windows-only is OK but heavier      |
| Python + PyQt/PySide  | External dependency, licensing considerations               |
| Web app (browser)     | Not a true desktop app, less resilient to browser closure   |

**Implications**: 
- All devs need Python 3.12+ installed
- UI will have native OS look (not custom styled)
- Packaging requires PyInstaller

## ADR-002: Persistence Strategy
**Date**: 2026-04-03
**Decision**: SQLite with WAL mode, timestamp-based timer reconstruction
**Rationale**:
- WAL mode survives app crashes and power loss (transactions are durable)
- Storing events with timestamps allows exact elapsed time reconstruction
- No in-memory-only counters - everything computed from persisted data
- Single file database is simple to backup and manage

**Alternatives Considered**:
| Alternative     | Why Rejected                                              |
|-----------------|-----------------------------------------------------------|
| JSON file       | No ACID guarantees, corruption risk on crash              |
| LevelDB/LMDB   | External dependency, overkill for this use case           |
| Plain text logs | Hard to query, no structured recovery                    |

**Implications**:
- Must use UTC timestamps consistently
- Event log grows over time (may need periodic archival)
- Recovery logic must handle all event combinations

## ADR-003: Timer Model Design
**Date**: 2026-04-03
**Decision**: Event-sourced timer with explicit state machine
**Rationale**:
- States: available -> active -> paused -> active -> finished -> available
- Each transition creates a timestamped event in the DB
- Elapsed time = sum of active intervals computed from event history
- This model is inherently crash-resilient

**Alternatives Considered**:
| Alternative              | Why Rejected                                    |
|--------------------------|-------------------------------------------------|
| Simple start/end only    | Cannot support pause/resume                     |
| RAM counter with periodic save | Loses time between saves on crash          |

**Implications**:
- Event table grows with usage
- Reconstruction algorithm must be well-tested
- All time computations derive from event records

## ADR-004: UI Interaction Model
**Date**: 2026-04-03
**Decision**: Left-click for primary action (start/stop), right-click for pause
**Rationale**:
- Minimizes clicks for the most common operation (start/stop)
- Pause is less frequent, right-click is discoverable but not accidental
- Confirmation dialog on stop prevents accidental timer termination

**Alternatives Considered**:
| Alternative              | Why Rejected                                    |
|--------------------------|-------------------------------------------------|
| Context menu for all     | Too many clicks for fast operation               |
| Double-click to start    | Error-prone under time pressure                  |

**Implications**:
- Must handle right-click binding in tkinter
- Need tooltip or visual hint for pause functionality

## ADR-005: Room Layout as Configuration
**Date**: 2026-04-03
**Decision**: Room layout defined as a 2D array in config.py, UI generated dynamically
**Rationale**:
- Layout changes require only config edit, not code changes
- Dynamic generation prevents hardcoding errors
- Null entries naturally become empty grid cells
- Easy to validate layout matches specification

**Implications**:
- Config validation needed at startup
- Room numbers must be unique in the layout
- UI must handle variable grid sizes
