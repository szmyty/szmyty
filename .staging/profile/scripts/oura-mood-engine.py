#!/usr/bin/env python3
"""
Oura Mood Engine - Compute mood classification from Oura Ring metrics.
This script reads normalized Oura metrics from JSON and computes a mood state
based on sleep, readiness, activity, HRV, resting HR, and temperature deviation.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

from lib.utils import safe_get, load_json


# Mood definitions with thresholds and visual attributes
MOOD_CATEGORIES = {
    "cosmic_clarity": {
        "name": "Cosmic Clarity",
        "icon": "✨",
        "gradient": ["#667eea", "#764ba2"],
        "description": "Peak mental clarity and physical readiness",
    },
    "solar_focus": {
        "name": "Solar Focus",
        "icon": "🔥",
        "gradient": ["#f093fb", "#f5576c"],
        "description": "High energy and sharp focus",
    },
    "restorative_drift": {
        "name": "Restorative Drift",
        "icon": "🌙",
        "gradient": ["#4facfe", "#00f2fe"],
        "description": "Body in recovery mode",
    },
    "quiet_neutrality": {
        "name": "Quiet Neutrality",
        "icon": "☁️",
        "gradient": ["#a8c0ff", "#3f2b96"],
        "description": "Balanced, steady state",
    },
    "chaotic_overdrive": {
        "name": "Chaotic Overdrive",
        "icon": "🌪️",
        "gradient": ["#ff6b6b", "#feca57"],
        "description": "High activity, body under stress",
    },
    "storm_state": {
        "name": "Storm State",
        "icon": "⛈️",
        "gradient": ["#2c3e50", "#4ca1af"],
        "description": "Recovery needed, challenging metrics",
    },
    "energetic_compression": {
        "name": "Energetic Compression",
        "icon": "⚡",
        "gradient": ["#11998e", "#38ef7d"],
        "description": "Building energy, readying for action",
    },
}


def normalize_score(value: Any, min_val: float = 0, max_val: float = 100) -> float:
    """Normalize a value to 0-100 scale."""
    if value is None:
        return 50.0  # Return neutral if no data
    try:
        v = float(value)
        # Clamp to range
        return max(min_val, min(max_val, v))
    except (ValueError, TypeError):
        return 50.0


def compute_mood_score(metrics: Dict[str, Any]) -> float:
    """
    Compute overall mood score from 0-100 based on metrics.
    Higher score = better overall state.
    """
    sleep_score = normalize_score(metrics.get("sleep_score"))
    readiness_score = normalize_score(metrics.get("readiness_score"))
    activity_score = normalize_score(metrics.get("activity_score"))
    hrv = normalize_score(metrics.get("hrv"))
    resting_hr = normalize_score(metrics.get("resting_hr"))
    temp_deviation = normalize_score(metrics.get("temp_deviation"))

    # Weighted average - sleep and readiness are most important
    # For resting HR, lower is generally better (invert the contribution)
    score = (
        sleep_score * 0.30
        + readiness_score * 0.30
        + activity_score * 0.15
        + hrv * 0.10
        + (100 - resting_hr) * 0.05  # Lower HR is better
        + temp_deviation * 0.10
    )

    return round(max(0, min(100, score)), 1)


def classify_mood(metrics: dict) -> str:
    """
    Classify mood category based on metrics patterns.
    Returns the mood category key.
    """
    sleep_score = normalize_score(metrics.get("sleep_score"))
    readiness_score = normalize_score(metrics.get("readiness_score"))
    activity_score = normalize_score(metrics.get("activity_score"))
    hrv = normalize_score(metrics.get("hrv"))
    temp_deviation = normalize_score(metrics.get("temp_deviation"))

    # Decision tree for mood classification
    # Cosmic Clarity: All metrics excellent
    if sleep_score >= 80 and readiness_score >= 80 and hrv >= 70:
        return "cosmic_clarity"

    # Solar Focus: High readiness and good activity
    if readiness_score >= 75 and activity_score >= 70:
        return "solar_focus"

    # Restorative Drift: High sleep, moderate everything else
    if sleep_score >= 75 and readiness_score < 70 and activity_score < 60:
        return "restorative_drift"

    # Chaotic Overdrive: High activity but poor recovery
    if activity_score >= 80 and (readiness_score < 60 or sleep_score < 60):
        return "chaotic_overdrive"

    # Storm State: Poor metrics across the board
    if sleep_score < 50 or readiness_score < 50:
        return "storm_state"

    # Energetic Compression: Good sleep, building energy
    if sleep_score >= 70 and readiness_score >= 60 and activity_score < 70:
        return "energetic_compression"

    # Default to Quiet Neutrality
    return "quiet_neutrality"


def interpret_metrics(metrics: dict) -> dict:
    """
    Create human-readable interpretations of key metrics.
    """
    interpretations = {}

    # Sleep interpretation
    sleep = normalize_score(metrics.get("sleep_score"))
    if sleep >= 85:
        interpretations["sleep"] = "Excellent rest"
    elif sleep >= 70:
        interpretations["sleep"] = "Good sleep"
    elif sleep >= 50:
        interpretations["sleep"] = "Moderate sleep"
    else:
        interpretations["sleep"] = "Poor rest"

    # Readiness interpretation
    readiness = normalize_score(metrics.get("readiness_score"))
    if readiness >= 85:
        interpretations["readiness"] = "Peak performance ready"
    elif readiness >= 70:
        interpretations["readiness"] = "Good to go"
    elif readiness >= 50:
        interpretations["readiness"] = "Take it easy"
    else:
        interpretations["readiness"] = "Recovery needed"

    # Activity interpretation
    activity = normalize_score(metrics.get("activity_score"))
    if activity >= 85:
        interpretations["activity"] = "Highly active"
    elif activity >= 70:
        interpretations["activity"] = "Active day"
    elif activity >= 50:
        interpretations["activity"] = "Moderate movement"
    else:
        interpretations["activity"] = "Low activity"

    # HRV interpretation
    hrv = normalize_score(metrics.get("hrv"))
    if hrv >= 80:
        interpretations["hrv"] = "Excellent variability"
    elif hrv >= 60:
        interpretations["hrv"] = "Good variability"
    elif hrv >= 40:
        interpretations["hrv"] = "Moderate variability"
    else:
        interpretations["hrv"] = "Low variability"

    return interpretations


def compute_mood(metrics: dict) -> dict:
    """
    Main function to compute full mood state from metrics.
    Returns mood object with all required fields.
    """
    # Compute overall score
    mood_score = compute_mood_score(metrics)

    # Classify mood category
    mood_key = classify_mood(metrics)
    mood_info = MOOD_CATEGORIES[mood_key]

    # Get interpretations
    interpreted = interpret_metrics(metrics)

    # Build output
    return {
        "mood_name": mood_info["name"],
        "mood_score": mood_score,
        "mood_icon": mood_info["icon"],
        "mood_color_gradient": mood_info["gradient"],
        "mood_description": mood_info["description"],
        "mood_key": mood_key,
        "interpreted_metrics": interpreted,
        "raw_scores": {
            "sleep_score": metrics.get("sleep_score"),
            "readiness_score": metrics.get("readiness_score"),
            "activity_score": metrics.get("activity_score"),
            "hrv": metrics.get("hrv"),
            "resting_hr": metrics.get("resting_hr"),
            "temp_deviation": metrics.get("temp_deviation"),
        },
        "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: oura-mood-engine.py <metrics.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metrics_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "oura/mood.json"

    # Read metrics
    metrics = load_json(metrics_path, "Metrics file")

    # Compute mood
    mood = compute_mood(metrics)

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(mood, f, indent=2)

    print(f"Generated mood state: {output_path}", file=sys.stderr)
    print(f"Mood: {mood['mood_name']} ({mood['mood_icon']}) - Score: {mood['mood_score']}", file=sys.stderr)


if __name__ == "__main__":
    main()
