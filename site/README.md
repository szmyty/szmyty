# site/

> **Status:** Foundation — deployable through the least-privilege
> `.github/workflows/pages.yml` workflow.

Optional GitHub Pages companion to the profile README.
See [docs/adr/0002-site-companion-static-html.md](../docs/adr/0002-site-companion-static-html.md)
for the full architectural decision.

## Directory structure

```
site/
  index.html            # Single entry point; all sections in semantic HTML
  css/
    tokens.css          # Design tokens (color, typography, spacing, motion)
    base.css            # Reset and baseline styles
    layout.css          # Responsive grid and section layout
    components.css      # Cards, badges, code blocks, diagrams
    theme.css           # Light/dark and high-contrast themes
    print.css           # Print stylesheet
  js/
    main.js             # Progressive enhancement only; no framework
  assets/
    favicon.svg         # Profile mark / favicon (placeholder)
    og-image.png        # Open Graph image — generate at build time
  data/
    profile.json        # Build-time generated from profile/ inputs
  robots.txt            # Allow all crawlers; reference sitemap
  sitemap.xml           # Single-page sitemap
  manifest.webmanifest  # PWA manifest
```

## Content ownership

All rendered content must be derived at build time from `profile/content/`
YAML inputs validated against `profile/schemas/`.  No content must be manually
duplicated between `README.md` and `site/index.html`.

## Performance budgets

| Asset | Budget |
|-------|--------|
| HTML | ≤ 50 KB uncompressed |
| CSS (total) | ≤ 30 KB uncompressed |
| JS (total) | ≤ 10 KB uncompressed |
| Images (total) | ≤ 300 KB |
| Fonts | System fonts preferred; web fonts ≤ 50 KB per face |

## What is not in this directory

- No React, Vue, Svelte, or other framework runtime.
- No Axios or `fetch()` calls to private APIs.
- No analytics scripts.
- No health, biometric, location, or weather modules.
- No default Vite starter assets.

## Deployment

GitHub Pages deployment is optional and is scoped to the dedicated
`pages.yml` workflow. Local validation parity is available via
`task validate-site`. `act` may be used for best-effort syntax checks, but it
does not faithfully reproduce Pages environments or OIDC-based deployment.
