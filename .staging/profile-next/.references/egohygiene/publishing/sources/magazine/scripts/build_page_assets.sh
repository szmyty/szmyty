#!/usr/bin/env bash
#
# Production-grade page build pipeline
# Updated for scripttool, wrap (HTML), and afterwriting (PDF)
#

set -euo pipefail

PRINT_DPI=300
WEB_WIDTH=1080
INSTAGRAM_WIDTH=1080
INSTAGRAM_HEIGHT=1350

log_info()      { printf "ℹ️  %s\n" "$1"; }
log_process()   { printf "🔎 %s\n" "$1"; }
log_warn()      { printf "⚠️  %s\n" "$1" >&2; }
log_error()     { printf "❌ %s\n" "$1" >&2; }
log_success()   { printf "✅ %s\n" "$1"; }

ensure_dir() {
  [ -d "$1" ] || mkdir -p "$1"
}

magick_convert() {
  if command -v magick >/dev/null 2>&1; then
    magick "$@"
  else
    convert "$@"
  fi
}

validate_dependencies() {
  local missing=()

  command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1 || missing+=("imagemagick")
  command -v img2pdf >/dev/null 2>&1 || missing+=("img2pdf")
  command -v afterwriting >/dev/null 2>&1 || missing+=("afterwriting")
  command -v scripttool >/dev/null 2>&1 || missing+=("scripttool")
  command -v wrap >/dev/null 2>&1 || missing+=("wrap")

  if [ "${#missing[@]}" -gt 0 ]; then
    log_error "Missing dependencies:"
    for dep in "${missing[@]}"; do printf "  - %s\n" "$dep"; done
    exit 1
  fi
}

base_name() {
  local f
  f="$(basename -- "$1")"
  printf "%s" "${f%.png}"
}

export_visual_formats() {
  local input="$1"
  local exports="$2"
  local base="$3"

  log_process "Generating JPG..."
  magick_convert "$input" -quality 95 "$exports/${base}.jpg"

  log_process "Generating Web JPG..."
  magick_convert "$input" -resize "${WEB_WIDTH}x" -quality 85 "$exports/${base}.web.jpg"

  log_process "Generating Instagram 4:5..."
  magick_convert "$input" \
    -resize "${INSTAGRAM_WIDTH}x${INSTAGRAM_HEIGHT}^" \
    -gravity center \
    -extent "${INSTAGRAM_WIDTH}x${INSTAGRAM_HEIGHT}" \
    -quality 90 \
    "$exports/${base}.instagram.jpg"

  log_process "Generating TIFF..."
  magick_convert "$input" \
    -density "$PRINT_DPI" \
    -units PixelsPerInch \
    -compress lzw \
    "$exports/${base}.tiff"

  log_process "Generating WebP..."
  magick_convert "$input" -quality 90 "$exports/${base}.webp"

  log_process "Generating Full-bleed PDF..."
  img2pdf "$input" -o "$exports/${base}.fullbleed.pdf"

  cp "$exports/${base}.fullbleed.pdf" \
     "$(dirname "$input")/${base}.pdf"

  log_success "Visual exports complete"
}

export_html_preview() {
  local input="$1"
  local exports="$2"
  local base="$3"

  log_process "Generating self-contained HTML preview..."

  # Convert PNG to Base64
  local base64_data
  base64_data=$(base64 < "$input" | tr -d '\n')

  # Determine MIME type based on file format
  local mime_type="image/png"
  if [[ "$input" =~ \.jpg$ ]] || [[ "$input" =~ \.jpeg$ ]]; then
    mime_type="image/jpeg"
  fi

  # Generate self-contained HTML with embedded image
  cat > "$exports/${base}.html" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>$base</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html,body{margin:0;padding:0;background:black;height:100%}
body{display:flex;align-items:center;justify-content:center}
img{max-width:100%;max-height:100%;object-fit:contain}
</style>
</head>
<body>
<img src="data:$mime_type;base64,$base64_data" alt="$base">
</body>
</html>
EOF

  log_success "HTML preview generated"
}

export_fountain() {
  local page_dir="$1"
  local screenplay_dir="$page_dir/screenplay"

  ensure_dir "$screenplay_dir"

  # Find only original fountain files, ignoring .pretty.fountain
  find "$screenplay_dir" -maxdepth 1 -type f -name "*.fountain" ! -name "*.pretty.fountain" | while read -r f; do
    local base
    base="$(basename "$f" .fountain)"

    log_process "Rendering Fountain PDF via Afterwriting..."
    afterwriting \
      --source "$f" \
      --pdf "$screenplay_dir/${base}.pdf" \
      --overwrite

    log_process "Converting to Industry Formats (FDX, FadeIn, OSF)..."
    scripttool fountain2fdx "$f" "$screenplay_dir/${base}.fdx"
    scripttool fountain2fadein "$f" "$screenplay_dir/${base}.fadein"
    scripttool fountain2osf "$f" "$screenplay_dir/${base}.osf"

    log_process "Generating Pretty Print and JSON..."
    scripttool fountainfmt "$f" > "$screenplay_dir/${base}.pretty.fountain"

    log_process "Generating Pretty-Printed JSON..."
    # Pipe the scripttool output into jq for indentation
    scripttool fountain2json "$f" | jq '.' > "$screenplay_dir/${base}.json"
    
    log_process "Exporting HTML via Wrap..."
    cat "$f" | wrap html -o "$screenplay_dir/${base}.html"

    log_success "Fountain suite rendered: $base"
  done
}

generate_meta() {
  local input="$1"
  local page_dir="$2"
  local exports="$3"
  local base="$4"

  log_process "Generating meta.json..."

  local width height format size
  width=$(magick identify -format "%w" "$input")
  height=$(magick identify -format "%h" "$input")
  format=$(magick identify -format "%m" "$input")
  size=$(stat -f%z "$input" 2>/dev/null || stat -c%s "$input")

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  cat > "$page_dir/meta.json" <<EOF
{
  "page_id": "$base",
  "status": "locked",
  "generated_at": "$timestamp",
  "master_image": {
    "filename": "$(basename "$input")",
    "format": "$format",
    "width_px": $width,
    "height_px": $height,
    "file_size_bytes": $size
  }
}
EOF

  log_success "meta.json generated"
}

build_page() {
  local input="$1"

  [ -f "$input" ] || { log_error "File not found: $input"; exit 1; }

  local page_dir
  page_dir="$(dirname "$input")"

  local exports="$page_dir/exports"
  ensure_dir "$exports"

  local base
  base="$(base_name "$input")"

  log_info "Building: $base"

  export_visual_formats "$input" "$exports" "$base"
  export_html_preview "$input" "$exports" "$base"
  export_fountain "$page_dir"
  generate_meta "$input" "$page_dir" "$exports" "$base"

  log_success "Build complete for $base"
}

build_all() {
  find "$1" -type f \( -name "*.front.final.png" -o -name "*.front.page.png" \) | while read -r file; do
    build_page "$file"
  done
}

main() {
  validate_dependencies

  if [ "$#" -lt 1 ]; then
    log_error "Usage: build_page_assets.sh <page.png> | --all <edition>"
    exit 1
  fi

  if [ "$1" = "--all" ]; then
    build_all "$2"
  else
    build_page "$1"
  fi
}

main "$@"