import json
from pathlib import Path
from typing import Optional

from src.config import HOTKEY_CONFIG_PATH


DEFAULT_BINDINGS: dict[str, str] = {
    "speed_up": "<Control-Shift-equal>",
    "speed_down": "<Control-Shift-minus>",
}

# Chord digit keysym patterns covering both raw digit and shifted-symbol keysyms
# so Ctrl+Shift+<digit> works regardless of keyboard layout quirks.
CHORD_DIGIT_SEQS: dict[str, list[str]] = {
    "0": ["<Control-Shift-Key-0>", "<Control-Shift-parenright>"],
    "1": ["<Control-Shift-Key-1>", "<Control-Shift-exclam>"],
    "2": ["<Control-Shift-Key-2>", "<Control-Shift-at>"],
    "3": ["<Control-Shift-Key-3>", "<Control-Shift-numbersign>"],
    "4": ["<Control-Shift-Key-4>", "<Control-Shift-dollar>"],
    "5": ["<Control-Shift-Key-5>", "<Control-Shift-percent>"],
    "6": ["<Control-Shift-Key-6>", "<Control-Shift-asciicircum>"],
    "7": ["<Control-Shift-Key-7>", "<Control-Shift-ampersand>"],
    "8": ["<Control-Shift-Key-8>", "<Control-Shift-asterisk>"],
    "9": ["<Control-Shift-Key-9>", "<Control-Shift-parenleft>"],
}

CHORD_TIMEOUT_MS = 700


def action_display_name(action: str) -> str:
    if action.startswith("room_"):
        return f"Room {action[5:]}"
    return action.replace("_", " ").title()


def binding_display(seq: str) -> str:
    inner = seq.strip("<>")
    parts = inner.split("-")
    display: list[str] = []
    for p in parts:
        if p == "Control":
            display.append("Ctrl")
        elif p == "Key":
            continue
        elif p == "equal":
            display.append("=")
        elif p == "minus":
            display.append("-")
        elif p == "plus":
            display.append("+")
        else:
            display.append(p)
    return "+".join(display)


class HotkeyConfig:

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self._path = config_path or HOTKEY_CONFIG_PATH
        self._bindings: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._bindings = data.get("bindings", {})
                return
            except (json.JSONDecodeError, OSError):
                pass
        self._bindings = dict(DEFAULT_BINDINGS)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"bindings": self._bindings}, f, indent=2)

    @property
    def bindings(self) -> dict[str, str]:
        return dict(self._bindings)

    def get(self, action: str) -> Optional[str]:
        return self._bindings.get(action)

    def set_binding(self, action: str, key_sequence: str) -> None:
        self._bindings[action] = key_sequence

    def remove(self, action: str) -> None:
        self._bindings.pop(action, None)

    def update_all(self, bindings: dict[str, str]) -> None:
        self._bindings = dict(bindings)
