"""Tests for the size generation stage (magazine.assets.sizes)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from magazine.assets.sizes import (
    _hash_file_list,
    _load_sizes_config,
    _magick_args,
    parse_sizes_list,
    _resolve_sizes,
    _should_regenerate_bundle_variant,
    _should_regenerate_variant,
    _size_config_hash,
    generate_bundle_size_variants,
    generate_size_variants,
)


class TestParseSizesList:
    def test_none_returns_none(self) -> None:
        assert parse_sizes_list(None) is None

    def test_empty_string_returns_none(self) -> None:
        assert parse_sizes_list("") is None

    def test_all_returns_none(self) -> None:
        assert parse_sizes_list("all") is None

    def test_all_case_insensitive(self) -> None:
        assert parse_sizes_list("ALL") is None
        assert parse_sizes_list("All") is None

    def test_single_size(self) -> None:
        assert parse_sizes_list("modern") == ["modern"]

    def test_multiple_sizes(self) -> None:
        assert parse_sizes_list("modern,manga") == ["modern", "manga"]

    def test_whitespace_stripped(self) -> None:
        assert parse_sizes_list(" modern , manga ") == ["modern", "manga"]

    def test_empty_entries_excluded(self) -> None:
        assert parse_sizes_list("modern,,manga") == ["modern", "manga"]


class TestResolveSizes:
    def test_none_returns_all(self) -> None:
        cfg = {"a": 1, "b": 2}
        assert _resolve_sizes(None, cfg) == cfg

    def test_filters_to_requested(self) -> None:
        cfg = {"a": 1, "b": 2, "c": 3}
        assert set(_resolve_sizes(["a", "c"], cfg).keys()) == {"a", "c"}

    def test_unknown_sizes_excluded(self) -> None:
        cfg = {"modern": 1}
        assert _resolve_sizes(["modern", "nonexistent"], cfg) == {"modern": 1}

    def test_empty_list_returns_all(self) -> None:
        cfg = {"modern": 1}
        assert _resolve_sizes([], cfg) == cfg


class TestSizeConfigHash:
    def test_deterministic(self) -> None:
        entry = {"width": 1988, "height": 3075, "dpi": 300, "scaling_strategy": "fit"}
        assert _size_config_hash(entry) == _size_config_hash(entry)

    def test_length_16(self) -> None:
        h = _size_config_hash({"width": 100, "height": 150})
        assert len(h) == 16

    def test_different_entry_different_hash(self) -> None:
        e1 = {"width": 100, "scaling_strategy": "fit"}
        e2 = {"width": 100, "scaling_strategy": "crop"}
        assert _size_config_hash(e1) != _size_config_hash(e2)


class TestMagickArgs:
    def test_fit_strategy(self) -> None:
        args = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=1000, height=1500, dpi=72, strategy="fit",
        )
        assert args[0] == "magick"
        assert "1000x1500" in args
        assert args[-1] == str(Path("/out/p.png"))
        assert "^" not in " ".join(args)

    def test_crop_strategy(self) -> None:
        args = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=1080, height=1080, dpi=72, strategy="crop",
        )
        assert "1080x1080^" in " ".join(args)
        assert "-gravity" in args
        assert "-extent" in args

    def test_pad_strategy(self) -> None:
        args = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=800, height=1200, dpi=72, strategy="pad",
        )
        assert "-background" in args
        assert "white" in args
        assert "-extent" in args

    def test_default_is_fit(self) -> None:
        args_fit = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=100, height=150, dpi=72, strategy="fit",
        )
        args_unknown = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=100, height=150, dpi=72, strategy="unknown",
        )
        assert args_fit == args_unknown

    def test_dpi_included(self) -> None:
        args = _magick_args(
            Path("/in/p.png"), Path("/out/p.png"),
            width=100, height=150, dpi=300, strategy="fit",
        )
        assert "300" in args


class TestShouldRegenerateVariant:
    def test_force_always_true(self, tmp_path: Path) -> None:
        (tmp_path / "out.png").write_bytes(b"x")
        assert _should_regenerate_variant(
            tmp_path / "out.png", tmp_path / "meta.json",
            img_hash="abc", size_hash="def", force=True,
        ) is True

    def test_missing_output_true(self, tmp_path: Path) -> None:
        assert _should_regenerate_variant(
            tmp_path / "missing.png", tmp_path / "meta.json",
            img_hash="abc", size_hash="def", force=False,
        ) is True

    def test_missing_meta_true(self, tmp_path: Path) -> None:
        (tmp_path / "out.png").write_bytes(b"x")
        assert _should_regenerate_variant(
            tmp_path / "out.png", tmp_path / "meta.json",
            img_hash="abc", size_hash="def", force=False,
        ) is True

    def test_matching_hashes_false(self, tmp_path: Path) -> None:
        out = tmp_path / "out.png"
        out.write_bytes(b"x")
        meta = tmp_path / ".size_meta.json"
        meta.write_text(json.dumps({"source_image_hash": "abc", "size_config_hash": "def"}))
        assert _should_regenerate_variant(
            out, meta, img_hash="abc", size_hash="def", force=False,
        ) is False

    def test_changed_image_hash_true(self, tmp_path: Path) -> None:
        out = tmp_path / "out.png"
        out.write_bytes(b"x")
        meta = tmp_path / ".size_meta.json"
        meta.write_text(json.dumps({"source_image_hash": "old", "size_config_hash": "def"}))
        assert _should_regenerate_variant(
            out, meta, img_hash="new", size_hash="def", force=False,
        ) is True

    def test_changed_size_config_hash_true(self, tmp_path: Path) -> None:
        out = tmp_path / "out.png"
        out.write_bytes(b"x")
        meta = tmp_path / ".size_meta.json"
        meta.write_text(json.dumps({"source_image_hash": "abc", "size_config_hash": "old"}))
        assert _should_regenerate_variant(
            out, meta, img_hash="abc", size_hash="new", force=False,
        ) is True

    def test_corrupt_meta_true(self, tmp_path: Path) -> None:
        out = tmp_path / "out.png"
        out.write_bytes(b"x")
        meta = tmp_path / ".size_meta.json"
        meta.write_text("NOT JSON {{{")
        assert _should_regenerate_variant(
            out, meta, img_hash="abc", size_hash="def", force=False,
        ) is True


class TestHashFileList:
    def test_deterministic(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.png"
        f2 = tmp_path / "b.png"
        f1.write_bytes(b"alpha")
        f2.write_bytes(b"beta")
        assert _hash_file_list([f1, f2]) == _hash_file_list([f1, f2])

    def test_order_sensitive(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.png"
        f2 = tmp_path / "b.png"
        f1.write_bytes(b"alpha")
        f2.write_bytes(b"beta")
        assert _hash_file_list([f1, f2]) != _hash_file_list([f2, f1])

    def test_content_sensitive(self, tmp_path: Path) -> None:
        f = tmp_path / "a.png"
        f.write_bytes(b"v1")
        h1 = _hash_file_list([f])
        f.write_bytes(b"v2")
        h2 = _hash_file_list([f])
        assert h1 != h2


class TestLoadSizesConfig:
    def test_loads_from_explicit_path(self, tmp_path: Path) -> None:
        cfg = {"s": {"width": 100, "height": 200}}
        p = tmp_path / "s.json"
        p.write_text(json.dumps(cfg))
        assert _load_sizes_config(p) == cfg

    def test_invalid_json_falls_through(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("NOT JSON")
        # Falls through to next candidate (repo default or empty)
        result = _load_sizes_config(p)
        assert isinstance(result, dict)

    def test_missing_path_falls_through(self, tmp_path: Path) -> None:
        result = _load_sizes_config(tmp_path / "nonexistent.json")
        assert isinstance(result, dict)

    def test_repo_default_loaded(self) -> None:
        result = _load_sizes_config()
        assert "modern" in result
        assert "manga" in result


class TestGenerateSizeVariants:
    def _cfg(self, tmp_path: Path) -> Path:
        p = tmp_path / "sizes.json"
        p.write_text(json.dumps({
            "sm": {"width": 50, "height": 75, "dpi": 72,
                   "bleed": 0, "safe_margin": 0,
                   "output_suffix": "sm", "scaling_strategy": "fit"},
        }))
        return p

    def test_skips_when_no_page_png(self, tmp_path: Path) -> None:
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
        assert not (artifacts / "sizes").exists()

    def test_creates_size_dir(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run"):
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
        assert (artifacts / "sizes" / "sm").is_dir()

    def test_writes_size_meta_json(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run"):
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
        meta = json.loads((artifacts / "sizes" / "sm" / ".size_meta.json").read_text())
        assert meta["size_name"] == "sm"
        assert "source_image_hash" in meta
        assert "size_config_hash" in meta

    def test_safe_mode_in_meta(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run"):
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path), safe_mode=True)
        meta = json.loads((artifacts / "sizes" / "sm" / ".size_meta.json").read_text())
        assert meta["size_mode"] == "safe_margin"

    def test_idempotent_second_run(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"stable")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run") as m_run:
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
            (artifacts / "sizes" / "sm" / "page.png").write_bytes(b"sized")
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
        assert m_run.call_count == 1

    def test_force_reruns(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"stable")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run") as m_run:
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
            (artifacts / "sizes" / "sm" / "page.png").write_bytes(b"sized")
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path), force=True)
        assert m_run.call_count == 2

    def test_skips_when_no_config(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes._load_sizes_config", return_value={}):
            generate_size_variants(tmp_path, artifacts)
        assert not (artifacts / "sizes").exists()

    def test_size_meta_excludes_timestamps(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.sizes.run"):
            generate_size_variants(tmp_path, artifacts, config_path=self._cfg(tmp_path))
        meta = json.loads((artifacts / "sizes" / "sm" / ".size_meta.json").read_text())
        timestamp_fields = {"size_generated_at", "generated_at", "created_at"}
        for field in timestamp_fields:
            assert field not in meta, (
                f"Timestamp field '{field}' must not appear in .size_meta.json"
            )

    def test_hash_invalidation_unaffected_by_injected_timestamp(self, tmp_path: Path) -> None:
        """Idempotency check ignores any timestamp fields that may exist in
        an older .size_meta.json file."""
        from magazine.hashing import hash_file
        img = tmp_path / "page.png"
        img.write_bytes(b"stable image")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        cfg = self._cfg(tmp_path)
        # Pre-populate .size_meta.json with matching hashes + a legacy timestamp
        import hashlib
        sizes_cfg = json.loads(cfg.read_text())
        size_entry = sizes_cfg["sm"]
        size_hash = hashlib.sha256(
            json.dumps(size_entry, sort_keys=True).encode()
        ).hexdigest()[:16]
        size_dir = artifacts / "sizes" / "sm"
        size_dir.mkdir(parents=True)
        (size_dir / "page.png").write_bytes(b"sized output")
        (size_dir / ".size_meta.json").write_text(
            json.dumps({
                "source_image_hash": hash_file(img),
                "size_config_hash": size_hash,
                "size_generated_at": "2024-01-01T00:00:00Z",  # legacy field
            })
        )
        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(tmp_path, artifacts, config_path=cfg)
        assert mock_run.call_count == 0, "No regeneration expected: hashes match"


class TestGenerateBundleSizeVariants:
    def _make_stage(self, edition_dir: Path, page_count: int = 2) -> Path:
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        stage_dir.mkdir(parents=True)
        for i in range(1, page_count + 1):
            (stage_dir / f"page_{i:02d}.png").write_bytes(b"fake page png")
        return stage_dir

    def _make_cfg(self, tmp_path: Path) -> Path:
        cfg = {
            "test_size": {
                "width": 100,
                "height": 150,
                "dpi": 72,
                "scaling_strategy": "fit",
            }
        }
        p = tmp_path / "sizes.json"
        p.write_text(json.dumps(cfg))
        return p

    def test_skips_when_no_staged_pngs(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "artifacts" / "final_build_stage").mkdir(parents=True)
        generate_bundle_size_variants(edition_dir, config_path=self._make_cfg(tmp_path))
        assert not (edition_dir / "publishing" / "sizes").exists()

    def test_creates_output_structure(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        self._make_stage(edition_dir)
        cfg_path = self._make_cfg(tmp_path)
        with patch("magazine.assets.sizes.run"):
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
        size_dir = edition_dir / "publishing" / "sizes" / "test_size"
        assert size_dir.is_dir()

    def test_writes_bundle_meta_json(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        self._make_stage(edition_dir)
        cfg_path = self._make_cfg(tmp_path)
        with patch("magazine.assets.sizes.run"):
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
        meta_path = edition_dir / "publishing" / "sizes" / "test_size" / ".bundle_size_meta.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert meta["size_name"] == "test_size"
        assert "source_bundle_hash" in meta
        assert "size_config_hash" in meta
        assert meta["page_count"] == 2

    def test_idempotent_skips_second_run(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        self._make_stage(edition_dir)
        cfg_path = self._make_cfg(tmp_path)
        with patch("magazine.assets.sizes.run") as mock_run:
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
            # Create fake PDF so idempotency check passes
            pdf = edition_dir / "publishing" / "sizes" / "test_size" / "edition_01_test_size.pdf"
            pdf.write_bytes(b"fake pdf")
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
        assert mock_run.call_count == 3  # 2 pages + 1 img2pdf in first run; second run skipped (still 3 total)

    def test_force_reruns(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        self._make_stage(edition_dir)
        cfg_path = self._make_cfg(tmp_path)
        with patch("magazine.assets.sizes.run") as mock_run:
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
            pdf = edition_dir / "publishing" / "sizes" / "test_size" / "edition_01_test_size.pdf"
            pdf.write_bytes(b"fake pdf")
            generate_bundle_size_variants(edition_dir, config_path=cfg_path, force=True)
        # (2 pages + 1 img2pdf) × 2 runs = 6 run() calls
        assert mock_run.call_count == 6

    def test_bundle_meta_excludes_timestamps(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        self._make_stage(edition_dir)
        cfg_path = self._make_cfg(tmp_path)
        with patch("magazine.assets.sizes.run"):
            generate_bundle_size_variants(edition_dir, config_path=cfg_path)
        meta_path = edition_dir / "publishing" / "sizes" / "test_size" / ".bundle_size_meta.json"
        meta = json.loads(meta_path.read_text())
        timestamp_fields = {"generated_at", "size_generated_at", "created_at"}
        for field in timestamp_fields:
            assert field not in meta, (
                f"Timestamp field '{field}' must not appear in .bundle_size_meta.json"
            )


class TestBundledSizesConfig:
    def test_all_presets_present(self) -> None:
        sizes_config = _load_sizes_config()
        expected = {
            "modern", "silver_age", "golden_age", "manga",
            "trade_paperback", "a4", "digital_vertical", "framing_hd",
        }
        assert expected.issubset(sizes_config.keys())

    def test_each_preset_has_required_fields(self) -> None:
        sizes_config = _load_sizes_config()
        required = {"width", "height", "dpi", "bleed", "safe_margin",
                    "output_suffix", "scaling_strategy"}
        for name, entry in sizes_config.items():
            missing = required - entry.keys()
            assert not missing, f"Preset '{name}' missing fields: {missing}"

    def test_scaling_strategies_are_valid(self) -> None:
        valid = {"fit", "crop", "pad"}
        sizes_config = _load_sizes_config()
        for name, entry in sizes_config.items():
            assert entry["scaling_strategy"] in valid, (
                f"Preset '{name}' has invalid scaling_strategy: {entry['scaling_strategy']}"
            )
