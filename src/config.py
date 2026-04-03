from pathlib import Path
from typing import Optional

APP_NAME = "Motel Room Timer"
APP_VERSION = "1.0.0"

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

COLORS = {
    "available": {"bg": "#2ecc71", "fg": "#ffffff"},
    "active":    {"bg": "#e74c3c", "fg": "#ffffff"},
    "paused":    {"bg": "#f39c12", "fg": "#000000"},
    "finished":  {"bg": "#3498db", "fg": "#ffffff"},
    "empty":     {"bg": "#ecf0f1", "fg": "#ecf0f1"},
}


def get_all_room_numbers() -> list[int]:
    rooms = []
    for row in ROOM_LAYOUT:
        for cell in row:
            if cell is not None:
                rooms.append(cell)
    return sorted(rooms)
