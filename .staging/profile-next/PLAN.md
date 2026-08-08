# Profile Reconstruction and Cutover Plan

## Status

Active

## Target Repository

`szmyty/profile-next`

## Final Destination

`szmyty/szmyty`

## Purpose

This plan defines how to reconstruct Alan Szmyt's GitHub profile as a clean, polished, maintainable, and portable repository.

The new profile will be built inside `szmyty/profile-next` using three locally cloned repositories as read-only references:

* `.references/szmyty`
* `.references/profile`
* `.references/egohygiene`

The completed repository must be suitable for direct migration into `szmyty/szmyty`, which is the special GitHub profile repository rendered on Alan's public GitHub account.

At the end of this effort, the contents of `profile-next` should be transferable into `szmyty/szmyty` without architectural changes, path rewrites, or feature reconstruction.

---

# 1. Outcome

The finished repository should provide:

* A polished public GitHub profile README.
* A coherent personal operating system aesthetic.
* Strong recruiter and engineering-team first impressions.
* Clear navigation into Alan's projects, organizations, portfolio, résumé, research, and creative work.
* Beautiful, statically generated visualizations.
* Reliable scheduled automation.
* Reusable and understandable profile modules.
* A documented architecture that supports future iteration.
* A safe and predictable migration path into `szmyty/szmyty`.

The final result should feel intentional, personal, technically sophisticated, and visually distinctive without becoming noisy or overengineered.

---

# 2. Source Repositories

## 2.1 `.references/szmyty`

This is the current live GitHub profile repository.

Use it to understand:

* Existing public profile behavior.
* Current README content.
* Existing working workflows.
* Existing generated visualizations.
* Existing branding.
* Current links and integrations.
* Features that are already known to work in a GitHub profile repository.

This repository represents the current production state, but it is not automatically the architectural source of truth.

---

## 2.2 `.references/profile`

This is the previous experimental profile repository.

Use it to identify:

* Strong ideas that were not completed.
* Visual concepts.
* Dashboard concepts.
* SVG generators.
* Data integrations.
* Organization and repository navigation ideas.
* Personal telemetry experiments.
* Useful scripts, templates, and assets.

Treat this repository as an idea mine rather than a codebase to merge wholesale.

---

## 2.3 `.references/egohygiene`

This repository contains mature and reusable engineering infrastructure.

Use it selectively for:

* Repository conventions.
* Architecture documentation patterns.
* Copilot instructions.
* Agent definitions.
* Specifications.
* Skills.
* Workflow hardening.
* Validation practices.
* Documentation structure.
* Licensing and governance patterns.
* Reusable configuration files.

Do not copy the entire engineering system.

Only adopt files and patterns that materially improve the profile repository.

---

# 3. Reference Repository Rules

The `.references/` directory is temporary development context.

It must follow these rules:

1. Treat all reference repositories as read-only.
2. Do not modify files inside `.references/`.
3. Do not create runtime dependencies on `.references/`.
4. Do not reference `.references/` from the public README.
5. Do not reference `.references/` from production workflows.
6. Do not import scripts or modules from `.references/`.
7. Do not copy files without reviewing and adapting them.
8. Do not carry forward obsolete architecture merely because it exists.
9. Do not commit nested repository metadata.
10. Remove `.references/` before final migration.

The finished repository must remain fully functional after `.references/` is deleted.

---

# 4. Core Engineering Principles

## 4.1 The profile is the product

The public profile experience is the primary deliverable.

Supporting infrastructure exists only to improve:

* Presentation.
* Reliability.
* Maintainability.
* Portability.
* Developer experience.

Infrastructure must not become the dominant product.

---

## 4.2 Rebuild concepts, not repositories

Do not combine the old repositories through bulk copying.

For each discovered feature, choose one classification:

* **Keep** — the implementation is strong and portable.
* **Adapt** — the idea and implementation are useful but require cleanup.
* **Rewrite** — the concept is strong but the implementation is unsuitable.
* **Defer** — useful, but not required for the first migration milestone.
* **Discard** — does not improve the final profile.
* **Archive only** — historically interesting but not part of the new system.

---

## 4.3 Design before automation

For every public profile section:

1. Define its purpose.
2. Define the information it communicates.
3. Build a static or handwritten version.
4. Validate the visual hierarchy.
5. Introduce automation only when automation reduces maintenance.

Automation must not determine the design.

---

## 4.4 Static generation over live dependencies

The GitHub profile README is a static document.

Dynamic information should generally follow this lifecycle:

```
External or repository data
        ↓
Provider or collector
        ↓
Normalized data
        ↓
Renderer
        ↓
Committed static artifact
        ↓
README
```

Prefer committed SVG, JSON, or Markdown artifacts over runtime third-party embeds.

---

## 4.5 Portable by construction

The repository is temporarily named `profile-next`, but its final home is `szmyty/szmyty`.

Therefore:

* Do not hardcode `szmyty/profile-next` into generated assets.
* Do not hardcode `profile-next` into workflow logic.
* Do not rely on the staging repository name.
* Prefer repository-relative paths.
* Use GitHub context variables where repository identity is needed.
* Design workflows to run unchanged after migration.
* Ensure links intended for the public profile resolve correctly from `szmyty/szmyty`.

---

## 4.6 Progressive complexity

Begin with the smallest architecture that satisfies the profile.

Add abstractions only after at least two concrete consumers justify them.

Avoid:

* Framework-building before the profile is complete.
* Large custom action ecosystems.
* Duplicate provider patterns.
* Multiple competing rendering systems.
* Excessive generated files.
* Unnecessary dashboards or web applications.
* Infrastructure copied only for completeness.

---

# 5. Public Profile Information Architecture

The README should evolve toward a cohesive structure similar to:

1. Hero
2. Primary navigation
3. About
4. Current focus
5. GitHub statistics
6. Project ecosystem
7. Organizations
8. Featured projects
9. Engineering principles
10. Technology and capabilities
11. Research and learning
12. Creative technology and music
13. Latest activity
14. Contact
15. Footer

This structure is directional rather than rigid.

Sections may be combined, reordered, or removed when doing so produces a stronger profile.

Every section must answer a useful visitor question.

Examples:

* Who is Alan?
* What does he build?
* What kinds of roles fit him?
* How does he think?
* What has he shipped?
* Where should I explore next?
* How can I contact him?

---

# 6. Target Repository Architecture

The implementation should converge toward a small and understandable structure.

A likely target is:

```
.
├── .github
│   ├── agents
│   ├── artifacts
│   │   └── <module>
│   ├── instructions
│   ├── scripts
│   │   └── <module>
│   ├── specs
│   │   └── <module>.spec.md
│   ├── templates
│   │   └── <module>
│   └── workflows
├── assets
│   ├── branding
│   ├── icons
│   └── images
├── docs
│   ├── ARCHITECTURE.md
│   ├── DESIGN.md
│   ├── MODULES.md
│   ├── MIGRATION.md
│   └── ROADMAP.md
├── tests
├── .editorconfig
├── .gitignore
├── AGENTS.md
├── LICENSE
├── PLAN.md
├── README.md
└── pyproject.toml
```

This is not a mandate to create every directory immediately.

Only create directories that have a clear current purpose.

---

# 7. Module Architecture

Dynamic or visually complex profile sections should be modeled as modules.

A module may contain:

* A specification.
* A data provider.
* A normalizer.
* A renderer.
* Templates.
* Generated artifacts.
* Tests.
* A scheduled or manual workflow.
* README integration.

A complete module lifecycle is:

```
Discovery
    ↓
Design
    ↓
Specification
    ↓
Static prototype
    ↓
Implementation
    ↓
Artifact generation
    ↓
Validation
    ↓
README integration
    ↓
Maintenance
```

Modules should remain independent enough that one failed integration does not corrupt the entire README.

---

# 8. Generated Artifact Strategy

Generated public outputs should live under:

```
.github/artifacts/<module>/
```

Examples:

```
.github/artifacts/github/overview.svg
.github/artifacts/github/languages.svg
.github/artifacts/github/stats.json
.github/artifacts/activity/recent.svg
```

Hand-authored visual assets should live under:

```
assets/
```

The distinction is:

* `assets/` contains source-controlled creative material.
* `.github/artifacts/` contains reproducible generated outputs.

Generated artifacts must be committed when the README embeds them.

---

# 9. Automation Strategy

Use GitHub Actions for scheduled updates.

Each automation should:

* Support `workflow_dispatch`.
* Use a reasonable schedule rather than excessive polling.
* Use least-privilege permissions.
* Pin or deliberately version third-party actions.
* Avoid exposing secrets.
* Generate deterministic outputs where practical.
* Preserve the last successful artifacts when an API fails.
* Commit only meaningful changes.
* Prevent workflow-trigger loops.
* expose useful failure diagnostics.
* Work after migration to `szmyty/szmyty`.

Prefer one coordinated profile update workflow or a small number of coherent workflows over many tiny and inconsistent workflows.

Nightly or daily refreshes are sufficient for most profile telemetry.

---

# 10. Data and Privacy Boundaries

Public profile data must be intentionally public.

Do not expose:

* Private repository names.
* Private contribution details.
* Personal access tokens.
* Health information.
* Precise location.
* Sensitive Oura or biometric data.
* Private email addresses not intended for publication.
* Internal employment information.
* Secret organization metadata.

Any personal telemetry feature must be explicitly reviewed before inclusion.

Public value must justify the integration and privacy cost.

---

# 11. Documentation Foundation

The repository should include concise documentation that prevents future architectural drift.

## `README.md`

The public GitHub profile and primary product.

## `PLAN.md`

The reconstruction, migration, and cutover plan.

## `docs/ARCHITECTURE.md`

Defines:

* Repository boundaries.
* Data flow.
* Module organization.
* Automation model.
* Generated artifact ownership.
* Portability requirements.

## `docs/DESIGN.md`

Defines:

* Visual direction.
* Tone.
* Layout principles.
* Accessibility expectations.
* Dark and light mode behavior.
* SVG design conventions.

## `docs/MODULES.md`

Defines:

* What constitutes a module.
* Required and optional module files.
* Module lifecycle.
* Failure isolation.
* README integration conventions.

## `docs/ROADMAP.md`

Tracks:

* Foundation work.
* Profile sections.
* Dynamic modules.
* Migration readiness.
* Post-migration enhancements.

## `docs/MIGRATION.md`

Defines the exact staging-to-production cutover procedure.

## `AGENTS.md`

Gives AI coding agents repository-specific implementation instructions.

Documentation should remain proportional to the repository.

Do not reproduce the full Ego Hygiene documentation system unless it is genuinely needed.

---

# 12. Discovery Phase

Before implementing the new profile, inspect all three reference repositories.

Produce a discovery inventory covering:

* Existing README sections.
* Branding assets.
* Static images.
* SVG visualizations.
* Generators.
* Data providers.
* Workflows.
* Secrets and required environment variables.
* Reusable scripts.
* Existing tests.
* Documentation.
* Broken integrations.
* Duplicate implementations.
* Hardcoded repository paths.
* Features that depend on retired APIs.
* Features unsuitable for a public profile.
* Features worth preserving.

Document the result in:

```
docs/reference-inventory.md
```

The inventory should include a decision table:

| Source | Feature | Current State | Decision | Target Module | Notes |
| ------ | ------- | ------------- | -------- | ------------- | ----- |

---

# 13. Reconstruction Phases

## Phase 1: Repository foundation

Establish:

* Repository purpose.
* Architecture.
* Design principles.
* AI instructions.
* Coding conventions.
* Dependency management.
* Validation commands.
* Migration constraints.

Do not implement every profile feature during this phase.

---

## Phase 2: Reference discovery

Inspect all source repositories.

Create:

* Feature inventory.
* Asset inventory.
* Workflow inventory.
* Integration inventory.
* Keep/adapt/rewrite/defer/discard decisions.

---

## Phase 3: Static profile composition

Build a coherent static README using placeholders or manually authored sections.

The static profile should already communicate a compelling engineering story before dynamic features are introduced.

---

## Phase 4: Dynamic modules

Implement selected modules one at a time.

Likely early modules include:

1. GitHub statistics.
2. Organizations and repository navigation.
3. Featured projects.
4. Recent activity.
5. Project ecosystem visualization.

Each module must follow the established architecture.

---

## Phase 5: Visual polish

Validate:

* GitHub light mode.
* GitHub dark mode.
* Desktop width.
* Narrow/mobile width.
* SVG clipping.
* Text readability.
* Link behavior.
* Image loading.
* Visual consistency.
* Accessibility.
* Reduced-motion behavior where relevant.

---

## Phase 6: Migration readiness

Confirm that:

* `.references/` is no longer needed.
* No path references `profile-next`.
* No URL incorrectly targets the staging repository.
* Workflows use portable GitHub context.
* Secrets required in the production repository are documented.
* All embedded assets use valid relative paths.
* All generation commands work from a clean clone.
* Scheduled workflows can run in `szmyty/szmyty`.
* The README renders correctly in GitHub's profile context.

---

## Phase 7: Production cutover

Archive the old repositories before destructive changes.

Then:

1. Preserve the existing `szmyty/szmyty` repository state in the archive repository.
2. Preserve `szmyty/profile` in the archive repository.
3. Disable or remove obsolete workflows from the production profile.
4. Clear the replaceable contents of `szmyty/szmyty`.
5. Copy the final contents of `profile-next` into `szmyty/szmyty`.
6. Exclude `.references/`, local workspace files, nested `.git` directories, caches, and temporary audit outputs.
7. Review the migration diff.
8. Push the replacement.
9. Run all manual workflows.
10. Verify the public GitHub profile.
11. Observe at least one scheduled automation cycle.
12. Delete `szmyty/profile` and `szmyty/profile-next` only after verification.

---

# 14. Migration Exclusions

Do not migrate:

```
.references/
profile-next.code-workspace
nested .git directories
local environment files
caches
temporary logs
generated debug output
obsolete audit artifacts
stale secrets
development-only credentials
```

Add appropriate exclusions to `.gitignore`.

---

# 15. Migration Validation Checklist

## Repository portability

* [ ] No production code references `.references/`.
* [ ] No production code references `profile-next`.
* [ ] No required link points to the staging repository.
* [ ] Relative asset paths work from the repository root.
* [ ] Workflows derive repository identity from GitHub context.
* [ ] The default branch is not unnecessarily hardcoded.
* [ ] Installation and generation commands work from a clean clone.

## README rendering

* [ ] README renders on GitHub without broken HTML.
* [ ] All images load.
* [ ] All SVGs load.
* [ ] All links resolve.
* [ ] Light mode is readable.
* [ ] Dark mode is readable.
* [ ] Narrow layouts remain usable.
* [ ] Alt text exists for meaningful images.
* [ ] Decorative animation does not impair readability.

## Automation

* [ ] Manual workflows succeed.
* [ ] Scheduled workflows are enabled.
* [ ] Permissions use least privilege.
* [ ] Secrets are documented.
* [ ] Generated artifacts are committed correctly.
* [ ] No recursive workflow loop occurs.
* [ ] API failure does not erase valid existing artifacts.
* [ ] Automation commit messages are consistent.

## Repository quality

* [ ] Documentation matches implementation.
* [ ] Tests pass.
* [ ] Formatting and linting pass.
* [ ] No secrets are committed.
* [ ] No unnecessary reference files remain.
* [ ] No obsolete duplicate implementations remain.
* [ ] The repository remains reasonably small and understandable.

---

# 16. Definition of Done

The reconstruction milestone is complete when:

1. The public README presents a polished and coherent profile.
2. Selected dynamic modules generate reliable static artifacts.
3. The architecture is documented.
4. The repository works independently of `.references/`.
5. The repository is portable into `szmyty/szmyty`.
6. Migration documentation is complete.
7. Validation succeeds from a clean clone.
8. The production cutover has been completed successfully.
9. The public profile has been manually verified.
10. The old repositories have been archived before deletion.
11. A post-migration audit has been generated.
12. Future improvements can be handled through focused GitHub issues.

---

# 17. Post-Migration Audit

After the final repository is running as `szmyty/szmyty`, perform a comprehensive audit.

The audit should evaluate:

* Public profile impact.
* Recruiter readability.
* Technical credibility.
* Visual design.
* Accessibility.
* Responsive rendering.
* GitHub Actions reliability.
* API usage.
* Security.
* Privacy.
* Repository maintainability.
* Documentation accuracy.
* Dead files.
* Duplicate code.
* Broken links.
* Broken assets.
* Performance.
* Future module opportunities.
* Features worth removing.
* Features worth simplifying.

Write the audit to:

```
.engineering/audits/profile-post-migration-audit.md
```

The audit must separate findings into:

* Critical fixes.
* High-value improvements.
* Medium-priority enhancements.
* Low-priority polish.
* Deferred ideas.
* Explicit non-recommendations.

Each actionable finding should be suitable for conversion into a focused GitHub issue.

---

# 18. Final Principle

This project is not a merge of two old profiles.

It is a deliberate reconstruction informed by their strongest ideas.

The final repository should demonstrate the same qualities the profile claims Alan brings to engineering:

* Systems thinking.
* Architectural judgment.
* Automation.
* Design awareness.
* Maintainability.
* Curiosity.
* Human-centered decision-making.
* Continuous improvement.

