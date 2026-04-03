from enum import Enum


class RoomState(str, Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"


class EventType(str, Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"


VALID_TRANSITIONS: dict[RoomState, dict[str, RoomState]] = {
    RoomState.AVAILABLE: {"start": RoomState.ACTIVE},
    RoomState.ACTIVE:    {"pause": RoomState.PAUSED, "stop": RoomState.FINISHED},
    RoomState.PAUSED:    {"resume": RoomState.ACTIVE, "stop": RoomState.FINISHED},
    RoomState.FINISHED:  {"reset": RoomState.AVAILABLE},
}


def can_transition(current: RoomState, action: str) -> bool:
    return action in VALID_TRANSITIONS.get(current, {})


def next_state(current: RoomState, action: str) -> RoomState:
    transitions = VALID_TRANSITIONS.get(current, {})
    if action not in transitions:
        raise ValueError(f"Invalid transition: {current.value} -> {action}")
    return transitions[action]
