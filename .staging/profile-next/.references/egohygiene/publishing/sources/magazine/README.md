<p align="center">
  <img src="assets/logo.png" alt="Magazine Header" width="800">
</p>

<h1 align="center">Magazine</h1>

<p align="center">
  Deterministic AI-Powered Publishing Engine
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/poetry-managed-informational?style=flat-square" alt="Poetry">
  <img src="https://img.shields.io/badge/cli-click-darkgreen?style=flat-square" alt="CLI">
  <img src="https://img.shields.io/badge/code%20style-ruff-black?style=flat-square" alt="Code Style">
  <img src="https://img.shields.io/badge/tests-pytest-blue?style=flat-square" alt="Tests">
  <br>
  <img src="https://img.shields.io/badge/AI-powered-6a0dad?style=flat-square" alt="AI Powered">
  <img src="https://img.shields.io/badge/builds-deterministic-4682b4?style=flat-square" alt="Deterministic Builds">
  <img src="https://img.shields.io/badge/architecture-modular-4682b4?style=flat-square" alt="Modular Architecture">
  <img src="https://img.shields.io/badge/config-12--factor-4682b4?style=flat-square" alt="12-Factor Ready">
  <img src="https://img.shields.io/badge/pattern-strategy-607d8b?style=flat-square" alt="Strategy Pattern">
  <br>
  <img src="https://img.shields.io/badge/export-CBZ%20%7C%20PDF%20%7C%20META-informational?style=flat-square" alt="Multi-Format Export">
  <img src="https://img.shields.io/badge/fountain-AI%20compiler-6a0dad?style=flat-square" alt="AI Fountain Compiler">
  <br>
  <img src="https://img.shields.io/badge/license-proprietary-lightgrey?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/version-0.1.0-orange?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/status-alpha-yellow?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform">
</p>

---

## Overview

**Magazine** is a deterministic, AI-powered publishing engine for generating polished magazine pages and edition bundles from structured source assets.

It solves the problem of reproducible, high-quality creative production by combining a hash-based caching pipeline, an AI Fountain screenplay compiler, and a modular stage architecture into a single clean CLI tool.

Built for creators who need professional output without manual overhead.

**Key capabilities:**

- Compile AI-generated screenplays from page assets
- Build multi-format edition bundles (CBZ, PDF, metadata)
- Deterministic, cache-aware regeneration
- Click-based CLI with Poetry-managed environment

---

## Features

- **Deterministic AI Fountain compiler** — generates screenplays from page images using configurable AI models
- **Modular pipeline architecture** — each production stage is independently composable
- **Click-based CLI** — clean command interface for pages, editions, and bundles
- **Poetry-managed environment** — reproducible dependency resolution
- **Hash-based regeneration** — only rebuilds when source assets change
- **AI stage invalidation** — force or disable AI stages independently
- **Multi-format asset generation** — CBZ, reader PDF, press PDF, and metadata bundles
- **Future video stage** — AI-driven animation per page (planned)
- **Future size variants** — multi-format comic size export (planned)
- **12-factor configuration** — all behaviour overridable via environment variables
- **Modular design (Strategy pattern)** — swap AI backends without changing pipeline logic
- **CI-ready** — deterministic output suitable for automated publishing workflows

---

## Architecture

Conceptual production pipeline:

    page.png
        ↓
    Fountain AI Stage
        ↓
    Image Assets
        ↓
    Screenplay Assets
        ↓
    Size Variants (future)
        ↓
    Video Variants (future)
        ↓
    Edition Bundle

---

## Installation

Requires Python 3.11+ and [Poetry](https://python-poetry.org/).

    git clone https://github.com/egohygiene/magazine.git
    cd magazine
    poetry install
    poetry shell

---

## CLI Usage

### Commands

    magazine page <page_path>
    magazine edition <edition_path>
    magazine finalize <edition_path>
    magazine manifest <edition_path>

### Flags

    --dry-run                   Preview actions without writing files
    --verbose                   Enable verbose output
    --ci                        Run in CI mode (strict, non-interactive)
    --skip-existing             Skip pages that already have artifacts (edition command)
    --force                     Continue even if required files are missing (finalize command)

    --ai-fountain-disable       Skip the Fountain AI stage
    --ai-fountain-force         Force Fountain AI regeneration
    --ai-fountain-model         Override the AI model for Fountain stage
    --ai-fountain-runtime       Override the AI runtime for Fountain stage

    --metadata-disable          Skip metadata generation
    --metadata-force            Force metadata regeneration

    --sizes-disable             Skip size variant generation (future)
    --sizes-force               Force size variant regeneration (future)

    --ai-video-disable          Skip the video AI stage (future)
    --ai-video-force            Force video AI regeneration (future)

### Examples

Build a single page:

    magazine page editions/edition_01/pages/02_presence

Build all pages in an edition:

    magazine edition editions/edition_01

Build all pages, skipping pages that already have artifacts:

    magazine edition editions/edition_01 --skip-existing

Bundle an edition into publishing artifacts:

    magazine finalize editions/edition_01

Force a full bundle rebuild:

    magazine finalize editions/edition_01 --force

Generate metadata for all pages:

    magazine manifest editions/edition_01

---

## Configuration

Magazine follows 12-factor configuration principles. All settings can be overridden via environment variables.

| Variable                    | Description                                 |
|-----------------------------|---------------------------------------------|
| `MAGAZINE_DEFAULT_EDITION`  | Default edition path used by CLI commands   |
| `MAGAZINE_FOUNTAIN_MODEL`   | AI model used by the Fountain stage         |
| `MAGAZINE_ENABLE_VIDEO`     | Enable the video AI stage (`true`/`false`)  |
| `MAGAZINE_ENABLE_SIZES`     | Enable size variant generation (`true`/`false`) |

Edition-level configuration can be placed in `manifest.json` at the edition root to override defaults per edition.

---

## Development

Run a single page build via Poetry:

    poetry run magazine page editions/edition_01/pages/02_presence

Build a full edition:

    poetry run magazine edition editions/edition_01

Finalize an edition bundle:

    poetry run magazine finalize editions/edition_01

Run in dry-run mode (preview only):

    poetry run magazine edition editions/edition_01 --dry-run

Run tests:

    poetry run pytest

---

## Developer Utilities

Internal tools for content production and quality assurance live in `scripts/`.
They are not part of the `magazine` package and are not invoked by the CLI.

| Script | Purpose |
|---|---|
| `scripts/lint_ip_references.py` | Scan edition schemas for forbidden external IP references |
| `scripts/visual_dna.py` | Audit page aesthetic consistency within an edition |
| `scripts/build_page_assets.sh` | Build distribution-ready assets from master artwork |
| `scripts/fix_fountain_html.sh` | Fix known HTML export issues from Fountain screenplays |
| `scripts/generate_cover_meta.sh` | Generate cover metadata files |

See [`scripts/README.md`](scripts/README.md) for full usage details.

---

## Editorial Constraints

`context/constraints.json` is the canonical editorial constraint manifest for the publication.
It defines the creative and ethical boundaries that every AI-generated asset, page schema, and prompt must respect:

- **Forbidden IP references** — external franchises and named properties that must never appear
- **Mandatory tone markers** — tonal qualities every page must embody
- **Style invariants** — visual aesthetic rules that apply across all editions
- **Conceptual guardrails** — content boundaries that protect readers and preserve the Ego Hygiene ethos

The file is not executed by the pipeline. It is consulted when authoring AI prompts, writing page schemas, or extending the IP lint check.

See [`docs/CONSTRAINTS.md`](docs/CONSTRAINTS.md) for full documentation.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes following the existing code style
4. Keep the modular design — new stages belong in `magazine/`
5. Add tests for new functionality
6. Open a pull request with a clear description

Please keep pipeline stages composable and independently testable.

---

## Roadmap

- [ ] Video AI stage — AI-driven animation per page
- [ ] Size variants stage — multi-format comic size export (modern, manga, trade paperback, digital)
- [ ] Metadata enhancer — richer structured metadata per page and edition
- [ ] Web API — HTTP interface for remote build triggering
- [ ] Cloud deployment — containerised production pipeline
- [ ] Plugin system — third-party stage extensions

---

## License

Proprietary. All rights reserved.
