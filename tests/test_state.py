import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.state import RoomState, can_transition, next_state
import pytest


def test_available_can_start():
    assert can_transition(RoomState.AVAILABLE, "start") is True


def test_available_cannot_pause():
    assert can_transition(RoomState.AVAILABLE, "pause") is False


def test_active_can_pause():
    assert can_transition(RoomState.ACTIVE, "pause") is True


def test_active_can_stop():
    assert can_transition(RoomState.ACTIVE, "stop") is True


def test_active_cannot_start():
    assert can_transition(RoomState.ACTIVE, "start") is False


def test_paused_can_resume():
    assert can_transition(RoomState.PAUSED, "resume") is True


def test_paused_can_stop():
    assert can_transition(RoomState.PAUSED, "stop") is True


def test_finished_can_reset():
    assert can_transition(RoomState.FINISHED, "reset") is True


def test_finished_cannot_start():
    assert can_transition(RoomState.FINISHED, "start") is False


def test_next_state_transitions():
    assert next_state(RoomState.AVAILABLE, "start") == RoomState.ACTIVE
    assert next_state(RoomState.ACTIVE, "pause") == RoomState.PAUSED
    assert next_state(RoomState.ACTIVE, "stop") == RoomState.FINISHED
    assert next_state(RoomState.PAUSED, "resume") == RoomState.ACTIVE
    assert next_state(RoomState.PAUSED, "stop") == RoomState.FINISHED
    assert next_state(RoomState.FINISHED, "reset") == RoomState.AVAILABLE


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        next_state(RoomState.AVAILABLE, "stop")


def test_full_lifecycle():
    state = RoomState.AVAILABLE
    state = next_state(state, "start")
    assert state == RoomState.ACTIVE
    state = next_state(state, "pause")
    assert state == RoomState.PAUSED
    state = next_state(state, "resume")
    assert state == RoomState.ACTIVE
    state = next_state(state, "stop")
    assert state == RoomState.FINISHED
    state = next_state(state, "reset")
    assert state == RoomState.AVAILABLE
