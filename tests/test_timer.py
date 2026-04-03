import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone, timedelta
from src.models.state import RoomState, EventType
from src.models.timer import TimerEvent, compute_elapsed_seconds, format_elapsed


def _make_event(event_type: EventType, ts: datetime) -> TimerEvent:
    return TimerEvent(event_type=event_type, timestamp=ts, session_id="test-session")


def test_empty_events():
    assert compute_elapsed_seconds([], RoomState.AVAILABLE) == 0.0


def test_active_timer_elapsed():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    now = t0 + timedelta(minutes=30)
    events = [_make_event(EventType.START, t0)]
    elapsed = compute_elapsed_seconds(events, RoomState.ACTIVE, now=now)
    assert elapsed == 1800.0


def test_paused_timer_elapsed():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)
    now = t0 + timedelta(minutes=30)
    events = [
        _make_event(EventType.START, t0),
        _make_event(EventType.PAUSE, t1),
    ]
    elapsed = compute_elapsed_seconds(events, RoomState.PAUSED, now=now)
    assert elapsed == 600.0


def test_resumed_timer_elapsed():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)
    t2 = t0 + timedelta(minutes=20)
    now = t0 + timedelta(minutes=30)
    events = [
        _make_event(EventType.START, t0),
        _make_event(EventType.PAUSE, t1),
        _make_event(EventType.RESUME, t2),
    ]
    elapsed = compute_elapsed_seconds(events, RoomState.ACTIVE, now=now)
    assert elapsed == 1200.0  # 10min + 10min


def test_stopped_timer_elapsed():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=2)
    events = [
        _make_event(EventType.START, t0),
        _make_event(EventType.STOP, t1),
    ]
    elapsed = compute_elapsed_seconds(events, RoomState.FINISHED)
    assert elapsed == 7200.0


def test_pause_resume_stop_elapsed():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)
    t2 = t0 + timedelta(minutes=20)
    t3 = t0 + timedelta(minutes=40)
    events = [
        _make_event(EventType.START, t0),
        _make_event(EventType.PAUSE, t1),
        _make_event(EventType.RESUME, t2),
        _make_event(EventType.STOP, t3),
    ]
    elapsed = compute_elapsed_seconds(events, RoomState.FINISHED)
    assert elapsed == 1800.0  # 10min + 20min


def test_format_elapsed():
    assert format_elapsed(0) == "00:00:00"
    assert format_elapsed(61) == "00:01:01"
    assert format_elapsed(3661) == "01:01:01"
    assert format_elapsed(86400) == "24:00:00"


def test_multiple_pause_resume_cycles():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        _make_event(EventType.START, t0),
        _make_event(EventType.PAUSE, t0 + timedelta(minutes=5)),
        _make_event(EventType.RESUME, t0 + timedelta(minutes=10)),
        _make_event(EventType.PAUSE, t0 + timedelta(minutes=15)),
        _make_event(EventType.RESUME, t0 + timedelta(minutes=20)),
        _make_event(EventType.STOP, t0 + timedelta(minutes=25)),
    ]
    elapsed = compute_elapsed_seconds(events, RoomState.FINISHED)
    assert elapsed == 900.0  # 5 + 5 + 5 = 15 min
