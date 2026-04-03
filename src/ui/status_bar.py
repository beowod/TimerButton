import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bd=1, relief=tk.SUNKEN)
        self._label = tk.Label(self, text="", anchor=tk.W, padx=10)
        self._label.pack(fill=tk.X)

    def update_counts(self, total: int, active: int, paused: int, available: int) -> None:
        self._label.config(
            text=f"Rooms: {total}  |  Active: {active}  |  "
                 f"Paused: {paused}  |  Available: {available}"
        )
