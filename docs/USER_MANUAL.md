# User Manual

## Overview

The Motel Room Timer displays all 43 motel rooms as a visual map matching the physical layout. Each room button shows its number and, when active, the elapsed time.

## Starting the Application

```powershell
python src\main.py
```

## Room States and Colors

| Color  | State     | Meaning                    |
|--------|-----------|----------------------------|
| Green  | Available | Room is free               |
| Red    | Active    | Timer is running           |
| Orange | Paused    | Timer is paused            |
| Blue   | Finished  | Timer stopped, showing time|

## Operating Rooms

### Start a Timer
- Left-click a **green** room button
- The room turns red and the timer starts counting up

### Pause a Timer
- Right-click a **red** (active) room button
- The room turns orange and the timer pauses
- Elapsed time is preserved

### Resume a Paused Timer
- Left-click an **orange** (paused) room button
- The room turns red and the timer resumes from where it paused

### Stop a Timer
- Left-click a **red** (active) room button
- A confirmation dialog shows the elapsed time
- Click "Yes" to stop, "No" to keep running
- Room turns blue briefly showing final time, then resets to green

### View History
- Click the "History" button in the top-right corner
- See all completed sessions with room number, start/end time, and elapsed time

## Status Bar

The bottom bar shows:
- Total number of rooms
- Number of active timers
- Number of paused timers
- Number of available rooms

## Data Safety

- Every action is saved immediately to the database
- If the app closes unexpectedly, all timer data is preserved
- On next launch, active timers continue from their correct elapsed time
- No data is ever lost due to crashes, reboots, or power loss
