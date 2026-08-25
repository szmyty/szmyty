"""Render the Pages companion from reviewed public evidence.

The committed ``site/index.html`` is a deterministic build artifact. Stable
profile claims stay in ``profile/content/evidence.yml``; ``site.yml`` only
selects which verified records the companion presents.
"""

from __future__ import annotations

import difflib
from pathlib import Path
from urllib.parse import urlparse

import click
import jinja2
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tools.profile_builder.models import EvidenceEntry

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "profile" / "content" / "site.yml"
DEFAULT_EVIDENCE = REPO_ROOT / "profile" / "content" / "evidence.yml"
DEFAULT_TEMPLATE = REPO_ROOT / "profile" / "templates" / "site-index.html.j2"
DEFAULT_OUTPUT = REPO_ROOT / "site" / "index.html"


class SiteMetadata(BaseModel):
    """Stable deployment metadata for the companion site."""

    model_config = ConfigDict(extra="forbid")

    canonical_url: str
    source_url: str
    default_branch: str = Field(min_length=1, pattern=r"^[A-Za-z0-9._/-]+$")

    @field_validator("canonical_url", "source_url")
    @classmethod
    def _require_https(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("site URLs must be absolute HTTPS URLs")
        return value.rstrip("/") + ("/" if parsed.path.endswith("/") else "")

    @field_validator("canonical_url")
    @classmethod
    def _require_canonical_trailing_slash(cls, value: str) -> str:
        if not value.endswith("/"):
            raise ValueError("canonical_url must end with a slash")
        return value

    @field_validator("source_url")
    @classmethod
    def _require_github_source_repo(cls, value: str) -> str:
        parsed = urlparse(value)
        path_parts = [part for part in parsed.path.split("/") if part]
        if parsed.netloc != "github.com" or len(path_parts) != 2:
            raise ValueError("source_url must identify a GitHub repository")
        if parsed.query or parsed.fragment:
            raise ValueError("source_url must not include a query or fragment")
        return value


class SiteEvidenceRefs(BaseModel):
    """Evidence records required by the site template."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    positioning: str = Field(min_length=1)
    lanes: str = Field(min_length=1)
    ai_disclosure: str = Field(min_length=1)
    public_lab: str = Field(min_length=1)
    github: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    creative: str = Field(min_length=1)


class SelectedSystem(BaseModel):
    """Display label paired with a verified repository evidence record."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)


class SiteCompanionConfig(BaseModel):
    """Validated build configuration for ``site/index.html``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    site: SiteMetadata
    evidence: SiteEvidenceRefs
    selected_systems: list[SelectedSystem] = Field(min_length=1)

    @field_validator("schema_version")
    @classmethod
    def _require_supported_schema(cls, value: str) -> str:
        if value != "1":
            raise ValueError("unsupported site config schema_version")
        return value

    @model_validator(mode="after")
    def _require_unique_systems(self) -> SiteCompanionConfig:
        evidence_ids = [system.evidence_id for system in self.selected_systems]
        names = [system.name.casefold() for system in self.selected_systems]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("selected system evidence IDs must be unique")
        if len(names) != len(set(names)):
            raise ValueError("selected system names must be unique")
        return self


def load_config(path: Path = DEFAULT_CONFIG) -> SiteCompanionConfig:
    """Load and validate the site projection configuration."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("site config must contain a mapping")
    return SiteCompanionConfig.model_validate(raw)


def load_evidence(path: Path = DEFAULT_EVIDENCE) -> dict[str, EvidenceEntry]:
    """Load the evidence catalog keyed by stable record ID."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    records = raw.get("records", []) if isinstance(raw, dict) else []
    if not isinstance(records, list):
        raise ValueError("evidence catalog records must contain a list")

    entries = [EvidenceEntry.model_validate(record) for record in records]
    by_id = {entry.id: entry for entry in entries}
    if len(by_id) != len(entries):
        raise ValueError("evidence catalog record IDs must be unique")
    return by_id


def _resolve_record(
    evidence_id: str,
    catalog: dict[str, EvidenceEntry],
    *,
    require_url: bool = False,
) -> EvidenceEntry:
    try:
        entry = catalog[evidence_id]
    except KeyError as error:
        raise ValueError(f"unknown site evidence record: {evidence_id}") from error
    if entry.status != "verified" or entry.sensitivity != "public":
        raise ValueError(f"site evidence must be verified and public: {evidence_id}")
    if require_url and not entry.url:
        raise ValueError(f"site evidence must have a public URL: {evidence_id}")
    if require_url and urlparse(entry.url or "").scheme != "https":
        raise ValueError(f"site evidence URL must use HTTPS: {evidence_id}")
    return entry


def _system_description(name: str, entry: EvidenceEntry) -> str:
    """Remove the repository prefix from a catalog claim for card copy."""
    for separator in (" — ", " - "):
        prefix, found, description = entry.claim.partition(separator)
        if found and prefix.casefold().endswith(name.casefold()):
            return description[:1].upper() + description[1:]
    raise ValueError(f"system evidence {entry.id} must start with its repository name")


def build_context(
    config: SiteCompanionConfig,
    catalog: dict[str, EvidenceEntry],
) -> dict[str, object]:
    """Resolve a site config into an HTML template context."""
    refs = {
        key: _resolve_record(
            evidence_id,
            catalog,
            require_url=key in {"github", "contact", "creative", "public_lab"},
        )
        for key, evidence_id in config.evidence.model_dump().items()
    }

    systems = []
    for selected in config.selected_systems:
        entry = _resolve_record(selected.evidence_id, catalog, require_url=True)
        systems.append(
            {
                "name": selected.name,
                "description": _system_description(selected.name, entry),
                "url": entry.url,
                "evidence_id": entry.id,
            }
        )

    source_url = config.site.source_url.rstrip("/")
    page_title = f"{refs['name'].claim} — {refs['role'].claim.title()}"
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": refs["name"].claim,
        "url": config.site.canonical_url,
        "sameAs": [
            refs["github"].url,
            refs["public_lab"].url,
            refs["creative"].url,
        ],
        "jobTitle": refs["role"].claim,
        "description": refs["positioning"].claim,
    }
    return {
        "site": config.site,
        "profile": refs,
        "systems": systems,
        "page_title": page_title,
        "license_url": (f"{source_url}/blob/{config.site.default_branch}/LICENSE"),
        "structured_data": structured_data,
    }


def render_site(
    config_path: Path = DEFAULT_CONFIG,
    evidence_path: Path = DEFAULT_EVIDENCE,
    template_path: Path = DEFAULT_TEMPLATE,
) -> str:
    """Render the companion site deterministically from validated inputs."""
    config = load_config(config_path)
    catalog = load_evidence(evidence_path)
    context = build_context(config, catalog)
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_path.parent)),
        autoescape=jinja2.select_autoescape(
            enabled_extensions=("html", "xml"),
            default_for_string=True,
        ),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )
    return environment.get_template(template_path.name).render(**context)


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path, exists=True),
    default=DEFAULT_CONFIG,
    show_default=True,
)
@click.option(
    "--evidence",
    "evidence_path",
    type=click.Path(path_type=Path, exists=True),
    default=DEFAULT_EVIDENCE,
    show_default=True,
)
@click.option(
    "--template",
    "template_path",
    type=click.Path(path_type=Path, exists=True),
    default=DEFAULT_TEMPLATE,
    show_default=True,
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT,
    show_default=True,
)
@click.option(
    "--check",
    is_flag=True,
    help="Fail when the committed output differs from the rendered site.",
)
def main(
    config_path: Path,
    evidence_path: Path,
    template_path: Path,
    output_path: Path,
    check: bool,
) -> None:
    """Render or verify the static Pages companion."""
    rendered = render_site(config_path, evidence_path, template_path)
    if check:
        current = (
            output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        )
        if current != rendered:
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile=str(output_path),
                    tofile="rendered site",
                )
            )
            raise click.ClickException(
                "site/index.html is stale; regenerate it with "
                "python -m tools.modules.site_companion\n" + diff
            )
        click.echo("Site companion is current.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    click.echo(f"Rendered site companion: {output_path}")


if __name__ == "__main__":
    main()
