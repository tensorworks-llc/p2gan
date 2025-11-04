"""
Weather data providers
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import requests

from .models import WeatherData, ForecastData, HistoricalData, Location, Temperature


class BaseProvider(ABC):
    """Abstract base class for weather providers"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def get_current(self, location: str) -> WeatherData:
        """Get current weather"""
        pass

    @abstractmethod
    def get_forecast(self, location: str, days: int) -> ForecastData:
        """Get weather forecast"""
        pass

    @abstractmethod
    def get_historical(
        self,
        location: str,
        start_date: datetime,
        end_date: datetime
    ) -> HistoricalData:
        """Get historical weather data"""
        pass


class OpenWeatherProvider(BaseProvider):
    """OpenWeatherMap API provider"""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def get_current(self, location: str) -> WeatherData:
        """Get current weather from OpenWeatherMap"""
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse response into our models
        return self._parse_current_response(data)

    def get_forecast(self, location: str, days: int) -> ForecastData:
        """Get forecast from OpenWeatherMap"""
        # TODO: Implement forecast parsing
        raise NotImplementedError("Forecast support coming soon")

    def get_historical(
        self,
        location: str,
        start_date: datetime,
        end_date: datetime
    ) -> HistoricalData:
        """Get historical data from OpenWeatherMap"""
        # TODO: Implement historical data retrieval
        raise NotImplementedError("Historical data support coming soon")

    def _parse_current_response(self, data: dict) -> WeatherData:
        """Parse OpenWeatherMap current weather response"""
        # TODO: Add better error handling
        # TODO: Support all weather fields
        # Implementation would go here
        pass


class WeatherStackProvider(BaseProvider):
    """WeatherStack API provider"""

    BASE_URL = "http://api.weatherstack.com"

    def get_current(self, location: str) -> WeatherData:
        """Get current weather from WeatherStack"""
        # TODO: Implement WeatherStack support
        raise NotImplementedError("WeatherStack provider coming in v0.3.0")

    def get_forecast(self, location: str, days: int) -> ForecastData:
        """Get forecast from WeatherStack"""
        raise NotImplementedError("WeatherStack provider coming in v0.3.0")

    def get_historical(
        self,
        location: str,
        start_date: datetime,
        end_date: datetime
    ) -> HistoricalData:
        """Get historical data from WeatherStack"""
        raise NotImplementedError("WeatherStack provider coming in v0.3.0")
