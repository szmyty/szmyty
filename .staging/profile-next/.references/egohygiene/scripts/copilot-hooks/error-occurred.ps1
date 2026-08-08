#Requires -Version 7.0
# SPDX-License-Identifier: MIT
#
# error-occurred.ps1 — Copilot errorOccurred hook for Ego Hygiene (PowerShell)
#
# Emits sanitized diagnostics when a Copilot session encounters an error.
# Behavior mirrors error-occurred.sh.
#
# Input (stdin): JSON payload with fields:
#   sessionId    — unique session identifier
#   timestamp    — Unix timestamp in milliseconds
#   cwd          — working directory reported by the Copilot runtime
#   error        — object: { message, name, stack? }
#   errorContext — "model_call" | "tool_execution" | "system" | "user_input"
#   recoverable  — boolean
#
# Output: none; exits 0 always.
#
# Docs: https://docs.github.com/en/copilot/reference/hooks-reference

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

$script:HookName = 'error-occurred'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Write-HookLog {
  <#
  .SYNOPSIS
  Writes a labelled diagnostic line to stderr.
  .PARAMETER Label
  Log level label.
  .PARAMETER Message
  Human-readable message — must not contain secrets.
  #>
  param(
    [Parameter(Mandatory)][string]$Label,
    [Parameter(Mandatory)][string]$Message
  )
  [Console]::Error.WriteLine("[copilot/$script:HookName] ${Label}: ${Message}")
}

function Get-Sanitized {
  <#
  .SYNOPSIS
  Sanitizes a string for safe inclusion in a log line.
  Removes newlines, carriage returns, and truncates to 200 characters.
  .PARAMETER Value
  Raw string value.
  #>
  param([string]$Value = '')
  $safe = ($Value -replace '[\r\n]', '')
  if ($safe.Length -gt 200) { $safe = $safe.Substring(0, 200) }
  return $safe
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Read stdin once; never log its raw contents.
$raw = ''
try {
  $raw = [Console]::In.ReadToEnd()
} catch {
  Write-HookLog -Label 'WARN' -Message 'Could not read stdin'
  exit 0
}

# Validate JSON.
$payload = $null
try {
  if (-not [string]::IsNullOrWhiteSpace($raw)) {
    $payload = $raw | ConvertFrom-Json -AsHashtable -ErrorAction Stop
  }
} catch {
  Write-HookLog -Label 'WARN' -Message 'errorOccurred payload is not valid JSON; cannot extract fields'
  exit 0
}

if ($null -eq $payload) {
  Write-HookLog -Label 'WARN' -Message 'Empty errorOccurred payload'
  exit 0
}

# Extract only safe fields — do NOT log error.message, stack, or prompt text.
$sessionId    = Get-Sanitized ($payload['sessionId']    ?? '(unknown)')
$errorName    = Get-Sanitized ($payload['error']?['name'] ?? '(unknown)')
$errorContext = Get-Sanitized ($payload['errorContext'] ?? '(unknown)')
$recoverable  = Get-Sanitized ([string]($payload['recoverable'] ?? '(unknown)'))
$timestamp    = Get-Sanitized ([string]($payload['timestamp']   ?? ''))

# Convert Unix ms timestamp to ISO 8601 when possible.
$timeDisplay = $timestamp
if ($timestamp -match '^\d{10,13}$') {
  try {
    $tsMs = [long]$timestamp
    $tsSec = [long]($tsMs / 1000)
    $dt = [System.DateTimeOffset]::FromUnixTimeSeconds($tsSec).UtcDateTime
    $timeDisplay = $dt.ToString('yyyy-MM-ddTHH:mm:ssZ')
  } catch {
    $timeDisplay = $timestamp
  }
}

Write-HookLog -Label 'ERROR' -Message "session=$sessionId error_name=$errorName context=$errorContext recoverable=$recoverable timestamp=$timeDisplay"

exit 0
