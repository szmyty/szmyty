"""Contract tests for the evidence-backed Pages companion."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tools.modules import site_companion

REPO_ROOT = Path(__file__).parents[1]
SITE_DIR = REPO_ROOT / "site"
INDEX_PATH = SITE_DIR / "index.html"


class SiteParser(HTMLParser):
    """Collect navigation and metadata attributes from the generated page."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        if element_id := values.get("id"):
            self.ids.add(element_id)
        for attribute in ("href", "src"):
            if reference := values.get(attribute):
                self.references.append(reference)
        if tag == "meta":
            key = values.get("name") or values.get("property")
            content = values.get("content")
            if key and content:
                self.meta[key] = content
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")


def _parse_site() -> tuple[str, SiteParser]:
    html = INDEX_PATH.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    return html, parser


def test_committed_site_matches_deterministic_render() -> None:
    assert INDEX_PATH.read_text(encoding="utf-8") == site_companion.render_site()


def test_site_config_references_only_verified_public_evidence() -> None:
    config = site_companion.load_config()
    catalog = site_companion.load_evidence()
    evidence_ids = list(config.evidence.model_dump().values()) + [
        system.evidence_id for system in config.selected_systems
    ]
    for evidence_id in evidence_ids:
        entry = catalog[evidence_id]
        assert entry.status == "verified"
        assert entry.sensitivity == "public"


def test_build_rejects_unverified_selected_system() -> None:
    config = site_companion.load_config()
    catalog = site_companion.load_evidence()
    evidence_id = config.selected_systems[0].evidence_id
    catalog[evidence_id] = catalog[evidence_id].model_copy(
        update={"status": "needs-user-verification"}
    )
    with pytest.raises(ValueError, match="must be verified and public"):
        site_companion.build_context(config, catalog)


def test_generated_links_are_local_or_configured_public_destinations() -> None:
    _, parser = _parse_site()
    config = site_companion.load_config()
    context = site_companion.build_context(config, site_companion.load_evidence())
    profile = context["profile"]
    systems = context["systems"]
    expected_public_urls = {
        config.site.canonical_url,
        config.site.source_url,
        context["license_url"],
        profile["github"].url,
        profile["contact"].url,
        profile["creative"].url,
        profile["public_lab"].url,
        *(system["url"] for system in systems),
    }
    actual_public_urls = {
        reference for reference in parser.references if reference.startswith("https://")
    }
    assert actual_public_urls == expected_public_urls

    for reference in parser.references:
        if reference.startswith(("https://", "#")):
            continue
        assert (SITE_DIR / reference).is_file(), f"missing local asset: {reference}"


def test_page_anchors_resolve() -> None:
    _, parser = _parse_site()
    for reference in parser.references:
        if reference.startswith("#"):
            assert reference.removeprefix("#") in parser.ids


def test_metadata_uses_current_positioning_without_missing_card_image() -> None:
    _, parser = _parse_site()
    config = site_companion.load_config()
    catalog = site_companion.load_evidence()
    positioning = catalog[config.evidence.positioning].claim
    assert parser.canonical == config.site.canonical_url
    assert parser.meta["description"] == positioning
    assert parser.meta["og:description"] == positioning
    assert parser.meta["og:url"] == config.site.canonical_url
    assert parser.meta["twitter:card"] == "summary"
    assert "og:image" not in parser.meta
    assert "twitter:image" not in parser.meta


def test_structured_data_matches_verified_identity() -> None:
    html, _ = _parse_site()
    match = re.search(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None
    data = json.loads(match.group(1))
    config = site_companion.load_config()
    catalog = site_companion.load_evidence()
    assert data["name"] == catalog[config.evidence.name].claim
    assert data["jobTitle"] == catalog[config.evidence.role].claim
    assert data["description"] == catalog[config.evidence.positioning].claim
    assert data["url"] == config.site.canonical_url


def test_repository_links_use_configured_default_branch() -> None:
    html, _ = _parse_site()
    config = site_companion.load_config()
    expected_license = (
        f"{config.site.source_url}/blob/{config.site.default_branch}/LICENSE"
    )
    assert expected_license in html
    assert f"{config.site.source_url}/blob/main/" not in html


def test_retired_placeholder_content_is_absent() -> None:
    html, _ = _parse_site()
    retired_fragments = {
        "Staff-level software architect",
        "github.com/szmyty/soliloquy",
        "github.com/szmyty/universal",
        "soundcloud.com/szmyty",
        "og-image.png",
        "React Native / Tauri",
        "architecture diagram placeholder",
    }
    for fragment in retired_fragments:
        assert fragment not in html
