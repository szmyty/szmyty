"""LaTeX asset generation: page.tex and edition.tex assembly with compilation."""

import hashlib
import json
import shutil
from pathlib import Path

from magazine.config import Config
from magazine.hashing import hash_file
from magazine.utils import log_info, log_warn, page_dirs, run


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _resolve_engine(engine: str) -> str:
    """Return *engine* if found on PATH, else fall back to pdflatex."""
    if shutil.which(engine):
        return engine
    if engine != "pdflatex" and shutil.which("pdflatex"):
        log_warn(f"LaTeX engine '{engine}' not found — falling back to pdflatex")
        return "pdflatex"
    return engine  # let the caller fail with a useful subprocess error


def _latex_config_hash(engine: str, safe_mode: bool, safe_margin: str) -> str:
    """Return a short deterministic hash of the active LaTeX configuration."""
    data = f"{engine}|{safe_mode}|{safe_margin}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _geometry_options(*, safe_mode: bool, safe_margin: str) -> str:
    """Return the geometry package options string for the given layout mode."""
    if safe_mode:
        return f"margin={safe_margin}"
    return "margin=0in"


def _page_tex_content(
    image_rel_path: str,
    *,
    safe_mode: bool,
    safe_margin: str,
    paper_width: str,
    paper_height: str,
) -> str:
    """Return the .tex source for a single full-bleed or safe-margin page."""
    geometry = _geometry_options(safe_mode=safe_mode, safe_margin=safe_margin)
    return (
        "\\documentclass{article}\n"
        f"\\usepackage[paperwidth={paper_width},paperheight={paper_height},{geometry}]{{geometry}}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage{xcolor}\n"
        "\\begin{document}\n"
        "\\pagestyle{empty}\n"
        "\\noindent\\includegraphics"
        "[width=\\paperwidth,height=\\paperheight,keepaspectratio=false]"
        "{" + image_rel_path + "}\n"
        "\\end{document}\n"
    )


def _edition_tex_content(
    page_image_paths: list[str],
    *,
    safe_mode: bool,
    safe_margin: str,
    paper_width: str,
    paper_height: str,
) -> str:
    """Return the .tex source for a complete edition (one image per page)."""
    geometry = _geometry_options(safe_mode=safe_mode, safe_margin=safe_margin)
    lines = [
        "\\documentclass{article}",
        f"\\usepackage[paperwidth={paper_width},paperheight={paper_height},{geometry}]{{geometry}}",
        "\\usepackage{graphicx}",
        "\\usepackage{xcolor}",
        "\\begin{document}",
        "\\pagestyle{empty}",
    ]
    for i, img_path in enumerate(page_image_paths):
        lines.append(
            "\\noindent\\includegraphics"
            "[width=\\paperwidth,height=\\paperheight,keepaspectratio=false]"
            "{" + img_path + "}"
        )
        if i < len(page_image_paths) - 1:
            lines.append("\\clearpage")
    lines.append("\\end{document}")
    return "\n".join(lines) + "\n"


def _compile_latex(tex_path: Path, out_dir: Path, *, engine: str) -> None:
    """Compile *tex_path* with *engine*, placing all output in *out_dir*."""
    resolved = _resolve_engine(engine)
    run(
        [
            resolved,
            "-interaction=nonstopmode",
            "-output-directory",
            str(out_dir),
            tex_path.name,
        ],
        cwd=str(out_dir),
    )


def _read_meta(meta_path: Path) -> dict:
    """Read *meta_path* as JSON; return {} on any failure."""
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _write_meta(meta_path: Path, meta: dict) -> None:
    """Write *meta* as pretty JSON to *meta_path*."""
    meta_path.write_text(json.dumps(meta, indent=2))


# --------------------------------------------------------------------------- #
# Page-level LaTeX generation
# --------------------------------------------------------------------------- #

def _should_regenerate_page_latex(
    page_dir: Path,
    artifacts_dir: Path,
    *,
    engine: str,
    safe_mode: bool,
    safe_margin: str,
    force: bool,
) -> bool:
    """Return True when page.tex must be (re)generated."""
    if force:
        return True
    if not (artifacts_dir / "page.tex").exists():
        return True
    img = page_dir / "page.png"
    if not img.exists():
        return False
    build_state = _read_meta(page_dir / ".build_state.json")
    return (
        build_state.get("latex_page_png_hash") != hash_file(img)
        or build_state.get("latex_config_hash") != _latex_config_hash(engine, safe_mode, safe_margin)
    )


def generate_latex_page(
    page_dir: Path,
    artifacts_dir: Path,
    *,
    safe_mode: bool = False,
    engine: str | None = None,
    force: bool = False,
    config: Config | None = None,
) -> None:
    """Generate *artifacts_dir*/page.tex and compile it to page.pdf.

    Skips regeneration when page.png and the LaTeX configuration are unchanged
    (idempotent unless *force* is True).

    Args:
        page_dir:      Directory containing page.png and meta.json.
        artifacts_dir: Destination for generated artifacts.
        safe_mode:     When True, apply safe-margin layout instead of full-bleed.
        engine:        LaTeX engine to use (``xelatex`` or ``pdflatex``).
                       Falls back to ``pdflatex`` when *engine* is unavailable.
        force:         Regenerate even if inputs are unchanged.
        config:        Configuration instance.  Defaults to a fresh ``Config()``
                       when not provided.
    """
    if config is None:
        config = Config()
    resolved_engine = _resolve_engine(engine or config.LATEX_ENGINE)
    safe_margin = config.LATEX_SAFE_MARGIN

    img = page_dir / "page.png"
    if not img.exists():
        log_warn(f"generate_latex_page: no page.png in {page_dir.name} — skipping.")
        return

    if not _should_regenerate_page_latex(
        page_dir,
        artifacts_dir,
        engine=resolved_engine,
        safe_mode=safe_mode,
        safe_margin=safe_margin,
        force=force,
    ):
        log_info(f"LaTeX page up-to-date, skipping: {page_dir.name}")
        return

    log_info(f"Generating LaTeX page for {page_dir.name}…")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    tex_out = artifacts_dir / "page.tex"
    tex_out.write_text(
        _page_tex_content(
            "../page.png",
            safe_mode=safe_mode,
            safe_margin=safe_margin,
            paper_width=config.LATEX_PAPER_WIDTH,
            paper_height=config.LATEX_PAPER_HEIGHT,
        )
    )

    _compile_latex(tex_out, artifacts_dir, engine=resolved_engine)

    compiled_pdf = artifacts_dir / "page.pdf"
    if compiled_pdf.exists():
        compiled_pdf.replace(artifacts_dir / "page.latex.pdf")

    # Persist deterministic cache fields so subsequent runs can skip regeneration.
    # --- Metadata boundary ---
    # .build_state.json  → deterministic fields only (hashes, engine, layout mode).
    #                       Timestamps are excluded so the file stays byte-for-byte
    #                       stable when inputs are unchanged.
    # meta.json          → publishable metadata (generated_at controlled by --reproducible).
    build_state_path = page_dir / ".build_state.json"
    build_state = _read_meta(build_state_path)
    build_state.update(
        {
            "latex_layout_mode": "safe_margin" if safe_mode else "full_bleed",
            "latex_engine": resolved_engine,
            "latex_page_png_hash": hash_file(img),
            "latex_config_hash": _latex_config_hash(resolved_engine, safe_mode, safe_margin),
        }
    )
    _write_meta(build_state_path, build_state)

    log_info(f"LaTeX page generated: {tex_out}")


# --------------------------------------------------------------------------- #
# Edition-level LaTeX assembly
# --------------------------------------------------------------------------- #

def _page_set_hash(page_dirs: list[Path]) -> str:
    """Return a deterministic hash of the ordered page directory names."""
    data = "|".join(p.name for p in page_dirs)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _should_regenerate_edition_latex(
    edition_dir: Path,
    build_dir: Path,
    page_dirs: list[Path],
    *,
    engine: str,
    safe_mode: bool,
    safe_margin: str,
    force: bool,
) -> bool:
    """Return True when edition.tex must be (re)generated."""
    if force:
        return True
    tex_out = build_dir / f"{edition_dir.name}.tex"
    if not tex_out.exists():
        return True
    # Use the sidecar meta file written after successful compilation as the
    # "build completed" signal — avoids depending on the .pdf file which may
    # not be present when compilation is mocked in tests.
    meta = _read_meta(build_dir / ".build_state.json")
    if not meta:
        return True
    return (
        meta.get("page_set_hash") != _page_set_hash(page_dirs)
        or meta.get("latex_config_hash") != _latex_config_hash(engine, safe_mode, safe_margin)
    )


def assemble_latex_edition(
    edition_dir: Path,
    *,
    safe_mode: bool = False,
    engine: str | None = None,
    force: bool = False,
    config: Config | None = None,
) -> None:
    """Assemble and compile a master LaTeX document for the full edition.

    Reads page order from the sorted ``pages/`` subdirectories, generates
    ``build/<edition_name>.tex``, and compiles it to ``build/<edition_name>.pdf``.

    Skips regeneration when the page set and LaTeX configuration are unchanged
    (idempotent unless *force* is True).

    Args:
        edition_dir: Root directory of the edition (contains ``pages/``).
        safe_mode:   When True, apply safe-margin layout instead of full-bleed.
        engine:      LaTeX engine override.  Falls back to ``pdflatex`` when
                     *engine* is unavailable.
        force:       Regenerate even if inputs are unchanged.
        config:      Configuration instance.  Defaults to a fresh ``Config()``
                     when not provided.
    """
    if config is None:
        config = Config()
    resolved_engine = _resolve_engine(engine or config.LATEX_ENGINE)
    safe_margin = config.LATEX_SAFE_MARGIN

    dirs = page_dirs(edition_dir)
    page_images = [p / "page.png" for p in dirs if (p / "page.png").exists()]

    if not page_images:
        log_warn("assemble_latex_edition: no page.png files found — skipping.")
        return

    build_dir = edition_dir / "build"

    if not _should_regenerate_edition_latex(
        edition_dir,
        build_dir,
        dirs,
        engine=resolved_engine,
        safe_mode=safe_mode,
        safe_margin=safe_margin,
        force=force,
    ):
        log_info("Edition LaTeX up-to-date (skipped)")
        return

    log_info(f"Assembling LaTeX edition: {edition_dir.name}…")
    build_dir.mkdir(parents=True, exist_ok=True)

    # Paths are relative to build/ so that the .tex file is portable.
    rel_paths = [f"../pages/{img.parent.name}/page.png" for img in page_images]

    tex_out = build_dir / f"{edition_dir.name}.tex"
    tex_out.write_text(
        _edition_tex_content(
            rel_paths,
            safe_mode=safe_mode,
            safe_margin=safe_margin,
            paper_width=config.LATEX_PAPER_WIDTH,
            paper_height=config.LATEX_PAPER_HEIGHT,
        )
    )

    _compile_latex(tex_out, build_dir, engine=resolved_engine)

    # Persist deterministic cache fields for subsequent idempotency checks.
    # --- Metadata boundary ---
    # .build_state.json  → deterministic fields only (hashes, engine, layout mode).
    #                       Timestamps are excluded so the file stays byte-for-byte
    #                       stable when inputs are unchanged.
    _write_meta(
        build_dir / ".build_state.json",
        {
            "edition_id": edition_dir.name,
            "page_set_hash": _page_set_hash(dirs),
            "latex_config_hash": _latex_config_hash(resolved_engine, safe_mode, safe_margin),
            "latex_layout_mode": "safe_margin" if safe_mode else "full_bleed",
            "latex_engine": resolved_engine,
        },
    )

    log_info(f"LaTeX edition assembled: {tex_out}")
