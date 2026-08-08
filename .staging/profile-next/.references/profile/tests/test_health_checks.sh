#!/bin/bash
# Test health check and circuit breaker functionality from common.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../scripts/lib/common.sh"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0

# Set up test environment
TEST_CIRCUIT_DIR=$(mktemp -d)
export CIRCUIT_BREAKER_DIR="$TEST_CIRCUIT_DIR"
export CIRCUIT_BREAKER_THRESHOLD=2
export CIRCUIT_BREAKER_TIMEOUT=5

# Cleanup function
cleanup() {
    rm -rf "$TEST_CIRCUIT_DIR"
}
trap cleanup EXIT

# Helper function to run a test
run_test() {
    local test_name=$1
    local test_func=$2
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing: ${test_name}... "
    
    if $test_func; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Test 1: Health check returns proper format
test_health_check_format() {
    # Test that health_check_api produces expected output format
    # We can't rely on external APIs being available in CI, so test the function exists and returns properly
    local output
    output=$(health_check_api "https://example.com" "Test API" 2>&1 || true)
    echo "$output" | grep -q "Health check"
}

# Test 2: Circuit breaker starts closed
test_circuit_starts_closed() {
    local test_api="TestAPI_$$"
    if is_circuit_open "$test_api" 2>/dev/null; then
        return 1
    fi
    return 0
}

# Test 3: Record API failure increases count
test_record_failure() {
    local test_api="TestFailAPI_$$"
    record_api_failure "$test_api" >/dev/null 2>&1
    local circuit_file
    circuit_file=$(get_circuit_breaker_file "$test_api")
    [ -f "$circuit_file" ]
}

# Test 4: Circuit opens after threshold failures
test_circuit_opens() {
    local test_api="TestOpenAPI_$$"
    
    # Record failures up to threshold
    for i in $(seq 1 $CIRCUIT_BREAKER_THRESHOLD); do
        record_api_failure "$test_api" >/dev/null 2>&1
    done
    
    # Circuit should now be open
    is_circuit_open "$test_api" >/dev/null 2>&1
}

# Test 5: Circuit closes after timeout
test_circuit_closes_after_timeout() {
    local test_api="TestTimeoutAPI_$$"
    
    # Open the circuit
    for i in $(seq 1 $CIRCUIT_BREAKER_THRESHOLD); do
        record_api_failure "$test_api" >/dev/null 2>&1
    done
    
    # Wait for timeout + 1 second
    sleep $((CIRCUIT_BREAKER_TIMEOUT + 1))
    
    # Circuit should be closed now
    if is_circuit_open "$test_api" 2>/dev/null; then
        return 1
    fi
    return 0
}

# Test 6: API success resets circuit breaker
test_success_resets_circuit() {
    local test_api="TestResetAPI_$$"
    
    # Record a failure
    record_api_failure "$test_api" >/dev/null 2>&1
    
    # Record success
    record_api_success "$test_api" >/dev/null 2>&1
    
    # Circuit file should be removed
    local circuit_file
    circuit_file=$(get_circuit_breaker_file "$test_api")
    [ ! -f "$circuit_file" ]
}

# Test 7: Circuit breaker file path is safe
test_circuit_file_safe() {
    local unsafe_name="Test API/With:Unsafe*Chars"
    local safe_file
    safe_file=$(get_circuit_breaker_file "$unsafe_name")
    
    # Check that the filename contains only safe characters
    basename "$safe_file" | grep -qE '^[a-z0-9_-]+_circuit\.state$'
}

# Test 8: Init circuit breaker creates directory
test_init_circuit_breaker() {
    local test_dir=$(mktemp -d)
    rm -rf "$test_dir"
    
    CIRCUIT_BREAKER_DIR="$test_dir" init_circuit_breaker
    [ -d "$test_dir" ]
    
    rm -rf "$test_dir"
}

# Run all tests
echo "Running health check and circuit breaker tests..."
echo ""

run_test "Health check format" test_health_check_format
run_test "Circuit starts closed" test_circuit_starts_closed
run_test "Record API failure" test_record_failure
run_test "Circuit opens after threshold" test_circuit_opens
run_test "Circuit closes after timeout" test_circuit_closes_after_timeout
run_test "Success resets circuit" test_success_resets_circuit
run_test "Circuit file path is safe" test_circuit_file_safe
run_test "Init circuit breaker" test_init_circuit_breaker

echo ""
echo "Results: ${TESTS_PASSED}/${TESTS_RUN} tests passed"

if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
