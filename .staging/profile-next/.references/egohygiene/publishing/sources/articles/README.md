<p align="center">
  <img src="assets/logo.png" alt="Ego Hygiene Logo" width="180">
</p>

<h1 align="center">Ego Hygiene — Articles</h1>

<p align="center">
  🧠 Context-engineered essays on cognitive load, ADHD, software engineering, and systems-level thinking.
</p>

<p align="center">
  <a href="https://articles.egohygiene.io"><strong>Live Site</strong></a> •
  <a href="https://medium.com/@szmyty"><strong>Medium</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/egohygiene/articles/pages.yml?label=deploy&style=flat-square" alt="Deploy Status">
  <img src="https://img.shields.io/github/license/egohygiene/articles?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/last-commit/egohygiene/articles?style=flat-square" alt="Last Commit">
</p>

---

## About

This repository contains the canonical source for all Ego Hygiene essays.

Articles are written in Markdown, converted to HTML via GitHub Actions, and deployed automatically to:

👉 https://articles.egohygiene.io

Medium is used for distribution.  
GitHub Pages is the canonical source.

---

## Architecture

    articles/
      YYYY-MM-slug/
        published.md        ← canonical content
        draft.md
        references.md
        assets/

    templates/
      article-template.html
      article.css

    site/
      index.html
      article.css
      articles/...          ← generated

---

## Publishing Model

1. Write in `published.md`
2. Push to `main`
3. GitHub Action:
   - Converts Markdown → HTML via Pandoc
   - Injects into template
   - Regenerates index
   - Deploys to GitHub Pages
4. Publish to Medium with canonical link

---

## Canonical Rule

- Markdown is source of truth.
- HTML is generated.
- Do not manually edit files in `/site/articles`.
- Do not embed styling in Markdown.

Infrastructure should never slow idea expression.

---

## First Article

- Cognitive Load Is the Missing Layer in Developer Experience

---

## License

MIT
