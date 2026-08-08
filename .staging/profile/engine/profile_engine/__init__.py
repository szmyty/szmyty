"""
Profile Engine - Unified package for GitHub profile cards.

This package provides:
- CLI tools for GitHub Actions
- FastAPI server for React dashboard
- Reusable clients, services, and generators
"""

__version__ = "1.0.0"
__author__ = "szmyty"

# Expose main components
from profile_engine.cli import cli
from profile_engine.api import app

__all__ = ["cli", "app", "__version__"]
