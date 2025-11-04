"""
Tests for data models
"""

import pytest
from datetime import datetime
from weatherapi.models import Temperature, Location, WeatherData, WeatherCondition


class TestTemperature:
    """Test suite for Temperature model"""

    def test_from_celsius(self):
        """Test creating Temperature from Celsius"""
        temp = Temperature.from_celsius(20.0)
        assert temp.celsius == 20.0
        assert temp.fahrenheit == 68.0
        assert temp.kelvin == 293.15

    def test_from_celsius_freezing(self):
        """Test freezing point conversion"""
        temp = Temperature.from_celsius(0.0)
        assert temp.celsius == 0.0
        assert temp.fahrenheit == 32.0
        assert temp.kelvin == 273.15


class TestLocation:
    """Test suite for Location model"""

    def test_location_creation(self):
        """Test creating a Location"""
        loc = Location(
            name="New York",
            country="US",
            latitude=40.7128,
            longitude=-74.0060
        )
        assert loc.name == "New York"
        assert loc.country == "US"

    # TODO: Add validation tests for coordinates
    # TODO: Add tests for timezone handling
