# Staging Cutover Report

Date: 2026-08-09 (UTC)
Issue: szmyty/szmyty#80
Queue key: `szmyty-profile-rebuild-15`

## 1) Pre-removal gate status

- Queue items `01` through `14` are closed: issues [#66](https://github.com/szmyty/szmyty/issues/66) through [#79](https://github.com/szmyty/szmyty/issues/79).
- Migration ledger (`docs/MIGRATION.md`) now has completion evidence on all 95 rows.
- Adopted/merged/rewritten outputs exist in production paths tracked by the ledger.
- Deferred work is bounded to roadmap/epic tracking (`docs/ROADMAP.md`, szmyty/szmyty#65).
- Privacy-denied staged data families are not present in production paths.

## 2) Migration ledger final summary

Decision counts from `docs/MIGRATION.md`:

- `ADOPT`: 20
- `MERGE`: 7
- `REWRITE`: 2
- `REGENERATE`: 2
- `DEFER`: 18
- `ARCHIVE`: 24
- `DISCARD`: 10
- `PURGE`: 12
- Total rows: 95

Unresolved rows: **0**.

## 3) Feature inventory comparison (production vs staged variants)

Production README intentionally retains public, evidence-first sections and omits denied/deferred staged features.

Included in production:
- Brief, proof-at-a-glance, selected impact, featured systems, ecosystem map
- Engineering capabilities, experience/education, OSS collaboration, creative practice
- Current focus, contact
- Generated modules: `github-metrics`, `recent-activity`, `music-highlight`

Deliberately omitted from staged variants:
- Oura health dashboard / mood dashboard
- Precise location and location-derived weather cards
- Quote-of-the-day and staged operational-monitoring/log dashboards
- Staged React dashboard app runtime surfaces

These omissions are deliberate and align with `docs/PRIVACY.md` deny-list and architecture scope.

## 4) Privacy-denied data verification

Denied families checked:
- health/biometric (`oura`)
- mood inference
- location and map payloads
- location-derived weather

History-risk record remains explicitly tracked at:
- `docs/audits/public-data-security-audit.md`

No history rewrite was performed as part of this cutover.

## 5) Reproducibility without staged inputs

The active generation pipeline references only:
- `profile/content/*`
- `profile/artifacts/*`
- `profile/templates/*`
- `tools/modules/*`

No runtime path requires `.staging` inputs.

## 6) Runtime/reference cleanup

Cutover cleanup completed:
- Removed `.staging/` from production tree.
- Removed staging-only ignore and task references.
- Removed active instruction/config references to staged paths.

## 7) Rendering review notes

README media/fallback behavior confirmed in source:
- `<picture>` + light/dark `<source>` variants for hero banner.
- `<img>` fallback present for clients that ignore color-scheme sources.

Manual visual checklist documented for owner verification:
- [ ] Light theme desktop render
- [ ] Dark theme desktop render
- [ ] Mobile render (narrow viewport)
- [ ] Images-disabled behavior
- [ ] Third-party-failure behavior (external badge/service unavailable)

## 8) Manual GitHub settings checklist (not enforceable in repo code)

- [ ] Profile repository visibility and special-profile behavior
- [ ] About/website metadata
- [ ] Pinned repositories
- [ ] Pages configuration (if retained)
- [ ] Actions permissions
- [ ] Branch protection / rulesets
- [ ] Dependabot and security settings
- [ ] Funding/contact links

## 9) History-safety statement

Issue `01` historical exposure follow-up remains explicit and unhidden:
- see `docs/audits/public-data-security-audit.md` (“Reachable history”).
- any history rewrite/credential-rotation action remains a separate, manually approved operation.
