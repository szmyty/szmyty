"""
Card generator service for creating SVG cards.

This service wraps the existing card generation scripts until they can be
fully refactored into the engine package.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CardGenerator:
    """Service for generating SVG cards from data."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize card generator.
        
        Args:
            repo_root: Root directory of the repository. If None, auto-detects.
        """
        if repo_root is None:
            # Auto-detect repo root (4 levels up from this file)
            self.repo_root = Path(__file__).parent.parent.parent.parent
        else:
            self.repo_root = repo_root
        
        self.scripts_dir = self.repo_root / "scripts"
    
    def _run_generator_script(
        self,
        script_name: str,
        input_path: Path,
        output_path: Path,
        theme_path: Optional[Path] = None
    ) -> None:
        """
        Run a generator script.
        
        Args:
            script_name: Name of the script file
            input_path: Input JSON file
            output_path: Output SVG file
            theme_path: Optional theme configuration file
        """
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            raise FileNotFoundError(f"Generator script not found: {script_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path), str(input_path), str(output_path)],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Generator script failed: {result.stderr}\n{result.stdout}"
            )
        
        logger.info(f"Generated: {output_path}")
    
    def generate_weather_card(
        self,
        input_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        theme_path: Optional[Path] = None
    ) -> Path:
        """Generate weather card SVG."""
        input_path = input_path or Path("weather/weather.json")
        output_path = output_path or Path("weather/weather-today.svg")
        
        logger.info(f"Generating weather card from {input_path}")
        self._run_generator_script(
            "generate-weather-card.py",
            input_path,
            output_path,
            theme_path
        )
        return output_path
    
    def generate_developer_dashboard(
        self,
        input_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        theme_path: Optional[Path] = None
    ) -> Path:
        """Generate developer dashboard SVG."""
        input_path = input_path or Path("developer/stats.json")
        output_path = output_path or Path("developer/developer_dashboard.svg")
        
        logger.info(f"Generating developer dashboard from {input_path}")
        self._run_generator_script(
            "generate-developer-dashboard.py",
            input_path,
            output_path,
            theme_path
        )
        return output_path
    
    def generate_oura_dashboard(
        self,
        input_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        theme_path: Optional[Path] = None
    ) -> Path:
        """Generate Oura health dashboard SVG."""
        input_path = input_path or Path("oura/metrics.json")
        output_path = output_path or Path("oura/health_dashboard.svg")
        
        logger.info(f"Generating Oura dashboard from {input_path}")
        self._run_generator_script(
            "generate-health-dashboard.py",
            input_path,
            output_path,
            theme_path
        )
        return output_path
    
    def generate_oura_mood(
        self,
        input_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        theme_path: Optional[Path] = None
    ) -> Path:
        """Generate Oura mood dashboard SVG."""
        input_path = input_path or Path("oura/mood.json")
        output_path = output_path or Path("oura/mood_dashboard.svg")
        
        logger.info(f"Generating Oura mood dashboard from {input_path}")
        self._run_generator_script(
            "generate-oura-mood-card.py",
            input_path,
            output_path,
            theme_path
        )
        return output_path
    
    def generate_quote_card(
        self,
        input_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        theme_path: Optional[Path] = None
    ) -> Path:
        """Generate quote card SVG."""
        input_path = input_path or Path("quotes/quote.json")
        output_path = output_path or Path("quotes/quote_card.svg")
        
        logger.info(f"Generating quote card from {input_path}")
        self._run_generator_script(
            "generate_quote_card.py",
            input_path,
            output_path,
            theme_path
        )
        return output_path
