"""Tests for enriched Steam card rendering."""

from __future__ import annotations

import json

from tools.modules import steam


def test_extended_stats_uses_owned_games_and_badges(monkeypatch) -> None:
    responses = {
        "IPlayerService/GetOwnedGames/v1": {
            "response": {"game_count": 321, "games": []}
        },
        "IPlayerService/GetBadges/v1": {
            "response": {
                "badges": [{"badgeid": 1}, {"badgeid": 2}],
                "player_xp": 9876,
            }
        },
    }

    def fake_get(endpoint: str, params: dict[str, str], api_key: str):
        return responses[endpoint]

    monkeypatch.setattr(steam, "_steam_get", fake_get)
    stats = steam.fetch_extended_stats("key", "76561198000000000")

    assert stats["owned_games"] == 321
    assert stats["badge_count"] == 2
    assert stats["player_xp"] == 9876
    assert stats["is_synthetic"] is False


def test_fixture_cache_is_not_promoted_to_public_cache(tmp_path) -> None:
    output = tmp_path / "cache.json"
    output.write_text(
        steam.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    assert steam.load_cached(output) is None


def test_build_snapshot_generates_responsive_cards(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("STEAM_WEB_API_KEY", raising=False)
    monkeypatch.delenv("STEAM_ID64", raising=False)
    output = tmp_path / "steam" / "cache.json"

    snapshot = steam.build_snapshot(
        output_path=output,
        fixture_path=steam.DEFAULT_FIXTURE,
    )

    assert snapshot.data_source == "fixture"
    assert (output.parent / "stats.json").exists()
    assert (output.parent / "card-light.svg").exists()
    assert (output.parent / "card-mobile-dark.svg").exists()


def test_fixture_context_is_hidden_from_readme(tmp_path) -> None:
    artifact = tmp_path / "cache.json"
    artifact.write_text(
        steam.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "stats.json").write_text(
        json.dumps(steam._empty_stats()),
        encoding="utf-8",
    )

    context = steam.load_template_context(artifact)
    assert context["is_public"] is False


def test_svg_contains_steam_native_metrics(tmp_path) -> None:
    snapshot = steam.load_fixture().model_copy(
        update={"data_source": "live", "display_name": "Test Player"}
    )
    stats = {
        "owned_games": 321,
        "badge_count": 12,
        "player_xp": 9876,
        "data_source": "live",
        "is_synthetic": False,
    }
    steam.render_cards(snapshot, stats, tmp_path)
    svg = (tmp_path / "card-light.svg").read_text(encoding="utf-8")

    assert "STEAM SNAPSHOT" in svg
    assert "PLAYER XP" in svg
    assert "OWNED GAMES" in svg
    assert "BADGES" in svg
    assert "online" not in svg.casefold()
