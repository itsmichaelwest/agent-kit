#!/bin/bash
# Install/update skills from the skills manifest.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.
# Requires: jq, python3, gh

SKILLS_DIR="$DOTFILES_DIR/skills"
MANIFEST="$DOTFILES_DIR/scripts/skills-manifest.json"
INSTALLER="$SKILLS_DIR/.system/skill-installer/scripts/install-skill-from-github.py"

update_skills() {
  if ! command -v jq &>/dev/null; then err "jq is required"; return 1; fi
  if ! command -v git &>/dev/null; then err "git is required"; return 1; fi
  if ! command -v gh &>/dev/null; then err "gh CLI is required"; return 1; fi
  if ! command -v python3 &>/dev/null; then err "python3 is required"; return 1; fi
  if [[ ! -f "$MANIFEST" ]]; then err "Missing manifest: $MANIFEST"; return 1; fi
  if [[ ! -f "$INSTALLER" ]]; then err "Missing installer: $INSTALLER"; return 1; fi

  local count updated=0 skipped=0 failed=0
  local temp_root
  temp_root="$(mktemp -d "${TMPDIR:-/tmp}/skills-update.XXXXXX")"
  count=$(jq '.skills | length' "$MANIFEST")

  info "Updating $count skills from manifest..."

  for ((i = 0; i < count; i++)); do
    local name repo path ref
    name=$(jq -r ".skills[$i].name" "$MANIFEST")
    repo=$(jq -r ".skills[$i].repo" "$MANIFEST")
    path=$(jq -r ".skills[$i].path" "$MANIFEST")
    ref=$(jq -r ".skills[$i].ref // \"main\"" "$MANIFEST")

    local dest="$SKILLS_DIR/$name"
    local staged="$temp_root/$name"

    rm -rf "$staged"

    if python3 "$INSTALLER" --repo "$repo" --path "$path" --ref "$ref" --dest "$temp_root" --name "$name" 2>/dev/null; then
      if [[ -d "$dest" ]] && git diff --no-index --ignore-cr-at-eol --exit-code -- "$dest" "$staged" >/dev/null 2>&1; then
        rm -rf "$staged"
        echo -e "  ${YELLOW}[SKIP]${NC} $name (unchanged)"
        ((skipped++))
        continue
      fi

      rm -rf "$dest"
      if mv "$staged" "$dest" 2>/dev/null || { cp -a "$staged" "$dest" && rm -rf "$staged"; }; then
        echo -e "  ${GREEN}[OK]${NC} $name (from $repo)"
        ((updated++))
      else
        echo -e "  ${RED}[FAIL]${NC} $name (from $repo)"
        ((failed++))
      fi
    else
      echo -e "  ${RED}[FAIL]${NC} $name (from $repo)"
      ((failed++))
    fi
  done

  rm -rf "$temp_root"
  echo ""
  info "Updated: $updated, Skipped: $skipped, Failed: $failed"
  ((failed == 0))
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
