import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone
from typing import Callable, Optional

from src.config import (
    APP_NAME, APP_VERSION, DB_PATH, UI_UPDATE_INTERVAL_MS, TIMER_LIMIT_SECONDS,
    BLINK_INTERVAL_MS, SPEED_LABEL_FONT, get_all_room_numbers
)
from src.models.state import RoomState, EventType, can_transition, next_state
from src.models.timer import Room, compute_elapsed_seconds, format_elapsed
from src.persistence.database import Database
from src.persistence.room_repo import RoomRepository
from src.persistence.event_repo import EventRepository
from src.speed import SpeedController
from src.hotkeys import HotkeyConfig, CHORD_DIGIT_SEQS, CHORD_TIMEOUT_MS
from src.ui.room_map import RoomMap
from src.ui.status_bar import StatusBar
from src.ui.history_dialog import HistoryDialog
from src.ui.hotkey_editor import HotkeyEditorDialog
from src.ui.update_dialog import UpdateDialog


class Application:
    def __init__(self) -> None:
        self._db = Database(DB_PATH)
        self._room_repo = RoomRepository(self._db)
        self._event_repo = EventRepository(self._db)
        self._speed = SpeedController()
        self._hotkey_config = HotkeyConfig()

        self._room_repo.ensure_rooms_exist(get_all_room_numbers())

        self._rooms: dict[int, Room] = {}
        self._load_rooms()

        self._root = tk.Tk()
        self._root.title(f"{APP_NAME} v{APP_VERSION}")
        self._root.resizable(True, True)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._bound_keys: list[str] = []
        self._chord_digits: str = ""
        self._chord_timer_id: Optional[str] = None

        self._build_ui()
        self._bind_hotkeys()
        self._refresh_all_buttons()
        self._schedule_tick()
        self._schedule_blink()

    def _load_rooms(self) -> None:
        for room in self._room_repo.get_all_rooms():
            self._rooms[room.room_number] = room

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self._root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)

        title = tk.Label(toolbar, text=APP_NAME, font=("Segoe UI", 14, "bold"))
        title.pack(side=tk.LEFT)

        update_btn = tk.Button(toolbar, text="Check for Updates",
                               command=self._show_update_dialog)
        update_btn.pack(side=tk.RIGHT, padx=(5, 0))

        hotkeys_btn = tk.Button(toolbar, text="Hotkeys", command=self._show_hotkey_editor)
        hotkeys_btn.pack(side=tk.RIGHT, padx=(5, 0))

        history_btn = tk.Button(toolbar, text="History", command=self._show_history)
        history_btn.pack(side=tk.RIGHT)

        speed_frame = tk.Frame(toolbar)
        speed_frame.pack(side=tk.RIGHT, padx=20)
        tk.Button(speed_frame, text="\u2212", width=2,
                  command=self._speed_down).pack(side=tk.LEFT)
        self._speed_label = tk.Label(
            speed_frame, text="Speed: 1x", font=SPEED_LABEL_FONT, width=10
        )
        self._speed_label.pack(side=tk.LEFT, padx=5)
        tk.Button(speed_frame, text="+", width=2,
                  command=self._speed_up).pack(side=tk.LEFT)

        self._room_map = RoomMap(
            self._root,
            on_left_click=self._on_room_left_click,
            on_right_click=self._on_room_right_click
        )
        self._room_map.pack(fill=tk.BOTH, expand=True)

        self._status_bar = StatusBar(self._root)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # -- Speed control ---------------------------------------------------------

    def _speed_up(self) -> None:
        self._speed.speed_up()
        self._update_speed_label()

    def _speed_down(self) -> None:
        self._speed.speed_down()
        self._update_speed_label()

    def _update_speed_label(self) -> None:
        self._speed_label.config(text=f"Speed: {self._speed.speed}x")

    # -- Hotkey management -----------------------------------------------------

    def _bind_hotkeys(self) -> None:
        self._unbind_hotkeys()
        # Chord-based digit bindings for room selection
        for digit, seqs in CHORD_DIGIT_SEQS.items():
            handler = self._make_digit_handler(digit)
            for seq in seqs:
                self._try_bind(seq, handler)
        # Config-based bindings (speed controls + optional room overrides)
        for action, seq in self._hotkey_config.bindings.items():
            if action == "speed_up":
                self._try_bind(seq, self._make_handler(self._speed_up))
            elif action == "speed_down":
                self._try_bind(seq, self._make_handler(self._speed_down))
            elif action.startswith("room_"):
                try:
                    room_num = int(action.split("_", 1)[1])
                except ValueError:
                    continue
                self._try_bind(seq, self._make_room_handler(room_num))

    def _try_bind(self, seq: str, handler: Callable[[tk.Event], str]) -> None:
        try:
            self._root.bind(seq, handler)
            self._bound_keys.append(seq)
        except tk.TclError:
            pass

    @staticmethod
    def _make_handler(fn: Callable[[], None]) -> Callable[[tk.Event], str]:
        def handler(event: tk.Event) -> str:
            fn()
            return "break"
        return handler

    def _make_room_handler(self, room_num: int) -> Callable[[tk.Event], str]:
        def handler(event: tk.Event) -> str:
            self._on_room_left_click(room_num)
            return "break"
        return handler

    def _make_digit_handler(self, digit: str) -> Callable[[tk.Event], str]:
        def handler(event: tk.Event) -> str:
            self._on_digit_hotkey(digit)
            return "break"
        return handler

    def _on_digit_hotkey(self, digit: str) -> None:
        if self._chord_timer_id is not None:
            self._root.after_cancel(self._chord_timer_id)
            self._chord_timer_id = None

        self._chord_digits += digit
        room_num = int(self._chord_digits)

        has_longer = any(
            str(rn).startswith(self._chord_digits)
            and len(str(rn)) > len(self._chord_digits)
            for rn in self._rooms
        )

        if room_num in self._rooms and not has_longer:
            self._on_room_left_click(room_num)
            self._chord_digits = ""
        elif has_longer:
            self._chord_timer_id = self._root.after(
                CHORD_TIMEOUT_MS, self._resolve_chord
            )
        else:
            self._chord_digits = ""

    def _resolve_chord(self) -> None:
        self._chord_timer_id = None
        if self._chord_digits:
            try:
                room_num = int(self._chord_digits)
                if room_num in self._rooms:
                    self._on_room_left_click(room_num)
            except ValueError:
                pass
        self._chord_digits = ""

    def _unbind_hotkeys(self) -> None:
        for seq in self._bound_keys:
            try:
                self._root.unbind(seq)
            except tk.TclError:
                pass
        self._bound_keys.clear()

    def _show_hotkey_editor(self) -> None:
        HotkeyEditorDialog(self._root, self._hotkey_config, self._on_hotkeys_changed)

    def _on_hotkeys_changed(self) -> None:
        self._bind_hotkeys()

    # -- Room actions ----------------------------------------------------------

    def _on_room_left_click(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        if room is None:
            return

        if room.state == RoomState.AVAILABLE:
            self._start_timer(room)
        elif room.state == RoomState.ACTIVE:
            self._stop_timer(room)
        elif room.state == RoomState.PAUSED:
            self._resume_timer(room)
        elif room.state == RoomState.FINISHED:
            self._reset_room(room)

    def _on_room_right_click(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        if room is None:
            return

        if room.state == RoomState.ACTIVE:
            self._pause_timer(room)
        elif room.state == RoomState.PAUSED:
            self._resume_timer(room)

    def _start_timer(self, room: Room) -> None:
        if not can_transition(room.state, "start"):
            return
        now = datetime.now(timezone.utc)
        session = self._event_repo.create_session(room.room_number, now)
        new_state = next_state(room.state, "start")
        self._room_repo.update_room_state(room.room_number, new_state, session.id)
        room.state = new_state
        room.current_session_id = session.id
        self._refresh_button(room.room_number)

    def _pause_timer(self, room: Room) -> None:
        if not can_transition(room.state, "pause") or room.current_session_id is None:
            return
        now = datetime.now(timezone.utc)
        self._event_repo.add_event(room.current_session_id, EventType.PAUSE, now)
        new_state = next_state(room.state, "pause")
        self._room_repo.update_room_state(room.room_number, new_state, room.current_session_id)
        room.state = new_state
        self._refresh_button(room.room_number)

    def _resume_timer(self, room: Room) -> None:
        if not can_transition(room.state, "resume") or room.current_session_id is None:
            return
        now = datetime.now(timezone.utc)
        self._event_repo.add_event(room.current_session_id, EventType.RESUME, now)
        new_state = next_state(room.state, "resume")
        self._room_repo.update_room_state(room.room_number, new_state, room.current_session_id)
        room.state = new_state
        self._refresh_button(room.room_number)

    def _stop_timer(self, room: Room) -> None:
        if not can_transition(room.state, "stop") or room.current_session_id is None:
            return

        events = self._event_repo.get_session_events(room.current_session_id)
        now = datetime.now(timezone.utc)
        elapsed = compute_elapsed_seconds(events, room.state, now)
        elapsed += self._speed.get_offset(room.current_session_id)
        elapsed_str = format_elapsed(elapsed)

        confirm = messagebox.askyesno(
            "Stop Timer",
            f"Stop timer for Room {room.room_number}?\n"
            f"Elapsed time: {elapsed_str}",
            parent=self._root
        )
        if not confirm:
            return

        self._event_repo.add_event(room.current_session_id, EventType.STOP, now)
        self._event_repo.finalize_session(room.current_session_id, now, elapsed)
        new_state = next_state(room.state, "stop")
        self._room_repo.update_room_state(room.room_number, new_state, room.current_session_id)
        room.state = new_state
        self._speed.clear_offset(room.current_session_id)
        self._refresh_button(room.room_number)

        self._root.after(3000, lambda rn=room.room_number: self._auto_reset(rn))

    def _reset_room(self, room: Room) -> None:
        if not can_transition(room.state, "reset"):
            return
        if room.current_session_id:
            self._speed.clear_offset(room.current_session_id)
        new_state = next_state(room.state, "reset")
        self._room_repo.update_room_state(room.room_number, new_state, None)
        room.state = new_state
        room.current_session_id = None
        self._refresh_button(room.room_number)

    def _auto_reset(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        if room and room.state == RoomState.FINISHED:
            self._reset_room(room)

    # -- Display refresh -------------------------------------------------------

    def _refresh_button(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        btn = self._room_map.get_button(room_number)
        if room is None or btn is None:
            return

        elapsed_text: Optional[str] = None
        overdue = False
        if room.state in (RoomState.ACTIVE, RoomState.PAUSED, RoomState.FINISHED):
            if room.current_session_id:
                events = self._event_repo.get_session_events(room.current_session_id)
                elapsed = compute_elapsed_seconds(events, room.state)
                elapsed += self._speed.get_offset(room.current_session_id)
                elapsed_text = format_elapsed(elapsed)
                if elapsed >= TIMER_LIMIT_SECONDS and room.state in (
                    RoomState.ACTIVE, RoomState.PAUSED
                ):
                    overdue = True

        btn.update_display(room.state, elapsed_text, overdue=overdue)
        self._update_status_bar()

    def _refresh_all_buttons(self) -> None:
        for room_number in self._rooms:
            self._refresh_button(room_number)

    def _update_status_bar(self) -> None:
        total = len(self._rooms)
        active = sum(1 for r in self._rooms.values() if r.state == RoomState.ACTIVE)
        paused = sum(1 for r in self._rooms.values() if r.state == RoomState.PAUSED)
        available = sum(1 for r in self._rooms.values() if r.state == RoomState.AVAILABLE)
        self._status_bar.update_counts(total, active, paused, available)

    # -- Tick and blink --------------------------------------------------------

    def _schedule_tick(self) -> None:
        self._tick()
        self._root.after(UI_UPDATE_INTERVAL_MS, self._schedule_tick)

    def _tick(self) -> None:
        active_sessions: list[str] = []
        for room in self._rooms.values():
            if room.state == RoomState.ACTIVE and room.current_session_id:
                active_sessions.append(room.current_session_id)
        self._speed.tick(active_sessions)
        for room in self._rooms.values():
            if room.state == RoomState.ACTIVE:
                self._refresh_button(room.room_number)

    def _schedule_blink(self) -> None:
        for btn in self._room_map.buttons.values():
            if btn.overdue:
                btn.toggle_blink()
        self._root.after(BLINK_INTERVAL_MS, self._schedule_blink)

    # -- Dialogs ---------------------------------------------------------------

    def _show_history(self) -> None:
        sessions = self._event_repo.get_completed_sessions(limit=200)
        HistoryDialog(self._root, sessions)

    def _show_update_dialog(self) -> None:
        UpdateDialog(self._root)

    # -- Cleanup ---------------------------------------------------------------

    def _on_close(self) -> None:
        self._db.close()
        self._root.destroy()

    def run(self) -> None:
        self._root.mainloop()
