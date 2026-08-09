# Final Owner Handoff Checklist

This checklist is the owner-facing companion to
[`docs/audits/FINAL-PROFILE-READINESS-REPORT.md`](audits/FINAL-PROFILE-READINESS-REPORT.md).
Use it after reviewing the audit report and before declaring the profile fully
signed off for active job-search use.

## Automated evidence snapshot

- [x] Local validation gate passed during the audit:
  - `poetry run python -m tools.profile_builder.cli validate`
  - `poetry run python profile/validate_assets.py assets/profile`
  - `bash .tasks/check-identity.sh`
  - `poetry run ruff check .`
  - `poetry run ruff format --check .`
  - `poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml`
  - `poetry run python -m pytest tests/test_workflows.py -k "workflow or site"`
  - `poetry run python -m pytest`
- [x] Latest `CI` push run on `master` succeeded: `31340834598`
- [x] Latest `Pages` run succeeded: `31337341343`
- [x] Latest `Update Profile` push run on `master` succeeded: `31340834587`
- [ ] Review the bounded follow-up from the audit report for the latest failed
      issue-triggered `Update Profile` run: `31340834869`

## Required owner-only GitHub UI verification

### Branch rules and required checks

- [ ] `master` has a branch protection rule or ruleset enabled.
- [ ] Required status checks match the current `CI` workflow expectations.
- [ ] Force-push to `master` is disabled.
- [ ] Branch deletion for `master` is disabled.

### Repository About, topics, and social preview

- [ ] About description is current and hiring-appropriate.
- [ ] Homepage points to the intended public destination.
- [ ] Repository topics still match the current profile/search strategy.
- [ ] Social preview image renders correctly in GitHub link previews.

### Pinned repositories

- [ ] Pinned repositories still reflect the strongest public work.
- [ ] No stale, archived, or placeholder repositories are pinned.

### Pages

- [ ] The live Pages URL loads successfully in a normal browser session:
      `https://szmyty.github.io/szmyty/`
- [ ] The AI-agent showcase detail page loads successfully:
      `https://szmyty.github.io/szmyty/ai-agent-showcase.html`
- [ ] The Pages environment shows a successful last deployment.
- [ ] The static preview image in the README still matches the live observatory
      closely enough for hiring-manager use.

### Discussions and issue routing

- [ ] Discussions remain enabled.
- [ ] The expected categories exist: `Announcements`, `General`, `Ideas`,
      `Polls`, `Q&A`, `Show and tell`.
- [ ] The contact links in `.github/ISSUE_TEMPLATE/config.yml` still resolve.
- [ ] The private security advisory flow is still enabled and reachable.

## Optional public-module decisions

- [ ] Leave ORCID disabled, or provide a verified public ORCID iD and enable it.
- [ ] Leave Medium disabled, or provide a verified public Medium profile and
      enable it.
- [ ] Leave education cards disabled, or confirm the UMass Lowell and Boston
      University records and enable the approved cards.
- [ ] Leave resume disabled, or publish a sanitized resume that passes
      `docs/RESUME-CHECKLIST.md`.
- [ ] Leave SoundCloud snapshot disabled, or provide the verified profile plus
      credentials/variables needed to publish the live snapshot.
- [ ] Leave Steam snapshot disabled, or provide `STEAM_ID64` and
      `STEAM_WEB_API_KEY` if the live snapshot should publish.
- [ ] Leave working-style disabled, or provide the approved 16Personalities
      fields before enabling it.
- [ ] Keep STARS disabled unless explicitly selecting public-safe items.
- [ ] Keep Oura disabled unless the full privacy approval path in
      `docs/RUNBOOK.md` is intentionally completed.

## Sign-off

- [ ] I reviewed
      `docs/audits/FINAL-PROFILE-READINESS-REPORT.md`
      and accept its recommendation.
- [ ] I completed or intentionally deferred each owner-only action above.
- [ ] The public profile is ready for active job-search use under the selected
      recommendation.
