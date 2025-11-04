# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-10-15

### Added
- Caching support for API responses
- Rate limiting to prevent API quota exhaustion
- WeatherStack provider (partial implementation)
- Comprehensive data models with Pydantic validation

### Changed
- Improved error handling in providers
- Updated documentation with examples

### In Progress
- Historical data retrieval
- Forecast endpoint improvements
- Async API support

## [0.1.0] - 2024-09-01

### Added
- Initial release
- Basic WeatherClient implementation
- OpenWeatherMap provider
- Current weather endpoint
- Temperature, Location, and WeatherData models
- Basic test suite

### Known Issues
- Forecast endpoint not fully implemented
- Historical data not available yet
- No async support

## [Planned] - v0.3.0

### To Be Added
- Full async API support
- Complete historical data retrieval
- Weather alerts and notifications
- Advanced caching strategies (Redis, Memcached)
- GraphQL API support
- CLI tool for quick weather queries
