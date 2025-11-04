"""
Data models for weather information
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Temperature(BaseModel):
    """Temperature data"""
    celsius: float
    fahrenheit: float
    kelvin: float

    @classmethod
    def from_celsius(cls, celsius: float):
        """Create Temperature from Celsius value"""
        return cls(
            celsius=celsius,
            fahrenheit=celsius * 9/5 + 32,
            kelvin=celsius + 273.15
        )


class Location(BaseModel):
    """Geographic location"""
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: Optional[str] = None


class WeatherCondition(BaseModel):
    """Weather condition description"""
    main: str
    description: str
    icon: Optional[str] = None


class WeatherData(BaseModel):
    """Complete weather data response"""
    location: Location
    temperature: Temperature
    conditions: List[WeatherCondition]
    humidity: float = Field(ge=0, le=100)
    pressure: float
    wind_speed: float
    timestamp: datetime

    # Optional fields for extended data
    visibility: Optional[float] = None
    cloudiness: Optional[float] = None
    precipitation: Optional[float] = None


class ForecastData(BaseModel):
    """Weather forecast data"""
    location: Location
    forecasts: List[WeatherData]
    generated_at: datetime

    # TODO: Add forecast accuracy metrics
    # TODO: Add confidence intervals


class HistoricalData(BaseModel):
    """Historical weather data"""
    location: Location
    data_points: List[WeatherData]
    date_range_start: datetime
    date_range_end: datetime

    # TODO: Add statistical summaries
    # TODO: Add trend analysis
