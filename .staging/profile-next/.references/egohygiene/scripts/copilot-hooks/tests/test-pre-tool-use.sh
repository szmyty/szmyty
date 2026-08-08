#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# test-pre-tool-use.sh — Automated tests for scripts/copilot-hooks/pre-tool-use.sh
#
# Validates that the preToolUse hook:
#   - allows a normal read-only command
#   - allows a normal repository-local development command
#   - denies a clearly destructive filesystem command
#   - denies a force push to the default branch
#   - denies an attempt to print likely secret environment variables
#   - handles malformed JSON safely
#   - does not expose raw input in failure output

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly HOOK="${SCRIPT_DIR}/../pre-tool-use.sh"

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

PASS=0
FAIL=0

## @description Run a single test case.
## @param $1 description  Human-readable test name
## @param $2 payload      JSON payload string to feed as stdin
## @param $3 expect       "allow" | "deny" — expected permissionDecision
run_test() {
  local description="${1}"
  local payload="${2}"
  local expect="${3}"

  local output
  output="$(printf '%s' "${payload}" | bash "${HOOK}")"

  local decision
  decision="$(printf '%s' "${output}" | jq --raw-output '.permissionDecision' 2>/dev/null || printf 'parse_error')"

  if [[ "${decision}" == "${expect}" ]]; then
    printf 'PASS: %s\n' "${description}"
    PASS=$((PASS + 1))
  else
    printf 'FAIL: %s (expected=%s got=%s)\n' "${description}" "${expect}" "${decision}"
    FAIL=$((FAIL + 1))
  fi
}

## @description Verify that the output contains no raw input fragments.
## @param $1 description  Human-readable test name
## @param $2 payload      JSON payload that contains a sentinel secret string
## @param $3 sentinel     String that must NOT appear in stdout or stderr
run_no_secret_test() {
  local description="${1}"
  local payload="${2}"
  local sentinel="${3}"

  local combined
  combined="$(printf '%s' "${payload}" | bash "${HOOK}" 2>&1)"

  if printf '%s' "${combined}" | grep --fixed-strings --quiet "${sentinel}"; then
    printf 'FAIL: %s (raw input found in output)\n' "${description}"
    FAIL=$((FAIL + 1))
  else
    printf 'PASS: %s\n' "${description}"
    PASS=$((PASS + 1))
  fi
}

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

# 1. Allow: read-only command (cat a tracked file)
run_test "allows a read-only command" \
  '{"toolName":"bash","toolArgs":{"command":"cat README.md"}}' \
  "allow"

# 2. Allow: normal development command inside working tree
run_test "allows a normal flutter test command" \
  '{"toolName":"bash","toolArgs":{"command":"fvm flutter test"}}' \
  "allow"

# 3. Allow: non-shell tool (view)
run_test "allows a non-shell tool unconditionally" \
  '{"toolName":"view","toolArgs":{"path":"lib/main.dart"}}' \
  "allow"

# 4. Deny: rm -rf /
run_test "denies rm -rf targeting filesystem root" \
  '{"toolName":"bash","toolArgs":{"command":"rm -rf /"}}' \
  "deny"

# 5. Deny: rm -rf ~ (home directory)
run_test "denies rm -rf targeting home directory" \
  '{"toolName":"bash","toolArgs":{"command":"rm -rf ~/"}}' \
  "deny"

# 6. Deny: force push to main
run_test "denies force push to main branch" \
  '{"toolName":"bash","toolArgs":{"command":"git push --force origin main"}}' \
  "deny"

# 7. Deny: force push to master
run_test "denies force push to master branch" \
  '{"toolName":"bash","toolArgs":{"command":"git push --force-with-lease origin master"}}' \
  "deny"

# 8. Deny: git filter-branch
run_test "denies git filter-branch" \
  '{"toolName":"bash","toolArgs":{"command":"git filter-branch --tree-filter rm HEAD"}}' \
  "deny"

# 9. Deny: printenv (secret exposure)
run_test "denies printenv command" \
  '{"toolName":"bash","toolArgs":{"command":"printenv"}}' \
  "deny"

# 10. Deny: echoing a secret env var
run_test "denies echoing a SECRET variable" \
  '{"toolName":"bash","toolArgs":{"command":"echo $SECRET_KEY"}}' \
  "deny"

# 11. Allow: malformed JSON — must default to allow
run_test "allows when JSON is malformed" \
  'not valid json at all' \
  "allow"

# 12. Allow: empty toolArgs command — no command to inspect
run_test "allows when toolArgs has no command field" \
  '{"toolName":"bash","toolArgs":{}}' \
  "allow"

# 13. Allow: git commit (normal dev operation)
run_test "allows git commit" \
  '{"toolName":"bash","toolArgs":{"command":"git commit -m \"fix: update tests\""}}' \
  "allow"

# 14. No secret leakage: a payload with a sentinel secret must not appear in output
run_no_secret_test "does not expose raw input in output" \
  '{"toolName":"bash","toolArgs":{"command":"echo $MY_SUPER_SECRET_PASSWORD_XYZ123"}}' \
  "MY_SUPER_SECRET_PASSWORD_XYZ123"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

printf '\n%d passed, %d failed\n' "${PASS}" "${FAIL}"
[[ "${FAIL}" -eq 0 ]]
