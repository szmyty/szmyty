# Design

This document defines the visual direction, layout principles, tone, and
accessibility expectations for Alan Szmyt's GitHub profile.

---

## Visual Direction

The profile should feel:

- **Technically sophisticated** — structured, intentional, developer-native.
- **Personally distinctive** — not a template; reflects Alan's identity.
- **Calm and legible** — not noisy, flashy, or cluttered.
- **Purposeful** — every visual element earns its place.

Avoid:
- Excessive animated GIFs.
- Badge overload (use badges only where they add signal).
- Dense walls of text without structure.
- Visual inconsistency between sections.
- Features copied from other profiles without an intentional decision.

---

## Color Palette

The profile inherits the branding palette established in `assets/branding/`:

| Role | Light mode | Dark mode |
|------|-----------|-----------|
| Background | `#ffffff` | `#0d1117` |
| Primary text | `#1f2328` | `#e6edf3` |
| Accent | `#4a4e69` | `#8b949e` |
| Accent dark | `#1a1a2e` | `#161b22` |
| Link | `#0969da` | `#58a6ff` |

Badge style: `for-the-badge` with `labelColor=1a1a2e` and `color=4a4e69`.

---

## Typography

GitHub profile READMEs use GitHub Markdown rendering. Typography is therefore
constrained to:

- Standard Markdown heading levels (`h1`–`h4`).
- `<div align="center">` for centering.
- `<table>` for multi-column layouts.
- `<p>` for prose with alignment control.
- `<strong>` / `<em>` for emphasis.
- `<details>` / `<summary>` for collapsible sections.

Use heading levels consistently:
- `h2` — major sections.
- `h3` — subsections within a section.
- `h4` — fine-grained groupings (use sparingly).

---

## Layout Principles

### Information hierarchy

Top of the README answers: **Who is Alan?**
Middle sections answer: **What does he build? How does he think?**
Bottom sections answer: **Where do I go next? How do I reach him?**

### Section ordering (directional, not rigid)

1. Hero — branding header, badges, tagline.
2. Navigation — collapsible quick-links to sections.
3. About — brief personal introduction.
4. Current Focus — what is actively being worked on.
5. GitHub Statistics — generated metrics.
6. Project Ecosystem — overview of Alan's project landscape.
7. Organizations — Incompris LLC, egohygiene, szmyty.
8. Featured Projects — 6–8 flagship repositories.
9. Engineering Principles — how Alan thinks about engineering.
10. Technology Stack — languages, frameworks, infrastructure.
11. Research & Learning — current exploration areas.
12. Creative Technology — music, AI-creative intersections.
13. Latest Activity — recent GitHub activity (automated).
14. Contact — ways to reach Alan.
15. Footer — closing branding element.

### Column layouts

Use `<table>` with `width="33%"` columns for three-column grids.
Use `<table>` with `width="50%"` columns for two-column grids.
Always include `align="center"` and `valign="top"`.

### Section dividers

Use `<br/>` between major sections.
Use `---` (horizontal rule) to separate top-level sections in Markdown.

---

## Dark Mode and Light Mode

The profile must be readable in both GitHub themes.

SVG assets must use `prefers-color-scheme` media queries or be designed for
contrast in both modes.

Avoid:
- SVGs with white text on white backgrounds in light mode.
- SVGs with black text on black backgrounds in dark mode.
- Hardcoded `fill` colors that do not work in one mode.

Test profile rendering in both themes before marking any visual section as
complete.

---

## Accessibility

- All images must include descriptive `alt` text.
- Decorative SVGs may use `alt=""` or `role="presentation"`.
- Avoid relying on color alone to convey information.
- Animated elements must not flash faster than 3 times per second.
- Layout must remain readable at narrow viewport widths (GitHub's mobile view).

---

## Badge Conventions

Use badges consistently:

```markdown
[![Label](https://img.shields.io/badge/Label-Value-COLOR?style=for-the-badge&logo=LOGO&logoColor=white&labelColor=1a1a2e)](URL)
```

Badge categories:
- Profile identity (followers, views, stars) — in Hero section.
- Technology stack — in Technology section (use devicons, not badges).
- Project status — in Featured Projects section.
- Workflow status — in Automation section only.

Avoid:
- More than 6 identity badges in the Hero section.
- Badge rows that wrap awkwardly at standard GitHub viewport widths.
- Badges that link to external services that may go down.

---

## SVG Design Conventions

Generated SVGs in `.github/artifacts/` must:

- Use `viewBox` rather than fixed `width`/`height` where possible.
- Include a `<title>` element for accessibility.
- Use `currentColor` or explicit, contrast-safe fills.
- Include a UTC generation timestamp in an XML comment.
- Be reproducible given the same input data.

Hand-authored SVGs in `assets/branding/` must:
- Be optimized (remove unnecessary metadata, editor layers).
- Work at full width (`width="100%"`) without distortion.
- Be tested in both light and dark GitHub themes.

---

## Tone

The profile should read as:

- **Confident but not arrogant.**
- **Technical but approachable.**
- **Curious and reflective.**
- **Professional but personal.**

Write section copy in the first person singular ("I build", "I focus on").
Avoid corporate buzzword density.
Favor concrete examples over abstract claims.

---

## Section Copy Standards

- Keep "About" to 3–5 sentences.
- Keep "Current Focus" to 5–8 bullet points.
- Keep "Engineering Principles" to 6–8 principles.
- Keep "Research & Learning" to 5–8 topics.
- Keep "Contact" concise — link, don't explain.

---

## Anti-Patterns

| Anti-pattern | Why to avoid |
|-------------|-------------|
| Walls of text | Kills scanability; profiles are skimmed |
| Too many animated GIFs | Distracting; accessibility concern |
| Stale data sections | Outdated info degrades trust |
| Placeholder text left visible | Profile looks unfinished |
| External badge services with no fallback | Broken images look unprofessional |
| Copying entire profiles | Makes the profile feel impersonal |
