#!/bin/bash
# Tests for the new-card.sh card template generator script
#
# Usage:
#   ./tests/test_new_card.sh
#
# Returns:
#   0 if all tests pass, 1 if any test fails

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NEW_CARD_SCRIPT="${REPO_ROOT}/scripts/new-card.sh"

# Test directory for generated files
TEST_DIR="/tmp/test_new_card_$$"
TEST_REPO="${TEST_DIR}/repo"

# Track test results
TESTS_RUN=0
TESTS_PASSED=0

# Cleanup function
cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Setup function - creates a minimal test repo structure
setup_test_repo() {
    rm -rf "$TEST_REPO"
    mkdir -p "$TEST_REPO/scripts/lib"
    mkdir -p "$TEST_REPO/.github/workflows"
    
    # Create minimal README.md
    cat > "$TEST_REPO/README.md" << 'EOF'
# Test Profile

## Content
EOF
    
    # Create minimal common.sh (required by generated scripts)
    cat > "$TEST_REPO/scripts/lib/common.sh" << 'EOF'
#!/bin/bash
# Minimal common.sh for testing
EOF
    
    # Copy the new-card.sh script to test repo
    cp "$NEW_CARD_SCRIPT" "$TEST_REPO/scripts/new-card.sh"
    chmod +x "$TEST_REPO/scripts/new-card.sh"
}

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

# Test: Script shows help with --help flag
test_help_flag() {
    run_test "Script shows help with --help flag"
    
    local output
    output=$("$NEW_CARD_SCRIPT" --help 2>&1)
    
    if echo "$output" | grep -q "Usage:" && echo "$output" | grep -q "card-name"; then
        test_pass "Help message is displayed"
    else
        test_fail "Should show help message" "Usage: ... card-name" "$output"
    fi
}

# Test: Script shows help with -h flag
test_short_help_flag() {
    run_test "Script shows help with -h flag"
    
    local output
    output=$("$NEW_CARD_SCRIPT" -h 2>&1)
    
    if echo "$output" | grep -q "Usage:"; then
        test_pass "Short help flag works"
    else
        test_fail "Should show help with -h" "Usage:" "$output"
    fi
}

# Test: Script fails without card name
test_missing_card_name() {
    run_test "Script fails without card name"
    
    local output
    output=$("$NEW_CARD_SCRIPT" 2>&1 || true)
    
    if echo "$output" | grep -q "Error: Card name is required"; then
        test_pass "Missing card name shows error"
    else
        test_fail "Should show error for missing name" "Error: Card name is required" "$output"
    fi
}

# Test: Script rejects uppercase card names
test_rejects_uppercase() {
    run_test "Script rejects uppercase card names"
    
    local output
    output=$("$NEW_CARD_SCRIPT" "MyCard" 2>&1 || true)
    
    if echo "$output" | grep -q "Error:"; then
        test_pass "Uppercase card names are rejected"
    else
        test_fail "Should reject uppercase" "Error message" "$output"
    fi
}

# Test: Script rejects names starting with numbers
test_rejects_number_start() {
    run_test "Script rejects names starting with numbers"
    
    local output
    output=$("$NEW_CARD_SCRIPT" "123card" 2>&1 || true)
    
    if echo "$output" | grep -q "Error:"; then
        test_pass "Names starting with numbers are rejected"
    else
        test_fail "Should reject number start" "Error message" "$output"
    fi
}

# Test: Script rejects names with special characters
test_rejects_special_chars() {
    run_test "Script rejects names with special characters"
    
    local output
    output=$("$NEW_CARD_SCRIPT" "my_card" 2>&1 || true)
    
    if echo "$output" | grep -q "Error:"; then
        test_pass "Names with underscores are rejected"
    else
        test_fail "Should reject underscore" "Error message" "$output"
    fi
}

# Test: Script rejects names with double hyphens
test_rejects_double_hyphen() {
    run_test "Script rejects names with double hyphens"
    
    local output
    output=$("$NEW_CARD_SCRIPT" "my--card" 2>&1 || true)
    
    if echo "$output" | grep -q "Error:"; then
        test_pass "Names with double hyphens are rejected"
    else
        test_fail "Should reject double hyphen" "Error message" "$output"
    fi
}

# Test: Script rejects names ending with hyphen
test_rejects_trailing_hyphen() {
    run_test "Script rejects names ending with hyphen"
    
    local output
    output=$("$NEW_CARD_SCRIPT" "mycard-" 2>&1 || true)
    
    if echo "$output" | grep -q "Error:"; then
        test_pass "Names ending with hyphen are rejected"
    else
        test_fail "Should reject trailing hyphen" "Error message" "$output"
    fi
}

# Test: Script creates fetch script
test_creates_fetch_script() {
    run_test "Script creates fetch script"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -f "scripts/fetch-testcard.sh" ]; then
        test_pass "Fetch script was created"
    else
        test_fail "Should create fetch script" "scripts/fetch-testcard.sh" "file not found"
    fi
}

# Test: Fetch script is executable
test_fetch_script_executable() {
    run_test "Fetch script is executable"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -x "scripts/fetch-testcard.sh" ]; then
        test_pass "Fetch script is executable"
    else
        test_fail "Fetch script should be executable" "executable" "not executable"
    fi
}

# Test: Fetch script has correct shebang
test_fetch_script_shebang() {
    run_test "Fetch script has correct shebang"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    local first_line
    first_line=$(head -1 scripts/fetch-testcard.sh)
    
    if [ "$first_line" = "#!/bin/bash" ]; then
        test_pass "Fetch script has bash shebang"
    else
        test_fail "Should have bash shebang" "#!/bin/bash" "$first_line"
    fi
}

# Test: Script creates generator script
test_creates_generator_script() {
    run_test "Script creates generator script"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -f "scripts/generate-testcard-card.py" ]; then
        test_pass "Generator script was created"
    else
        test_fail "Should create generator" "scripts/generate-testcard-card.py" "file not found"
    fi
}

# Test: Generator script is executable
test_generator_script_executable() {
    run_test "Generator script is executable"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -x "scripts/generate-testcard-card.py" ]; then
        test_pass "Generator script is executable"
    else
        test_fail "Generator script should be executable" "executable" "not executable"
    fi
}

# Test: Generator script has Python shebang
test_generator_script_shebang() {
    run_test "Generator script has Python shebang"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    local first_line
    first_line=$(head -1 scripts/generate-testcard-card.py)
    
    if [ "$first_line" = "#!/usr/bin/env python3" ]; then
        test_pass "Generator script has Python shebang"
    else
        test_fail "Should have Python shebang" "#!/usr/bin/env python3" "$first_line"
    fi
}

# Test: Script creates workflow file
test_creates_workflow() {
    run_test "Script creates workflow file"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -f ".github/workflows/testcard-card.yml" ]; then
        test_pass "Workflow file was created"
    else
        test_fail "Should create workflow" ".github/workflows/testcard-card.yml" "file not found"
    fi
}

# Test: Workflow file has correct name
test_workflow_has_name() {
    run_test "Workflow file has correct name field"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if grep -q "name: Testcard Card" .github/workflows/testcard-card.yml; then
        test_pass "Workflow has correct name"
    else
        test_fail "Should have workflow name" "name: Testcard Card" ""
    fi
}

# Test: Script adds README markers
test_adds_readme_markers() {
    run_test "Script adds README markers"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if grep -q "<!-- TESTCARD-CARD:START -->" README.md && grep -q "<!-- TESTCARD-CARD:END -->" README.md; then
        test_pass "README markers were added"
    else
        test_fail "Should add README markers" "TESTCARD-CARD markers" ""
    fi
}

# Test: Script creates output directory
test_creates_output_directory() {
    run_test "Script creates output directory"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -d "testcard" ]; then
        test_pass "Output directory was created"
    else
        test_fail "Should create output directory" "testcard/" "directory not found"
    fi
}

# Test: Script creates .gitkeep in output directory
test_creates_gitkeep() {
    run_test "Script creates .gitkeep in output directory"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    if [ -f "testcard/.gitkeep" ]; then
        test_pass ".gitkeep file was created"
    else
        test_fail "Should create .gitkeep" "testcard/.gitkeep" "file not found"
    fi
}

# Test: Script warns on existing files
test_warns_on_existing() {
    run_test "Script warns on existing files"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    # Create files first
    ./scripts/new-card.sh testcard >/dev/null 2>&1
    
    # Run again
    local output
    output=$(./scripts/new-card.sh testcard 2>&1)
    
    if echo "$output" | grep -q "Warning:"; then
        test_pass "Shows warning for existing files"
    else
        test_fail "Should show warning for existing files" "Warning:" "$output"
    fi
}

# Test: Hyphenated card names work
test_hyphenated_names() {
    run_test "Hyphenated card names work"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh github-stats >/dev/null 2>&1
    
    if [ -f "scripts/fetch-github-stats.sh" ] && [ -f "scripts/generate-github-stats-card.py" ]; then
        test_pass "Hyphenated names create correct files"
    else
        test_fail "Should create files for hyphenated names" "fetch-github-stats.sh" ""
    fi
}

# Test: Card name with numbers works
test_name_with_numbers() {
    run_test "Card name with numbers works"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh test123 >/dev/null 2>&1
    
    if [ -f "scripts/fetch-test123.sh" ]; then
        test_pass "Names with numbers work"
    else
        test_fail "Should create files for names with numbers" "fetch-test123.sh" ""
    fi
}

# Test: Fetch script has placeholder for card name
test_fetch_script_placeholders() {
    run_test "Fetch script has correct card name placeholder"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh mytest >/dev/null 2>&1
    
    if grep -q 'OUTPUT_DIR="${OUTPUT_DIR:-mytest}"' scripts/fetch-mytest.sh; then
        test_pass "Fetch script has correct OUTPUT_DIR"
    else
        test_fail "Should have correct OUTPUT_DIR" 'OUTPUT_DIR="${OUTPUT_DIR:-mytest}"' ""
    fi
}

# Test: Generator script references correct card type
test_generator_script_card_type() {
    run_test "Generator script references correct card type"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh mytest >/dev/null 2>&1
    
    if grep -q 'get_theme_card_dimension("widths", "mytest")' scripts/generate-mytest-card.py; then
        test_pass "Generator references correct card type"
    else
        test_fail "Should reference correct card type" 'widths", "mytest"' ""
    fi
}

# Test: Workflow has correct trigger paths
test_workflow_trigger_paths() {
    run_test "Workflow has correct trigger paths"
    
    setup_test_repo
    cd "$TEST_REPO"
    
    ./scripts/new-card.sh mytest >/dev/null 2>&1
    
    if grep -q "scripts/fetch-mytest.sh" .github/workflows/mytest-card.yml && \
       grep -q "scripts/generate-mytest-card.py" .github/workflows/mytest-card.yml; then
        test_pass "Workflow has correct trigger paths"
    else
        test_fail "Should have correct paths" "fetch-mytest.sh and generate-mytest-card.py" ""
    fi
}

# Run all tests
echo "====================================="
echo "Running new-card.sh tests"
echo "====================================="
echo ""

test_help_flag
test_short_help_flag
test_missing_card_name
test_rejects_uppercase
test_rejects_number_start
test_rejects_special_chars
test_rejects_double_hyphen
test_rejects_trailing_hyphen
test_creates_fetch_script
test_fetch_script_executable
test_fetch_script_shebang
test_creates_generator_script
test_generator_script_executable
test_generator_script_shebang
test_creates_workflow
test_workflow_has_name
test_adds_readme_markers
test_creates_output_directory
test_creates_gitkeep
test_warns_on_existing
test_hyphenated_names
test_name_with_numbers
test_fetch_script_placeholders
test_generator_script_card_type
test_workflow_trigger_paths

echo ""
echo "====================================="
echo "Results: ${TESTS_PASSED}/${TESTS_RUN} tests passed"
echo "====================================="

if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    exit 0
else
    exit 1
fi
