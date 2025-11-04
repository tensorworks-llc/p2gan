# User Guide

## Getting Started

### Installation

```bash
pip install weatherapi-client
```

### Basic Usage

```python
from weatherapi import WeatherClient

# Initialize the client
client = WeatherClient(api_key="your_api_key_here")

# Get current weather
weather = client.get_current_weather("London")

# Access temperature data
print(f"Temperature: {weather.temperature.celsius}°C")
print(f"Humidity: {weather.humidity}%")
print(f"Conditions: {weather.conditions[0].description}")
```

## Advanced Features

### Caching

By default, the client caches responses for 5 minutes to reduce API calls:

```python
# Custom cache TTL (10 minutes)
client = WeatherClient(api_key="key", cache_ttl=600)

# Disable caching
client = WeatherClient(api_key="key", enable_cache=False)
```

### Multiple Providers

Switch between weather data providers:

```python
from weatherapi import WeatherClient
from weatherapi.providers import WeatherStackProvider

provider = WeatherStackProvider(api_key="your_key")
client = WeatherClient(api_key="key", provider=provider)
```

## Planned Features

### Historical Data (Coming in v0.3.0)

```python
from datetime import datetime

# Get historical weather data
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)
history = client.get_historical("New York", start, end)
```

### Async Support (Coming in v0.3.0)

```python
# Async API calls
weather = await client.get_current_async("Tokyo")
```

## Rate Limiting

The client automatically handles rate limiting. By default:
- 60 requests per minute
- Raises `RateLimitError` when exceeded

## Error Handling

```python
from weatherapi import WeatherClient
from weatherapi.rate_limiter import RateLimitError

try:
    weather = client.get_current_weather("Invalid Location")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except Exception as e:
    print(f"Error: {e}")
```
