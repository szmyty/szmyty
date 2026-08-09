#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$REPO_ROOT"
SECRET_HITS_FILE="$(mktemp)"
trap 'rm -f "$SECRET_HITS_FILE"' EXIT

DENIED_PATH_REGEX='^(\.staging/(oura/.*\.(json|svg)|location/.*\.(json|png|svg)|weather/.*\.(json|svg)|dashboard-app/public/(oura|location|weather)/.*\.json|data/snapshots/.+\.json|data/metrics/(location|oura|weather)\.json))$'

# Covers obvious real-secret formats: GitHub PATs, AWS access keys, GCP API keys,
# Slack tokens, and PEM private key headers.
SECRET_REGEX='(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{80,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----)'

printf '🔒 Checking denied staged data paths...\n'

denied_hits="$(git ls-files | grep -E "$DENIED_PATH_REGEX" || true)"
if [[ -n "$denied_hits" ]]; then
  printf '❌ Denied tracked paths detected in quarantined families:\n'
  printf '%s\n' "$denied_hits" | awk -F/ '{print $1"/"$2"/"$3"/"$4}' | sort -u
  exit 1
fi

printf '🔒 Checking tracked files for obvious credential patterns...\n'
set +e
git grep -nIE -- "$SECRET_REGEX" >"$SECRET_HITS_FILE"
grep_status=$?
set -e

if [[ $grep_status -eq 0 ]]; then
  printf '❌ Potential credential pattern detected (sanitized output):\n'
  cut -d: -f1-2 "$SECRET_HITS_FILE"
  exit 1
fi
if [[ $grep_status -gt 1 ]]; then
  printf '❌ Error while scanning tracked files for credential patterns.\n'
  exit "$grep_status"
fi

printf '✅ Public-data boundary checks passed.\n'
