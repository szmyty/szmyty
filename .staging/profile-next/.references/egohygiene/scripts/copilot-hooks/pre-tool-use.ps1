#Requires -Version 7.0
# SPDX-License-Identifier: MIT
#
# pre-tool-use.ps1 — Copilot preToolUse safety guardrail for Ego Hygiene (PowerShell)
#
# Inspects proposed tool calls before Copilot executes them and denies
# clearly unsafe patterns.  Behavior mirrors pre-tool-use.sh.
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
# Trust boundary: Input is never evaluated as code.  No environment values
# or prompt text are logged.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

$script:HookName    = 'pre-tool-use'
$script:ShellTools  = @('bash', 'sh', 'zsh', 'powershell', 'pwsh', 'cmd')

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

function Write-Allow {
  <#
  .SYNOPSIS
  Emits a JSON allow decision to stdout.
  #>
  Write-Output '{"permissionDecision":"allow"}'
}

function Write-Deny {
  <#
  .SYNOPSIS
  Emits a JSON deny decision with a sanitized reason to stdout.
  .PARAMETER Reason
  Human-readable reason shown to the agent.
  #>
  param([Parameter(Mandatory)][string]$Reason)
  # Sanitize: strip newlines, limit to 200 characters.
  $safe = ($Reason -replace '[\r\n]', '') -replace '^(.{0,200}).*$', '$1'
  $json = [System.Text.Json.JsonSerializer]::Serialize(@{
    permissionDecision       = 'deny'
    permissionDecisionReason = $safe
  })
  Write-Output $json
}

function Test-DeniedPattern {
  <#
  .SYNOPSIS
  Checks whether a command string matches any denied patterns.
  Returns $true when the command should be denied.
  Emits the deny decision JSON to stdout when denying.
  .PARAMETER Cmd
  Command string to inspect (not evaluated as code).
  #>
  param([Parameter(Mandatory)][string]$Cmd)

  # Normalise whitespace.
  $n = $Cmd -replace '\s+', ' '

  # 1. Destructive filesystem targeting root or home.
  # Two-step: confirm rm with recursive+force flags, then check target path.
  if ($n -match 'rm\s') {
    if ($n -match '\s-(rf|fr|[^\s]*r[^\s]*f[^\s]*)(\s|$)') {
      if ($n -match '\s(/\*?|~/?)(\s|$)') {
        Write-Deny 'Destructive recursive deletion targeting the filesystem root or home directory is not permitted.'
        return $true
      }
    }
  }

  # 2. Force pushes to protected branches.
  if ($n -match 'git\s+.*push\s+.*--force(-with-lease)?\s+.*(origin|upstream)\s+(main|master|develop)\b') {
    Write-Deny 'Force push to a protected branch (main, master, develop) is not permitted.'
    return $true
  }
  if ($n -match 'git\s+.*push\s+.*--force(-with-lease)?\s+.*(origin|upstream)/(main|master|develop)\b') {
    Write-Deny 'Force push to a protected branch (main, master, develop) is not permitted.'
    return $true
  }

  # 3. Destructive Git history rewrites.
  if ($n -match 'git\s+.*filter-branch') {
    Write-Deny 'git filter-branch rewrites history and is not permitted. Use git filter-repo for intentional history surgery.'
    return $true
  }
  if ($n -match 'git\s+.*reset\s+.*--hard\s+(origin|upstream)/') {
    Write-Deny 'git reset --hard to a remote ref is not permitted as it discards local commits.'
    return $true
  }

  # 4. Commands that may print secret environment variables.
  if ($n -imatch '(printenv|\benv\b|\$(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY|ACCESS_KEY|AUTH|CREDENTIAL))') {
    Write-Deny 'Commands that may expose secret environment variables are not permitted.'
    return $true
  }

  # 5. Reading well-known credential files.
  if ($n -match '(cat|less|more|head|tail|Get-Content|type)\s+.*(\.netrc|\.ssh.id_|\.aws.credentials|\.aws.config|\.env\b|credentials\.json|keystore|\.pem|\.p12|\.pfx)') {
    Write-Deny 'Reading credential files is not permitted.'
    return $true
  }

  # 6. Broad recursive permission changes (chmod -R 777 on / or ~).
  # Two-step: confirm recursive mode and broad permission, then check target.
  if ($n -match 'chmod\s+.*-[^\s]*R[^\s]*\s+(777|a\+rwx)') {
    if ($n -match '(777|a\+rwx)\s+(/|~)') {
      Write-Deny 'Broad recursive permission changes on the filesystem root or home directory are not permitted.'
      return $true
    }
  }

  # 7. Unreviewed package publication.
  # Two-step: match the publication command, then verify the safe flag is absent.
  if ($n -match 'npm\s+publish(\s|$)') {
    if ($n -notmatch '--dry-run') {
      Write-Deny 'Package publication without explicit dry-run or review flag is not permitted.'
      return $true
    }
  }
  if ($n -match 'pub\s+publish(\s|$)') {
    if ($n -notmatch '--dry-run') {
      Write-Deny 'Package publication without explicit dry-run or review flag is not permitted.'
      return $true
    }
  }
  if ($n -match 'twine\s+upload(\s|$)') {
    if ($n -notmatch '--repository\s+testpypi') {
      Write-Deny 'Package publication without explicit dry-run or review flag is not permitted.'
      return $true
    }
  }

  return $false
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Read stdin once; never log its raw contents.
try {
  $raw = [Console]::In.ReadToEnd()
} catch {
  Write-HookLog -Label 'WARN' -Message 'Could not read stdin'
  Write-Allow
  exit 0
}

# Validate JSON.
try {
  $payload = $raw | ConvertFrom-Json -AsHashtable -ErrorAction Stop
} catch {
  Write-HookLog -Label 'WARN' -Message 'preToolUse payload is not valid JSON; defaulting to allow'
  Write-Allow
  exit 0
}

$toolName = $payload['toolName'] ?? ''
Write-HookLog -Label 'INFO' -Message "preToolUse: tool=$toolName"

# Only inspect shell-executing tools.
if ($toolName -notin $script:ShellTools) {
  Write-Allow
  exit 0
}

# Extract command string from toolArgs.
$toolArgs = $payload['toolArgs']
$cmd = ''
if ($toolArgs -is [hashtable]) {
  $cmd = $toolArgs['command'] ?? $toolArgs['input'] ?? ''
}

if ([string]::IsNullOrWhiteSpace($cmd)) {
  Write-Allow
  exit 0
}

# Run pattern checks.
if (Test-DeniedPattern -Cmd $cmd) {
  exit 0
}

Write-Allow
exit 0
