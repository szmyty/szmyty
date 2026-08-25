# site/

> **Status:** Evidence-backed static companion, deployed through the
> least-privilege `.github/workflows/pages.yml` workflow.

This directory contains the optional GitHub Pages companion to the profile
README. The README remains the complete profile; this page presents a focused,
responsive view of the same approved positioning and selected public systems.

See
[ADR 0002](../docs/adr/0002-site-companion-static-html.md)
for the architectural decision.

## Content ownership

Stable public claims live in `profile/content/evidence.yml`. The projection in
`profile/content/site.yml` selects verified, public evidence IDs and declares
deployment metadata such as the canonical URL and default branch. It does not
duplicate claim prose.

`profile/templates/site-index.html.j2` renders those inputs into the committed
`site/index.html` artifact. Rendering fails when a selected record is missing,
not verified, not public, or lacks a required public URL.

Generate the page:

```sh
python -m tools.modules.site_companion
```

Verify that the committed page is current:

```sh
python -m tools.modules.site_companion --check
```

## Directory structure

```text
site/
  index.html                  # Generated, committed entry point
  ai-agent-showcase.html      # Separately generated optional observatory
  assets/favicon.svg          # Reviewed profile mark
  css/                        # Framework-free responsive styles
  js/main.js                  # Theme and navigation enhancement
  js/execution-observatory.js # Lazy observatory enhancement
  manifest.webmanifest        # Install metadata
  robots.txt                  # Public crawler policy
  sitemap.xml                 # Canonical page URL
```

## Boundaries

- No framework runtime or browser-side calls to private APIs.
- No analytics, tracking pixels, health, biometric, location, or weather data.
- No unpublished claims or records awaiting owner verification.
- No social-card image metadata unless the referenced asset is committed.
- The professional contact path remains the canonical portfolio.

## Validation and deployment

Run local parity checks with:

```sh
task validate-site
```

The Pages workflow performs the deterministic render check and site contract
tests before uploading the committed `site/` directory. Deployment remains
limited to pushes on `master`.
