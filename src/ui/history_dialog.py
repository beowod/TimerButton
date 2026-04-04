import csv
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime

from src.models.timer import Session, format_elapsed


class HistoryDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, sessions: list[Session]) -> None:
        super().__init__(parent)
        self.title("Session History")
        self.geometry("700x450")
        self.transient(parent)
        self._sessions = sessions

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

        self._rows: list[tuple[int, str, str, str]] = []
        for session in sessions:
            start_local = session.start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            end_local = (session.end_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                         if session.end_time else "---")
            elapsed = (format_elapsed(session.total_elapsed_seconds)
                       if session.total_elapsed_seconds is not None else "---")
            row = (session.room_number, start_local, end_local, elapsed)
            self._rows.append(row)
            self._tree.insert("", tk.END, values=row)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)
        export_btn = tk.Button(btn_frame, text="Export CSV", command=self._export_csv)
        export_btn.pack(side=tk.RIGHT, padx=5)

    def _export_csv(self) -> None:
        default_name = datetime.now().strftime("history_%Y-%m-%d_%H-%M-%S.csv")
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Room", "Start Time", "End Time", "Elapsed"])
            for row in self._rows:
                writer.writerow(row)
