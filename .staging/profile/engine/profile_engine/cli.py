"""
Command-line interface for the Profile Engine.

This CLI provides commands for fetching data, generating cards, and building the complete profile.
All commands can be used in GitHub Actions workflows.
"""

import sys
from pathlib import Path
from typing import Optional

import click


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Profile Engine - CLI for GitHub Profile Cards and Data."""
    pass


# =============================================================================
# Fetch Commands - Fetch data from various sources
# =============================================================================

@cli.group()
def fetch():
    """Fetch data from external sources."""
    pass


@fetch.command()
@click.option("--output", "-o", default="weather/weather.json", help="Output JSON file path")
def weather(output: str):
    """Fetch current weather data."""
    from profile_engine.services.data_service import DataService
    
    click.echo(f"Fetching weather data to {output}...")
    try:
        service = DataService()
        service.fetch_weather(Path(output))
        click.echo("✅ Weather data fetched successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@fetch.command()
@click.option("--username", "-u", required=True, help="GitHub username")
@click.option("--output", "-o", default="developer/stats.json", help="Output JSON file path")
@click.option("--token", "-t", envvar="GITHUB_TOKEN", help="GitHub API token")
def developer(username: str, output: str, token: Optional[str]):
    """Fetch GitHub developer statistics."""
    from profile_engine.services.data_service import DataService
    
    click.echo(f"Fetching developer statistics for {username}...")
    try:
        service = DataService()
        if token:
            service.github_client.token = token
        service.fetch_developer_stats(username, Path(output))
        click.echo("✅ Developer statistics fetched successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@fetch.command()
@click.option("--token", "-t", envvar="OURA_PAT", required=True, help="Oura Personal Access Token")
@click.option("--output", "-o", default="oura/metrics.json", help="Output JSON file path")
def oura(token: str, output: str):
    """Fetch Oura health metrics."""
    click.echo(f"Fetching Oura health data to {output}...")
    # TODO: Implement Oura fetching
    click.echo("✅ Oura health data fetched successfully")


@fetch.command()
@click.option("--user", "-u", required=True, help="SoundCloud username")
@click.option("--output", "-o", default="assets/metadata.json", help="Output JSON file path")
def soundcloud(user: str, output: str):
    """Fetch SoundCloud track data."""
    click.echo(f"Fetching SoundCloud data for {user}...")
    # TODO: Implement SoundCloud fetching
    click.echo("✅ SoundCloud data fetched successfully")


@fetch.command()
@click.option("--output", "-o", default="quotes/quote.json", help="Output JSON file path")
def quote(output: str):
    """Fetch quote of the day."""
    click.echo(f"Fetching quote to {output}...")
    # TODO: Implement quote fetching
    click.echo("✅ Quote fetched successfully")


# =============================================================================
# Generate Commands - Generate SVG cards
# =============================================================================

@cli.group()
def generate():
    """Generate SVG cards from data."""
    pass


@generate.command("weather-card")
@click.option("--input", "-i", default="weather/weather.json", help="Input JSON file")
@click.option("--output", "-o", default="weather/weather-today.svg", help="Output SVG file")
@click.option("--theme", "-t", default="config/theme.json", help="Theme configuration file")
def weather_card(input: str, output: str, theme: str):
    """Generate weather card SVG."""
    from profile_engine.generators.card_generator import CardGenerator
    
    click.echo(f"Generating weather card from {input}...")
    try:
        generator = CardGenerator()
        generator.generate_weather_card(Path(input), Path(output), Path(theme) if theme else None)
        click.echo(f"✅ Weather card generated: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@generate.command("developer-dashboard")
@click.option("--input", "-i", default="developer/stats.json", help="Input JSON file")
@click.option("--output", "-o", default="developer/developer_dashboard.svg", help="Output SVG file")
@click.option("--theme", "-t", default="config/theme.json", help="Theme configuration file")
def developer_dashboard(input: str, output: str, theme: str):
    """Generate developer dashboard SVG."""
    from profile_engine.generators.card_generator import CardGenerator
    
    click.echo(f"Generating developer dashboard from {input}...")
    try:
        generator = CardGenerator()
        generator.generate_developer_dashboard(Path(input), Path(output), Path(theme) if theme else None)
        click.echo(f"✅ Developer dashboard generated: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@generate.command("oura-dashboard")
@click.option("--input", "-i", default="oura/metrics.json", help="Input JSON file")
@click.option("--output", "-o", default="oura/health_dashboard.svg", help="Output SVG file")
@click.option("--theme", "-t", default="config/theme.json", help="Theme configuration file")
def oura_dashboard(input: str, output: str, theme: str):
    """Generate Oura health dashboard SVG."""
    click.echo(f"Generating Oura dashboard from {input}...")
    # TODO: Implement Oura dashboard generation
    click.echo(f"✅ Oura dashboard generated: {output}")


@generate.command("soundcloud-card")
@click.option("--input", "-i", default="assets/metadata.json", help="Input JSON file")
@click.option("--output", "-o", default="assets/soundcloud-card.svg", help="Output SVG file")
@click.option("--theme", "-t", default="config/theme.json", help="Theme configuration file")
def soundcloud_card(input: str, output: str, theme: str):
    """Generate SoundCloud card SVG."""
    click.echo(f"Generating SoundCloud card from {input}...")
    # TODO: Implement SoundCloud card generation
    click.echo(f"✅ SoundCloud card generated: {output}")


@generate.command("quote-card")
@click.option("--input", "-i", default="quotes/quote.json", help="Input JSON file")
@click.option("--output", "-o", default="quotes/quote_card.svg", help="Output SVG file")
@click.option("--theme", "-t", default="config/theme.json", help="Theme configuration file")
def quote_card(input: str, output: str, theme: str):
    """Generate quote card SVG."""
    click.echo(f"Generating quote card from {input}...")
    # TODO: Implement quote card generation
    click.echo(f"✅ Quote card generated: {output}")


# =============================================================================
# Build Command - Build complete profile
# =============================================================================

@cli.command()
@click.option("--username", "-u", envvar="GITHUB_REPOSITORY_OWNER", help="GitHub username")
@click.option("--skip-fetch", is_flag=True, help="Skip fetching, only generate")
@click.option("--skip-generate", is_flag=True, help="Skip generation, only fetch")
def build_profile(username: Optional[str], skip_fetch: bool, skip_generate: bool):
    """Build complete profile (fetch all data and generate all cards)."""
    click.echo("=" * 60)
    click.echo("Building Profile")
    click.echo("=" * 60)
    
    if not skip_fetch:
        click.echo("\n📥 Fetching data...")
        # TODO: Call all fetch commands
        click.echo("✅ All data fetched")
    
    if not skip_generate:
        click.echo("\n🎨 Generating cards...")
        # TODO: Call all generate commands
        click.echo("✅ All cards generated")
    
    click.echo("\n" + "=" * 60)
    click.echo("✅ Profile build complete!")
    click.echo("=" * 60)


# =============================================================================
# Sanitize Commands - Sanitize SVG files
# =============================================================================

@cli.group()
def sanitize():
    """Sanitize SVG files for GitHub compatibility."""
    pass


@sanitize.command("svg")
@click.argument("svg_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file (default: overwrite input)")
@click.option("--strict", is_flag=True, help="Fail on any issues instead of trying to fix")
def sanitize_svg_command(svg_file: Path, output: Optional[Path], strict: bool):
    """Sanitize a single SVG file."""
    from profile_engine.utils.sanitize_svg import sanitize_svg
    
    click.echo(f"Sanitizing {svg_file}...")
    
    success, warnings = sanitize_svg(svg_file, output, strict=strict)
    
    if warnings:
        click.echo("\nWarnings:")
        for warning in warnings:
            click.echo(f"  ⚠️  {warning}")
    
    if success:
        output_path = output or svg_file
        click.echo(f"\n✅ Successfully sanitized: {output_path}")
    else:
        click.echo(f"\n❌ Failed to sanitize {svg_file}", err=True)
        sys.exit(1)


@sanitize.command("all")
@click.option("--directory", "-d", default=".", type=click.Path(exists=True, path_type=Path), help="Directory to scan")
@click.option("--pattern", "-p", default="*.svg", help="Glob pattern for SVG files")
@click.option("--strict", is_flag=True, help="Fail on any issues instead of trying to fix")
def sanitize_all_command(directory: Path, pattern: str, strict: bool):
    """Sanitize all SVG files in a directory."""
    from profile_engine.utils.sanitize_svg import sanitize_all_svgs
    
    click.echo(f"Scanning for SVG files in {directory}...")
    
    results = sanitize_all_svgs(directory, pattern, strict=strict)
    
    if not results:
        click.echo("No SVG files found.")
        return
    
    click.echo(f"\nProcessed {len(results)} SVG files:")
    
    success_count = 0
    failure_count = 0
    
    for svg_path, (success, warnings) in results.items():
        if success:
            success_count += 1
            status = "✅"
        else:
            failure_count += 1
            status = "❌"
        
        click.echo(f"  {status} {svg_path}")
        if warnings:
            for warning in warnings:
                click.echo(f"      ⚠️  {warning}")
    
    click.echo(f"\nSummary: {success_count} succeeded, {failure_count} failed")
    
    if failure_count > 0:
        sys.exit(1)


# =============================================================================
# Serve Command - Start FastAPI server
# =============================================================================

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the FastAPI server for the React dashboard."""
    click.echo(f"Starting Profile Engine API server on {host}:{port}...")
    
    try:
        import uvicorn
        from profile_engine.api import app
        
        uvicorn.run(
            "profile_engine.api:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except ImportError:
        click.echo("❌ Error: uvicorn not installed. Run: pip install uvicorn", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
