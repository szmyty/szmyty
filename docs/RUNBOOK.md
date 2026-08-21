# Operations Runbook

**Repository:** `szmyty/szmyty`
**Status:** Active

This runbook covers failure response for the profile build, live telemetry, and
publish pipeline.

---

## 1. Scheduled Update Failure

**Symptom:** `update-profile.yml` ends in failure or partial failure.

1. Open the failed Actions run and read the module refresh summary.
2. Identify the module outcome (`success`, `failure`, or `skipped`) and its
   artifact `data_source`.
3. Treat one provider failure as isolated: other modules should still refresh
   and the failed module should retain last-known-good output when available.
4. Re-run a transient provider/network failure manually.
5. For a structural failure, run the module-specific command below and fix the
   provider adapter, schema, template, or workflow contract.
6. If scheduled workflows were disabled after repository inactivity, re-enable
   the workflow in the Actions UI.

### Expected schedule

- Weather: `17 0,3,9,12,15,18,21 * * *`.
- Full profile refresh: `0 6 * * *`.

The daily full run also refreshes weather. Non-06:00 scheduled runs skip the
heavier GitHub/Steam/Oura modules.

---

## 2. Local Validation

Run before merging provider or rendering changes:

```sh
poetry install --with lint,test
poetry run python -m tools.profile_builder.cli validate
poetry run python profile/validate_assets.py assets/profile
poetry run python -m pytest
poetry run ruff check .
poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml
bash .tasks/check-identity.sh
```

Provider tests are deterministic and must not call live APIs.

---

## 3. Weather Module

### Live command

```sh
GITHUB_TOKEN="${GITHUB_TOKEN}" \
  poetry run python -m tools.modules.weather \
  --output profile/artifacts/weather/cache.json
```

`GITHUB_TOKEN` is optional locally for the public GitHub user endpoint but is
provided automatically in Actions.

### Expected behavior

1. Read the public `@szmyty` GitHub `location` field.
2. Geocode that string transiently with Open-Meteo.
3. Fetch weather using the in-memory coordinates.
4. Persist the public location label and normalized weather only.
5. Generate desktop/mobile light/dark SVGs.

### Failure response

- **GitHub location missing:** update the public GitHub profile location if a
  weather card is still desired. The module must not silently substitute a
  hard-coded city.
- **Open-Meteo unavailable:** retain the last-known-good real cache. A synthetic
  fixture may exercise CI but remains hidden from the public README.
- **Wrong city resolution:** inspect the public GitHub location string and the
  geocoding selection logic. Never fix this by committing coordinates.
- **Coordinate/timezone/elevation appears in a tracked artifact:** treat as a
  privacy-boundary failure, remove the value, and follow the incident procedure.

### Disable

Set `weather.enabled: false` in both module registries and remove or relocate the
README marker surface in the same PR. Do not leave two location sources behind.

---

## 4. Steam Module

### Required repository configuration

- Actions secret: `STEAM_WEB_API_KEY`
- Actions variable: `STEAM_ID64`

`STEAM_ID64` is a public profile identifier and is intentionally a variable,
not a secret.

### Live command

```sh
STEAM_WEB_API_KEY="${STEAM_WEB_API_KEY}" \
STEAM_ID64="${STEAM_ID64}" \
  poetry run python -m tools.modules.steam \
  --output profile/artifacts/steam/cache.json
```

### Expected public metrics

- Steam level
- player XP
- badge count
- owned-game count
- up to five recent games
- bounded recent playtime

Steam does not expose an Xbox-style Gamerscore; do not invent a composite score
unless a future specification explicitly defines and labels it as a custom
metric.

### Failure response

- **No live card after enabling:** verify both repository configuration values
  exist and that the Steam profile/game-details privacy settings expose the
  requested public data.
- **401:** rotate `STEAM_WEB_API_KEY` at the Steam provider and replace the
  Actions secret.
- **403/private response:** respect Steam privacy settings; do not add a scraper
  to bypass them.
- **Partial endpoint failure:** the card may omit unavailable level/library or
  badge metrics while preserving the rest of the public snapshot.

### Revoke/rotate

1. Revoke or replace the key at the Steam provider.
2. Update `STEAM_WEB_API_KEY` in GitHub Actions secrets.
3. Trigger `Update Profile` manually.
4. Confirm the new artifact has `data_source: live`.

---

## 5. Oura Trends Module

### Authentication model

Oura Cloud API V2 requires OAuth2. Personal Access Tokens are no longer an
available authentication path. The module expects:

- Actions secret: `OURA_ACCESS_TOKEN`
- OAuth scope: `daily`

The workflow intentionally does not store an OAuth refresh token and does not
grant itself repository-secret mutation privileges to rotate one. When the
access token expires, the public card remains on last-known-good real output
until the owner re-authorizes and updates the secret.

### Live command

```sh
OURA_ACCESS_TOKEN="${OURA_ACCESS_TOKEN}" \
  poetry run python -m tools.modules.oura_trends \
  --allow-publication \
  --output profile/artifacts/oura-trends/cache.json
```

### Public transformation

Only the owner-approved #149 transformation may be published:

- `daily_sleep`, `daily_readiness`, and `daily_activity` summary score streams;
- recent-day safety buffer;
- in-memory daily rows only;
- up to eight unlabeled weekly averages;
- weekly values rounded to 5-point buckets;
- aggregate JSON limited by `OURA_PUBLIC_AGGREGATE_ALLOWLIST`;
- no raw/daily records, precise schedules, workouts, tags, heart-rate series,
  precise HRV, travel/location inference, or authentication data.

### Expired/revoked access token

1. Confirm the failure is 401/403 in the sanitized workflow message. Do not log
   the provider response body or token.
2. Complete the Oura OAuth authorization flow again with only the `daily` scope.
3. Replace the `OURA_ACCESS_TOKEN` Actions secret.
4. Trigger `Update Profile` manually.
5. Confirm the artifact changes from `cache` to `live`.

### Provider/API failure

- A transient provider failure must retain the last-known-good real aggregate
  and SVGs.
- If no real cache exists, synthetic fixture output stays hidden from README.
- If all three daily summary endpoints fail, treat the fetch as failed rather
  than publishing an empty “healthy” chart.

### Disable/delete public Oura output

1. Set `oura-trends.enabled: false` in both registries.
2. Set `publication: blocked-pending-owner-approval` in the canonical registry
   if approval is being withdrawn.
3. Clear the README region or allow the renderer to clear it once disabled.
4. Remove tracked `profile/artifacts/oura-trends/` if the owner wants the
   current public artifact removed from the tree.
5. Review reachable history separately; do not rewrite shared history without
   explicit coordination.

---

## 6. GitHub Dashboard and Manual Modules

### GitHub dashboard failure

```sh
GITHUB_TOKEN="${GITHUB_TOKEN}" \
  poetry run python -m tools.modules.github_dashboard \
  --output-dir profile/artifacts/github-dashboard
```

On rate-limit or transient API failure, preserve the committed cache rather
than fabricating metrics.

### Music highlight failure

```sh
poetry run python -m tools.modules.music_highlight \
  --input profile/content/music-highlight.yml \
  --output profile/artifacts/music-highlight/music.yml
```

Inspect the manual YAML input for malformed or missing required fields.

---

## 7. Stale Output

1. Confirm `Update Profile` remains enabled in Actions.
2. Inspect `profile/artifacts/<module>/metadata.json` for `state`,
   `data_source`, and generation time.
3. Confirm the provider credential/variable exists where required.
4. Trigger the workflow manually after resolving configuration/provider issues.
5. Do not hand-edit generated live artifacts to “freshen” timestamps or values.

Expected freshness policy is declared in
`profile/content/modules-registry.yml`.

---

## 8. Broken Generated Card

**Symptom:** README shows a broken SVG, wrong theme variant, or bad mobile
layout.

1. Confirm all four visual assets exist in the module artifact directory:
   - `card-light.svg`
   - `card-dark.svg`
   - `card-mobile-light.svg`
   - `card-mobile-dark.svg`
2. Render the module locally from fixtures/mocked data.
3. Validate SVG markup and confirm `<title>`/`<desc>` accessibility text exists.
4. Inspect the module Jinja2 template's `<picture>` media queries.
5. Do not replace first-party generated SVGs with third-party badge/card services
   solely to hide a renderer bug.

---

## 9. Suspected Sensitive-Data or Secret Exposure

1. **Revoke credentials immediately** if any credential may be exposed.
2. **Disable the affected module** if it can continue generating the bad field.
3. Remove the disallowed value/file from the tracked tree.
4. Delete affected Actions logs if they contain a credential or raw sensitive
   payload.
5. Scan the current tree and recent history for the same class/pattern.
6. Add/repair tests that enforce the transformation boundary.
7. Document a sanitized incident summary under `docs/audits/` without copying
   the sensitive value.
8. Plan any history rewrite separately with `@szmyty`; never rewrite shared
   history automatically.

For Oura, daily records or exact timestamps entering artifacts are a privacy
incident even when no credential leaked. For weather, persisted coordinates are
a privacy incident under the current #149 contract.

---

## 10. GitHub Pages Rollback

1. Identify the last known-good site commit:

   ```sh
   git log --oneline -- site/
   ```

2. Restore the known-good site files:

   ```sh
   git checkout <good-commit-sha> -- site/
   ```

3. Validate:

   ```sh
   poetry run python -m pytest tests/test_workflows.py -k "workflow or site"
   ```

4. Commit the rollback with a conventional commit and let `pages.yml` redeploy.

---

## 11. Evidence Verification Request

For stable profile prose, do not change a `needs-user-verification` record to
`verified` without explicit owner confirmation or a public supporting artifact.

Dynamic telemetry values follow the provider-transformation contract in
`docs/CONTENT.md` and `docs/PRIVACY.md`; issue #149 records the current owner
approval for weather/Steam/Oura. That approval does not automatically verify
separate stable personal claims.

---

## 12. GitHub Surface Owner Checklist

Repository files and CI cannot verify every GitHub UI setting. Before a major
profile release, review:

- branch/ruleset protection for `master`;
- required CI checks;
- About text/homepage/topics/social preview;
- pinned repositories;
- Pages environment/deployment URL;
- Discussions categories and issue-routing links;
- Actions secrets/variables required by enabled modules.

Use `docs/FINAL-OWNER-HANDOFF-CHECKLIST.md` together with
`docs/audits/FINAL-PROFILE-READINESS-REPORT.md` for the broader release gate.
