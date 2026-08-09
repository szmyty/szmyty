# Architecture

## Repository: szmyty/szmyty

**Status:** Active — clean foundation phase

## Purpose

This repository serves two roles:

1. **GitHub Profile README** — the `README.md` at the repository root is
   rendered as Alan Szmyt's public GitHub profile page.

2. **Reusable template assets** — configuration files, issue forms, task
   definitions, and documentation conventions intended for reuse across
   personal and organisational repositories.

## Directory Responsibilities

| Path | Responsibility |
|------|---------------|
| `README.md` | Active profile README; rendered by GitHub |
| `LICENSE` | MIT license — applies to all content in this repository |
| `.editorconfig` | Shared editor formatting defaults |
| `AGENTS.md` | Agent and contributor guidance for this repository |
| `Taskfile.yml` | Task runner entrypoint; includes modular task files |
| `pyproject.toml` | Python project metadata and active tooling configuration |
| `humans.txt` | Human-readable project metadata |
| `docs/` | Documentation; architecture, roadmap, privacy, audits |
| `.github/` | GitHub configuration: funding, issue templates, PR template |
| `.tasks/` | Modular Taskfile includes (git, agents, security, tests) |
| `.staging/` | In-progress work; not promoted to active files |

## Boundaries

- `.staging/` is preserved but not promoted until explicitly reviewed.
- No speculative or aspirational content exists in active files.
- All production configuration targets `szmyty/szmyty` exclusively.

## Technology

- **Task** — optional task runner (`Taskfile.yml`)
- **Poetry** — Python dependency management
- **GitHub Actions** — CI/CD (`.github/workflows/`)
- **yamllint, ruff** — linting

## Current Status

The repository is in a clean-foundation phase following the reconciliation
described in [szmyty/szmyty#67](https://github.com/szmyty/szmyty/issues/67).
