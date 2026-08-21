from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_first_viewport_carries_identity_proof_and_action_paths() -> None:
    head = "\n".join(_readme_text().splitlines()[:60])

    assert "# Alan Szmyt" in head
    assert (
        "Software engineer building reliable developer platforms, local-first "
        "systems, and AI-assisted workflows."
    ) in head
    assert "[Portfolio](https://szmyty.vercel.app)" in head
    assert "[Ego Hygiene](https://github.com/egohygiene)" in head
    assert "[Repositories](https://github.com/szmyty?tab=repositories)" in head
    assert "## Selected work" in head

    for project in ["Reflector", "Renderflow", "Relay", "Optiflow"]:
        assert project in head


def test_readme_excludes_broken_and_internal_profile_state() -> None:
    readme = _readme_text()

    for forbidden in [
        "soliloquy",
        "szmyty/universal",
        "GitHub Engineering Dashboard",
        "AI Agent Execution Showcase",
        "Completion Matrix",
        "Queue key:",
        "failed-with-fallback",
        "needs-user-verification",
        "GitHub noreply",
    ]:
        assert forbidden not in readme


def test_readme_uses_only_approved_public_destinations() -> None:
    readme = _readme_text()

    approved = [
        "https://szmyty.vercel.app",
        "https://github.com/egohygiene",
        "https://github.com/szmyty?tab=repositories",
        "https://github.com/egohygiene/reflector",
        "https://github.com/egohygiene/renderflow",
        "https://github.com/egohygiene/relay",
        "https://github.com/egohygiene/optiflow",
    ]
    for destination in approved:
        assert destination in readme

    assert "mailto:" not in readme
    assert "@users.noreply.github.com" not in readme


def test_generated_regions_are_reserved_and_empty() -> None:
    readme = _readme_text()
    modules = [
        "github-dashboard",
        "ai-agent-showcase",
        "music-highlight",
        "orcid",
        "medium",
        "education",
        "resume",
        "working-style",
        "soundcloud",
        "steam",
        "stars",
        "oura-trends",
    ]

    for module in modules:
        assert (
            f"<!-- START:{module} -->\n<!-- END:{module} -->"
            in readme
        )
