"""GitHub API client for fetching developer statistics."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from profile_engine.models.developer import DeveloperStats


class GitHubClient:
    """Client for fetching GitHub developer statistics."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, uses GITHUB_TOKEN env var.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
    
    def fetch_developer_stats(self, username: str, output_path: Optional[Path] = None) -> DeveloperStats:
        """
        Fetch developer statistics for a GitHub user.
        
        Args:
            username: GitHub username
            output_path: Optional path to save JSON output
            
        Returns:
            DeveloperStats model with user statistics
            
        Note:
            Current implementation uses subprocess to call legacy script.
            Future: Replace with direct GitHub API calls using httpx for:
            - Better performance (no subprocess overhead)
            - Proper async support
            - Better error handling
            - Easier testing (mock HTTP instead of subprocess)
        """
        # TODO: Replace subprocess wrapper with direct HTTP implementation
        # Example: async with httpx.AsyncClient() as client:
        #             response = await client.get(f"https://api.github.com/users/{username}")
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fetch-developer-stats.py"
        
        if output_path is None:
            output_path = Path("developer") / "stats.json"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set environment if token provided
        env = os.environ.copy()
        if self.token:
            env["GITHUB_TOKEN"] = self.token
        
        # Run the existing script
        result = subprocess.run(
            [sys.executable, str(script_path), username, str(output_path)],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch developer stats: {result.stderr}")
        
        # Load and validate the output
        with open(output_path, "r") as f:
            data = json.load(f)
        
        # Convert to Pydantic model for validation
        # Note: The model may not match exactly yet, so we'll be flexible
        return DeveloperStats(**data)
