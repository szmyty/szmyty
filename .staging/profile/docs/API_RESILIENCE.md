# API Resilience Features

This document describes the API resilience features implemented in the profile repository to handle external API failures gracefully.

## Overview

The repository now includes comprehensive API resilience features to protect against:
- **Rate limiting** (HTTP 429 responses)
- **Network failures** and timeouts
- **Temporary service outages**
- **Cascading failures** through circuit breaker pattern

## Features

### 1. Health Checks

Before making API calls, the system performs health checks to verify API availability.

**Function:** `health_check_api()`

**Usage:**
```bash
source scripts/lib/common.sh

# Basic health check
health_check_api "https://api.example.com" "Example API"

# Health check with authentication
health_check_api "https://api.example.com" "Example API" "Bearer your-token"
```

**Benefits:**
- Early detection of API unavailability
- Reduces unnecessary retry attempts
- Provides clear status messages

### 2. Rate Limit Detection

The system automatically detects HTTP 429 (Too Many Requests) responses and handles them appropriately.

**Features:**
- Detects `Retry-After` header from API responses
- Increases backoff delay for rate-limited requests
- Logs rate limit events for monitoring
- Records failures in circuit breaker

**Example Output:**
```
🚫 Rate limit detected (HTTP 429) from Oura API
   → Server requested 60s wait time
```

### 3. Circuit Breaker Pattern

Prevents repeated calls to failing APIs by "opening the circuit" after a threshold of failures.

**Function:** `retry_api_call()`

**Configuration:**
```bash
# Environment variables
CIRCUIT_BREAKER_THRESHOLD=3      # Number of failures before opening circuit (default: 3)
CIRCUIT_BREAKER_TIMEOUT=300      # Timeout in seconds before allowing retry (default: 300 = 5 minutes)
CIRCUIT_BREAKER_DIR=cache/circuit_breaker  # Directory for circuit state files
```

**Usage:**
```bash
# Make API call with circuit breaker protection
response=$(retry_api_call "My API" curl -sf "https://api.example.com/data" \
    -H "Authorization: Bearer $TOKEN")
```

**Circuit States:**
- **CLOSED**: Normal operation, requests proceed
- **OPEN**: API is temporarily disabled after repeated failures
- **HALF-OPEN**: Testing if API has recovered after timeout

**Example Flow:**
```
Attempt 1: ❌ Failed
   ⚠️  Recorded failure #1 for My API

Attempt 2: ❌ Failed
   ⚠️  Recorded failure #2 for My API

Attempt 3: ❌ Failed
   ⚠️  Recorded failure #3 for My API
   🚨 Circuit breaker OPENED for My API after 3 failures
      → API calls will be blocked for 300s

Future attempts (within timeout):
   ⛔ Circuit breaker is OPEN for My API (3 failures, retry in 245s)

After timeout expires:
   🔄 Circuit breaker timeout expired for My API, allowing retry
```

### 4. Recovery Logging

When an API recovers after failures, the system logs the recovery and resets the circuit breaker.

**Example:**
```
✅ API recovered: Oura API - resetting circuit breaker
```

## API-Specific Implementations

### Oura Ring API

**File:** `scripts/fetch-oura.sh`

**Features:**
- Health check before fetching metrics
- Circuit breaker for all endpoints
- Rate limit detection with exponential backoff
- Automatic recovery tracking

**Usage:**
```bash
OURA_PAT="your-token" ./scripts/fetch-oura.sh
```

### Weather API (Open-Meteo)

**File:** `scripts/fetch-weather.sh`

**Features:**
- Health check before fetching weather data
- Circuit breaker protection
- 1-hour response caching to reduce API calls
- Rate limit detection

**Usage:**
```bash
GITHUB_OWNER="username" ./scripts/fetch-weather.sh
```

### SoundCloud API

**File:** `scripts/fetch-soundcloud.sh`

**Features:**
- Circuit breaker for user resolution and track fetching
- Rate limit detection
- Fallback to cached data on failures

**Usage:**
```bash
SOUNDCLOUD_USER="username" ./scripts/fetch-soundcloud.sh
```

### Location APIs (Nominatim & Mapbox)

**File:** `scripts/fetch-location.sh` and `scripts/lib/common.sh`

**Features:**
- Health check for Nominatim geocoding API
- Health check for Mapbox static maps API
- Rate limit detection for Nominatim (strict 1 req/sec limit)
- Circuit breaker tracking for both APIs
- Long-term coordinate caching (7 days)

**Usage:**
```bash
GITHUB_OWNER="username" MAPBOX_TOKEN="token" ./scripts/fetch-location.sh
```

## Testing

### Health Check Tests

Run comprehensive tests for health checks and circuit breaker:

```bash
bash tests/test_health_checks.sh
```

**Test Coverage:**
- Health check function format and output
- Circuit breaker starts in closed state
- Recording API failures
- Circuit opens after threshold failures
- Circuit closes after timeout expires
- Success resets circuit breaker
- Safe filename generation for circuit state files
- Circuit breaker directory initialization

### Retry Logic Tests

Run tests for retry mechanisms and validation:

```bash
bash tests/test_retry_logic.sh
```

## Circuit Breaker State Files

Circuit breaker state is persisted in files under `cache/circuit_breaker/`:

**File Format:**
```
<timestamp>
<failure_count>
```

**Example:**
```
cache/circuit_breaker/
├── oura_api_circuit.state
├── soundcloud_api_circuit.state
├── nominatim_api_circuit.state
└── open-meteo_api_circuit.state
```

**State File Cleanup:**
- Automatically removed on successful API calls
- Automatically reset after timeout expires
- Can be manually deleted to force retry

## Best Practices

1. **Always use `retry_api_call()` for external API calls** instead of plain `retry_with_backoff()`
2. **Set appropriate circuit breaker thresholds** based on API sensitivity
3. **Monitor circuit breaker events** in logs to identify problematic APIs
4. **Use caching aggressively** to reduce API calls
5. **Implement fallback data** for critical features
6. **Respect API rate limits** even before hitting 429 responses

## Configuration Examples

### Strict Rate Limiting (Critical APIs)
```bash
export CIRCUIT_BREAKER_THRESHOLD=2
export CIRCUIT_BREAKER_TIMEOUT=600  # 10 minutes
export MAX_RETRIES=2
```

### Lenient Configuration (Testing)
```bash
export CIRCUIT_BREAKER_THRESHOLD=5
export CIRCUIT_BREAKER_TIMEOUT=60   # 1 minute
export MAX_RETRIES=4
```

## Troubleshooting

### Circuit Breaker Stuck Open

If a circuit breaker remains open longer than expected:

```bash
# Find circuit state files
ls cache/circuit_breaker/

# Remove specific circuit state
rm cache/circuit_breaker/my_api_circuit.state

# Or remove all circuits
rm -rf cache/circuit_breaker/*.state
```

### Rate Limiting Issues

If you're consistently hitting rate limits:

1. **Check cache TTL** - Increase caching duration
2. **Review request frequency** - Reduce workflow trigger frequency
3. **Check API quotas** - Verify your API plan limits
4. **Implement request throttling** - Add delays between requests

### Debugging Circuit Breaker

To debug circuit breaker behavior:

```bash
# Set environment for verbose logging
export CIRCUIT_BREAKER_DIR="./debug_circuits"
export CIRCUIT_BREAKER_THRESHOLD=2
export CIRCUIT_BREAKER_TIMEOUT=30

# Run your script
./scripts/fetch-oura.sh

# Inspect circuit state
cat debug_circuits/*.state
```

## Future Enhancements

Potential improvements for consideration:

1. **Metrics Dashboard** - Visualize circuit breaker events and API health
2. **Adaptive Thresholds** - Dynamically adjust thresholds based on API behavior
3. **Priority Queuing** - Prioritize critical API calls during rate limiting
4. **Distributed Circuit Breaker** - Share circuit state across workflow runs
5. **Alert Integration** - Send notifications when circuits open
6. **API Health Score** - Track and display long-term API reliability

## References

- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [HTTP Status Code 429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
