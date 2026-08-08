#!/usr/bin/env bash
#
# magazine - Holistic Production Engine
#
# Description:
#   Production build system for magazine pages and editions.
#
# Commands:
#   manifest  <edition_path>
#   page      <page_path>
#   edition   <edition_path> [--skip-existing]
#   finalize  <edition_path> [--force]
#
# Requirements:
#   magick, img2pdf, jq, exiftool, zip
#
# Author: Play Function
#

# ------------------------------------------------------------
# Strict Mode
# ------------------------------------------------------------
set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

# ------------------------------------------------------------
# Global Configuration
# ------------------------------------------------------------
readonly PRINT_DPI=300
readonly WEB_WIDTH=1080
readonly INSTAGRAM_WIDTH=1080
readonly INSTAGRAM_HEIGHT=1350

# ------------------------------------------------------------
# AI Configuration
# ------------------------------------------------------------
readonly FOUNTAIN_AI_RUNTIME="ollama"
readonly FOUNTAIN_AI_MODEL="qwen3-vl-fountain:latest"
readonly FOUNTAIN_MODELFILE_PATH="magazine/ai/fountain.modelfile"

# ------------------------------------------------------------
# Color Handling (NO_COLOR compatible)
# ------------------------------------------------------------
if [[ -z "${NO_COLOR:-}" ]]; then
    readonly COLOR_BLUE="\e[34m"
    readonly COLOR_YELLOW="\e[33m"
    readonly COLOR_GREEN="\e[32m"
    readonly COLOR_RED="\e[31m"
    readonly COLOR_RESET="\e[0m"
else
    readonly COLOR_BLUE=""
    readonly COLOR_YELLOW=""
    readonly COLOR_GREEN=""
    readonly COLOR_RED=""
    readonly COLOR_RESET=""
fi

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

log_info() {
    printf "%b[%s] ℹ INFO  %s%b\n" \
        "$COLOR_BLUE" "$(_timestamp)" "$1" "$COLOR_RESET"
}

log_warn() {
    printf "%b[%s] ⚠ WARN  %s%b\n" \
        "$COLOR_YELLOW" "$(_timestamp)" "$1" "$COLOR_RESET" >&2
}

log_success() {
    printf "%b[%s] ✔ SUCCESS  %s%b\n" \
        "$COLOR_GREEN" "$(_timestamp)" "$1" "$COLOR_RESET"
}

log_error() {
    printf "%b[%s] ✖ ERROR  %s%b\n" \
        "$COLOR_RED" "$(_timestamp)" "$1" "$COLOR_RESET" >&2
}

# ------------------------------------------------------------
# Trap / Cleanup Handling
# ------------------------------------------------------------
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script exited with code $exit_code"
    fi
    exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# ------------------------------------------------------------
# Dependency Shield
# ------------------------------------------------------------
check_dependencies() {
    local dependencies=(
        "magick"
        "img2pdf"
        "jq"
        "exiftool"
        "zip"
    )

    local missing=()

    for tool in "${dependencies[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing+=("$tool")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Install with: brew install imagemagick img2pdf jq exiftool"
        exit 1
    fi
}

generate_image_hash() {
    local image_path="$1"

    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$image_path" | awk '{print $1}'
    else
        shasum -a 256 "$image_path" | awk '{print $1}'
    fi
}

# ------------------------------------------------------------
# Asset Generators (Atomic)
# ------------------------------------------------------------
gen_jpg()           { magick "$1" -quality 95 "$2/page.jpg"; }
gen_webp()          { magick "$1" -quality 90 "$2/page.webp"; }
gen_web_jpg()       { magick "$1" -resize "${WEB_WIDTH}x" -quality 85 "$2/page.web.jpg"; }
gen_instagram()     { magick "$1" -resize "${INSTAGRAM_WIDTH}x${INSTAGRAM_HEIGHT}^" -gravity center -extent "${INSTAGRAM_WIDTH}x${INSTAGRAM_HEIGHT}" -quality 90 "$2/page.instagram.jpg"; }
gen_tiff()          { magick "$1" -density "$PRINT_DPI" -units PixelsPerInch -compress lzw "$2/page.tiff"; }
gen_fullbleed_pdf() { img2pdf "$1" -o "$2/page.fullbleed.pdf"; }

gen_screenplay_pdf()  { afterwriting --source "$1" --pdf "$2/page.pdf" --overwrite; }
gen_screenplay_json() { scripttool fountain2json "$1" | jq '.' > "$2/page.json"; }
gen_screenplay_html() { wrap html "$1" -o "$2/page.html"; }

# ------------------------------------------------------------
# Metadata Generation
# ------------------------------------------------------------
gen_page_meta() {
    local page_dir="$1"
    local img_in="$page_dir/page.png"
    local meta_out="$page_dir/meta.json"

    local slug
    slug="$(basename "$page_dir")"

    local idx
    idx="$(printf "%s" "$slug" | cut -d'_' -f1)"

    local exif_json="{}"
    if [[ -f "$img_in" ]]; then
        if ! exif_json="$(exiftool -j -g1 "$img_in" | jq '.[0]' 2>/dev/null)"; then
            exif_json="{}"
        fi
    fi

    jq -n \
        --arg id "$slug" \
        --arg idx "$idx" \
        --arg ts "$(_timestamp)" \
        --argjson exif "$exif_json" \
        '{
            page_id: $id,
            sequence_index: $idx,
            generated_at: $ts,
            project_context: {
                author: "Alan R Szmyt",
                alias: "Play Function",
                location: "Wilmington, MA"
            },
            raw_exif: $exif
        }' > "$meta_out"
}

ensure_ai_runtime() {
    if ! command -v "$FOUNTAIN_AI_RUNTIME" >/dev/null 2>&1; then
        log_error "AI runtime '$FOUNTAIN_AI_RUNTIME' not found."
        log_info "Install Ollama from: https://ollama.com"
        exit 1
    fi
}

ensure_ai_model() {
    local model="$FOUNTAIN_AI_MODEL"

    if ! "$FOUNTAIN_AI_RUNTIME" show "$model" >/dev/null 2>&1; then
        log_warn "AI model '$model' not found. Building from Modelfile..."

        if [[ ! -f "$FOUNTAIN_MODELFILE_PATH" ]]; then
            log_error "Modelfile not found at $FOUNTAIN_MODELFILE_PATH"
            exit 1
        fi

        "$FOUNTAIN_AI_RUNTIME" create "$model" -f "$FOUNTAIN_MODELFILE_PATH"
        log_success "Model '$model' created successfully."
    fi
}


generate_fountain_from_image() {
    local page_dir="$1"
    local image_path="$page_dir/page.png"
    local fountain_path="$page_dir/page.fountain"
    local meta_path="$page_dir/meta.json"

    ensure_ai_runtime
    ensure_ai_model

    if [[ ! -f "$image_path" ]]; then
        return
    fi

    local current_hash
    current_hash="$(generate_image_hash "$image_path")"

    local previous_hash=""
    if [[ -f "$meta_path" ]]; then
        previous_hash="$(jq -r '.image_hash // empty' "$meta_path" 2>/dev/null || true)"
    fi

    if [[ -f "$fountain_path" && "$current_hash" == "$previous_hash" ]]; then
        log_info "Fountain script up-to-date. Skipping generation."
        return
    fi

    log_info "Generating fountain script from artwork..."

    local prompt
    prompt=$(cat <<EOF
You are generating a Fountain screenplay for a printed magazine page.

You must follow this structure exactly.

1. Begin with metadata header:
Title: Ego Hygiene
Credit: Written & Designed by Alan Szmyt
Draft date: <today's date>
Source: Edition 1 – Orientation

2. Add a blank line.

3. Write a proper Fountain scene heading in this format:
INT. PRINTED MAGAZINE – <PAGE TITLE> – TIMELESS

4. Describe the page layout visually in short, deliberate lines.
- Do NOT over-explain.
- Do NOT interpret symbolism.
- Do NOT speculate.
- Describe only what is visible.

5. Transcribe all clearly visible text exactly as written on the page.
- Preserve capitalization.
- Preserve punctuation.
- Keep formatting clean.

6. End with 2–4 minimal reflective lines in the same tone as:
"Instruction, embedded in artifact."
"Stillness, applied."

Rules:
- No markdown.
- No commentary.
- No explanation.
- No bullet points.
- Output only valid Fountain script text.
- Keep language restrained and cinematic.
- Avoid flowery or spiritual interpretation.

Be precise.
Be minimal.
Be structured.
EOF
)
    "$FOUNTAIN_AI_RUNTIME" run "$FOUNTAIN_AI_MODEL" \
        --think false \
        --hidethinking \
        "$image_path" \
        "$prompt" \
        > "$fountain_path"

    # Update meta.json with hash + AI info
    jq \
        --arg hash "$current_hash" \
        --arg model "$FOUNTAIN_AI_MODEL" \
        --arg ts "$(_timestamp)" \
        '.image_hash = $hash
        | .fountain_generated_by = $model
        | .fountain_generated_at = $ts' \
        "$meta_path" > "$meta_path.tmp"

    mv "$meta_path.tmp" "$meta_path"

    log_success "Fountain script generated."
}


# ------------------------------------------------------------
# Edition Finalization
# ------------------------------------------------------------
finalize_edition() {
    local edition_dir="$1"
    local force_flag="${2:-}"
    local pub_dir="$edition_dir/publishing"
    local stage_dir="$edition_dir/artifacts/final_build_stage"

    log_info "Initializing Final Assembly: $(basename "$edition_dir")"

    mapfile -t page_dirs < <(
        find "$edition_dir/pages" -maxdepth 1 -mindepth 1 -type d | sort
    )

    for p in "${page_dirs[@]}"; do
        if [[ ! -f "$p/page.png" ]]; then
            if [[ "$force_flag" == "--force" ]]; then
                log_warn "Missing page.png in $(basename "$p"), continuing due to --force"
            else
                log_error "Validation failed: Missing page.png in $(basename "$p")"
                exit 1
            fi
        fi
    done

    mkdir -p "$pub_dir/digital" "$pub_dir/print" "$stage_dir"
    rm -f "$stage_dir"/* 2>/dev/null || true

    log_info "Staging masters..."
    for p in "${page_dirs[@]}"; do
        local slug
        slug="$(basename "$p")"

        [[ -f "$p/page.png" ]] && cp "$p/page.png" "$stage_dir/$slug.png"
        [[ -f "$p/page.tiff" ]] && cp "$p/page.tiff" "$stage_dir/$slug.tiff"
    done

    log_info "Building CBZ..."
    (
        cd "$stage_dir"
        zip -q -X "../../publishing/digital/comic.cbz" ./*.png -x "*.DS_Store"
    )

    log_info "Building Reader PDF..."
    img2pdf "$stage_dir"/*.png -o "$pub_dir/digital/reader.pdf"

    if compgen -G "$stage_dir/*.tiff" >/dev/null; then
        log_info "Building Press PDF..."
        img2pdf "$stage_dir"/*.tiff -o "$pub_dir/print/press.pdf"
    else
        log_warn "No TIFF masters found — skipping press.pdf"
    fi

    jq -n \
        --arg ts "$(_timestamp)" \
        --arg edition "$(basename "$edition_dir")" \
        --arg count "${#page_dirs[@]}" \
        '{
            edition_id: $edition,
            page_count: ($count | tonumber),
            published_at: $ts,
            format_version: "1.0",
            publisher: "Play Function",
            author: "Alan R Szmyt"
        }' > "$pub_dir/meta.json"

    log_success "Publishing assets ready in $pub_dir"
}

# ------------------------------------------------------------
# Build Page
# ------------------------------------------------------------
build_page() {
    local page_dir="$1"
    local force="${2:-true}"
    local skip_existing="${3:-false}"

    local artifacts="$page_dir/artifacts"

    if [[ "$force" == "true" ]]; then
        rm -rf "$artifacts"
    fi

    mkdir -p "$artifacts"

    gen_page_meta "$page_dir"
    log_info "Building page: $(basename "$page_dir")"

    if [[ -f "$page_dir/page.png" ]]; then
        gen_jpg "$page_dir/page.png" "$artifacts"
        gen_webp "$page_dir/page.png" "$artifacts"
        gen_web_jpg "$page_dir/page.png" "$artifacts"
        gen_instagram "$page_dir/page.png" "$artifacts"
        gen_tiff "$page_dir/page.png" "$artifacts"
        gen_fullbleed_pdf "$page_dir/page.png" "$artifacts"

generate_fountain_from_image "$page_dir"
    fi

    if [[ -f "$page_dir/page.fountain" ]]; then
        gen_screenplay_pdf "$page_dir/page.fountain" "$artifacts"
        gen_screenplay_json "$page_dir/page.fountain" "$artifacts"
        gen_screenplay_html "$page_dir/page.fountain" "$artifacts"
    fi
}

# ------------------------------------------------------------
# CLI Controller
# ------------------------------------------------------------
main() {
    check_dependencies

    local cmd="${1:-help}"
    shift || true

    case "$cmd" in
        manifest)
            mapfile -t pages < <(
                find "$1/pages" -maxdepth 1 -mindepth 1 -type d | sort
            )
            for p in "${pages[@]}"; do
                gen_page_meta "$p"
            done
            ;;
        page)
            build_page "$1" true false
            ;;
        edition)
            local skip=false
            [[ "$*" == *"--skip-existing"* ]] && skip=true
            mapfile -t pages < <(
                find "$1/pages" -maxdepth 1 -mindepth 1 -type d | sort
            )
            for p in "${pages[@]}"; do
                build_page "$p" "true" "$skip"
            done
            log_success "Individual page builds complete."
            ;;
        finalize)
            finalize_edition "$1" "${2:-}"
            ;;
        *)
            printf "Usage: magazine [manifest|page|edition|finalize] <path> [--force]\n"
            ;;
    esac
}

main "$@"
