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
| `README.md` | Active profile README; rendered by GitHub; partially generated |
| `LICENSE` | MIT license — applies to all content in this repository |
| `.editorconfig` | Shared editor formatting defaults |
| `AGENTS.md` | Agent and contributor guidance for this repository |
| `Taskfile.yml` | Task runner entrypoint; includes modular task files |
| `pyproject.toml` | Python project metadata and active tooling configuration |
| `humans.txt` | Human-readable project metadata |
| `assets/profile/` | Hand-authored SVG/image assets referenced by `README.md` |
| `profile/content/` | Hand-authored module inputs and evidence catalog |
| `profile/artifacts/` | Generated module caches (committed; serve as CI fallbacks) |
| `profile/fixtures/` | Sanitized synthetic test data; never real personal data |
| `profile/templates/` | Jinja2 templates for generated README regions |
| `profile/schemas/` | JSON schemas for YAML content files |
| `site/` | Companion static site; deployed to GitHub Pages by `pages.yml` |
| `tools/` | Python module scripts and profile-builder library |
| `tests/` | pytest test suite |
| `templates/` | Reusable repository template assets for external use |
| `docs/` | Documentation: architecture, design, content, development, runbook, roadmap, migration, privacy |
| `.github/` | GitHub configuration: funding, issue templates, PR template, workflows |
| `.tasks/` | Modular Taskfile includes (git, agents, security, tests) |

## Boundaries

- No speculative or aspirational content exists in active files.
- All production configuration targets `szmyty/szmyty` exclusively.
- The modules listed under "Prohibited Modules" below must never be implemented
  or revived from historical experimental artifacts.

## Content and Data Flow

```
Hand-authored inputs                 Generated outputs
─────────────────                    ─────────────────
profile/content/evidence.yml   ──►  (gates what appears in README)
profile/content/modules.yml    ──►  defines README region markers
profile/content/music-highlight.yml ──► profile/artifacts/music-highlight/music.yml
                                         │
GitHub API (GITHUB_TOKEN)       ──►  profile/artifacts/github-metrics/cache.json
GitHub API (GITHUB_TOKEN)       ──►  profile/artifacts/recent-activity/cache.json
                                         │
profile/artifacts/*             ──►  tools/modules/update_readme.py
profile/templates/*.md.j2       ──►  README.md (generated regions only)
```

Hand-authored prose in `README.md` outside module markers is never modified
by the pipeline.

## Module Lifecycle

Each active profile module follows this lifecycle:

1. **Declaration** — entry in `profile/content/modules.yml` with
   `enabled: true`, region markers, template path, and artifact path.
2. **Fetch** — a Python script under `tools/modules/` retrieves or processes
   data and writes a cache artifact to `profile/artifacts/<name>/`.
3. **Render** — `tools/modules/update_readme.py` reads the artifact, renders
   the Jinja2 template, and writes the output between the region markers in
   `README.md`.
4. **Commit** — the `update-profile.yml` workflow commits changed artifacts
   and the updated `README.md` to `master`.
5. **Fallback** — if the fetch step fails, the previously committed artifact
   cache is used.  The README is re-rendered from stale but valid data.

Disabling a module (`enabled: false` in `modules.yml`) leaves its markers in
`README.md` empty without removing them.

## Technology

- **Task** — optional task runner (`Taskfile.yml`)
- **Poetry** — Python dependency management
- **GitHub Actions** — CI/CD (`.github/workflows/`)
- **yamllint, ruff** — linting
- **pytest** — test runner
- **Jinja2** — README template rendering
- **Pydantic** — schema validation for profile content

## Automation

The production workflow set is intentionally limited to three files:

| Workflow | Responsibility | Local parity |
|----------|----------------|--------------|
| `ci.yml` | Read-only validation for pull requests, pushes, and manual diagnosis | `poetry run python -m tools.profile_builder.cli validate && poetry run python -m pytest` |
| `update-profile.yml` | Scheduled/manual refresh of public module artifacts and README regions | `task update-profile` (requires `GITHUB_TOKEN`) |
| `pages.yml` | Validate the committed static site and deploy `site/` to GitHub Pages | `poetry run python -m pytest tests/test_workflows.py -k "workflow or site"` |

`act` use is best-effort only for syntax and basic runner parity. GitHub Pages
OIDC, deployment environments, and hosted Pages infrastructure are not fully
reproducible under `act`.

## Environment Variables

This table is the canonical reference for all environment variables used by
workflows and local tooling.  Do not add secrets for deferred or prohibited
features.

| Variable | Required | Secret | Scope | Module / owner | Value / Notes | Disable behavior | Rotation procedure |
|----------|----------|--------|-------|---------------|---------------|-----------------|-------------------|
| `GITHUB_TOKEN` | Yes (CI) | No — automatic | GitHub Actions only | `github-metrics`, `recent-activity` | Injected automatically by Actions (`github.token`) | Module falls back to committed artifact cache | No rotation needed; token expires per-run |
| `POETRY_VIRTUALENVS_IN_PROJECT` | No | No | Local and CI | Build tooling | Set to `true` in `poetry.toml`; creates `.venv/` inside the project | Virtualenv is created outside the project directory | Not applicable |

### Notes

- `GITHUB_TOKEN` is injected automatically by GitHub Actions with read-only
  `contents: read` scope for most jobs.  The `commit` job in
  `update-profile.yml` uses `contents: write` to push the refreshed profile.
- No additional secrets beyond the automatic `GITHUB_TOKEN` are required for
  the current production feature set.
- Do not add secrets for health, location, weather, or Oura modules — those
  modules are permanently prohibited.

## Prohibited Modules

The following modules are permanently prohibited and must not be built or
revived:

| Module | Reason |
|--------|--------|
| `fetch-location` / `generate-location-card` | Location data is on the deny-list |
| `fetch-weather` / `generate-weather-card` | Location-derived weather is on the deny-list |
| `fetch-oura` / `generate-oura-dashboard` / `generate-oura-mood` | Health/biometric data is on the deny-list |

See `docs/PRIVACY.md` for the full public-data deny-list.

## Current Status

The repository is in a clean-foundation phase following the reconciliation
described in [szmyty/szmyty#67](https://github.com/szmyty/szmyty/issues/67).
The site companion is deployed to GitHub Pages.  The three production workflows
are active.
