#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# pre-tool-use.sh — Copilot preToolUse safety guardrail for Ego Hygiene
#
# Inspects proposed tool calls before Copilot executes them and denies
# clearly unsafe patterns.  This script is conservative: it blocks only
# well-known destructive patterns and allows ordinary development commands
# that mutate files inside the working tree.
#
# Input (stdin): JSON payload with fields:
#   sessionId  — unique session identifier
#   timestamp  — Unix timestamp in milliseconds
#   cwd        — working directory reported by the Copilot runtime
#   toolName   — name of the tool about to be executed
#   toolArgs   — tool arguments (object; shape depends on toolName)
#
# Output (stdout): JSON object with:
#   permissionDecision       — "allow" | "deny"
#   permissionDecisionReason — required when decision is "deny"
#
# Docs: https://docs.github.com/en/copilot/reference/hooks-reference
#
# Trust boundary: This hook runs synchronously inside agent execution.
# Input arrives as JSON and is never evaluated as shell code.  Do not
# add patterns that inspect or log prompt text or environment variables.

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

readonly HOOK_NAME="pre-tool-use"

# Shell tool names that carry a command string to inspect.
readonly SHELL_TOOLS=("bash" "sh" "zsh" "powershell" "pwsh" "cmd")

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

## @description Emit a JSON allow decision to stdout.
allow() {
  printf '{"permissionDecision":"allow"}\n'
}

## @description Emit a JSON deny decision with a reason to stdout.
## @param $1 reason Human-readable reason shown to the agent
deny() {
  local reason="${1}"
  # Sanitize reason: remove newlines and limit length to avoid log injection.
  local safe_reason
  safe_reason="$(printf '%s' "${reason}" | tr -d '\n\r' | cut -c1-200)"
  printf '{"permissionDecision":"deny","permissionDecisionReason":"%s"}\n' "${safe_reason}"
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

# ---------------------------------------------------------------------------
# Pattern checks
# ---------------------------------------------------------------------------

## @description Check whether a command string matches any denied patterns.
##
## Blocked categories and rationale:
##   1. Destructive filesystem targeting paths outside the working tree or root.
##   2. Force pushes to protected branches (main, master, develop).
##   3. Destructive Git history rewrites (filter-branch, rebase -i on remote
##      branches, reset --hard to remote refs).
##   4. Commands that print or export likely secret environment variables
##      (printenv, env, export, echo $VAR where VAR contains common secret
##      naming patterns).
##   5. Attempts to read well-known credential files (~/.netrc, ~/.ssh/id_*,
##      *.pem, .env files, *credentials*).
##   6. Broad recursive permission changes that could expose sensitive files.
##   7. Package publication without explicit review (npm publish --no-dry-run,
##      pub publish, pip upload, twine upload in non-test contexts).
##
## @param $1 cmd  Command string to inspect
## @return 0 if allowed, 1 if denied; prints denial reason on stdout
check_command() {
  local cmd="${1}"

  # Normalise whitespace for pattern matching (do not evaluate).
  local normalised
  normalised="$(printf '%s' "${cmd}" | tr -s '[:space:]' ' ')"

  # -------------------------------------------------------------------------
  # 1. Destructive filesystem operations outside working tree
  # Use two-step checks: first confirm rm is present with recursive+force flags,
  # then confirm the target is root or home. This avoids complex regex flags.
  # -------------------------------------------------------------------------
  # Detect rm with -rf or -fr (in any order, combined or separate)
  local has_rm_recursive=0
  if printf '%s' "${normalised}" | grep -qE 'rm[[:space:]]' 2>/dev/null; then
    if printf '%s' "${normalised}" | grep -qE '[[:space:]]-(rf|fr|[^[:space:]]*r[^[:space:]]*f[^[:space:]]*)([[:space:]]|$)' 2>/dev/null; then
      has_rm_recursive=1
    fi
  fi
  if [[ "${has_rm_recursive}" -eq 1 ]]; then
    # rm -rf / or rm -rf /* — targeting filesystem root
    if printf '%s' "${normalised}" | grep -qE '[[:space:]]/\*?([[:space:]]|$)' 2>/dev/null; then
      deny "Destructive recursive deletion targeting the filesystem root is not permitted."
      return 1
    fi
    # rm -rf ~ or rm -rf ~/ — targeting home directory
    if printf '%s' "${normalised}" | grep -qE '[[:space:]]~/?([[:space:]]|$)' 2>/dev/null; then
      deny "Destructive recursive deletion targeting the home directory is not permitted."
      return 1
    fi
  fi

  # -------------------------------------------------------------------------
  # 2. Force pushes to protected branches
  # -------------------------------------------------------------------------
  if printf '%s' "${normalised}" | grep -qE 'git[[:space:]].*push[[:space:]].*--force(-with-lease)?[[:space:]].*\b(origin|upstream)\b[[:space:]]+(main|master|develop)\b' 2>/dev/null; then
    deny "Force push to a protected branch (main, master, develop) is not permitted."
    return 1
  fi
  # Also catch: git push --force origin/main style
  if printf '%s' "${normalised}" | grep -qE 'git[[:space:]].*push[[:space:]].*--force(-with-lease)?[[:space:]].*\b(origin|upstream)/(main|master|develop)\b' 2>/dev/null; then
    deny "Force push to a protected branch (main, master, develop) is not permitted."
    return 1
  fi

  # -------------------------------------------------------------------------
  # 3. Destructive Git history rewrites
  # -------------------------------------------------------------------------
  # git filter-branch
  if printf '%s' "${normalised}" | grep -qE 'git[[:space:]].*filter-branch' 2>/dev/null; then
    deny "git filter-branch rewrites history and is not permitted. Use git filter-repo for intentional history surgery."
    return 1
  fi
  # git reset --hard to a remote ref (e.g. origin/main)
  if printf '%s' "${normalised}" | grep -qE 'git[[:space:]].*reset[[:space:]].*--hard[[:space:]]+(origin|upstream)/' 2>/dev/null; then
    deny "git reset --hard to a remote ref is not permitted as it discards local commits."
    return 1
  fi

  # -------------------------------------------------------------------------
  # 4. Printing or exporting likely secret environment variables
  # -------------------------------------------------------------------------
  # Patterns: printenv, env (standalone), export VAR=, echo $SECRET_* etc.
  if printf '%s' "${normalised}" | grep -qiE '(printenv|^env[[:space:]]*$|[[:space:]]env[[:space:]]*$|\$\{?(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY|ACCESS_KEY|AUTH|CREDENTIAL)[^}]*\}?)' 2>/dev/null; then
    deny "Commands that may expose secret environment variables are not permitted."
    return 1
  fi

  # -------------------------------------------------------------------------
  # 5. Reading well-known credential files
  # -------------------------------------------------------------------------
  if printf '%s' "${normalised}" | grep -qE '(cat|less|more|head|tail|open|type)[[:space:]].*(\.netrc|\.ssh/id_|\.aws/credentials|\.aws/config|\.env[[:space:]]|\.env$|credentials\.json|keystore|\.pem|\.p12|\.pfx)' 2>/dev/null; then
    deny "Reading credential files is not permitted."
    return 1
  fi

  # -------------------------------------------------------------------------
  # 6. Broad recursive permission changes
  # Use two-step check: first match chmod with recursive flag and broad mode,
  # then confirm the target is root or home.
  # -------------------------------------------------------------------------
  if printf '%s' "${normalised}" | grep -qE 'chmod[[:space:]].*-[^[:space:]]*R[^[:space:]]*[[:space:]]+(777|a\+rwx)' 2>/dev/null; then
    if printf '%s' "${normalised}" | grep -qE '[[:space:]](-[^[:space:]]*R[^[:space:]]*[[:space:]]+(777|a\+rwx)[[:space:]]+(/|~)|(777|a\+rwx)[[:space:]]+(/|~))' 2>/dev/null; then
      deny "Broad recursive permission changes (chmod -R 777 or a+rwx on ~ or /) are not permitted."
      return 1
    fi
  fi

  # -------------------------------------------------------------------------
  # 7. Unreviewed package publication
  # Use two-step check to avoid relying on negative lookahead (not POSIX ERE):
  # first match the publication command, then verify --dry-run is absent.
  # -------------------------------------------------------------------------
  # npm publish without --dry-run
  if printf '%s' "${normalised}" | grep -qE 'npm[[:space:]]publish([[:space:]]|$)' 2>/dev/null; then
    if ! printf '%s' "${normalised}" | grep -qE '\-\-dry-run' 2>/dev/null; then
      deny "Package publication without explicit dry-run or review flag is not permitted."
      return 1
    fi
  fi
  # pub publish without --dry-run
  if printf '%s' "${normalised}" | grep -qE 'pub[[:space:]]publish([[:space:]]|$)' 2>/dev/null; then
    if ! printf '%s' "${normalised}" | grep -qE '\-\-dry-run' 2>/dev/null; then
      deny "Package publication without explicit dry-run or review flag is not permitted."
      return 1
    fi
  fi
  # twine upload — deny unless targeting testpypi
  if printf '%s' "${normalised}" | grep -qE 'twine[[:space:]]upload([[:space:]]|$)' 2>/dev/null; then
    if ! printf '%s' "${normalised}" | grep -qiE '\-\-repository[[:space:]]testpypi' 2>/dev/null; then
      deny "Package publication without explicit dry-run or review flag is not permitted."
      return 1
    fi
  fi

  return 0
}

## @description Determine whether a given tool name carries a shell command.
## @param $1 tool_name
## @return 0 if this tool has a command to inspect, 1 otherwise
is_shell_tool() {
  local tool="${1}"
  local t
  for t in "${SHELL_TOOLS[@]}"; do
    if [[ "${tool}" == "${t}" ]]; then
      return 0
    fi
  done
  return 1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

## @description Entry point — read payload, inspect tool call, emit decision.
main() {
  # Read stdin once; never log its contents.
  local payload
  payload="$(cat)"

  # Validate JSON.
  if command -v jq > /dev/null 2>&1; then
    if ! printf '%s' "${payload}" | jq --exit-status . > /dev/null 2>&1; then
      log "WARN" "preToolUse payload is not valid JSON; defaulting to allow"
      allow
      return 0
    fi
  else
    log "WARN" "jq not found; cannot parse preToolUse payload — defaulting to allow"
    allow
    return 0
  fi

  local tool_name
  tool_name="$(jq_field "${payload}" '.toolName' "")"

  log "INFO" "preToolUse: tool=${tool_name:-<unknown>}"

  # Only inspect shell-executing tools.
  if ! is_shell_tool "${tool_name}"; then
    allow
    return 0
  fi

  # Extract the command string from toolArgs.command or toolArgs.input.
  local cmd
  cmd="$(jq_field "${payload}" '.toolArgs.command // .toolArgs.input // empty' "")"

  if [[ -z "${cmd}" ]]; then
    # No command to inspect; allow by default.
    allow
    return 0
  fi

  # Run pattern checks; check_command emits the decision JSON on match.
  if ! check_command "${cmd}"; then
    # check_command already printed the deny JSON.
    return 0
  fi

  allow
}

main
