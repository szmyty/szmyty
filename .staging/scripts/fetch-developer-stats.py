#!/usr/bin/env python3
"""
Fetch GitHub developer statistics using the GitHub API.

This script gathers metrics for a GitHub user including:
- Repository counts (public/private)
- Commit activity
- Pull requests and issues
- Stars received
- Followers/following
- Language breakdown
- Top repositories by commits

Usage:
    python fetch-developer-stats.py <username> [output_path]

Environment Variables:
    GITHUB_TOKEN: Personal access token for GitHub API (optional but recommended)
    MAX_REPOS_TO_ANALYZE: Maximum repositories to analyze for language/commit stats (default: 15)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# Maximum number of repositories to analyze for detailed stats (language, commits)
# This limit helps avoid GitHub API rate limits
MAX_REPOS_TO_ANALYZE = int(os.environ.get("MAX_REPOS_TO_ANALYZE", "15"))


def get_github_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Developer-Stats-Dashboard/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def make_request(url: str, headers: Dict[str, str]) -> Optional[Dict]:
    """Make an HTTP request and return JSON response."""
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        print(f"HTTP Error {e.code} for {url}: {e.reason}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"URL Error for {url}: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {url}: {e}", file=sys.stderr)
        return None


def make_request_list(url: str, headers: Dict[str, str]) -> List[Dict]:
    """Make an HTTP request and return JSON list response."""
    result = make_request(url, headers)
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return []


def fetch_paginated(base_url: str, headers: Dict[str, str], max_pages: int = 10) -> List[Dict]:
    """Fetch paginated results from GitHub API."""
    results = []
    for page in range(1, max_pages + 1):
        separator = "&" if "?" in base_url else "?"
        url = f"{base_url}{separator}page={page}&per_page=100"
        page_results = make_request_list(url, headers)
        if not page_results:
            break
        results.extend(page_results)
        if len(page_results) < 100:
            break
    return results


def fetch_user_data(username: str, headers: Dict[str, str]) -> Optional[Dict]:
    """Fetch user profile data."""
    url = f"https://api.github.com/users/{username}"
    return make_request(url, headers)


def fetch_repos(username: str, headers: Dict[str, str]) -> List[Dict]:
    """Fetch all repositories for a user."""
    url = f"https://api.github.com/users/{username}/repos?type=owner"
    return fetch_paginated(url, headers)


def fetch_events(username: str, headers: Dict[str, str]) -> List[Dict]:
    """Fetch recent events for a user (max 300, last 90 days)."""
    url = f"https://api.github.com/users/{username}/events"
    return fetch_paginated(url, headers, max_pages=3)


def fetch_commit_activity(username: str, repo: str, headers: Dict[str, str]) -> List[Dict]:
    """Fetch commit activity for a repository."""
    url = f"https://api.github.com/repos/{username}/{repo}/stats/commit_activity"
    result = make_request(url, headers)
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return []


def fetch_contributor_stats(username: str, repo: str, headers: Dict[str, str]) -> Optional[Dict]:
    """Fetch contributor statistics for a repository."""
    url = f"https://api.github.com/repos/{username}/{repo}/stats/contributors"
    result = make_request(url, headers)
    if result is None or not isinstance(result, list):
        return None
    # Find the user's contribution data
    for contributor in result:
        if contributor.get("author", {}).get("login", "").lower() == username.lower():
            return contributor
    return None


def calculate_language_stats(repos: List[Dict], username: str, headers: Dict[str, str]) -> Dict[str, int]:
    """Calculate total bytes per language across all repos."""
    language_totals: Dict[str, int] = {}
    for repo in repos[:MAX_REPOS_TO_ANALYZE]:
        repo_name = repo.get("name")
        if not repo_name:
            continue
        url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
        languages = make_request(url, headers)
        if languages and isinstance(languages, dict):
            for lang, bytes_count in languages.items():
                language_totals[lang] = language_totals.get(lang, 0) + bytes_count
    return language_totals


def calculate_language_percentages(language_bytes: Dict[str, int]) -> Dict[str, float]:
    """Convert language bytes to percentages."""
    total = sum(language_bytes.values())
    if total == 0:
        return {}
    
    percentages = {}
    for lang, bytes_count in sorted(language_bytes.items(), key=lambda x: -x[1]):
        pct = (bytes_count / total) * 100
        if pct >= 1.0:  # Only include languages with >= 1%
            percentages[lang] = round(pct, 1)
    
    # Add "Other" for remaining
    main_total = sum(percentages.values())
    if main_total < 100:
        other = round(100 - main_total, 1)
        if other > 0.5:
            percentages["Other"] = other
    
    return percentages


def extract_commit_timestamps(events: List[Dict], username: str) -> List[str]:
    """Extract commit timestamps from push events."""
    timestamps = []
    for event in events:
        if event.get("type") != "PushEvent":
            continue
        payload = event.get("payload", {})
        commits = payload.get("commits", [])
        for commit in commits:
            # Use event created_at as commit timestamp approximation
            created_at = event.get("created_at")
            if created_at:
                timestamps.append(created_at)
    return timestamps


def calculate_commit_activity_distribution(timestamps: List[str]) -> Dict[str, Union[List[List[int]], List[str]]]:
    """Calculate commit activity distribution by hour and day."""
    # Initialize 7x24 grid (day_of_week x hour_of_day)
    activity_grid = [[0] * 24 for _ in range(7)]
    
    for ts in timestamps:
        try:
            # Parse ISO 8601 timestamp
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
            hour = dt.hour
            activity_grid[day_of_week][hour] += 1
        except (ValueError, AttributeError):
            continue
    
    return {
        "grid": activity_grid,  # 7x24 array
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    }


def calculate_daily_commits(timestamps: List[str], days: int = 30) -> List[int]:
    """Calculate daily commit counts for the last N days."""
    now = datetime.now(timezone.utc)
    daily_counts = [0] * days
    
    for ts in timestamps:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            days_ago = (now - dt).days
            if 0 <= days_ago < days:
                daily_counts[days - 1 - days_ago] += 1
        except (ValueError, AttributeError):
            continue
    
    return daily_counts


def count_prs_and_issues(events: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Count PRs opened/merged and issues opened from events."""
    prs_opened = 0
    prs_merged = 0
    issues_opened = 0
    
    for event in events:
        event_type = event.get("type")
        payload = event.get("payload", {})
        action = payload.get("action")
        
        if event_type == "PullRequestEvent":
            if action == "opened":
                prs_opened += 1
            elif action == "closed":
                pr = payload.get("pull_request", {})
                if pr.get("merged"):
                    prs_merged += 1
        elif event_type == "IssuesEvent":
            if action == "opened":
                issues_opened += 1
    
    return {
        "prs": {"opened": prs_opened, "merged": prs_merged},
        "issues": {"opened": issues_opened},
    }


def get_top_repos_by_commits(repos: List[Dict], username: str, headers: Dict[str, str], limit: int = 5) -> List[Dict]:
    """Get top repositories by commit count."""
    repo_commits = []
    
    for repo in repos[:MAX_REPOS_TO_ANALYZE]:
        repo_name = repo.get("name")
        if not repo_name:
            continue
        
        contributor = fetch_contributor_stats(username, repo_name, headers)
        if contributor:
            total_commits = contributor.get("total", 0)
            repo_commits.append({
                "name": repo_name,
                "commits": total_commits,
            })
    
    # Sort by commits and return top N
    repo_commits.sort(key=lambda x: -x["commits"])
    return repo_commits[:limit]


def calculate_total_stars(repos: List[Dict]) -> int:
    """Calculate total stars across all repos."""
    return sum(repo.get("stargazers_count", 0) for repo in repos)


def fetch_developer_stats(username: str) -> Dict[str, Any]:
    """Fetch and compile all developer statistics."""
    headers = get_github_headers()
    
    print(f"Fetching data for user: {username}", file=sys.stderr)
    
    # Fetch user profile
    user = fetch_user_data(username, headers)
    if not user:
        print("Error: Could not fetch user data", file=sys.stderr)
        sys.exit(1)
    
    # Fetch repositories
    print("Fetching repositories...", file=sys.stderr)
    repos = fetch_repos(username, headers)
    
    # Fetch events for commit/PR/issue activity
    print("Fetching events...", file=sys.stderr)
    events = fetch_events(username, headers)
    
    # Calculate language stats
    print("Calculating language statistics...", file=sys.stderr)
    language_bytes = calculate_language_stats(repos, username, headers)
    language_percentages = calculate_language_percentages(language_bytes)
    
    # Extract commit timestamps and activity
    commit_timestamps = extract_commit_timestamps(events, username)
    activity_distribution = calculate_commit_activity_distribution(commit_timestamps)
    daily_commits = calculate_daily_commits(commit_timestamps, 30)
    
    # Count PRs and issues
    pr_issue_counts = count_prs_and_issues(events)
    
    # Get top repos by commits
    print("Fetching top repositories...", file=sys.stderr)
    top_repos = get_top_repos_by_commits(repos, username, headers, 5)
    
    # Calculate total stars
    total_stars = calculate_total_stars(repos)
    
    # Compile stats
    stats = {
        "username": username,
        "name": user.get("name", username),
        "avatar_url": user.get("avatar_url", ""),
        "repos": user.get("public_repos", 0),
        "private_repos": user.get("total_private_repos", 0),
        "stars": total_stars,
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "commit_activity": {
            "last_30_days": daily_commits,
            "total_30_days": sum(daily_commits),
            "activity_grid": activity_distribution["grid"],
            "days": activity_distribution["days"],
        },
        "prs": pr_issue_counts["prs"],
        "issues": pr_issue_counts["issues"],
        "languages": language_percentages,
        "top_repositories": top_repos,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    
    return stats


def save_raw_data(output_dir: Path, data: Dict[str, Any], filename: str) -> None:
    """Save raw API response data for debugging."""
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    raw_path = raw_dir / filename
    with open(raw_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved raw data: {raw_path}", file=sys.stderr)


def main() -> None:
    """Main entry point."""
    # Set up logging
    try:
        sys.path.insert(0, str(Path(__file__).parent / "lib"))
        from logging_utils import setup_logging  # type: ignore[import-not-found]
        logger = setup_logging("developer")
        logger.log_workflow_start("Developer Statistics - Fetch Data")
    except ImportError:
        logger = None
    
    if len(sys.argv) < 2:
        # Try to get username from GITHUB_REPOSITORY_OWNER environment variable
        username = os.environ.get("GITHUB_REPOSITORY_OWNER")
        if not username:
            if logger:
                logger.error("Missing username argument and GITHUB_REPOSITORY_OWNER not set")
                logger.log_workflow_end(1)
            print(
                "Usage: fetch-developer-stats.py <username> [output_path]",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        username = sys.argv[1]
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else "developer/stats.json"
    
    if logger:
        logger.info(f"Fetching developer statistics for: {username}")
    
    # Fetch stats
    stats = fetch_developer_stats(username)
    
    # Output to stdout (for piping) or write to file
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w") as f:
        json.dump(stats, f, indent=2)
    
    if logger:
        logger.info(f"Developer stats saved to: {output_path}")
        logger.info(f"Total repositories: {stats.get('total_repos', 'N/A')}")
        logger.info(f"Total commits (30 days): {stats.get('commit_activity', {}).get('total_30_days', 'N/A')}")
    print(f"Developer stats saved to: {output_path}", file=sys.stderr)
    
    # Also save a copy of the raw stats data
    output_dir = output.parent
    save_raw_data(output_dir, stats, "stats_raw.json")
    
    if logger:
        logger.log_workflow_end(0)


if __name__ == "__main__":
    main()
