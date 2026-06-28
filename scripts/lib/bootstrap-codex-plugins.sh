#!/bin/bash
# Bootstrap Codex plugins declared in .codex/config.toml.
#
# Codex config declares the desired plugin state, but the app/CLI plugin
# manager still needs marketplace snapshots and plugin installs to converge on
# a fresh machine. This script reads the repo-owned Codex config, registers
# declared marketplaces, refreshes snapshots, and installs enabled plugins.

set -u

BOOTSTRAP_CODEX_PLUGINS_SCRIPT="$DOTFILES_DIR/scripts/lib/bootstrap-codex-plugins.py"

bootstrap_codex_plugins() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$BOOTSTRAP_CODEX_PLUGINS_SCRIPT" ]]; then
    err "Missing Codex bootstrap script: $BOOTSTRAP_CODEX_PLUGINS_SCRIPT"
    return 1
  fi

  python3 "$BOOTSTRAP_CODEX_PLUGINS_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --home-dir "$HOME"
}
