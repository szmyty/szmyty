#!/usr/bin/env bash

set -euo pipefail

COVER_DIR="$1"
MASTER_IMAGE="$COVER_DIR/cover.front.final.png"
META_FILE="$COVER_DIR/meta.json"

if [ ! -f "$MASTER_IMAGE" ]; then
  printf "❌ Master image not found: %s\n" "$MASTER_IMAGE"
  exit 1
fi

printf "🔎 Extracting metadata from master image...\n"

WIDTH=$(magick identify -format "%w" "$MASTER_IMAGE")
HEIGHT=$(magick identify -format "%h" "$MASTER_IMAGE")
FORMAT=$(magick identify -format "%m" "$MASTER_IMAGE")
FILE_SIZE=$(stat -f%z "$MASTER_IMAGE" 2>/dev/null || stat -c%s "$MASTER_IMAGE")

ASPECT_RATIO=$(awk "BEGIN {printf \"%.3f\", $WIDTH/$HEIGHT}")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

printf "📝 Writing meta.json...\n"

cat > "$META_FILE" <<EOF
{
  "page_id": "cover.front",
  "status": "locked",
  "generated_at": "$TIMESTAMP",

  "master_image": {
    "filename": "cover.front.final.png",
    "format": "$FORMAT",
    "width_px": $WIDTH,
    "height_px": $HEIGHT,
    "aspect_ratio": "$ASPECT_RATIO",
    "file_size_bytes": $FILE_SIZE
  },

  "exports_present": [
$(find "$COVER_DIR/exports" -type f 2>/dev/null | sed "s|.*/||" | sed 's/^/    "/; s/$/",/' | sed '$ s/,$//')
  ],

  "animation_present": $( [ -f "$COVER_DIR/cover.front.animation.mp4" ] && echo "true" || echo "false" ),

  "notes": "Generated automatically by pipeline."
}
EOF

printf "✅ meta.json generated at %s\n" "$META_FILE"
