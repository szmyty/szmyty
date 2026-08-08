#!/usr/bin/env bash
#
# Cross-platform install script for the wrap CLI tool
# Supports: macOS (Homebrew or source) and Ubuntu (apt or source)
# Repository: https://github.com/eprovst/wrap
#

set -euo pipefail

WRAP_REPO="https://github.com/eprovst/wrap"

log_process() { printf "🔎 %s\n" "$1"; }
log_warn()    { printf "⚠️  %s\n" "$1" >&2; }
log_error()   { printf "❌ %s\n" "$1" >&2; }
log_success() { printf "✅ %s\n" "$1"; }

verify_wrap() {
  if wrap --version >/dev/null 2>&1; then
    log_success "wrap installed successfully"
    return 0
  else
    log_error "Installation failed"
    exit 1
  fi
}

install_from_source() {
  log_process "Installing wrap from source ($WRAP_REPO)"

  if ! command -v go >/dev/null 2>&1; then
    log_error "Go is required to build wrap from source but was not found in PATH"
    exit 1
  fi

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' EXIT

  git clone --depth 1 "$WRAP_REPO" "$tmp_dir/wrap"
  (
    cd "$tmp_dir/wrap"
    go build -o wrap .
    install -m 0755 wrap /usr/local/bin/wrap
  )
}

install_macos() {
  if command -v brew >/dev/null 2>&1; then
    log_process "Installing wrap via Homebrew"
    brew install eprovst/tap/wrap
  else
    install_from_source
  fi
}

install_ubuntu() {
  if command -v apt-get >/dev/null 2>&1; then
    log_process "Installing wrap via apt"
    if apt-get install -y wrap 2>/dev/null; then
      return 0
    fi
    log_warn "wrap not found in apt repositories — falling back to source build"
  fi
  install_from_source
}

main() {
  log_process "Checking OS"

  if command -v wrap >/dev/null 2>&1; then
    log_warn "wrap already installed"
    verify_wrap
    return 0
  fi

  log_process "Installing wrap"

  local os
  os="$(uname -s)"

  case "$os" in
    Darwin)
      install_macos
      ;;
    Linux)
      install_ubuntu
      ;;
    *)
      log_error "Unsupported operating system: $os"
      exit 1
      ;;
  esac

  verify_wrap
}

main "$@"
