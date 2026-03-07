#!/bin/bash
# Link AI agent configs using the JSON manifest.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.
# Requires: jq

link_ai_agents() {
  local config="$DOTFILES_DIR/scripts/ai-agent-links.json"

  if ! command -v jq &>/dev/null; then
    err "jq is required but not installed"
    return 1
  fi

  if [[ ! -f "$config" ]]; then
    err "Missing config: $config"
    return 1
  fi

  info "Linking AI agent configs..."

  local count
  count=$(jq '.targets | length' "$config")

  for ((i = 0; i < count; i++)); do
    local source_key target_path source_rel source_abs

    source_key=$(jq -r ".targets[$i].source" "$config")
    target_path=$(jq -r ".targets[$i].path" "$config")
    source_rel=$(jq -r ".sources[\"$source_key\"] // empty" "$config")

    if [[ -z "$source_rel" ]]; then
      warn "Unknown source key '$source_key', skipping"
      continue
    fi

    source_abs="$DOTFILES_DIR/$source_rel"
    target_path="${target_path/#\~/$HOME}"

    if [[ ! -e "$source_abs" ]]; then
      warn "Missing source: $source_abs, skipping"
      continue
    fi

    ensure_linked "$source_abs" "$target_path"
  done
}

unlink_ai_agents() {
  local config="$DOTFILES_DIR/scripts/ai-agent-links.json"

  if ! command -v jq &>/dev/null || [[ ! -f "$config" ]]; then
    err "jq or config missing, cannot unlink"
    return 1
  fi

  info "Removing AI agent links..."

  local count
  count=$(jq '.targets | length' "$config")

  for ((i = 0; i < count; i++)); do
    local target_path
    target_path=$(jq -r ".targets[$i].path" "$config")
    target_path="${target_path/#\~/$HOME}"
    remove_link "$target_path"
  done
}

show_ai_agent_status() {
  local config="$DOTFILES_DIR/scripts/ai-agent-links.json"

  if ! command -v jq &>/dev/null || [[ ! -f "$config" ]]; then
    warn "Cannot read manifest; falling back to basic status"
    return
  fi

  local count
  count=$(jq '.targets | length' "$config")

  for ((i = 0; i < count; i++)); do
    local target_path
    target_path=$(jq -r ".targets[$i].path" "$config")
    target_path="${target_path/#\~/$HOME}"

    if [[ -L "$target_path" ]]; then
      echo -e "  ${GREEN}[OK]${NC} $target_path -> $(readlink "$target_path")"
    elif [[ -e "$target_path" ]]; then
      echo -e "  ${YELLOW}[EXISTS]${NC} $target_path (not a symlink)"
    else
      echo -e "  ${RED}[MISSING]${NC} $target_path"
    fi
  done
}
