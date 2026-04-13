import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from src.updater import (
    ReleaseInfo, check_for_update, download_update, apply_update, is_frozen,
)
from src.config import APP_VERSION


class UpdateDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Check for Updates")
        self.geometry("420x200")
        self.transient(parent)  # type: ignore[call-overload]
        self.resizable(False, False)

        self._parent = parent
        self._release: Optional[ReleaseInfo] = None

        self._status = tk.Label(
            self, text="Checking for updates...", font=("Segoe UI", 10),
        )
        self._status.pack(pady=(20, 5))

        self._progress = ttk.Progressbar(self, length=350, mode="indeterminate")
        self._progress.pack(pady=5)
        self._progress.start(20)

        self._btn_frame = tk.Frame(self)
        self._btn_frame.pack(pady=10)
        self._close_btn = tk.Button(
            self._btn_frame, text="Cancel", command=self.destroy,
        )
        self._close_btn.pack(side=tk.RIGHT, padx=5)

        self._update_btn = tk.Button(
            self._btn_frame, text="Download && Install", state=tk.DISABLED,
            command=self._start_download,
        )
        self._update_btn.pack(side=tk.RIGHT, padx=5)

        self._check_thread = threading.Thread(target=self._do_check, daemon=True)
        self._check_thread.start()

    def _do_check(self) -> None:
        release = check_for_update()
        self.after(0, self._on_check_done, release)

    def _on_check_done(self, release: Optional[ReleaseInfo]) -> None:
        self._progress.stop()
        if release is None:
            self._status.config(
                text=f"You are up to date! (v{APP_VERSION})"
            )
            self._progress.config(mode="determinate", value=100)
            self._close_btn.config(text="Close")
            return

        self._release = release
        size_mb = release.asset_size / (1024 * 1024)
        self._status.config(
            text=f"New version available: v{release.version}  ({size_mb:.1f} MB)"
        )
        self._progress.config(mode="determinate", value=0)
        self._update_btn.config(state=tk.NORMAL)
        self._close_btn.config(text="Skip")

    def _start_download(self) -> None:
        if self._release is None:
            return
        self._update_btn.config(state=tk.DISABLED)
        self._close_btn.config(state=tk.DISABLED)
        self._status.config(text="Downloading update...")
        self._progress.config(mode="determinate", value=0, maximum=100)

        thread = threading.Thread(
            target=self._do_download, args=(self._release,), daemon=True,
        )
        thread.start()

    def _do_download(self, release: ReleaseInfo) -> None:
        try:
            def _progress(done: int, total: int) -> None:
                self.after(0, self._on_download_progress, done, total)

            new_exe = download_update(release, on_progress=_progress)
            self.after(0, self._on_download_done, new_exe, None)
        except Exception as exc:
            self.after(0, self._on_download_done, None, str(exc))

    def _on_download_progress(self, downloaded: int, total: int) -> None:
        pct = int(downloaded * 100 / total) if total else 0
        self._progress.config(value=pct)
        mb_done = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        self._status.config(
            text=f"Downloading... {mb_done:.1f} / {mb_total:.1f} MB  ({pct}%)"
        )

    def _on_download_done(self, new_exe: object, error: Optional[str]) -> None:
        if error or new_exe is None:
            self._status.config(text=f"Download failed: {error}")
            self._close_btn.config(state=tk.NORMAL, text="Close")
            return

        self._progress.config(value=100)
        self._status.config(text="Download complete. Ready to install.")

        if not is_frozen():
            messagebox.showinfo(
                "Update Downloaded",
                f"Update downloaded to:\n{new_exe}\n\n"
                "Auto-install is only available for the packaged .exe build.\n"
                "Please replace the executable manually.",
                parent=self,
            )
            self._close_btn.config(state=tk.NORMAL, text="Close")
            return

        confirm = messagebox.askyesno(
            "Install Update",
            "The application will close and restart with the new version.\n\n"
            "Proceed?",
            parent=self,
        )
        if not confirm:
            self._close_btn.config(state=tk.NORMAL, text="Close")
            return

        import sys
        from pathlib import Path
        apply_update(Path(str(new_exe)))
        sys.exit(0)
