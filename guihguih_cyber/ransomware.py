"""Local heuristic for bursts of file modifications; alert-only, never blocks."""

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from time import monotonic


class ChangeBurstDetector:
    """Detect many changed-file events in a short window in watched folders.

    Polling cannot see every operation and this heuristic is not an antivirus
    verdict. It is intended to notify the user about unusually fast changes.
    """

    def __init__(self, threshold: int = 20, window_seconds: float = 10.0):
        if threshold < 2:
            raise ValueError("O limite precisa ser de pelo menos 2 alterações")
        if window_seconds <= 0:
            raise ValueError("A janela precisa ser maior que zero")
        self.threshold = threshold
        self.window_seconds = window_seconds
        self._events: deque[tuple[float, str]] = deque()
        self._armed = True
        self._lock = Lock()

    def record_change(self, path: str, now: float | None = None) -> dict | None:
        now = monotonic() if now is None else now
        with self._lock:
            self._events.append((now, str(path)))
            cutoff = now - self.window_seconds
            while self._events and self._events[0][0] < cutoff:
                self._events.popleft()

            distinct_files = {event_path for _, event_path in self._events}
            if len(distinct_files) < self.threshold:
                self._armed = True
                return None
            if not self._armed:
                return None

            self._armed = False
            return {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "event_count": len(distinct_files),
                "window_seconds": self.window_seconds,
            }

    def reset(self) -> None:
        with self._lock:
            self._events.clear()
            self._armed = True
