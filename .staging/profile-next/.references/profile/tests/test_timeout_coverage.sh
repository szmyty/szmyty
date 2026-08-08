#!/bin/bash
# Test to verify all curl commands have --max-time timeouts
# This ensures workflows won't hang indefinitely on API calls

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
ISSUES_FOUND=0

echo "Testing curl timeout coverage..."
echo ""

# Find all shell scripts with curl commands
SCRIPTS_TO_CHECK=(
    "${SCRIPT_DIR}/../scripts/fetch-soundcloud.sh"
    "${SCRIPT_DIR}/../scripts/fetch-timezone.sh"
    "${SCRIPT_DIR}/../scripts/fetch-weather.sh"
    "${SCRIPT_DIR}/../scripts/fetch-oura.sh"
    "${SCRIPT_DIR}/../scripts/fetch-location.sh"
    "${SCRIPT_DIR}/../scripts/health_check.sh"
    "${SCRIPT_DIR}/../scripts/lib/common.sh"
)

for script in "${SCRIPTS_TO_CHECK[@]}"; do
    if [ ! -f "$script" ]; then
        echo -e "${YELLOW}Warning: Script not found: $script${NC}"
        continue
    fi
    
    script_name=$(basename "$script")
    TESTS_RUN=$((TESTS_RUN + 1))
    
    echo -n "Checking $script_name... "
    
    # Extract curl commands (exclude comments and handle multi-line commands)
    # Look for actual curl command invocations that are not commented out
    curl_lines=$(grep -nE 'curl\s+-' "$script" | grep -vE '^\s*#' | grep -vE '(Curl |curl_exit)' || true)
    
    if [ -z "$curl_lines" ]; then
        echo -e "${GREEN}PASSED (no curl commands)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        continue
    fi
    
    # Check if curl commands have --max-time
    missing_timeout=false
    while IFS= read -r line; do
        line_num=$(echo "$line" | cut -d: -f1)
        
        # Get the full curl command (may span multiple lines)
        # Check the next 10 lines after the curl command for --max-time
        context=$(sed -n "${line_num},$((line_num + 10))p" "$script")
        
        if ! echo "$context" | grep -q "\-\-max-time"; then
            # Check if it's part of a retry_with_backoff wrapper
            if ! echo "$context" | grep -q "retry_with_backoff"; then
                echo -e "${RED}FAILED${NC}"
                echo "  → Line $line_num: curl command without --max-time or retry_with_backoff"
                missing_timeout=true
                ISSUES_FOUND=$((ISSUES_FOUND + 1))
                break
            fi
        fi
    done <<< "$curl_lines"
    
    if [ "$missing_timeout" = false ]; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
done

echo ""
echo "Results: ${TESTS_PASSED}/${TESTS_RUN} scripts passed"
echo "Issues found: ${ISSUES_FOUND}"
echo ""

if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    echo -e "${GREEN}✓ All curl commands have timeout protection!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some curl commands are missing timeout protection!${NC}"
    exit 1
fi
