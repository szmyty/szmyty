#!/usr/bin/env bash
#
# Post-processor for Fountain-generated HTML files
# Fixes common htmlhint validation issues
#
# Usage: ./fix_fountain_html.sh <input.html>

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <input.html>"
    exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File not found: $INPUT_FILE"
    exit 1
fi

echo "Fixing HTML lint issues in: $INPUT_FILE"

# Create backup
cp "$INPUT_FILE" "$INPUT_FILE.bak"

# Fix 1: Add title tag if missing
if ! grep -q "<title>" "$INPUT_FILE"; then
    echo "  → Adding missing <title> tag"
    sed -i 's|</head>|    <title>Ego Hygiene - Cover</title>\n</head>|' "$INPUT_FILE"
fi

# Fix 2: Convert single quotes to double quotes for attributes
echo "  → Converting single-quoted attributes to double quotes"
# This is a simplified approach - may need refinement for edge cases
sed -i "s/id='\([^']*\)'/id=\"\1\"/g" "$INPUT_FILE"
sed -i "s/class='\([^']*\)'/class=\"\1\"/g" "$INPUT_FILE"
sed -i "s/style='\([^']*\)'/style=\"\1\"/g" "$INPUT_FILE"

# Fix 3: Remove duplicate IDs on nested elements (heuristic)
# This finds patterns like: id="X"><span ... id="X"> and removes the inner id
echo "  → Checking for duplicate IDs"
# Match pattern: id="ANYTHING"><span ... id="SAME_THING" and remove the inner id
sed -i -E 's/id="(sourceline_[0-9]+)">([^<]*<span[^>]*) id="\1"/id="\1">\2/g' "$INPUT_FILE"
# Generic pattern for any duplicate ID (not just sourceline_*)
sed -i -E 's/id="([^"]+)">([^<]*<span[^>]*) id="\1"/id="\1">\2/g' "$INPUT_FILE"

# Fix 4: Fix common double-closing tags
echo "  → Fixing unpaired tags"
sed -i 's|</p></p>|</p>|g' "$INPUT_FILE"

echo "✓ HTML fixes applied"
echo "  Backup saved as: $INPUT_FILE.bak"

# Validate with htmlhint if available
if command -v htmlhint &> /dev/null; then
    echo ""
    echo "Running htmlhint validation..."
    htmlhint "$INPUT_FILE"
else
    echo ""
    echo "⚠ htmlhint not found - skipping validation"
    echo "  Install with: npm install -g htmlhint"
fi
