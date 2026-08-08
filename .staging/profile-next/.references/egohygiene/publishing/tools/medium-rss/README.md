# medium-rss

Incremental Medium RSS ingestion tool for the Ego Hygiene repository.

---

## Overview

`medium-rss` fetches configured Medium RSS feeds, normalizes article metadata, preserves the original HTML content, converts articles to Markdown, downloads associated images, and maintains an incremental manifest. Only newly discovered or changed articles are processed on each run.

The tool is designed to be:

- **Idempotent** – repeated runs produce the same result
- **Incremental** – only new or changed articles are processed
- **Reliable** – HTTP timeouts, retries, and partial-failure handling are built in
- **Human-readable** – article directories use title-derived slugs

---

## Architecture

```
tools/medium-rss/
├── pyproject.toml
├── README.md
└── src/
    └── medium_rss/
        ├── __init__.py        – package version
        ├── cli.py             – Click CLI entry point
        ├── feed.py            – RSS fetch and namespace-aware parse
        ├── normalizer.py      – entry normalization, stable post ID + slug generation
        ├── content_parser.py  – HTML cleanup, tracking pixel removal, image extraction
        ├── renderer.py        – HTML-to-Markdown conversion
        ├── downloader.py      – image download with retry and atomic write
        ├── manifest.py        – manifest load/save, change detection
        └── models.py          – data models (MediumArticle, Manifest, etc.)
```

### Configuration and output

```
publishing/
  channels/medium/
    config.yaml     – feed configuration
    manifest.json   – incremental sync manifest
    articles/
      mood-colors-your-reality/
        metadata.json
        article.html
        article.md
        assets/
          mood-hero-abc12345.png
```

---

## Feed Source

Medium custom-domain publications expose RSS feeds at the `/feed` path.

The feed includes:

- Article metadata (`title`, `link`, `guid`, `dc:creator`, `pubDate`, `atom:updated`, `category`)
- Full HTML article body via `content:encoded`

---

## Installation

```bash
cd tools/medium-rss
poetry install
```

---

## CLI Usage

### Synchronize

```bash
poetry run medium-rss sync \
  --config publishing/channels/medium/config.yaml
```

Dry-run (no files written):

```bash
poetry run medium-rss sync \
  --config publishing/channels/medium/config.yaml \
  --dry-run
```

Skip image downloads:

```bash
poetry run medium-rss sync \
  --config publishing/channels/medium/config.yaml \
  --no-download-images
```

Skip Markdown rendering:

```bash
poetry run medium-rss sync \
  --config publishing/channels/medium/config.yaml \
  --no-render-markdown
```

### Validate configuration

```bash
poetry run medium-rss validate \
  --config publishing/channels/medium/config.yaml
```

### Inspect manifest

```bash
poetry run medium-rss inspect \
  --config publishing/channels/medium/config.yaml
```

### Migrate slugs

```bash
poetry run medium-rss migrate-slugs \
  --config publishing/channels/medium/config.yaml
```

---

## Configuration

`publishing/channels/medium/config.yaml`:

```yaml
feeds:
  - id: ego-hygiene-medium
    url: https://articles.egohygiene.io/feed
    output: publishing/channels/medium
```

### Environment-variable overrides

| Variable                    | Effect                                           |
|-----------------------------|--------------------------------------------------|
| `MEDIUM_RSS_URL`            | Override the feed URL for the first configured feed |
| `MEDIUM_OUTPUT_DIRECTORY`   | Override the output directory                   |
| `MEDIUM_DOWNLOAD_IMAGES`    | Set to `false` / `0` to skip image downloads    |
| `MEDIUM_RENDER_MARKDOWN`    | Set to `false` / `0` to skip Markdown rendering |

---

## Article Identity

Medium articles have a stable 12-character hex post ID embedded in their GUID and URL.

Example GUID: `https://medium.com/p/f284b362c931` → post ID: `f284b362c931`

Fallback priority when no Medium post ID is extractable:

1. Medium GUID
2. Canonical article URL → deterministic SHA-256 hash prefix
3. Content hash

---

## Slug Generation

Human-readable article directory names are derived from the article title.

Example:

```
Mood Colors Your Reality → mood-colors-your-reality
```

Normalization steps:

- Normalize Unicode (NFKD) and transliterate to ASCII
- Strip HTML tags
- Lowercase
- Remove non-alphanumeric characters (except hyphens)
- Replace whitespace with hyphens
- Collapse repeated hyphens
- Strip leading/trailing hyphens
- Limit to 80 characters

Collision suffixes (`-2`, `-3`, …) are applied deterministically when multiple articles produce the same slug.

---

## Medium-Specific HTML Cleanup

The following elements are removed from article HTML before storage:

- Medium tracking pixels (URLs matching `medium.com/_/stat`)
- Invisible 1×1 images with no alt text
- Empty block elements with no visible content

Legitimate article images, figures, and captions are preserved.

---

## Incremental Synchronization

The manifest at `publishing/channels/medium/manifest.json` tracks:

- Feed URL
- Last successful synchronization time
- Per-article: stable ID, slug, canonical URL, published/updated timestamps, content hash, asset paths, sync status

On each run:

1. Fetch and parse the RSS feed
2. Normalize each entry
3. Compare content hashes against the manifest
4. Process only new or changed articles
5. Skip unchanged articles
6. Update the manifest

**Important**: Articles already in the manifest are never deleted when they disappear from the RSS feed. Medium feeds expose only a limited window of recent entries. Previously synchronized articles are always preserved.

---

## Feed Window Limitation

Medium RSS feeds commonly expose only the most recent articles rather than the complete historical archive. This tool treats the feed as an incremental discovery source. Older articles that no longer appear in the feed are preserved in the manifest and on disk.

A separate backfill strategy would be required to ingest the full historical archive.

---

## Workflow Behavior

The GitHub Actions workflow at `.github/workflows/medium-rss-sync.yml`:

- Runs on a daily schedule (08:30 UTC)
- Supports manual dispatch
- Reruns when the tool, configuration, or workflow changes
- Uses concurrency groups to prevent simultaneous runs
- Commits only when content changes (using `[skip ci]` to prevent recursive execution)

---

## Local Testing

```bash
cd tools/medium-rss
poetry install --no-interaction
poetry run pytest tests/ -v
```

---

## Failure Recovery

- One malformed article entry does not abort the entire sync
- Failed image downloads are logged and counted but do not fail the run
- The manifest is only written when at least one article changes
- Interrupted runs can be safely re-run (idempotent)
- The exit code is nonzero if any entries failed to process

---

## Future Enrichment Extension Points

- Full historical backfill via Medium export or web scraping
- Full-text search index generation
- Reading time estimation
- Cross-reference linking between articles
- Category/tag taxonomy normalization
