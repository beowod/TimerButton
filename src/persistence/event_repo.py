from datetime import datetime, timezone
from typing import Optional
import uuid

from src.models.state import EventType
from src.models.timer import TimerEvent, Session
from src.persistence.database import Database


class EventRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create_session(self, room_number: int, start_time: datetime) -> Session:
        session_id = str(uuid.uuid4())
        ts = start_time.isoformat()
        with self._db.transaction() as cursor:
            cursor.execute(
                "INSERT INTO sessions (id, room_number, start_time) VALUES (?, ?, ?)",
                (session_id, room_number, ts)
            )
            cursor.execute(
                "INSERT INTO events (session_id, event_type, timestamp) VALUES (?, ?, ?)",
                (session_id, EventType.START.value, ts)
            )
        return Session(id=session_id, room_number=room_number, start_time=start_time)

    def add_event(self, session_id: str, event_type: EventType,
                  timestamp: Optional[datetime] = None) -> TimerEvent:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        ts = timestamp.isoformat()
        with self._db.transaction() as cursor:
            cursor.execute(
                "INSERT INTO events (session_id, event_type, timestamp) VALUES (?, ?, ?)",
                (session_id, event_type.value, ts)
            )
            event_id = cursor.lastrowid
        return TimerEvent(
            id=event_id, event_type=event_type,
            timestamp=timestamp, session_id=session_id
        )

    def finalize_session(self, session_id: str, end_time: datetime,
                         elapsed_seconds: float) -> None:
        with self._db.transaction() as cursor:
            cursor.execute(
                "UPDATE sessions SET end_time = ?, total_elapsed_seconds = ? WHERE id = ?",
                (end_time.isoformat(), elapsed_seconds, session_id)
            )

    def get_session_events(self, session_id: str) -> list[TimerEvent]:
        rows = self._db.execute(
            "SELECT id, session_id, event_type, timestamp FROM events "
            "WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        return [
            TimerEvent(
                id=r["id"],
                session_id=r["session_id"],
                event_type=EventType(r["event_type"]),
                timestamp=datetime.fromisoformat(r["timestamp"])
            )
            for r in rows
        ]

    def get_session(self, session_id: str) -> Optional[Session]:
        row = self._db.execute(
            "SELECT id, room_number, start_time, end_time, total_elapsed_seconds "
            "FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        if row is None:
            return None
        events = self.get_session_events(session_id)
        return Session(
            id=row["id"],
            room_number=row["room_number"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            total_elapsed_seconds=row["total_elapsed_seconds"],
            events=events
        )

    def get_completed_sessions(self, limit: int = 100) -> list[Session]:
        rows = self._db.execute(
            "SELECT id, room_number, start_time, end_time, total_elapsed_seconds "
            "FROM sessions WHERE end_time IS NOT NULL "
            "ORDER BY end_time DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            Session(
                id=r["id"],
                room_number=r["room_number"],
                start_time=datetime.fromisoformat(r["start_time"]),
                end_time=datetime.fromisoformat(r["end_time"]) if r["end_time"] else None,
                total_elapsed_seconds=r["total_elapsed_seconds"],
            )
            for r in rows
        ]
