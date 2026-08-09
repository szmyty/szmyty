from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
SHOWCASE_PAGE = REPO_ROOT / "site" / "ai-agent-showcase.html"
OBSERVATORY_JS = REPO_ROOT / "site" / "js" / "execution-observatory.js"
THREE_VENDOR = REPO_ROOT / "site" / "js" / "vendor" / "three.module.min.js"
PREVIEW_IMAGE = (
    REPO_ROOT / "profile" / "artifacts" / "interactive-showcase" / "preview.png"
)
CAPTURE_SCRIPT = REPO_ROOT / "tools" / "capture_interactive_showcase_preview.py"
README = REPO_ROOT / "README.md"


def test_showcase_has_semantic_fallback_before_js() -> None:
    html = SHOWCASE_PAGE.read_text(encoding="utf-8")
    assert "id=\"execution-observatory\"" in html
    assert "trace-observatory-fallback" in html
    assert "<noscript>" in html
    assert html.index("trace-observatory-fallback") < html.index(
        "execution-observatory.js"
    )


def test_showcase_exposes_accessible_controls_and_stage_links() -> None:
    html = SHOWCASE_PAGE.read_text(encoding="utf-8")
    assert "Observatory controls" in html
    assert "data-observatory-toggle-motion" in html
    assert "data-observatory-reduce-motion" in html
    assert "tabindex=\"0\"" in html
    assert html.count("id=\"stage-") >= 6
    assert html.count("data-stage-type=") >= 6


def test_observatory_js_covers_webgl_reduced_motion_and_keyboard() -> None:
    content = OBSERVATORY_JS.read_text(encoding="utf-8")
    assert "WebGLRenderingContext" in content
    assert "prefers-reduced-motion: reduce" in content
    assert "ArrowRight" in content
    assert "ArrowLeft" in content
    assert "requestIdleCallback" in content
    assert 'import("./vendor/three.module.min.js")' in content


def test_three_is_local_and_budgeted() -> None:
    assert THREE_VENDOR.exists()
    assert THREE_VENDOR.stat().st_size <= 380 * 1024
    assert OBSERVATORY_JS.stat().st_size <= 24 * 1024


def test_preview_bridge_artifact_and_capture_command_exist() -> None:
    assert PREVIEW_IMAGE.exists()
    assert PREVIEW_IMAGE.stat().st_size <= 400 * 1024
    script = CAPTURE_SCRIPT.read_text(encoding="utf-8")
    assert "--window-size=" in script
    assert "--virtual-time-budget=6000" in script
    assert "preview=1" in script
    assert "keeping last-known-good preview" in script


def test_readme_preview_links_to_live_pages_experience() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "./profile/artifacts/interactive-showcase/preview.png" in readme
    assert "https://szmyty.github.io/szmyty/ai-agent-showcase.html" in readme
