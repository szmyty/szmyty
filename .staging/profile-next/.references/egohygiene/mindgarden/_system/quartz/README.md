# Quartz — Digital Garden Publishing

This directory contains the configuration layer for publishing the Garden as a
static digital garden website using [Quartz v5](https://github.com/jackyzha0/quartz).

Quartz is the **rendering layer** for the Garden. It transforms the Obsidian
vault into a publicly navigable, interconnected website — while the vault
remains the canonical authoring environment.

## Architecture

```
garden/
├── .obsidian/       # Obsidian configuration (authoring)
├── publish/         # Notes flagged for public publication (content source)
├── quartz/
│   ├── quartz.config.yaml   # Quartz site configuration (this layer)
│   └── README.md            # This document
└── ...              # Rest of vault (authoring only)
```

The separation of concerns is explicit:

| Layer | Tool | Directory |
|-------|------|-----------|
| Authoring | Obsidian | `garden/` |
| Content selection | Manual (`publish:` frontmatter or `publish/` folder) | `garden/publish/` |
| Rendering / publishing | Quartz | `garden/quartz/` |

Quartz is **not** vendored into this repository. The Quartz engine is fetched at
build time (see [Deployment](#deployment)), keeping the repository lean while
pinning to a reproducible version.

## Configuration

`quartz.config.yaml` drives all Quartz behaviour: site metadata, theme,
plugins, layout, and ignore patterns.

Key customisations for this garden:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `pageTitle` | `The Garden` | Human-readable site name |
| `baseUrl` | `garden.egohygiene.io` | Intended public domain |
| `ignorePatterns` | See config | Excludes private vault folders |
| `obsidian-flavored-markdown` | enabled | Preserves Obsidian wiki-links |
| `explicit-publish` | disabled | All notes in `publish/` are published |

To change the base URL for a different deployment target, update the `baseUrl`
field in `quartz.config.yaml` before running the build.

## Local Development

### Prerequisites

- Node.js ≥ 22
- npm ≥ 10 (or your preferred package manager)
- Git

### Setup

```sh
# 1. Clone the Quartz engine into a local working directory.
git clone https://github.com/jackyzha0/quartz.git /tmp/quartz
cd /tmp/quartz

# 2. Check out the pinned commit used in CI.
#    The authoritative SHA lives in the QUARTZ_COMMIT variable in:
#    .github/workflows/garden.yml → env.QUARTZ_COMMIT
#    Always use the value from the workflow to stay in sync with CI.
QUARTZ_COMMIT=$(grep 'QUARTZ_COMMIT:' /path/to/sanctuary/.github/workflows/garden.yml | awk '{print $2}')
git checkout "$QUARTZ_COMMIT"

# 3. Copy the Garden's Quartz configuration over the default.
cp /path/to/sanctuary/garden/quartz/quartz.config.yaml quartz.config.yaml

# 4. Install dependencies and community plugins.
npm ci
npx quartz plugin install

# 5. Start the local development server, pointing at the publish/ directory.
npx quartz build --serve -d /path/to/sanctuary/garden/publish
```

The local site will be available at `http://localhost:8080`.

Changes to files under `garden/publish/` are hot-reloaded automatically.

### Building Only

To produce a static build without serving:

```sh
npx quartz build -d /path/to/sanctuary/garden/publish
```

Output is written to `/tmp/quartz/public/`.

## Deployment

Deployment is handled by the [`garden.yml`](../../.github/workflows/garden.yml)
GitHub Actions workflow. On every push to `main` that modifies content in
`garden/publish/**` or configuration in `garden/quartz/**`, the workflow:

1. Checks out the repository.
2. Clones Quartz at the pinned commit.
3. Copies `quartz.config.yaml` into the Quartz working directory.
4. Runs `npm ci` and `npx quartz plugin install`.
5. Builds the static site with `npx quartz build -d garden/publish`.
6. Uploads the build output as a GitHub Actions artifact.

### Deploying to GitHub Pages

The workflow can be extended to deploy to GitHub Pages. If the repository is
already using GitHub Pages for the `docs/` site (via `github-pages.yml`), the
two deployments must be coordinated — GitHub Pages only supports one active
deployment per repository.

Options:

| Approach | When to use |
|----------|-------------|
| Replace mkdocs with Quartz | When the garden becomes the primary published site |
| Deploy garden to a subdomain | Configure Cloudflare Pages / Netlify to serve the `garden` workflow artifact |
| Combine builds | Add a `garden-build` job to `github-pages.yml` and merge both output directories |

### Deploying to Cloudflare Pages or Netlify

Point your platform's build command at `garden/quartz/` and provide the
following settings:

| Setting | Value |
|---------|-------|
| Build command | See `garden.yml` for the full multi-step build |
| Output directory | `public` |
| Node.js version | 22 |
| Environment variable | `CONTENT_DIR=garden/publish` |

## Publishing Workflow

1. **Author notes** in Obsidian as usual. All notes live under `garden/`.
2. **Flag notes for publication** by placing them in `garden/publish/` or by
   adding `publish: true` to the frontmatter (when using the `explicit-publish`
   plugin).
3. **Commit and push** to `main`. The `garden.yml` workflow builds and
   publishes automatically.

For the full list of Quartz-supported frontmatter properties (title, tags,
aliases, description, date, draft), see the
[Quartz documentation](https://github.com/jackyzha0/quartz).

## Reuse

This integration is designed to be portable. To reuse it in another repository:

1. Copy `garden/quartz/quartz.config.yaml` and `garden/quartz/README.md`.
2. Copy `.github/workflows/garden.yml`.
3. Update `baseUrl`, `pageTitle`, and the `CONTENT_DIR` path to match the
   target repository's layout.
4. Update the Quartz commit pin to the desired version.

## Related

- [Garden README](../README.md)
- [Architecture Audit](../../docs/architecture/audit.md)
- [Quartz repository](https://github.com/jackyzha0/quartz)
