from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_first_viewport_carries_identity_proof_and_action_paths() -> None:
    head = "\n".join(_readme_text().splitlines()[:60])

    assert "# Alan Szmyt" in head
    assert "**Software Engineer**" in head
    assert "[GitHub](https://github.com/szmyty)" in head
    assert "[Repositories](https://github.com/szmyty?tab=repositories)" in head
    assert "[Evidence Catalog](profile/content/evidence.yml)" in head
    assert "## Hiring Snapshot" in head
    assert "## Selected Work" in head
    assert "soliloquy" in head
    assert "universal" in head


def test_readme_sections_follow_hiring_focused_order() -> None:
    readme = _readme_text()

    ordered_sections = [
        "## Hiring Snapshot",
        "## Selected Work",
        "## Flagship Systems",
        "## Experience and Education",
        "## AI Agent Execution Showcase",
        "## GitHub Engineering Dashboard",
        "## Ego Hygiene Platform",
        "## Research, Writing, and Publications",
        "## Creative Practice",
        "## Gaming and Working Style",
        "## Completion Matrix",
        "## Contact",
    ]

    indices = [readme.index(section) for section in ordered_sections]
    assert indices == sorted(indices)


def test_active_and_hidden_modules_are_placed_in_their_intended_sections() -> None:
    readme = _readme_text()

    ai_heading = readme.index("## AI Agent Execution Showcase")
    github_heading = readme.index("## GitHub Engineering Dashboard")
    creative_heading = readme.index("## Creative Practice")
    gaming_heading = readme.index("## Gaming and Working Style")
    matrix_heading = readme.index("## Completion Matrix")
    contact_heading = readme.index("## Contact")

    assert (
        ai_heading
        < readme.index("<!-- START:ai-agent-showcase -->")
        < github_heading
    )
    assert (
        github_heading
        < readme.index("<!-- START:github-metrics -->")
        < contact_heading
    )
    assert (
        github_heading
        < readme.index("<!-- START:recent-activity -->")
        < contact_heading
    )
    assert (
        creative_heading
        < readme.index("<!-- START:music-highlight -->")
        < gaming_heading
    )
    assert creative_heading < readme.index("<!-- START:soundcloud -->") < gaming_heading
    assert gaming_heading < readme.index("<!-- START:steam -->") < matrix_heading
    assert (
        gaming_heading
        < readme.index("<!-- START:working-style -->")
        < matrix_heading
    )
    assert matrix_heading < readme.index("<!-- START:stars -->") < contact_heading
    assert matrix_heading < readme.index("<!-- START:oura-trends -->") < contact_heading


def test_completion_matrix_records_non_public_modules_without_inline_evidence_ids(
) -> None:
    readme = _readme_text()

    assert "Evidence ID" not in readme

    for label in [
        "Education",
        "Resume",
        "ORCID / publications",
        "Medium / writing",
        "SoundCloud",
        "Steam",
        "Working style",
        "STARS",
        "Oura / personal systems",
    ]:
        assert label in readme
