#!/bin/bash
# Script to fetch ALL Oura Ring health metrics from Oura Cloud API v2
# This script:
# 1. Authenticates with Oura API using OURA_PAT secret
# 2. Fetches personal_info (mandatory)
# 3. Fetches daily sleep, readiness, activity metrics with ALL fields
# 4. Fetches heart rate time series data
# 5. Outputs combined health snapshot as JSON
# 6. Creates a unified health_snapshot.json

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/lib/common.sh" ]; then
    source "${SCRIPT_DIR}/lib/common.sh"
fi
if [ -f "${SCRIPT_DIR}/lib/logging.sh" ]; then
    source "${SCRIPT_DIR}/lib/logging.sh"
fi

# Initialize logging early
init_logging "oura"
log_workflow_start "Oura Health - Fetch Data"

OURA_PAT="${OURA_PAT:-}"
OUTPUT_DIR="${OUTPUT_DIR:-oura}"

# Validate that we have the Oura Personal Access Token
if [ -z "$OURA_PAT" ]; then
    log_error "OURA_PAT environment variable is not set"
    log_workflow_end "Oura Health - Fetch Data" 1
    echo "Error: OURA_PAT environment variable is not set" >&2
    exit 1
fi

# Calculate date range (last 7 days to ensure we get most recent data)
END_DATE=$(date -u +"%Y-%m-%d")
START_DATE=$(date -u -d "7 days ago" +"%Y-%m-%d" 2>/dev/null || date -u -v-7d +"%Y-%m-%d")

# Logging: Show date range being used
log_info "Date range: ${START_DATE} to ${END_DATE}"
echo "Start date: $START_DATE" >&2
echo "End date: $END_DATE" >&2

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to make Oura API request with retry logic, rate limit detection, and circuit breaker
oura_api_request() {
    local endpoint=$1
    local params="${2:-}"
    
    local url="https://api.ouraring.com/v2/usercollection/${endpoint}"
    if [ -n "$params" ]; then
        url="${url}?${params}"
    fi
    
    echo "Fetching from: ${url}" >&2
    
    local response
    # Use retry_api_call with circuit breaker and rate limit detection
    if ! response=$(retry_api_call "Oura API" curl -sf --max-time 10 "$url" \
        -H "Authorization: Bearer ${OURA_PAT}" \
        -H "Content-Type: application/json" \
        -H "User-Agent: GitHub-Profile-Oura-Card/1.0"); then
        echo "Error: Failed to fetch from Oura API endpoint after retries: ${endpoint}" >&2
        return 1
    fi
    
    # Validate JSON response
    if ! validate_api_response "$response"; then
        echo "Error: Invalid JSON from Oura API endpoint: ${endpoint}" >&2
        echo "$response" > "${OUTPUT_DIR}/debug_invalid_response_${endpoint}.txt"
        return 1
    fi
    
    echo "$response"
}

# Fetch personal info (mandatory)
fetch_personal_info() {
    echo "Fetching personal info..." >&2
    local response
    response=$(oura_api_request "personal_info") || {
        echo "Warning: Could not fetch personal info" >&2
        echo "{}"
        return 0
    }
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_personal_info.json"
    echo "Personal info JSON saved to raw_personal_info.json" >&2
    
    echo "$response"
}

# Fetch daily sleep data with ALL available fields
fetch_daily_sleep() {
    echo "Fetching daily sleep data..." >&2
    local response
    response=$(oura_api_request "daily_sleep" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_sleep.json"
    echo "Sleep JSON saved to raw_sleep.json" >&2
    
    # Check if data array is empty (use .data NOT .items)
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_sleep" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry with ALL available fields
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily readiness data with ALL available fields
fetch_daily_readiness() {
    echo "Fetching daily readiness data..." >&2
    local response
    response=$(oura_api_request "daily_readiness" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_readiness.json"
    echo "Readiness JSON saved to raw_readiness.json" >&2
    
    # Check if data array is empty (use .data NOT .items)
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_readiness" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry with ALL available fields
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily activity data with ALL available fields
fetch_daily_activity() {
    echo "Fetching daily activity data..." >&2
    local response
    response=$(oura_api_request "daily_activity" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_activity.json"
    echo "Activity JSON saved to raw_activity.json" >&2
    
    # Check if data array is empty (use .data NOT .items)
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_activity" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry with ALL available fields
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch heart rate time series data (use heart_rate endpoint correctly)
fetch_heart_rate() {
    echo "Fetching heart rate data..." >&2
    local response
    # Correct endpoint is "heart_rate" (with underscore)
    response=$(oura_api_request "heart_rate" "start_datetime=${START_DATE}T00:00:00&end_datetime=${END_DATE}T23:59:59") || {
        echo "Warning: Could not fetch heart rate data, continuing without it" >&2
        echo "{}"
        return 0
    }
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_heart_rate.json"
    echo "Heart rate JSON saved to raw_heart_rate.json" >&2
    
    # Check if data array is empty (use .data NOT .items)
    local item_count
    item_count=$(echo "$response" | jq '.data | length' 2>/dev/null || echo "0")
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for heart_rate" >&2
        echo '{"data":[],"latest_bpm":null,"avg_bpm":null,"resting_bpm":null}'
        return 0
    fi
    
    # Process heart rate data with separate calculations for clarity:
    # - latest_bpm: BPM from the most recent heart rate reading
    # - avg_bpm: Average BPM across all readings
    # - resting_bpm: Average BPM from readings where source is "rest"
    # - trend_values: Last 24 BPM values for sparkline visualization
    echo "$response" | jq '
        # Extract data array with fallback
        .data as $data |
        
        # Calculate latest BPM from last reading
        (if ($data | length) > 0 then ($data | last | .bpm) else null end) as $latest |
        
        # Calculate average BPM across all readings
        (if ($data | length) > 0 then (($data | map(.bpm) | add) / ($data | length) | floor) else null end) as $avg |
        
        # Calculate resting BPM from readings with source "rest"
        (if ($data | length) > 0 then
            ($data | map(select(.source == "rest"))) as $rest_data |
            if ($rest_data | length) > 0 then
                (($rest_data | map(.bpm) | add) / ($rest_data | length) | floor)
            else null end
        else null end) as $resting |
        
        # Get last 24 BPM values for trend visualization
        (if ($data | length) > 0 then ($data | map(.bpm) | .[-24:]) else [] end) as $trend |
        
        # Build output object
        {
            data: ($data // []),
            latest_bpm: $latest,
            avg_bpm: $avg,
            resting_bpm: $resting,
            trend_values: $trend
        }
    '
}

# Main execution
main() {
    echo "Starting Oura data fetch..." >&2
    echo "Date range: ${START_DATE} to ${END_DATE}" >&2
    
    # Perform health check before making API calls
    log_info "Performing Oura API health check..."
    if ! health_check_api "https://api.ouraring.com/v2/usercollection/personal_info" "Oura API" "Bearer ${OURA_PAT}"; then
        log_warn "Oura API health check failed, but continuing anyway..."
        # Don't exit - the retry logic will handle failures
    fi
    
    # Fetch all data types including personal info
    local personal_info_data sleep_data readiness_data activity_data hr_data
    
    personal_info_data=$(fetch_personal_info) || personal_info_data="{}"
    sleep_data=$(fetch_daily_sleep) || sleep_data="{}"
    readiness_data=$(fetch_daily_readiness) || readiness_data="{}"
    activity_data=$(fetch_daily_activity) || activity_data="{}"
    hr_data=$(fetch_heart_rate) || hr_data="{}"
    
    # Ensure all data variables contain valid JSON (default to empty object)
    if [ -z "$personal_info_data" ] || ! echo "$personal_info_data" | jq empty 2>/dev/null; then
        echo "Warning: personal_info_data is invalid, defaulting to empty object" >&2
        personal_info_data="{}"
    fi
    if [ -z "$sleep_data" ] || ! echo "$sleep_data" | jq empty 2>/dev/null; then
        echo "Warning: sleep_data is invalid, defaulting to empty object" >&2
        sleep_data="{}"
    fi
    if [ -z "$readiness_data" ] || ! echo "$readiness_data" | jq empty 2>/dev/null; then
        echo "Warning: readiness_data is invalid, defaulting to empty object" >&2
        readiness_data="{}"
    fi
    if [ -z "$activity_data" ] || ! echo "$activity_data" | jq empty 2>/dev/null; then
        echo "Warning: activity_data is invalid, defaulting to empty object" >&2
        activity_data="{}"
    fi
    if [ -z "$hr_data" ] || ! echo "$hr_data" | jq empty 2>/dev/null; then
        echo "Warning: hr_data is invalid, defaulting to empty object" >&2
        hr_data="{}"
    fi
    
    # Log what data was received
    echo "Personal info received: $(echo "$personal_info_data" | jq -c '.')" >&2
    echo "Sleep data received: $(echo "$sleep_data" | jq -c '.')" >&2
    echo "Readiness data received: $(echo "$readiness_data" | jq -c '.')" >&2
    echo "Activity data received: $(echo "$activity_data" | jq -c '.')" >&2
    echo "Heart rate data received: $(echo "$hr_data" | jq -c '.')" >&2
    
    # Check if we got any meaningful data (don't fail if some categories are empty)
    if [ "$sleep_data" = "{}" ] && [ "$readiness_data" = "{}" ] && [ "$activity_data" = "{}" ]; then
        echo "Warning: No data returned from any Oura API endpoint. Check if your token is valid and you have data available." >&2
        # Don't exit, continue with empty data to allow workflow to complete
    fi
    
    # Extract key metrics with null-safe defaults
    local sleep_score readiness_score activity_score hrv resting_hr temp_deviation
    
    sleep_score=$(echo "$sleep_data" | jq '.score // null')
    readiness_score=$(echo "$readiness_data" | jq '.score // null')
    activity_score=$(echo "$activity_data" | jq '.score // null')
    
    # HRV from readiness contributors
    hrv=$(echo "$readiness_data" | jq '.contributors.hrv_balance // null')
    
    # Resting HR from readiness
    resting_hr=$(echo "$readiness_data" | jq '.contributors.resting_heart_rate // null')
    
    # Temperature deviation from readiness
    temp_deviation=$(echo "$readiness_data" | jq '.contributors.body_temperature // null')
    
    # Get current UTC time for update timestamp in ISO 8601 format
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Output combined JSON - always include all categories
    jq -n \
        --argjson sleep_score "$sleep_score" \
        --argjson readiness_score "$readiness_score" \
        --argjson activity_score "$activity_score" \
        --argjson hrv "$hrv" \
        --argjson resting_hr "$resting_hr" \
        --argjson temp_deviation "$temp_deviation" \
        --argjson personal_info "$personal_info_data" \
        --argjson sleep "$sleep_data" \
        --argjson readiness "$readiness_data" \
        --argjson activity "$activity_data" \
        --argjson heart_rate "$hr_data" \
        --arg updated_at "$updated_at" \
        '{
            sleep_score: $sleep_score,
            readiness_score: $readiness_score,
            activity_score: $activity_score,
            hrv: $hrv,
            resting_hr: $resting_hr,
            temp_deviation: $temp_deviation,
            personal_info: $personal_info,
            sleep: $sleep,
            readiness: $readiness,
            activity: $activity,
            heart_rate: $heart_rate,
            updated_at: $updated_at
        }'
    
    # Log completion
    log_info "Oura metrics fetched successfully"
    log_info "Scores - Sleep: ${sleep_score}, Readiness: ${readiness_score}, Activity: ${activity_score}"
    log_workflow_end "Oura Health - Fetch Data" 0
}

main "$@"
