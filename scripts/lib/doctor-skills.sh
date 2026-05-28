#!/bin/bash
# Check skills manifest/lockfile/disk consistency.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

DOCTOR_SKILLS_SCRIPT="$DOTFILES_DIR/scripts/lib/doctor-skills.py"

doctor_skills() {
  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$DOCTOR_SKILLS_SCRIPT" ]]; then
    err "Missing doctor script: $DOCTOR_SKILLS_SCRIPT"
    return 1
  fi

  info "Skills doctor"
  python3 "$DOCTOR_SKILLS_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --home-dir "$HOME" \
    "$@"
}
