# Robustness & Reliability Improvements

This document describes the robustness and reliability improvements implemented to increase system stability, error handling, resilience, and correctness across all workflows.

## Overview

The following improvements have been implemented to make the profile system more resilient to transient failures, API outages, and network issues:

1. **Fallback Caching**
2. **Exponential Backoff Retries**
3. **API Health Checks**
4. **Fallback Location**
5. **Data Staleness Indicators**
6. **JSON Response Validation**

## 1. Fallback Caching

### SoundCloud Fallback Cache

**Location**: `soundcloud/last-success.json`

**Purpose**: Store the last successful SoundCloud track metadata to prevent card disappearance when the API is unavailable.

**Implementation**:
- `fetch-soundcloud.sh` saves successful responses to `soundcloud/last-success.json`
- If API fetch fails, the script automatically falls back to cached data
- Cards continue to display with "(cached)" indicator

**Benefits**:
- Cards never disappear from README
- Graceful degradation during API outages
- User experience remains consistent

### Location Cache

**Location**: `cached/location.json`

**Purpose**: Store GitHub profile location to continue functioning when the GitHub API is unavailable.

**Implementation**:
- `get_github_location()` in `common.sh` saves successful location lookups
- Automatic fallback when GitHub API returns no location or fails
- Includes timestamp for cache validation

**Benefits**:
- Weather and location cards continue to work during GitHub API issues
- Reduces dependency on GitHub API availability

## 2. Exponential Backoff Retries

### Retry Function

**Location**: `scripts/lib/common.sh`

**Function**: `retry_with_backoff()`

**Pattern**: 5s → 10s → 20s (exponential doubling)

**Usage Example**:
```bash
retry_with_backoff curl -sf "https://api.example.com/data"
```

**Configuration**:
- `MAX_RETRIES`: Maximum number of retry attempts (default: 3)
- `INITIAL_RETRY_DELAY`: Starting delay in seconds (default: 5)

### Applied To

| Script | API Calls with Retry |
|--------|---------------------|
| `fetch-soundcloud.sh` | ✅ User resolution<br>✅ Track fetching<br>✅ Artwork download |
| `fetch-weather.sh` | ✅ Open-Meteo forecast API |
| `fetch-location.sh` | ✅ Static map download |
| `common.sh::get_coordinates()` | ✅ Nominatim geocoding |

**Benefits**:
- Transient network issues don't cause failures
- Reduces workflow failure rate
- Respectful backoff pattern prevents API rate limiting

## 3. API Health Checks

### Health Check Script

**Location**: `scripts/health_check.sh`

**Purpose**: Pre-flight checks for API availability before running full workflows.

**Supported APIs**:
- ✅ SoundCloud (homepage accessibility)
- ✅ Open-Meteo (forecast API)
- ✅ Nominatim (geocoding API)
- ✅ Oura (API authentication)

**Usage**:
```bash
# Check all APIs
./scripts/health_check.sh

# Check specific API
./scripts/health_check.sh soundcloud

# Check multiple APIs
./scripts/health_check.sh weather location
```

**Output**:
```json
{
  "checks_run": 4,
  "checks_passed": 4,
  "all_passed": true
}
```

**Benefits**:
- Early detection of API outages
- Can skip workflows when APIs are down
- Better logging and observability

## 4. Data Staleness Indicators

### Time Since Function

**Location**: `scripts/lib/utils.py`

**Function**: `format_time_since(timestamp: str) -> str`

**Output Formats**:
- `"just now"` - Less than 1 minute
- `"5m ago"` - Minutes (1-59)
- `"3h ago"` - Hours (1-23)
- `"7d ago"` - Days (1+)

**Implementation**:
- Parses ISO 8601 timestamps
- Calculates time elapsed from current UTC time
- Returns human-readable string

### Card Integration

**SoundCloud Card**:
- Added `updated_at` field to metadata JSON
- Schema updated to include timestamp
- Badge displayed in top-right corner: "Updated: 2h ago"

**Benefits**:
- Users know when data was last refreshed
- Easy to spot stale data
- Transparency about cache vs. fresh data

## 5. JSON Response Validation

### Validation Function

**Location**: `scripts/lib/common.sh`

**Function**: `validate_api_response(response, required_field)`

**Checks**:
1. Response is non-empty
2. Valid JSON structure (via `jq empty`)
3. Required field exists (optional)

**Usage Example**:
```bash
weather_data=$(curl -sf "https://api.open-meteo.com/v1/forecast?...")
validate_api_response "$weather_data" "current_weather"
```

### Applied To

| API | Required Field Check |
|-----|---------------------|
| SoundCloud User Resolution | `id` |
| SoundCloud Track Fetch | `collection` |
| Open-Meteo Weather | `current_weather` |
| Nominatim Geocoding | *(validated separately)* |

**Benefits**:
- Catch malformed API responses early
- Prevent downstream errors from bad data
- Better error messages for debugging

## 6. Testing

### Test Coverage

**Python Tests** (106 tests):
- Existing card generator tests
- Fallback mechanism tests
- Utility function tests

**New Tests** (15 tests):
- `test_time_utils.py`: Tests for `format_time_since()` function
  - Just now, minutes, hours, days
  - Invalid timestamps
  - Various ISO 8601 formats

**Bash Tests** (6 tests):
- `test_retry_logic.sh`: Tests for retry and validation
  - Success on first try
  - Success after retry
  - JSON validation (valid, invalid, empty)
  - Required field checking

**Total**: 121 tests passing ✅

### Code Quality

- ✅ All bash scripts have valid syntax
- ✅ Code review completed - all feedback addressed
- ✅ CodeQL security scan passed (0 alerts)

## Usage Examples

### Using Fallback Cache

```bash
# Fetch SoundCloud data with fallback
./scripts/fetch-soundcloud.sh > assets/metadata.json
# If API fails, automatically uses soundcloud/last-success.json
```

### Using Retry Logic

```bash
# Source common utilities
source scripts/lib/common.sh

# Retry an API call with exponential backoff
retry_with_backoff curl -sf "https://api.example.com/data"
```

### Running Health Checks

```bash
# Check all APIs before workflow
./scripts/health_check.sh

# Check only specific API
./scripts/health_check.sh soundcloud
```

### Validating API Responses

```bash
# Fetch and validate
response=$(curl -sf "https://api.example.com/data")
validate_api_response "$response" "required_field"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `INITIAL_RETRY_DELAY` | `5` | Initial delay in seconds |
| `CACHE_DIR` | `cache` | Cache directory for general use |
| `CACHE_TTL_DAYS` | `7` | Cache time-to-live in days |
| `FALLBACK_CACHE_FILE` | `soundcloud/last-success.json` | SoundCloud fallback cache |
| `LOCATION_CACHE_FILE` | `cached/location.json` | Location fallback cache |

## Impact Summary

### Reliability
- ✅ Reduced workflow failure rate from transient issues
- ✅ Cards never disappear during API outages
- ✅ Graceful degradation with fallback data

### Observability
- ✅ Staleness indicators show data freshness
- ✅ Better error logging with context
- ✅ Health checks for proactive monitoring

### Performance
- ✅ Cached data reduces API calls
- ✅ Retry backoff prevents rate limiting
- ✅ Validation catches errors early

### Maintainability
- ✅ Centralized retry logic in common.sh
- ✅ Consistent error handling patterns
- ✅ Comprehensive test coverage

## Future Enhancements

Possible additional improvements:

1. **Extend Staleness Indicators**: Add to weather, location, and Oura cards
2. **Workflow Integration**: Add health checks as workflow pre-flight step
3. **Metrics Collection**: Track success rates and retry statistics
4. **Cache Expiration**: Add TTL validation for fallback caches
5. **Notification System**: Alert on repeated failures

## Troubleshooting

### Card Shows Stale Data

**Symptom**: Card displays "Updated: 2d ago"

**Diagnosis**:
1. Check workflow logs for errors
2. Run health check: `./scripts/health_check.sh`
3. Manually test API: `./scripts/fetch-soundcloud.sh`

**Resolution**:
- If API is down, wait for recovery
- If API is up, check credentials and rate limits
- Review workflow logs for specific errors

### Retry Logic Not Working

**Symptom**: Script fails immediately without retries

**Diagnosis**:
1. Check if `common.sh` is sourced
2. Verify `MAX_RETRIES` environment variable
3. Check command syntax with `retry_with_backoff`

**Resolution**:
```bash
# Ensure common.sh is sourced
source scripts/lib/common.sh

# Set retry configuration
export MAX_RETRIES=3
export INITIAL_RETRY_DELAY=5

# Use correct syntax
retry_with_backoff your_command_here
```

### Validation Failures

**Symptom**: "Invalid JSON in API response" errors

**Diagnosis**:
1. Check API response directly: `curl -sf "API_URL"`
2. Validate JSON: `echo "$response" | jq empty`
3. Check for required fields: `echo "$response" | jq '.field'`

**Resolution**:
- Verify API endpoint is correct
- Check API credentials and permissions
- Review API documentation for response format

## Support

For issues or questions:
1. Review workflow logs in GitHub Actions
2. Check this documentation for troubleshooting
3. Open an issue in the repository
