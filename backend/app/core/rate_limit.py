"""In-process sliding-window rate limiter for brute-force-sensitive endpoints
(login, register). State is a per-worker in-memory dict keyed by client IP —
it resets on restart and isn't shared across multiple worker processes. That
is an accepted trade-off at this scale, consistent with the project's other
single-process designs (no job queue, no token blacklist — see backend/README's
Phase 11 section for what a Redis-backed limiter would add).
"""
import time
from collections import defaultdict
from threading import Lock

from fastapi import Request

from app.core.exceptions import AppError


class TooManyRequestsError(AppError):
    def __init__(self, message: str = "Too many attempts. Please wait a moment and try again."):
        super().__init__(message, status_code=429, code="too_many_requests")


class _SlidingWindowLimiter:
    def __init__(self, *, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = [t for t in self._hits[key] if t > cutoff]
            if len(hits) >= self.max_requests:
                self._hits[key] = hits
                raise TooManyRequestsError()
            hits.append(now)
            self._hits[key] = hits

    def reset(self) -> None:
        """Test-only: clear all tracked state between test cases."""
        self._hits.clear()


_limiters: dict[str, _SlidingWindowLimiter] = {}


def rate_limit(name: str, *, max_requests: int, window_seconds: float):
    """FastAPI dependency factory. Each distinct `name` gets its own counters,
    keyed further by client IP, e.g. `Depends(rate_limit("login", max_requests=10, window_seconds=60))`.
    """
    limiter = _limiters.setdefault(name, _SlidingWindowLimiter(max_requests=max_requests, window_seconds=window_seconds))

    def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        limiter.check(client_ip)

    return _dependency


def reset_all() -> None:
    """Test-only: clear every limiter's state (autouse fixture in conftest.py)."""
    for limiter in _limiters.values():
        limiter.reset()
