# API Timeout and Retry Handling Guide

This document describes the timeout and retry handling mechanisms implemented across all API calls in the profile repository.

## Overview

All API calls in this repository are protected against indefinite hangs and transient failures through:

1. **Timeouts**: Every `curl` command has a `--max-time 10` flag (10 seconds)
2. **Retry Logic**: Critical API calls use exponential backoff retry mechanism
3. **Error Handling**: Detailed error messages and exit codes for debugging
4. **Fallback Mechanisms**: Graceful degradation when APIs are unavailable

## Timeout Configuration

### Standard Timeout
All `curl` commands include `--max-time 10`:
```bash
curl -sf --max-time 10 "https://api.example.com/endpoint"
```

This prevents workflows from hanging indefinitely if an API becomes unresponsive.

### Why 10 Seconds?
- Balances responsiveness with network latency tolerance
- Sufficient for most API responses under normal conditions
- Short enough to fail fast and retry on transient issues

## Retry Logic

### Centralized Retry Function
The `retry_with_backoff` function in `scripts/lib/common.sh` provides:

- **Exponential Backoff**: Delays increase exponentially (5s → 10s → 20s)
- **Configurable**: Environment variables control behavior
- **Consistent**: Used across all scripts for uniform retry behavior

### Configuration
```bash
MAX_RETRIES=3                    # Default: 3 attempts
INITIAL_RETRY_DELAY=5            # Default: 5 seconds
```

### Usage Example
```bash
# Source common utilities
source "${SCRIPT_DIR}/lib/common.sh"

# Use retry_with_backoff for API calls
if ! data=$(retry_with_backoff curl -sf --max-time 10 "https://api.example.com/data"); then
    echo "Error: Failed to fetch data after retries" >&2
    return 1
fi
```

### Retry Schedule
With default configuration:
- Attempt 1: Immediate
- Attempt 2: After 5 seconds
- Attempt 3: After 10 seconds (5s delay × 2)
- Attempt 4: After 20 seconds (10s delay × 2)

Total time: ~35 seconds for all attempts

## Scripts with Timeout and Retry Protection

### 1. fetch-soundcloud.sh
- **API Calls**: 6 curl commands
- **Timeout**: All have `--max-time 10`
- **Retry**: Uses `retry_with_backoff` for critical API calls
- **Fallback**: Cached client_id and track data

### 2. fetch-timezone.sh
- **API Calls**: 1 curl command (Open-Meteo)
- **Timeout**: `--max-time 10`
- **Retry**: Uses `retry_with_backoff`

### 3. fetch-weather.sh
- **API Calls**: 1 curl command (Open-Meteo)
- **Timeout**: `--max-time 10`
- **Retry**: Uses `retry_with_backoff`
- **Caching**: Weather data cached for 1 hour

### 4. fetch-oura.sh
- **API Calls**: 1 curl command (wrapped in oura_api_request)
- **Timeout**: `--max-time 10`
- **Retry**: Uses `retry_with_backoff` with exponential backoff
- **Validation**: JSON validation for all responses

### 5. fetch-location.sh
- **API Calls**: 2 curl commands (Open-Meteo, Mapbox)
- **Timeout**: Both have `--max-time 10`
- **Retry**: Open-Meteo uses `retry_with_backoff`
- **Fallback**: Generates fallback map image if Mapbox fails

### 6. common.sh (get_github_location, get_coordinates)
- **API Calls**: 2 curl commands (GitHub API, Nominatim)
- **Timeout**: Both have `--max-time 10`
- **Caching**: Location and coordinate data cached for 7 days
- **Rate Limiting**: Respects Nominatim rate limits (1 request/second)

### 7. health_check.sh
- **API Calls**: 4 curl commands (health checks)
- **Timeout**: All have `--max-time 10`
- **Purpose**: Pre-flight checks for API availability

## Error Handling

### Exit Codes
- `0`: Success
- `1`: General failure (all retries exhausted)
- `6`: DNS resolution failure (curl exit code)
- `7`: Failed to connect (curl exit code)
- `28`: Timeout (curl exit code)

### Error Messages
All scripts provide detailed error messages:
```bash
if [ $curl_exit -ne 0 ]; then
    echo "❌ FAILURE: API request failed (Curl exit code: ${curl_exit})" >&2
    echo "   → Network error or DNS resolution failure" >&2
    return 1
fi
```

### HTTP Status Codes
Scripts check HTTP status codes and provide context:
- `200-299`: Success
- `400-499`: Client errors (invalid request, rate limiting, auth)
- `500-599`: Server errors (API service issues)

## Testing

### Automated Tests

#### test_retry_logic.sh
Tests the core retry functionality:
- Success on first try
- Success after retry
- Failure after max retries
- JSON validation

#### test_timeout_coverage.sh
Verifies all curl commands have timeout protection:
- Scans all shell scripts
- Checks for `--max-time` or `retry_with_backoff`
- Reports any missing timeout protection

Run tests:
```bash
bash tests/test_retry_logic.sh
bash tests/test_timeout_coverage.sh
```

### Manual Testing

Test timeout behavior:
```bash
# Test immediate timeout with unreachable host
curl -sf --max-time 10 "https://10.255.255.1/test"

# Test retry with exponential backoff
source scripts/lib/common.sh
MAX_RETRIES=2 INITIAL_RETRY_DELAY=2 retry_with_backoff false
```

## Best Practices

### When Adding New API Calls

1. **Always add timeout**:
   ```bash
   curl -sf --max-time 10 "https://api.example.com/endpoint"
   ```

2. **Use retry for critical calls**:
   ```bash
   if ! data=$(retry_with_backoff curl -sf --max-time 10 "https://api.example.com/data"); then
       echo "Error: Failed to fetch data after retries" >&2
       return 1
   fi
   ```

3. **Validate responses**:
   ```bash
   if ! validate_api_response "$data" "required_field"; then
       echo "Error: Invalid API response" >&2
       return 1
   fi
   ```

4. **Provide fallback when possible**:
   ```bash
   if ! data=$(fetch_fresh_data); then
       data=$(load_cached_data) || return 1
   fi
   ```

5. **Log detailed errors**:
   ```bash
   echo "❌ FAILURE: Detailed error description" >&2
   echo "   → Helpful troubleshooting tip" >&2
   ```

### Choosing Retry Strategy

**Use `retry_with_backoff` for**:
- Critical data fetching operations
- APIs with transient failures
- Network-sensitive operations

**Don't use retry for**:
- Health checks (want fast failure detection)
- User-triggered actions (avoid long waits)
- Operations with side effects (idempotency concerns)

## Monitoring and Debugging

### Diagnostic Files
Several scripts save diagnostic information:
- `location/debug_nominatim.json`: Nominatim API responses
- `location/debug_map_response.txt`: Mapbox API diagnostic info
- `oura/debug_invalid_response_*.txt`: Failed Oura API responses

### Logging
Scripts use structured logging via `scripts/lib/logging.sh`:
```bash
log_info "Fetching data from API..."
log_error "Failed to fetch data: ${error_msg}"
log_workflow_end "Workflow Name" 0  # 0 = success, 1 = failure
```

## Troubleshooting

### Workflow Hangs
- **Check**: Ensure all curl commands have `--max-time`
- **Run**: `bash tests/test_timeout_coverage.sh`

### Frequent Timeouts
- **Increase timeout**: Change `--max-time 10` to higher value
- **Check network**: Verify internet connectivity
- **Check API status**: Use `scripts/health_check.sh`

### Rate Limiting
- **Nominatim**: 1 request per second (strict)
- **Solution**: Use caching (already implemented)
- **Cache TTL**: 7 days for location data

### All Retries Exhausted
- **Check API status**: Run health checks
- **Review logs**: Check diagnostic files
- **Increase retries**: Set `MAX_RETRIES` environment variable

## References

- [curl timeout options](https://curl.se/docs/manpage.html#-m)
- [Exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)
