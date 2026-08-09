# Development Guide

**Repository:** `szmyty/szmyty`
**Status:** Active

This document covers everything needed to work on this repository from a fresh
checkout, including setup, the command surface, local testing, and fixture usage.

---

## 1. Prerequisites

| Tool | Minimum version | Purpose | Required |
|------|----------------|---------|----------|
| Python | 3.12 | Runtime and tooling | Yes |
| Poetry | 2.1.x | Dependency management | Yes |
| Git | 2.x | Version control | Yes |
| Task | 3.x | Optional task runner | No |
| yamllint | 1.x | YAML linting | No (installed via Poetry) |
| ruff | 0.11.x | Python linting | No (installed via Poetry) |
| act | latest | Local Actions runner | No — best-effort only |

Python and Poetry are the only hard requirements.  All other tools are installed
as Poetry dev-dependencies or are truly optional.

---

## 2. Setup

### Clone and bootstrap

```sh
git clone https://github.com/szmyty/szmyty.git
cd szmyty
python -m pip install poetry==2.1.4
poetry install --with lint,test
```

This creates a `.venv/` inside the project directory (`poetry.toml` sets
`virtualenvs.in-project = true`).

### Activate the environment (optional)

```sh
# Activate for the current shell session
source .venv/bin/activate

# Or prefix commands with `poetry run`
poetry run python -m pytest
```

---

## 3. Command Surface

All commands are available through `poetry run` regardless of whether Task is
installed.

### Validate

```sh
# Validate profile inputs (schemas, evidence catalog, asset presence)
poetry run python -m tools.profile_builder.cli validate

# Validate profile SVG and image assets
poetry run python profile/validate_assets.py assets/profile

# Run both validations (local parity with CI)
poetry run python -m tools.profile_builder.cli validate && \
  poetry run python profile/validate_assets.py assets/profile
```

### Test

```sh
# Run full test suite
poetry run python -m pytest

# Run a specific test file
poetry run python -m pytest tests/test_modules.py

# Run tests with verbose output
poetry run python -m pytest -v

# Run only workflow/site tests (parity with pages.yml CI job)
poetry run python -m pytest tests/test_workflows.py -k "workflow or site"
```

### Lint

```sh
# Lint Python source
poetry run ruff check .

# Lint YAML files (workflows, config)
poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml

# Identity check — rejects stale source-repository names
bash .tasks/check-identity.sh
```

### Update profile (local refresh)

Run each module fetch step and regenerate README regions:

```sh
# Fetch the GitHub engineering dashboard (requires GITHUB_TOKEN)
GITHUB_TOKEN=<your-pat> \
  poetry run python -m tools.modules.github_dashboard \
    --output-dir profile/artifacts/github-dashboard

# Refresh music highlight from hand-authored YAML
poetry run python -m tools.modules.music_highlight \
  --input profile/content/music-highlight.yml \
  --output profile/artifacts/music-highlight/music.yml

# Render all README regions from refreshed artifacts
poetry run python -m tools.modules.update_readme
```

When `GITHUB_TOKEN` is absent the GitHub-backed modules fall back to the
committed fixture caches.  See [§ 5 Fixtures](#5-fixtures) below.

### Render one module

Re-render a single README region without running all modules:

```sh
# Re-render only the music-highlight region
poetry run python -m tools.modules.update_readme --module music-highlight
```

### Validate site

```sh
# Validate Pages workflow and static site inputs
poetry run python -m pytest tests/test_workflows.py -k "workflow or site"

# Capture the deterministic README preview for the interactive observatory
python tools/capture_interactive_showcase_preview.py \
  --output profile/artifacts/interactive-showcase/preview.png
```

### Clean generated caches

Remove transient generated files without deleting committed fixtures or tracked
artifacts:

```sh
# Remove virtualenv (force-reinstall on next poetry install)
rm -rf .venv

# Remove pytest cache
rm -rf .pytest_cache

# Remove ruff cache
rm -rf .ruff_cache

# Remove Python bytecode
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

> **Do not delete** committed artifact caches
> (`profile/artifacts/*/cache.json`, `profile/artifacts/music-highlight/music.yml`).
> Those files are tracked and serve as fallbacks in CI.

### Task shortcuts (optional)

If Task is installed (`brew install go-task` or equivalent):

```sh
task --list                # Show all available commands
task lint                  # yamllint + ruff
task tests:pytest          # Run full test suite
task validate-profile      # Profile input validation
task validate-site         # Site and workflow tests
task update-profile        # Local module refresh
task check-identity        # Identity constraint check
```

---

## 4. Local Workflow Parity with CI

| CI job | Local equivalent |
|--------|----------------|
| `ci.yml` → validate | `poetry run python -m tools.profile_builder.cli validate` |
| `ci.yml` → assets | `poetry run python profile/validate_assets.py assets/profile` |
| `ci.yml` → lint Python | `poetry run ruff check tests` |
| `ci.yml` → lint YAML | `poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml` |
| `ci.yml` → tests | `poetry run python -m pytest` |
| `update-profile.yml` | `task update-profile` (requires `GITHUB_TOKEN`) |
| `pages.yml` → validate | `poetry run python -m pytest tests/test_workflows.py -k "workflow or site"` |

`act` provides best-effort local runner parity for workflow syntax.  GitHub
Pages OIDC, deployment environments, and hosted Pages infrastructure are not
fully reproducible under `act`.

---

## 5. Fixtures

Fixtures provide deterministic inputs for tests and for offline module
rendering.  They live in `profile/fixtures/` and must contain sanitized
synthetic data only — no real personal measurements, coordinates, or auth
payloads.

| Fixture file | Used by | Purpose |
|-------------|---------|---------|
| `profile/fixtures/github-dashboard.json` | `tests/test_github_dashboard.py`, `tests/test_modules.py` | Synthetic GitHub dashboard snapshot |
| `profile/fixtures/github-metrics.json` | `tests/test_modules.py`, `test_profile_builder_*` | Synthetic legacy GitHub metrics response |
| `profile/fixtures/recent-activity.json` | `tests/test_modules.py` | Synthetic legacy activity feed |
| `profile/fixtures/music-highlight.yml` | `tests/test_modules.py` | Synthetic music entry |

When a module artifact cache is absent, the module falls back to the
corresponding committed fixture.  Tests always use fixtures and never call live
APIs.

---

## 6. Adding or Modifying a Module

1. Add the canonical module declaration to `profile/content/modules-registry.yml`
   with `enabled: true`, provider metadata, and the correct region markers.
2. Mirror the README-owned subset in `profile/content/modules.yml`.
3. Create the Jinja2 template in `profile/templates/<name>.md.j2`.
4. Create or update the corresponding Python module under `tools/modules/`.
5. Add a fixture file in `profile/fixtures/` with sanitized synthetic data.
6. Add tests in `tests/` covering the fetch, render, and region-update logic.
7. Run `poetry run python -m tools.profile_builder.cli validate` to confirm
   the new module passes validation.
8. Update `docs/ARCHITECTURE.md` module inventory if the module is new.
9. Verify the `profile/content/evidence.yml` catalog covers any new public
   claims the module introduces.

Consult `docs/PRIVACY.md` before adding any data source to confirm it is on
the allow-list.

---

## 7. Adding or Rotating a Secret

1. Confirm the secret is necessary — see the environment variable table in
   `docs/ARCHITECTURE.md`.
2. Add the secret to the repository's Settings → Secrets and variables →
   Actions.
3. Reference it in the workflow with `${{ secrets.SECRET_NAME }}`.
4. Update the environment variable table in `docs/ARCHITECTURE.md`.
5. Document the rotation procedure in `docs/RUNBOOK.md`.
6. Never commit secret values to any file.

---

## 8. Dependency Updates

```sh
# Update a single dependency
poetry add <package>@<version>

# Update all dependencies within constraints
poetry update

# Lock without installing
poetry lock

# Check for outdated packages
poetry show --outdated
```

After updating `poetry.lock`, commit both `pyproject.toml` and `poetry.lock`.
CI caches the virtualenv keyed on `poetry.lock`; a changed lock file
invalidates the cache and triggers a fresh install.

---

## 9. Editor Configuration

`.editorconfig` at the repository root sets formatting defaults for all files.
Most modern editors respect this automatically.  The Python tooling enforces
additional constraints via `pyproject.toml` (`ruff`, `pytest` configuration).

---

## 10. Quality Tool Boundary

**Authoritative tools** for this repository until further notice:

| Tool | Role | Installed via |
|------|------|--------------|
| Poetry | Dependency management | system |
| Ruff | Python linting and import ordering | `poetry install --with lint` |
| yamllint | YAML linting | `poetry install --with lint` |
| pytest | Test runner | `poetry install --with test` |
| `profile/validate_assets.py` | Asset presence and format validation | repository |
| `profile/validate_evidence.py` | Evidence catalog validation | repository |
| `tools/profile_builder/cli.py` | Profile input validation | repository |

These tools constitute the authoritative validation gate and map directly to
the CI jobs in `.github/workflows/ci.yml`.  No additional linting or quality
tool is required to pass CI.

### Future migration seam: `egolint`

`egolint` is an independently-developed linting tool that may replace or
supplement Ruff for this repository's Python quality checks once it is
released and validated.  Until that release:

- Do **not** import, vendor, mock, or depend on `egolint` in any repository
  file, test, or workflow.
- Do **not** add an `egolint` configuration stub to `pyproject.toml` or
  `.github/workflows/`.
- When `egolint` reaches a stable public release and is validated against
  this codebase, migrate by replacing the `poetry run ruff check .` invocation
  in `ci.yml` and the equivalent local command above, then remove this note.

The migration command will be:

```sh
# Future — not yet available; do not run
# poetry run egolint check .
```

Until that command is available and tested, continue using Ruff as documented
in § 3 above.
