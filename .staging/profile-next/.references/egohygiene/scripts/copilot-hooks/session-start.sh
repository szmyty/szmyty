#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# session-start.sh — Copilot sessionStart hook for Ego Hygiene
#
# Performs lightweight repository validation at the start of every Copilot
# cloud agent or CLI session.  This script intentionally avoids installing
# dependencies, mutating source files, or running expensive operations.
#
# Input (stdin): JSON payload with fields:
#   sessionId  — unique session identifier
#   timestamp  — Unix timestamp in milliseconds
#   cwd        — working directory reported by the Copilot runtime
#   source     — "startup" | "resume" | "new"
#
# Output: none required; exit 0 on success, non-zero to surface a warning.
#
# Docs: https://docs.github.com/en/copilot/reference/hooks-reference

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

readonly HOOK_NAME="session-start"
readonly REQUIRED_FILES=(
  "Taskfile.yml"
  ".github/hooks/ego-hygiene.json"
)
readonly RECOMMENDED_TOOLS=(
  "git"
  "jq"
  "task"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

## @description Print a labelled status line to stderr (not captured by hook output).
## @param $1 label   Log level label (INFO, WARN, ERROR)
## @param $2 message Human-readable message
log() {
  local label="${1}"
  local message="${2}"
  printf '[copilot/%s] %s: %s\n' "${HOOK_NAME}" "${label}" "${message}" >&2
}

## @description Validate that the payload received on stdin is well-formed JSON.
## @param $1 raw  Raw JSON string to validate
## @return 0 if valid or jq unavailable, 1 if JSON is invalid
validate_payload() {
  local raw="${1}"
  if ! command -v jq > /dev/null 2>&1; then
    log "WARN" "jq is not available; skipping JSON validation"
    return 0
  fi
  if ! printf '%s' "${raw}" | jq --exit-status . > /dev/null 2>&1; then
    log "WARN" "Received malformed JSON payload; continuing with defaults"
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

## @description Confirm execution starts from the repository root.
## @return 0 if root markers exist, 1 otherwise
check_repository_root() {
  if [[ ! -f "Taskfile.yml" ]]; then
    log "WARN" "Taskfile.yml not found — session may not be running from the repository root"
    return 1
  fi
  log "INFO" "Repository root confirmed"
  return 0
}

## @description Confirm that expected sentinel files are present.
check_required_files() {
  local missing=0
  for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -e "${file}" ]]; then
      log "WARN" "Expected file not found: ${file}"
      missing=1
    fi
  done
  if [[ "${missing}" -eq 0 ]]; then
    log "INFO" "Required repository files present"
  fi
}

## @description Warn when recommended tooling is unavailable.
check_recommended_tools() {
  for tool in "${RECOMMENDED_TOOLS[@]}"; do
    if ! command -v "${tool}" > /dev/null 2>&1; then
      log "WARN" "Recommended tool not found on PATH: ${tool}"
    fi
  done
}

## @description Print a concise environment summary (no secrets or env values).
print_environment_summary() {
  local rev="(unknown)"
  if command -v git > /dev/null 2>&1 && git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    rev="$(git rev-parse --short HEAD 2>/dev/null || printf '(unavailable)')"
  fi

  log "INFO" "OS: $(uname -s 2>/dev/null || printf unknown)"
  log "INFO" "Repository revision: ${rev}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

## @description Entry point — read payload, run validation checks.
main() {
  # Consume stdin but do not log its contents (may include sensitive context).
  local payload
  payload="$(cat)"

  # Validate JSON silently when jq is available.
  validate_payload "${payload}" || true

  print_environment_summary
  check_repository_root || true
  check_required_files
  check_recommended_tools

  log "INFO" "Session validation complete"
  exit 0
}

main
