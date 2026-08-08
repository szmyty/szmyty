# Ego Hygiene — Publishing

The publishing workspace for the Ego Hygiene ecosystem.

This workspace is organized around the **content lifecycle** — how knowledge moves from lived experience through extraction, authorship, and distribution.

---

## Publishing Lifecycle

```
Experience
      ↓
Knowledge Extraction
      ↓
Synapse
      ↓
Research
      ↓
Article
      ↓
Publication
      ↓
Distribution
      ↓
Archive
```

Platforms such as Medium and Pinterest are **publication channels** — not the source of truth.

Authored content in `sources/` is the canonical source of truth.

---

## Repository Organization

```
publishing/
    sources/        – Canonical authored source material
    channels/       – Publication mirrors and external platform output
    tools/          – Reusable publishing tooling
    specs/          – Publishing specifications
    schemas/        – Content schemas
    docs/           – Publishing documentation
```

---

## sources/

Canonical authored content. This is the source of truth.

```
sources/
    articles/       – Long-form essays authored in Markdown
    synapses/       – Living stream of insights and knowledge notes
    magazine/       – AI-powered magazine publishing engine and editions
    books/          – Placeholder for future book content
    papers/         – Placeholder for future research papers
```

Content here is actively authored and evolved inside the repository.

---

## channels/

Publication mirrors — synchronized or generated representations of published work.

These directories contain output synced from external platforms, not canonical authored content.

```
channels/
    medium/         – Synchronized Medium article archive
    pinterest/      – Synchronized Pinterest board archive
    website/        – Placeholder for future website publication
    newsletter/     – Placeholder for future newsletter output
    linkedin/       – Placeholder for future LinkedIn publication
```

---

## tools/

Reusable publishing tools, independent of any specific publication channel.

```
tools/
    mindlint/       – Spec-driven article linter for Ego Hygiene articles
    medium-rss/     – Medium RSS ingestion and synchronization tool
    pinterest-rss/  – Pinterest RSS ingestion and synchronization tool
```

---

## specs/

Publishing specifications that define structure, voice, compliance, and standards.

```
specs/
    article-structure.spec.md   – Article structural pattern
    medium-compliance.spec.md   – Medium publishing compliance rules
    research.spec.md            – Research and citation standards
    visuals.spec.md             – Visual asset standards
    voice.spec.md               – Brand voice and tone
```

---

## schemas/

Content schema definitions for structured content types.

---

## docs/

Publishing documentation — lifecycle, architecture, and operational guides.

See [docs/publishing-lifecycle.md](docs/publishing-lifecycle.md) for a detailed explanation of the publishing pipeline.

---

## Canonical Rule

- Markdown authored in `sources/` is the source of truth.
- Content in `channels/` is synchronized output — not manually edited.
- Tools in `tools/` are reusable and channel-agnostic.
- Specifications in `specs/` govern all authored content.
