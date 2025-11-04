"""
Rate limiter for API requests
"""

from datetime import datetime, timedelta
from collections import deque
from threading import Lock


class RateLimiter:
    """
    Token bucket rate limiter for API calls
    """

    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests = deque()
        self._lock = Lock()

    def check(self) -> bool:
        """
        Check if request is allowed under rate limit

        Returns:
            True if allowed, raises exception if rate limited
        """
        with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window)

            # Remove old requests
            while self._requests and self._requests[0] < cutoff:
                self._requests.popleft()

            # Check limit
            if len(self._requests) >= self.max_requests:
                raise RateLimitError(
                    f"Rate limit exceeded: {self.max_requests} requests per {self.time_window}s"
                )

            # Record this request
            self._requests.append(now)
            return True

    def reset(self) -> None:
        """Reset the rate limiter"""
        with self._lock:
            self._requests.clear()


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass
