"""
WeatherAPI Client - Python library for weather data access
"""

__version__ = "0.2.0"
__author__ = "Weather Team"

from .client import WeatherClient
from .models import WeatherData, Location, Temperature
from .providers import OpenWeatherProvider, WeatherStackProvider

__all__ = [
    "WeatherClient",
    "WeatherData",
    "Location",
    "Temperature",
    "OpenWeatherProvider",
    "WeatherStackProvider",
]
