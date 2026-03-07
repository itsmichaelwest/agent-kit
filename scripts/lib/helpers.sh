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
