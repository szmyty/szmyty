"""Screenplay asset generation: PDF (afterwriting), JSON (scripttool), HTML (wrap)."""

from pathlib import Path

from magazine.utils import log_info, run


def gen_screenplay_pdf(fountain: Path, out_dir: Path) -> None:
    """Render Fountain → PDF via afterwriting."""
    run(
        [
            "afterwriting",
            "--source",
            str(fountain),
            "--pdf",
            str(out_dir / "page.fountain.pdf"),
            "--overwrite",
        ]
    )


def gen_screenplay_json(fountain: Path, out_dir: Path) -> None:
    """Convert Fountain → pretty-printed JSON via scripttool + jq."""
    scripttool_result = run(
        ["scripttool", "fountain2json", str(fountain)],
        capture_output=True,
        text=True,
    )
    jq_result = run(
        ["jq", "."],
        input=scripttool_result.stdout,
        capture_output=True,
        text=True,
    )
    (out_dir / "page.json").write_text(jq_result.stdout)


def gen_screenplay_html(fountain: Path, out_dir: Path) -> None:
    """Convert Fountain → HTML via wrap."""
    run(["wrap", "html", str(fountain), "-o", str(out_dir / "page.html")])


def generate_screenplay_assets(page_dir: Path, artifacts_dir: Path) -> None:
    """Run all screenplay asset generators for *page_dir*/page.fountain."""
    fountain = page_dir / "page.fountain"
    if not fountain.exists():
        return

    log_info(f"Generating screenplay assets for {page_dir.name}…")
    gen_screenplay_pdf(fountain, artifacts_dir)
    gen_screenplay_json(fountain, artifacts_dir)
    gen_screenplay_html(fountain, artifacts_dir)
