import tkinter as tk
from typing import Callable, Optional

from src.config import ROOM_LAYOUT, COLORS
from src.ui.room_button import RoomButton


class RoomMap(tk.Frame):
    def __init__(self, parent: tk.Widget,
                 on_left_click: Callable[[int], None],
                 on_right_click: Callable[[int], None]) -> None:
        super().__init__(parent, padx=10, pady=10)
        self._buttons: dict[int, RoomButton] = {}
        self._build_grid(on_left_click, on_right_click)

    def _build_grid(self, on_left_click: Callable[[int], None],
                    on_right_click: Callable[[int], None]) -> None:
        for row_idx, row in enumerate(ROOM_LAYOUT):
            for col_idx, cell in enumerate(row):
                if cell is None:
                    placeholder = tk.Frame(
                        self, width=120, height=60,
                        bg=COLORS["empty"]["bg"]
                    )
                    placeholder.grid(row=row_idx, column=col_idx,
                                     padx=2, pady=2, sticky="nsew")
                    placeholder.grid_propagate(False)
                else:
                    btn = RoomButton(
                        self, room_number=cell,
                        on_left_click=on_left_click,
                        on_right_click=on_right_click
                    )
                    btn.grid(row=row_idx, column=col_idx,
                             padx=2, pady=2, sticky="nsew")
                    self._buttons[cell] = btn

        for col in range(len(ROOM_LAYOUT[0])):
            self.grid_columnconfigure(col, weight=1, uniform="col")
        for row in range(len(ROOM_LAYOUT)):
            self.grid_rowconfigure(row, weight=1, uniform="row")

    def get_button(self, room_number: int) -> Optional[RoomButton]:
        return self._buttons.get(room_number)

    @property
    def buttons(self) -> dict[int, RoomButton]:
        return self._buttons
