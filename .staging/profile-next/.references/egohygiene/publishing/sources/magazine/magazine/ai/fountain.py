"""Fountain screenplay AI generation stage (Ollama-based)."""

import json
import shutil
from pathlib import Path

from magazine.ai.base import AIStage
from magazine.config import Config
from magazine.exceptions import AIRuntimeError, ModelfileError
from magazine.hashing import hash_file
from magazine.utils import log_info, log_success, log_warn, run

_ERROR_PHRASES = ("Error", "Failed", "Cannot see image", "Thinking...")


def _build_prompt(author: str, edition_name: str) -> str:
    """Build the Fountain generation prompt with injected author and edition metadata."""
    return f"""\
You are generating a Fountain screenplay for a printed magazine page.

You must follow this structure exactly.

1. Begin with metadata header:
Title: <most prominent visible title on the page>
Credit: Written & Designed by {author}
Draft date: <today's date>
Source: {edition_name}

2. Add a blank line.

3. Write a proper Fountain scene heading in this format:
INT. PRINTED MAGAZINE – <PAGE TITLE> – TIMELESS

4. Describe the page layout visually in short, deliberate lines.
- Do NOT over-explain.
- Do NOT interpret symbolism.
- Do NOT speculate.
- Describe only what is visible.

5. Transcribe all clearly visible text exactly as written on the page.
- Preserve capitalization.
- Preserve punctuation.
- Keep formatting clean.

6. End with 2–4 minimal reflective lines in the same tone as:
"Instruction, embedded in artifact."
"Stillness, applied."

Rules:
- No markdown.
- No commentary.
- No explanation.
- No bullet points.
- Output only valid Fountain script text.
- Keep language restrained and cinematic.
- Avoid flowery or spiritual interpretation.

Be precise.
Be minimal.
Be structured.\
"""


class FountainAIStage(AIStage):
    """Generate Fountain screenplays from page artwork via Ollama."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config if config is not None else Config()

    def ensure_model(self) -> None:
        """Ensure the Ollama runtime and model are available."""
        if shutil.which(self._config.FOUNTAIN_AI_RUNTIME) is None:
            raise AIRuntimeError(
                f"AI runtime '{self._config.FOUNTAIN_AI_RUNTIME}' not found.\n"
                "Install Ollama from: https://ollama.com"
            )

        try:
            run(
                [self._config.FOUNTAIN_AI_RUNTIME, "show", self._config.FOUNTAIN_AI_MODEL],
                capture_output=True,
            )
        except Exception:  # noqa: BLE001
            log_warn(
                f"AI model '{self._config.FOUNTAIN_AI_MODEL}' not found. "
                "Building from Modelfile…"
            )
            modelfile = Path(self._config.FOUNTAIN_MODELFILE_PATH)
            if not modelfile.exists():
                raise ModelfileError(
                    f"Modelfile not found at {self._config.FOUNTAIN_MODELFILE_PATH}"
                ) from None
            run(
                [
                    self._config.FOUNTAIN_AI_RUNTIME,
                    "create",
                    self._config.FOUNTAIN_AI_MODEL,
                    "-f",
                    str(modelfile),
                ]
            )
            log_success(f"Model '{self._config.FOUNTAIN_AI_MODEL}' created successfully.")

    def should_regenerate(self, page_dir: Path) -> bool:
        """Return True when the image has changed or fountain file is absent."""
        image_path = page_dir / "page.png"
        fountain_path = page_dir / "page.fountain"
        build_state_path = page_dir / ".build_state.json"

        if not image_path.exists():
            return False

        if not fountain_path.exists():
            return True

        current_hash = hash_file(image_path)

        if build_state_path.exists():
            try:
                build_state = json.loads(build_state_path.read_text())
                previous_hash = build_state.get("image_hash", "")
                return current_hash != previous_hash
            except Exception:  # noqa: BLE001
                pass

        return True

    def _validate_output(self, output: str) -> None:
        """Raise AIRuntimeError if output is not a valid Fountain script.

        Checks performed (lightweight, not a full syntax parse):
        - Output is non-empty and contains non-whitespace content.
        - Output does not contain known AI error phrases.
        - Output contains a ``Title:`` metadata line.
        - Output contains at least one scene heading (``INT.`` or ``EXT.``).
        - Output contains at least two newline-separated structural blocks.
        """
        if not output or not output.strip():
            raise AIRuntimeError(
                "AI returned empty output. Refusing to write page.fountain."
            )

        preview = output[:200]

        for phrase in _ERROR_PHRASES:
            if phrase in output:
                log_warn(
                    f"AI output contains error phrase '{phrase}'. "
                    f"First 200 chars: {preview!r}"
                )
                raise AIRuntimeError(
                    f"AI output contains error phrase '{phrase}'. "
                    "Refusing to write page.fountain."
                )

        if "Title:" not in output:
            log_warn(f"AI output missing Title line. First 200 chars: {preview!r}")
            raise AIRuntimeError(
                "AI output missing Title line. Refusing to write page.fountain."
            )

        lines = output.splitlines()
        has_scene_heading = any(
            line.startswith("INT.") or line.startswith("EXT.") for line in lines
        )
        if not has_scene_heading:
            log_warn(
                f"AI output missing scene heading. First 200 chars: {preview!r}"
            )
            raise AIRuntimeError(
                "AI output missing scene heading (INT./EXT.). "
                "Refusing to write page.fountain."
            )

        blocks = [b for b in output.split("\n\n") if b.strip()]
        if len(blocks) < 2:
            log_warn(
                f"AI output has insufficient structure. First 200 chars: {preview!r}"
            )
            raise AIRuntimeError(
                "AI output has insufficient structure. Refusing to write page.fountain."
            )

    def generate(self, page_dir: Path, edition_name: str = "") -> None:
        """Generate a Fountain screenplay from the page artwork."""
        image_path = page_dir / "page.png"
        fountain_path = page_dir / "page.fountain"
        build_state_path = page_dir / ".build_state.json"

        if not image_path.exists():
            return

        self.ensure_model()
        log_info("Generating fountain script from artwork…")

        prompt = _build_prompt(self._config.AUTHOR, edition_name)

        result = run(
            [
                self._config.FOUNTAIN_AI_RUNTIME,
                "run",
                self._config.FOUNTAIN_AI_MODEL,
                "--think",
                "false",
                "--hidethinking",
                str(image_path),
                prompt,
            ],
            capture_output=True,
            text=True,
        )
        self._validate_output(result.stdout)
        fountain_path.write_text(result.stdout)

        # Update .build_state.json with deterministic cache fields only.
        # --- Metadata boundary ---
        # .build_state.json  → deterministic fields only (hashes, model name).
        #                       Must NOT contain timestamps or other non-deterministic
        #                       data so that invalidation logic remains stable across runs.
        # meta.json          → publishable metadata (generated_at controlled by
        #                       --reproducible flag).
        current_hash = hash_file(image_path)
        build_state: dict = {}
        if build_state_path.exists():
            try:
                build_state = json.loads(build_state_path.read_text())
            except Exception:  # noqa: BLE001
                build_state = {}

        build_state["image_hash"] = current_hash
        build_state["fountain_generated_by"] = self._config.FOUNTAIN_AI_MODEL
        build_state_path.write_text(json.dumps(build_state, indent=2))

        log_success("Fountain script generated.")
