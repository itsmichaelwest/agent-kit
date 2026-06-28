#!/bin/bash
# Uninstall one upstream skill and update the manifest.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

UNINSTALL_SKILL_SCRIPT="$DOTFILES_DIR/scripts/lib/uninstall-skill.py"

_uninstall_skill_manifest() {
  local skill_name="$1"
  shift

  if ! command -v python3 &>/dev/null; then
    err "python3 is required"
    return 1
  fi
  if [[ ! -f "$UNINSTALL_SKILL_SCRIPT" ]]; then
    err "Missing uninstall script: $UNINSTALL_SKILL_SCRIPT"
    return 1
  fi

  python3 "$UNINSTALL_SKILL_SCRIPT" \
    --repo-root "$DOTFILES_DIR" \
    --skill "$skill_name" \
    "$@"
}

uninstall_skill() {
  _skills_preflight || return 1
  if (( $# != 1 )); then
    err "Usage: setup.sh uninstall-skill <installed-skill-name>"
    return 1
  fi

  local skill_name="$1"
  _skills_link_lockfile
  _uninstall_skill_manifest "$skill_name"

  info "Uninstalling skill via npx skills: $skill_name"
  npx -y skills@latest remove "$skill_name" -g -y

  _uninstall_skill_manifest "$skill_name" --apply
}
