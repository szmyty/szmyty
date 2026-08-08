#!/usr/bin/env python3
"""
Generate unified health snapshot from Oura Ring metrics.
This script reads raw Oura metrics from JSON and creates a normalized health_snapshot.json.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from lib.utils import safe_get, load_and_validate_json


def calculate_bmi(weight_kg: Optional[float], height_m: Optional[float]) -> Optional[float]:
    """Calculate BMI from weight (kg) and height (m)."""
    if weight_kg is None or height_m is None or height_m == 0:
        return None
    return round(weight_kg / (height_m * height_m), 1)


def meters_to_cm(height_m: Optional[float]) -> Optional[float]:
    """Convert meters to centimeters."""
    if height_m is None:
        return None
    return round(height_m * 100, 1)


def kg_to_lbs(weight_kg: Optional[float]) -> Optional[float]:
    """Convert kilograms to pounds."""
    if weight_kg is None:
        return None
    return round(weight_kg * 2.20462, 1)


def generate_health_snapshot(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a unified health snapshot from raw Oura metrics.
    """
    # Extract personal info (excluding private identifiers: email, id, biological_sex)
    personal_info = metrics.get("personal_info", {})
    
    height_m = safe_get(personal_info, "height")
    weight_kg = safe_get(personal_info, "weight")
    age = safe_get(personal_info, "age")
    
    # Calculate derived values
    bmi = calculate_bmi(weight_kg, height_m)
    height_cm = meters_to_cm(height_m)
    weight_lbs = kg_to_lbs(weight_kg)
    
    # Extract sleep data
    sleep_data = metrics.get("sleep", {})
    sleep_contributors = safe_get(sleep_data, "contributors", default={})
    
    # Extract readiness data  
    readiness_data = metrics.get("readiness", {})
    readiness_contributors = safe_get(readiness_data, "contributors", default={})
    
    # Extract activity data
    activity_data = metrics.get("activity", {})
    activity_contributors = safe_get(activity_data, "contributors", default={})
    
    # Extract heart rate data
    heart_rate_data = metrics.get("heart_rate", {})
    hr_trend_values = safe_get(heart_rate_data, "trend_values", default=[])
    
    # Build unified snapshot (excluding private identifiers: email, id, sex)
    snapshot = {
        "personal": {
            "age": age,
            "height_m": height_m,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "weight_lbs": weight_lbs,
            "bmi": bmi,
        },
        "sleep": {
            "score": safe_get(sleep_data, "score"),
            "day": safe_get(sleep_data, "day"),
            "deep_sleep": safe_get(sleep_contributors, "deep_sleep"),
            "rem_sleep": safe_get(sleep_contributors, "rem_sleep"),
            "total_sleep": safe_get(sleep_contributors, "total_sleep"),
            "efficiency": safe_get(sleep_contributors, "efficiency"),
            "latency": safe_get(sleep_contributors, "latency"),
            "restfulness": safe_get(sleep_contributors, "restfulness"),
            "timing": safe_get(sleep_contributors, "timing"),
        },
        "readiness": {
            "score": safe_get(readiness_data, "score"),
            "day": safe_get(readiness_data, "day"),
            "recovery_index": safe_get(readiness_contributors, "recovery_index"),
            "hrv_balance": safe_get(readiness_contributors, "hrv_balance"),
            "resting_heart_rate": safe_get(readiness_contributors, "resting_heart_rate"),
            "body_temperature": safe_get(readiness_contributors, "body_temperature"),
            "temperature_deviation": safe_get(readiness_data, "temperature_deviation"),
            "temperature_trend_deviation": safe_get(readiness_data, "temperature_trend_deviation"),
            "activity_balance": safe_get(readiness_contributors, "activity_balance"),
            "sleep_balance": safe_get(readiness_contributors, "sleep_balance"),
            "previous_day_activity": safe_get(readiness_contributors, "previous_day_activity"),
            "previous_night": safe_get(readiness_contributors, "previous_night"),
            "sleep_regularity": safe_get(readiness_contributors, "sleep_regularity"),
        },
        "activity": {
            "score": safe_get(activity_data, "score"),
            "day": safe_get(activity_data, "day"),
            "steps": safe_get(activity_data, "steps"),
            "active_calories": safe_get(activity_data, "active_calories"),
            "total_calories": safe_get(activity_data, "total_calories"),
            "target_calories": safe_get(activity_data, "target_calories"),
            "equivalent_walking_distance": safe_get(activity_data, "equivalent_walking_distance"),
            "target_meters": safe_get(activity_data, "target_meters"),
            "inactivity_alerts": safe_get(activity_data, "inactivity_alerts"),
            "low_activity_time": safe_get(activity_data, "low_activity_time"),
            "medium_activity_time": safe_get(activity_data, "medium_activity_time"),
            "high_activity_time": safe_get(activity_data, "high_activity_time"),
            "average_met_minutes": safe_get(activity_data, "average_met_minutes"),
            "meet_daily_targets": safe_get(activity_contributors, "meet_daily_targets"),
            "move_every_hour": safe_get(activity_contributors, "move_every_hour"),
            "recovery_time": safe_get(activity_contributors, "recovery_time"),
            "stay_active": safe_get(activity_contributors, "stay_active"),
            "training_frequency": safe_get(activity_contributors, "training_frequency"),
            "training_volume": safe_get(activity_contributors, "training_volume"),
        },
        "heart_rate": {
            "latest_bpm": safe_get(heart_rate_data, "latest_bpm"),
            "avg_bpm": safe_get(heart_rate_data, "avg_bpm"),
            "resting_bpm": safe_get(heart_rate_data, "resting_bpm"),
            "trend_values": hr_trend_values if hr_trend_values else [],
        },
        "updated_at": metrics.get("updated_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
    }
    
    return snapshot


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-health-snapshot.py <metrics.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metrics_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "oura/health_snapshot.json"

    # Read and validate metrics
    metrics = load_and_validate_json(
        metrics_path, "oura-metrics", "Oura metrics file"
    )

    # Generate health snapshot
    snapshot = generate_health_snapshot(metrics)

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Generated health snapshot: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
