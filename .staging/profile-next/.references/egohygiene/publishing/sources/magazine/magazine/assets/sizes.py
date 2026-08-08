"""Size variant generation stage (page + bundle).

Produces deterministic, config-driven comic trim-size variants for both
individual pages and compiled edition bundles.  A Strategy pattern is used
for scaling so that a future AI-resize phase can plug in without modifying
this module.
"""

import hashlib
import importlib.resources
import json
from pathlib import Path

from magazine.config import Config
from magazine.hashing import hash_file
from magazine.utils import log_info, log_warn, run

# ---------------------------------------------------------------------------
# Internal path helpers
# ---------------------------------------------------------------------------


def _load_sizes_config(config_path: Path | None = None, config: Config | None = None) -> dict:
    """Load size presets from *config_path*, the env-configured path, or the
    bundled ``magazine/assets/data/sizes.json``.  Returns an empty dict when no
    file is found.
    """
    if config is None:
        config = Config()
    candidates = [
        config_path,
        Path(config.SIZES_CONFIG_PATH) if config.SIZES_CONFIG_PATH else None,
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            try:
                return json.loads(candidate.read_text())
            except (json.JSONDecodeError, OSError):
                pass
    # Fall back to the bundled config distributed with the package.
    try:
        data = (
            importlib.resources.files("magazine.assets.data")
            .joinpath("sizes.json")
            .read_text(encoding="utf-8")
        )
        return json.loads(data)
    except (json.JSONDecodeError, OSError, ModuleNotFoundError, FileNotFoundError, AttributeError):
        pass
    return {}


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def _size_config_hash(size_entry: dict) -> str:
    """Return a 16-character deterministic hash of a size config entry."""
    data = json.dumps(size_entry, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _hash_file_list(paths: list[Path]) -> str:
    """Return a combined hash of an ordered list of files."""
    h = hashlib.sha256()
    for p in paths:
        h.update(p.name.encode())
        h.update(hash_file(p).encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Size selection
# ---------------------------------------------------------------------------

def parse_sizes_list(value: str | None) -> list[str] | None:
    """Parse a comma-separated size list string into a Python list.

    Returns ``None`` when *value* is empty, ``None``, or the literal ``"all"``,
    which signals "generate every configured size".
    """
    if not value or value.strip().lower() == "all":
        return None
    return [s.strip() for s in value.split(",") if s.strip()]


def _resolve_sizes(requested: list[str] | None, sizes_cfg: dict) -> dict:
    """Return the subset of *sizes_cfg* entries to generate.

    When *requested* is ``None`` every entry in *sizes_cfg* is returned.
    """
    if not requested:
        return dict(sizes_cfg)
    return {k: v for k, v in sizes_cfg.items() if k in requested}


# ---------------------------------------------------------------------------
# ImageMagick strategy dispatch
# ---------------------------------------------------------------------------

def _magick_args(
    src: Path,
    out_path: Path,
    *,
    width: int,
    height: int,
    dpi: int,
    strategy: str,
) -> list[str]:
    """Return the ImageMagick command for *strategy*.

    Strategies:
        fit  – Resize to fit *within* the target dimensions; aspect ratio
               preserved; no padding or cropping.
        crop – Resize to *fill* the target dimensions, then center-crop any
               excess; no padding; aspect ratio preserved.
        pad  – Resize to fit within the target dimensions and pad the
               remaining area with white; aspect ratio preserved.
    """
    dims = f"{width}x{height}"
    base: list[str] = [
        "magick", str(src),
        "-units", "PixelsPerInch",
        "-density", str(dpi),
    ]
    if strategy == "crop":
        return base + [
            "-resize", f"{dims}^",
            "-gravity", "center",
            "-extent", dims,
            str(out_path),
        ]
    if strategy == "pad":
        return base + [
            "-resize", dims,
            "-gravity", "center",
            "-background", "white",
            "-extent", dims,
            str(out_path),
        ]
    # Default: "fit"
    return base + ["-resize", dims, str(out_path)]


# ---------------------------------------------------------------------------
# Idempotency checks
# ---------------------------------------------------------------------------

def _should_regenerate_variant(
    out_path: Path,
    meta_path: Path,
    *,
    img_hash: str,
    size_hash: str,
    force: bool,
) -> bool:
    """Return ``True`` when the size variant must be (re)generated."""
    if force or not out_path.exists():
        return True
    if not meta_path.exists():
        return True
    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return True
    return (
        meta.get("source_image_hash") != img_hash
        or meta.get("size_config_hash") != size_hash
    )


def _should_regenerate_bundle_variant(
    meta_path: Path,
    *,
    bundle_hash: str,
    size_hash: str,
    force: bool,
    pdf_path: Path,
) -> bool:
    """Return ``True`` when the bundle size variant must be (re)generated."""
    if force or not pdf_path.exists():
        return True
    if not meta_path.exists():
        return True
    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return True
    return (
        meta.get("source_bundle_hash") != bundle_hash
        or meta.get("size_config_hash") != size_hash
    )


# ---------------------------------------------------------------------------
# Page-level size variant generation
# ---------------------------------------------------------------------------

def generate_size_variants(
    page_dir: Path,
    artifacts_dir: Path,
    *,
    sizes: list[str] | None = None,
    config_path: Path | None = None,
    force: bool = False,
    safe_mode: bool = False,
    config: Config | None = None,
) -> None:
    """Generate size variants for ``page_dir/page.png``.

    Outputs are written to ``artifacts_dir/sizes/<size_name>/page.png``.
    Each variant directory also contains a ``.size_meta.json`` file that
    records the source-image hash and size-config hash so that subsequent
    runs can skip unchanged variants (idempotent by default).

    Args:
        page_dir:      Directory containing ``page.png``.
        artifacts_dir: Destination root for generated artifacts.
        sizes:         Explicit list of size names to generate, or ``None``
                       to use the value of ``MAGAZINE_DEFAULT_SIZES``
                       (defaults to all configured sizes).
        config_path:   Override path to a sizes JSON config file.
        force:         Regenerate all variants even when inputs are unchanged.
        safe_mode:     Recorded in metadata; reserved for future use.
        config:        Configuration instance.  Defaults to a fresh ``Config()``
                       when not provided.
    """
    if config is None:
        config = Config()
    src = page_dir / "page.png"
    if not src.exists():
        log_warn(f"generate_size_variants: no page.png in {page_dir.name} — skipping.")
        return

    sizes_cfg = _load_sizes_config(config_path, config)
    if not sizes_cfg:
        log_warn("generate_size_variants: no size config found — skipping.")
        return

    default_sizes = parse_sizes_list(config.SIZES_DEFAULT)
    requested = sizes if sizes is not None else default_sizes
    active = _resolve_sizes(requested, sizes_cfg)

    if not active:
        log_warn("generate_size_variants: no matching sizes to generate — skipping.")
        return

    img_hash = hash_file(src)
    sizes_out_dir = artifacts_dir / "sizes"

    for size_name, size_entry in active.items():
        size_dir = sizes_out_dir / size_name
        size_dir.mkdir(parents=True, exist_ok=True)

        out_path = size_dir / "page.png"
        meta_path = size_dir / ".size_meta.json"
        size_hash = _size_config_hash(size_entry)

        if not _should_regenerate_variant(
            out_path,
            meta_path,
            img_hash=img_hash,
            size_hash=size_hash,
            force=force,
        ):
            log_info(f"Size variant up-to-date, skipping: {page_dir.name}/{size_name}")
            continue

        log_info(f"Generating size variant '{size_name}' for {page_dir.name}…")
        strategy = size_entry.get("scaling_strategy", "fit")
        width = size_entry["width"]
        height = size_entry["height"]
        dpi = size_entry.get("dpi", 72)

        run(
            _magick_args(
                src,
                out_path,
                width=width,
                height=height,
                dpi=dpi,
                strategy=strategy,
            )
        )

        # Write deterministic cache fields only.
        # --- Metadata boundary ---
        # .size_meta.json  → deterministic fields only (hashes, dimensions, strategy).
        #                     Timestamps are excluded so the file stays byte-for-byte
        #                     stable when inputs are unchanged.
        meta_path.write_text(
            json.dumps(
                {
                    "size_name": size_name,
                    "source_image_hash": img_hash,
                    "size_config_hash": size_hash,
                    "size_mode": "safe_margin" if safe_mode else "full_bleed",
                    "size_strategy": strategy,
                    "width": width,
                    "height": height,
                    "dpi": dpi,
                },
                indent=2,
            )
        )

    log_info(f"Size variants complete: {page_dir.name}")


# ---------------------------------------------------------------------------
# Edition-bundle size variant generation
# ---------------------------------------------------------------------------

def generate_bundle_size_variants(
    edition_dir: Path,
    *,
    sizes: list[str] | None = None,
    config_path: Path | None = None,
    force: bool = False,
    safe_mode: bool = False,
    config: Config | None = None,
) -> None:
    """Generate size variants for a compiled edition bundle.

    For each requested size, every staged page PNG is resized and the
    collection is compiled into a single PDF placed at
    ``publishing/sizes/<size_name>/<edition_name>_<size_name>.pdf``.

    Skips regeneration when source images and size config are unchanged
    (idempotent by default).

    Args:
        edition_dir: Root directory of the edition (contains ``artifacts/``
                     and ``publishing/``).
        sizes:       Explicit list of size names, or ``None`` for
                     ``MAGAZINE_DEFAULT_SIZES`` / all configured sizes.
        config_path: Override path to a sizes JSON config file.
        force:       Regenerate all bundle variants even when unchanged.
        safe_mode:   Recorded in metadata; reserved for future use.
        config:      Configuration instance.  Defaults to a fresh ``Config()``
                     when not provided.
    """
    if config is None:
        config = Config()
    stage_dir = edition_dir / "artifacts" / "final_build_stage"
    pub_dir = edition_dir / "publishing"

    staged_pngs = sorted(stage_dir.glob("*.png"))
    if not staged_pngs:
        log_warn("generate_bundle_size_variants: no staged PNGs found — skipping.")
        return

    sizes_cfg = _load_sizes_config(config_path, config)
    if not sizes_cfg:
        log_warn("generate_bundle_size_variants: no size config found — skipping.")
        return

    default_sizes = parse_sizes_list(config.SIZES_DEFAULT)
    requested = sizes if sizes is not None else default_sizes
    active = _resolve_sizes(requested, sizes_cfg)

    if not active:
        log_warn("generate_bundle_size_variants: no matching sizes to generate — skipping.")
        return

    bundle_hash = _hash_file_list(staged_pngs)

    for size_name, size_entry in active.items():
        size_dir = pub_dir / "sizes" / size_name
        size_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = size_dir / f"{edition_dir.name}_{size_name}.pdf"
        meta_path = size_dir / ".bundle_size_meta.json"
        size_hash = _size_config_hash(size_entry)

        if not _should_regenerate_bundle_variant(
            meta_path,
            bundle_hash=bundle_hash,
            size_hash=size_hash,
            force=force,
            pdf_path=pdf_path,
        ):
            log_info(f"Bundle size variant up-to-date, skipping: {size_name}")
            continue

        log_info(f"Generating bundle size variant '{size_name}'…")
        strategy = size_entry.get("scaling_strategy", "fit")
        width = size_entry["width"]
        height = size_entry["height"]
        dpi = size_entry.get("dpi", 72)

        # Resize each staged page PNG into the size directory.
        sized_pngs: list[Path] = []
        for png in staged_pngs:
            out_png = size_dir / png.name
            run(
                _magick_args(
                    png,
                    out_png,
                    width=width,
                    height=height,
                    dpi=dpi,
                    strategy=strategy,
                )
            )
            sized_pngs.append(out_png)

        # Compile sized PNGs into a single PDF.
        run(["img2pdf"] + [str(p) for p in sized_pngs] + ["-o", str(pdf_path)])

        # Write deterministic cache fields only.
        # --- Metadata boundary ---
        # .bundle_size_meta.json  → deterministic fields only (hashes, dimensions, strategy).
        #                           Timestamps are excluded so the file stays byte-for-byte
        #                           stable when inputs are unchanged.
        meta_path.write_text(
            json.dumps(
                {
                    "size_name": size_name,
                    "source_bundle_hash": bundle_hash,
                    "size_config_hash": size_hash,
                    "size_mode": "safe_margin" if safe_mode else "full_bleed",
                    "size_strategy": strategy,
                    "width": width,
                    "height": height,
                    "dpi": dpi,
                    "page_count": len(sized_pngs),
                },
                indent=2,
            )
        )

    log_info("Bundle size variants complete.")
