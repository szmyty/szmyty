#!/usr/bin/env bash
#
# Cross-platform install script for the scripttool CLI utility
# Supports: macOS (Homebrew or go install) and Ubuntu/Linux (go install or source)
# Repository: https://github.com/rsdoiel/scripttool
#

set -euo pipefail

SCRIPTTOOL_REPO="https://github.com/rsdoiel/scripttool"
SCRIPTTOOL_PKG="github.com/rsdoiel/scripttool/cmd/scripttool@latest"

log_process() { printf "🔎 %s\n" "$1"; }
log_warn()    { printf "⚠️  %s\n" "$1" >&2; }
log_error()   { printf "❌ %s\n" "$1" >&2; }
log_success() { printf "✅ %s\n" "$1"; }

# Run a command with sudo when not already root
_sudo() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    log_error "Root privileges required but sudo is not available"
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Ensure GOPATH/bin is in PATH so that `go install`-ed binaries are found
# ---------------------------------------------------------------------------
ensure_gopath_in_path() {
  local gopath
  gopath="$(go env GOPATH 2>/dev/null || true)"
  if [[ -n "$gopath" && ":$PATH:" != *":${gopath}/bin:"* ]]; then
    export PATH="${gopath}/bin:${PATH}"
  fi
}

# ---------------------------------------------------------------------------
# Verify that scripttool is usable after installation
# ---------------------------------------------------------------------------
verify_scripttool() {
  if scripttool --help >/dev/null 2>&1; then
    log_success "scripttool installed successfully"
    return 0
  else
    log_error "Installation failed"
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Install via `go install` (preferred on all platforms when Homebrew absent)
# ---------------------------------------------------------------------------
install_via_go() {
  log_process "Installing scripttool via go install"
  go install "$SCRIPTTOOL_PKG"
  ensure_gopath_in_path
}

# ---------------------------------------------------------------------------
# Install from source (fallback when `go install` cannot fetch the module)
# ---------------------------------------------------------------------------
install_from_source() {
  log_process "Installing scripttool from source ($SCRIPTTOOL_REPO)"

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' EXIT

  git clone --depth 1 "$SCRIPTTOOL_REPO" "$tmp_dir/scripttool"
  (
    cd "$tmp_dir/scripttool"
    go build -o scripttool ./cmd/scripttool
    _sudo install -m 0755 scripttool /usr/local/bin/scripttool
  )
}

# ---------------------------------------------------------------------------
# Ensure Go is available; install it on Ubuntu if missing
# ---------------------------------------------------------------------------
ensure_go() {
  if command -v go >/dev/null 2>&1; then
    return 0
  fi

  log_process "Go not found — attempting to install Go"

  local os
  os="$(uname -s)"

  if [[ "$os" == "Linux" ]] && command -v apt-get >/dev/null 2>&1; then
    _sudo apt-get update -qq
    _sudo apt-get install -y golang-go
  else
    log_error "Go is required but was not found and cannot be installed automatically on this platform"
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Platform-specific install paths
# ---------------------------------------------------------------------------
install_macos() {
  if command -v brew >/dev/null 2>&1; then
    log_process "Installing scripttool via Homebrew"
    if brew install rsdoiel/scripttool/scripttool 2>/dev/null; then
      return 0
    fi
    log_warn "Homebrew tap not available — falling back to go install"
  fi

  ensure_go
  install_via_go || install_from_source
}

install_linux() {
  ensure_go
  install_via_go || install_from_source
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
main() {
  log_process "Detecting OS"

  if command -v scripttool >/dev/null 2>&1; then
    log_warn "scripttool already installed"
    verify_scripttool
    return 0
  fi

  log_process "Installing scripttool"

  local os
  os="$(uname -s)"

  case "$os" in
    Darwin)
      install_macos
      ;;
    Linux)
      install_linux
      ;;
    *)
      log_error "Unsupported operating system: $os"
      exit 1
      ;;
  esac

  verify_scripttool
}

main "$@"
