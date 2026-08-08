"""Tests for the CLI commands."""

from __future__ import annotations

from datetime import UTC
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from pinterest_rss.cli import main


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    config = {
        "feeds": [
            {
                "id": "ego-hygiene",
                "url": "https://www.pinterest.com/egohygiene/ego-hygiene.rss",
                "output": str(tmp_path / "boards" / "ego-hygiene"),
            }
        ]
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config), encoding="utf-8")
    return tmp_path


def test_validate_command(config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0
    assert "ego-hygiene" in result.output


def test_validate_missing_config() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--config", "nonexistent.yaml"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "error" in result.output.lower()


def test_sync_dry_run_no_writes(config_dir: Path, sample_rss_path: Path) -> None:
    """Dry-run should print what would change but not write any files."""
    output_dir = config_dir / "boards" / "ego-hygiene"

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch:
        import feedparser
        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--dry-run"],
        )

    assert result.exit_code == 0
    # No manifest should have been written in dry-run mode
    assert not (output_dir / "manifest.json").exists()


def test_sync_fetches_and_writes_manifest(config_dir: Path, sample_rss_path: Path) -> None:
    output_dir = config_dir / "boards" / "ego-hygiene"

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, \
         patch("pinterest_rss.cli.download_image", return_value=None):
        import feedparser
        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    assert result.exit_code == 0
    assert (output_dir / "manifest.json").exists()


def test_sync_idempotent(config_dir: Path, sample_rss_path: Path) -> None:
    """Running sync twice should produce the same manifest."""
    import json

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, \
         patch("pinterest_rss.cli.download_image", return_value=None):
        import feedparser
        entries = [dict(e) for e in feedparser.parse(sample_rss_path.read_bytes()).entries]
        mock_fetch.return_value = entries

        runner = CliRunner()
        args = ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"]
        runner.invoke(main, args)
        mock_fetch.return_value = entries
        runner.invoke(main, args)

    output_dir = config_dir / "boards" / "ego-hygiene"
    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    # Item count should equal number of unique valid entries
    assert len(manifest_data["items"]) >= 2


def test_sync_feed_fetch_failure_reports_error(config_dir: Path) -> None:
    import httpx

    with patch("pinterest_rss.cli.fetch_feed", side_effect=httpx.ConnectError("timeout")):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml")],
        )

    assert result.exit_code != 0


def test_inspect_command_empty_manifest(config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["inspect", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0
    assert "ego-hygiene" in result.output.lower() or "0" in result.output


def test_sync_resolves_repo_relative_paths_from_nested_working_directory(
    tmp_path: Path, sample_rss_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "pinterest-rss"
    config_dir = repo_root / "publishing" / "pinterest"
    output_dir = config_dir / "boards" / "ego-hygiene"

    (repo_root / ".git").mkdir(parents=True)
    tool_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)
    (config_dir / "config.yaml").write_text(
        yaml.dump(
            {
                "feeds": [
                    {
                        "id": "ego-hygiene",
                        "url": "https://www.pinterest.com/egohygiene/ego-hygiene.rss",
                        "output": "publishing/pinterest/boards/ego-hygiene",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tool_dir)

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, patch(
        "pinterest_rss.cli.download_image", return_value=None
    ):
        import feedparser

        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", "publishing/pinterest/config.yaml", "--no-download-images"],
        )

    assert result.exit_code == 0
    assert (output_dir / "manifest.json").exists()


# ---------------------------------------------------------------------------
# Slug-based directory tests
# ---------------------------------------------------------------------------


def test_sync_creates_pin_id_based_directories(config_dir: Path, sample_rss_path: Path) -> None:
    """After sync, item directories for Pinterest pins should use pin-<id> format."""
    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, \
         patch("pinterest_rss.cli.download_image", return_value=None):
        import feedparser
        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    assert result.exit_code == 0
    assert items_dir.exists()

    dir_names = [d.name for d in items_dir.iterdir() if d.is_dir()]
    assert len(dir_names) >= 2

    for name in dir_names:
        # Directory names must be lowercase and hyphen-separated.
        assert name == name.lower(), f"Expected lowercase directory name, got: {name}"
        assert "." not in name, f"Unexpected dot in directory name: {name}"
        # URL-derived stable IDs (old format) should not appear.
        assert "www-" not in name, f"Directory looks like a URL-derived stable ID: {name}"
        assert "pinterest-com" not in name, f"Directory looks like a URL-derived stable ID: {name}"

    # The two well-formed fixture entries must produce pin-<id> directories.
    # Fixture GUIDs: pin/123456789/ and pin/987654321/
    assert "pin-123456789" in dir_names
    assert "pin-987654321" in dir_names


def test_sync_manifest_records_directory(config_dir: Path, sample_rss_path: Path) -> None:
    """The manifest should record the directory for each item alongside the stable_id."""
    import json

    output_dir = config_dir / "boards" / "ego-hygiene"

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, \
         patch("pinterest_rss.cli.download_image", return_value=None):
        import feedparser
        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    for entry in manifest_data["items"].values():
        assert "directory" in entry, "manifest entry missing directory field"
        assert entry["directory"], "manifest entry has empty directory"


def test_sync_metadata_json_records_directory(config_dir: Path, sample_rss_path: Path) -> None:
    """metadata.json for each item should contain the directory field."""
    import json

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    with patch("pinterest_rss.cli.fetch_feed") as mock_fetch, \
         patch("pinterest_rss.cli.download_image", return_value=None):
        import feedparser
        parsed = feedparser.parse(sample_rss_path.read_bytes())
        mock_fetch.return_value = [dict(e) for e in parsed.entries]

        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    for item_dir in items_dir.iterdir():
        meta_path = item_dir / "metadata.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert "directory" in meta
        assert meta["directory"]


def test_sync_collision_handling(config_dir: Path) -> None:
    """Two non-Pinterest items with the same title should get distinct slugs."""

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    # Non-Pinterest entries (no pin ID in URL) with same title → collision on slug
    entries = [
        {
            "id": "https://example.com/article/001/",
            "link": "https://example.com/article/001/",
            "title": "Same Title",
            "summary": "First item",
            "media_content": [],
        },
        {
            "id": "https://example.com/article/002/",
            "link": "https://example.com/article/002/",
            "title": "Same Title",
            "summary": "Second item",
            "media_content": [],
        },
    ]

    with patch("pinterest_rss.cli.fetch_feed", return_value=entries), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    dir_names = sorted(d.name for d in items_dir.iterdir() if d.is_dir())
    assert "same-title" in dir_names
    assert "same-title-2" in dir_names


def test_sync_collision_handling_third_item(config_dir: Path) -> None:
    """Three non-Pinterest items with the same title should get -2, -3 style slugs."""
    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    entries = [
        {
            "id": f"https://example.com/article/00{i}/",
            "link": f"https://example.com/article/00{i}/",
            "title": "Duplicate",
            "summary": f"Item {i}",
            "media_content": [],
        }
        for i in range(1, 4)
    ]

    with patch("pinterest_rss.cli.fetch_feed", return_value=entries), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    dir_names = sorted(d.name for d in items_dir.iterdir() if d.is_dir())
    assert "duplicate" in dir_names
    assert "duplicate-2" in dir_names
    assert "duplicate-3" in dir_names


def test_sync_pinterest_pins_use_unique_pin_id_directories(config_dir: Path) -> None:
    """Pinterest items always get pin-<id> directories – no collision handling needed."""
    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    entries = [
        {
            "id": "https://www.pinterest.com/pin/111111111111111/",
            "link": "https://www.pinterest.com/pin/111111111111111/",
            "title": "Same Title",
            "summary": "First item",
            "media_content": [],
        },
        {
            "id": "https://www.pinterest.com/pin/222222222222222/",
            "link": "https://www.pinterest.com/pin/222222222222222/",
            "title": "Same Title",
            "summary": "Second item",
            "media_content": [],
        },
    ]

    with patch("pinterest_rss.cli.fetch_feed", return_value=entries), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    dir_names = sorted(d.name for d in items_dir.iterdir() if d.is_dir())
    assert "pin-111111111111111" in dir_names
    assert "pin-222222222222222" in dir_names


# ---------------------------------------------------------------------------
# Migrate command tests
# ---------------------------------------------------------------------------


def test_migrate_command_no_items(config_dir: Path) -> None:
    """migrate with an empty manifest should succeed with nothing to do."""
    runner = CliRunner()
    result = runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0
    assert "nothing to migrate" in result.output.lower() or "no items" in result.output.lower()


def test_migrate_command_renames_old_style_directories(config_dir: Path) -> None:
    """migrate should rename legacy stable-ID directories to pin-<id> format."""
    import json
    from datetime import datetime

    from pinterest_rss.manifest import save_manifest
    from pinterest_rss.models import Manifest, ManifestEntry

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    # Simulate old-style layout: directory named after stable_id (URL slug), no directory field.
    stable_id = "www-pinterest-com-pin-123456789-"
    old_dir = items_dir / stable_id
    old_dir.mkdir(parents=True)

    # Write metadata.json with the item details including the source URL.
    now = datetime.now(UTC)
    meta = {
        "stable_id": stable_id,
        "slug": "",
        "title": "Morning Ritual Pin",
        "description": "A morning ritual.",
        "board_id": "ego-hygiene",
        "source_url": "https://www.pinterest.com/pin/123456789/",
        "canonical_url": "https://www.pinterest.com/pin/123456789/",
        "image_url": None,
        "pub_date": None,
        "first_seen": now.isoformat(),
        "last_updated": now.isoformat(),
        "content_hash": "abc123",
        "original_metadata": {},
        "local_paths": {
            "image": (
                f"publishing/pinterest/boards/ego-hygiene/items/{stable_id}/image.jpg"
            )
        },
    }
    (old_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    # Write manifest without directory field.
    image_path = (
        f"publishing/pinterest/boards/ego-hygiene/items/{stable_id}/image.jpg"
    )
    manifest = Manifest(
        feed_url="https://www.pinterest.com/egohygiene/ego-hygiene.rss",
        board_id="ego-hygiene",
        items={
            stable_id: ManifestEntry(
                stable_id=stable_id,
                slug="",
                source_url="https://www.pinterest.com/pin/123456789/",
                content_hash="abc123",
                first_seen=now,
                last_updated=now,
                local_paths={"image": image_path},
            )
        },
    )
    save_manifest(manifest, output_dir)

    runner = CliRunner()
    result = runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0

    # Directory should have been renamed to pin-<id> format.
    assert not old_dir.exists(), "Old stable-ID directory should have been removed"
    new_dir = items_dir / "pin-123456789"
    assert new_dir.exists(), "New pin-<id> directory should exist"

    # Manifest should be updated with the directory field.
    updated = json.loads((output_dir / "manifest.json").read_text())
    entry = updated["items"][stable_id]
    assert entry["directory"] == "pin-123456789"

    # local_paths should reference the new directory.
    assert "pin-123456789" in entry["local_paths"]["image"]


def test_migrate_command_dry_run_no_writes(config_dir: Path) -> None:
    """migrate --dry-run should report what would change without touching the filesystem."""
    import json
    from datetime import datetime

    from pinterest_rss.manifest import save_manifest
    from pinterest_rss.models import Manifest, ManifestEntry

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    stable_id = "www-pinterest-com-pin-999-"
    old_dir = items_dir / stable_id
    old_dir.mkdir(parents=True)

    now = datetime.now(UTC)
    meta = {
        "stable_id": stable_id,
        "slug": "",
        "title": "Evening Reflection",
        "description": "Evening ritual.",
        "board_id": "ego-hygiene",
        "source_url": "",
        "canonical_url": "",
        "image_url": None,
        "pub_date": None,
        "first_seen": now.isoformat(),
        "last_updated": now.isoformat(),
        "content_hash": "def456",
        "original_metadata": {},
        "local_paths": {},
    }
    (old_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    manifest = Manifest(
        feed_url="https://www.pinterest.com/egohygiene/ego-hygiene.rss",
        board_id="ego-hygiene",
        items={
            stable_id: ManifestEntry(
                stable_id=stable_id,
                slug="",
                source_url="",
                content_hash="def456",
                first_seen=now,
                last_updated=now,
            )
        },
    )
    save_manifest(manifest, output_dir)

    runner = CliRunner()
    result = runner.invoke(
        main, ["migrate", "--dry-run", "--config", str(config_dir / "config.yaml")]
    )
    assert result.exit_code == 0

    # In dry-run, the old directory must remain and manifest must be unchanged.
    assert old_dir.exists(), "Dry-run should not rename the directory"
    manifest_after = json.loads((output_dir / "manifest.json").read_text())
    assert manifest_after["items"][stable_id]["directory"] == ""


def test_migrate_command_idempotent(config_dir: Path) -> None:
    """Running migrate twice should produce the same result."""
    import json
    from datetime import datetime

    from pinterest_rss.manifest import save_manifest
    from pinterest_rss.models import Manifest, ManifestEntry

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    stable_id = "www-pinterest-com-pin-777-"
    old_dir = items_dir / stable_id
    old_dir.mkdir(parents=True)

    now = datetime.now(UTC)
    meta = {
        "stable_id": stable_id, "slug": "", "title": "Mindfulness Now",
        "description": "desc", "board_id": "ego-hygiene",
        "source_url": "https://www.pinterest.com/pin/777/",
        "canonical_url": "https://www.pinterest.com/pin/777/",
        "image_url": None, "pub_date": None,
        "first_seen": now.isoformat(), "last_updated": now.isoformat(),
        "content_hash": "ghi789", "original_metadata": {}, "local_paths": {},
    }
    (old_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    manifest = Manifest(
        feed_url="https://www.pinterest.com/egohygiene/ego-hygiene.rss",
        board_id="ego-hygiene",
        items={
            stable_id: ManifestEntry(
                stable_id=stable_id, slug="", source_url="",
                content_hash="ghi789", first_seen=now, last_updated=now,
            )
        },
    )
    save_manifest(manifest, output_dir)

    runner = CliRunner()
    runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    result2 = runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    assert result2.exit_code == 0

    # After two runs, pin-<id> directory should still exist and manifest should be consistent.
    new_dir = items_dir / "pin-777"
    assert new_dir.exists()
    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    assert manifest_data["items"][stable_id]["directory"] == "pin-777"


def test_migrate_handles_collision_between_old_items(config_dir: Path) -> None:
    """Two old items that would produce the same slug should get distinct slugs."""
    import json
    from datetime import datetime

    from pinterest_rss.manifest import save_manifest
    from pinterest_rss.models import Manifest, ManifestEntry

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    now = datetime.now(UTC)
    items_to_create = [
        ("www-pinterest-com-pin-aaa-", "Same Title", "aaa-hash"),
        ("www-pinterest-com-pin-bbb-", "Same Title", "bbb-hash"),
    ]

    manifest_items: dict = {}
    for stable_id, title, content_hash in items_to_create:
        old_dir = items_dir / stable_id
        old_dir.mkdir(parents=True)
        meta = {
            "stable_id": stable_id, "slug": "", "title": title, "description": "desc",
            "board_id": "ego-hygiene", "source_url": "", "canonical_url": "",
            "image_url": None, "pub_date": None, "first_seen": now.isoformat(),
            "last_updated": now.isoformat(), "content_hash": content_hash,
            "original_metadata": {}, "local_paths": {},
        }
        (old_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")
        manifest_items[stable_id] = ManifestEntry(
            stable_id=stable_id, slug="", source_url="",
            content_hash=content_hash, first_seen=now, last_updated=now,
        )

    save_manifest(Manifest(
        feed_url="https://www.pinterest.com/egohygiene/ego-hygiene.rss",
        board_id="ego-hygiene",
        items=manifest_items,
    ), output_dir)

    runner = CliRunner()
    result = runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0

    dir_names = sorted(d.name for d in items_dir.iterdir() if d.is_dir())
    assert "same-title" in dir_names
    assert "same-title-2" in dir_names


# ---------------------------------------------------------------------------
# Multi-URL feed tests (additional_urls support)
# ---------------------------------------------------------------------------


def test_sync_deduplicates_entries_from_additional_urls(config_dir: Path) -> None:
    """Items appearing in both the primary URL and additional_urls should not be duplicated."""
    import json

    # Add additional_urls to the config
    config = {
        "feeds": [
            {
                "id": "ego-hygiene",
                "url": "https://www.pinterest.com/egohygiene/ego-hygiene.rss",
                "additional_urls": [
                    "https://www.pinterest.com/playfunctionmusic/ego-hygiene.rss"
                ],
                "output": str(config_dir / "boards" / "ego-hygiene"),
            }
        ]
    }
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump(config), encoding="utf-8")

    output_dir = config_dir / "boards" / "ego-hygiene"

    # Primary URL returns two pins; secondary URL returns the same pins (dedup scenario)
    primary_entries = [
        {
            "id": "https://www.pinterest.com/pin/111111111111111/",
            "link": "https://www.pinterest.com/pin/111111111111111/",
            "title": "Pin One",
            "summary": "First pin",
            "media_content": [],
        },
    ]
    secondary_entries = [
        {
            "id": "https://www.pinterest.com/pin/111111111111111/",
            "link": "https://www.pinterest.com/pin/111111111111111/",
            "title": "Pin One",
            "summary": "First pin",
            "media_content": [],
        },
        {
            "id": "https://www.pinterest.com/pin/222222222222222/",
            "link": "https://www.pinterest.com/pin/222222222222222/",
            "title": "Pin Two (legacy)",
            "summary": "Only in legacy feed",
            "media_content": [],
        },
    ]

    call_count = [0]

    def mock_fetch(url: str) -> list:
        call_count[0] += 1
        if "playfunctionmusic" in url:
            return secondary_entries
        return primary_entries

    with patch("pinterest_rss.cli.fetch_feed", side_effect=mock_fetch), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    assert result.exit_code == 0
    manifest_data = json.loads((output_dir / "manifest.json").read_text())

    # Should have exactly 2 unique pins (deduplicated)
    assert len(manifest_data["items"]) == 2
    assert "111111111111111" in manifest_data["items"]
    assert "222222222222222" in manifest_data["items"]

    # Both feeds should have been fetched
    assert call_count[0] == 2


def test_sync_additional_url_fetch_failure_does_not_abort_primary(config_dir: Path) -> None:
    """A failure on an additional_url should not abort the primary feed sync."""
    import json

    import httpx

    config = {
        "feeds": [
            {
                "id": "ego-hygiene",
                "url": "https://www.pinterest.com/egohygiene/ego-hygiene.rss",
                "additional_urls": [
                    "https://www.pinterest.com/legacy/ego-hygiene.rss"
                ],
                "output": str(config_dir / "boards" / "ego-hygiene"),
            }
        ]
    }
    (config_dir / "config.yaml").write_text(yaml.dump(config), encoding="utf-8")

    output_dir = config_dir / "boards" / "ego-hygiene"
    primary_entries = [
        {
            "id": "https://www.pinterest.com/pin/333333333333333/",
            "link": "https://www.pinterest.com/pin/333333333333333/",
            "title": "Primary Only Pin",
            "summary": "Only in primary feed",
            "media_content": [],
        },
    ]

    def mock_fetch(url: str) -> list:
        if "legacy" in url:
            raise httpx.ConnectError("Network unreachable")
        return primary_entries

    with patch("pinterest_rss.cli.fetch_feed", side_effect=mock_fetch), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    # Primary sync should have succeeded even though the additional URL failed
    assert result.exit_code == 0
    assert (output_dir / "manifest.json").exists()
    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    assert "333333333333333" in manifest_data["items"]


# ---------------------------------------------------------------------------
# Username migration handling tests
# ---------------------------------------------------------------------------


def test_sync_guid_unchanged_after_username_migration(config_dir: Path) -> None:
    """Pin stable IDs (numeric pin IDs) remain stable across username changes.

    When a Pinterest account is renamed (e.g., playfunctionmusic → egohygiene),
    the GUID URL in the RSS feed may change in the 'link' field, but the pin ID
    embedded in the GUID remains the canonical stable identity.
    """
    import json

    output_dir = config_dir / "boards" / "ego-hygiene"

    # First sync: pin appears under old username URL
    old_entry = {
        "id": "https://www.pinterest.com/pin/999888777666555/",
        "link": "https://www.pinterest.com/playfunctionmusic/ego-hygiene/999888777666555/",
        "title": "Mindful Moment",
        "summary": "A mindful moment pin",
        "media_content": [],
    }

    with patch("pinterest_rss.cli.fetch_feed", return_value=[old_entry]), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    manifest_after_first = json.loads((output_dir / "manifest.json").read_text())
    # Pin ID extracted from GUID is the stable identifier
    assert "999888777666555" in manifest_after_first["items"]

    # Second sync: same pin appears with new username (after account rename)
    new_entry = {
        "id": "https://www.pinterest.com/pin/999888777666555/",
        "link": "https://www.pinterest.com/egohygiene/ego-hygiene/999888777666555/",
        "title": "Mindful Moment",
        "summary": "A mindful moment pin",
        "media_content": [],
    }

    with patch("pinterest_rss.cli.fetch_feed", return_value=[new_entry]), \
         patch("pinterest_rss.cli.download_image", return_value=None):
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    manifest_after_second = json.loads((output_dir / "manifest.json").read_text())
    # Still the same stable ID – no duplicate
    assert len(manifest_after_second["items"]) == 1
    assert "999888777666555" in manifest_after_second["items"]


def test_migrate_slug_dir_to_pin_id_directory(config_dir: Path) -> None:
    """migrate should upgrade items already in slug-based dirs to pin-<id> dirs."""
    import json
    from datetime import datetime

    from pinterest_rss.manifest import save_manifest
    from pinterest_rss.models import Manifest, ManifestEntry

    output_dir = config_dir / "boards" / "ego-hygiene"
    items_dir = output_dir / "items"

    now = datetime.now(UTC)
    # Simulate an item that was previously migrated to a slug-based directory
    # (from a previous 'migrate' run under the old strategy)
    stable_id = "www-pinterest-com-pin-101010101010101-"
    slug_dir = items_dir / "context-is-everything"
    slug_dir.mkdir(parents=True)

    _slug_image_path = (
        "publishing/pinterest/boards/ego-hygiene/items/context-is-everything/image.jpg"
    )
    meta = {
        "stable_id": stable_id,
        "slug": "context-is-everything",
        "title": "Context Is Everything",
        "description": "A context pin.",
        "board_id": "ego-hygiene",
        "source_url": "https://www.pinterest.com/pin/101010101010101/",
        "canonical_url": "https://www.pinterest.com/pin/101010101010101/",
        "guid": "https://www.pinterest.com/pin/101010101010101/",
        "image_url": None,
        "pub_date": None,
        "first_seen": now.isoformat(),
        "last_updated": now.isoformat(),
        "content_hash": "ctx123",
        "original_metadata": {},
        "local_paths": {"image": _slug_image_path},
    }
    (slug_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    manifest = Manifest(
        feed_url="https://www.pinterest.com/egohygiene/ego-hygiene.rss",
        board_id="ego-hygiene",
        items={
            stable_id: ManifestEntry(
                stable_id=stable_id,
                slug="context-is-everything",
                directory="",  # not yet migrated to pin-<id>
                source_url="https://www.pinterest.com/pin/101010101010101/",
                content_hash="ctx123",
                first_seen=now,
                last_updated=now,
                local_paths={"image": _slug_image_path},
            )
        },
    )
    save_manifest(manifest, output_dir)

    runner = CliRunner()
    result = runner.invoke(main, ["migrate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0

    # Directory should be upgraded to pin-<id> format
    assert not slug_dir.exists(), "Old slug directory should be renamed"
    new_dir = items_dir / "pin-101010101010101"
    assert new_dir.exists(), "New pin-<id> directory should exist"

    updated = json.loads((output_dir / "manifest.json").read_text())
    entry = updated["items"][stable_id]
    assert entry["directory"] == "pin-101010101010101"
    assert "pin-101010101010101" in entry["local_paths"]["image"]
