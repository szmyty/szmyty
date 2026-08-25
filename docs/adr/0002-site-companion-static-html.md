# ADR 0002: Profile Companion Site — Generated Static HTML

**Status:** Accepted, amended 2026-08-25

**Date:** 2026-08-09

**Stable queue key:** `szmyty-profile-rebuild-11`

**Original issue:** `szmyty/szmyty#76`

**Current-content amendment:** `szmyty/szmyty#169`

---

## Context

The original companion-site work replaced an incomplete Vite and React starter
with a framework-free page under `site/`. That kept the runtime small and the
deployment simple, but the first implementation left its professional copy,
repository links, metadata, and architecture narrative hand-authored in
`site/index.html`.

By August 2026, that copy had drifted from the approved README and evidence
catalog. It included retired repositories, an unsupported staff-level title, a
placeholder architecture diagram, a stale SoundCloud path, a missing social
card image, and a license URL bound to the wrong default branch. The page could
no longer meet its stated same-source contract.

The companion still provides useful responsive navigation, theme controls, and
structured metadata, so retiring it is not necessary if drift is prevented.

## Decision

Keep the companion as plain HTML, CSS, and progressive JavaScript, but treat
`site/index.html` as a generated and committed artifact.

```text
profile/content/evidence.yml
          +
profile/content/site.yml
          +
profile/templates/site-index.html.j2
          |
          v
tools/modules/site_companion.py
          |
          v
site/index.html
```

The responsibilities are deliberately separate:

| Input | Responsibility |
|---|---|
| `evidence.yml` | Reviewed claim text, verification status, sensitivity, and public proof URL |
| `site.yml` | Evidence-ID selection, canonical URL, source repository, and default branch |
| `site-index.html.j2` | Semantic presentation and metadata structure |
| `site_companion.py` | Validation, evidence resolution, HTML escaping, and deterministic rendering |
| `site/index.html` | Immediately deployable build artifact |

The generator rejects evidence that is missing, not verified, not public, or
missing a URL where the page needs a destination. The Pages workflow runs the
generator in `--check` mode and fails if the committed HTML is stale.

## Information architecture

The current page is intentionally narrower than the original draft:

1. Approved positioning and portfolio/GitHub actions.
2. Reflector, Renderflow, Relay, and Optiflow as the current proof set.
3. The approved AI-assisted-work disclosure.
4. The public Ego Hygiene lab relationship and approved professional lanes.
5. Verified creative-work and professional-contact destinations.
6. Repository source and a default-branch-safe license link.

The speculative architecture diagram and generic capability claims were
removed. Future architecture claims require their own verified public evidence
before they can enter the projection.

## Metadata and asset policy

- The page title, description, Open Graph fields, Twitter fields, and JSON-LD
  use the approved identity and positioning records.
- The canonical URL is declared once in `site.yml`.
- Social-card image fields are omitted until a reviewed image is committed.
- Repository file links derive their branch from `site.yml`; they must not
  assume `main`.
- Local asset references and page anchors are covered by deterministic tests.

## Runtime and privacy boundaries

- No React, Vue, Svelte, or other component runtime.
- No browser-side `fetch()` or Axios calls to private APIs.
- No analytics or tracking pixels.
- No health, biometric, location, or weather content.
- No direct personal mailbox; professional inquiries route through the public
  portfolio.
- The document remains usable without JavaScript. JavaScript only enhances the
  theme control and active navigation state.

## Consequences

- Stable copy is edited in the evidence catalog, not in generated HTML.
- Selecting a different public system requires a reviewed evidence record and a
  small `site.yml` projection change.
- Contributors must regenerate `site/index.html` after relevant input changes.
- CI prevents source/output drift before a Pages deployment.
- The static deployment remains simple, cacheable, accessible, and independent
  of private services.
- A framework or runtime data source still requires a new ADR.
