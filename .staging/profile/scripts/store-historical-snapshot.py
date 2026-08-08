#!/usr/bin/env python3
"""
Store historical snapshots for trend analysis.

This script creates and stores daily snapshots of health metrics that can be
used for historical visualizations and trend analysis.

The snapshots are stored in:
- data/snapshots/daily/YYYY/MM/YYYY-MM-DD.json
- data/snapshots/weekly/YYYY-WW.json (aggregated)
- data/snapshots/monthly/YYYY-MM.json (aggregated)

Usage:
    python store-historical-snapshot.py [--output-dir data/snapshots]
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import statistics

from lib.utils import (
    try_load_json,
    safe_get,
)


def load_current_health_data() -> Optional[Dict]:
    """Load current Oura health data."""
    data, error = try_load_json("oura/health_snapshot.json")
    return data


def load_mood_data() -> Optional[Dict]:
    """Load current mood data."""
    data, error = try_load_json("oura/mood.json")
    return data


def load_weather_data() -> Optional[Dict]:
    """Load current weather data."""
    data, error = try_load_json("weather/weather.json")
    return data


def load_developer_stats() -> Optional[Dict]:
    """Load current developer stats."""
    data, error = try_load_json("developer/stats.json")
    return data


def create_daily_snapshot() -> Dict:
    """Create a daily snapshot of all metrics."""
    now = datetime.now(timezone.utc)
    
    # Load all data sources
    health_data = load_current_health_data()
    mood_data = load_mood_data()
    weather_data = load_weather_data()
    dev_stats = load_developer_stats()
    
    snapshot = {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date": now.strftime("%Y-%m-%d"),
        "health": {},
        "mood": {},
        "weather": {},
        "developer": {},
    }
    
    # Extract health metrics
    if health_data:
        sleep = health_data.get("sleep", {})
        readiness = health_data.get("readiness", {})
        activity = health_data.get("activity", {})
        
        snapshot["health"] = {
            "sleep_score": sleep.get("score"),
            "sleep_total": sleep.get("total_sleep"),
            "sleep_deep": sleep.get("deep_sleep"),
            "sleep_rem": sleep.get("rem_sleep"),
            "sleep_efficiency": sleep.get("efficiency"),
            "readiness_score": readiness.get("score"),
            "readiness_hrv": readiness.get("hrv_balance"),
            "readiness_temp": readiness.get("temperature_deviation"),
            "resting_hr": readiness.get("resting_heart_rate"),
            "activity_score": activity.get("score"),
            "activity_steps": activity.get("steps"),
            "activity_calories": activity.get("active_calories"),
            "activity_met": activity.get("average_met_minutes"),
        }
    
    # Extract mood metrics
    if mood_data:
        snapshot["mood"] = {
            "mood_name": mood_data.get("mood_name"),
            "mood_score": mood_data.get("mood_score"),
            "mood_icon": mood_data.get("mood_icon"),
        }
    
    # Extract weather data
    if weather_data:
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})
        
        snapshot["weather"] = {
            "temperature": current.get("temperature"),
            "condition": current.get("condition"),
            "weathercode": current.get("weathercode"),
            "temp_max": daily.get("temperature_max"),
            "temp_min": daily.get("temperature_min"),
            "wind_speed": current.get("wind_speed"),
        }
    
    # Extract developer metrics
    if dev_stats:
        commit_activity = dev_stats.get("commit_activity", {})
        snapshot["developer"] = {
            "repos": dev_stats.get("repos"),
            "stars": dev_stats.get("stars"),
            "commits_30d": commit_activity.get("total_30_days"),
            "prs_opened": safe_get(dev_stats, "prs", "opened"),
            "prs_merged": safe_get(dev_stats, "prs", "merged"),
        }
    
    return snapshot


def save_snapshot(snapshot: Dict, output_dir: Path) -> None:
    """Save snapshot to appropriate files."""
    date = snapshot["date"]
    year, month, day = date.split("-")
    
    # Daily snapshot
    daily_dir = output_dir / "daily" / year / month
    daily_dir.mkdir(parents=True, exist_ok=True)
    daily_file = daily_dir / f"{date}.json"
    
    with open(daily_file, "w") as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"Saved daily snapshot: {daily_file}", file=sys.stderr)


def load_daily_snapshots(output_dir: Path, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Load all daily snapshots within a date range."""
    snapshots = []
    current = start_date
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        year, month, day = date_str.split("-")
        
        daily_file = output_dir / "daily" / year / month / f"{date_str}.json"
        if daily_file.exists():
            data, error = try_load_json(str(daily_file))
            if data:
                snapshots.append(data)
        
        current += timedelta(days=1)
    
    return snapshots


def aggregate_weekly_snapshot(snapshots: List[Dict]) -> Dict:
    """Aggregate daily snapshots into weekly summary."""
    if not snapshots:
        return {}
    
    # Extract values for aggregation
    sleep_scores = [s.get("health", {}).get("sleep_score") for s in snapshots if s.get("health", {}).get("sleep_score") is not None]
    readiness_scores = [s.get("health", {}).get("readiness_score") for s in snapshots if s.get("health", {}).get("readiness_score") is not None]
    activity_scores = [s.get("health", {}).get("activity_score") for s in snapshots if s.get("health", {}).get("activity_score") is not None]
    steps = [s.get("health", {}).get("activity_steps") for s in snapshots if s.get("health", {}).get("activity_steps") is not None]
    commits = [s.get("developer", {}).get("commits_30d") for s in snapshots if s.get("developer", {}).get("commits_30d") is not None]
    
    first_snapshot = snapshots[0]
    last_snapshot = snapshots[-1]
    
    return {
        "period": "weekly",
        "start_date": first_snapshot.get("date"),
        "end_date": last_snapshot.get("date"),
        "days_count": len(snapshots),
        "health": {
            "avg_sleep_score": round(statistics.mean(sleep_scores), 1) if sleep_scores else None,
            "avg_readiness_score": round(statistics.mean(readiness_scores), 1) if readiness_scores else None,
            "avg_activity_score": round(statistics.mean(activity_scores), 1) if activity_scores else None,
            "total_steps": sum(steps) if steps else None,
            "avg_steps": round(statistics.mean(steps), 0) if steps else None,
        },
        "developer": {
            "avg_commits": round(statistics.mean(commits), 1) if commits else None,
        }
    }


def aggregate_monthly_snapshot(snapshots: List[Dict]) -> Dict:
    """Aggregate daily snapshots into monthly summary."""
    if not snapshots:
        return {}
    
    # Extract values for aggregation
    sleep_scores = [s.get("health", {}).get("sleep_score") for s in snapshots if s.get("health", {}).get("sleep_score") is not None]
    readiness_scores = [s.get("health", {}).get("readiness_score") for s in snapshots if s.get("health", {}).get("readiness_score") is not None]
    activity_scores = [s.get("health", {}).get("activity_score") for s in snapshots if s.get("health", {}).get("activity_score") is not None]
    steps = [s.get("health", {}).get("activity_steps") for s in snapshots if s.get("health", {}).get("activity_steps") is not None]
    commits = [s.get("developer", {}).get("commits_30d") for s in snapshots if s.get("developer", {}).get("commits_30d") is not None]
    
    first_snapshot = snapshots[0]
    last_snapshot = snapshots[-1]
    
    return {
        "period": "monthly",
        "start_date": first_snapshot.get("date"),
        "end_date": last_snapshot.get("date"),
        "days_count": len(snapshots),
        "health": {
            "avg_sleep_score": round(statistics.mean(sleep_scores), 1) if sleep_scores else None,
            "max_sleep_score": max(sleep_scores) if sleep_scores else None,
            "min_sleep_score": min(sleep_scores) if sleep_scores else None,
            "avg_readiness_score": round(statistics.mean(readiness_scores), 1) if readiness_scores else None,
            "avg_activity_score": round(statistics.mean(activity_scores), 1) if activity_scores else None,
            "total_steps": sum(steps) if steps else None,
            "avg_steps": round(statistics.mean(steps), 0) if steps else None,
        },
        "developer": {
            "avg_commits": round(statistics.mean(commits), 1) if commits else None,
        }
    }


def update_aggregated_snapshots(output_dir: Path) -> None:
    """Update weekly and monthly aggregated snapshots."""
    now = datetime.now(timezone.utc)
    
    # Weekly snapshot (last 7 days)
    week_start = now - timedelta(days=6)
    weekly_snapshots = load_daily_snapshots(output_dir, week_start, now)
    
    if weekly_snapshots:
        weekly_summary = aggregate_weekly_snapshot(weekly_snapshots)
        
        weekly_dir = output_dir / "weekly"
        weekly_dir.mkdir(parents=True, exist_ok=True)
        
        # ISO week number
        year, week, _ = now.isocalendar()
        weekly_file = weekly_dir / f"{year}-W{week:02d}.json"
        
        with open(weekly_file, "w") as f:
            json.dump(weekly_summary, f, indent=2)
        
        print(f"Saved weekly snapshot: {weekly_file}", file=sys.stderr)
    
    # Monthly snapshot (current month)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_snapshots = load_daily_snapshots(output_dir, month_start, now)
    
    if monthly_snapshots:
        monthly_summary = aggregate_monthly_snapshot(monthly_snapshots)
        
        monthly_dir = output_dir / "monthly"
        monthly_dir.mkdir(parents=True, exist_ok=True)
        
        monthly_file = monthly_dir / f"{now.strftime('%Y-%m')}.json"
        
        with open(monthly_file, "w") as f:
            json.dump(monthly_summary, f, indent=2)
        
        print(f"Saved monthly snapshot: {monthly_file}", file=sys.stderr)


def main() -> None:
    """Main entry point for snapshot generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Store historical snapshots for trend analysis")
    parser.add_argument("--output-dir", default="data/snapshots", help="Output directory for snapshots")
    parser.add_argument("--no-aggregate", action="store_true", help="Skip aggregating weekly/monthly summaries")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    try:
        # Create daily snapshot
        snapshot = create_daily_snapshot()
        save_snapshot(snapshot, output_dir)
        
        # Update aggregated snapshots
        if not args.no_aggregate:
            update_aggregated_snapshots(output_dir)
        
        print("Snapshot generation completed successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error generating snapshots: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
