#!/bin/bash
# Install/update skills from the skills manifest.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.
# Requires: jq, python3, gh

SKILLS_DIR="$DOTFILES_DIR/skills"
MANIFEST="$DOTFILES_DIR/scripts/skills-manifest.json"
INSTALLER="$SKILLS_DIR/.system/skill-installer/scripts/install-skill-from-github.py"

update_skills() {
  if ! command -v jq &>/dev/null; then err "jq is required"; return 1; fi
  if ! command -v gh &>/dev/null; then err "gh CLI is required"; return 1; fi
  if ! command -v python3 &>/dev/null; then err "python3 is required"; return 1; fi
  if [[ ! -f "$MANIFEST" ]]; then err "Missing manifest: $MANIFEST"; return 1; fi
  if [[ ! -f "$INSTALLER" ]]; then err "Missing installer: $INSTALLER"; return 1; fi

  local count updated=0 skipped=0 failed=0
  count=$(jq '.skills | length' "$MANIFEST")

  info "Updating $count skills from manifest..."

  for ((i = 0; i < count; i++)); do
    local name repo path
    name=$(jq -r ".skills[$i].name" "$MANIFEST")
    repo=$(jq -r ".skills[$i].repo" "$MANIFEST")
    path=$(jq -r ".skills[$i].path" "$MANIFEST")
    ref=$(jq -r ".skills[$i].ref // \"main\"" "$MANIFEST")

    local dest="$SKILLS_DIR/$name"

    if [[ -d "$dest" ]]; then
      # Remove existing to re-install latest
      rm -rf "$dest"
    fi

    if python3 "$INSTALLER" --repo "$repo" --path "$path" --ref "$ref" --dest "$SKILLS_DIR" --name "$name" 2>/dev/null; then
      echo -e "  ${GREEN}[OK]${NC} $name (from $repo)"
      ((updated++))
    else
      echo -e "  ${RED}[FAIL]${NC} $name (from $repo)"
      ((failed++))
    fi
  done

  echo ""
  info "Updated: $updated, Failed: $failed"
}

list_skills() {
  if [[ ! -f "$MANIFEST" ]]; then err "Missing manifest: $MANIFEST"; return 1; fi

  local count
  count=$(jq '.skills | length' "$MANIFEST")

  info "Skills manifest ($count skills):"
  echo ""

  for ((i = 0; i < count; i++)); do
    local name repo
    name=$(jq -r ".skills[$i].name" "$MANIFEST")
    repo=$(jq -r ".skills[$i].repo" "$MANIFEST")

    local dest="$SKILLS_DIR/$name"
    if [[ -d "$dest" ]]; then
      echo -e "  ${GREEN}[INSTALLED]${NC} $name  ($repo)"
    else
      echo -e "  ${RED}[MISSING]${NC}   $name  ($repo)"
    fi
  done
}
