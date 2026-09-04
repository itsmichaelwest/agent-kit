#!/bin/bash
# Synchronize explicitly owned Codex settings. Sourced by setup.sh.

SYNC_CODEX_CONFIG_SCRIPT="$DOTFILES_DIR/scripts/lib/sync-codex-config.py"

sync_codex_config() {
  local action="${1:-apply}"
  require_python || return 1
  if [[ ! -f "$SYNC_CODEX_CONFIG_SCRIPT" ]]; then
    err "Missing Codex config sync script: $SYNC_CODEX_CONFIG_SCRIPT"
    return 1
  fi
  "$PYTHON" "$SYNC_CODEX_CONFIG_SCRIPT" "$action" --repo-root "$DOTFILES_DIR" --home-dir "$HOME"
}
