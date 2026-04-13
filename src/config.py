from pathlib import Path
from typing import Optional

APP_NAME = "Motel Room Timer"
APP_VERSION = "2.2.9"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "timerbutton.db"

ROOM_LAYOUT: list[list[Optional[int]]] = [
    [None, 38, 15, 13],
    [45,   37, 16, 12],
    [46,   36, 17, 11],
    [47,   35, 18, 10],
    [48,   34, 19,  9],
    [49,   33, 20,  6],
    [51,   32, 21,  5],
    [52,   31, 22,  4],
    [53,   30, 23,  3],
    [54,   29, 24,  2],
    [55,   28, 25,  1],
]

UI_UPDATE_INTERVAL_MS = 1000
BUTTON_WIDTH = 12
BUTTON_HEIGHT = 3
BUTTON_FONT = ("Segoe UI", 11, "bold")
ELAPSED_FONT = ("Segoe UI", 9)

# Timer limit in seconds. When elapsed time reaches this value, the room
# button starts blinking to signal that the room must be vacated soon.
# Default: 3 hours (10800 seconds).
# For testing, set to a lower value, e.g. 10 for 10 seconds.
TIMER_LIMIT_SECONDS = 3 * 60 * 60

# Blink interval in milliseconds (how fast the overdue indicator flashes)
BLINK_INTERVAL_MS = 500

SPEED_MIN = 1
SPEED_MAX = 10
SPEED_LABEL_FONT = ("Segoe UI", 11, "bold")
HOTKEY_CONFIG_PATH = DATA_DIR / "hotkeys.json"
GITHUB_REPO = "beowod/TimerButton"

COLORS = {
    "available": {"bg": "#2ecc71", "fg": "#ffffff"},
    "active":    {"bg": "#e74c3c", "fg": "#ffffff"},
    "paused":    {"bg": "#f39c12", "fg": "#000000"},
    "finished":  {"bg": "#3498db", "fg": "#ffffff"},
    "empty":     {"bg": "#ecf0f1", "fg": "#ecf0f1"},
    "overdue":   {"bg": "#ffffff", "fg": "#e74c3c"},
}


def get_all_room_numbers() -> list[int]:
    rooms = []
    for row in ROOM_LAYOUT:
        for cell in row:
            if cell is not None:
                rooms.append(cell)
    return sorted(rooms)
