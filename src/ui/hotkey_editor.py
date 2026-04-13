import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from src.config import get_all_room_numbers
from src.hotkeys import HotkeyConfig, action_display_name, binding_display


MODIFIER_KEYSYMS = frozenset({
    "Control_L", "Control_R", "Shift_L", "Shift_R",
    "Alt_L", "Alt_R", "Meta_L", "Meta_R", "Caps_Lock",
})


def _event_to_binding(event: tk.Event) -> Optional[str]:
    if event.keysym in MODIFIER_KEYSYMS:
        return None
    state = int(event.state)
    parts: list[str] = []
    if state & 0x4:
        parts.append("Control")
    if state & 0x1:
        parts.append("Shift")
    if state & 0x20000:
        parts.append("Alt")
    parts.append(f"Key-{event.keysym}")
    return "<" + "-".join(parts) + ">"


class HotkeyEditorDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config: HotkeyConfig,
                 on_save: Callable[[], None]) -> None:
        super().__init__(parent)
        self.title("Edit Hotkeys")
        self.geometry("520x480")
        self.transient(parent)  # type: ignore[call-overload]
        self.grab_set()

        self._config = config
        self._on_save = on_save
        self._edited: dict[str, str] = dict(config.bindings)

        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        info = tk.Label(
            self, anchor="w", justify=tk.LEFT, padx=10, pady=6,
            text="Rooms: press Ctrl+Shift+<room number> (e.g. 3 then 8 for room 38).\n"
                 "Below you can edit speed controls or add explicit room shortcuts.",
            font=("Segoe UI", 9),
        )
        info.pack(fill=tk.X)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        columns = ("action", "binding")
        self._tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self._tree.heading("action", text="Action")
        self._tree.heading("binding", text="Hotkey")
        self._tree.column("action", width=180, anchor="w")
        self._tree.column("binding", width=260, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_row = tk.Frame(self)
        btn_row.pack(fill=tk.X, padx=10, pady=2)
        tk.Button(btn_row, text="Set Hotkey", command=self._on_set).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_row, text="Clear", command=self._on_clear).pack(side=tk.LEFT, padx=2)

        add_frame = tk.Frame(self)
        add_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(add_frame, text="Add room shortcut:").pack(side=tk.LEFT)
        self._room_var = tk.StringVar()
        rooms = [str(r) for r in sorted(get_all_room_numbers())]
        self._room_combo = ttk.Combobox(
            add_frame, textvariable=self._room_var,
            values=rooms, width=6, state="readonly"
        )
        self._room_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(add_frame, text="Add", command=self._on_add_room).pack(side=tk.LEFT, padx=2)

        bottom = tk.Frame(self)
        bottom.pack(fill=tk.X, padx=10, pady=(5, 10))
        tk.Button(bottom, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=2)
        tk.Button(bottom, text="Save", command=self._on_save_click).pack(side=tk.RIGHT, padx=2)

    def _refresh_list(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        for action in ("speed_up", "speed_down"):
            seq = self._edited.get(action, "")
            display = binding_display(seq) if seq else "(unbound)"
            self._tree.insert("", tk.END, iid=action,
                              values=(action_display_name(action), display))
        room_actions = sorted(
            [(a, s) for a, s in self._edited.items() if a.startswith("room_")],
            key=lambda x: int(x[0].split("_")[1])
        )
        for action, seq in room_actions:
            display = binding_display(seq) if seq else "(unbound)"
            self._tree.insert("", tk.END, iid=action,
                              values=(action_display_name(action), display))

    def _selected_action(self) -> Optional[str]:
        sel = self._tree.selection()
        return sel[0] if sel else None

    def _on_set(self) -> None:
        action = self._selected_action()
        if not action:
            return
        self._capture_key(action)

    def _on_clear(self) -> None:
        action = self._selected_action()
        if not action:
            return
        self._edited.pop(action, None)
        self._refresh_list()

    def _on_add_room(self) -> None:
        room_str = self._room_var.get()
        if not room_str:
            return
        action = f"room_{room_str}"
        if action not in self._edited:
            self._edited[action] = ""
        self._refresh_list()
        self._tree.selection_set(action)
        self._tree.see(action)

    def _capture_key(self, action: str) -> None:
        win = tk.Toplevel(self)
        win.title("Capture Hotkey")
        win.geometry("300x80")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        tk.Label(win, text="Press a key combination...",
                 font=("Segoe UI", 11)).pack(expand=True)

        def on_key(event: tk.Event) -> None:
            binding = _event_to_binding(event)
            if binding:
                self._edited[action] = binding
                self._refresh_list()
                win.destroy()

        def on_escape(event: tk.Event) -> None:
            win.destroy()

        win.bind("<KeyPress>", on_key)
        win.bind("<Escape>", on_escape)
        win.focus_force()

    def _on_save_click(self) -> None:
        clean = {a: s for a, s in self._edited.items() if s}
        self._config.update_all(clean)
        self._config.save()
        self._on_save()
        self.destroy()
