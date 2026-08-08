"""Page metadata generation (meta.json)."""

import json
from pathlib import Path

from magazine.config import Config
from magazine.utils import REPRODUCIBLE_TIMESTAMP, log_info, log_warn, run, timestamp


def _exif_json(image_path: Path) -> dict:
    """Return a dict of EXIF data for *image_path*, or {} on failure.

    Logs a warning when EXIF extraction fails (e.g. missing ``exiftool`` or
    malformed image data) so that problems are visible rather than silent.
    """
    try:
        result = run(
            ["exiftool", "-j", "-g1", str(image_path)],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        return data[0] if data else {}
    except Exception as exc:  # noqa: BLE001
        log_warn(f"EXIF extraction failed for {image_path}: {exc}")
        return {}


def gen_page_meta(page_dir: Path, *, reproducible: bool = False, exif_disable: bool = False, config: Config | None = None) -> None:
    """Write *page_dir*/meta.json with page metadata (and EXIF if available).

    Page directories must follow the ``NN_slug`` naming convention, where
    ``NN`` is a zero-padded integer (e.g. ``01``, ``10``) and ``slug`` is
    descriptive text (e.g. ``01_intro``, ``10_finale``).  A ``ValueError``
    is raised when the directory name does not conform to this format.

    Args:
        page_dir: Directory containing the page assets.  Must be named
            ``NN_slug`` (e.g. ``01_intro``).
        reproducible: When ``True``, use a fixed epoch timestamp for
            ``generated_at`` instead of the current UTC time, ensuring
            byte-for-byte identical output across builds.
        exif_disable: When ``True``, skip EXIF extraction entirely.
            ``raw_exif`` will be an empty dict in the output.
        config: Configuration instance.  Defaults to a fresh ``Config()``
            when not provided.

    Raises:
        ValueError: When *page_dir* does not follow the ``NN_slug`` format.
    """
    if config is None:
        config = Config()
    img_in = page_dir / "page.png"
    meta_out = page_dir / "meta.json"

    slug = page_dir.name
    raw_idx = slug.split("_")[0]
    if not raw_idx.isdigit():
        raise ValueError(
            f"Invalid page directory name '{slug}': expected 'NN_slug' format "
            "(NN must be a numeric prefix, e.g. '01_intro')."
        )
    idx = int(raw_idx)

    exif_data: dict = {}
    if img_in.exists() and not exif_disable:
        exif_data = _exif_json(img_in)

    meta = {
        "page_id": slug,
        "sequence_index": idx,
        "generated_at": REPRODUCIBLE_TIMESTAMP if reproducible else timestamp(),
        "project_context": {
            "author": config.AUTHOR,
            "alias": config.ALIAS,
            "location": config.LOCATION,
        },
        "raw_exif": exif_data,
    }

    meta_out.write_text(json.dumps(meta, indent=2))
    log_info(f"Metadata written: {meta_out}")
