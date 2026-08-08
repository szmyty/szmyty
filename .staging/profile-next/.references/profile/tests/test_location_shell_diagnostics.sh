#!/bin/bash
# Integration tests for location fetching shell script diagnostics
# This script tests that the fetch-location.sh script properly saves
# diagnostic information when failures occur.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEST_OUTPUT_DIR=$(mktemp -d)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Cleanup function
cleanup() {
    rm -rf "$TEST_OUTPUT_DIR"
}
trap cleanup EXIT

# Test assertion function
assert_file_exists() {
    local file=$1
    local description=$2
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} FAIL: $description - File not found: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_file_contains() {
    local file=$1
    local pattern=$2
    local description=$3
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗${NC} FAIL: $description - File not found: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    
    if grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} FAIL: $description - Pattern not found: $pattern"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "=================================================="
echo "Location Shell Script Diagnostics Tests"
echo "=================================================="
echo ""

# Test 1: Verify diagnostic files are created even on failure
echo "Test 1: Diagnostic files created on network failure"
echo "---------------------------------------------------"

# Create a cached location to bypass GitHub API
mkdir -p "$TEST_OUTPUT_DIR/cached"
echo '{"location":"New York, NY","updated_at":"2024-01-01T00:00:00Z"}' > "$TEST_OUTPUT_DIR/cached/location.json"

# Run the script (it will fail due to network restrictions)
cd "$PROJECT_ROOT"
export OUTPUT_DIR="$TEST_OUTPUT_DIR/location"
export LOCATION_CACHE_FILE="$TEST_OUTPUT_DIR/cached/location.json"
mkdir -p "$OUTPUT_DIR"

# Run script and capture output (will fail)
"${PROJECT_ROOT}/scripts/fetch-location.sh" > "$TEST_OUTPUT_DIR/output.json" 2> "$TEST_OUTPUT_DIR/stderr.log" || true

# Verify diagnostic files were created
assert_file_exists "$OUTPUT_DIR/debug_nominatim.json" "Nominatim debug JSON file created"
assert_file_exists "$OUTPUT_DIR/debug_nominatim_response.txt" "Nominatim response debug file created"

# Verify diagnostic content
assert_file_contains "$OUTPUT_DIR/debug_nominatim_response.txt" "Location Query:" "Debug file contains location query"
assert_file_contains "$OUTPUT_DIR/debug_nominatim_response.txt" "HTTP Code:" "Debug file contains HTTP code"
assert_file_contains "$OUTPUT_DIR/debug_nominatim_response.txt" "Curl Exit Code:" "Debug file contains curl exit code"

# Verify error messages are actionable
assert_file_contains "$TEST_OUTPUT_DIR/stderr.log" "❌ FAILURE:" "Error message uses clear failure indicator"

echo ""

# Test 2: Verify get_coordinates saves diagnostic info
echo "Test 2: get_coordinates function saves diagnostic data"
echo "--------------------------------------------------------"

# Source the common.sh to test the function directly
source "${PROJECT_ROOT}/scripts/lib/common.sh"

TEST_OUTPUT_DIR2=$(mktemp -d)
# Ensure cleanup even on unexpected exit
trap "rm -rf '$TEST_OUTPUT_DIR2'" EXIT
export OUTPUT_DIR="$TEST_OUTPUT_DIR2"

# Try to get coordinates (will fail)
get_coordinates "Test Location" 2>/dev/null || true

# Verify files were created
assert_file_exists "$TEST_OUTPUT_DIR2/debug_nominatim.json" "Nominatim JSON created by get_coordinates"
assert_file_exists "$TEST_OUTPUT_DIR2/debug_nominatim_response.txt" "Nominatim response created by get_coordinates"

echo ""
echo "=================================================="
echo "Test Summary"
echo "=================================================="
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
else
    echo -e "Tests failed: $TESTS_FAILED"
fi
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
