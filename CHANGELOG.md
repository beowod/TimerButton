# Changelog

All notable changes to the Motel Room Timer application will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
