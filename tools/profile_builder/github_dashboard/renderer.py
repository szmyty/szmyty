# ruff: noqa: E501
"""Deterministic native-SVG renderer for the GitHub engineering dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Literal

from tools.profile_builder.github_dashboard.models import GitHubDashboardSnapshot

_FONT_STACK = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


@dataclass(frozen=True)
class Palette:
    background: str
    panel: str
    panel_alt: str
    border: str
    text: str
    muted: str
    accent: str
    accent_alt: str
    success: str
    legend: tuple[str, str, str, str, str]


_LIGHT = Palette(
    background="#ffffff",
    panel="#f6f8fa",
    panel_alt="#eef2ff",
    border="#d0d7de",
    text="#1f2328",
    muted="#59636e",
    accent="#0969da",
    accent_alt="#6639ba",
    success="#1a7f64",
    legend=("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"),
)
_DARK = Palette(
    background="#0d1117",
    panel="#161b22",
    panel_alt="#1e1b4b",
    border="#30363d",
    text="#e6edf3",
    muted="#7d8590",
    accent="#388bfd",
    accent_alt="#a371f7",
    success="#3fb950",
    legend=("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
)


def _month_labels(snapshot: GitHubDashboardSnapshot) -> list[tuple[str, int]]:
    labels: list[tuple[str, int]] = []
    seen: set[tuple[int, int]] = set()
    start = date.fromisoformat(snapshot.window_start)
    for day in snapshot.contribution_days:
        value = date.fromisoformat(day.date)
        if value.weekday() != 6:
            continue
        marker = (value.year, value.month)
        if marker in seen:
            continue
        seen.add(marker)
        labels.append((value.strftime("%b"), (value - start).days // 7))
    return labels


def _heatmap_cells(
    snapshot: GitHubDashboardSnapshot,
    *,
    cell_size: int,
    gap: int,
    origin_x: int,
    origin_y: int,
    palette: Palette,
) -> str:
    start = date.fromisoformat(snapshot.window_start)
    cells: list[str] = []
    for day in snapshot.contribution_days:
        value = date.fromisoformat(day.date)
        column = (value - start).days // 7
        row = day.weekday
        x = origin_x + column * (cell_size + gap)
        y = origin_y + row * (cell_size + gap)
        color = palette.legend[day.level]
        cells.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
            f'rx="{max(2, cell_size // 4)}" fill="{color}" />'
        )
    return "\n".join(cells)


def _language_rows(
    snapshot: GitHubDashboardSnapshot,
    *,
    origin_x: int,
    origin_y: int,
    width: int,
    palette: Palette,
) -> str:
    rows: list[str] = []
    for index, language in enumerate(snapshot.languages[:6]):
        y = origin_y + index * 28
        bar_width = max(12, int((width - 88) * (language.percentage / 100)))
        rows.append(
            "\n".join(
                [
                    f'<text x="{origin_x}" y="{y}" fill="{palette.muted}" font-size="11" '
                    f'font-family="{_FONT_STACK}">{escape(language.name)}</text>',
                    f'<text x="{origin_x + width}" y="{y}" text-anchor="end" fill="{palette.text}" '
                    f'font-size="11" font-family="{_FONT_STACK}">{language.percentage}%</text>',
                    f'<rect x="{origin_x}" y="{y + 8}" width="{width}" height="8" rx="4" fill="{palette.border}" opacity="0.28" />',
                    f'<rect x="{origin_x}" y="{y + 8}" width="{bar_width}" height="8" rx="4" fill="{palette.accent_alt}" />',
                ]
            )
        )
    return "\n".join(rows)


def render_dashboard_svg(
    snapshot: GitHubDashboardSnapshot,
    *,
    theme: Literal["light", "dark"],
    mobile: bool = False,
) -> str:
    """Render one theme/viewport SVG variant from the normalized snapshot."""
    if theme not in {"light", "dark"}:
        raise ValueError(f"Unsupported dashboard theme: {theme}")
    palette = _DARK if theme == "dark" else _LIGHT
    width = 420 if mobile else 960
    height = 760 if mobile else 420
    heatmap_cell = 5 if mobile else 9
    heatmap_gap = 2
    heatmap_x = 24
    heatmap_y = 118
    metrics_x = 24 if mobile else 620
    metrics_y = 360 if mobile else 118
    panel_width = width - 48 if mobile else 316
    heatmap_panel_width = width - 48 if mobile else 570
    month_labels = "\n".join(
        f'<text x="{heatmap_x + col * (heatmap_cell + heatmap_gap)}" y="{heatmap_y - 10}" '
        f'fill="{palette.muted}" font-size="10" font-family="{_FONT_STACK}">{label}</text>'
        for label, col in _month_labels(snapshot)
    )
    legend_x = heatmap_x + (320 if mobile else 422)
    legend = "\n".join(
        f'<rect x="{legend_x + idx * 13}" y="{heatmap_y + 52 if mobile else heatmap_y + 79}" '
        f'width="10" height="10" rx="3" fill="{color}" />'
        for idx, color in enumerate(palette.legend)
    )
    breakdown = snapshot.contribution_breakdown
    streaks = snapshot.streaks
    inventory = snapshot.repository_inventory
    title = f"{snapshot.title} for @{snapshot.username}"
    desc = (
        f"Trailing {snapshot.trailing_window_days}-day GitHub dashboard showing "
        f"{breakdown.total_public_contributions} public contributions, a current streak of "
        f"{streaks.current_days} days, a longest streak of {streaks.longest_days} days, "
        f"{inventory.owned_public_non_archived_repositories} eligible repositories, "
        f"{inventory.stars_received} stars, and {inventory.public_releases_past_year} public releases."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        'aria-labelledby="title desc">\n'
        f'  <title id="title">{escape(title)}</title>\n'
        f'  <desc id="desc">{escape(desc)}</desc>\n'
        "  <defs>\n"
        f'    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">\n'
        f'      <stop offset="0%" stop-color="{palette.background}" />\n'
        f'      <stop offset="100%" stop-color="{palette.panel_alt}" />\n'
        "    </linearGradient>\n"
        "    <style>\n"
        "      @media (prefers-reduced-motion: no-preference) {\n"
        "        .orbit { animation: orbitPulse 14s ease-in-out infinite; }\n"
        "      }\n"
        "      @keyframes orbitPulse {\n"
        "        0%, 100% { opacity: 0.55; }\n"
        "        50% { opacity: 1; }\n"
        "      }\n"
        "    </style>\n"
        "  </defs>\n"
        f'  <rect width="{width}" height="{height}" rx="24" fill="url(#bg)" />\n'
        f'  <rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="20" fill="{palette.panel}" opacity="0.96" />\n'
        f'  <circle class="orbit" cx="{width - 80}" cy="54" r="18" fill="{palette.accent_alt}" opacity="0.18" />\n'
        f'  <circle class="orbit" cx="{width - 112}" cy="80" r="4" fill="{palette.accent}" />\n'
        f'  <circle class="orbit" cx="{width - 52}" cy="84" r="3" fill="{palette.success}" />\n'
        f'  <text x="24" y="42" fill="{palette.muted}" font-size="12" font-family="{_FONT_STACK}">GitHub Engineering</text>\n'
        f'  <text x="24" y="70" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">@{escape(snapshot.username)}</text>\n'
        f'  <text x="24" y="92" fill="{palette.muted}" font-size="12" font-family="{_FONT_STACK}">'
        f"{escape(snapshot.window_start)} → {escape(snapshot.window_end)} · {escape(snapshot.status.data_source)} · {escape(snapshot.status.source_state)}</text>\n"
        f'  <rect x="24" y="106" width="{heatmap_panel_width}" height="{228 if mobile else 120}" rx="16" fill="{palette.background}" opacity="0.52" stroke="{palette.border}" />\n'
        f'  <text x="{heatmap_x}" y="{heatmap_y - 28}" fill="{palette.text}" font-size="14" font-weight="600" font-family="{_FONT_STACK}">Contribution heatmap</text>\n'
        f'  <text x="{heatmap_x}" y="{heatmap_y - 12}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">{breakdown.total_public_contributions} public contributions represented</text>\n'
        f"{month_labels}\n"
        f"{_heatmap_cells(snapshot, cell_size=heatmap_cell, gap=heatmap_gap, origin_x=heatmap_x, origin_y=heatmap_y, palette=palette)}\n"
        f"{legend}\n"
        f'  <text x="{legend_x - 40}" y="{heatmap_y + 61 if mobile else heatmap_y + 88}" fill="{palette.muted}" font-size="10" font-family="{_FONT_STACK}">Less</text>\n'
        f'  <text x="{legend_x + 70}" y="{heatmap_y + 61 if mobile else heatmap_y + 88}" fill="{palette.muted}" font-size="10" font-family="{_FONT_STACK}">More</text>\n'
        f'  <rect x="{metrics_x}" y="{metrics_y}" width="{panel_width}" height="164" rx="16" fill="{palette.background}" opacity="0.52" stroke="{palette.border}" />\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 28}" fill="{palette.text}" font-size="14" font-weight="600" font-family="{_FONT_STACK}">Activity mix</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 54}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{breakdown.public_commit_contributions}</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 72}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Commits</text>\n'
        f'  <text x="{metrics_x + 112}" y="{metrics_y + 54}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{breakdown.public_pull_request_contributions}</text>\n'
        f'  <text x="{metrics_x + 112}" y="{metrics_y + 72}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Pull requests</text>\n'
        f'  <text x="{metrics_x + 220}" y="{metrics_y + 54}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{breakdown.public_issue_contributions}</text>\n'
        f'  <text x="{metrics_x + 220}" y="{metrics_y + 72}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Issues</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 118}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{breakdown.public_pull_request_review_contributions}</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 136}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">PR reviews</text>\n'
        f'  <text x="{metrics_x + 188}" y="{metrics_y + 118}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{streaks.current_days}d</text>\n'
        f'  <text x="{metrics_x + 188}" y="{metrics_y + 136}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Current streak</text>\n'
        f'  <text x="{metrics_x + 262}" y="{metrics_y + 118}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{streaks.longest_days}d</text>\n'
        f'  <text x="{metrics_x + 262}" y="{metrics_y + 136}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Longest streak</text>\n'
        f'  <rect x="{metrics_x}" y="{metrics_y + 178}" width="{panel_width}" height="98" rx="16" fill="{palette.background}" opacity="0.52" stroke="{palette.border}" />\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 206}" fill="{palette.text}" font-size="14" font-weight="600" font-family="{_FONT_STACK}">Repository inventory</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 240}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{inventory.owned_public_non_archived_repositories}</text>\n'
        f'  <text x="{metrics_x + 18}" y="{metrics_y + 258}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Owned public repos</text>\n'
        f'  <text x="{metrics_x + 146}" y="{metrics_y + 240}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{inventory.stars_received}</text>\n'
        f'  <text x="{metrics_x + 146}" y="{metrics_y + 258}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Stars</text>\n'
        f'  <text x="{metrics_x + 240}" y="{metrics_y + 240}" fill="{palette.text}" font-size="26" font-weight="700" font-family="{_FONT_STACK}">{inventory.public_releases_past_year}</text>\n'
        f'  <text x="{metrics_x + 240}" y="{metrics_y + 258}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">Releases / 365d</text>\n'
        f'  <rect x="{24 if mobile else 620}" y="{558 if mobile else 290}" width="{panel_width}" height="{178 if mobile else 104}" rx="16" fill="{palette.background}" opacity="0.52" stroke="{palette.border}" />\n'
        f'  <text x="{42 if mobile else 638}" y="{586 if mobile else 318}" fill="{palette.text}" font-size="14" font-weight="600" font-family="{_FONT_STACK}">Language distribution</text>\n'
        f"{_language_rows(snapshot, origin_x=42 if mobile else 638, origin_y=604 if mobile else 338, width=panel_width - 36, palette=palette)}\n"
        f'  <text x="24" y="{height - 20}" fill="{palette.muted}" font-size="11" font-family="{_FONT_STACK}">'
        f"Data: {escape(snapshot.status.data_timestamp[:19].replace('T', ' '))} UTC · Generated: {escape(snapshot.status.generation_timestamp[:19].replace('T', ' '))} UTC</text>\n"
        "</svg>\n"
    )
