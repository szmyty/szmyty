"""Edition finalization: staging, CBZ, Reader PDF, Press PDF, metadata."""

import json
import shutil
import zipfile
from io import BytesIO
from pathlib import Path

try:
    from cbz.comic import ComicInfo as _ComicInfo
    from cbz.constants import PageType as _PageType
    from cbz.page import PageInfo as _PageInfo
    _CBZ_AVAILABLE = True
except ImportError:
    _CBZ_AVAILABLE = False

from magazine.assets.latex import assemble_latex_edition
from magazine.assets.sizes import generate_bundle_size_variants
from magazine.config import Config
from magazine.exceptions import EditionBuildError
from magazine.utils import REPRODUCIBLE_TIMESTAMP, log_info, log_success, log_warn, page_dirs, run, timestamp


def finalize_edition(
    edition_dir: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    reproducible: bool = False,
    sizes_disable: bool = False,
    sizes_force: bool = False,
    sizes: list[str] | None = None,
    sizes_config: Path | None = None,
    sizes_safe_mode: bool = False,
    config: Config | None = None,
) -> None:
    """Bundle staged page masters into publishing artifacts.

    Steps:
        1. Validate page.png presence (honour --force to skip validation)
        2. Stage PNG + TIFF masters into artifacts/final_build_stage/
        3. Build comic.cbz (digital)
        4. Build reader.pdf (digital, img2pdf from PNG)
        5. Build press.pdf (print, img2pdf from TIFF) if TIFFs exist
        6. Write publishing/meta.json
        7. Generate bundle size variants (unless sizes_disable=True)

    Args:
        reproducible: When ``True``, use a fixed epoch timestamp for
            ``published_at`` instead of the current UTC time, ensuring
            byte-for-byte identical output across builds.
    """
    if config is None:
        config = Config()
    edition_dir = edition_dir.resolve()
    pub_dir = edition_dir / "publishing"
    stage_dir = edition_dir / "artifacts" / "final_build_stage"

    log_info(f"Initializing Final Assembly: {edition_dir.name}")

    # ------------------------------------------------------------------ #
    # LaTeX edition assembly (idempotent – skips when inputs unchanged)
    # ------------------------------------------------------------------ #
    log_info("🔎 Assembling edition LaTeX before finalize")
    assemble_latex_edition(edition_dir, force=force, config=config)

    page_dirs_list = page_dirs(edition_dir)

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    for p in page_dirs_list:
        if not (p / "page.png").exists():
            if force:
                log_warn(f"Missing page.png in {p.name}, continuing due to --force")
            else:
                raise EditionBuildError(
                    f"Validation failed: Missing page.png in {p.name}"
                )

    # ------------------------------------------------------------------ #
    # Staging
    # ------------------------------------------------------------------ #
    (pub_dir / "digital").mkdir(parents=True, exist_ok=True)
    (pub_dir / "print").mkdir(parents=True, exist_ok=True)
    stage_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        log_warn(f"[dry-run] Would remove and recreate stage_dir: {stage_dir}")
    else:
        shutil.rmtree(stage_dir, ignore_errors=True)
        stage_dir.mkdir(parents=True, exist_ok=True)

    log_info("Staging masters…")
    for p in page_dirs_list:
        slug = p.name
        png = p / "page.png"
        tiff = p / "artifacts" / "page.tiff"
        if png.exists():
            shutil.copy2(png, stage_dir / f"{slug}.png")
        if tiff.exists():
            shutil.copy2(tiff, stage_dir / f"{slug}.tiff")

    # ------------------------------------------------------------------ #
    # CBZ
    # ------------------------------------------------------------------ #
    if not _CBZ_AVAILABLE:
        raise EditionBuildError("❌ CBZ library not installed")

    log_info("🔎 Building CBZ using Python library")
    pngs = sorted(stage_dir.glob("*.png"))
    cbz_path = pub_dir / "digital" / "comic.cbz"

    # Determine page order from manifest.json when available.
    manifest_path = edition_dir / "manifest.json"
    if manifest_path.exists():
        manifest_slugs = json.loads(manifest_path.read_text()).get("pages", [])
        slug_to_png = {p.stem: p for p in pngs}
        ordered_pngs = [slug_to_png[s] for s in manifest_slugs if s in slug_to_png]
        ordered_pngs += [p for p in pngs if p not in ordered_pngs]
    else:
        ordered_pngs = pngs

    cbz_pages = [
        _PageInfo.load(
            path=png,
            type=(
                _PageType.FRONT_COVER
                if i == 0
                else _PageType.BACK_COVER if i == len(ordered_pngs) - 1 else _PageType.STORY
            ),
        )
        for i, png in enumerate(ordered_pngs)
    ]
    comic = _ComicInfo.from_pages(pages=cbz_pages)
    cbz_content = comic.pack()

    if reproducible:
        # Repack with zeroed timestamps to ensure byte-for-byte reproducibility.
        # cbz.pack() uses ZIP_STORED, so we preserve that compression method.
        buf_in = BytesIO(cbz_content)
        buf_out = BytesIO()
        with zipfile.ZipFile(buf_in, "r") as zin, zipfile.ZipFile(buf_out, "w", zipfile.ZIP_STORED) as zout:
            for item in zin.infolist():
                item.date_time = (1980, 1, 1, 0, 0, 0)
                zout.writestr(item, zin.read(item.filename))
        cbz_content = buf_out.getvalue()

    cbz_path.write_bytes(cbz_content)

    # ------------------------------------------------------------------ #
    # Reader PDF
    # ------------------------------------------------------------------ #
    log_info("Building Reader PDF…")
    run(
        ["img2pdf"] + [str(p) for p in pngs] + ["-o", str(pub_dir / "digital" / "reader.pdf")],
    )

    # ------------------------------------------------------------------ #
    # Press PDF (TIFF-based)
    # ------------------------------------------------------------------ #
    tiffs = sorted(stage_dir.glob("*.tiff"))
    if tiffs:
        log_info("🔎 Generating press.pdf from artifacts/page.tiff")
        run(
            ["img2pdf"] + [str(t) for t in tiffs] + ["-o", str(pub_dir / "print" / "press.pdf")],
        )
    else:
        log_warn("⚠️ No TIFF found in artifacts — press.pdf skipped")

    # ------------------------------------------------------------------ #
    # Publishing metadata
    # ------------------------------------------------------------------ #
    meta = {
        "edition_id": edition_dir.name,
        "page_count": len(page_dirs_list),
        "published_at": REPRODUCIBLE_TIMESTAMP if reproducible else timestamp(),
        "format_version": config.FORMAT_VERSION,
        "publisher": config.PUBLISHER,
        "author": config.AUTHOR,
    }
    (pub_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    # ------------------------------------------------------------------ #
    # Bundle size variants
    # ------------------------------------------------------------------ #
    if not sizes_disable:
        generate_bundle_size_variants(
            edition_dir,
            sizes=sizes,
            config_path=sizes_config,
            force=sizes_force,
            safe_mode=sizes_safe_mode,
            config=config,
        )

    log_success(f"Publishing assets ready in {pub_dir}")
