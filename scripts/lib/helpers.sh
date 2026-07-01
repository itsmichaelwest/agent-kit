#!/bin/bash
# Shared helpers: colors, logging, symlink logic.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERROR]${NC} $1"; }

ensure_linked() {
  local source="$1"
  local target="$2"

  [[ ! -e "$source" ]] && return

  if [[ -L "$target" ]]; then
    local existing
    existing="$(readlink "$target")"
    [[ "$existing" != /* ]] && existing="$(cd "$(dirname "$target")" && cd "$(dirname "$existing")" && pwd)/$(basename "$existing")"
    if [[ "$existing" == "$source" ]]; then
      echo "  [SKIP] $target"
      return
    fi
    rm "$target"
  elif [[ -e "$target" ]]; then
    mv "$target" "${target}.backup.$(date +%Y%m%d_%H%M%S)"
    info "Backed up: $target"
  fi

  mkdir -p "$(dirname "$target")"
  ln -sf "$source" "$target"
  echo "  [LINK] $source -> $target"
}

remove_link() {
  local target="$1"
  if [[ -L "$target" ]]; then
    rm "$target"
    echo "  [REMOVED] $target"

    # Restore the most recent backup created by ensure_linked
    local dir basename latest
    dir="$(dirname "$target")"
    basename="$(basename "$target")"
    latest="$(ls -1t "$dir/${basename}.backup."* 2>/dev/null | head -1)"
    if [[ -n "$latest" ]]; then
      mv "$latest" "$target"
      echo "  [RESTORED] $target (from $(basename "$latest"))"
    fi
  elif [[ -e "$target" ]]; then
    warn "Not a symlink, skipping: $target"
  fi
}

detect_os() {
  if [[ "$OSTYPE" == darwin* ]]; then echo "macos"
  elif [ -f /etc/arch-release ]; then echo "arch"
  elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then echo "ubuntu"
  else echo "unknown"
  fi
}

# Resolve a Python interpreter >= 3.11 (required for the stdlib `tomllib`
# module used to parse TOML config). Echoes the interpreter on success and
# returns 0; returns 1 if no suitable interpreter is found.
#
# macOS ships an older system python3 (3.9) that usually shadows a Homebrew
# install on PATH, so we can't just trust `python3`. We probe versioned
# binaries (python3.14, python3.13, ...) high-to-low first, then fall back to
# the bare names, and version-check each before accepting it.
resolve_python() {
  local candidate minor
  local candidates=()
  for minor in $(seq 30 -1 11); do
    candidates+=("python3.$minor")
  done
  candidates+=(python3 python)

  for candidate in "${candidates[@]}"; do
    command -v "$candidate" &>/dev/null || continue
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' &>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

# Set PYTHON to a >= 3.11 interpreter or fail with a clear, actionable error.
require_python() {
  if PYTHON="$(resolve_python)"; then
    return 0
  fi
  err "Python 3.11+ is required (stdlib tomllib). Install it, e.g.:"
  err "  macOS:  brew install python"
  err "  Ubuntu: sudo apt install python3"
  err "  Arch:   sudo pacman -S python"
  return 1
}
