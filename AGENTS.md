# AGENTS.md

## Repository Identity

- **Repository:** `szmyty/szmyty`
- **Owner:** Alan Szmyt (`@szmyty`)
- **Purpose:** Alan Szmyt's public GitHub profile and reusable README/template assets.
- **License:** MIT

## Repository Layout

```
szmyty/szmyty
├── README.md              # Active GitHub profile README
├── LICENSE                # MIT license
├── .editorconfig          # Editor formatting defaults
├── AGENTS.md              # This file — agent and contributor guidance
├── Taskfile.yml           # Task runner entrypoint (optional, Git-based tasks)
├── pyproject.toml         # Python project metadata and tooling configuration
├── humans.txt             # Human-readable project metadata
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # Current architecture overview
│   ├── ROADMAP.md         # Near-term roadmap
│   └── audits/            # Audit reports
├── .github/               # GitHub configuration
│   ├── FUNDING.yml        # Sponsor configuration
│   ├── ISSUE_TEMPLATE/    # Issue forms
│   └── PULL_REQUEST_TEMPLATE.md
├── .tasks/                # Modular Taskfile includes
│   ├── git.yml            # Git utility tasks
│   ├── agents.yml         # Agent workflow tasks
│   ├── security.yml       # Security audit tasks
│   └── tests.yml          # Test tasks
└── .staging/              # Staged/in-progress work (not promoted yet)
```

## Constraints for Agents

- Do **not** promote content from `.staging/` without explicit instruction.
- Do **not** create speculative or aspirational content in active files.
- Do **not** reference `egohygiene`, `sanctuary`, or `profile-next` in any
  production configuration or documentation outside explicit migration notes.
- Do **not** introduce new dependency groups in `pyproject.toml` for
  libraries that are not currently in active use.
- All external URLs in configuration files must point to `szmyty/szmyty`
  or verified external services.

## Identity Check

When modifying configuration files, verify that:

1. No file references `egohygiene/egohygiene`, `egohygiene/sanctuary`,
   or `profile-next` as a production target.
2. No file contains unresolved template tokens such as `{{TOKEN}}`.
3. All relative asset links in `README.md` point to existing files.

## Working with Tasks

Task is optional. Run `task --list` to see available commands.
All task commands must point to real paths and must either succeed or
report a precise missing optional dependency message.

## Python Environment

This repository uses [Poetry](https://python-poetry.org/) for Python
dependency management. The Python version requirement is `>=3.12,<4.0`.

Install the development environment:

```sh
poetry install --with dev,lint,security
```
