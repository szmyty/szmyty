# GitHub Copilot Hooks — Ego Hygiene

This directory contains the repository-level hook configuration for GitHub
Copilot cloud agent and Copilot CLI.

## What are Copilot hooks?

Copilot hooks are external commands that execute at specific points in the
agent lifecycle.  They allow repositories to enforce lightweight guardrails,
emit diagnostics, and integrate custom automation without modifying the agent
itself.

Hooks are configured in JSON files under `.github/hooks/` and committed to
the default branch.  The Copilot runtime discovers and executes them
automatically.

Reference: [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)

## Agent surfaces

| Surface               | Reads `.github/hooks/` | Notes                                         |
|-----------------------|------------------------|-----------------------------------------------|
| Copilot cloud agent   | ✅ Yes                 | Only `bash` entries honored (Linux sandbox)   |
| Copilot CLI           | ✅ Yes                 | Both `bash` and `powershell` entries honored  |

## Supported lifecycle events

| Event               | Fires when                                      | Output processed |
|---------------------|-------------------------------------------------|------------------|
| `sessionStart`      | A new or resumed session begins                 | Optional         |
| `preToolUse`        | Before each tool executes                       | Yes — allow/deny |
| `postToolUse`       | After each tool completes successfully          | Yes              |
| `errorOccurred`     | An error occurs during execution                | No               |
| `agentStop`         | The main agent finishes a turn                  | Yes              |
| `sessionEnd`        | The session terminates                          | No               |
| `userPromptSubmitted` | The user submits a prompt                     | No               |
| `subagentStart`     | A subagent is spawned                           | Optional         |
| `subagentStop`      | A subagent completes                            | Yes              |

See the [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference) for full details.

## Enabled hooks

### `sessionStart` → `scripts/copilot-hooks/session-start.sh`

Performs lightweight repository validation at the start of every session.

- Confirms the session starts from the repository root.
- Checks that expected sentinel files exist (`Taskfile.yml`,
  `.github/hooks/ego-hygiene.json`).
- Prints a concise environment summary: OS name and Git revision.
- Warns when recommended tooling (`git`, `jq`, `task`) is absent.

This hook does **not** install dependencies, mutate source files, run tests,
or perform any expensive setup.

### `preToolUse` → `scripts/copilot-hooks/pre-tool-use.sh`

Inspects proposed shell commands before execution and denies clearly unsafe
patterns.  Applies only to shell-executing tools (`bash`, `sh`, `zsh`,
`powershell`, `pwsh`, `cmd`).  All other tool types are allowed without
inspection.

Blocked categories and rationale:

| Category | Example | Rationale |
|---|---|---|
| Destructive filesystem (root/home) | `rm -rf /`, `rm -rf ~/` | Irreversible data loss |
| Force push to protected branches | `git push --force origin main` | History rewrite on shared branch |
| Git history rewrite | `git filter-branch` | Irreversible history mutation |
| Hard reset to remote ref | `git reset --hard origin/main` | Discards committed work |
| Secret variable exposure | `printenv`, `echo $SECRET_KEY` | Leaks credentials to logs |
| Credential file reads | `cat ~/.netrc`, `cat .env` | Exposes stored secrets |
| Broad chmod on root/home | `chmod -R 777 /` | Unsafe permission escalation |
| Unreviewed publication | `npm publish`, `twine upload` | Accidental release |

This hook is conservative.  Ordinary development commands that mutate files
inside the working tree are allowed.

### `errorOccurred` → `scripts/copilot-hooks/error-occurred.sh`

Emits a one-line sanitized diagnostic to stderr when an error occurs.

Logged fields: session ID, error name, error context, recoverability flag,
and timestamp.

Does **not** log: error message text, stack traces, prompt content,
environment variables, tokens, file contents, or any other sensitive data.

## Deferred hooks

The following hooks are intentionally not enabled.

| Hook | Rationale for deferral | Future justification |
|---|---|---|
| `userPromptSubmitted` | Fires on every user message — capturing prompt events risks logging sensitive content inadvertently | Enable only if a narrow, audited use case requires per-prompt validation |
| `postToolUse` | Post-execution inspection adds latency with no current use case | Enable if result auditing or structured logging is required |
| `sessionEnd` | Ephemeral sandbox discards output when the cloud agent job ends | Enable if a persisted completion record is sent via HTTP to an allow-listed endpoint |
| `agentStop` | No current requirement to block or continue agent turns | Enable if automated quality gates over agent output are needed |
| `subagentStop` | No current subagent lifecycle requirement | Enable if per-subagent outcome tracking is required |

## Script input and output

Each script reads a JSON payload from **stdin**.  The payload schema is
defined by the [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).

`preToolUse` scripts write a JSON decision object to **stdout**:

```json
{"permissionDecision": "allow"}
{"permissionDecision": "deny", "permissionDecisionReason": "..."}
```

All scripts write diagnostic messages to **stderr** only.

## Local validation

Validate the JSON configuration:

```bash
task copilot:hooks:validate
# or directly:
jq . .github/hooks/ego-hygiene.json
```

Run the automated test fixtures:

```bash
task copilot:hooks:test
# or directly:
bash scripts/copilot-hooks/tests/test-pre-tool-use.sh
```

## Cross-platform behavior

| Platform | Copilot cloud agent | Copilot CLI |
|---|---|---|
| Linux | `bash` scripts used | `bash` scripts used |
| macOS | N/A (cloud agent is Linux) | `bash` scripts used |
| Windows | N/A (cloud agent is Linux) | `powershell` scripts used |

PowerShell scripts (`.ps1`) are functional equivalents of the Bash scripts
and require PowerShell 7.0+ (`pwsh`).

## Security limitations

- Hooks are **repository guardrails** and **defense-in-depth**, not a
  complete security sandbox.
- Pattern matching can be bypassed by crafting obfuscated commands.
- The `preToolUse` hook is **fail-closed** on script errors (non-zero exit
  denies the tool call) but **fail-open** on timeouts (execution proceeds).
- Scripts receive untrusted JSON input.  All input is validated before use
  and never evaluated as code.
- No hook logs prompt text, tokens, environment variables, or file contents.
- No hook makes external network calls.

## Adding a new hook

1. Identify the lifecycle event and confirm it provides concrete value.
2. Add an entry to `ego-hygiene.json` with `"type": "command"`, `timeoutSec`,
   `bash`, `powershell`, and `"cwd": "."`.
3. Create `scripts/copilot-hooks/<hook-name>.sh` (Bash) and
   `scripts/copilot-hooks/<hook-name>.ps1` (PowerShell).
4. Follow the Bash standards: `#!/usr/bin/env bash`, `set -euo pipefail`,
   `printf` over `echo`, shdoc comments, quoted expansions, no `eval`.
5. Add test fixtures to `scripts/copilot-hooks/tests/`.
6. Run `task copilot:hooks:validate` and `task copilot:hooks:test`.
7. Update this README.

## Troubleshooting

**Hook not executing in cloud agent**
- Confirm the JSON file is committed to the repository's default branch.
- Validate JSON syntax: `jq . .github/hooks/ego-hygiene.json`
- Confirm the scripts are executable: `ls -l scripts/copilot-hooks/*.sh`

**`preToolUse` blocking expected commands**
- Run the test suite to reproduce: `task copilot:hooks:test`
- Review the blocked patterns in `scripts/copilot-hooks/pre-tool-use.sh`
- The pattern matching section is clearly documented — narrow or remove a
  pattern and add a test case confirming the allow behaviour.

**`jq` not available**
- `session-start.sh` and `error-occurred.sh` skip JSON validation and emit
  a warning.
- `pre-tool-use.sh` defaults to **allow** with a warning.
- Install `jq` to restore full validation: most package managers provide it
  as `jq`.
