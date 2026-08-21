"""Deterministic native-SVG renderer for the GitHub AFQC engineering dashboard.

Layout is fully declarative: each panel measures its required height, panels
stack vertically with a fixed gap, and canvas height is derived from the
measured content — no hard-coded global y-offsets.
"""

from __future__ import annotations

import calendar
import math
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Literal

from tools.profile_builder.github_dashboard.models import (
    GitHubDashboardSnapshot,
    MonthlyContribution,
)

# ---------------------------------------------------------------------------
# AFQC semantic token system
# ---------------------------------------------------------------------------

_FONT_STACK = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


@dataclass(frozen=True)
class AfqcTokens:
    """AFQC semantic design token set for one theme."""

    # Surfaces
    void: str
    void_elevated: str
    surface: str
    surface_glass: str
    border_subtle: str
    # Text
    text_primary: str
    text_secondary: str
    text_muted: str
    # Brand energy
    quantum_pink: str
    cosmic_violet: str
    signal_cyan: str
    iridescent_lavender: str
    starlight: str
    positive: str
    warning: str
    inactive: str
    # Heatmap levels
    heatmap: tuple[str, str, str, str, str]
    # Chart palette (categorical, 8 entries)
    chart_palette: tuple[str, ...]


_DARK_TOKENS = AfqcTokens(
    void="#0a0b11",
    void_elevated="#0f1019",
    surface="#161b2e",
    surface_glass="#1c2240",
    border_subtle="#2a2f4e",
    text_primary="#e8eaf6",
    text_secondary="#b0b8d8",
    text_muted="#9ca3af",
    quantum_pink="#e879a8",
    cosmic_violet="#7c3aed",
    signal_cyan="#22d3ee",
    iridescent_lavender="#a78bfa",
    starlight="#fbbf24",
    positive="#34d399",
    warning="#f59e0b",
    inactive="#374151",
    heatmap=("#161b2e", "#1e3a5f", "#1d4ed8", "#3b82f6", "#93c5fd"),
    chart_palette=(
        "#e879a8",
        "#7c3aed",
        "#22d3ee",
        "#a78bfa",
        "#34d399",
        "#f59e0b",
        "#fb923c",
        "#6b7280",
    ),
)

_LIGHT_TOKENS = AfqcTokens(
    void="#f0f1f8",
    void_elevated="#e8eaf6",
    surface="#ffffff",
    surface_glass="#f8f9ff",
    border_subtle="#d1d5db",
    text_primary="#111827",
    text_secondary="#374151",
    text_muted="#6b7280",
    quantum_pink="#be185d",
    cosmic_violet="#6d28d9",
    signal_cyan="#0891b2",
    iridescent_lavender="#7c3aed",
    starlight="#d97706",
    positive="#059669",
    warning="#d97706",
    inactive="#e5e7eb",
    heatmap=("#e5e7eb", "#bfdbfe", "#93c5fd", "#3b82f6", "#1d4ed8"),
    chart_palette=(
        "#be185d",
        "#6d28d9",
        "#0891b2",
        "#7c3aed",
        "#059669",
        "#d97706",
        "#ea580c",
        "#6b7280",
    ),
)

# ---------------------------------------------------------------------------
# Layout primitives
# ---------------------------------------------------------------------------

_CARD_RADIUS = 18
_PANEL_PADDING = 20
_SECTION_GAP = 16
_CARD_GAP = 12


@dataclass
class LayoutBox:
    """An axis-aligned bounding box for one rendered component."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


def _card_bg(box: LayoutBox, tok: AfqcTokens) -> str:
    return (
        f'<rect x="{box.x:.0f}" y="{box.y:.0f}" '
        f'width="{box.width:.0f}" height="{box.height:.0f}" '
        f'rx="{_CARD_RADIUS}" '
        f'fill="{tok.surface_glass}" opacity="0.92" '
        f'stroke="{tok.border_subtle}" stroke-width="1" />'
    )


def _label(
    text: str,
    x: float,
    y: float,
    tok: AfqcTokens,
    *,
    size: int = 11,
    color: str | None = None,
    weight: str = "normal",
    anchor: str = "start",
) -> str:
    fill = color or tok.text_muted
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" '
        f'fill="{fill}" '
        f'font-size="{size}" '
        f'font-family="{_FONT_STACK}" '
        f'font-weight="{weight}" '
        f'text-anchor="{anchor}">'
        f"{escape(text)}</text>"
    )


def _metric_tile(
    value: str,
    label: str,
    x: float,
    y: float,
    tok: AfqcTokens,
    *,
    value_color: str | None = None,
    value_size: int = 22,
) -> str:
    vc = value_color or tok.text_primary
    lines = [
        f'<text x="{x:.0f}" y="{y:.0f}" fill="{vc}" '
        f'font-size="{value_size}" font-weight="700" '
        f'font-family="{_FONT_STACK}">{escape(value)}</text>',
        _label(label, x, y + 16, tok, size=10),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------


def _heatmap_cell_size(mobile: bool) -> int:
    return 5 if mobile else 9


def _heatmap_cells(
    snapshot: GitHubDashboardSnapshot,
    *,
    cell_size: int,
    gap: int,
    origin_x: float,
    origin_y: float,
    tok: AfqcTokens,
) -> str:
    start = date.fromisoformat(snapshot.window_start)
    cells: list[str] = []
    for day in snapshot.contribution_days:
        value = date.fromisoformat(day.date)
        column = (value - start).days // 7
        row = day.weekday
        cx = origin_x + column * (cell_size + gap)
        cy = origin_y + row * (cell_size + gap)
        color = tok.heatmap[day.level]
        cells.append(
            f'<rect x="{cx:.0f}" y="{cy:.0f}" '
            f'width="{cell_size}" height="{cell_size}" '
            f'rx="{max(2, cell_size // 4)}" fill="{color}" />'
        )
    return "\n".join(cells)


def _heatmap_month_labels(
    snapshot: GitHubDashboardSnapshot,
    *,
    cell_size: int,
    gap: int,
    origin_x: float,
    origin_y: float,
    tok: AfqcTokens,
) -> str:
    labels: list[str] = []
    seen: set[tuple[int, int]] = set()
    last_label_x: float | None = None
    start = date.fromisoformat(snapshot.window_start)
    for day in snapshot.contribution_days:
        value = date.fromisoformat(day.date)
        if value.weekday() != 6:
            continue
        marker = (value.year, value.month)
        if marker in seen:
            continue
        seen.add(marker)
        col = (value - start).days // 7
        lx = origin_x + col * (cell_size + gap)
        if last_label_x is not None and lx - last_label_x < cell_size * 3:
            continue
        last_label_x = lx
        labels.append(
            f'<text x="{lx:.0f}" y="{origin_y - 6:.0f}" '
            f'fill="{tok.text_muted}" font-size="9" '
            f'font-family="{_FONT_STACK}">'
            f"{escape(value.strftime('%b'))}</text>"
        )
    return "\n".join(labels)


def _heatmap_height(cell_size: int, gap: int) -> float:
    return 7 * (cell_size + gap) - gap


# ---------------------------------------------------------------------------
# Contribution Pulse (monthly bar/line chart)
# ---------------------------------------------------------------------------


def _pulse_chart(
    monthly: list[MonthlyContribution],
    box: LayoutBox,
    tok: AfqcTokens,
) -> str:
    if not monthly:
        return _label("No data", box.x + _PANEL_PADDING, box.y + 40, tok)
    pad = _PANEL_PADDING
    inner_w = box.width - 2 * pad
    inner_h = box.height - 2 * pad - 20  # 20 for month labels at bottom
    max_count = max(m.count for m in monthly) or 1
    n = len(monthly)
    col_w = inner_w / n
    parts: list[str] = []
    points: list[tuple[float, float]] = []
    for idx, month in enumerate(monthly):
        bar_h = (month.count / max_count) * inner_h
        bx = box.x + pad + idx * col_w
        by = box.y + pad + inner_h - bar_h
        parts.append(
            f'<rect x="{bx + 2:.1f}" y="{by:.1f}" '
            f'width="{col_w - 4:.1f}" height="{bar_h:.1f}" '
            f'rx="3" fill="{tok.cosmic_violet}" opacity="0.35" />'
        )
        cx = bx + col_w / 2
        cy = by
        points.append((cx, cy))
        # Month label
        abbr = calendar.month_abbr[month.month]
        parts.append(
            f'<text x="{cx:.1f}" y="{box.y + box.height - 6:.1f}" '
            f'fill="{tok.text_muted}" font-size="9" '
            f'text-anchor="middle" font-family="{_FONT_STACK}">'
            f"{abbr}</text>"
        )
    # Line
    if len(points) > 1:
        poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
        parts.append(
            f'<polyline points="{poly}" '
            f'fill="none" stroke="{tok.quantum_pink}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />'
        )
    # Data points
    for px, py in points:
        parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{tok.quantum_pink}" />'
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Language Orbit (donut chart)
# ---------------------------------------------------------------------------


def _donut_arc(
    cx: float,
    cy: float,
    r_outer: float,
    r_inner: float,
    start_angle: float,
    sweep_angle: float,
    color: str,
) -> str:
    """Render one donut arc segment."""
    if sweep_angle >= 360:
        sweep_angle = 359.999
    sa = math.radians(start_angle - 90)
    ea = math.radians(start_angle + sweep_angle - 90)
    x1 = cx + r_outer * math.cos(sa)
    y1 = cy + r_outer * math.sin(sa)
    x2 = cx + r_outer * math.cos(ea)
    y2 = cy + r_outer * math.sin(ea)
    x3 = cx + r_inner * math.cos(ea)
    y3 = cy + r_inner * math.sin(ea)
    x4 = cx + r_inner * math.cos(sa)
    y4 = cy + r_inner * math.sin(sa)
    large = 1 if sweep_angle > 180 else 0
    return (
        f'<path d="M {x1:.2f} {y1:.2f} '
        f"A {r_outer:.2f} {r_outer:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} "
        f"L {x3:.2f} {y3:.2f} "
        f'A {r_inner:.2f} {r_inner:.2f} 0 {large} 0 {x4:.2f} {y4:.2f} Z" '
        f'fill="{color}" />'
    )


def _language_donut(
    snapshot: GitHubDashboardSnapshot,
    box: LayoutBox,
    tok: AfqcTokens,
) -> str:
    langs = snapshot.languages
    if not langs:
        return _label("No language data", box.x + _PANEL_PADDING, box.y + 40, tok)
    r_outer = min(box.height, 80) * 0.42
    r_inner = r_outer * 0.55
    cx = box.x + r_outer + _PANEL_PADDING + 4
    cy = box.y + box.height / 2
    parts: list[str] = []
    angle = 0.0
    for idx, lang in enumerate(langs):
        color = tok.chart_palette[idx % len(tok.chart_palette)]
        sweep = lang.percentage / 100 * 360
        parts.append(_donut_arc(cx, cy, r_outer, r_inner, angle, sweep, color))
        angle += sweep
    # Legend
    legend_x = cx + r_outer + 16
    for idx, lang in enumerate(langs[:8]):
        color = tok.chart_palette[idx % len(tok.chart_palette)]
        ly = box.y + _PANEL_PADDING + 2 + idx * 18
        parts.append(
            f'<rect x="{legend_x:.0f}" y="{ly - 8:.0f}" '
            f'width="9" height="9" rx="2" fill="{color}" />'
        )
        parts.append(
            f'<text x="{legend_x + 13:.0f}" y="{ly:.0f}" '
            f'fill="{tok.text_secondary}" font-size="10" '
            f'font-family="{_FONT_STACK}">'
            f"{escape(lang.name)} {lang.percentage}%</text>"
        )
    parts.append(
        _label(
            "Bytes by language — not a proficiency score",
            box.x + _PANEL_PADDING,
            box.bottom - 4,
            tok,
            size=9,
        )
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Engineering Signature radar chart
# ---------------------------------------------------------------------------


def _radar_chart(
    snapshot: GitHubDashboardSnapshot,
    box: LayoutBox,
    tok: AfqcTokens,
) -> str:
    dims = snapshot.radar_dimensions
    if not dims:
        return _label("No radar data", box.x + _PANEL_PADDING, box.y + 40, tok)
    n = len(dims)
    r_max = min(box.width, box.height) * 0.35
    cx = box.x + box.width / 2
    cy = box.y + box.height / 2 + 4
    parts: list[str] = []

    def _polar(idx: int, scale: float) -> tuple[float, float]:
        angle = math.radians(360 / n * idx - 90)
        return cx + r_max * scale * math.cos(angle), cy + r_max * scale * math.sin(
            angle
        )

    # Grid rings
    for ring in [0.25, 0.5, 0.75, 1.0]:
        ring_pts = " ".join(
            f"{_polar(i, ring)[0]:.2f},{_polar(i, ring)[1]:.2f}" for i in range(n)
        )
        parts.append(
            f'<polygon points="{ring_pts}" '
            f'fill="none" stroke="{tok.border_subtle}" stroke-width="1" />'
        )
    # Axes
    for i in range(n):
        ex, ey = _polar(i, 1.0)
        parts.append(
            f'<line x1="{cx:.2f}" y1="{cy:.2f}" '
            f'x2="{ex:.2f}" y2="{ey:.2f}" '
            f'stroke="{tok.border_subtle}" stroke-width="1" />'
        )
    # Data polygon
    pts = []
    for idx, dim in enumerate(dims):
        scale = 0.0 if dim.unavailable else dim.score / 100
        px, py = _polar(idx, scale)
        pts.append((px, py))
    poly = " ".join(f"{px:.2f},{py:.2f}" for px, py in pts)
    parts.append(
        f'<polygon points="{poly}" '
        f'fill="{tok.cosmic_violet}" opacity="0.25" '
        f'stroke="{tok.iridescent_lavender}" stroke-width="2" />'
    )
    for px, py in pts:
        parts.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4" fill="{tok.quantum_pink}" />'
        )
    # Axis labels
    label_r = r_max + 14
    for idx, dim in enumerate(dims):
        angle = math.radians(360 / n * idx - 90)
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        anchor = "middle"
        if lx < cx - 4:
            anchor = "end"
        elif lx > cx + 4:
            anchor = "start"
        parts.append(
            f'<text x="{lx:.2f}" y="{ly + 4:.2f}" '
            f'fill="{tok.text_secondary}" font-size="10" '
            f'text-anchor="{anchor}" font-family="{_FONT_STACK}">'
            f"{escape(dim.label)}</text>"
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Top-level renderer
# ---------------------------------------------------------------------------


def render_dashboard_svg(
    snapshot: GitHubDashboardSnapshot,
    *,
    theme: Literal["light", "dark"],
    mobile: bool = False,
) -> str:
    """Render one theme/viewport SVG variant from the normalized snapshot."""
    if theme not in {"light", "dark"}:
        raise ValueError(f"Unsupported dashboard theme: {theme}")
    tok = _DARK_TOKENS if theme == "dark" else _LIGHT_TOKENS
    pad = _PANEL_PADDING
    margin = 16
    width = 420 if mobile else 960

    # Component heights (measured, not hard-coded globally)
    cell = _heatmap_cell_size(mobile)
    gap = 2
    hmap_h = _heatmap_height(cell, gap) + 24  # +24 for month labels above
    hmap_panel_h = hmap_h + 2 * pad + 34
    activity_panel_h = 145
    language_panel_h = 185
    pulse_panel_h = 120
    explore_panel_h = 125
    radar_panel_h = 215
    footer_h = 52

    # Left / right column widths
    if mobile:
        left_w = width - 2 * margin
        right_w = left_w
    else:
        left_w = 580
        right_w = width - left_w - 3 * margin

    # Stack panels vertically per column; canvas height from tallest column
    col_x = float(margin)
    col_y = float(margin + 72)  # 72 for header

    if mobile:
        y_cursor = col_y

        def _add(h: float) -> LayoutBox:
            nonlocal y_cursor
            b = LayoutBox(col_x, y_cursor, left_w, h)
            y_cursor += h + _SECTION_GAP
            return b

        hmap_box = _add(hmap_panel_h)
        activity_box = _add(activity_panel_h)
        lang_box = _add(language_panel_h)
        pulse_box = _add(pulse_panel_h)
        explore_box = _add(explore_panel_h)
        radar_box = _add(radar_panel_h)
        canvas_h = y_cursor + footer_h
    else:
        # Desktop two-column layout
        left_x = col_x
        right_x = col_x + left_w + margin
        left_y = col_y
        right_y = col_y

        hmap_box = LayoutBox(left_x, left_y, left_w, hmap_panel_h)
        left_y += hmap_panel_h + _SECTION_GAP
        pulse_box = LayoutBox(left_x, left_y, left_w, pulse_panel_h)
        left_y += pulse_panel_h + _SECTION_GAP
        explore_box = LayoutBox(left_x, left_y, left_w, explore_panel_h)
        left_y += explore_panel_h + _SECTION_GAP

        activity_box = LayoutBox(right_x, right_y, right_w, activity_panel_h)
        right_y += activity_panel_h + _SECTION_GAP
        lang_box = LayoutBox(right_x, right_y, right_w, language_panel_h)
        right_y += language_panel_h + _SECTION_GAP
        radar_box = LayoutBox(right_x, right_y, right_w, radar_panel_h)
        right_y += radar_panel_h

        canvas_h = max(left_y, right_y) + footer_h + margin

    breakdown = snapshot.contribution_breakdown
    streaks = snapshot.streaks
    inventory = snapshot.repository_inventory
    starred_total = (
        snapshot.starred_repository_totals.total_starred
        if snapshot.starred_repository_totals is not None
        else 0
    )
    title_text = f"{snapshot.title} — @{snapshot.username}"
    n_owners = len(snapshot.repository_owners)
    active_repos = inventory.owned_public_non_archived_repositories
    desc_text = (
        f"Trailing {snapshot.trailing_window_days}-day GitHub engineering telemetry"
        f" for @{snapshot.username}. "
        f"{breakdown.total_public_contributions} public contributions. "
        f"Current streak: {streaks.current_days} days. "
        f"{active_repos} active public repositories across {n_owners} owners. "
        f"{inventory.stars_received} stars received. "
        f"{starred_total} public repositories starred as a research index. "
        f"{inventory.detected_languages} languages detected."
    )

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {canvas_h:.0f}" '
        f'width="100%" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(title_text)}</title>',
        f'  <desc id="desc">{escape(desc_text)}</desc>',
        "  <defs>",
        '    <linearGradient id="afqc-bg" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'      <stop offset="0%" stop-color="{tok.void}" />',
        f'      <stop offset="100%" stop-color="{tok.void_elevated}" />',
        "    </linearGradient>",
        '    <linearGradient id="afqc-accent" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'      <stop offset="0%" stop-color="{tok.quantum_pink}" />',
        f'      <stop offset="100%" stop-color="{tok.iridescent_lavender}" />',
        "    </linearGradient>",
        "    <style>",
        "      @media (prefers-reduced-motion: no-preference) {",
        "        .afqc-orb { animation: afqcPulse 16s ease-in-out infinite; }",
        "      }",
        "      @keyframes afqcPulse {",
        "        0%, 100% { opacity: 0.18; }",
        "        50% { opacity: 0.36; }",
        "      }",
        "    </style>",
        "  </defs>",
        # Background
        (
            f'  <rect width="{width}" height="{canvas_h:.0f}" '
            f'rx="24" fill="url(#afqc-bg)" />'
        ),
        # Decorative orbs (quiet, bounded, reduced-motion safe)
        (
            f'  <circle class="afqc-orb" cx="{width - 60}" cy="50" r="44" '
            f'fill="{tok.cosmic_violet}" opacity="0.18" />'
        ),
        (
            f'  <circle class="afqc-orb" cx="{width - 30}" cy="110" r="22" '
            f'fill="{tok.quantum_pink}" opacity="0.12" />'
        ),
        # Header accent line
        (
            f'  <rect x="{margin}" y="{margin}" width="120" height="3" '
            f'rx="2" fill="url(#afqc-accent)" />'
        ),
        # Header text
        _label(
            "GitHub Engineering  ·  AFQC Telemetry",
            margin,
            margin + 20,
            tok,
            size=11,
        ),
        _label(
            f"@{snapshot.username}",
            margin,
            margin + 48,
            tok,
            size=28,
            color=tok.text_primary,
            weight="700",
        ),
        _label(
            (
                f"{snapshot.window_start} → {snapshot.window_end}  ·  "
                f"{', '.join(o.login for o in snapshot.repository_owners)}  ·  "
                f"{snapshot.status.data_source}"
            ),
            margin,
            margin + 66,
            tok,
            size=10,
        ),
    ]

    # ---------- Contribution Heatmap panel ----------
    hmap_inner_x = hmap_box.x + pad
    hmap_inner_y = hmap_box.y + pad + 50
    parts.append(_card_bg(hmap_box, tok))
    parts.append(
        _label(
            "Contribution Rhythm",
            hmap_box.x + pad,
            hmap_box.y + pad + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            f"{breakdown.total_public_contributions:,} contributions  ·  "
            f"{snapshot.active_contribution_days} active days  ·  "
            f"Activity attributed to @{snapshot.username}",
            hmap_box.x + pad,
            hmap_box.y + pad + 26,
            tok,
            size=9,
        )
    )
    parts.append(
        _heatmap_month_labels(
            snapshot,
            cell_size=cell,
            gap=gap,
            origin_x=hmap_inner_x,
            origin_y=hmap_inner_y,
            tok=tok,
        )
    )
    parts.append(
        _heatmap_cells(
            snapshot,
            cell_size=cell,
            gap=gap,
            origin_x=hmap_inner_x,
            origin_y=hmap_inner_y,
            tok=tok,
        )
    )

    # ---------- Contribution Pulse panel ----------
    parts.append(_card_bg(pulse_box, tok))
    parts.append(
        _label(
            "Contribution Pulse",
            pulse_box.x + pad,
            pulse_box.y + pad + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            "Monthly totals — trailing 12 months",
            pulse_box.x + pad,
            pulse_box.y + pad + 24,
            tok,
            size=9,
        )
    )
    chart_box = LayoutBox(
        pulse_box.x,
        pulse_box.y + pad + 28,
        pulse_box.width,
        pulse_box.height - pad - 28,
    )
    parts.append(_pulse_chart(snapshot.monthly_contributions, chart_box, tok))

    # ---------- Open-source Exploration panel ----------
    parts.append(_card_bg(explore_box, tok))
    ex = explore_box.x + pad
    ey = explore_box.y + pad
    parts.append(
        _label(
            "Open-source Exploration Index",
            ex,
            ey + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            "A long-running map of tools, papers, patterns, and public systems",
            ex,
            ey + 25,
            tok,
            size=9,
        )
    )
    parts.append(
        _metric_tile(
            f"{starred_total:,}" if starred_total else "Unavailable",
            "public repositories starred · exploration, not authorship",
            ex,
            ey + 62,
            tok,
            value_color=tok.iridescent_lavender,
            value_size=28,
        )
    )

    # ---------- Engineering Activity panel ----------
    parts.append(_card_bg(activity_box, tok))
    ax = activity_box.x + pad
    ay = activity_box.y + pad
    parts.append(
        _label(
            "Engineering Activity",
            ax,
            ay + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            f"Activity attributed to @{snapshot.username} across public GitHub",
            ax,
            ay + 24,
            tok,
            size=9,
        )
    )
    tile_y = ay + 48
    col_step = (activity_box.width - 2 * pad) / 3
    metrics_row1 = [
        (f"{breakdown.public_commit_contributions:,}", "Commits", tok.quantum_pink),
        (f"{breakdown.public_pull_request_contributions:,}", "Pull requests", None),
        (f"{breakdown.public_issue_contributions:,}", "Issues", None),
    ]
    metrics_row2 = [
        (f"{breakdown.public_pull_request_review_contributions:,}", "PR reviews", None),
        (f"{streaks.current_days}d", "Current streak", tok.signal_cyan),
        (f"{streaks.longest_days}d", "Longest streak", tok.iridescent_lavender),
    ]
    for idx, (val, lbl, vc) in enumerate(metrics_row1):
        parts.append(
            _metric_tile(val, lbl, ax + idx * col_step, tile_y, tok, value_color=vc)
        )
    for idx, (val, lbl, vc) in enumerate(metrics_row2):
        parts.append(
            _metric_tile(
                val, lbl, ax + idx * col_step, tile_y + 50, tok, value_color=vc
            )
        )

    # ---------- Language Orbit panel ----------
    parts.append(_card_bg(lang_box, tok))
    parts.append(
        _label(
            "Language Orbit",
            lang_box.x + pad,
            lang_box.y + pad + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            (
                "Public non-fork repositories · "
                f"{inventory.detected_languages} languages detected"
            ),
            lang_box.x + pad,
            lang_box.y + pad + 24,
            tok,
            size=9,
        )
    )
    donut_box = LayoutBox(
        lang_box.x,
        lang_box.y + pad + 28,
        lang_box.width,
        lang_box.height - pad - 28,
    )
    parts.append(_language_donut(snapshot, donut_box, tok))

    # ---------- Engineering Signature radar ----------
    parts.append(_card_bg(radar_box, tok))
    parts.append(
        _label(
            "Engineering Signature",
            radar_box.x + pad,
            radar_box.y + pad + 12,
            tok,
            size=12,
            color=tok.text_primary,
            weight="600",
        )
    )
    parts.append(
        _label(
            "GitHub activity dimensions — not a proficiency score",
            radar_box.x + pad,
            radar_box.y + pad + 24,
            tok,
            size=9,
        )
    )
    radar_inner = LayoutBox(
        radar_box.x,
        radar_box.y + pad + 36,
        radar_box.width,
        radar_box.height - pad - 36,
    )
    parts.append(_radar_chart(snapshot, radar_inner, tok))

    # Metric constellation footer strip
    owners_str = " · ".join(o.login for o in snapshot.repository_owners)
    if mobile:
        footer_items = [
            (f"{inventory.owned_public_non_archived_repositories}", "Active repos"),
            (f"{starred_total:,}", "Starred repos"),
            (f"{inventory.detected_languages}", "Languages"),
        ]
    else:
        footer_items = [
            (f"{inventory.owned_public_non_archived_repositories}", "Active repos"),
            (f"{inventory.total_public_repositories}", "Total repos"),
            (f"{starred_total:,}", "Starred repos"),
            (f"{inventory.stars_received:,}", "Stars received"),
            (f"{inventory.public_releases_past_year}", "Releases / yr"),
            (f"{inventory.detected_languages}", "Languages"),
        ]
    footer_y = canvas_h - footer_h + 10
    parts.append(
        _label(
            f"Ecosystem: {owners_str}",
            margin,
            footer_y,
            tok,
            size=9,
        )
    )
    fi_x = margin
    fi_step = (width - 2 * margin) / max(1, len(footer_items))
    for idx, (val, lbl) in enumerate(footer_items):
        fx = fi_x + (idx + 0.5) * fi_step
        parts.append(
            f'<text x="{fx:.0f}" y="{footer_y + 20:.0f}" '
            f'fill="{tok.text_primary}" font-size="10" font-weight="600" '
            f'text-anchor="middle" font-family="{_FONT_STACK}">'
            f"{escape(val)}</text>"
        )
        parts.append(
            f'<text x="{fx:.0f}" y="{footer_y + 31:.0f}" '
            f'fill="{tok.text_muted}" font-size="8" '
            f'text-anchor="middle" font-family="{_FONT_STACK}">'
            f"{escape(lbl)}</text>"
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"
