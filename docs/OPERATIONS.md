# Operations Guide

## Daily Operations

1. Start the app at the beginning of the shift
2. Start timers as rooms are rented
3. Stop timers when rooms are vacated
4. Use History to review completed sessions if needed

## Database Location

- Database file: `data\timerbutton.db`
- This is an SQLite database in WAL mode
- Do NOT delete this file while the app is running

## Backup

To backup timer data:
```powershell
copy data\timerbutton.db data\timerbutton_backup.db
```

## Restore

To restore from backup:
1. Close the application
2. Replace `data\timerbutton.db` with your backup file
3. Restart the application

## After Unexpected Shutdown

1. Simply restart the application
2. All active timers will resume with correct elapsed times
3. Paused timers remain paused
4. No manual intervention needed

## Log / History

All timer events are stored in the database. The History dialog shows completed sessions. For advanced queries, use any SQLite viewer (e.g., DB Browser for SQLite) to inspect `data\timerbutton.db`.

## Performance

The app is designed to use minimal resources:
- Memory: ~20-30 MB
- CPU: Near zero when idle, minimal during updates
- Disk: Database grows slowly with usage
