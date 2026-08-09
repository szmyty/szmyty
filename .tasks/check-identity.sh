#!/usr/bin/env bash
# .tasks/check-identity.sh
# Rejects stale source-repository names and obsolete production URLs in
# configuration files. Markdown prose linking to real external projects
# is permitted. Only configuration file types are scanned.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"

# Patterns that must NOT appear as production config targets.
# These are checked only in structured config file types.
STALE_PATTERNS=(
    "egohygiene/egohygiene"
    "egohygiene/sanctuary"
    "profile-next"
)

# Additionally, egohygiene/egohygiene must not appear as a projectOwner/projectName
# in allcontributorsrc or as a config URL.
CONFIG_EXTENSIONS=("*.yml" "*.yaml" "*.json" "*.toml")

EXCLUDE_DIRS=("docs/audits" ".git")

EXCLUDE_ARGS=()
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_ARGS+=("--exclude-dir=${dir}")
done

EXT_ARGS=()
for ext in "${CONFIG_EXTENSIONS[@]}"; do
    EXT_ARGS+=("--include=${ext}")
done

FOUND=0

for pattern in "${STALE_PATTERNS[@]}"; do
    results=$(grep -r "${EXCLUDE_ARGS[@]}" "${EXT_ARGS[@]}" \
        -l "$pattern" "$REPO_ROOT" 2>/dev/null || true)
    if [[ -n "$results" ]]; then
        echo "ERROR: Stale reference '$pattern' found in config file(s):"
        echo "$results" | sed "s|$REPO_ROOT/||"
        FOUND=1
    fi
done

if [[ "$FOUND" -eq 1 ]]; then
    echo ""
    echo "Identity check FAILED: remove or migrate the stale references above."
    exit 1
else
    echo "Identity check PASSED: no stale repository references found."
fi
