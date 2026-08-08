# Copilot Hook Scripts

Shell and PowerShell implementations for the Ego Hygiene Copilot agent hook
baseline.  These scripts are invoked by the hook configuration in
[`../.github/hooks/ego-hygiene.json`](../../.github/hooks/ego-hygiene.json).

## Directory layout

```text
scripts/copilot-hooks/
  session-start.sh      Bash — lightweight repository validation
  session-start.ps1     PowerShell — equivalent for Windows
  pre-tool-use.sh       Bash — safety guardrails before tool execution
  pre-tool-use.ps1      PowerShell — equivalent for Windows
  error-occurred.sh     Bash — sanitized failure diagnostics
  error-occurred.ps1    PowerShell — equivalent for Windows
  tests/
    test-pre-tool-use.sh  Automated test fixtures for pre-tool-use.sh
  README.md             This file
```

## Script contract

Each script reads a JSON payload from **stdin** and may write to **stdout**
and/or **stderr**.

### Input

Input is a single JSON object.  The schema varies by hook event; see the
[hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).

Scripts must:
- validate that stdin is valid JSON before extracting fields
- treat all input as untrusted
- never evaluate input as shell code
- never log prompt text, environment variable values, tokens, or file contents

### Output

| Hook            | stdout expected                                                 |
|-----------------|-----------------------------------------------------------------|
| `sessionStart`  | None (output is ignored; exit 0 signals success)                |
| `preToolUse`    | JSON: `{"permissionDecision":"allow"|"deny", "permissionDecisionReason":"..."}` |
| `errorOccurred` | None (output is ignored; exit 0 always)                         |

Stderr is for diagnostic messages only and is not processed by the runtime.

## Dependencies

- **Bash scripts**: require `bash` ≥ 4.x and `jq` ≥ 1.6.
  When `jq` is absent the scripts degrade gracefully: `session-start.sh` and
  `error-occurred.sh` skip JSON validation; `pre-tool-use.sh` defaults to
  **allow** with a warning.
- **PowerShell scripts**: require PowerShell 7.0+ (`pwsh`).

## Running tests

```bash
bash scripts/copilot-hooks/tests/test-pre-tool-use.sh
```

Or via Taskfile:

```bash
task copilot:hooks:test
```

## Validating the JSON configuration

```bash
jq . .github/hooks/ego-hygiene.json
```

Or via Taskfile:

```bash
task copilot:hooks:validate
```

## Adding a new hook

1. Add a new entry to `.github/hooks/ego-hygiene.json` following the existing
   pattern (`"type": "command"`, explicit `timeoutSec`, both `bash` and
   `powershell` fields, `"cwd": "."`).
2. Create the Bash implementation under `scripts/copilot-hooks/`.
3. Create the PowerShell equivalent.
4. Add test fixtures to `scripts/copilot-hooks/tests/`.
5. Update `.github/hooks/README.md` to document the new hook.
6. Run both validation and test Taskfile commands before committing.

## Security notes

- Scripts never evaluate input as code.
- Scripts never log prompt text, token values, or environment variables.
- The `preToolUse` hook is **fail-closed** on non-zero exit: a crash denies
  the tool call.  A timeout is **fail-open**: execution proceeds.
- These scripts are repository guardrails, not a complete security sandbox.
  A determined agent can construct commands that bypass pattern matching.
  Use these hooks as defense-in-depth alongside code review and CI.
