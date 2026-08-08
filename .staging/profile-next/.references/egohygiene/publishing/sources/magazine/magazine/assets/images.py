"""Image asset generation: JPG, WEBP, AVIF, TIFF, Instagram, Web, full-bleed PDF, JPEG XL."""

import shutil
from pathlib import Path

from magazine.config import Config
from magazine.utils import log_info, log_warn, run


def gen_jpg(src: Path, out_dir: Path) -> None:
    """Generate high-quality JPEG."""
    run(["magick", str(src), "-quality", "95", str(out_dir / "page.jpg")])


def gen_webp(src: Path, out_dir: Path) -> None:
    """Generate WEBP version."""
    run(["magick", str(src), "-quality", "90", str(out_dir / "page.webp")])


def gen_web_jpg(src: Path, out_dir: Path, config: Config) -> None:
    """Generate web-optimised JPEG (resized to WEB_WIDTH)."""
    run(
        [
            "magick",
            str(src),
            "-resize",
            f"{config.WEB_WIDTH}x",
            "-quality",
            "85",
            str(out_dir / "page.web.jpg"),
        ]
    )


def gen_instagram(src: Path, out_dir: Path, config: Config) -> None:
    """Generate Instagram 4:5 crop JPEG."""
    dims = f"{config.INSTAGRAM_WIDTH}x{config.INSTAGRAM_HEIGHT}"
    run(
        [
            "magick",
            str(src),
            "-resize",
            f"{dims}^",
            "-gravity",
            "center",
            "-extent",
            dims,
            "-quality",
            "90",
            str(out_dir / "page.instagram.jpg"),
        ]
    )


def gen_tiff(src: Path, out_dir: Path, config: Config) -> None:
    """Generate print-quality LZW-compressed TIFF."""
    run(
        [
            "magick",
            str(src),
            "-density",
            str(config.PRINT_DPI),
            "-units",
            "PixelsPerInch",
            "-compress",
            "lzw",
            str(out_dir / "page.tiff"),
        ]
    )


def gen_avif(src: Path, out_dir: Path) -> None:
    """Generate AVIF version using pillow-avif-plugin."""
    try:
        import pillow_avif  # noqa: F401
    except ImportError:
        log_warn("⚠️ AVIF plugin not installed — skipping AVIF generation")
        return
    log_info("🔎 Generating AVIF artifact")
    from PIL import Image
    img = Image.open(src)
    img.save(str(out_dir / "page.avif"))


def gen_fullbleed_pdf(src: Path, out_dir: Path) -> None:
    """Generate full-bleed PDF via img2pdf."""
    run(["img2pdf", str(src), "-o", str(out_dir / "page.fullbleed.pdf")])


def gen_jxl(src: Path, out_dir: Path) -> None:
    """Generate JPEG XL artifact using pillow-jpegxl-plugin."""
    try:
        import pillow_jxl  # noqa: F401
        from PIL import Image
    except ImportError:
        log_warn("JPEG XL plugin not installed — skipping JXL generation")
        return
    log_info("🔎 Generating JPEG XL artifact")
    with Image.open(src) as img:
        img.save(out_dir / "page.jxl")


def generate_image_assets(page_dir: Path, artifacts_dir: Path, config: Config | None = None) -> None:
    """Run all image asset generators for *page_dir*/page.png."""
    if config is None:
        config = Config()
    src = page_dir / "page.png"
    if not src.exists():
        return

    log_info(f"Generating image assets for {page_dir.name}…")
    gen_jpg(src, artifacts_dir)
    gen_webp(src, artifacts_dir)
    gen_avif(src, artifacts_dir)
    gen_web_jpg(src, artifacts_dir, config)
    gen_instagram(src, artifacts_dir, config)
    gen_tiff(src, artifacts_dir, config)
    gen_fullbleed_pdf(src, artifacts_dir)
    gen_jxl(src, artifacts_dir)

    fullbleed_pdf = artifacts_dir / "page.fullbleed.pdf"
    if fullbleed_pdf.exists():
        shutil.copy2(fullbleed_pdf, page_dir / "page.pdf")
