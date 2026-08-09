#!/bin/bash
# Card Template Generator Script
# Creates scaffolding for new card types:
# - Fetch script
# - Generator script
# - GitHub Actions workflow
# - README markers
#
# Usage: ./scripts/new-card.sh <card-name>
# Example: ./scripts/new-card.sh spotify

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print usage information
usage() {
    cat << EOF
Usage: $(basename "$0") <card-name>

Creates scaffolding for a new card type including:
  - Fetch script (scripts/fetch-<name>.sh)
  - Generator script (scripts/generate-<name>-card.py)
  - GitHub Actions workflow (.github/workflows/<name>-card.yml)
  - README markers

Arguments:
  card-name    Name of the new card (lowercase, alphanumeric with hyphens)
               Examples: spotify, github-stats, strava

Options:
  -h, --help   Show this help message

Examples:
  $(basename "$0") spotify
  $(basename "$0") github-stats
  $(basename "$0") strava
EOF
}

# Validate card name
validate_card_name() {
    local name="$1"
    
    if [ -z "$name" ]; then
        echo -e "${RED}Error: Card name is required${NC}" >&2
        usage >&2
        exit 1
    fi
    
    # Check for valid characters (lowercase letters, numbers, hyphens)
    if ! [[ "$name" =~ ^[a-z][a-z0-9-]*$ ]]; then
        echo -e "${RED}Error: Card name must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens${NC}" >&2
        exit 1
    fi
    
    # Check for double hyphens or trailing hyphens
    if [[ "$name" =~ -- ]] || [[ "$name" =~ -$ ]]; then
        echo -e "${RED}Error: Card name cannot contain double hyphens or end with a hyphen${NC}" >&2
        exit 1
    fi
}

# Convert card name to different formats
to_upper_snake() {
    echo "$1" | tr '[:lower:]-' '[:upper:]_'
}

to_title_case() {
    echo "$1" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g'
}

# Generate fetch script
generate_fetch_script() {
    local name="$1"
    local upper_name
    upper_name=$(to_upper_snake "$name")
    local title_name
    title_name=$(to_title_case "$name")
    local output_file="${SCRIPT_DIR}/fetch-${name}.sh"
    
    if [ -f "$output_file" ]; then
        echo -e "${YELLOW}Warning: Fetch script already exists: ${output_file}${NC}" >&2
        return 1
    fi
    
    cat > "$output_file" << 'FETCH_TEMPLATE'
#!/bin/bash
# Script to fetch __TITLE_NAME__ data
# This script:
# 1. Fetches data from the __TITLE_NAME__ API
# 2. Parses and transforms the response
# 3. Outputs data as JSON for card generation

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

OUTPUT_DIR="${OUTPUT_DIR:-__NAME__}"

# TODO: Add your API token environment variable
# __UPPER_NAME___TOKEN="${__UPPER_NAME___TOKEN:-}"

# Function to fetch data from the API
fetch_data() {
    echo "Fetching __TITLE_NAME__ data..." >&2
    
    # TODO: Implement API call
    # Example:
    # local response
    # response=$(curl -sf "https://api.example.com/data" \
    #     -H "Authorization: Bearer ${__UPPER_NAME___TOKEN}" \
    #     -H "User-Agent: GitHub-Profile-Card/1.0") || {
    #     echo "Error: Failed to fetch __TITLE_NAME__ data" >&2
    #     return 1
    # }
    # echo "$response"
    
    echo "Error: API fetch not implemented" >&2
    return 1
}

# Main execution
main() {
    # TODO: Add API token validation
    # if [ -z "${__UPPER_NAME___TOKEN:-}" ]; then
    #     echo "Error: __UPPER_NAME___TOKEN environment variable is required" >&2
    #     exit 1
    # fi
    
    # Fetch data
    local data
    data=$(fetch_data) || {
        echo "Error: Failed to fetch __TITLE_NAME__ data" >&2
        exit 1
    }
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Get current UTC time for update timestamp
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # TODO: Transform and output the data
    # Example output structure:
    jq -n \
        --arg updated_at "$updated_at" \
        '{
            updated_at: $updated_at
        }'
}

main "$@"
FETCH_TEMPLATE

    # Replace placeholders
    sed -i "s/__NAME__/${name}/g" "$output_file"
    sed -i "s/__UPPER_NAME__/${upper_name}/g" "$output_file"
    sed -i "s/__TITLE_NAME__/${title_name}/g" "$output_file"
    
    chmod +x "$output_file"
    echo -e "${GREEN}Created fetch script: ${output_file}${NC}"
}

# Generate Python generator script
generate_generator_script() {
    local name="$1"
    local title_name
    title_name=$(to_title_case "$name")
    local output_file="${SCRIPT_DIR}/generate-${name}-card.py"
    
    if [ -f "$output_file" ]; then
        echo -e "${YELLOW}Warning: Generator script already exists: ${output_file}${NC}" >&2
        return 1
    fi
    
    cat > "$output_file" << 'GENERATOR_TEMPLATE'
#!/usr/bin/env python3
"""
Generate a styled SVG card for __TITLE_NAME__ data.
This script reads __TITLE_NAME__ metadata from JSON and creates an SVG card.
"""

import sys
from pathlib import Path

from lib.utils import (
    escape_xml,
    load_and_validate_json,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    format_timestamp_local,
)


def generate_svg(
    # TODO: Add parameters for your card data
    updated_at: str,
) -> str:
    """Generate SVG card markup."""
    
    # Load theme values
    theme = load_theme()
    bg_gradient = get_theme_gradient("background.default")
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    bg_primary = bg_gradient[0]
    bg_secondary = bg_gradient[1]
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    
    # Card dimensions from theme
    # TODO: Add your card dimensions to config/theme.json
    card_width = get_theme_card_dimension("widths", "__NAME__")
    card_height = get_theme_card_dimension("heights", "__NAME__")
    border_radius = get_theme_border_radius("xl")
    
    # Font sizes from theme
    font_size_base = get_theme_font_size("base")
    font_size_lg = get_theme_font_size("lg")
    font_size_xl = get_theme_font_size("xl")
    font_size_2xl = get_theme_font_size("2xl")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_primary}"/>
      <stop offset="100%" style="stop-color:{bg_secondary}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{glow_std}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Header -->
  <g transform="translate(20, 35)">
    <text font-family="{font_family}" font-size="{font_size_2xl}" fill="{accent_teal}" font-weight="600" filter="url(#glow)">
      🎵 __TITLE_NAME__
    </text>
  </g>

  <!-- TODO: Add your card content here -->
  <g transform="translate(20, 70)">
    <text font-family="{font_family}" font-size="{font_size_lg}" fill="{text_primary}">
      Card content goes here
    </text>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate(20, {card_height - 25})">
    <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_muted}">
      Updated: {updated_at}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="{card_width - 20}" y="15" width="4" height="{card_height - 30}" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-__NAME__-card.py <metadata.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "__NAME__/__NAME__-card.svg"

    # Read and validate metadata
    # TODO: Create a JSON schema for your card data in schemas/__NAME__.schema.json
    # metadata = load_and_validate_json(metadata_path, "__NAME__", "__TITLE_NAME__ metadata file")
    
    # For now, just load without validation
    from lib.utils import load_json
    metadata = load_json(metadata_path, "__TITLE_NAME__ metadata file")

    # Format updated_at to local time for display
    updated_at_raw = metadata.get("updated_at", "")
    updated_at_display = format_timestamp_local(updated_at_raw) if updated_at_raw else ""

    # Generate SVG
    svg = generate_svg(
        # TODO: Pass your card data here
        updated_at=updated_at_display,
    )

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated __TITLE_NAME__ SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
GENERATOR_TEMPLATE

    # Replace placeholders
    sed -i "s/__NAME__/${name}/g" "$output_file"
    sed -i "s/__TITLE_NAME__/${title_name}/g" "$output_file"
    
    chmod +x "$output_file"
    echo -e "${GREEN}Created generator script: ${output_file}${NC}"
}

# Generate GitHub Actions workflow
generate_workflow() {
    local name="$1"
    local upper_name
    upper_name=$(to_upper_snake "$name")
    local title_name
    title_name=$(to_title_case "$name")
    local output_file="${REPO_ROOT}/.github/workflows/${name}-card.yml"
    
    if [ -f "$output_file" ]; then
        echo -e "${YELLOW}Warning: Workflow already exists: ${output_file}${NC}" >&2
        return 1
    fi
    
    cat > "$output_file" << 'WORKFLOW_TEMPLATE'
name: __TITLE_NAME__ Card

on:
  schedule:
    # Run once per day at 8 AM UTC
    - cron: '0 8 * * *'
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - 'scripts/fetch-__NAME__.sh'
      - 'scripts/generate-__NAME__-card.py'
      - 'scripts/update_readme.py'
      - 'scripts/lib/utils.py'
      - 'config/theme.json'
      - '.github/workflows/__NAME__-card.yml'

concurrency:
  group: profile-update
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  update-__NAME__-card:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y jq curl

      - name: Fetch __TITLE_NAME__ data
        id: fetch
        env:
          # TODO: Add your API token secret
          # __UPPER_NAME___TOKEN: ${{ secrets.__UPPER_NAME___TOKEN }}
          OUTPUT_DIR: __NAME__
        run: |
          chmod +x scripts/fetch-__NAME__.sh
          mkdir -p __NAME__
          
          if ! scripts/fetch-__NAME__.sh > __NAME__/metadata.json; then
            echo "Error: Failed to fetch __TITLE_NAME__ data"
            exit 1
          fi
          
          # Validate the metadata file
          if ! jq empty __NAME__/metadata.json 2>/dev/null; then
            echo "Error: Invalid JSON in metadata file"
            exit 1
          fi
          
          echo "__TITLE_NAME__ data fetched successfully"
          cat __NAME__/metadata.json

      - name: Generate __TITLE_NAME__ SVG card
        run: |
          python scripts/generate-__NAME__-card.py __NAME__/metadata.json __NAME__/__NAME__-card.svg

      - name: Optimize SVG with SVGO
        run: |
          npm install -g svgo
          ORIGINAL_SIZE=$(stat -c%s __NAME__/__NAME__-card.svg)
          if [ "$ORIGINAL_SIZE" -gt 0 ]; then
            svgo __NAME__/__NAME__-card.svg -o __NAME__/__NAME__-card.svg
            OPTIMIZED_SIZE=$(stat -c%s __NAME__/__NAME__-card.svg)
            echo "SVG optimized: ${ORIGINAL_SIZE} bytes → ${OPTIMIZED_SIZE} bytes ($(( 100 - OPTIMIZED_SIZE * 100 / ORIGINAL_SIZE ))% reduction)"
          else
            echo "Warning: SVG file is empty, skipping optimization"
          fi

      - name: Update README with __TITLE_NAME__ card
        run: |
          python scripts/update_readme.py \
            --marker __UPPER_NAME__-CARD \
            --content "![__TITLE_NAME__](./__NAME__/__NAME__-card.svg)"

      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # Add all relevant files
          git add __NAME__/metadata.json __NAME__/__NAME__-card.svg README.md
          
          # Check if there are changes to commit
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "🔄 Update __TITLE_NAME__ card"
            git push
          fi
WORKFLOW_TEMPLATE

    # Replace placeholders
    sed -i "s/__NAME__/${name}/g" "$output_file"
    sed -i "s/__UPPER_NAME__/${upper_name}/g" "$output_file"
    sed -i "s/__TITLE_NAME__/${title_name}/g" "$output_file"
    
    echo -e "${GREEN}Created workflow: ${output_file}${NC}"
}

# Add README markers
add_readme_markers() {
    local name="$1"
    local upper_name
    upper_name=$(to_upper_snake "$name")
    local title_name
    title_name=$(to_title_case "$name")
    local readme_file="${REPO_ROOT}/README.md"
    
    # Check if markers already exist
    if grep -q "<!-- ${upper_name}-CARD:START -->" "$readme_file" 2>/dev/null; then
        echo -e "${YELLOW}Warning: README markers already exist for ${name}${NC}" >&2
        return 1
    fi
    
    # Add markers at the end of the README
    cat >> "$readme_file" << EOF

## 🎵 ${title_name}

<!-- ${upper_name}-CARD:START -->
![${title_name}](./${name}/${name}-card.svg)
<!-- ${upper_name}-CARD:END -->
EOF
    
    echo -e "${GREEN}Added README markers for: ${name}${NC}"
}

# Create output directory
create_output_directory() {
    local name="$1"
    local output_dir="${REPO_ROOT}/${name}"
    
    if [ -d "$output_dir" ]; then
        echo -e "${YELLOW}Warning: Output directory already exists: ${output_dir}${NC}" >&2
        return 0
    fi
    
    mkdir -p "$output_dir"
    touch "${output_dir}/.gitkeep"
    echo -e "${GREEN}Created output directory: ${output_dir}${NC}"
}

# Main function
main() {
    # Handle help flag
    if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
        usage
        exit 0
    fi
    
    # Check for required argument
    if [ $# -lt 1 ]; then
        echo -e "${RED}Error: Card name is required${NC}" >&2
        usage >&2
        exit 1
    fi
    
    local card_name="$1"
    
    # Validate card name
    validate_card_name "$card_name"
    
    echo -e "${BLUE}Creating scaffolding for card: ${card_name}${NC}"
    echo ""
    
    local success_count=0
    local total_count=5
    
    # Create output directory
    create_output_directory "$card_name" && ((success_count++)) || true
    
    # Generate fetch script
    generate_fetch_script "$card_name" && ((success_count++)) || true
    
    # Generate generator script
    generate_generator_script "$card_name" && ((success_count++)) || true
    
    # Generate workflow
    generate_workflow "$card_name" && ((success_count++)) || true
    
    # Add README markers
    add_readme_markers "$card_name" && ((success_count++)) || true
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Scaffolding complete!${NC} (${success_count}/${total_count} items created)"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Edit scripts/fetch-${card_name}.sh to implement API fetching"
    echo "  2. Edit scripts/generate-${card_name}-card.py to customize the SVG card"
    echo "  3. Add card dimensions to config/theme.json:"
    echo "     - cards.widths.${card_name}: <width>"
    echo "     - cards.heights.${card_name}: <height>"
    echo "  4. (Optional) Create schemas/${card_name}.schema.json for data validation"
    echo "  5. Add any required secrets to GitHub repository settings"
    echo "  6. Test locally: ./scripts/fetch-${card_name}.sh > ${card_name}/metadata.json"
    echo "  7. Test generator: python scripts/generate-${card_name}-card.py ${card_name}/metadata.json"
    echo ""
}

main "$@"
