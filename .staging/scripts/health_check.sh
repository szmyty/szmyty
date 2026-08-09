#!/bin/bash
# Script to perform health checks on external APIs
# This script tests API availability before running full workflows

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check SoundCloud API
check_soundcloud() {
    echo "Checking SoundCloud API..." >&2
    
    # Try to access SoundCloud homepage
    local http_code
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        "https://soundcloud.com" \
        -H "User-Agent: Mozilla/5.0" \
        --max-time 10 \
        2>/dev/null) || http_code="000"
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ SoundCloud: Available${NC}" >&2
        return 0
    else
        echo -e "${RED}✗ SoundCloud: Unavailable (HTTP $http_code)${NC}" >&2
        return 1
    fi
}

# Function to check Open-Meteo API
check_open_meteo() {
    echo "Checking Open-Meteo API..." >&2
    
    # Test with a simple forecast request
    local http_code
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        "https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current_weather=true" \
        --max-time 10 \
        2>/dev/null) || http_code="000"
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Open-Meteo: Available${NC}" >&2
        return 0
    else
        echo -e "${RED}✗ Open-Meteo: Unavailable (HTTP $http_code)${NC}" >&2
        return 1
    fi
}

# Function to check Nominatim API
check_nominatim() {
    echo "Checking Nominatim API..." >&2
    
    # Test with a simple search request
    local http_code
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        "https://nominatim.openstreetmap.org/search?q=London&format=json&limit=1" \
        -H "User-Agent: GitHub-Profile-Health-Check/1.0" \
        --max-time 10 \
        2>/dev/null) || http_code="000"
    
    # Add delay to respect rate limits
    sleep 1
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Nominatim: Available${NC}" >&2
        return 0
    else
        echo -e "${RED}✗ Nominatim: Unavailable (HTTP $http_code)${NC}" >&2
        return 1
    fi
}

# Function to check Oura API
check_oura() {
    echo "Checking Oura API..." >&2
    
    # Check if OURA_PAT is set
    if [ -z "${OURA_PAT:-}" ]; then
        echo -e "${YELLOW}⊘ Oura: Skipped (no OURA_PAT)${NC}" >&2
        return 0  # Not a failure, just skipped
    fi
    
    # Test the API with a simple request
    local http_code
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        "https://api.ouraring.com/v2/usercollection/personal_info" \
        -H "Authorization: Bearer ${OURA_PAT}" \
        --max-time 10 \
        2>/dev/null) || http_code="000"
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Oura: Available${NC}" >&2
        return 0
    else
        echo -e "${RED}✗ Oura: Unavailable (HTTP $http_code)${NC}" >&2
        return 1
    fi
}

# Main execution
main() {
    local all_healthy=0
    local checks_run=0
    local checks_passed=0
    
    # Parse command line arguments
    local check_all=true
    local check_soundcloud=false
    local check_weather=false
    local check_location=false
    local check_oura_api=false
    
    # If specific APIs are requested, only check those
    if [ $# -gt 0 ]; then
        check_all=false
        for arg in "$@"; do
            case "$arg" in
                soundcloud)
                    check_soundcloud=true
                    ;;
                weather|open-meteo)
                    check_weather=true
                    ;;
                location|nominatim)
                    check_location=true
                    ;;
                oura)
                    check_oura_api=true
                    ;;
                all)
                    check_all=true
                    ;;
                *)
                    echo "Unknown API: $arg" >&2
                    echo "Usage: $0 [soundcloud|weather|location|oura|all]" >&2
                    exit 1
                    ;;
            esac
        done
    fi
    
    echo "Running API health checks..." >&2
    echo "" >&2
    
    # Run health checks
    if [ "$check_all" = true ] || [ "$check_soundcloud" = true ]; then
        checks_run=$((checks_run + 1))
        if check_soundcloud; then
            checks_passed=$((checks_passed + 1))
        fi
    fi
    
    if [ "$check_all" = true ] || [ "$check_weather" = true ]; then
        checks_run=$((checks_run + 1))
        if check_open_meteo; then
            checks_passed=$((checks_passed + 1))
        fi
    fi
    
    if [ "$check_all" = true ] || [ "$check_location" = true ]; then
        checks_run=$((checks_run + 1))
        if check_nominatim; then
            checks_passed=$((checks_passed + 1))
        fi
    fi
    
    if [ "$check_all" = true ] || [ "$check_oura_api" = true ]; then
        checks_run=$((checks_run + 1))
        if check_oura; then
            checks_passed=$((checks_passed + 1))
        fi
    fi
    
    echo "" >&2
    
    # Output summary as JSON
    local all_passed="false"
    if [ "$checks_passed" -eq "$checks_run" ]; then
        all_passed="true"
        echo -e "${GREEN}All health checks passed ($checks_passed/$checks_run)${NC}" >&2
    else
        echo -e "${YELLOW}Some health checks failed ($checks_passed/$checks_run)${NC}" >&2
    fi
    
    # Output JSON result
    jq -n \
        --argjson checks_run "$checks_run" \
        --argjson checks_passed "$checks_passed" \
        --argjson all_passed "$all_passed" \
        '{
            checks_run: $checks_run,
            checks_passed: $checks_passed,
            all_passed: $all_passed
        }'
    
    # Exit with non-zero if any checks failed
    if [ "$checks_passed" -ne "$checks_run" ]; then
        return 1
    fi
    
    return 0
}

main "$@"
