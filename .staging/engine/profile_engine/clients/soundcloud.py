"""SoundCloud API client for fetching track data."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from profile_engine.models.soundcloud import SoundCloudTrack


class SoundCloudClient:
    """Client for fetching SoundCloud track data."""
    
    def __init__(self):
        """Initialize SoundCloud client."""
        pass
    
    def fetch_track(self, username: str, output_path: Optional[Path] = None) -> SoundCloudTrack:
        """
        Fetch SoundCloud track data for a user.
        
        Args:
            username: SoundCloud username
            output_path: Optional path to save JSON output
            
        Returns:
            SoundCloudTrack model with track data
        """
        # For now, use the existing script as a wrapper
        # TODO: Refactor to use httpx directly
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fetch-soundcloud.sh"
        
        if output_path is None:
            output_path = Path("assets") / "metadata.json"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run the existing script with username
        result = subprocess.run(
            [str(script_path), username],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch SoundCloud data: {result.stderr}")
        
        # Load and validate the output
        if output_path.exists():
            with open(output_path, "r") as f:
                data = json.load(f)
            return SoundCloudTrack(**data)
        
        raise RuntimeError("SoundCloud metadata file not created")
