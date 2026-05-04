#!/bin/bash
# Report plugin declaration drift between repo-owned configs and live tool state.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

PLUGIN_STATUS_SCRIPT="$DOTFILES_DIR/scripts/lib/plugin-status.py"

show_plugin_status() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$PLUGIN_STATUS_SCRIPT" ]]; then
    err "Missing status script: $PLUGIN_STATUS_SCRIPT"
    return 1
  fi

  info "Plugin status"
  python3 "$PLUGIN_STATUS_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --home-dir "$HOME"
}
