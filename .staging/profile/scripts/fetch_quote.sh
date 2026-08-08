#!/bin/bash
# Script to fetch a daily quote from various APIs with fallback support
# This script:
# 1. Attempts to fetch from ZenQuotes.io API (no API key required)
# 2. Falls back to Quotable.io API if ZenQuotes fails
# 3. Falls back to local curated quotes database if all APIs fail
# 4. Outputs normalized quote data as JSON

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
source "${SCRIPT_DIR}/lib/logging.sh"

OUTPUT_DIR="${OUTPUT_DIR:-quotes}"
LOG_DIR="${LOG_DIR:-logs/quotes}"
DATA_DIR="data/quotes"

# Ensure directories exist
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# Function to fetch quote from ZenQuotes.io
fetch_zenquotes() {
    log_info "Fetching quote from ZenQuotes.io..."
    
    local raw_response
    if ! raw_response=$(retry_api_call "ZenQuotes" curl -sf --max-time 10 "https://zenquotes.io/api/today" 2>&1); then
        log_warn "Failed to fetch from ZenQuotes.io"
        return 1
    fi
    
    # Save raw response for debugging
    echo "$raw_response" > "${LOG_DIR}/quote_raw.json"
    
    # Validate JSON
    if ! echo "$raw_response" | jq empty 2>/dev/null; then
        log_warn "Invalid JSON from ZenQuotes.io"
        return 1
    fi
    
    # ZenQuotes returns an array with one quote
    local quote_text author
    quote_text=$(echo "$raw_response" | jq -r '.[0].q // empty')
    author=$(echo "$raw_response" | jq -r '.[0].a // empty')
    
    if [ -z "$quote_text" ] || [ -z "$author" ]; then
        log_warn "Missing required fields from ZenQuotes.io"
        return 1
    fi
    
    # Normalize and output
    jq -n \
        --arg text "$quote_text" \
        --arg author "$author" \
        --arg source "zenquotes" \
        --arg fetched_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            text: $text,
            author: $author,
            source: $source,
            fetched_at: $fetched_at
        }'
    
    return 0
}

# Function to fetch quote from Quotable.io
fetch_quotable() {
    log_info "Fetching quote from Quotable.io..."
    
    local raw_response
    if ! raw_response=$(retry_api_call "Quotable" curl -sf --max-time 10 "https://api.quotable.io/random" 2>&1); then
        log_warn "Failed to fetch from Quotable.io"
        return 1
    fi
    
    # Save raw response for debugging
    echo "$raw_response" > "${LOG_DIR}/quote_raw.json"
    
    # Validate JSON
    if ! echo "$raw_response" | jq empty 2>/dev/null; then
        log_warn "Invalid JSON from Quotable.io"
        return 1
    fi
    
    # Extract fields
    local quote_text author category
    quote_text=$(echo "$raw_response" | jq -r '.content // empty')
    author=$(echo "$raw_response" | jq -r '.author // empty')
    category=$(echo "$raw_response" | jq -r '.tags[0] // "wisdom"')
    
    if [ -z "$quote_text" ] || [ -z "$author" ]; then
        log_warn "Missing required fields from Quotable.io"
        return 1
    fi
    
    # Normalize and output
    jq -n \
        --arg text "$quote_text" \
        --arg author "$author" \
        --arg category "$category" \
        --arg source "quotable" \
        --arg fetched_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            text: $text,
            author: $author,
            category: $category,
            source: $source,
            fetched_at: $fetched_at
        }'
    
    return 0
}

# Function to get a quote from local database
fetch_local_quote() {
    log_info "Using local quote database..." >&2
    
    local quotes_file="${DATA_DIR}/quotes.json"
    
    if [ ! -f "$quotes_file" ]; then
        log_error "Local quotes file not found: $quotes_file" >&2
        return 1
    fi
    
    # Validate JSON
    if ! jq empty "$quotes_file" 2>/dev/null; then
        log_error "Invalid JSON in local quotes file" >&2
        return 1
    fi
    
    # Get total number of quotes
    local total_quotes
    total_quotes=$(jq 'length' "$quotes_file")
    
    if [ "$total_quotes" -eq 0 ]; then
        log_error "No quotes in local database" >&2
        return 1
    fi
    
    # Use day of year to get a consistent "quote of the day"
    local day_of_year
    day_of_year=$(date +%j)
    local quote_index=$((day_of_year % total_quotes))
    
    log_info "Selecting quote ${quote_index} from ${total_quotes} local quotes" >&2
    
    # Extract the quote
    local quote_data
    quote_data=$(jq ".[$quote_index]" "$quotes_file")
    
    # Add metadata and normalize
    echo "$quote_data" | jq \
        --arg source "local" \
        --arg fetched_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '. + {
            source: $source,
            fetched_at: $fetched_at
        }'
    
    return 0
}

# Main execution
main() {
    log_info "Starting quote fetch process..." >&2
    
    local quote_data
    
    # Try ZenQuotes.io first
    if quote_data=$(fetch_zenquotes 2>&1); then
        log_info "✅ Successfully fetched quote from ZenQuotes.io" >&2
        echo "$quote_data"
        return 0
    fi
    
    log_warn "ZenQuotes.io failed, trying Quotable.io..." >&2
    
    # Try Quotable.io
    if quote_data=$(fetch_quotable 2>&1); then
        log_info "✅ Successfully fetched quote from Quotable.io" >&2
        echo "$quote_data"
        return 0
    fi
    
    log_warn "Quotable.io failed, using local quote database..." >&2
    
    # Fall back to local quotes
    if quote_data=$(fetch_local_quote); then
        log_info "✅ Successfully fetched quote from local database" >&2
        echo "$quote_data"
        return 0
    fi
    
    log_error "❌ All quote sources failed" >&2
    
    # Final fallback: provide a hardcoded quote
    log_warn "Using emergency fallback quote" >&2
    jq -n \
        --arg text "The only way to do great work is to love what you do." \
        --arg author "Steve Jobs" \
        --arg source "fallback" \
        --arg fetched_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            text: $text,
            author: $author,
            source: $source,
            fetched_at: $fetched_at
        }'
    
    return 0
}

# Run main
main "$@"
