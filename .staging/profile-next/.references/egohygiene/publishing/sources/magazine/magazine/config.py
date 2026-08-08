"""12-factor configuration for the magazine production engine.

All tuneable values are read from environment variables with sane defaults,
following the Twelve-Factor App methodology (https://12factor.net/config).
"""

import os
from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent


class Config:
    """Central configuration object.  Values come from env vars at instantiation."""

    def __init__(self) -> None:
        # ------------------------------------------------------------------ #
        # Image / print constants
        # ------------------------------------------------------------------ #
        self.PRINT_DPI: int = int(os.environ.get("MAGAZINE_PRINT_DPI", "300"))
        self.WEB_WIDTH: int = int(os.environ.get("MAGAZINE_WEB_WIDTH", "1080"))
        self.INSTAGRAM_WIDTH: int = int(os.environ.get("MAGAZINE_INSTAGRAM_WIDTH", "1080"))
        self.INSTAGRAM_HEIGHT: int = int(os.environ.get("MAGAZINE_INSTAGRAM_HEIGHT", "1350"))

        # ------------------------------------------------------------------ #
        # AI / Fountain generation
        # ------------------------------------------------------------------ #
        self.FOUNTAIN_AI_RUNTIME: str = os.environ.get(
            "MAGAZINE_FOUNTAIN_AI_RUNTIME", "ollama"
        )
        self.FOUNTAIN_AI_MODEL: str = os.environ.get(
            "MAGAZINE_FOUNTAIN_AI_MODEL", "qwen3-vl-fountain:latest"
        )
        self.FOUNTAIN_MODELFILE_PATH: str = os.environ.get(
            "MAGAZINE_FOUNTAIN_MODELFILE_PATH",
            str(_PACKAGE_DIR / "ai" / "fountain.modelfile"),
        )

        # ------------------------------------------------------------------ #
        # LaTeX export
        # ------------------------------------------------------------------ #
        self.LATEX_ENGINE: str = os.environ.get("MAGAZINE_LATEX_ENGINE", "xelatex")
        self.LATEX_SAFE_MARGIN: str = os.environ.get("MAGAZINE_LATEX_SAFE_MARGIN", "0.25in")
        self.LATEX_PAPER_WIDTH: str = os.environ.get("MAGAZINE_LATEX_PAPER_WIDTH", "8.5in")
        self.LATEX_PAPER_HEIGHT: str = os.environ.get("MAGAZINE_LATEX_PAPER_HEIGHT", "11in")

        # ------------------------------------------------------------------ #
        # Size variants
        # ------------------------------------------------------------------ #
        self.SIZES_CONFIG_PATH: str = os.environ.get("MAGAZINE_SIZES_CONFIG", "")
        self.SIZES_DEFAULT: str = os.environ.get("MAGAZINE_DEFAULT_SIZES", "all")

        # ------------------------------------------------------------------ #
        # Metadata / authorship
        # ------------------------------------------------------------------ #
        self.AUTHOR: str = os.environ.get("MAGAZINE_AUTHOR", "Alan R Szmyt")
        self.ALIAS: str = os.environ.get("MAGAZINE_ALIAS", "Play Function")
        self.LOCATION: str = os.environ.get("MAGAZINE_LOCATION", "Wilmington, MA")
        self.PUBLISHER: str = os.environ.get("MAGAZINE_PUBLISHER", "Play Function")
        self.FORMAT_VERSION: str = os.environ.get("MAGAZINE_FORMAT_VERSION", "1.0")
        self.EDITION_NAME: str = os.environ.get("MAGAZINE_EDITION_NAME", "")

        # ------------------------------------------------------------------ #
        # Subprocess execution
        # ------------------------------------------------------------------ #
        self.SUBPROCESS_TIMEOUT: int = int(
            os.environ.get("MAGAZINE_SUBPROCESS_TIMEOUT", "300")
        )


