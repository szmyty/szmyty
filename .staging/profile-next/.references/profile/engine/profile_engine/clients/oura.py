"""Oura API client for fetching health metrics."""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from profile_engine.models.oura import OuraHealthMetrics, OuraMood


class OuraClient:
    """Client for fetching Oura health data."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Oura client.
        
        Args:
            token: Oura Personal Access Token. If None, uses OURA_PAT env var.
        """
        self.token = token or os.environ.get("OURA_PAT")
    
    def fetch_health_metrics(self, output_path: Optional[Path] = None) -> OuraHealthMetrics:
        """
        Fetch Oura health metrics.
        
        Args:
            output_path: Optional path to save JSON output
            
        Returns:
            OuraHealthMetrics model with health data
        """
        # For now, use the existing script as a wrapper
        # TODO: Refactor to use httpx directly
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fetch-oura.sh"
        
        if output_path is None:
            output_path = Path("oura") / "metrics.json"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set environment if token provided
        env = os.environ.copy()
        if self.token:
            env["OURA_PAT"] = self.token
        
        # Run the existing script
        result = subprocess.run(
            [str(script_path)],
            env=env,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch Oura metrics: {result.stderr}")
        
        # Load and validate the output
        if output_path.exists():
            with open(output_path, "r") as f:
                data = json.load(f)
            return OuraHealthMetrics(**data)
        
        raise RuntimeError("Oura metrics file not created")
    
    def fetch_mood(self, output_path: Optional[Path] = None) -> OuraMood:
        """
        Fetch Oura mood data.
        
        Args:
            output_path: Optional path to save JSON output
            
        Returns:
            OuraMood model with mood data
        """
        if output_path is None:
            output_path = Path("oura") / "mood.json"
        
        # Load mood data if it exists
        if output_path.exists():
            with open(output_path, "r") as f:
                data = json.load(f)
            return OuraMood(**data)
        
        raise RuntimeError("Oura mood file not found")
