import tkinter as tk
from typing import Callable, Optional

from src.config import COLORS, BUTTON_WIDTH, BUTTON_FONT, ELAPSED_FONT
from src.models.state import RoomState


class RoomButton(tk.Frame):
    def __init__(self, parent: tk.Widget, room_number: int,
                 on_left_click: Callable[[int], None],
                 on_right_click: Callable[[int], None]) -> None:
        super().__init__(parent, bd=1, relief=tk.RAISED)
        self._room_number = room_number
        self._state = RoomState.AVAILABLE
        self._overdue = False
        self._blink_on = True
        self._on_left_click = on_left_click
        self._on_right_click = on_right_click

        self._number_label = tk.Label(
            self, text=str(room_number), font=BUTTON_FONT,
            width=BUTTON_WIDTH, height=1
        )
        self._number_label.pack(fill=tk.X)

        self._elapsed_label = tk.Label(
            self, text="", font=ELAPSED_FONT,
            width=BUTTON_WIDTH, height=1
        )
        self._elapsed_label.pack(fill=tk.X)

        self._apply_colors(RoomState.AVAILABLE)

        self.bind("<Button-1>", self._handle_left_click)
        self._number_label.bind("<Button-1>", self._handle_left_click)
        self._elapsed_label.bind("<Button-1>", self._handle_left_click)

        self.bind("<Button-3>", self._handle_right_click)
        self._number_label.bind("<Button-3>", self._handle_right_click)
        self._elapsed_label.bind("<Button-3>", self._handle_right_click)

    @property
    def room_number(self) -> int:
        return self._room_number

    @property
    def overdue(self) -> bool:
        return self._overdue

    def update_display(self, state: RoomState,
                       elapsed_text: Optional[str] = None,
                       overdue: bool = False) -> None:
        self._state = state
        self._overdue = overdue
        if not overdue:
            self._blink_on = True
        self._apply_colors(state)
        self._elapsed_label.config(text=elapsed_text or "")

    def toggle_blink(self) -> None:
        if not self._overdue:
            return
        self._blink_on = not self._blink_on
        if self._blink_on:
            colors = COLORS[self._state.value]
        else:
            colors = COLORS["overdue"]
        self.config(bg=colors["bg"])
        self._number_label.config(bg=colors["bg"], fg=colors["fg"])
        self._elapsed_label.config(bg=colors["bg"], fg=colors["fg"])

    def _apply_colors(self, state: RoomState) -> None:
        colors = COLORS[state.value]
        self.config(bg=colors["bg"])
        self._number_label.config(bg=colors["bg"], fg=colors["fg"])
        self._elapsed_label.config(bg=colors["bg"], fg=colors["fg"])

    def _handle_left_click(self, event: tk.Event) -> None:
        self._on_left_click(self._room_number)

    def _handle_right_click(self, event: tk.Event) -> None:
        self._on_right_click(self._room_number)
