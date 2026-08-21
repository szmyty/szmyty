# Cross-Surface Application Launch Review

**Review date:** 2026-08-21

**Roadmap item:** M6-05

**Tracking issue:** [`szmyty/szmyty#146`](https://github.com/szmyty/szmyty/issues/146)

**Machine gate:** [`docs/launch-gates/2026-08-21.json`](../launch-gates/2026-08-21.json)

## Decision

**NOT READY**

The application path is visibly stronger, but it is not yet safe to declare
finished. The profile has one bounded live pass, while the portfolio changes,
trust suite, resume, owner-only GitHub controls, Guild restriction, history
remediation, Scout privacy remediation, and Alan's final approval are still
open.

This review is the current launch decision. The 2026-08-09 final-readiness
report remains historical evidence and must not be treated as a current launch
approval.

## What is proven

- [`szmyty/szmyty#145`](https://github.com/szmyty/szmyty/pull/145) merged on
  2026-08-21 and published the Profile Done v1 composition.
- A signed-out review of the live GitHub profile README on desktop in GitHub's
  light theme passed on 2026-08-21.
- That README pass is deliberately narrow. Mobile, dark-theme, and
  reduced-motion behavior are not promoted to `PASS` by this observation.
- Portfolio pull requests #290 through #293 have successful GitHub Actions
  checks and Vercel reports each deployment as `Ready`.
- A `Ready` deployment is not a visual approval. The four draft previews are
  protected by Vercel SSO from the signed-out review environment, so their
  recruiter-facing matrix remains pending.

## Portfolio integration path

| PR | Scope | Automated state | Launch dependency |
| --- | --- | --- | --- |
| [`#291`](https://github.com/szmyty/portfolio/pull/291) | Mobile navigation and safe areas | Draft; CI and image optimization pass; Vercel Ready | Review at 360x740, 390x844, 412x915, phone landscape, and desktop |
| [`#293`](https://github.com/szmyty/portfolio/pull/293) | Infinity geometry and floppy camera fit | Draft; CI and image optimization pass; Vercel Ready | Its measured floppy bounds and camera-fit helper must survive integration into #292 |
| [`#292`](https://github.com/szmyty/portfolio/pull/292) | Canvas, media, and performance lifecycle | Draft; CI, performance budgets, and image optimization pass; Vercel Ready | Integrate #293's camera contract, then review reduced motion, no-WebGL, JavaScript failure, slow network, and context release |
| [`#290`](https://github.com/szmyty/portfolio/pull/290) | Selected engineering case studies | Draft; CI and image optimization pass; Vercel Ready | Review navigation, content hierarchy, claims, and links against the integrated shell |

The launch review must exercise the integrated result rather than approving
four independent previews as if they were one release. Integrate #291 and #293,
then preserve #293's camera-fit contract while merging #292. Merge the
independent #290 content lane next. Rebase #294 last, preserving #292's
Canvas/media lifecycle and static fallbacks, and rerun the complete trust
matrix.

## Open launch blockers

### Portfolio release and signed-out review

- [ ] Integrate and merge the approved portfolio drafts without losing the
      #293-to-#292 camera-fit contract.
- [ ] Complete desktop/mobile, light/dark, and reduced-motion review.
- [ ] Complete no-WebGL, JavaScript-failure, and slow-network fallback review.
- [ ] Confirm every selected-work and contact destination signed out.

### Trust suite

- [x] Record draft trust suite
      [`szmyty/portfolio#294`](https://github.com/szmyty/portfolio/pull/294)
      in the machine gate; its deterministic local suite passed.
- [x] CI run `32511398330` and the static-contract portion of Application
      Readiness run `32511398253` passed. The deployed release job was
      intentionally skipped.
- [x] Image-optimization run `32511398215` passed and Vercel reports the draft
      deployment Ready; the preview remains SSO-protected from signed-out
      review.
- [ ] Integrate #290 through #293 in the order above, rebase #294 last, rerun
      its checks, and merge it.
- [ ] Confirm Ego Hygiene and all four showcase destinations resolve with
      conservative, public-evidence-backed claims.
- [ ] Run the deployed-browser and live-destination release gate only against
      the integrated release candidate. No live release-gate pass is claimed
      by the draft PR.

### Resume

- [x] Record draft resume
      [`szmyty/resume#22`](https://github.com/szmyty/resume/pull/22) in the
      machine gate.
- [x] The final local 9-artifact/18-page public/application matrix passed
      visual quality, ATS text extraction, links, and privacy validation after
      the research-CV rebalance.
- [x] Corrective GitHub CI run `32511953627` passed both validation and full
      build/publication jobs, including all public/application/CV builds,
      gates, summary, and public artifact upload.
- [ ] Review and merge the draft. The exact-CI matrix clears the unchanged 30%
      word-share floor.

### Guild safety

- [ ] Restrict or intentionally unpublish
      [`167guild/167guild.io`](https://github.com/167guild/167guild.io) under
      [tracking issue #69](https://github.com/167guild/167guild.io/issues/69).
- [ ] Repeat a signed-out check of [`167guild.io`](https://167guild.io/).

The signed-out 2026-08-21 observation returned a public Wiki.js page titled
`Welcome | Wiki.js`. This is an active blocker until a later signed-out check
proves the deployment restricted or intentionally unpublished.

### Scout application-strategy privacy

- [ ] Complete
      [`szmyty/scout#3`](https://github.com/szmyty/scout/issues/3) and verify
      the public repository and Pages artifact expose only the approved
      aggregate career lanes.

Scout's current employer-level application strategy remains a separate active
privacy blocker. The launch gate cannot pass while exact employer, role,
status, deadline, score, priority, posting, or next-action data is public.

### Profile history remediation

- [ ] Complete the separately coordinated
      [profile-history remediation #147](https://github.com/szmyty/szmyty/issues/147)
      and its backup/recovery checks.

History remediation is intentionally outside issue #146's implementation
scope, but it remains a separate launch blocker. This review does not rewrite
or force-push repository history.

## Owner-only GitHub controls

These controls cannot be completed from repository code and remain Alan's
responsibility:

- [ ] Replace the currently observed GitHub bio, `🧠 Systems architect building
      AI-native workflows, agent tooling, and knowledge systems.`, with:
      `Software engineer building reliable developer platforms, local-first
      systems, and AI-assisted workflows.`
- [ ] Pin exactly the approved public proof set: `egohygiene/reflector`,
      `egohygiene/renderflow`, `egohygiene/relay`, `egohygiene/aether`,
      `egohygiene/optiflow`, and `egohygiene/mantle`.
- [ ] Confirm or change the public location from the currently observed
      `Boston, Massachusetts` to the approved region-level
      `Greater Boston, MA`.
- [ ] Configure branch protection or rulesets to require pull requests and the
      current required checks, and to prohibit default-branch deletion and
      force-pushes. Any temporary force-push exception for the history cutover
      belongs only to the separately approved
      [#147 operation](https://github.com/szmyty/szmyty/issues/147) and must be
      removed immediately after its validation.

## Promotion rule

The machine gate may move from `blocked` to `ready` only when all of the
following are true:

1. Every blocker in the manifest is resolved.
2. The integrated portfolio passes the complete signed-out visual and fallback
   matrix.
3. The trust-suite and resume PRs are recorded and their required validation
   passes.
4. Guild is restricted or intentionally unpublished and verified signed out.
5. Scout exposes only the approved aggregate public career strategy.
6. Profile-history remediation is complete.
7. Alan completes the owner-only controls and explicitly signs off.

## Alan sign-off

- [ ] Alan reviewed the final integrated recruiter journey and approves launch.
