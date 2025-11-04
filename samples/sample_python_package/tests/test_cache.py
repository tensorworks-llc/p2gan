"""
Tests for caching functionality
"""

import pytest
import time
from weatherapi.cache import WeatherCache


class TestWeatherCache:
    """Test suite for WeatherCache"""

    def test_cache_stores_value(self):
        """Test that cache stores and retrieves values"""
        cache = WeatherCache(ttl=60)
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_cache_returns_none_for_missing_key(self):
        """Test that cache returns None for missing keys"""
        cache = WeatherCache(ttl=60)
        assert cache.get("nonexistent") is None

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL"""
        cache = WeatherCache(ttl=1)  # 1 second TTL
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        time.sleep(1.1)  # Wait for expiration
        assert cache.get("test_key") is None

    def test_cache_clear(self):
        """Test that clear removes all entries"""
        cache = WeatherCache(ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    # TODO: Add thread safety tests
    # TODO: Add performance tests for large datasets
