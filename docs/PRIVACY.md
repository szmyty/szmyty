# Public Profile Privacy Policy

## Scope

This repository publishes a public profile. Only intentionally public data or
explicitly owner-approved public transformations of sensitive inputs may enter
tracked production content.

Sensitive and location-derived sources are **deny-by-default**. A source may be
used only when its public projection is narrowly allow-listed, documented,
tested, and explicitly approved by the data owner.

Issue [#149](https://github.com/szmyty/szmyty/issues/149) records the current
owner approval for the `weather`, `steam`, and `oura-trends` modules.

## Public-data allow-list

- Profile prose intentionally authored for publication (`README.md`, public docs).
- Public GitHub metadata/activity from public repositories only.
- Public education/professional chronology explicitly approved for publication.
- Public project docs, releases, and demos.
- Public music metadata/links explicitly published by the data owner.
- Professional contact route: the approved public portfolio
  (`https://szmyty.vercel.app`).
- `weather`: the public GitHub profile city/region label and weather derived
  from that label. Geocoded coordinates are transient implementation details.
- `steam`: public profile identity, Steam level, player XP, badge count,
  owned-game count, bounded recent games, and bounded recent playtime when the
  owner's Steam privacy settings expose them.
- `oura-trends`: the explicitly approved aggregate model plus coarse weekly
  sleep/readiness/activity score charts. Weekly values are rounded to 5-point
  buckets, recent days are excluded, and no daily records are retained.

## Public-data deny-list

The following remain prohibited even when an approved telemetry module is
active:

- Precise coordinates, persistent geocoding results, timezone/elevation
  payloads, maps of routine location, or location history.
- Raw Oura/health API responses, daily records, exact sleep/wake times, exact
  measurement timestamps, workouts, tags, heart-rate time series, precise HRV
  values, mood/mood inference, illness inference, travel/location inference,
  or present-day readiness/availability inference.
- Steam online/presence state, session timestamps, or fields unavailable under
  the owner's current Steam privacy settings.
- Private repository/activity metadata.
- Tokens, cookies, refresh tokens, auth headers, raw authenticated responses,
  debug dumps, or provider credentials of any kind.
- Restricted employer/project details not explicitly public.
- Personal email addresses not intentionally selected as public contact.

## Data owner and approved sources

- **Data owner:** repository owner (`@szmyty`).
- **General approved sources:** authored markdown, public GitHub APIs, and
  explicitly public media metadata.
- **Telemetry sources approved by #149:**
  - GitHub public user API for the profile location string.
  - Open-Meteo geocoding and forecast APIs; coordinates may exist in memory
    only and must not enter tracked artifacts or logs.
  - Official Steam Web API, bounded by Steam privacy settings.
  - Oura Cloud API V2 using OAuth2 and the `daily` scope; only the public
    transformation described above may be persisted.

Approval of a provider does **not** approve all fields returned by that
provider. The transformation contract is authoritative.

## Retention rules

- Raw provider payloads from weather geocoding, Steam authenticated endpoints,
  and Oura authenticated endpoints must not be committed or uploaded as
  workflow artifacts.
- Weather artifacts may retain the public city/region label and normalized
  weather values, but never coordinates/timezone/elevation.
- Steam artifacts may retain only the public metrics enumerated in the
  allow-list.
- Oura artifacts may retain only fields in
  `OURA_PUBLIC_AGGREGATE_ALLOWLIST` and generated SVGs containing coarse weekly
  score buckets. Daily arrays must never be written.
- Real telemetry artifacts may be committed as last-known-good fallbacks.
- Test fixtures must be sanitized synthetic data and must be explicitly marked
  synthetic where the module supports that flag.
- Synthetic fixtures must never be rendered to the public README as if they
  were live values.
- Historical incidents are documented in `docs/audits/` using sanitized
  summaries only.

## Oura transformation boundary

Oura is a sensitive source even though its public projection is intentionally
coarse. The module must preserve all of these controls:

1. Use OAuth2 access tokens stored only in GitHub Actions secrets.
2. Request only the `daily` scope required for daily sleep/readiness/activity
   summary scores.
3. Exclude the current day and `SAFETY_BUFFER_DAYS` recent days.
4. Hold provider daily rows in memory only.
5. Reduce daily scores to unlabeled weekly means.
6. Round weekly chart values to 5-point buckets.
7. Require at least `MIN_SAMPLE_DAYS` before rendering real public data.
8. Persist only the aggregate allow-list and generated SVGs.
9. Fall back to last-known-good real output when the access token expires or
   the provider is unavailable.
10. Never persist an OAuth refresh token or grant the profile workflow broad
    repository-secret mutation privileges solely to rotate credentials.

## Weather transformation boundary

The weather module must:

1. Read the location string from the public GitHub profile on each live run.
2. Geocode that string transiently using Open-Meteo.
3. Use the resulting coordinates only to make the weather request.
4. Discard coordinates before normalization.
5. Persist only the public location label and normalized weather snapshot.
6. Attribute Open-Meteo in the rendered card/README.

Changing the GitHub profile location therefore changes the next live weather
snapshot without creating a second location configuration source.

## Steam transformation boundary

The Steam module must:

1. Store `STEAM_WEB_API_KEY` only as a GitHub Actions secret.
2. Store the public `STEAM_ID64` as a repository Actions variable.
3. Treat Steam privacy settings as authoritative.
4. Publish only the allow-listed profile/game metrics.
5. Never infer or expose presence/availability from Steam state.
6. Retain last-known-good real data if the provider becomes unavailable.

## Redaction and incident response

1. **Quarantine:** remove any disallowed file/value from the tracked tree.
2. **Contain:** disable the affected module or narrow its output gate.
3. **Revoke:** invalidate any exposed credential immediately.
4. **Assess:** scan the current tree and reachable history for the same data
   class or credential pattern.
5. **Report:** record sanitized findings (type/path/range, never the value).
6. **Restore:** re-enable only after tests demonstrate the transformation
   boundary again.
7. **Plan history cleanup separately:** do not rewrite shared history
   automatically.

## Public contact policy

- Route professional inquiries through the approved public portfolio.
- Use GitHub issues only for repository-specific questions.
- Do not embed a personal mailbox address in profile artifacts unless the
  exact address is explicitly approved as public.
- A destination may expose an owner-approved contact method without copying
  that value into this repository.

## Employment and restricted-detail policy

- Include only employer/project details already intentionally public.
- Exclude confidential client names, internal code names, non-public roadmap
  details, or restricted claims.

## Dynamic module review checklist

Required for every new or materially changed dynamic module:

- [ ] Data source is approved or has an explicit owner-approved transformation.
- [ ] Public fields are allow-listed rather than merely deny-listed.
- [ ] Raw provider payloads and credentials are never persisted.
- [ ] Exact coordinates/timestamps/routine information are absent unless the
      policy explicitly allows them.
- [ ] Synthetic fixtures cannot be mistaken for real profile data.
- [ ] Last-known-good fallback behavior is defined.
- [ ] Secrets scan passes.
- [ ] Provider attribution/terms requirements are satisfied.
- [ ] Reachable-history impact is reviewed when changing a sensitive module.
- [ ] Contact/employment claims meet policy.
