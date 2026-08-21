# Architecture

## Repository: szmyty/szmyty

**Status:** Active

## Purpose

This repository serves two roles:

1. **GitHub profile README** — `README.md` is rendered as Alan Szmyt's public
   GitHub profile and contains both hand-authored and generated regions.
2. **Reusable profile platform** — configuration, snapshot modules, templates,
   tests, workflows, and documentation provide a reproducible first-party
   profile-generation system.

## Directory Responsibilities

| Path | Responsibility |
|------|---------------|
| `README.md` | Public profile; generated content is constrained to owned markers |
| `assets/profile/` | Hand-authored profile imagery |
| `profile/content/` | Canonical module registry, compatibility mirror, evidence, manual inputs |
| `profile/artifacts/` | Generated last-known-good module snapshots and SVGs |
| `profile/fixtures/` | Sanitized synthetic fixtures; never presented publicly as live data |
| `profile/templates/` | Jinja2 templates for generated README regions |
| `profile/schemas/` | Schemas for profile configuration |
| `tools/modules/` | Provider adapters, normalization, SVG generation, README rendering |
| `tools/profile_builder/` | Shared profile-builder models, validation, cache, and rendering support |
| `tests/` | Deterministic provider, privacy, rendering, and workflow tests |
| `.github/workflows/` | CI, scheduled profile refresh, and Pages deployment |
| `docs/` | Architecture, privacy, content, development, and operating policy |
| `site/` | Companion static site deployed with GitHub Pages |

## Architectural Boundaries

- Hand-authored README prose outside module markers is never rewritten by the
  module pipeline.
- Dynamic modules normalize provider responses before persistence; raw provider
  payloads are not tracked.
- Sensitive/location-derived providers are deny-by-default and require an
  explicit owner-approved public transformation in `docs/PRIVACY.md`.
- Synthetic fixture values may exercise the complete render path in CI but may
  never be rendered as live profile values.
- All provider failures degrade independently to last-known-good real output or
  a hidden synthetic fixture; one provider must not destroy unrelated cards.
- Historical experimental weather/location/Oura implementations remain
  prohibited. The active modules are bounded reimplementations approved by
  issue #149.

## Snapshot Module Platform

Every active README module follows one lifecycle:

1. **Declare** — `profile/content/modules-registry.yml` declares provider,
   sensitivity, freshness, artifacts, marker ownership, and template.
2. **Mirror** — `profile/content/modules.yml` mirrors README-region ownership
   for compatibility validation.
3. **Fetch** — `tools/modules/<module>.py` reads the provider and normalizes
   data into the module's public contract.
4. **Persist** — only the normalized snapshot and generated visual assets enter
   `profile/artifacts/<module>/`.
5. **Render** — `tools/modules/update_readme.py` imports
   `load_template_context()` from each enabled provider and renders the Jinja2
   template into its owned README marker pair.
6. **Commit** — `update-profile.yml` commits semantic changes using the Actions
   bot.
7. **Fallback** — provider failures use last-known-good real artifacts when
   available. Synthetic fixtures remain visibly classified and templates hide
   them from public output.

## Active Dynamic Modules

| Module | Source | Public projection | Cadence |
|--------|--------|-------------------|---------|
| `github-dashboard` | Public GitHub REST/GraphQL | Engineering/activity dashboard | Daily |
| `weather` | Public GitHub profile location + Open-Meteo | Current weather for public city/region; no coordinates retained | About every 3 hours |
| `steam` | Official Steam Web API | Level, XP, badges, owned games, recent games/playtime | Daily |
| `oura-trends` | Oura Cloud API V2 OAuth2 `daily` scope | Coarse weekly sleep/readiness/activity score charts | Daily |

Other registered modules remain disabled until their separate launch gates are
satisfied.

## Data Flow

```text
profile/content/modules-registry.yml ─────────────┐
profile/content/modules.yml ──────────────────────┤
profile/content/evidence.yml ─────────────────────┤
                                                  │
GitHub REST/GraphQL ──► github-dashboard ─────────┤
GitHub public location ─► Open-Meteo ─► weather ──┤
Steam Web API ────────────────────────► steam ─────┤
Oura API V2 OAuth2 ──────────────────► oura-trends│
                                                  ▼
                                     profile/artifacts/*
                                                  │
profile/templates/*.md.j2 ────────────────────────┤
                                                  ▼
                                  tools/modules/update_readme.py
                                                  │
                                                  ▼
                                             README.md
```

### Weather boundary

1. Read `@szmyty`'s public GitHub `location` field at runtime.
2. Geocode the location transiently with Open-Meteo.
3. Use coordinates only for the immediate forecast request.
4. Discard coordinates before normalization.
5. Persist the public location label, normalized weather values, attribution,
   metadata, and responsive SVGs.

This deliberately avoids a second hard-coded location source. Updating the
GitHub profile location changes the next live weather refresh.

### Steam boundary

The Steam adapter uses the official Web API and treats Steam privacy settings
as authoritative. It publishes Steam-native profile signals rather than an
invented Xbox-style Gamerscore:

- Steam level
- player XP
- badge count
- owned-game count
- bounded recent games
- bounded recent playtime

Presence/online state and session timestamps are excluded.

### Oura boundary

The Oura source remains classified `sensitive`. The public projection is
strictly narrower than the provider data:

1. `OURA_ACCESS_TOKEN` is an OAuth2 access token with only the `daily` scope.
2. Daily sleep/readiness/activity summary rows are fetched into memory.
3. The current day plus `SAFETY_BUFFER_DAYS` recent days are excluded.
4. Rows are reduced to weekly means.
5. Weekly chart values are rounded to 5-point buckets and rendered without
   exact date labels.
6. Only `OURA_PUBLIC_AGGREGATE_ALLOWLIST` fields are persisted in JSON.
7. Raw/daily records, precise schedules, workouts, tags, heart-rate series,
   exact HRV, travel/location inference, and authentication material are never
   persisted.

See `docs/PRIVACY.md` for the complete transformation contract.

## Generated Visual Contract

Weather, Steam, Oura, and GitHub dashboard cards use repository-owned SVGs
rather than third-party README image services. Visual modules generate:

- `card-light.svg`
- `card-dark.svg`
- `card-mobile-light.svg`
- `card-mobile-dark.svg`

README templates use `<picture>` source selection for color scheme and mobile
viewport. SVGs use system font stacks and accessible `<title>`/`<desc>` text.

## Automation

The production workflow set remains intentionally limited to three workflows:

| Workflow | Responsibility |
|----------|----------------|
| `ci.yml` | Read-only validation on PRs/pushes |
| `update-profile.yml` | Provider refresh, rendering, artifact upload, semantic commit |
| `pages.yml` | Static-site validation and GitHub Pages deployment |

### Refresh schedule

`update-profile.yml` has two schedule classes:

- **Weather refresh:** `17 0,3,9,12,15,18,21 * * *` — approximately every
  three hours without duplicating the daily 06:00 full run.
- **Full refresh:** `0 6 * * *` — GitHub dashboard, Steam, Oura, and other
  full-profile modules, plus weather.

Manual, issue-triggered, and relevant push-triggered runs execute the full
module set. Scheduled non-06:00 runs skip the heavier modules and refresh only
weather before re-rendering the README.

## Environment Variables and Secrets

| Variable | Required | Secret | Consumer | Notes |
|----------|----------|--------|----------|-------|
| `GITHUB_TOKEN` | Actions | No; automatic | GitHub dashboard, weather location lookup | Per-run token supplied by GitHub Actions |
| `STEAM_WEB_API_KEY` | For live Steam | Yes | `steam` | Official Steam Web API credential |
| `STEAM_ID64` | For live Steam | No; Actions variable | `steam` | Public SteamID64, not a credential |
| `OURA_ACCESS_TOKEN` | For live Oura | Yes | `oura-trends` | OAuth2 access token with `daily` scope |
| `POETRY_VIRTUALENVS_IN_PROJECT` | No | No | Tooling | Keeps Poetry virtualenv in `.venv/` |

### Secret lifecycle

- Secret values never belong in repository files, issues, PR descriptions,
  fixtures, metadata, SVGs, or logs.
- Steam keys are rotated at the Steam provider and replaced in Actions.
- Oura Personal Access Tokens are not supported. Oura OAuth2 access must be
  re-authorized when the stored access token expires or is revoked.
- This profile workflow intentionally does not persist Oura refresh tokens or
  grant itself broad repository-secret mutation permission to rotate a
  single-use refresh token.

## Technology

- Python 3.12+
- Poetry
- Click
- Pydantic
- Jinja2
- PyYAML
- pytest
- Ruff
- yamllint
- GitHub Actions

No new runtime dependency is required for the telemetry modules; provider calls
use Python's standard-library HTTP client and SVGs are generated directly.

## Validation

Primary local parity:

```sh
poetry run python -m tools.profile_builder.cli validate
poetry run python profile/validate_assets.py assets/profile
poetry run python -m pytest
poetry run ruff check .
poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml
bash .tasks/check-identity.sh
```

Provider tests use synthetic or mocked inputs and do not require live API calls.

## Historical Modules That Remain Prohibited

Do not promote or revive these legacy paths:

| Legacy implementation | Reason |
|----------------------|--------|
| `fetch-location/` | Persisted/unbounded location design |
| `fetch-weather/` | Superseded by bounded `weather` adapter |
| `generate-location-card/` | Unbounded location projection |
| `generate-weather-card/` | Superseded by first-party bounded SVG renderer |
| `fetch-oura/` | Legacy raw health/biometric design |
| `generate-oura-dashboard/` | Excessive health-detail projection |
| `generate-oura-mood/` | Mood inference remains prohibited |

The active `weather` and `oura-trends` modules do not authorize these historical
implementations or broaden the approved data surface.
