#!/bin/bash
# Check that every link declared in ai-agent-links.json is in place.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

DOCTOR_LINKS_SCRIPT="$DOTFILES_DIR/scripts/lib/doctor-links.py"

doctor_links() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$DOCTOR_LINKS_SCRIPT" ]]; then
    err "Missing doctor script: $DOCTOR_LINKS_SCRIPT"
    return 1
  fi

  info "Links doctor"
  python3 "$DOCTOR_LINKS_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --home-dir "$HOME" \
    "$@"
}
