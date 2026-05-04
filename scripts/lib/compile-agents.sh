#!/bin/bash
# Compile agent templates into provider-specific outputs.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

COMPILE_AGENTS_SCRIPT="$DOTFILES_DIR/scripts/lib/compile-agents.py"

compile_agents() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$COMPILE_AGENTS_SCRIPT" ]]; then
    err "Missing compile script: $COMPILE_AGENTS_SCRIPT"
    return 1
  fi
  if [[ ! -d "$DOTFILES_DIR/agent-templates" ]]; then
    warn "No agent templates directory found; skipping agent compilation"
    return 0
  fi

  info "Compiling agent templates..."
  python3 "$COMPILE_AGENTS_SCRIPT" --repo-root "$DOTFILES_DIR"
}
