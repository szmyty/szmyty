# Content Guidelines

**Repository:** `szmyty/szmyty`
**Status:** Active

This document defines the rules for authoring and generating the public profile
README. The goal is to keep stable claims evidence-backed while allowing
narrowly governed dynamic modules to publish changing provider values without
pretending those values are permanent claims.

---

## 1. Stable Claims and Evidence

`profile/content/evidence.yml` is the source of truth for stable factual claims
in the hand-authored profile narrative.

A stable claim may appear when:

1. a matching evidence record exists;
2. its `status` is `verified`;
3. its `sensitivity` is `public`; and
4. the README wording does not exceed the scope of the recorded claim.

A stable claim must remain absent when its record is
`needs-user-verification`, `excluded`, `sensitive`, or `internal`, unless a
separate explicitly owner-approved public transformation governs the output.

### Evidence types

| Type | Meaning |
|------|---------|
| `url` | Publicly inspectable supporting artifact |
| `repo-path` | Supporting artifact in this repository |
| `self-reported` | Owner-confirmed claim without independent public proof |
| `inferred` | Bounded conclusion from public observable signals |
| `none` | No supporting artifact is currently available |

### Needs-user-verification protocol

When a record is `needs-user-verification`:

1. open or reference an issue requesting the specific confirmation;
2. do not mark the stable claim `verified` without explicit owner confirmation
   or a public artifact; and
3. do not render that stable claim while it remains unverified.

---

## 2. Dynamic Provider Modules

Dynamic module values are not stable claims. Weather temperature, Steam game
counts, and Oura trend buckets change over time and therefore are governed by a
**source + transformation + owner-approval contract** instead of one evidence
record per value.

A dynamic module may render changing values only when all of the following are
true:

1. the module is declared in `profile/content/modules-registry.yml`;
2. its provider and public transformation are documented in
   `docs/PRIVACY.md` and `docs/ARCHITECTURE.md`;
3. the data owner has explicitly approved that public projection;
4. tests demonstrate that disallowed source fields cannot enter tracked output;
5. synthetic fixtures are distinguishable from real values and are hidden from
   the public README; and
6. the README accurately attributes or characterizes the data source.

Issue [#149](https://github.com/szmyty/szmyty/issues/149) is the owner-approval
record for the current `weather`, `steam`, and `oura-trends` projections.

### Dynamic disclosure does not broaden stable identity claims

The weather module may display the public GitHub profile location string because
that exact runtime source and granularity were approved in #149. That does not
silently verify the older `identity-location` evidence record for use in other
profile prose. A sentence such as "I live in Boston" remains a separate stable
claim and requires its own verified evidence/approval.

Likewise, approving coarse Oura charts does not authorize health claims,
diagnoses, current-condition statements, or interpretation of the underlying
wellness data.

---

## 3. Tense and Tone

- Use present tense for current capabilities and ongoing work.
- Use past tense for completed projects and historical events.
- Lead with outcomes rather than technology inventories.
- State ownership proportionally and distinguish individual work from
  collaborative contribution.
- Avoid generic evaluative claims such as "expert", "world-class", or
  "results-driven" when evidence does not make them necessary.
- Do not fabricate or estimate adoption, impact, repository stars, users,
  releases, scale, time savings, or proficiency.
- Dynamic telemetry must describe what the provider reports rather than imply a
  broader personal-quality score.

### Steam-specific wording

Steam does not define an Xbox-style Gamerscore. The profile therefore displays
Steam-native signals—level, XP, badges, owned games, and recent playtime—without
combining them into an invented score.

### Oura-specific wording

Oura output is voluntarily shared aggregate wellness telemetry. Do not describe
it as a diagnosis, medical assessment, current health state, or productivity
score. The README must retain a plain-language aggregation/privacy disclaimer.

---

## 4. Confidential and Restricted Work

Employment history remains governed by the repository's confidentiality policy.
Do not publish non-public employer, team, customer, mission, program, dataset,
security, or internal-tool details.

If professional experience is later approved for publication:

- use only explicitly approved public facts;
- do not narrow restricted programs through indirect technical details; and
- mark uncertain records `internal` or `needs-user-verification` until the
  owner resolves them.

---

## 5. Sensitive Personal Data

Sensitive sources are deny-by-default. `docs/PRIVACY.md` is authoritative for
approved public transformations.

Current owner-approved transformations are limited to:

- public GitHub city/region label → weather card, without coordinates;
- public Steam API fields → gaming card, without presence/session telemetry;
- Oura daily summary scores → coarse weekly aggregate charts, without raw daily
  rows, exact schedules, location/travel inference, or authentication data.

Do not infer or add additional personal information from those sources.

---

## 6. Current Focus and Availability

The **Current Focus** table and any availability or target-role language are
manual owner-controlled content. Do not infer them from GitHub activity,
telemetry, old README content, or staged files.

To change them:

1. create or update the matching evidence record;
2. obtain explicit owner confirmation when needed;
3. update `last_reviewed`;
4. change the hand-authored README section; and
5. reference the approval/evidence in the PR.

---

## 7. Accomplishment Graduation

A candidate accomplishment normally begins as `needs-user-verification` and
graduates to `verified` only after explicit owner confirmation or a public
artifact supports the exact wording.

| Step | Action |
|------|--------|
| 1 | Create candidate evidence record |
| 2 | Request specific verification |
| 3 | Owner supplies confirmation/artifact/correction |
| 4 | Update to `verified` with current review date |
| 5 | Add bounded README wording |
| 6 | Review in PR |

Claims do not graduate automatically from old README content or inferred
activity.

---

## 8. Freshness and Ownership

| Content area | Owner |
|-------------|-------|
| Evidence catalog | `@szmyty` |
| Hand-authored README narrative | `@szmyty` |
| Dynamic module public-transformation approval | `@szmyty` |
| Provider adapters/templates/tests | Repository maintainers under documented contract |

Review stable evidence at least every six months and re-review records older
than twelve months before promoting them into new public prose.

Dynamic provider freshness is declared per module in
`profile/content/modules-registry.yml`; stale provider output must follow the
module's last-known-good fallback semantics rather than inventing new values.

---

## 9. Relationship to Profile Reconstruction

These rules originated in the profile reconstruction work tracked by
[szmyty/szmyty#65](https://github.com/szmyty/szmyty/issues/65) and the content
governance work in #71. Issue #149 extends that governance model with explicit,
tested dynamic telemetry transformations rather than weakening the original
privacy/evidence constraints.
