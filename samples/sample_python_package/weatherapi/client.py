"""
Main WeatherClient implementation
"""

from typing import Optional, List
from datetime import datetime, timedelta
from .models import WeatherData, ForecastData, HistoricalData
from .providers import BaseProvider, OpenWeatherProvider
from .cache import WeatherCache
from .rate_limiter import RateLimiter


class WeatherClient:
    """
    Main client for weather data access

    Supports multiple providers and includes caching and rate limiting.
    """

    def __init__(
        self,
        api_key: str,
        provider: Optional[BaseProvider] = None,
        enable_cache: bool = True,
        cache_ttl: int = 300,  # 5 minutes default
    ):
        """
        Initialize the weather client

        Args:
            api_key: API key for the weather provider
            provider: Weather provider instance (defaults to OpenWeather)
            enable_cache: Whether to enable response caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.provider = provider or OpenWeatherProvider(api_key)
        self.cache = WeatherCache(ttl=cache_ttl) if enable_cache else None
        self.rate_limiter = RateLimiter(max_requests=60, time_window=60)

    def get_current_weather(self, location: str) -> WeatherData:
        """
        Get current weather for a location

        Args:
            location: City name or coordinates

        Returns:
            WeatherData object with current conditions
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(f"current:{location}")
            if cached:
                return cached

        # Rate limit check
        self.rate_limiter.check()

        # Fetch from provider
        data = self.provider.get_current(location)

        # Cache the result
        if self.cache:
            self.cache.set(f"current:{location}", data)

        return data

    def get_forecast(self, location: str, days: int = 5) -> ForecastData:
        """
        Get weather forecast for a location

        Args:
            location: City name or coordinates
            days: Number of days to forecast

        Returns:
            ForecastData with future predictions
        """
        # TODO: Implement forecast caching
        self.rate_limiter.check()
        return self.provider.get_forecast(location, days)

    def get_historical(
        self,
        location: str,
        start_date: datetime,
        end_date: datetime
    ) -> HistoricalData:
        """
        Get historical weather data for a location

        Args:
            location: City name or coordinates
            start_date: Start of date range
            end_date: End of date range

        Returns:
            HistoricalData with past weather information
        """
        # TODO: Implement historical data retrieval
        # TODO: Add data validation
        # TODO: Support different time granularities
        self.rate_limiter.check()
        return self.provider.get_historical(location, start_date, end_date)

    async def get_current_async(self, location: str) -> WeatherData:
        """Async version of get_current_weather"""
        # TODO: Implement async API calls
        # TODO: Add concurrent request support
        raise NotImplementedError("Async API coming in v0.3.0")
