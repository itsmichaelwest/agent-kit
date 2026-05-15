#!/bin/bash
# Install/update skills via `npx skills` (vercel-labs/skills).
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.
# Requires: jq, npx (Node.js)

MANIFEST="$DOTFILES_DIR/scripts/skills-manifest.json"
LOCKFILE_REPO="$DOTFILES_DIR/.skill-lock.json"
LOCKFILE_HOME="$HOME/.agents/.skill-lock.json"

_skills_preflight() {
  command -v jq  &>/dev/null || { err "jq is required";  return 1; }
  command -v npx &>/dev/null || { err "npx (Node.js) is required"; return 1; }
  [[ -f "$MANIFEST" ]] || { err "Missing manifest: $MANIFEST"; return 1; }
}

# Symlink the global lockfile into the repo so it's tracked.
_skills_link_lockfile() {
  mkdir -p "$HOME/.agents"
  if [[ -L "$LOCKFILE_HOME" ]]; then
    return 0
  fi
  if [[ -f "$LOCKFILE_HOME" && ! -f "$LOCKFILE_REPO" ]]; then
    mv "$LOCKFILE_HOME" "$LOCKFILE_REPO"
  fi
  if [[ ! -f "$LOCKFILE_REPO" ]]; then
    echo '{"version":3,"skills":{}}' > "$LOCKFILE_REPO"
  fi
  if [[ -e "$LOCKFILE_HOME" && ! -L "$LOCKFILE_HOME" ]]; then
    mv "$LOCKFILE_HOME" "${LOCKFILE_HOME}.backup.$(date +%Y%m%d_%H%M%S)"
  fi
  ln -sf "$LOCKFILE_REPO" "$LOCKFILE_HOME"
}

update_skills() {
  _skills_preflight || return 1
  _skills_link_lockfile

  local agent_args=()
  while IFS= read -r a; do agent_args+=("-a" "$a"); done < <(jq -r '.agents[]' "$MANIFEST")

  local count
  count=$(jq '.sources | length' "$MANIFEST")
  info "Installing skills from $count sources via npx skills..."

  local ok=0 failed=0
  for ((i = 0; i < count; i++)); do
    local repo
    repo=$(jq -r ".sources[$i].repo" "$MANIFEST")

    local skill_args=()
    local skill_count
    skill_count=$(jq -r ".sources[$i].skills // [] | length" "$MANIFEST")
    if (( skill_count > 0 )); then
      while IFS= read -r s; do skill_args+=("-s" "$s"); done < <(jq -r ".sources[$i].skills[]" "$MANIFEST")
    else
      skill_args+=("-s" "*")
    fi

    echo -e "  ${YELLOW}[ADD]${NC}  $repo"
    if npx -y skills@latest add "$repo" -g -y "${agent_args[@]}" "${skill_args[@]}" >/dev/null 2>&1; then
      echo -e "  ${GREEN}[OK]${NC}   $repo"
      ((ok++))
    else
      echo -e "  ${RED}[FAIL]${NC} $repo"
      ((failed++))
    fi
  done

  echo ""
  info "Sources installed: $ok, Failed: $failed"
  ((failed == 0))
}

list_skills() {
  _skills_preflight || return 1
  npx -y skills@latest list -g
}
