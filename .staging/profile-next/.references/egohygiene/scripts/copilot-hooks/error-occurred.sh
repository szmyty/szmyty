#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# error-occurred.sh — Copilot errorOccurred hook for Ego Hygiene
#
# Emits sanitized diagnostics when a Copilot session encounters an error.
# This hook deliberately omits raw prompt text, environment variables, tokens,
# journal content, and any other sensitive data.
#
# Input (stdin): JSON payload with fields:
#   sessionId    — unique session identifier
#   timestamp    — Unix timestamp in milliseconds
#   cwd          — working directory reported by the Copilot runtime
#   error        — object: { message, name, stack? }
#   errorContext — "model_call" | "tool_execution" | "system" | "user_input"
#   recoverable  — boolean
#
# Output: none; exit 0 always (errorOccurred output is not processed).
#
# Docs: https://docs.github.com/en/copilot/reference/hooks-reference

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

readonly HOOK_NAME="error-occurred"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

## @description Print a labelled diagnostic line to stderr.
## @param $1 label   Log level (INFO, WARN, ERROR)
## @param $2 message Human-readable message (must not contain secrets)
log() {
  local label="${1}"
  local message="${2}"
  printf '[copilot/%s] %s: %s\n' "${HOOK_NAME}" "${label}" "${message}" >&2
}

## @description Extract a field from JSON using jq, or return a default.
## @param $1 json    Raw JSON string
## @param $2 query   jq query expression
## @param $3 default Value to return when jq is unavailable or field is absent
jq_field() {
  local json="${1}"
  local query="${2}"
  local default="${3:-}"
  if ! command -v jq > /dev/null 2>&1; then
    printf '%s' "${default}"
    return 0
  fi
  local result
  result="$(printf '%s' "${json}" | jq --raw-output "${query} // empty" 2>/dev/null || true)"
  printf '%s' "${result:-${default}}"
}

## @description Sanitize a string for safe inclusion in a log line.
##
## Removes newlines, carriage returns, and truncates to 200 characters.
## This prevents log injection and avoids accidentally emitting multi-line
## values that might contain sensitive content on subsequent lines.
##
## @param $1 value  Raw value to sanitize
sanitize() {
  local value="${1}"
  printf '%s' "${value}" | tr -d '\n\r' | cut -c1-200
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

## @description Entry point — read payload, emit sanitized diagnostic summary.
main() {
  # Read stdin once; never log its raw contents.
  local payload
  payload="$(cat)"

  # Validate JSON silently; on failure emit a minimal diagnostic and exit.
  if command -v jq > /dev/null 2>&1; then
    if ! printf '%s' "${payload}" | jq --exit-status . > /dev/null 2>&1; then
      log "WARN" "errorOccurred payload is not valid JSON; cannot extract fields"
      exit 0
    fi
  else
    log "WARN" "jq not available; skipping errorOccurred field extraction"
    exit 0
  fi

  # Extract only the fields that are safe to surface.
  # Note: .recoverable is a boolean; use tostring to avoid jq's // treating false as empty.
  local session_id error_name error_context recoverable timestamp
  session_id="$(sanitize "$(jq_field "${payload}" '.sessionId' "(unknown)")")"
  error_name="$(sanitize "$(jq_field "${payload}" '.error.name' "(unknown)")")"
  error_context="$(sanitize "$(jq_field "${payload}" '.errorContext' "(unknown)")")"
  recoverable="$(sanitize "$(printf '%s' "${payload}" | jq --raw-output 'if .recoverable == null then "(unknown)" else (.recoverable | tostring) end' 2>/dev/null || printf '(unknown)')")"
  timestamp="$(sanitize "$(jq_field "${payload}" '.timestamp' "")")"

  # Convert Unix ms timestamp to a human-readable form when possible.
  local time_display="${timestamp}"
  if [[ -n "${timestamp}" ]] && command -v date > /dev/null 2>&1; then
    local ts_sec
    ts_sec="$(printf '%s' "${timestamp}" | cut -c1-10)"
    time_display="$(date --date="@${ts_sec}" --utc '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || printf '%s' "${timestamp}")"
  fi

  # Emit a sanitized one-line diagnostic (no stack trace, no error message).
  log "ERROR" "session=${session_id} error_name=${error_name} context=${error_context} recoverable=${recoverable} timestamp=${time_display}"

  exit 0
}

main
