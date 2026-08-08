"""Quote API client for fetching daily quotes."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from profile_engine.models.quote import Quote


class QuoteClient:
    """Client for fetching quote of the day."""
    
    def __init__(self):
        """Initialize Quote client."""
        pass
    
    def fetch_quote(self, output_path: Optional[Path] = None) -> Quote:
        """
        Fetch quote of the day.
        
        Args:
            output_path: Optional path to save JSON output
            
        Returns:
            Quote model with daily quote
        """
        # For now, use the existing script as a wrapper
        # TODO: Refactor to use httpx directly
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fetch_quote.sh"
        
        if output_path is None:
            output_path = Path("quotes") / "quote.json"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run the existing script
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch quote: {result.stderr}")
        
        # Load and validate the output
        if output_path.exists():
            with open(output_path, "r") as f:
                data = json.load(f)
            return Quote(**data)
        
        raise RuntimeError("Quote file not created")
