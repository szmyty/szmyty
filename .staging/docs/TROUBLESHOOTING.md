# Troubleshooting Guide for Common Workflow Failures

This guide provides solutions for common issues encountered in GitHub Actions workflows. Use this guide to quickly diagnose and resolve workflow failures.

## Quick Reference

| Issue | Symptoms | Quick Fix | Section |
|-------|----------|-----------|---------|
| Rate Limiting | HTTP 429, "API rate limit exceeded" | Wait or use authentication | [Rate Limiting](#rate-limiting-issues) |
| Invalid JSON | "parse error", "Invalid JSON" | Validate with `jq empty` | [Invalid JSON](#invalid-json-errors) |
| API Timeout | "timeout", "max-time exceeded" | Check network, increase timeout | [External API Failures](#external-api-failures) |
| Missing Keys | "KeyError", "field not found" | Use safe accessors, validate schema | [Missing Keys](#missing-keys-in-data) |
| Concurrency | "git conflict", "another workflow running" | Wait for completion, check concurrency group | [Concurrency](#workflow-concurrency-collisions) |
| Theme Errors | "theme.json not found", color errors | Validate JSON, check file exists | [Theme.json](#themejson-errors) |
| Timeout | Workflow hangs, no output | Add `--max-time`, check logs | [Timeout Handling](#timeout-handling) |
| Schema Validation | "schema validation failed" | Update data to match schema | [Schema Validation](#missing-schema-validation) |

---

## Rate Limiting Issues

### GitHub API Rate Limiting

**Symptoms:**
- HTTP 403 with message "API rate limit exceeded"
- Workflow fails after making multiple GitHub API calls
- Error: "X-RateLimit-Remaining: 0"

**Root Cause:**
Unauthenticated GitHub API requests are limited to 60 requests/hour per IP address.

**Solutions:**

1. **Use Authentication Token (Recommended):**
   ```bash
   # In workflow YAML
   - name: Fetch GitHub data
     run: |
       curl -sf --max-time 10 \
         -H "Authorization: Bearer ${{ github.token }}" \
         "https://api.github.com/user"
   ```

2. **Check Current Rate Limit:**
   ```bash
   curl -sf -H "Authorization: Bearer ${{ github.token }}" \
     https://api.github.com/rate_limit
   ```

3. **Implement Caching:**
   ```bash
   # Cache GitHub profile location for 7 days
   CACHE_FILE="cache/github_location.json"
   CACHE_TTL=$((7 * 24 * 3600))  # 7 days in seconds
   
   if [ -f "$CACHE_FILE" ]; then
     cache_age=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE")))
     if [ $cache_age -lt $CACHE_TTL ]; then
       location=$(cat "$CACHE_FILE")
       echo "Using cached location"
     fi
   fi
   ```

### Nominatim Rate Limiting

**Symptoms:**
- HTTP 429 "Too Many Requests"
- Geocoding fails with "Request denied"
- Multiple location/weather workflows fail simultaneously

**Root Cause:**
Nominatim has strict rate limits: **1 request per second** per IP address.

**Solutions:**

1. **Add Delays Between Requests:**
   ```bash
   # Already implemented in scripts/lib/common.sh
   sleep 1  # Wait 1 second between Nominatim requests
   ```

2. **Cache Geocoding Results:**
   ```bash
   # Location rarely changes - cache for 7 days
   COORD_CACHE="cache/coordinates_${location_hash}.json"
   if [ -f "$COORD_CACHE" ] && [ $(find "$COORD_CACHE" -mtime -7) ]; then
     coordinates=$(cat "$COORD_CACHE")
   else
     coordinates=$(curl -sf "https://nominatim.openstreetmap.org/search?...")
     echo "$coordinates" > "$COORD_CACHE"
   fi
   ```

3. **Stagger Workflow Schedules:**
   ```yaml
   # .github/workflows/location-card.yml
   on:
     schedule:
       - cron: '0 6 * * *'  # 6 AM UTC
   
   # .github/workflows/weather.yml
   on:
     schedule:
       - cron: '0 7 * * *'  # 7 AM UTC (1 hour later)
   ```

### External API Rate Limits

**Symptoms:**
- SoundCloud: "403 Forbidden" or client_id extraction fails
- Oura: "429 Too Many Requests"
- Mapbox: "Rate limit exceeded"

**Solutions:**

1. **Use Retry with Exponential Backoff:**
   ```bash
   source scripts/lib/common.sh
   retry_with_backoff curl -sf --max-time 10 "https://api.example.com/data"
   ```

2. **Reduce Workflow Frequency:**
   ```yaml
   # Change from hourly to every 6 hours
   on:
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours
   ```

3. **Implement Fallback Caching:**
   ```bash
   # Try API first, fall back to cache on failure
   if ! data=$(fetch_from_api); then
     echo "⚠️ API failed, using cached data" >&2
     data=$(cat soundcloud/last-success.json)
   fi
   ```

---

## Invalid JSON Errors

### Malformed API Responses

**Symptoms:**
- Error: "parse error: Invalid numeric literal"
- Error: "jq: error: Cannot parse JSON"
- Python: `json.JSONDecodeError: Expecting value`

**Root Cause:**
- API returns HTML error page instead of JSON
- Network error results in partial response
- API returns empty response
- Invalid characters in JSON

**Solutions:**

1. **Validate JSON Before Processing:**
   ```bash
   # Use jq to validate JSON structure
   if ! echo "$response" | jq empty 2>/dev/null; then
     echo "❌ ERROR: Invalid JSON in API response" >&2
     echo "$response" > debug_invalid_response.txt
     return 1
   fi
   ```

2. **Check HTTP Status Before Parsing:**
   ```bash
   # Get both status and response
   response=$(curl -sf -w "\n%{http_code}" --max-time 10 "$url")
   http_code=$(echo "$response" | tail -n1)
   body=$(echo "$response" | sed '$d')
   
   if [ "$http_code" != "200" ]; then
     echo "❌ ERROR: API returned status $http_code" >&2
     return 1
   fi
   
   # Now safe to parse JSON
   data=$(echo "$body" | jq '.')
   ```

3. **Use Python JSON Validation:**
   ```python
   import json
   
   def load_json_safely(filepath):
       """Load JSON file with error handling."""
       try:
           with open(filepath, 'r') as f:
               return json.load(f)
       except json.JSONDecodeError as e:
           print(f"❌ ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
           print(f"   → Line {e.lineno}, Column {e.colno}", file=sys.stderr)
           return None
       except FileNotFoundError:
           print(f"❌ ERROR: File not found: {filepath}", file=sys.stderr)
           return None
   ```

4. **Validate Required Fields Exist:**
   ```bash
   # Use validate_api_response from common.sh
   source scripts/lib/common.sh
   
   if ! validate_api_response "$response" "required_field"; then
     echo "❌ ERROR: Response missing required field" >&2
     return 1
   fi
   ```

### Empty or Null Responses

**Symptoms:**
- Error: "Cannot iterate over null"
- Error: "Expected object, got null"
- Workflow succeeds but generates empty cards

**Solutions:**

1. **Check for Empty Response:**
   ```bash
   if [ -z "$response" ]; then
     echo "❌ ERROR: Empty API response" >&2
     return 1
   fi
   ```

2. **Handle Null Values in Python:**
   ```python
   def safe_get(data, *keys, default=None):
       """Safely get nested dictionary value."""
       for key in keys:
           if isinstance(data, dict):
               data = data.get(key)
           else:
               return default
           if data is None:
               return default
       return data
   
   # Usage
   sleep_score = safe_get(metrics, "sleep", "score", default=0)
   ```

---

## External API Failures

### SoundCloud API Issues

**Common Failures:**

1. **Client ID Extraction Fails**

**Symptoms:**
- Error: "Failed to extract client_id"
- Error: "No valid client_id found"

**Diagnosis:**
```bash
# Check if SoundCloud is accessible
curl -sf --max-time 10 https://soundcloud.com
```

**Solutions:**
- SoundCloud may have changed their JavaScript structure
- Check workflow logs for the extracted client_id pattern
- Use cached client_id from `assets/.cache/soundcloud_client_id.txt`
- Update regex pattern in `scripts/fetch-soundcloud.sh` if needed

2. **Track Fetch Fails**

**Symptoms:**
- Error: "Failed to fetch track data"
- Empty or invalid `metadata.json`

**Solutions:**
```bash
# Test SoundCloud API directly
client_id="YOUR_EXTRACTED_CLIENT_ID"
curl -sf --max-time 10 \
  "https://api-v2.soundcloud.com/users/$user_id/tracks?client_id=$client_id"

# Use fallback cache
if [ -f "soundcloud/last-success.json" ]; then
  cp soundcloud/last-success.json assets/metadata.json
fi
```

### Open-Meteo API (Weather/Location)

**Symptoms:**
- Error: "Failed to fetch weather data"
- Timeout after 10 seconds
- Invalid coordinates

**Solutions:**

1. **Verify API Endpoint:**
   ```bash
   # Test weather API
   curl -sf --max-time 10 \
     "https://api.open-meteo.com/v1/forecast?latitude=42.36&longitude=-71.06&current_weather=true"
   ```

2. **Check Coordinate Format:**
   ```bash
   # Coordinates must be numeric
   if ! [[ "$lat" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
     echo "❌ ERROR: Invalid latitude: $lat" >&2
     return 1
   fi
   ```

3. **Use Retry Logic:**
   ```bash
   source scripts/lib/common.sh
   weather_data=$(retry_with_backoff curl -sf --max-time 10 "$weather_url")
   ```

### Oura API Issues

**Symptoms:**
- Error: "401 Unauthorized"
- Error: "Failed to fetch Oura metrics"
- Invalid or expired Personal Access Token (PAT)

**Solutions:**

1. **Verify PAT is Set:**
   ```yaml
   # In workflow YAML
   - name: Check Oura PAT
     run: |
       if [ -z "${{ secrets.OURA_PAT }}" ]; then
         echo "❌ ERROR: OURA_PAT secret is not set" >&2
         exit 1
       fi
   ```

2. **Test Oura API Directly:**
   ```bash
   curl -sf --max-time 10 \
     -H "Authorization: Bearer $OURA_PAT" \
     "https://api.ouraring.com/v2/usercollection/daily_sleep"
   ```

3. **Regenerate PAT:**
   - Go to https://cloud.ouraring.com/personal-access-tokens
   - Create new token
   - Update GitHub secret: Settings → Secrets → OURA_PAT

4. **Check API Response Format:**
   ```bash
   # Oura API may return null for recent days
   # Handle gracefully in generate scripts
   ```

### Mapbox Static Map API

**Symptoms:**
- Error: "Failed to download map image"
- Empty or corrupted PNG file
- HTTP 401 or 403 errors

**Solutions:**

1. **Use Fallback Image Generation:**
   ```bash
   # Already implemented in fetch-location.sh
   if ! retry_with_backoff curl -sf --max-time 10 "$mapbox_url" > map.png; then
     echo "⚠️ Mapbox failed, generating fallback image" >&2
     python scripts/generate-fallback-map.py location.json map.png
   fi
   ```

2. **Verify Mapbox Token (if using authenticated API):**
   ```bash
   # Check if token is set
   if [ -n "$MAPBOX_TOKEN" ]; then
     curl -sf "https://api.mapbox.com/v4/mapbox.satellite/...?access_token=$MAPBOX_TOKEN"
   fi
   ```

---

## Missing Keys in Data

### Handling Missing Fields

**Symptoms:**
- Python: `KeyError: 'field_name'`
- Bash: Empty variable leading to errors
- Cards show "—" or blank values

**Root Cause:**
- API doesn't always return all fields
- Oura Ring may not have data for recent days
- User profile may be incomplete

**Solutions:**

1. **Use Safe Dictionary Access in Python:**
   ```python
   # Use .get() with defaults
   sleep_score = data.get("sleep_score", 0)
   
   # Use safe_get for nested access
   def safe_get(data, *keys, default=None):
       for key in keys:
           if isinstance(data, dict):
               data = data.get(key)
           else:
               return default
           if data is None:
               return default
       return data
   
   # Example usage
   hr_avg = safe_get(metrics, "heart_rate", "average", default=0)
   ```

2. **Check Field Exists in Bash:**
   ```bash
   # Use jq to safely extract with default
   sleep_score=$(echo "$data" | jq -r '.sleep_score // 0')
   
   # Or check if field exists first
   if echo "$data" | jq -e '.sleep_score' >/dev/null 2>&1; then
     sleep_score=$(echo "$data" | jq -r '.sleep_score')
   else
     sleep_score=0
   fi
   ```

3. **Validate Required Fields:**
   ```python
   def validate_required_fields(data, required_fields):
       """Validate that all required fields exist."""
       missing = [field for field in required_fields if field not in data]
       if missing:
           print(f"⚠️ WARNING: Missing fields: {', '.join(missing)}", file=sys.stderr)
           return False
       return True
   
   # Usage
   required = ["sleep_score", "readiness_score", "activity_score"]
   if not validate_required_fields(metrics, required):
       # Use fallback values or skip card generation
       pass
   ```

4. **Set Defaults for Optional Fields:**
   ```python
   # Provide sensible defaults
   snapshot = {
       "sleep_score": metrics.get("sleep_score", 0),
       "readiness_score": metrics.get("readiness_score", 0),
       "activity_score": metrics.get("activity_score", 0),
       "heart_rate": metrics.get("heart_rate", {}),
       "hrv": metrics.get("hrv", {}),
       # ... more fields
   }
   ```

---

## Workflow Concurrency Collisions

### Git Conflicts

**Symptoms:**
- Error: "failed to push some refs"
- Error: "Updates were rejected"
- Error: "! [rejected] main -> main (non-fast-forward)"

**Root Cause:**
Multiple workflows running simultaneously trying to push to the same branch.

**Solutions:**

1. **Use Concurrency Groups (Recommended):**
   ```yaml
   # Add to all workflow files
   concurrency:
     group: profile-update
     cancel-in-progress: false  # Wait for other workflows to finish
   ```

2. **Pull Before Push:**
   ```yaml
   - name: Commit and push changes
     run: |
       if git diff --quiet; then
         echo "No changes to commit"
         exit 0
       fi
       
       git config --local user.email "github-actions[bot]@users.noreply.github.com"
       git config --local user.name "github-actions[bot]"
       
       git pull --rebase origin main
       git add .
       git commit -m "🔄 Update cards [automated]"
       git push
   ```

3. **Stagger Workflow Schedules:**
   ```yaml
   # Location: 6:00 AM UTC
   - cron: '0 6 * * *'
   
   # Weather: 7:00 AM UTC  
   - cron: '0 7 * * *'
   
   # SoundCloud: 8:00 AM, 2:00 PM, 8:00 PM, 2:00 AM
   - cron: '0 8,14,20,2 * * *'
   
   # Oura: Every 6 hours starting at 9 AM
   - cron: '0 9,15,21,3 * * *'
   ```

4. **Use Retry on Push Failure:**
   ```bash
   # Retry push up to 3 times
   MAX_RETRIES=3
   for i in $(seq 1 $MAX_RETRIES); do
     if git push; then
       echo "✅ Push successful"
       break
     else
       echo "⚠️ Push failed, retrying in 10s (attempt $i/$MAX_RETRIES)"
       sleep 10
       git pull --rebase origin main
     fi
   done
   ```

### Workflow Queue Management

**Check Running Workflows:**
```bash
# Use GitHub CLI to check workflow status
gh run list --workflow=oura.yml --limit 5

# Check if a workflow is currently running
gh run list --workflow=oura.yml --status in_progress
```

**Cancel Stuck Workflows:**
```bash
# Cancel a specific run
gh run cancel <run_id>

# Cancel all in-progress runs for a workflow
gh run list --workflow=oura.yml --status in_progress --json databaseId --jq '.[].databaseId' | xargs -I {} gh run cancel {}
```

---

## Theme.json Errors

### Missing Theme File

**Symptoms:**
- Error: "config/theme.json not found"
- Error: "FileNotFoundError: [Errno 2] No such file or directory: 'config/theme.json'"

**Solutions:**

1. **Create Default Theme File:**
   ```json
   {
     "colors": {
       "background_start": "#0f0f23",
       "background_end": "#1a1a2e",
       "accent": "#64ffda",
       "text_primary": "#ffffff",
       "text_secondary": "#8892b0",
       "text_muted": "#4a5568"
     },
     "spacing": {
       "card_padding": 20,
       "section_gap": 15
     },
     "typography": {
       "font_family": "'Segoe UI', Arial, sans-serif",
       "heading_size": 14,
       "body_size": 12,
       "small_size": 10
     }
   }
   ```

2. **Check File Exists in Script:**
   ```python
   import os
   
   theme_path = "config/theme.json"
   if not os.path.exists(theme_path):
       print(f"⚠️ WARNING: {theme_path} not found, using defaults", file=sys.stderr)
       theme = get_default_theme()
   else:
       with open(theme_path) as f:
           theme = json.load(f)
   ```

### Invalid Theme JSON

**Symptoms:**
- Error: "Expecting property name enclosed in double quotes"
- Error: "Extra data" or "Missing required property"

**Solutions:**

1. **Validate JSON Syntax:**
   ```bash
   # Use jq to validate
   jq empty config/theme.json
   
   # Or use Python
   python -m json.tool config/theme.json
   ```

2. **Common JSON Errors:**
   - Missing comma between properties
   - Trailing comma after last property
   - Single quotes instead of double quotes
   - Unescaped special characters

3. **Use JSON Schema Validation:**
   ```python
   import jsonschema
   
   theme_schema = {
       "type": "object",
       "required": ["colors", "spacing", "typography"],
       "properties": {
           "colors": {
               "type": "object",
               "required": ["background_start", "background_end", "accent"]
           }
       }
   }
   
   try:
       jsonschema.validate(theme, theme_schema)
   except jsonschema.ValidationError as e:
       print(f"❌ Theme validation error: {e.message}", file=sys.stderr)
   ```

---

## Timeout Handling

### Workflow Timeouts

**Symptoms:**
- Workflow runs for hours without completing
- No output or logs after certain step
- Error: "The job running on runner has exceeded the maximum execution time of 360 minutes"

**Solutions:**

1. **Add Timeout to Workflow Jobs:**
   ```yaml
   jobs:
     update-card:
       runs-on: ubuntu-latest
       timeout-minutes: 10  # Kill job after 10 minutes
       steps:
         # ...
   ```

2. **Add Timeout to Individual Steps:**
   ```yaml
   - name: Fetch data with timeout
     timeout-minutes: 2
     run: |
       ./scripts/fetch-oura.sh
   ```

### HTTP Request Timeouts

**Symptoms:**
- Curl hangs indefinitely
- Workflow stuck on API call step
- No error message, just silence

**Solutions:**

1. **Always Use --max-time with curl:**
   ```bash
   # Set maximum time for entire operation to 10 seconds
   curl -sf --max-time 10 "https://api.example.com/data"
   ```

2. **Also Add Connection Timeout:**
   ```bash
   # Limit connection time (DNS + TCP handshake) to 5s, total to 10s
   curl -sf --connect-timeout 5 --max-time 10 "https://api.example.com/data"
   ```

3. **Use Retry with Timeout:**
   ```bash
   source scripts/lib/common.sh
   
   # Each attempt has 10s timeout, with exponential backoff between retries
   retry_with_backoff curl -sf --max-time 10 "https://api.example.com/data"
   ```

4. **Verify All curl Commands Have Timeout:**
   ```bash
   # Run timeout coverage test
   bash tests/test_timeout_coverage.sh
   
   # Output shows any curl commands missing --max-time
   ```

### Script Timeouts

**Symptoms:**
- Python script runs forever
- Infinite loop or deadlock
- No progress for extended period

**Solutions:**

1. **Use timeout Command:**
   ```bash
   # Kill script after 30 seconds
   timeout 30s python scripts/generate-card.py
   ```

2. **Add Timeouts in Python:**
   ```python
   import signal
   
   class TimeoutError(Exception):
       pass
   
   def timeout_handler(signum, frame):
       raise TimeoutError("Script execution timed out")
   
   # Set 30 second timeout
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(30)
   
   try:
       # Your code here
       generate_card()
   except TimeoutError:
       print("❌ ERROR: Script timed out", file=sys.stderr)
       sys.exit(1)
   finally:
       signal.alarm(0)  # Cancel alarm
   ```

---

## Missing Schema Validation

### Setting Up Schema Validation

**Why Validate:**
- Catch data format issues early
- Ensure consistency across workflows
- Document expected data structure
- Prevent downstream errors

**Creating JSON Schemas:**

1. **Create Schema Directory:**
   ```bash
   mkdir -p schemas
   ```

2. **Define Schema for Each Data Type:**

   **schemas/weather.schema.json:**
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "type": "object",
     "required": ["current", "daily"],
     "properties": {
       "current": {
         "type": "object",
         "required": ["temperature", "condition", "emoji"],
         "properties": {
           "temperature": {"type": "number"},
           "condition": {"type": "string"},
           "emoji": {"type": "string"}
         }
       },
       "daily": {
         "type": "array",
         "items": {
           "type": "object",
           "required": ["date", "temp_max", "temp_min"]
         }
       }
     }
   }
   ```

   **schemas/oura-metrics.schema.json:**
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "type": "object",
     "required": ["sleep_score", "readiness_score", "activity_score"],
     "properties": {
       "sleep_score": {"type": "integer", "minimum": 0, "maximum": 100},
       "readiness_score": {"type": "integer", "minimum": 0, "maximum": 100},
       "activity_score": {"type": "integer", "minimum": 0, "maximum": 100}
     }
   }
   ```

3. **Validate in Workflows:**

   **Using jq:**
   ```bash
   # Install jq with schema validation support
   sudo apt-get install -y jq
   
   # Note: jq doesn't have built-in schema validation
   # Use check-jsonschema instead
   pip install check-jsonschema
   
   check-jsonschema --schemafile schemas/weather.schema.json weather/weather.json
   ```

   **Using Python:**
   ```python
   import json
   import jsonschema
   
   def validate_against_schema(data_file, schema_file):
       """Validate JSON data against schema."""
       with open(schema_file) as f:
           schema = json.load(f)
       
       with open(data_file) as f:
           data = json.load(f)
       
       try:
           jsonschema.validate(data, schema)
           print(f"✅ {data_file} is valid")
           return True
       except jsonschema.ValidationError as e:
           print(f"❌ Validation error in {data_file}:", file=sys.stderr)
           print(f"   → {e.message}", file=sys.stderr)
           print(f"   → Path: {' -> '.join(str(p) for p in e.path)}", file=sys.stderr)
           return False
   
   # Usage
   validate_against_schema("weather/weather.json", "schemas/weather.schema.json")
   ```

4. **Add Validation to Workflows:**
   ```yaml
   - name: Validate data schema
     run: |
       pip install check-jsonschema
       check-jsonschema --schemafile schemas/oura-metrics.schema.json oura/metrics.json
   ```

### Handling Validation Failures

**When Validation Fails:**

1. **Check Error Message:**
   ```
   ❌ Validation error in oura/metrics.json:
      → 'sleep_score' is a required property
      → Path: 
   ```

2. **Fix Data Source:**
   - Update fetch script to include missing fields
   - Add default values for optional fields
   - Fix data transformation logic

3. **Update Schema if Needed:**
   - If API changed, update schema to match
   - Make fields optional if they're not always present:
   ```json
   {
     "properties": {
       "sleep_score": {"type": ["integer", "null"]}
     }
   }
   ```

---

## Diagnostic Commands

### Quick Health Check

```bash
# Check all external APIs
./scripts/health_check.sh

# Check specific API
./scripts/health_check.sh soundcloud
./scripts/health_check.sh weather
./scripts/health_check.sh oura
```

### Validate JSON Files

```bash
# Validate all JSON files
find . -name "*.json" -not -path "./node_modules/*" -exec sh -c 'echo "Checking {}"; jq empty {} || echo "Invalid: {}"' \;

# Validate specific file
jq empty weather/weather.json && echo "✅ Valid" || echo "❌ Invalid"
```

### Check Workflow Logs

```bash
# List recent workflow runs
gh run list --limit 10

# View logs for specific run
gh run view <run_id> --log

# View failed runs only
gh run list --status failure --limit 5
```

### Test Scripts Locally

```bash
# Run fetch scripts in development mode
export GITHUB_OWNER="your-username"
export GITHUB_TOKEN="your-token"

# Test weather fetch
./scripts/fetch-weather.sh > weather/weather.json

# Test card generation
python scripts/generate-weather-card.py
```

---

## Preventive Measures

### 1. Pre-Flight Checks

Add health checks before running main workflow:

```yaml
- name: Check API health
  run: |
    if ! ./scripts/health_check.sh soundcloud; then
      echo "⚠️ SoundCloud API is down, skipping workflow"
      exit 0  # Exit gracefully
    fi
```

### 2. Comprehensive Logging

```bash
# Log all API requests
log_api_call() {
  local url="$1"
  local response="$2"
  local status="$3"
  
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $status | $url" >> logs/api_calls.log
}
```

### 3. Monitoring

Set up monitoring workflow to detect failures:

```yaml
# .github/workflows/monitoring.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  check-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check workflow status
        run: |
          python scripts/generate-status-page.py
          
      - name: Create issue if failures detected
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '⚠️ Workflow Failures Detected',
              body: 'Multiple workflows have failed. Check the logs for details.'
            })
```

### 4. Fallback Mechanisms

Always provide fallbacks:

```python
# Try primary data source, fall back to cache
def get_data_with_fallback(primary_source, cache_file):
    try:
        data = fetch_from_api(primary_source)
        save_to_cache(data, cache_file)
        return data
    except Exception as e:
        print(f"⚠️ Primary source failed: {e}", file=sys.stderr)
        if os.path.exists(cache_file):
            print(f"   → Using cached data from {cache_file}", file=sys.stderr)
            return load_from_cache(cache_file)
        raise
```

---

## Getting Help

### Resources

1. **Repository Documentation:**
   - [Workflows Guide](workflows.md)
   - [API Timeout & Retry Guide](API_TIMEOUT_RETRY_GUIDE.md)
   - [Robustness Improvements](ROBUSTNESS_IMPROVEMENTS.md)
   - [Monitoring Guide](MONITORING.md)

2. **External Documentation:**
   - [GitHub Actions Documentation](https://docs.github.com/en/actions)
   - [curl Manual](https://curl.se/docs/manpage.html)
   - [jq Manual](https://stedolan.github.io/jq/manual/)

3. **API Documentation:**
   - [Oura API Docs](https://cloud.ouraring.com/docs)
   - [Open-Meteo API](https://open-meteo.com/en/docs)
   - [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)

### Reporting Issues

When reporting a workflow failure:

1. **Include:**
   - Workflow name and run ID
   - Error messages from logs
   - Recent changes to code or configuration
   - Steps to reproduce

2. **Provide Context:**
   - What were you trying to achieve?
   - What happened instead?
   - What have you tried already?

3. **Check First:**
   - Is the external API working? (use health check)
   - Are secrets configured correctly?
   - Did a recent commit break something?
   - Is this a known issue? (check open issues)

---

## Summary Checklist

When troubleshooting a workflow failure:

- [ ] Check workflow logs in GitHub Actions tab
- [ ] Run `./scripts/health_check.sh` to verify API availability
- [ ] Validate JSON files with `jq empty <file>.json`
- [ ] Verify secrets are configured (Settings → Secrets)
- [ ] Check for rate limiting (429 errors)
- [ ] Look for timeout issues (max-time settings)
- [ ] Verify all required fields exist in data
- [ ] Check for concurrency conflicts (multiple workflows running)
- [ ] Review recent code changes that might have caused the issue
- [ ] Test scripts locally to isolate the problem
- [ ] Check external API status pages
- [ ] Review schema validation errors if applicable

---

*For more detailed information on specific topics, refer to the linked documentation sections.*
