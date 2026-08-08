"""Tests for scripts/visual_dna.py – visual pattern extraction and DNA synthesis."""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

# Make the scripts/ directory importable without modifying production code.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from visual_dna import (  # noqa: E402
    harvest_visual_patterns,
    synthesize_edition_visual_dna,
    verify_page_adherence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_page_schema(
    textures: list[str],
    color_palette: dict[str, list[str]],
    iconography: list[str],
    aesthetic: list[str] | None = None,
) -> dict:
    """Return a minimal page schema dict with a visual_style block."""
    vs: dict = {
        "texture": textures,
        "color_palette": color_palette,
        "iconography": iconography,
    }
    if aesthetic is not None:
        vs["aesthetic"] = aesthetic
    return {"visual_style": vs}


def _write_page_schema(page_dir: Path, name: str, schema: dict) -> None:
    """Write *schema* to ``<page_dir>/<name>.page.json``."""
    (page_dir / f"{name}.page.json").write_text(json.dumps(schema))


def _make_edition(
    tmp_path: Path,
    pages: dict[str, dict],
) -> Path:
    """
    Create a minimal edition directory structure and return its path.

    *pages* maps page-slug → schema dict.
    """
    edition = tmp_path / "test_edition"
    edition.mkdir()
    pages_dir = edition / "pages"
    pages_dir.mkdir()
    for slug, schema in pages.items():
        page_dir = pages_dir / slug
        page_dir.mkdir()
        _write_page_schema(page_dir, slug, schema)
    return edition


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SCHEMA_A = _make_page_schema(
    textures=["aged_paper", "worn_ink", "grain"],
    color_palette={
        "primary": ["warm_gold", "burnt_amber"],
        "secondary": ["deep_brown"],
    },
    iconography=["crystal_cluster", "skull_emblem"],
    aesthetic=["retro", "mystic"],
)

SCHEMA_B = _make_page_schema(
    textures=["aged_paper", "edge_burn", "print_noise"],
    color_palette={
        "primary": ["warm_gold", "rust_red"],
        "accent": ["prismatic_crystal"],
    },
    iconography=["crystal_cluster", "retro_price_tag"],
    aesthetic=["retro"],
)


# ===========================================================================
# TestHarvestVisualPatterns
# ===========================================================================


class TestHarvestVisualPatterns:
    """Tests for harvest_visual_patterns()."""

    def test_returns_required_vocabulary_keys(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert "texture_vocabulary" in result
        assert "color_vocabulary" in result
        assert "icon_vocabulary" in result
        assert "aesthetic_vocabulary" in result

    def test_texture_vocabulary_is_counter(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert isinstance(result["texture_vocabulary"], Counter)

    def test_color_vocabulary_is_counter(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert isinstance(result["color_vocabulary"], Counter)

    def test_icon_vocabulary_is_counter(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert isinstance(result["icon_vocabulary"], Counter)

    def test_aesthetic_vocabulary_is_counter(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert isinstance(result["aesthetic_vocabulary"], Counter)

    def test_collects_textures_from_single_page(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert "aged_paper" in result["texture_vocabulary"]
        assert "worn_ink" in result["texture_vocabulary"]
        assert "grain" in result["texture_vocabulary"]

    def test_collects_colors_from_all_palette_categories(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        for color in ("warm_gold", "burnt_amber", "deep_brown"):
            assert color in result["color_vocabulary"], f"Expected color '{color}' in vocabulary"

    def test_collects_iconography(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert "crystal_cluster" in result["icon_vocabulary"]
        assert "skull_emblem" in result["icon_vocabulary"]

    def test_collects_aesthetics_when_present(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        result = harvest_visual_patterns(edition)
        assert "retro" in result["aesthetic_vocabulary"]
        assert "mystic" in result["aesthetic_vocabulary"]

    def test_aggregates_textures_across_multiple_pages(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A, "02_page": SCHEMA_B})
        result = harvest_visual_patterns(edition)
        # aged_paper appears in both schemas → count 2
        assert result["texture_vocabulary"]["aged_paper"] == 2

    def test_aggregates_colors_across_multiple_pages(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A, "02_page": SCHEMA_B})
        result = harvest_visual_patterns(edition)
        # warm_gold appears in both
        assert result["color_vocabulary"]["warm_gold"] == 2

    def test_counts_shared_icons_correctly(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A, "02_page": SCHEMA_B})
        result = harvest_visual_patterns(edition)
        # crystal_cluster appears in both schemas
        assert result["icon_vocabulary"]["crystal_cluster"] == 2

    def test_aesthetic_count_per_page(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A, "02_page": SCHEMA_B})
        result = harvest_visual_patterns(edition)
        # 'retro' appears in both schemas
        assert result["aesthetic_vocabulary"]["retro"] == 2
        # 'mystic' only in SCHEMA_A
        assert result["aesthetic_vocabulary"]["mystic"] == 1

    def test_skips_non_directory_entries_in_pages(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        # Place a stray file directly inside pages/
        (edition / "pages" / "README.md").write_text("not a page")
        result = harvest_visual_patterns(edition)
        assert "aged_paper" in result["texture_vocabulary"]

    def test_skips_page_dirs_without_page_json_file(self, tmp_path: Path) -> None:
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A})
        # Add a page directory with no .page.json
        (edition / "pages" / "02_empty").mkdir()
        # Should not raise; known page still processed
        result = harvest_visual_patterns(edition)
        assert "aged_paper" in result["texture_vocabulary"]

    def test_empty_pages_dir_returns_empty_counters(self, tmp_path: Path) -> None:
        edition = tmp_path / "empty_edition"
        edition.mkdir()
        (edition / "pages").mkdir()
        result = harvest_visual_patterns(edition)
        assert len(result["texture_vocabulary"]) == 0
        assert len(result["color_vocabulary"]) == 0
        assert len(result["icon_vocabulary"]) == 0
        assert len(result["aesthetic_vocabulary"]) == 0

    def test_page_without_aesthetic_key_is_handled(self, tmp_path: Path) -> None:
        schema = _make_page_schema(
            textures=["grain"],
            color_palette={"primary": ["black"]},
            iconography=["star"],
            aesthetic=None,  # no aesthetic field
        )
        edition = _make_edition(tmp_path, {"01_page": schema})
        result = harvest_visual_patterns(edition)
        assert len(result["aesthetic_vocabulary"]) == 0

    def test_page_with_empty_texture_list(self, tmp_path: Path) -> None:
        schema = _make_page_schema(
            textures=[],
            color_palette={"primary": ["blue"]},
            iconography=["circle"],
        )
        edition = _make_edition(tmp_path, {"01_page": schema})
        result = harvest_visual_patterns(edition)
        assert len(result["texture_vocabulary"]) == 0

    def test_page_with_empty_color_palette(self, tmp_path: Path) -> None:
        schema = _make_page_schema(
            textures=["grain"],
            color_palette={},
            iconography=["star"],
        )
        edition = _make_edition(tmp_path, {"01_page": schema})
        result = harvest_visual_patterns(edition)
        assert len(result["color_vocabulary"]) == 0


# ===========================================================================
# TestSynthesizeEditionVisualDna
# ===========================================================================


class TestSynthesizeEditionVisualDna:
    """Tests for synthesize_edition_visual_dna()."""

    def _sample_patterns(self) -> dict:
        return {
            "texture_vocabulary": Counter(
                {"aged_paper": 5, "worn_ink": 4, "grain": 3, "edge_burn": 2, "print_noise": 2, "scuffed": 1}
            ),
            "color_vocabulary": Counter(
                {
                    "warm_gold": 6,
                    "burnt_amber": 5,
                    "deep_brown": 4,
                    "rust_red": 3,
                    "muted_teal": 2,
                    "earth_brown": 2,
                    "crystal_glow": 1,
                    "shadow_black": 1,
                    "pale_ivory": 1,
                }
            ),
            "icon_vocabulary": Counter(
                {
                    "crystal_cluster": 5,
                    "skull_emblem": 4,
                    "retro_price_tag": 3,
                    "meditating_silhouette": 3,
                    "infinity_symbol": 2,
                    "concentric_rings": 2,
                    "star": 1,
                }
            ),
            "aesthetic_vocabulary": Counter(
                {"retro": 6, "mystic": 5, "distressed": 4, "pulp": 3, "sci_fi": 1}
            ),
        }

    def test_returns_required_dna_keys(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert "canonical_textures" in dna
        assert "canonical_colors" in dna
        assert "canonical_iconography" in dna
        assert "canonical_aesthetics" in dna

    def test_canonical_textures_is_list(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert isinstance(dna["canonical_textures"], list)

    def test_canonical_colors_is_list(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert isinstance(dna["canonical_colors"], list)

    def test_canonical_iconography_is_list(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert isinstance(dna["canonical_iconography"], list)

    def test_canonical_aesthetics_is_list(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert isinstance(dna["canonical_aesthetics"], list)

    def test_textures_capped_at_five(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert len(dna["canonical_textures"]) <= 5

    def test_colors_capped_at_eight(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert len(dna["canonical_colors"]) <= 8

    def test_iconography_capped_at_six(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert len(dna["canonical_iconography"]) <= 6

    def test_aesthetics_capped_at_four(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert len(dna["canonical_aesthetics"]) <= 4

    def test_most_common_texture_is_included(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert "aged_paper" in dna["canonical_textures"]

    def test_most_common_color_is_included(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert "warm_gold" in dna["canonical_colors"]

    def test_most_common_icon_is_included(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert "crystal_cluster" in dna["canonical_iconography"]

    def test_most_common_aesthetic_is_included(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        assert "retro" in dna["canonical_aesthetics"]

    def test_least_common_texture_excluded_when_beyond_cap(self) -> None:
        dna = synthesize_edition_visual_dna(self._sample_patterns())
        # "scuffed" has count 1 – lowest; with 6 textures only top 5 kept
        assert "scuffed" not in dna["canonical_textures"]

    def test_empty_patterns_return_empty_lists(self) -> None:
        empty = {
            "texture_vocabulary": Counter(),
            "color_vocabulary": Counter(),
            "icon_vocabulary": Counter(),
            "aesthetic_vocabulary": Counter(),
        }
        dna = synthesize_edition_visual_dna(empty)
        assert dna["canonical_textures"] == []
        assert dna["canonical_colors"] == []
        assert dna["canonical_iconography"] == []
        assert dna["canonical_aesthetics"] == []

    def test_output_is_deterministic(self) -> None:
        patterns = self._sample_patterns()
        dna1 = synthesize_edition_visual_dna(patterns)
        dna2 = synthesize_edition_visual_dna(patterns)
        assert dna1 == dna2

    def test_round_trip_harvest_then_synthesize(self, tmp_path: Path) -> None:
        """harvest → synthesize should produce valid, non-empty DNA."""
        edition = _make_edition(tmp_path, {"01_page": SCHEMA_A, "02_page": SCHEMA_B})
        patterns = harvest_visual_patterns(edition)
        dna = synthesize_edition_visual_dna(patterns)
        assert len(dna["canonical_textures"]) > 0
        assert len(dna["canonical_colors"]) > 0
        assert len(dna["canonical_iconography"]) > 0


# ===========================================================================
# TestVerifyPageAdherence  (bonus coverage for the third public function)
# ===========================================================================


class TestVerifyPageAdherence:
    """Tests for verify_page_adherence()."""

    _DNA = {
        "canonical_textures": ["aged_paper", "worn_ink", "grain", "edge_burn", "print_noise"],
        "canonical_colors": ["warm_gold", "burnt_amber", "deep_brown", "rust_red", "muted_teal", "crystal_glow"],
        "canonical_iconography": ["crystal_cluster", "skull_emblem", "retro_price_tag"],
        "canonical_aesthetics": ["retro", "mystic"],
    }

    def test_returns_required_adherence_keys(self) -> None:
        result = verify_page_adherence(SCHEMA_A, self._DNA)
        assert "texture_match_ratio" in result
        assert "color_match_ratio" in result
        assert "divergent_textures" in result
        assert "divergent_colors" in result

    def test_texture_match_ratio_is_float(self) -> None:
        result = verify_page_adherence(SCHEMA_A, self._DNA)
        assert isinstance(result["texture_match_ratio"], float)

    def test_color_match_ratio_is_float(self) -> None:
        result = verify_page_adherence(SCHEMA_A, self._DNA)
        assert isinstance(result["color_match_ratio"], float)

    def test_divergent_textures_is_list(self) -> None:
        result = verify_page_adherence(SCHEMA_A, self._DNA)
        assert isinstance(result["divergent_textures"], list)

    def test_divergent_colors_is_list(self) -> None:
        result = verify_page_adherence(SCHEMA_A, self._DNA)
        assert isinstance(result["divergent_colors"], list)

    def test_perfect_texture_compliance(self) -> None:
        schema = _make_page_schema(
            textures=list(self._DNA["canonical_textures"]),
            color_palette={"primary": ["warm_gold"]},
            iconography=[],
        )
        result = verify_page_adherence(schema, self._DNA)
        assert result["texture_match_ratio"] == pytest.approx(1.0)

    def test_zero_texture_compliance(self) -> None:
        schema = _make_page_schema(
            textures=["neon_glow", "plastic_sheen"],
            color_palette={"primary": ["warm_gold"]},
            iconography=[],
        )
        result = verify_page_adherence(schema, self._DNA)
        assert result["texture_match_ratio"] == pytest.approx(0.0)

    def test_partial_texture_compliance(self) -> None:
        # aged_paper matches, worn_ink does not (not in page schema)
        schema = _make_page_schema(
            textures=["aged_paper"],
            color_palette={"primary": ["warm_gold"]},
            iconography=[],
        )
        result = verify_page_adherence(schema, self._DNA)
        expected = 1 / len(self._DNA["canonical_textures"])
        assert result["texture_match_ratio"] == pytest.approx(expected)

    def test_divergent_textures_contains_non_canonical_items(self) -> None:
        schema = _make_page_schema(
            textures=["aged_paper", "neon_glow"],
            color_palette={},
            iconography=[],
        )
        result = verify_page_adherence(schema, self._DNA)
        assert "neon_glow" in result["divergent_textures"]
        assert "aged_paper" not in result["divergent_textures"]

    def test_divergent_colors_contains_non_canonical_items(self) -> None:
        schema = _make_page_schema(
            textures=[],
            color_palette={"primary": ["warm_gold", "electric_pink"]},
            iconography=[],
        )
        result = verify_page_adherence(schema, self._DNA)
        assert "electric_pink" in result["divergent_colors"]
        assert "warm_gold" not in result["divergent_colors"]

    def test_empty_page_schema_returns_zero_compliance(self) -> None:
        empty_schema: dict = {}
        result = verify_page_adherence(empty_schema, self._DNA)
        assert result["texture_match_ratio"] == pytest.approx(0.0)
        assert result["color_match_ratio"] == pytest.approx(0.0)
