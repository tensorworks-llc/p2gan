# API Reference

## WeatherClient

Main client class for accessing weather data.

### Constructor

```python
WeatherClient(
    api_key: str,
    provider: Optional[BaseProvider] = None,
    enable_cache: bool = True,
    cache_ttl: int = 300
)
```

**Parameters:**
- `api_key`: Your API key for the weather provider
- `provider`: Weather provider instance (defaults to OpenWeatherProvider)
- `enable_cache`: Enable response caching (default: True)
- `cache_ttl`: Cache time-to-live in seconds (default: 300)

### Methods

#### get_current_weather

```python
get_current_weather(location: str) -> WeatherData
```

Get current weather conditions for a location.

**Parameters:**
- `location`: City name or coordinates (e.g., "London" or "51.5074,-0.1278")

**Returns:**
- `WeatherData` object with current conditions

**Example:**
```python
client = WeatherClient(api_key="your_key")
weather = client.get_current_weather("Paris")
print(f"Temperature: {weather.temperature.celsius}°C")
```

#### get_forecast

```python
get_forecast(location: str, days: int = 5) -> ForecastData
```

Get weather forecast for a location.

**Status:** 🚧 In Progress

---

## Data Models

### WeatherData

Complete weather information for a location and time.

**Fields:**
- `location`: Location object
- `temperature`: Temperature object
- `conditions`: List of weather conditions
- `humidity`: Humidity percentage (0-100)
- `pressure`: Atmospheric pressure
- `wind_speed`: Wind speed
- `timestamp`: Time of observation

### Temperature

Temperature in multiple units.

**Fields:**
- `celsius`: Temperature in Celsius
- `fahrenheit`: Temperature in Fahrenheit
- `kelvin`: Temperature in Kelvin

**Methods:**
- `from_celsius(celsius: float)`: Create from Celsius value
