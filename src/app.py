import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone
from typing import Optional

from src.config import (
    APP_NAME, DB_PATH, UI_UPDATE_INTERVAL_MS, get_all_room_numbers
)
from src.models.state import RoomState, EventType, can_transition, next_state
from src.models.timer import Room, compute_elapsed_seconds, format_elapsed
from src.persistence.database import Database
from src.persistence.room_repo import RoomRepository
from src.persistence.event_repo import EventRepository
from src.ui.room_map import RoomMap
from src.ui.status_bar import StatusBar
from src.ui.history_dialog import HistoryDialog


class Application:
    def __init__(self) -> None:
        self._db = Database(DB_PATH)
        self._room_repo = RoomRepository(self._db)
        self._event_repo = EventRepository(self._db)

        self._room_repo.ensure_rooms_exist(get_all_room_numbers())

        self._rooms: dict[int, Room] = {}
        self._load_rooms()

        self._root = tk.Tk()
        self._root.title(APP_NAME)
        self._root.resizable(True, True)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._refresh_all_buttons()
        self._schedule_tick()

    def _load_rooms(self) -> None:
        for room in self._room_repo.get_all_rooms():
            self._rooms[room.room_number] = room

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self._root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)

        title = tk.Label(toolbar, text=APP_NAME, font=("Segoe UI", 14, "bold"))
        title.pack(side=tk.LEFT)

        history_btn = tk.Button(toolbar, text="History", command=self._show_history)
        history_btn.pack(side=tk.RIGHT)

        self._room_map = RoomMap(
            self._root,
            on_left_click=self._on_room_left_click,
            on_right_click=self._on_room_right_click
        )
        self._room_map.pack(fill=tk.BOTH, expand=True)

        self._status_bar = StatusBar(self._root)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)

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
        self._refresh_button(room.room_number)

        self._root.after(3000, lambda rn=room.room_number: self._auto_reset(rn))

    def _reset_room(self, room: Room) -> None:
        if not can_transition(room.state, "reset"):
            return
        new_state = next_state(room.state, "reset")
        self._room_repo.update_room_state(room.room_number, new_state, None)
        room.state = new_state
        room.current_session_id = None
        self._refresh_button(room.room_number)

    def _auto_reset(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        if room and room.state == RoomState.FINISHED:
            self._reset_room(room)

    def _refresh_button(self, room_number: int) -> None:
        room = self._rooms.get(room_number)
        btn = self._room_map.get_button(room_number)
        if room is None or btn is None:
            return

        elapsed_text: Optional[str] = None
        if room.state in (RoomState.ACTIVE, RoomState.PAUSED, RoomState.FINISHED):
            if room.current_session_id:
                events = self._event_repo.get_session_events(room.current_session_id)
                elapsed = compute_elapsed_seconds(events, room.state)
                elapsed_text = format_elapsed(elapsed)

        btn.update_display(room.state, elapsed_text)
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

    def _schedule_tick(self) -> None:
        self._tick()
        self._root.after(UI_UPDATE_INTERVAL_MS, self._schedule_tick)

    def _tick(self) -> None:
        for room in self._rooms.values():
            if room.state == RoomState.ACTIVE:
                self._refresh_button(room.room_number)

    def _show_history(self) -> None:
        sessions = self._event_repo.get_completed_sessions(limit=200)
        HistoryDialog(self._root, sessions)

    def _on_close(self) -> None:
        self._db.close()
        self._root.destroy()

    def run(self) -> None:
        self._root.mainloop()
