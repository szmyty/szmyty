#!/bin/bash
# Script to fetch location data and static map from Mapbox
# This script:
# 1. Gets the GitHub user's location
# 2. Converts location to coordinates via Nominatim
# 3. Determines day/night based on sunrise/sunset times
# 4. Downloads a static map from Mapbox with appropriate theme
# 5. Outputs location data as JSON

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
source "${SCRIPT_DIR}/lib/logging.sh"

GITHUB_OWNER="${GITHUB_OWNER:-szmyty}"
OUTPUT_DIR="${OUTPUT_DIR:-location}"
DEBUG_DIR="${OUTPUT_DIR}"
MAPBOX_TOKEN="${MAPBOX_TOKEN:-}"

# Function to save diagnostic information
save_diagnostic() {
    local filename=$1
    local content=$2
    
    mkdir -p "$DEBUG_DIR"
    echo "$content" > "${DEBUG_DIR}/${filename}"
    echo "Diagnostic info saved to ${DEBUG_DIR}/${filename}" >&2
}

# Function to determine if it's daytime based on sunrise/sunset
# Returns "light" for day, "dark" for night
determine_time_of_day() {
    local lat=$1
    local lon=$2
    
    echo "Determining time of day for coordinates ${lat}, ${lon}..." >&2
    
    # Fetch sunrise/sunset data from Open-Meteo
    local meteo_url="https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=sunrise,sunset&timezone=auto&forecast_days=1"
    local meteo_data
    
    # Use retry_with_backoff with better error handling
    if ! meteo_data=$(retry_with_backoff curl -sf --max-time 10 "$meteo_url"); then
        echo "Warning: Failed to fetch sunrise/sunset data after retries, defaulting to light mode" >&2
        echo "light"
        return 0
    fi
    
    # Save diagnostic info (note: retry_with_backoff abstracts HTTP details)
    save_diagnostic "debug_meteo_response.txt" "URL: $meteo_url
Status: Success (via retry_with_backoff)
Response:
$meteo_data"
    
    # Validate JSON
    if ! echo "$meteo_data" | jq empty 2>/dev/null; then
        echo "Warning: Invalid JSON from Open-Meteo, defaulting to light mode" >&2
        echo "light"
        return 0
    fi
    
    # Extract sunrise and sunset times
    local sunrise sunset
    sunrise=$(echo "$meteo_data" | jq -r '.daily.sunrise[0] // empty')
    sunset=$(echo "$meteo_data" | jq -r '.daily.sunset[0] // empty')
    
    if [ -z "$sunrise" ] || [ -z "$sunset" ] || [ "$sunrise" = "null" ] || [ "$sunset" = "null" ]; then
        echo "Warning: Could not parse sunrise/sunset times, defaulting to light mode" >&2
        echo "light"
        return 0
    fi
    
    # Get current time in the same timezone (ISO 8601 format)
    # Open-Meteo returns times like "2025-12-03T06:30"
    # We need to compare current time in local timezone
    local current_time
    current_time=$(date -u +"%Y-%m-%dT%H:%M")
    
    # Convert times to seconds since epoch for comparison
    local sunrise_epoch sunset_epoch current_epoch
    sunrise_epoch=$(date -d "$sunrise" +%s 2>/dev/null || echo "0")
    sunset_epoch=$(date -d "$sunset" +%s 2>/dev/null || echo "0")
    current_epoch=$(date -u +%s)
    
    if [ "$sunrise_epoch" -eq 0 ] || [ "$sunset_epoch" -eq 0 ]; then
        echo "Warning: Failed to parse times, defaulting to light mode" >&2
        echo "light"
        return 0
    fi
    
    echo "Sunrise: $sunrise (epoch: $sunrise_epoch)" >&2
    echo "Sunset: $sunset (epoch: $sunset_epoch)" >&2
    echo "Current: $current_time (epoch: $current_epoch)" >&2
    
    # Determine if it's day or night
    if [ "$current_epoch" -lt "$sunrise_epoch" ] || [ "$current_epoch" -gt "$sunset_epoch" ]; then
        echo "🌙 Night detected - using dark theme" >&2
        echo "dark"
    else
        echo "☀️ Day detected - using light theme" >&2
        echo "light"
    fi
}

# Function to generate fallback map image for API errors
generate_fallback_map() {
    local output_path=$1
    local lat=$2
    local lon=$3
    
    echo "Generating fallback map image..." >&2
    
    # Use Python script to generate fallback PNG
    if python3 "${SCRIPT_DIR}/generate-fallback-map.py" "$output_path" "$lat" "$lon"; then
        echo "✅ Fallback map generated: ${output_path}" >&2
        return 0
    else
        echo "❌ Failed to generate fallback map" >&2
        return 1
    fi
}

# Function to download static map from Mapbox
download_static_map() {
    local lat=$1
    local lon=$2
    local output_path=$3
    
    echo "Downloading static map from Mapbox centered on ${lat}, ${lon}..." >&2
    
    # Check if MAPBOX_TOKEN is set
    if [ -z "$MAPBOX_TOKEN" ]; then
        echo "❌ FAILURE: MAPBOX_TOKEN is not set" >&2
        echo "   → Set the MAPBOX_TOKEN environment variable or secret" >&2
        echo "   → Get your token from https://account.mapbox.com/access-tokens/" >&2
        
        # Generate fallback map image
        generate_fallback_map "$output_path" "$lat" "$lon"
        return 1
    fi
    
    # Perform health check for Mapbox API
    if ! health_check_api "https://api.mapbox.com/v1" "Mapbox API"; then
        log_warn "Mapbox API health check failed, but continuing anyway..."
    fi
    
    # Determine if it's day or night
    local theme
    theme=$(determine_time_of_day "$lat" "$lon")
    
    # Choose Mapbox style based on time of day
    local mapbox_style
    if [ "$theme" = "dark" ]; then
        mapbox_style="mapbox/dark-v11"
    else
        mapbox_style="mapbox/light-v11"
    fi
    
    echo "Using Mapbox style: ${mapbox_style}" >&2
    
    # Mapbox expects lon,lat order (opposite of Nominatim's lat,lon)
    local mapbox_coords="${lon},${lat}"
    local zoom=11
    local bearing=0
    local width=600
    local height=400
    
    # Mapbox Static Images API
    local map_url="https://api.mapbox.com/styles/v1/${mapbox_style}/static/${mapbox_coords},${zoom},${bearing}/${width}x${height}?access_token=${MAPBOX_TOKEN}"
    
    # Capture HTTP response with headers
    local http_code response_headers temp_file
    temp_file=$(mktemp)
    response_headers=$(mktemp)
    
    http_code=$(curl -w "%{http_code}" --max-time 10 -o "$temp_file" -D "$response_headers" -s "$map_url")
    local curl_exit=$?
    
    # Save diagnostic information (without exposing full token)
    local masked_token="${MAPBOX_TOKEN:0:8}...${MAPBOX_TOKEN: -4}"
    save_diagnostic "debug_map_response.txt" "URL: https://api.mapbox.com/styles/v1/${mapbox_style}/static/${mapbox_coords},${zoom},${bearing}/${width}x${height}?access_token=${masked_token}
HTTP Code: $http_code
Curl Exit Code: $curl_exit
Style: $mapbox_style
Theme: $theme (day/night)
Coordinates: lat=${lat}, lon=${lon}
Mapbox Format: ${mapbox_coords}
Response Headers:
$(cat "$response_headers")
File Size: $(stat -f%z "$temp_file" 2>/dev/null || stat -c%s "$temp_file" 2>/dev/null || echo "unknown")"
    
    save_diagnostic "debug_map_headers.txt" "$(cat "$response_headers")"
    
    # Check curl exit code
    if [ $curl_exit -ne 0 ]; then
        echo "❌ FAILURE: Map retrieval failed (Curl exit code: ${curl_exit})" >&2
        echo "   → This usually indicates a network error or DNS resolution failure" >&2
        echo "   → Check your network connection and try again" >&2
        rm -f "$temp_file" "$response_headers"
        
        # Generate fallback map image
        generate_fallback_map "$output_path" "$lat" "$lon"
        return 1
    fi
    
    # Check HTTP status code
    if [ "$http_code" -ge 400 ]; then
        echo "❌ FAILURE: Mapbox API request failed (HTTP Code: ${http_code})" >&2
        case "$http_code" in
            401)
                echo "   → Invalid or expired Mapbox token" >&2
                echo "   → Check your MAPBOX_TOKEN secret" >&2
                echo "   → Get a new token from https://account.mapbox.com/access-tokens/" >&2
                ;;
            403)
                echo "   → Access forbidden - token may lack required permissions" >&2
                echo "   → Ensure your token has 'styles:tiles' scope" >&2
                ;;
            404)
                echo "   → Mapbox style or endpoint not found" >&2
                echo "   → The style '${mapbox_style}' may not be available" >&2
                ;;
            429)
                echo "   → Rate limit exceeded" >&2
                echo "   → Mapbox has usage limits based on your plan" >&2
                echo "   → Consider upgrading or reducing request frequency" >&2
                ;;
            500|502|503|504)
                echo "   → Mapbox service is experiencing issues" >&2
                echo "   → Try again later" >&2
                ;;
            *)
                echo "   → Unexpected HTTP error" >&2
                echo "   → Check debug_map_response.txt for details" >&2
                ;;
        esac
        
        # Try to parse error message from response
        if command -v jq >/dev/null 2>&1; then
            local error_msg
            error_msg=$(jq -r '.message // empty' < "$temp_file" 2>/dev/null)
            if [ -n "$error_msg" ]; then
                echo "   → Mapbox error: $error_msg" >&2
            fi
        fi
        
        rm -f "$temp_file" "$response_headers"
        
        # Generate fallback map image
        generate_fallback_map "$output_path" "$lat" "$lon"
        return 1
    fi
    
    # Verify the downloaded file is not empty
    if [ ! -s "$temp_file" ]; then
        echo "❌ FAILURE: Downloaded map file is empty" >&2
        echo "   → Mapbox returned an empty response" >&2
        echo "   → This may indicate rate limiting, service issues, or invalid parameters" >&2
        rm -f "$temp_file" "$response_headers"
        
        # Generate fallback map image
        generate_fallback_map "$output_path" "$lat" "$lon"
        return 1
    fi
    
    # Verify the file is a valid image (PNG)
    if ! file "$temp_file" | grep -q "PNG image\|JPEG image"; then
        echo "❌ FAILURE: Downloaded file is not a valid image" >&2
        echo "   → Mapbox may have returned an error page or invalid data" >&2
        echo "   → File type: $(file "$temp_file")" >&2
        rm -f "$temp_file" "$response_headers"
        
        # Generate fallback map image
        generate_fallback_map "$output_path" "$lat" "$lon"
        return 1
    fi
    
    # Move temp file to final location
    mv "$temp_file" "$output_path"
    rm -f "$response_headers"
    
    echo "✅ Static map saved to ${output_path}" >&2
    echo "   → Style: ${mapbox_style}" >&2
    echo "   → Theme: ${theme}" >&2
}

# Main execution
main() {
    # Initialize logging
    init_logging "location"
    log_workflow_start "Location Card - Fetch Data"
    
    # Get GitHub location
    local location
    log_info "Fetching GitHub location..."
    location=$(get_github_location) || {
        log_error "Skipping location card generation: No location found"
        log_workflow_end "Location Card - Fetch Data" 1
        exit 1
    }
    log_info "GitHub location: ${location}"
    
    # Get coordinates
    local coord_data
    log_info "Converting location to coordinates..."
    coord_data=$(get_coordinates "$location") || {
        log_error "Skipping location card generation: Could not get coordinates"
        log_workflow_end "Location Card - Fetch Data" 1
        exit 1
    }
    
    local lat lon display_name
    lat=$(echo "$coord_data" | jq -r '.lat')
    lon=$(echo "$coord_data" | jq -r '.lon')
    display_name=$(echo "$coord_data" | jq -r '.display_name')
    log_info "Coordinates: lat=${lat}, lon=${lon}"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log_info "Output directory: ${OUTPUT_DIR}"
    
    # Download static map (with fallback handling)
    local map_status=0
    log_info "Downloading static map..."
    download_static_map "$lat" "$lon" "${OUTPUT_DIR}/location-map.png" || map_status=$?
    
    # Check if we have a map file (either from Mapbox or fallback)
    if [ ! -f "${OUTPUT_DIR}/location-map.png" ]; then
        log_error "Could not download map and fallback generation failed"
        log_workflow_end "Location Card - Fetch Data" 1
        exit 1
    fi
    
    # Log if we're using fallback
    if [ $map_status -ne 0 ]; then
        log_warn "Using fallback map image (Mapbox unavailable)"
    else
        log_info "Static map downloaded successfully"
    fi
    
    # Get current UTC time for update timestamp in ISO 8601 format
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    log_info "Generating location JSON output..."
    
    # Output combined JSON
    local json_output
    json_output=$(jq -n \
        --arg location "$location" \
        --arg display_name "$display_name" \
        --arg lat "$lat" \
        --arg lon "$lon" \
        --arg map_path "${OUTPUT_DIR}/location-map.png" \
        --arg updated_at "$updated_at" \
        '{
            location: $location,
            display_name: $display_name,
            coordinates: {lat: ($lat | tonumber), lon: ($lon | tonumber)},
            map_path: $map_path,
            updated_at: $updated_at
        }')
    
    log_info "Location data generated successfully"
    log_workflow_end "Location Card - Fetch Data" 0
    
    echo "$json_output"
}

main "$@"
