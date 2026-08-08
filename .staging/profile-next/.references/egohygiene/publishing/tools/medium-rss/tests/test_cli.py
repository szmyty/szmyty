"""Tests for CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import feedparser
import pytest
import yaml
from click.testing import CliRunner

from medium_rss.cli import main

_FEED_URL = "https://articles.egohygiene.io/feed"


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    config = {
        "feeds": [
            {
                "id": "ego-hygiene-medium",
                "url": _FEED_URL,
                "output": str(tmp_path / "medium"),
            }
        ]
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config), encoding="utf-8")
    return tmp_path


def _load_fixture_entries(sample_rss_path: Path) -> list[dict]:
    parsed = feedparser.parse(sample_rss_path.read_bytes())
    entries = []
    for entry in parsed.entries:
        raw = dict(entry)
        content_list = raw.get("content", [])
        if content_list and isinstance(content_list, list):
            raw["content_html"] = content_list[0].get("value", "")
        else:
            raw["content_html"] = ""
        entries.append(raw)
    return entries


def test_validate_command(config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0
    assert "ego-hygiene-medium" in result.output


def test_validate_missing_config() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--config", "nonexistent.yaml"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "error" in result.output.lower()


def test_sync_dry_run_no_writes(config_dir: Path, sample_rss_path: Path) -> None:
    """Dry-run should print what would change but not write any files."""
    output_dir = config_dir / "medium"

    with patch("medium_rss.cli.fetch_feed") as mock_fetch:
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--dry-run"],
        )

    assert result.exit_code == 0
    # No manifest should be written in dry-run mode
    assert not (output_dir / "manifest.json").exists()


def test_sync_writes_manifest(config_dir: Path, sample_rss_path: Path) -> None:
    output_dir = config_dir / "medium"

    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    assert result.exit_code == 0
    assert (output_dir / "manifest.json").exists()


def test_sync_writes_article_files(config_dir: Path, sample_rss_path: Path) -> None:
    output_dir = config_dir / "medium"

    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)

        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    articles_dir = output_dir / "articles"
    article_dirs = [d for d in articles_dir.iterdir() if d.is_dir()]
    assert len(article_dirs) >= 2

    for article_dir in article_dirs:
        assert (article_dir / "metadata.json").exists()
        assert (article_dir / "article.html").exists()
        assert (article_dir / "article.md").exists()


def test_sync_idempotent(config_dir: Path, sample_rss_path: Path) -> None:
    """Running sync twice should produce the same manifest (no duplicate articles)."""
    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        entries = _load_fixture_entries(sample_rss_path)
        mock_fetch.return_value = entries

        runner = CliRunner()
        args = ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"]
        runner.invoke(main, args)
        first_count = len(
            json.loads((config_dir / "medium" / "manifest.json").read_text())["articles"]
        )
        mock_fetch.return_value = entries
        runner.invoke(main, args)

    output_dir = config_dir / "medium"
    manifest_path = output_dir / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    # Second run should not add new articles beyond what the first run produced
    assert len(data["articles"]) == first_count


def test_sync_summary_output(config_dir: Path, sample_rss_path: Path) -> None:
    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    assert "Sync summary" in result.output
    assert "New articles" in result.output


def test_sync_slug_human_readable(config_dir: Path, sample_rss_path: Path) -> None:
    """Article directories should use human-readable slugs, not raw IDs."""
    output_dir = config_dir / "medium"

    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)

        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    articles_dir = output_dir / "articles"
    slugs = [d.name for d in articles_dir.iterdir() if d.is_dir()]
    # Should have human-readable slugs like 'mood-colors-your-reality'
    assert any("mood" in s for s in slugs)


def test_inspect_command(config_dir: Path, sample_rss_path: Path) -> None:
    """Inspect command should display the manifest without errors."""
    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    runner = CliRunner()
    result = runner.invoke(main, ["inspect", "--config", str(config_dir / "config.yaml")])
    assert result.exit_code == 0


def test_sync_preserves_existing_articles_not_in_feed(
    config_dir: Path, sample_rss_path: Path
) -> None:
    """Articles in the manifest must NOT be deleted when absent from the current feed."""
    output_dir = config_dir / "medium"

    # First sync with full fixture
    with patch("medium_rss.cli.fetch_feed") as mock_fetch, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch.return_value = _load_fixture_entries(sample_rss_path)
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    initial_count = len(json.loads((output_dir / "manifest.json").read_text())["articles"])

    # Second sync with empty feed (simulating a limited feed window)
    with patch("medium_rss.cli.fetch_feed") as mock_fetch2, \
         patch("medium_rss.cli.download_asset", return_value=None):
        mock_fetch2.return_value = []
        runner = CliRunner()
        runner.invoke(
            main,
            ["sync", "--config", str(config_dir / "config.yaml"), "--no-download-images"],
        )

    after_count = len(json.loads((output_dir / "manifest.json").read_text())["articles"])
    assert after_count == initial_count
