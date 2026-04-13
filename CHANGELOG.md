# Changelog

All notable changes to the Motel Room Timer application will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.6] - 2026-04-06

### Fixed
- Version bump to test self-update from v2.2.5

## [2.2.5] - 2026-04-06

### Fixed
- Replaced batch update script with PowerShell for reliable process detection
- PowerShell uses Get-Process by PID instead of fragile tasklist+find pipe
- Hidden window style prevents console flash during update
- Proper error handling with try/catch instead of errorlevel checks

## [2.2.4] - 2026-04-06

### Fixed
- Version bump to test self-update from v2.2.3

## [2.2.3] - 2026-04-06

### Fixed
- Version bump to test self-update from v2.2.2

## [2.2.2] - 2026-04-06

### Fixed
- Self-updater: use `os._exit(0)` to force-terminate (tkinter swallows `sys.exit`)
- Batch script: enable delayed expansion so retry counter works inside if-blocks
- Batch script: force-kill app after 30s timeout if it refuses to exit
- Batch script: writes log to `%TEMP%\_timerbutton_update.log` for debugging

## [2.2.1] - 2026-04-06

### Fixed
- Version bump to validate self-update flow from v2.2.0

## [2.2.0] - 2026-04-06

### Added
- Timer speed multiplier now goes up to 10x (was 8x)
- Pause All / Resume All button in toolbar
- Pause All hotkey: Ctrl+Shift+P (toggles between pause and resume)
- Pause All is configurable in the hotkey editor

## [2.1.0] - 2026-04-06

### Added
- "Check for Updates" button in toolbar
- Automatic update checker: queries GitHub Releases API for new versions
- Download progress dialog with percentage and MB counter
- Self-update for packaged .exe: downloads new version, swaps executable, restarts
- Rollback safety: keeps .exe.bak of previous version during update
- Graceful fallback when running from source (shows download path)

## [2.0.0] - 2026-04-06

### Added
- Timer speed multiplier (1x to 8x) affecting all active timers
- Speed multiplier label and +/- buttons in toolbar
- Configurable hotkey system with JSON-persisted bindings
- Hotkey editor dialog accessible from toolbar
- Default room hotkeys: Ctrl+Shift+{1-6, 9} for single-digit rooms
- Speed control hotkeys: Ctrl+Shift+= (up) and Ctrl+Shift+- (down)
- GitHub Actions release workflow for automated builds on version tags
- CHANGELOG.md for version tracking

## [1.0.0] - 2026-04-03

### Added
- Room map with 43 rooms in 4-column layout
- Timer states: Available, Active, Paused, Finished
- 3-hour timer limit with blinking overdue alert
- Session history dialog with CSV export
- SQLite persistence with WAL mode and crash recovery
