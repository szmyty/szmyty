# ADR 0002: Profile Companion Site — Static HTML over Vite/React

**Status:** Accepted
**Date:** 2026-08-09
**Stable queue key:** `szmyty-profile-rebuild-11`
**Closes:** szmyty/szmyty#76

---

## Context

The incomplete staged dashboard under `.staging/dashboard-app/` is a Vite +
React + TypeScript application scaffolded from the default Vite starter.  It
includes:

- Axios for runtime HTTP requests to profile APIs.
- Default Vite/React starter copy and placeholder assets.
- No real profile content.
- No accessibility, performance, or build-time validation.

The issue (`szmyty/szmyty#76`) requires a companion site that:

1. Consumes the same reviewed public content used by the README.
2. Works as a static deployment with no browser-side calls to private APIs.
3. Contains no health, biometric, location, or weather modules.
4. Includes responsive, keyboard, reduced-motion, high-contrast, and
   focus-state behavior.
5. Defines build-time schema validation and fails on unreviewed/private data.
6. Adds metadata: title, description, canonical URL, Open Graph/Twitter cards,
   favicon, robots policy, and structured data.
7. Remains optional; the README must still tell the complete professional story.
8. Is deployed only through a dedicated least-privilege GitHub Pages workflow.

---

## Decision

**Reject the Vite/React application** in `.staging/dashboard-app/` and instead
implement the companion site as **plain HTML + CSS** under `site/`.

### Rationale

| Criterion | Vite/React | Static HTML/CSS |
|-----------|-----------|-----------------|
| Build complexity | High — bundler, TS compiler, JSX transform | Low — no bundler required |
| JavaScript footprint | Large (React runtime) | Zero or minimal (progressive enhancement only) |
| No-JavaScript experience | Blank page | Full content |
| Accessibility baseline | Requires explicit ARIA instrumentation | Semantic HTML is accessible by default |
| Reduced-motion | Requires `prefers-reduced-motion` implementation across components | Single CSS rule |
| Content-source coupling | Runtime fetch or bundled duplication | Build-time template render from the same `profile/` inputs |
| Default starter junk | Present in `.staging/dashboard-app/` | None |
| Runtime Axios calls | Present in `.staging/dashboard-app/` | None |
| Deployment readiness | Requires CI build step | Single `site/index.html` is immediately deployable |
| Browser support | Depends on bundler target | Unrestricted |

### What the static site provides that the README cannot

- Richer visual layout (CSS grid, responsive typography, dark/light theme).
- Animated but reduced-motion-safe transitions.
- Keyboard-navigable project cards and architecture diagrams.
- Open Graph / Twitter card metadata.
- Structured data (JSON-LD for `Person` and `SoftwareApplication`).
- Sitemap and canonical URL.

### Explicitly rejected

| Rejected feature | Reason |
|-----------------|--------|
| Axios or `fetch()` to private APIs | No browser network call may require a secret |
| React / Vue / Svelte runtime | No interactivity requires a component framework |
| Canvas-only architecture diagrams | Must be keyboard-inspectable and have alt text |
| Analytics | Requires a separate, explicit privacy decision |
| Health / biometric / location / weather modules | Prohibited by issue requirements |
| Default Vite starter assets | Not relevant to this profile |

---

## Architecture: `site/` boundary

```
site/
  index.html          # Single entry point; all sections in semantic HTML
  css/
    tokens.css        # Design tokens (color, typography, spacing, motion)
    base.css          # Reset and baseline styles
    layout.css        # Responsive grid and section layout
    components.css    # Cards, badges, code blocks, diagrams
    theme.css         # Light/dark theme via CSS custom properties
    print.css         # Print stylesheet
  js/
    main.js           # Progressive-enhancement only; no framework
  assets/
    favicon.svg       # Profile mark / favicon
    og-image.png      # Open Graph image (1200×630)
  data/
    profile.json      # Build-time-generated; derived from profile/ inputs
  robots.txt          # Disallow nothing; allow crawlers
  sitemap.xml         # Single-page sitemap
  manifest.webmanifest  # PWA manifest (optional; name, icons, display)
```

### Information architecture (section order)

1. **Hero and positioning** — name, title, one-line summary, primary CTA.
2. **Selected impact** — three to five measurable outcomes from the README.
3. **Flagship system case studies** — project cards with inspectable links.
4. **Ego Hygiene architecture** — interactive but accessible diagram (SVG +
   ARIA roles, keyboard navigation, text alternative).
5. **Capabilities and experience** — skill areas aligned to the README.
6. **Creative technology / music** — SoundCloud embed or text link only.
7. **Contact** — GitHub link, email, no tracking pixels.

### Content ownership

- All text is rendered at build time from `profile/content/` YAML inputs.
- The build step fails if any required content key is missing or fails schema
  validation (`profile/schemas/`).
- No content is duplicated manually between `README.md` and `site/index.html`.

### Performance budgets

| Asset category | Budget |
|---------------|--------|
| HTML | ≤ 50 KB uncompressed |
| CSS (total) | ≤ 30 KB uncompressed |
| JS (total) | ≤ 10 KB uncompressed |
| Images (total) | ≤ 300 KB |
| Fonts | System fonts preferred; web fonts ≤ 50 KB per face |
| LCP | ≤ 2.5 s on 4G simulated |
| CLS | < 0.1 |
| FID/INP | ≤ 200 ms |

### Accessibility requirements

- WCAG 2.1 AA minimum.
- All interactive elements keyboard-reachable with visible focus indicator.
- `prefers-reduced-motion` removes or stills all animations.
- `prefers-contrast: more` switches to high-contrast palette.
- Semantic landmarks: `<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`.
- All images have meaningful `alt` text or `role="presentation"` if decorative.
- Color is not the sole carrier of information.

---

## Consequences

- `.staging/dashboard-app/` is archived (marked `ARCHIVE` in
  `docs/MIGRATION.md`); the directory remains as historical evidence but is
  not promoted.
- A new `site/` directory is created with the documented structure.
- The site is deployed only through `.github/workflows/pages.yml`, which keeps
  GitHub Pages permissions isolated to the deployment job.
- Future JavaScript enrichment (e.g., a filter or search widget) may be added
  via vanilla JS in `site/js/main.js` without introducing a framework.
- If requirements change to require a framework, a new ADR must be filed before
  any framework code is merged.
