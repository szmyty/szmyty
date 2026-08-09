#!/bin/bash
# Script to fetch the latest SoundCloud track data
# This script:
# 1. Extracts the client_id from SoundCloud's JavaScript assets
# 2. Validates the client_id with a lightweight API test
# 3. Falls back to cached client_id if extraction fails
# 4. Fetches the user's latest track metadata
# 5. Downloads the track artwork
# 6. Outputs track metadata as JSON

set -euo pipefail

SOUNDCLOUD_USER="${SOUNDCLOUD_USER:-playfunction}"
OUTPUT_DIR="${OUTPUT_DIR:-assets}"
CACHE_DIR="${CACHE_DIR:-${OUTPUT_DIR}/.cache}"
CLIENT_ID_CACHE_FILE="${CACHE_DIR}/soundcloud_client_id.txt"
FALLBACK_CACHE_FILE="${FALLBACK_CACHE_FILE:-soundcloud/last-success.json}"

# Source common utilities for retry logic
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/lib/common.sh" ]; then
    source "${SCRIPT_DIR}/lib/common.sh"
fi
if [ -f "${SCRIPT_DIR}/lib/logging.sh" ]; then
    source "${SCRIPT_DIR}/lib/logging.sh"
fi

# Function to validate a client_id with a lightweight API request
validate_client_id() {
    local client_id=$1
    echo "Validating client_id..." >&2
    
    # Use a lightweight /resolve request to validate the client_id
    local http_code
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        --max-time 10 \
        "https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/${SOUNDCLOUD_USER}&client_id=${client_id}" \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
        2>/dev/null) || http_code="000"
    
    if [ "$http_code" = "200" ]; then
        echo "Client_id validated successfully" >&2
        return 0
    else
        echo "Client_id validation failed (HTTP $http_code)" >&2
        return 1
    fi
}

# Function to save a valid client_id to cache
save_client_id_to_cache() {
    local client_id=$1
    mkdir -p "$CACHE_DIR"
    echo "$client_id" > "$CLIENT_ID_CACHE_FILE"
    echo "Saved client_id to cache" >&2
}

# Function to load client_id from cache
load_client_id_from_cache() {
    if [ -f "$CLIENT_ID_CACHE_FILE" ]; then
        local cached_id
        cached_id=$(tr -d '[:space:]' < "$CLIENT_ID_CACHE_FILE" 2>/dev/null)
        if [ -n "$cached_id" ]; then
            echo "$cached_id"
            return 0
        fi
    fi
    return 1
}

# Function to extract client_id from SoundCloud JavaScript assets
extract_client_id() {
    echo "Extracting SoundCloud client_id from assets..." >&2
    
    # Fetch the main page HTML
    local html
    html=$(curl -sf --max-time 10 "https://soundcloud.com/${SOUNDCLOUD_USER}" \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") || {
        echo "Warning: Failed to fetch SoundCloud profile page" >&2
        return 1
    }
    
    if [ -z "$html" ]; then
        echo "Warning: Empty response from SoundCloud" >&2
        return 1
    fi
    
    # Extract JS asset URLs - support multiple CDN patterns
    local js_urls
    js_urls=$(echo "$html" | grep -oE 'https://a-v2\.sndcdn\.com/assets/[^"'\'']+\.js' | head -15)
    
    # Fallback to alternative CDN pattern
    if [ -z "$js_urls" ]; then
        js_urls=$(echo "$html" | grep -oE 'https://[a-z0-9-]+\.sndcdn\.com/assets/[^"'\'']+\.js' | head -15)
    fi
    
    if [ -z "$js_urls" ]; then
        echo "Warning: No JavaScript assets found in SoundCloud page" >&2
        return 1
    fi
    
    # Search each JS file for client_id using multiple regex patterns
    # Note: The pattern ["'"'"'] uses bash quote escaping to match both " and ' characters:
    # ' ends the single quote, "'" adds a literal single quote, ' resumes single quoting
    for url in $js_urls; do
        local js_content
        js_content=$(curl -sf --max-time 10 "$url" \
            -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") || continue
        
        local client_id=""
        
        # Pattern 1: client_id="xxx" or client_id:'xxx'
        client_id=$(echo "$js_content" | grep -oE 'client_id[=:]["'"'"'][a-zA-Z0-9]{20,40}["'"'"']' | grep -oE '[a-zA-Z0-9]{20,40}' | head -1 || true)
        
        # Pattern 2: clientId:"xxx" or clientId='xxx' (camelCase variant)
        if [ -z "$client_id" ]; then
            client_id=$(echo "$js_content" | grep -oE 'clientId[=:]["'"'"'][a-zA-Z0-9]{20,40}["'"'"']' | grep -oE '[a-zA-Z0-9]{20,40}' | head -1 || true)
        fi
        
        # Pattern 3: "client_id":"xxx" (JSON-style)
        if [ -z "$client_id" ]; then
            client_id=$(echo "$js_content" | grep -oE '"client_id"\s*:\s*"[a-zA-Z0-9]{20,40}"' | grep -oE '[a-zA-Z0-9]{20,40}' | head -1 || true)
        fi
        
        # Pattern 4: {client_id:"xxx"} (object literal)
        if [ -z "$client_id" ]; then
            client_id=$(echo "$js_content" | grep -oE '\{client_id:"[a-zA-Z0-9]{20,40}"' | grep -oE '[a-zA-Z0-9]{20,40}' | head -1 || true)
        fi
        
        if [ -n "$client_id" ]; then
            echo "$client_id"
            return 0
        fi
    done
    
    echo "Warning: Failed to extract client_id from any JavaScript asset" >&2
    return 1
}

# Function to get a valid client_id (with extraction, validation, and fallback)
get_client_id() {
    echo "Fetching SoundCloud client_id..." >&2
    
    local client_id=""
    local extraction_failed=false
    
    # Step 1: Try to extract a fresh client_id
    client_id=$(extract_client_id) || extraction_failed=true
    
    # Step 2: If extraction succeeded, validate the client_id
    if [ "$extraction_failed" = "false" ] && [ -n "$client_id" ]; then
        if validate_client_id "$client_id"; then
            # Save valid client_id to cache for future fallback
            save_client_id_to_cache "$client_id"
            echo "$client_id"
            return 0
        else
            echo "Warning: Extracted client_id failed validation" >&2
        fi
    fi
    
    # Step 3: Fallback to cached client_id
    echo "Attempting to use cached client_id..." >&2
    local cached_id
    if cached_id=$(load_client_id_from_cache); then
        echo "Found cached client_id: ${cached_id:0:10}..." >&2
        if validate_client_id "$cached_id"; then
            echo "Cached client_id is valid, using it" >&2
            echo "$cached_id"
            return 0
        else
            echo "Warning: Cached client_id is no longer valid" >&2
        fi
    else
        echo "No cached client_id available" >&2
    fi
    
    # Step 4: All methods failed
    echo "Error: Failed to obtain a valid client_id" >&2
    return 1
}

# Function to get user ID from username
get_user_id() {
    local client_id=$1
    echo "Fetching user ID for ${SOUNDCLOUD_USER}..." >&2
    
    local user_data
    # Use retry_api_call with circuit breaker and rate limit detection
    if ! user_data=$(retry_api_call "SoundCloud API" curl -sf --max-time 10 "https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/${SOUNDCLOUD_USER}&client_id=${client_id}"); then
        echo "Error: Failed to resolve SoundCloud user after retries" >&2
        return 1
    fi
    
    # Validate JSON response
    if ! validate_api_response "$user_data" "id"; then
        echo "Error: Invalid user data from SoundCloud API" >&2
        return 1
    fi
    
    local user_id
    user_id=$(echo "$user_data" | jq -r '.id')
    
    if [ -z "$user_id" ] || [ "$user_id" = "null" ]; then
        echo "Error: Invalid user data received from SoundCloud API" >&2
        return 1
    fi
    
    echo "$user_id"
}

# Function to fetch latest track
fetch_latest_track() {
    local client_id=$1
    local user_id=$2
    echo "Fetching latest track..." >&2
    
    local tracks
    # Use retry_api_call with circuit breaker and rate limit detection
    if ! tracks=$(retry_api_call "SoundCloud API" curl -sf --max-time 10 "https://api-v2.soundcloud.com/users/${user_id}/tracks?representation=&client_id=${client_id}&limit=1&offset=0"); then
        echo "Error: Failed to fetch tracks from SoundCloud API after retries" >&2
        return 1
    fi
    
    # Validate JSON response
    if ! validate_api_response "$tracks" "collection"; then
        echo "Error: Invalid tracks data from SoundCloud API" >&2
        return 1
    fi
    
    local track
    track=$(echo "$tracks" | jq '.collection[0]')
    
    if [ -z "$track" ] || [ "$track" = "null" ]; then
        echo "Error: No tracks found for user" >&2
        return 1
    fi
    
    echo "$track"
}

# Function to download artwork
download_artwork() {
    local artwork_url=$1
    local output_path=$2
    
    echo "Downloading artwork..." >&2
    
    # Replace size placeholder with larger size
    # Bash parameter expansion safely returns original string if pattern not found
    local large_url
    large_url="${artwork_url/-large./-t500x500.}"
    
    curl -s --max-time 10 -o "$output_path" "$large_url" || curl -s --max-time 10 -o "$output_path" "$artwork_url"
    echo "Artwork saved to $output_path" >&2
}

# Function to save successful track data to fallback cache
save_fallback_cache() {
    local metadata=$1
    local fallback_dir
    fallback_dir=$(dirname "$FALLBACK_CACHE_FILE")
    
    mkdir -p "$fallback_dir"
    echo "$metadata" > "$FALLBACK_CACHE_FILE"
    echo "Saved fallback cache to ${FALLBACK_CACHE_FILE}" >&2
}

# Function to load track data from fallback cache
load_fallback_cache() {
    if [ ! -f "$FALLBACK_CACHE_FILE" ]; then
        echo "No fallback cache available" >&2
        return 1
    fi
    
    # Validate the cached JSON
    if ! jq empty "$FALLBACK_CACHE_FILE" 2>/dev/null; then
        echo "Warning: Invalid JSON in fallback cache" >&2
        return 1
    fi
    
    echo "Using fallback cache from ${FALLBACK_CACHE_FILE}" >&2
    cat "$FALLBACK_CACHE_FILE"
    return 0
}

# Main execution
main() {
    # Initialize logging
    init_logging "soundcloud"
    log_workflow_start "SoundCloud Card - Fetch Data"
    
    local metadata
    
    # Try to fetch fresh data
    log_info "Fetching fresh SoundCloud data..."
    if ! metadata=$(fetch_fresh_data); then
        log_warn "Failed to fetch fresh SoundCloud data, attempting fallback..."
        
        # Try to load from fallback cache
        if metadata=$(load_fallback_cache); then
            log_info "Using fallback cache successfully"
            log_workflow_end "SoundCloud Card - Fetch Data" 0
            echo "$metadata"
            return 0
        else
            log_error "No fallback cache available and fresh fetch failed"
            log_workflow_end "SoundCloud Card - Fetch Data" 1
            return 1
        fi
    fi
    
    log_info "Successfully fetched fresh SoundCloud data"
    
    # Save successful fetch to fallback cache
    save_fallback_cache "$metadata"
    
    # Output metadata
    log_workflow_end "SoundCloud Card - Fetch Data" 0
    echo "$metadata"
}

# Function to fetch fresh track data
fetch_fresh_data() {
    # Get client_id
    local client_id
    log_info "Obtaining SoundCloud client_id..."
    client_id=$(get_client_id) || return 1
    log_info "Got client_id: ${client_id:0:10}..."
    
    # Get user ID
    local user_id
    log_info "Resolving user ID for ${SOUNDCLOUD_USER}..."
    user_id=$(get_user_id "$client_id") || return 1
    log_info "Got user_id: $user_id"
    
    # Fetch latest track
    local track_data
    log_info "Fetching latest track for user..."
    track_data=$(fetch_latest_track "$client_id" "$user_id") || return 1
    
    # Extract track info
    local title artwork_url permalink_url genre duration playback_count created_at user_username
    title=$(echo "$track_data" | jq -r '.title')
    artwork_url=$(echo "$track_data" | jq -r '.artwork_url // .user.avatar_url')
    permalink_url=$(echo "$track_data" | jq -r '.permalink_url')
    genre=$(echo "$track_data" | jq -r '.genre // "Electronic"')
    duration=$(echo "$track_data" | jq -r '.duration')
    playback_count=$(echo "$track_data" | jq -r '.playback_count // 0')
    created_at=$(echo "$track_data" | jq -r '.created_at')
    user_username=$(echo "$track_data" | jq -r '.user.username')
    
    log_info "Track: ${title} by ${user_username}"
    log_info "Genre: ${genre}, Plays: ${playback_count}"
    
    # Download artwork (with retry)
    mkdir -p "$OUTPUT_DIR"
    log_info "Downloading track artwork..."
    if ! retry_with_backoff download_artwork "$artwork_url" "${OUTPUT_DIR}/soundcloud-artwork.jpg"; then
        log_warn "Failed to download artwork after retries, card may use stale artwork"
        # Continue anyway - the card generator can handle missing artwork
    else
        log_info "Artwork downloaded successfully"
    fi
    
    # Get current UTC time for update timestamp
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Output track metadata as JSON using jq for proper escaping
    jq -n \
        --arg title "$title" \
        --arg artist "$user_username" \
        --arg artwork_url "$artwork_url" \
        --arg permalink_url "$permalink_url" \
        --arg genre "$genre" \
        --argjson duration_ms "$duration" \
        --argjson playback_count "$playback_count" \
        --arg created_at "$created_at" \
        --arg updated_at "$updated_at" \
        '{
            title: $title,
            artist: $artist,
            artwork_url: $artwork_url,
            permalink_url: $permalink_url,
            genre: $genre,
            duration_ms: $duration_ms,
            playback_count: $playback_count,
            created_at: $created_at,
            updated_at: $updated_at
        }'
}

main "$@"
