"""Tests for Profile Engine CLI."""

import subprocess
import sys


def test_cli_help():
    """Test that CLI help command works."""
    result = subprocess.run(
        ["profile-engine", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Profile Engine" in result.stdout
    assert "fetch" in result.stdout
    assert "generate" in result.stdout


def test_cli_version():
    """Test that CLI version command works."""
    result = subprocess.run(
        ["profile-engine", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Just verify version output exists, don't hardcode version number
    assert "profile-engine" in result.stdout or "version" in result.stdout.lower()


def test_fetch_help():
    """Test that fetch help command works."""
    result = subprocess.run(
        ["profile-engine", "fetch", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Fetch data from external sources" in result.stdout
    assert "developer" in result.stdout
    assert "weather" in result.stdout


def test_generate_help():
    """Test that generate help command works."""
    result = subprocess.run(
        ["profile-engine", "generate", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Generate SVG cards" in result.stdout
    assert "weather-card" in result.stdout
    assert "developer-dashboard" in result.stdout


def test_build_profile_dry_run():
    """Test that build-profile command works in dry run mode."""
    result = subprocess.run(
        ["profile-engine", "build-profile", "--skip-fetch", "--skip-generate"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Building Profile" in result.stdout
    assert "Profile build complete" in result.stdout
