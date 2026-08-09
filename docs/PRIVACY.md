# Public Profile Privacy Policy

## Scope

This repository publishes a public profile. Only intentionally public data is allowed in tracked production content.

## Public-data allow-list

- Profile prose intentionally authored for publication (`README.md`, public docs).
- Public GitHub metadata/activity from public repositories only.
- Public education/professional chronology explicitly approved for publication.
- Public project docs, releases, and demos.
- Public music metadata/links explicitly published by the data owner.
- Public contact channel: GitHub profile/issues only (`https://github.com/szmyty`).

## Public-data deny-list

- Health, biometric, recovery, sleep, readiness, mood, or mood-inference data.
- Precise or routinely refreshed location, coordinates, maps, and geocoding payloads.
- Location-derived weather snapshots.
- Private repository/activity metadata.
- Tokens, cookies, auth headers, raw authenticated responses, debug dumps.
- Restricted employer/project details not explicitly public.
- Personal email addresses not intentionally selected as public contact.

## Data owner and sources

- **Data owner:** repository owner (`@szmyty`).
- **Approved sources:** authored markdown, public GitHub APIs, and explicitly public media metadata.
- **Denied sources:** Oura/health APIs, location/geocoding providers, weather tied to location, private API payload dumps.

## Retention rules

- Raw denied inputs must not be committed.
- Generated outputs derived from denied inputs must not be committed.
- Test fixtures may exist only as sanitized synthetic data under `profile/fixtures/` and must not include copied personal measurements or coordinates.
- Historical incidents are documented in `docs/audits/` using sanitized summaries only.

## Redaction and incident response

1. Quarantine: remove denied files from tracked tree immediately.
2. Contain: add/verify deny-list checks and ignore rules.
3. Assess: scan current tree and reachable history for sensitive exposure.
4. Report: record sanitized findings (type/path/range, never value).
5. Rotate: rotate any affected credentials.
6. Plan history cleanup separately; do not rewrite shared history automatically.

## Public contact policy

- Use GitHub as the public contact channel.
- Do not publish personal mailbox addresses in profile artifacts unless explicitly approved as public.

## Employment and restricted-detail policy

- Include only employer/project details already intentionally public.
- Exclude confidential client names, internal code names, non-public roadmap details, or restricted claims.

## Dynamic module review checklist (required for every new module)

- [ ] Data source is on the allow-list.
- [ ] No denied-path artifacts are generated or committed.
- [ ] Output contains no private repos/activity.
- [ ] Output contains no health/biometric/location-derived fields.
- [ ] Secrets scan passes.
- [ ] Reachable-history scan impact reviewed (sanitized findings only).
- [ ] Contact/employment claims meet policy.
