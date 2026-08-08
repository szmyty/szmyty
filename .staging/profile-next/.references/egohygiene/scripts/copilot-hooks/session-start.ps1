#Requires -Version 7.0
# SPDX-License-Identifier: MIT
#
# session-start.ps1 — Copilot sessionStart hook for Ego Hygiene (PowerShell)
#
# Performs lightweight repository validation at the start of every Copilot
# CLI session on Windows.  Behavior mirrors session-start.sh.
#
# Input (stdin): JSON payload with fields:
#   sessionId  — unique session identifier
#   timestamp  — Unix timestamp in milliseconds
#   cwd        — working directory reported by the Copilot runtime
#   source     — "startup" | "resume" | "new"
#
# Output: none required; exits 0 on success.
#
# Docs: https://docs.github.com/en/copilot/reference/hooks-reference

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

$script:HookName = 'session-start'
$script:RequiredFiles = @(
  'Taskfile.yml'
  '.github/hooks/ego-hygiene.json'
)
$script:RecommendedTools = @('git', 'jq', 'task')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Write-HookLog {
  <#
  .SYNOPSIS
  Writes a labelled diagnostic line to stderr.
  .PARAMETER Label
  Log level label (INFO, WARN, ERROR).
  .PARAMETER Message
  Human-readable message — must not contain secrets.
  #>
  param(
    [Parameter(Mandatory)][string]$Label,
    [Parameter(Mandatory)][string]$Message
  )
  [Console]::Error.WriteLine("[copilot/$script:HookName] ${Label}: ${Message}")
}

function Read-StdinPayload {
  <#
  .SYNOPSIS
  Reads stdin and attempts to parse it as JSON.
  Returns a hashtable (empty when parsing fails).
  #>
  try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { return @{} }
    return $raw | ConvertFrom-Json -AsHashtable -ErrorAction Stop
  } catch {
    Write-HookLog -Label 'WARN' -Message 'sessionStart payload is not valid JSON; continuing with defaults'
    return @{}
  }
}

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

function Test-RepositoryRoot {
  <#
  .SYNOPSIS
  Confirms execution starts from the repository root.
  #>
  if (-not (Test-Path 'Taskfile.yml')) {
    Write-HookLog -Label 'WARN' -Message 'Taskfile.yml not found — session may not be running from the repository root'
    return $false
  }
  Write-HookLog -Label 'INFO' -Message 'Repository root confirmed'
  return $true
}

function Test-RequiredFiles {
  <#
  .SYNOPSIS
  Confirms that expected sentinel files are present.
  #>
  $missing = $false
  foreach ($file in $script:RequiredFiles) {
    if (-not (Test-Path $file)) {
      Write-HookLog -Label 'WARN' -Message "Expected file not found: $file"
      $missing = $true
    }
  }
  if (-not $missing) {
    Write-HookLog -Label 'INFO' -Message 'Required repository files present'
  }
}

function Test-RecommendedTools {
  <#
  .SYNOPSIS
  Warns when recommended tooling is unavailable on PATH.
  #>
  foreach ($tool in $script:RecommendedTools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
      Write-HookLog -Label 'WARN' -Message "Recommended tool not found on PATH: $tool"
    }
  }
}

function Write-EnvironmentSummary {
  <#
  .SYNOPSIS
  Prints a concise environment summary (no secrets or environment values).
  #>
  $rev = '(unknown)'
  try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
      $rev = (git rev-parse --short HEAD 2>$null) ?? '(unavailable)'
    }
  } catch {
    $rev = '(unavailable)'
  }

  Write-HookLog -Label 'INFO' -Message "OS: $([System.Environment]::OSVersion.Platform)"
  Write-HookLog -Label 'INFO' -Message "Repository revision: $rev"
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

$null = Read-StdinPayload   # Consume stdin; do not log its contents.

Write-EnvironmentSummary
$null = Test-RepositoryRoot
Test-RequiredFiles
Test-RecommendedTools

Write-HookLog -Label 'INFO' -Message 'Session validation complete'
exit 0
