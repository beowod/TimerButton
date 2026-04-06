from src.config import SPEED_MIN, SPEED_MAX


class SpeedController:
    """Manages the global timer speed multiplier and per-session virtual time offsets."""

    def __init__(self) -> None:
        self._speed: int = SPEED_MIN
        self._offsets: dict[str, float] = {}

    @property
    def speed(self) -> int:
        return self._speed

    def speed_up(self) -> int:
        if self._speed < SPEED_MAX:
            self._speed += 1
        return self._speed

    def speed_down(self) -> int:
        if self._speed > SPEED_MIN:
            self._speed -= 1
        return self._speed

    def tick(self, active_session_ids: list[str]) -> None:
        """Accumulate virtual time offset for each active session."""
        extra = self._speed - 1
        if extra <= 0:
            return
        for sid in active_session_ids:
            if sid not in self._offsets:
                self._offsets[sid] = 0.0
            self._offsets[sid] += extra

    def get_offset(self, session_id: str) -> float:
        return self._offsets.get(session_id, 0.0)

    def clear_offset(self, session_id: str) -> None:
        self._offsets.pop(session_id, None)

    def reset(self) -> None:
        self._speed = SPEED_MIN
        self._offsets.clear()
