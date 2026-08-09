"""Tests for ORCID and Medium profile modules.

Covers: fixture loading, empty/unconfigured state, provider failure fallback,
and deterministic rendering via Jinja2 templates.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tools.modules import medium as medium_mod
from tools.modules import orcid as orcid_mod
from tools.profile_builder.models import (
    EducationConfig,
    EducationDegree,
    MediumArticle,
    MediumConfig,
    MediumFeed,
    OrcidConfig,
    OrcidData,
    OrcidWork,
    ResumeConfig,
    StarsConfig,
    WorkingStyleConfig,
)
from tools.profile_builder.rendering import render_template

# ---------------------------------------------------------------------------
# ORCID — model tests
# ---------------------------------------------------------------------------


def test_orcid_config_default_disabled() -> None:
    config = OrcidConfig()
    assert config.enabled is False
    assert config.orcid_id is None


def test_orcid_config_invalid_id_format() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OrcidConfig(enabled=True, orcid_id="not-valid")


def test_orcid_config_valid_id() -> None:
    config = OrcidConfig(enabled=True, orcid_id="0000-0001-2345-6789")
    assert config.orcid_id == "0000-0001-2345-6789"


def test_orcid_data_empty() -> None:
    data = OrcidData()
    assert data.works == []
    assert data.data_source == "disabled"


def test_orcid_work_normalises_doi() -> None:
    work = OrcidWork(title="Test Paper", doi="  10.1234/test  ")
    assert work.doi == "10.1234/test"


def test_orcid_work_empty_doi_is_none() -> None:
    work = OrcidWork(title="Test Paper", doi="")
    assert work.doi is None


# ---------------------------------------------------------------------------
# ORCID — module tests
# ---------------------------------------------------------------------------


def test_orcid_fixture_loads(tmp_path: Path) -> None:
    data = orcid_mod.load_fixture(orcid_mod.DEFAULT_FIXTURE)
    assert isinstance(data, OrcidData)
    assert data.data_source == "fixture"


def test_orcid_disabled_when_no_config(tmp_path: Path) -> None:
    config_path = tmp_path / "orcid-config.yml"
    output_path = tmp_path / "orcid.json"
    # No config file → disabled
    data = orcid_mod.build_orcid(
        config_path=config_path,
        output_path=output_path,
        fixture_path=orcid_mod.DEFAULT_FIXTURE,
    )
    assert data.data_source == "disabled"
    assert output_path.exists()
    written = OrcidData.model_validate_json(output_path.read_text())
    assert written.data_source == "disabled"


def test_orcid_disabled_when_enabled_false(tmp_path: Path) -> None:
    config_path = tmp_path / "orcid-config.yml"
    config_path.write_text("enabled: false\norcid_id: null\n", encoding="utf-8")
    output_path = tmp_path / "orcid.json"
    data = orcid_mod.build_orcid(
        config_path=config_path,
        output_path=output_path,
        fixture_path=orcid_mod.DEFAULT_FIXTURE,
    )
    assert data.data_source == "disabled"


def test_orcid_provider_failure_falls_back_to_cache(tmp_path: Path) -> None:
    # Pre-seed a cache file
    cached = OrcidData(
        orcid_id="0000-0001-2345-6789",
        profile_url="https://orcid.org/0000-0001-2345-6789",
        works=[],
        data_source="live",
    )
    output_path = tmp_path / "orcid.json"
    output_path.write_text(cached.model_dump_json(), encoding="utf-8")

    config_path = tmp_path / "orcid-config.yml"
    config_path.write_text(
        "enabled: true\norcid_id: \"0000-0001-2345-6789\"\n",
        encoding="utf-8",
    )

    with patch.object(
        orcid_mod, "fetch_live_data", side_effect=orcid_mod.ProviderFailure("down")
    ):
        data = orcid_mod.build_orcid(
            config_path=config_path,
            output_path=output_path,
            fixture_path=orcid_mod.DEFAULT_FIXTURE,
        )

    assert data.data_source == "cache"
    assert data.orcid_id == "0000-0001-2345-6789"


def test_orcid_provider_failure_falls_back_to_fixture(tmp_path: Path) -> None:
    config_path = tmp_path / "orcid-config.yml"
    config_path.write_text(
        "enabled: true\norcid_id: \"0000-0001-2345-6789\"\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "orcid.json"
    # No cache → falls back to fixture

    with patch.object(
        orcid_mod, "fetch_live_data", side_effect=orcid_mod.ProviderFailure("down")
    ):
        data = orcid_mod.build_orcid(
            config_path=config_path,
            output_path=output_path,
            fixture_path=orcid_mod.DEFAULT_FIXTURE,
        )

    assert data.data_source == "fixture"


def test_orcid_deterministic_rendering_disabled() -> None:
    data = OrcidData(data_source="disabled")
    rendered = render_template("orcid.md.j2", {"data": data})
    assert rendered.strip() == ""


def test_orcid_deterministic_rendering_with_works() -> None:
    data = OrcidData(
        orcid_id="0000-0001-2345-6789",
        profile_url="https://orcid.org/0000-0001-2345-6789",
        works=[
            OrcidWork(
                title="A Study of Things",
                work_type="journal-article",
                year=2023,
                doi="10.1234/test",
                contributor_role="author",
            )
        ],
        data_source="fixture",
    )
    rendered = render_template("orcid.md.j2", {"data": data})
    assert "0000-0001-2345-6789" in rendered
    assert "A Study of Things" in rendered
    assert "10.1234/test" in rendered


def test_orcid_rendering_is_deterministic() -> None:
    data = OrcidData(
        orcid_id="0000-0001-2345-6789",
        profile_url="https://orcid.org/0000-0001-2345-6789",
        works=[OrcidWork(title="Paper", year=2022, doi="10.0000/x")],
        data_source="fixture",
    )
    first = render_template("orcid.md.j2", {"data": data})
    second = render_template("orcid.md.j2", {"data": data})
    assert first == second


# ---------------------------------------------------------------------------
# Medium — model tests
# ---------------------------------------------------------------------------


def test_medium_config_default_disabled() -> None:
    config = MediumConfig()
    assert config.enabled is False
    assert config.username is None
    assert config.feed_url is None


def test_medium_config_feed_url() -> None:
    config = MediumConfig(enabled=True, username="alanwriter")
    assert config.feed_url == "https://medium.com/feed/@alanwriter"


def test_medium_feed_empty() -> None:
    feed = MediumFeed()
    assert feed.articles == []
    assert feed.data_source == "disabled"


def test_medium_article_model() -> None:
    article = MediumArticle(
        title="My Post",
        canonical_url="https://medium.com/@user/my-post-abc123",
        published_date="2024-01-15",
        summary="A short summary.",
    )
    assert article.title == "My Post"
    assert article.published_date == "2024-01-15"


# ---------------------------------------------------------------------------
# Medium — safe_summary helper
# ---------------------------------------------------------------------------


def test_safe_summary_strips_html() -> None:
    raw = "<p>Hello <b>world</b></p>"
    result = medium_mod._safe_summary(raw)
    assert "<" not in result
    assert "Hello" in result
    assert "world" in result


def test_safe_summary_strips_tracking_urls() -> None:
    raw = "Read more at https://example.com/post?utm_source=rss&utm_medium=email"
    result = medium_mod._safe_summary(raw)
    assert "utm_source" not in result


def test_safe_summary_truncates() -> None:
    raw = "word " * 100
    result = medium_mod._safe_summary(raw, max_chars=50)
    assert len(result) <= 60  # allow for the ellipsis and word boundary
    assert result.endswith("…")


def test_parse_date_iso() -> None:
    assert medium_mod._parse_date("2024-01-15T12:00:00Z") == "2024-01-15"


def test_parse_date_rfc2822() -> None:
    assert medium_mod._parse_date("Mon, 15 Jan 2024 00:00:00 +0000") == "2024-01-15"


# ---------------------------------------------------------------------------
# Medium — module tests
# ---------------------------------------------------------------------------


def test_medium_fixture_loads(tmp_path: Path) -> None:
    feed = medium_mod.load_fixture(medium_mod.DEFAULT_FIXTURE)
    assert isinstance(feed, MediumFeed)
    assert feed.data_source == "fixture"


def test_medium_disabled_when_no_config(tmp_path: Path) -> None:
    config_path = tmp_path / "medium-config.yml"
    output_path = tmp_path / "medium.json"
    data = medium_mod.build_medium(
        config_path=config_path,
        output_path=output_path,
        fixture_path=medium_mod.DEFAULT_FIXTURE,
    )
    assert data.data_source == "disabled"
    assert output_path.exists()


def test_medium_disabled_when_enabled_false(tmp_path: Path) -> None:
    config_path = tmp_path / "medium-config.yml"
    config_path.write_text("enabled: false\nusername: null\n", encoding="utf-8")
    output_path = tmp_path / "medium.json"
    data = medium_mod.build_medium(
        config_path=config_path,
        output_path=output_path,
        fixture_path=medium_mod.DEFAULT_FIXTURE,
    )
    assert data.data_source == "disabled"


def test_medium_provider_failure_falls_back_to_cache(tmp_path: Path) -> None:
    cached = MediumFeed(
        username="alanwriter",
        profile_url="https://medium.com/@alanwriter",
        articles=[
            MediumArticle(
                title="Cached Post",
                canonical_url="https://medium.com/@alanwriter/cached",
                published_date="2024-01-10",
            )
        ],
        data_source="live",
    )
    output_path = tmp_path / "medium.json"
    output_path.write_text(cached.model_dump_json(), encoding="utf-8")

    config_path = tmp_path / "medium-config.yml"
    config_path.write_text("enabled: true\nusername: alanwriter\n", encoding="utf-8")

    with patch.object(
        medium_mod, "fetch_live_feed", side_effect=medium_mod.ProviderFailure("down")
    ):
        data = medium_mod.build_medium(
            config_path=config_path,
            output_path=output_path,
            fixture_path=medium_mod.DEFAULT_FIXTURE,
        )

    assert data.data_source == "cache"
    assert data.articles[0].title == "Cached Post"


def test_medium_provider_failure_falls_back_to_fixture(tmp_path: Path) -> None:
    config_path = tmp_path / "medium-config.yml"
    config_path.write_text("enabled: true\nusername: alanwriter\n", encoding="utf-8")
    output_path = tmp_path / "medium.json"

    with patch.object(
        medium_mod, "fetch_live_feed", side_effect=medium_mod.ProviderFailure("down")
    ):
        data = medium_mod.build_medium(
            config_path=config_path,
            output_path=output_path,
            fixture_path=medium_mod.DEFAULT_FIXTURE,
        )

    assert data.data_source == "fixture"


def test_medium_deterministic_rendering_disabled() -> None:
    feed = MediumFeed(data_source="disabled")
    rendered = render_template("medium.md.j2", {"data": feed})
    assert rendered.strip() == ""


def test_medium_deterministic_rendering_with_articles() -> None:
    feed = MediumFeed(
        username="alanwriter",
        profile_url="https://medium.com/@alanwriter",
        articles=[
            MediumArticle(
                title="Engineering Thoughts",
                canonical_url="https://medium.com/@alanwriter/engineering-thoughts",
                published_date="2024-03-01",
                summary="Reflections on building reliable software.",
            )
        ],
        data_source="fixture",
    )
    rendered = render_template("medium.md.j2", {"data": feed})
    assert "Engineering Thoughts" in rendered
    assert "2024-03-01" in rendered


def test_medium_rendering_is_deterministic() -> None:
    feed = MediumFeed(
        username="alanwriter",
        profile_url="https://medium.com/@alanwriter",
        articles=[
            MediumArticle(
                title="Post A",
                canonical_url="https://medium.com/@alanwriter/post-a",
                published_date="2024-01-01",
            )
        ],
        data_source="fixture",
    )
    first = render_template("medium.md.j2", {"data": feed})
    second = render_template("medium.md.j2", {"data": feed})
    assert first == second


# ---------------------------------------------------------------------------
# Education — model tests
# ---------------------------------------------------------------------------


def test_education_config_no_public_degrees_by_default() -> None:
    config = EducationConfig(
        degrees=[
            EducationDegree(
                institution="UMass Lowell",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                evidence_id="education-umass-lowell-bs-cs",
                enabled=False,
            )
        ]
    )
    assert config.public_degrees == []


def test_education_config_enabled_degree_is_public() -> None:
    degree = EducationDegree(
        institution="UMass Lowell",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        institution_url="https://www.uml.edu/sciences/computer-science/",
        evidence_id="education-umass-lowell-bs-cs",
        enabled=True,
    )
    config = EducationConfig(degrees=[degree])
    assert len(config.public_degrees) == 1
    assert config.public_degrees[0].institution == "UMass Lowell"


# ---------------------------------------------------------------------------
# Resume — model tests
# ---------------------------------------------------------------------------


def test_resume_config_disabled_by_default() -> None:
    config = ResumeConfig()
    assert config.enabled is False
    assert config.public_url is None


def test_resume_config_checklist_path() -> None:
    config = ResumeConfig()
    assert config.checklist_path == "docs/RESUME-CHECKLIST.md"


# ---------------------------------------------------------------------------
# Working style — model tests
# ---------------------------------------------------------------------------


def test_working_style_disabled_by_default() -> None:
    config = WorkingStyleConfig()
    assert config.enabled is False
    assert config.personality_type is None


def test_working_style_not_renderable_without_approval() -> None:
    # The template must produce empty output when enabled is False
    config = WorkingStyleConfig(
        enabled=False,
        personality_type="INFJ-A",
        personality_url="https://www.16personalities.com/infj-personality",
        summary="I prefer deep focus and deliberate collaboration.",
    )
    rendered = render_template("working-style.md.j2", {"config": config})
    assert rendered.strip() == ""


def test_working_style_renders_when_approved() -> None:
    config = WorkingStyleConfig(
        enabled=True,
        personality_type="INFJ-A",
        personality_url="https://www.16personalities.com/infj-personality",
        summary="I prefer deep focus and deliberate collaboration.",
    )
    rendered = render_template("working-style.md.j2", {"config": config})
    assert "INFJ-A" in rendered
    assert "deep focus" in rendered


# ---------------------------------------------------------------------------
# STARS — model tests
# ---------------------------------------------------------------------------


def test_stars_config_disabled_by_default() -> None:
    config = StarsConfig()
    assert config.enabled is False
    assert config.public_items == []


def test_stars_not_renderable_without_approval() -> None:
    config = StarsConfig(enabled=False, public_items=["Growth mindset"])
    rendered = render_template("stars.md.j2", {"config": config})
    assert rendered.strip() == ""


def test_stars_remains_empty_by_default() -> None:
    config = StarsConfig()
    rendered = render_template("stars.md.j2", {"config": config})
    assert rendered.strip() == ""
