# Design - Motel Room Timer

## UX Goals
- Operator can see all rooms at a glance on a single screen
- Room status is immediately obvious by color
- Starting/stopping a timer is a single click
- Elapsed time is always visible on active rooms
- The screen layout matches the physical motel room arrangement
- Minimal training needed - the interface is self-explanatory

## UI Layout

### Main Window
```
┌─────────────────────────────────────────────────┐
│  Motel Room Timer                    [History]  │
├─────────────────────────────────────────────────┤
│                                                 │
│   [  ]  [38]  [15]  [13]                       │
│   [45]  [37]  [16]  [12]                       │
│   [46]  [36]  [17]  [11]                       │
│   [47]  [35]  [18]  [10]                       │
│   [48]  [34]  [19]  [ 9]                       │
│   [49]  [33]  [20]  [ 6]                       │
│   [51]  [32]  [21]  [ 5]                       │
│   [52]  [31]  [22]  [ 4]                       │
│   [53]  [30]  [23]  [ 3]                       │
│   [54]  [29]  [24]  [ 2]                       │
│   [55]  [28]  [25]  [ 1]                       │
│                                                 │
├─────────────────────────────────────────────────┤
│  Rooms: 43 | Active: 0 | Available: 43         │
└─────────────────────────────────────────────────┘
```

### Room Button States and Colors

| State        | Background       | Text Color | Label Content        |
|--------------|------------------|------------|----------------------|
| Available    | Green            | White      | Room number          |
| Active       | Red              | White      | Room # + HH:MM:SS   |
| Active (overdue) | Red/White blink | Red/White | Room # + HH:MM:SS (blinking) |
| Paused       | Orange           | Black      | Room # + HH:MM:SS   |
| Paused (overdue) | Orange/White blink | Orange/White | Room # + HH:MM:SS (blinking) |
| Finished     | Blue             | White      | Room # + final time  |

### Timer Limit and Overdue Alert
- Default timer limit: 3 hours (configurable in `src/config.py`)
- When elapsed time reaches the limit, the room button starts blinking
- Blink alternates between the normal state color and white/red every 500ms
- Blinking continues until the timer is stopped or reset
- To change the limit for testing, edit `TIMER_LIMIT_SECONDS` in `src/config.py`

### Room Button Rendering
- Each button is a fixed-size cell in a tkinter grid
- Null positions render as empty frames (no button)
- Grid dynamically generated from `config.ROOM_LAYOUT`
- Button size large enough for room number + elapsed time display
- Font size optimized for readability at typical screen distance

## Room-Map Rendering Strategy
1. Read `ROOM_LAYOUT` 2D array from config
2. Iterate rows and columns
3. For each cell: if `null`, place empty frame; if room number, place room button
4. Room button widget binds click to state transition handler
5. UI refresh loop updates elapsed times every second

## Visual States for Rooms

### State Machine Per Room
```
                 ┌─────────┐
                 │Available│
                 └────┬────┘
                      │ click (start)
                 ┌────▼────┐
            ┌────│ Active  │────┐
            │    └────┬────┘    │
     click  │         │ click   │ click
    (pause) │    (stop/finish)  │ (stop)
            │         │        │
       ┌────▼───┐     │        │
       │ Paused │     │        │
       └────┬───┘     │        │
            │ click   │        │
           (resume)   │        │
            │    ┌────▼────┐   │
            └───>│Finished │<──┘
                 └────┬────┘
                      │ click (reset)
                 ┌────▼────┐
                 │Available│
                 └─────────┘
```

## Operator Workflows

### Start a Room Timer
1. Click green (available) room button
2. Button turns red, timer starts counting

### Pause a Timer
1. Right-click active (red) room button
2. Button turns orange, timer pauses

### Resume a Paused Timer
1. Click orange (paused) room button
2. Button turns red, timer resumes

### Stop / Finalize a Timer
1. Click active (red) room button
2. Confirmation dialog appears
3. On confirm: button turns blue showing final time
4. After brief display, resets to green (available)

### View History
1. Click "History" button in toolbar
2. Dialog shows past sessions with room, start, end, elapsed

### Export History to CSV
1. Open the History dialog
2. Click "Export CSV" button
3. A save dialog appears with default filename set to current date/time
4. Choose location and save

## Accessibility and Readability
- High contrast colors for each state
- Large font for room numbers
- Elapsed time displayed in HH:MM:SS format
- Status bar shows summary counts
- Keyboard navigation support (Tab through rooms)

## Low-Friction Design Principles
- No menus to navigate for core operations
- Single click for most operations
- Confirmation only for destructive actions (stop timer)
- Auto-save: every state change persists immediately
- No manual save/load needed
