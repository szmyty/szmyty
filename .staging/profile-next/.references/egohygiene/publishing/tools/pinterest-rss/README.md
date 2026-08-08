# pinterest-rss

Incremental Pinterest RSS ingestion tool for the Ego Hygiene repository.

---

## Overview

`pinterest-rss` fetches configured Pinterest RSS feeds, normalizes entries, downloads associated images, and maintains an incremental manifest. Only newly discovered or changed content is processed on each run.

The tool is designed to be:

- **Idempotent** – repeated runs produce the same result
- **Incremental** – only new or changed items are downloaded
- **Reliable** – HTTP timeouts, retries, and partial-failure handling are built in
- **Stable identity** – item directories use `pin-<numeric-id>` derived from the Pinterest GUID

---

## Architecture

```
tools/pinterest-rss/
├── pyproject.toml
├── README.md
└── src/
    └── pinterest_rss/
        ├── __init__.py       – package version
        ├── cli.py            – Click CLI entry point
        ├── feed.py           – RSS fetch and raw parse
        ├── normalizer.py     – entry normalization, pin ID extraction, stable identity
        ├── downloader.py     – image download with retry and atomic write
        ├── manifest.py       – manifest load/save, change detection
        └── models.py         – data models (PinterestItem, Manifest, etc.)
```

### Configuration and output

```
publishing/channels/pinterest/
├── config.yaml                          – feed configuration
└── boards/
    └── ego-hygiene/
        ├── manifest.json                – incremental sync state
        └── items/
            └── pin-<numeric-id>/
                ├── metadata.json        – normalized item metadata
                ├── description.md       – item description as Markdown
                └── image.<ext>          – downloaded image
```

**Example item directories:**

```
publishing/
  channels/pinterest/
    boards/
      ego-hygiene/
        items/
          pin-1061301468459923611/
          pin-987654321012345678/
          pin-112233445566778899/
```

---

## Installation

Requires Python 3.11+ and [Poetry](https://python-poetry.org/).

```bash
cd tools/pinterest-rss
poetry install
```

---

## CLI Usage

### Sync all configured feeds

```bash
poetry run pinterest-rss sync \
  --config publishing/channels/pinterest/config.yaml
```

### Dry-run (report changes without writing)

```bash
poetry run pinterest-rss sync \
  --config publishing/channels/pinterest/config.yaml \
  --dry-run
```

### Skip image downloads

```bash
poetry run pinterest-rss sync \
  --config publishing/channels/pinterest/config.yaml \
  --no-download-images
```

### Validate configuration

```bash
poetry run pinterest-rss validate \
  --config publishing/channels/pinterest/config.yaml
```

### Inspect current manifest state

```bash
poetry run pinterest-rss inspect \
  --config publishing/channels/pinterest/config.yaml
```

### Migrate existing archive to pin-id layout

```bash
poetry run pinterest-rss migrate \
  --config publishing/channels/pinterest/config.yaml
```

Use `--dry-run` to preview the migration without writing:

```bash
poetry run pinterest-rss migrate \
  --config publishing/channels/pinterest/config.yaml \
  --dry-run
```

---

## Configuration

`publishing/channels/pinterest/config.yaml`:

```yaml
feeds:
  - id: ego-hygiene
    url: https://www.pinterest.com/egohygiene/ego-hygiene.rss
    output: publishing/channels/pinterest/boards/ego-hygiene
```

### Multiple feed URLs (username migration support)

When a Pinterest account is renamed, use `additional_urls` to combine the legacy feed with the current feed. Items are deduplicated by pin ID so no pin is archived twice:

```yaml
feeds:
  - id: ego-hygiene
    url: https://www.pinterest.com/egohygiene/ego-hygiene.rss
    additional_urls:
      - https://www.pinterest.com/playfunctionmusic/ego-hygiene.rss
    output: publishing/channels/pinterest/boards/ego-hygiene
```

Feed fetch failures for `additional_urls` are logged as warnings and do not abort the sync. Primary URL failures remain fatal.

### Environment-variable overrides

| Variable                      | Effect                                           |
|-------------------------------|--------------------------------------------------|
| `PINTEREST_RSS_URL`           | Override the feed URL for the first configured feed |
| `PINTEREST_OUTPUT_DIRECTORY`  | Override the output directory                   |
| `PINTEREST_DOWNLOAD_IMAGES`   | Set to `false` / `0` to skip image downloads    |

---

## Output Structure

Each synchronized item is stored under:

```
publishing/channels/pinterest/boards/<board-id>/items/<directory>/
```

Where `<directory>` is `pin-<numeric-id>` for Pinterest pins.

| File              | Contents                                                       |
|-------------------|----------------------------------------------------------------|
| `metadata.json`   | All normalized item fields as JSON (includes `directory`, `pin_id`, `guid`) |
| `description.md`  | Item description formatted as Markdown                         |
| `image.<ext>`     | Downloaded image (extension from content-type)                 |

---

## Archive Identity Strategy

### Stable pin IDs

The **Pinterest pin ID** (the numeric identifier embedded in the GUID URL) is the canonical stable identity for every archived pin.

```
RSS GUID: https://www.pinterest.com/pin/1061301468459923611/

↓ extract pin ID

1061301468459923611

↓ archive directory

pin-1061301468459923611/
```

Rules:

- Pin IDs are extracted from the RSS `<guid>` element first.
- If the GUID does not contain a pin ID, the canonical URL is used as fallback.
- Non-Pinterest items fall back to a title-derived slug (collision-handled).
- Pin IDs are globally unique – no collision handling is needed for Pinterest items.

### Stable ID priority

```
1. Pinterest pin ID from GUID URL          → "1061301468459923611"  (preferred)
2. Pinterest pin ID from canonical URL     → "1061301468459923611"  (fallback)
3. Slugified GUID / URL                    → "www-example-com-..."  (non-Pinterest)
4. Content hash prefix                     → "a3f7b2c1d4e9f0a2"    (last resort)
```

### Username migration

Pinterest pin IDs remain stable across account renames (e.g., `playfunctionmusic` → `egohygiene`). The numeric pin ID embedded in the GUID does not change when the username changes. As a result:

- `https://www.pinterest.com/pin/1061301468459923611/` always identifies the same pin.
- Adding the old feed URL to `additional_urls` enables historical backfill without duplicates.

---

## Manifest Semantics

`manifest.json` tracks the sync state for a board:

```json
{
  "feed_url": "https://www.pinterest.com/egohygiene/ego-hygiene.rss",
  "board_id": "ego-hygiene",
  "last_sync": "2024-01-15T08:00:00+00:00",
  "items": {
    "1061301468459923611": {
      "stable_id": "1061301468459923611",
      "directory": "pin-1061301468459923611",
      "pin_id": "1061301468459923611",
      "guid": "https://www.pinterest.com/pin/1061301468459923611/",
      "source_url": "https://www.pinterest.com/pin/1061301468459923611/",
      "content_hash": "sha256-hex…",
      "first_seen": "2024-01-10T08:00:00+00:00",
      "last_updated": "2024-01-15T08:00:00+00:00",
      "local_paths": {
        "image": "publishing/channels/pinterest/boards/ego-hygiene/items/pin-1061301468459923611/image.jpg"
      }
    }
  }
}
```

The manifest is the **source of truth**. Directory names are presentation only and can be changed by migration without losing any historical data.

Backward-compatible fields (`slug`) are preserved alongside new fields (`directory`) so that existing tooling continues to work.

---

## Migration

Run migration to upgrade an existing archive (any era) to `pin-<id>` directory names:

```bash
poetry run pinterest-rss migrate \
  --config publishing/channels/pinterest/config.yaml
```

The migration command handles all three archive states:

| State | Old directory | New directory |
|-------|--------------|---------------|
| Legacy stable-ID (era 1) | `www-pinterest-com-pin-123-` | `pin-123456789` |
| Title-slug (era 2)        | `morning-ritual-pin`        | `pin-123456789` |
| Already migrated (era 3)  | `pin-123456789`             | *(skipped)*     |

The pin ID is recovered from `metadata.json` using the `guid`, `canonical_url`, or `source_url` fields. Items without a recoverable pin ID fall back to title-slug naming.

Migration is **idempotent** – running it multiple times is safe. Items already in `pin-<id>` format are skipped. Use `--dry-run` to preview changes without modifying the filesystem.

---

## Synchronization Algorithm

1. Fetch primary feed URL and all `additional_urls`.
2. Deduplicate entries by GUID across all fetched URLs.
3. Normalize each entry: extract pin ID, compute content hash.
4. Load the existing manifest.
5. For each entry:
   - **Unchanged** (same content hash) → skip.
   - **New** → create `pin-<id>/` directory, write `metadata.json` + `description.md`, download image, add to manifest.
   - **Changed** (different content hash) → update existing directory, update manifest.
6. Save manifest atomically.

Pins that disappear from the RSS feed are **never deleted** from the local archive.

### RSS Limitations

Pinterest RSS feeds are typically limited to the most recent 50–100 pins. To archive historical pins that no longer appear in the current feed:

- Add the legacy board URL to `additional_urls` to capture pins from before account renames.
- Run an initial backfill with both URLs to maximize coverage.
- Once all pins are captured in the manifest, the archive is self-sufficient (pins do not need to remain in the RSS feed).

---

## Workflow Behavior

`.github/workflows/pinterest-rss-sync.yml` runs:

- **Manually** via `workflow_dispatch`
- **Daily** at 08:00 UTC
- **On push** to `main` when relevant paths change

A repository concurrency lock (`pinterest-rss-sync`) prevents parallel runs from corrupting the manifest.

The workflow commits only when content changes, using:

```
assets(pinterest): 🍱 sync Pinterest feed [skip ci]
```

The `[skip ci]` annotation prevents recursive workflow execution.

---

## Local Testing

Run the test suite from the `tools/pinterest-rss` directory:

```bash
cd tools/pinterest-rss
poetry install
poetry run pytest tests/ -v
```

Tests use fixture RSS data (no live network calls):

```
tests/
├── conftest.py
├── fixtures/
│   └── sample.rss
├── test_feed.py
├── test_normalizer.py
├── test_manifest.py
├── test_downloader.py
└── test_cli.py
```

---

## Failure Recovery

| Scenario                         | Behavior                                              |
|----------------------------------|-------------------------------------------------------|
| Primary feed unreachable         | Error reported; manifest unchanged; exit 1            |
| Additional URL unreachable       | Warning logged; primary sync continues normally       |
| Malformed feed entry             | Entry skipped with warning; others processed          |
| Image download failure           | Logged as failed; item metadata still written         |
| Corrupt manifest                 | Fresh manifest created; all items treated as new      |
| Repeated runs                    | Unchanged items are skipped; manifest not rewritten   |
| Migration on already-migrated    | Skipped; idempotent                                   |
| Username rename on Pinterest     | Pin IDs remain stable; use `additional_urls` for history |

---

## Future Enrichment Extension Points

The normalized `metadata.json` for each item preserves `original_metadata` from the raw feed entry. Future enrichment pipelines can:

1. Read items from `publishing/channels/pinterest/boards/*/items/`
2. Load `metadata.json` for source content and image paths
3. Append enrichment results to a separate field (e.g. `enrichment:` in a sidecar file)
4. Leave `metadata.json` and `manifest.json` unmodified to preserve the ingestion layer as source of truth

Planned future layers (out of scope for this tool):

- AI description enrichment
- Embedding generation
- Infographic pipeline
- Article generation
- Obsidian export
- Website generation
- Semantic indexing and search
