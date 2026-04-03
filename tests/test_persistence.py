import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tempfile
import os
from datetime import datetime, timezone, timedelta

from src.models.state import RoomState, EventType
from src.models.timer import compute_elapsed_seconds
from src.persistence.database import Database
from src.persistence.room_repo import RoomRepository
from src.persistence.event_repo import EventRepository


def _make_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(Path(path))
    return db, path


def test_database_creation():
    db, path = _make_db()
    try:
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {t["name"] for t in tables}
        assert "rooms" in names
        assert "sessions" in names
        assert "events" in names
    finally:
        db.close()
        os.unlink(path)


def test_ensure_rooms_exist():
    db, path = _make_db()
    try:
        repo = RoomRepository(db)
        repo.ensure_rooms_exist([1, 2, 3])
        rooms = repo.get_all_rooms()
        assert len(rooms) == 3
        for room in rooms:
            assert room.state == RoomState.AVAILABLE
    finally:
        db.close()
        os.unlink(path)


def test_update_room_state():
    db, path = _make_db()
    try:
        repo = RoomRepository(db)
        repo.ensure_rooms_exist([10])
        repo.update_room_state(10, RoomState.ACTIVE, "session-1")
        room = repo.get_room(10)
        assert room is not None
        assert room.state == RoomState.ACTIVE
        assert room.current_session_id == "session-1"
    finally:
        db.close()
        os.unlink(path)


def test_session_and_events():
    db, path = _make_db()
    try:
        repo = RoomRepository(db)
        event_repo = EventRepository(db)
        repo.ensure_rooms_exist([5])

        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        session = event_repo.create_session(5, t0)
        assert session.id is not None
        assert session.room_number == 5

        t1 = t0 + timedelta(minutes=10)
        event_repo.add_event(session.id, EventType.PAUSE, t1)

        events = event_repo.get_session_events(session.id)
        assert len(events) == 2
        assert events[0].event_type == EventType.START
        assert events[1].event_type == EventType.PAUSE
    finally:
        db.close()
        os.unlink(path)


def test_finalize_session():
    db, path = _make_db()
    try:
        event_repo = EventRepository(db)
        repo = RoomRepository(db)
        repo.ensure_rooms_exist([7])

        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        session = event_repo.create_session(7, t0)
        t1 = t0 + timedelta(hours=1)
        event_repo.add_event(session.id, EventType.STOP, t1)
        event_repo.finalize_session(session.id, t1, 3600.0)

        loaded = event_repo.get_session(session.id)
        assert loaded is not None
        assert loaded.total_elapsed_seconds == 3600.0
        assert loaded.end_time == t1
    finally:
        db.close()
        os.unlink(path)


def test_recovery_after_restart():
    """Simulate app restart: close DB, reopen, verify state recovery."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        db1 = Database(Path(path))
        repo1 = RoomRepository(db1)
        event_repo1 = EventRepository(db1)
        repo1.ensure_rooms_exist([20])

        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        session = event_repo1.create_session(20, t0)
        repo1.update_room_state(20, RoomState.ACTIVE, session.id)

        t1 = t0 + timedelta(minutes=15)
        event_repo1.add_event(session.id, EventType.PAUSE, t1)
        repo1.update_room_state(20, RoomState.PAUSED, session.id)

        t2 = t0 + timedelta(minutes=25)
        event_repo1.add_event(session.id, EventType.RESUME, t2)
        repo1.update_room_state(20, RoomState.ACTIVE, session.id)

        db1.close()

        db2 = Database(Path(path))
        repo2 = RoomRepository(db2)
        event_repo2 = EventRepository(db2)

        room = repo2.get_room(20)
        assert room is not None
        assert room.state == RoomState.ACTIVE
        assert room.current_session_id == session.id

        events = event_repo2.get_session_events(session.id)
        assert len(events) == 3

        now = t0 + timedelta(minutes=35)
        elapsed = compute_elapsed_seconds(events, room.state, now=now)
        assert elapsed == 25 * 60  # 15 min active + 10 min active after resume

        db2.close()
    finally:
        os.unlink(path)


def test_completed_sessions_query():
    db, path = _make_db()
    try:
        event_repo = EventRepository(db)
        repo = RoomRepository(db)
        repo.ensure_rooms_exist([1, 2])

        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        s1 = event_repo.create_session(1, t0)
        event_repo.add_event(s1.id, EventType.STOP, t0 + timedelta(hours=1))
        event_repo.finalize_session(s1.id, t0 + timedelta(hours=1), 3600.0)

        s2 = event_repo.create_session(2, t0 + timedelta(hours=2))
        event_repo.add_event(s2.id, EventType.STOP, t0 + timedelta(hours=3))
        event_repo.finalize_session(s2.id, t0 + timedelta(hours=3), 3600.0)

        completed = event_repo.get_completed_sessions()
        assert len(completed) == 2
        assert completed[0].room_number == 2  # most recent first
    finally:
        db.close()
        os.unlink(path)
