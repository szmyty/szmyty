# Public Data Security Audit

Date: 2026-08-09 (UTC)

## Scope

- Working tree scan for denied staged telemetry paths and obvious credential patterns.
- Reachable Git history scan for prior committed denied staged telemetry paths.
- Review of contact metadata and metrics workflow configuration risk points.

## Tooling and commands

- `git version 2.54.0`
- `detect-secrets 1.5.0`
- `rg` (repository search)

Commands used:

```bash
# Current tracked denied paths
 git ls-files | grep -E '^(\.staging/(oura/.*\.(json|svg)|location/.*\.(json|png|svg)|weather/.*\.(json|svg)|dashboard-app/public/(oura|location|weather)/.*\.json|data/snapshots/.+\.json|data/metrics/(location|oura|weather)\.json))$'

# Reachable-history path exposure
 git log --all --name-only --pretty=format: | grep -E '^(\.staging/(oura/|location/|weather/|dashboard-app/public/(oura|location|weather)/|data/snapshots/|data/metrics/(location|oura|weather)\.json))' | sort -u

# Secret scan
 detect-secrets scan --all-files > /tmp/detect-secrets-report.json
```

## Inventory of sensitive sources and generated copies

Identified families and disposition:

- `.staging/oura/**` (health/biometric + mood inference): **removed from tracked production tree**.
- `.staging/location/**` (precise location/maps): **removed from tracked production tree**.
- `.staging/weather/**` (location-derived weather): **removed from tracked production tree**.
- `.staging/dashboard-app/public/{oura,location,weather}/**` mirrors: **removed from tracked production tree**.
- `.staging/data/snapshots/**/*.json` and `.staging/data/metrics/{location,oura,weather}.json`: **removed from tracked production tree**.
- `.staging/.secrets.example` and secret-consuming workflows/scripts: **retained as templates/automation inputs; covered by boundary checks and secret scans**.
- Contact metadata (`.mailmap`, `pyproject.toml`, README variants): **personal mailbox references replaced with public contact channel / noreply metadata**.
- GitHub metrics config risk review: `.staging/.github/workflows/metrics.yml` and `.staging/.github/workflows/github-stats.yml` use tokenized metrics generation; private-activity risk documented and controlled by policy + review checklist.

## Findings (sanitized)

### Current tree

- Denied-path scan: **no matches** in currently tracked files.
- `detect-secrets` summary: **3 findings across 2 files**, all `Secret Keyword` classifier hits in workflow/workspace metadata.
  - `.staging/.github/workflows/profile-summary-cards.yml` (2 keyword hits)
  - `szmyty.code-workspace` (1 keyword hit)
- Assessment: keyword-only findings, no credential value disclosure in tracked content.

### Reachable history

Sensitive historical values were found in reachable history (not printed):

- Types: health/biometric telemetry, mood inference, precise location/maps, location-derived weather, and mirrored dashboard public copies.
- Affected families: `.staging/oura/**`, `.staging/location/**`, `.staging/weather/**`, `.staging/dashboard-app/public/{oura,location,weather}/**`, `.staging/data/snapshots/**/*.json`, `.staging/data/metrics/{location,oura,weather}.json`.
- Earliest/known commit in reachable history for sampled paths: `dc4f0eae` (2026-08-08).

## Required follow-up actions

1. **No automatic history rewrite performed in this issue.**
2. Prepare a separate, explicit history-cleaning plan (owner-reviewed) for the denied historical path families.
3. Credential rotation recommendation:
   - If any real credential is later confirmed from historical blobs, rotate that credential immediately and revoke old tokens.
4. Keep CI boundary checks enabled to prevent reintroduction.
