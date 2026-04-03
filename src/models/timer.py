from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

from src.models.state import RoomState, EventType


@dataclass
class TimerEvent:
    event_type: EventType
    timestamp: datetime
    session_id: str
    id: Optional[int] = None


@dataclass
class Session:
    id: str
    room_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_elapsed_seconds: Optional[float] = None
    events: list[TimerEvent] = field(default_factory=list)


@dataclass
class Room:
    room_number: int
    state: RoomState = RoomState.AVAILABLE
    current_session_id: Optional[str] = None


def compute_elapsed_seconds(events: list[TimerEvent],
                            state: RoomState,
                            now: Optional[datetime] = None) -> float:
    if not events:
        return 0.0

    if now is None:
        now = datetime.now(timezone.utc)

    sorted_events = sorted(events, key=lambda e: e.timestamp)
    elapsed = 0.0
    last_active_start: Optional[datetime] = None

    for event in sorted_events:
        if event.event_type == EventType.START:
            last_active_start = event.timestamp
        elif event.event_type == EventType.RESUME:
            last_active_start = event.timestamp
        elif event.event_type == EventType.PAUSE:
            if last_active_start is not None:
                elapsed += (event.timestamp - last_active_start).total_seconds()
                last_active_start = None
        elif event.event_type == EventType.STOP:
            if last_active_start is not None:
                elapsed += (event.timestamp - last_active_start).total_seconds()
                last_active_start = None

    if state == RoomState.ACTIVE and last_active_start is not None:
        elapsed += (now - last_active_start).total_seconds()

    return max(0.0, elapsed)


def format_elapsed(seconds: float) -> str:
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
