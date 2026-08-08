from __future__ import annotations

from pathlib import Path

import click
import structlog

from mindlint.ai import AIProvider, AnthropicProvider, OllamaProvider, OpenAIProvider
from mindlint.config.defaults import DEFAULT_OLLAMA_MODEL
from mindlint.core.logging import configure_logging
from mindlint.core.reporter import RichReporter
from mindlint.core.runner import LintRunner
from mindlint.models.issue import Severity

log = structlog.get_logger(__name__)


@click.command()
@click.argument(
    "path",
    default=".",
    required=False,
    type=click.Path(path_type=Path),
)
@click.option("--ai", "enable_ai", is_flag=True, help="Enable qualitative AI checks.")
@click.option(
    "--ai-provider",
    type=click.Choice(["ollama", "openai", "anthropic"]),
    default="ollama",
    show_default=True,
    help="AI provider to use when --ai is enabled.",
)
@click.option(
    "--ollama-model",
    default=DEFAULT_OLLAMA_MODEL,
    show_default=True,
    help="Ollama model to use when --ai-provider=ollama.",
)
@click.option(
    "--fail-on",
    type=click.Choice(["info", "warning", "error"]),
    default="error",
    show_default=True,
    help="Lowest issue severity that should return a non-zero exit code.",
)
@click.option("--debug", is_flag=True, help="Enable structured debug logging.")
def main(
    path: Path,
    enable_ai: bool,
    ai_provider: str,
    ollama_model: str,
    fail_on: Severity,
    debug: bool,
) -> None:
    configure_logging(debug=debug)
    target = path.resolve()
    log.debug(
        "cli.start",
        target=str(target),
        enable_ai=enable_ai,
        ai_provider=ai_provider,
        ollama_model=ollama_model,
        fail_on=fail_on,
        debug=debug,
    )

    if not target.exists():
        log.debug("cli.target_missing", target=str(target))
        raise click.ClickException(f"Path does not exist: {target}")

    provider = _build_ai_provider(ai_provider, ollama_model) if enable_ai else None
    runner = LintRunner(ai_provider=provider)
    result = runner.run_path(target)
    RichReporter().report(result)
    exit_code = result.exit_code(fail_on)
    log.debug("cli.complete", exit_code=exit_code, issue_count=len(result.issues))
    raise SystemExit(exit_code)


def _build_ai_provider(provider_name: str, ollama_model: str) -> AIProvider:
    if provider_name == "ollama":
        log.debug("cli.ai_provider_selected", provider=provider_name, model=ollama_model)
        return OllamaProvider(model=ollama_model)
    if provider_name == "openai":
        log.debug("cli.ai_provider_selected", provider=provider_name)
        return OpenAIProvider()
    if provider_name == "anthropic":
        log.debug("cli.ai_provider_selected", provider=provider_name)
        return AnthropicProvider()

    raise click.ClickException(f"Unsupported AI provider: {provider_name}")
