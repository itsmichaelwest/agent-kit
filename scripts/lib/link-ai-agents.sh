#!/bin/bash
# Link AI agent configs using the JSON manifest.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.
# Requires: jq

AI_AGENT_LAYOUT_VERSION="2"

ai_agent_state_file() {
  local state_root="${XDG_STATE_HOME:-$HOME/.local/state}"
  echo "$state_root/agent-kit/ai-agent-layout-version"
}

ensure_directory_target() {
  local target="$1"

  if [[ -L "$target" ]]; then
    rm "$target"
  elif [[ -e "$target" && ! -d "$target" ]]; then
    mv "$target" "${target}.backup.$(date +%Y%m%d_%H%M%S)"
    info "Backed up: $target"
  fi

  mkdir -p "$target"
}

legacy_ai_agent_targets() {
  printf '%s\n' \
    "$HOME/.copilot/instructions.md" \
    "$HOME/.codex/skills"
}

cleanup_legacy_ai_agent_targets() {
  local target
  while IFS= read -r target; do
    [[ -z "$target" ]] && continue

    if [[ -L "$target" ]]; then
      rm "$target"
      echo "  [MIGRATED] removed legacy link $target"
    elif [[ -e "$target" ]]; then
      mv "$target" "${target}.legacy-backup.$(date +%Y%m%d_%H%M%S)"
      info "Backed up legacy target: $target"
    fi
  done < <(legacy_ai_agent_targets)
}

write_ai_agent_layout_marker() {
  local marker
  marker="$(ai_agent_state_file)"
  mkdir -p "$(dirname "$marker")"
  printf '%s\n' "$AI_AGENT_LAYOUT_VERSION" > "$marker"
}

link_manifest_targets() {
  local config="$DOTFILES_DIR/scripts/ai-agent-links.json"
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

link_copilot_agents() {
  local source_dir="$DOTFILES_DIR/agents"
  local target_dir="$HOME/.copilot/agents"

  if [[ ! -d "$source_dir" ]]; then
    warn "Missing source directory: $source_dir"
    return
  fi

  ensure_directory_target "$target_dir"

  find "$target_dir" -maxdepth 1 -type l -name '*.agent.agent.md' -print0 2>/dev/null \
    | while IFS= read -r -d '' stale_link; do
      rm "$stale_link"
      echo "  [MIGRATED] removed stale $stale_link"
    done

  local source_file
  while IFS= read -r -d '' source_file; do
    local base_name
    base_name="$(basename "${source_file%.md}")"
    ensure_linked "$source_file" "$target_dir/$base_name.agent.md"
  done < <(find "$source_dir" -maxdepth 1 -type f -name '*.md' ! -name '*.agent.md' -print0 | sort -z)
}

# Generate ~/.copilot/settings.json by merging the committed shared settings
# with an optional gitignored .copilot/settings.local.json overlay. Written as
# a real file (not a symlink) so Copilot CLI can write runtime keys without
# polluting the repo.
link_copilot_settings() {
  local shared="$DOTFILES_DIR/.copilot/settings.json"
  local overlay="$DOTFILES_DIR/.copilot/settings.local.json"
  local target="$HOME/.copilot/settings.json"

  if [[ ! -f "$shared" ]]; then
    warn "Missing $shared"
    return
  fi

  if ! command -v jq &>/dev/null; then
    err "jq required to merge copilot settings"
    return 1
  fi

  mkdir -p "$(dirname "$target")"

  if [[ -L "$target" ]]; then
    rm "$target"
  elif [[ -e "$target" ]]; then
    mv "$target" "${target}.backup.$(date +%Y%m%d_%H%M%S)"
    info "Backed up existing settings.json"
  fi

  if [[ -f "$overlay" ]]; then
    jq -s '.[0] * .[1] | del(.["$schema_comment"])' "$shared" "$overlay" > "$target"
    echo "  [MERGE] $target (shared + local overlay)"
  else
    jq 'del(.["$schema_comment"])' "$shared" > "$target"
    echo "  [WRITE] $target (shared only — create .copilot/settings.local.json to override)"
  fi
}

# Generate ~/.codex/config.toml by merging shared declarative config with a
# gitignored personal overlay, while preserving [projects.*] trust entries
# Codex has written into the live file at runtime. Written as a real file
# (not a symlink) so Codex's own writes don't pollute the repo.
link_codex_config() {
  local shared="$DOTFILES_DIR/.codex/config.toml"
  local overlay="$DOTFILES_DIR/.codex/config.local.toml"
  local target="$HOME/.codex/config.toml"
  local merger="$DOTFILES_DIR/scripts/lib/merge-codex-config.py"

  if [[ ! -f "$shared" ]]; then
    warn "Missing $shared"
    return
  fi

  if ! command -v python3 &>/dev/null; then
    err "python3 (3.11+) required to merge codex config"
    return 1
  fi

  if [[ ! -f "$merger" ]]; then
    err "Missing $merger"
    return 1
  fi

  mkdir -p "$(dirname "$target")"

  local live_arg=""
  if [[ -f "$target" && ! -L "$target" ]]; then
    live_arg="$target"
  fi

  if [[ -L "$target" ]]; then
    rm "$target"
  elif [[ -e "$target" ]]; then
    cp "$target" "${target}.backup.$(date +%Y%m%d_%H%M%S)"
    info "Backed up existing config.toml"
  fi

  local tmp
  tmp="$(mktemp)"
  if python3 "$merger" "$shared" "$overlay" $live_arg > "$tmp" 2>/dev/null; then
    mv "$tmp" "$target"
    if [[ -f "$overlay" ]]; then
      echo "  [MERGE] $target (shared + local overlay + preserved [projects])"
    else
      echo "  [MERGE] $target (shared + preserved [projects] — create .codex/config.local.toml to predeclare trust)"
    fi
  else
    rm -f "$tmp"
    err "Failed to merge codex config"
    return 1
  fi
}

unlink_copilot_agents() {
  local source_dir="$DOTFILES_DIR/agents"
  local target_dir="$HOME/.copilot/agents"

  [[ ! -d "$source_dir" ]] && return

  local source_file
  while IFS= read -r -d '' source_file; do
    local base_name
    base_name="$(basename "${source_file%.md}")"
    remove_link "$target_dir/$base_name.agent.md"
  done < <(find "$source_dir" -maxdepth 1 -type f -name '*.md' ! -name '*.agent.md' -print0 | sort -z)
}

show_target_status() {
  local target_path="$1"

  if [[ -L "$target_path" ]]; then
    echo -e "  ${GREEN}[OK]${NC} $target_path -> $(readlink "$target_path")"
  elif [[ -e "$target_path" ]]; then
    echo -e "  ${YELLOW}[EXISTS]${NC} $target_path (not a symlink)"
  else
    echo -e "  ${RED}[MISSING]${NC} $target_path"
  fi
}

current_ai_agent_layout_status() {
  local marker=""
  local marker_file
  marker_file="$(ai_agent_state_file)"
  [[ -f "$marker_file" ]] && marker="$(tr -d '\n\r' < "$marker_file")"

  local current_ok=1
  local current_targets=(
    "$HOME/.claude/skills"
    "$HOME/.codex/agents"
    "$HOME/.agents/skills"
    "$HOME/.copilot/copilot-instructions.md"
    "$HOME/.copilot/agents"
  )

  local target
  for target in "${current_targets[@]}"; do
    if [[ ! -e "$target" && ! -L "$target" ]]; then
      current_ok=0
      break
    fi
  done

  local legacy_present=0
  while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    if [[ -e "$target" || -L "$target" ]]; then
      legacy_present=1
      break
    fi
  done < <(legacy_ai_agent_targets)

  if [[ "$marker" == "$AI_AGENT_LAYOUT_VERSION" && $current_ok -eq 1 && $legacy_present -eq 0 ]]; then
    echo "current"
  elif [[ $legacy_present -eq 1 && $current_ok -eq 0 ]]; then
    echo "legacy"
  elif [[ $legacy_present -eq 1 || "$marker" == "$AI_AGENT_LAYOUT_VERSION" || $current_ok -eq 1 ]]; then
    echo "mixed"
  else
    echo "unknown"
  fi
}

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
  cleanup_legacy_ai_agent_targets
  link_manifest_targets
  link_copilot_agents
  link_copilot_settings
  link_codex_config
  write_ai_agent_layout_marker
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

  unlink_copilot_agents

  local marker
  marker="$(ai_agent_state_file)"
  [[ -f "$marker" ]] && rm -f "$marker"
}

show_ai_agent_status() {
  local config="$DOTFILES_DIR/scripts/ai-agent-links.json"

  if ! command -v jq &>/dev/null || [[ ! -f "$config" ]]; then
    warn "Cannot read manifest; falling back to basic status"
    return
  fi

  local marker_file layout_version
  marker_file="$(ai_agent_state_file)"
  if [[ -f "$marker_file" ]]; then
    layout_version="$(tr -d '\n\r' < "$marker_file")"
  else
    layout_version="none"
  fi

  echo "  Layout: $(current_ai_agent_layout_status)"
  echo "  Layout version marker: $layout_version"

  local count
  count=$(jq '.targets | length' "$config")

  for ((i = 0; i < count; i++)); do
    local target_path
    target_path=$(jq -r ".targets[$i].path" "$config")
    target_path="${target_path/#\~/$HOME}"
    show_target_status "$target_path"
  done

  local source_dir="$DOTFILES_DIR/agents"
  if [[ -d "$source_dir" ]]; then
    local source_file
    while IFS= read -r -d '' source_file; do
      local base_name
      base_name="$(basename "${source_file%.md}")"
      show_target_status "$HOME/.copilot/agents/$base_name.agent.md"
    done < <(find "$source_dir" -maxdepth 1 -type f -name '*.md' ! -name '*.agent.md' -print0 | sort -z)
  fi
}
