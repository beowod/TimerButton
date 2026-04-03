from typing import Optional
from src.models.state import RoomState
from src.models.timer import Room
from src.persistence.database import Database


class RoomRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def ensure_rooms_exist(self, room_numbers: list[int]) -> None:
        with self._db.transaction() as cursor:
            for rn in room_numbers:
                cursor.execute(
                    "INSERT OR IGNORE INTO rooms (room_number, state) VALUES (?, ?)",
                    (rn, RoomState.AVAILABLE.value)
                )

    def get_room(self, room_number: int) -> Optional[Room]:
        row = self._db.execute(
            "SELECT room_number, state, current_session_id FROM rooms WHERE room_number = ?",
            (room_number,)
        ).fetchone()
        if row is None:
            return None
        return Room(
            room_number=row["room_number"],
            state=RoomState(row["state"]),
            current_session_id=row["current_session_id"]
        )

    def get_all_rooms(self) -> list[Room]:
        rows = self._db.execute(
            "SELECT room_number, state, current_session_id FROM rooms ORDER BY room_number"
        ).fetchall()
        return [
            Room(
                room_number=r["room_number"],
                state=RoomState(r["state"]),
                current_session_id=r["current_session_id"]
            )
            for r in rows
        ]

    def update_room_state(self, room_number: int, state: RoomState,
                          session_id: Optional[str] = None) -> None:
        with self._db.transaction() as cursor:
            cursor.execute(
                "UPDATE rooms SET state = ?, current_session_id = ? WHERE room_number = ?",
                (state.value, session_id, room_number)
            )
