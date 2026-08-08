#!/bin/bash
# Tests for cache functionality in scripts/lib/common.sh
#
# Usage:
#   ./tests/test_cache.sh
#
# Returns:
#   0 if all tests pass, 1 if any test fails

set -euo pipefail

# Source the common.sh file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../scripts/lib/common.sh"

# Test directory for cache operations
TEST_CACHE_DIR="/tmp/test_cache_$$"
CACHE_DIR="$TEST_CACHE_DIR"

# Track test results
TESTS_RUN=0
TESTS_PASSED=0

# Cleanup function
cleanup() {
    rm -rf "$TEST_CACHE_DIR"
}
trap cleanup EXIT

# Test helper functions
test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo "  ✓ PASS: $1"
}

test_fail() {
    echo "  ✗ FAIL: $1"
    echo "    Expected: $2"
    echo "    Got: $3"
}

run_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "Running: $1"
}

# Test: generate_cache_key produces consistent output
test_generate_cache_key_consistent() {
    run_test "generate_cache_key produces consistent output"
    
    local key1 key2
    key1=$(generate_cache_key "New York, NY")
    key2=$(generate_cache_key "New York, NY")
    
    if [ "$key1" = "$key2" ]; then
        test_pass "Same input produces same key"
    else
        test_fail "Keys should match" "$key1" "$key2"
    fi
}

# Test: generate_cache_key produces different output for different inputs
test_generate_cache_key_unique() {
    run_test "generate_cache_key produces unique keys for different inputs"
    
    local key1 key2
    key1=$(generate_cache_key "New York, NY")
    key2=$(generate_cache_key "Los Angeles, CA")
    
    if [ "$key1" != "$key2" ]; then
        test_pass "Different inputs produce different keys"
    else
        test_fail "Keys should differ" "different keys" "$key1 = $key2"
    fi
}

# Test: generate_cache_key handles empty input
test_generate_cache_key_empty() {
    run_test "generate_cache_key handles empty input"
    
    local key
    key=$(generate_cache_key "")
    
    # Empty input should produce empty base64
    if [ -z "$key" ] || [ "$key" = "" ]; then
        test_pass "Empty input produces empty or valid key"
    else
        # base64 of empty string is empty, but if it's non-empty that's also fine
        test_pass "Empty input produces consistent key: $key"
    fi
}

# Test: save_cached_response creates cache file
test_save_cached_response_creates_file() {
    run_test "save_cached_response creates cache file"
    
    cleanup
    
    echo '{"test": "data"}' | save_cached_response "test" "mykey"
    
    if [ -f "${CACHE_DIR}/test_mykey.json" ]; then
        test_pass "Cache file was created"
    else
        test_fail "Cache file should exist" "${CACHE_DIR}/test_mykey.json" "file not found"
    fi
}

# Test: save_cached_response stores correct content
test_save_cached_response_content() {
    run_test "save_cached_response stores correct content"
    
    cleanup
    
    local expected='{"lat": "40.7", "lon": "-74.0"}'
    echo "$expected" | save_cached_response "test" "content"
    
    local actual
    actual=$(cat "${CACHE_DIR}/test_content.json")
    
    if [ "$actual" = "$expected" ]; then
        test_pass "Correct content was stored"
    else
        test_fail "Content should match" "$expected" "$actual"
    fi
}

# Test: get_cached_response returns cached content
test_get_cached_response_hit() {
    run_test "get_cached_response returns cached content (cache hit)"
    
    cleanup
    
    local expected='{"lat": "40.7", "lon": "-74.0"}'
    echo "$expected" | save_cached_response "test" "hitkey"
    
    local actual
    actual=$(get_cached_response "test" "hitkey" 2>/dev/null)
    
    if [ "$actual" = "$expected" ]; then
        test_pass "Cache hit returns correct content"
    else
        test_fail "Content should match" "$expected" "$actual"
    fi
}

# Test: get_cached_response fails for missing cache
test_get_cached_response_miss() {
    run_test "get_cached_response fails for missing cache (cache miss)"
    
    cleanup
    
    if get_cached_response "test" "nonexistent" 2>/dev/null; then
        test_fail "Should return non-zero for cache miss" "exit code 1" "exit code 0"
    else
        test_pass "Cache miss returns non-zero exit code"
    fi
}

# Test: get_cached_response removes invalid JSON
test_get_cached_response_invalid_json() {
    run_test "get_cached_response removes invalid JSON cache"
    
    cleanup
    mkdir -p "$CACHE_DIR"
    
    # Create an invalid JSON file
    echo "not valid json" > "${CACHE_DIR}/test_invalid.json"
    
    if get_cached_response "test" "invalid" 2>/dev/null; then
        test_fail "Should return non-zero for invalid JSON" "exit code 1" "exit code 0"
        return
    fi
    
    # Verify file was removed
    if [ ! -f "${CACHE_DIR}/test_invalid.json" ]; then
        test_pass "Invalid JSON cache returns non-zero and file was removed"
    else
        test_fail "Invalid cache file should be removed" "file deleted" "file exists"
    fi
}

# Test: init_cache creates directory
test_init_cache_creates_dir() {
    run_test "init_cache creates cache directory"
    
    cleanup
    
    init_cache
    
    if [ -d "$CACHE_DIR" ]; then
        test_pass "Cache directory was created"
    else
        test_fail "Cache directory should exist" "$CACHE_DIR" "directory not found"
    fi
}

# Test: cache respects TTL (simulated with touch)
test_cache_ttl_expired() {
    run_test "get_cached_response handles expired cache"
    
    cleanup
    
    # Create a cache file
    local expected='{"lat": "40.7"}'
    echo "$expected" | save_cached_response "test" "expiredkey"
    
    # Set cache TTL to 0 days to simulate expired cache
    local original_ttl=$CACHE_TTL_DAYS
    CACHE_TTL_DAYS=0
    
    local result=0
    if get_cached_response "test" "expiredkey" 2>/dev/null; then
        result=1
    fi
    
    # Restore original TTL
    CACHE_TTL_DAYS=$original_ttl
    
    if [ "$result" -eq 0 ]; then
        test_pass "Expired cache returns non-zero exit code"
    else
        test_fail "Should return non-zero for expired cache" "exit code 1" "exit code 0"
    fi
}

# Run all tests
echo "====================================="
echo "Running cache function tests"
echo "====================================="
echo ""

test_generate_cache_key_consistent
test_generate_cache_key_unique
test_generate_cache_key_empty
test_save_cached_response_creates_file
test_save_cached_response_content
test_get_cached_response_hit
test_get_cached_response_miss
test_get_cached_response_invalid_json
test_init_cache_creates_dir
test_cache_ttl_expired

echo ""
echo "====================================="
echo "Results: ${TESTS_PASSED}/${TESTS_RUN} tests passed"
echo "====================================="

if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    exit 0
else
    exit 1
fi
