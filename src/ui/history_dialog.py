import tkinter as tk
from tkinter import ttk
from src.models.timer import Session, format_elapsed


class HistoryDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, sessions: list[Session]) -> None:
        super().__init__(parent)
        self.title("Session History")
        self.geometry("700x450")
        self.transient(parent)

        columns = ("room", "start", "end", "elapsed")
        self._tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        self._tree.heading("room", text="Room")
        self._tree.heading("start", text="Start Time")
        self._tree.heading("end", text="End Time")
        self._tree.heading("elapsed", text="Elapsed")

        self._tree.column("room", width=60, anchor="center")
        self._tree.column("start", width=200, anchor="center")
        self._tree.column("end", width=200, anchor="center")
        self._tree.column("elapsed", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        for session in sessions:
            start_local = session.start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            end_local = (session.end_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                         if session.end_time else "---")
            elapsed = (format_elapsed(session.total_elapsed_seconds)
                       if session.total_elapsed_seconds is not None else "---")
            self._tree.insert("", tk.END, values=(
                session.room_number, start_local, end_local, elapsed
            ))

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)
