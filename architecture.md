# Architecture - Motel Room Timer

## Stack

| Component       | Choice          | Rationale                                              |
|-----------------|-----------------|--------------------------------------------------------|
| Language        | Python 3.12     | Available, batteries-included, rapid development       |
| GUI Framework   | tkinter         | Built-in, zero-dependency, lightweight, grid layout    |
| Database        | SQLite (WAL)    | Built-in, embedded, crash-resilient, zero-config       |
| Packaging       | PyInstaller     | Single executable distribution for Windows             |
| Testing         | pytest          | Standard Python test framework, fixtures, assertions   |
| Linting         | flake8 + mypy   | PEP8 compliance + static type checking                 |

## Application Modules

```
┌──────────────────────────────────────────────────────────┐
│                      main.py                             │
│              (Entry point, app bootstrap)                 │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│                      app.py                              │
│         (Application controller, orchestration)          │
└────┬──────────────┬──────────────────┬───────────────────┘
     │              │                  │
┌────▼─────┐  ┌─────▼──────┐  ┌───────▼────────┐
│  ui/     │  │  models/   │  │  persistence/  │
│          │  │            │  │                │
│ room_map │  │ room       │  │ database       │
│ room_btn │  │ timer      │  │ room_repo      │
│ toolbar  │  │ event      │  │ event_repo     │
│ dialogs  │  │ state      │  │ migrations     │
└──────────┘  └────────────┘  └────────────────┘
```

## Data Flow

1. **Startup**: `main.py` -> `app.py` initializes DB -> loads room states from SQLite -> renders UI
2. **Timer Start**: UI click -> `app.py` records start event in DB -> updates room model -> refreshes UI
3. **Timer Running**: UI polls elapsed time by computing `now - start_timestamp` from persisted data
4. **Timer Pause/Resume**: Records pause/resume events with timestamps in DB
5. **Timer Stop**: Records end event -> computes final elapsed -> archives to history
6. **Recovery**: On restart, reads all persisted events -> reconstructs exact state and elapsed time

## Persistence Strategy

### SQLite with WAL Mode
- WAL (Write-Ahead Logging) ensures writes survive crashes
- Single database file: `data/timerbutton.db`
- Checkpoint on clean shutdown
- Journal mode set at DB creation

### Tables
```sql
rooms (
    room_number INTEGER PRIMARY KEY,
    state TEXT NOT NULL DEFAULT 'available',
    current_session_id TEXT
)

sessions (
    id TEXT PRIMARY KEY,
    room_number INTEGER NOT NULL,
    start_time TEXT NOT NULL,        -- ISO 8601 UTC
    end_time TEXT,                    -- ISO 8601 UTC, NULL if active
    total_elapsed_seconds REAL,      -- computed on finalization
    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
)

events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,         -- 'start', 'pause', 'resume', 'stop'
    timestamp TEXT NOT NULL,          -- ISO 8601 UTC
    FOREIGN KEY (session_id) REFERENCES sessions(id)
)
```

### Elapsed Time Reconstruction Formula
```
elapsed = 0
last_start = session.start_time
for event in session.events (ordered by timestamp):
    if event.type == 'pause':
        elapsed += (event.timestamp - last_start)
    elif event.type == 'resume':
        last_start = event.timestamp
    elif event.type == 'stop':
        elapsed += (event.timestamp - last_start)
if state == 'active':
    elapsed += (now - last_start)
```

## Recovery Strategy

1. On app start, open SQLite DB (creates if missing)
2. Read all rooms and their states
3. For rooms in 'active' or 'paused' state, reconstruct elapsed from events
4. Active rooms continue ticking from their last known timestamp
5. No data loss because elapsed time is computed, not stored in RAM

## Testing Architecture

- **Unit tests**: Models (timer state machine, elapsed calculation)
- **Integration tests**: Persistence layer (write/read/recover)
- **Recovery tests**: Simulate restart by closing/reopening DB connection
- **UI tests**: Layout verification (room positions match spec)

## Packaging / Deployment

- PyInstaller creates a single `.exe` for Windows
- No installer needed - just copy and run
- Data directory created on first launch
- Scripts provided for setup, build, and distribution
