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
| Red/White blinking | Active (overdue) | Timer exceeded 3 hours - room must be vacated |
| Orange | Paused    | Timer is paused            |
| Orange/White blinking | Paused (overdue) | Paused but already exceeded 3 hours |
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

### Export History to CSV
- In the History dialog, click "Export CSV"
- A save dialog opens with a default filename based on the current date and time
- Choose a location and click Save
- The CSV file contains: Room, Start Time, End Time, Elapsed

## Status Bar

The bottom bar shows:
- Total number of rooms
- Number of active timers
- Number of paused timers
- Number of available rooms

## Timer Limit (Overdue Alert)

By default, rooms have a **3-hour timer limit**. When the elapsed time reaches 3 hours:
- The room button starts **blinking** (alternating between its normal color and white)
- This signals the operator that the room must be vacated soon
- The blinking continues until the timer is stopped

To change the limit (e.g., for testing), edit `src\config.py`:
```python
TIMER_LIMIT_SECONDS = 10  # 10 seconds for testing
```
Restart the app after changing the value.

## Data Safety

- Every action is saved immediately to the database
- If the app closes unexpectedly, all timer data is preserved
- On next launch, active timers continue from their correct elapsed time
- No data is ever lost due to crashes, reboots, or power loss
