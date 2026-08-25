# Development Guide

**Repository:** `szmyty/szmyty`
**Status:** Active

This guide covers setup, local validation, snapshot-module development, and the
live telemetry credential boundary.

---

## 1. Prerequisites

| Tool | Minimum version | Purpose | Required |
|------|----------------|---------|----------|
| Python | 3.12 | Runtime and tooling | Yes |
| Poetry | 2.1.x | Dependency management | Yes |
| Git | 2.x | Version control | Yes |
| Task | 3.x | Optional task runner | No |
| act | current | Best-effort local Actions syntax/runner parity | No |

Ruff, yamllint, and pytest are installed through Poetry groups.

---

## 2. Bootstrap

```sh
git clone https://github.com/szmyty/szmyty.git
cd szmyty
python -m pip install poetry==2.1.4
poetry install --with lint,test
```

`poetry.toml` keeps the virtual environment in `.venv/`.

Optional shell activation:

```sh
source .venv/bin/activate
```

All documented commands work without activation when prefixed with
`poetry run`.

---

## 3. Validation Surface

Run the complete gate before a PR is ready:

```sh
poetry run python -m tools.profile_builder.cli validate
poetry run python profile/validate_assets.py assets/profile
poetry run python -m pytest
poetry run ruff check .
poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml
bash .tasks/check-identity.sh
```

Useful targeted tests:

```sh
poetry run python -m pytest tests/test_weather.py
poetry run python -m pytest tests/test_steam_cards.py
poetry run python -m pytest tests/test_oura_trends.py
poetry run python -m tools.modules.site_companion --check
poetry run python -m pytest tests/test_site_companion.py tests/test_workflows.py
```

Live providers are never required by tests. Provider calls must be mocked or
replaced by synthetic fixtures.

---

## 4. Local Profile Refresh

### GitHub dashboard

```sh
GITHUB_TOKEN="${GITHUB_TOKEN}" \
  poetry run python -m tools.modules.github_dashboard \
  --output-dir profile/artifacts/github-dashboard
```

### Weather

Weather uses the public GitHub profile `location` string and Open-Meteo. It
requires no weather-provider API key.

```sh
GITHUB_TOKEN="${GITHUB_TOKEN}" \
  poetry run python -m tools.modules.weather \
  --output profile/artifacts/weather/cache.json
```

The GitHub token is optional for the public user lookup when running locally,
but Actions supplies `github.token` automatically.

### Steam

```sh
STEAM_WEB_API_KEY="${STEAM_WEB_API_KEY}" \
STEAM_ID64="${STEAM_ID64}" \
  poetry run python -m tools.modules.steam \
  --output profile/artifacts/steam/cache.json
```

Required live configuration:

- `STEAM_WEB_API_KEY`: secret credential from the Steam Web API provider.
- `STEAM_ID64`: public SteamID64 identifier; store as a repository Actions
  variable rather than a secret.

### Oura

Oura Cloud API V2 uses OAuth2. Personal Access Tokens are no longer supported.
The access token must be authorized only for the `daily` scope used by the
profile transformation.

```sh
OURA_ACCESS_TOKEN="${OURA_ACCESS_TOKEN}" \
  poetry run python -m tools.modules.oura_trends \
  --allow-publication \
  --output profile/artifacts/oura-trends/cache.json
```

Do not save access or refresh tokens in `.env` files committed to this
repository. For local work, inject credentials through the shell or a local
secret manager outside the tracked tree.

### Manual music input

```sh
poetry run python -m tools.modules.music_highlight \
  --input profile/content/music-highlight.yml \
  --output profile/artifacts/music-highlight/music.yml
```

### Render README regions

After refreshing one or more module artifacts:

```sh
poetry run python -m tools.modules.update_readme
```

Only enabled modules are rendered. Their templates own only the content between
the corresponding README region markers.

---

## 5. Fixtures and Generated Artifacts

Fixtures live under `profile/fixtures/` and must contain sanitized synthetic
data only.

| Fixture | Module |
|---------|--------|
| `github-dashboard.json` | `github-dashboard` |
| `weather.json` | `weather` |
| `steam.json` | `steam` |
| `oura-trends.json` | `oura-trends` |
| `music-highlight.yml` | `music-highlight` |

### Synthetic-output rule

A fixture may be rendered during tests to exercise the complete SVG path, but
it must be unmistakably synthetic in the artifact contract and the README
template must refuse to present it as live personal data.

### Last-known-good rule

Real provider snapshots in `profile/artifacts/` are committed intentionally so
the public README remains stable during transient provider outages. Never
replace a real cached snapshot with a synthetic fixture while presenting the
result as live/cached real data.

Do not hand-edit generated telemetry values to make them look current.

---

## 6. Adding or Modifying a Module

Follow this order:

1. Define or update the public-data contract in `docs/PRIVACY.md`.
2. If the source is sensitive/location-derived or the output is a new personal
   disclosure, obtain explicit owner approval in a GitHub issue before
   implementation.
3. Add/update the canonical entry in
   `profile/content/modules-registry.yml`.
4. Mirror README marker ownership in `profile/content/modules.yml`.
5. Implement the provider adapter in `tools/modules/`.
6. Normalize before persistence; never write raw provider responses as an
   intermediate tracked file.
7. Add a synthetic fixture.
8. Add the Jinja2 README template.
9. For visual modules, generate desktop/mobile light/dark SVGs.
10. Add deterministic tests for provider parsing, privacy boundaries,
    fallback behavior, synthetic hiding, and rendering.
11. Integrate refresh behavior into the existing `update-profile.yml` workflow
    instead of creating workflow sprawl.
12. Update architecture, content, privacy, and runbook documentation.
13. Run the full validation gate.

Issue #149 is the owner-approval record for the current weather/Steam/Oura
transformations.

---

## 7. Secrets and Variables

Repository configuration lives under GitHub Settings → Secrets and variables →
Actions.

| Name | Kind | Purpose |
|------|------|---------|
| `STEAM_WEB_API_KEY` | Secret | Steam Web API authentication |
| `STEAM_ID64` | Variable | Public Steam account identifier |
| `OURA_ACCESS_TOKEN` | Secret | Oura OAuth2 access token with `daily` scope |
| `GITHUB_TOKEN` | Automatic Actions token | Public GitHub/provider workflow access |

### Adding or rotating a secret

1. Confirm the credential is declared in `docs/ARCHITECTURE.md` and the module
   registry.
2. Add/replace it in Actions secrets; never commit its value.
3. Trigger `Update Profile` manually.
4. Confirm the module metadata reports a live/fresh result.
5. Revoke the previous provider credential when rotation is required.

For Oura, do not attempt to automate secret mutation using a stored single-use
refresh token unless a future architecture explicitly provides a safe external
secret-rotation service. The current design prefers explicit re-authorization
and last-known-good fallback.

---

## 8. Workflow Parity

| CI / workflow | Local equivalent |
|---------------|------------------|
| `ci.yml` validation | `poetry run python -m tools.profile_builder.cli validate` |
| Asset validation | `poetry run python profile/validate_assets.py assets/profile` |
| Python lint | `poetry run ruff check .` |
| YAML lint | `poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml` |
| Tests | `poetry run python -m pytest` |
| README render | `poetry run python -m tools.modules.update_readme` |
| Pages checks | `task validate-site` |

`act` is best-effort only. Hosted GitHub token behavior, secrets, scheduled-event
payloads, Pages OIDC, and deployment environments are not fully reproducible
locally.

---

## 9. Generated Cache Cleanup

Safe transient cleanup:

```sh
rm -rf .venv
rm -rf .pytest_cache
rm -rf .ruff_cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

Do **not** delete committed `profile/artifacts/` merely as routine cleanup; they
are part of the graceful-degradation architecture.

---

## 10. Dependency Updates

```sh
poetry add <package>@<version>
poetry update
poetry lock
poetry show --outdated
```

Commit both `pyproject.toml` and `poetry.lock` when dependency resolution
changes.

---

## 11. Quality Tool Boundary

The authoritative validation stack is:

- Poetry
- Ruff
- yamllint
- pytest
- `profile/validate_assets.py`
- `profile/validate_evidence.py`
- `tools/profile_builder/cli.py`

`egolint` may replace or supplement part of this stack after a stable public
release and explicit repository migration. Do not add speculative `egolint`
configuration before that migration is designed and validated.
