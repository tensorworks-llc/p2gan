"""
Simple in-memory cache for weather data
"""

from typing import Optional, Any
from datetime import datetime, timedelta
from threading import Lock


class WeatherCache:
    """
    Thread-safe in-memory cache with TTL support
    """

    def __init__(self, ttl: int = 300):
        """
        Initialize cache

        Args:
            ttl: Time-to-live in seconds (default 5 minutes)
        """
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        with self._lock:
            if key not in self._cache:
                return None

            # Check expiration
            if self._is_expired(key):
                self._remove(key)
                return None

            return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Store value in cache

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now()

    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._timestamps:
            return True

        age = (datetime.now() - self._timestamps[key]).total_seconds()
        return age > self.ttl

    def _remove(self, key: str) -> None:
        """Remove entry from cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    # TODO: Add cache size limits
    # TODO: Add LRU eviction policy
    # TODO: Add cache statistics (hit rate, etc.)
