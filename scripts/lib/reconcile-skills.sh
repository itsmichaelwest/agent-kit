#!/bin/bash
# Reconcile out-of-band `npx skills` installs into manifest + lockfile.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

RECONCILE_SKILLS_SCRIPT="$DOTFILES_DIR/scripts/lib/reconcile-skills.py"

reconcile_skills() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$RECONCILE_SKILLS_SCRIPT" ]]; then
    err "Missing reconcile script: $RECONCILE_SKILLS_SCRIPT"
    return 1
  fi

  info "Skills reconcile"
  python3 "$RECONCILE_SKILLS_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --home-dir "$HOME"
}
