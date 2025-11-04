"""
Tests for WeatherClient
"""

import pytest
from datetime import datetime
from weatherapi import WeatherClient
from weatherapi.models import WeatherData, Temperature, Location


class TestWeatherClient:
    """Test suite for WeatherClient"""

    def test_client_initialization(self):
        """Test client can be initialized"""
        client = WeatherClient(api_key="test_key")
        assert client is not None
        assert client.provider is not None

    def test_cache_enabled_by_default(self):
        """Test that caching is enabled by default"""
        client = WeatherClient(api_key="test_key")
        assert client.cache is not None

    def test_cache_can_be_disabled(self):
        """Test that caching can be disabled"""
        client = WeatherClient(api_key="test_key", enable_cache=False)
        assert client.cache is None

    # TODO: Add test for get_current_weather
    # TODO: Add test for get_forecast
    # TODO: Add test for get_historical
    # TODO: Add test for rate limiting
    # TODO: Add test for cache hits
    # TODO: Add integration tests with real API
