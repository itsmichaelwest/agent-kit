#!/bin/bash
# Install MCP servers from mcp/mcp-config.json at Claude Code user scope.
# Idempotent: removes existing user-scope entry before re-adding.
# Skips entries whose ${ENV_VAR} references are unset (warns but continues).
#
# Note: Copilot CLI consumes mcp/mcp-config.json directly via symlink
# (~/.copilot/mcp-config.json — see scripts/ai-agent-links.json), so this
# installer only handles Claude Code where ~/.claude.json mixes config with
# state and can't be safely symlinked.

install_mcp() {
  local manifest="$DOTFILES_DIR/mcp/mcp-config.json"

  if [[ ! -f "$manifest" ]]; then
    warn "No MCP manifest at $manifest — skipping"
    return 0
  fi

  if ! command -v claude >/dev/null 2>&1; then
    warn "claude CLI not found — skipping MCP install"
    return 0
  fi

  if ! command -v jq >/dev/null 2>&1; then
    err "jq required for MCP install"
    return 1
  fi

  info "Installing Claude Code user-scope MCP servers from $manifest"

  local names
  names=$(jq -r '.mcpServers | keys[]' "$manifest")

  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    _install_mcp_server "$name" "$manifest" || warn "Failed to install MCP server: $name"
  done <<< "$names"
}

_install_mcp_server() {
  local name="$1"
  local manifest="$2"

  local type url command
  type=$(jq -r --arg n "$name" '.mcpServers[$n].type // "stdio"' "$manifest")
  url=$(jq -r --arg n "$name" '.mcpServers[$n].url // ""' "$manifest")
  command=$(jq -r --arg n "$name" '.mcpServers[$n].command // ""' "$manifest")

  url=$(_expand_env "$url") || { warn "  [SKIP] $name (missing env vars in url)"; return 0; }

  local cmd=(claude mcp add --scope user --transport "$type")

  # Headers — accept object form {"Name":"Value"} or array form ["Name: Value"]
  if [[ "$type" == "http" || "$type" == "sse" ]]; then
    local header_kind
    header_kind=$(jq -r --arg n "$name" '.mcpServers[$n].headers | type' "$manifest")
    case "$header_kind" in
      object)
        while IFS= read -r line; do
          [[ -z "$line" ]] && continue
          local expanded
          expanded=$(_expand_env "$line") || { warn "  [SKIP] $name (missing env in header)"; return 0; }
          cmd+=(--header "$expanded")
        done < <(jq -r --arg n "$name" '.mcpServers[$n].headers | to_entries[] | "\(.key): \(.value)"' "$manifest")
        ;;
      array)
        while IFS= read -r line; do
          [[ -z "$line" ]] && continue
          local expanded
          expanded=$(_expand_env "$line") || { warn "  [SKIP] $name (missing env in header)"; return 0; }
          cmd+=(--header "$expanded")
        done < <(jq -r --arg n "$name" '.mcpServers[$n].headers[]' "$manifest")
        ;;
    esac
  fi

  # Env vars (stdio only)
  if [[ "$type" == "stdio" ]]; then
    while IFS= read -r kv; do
      [[ -z "$kv" ]] && continue
      local expanded
      expanded=$(_expand_env "$kv") || { warn "  [SKIP] $name (missing env)"; return 0; }
      cmd+=(-e "$expanded")
    done < <(jq -r --arg n "$name" '.mcpServers[$n].env // {} | to_entries[] | "\(.key)=\(.value)"' "$manifest")
  fi

  claude mcp remove "$name" -s user >/dev/null 2>&1 || true

  if [[ "$type" == "http" || "$type" == "sse" ]]; then
    [[ -z "$url" ]] && { err "  [FAIL] $name missing url for $type transport"; return 1; }
    cmd+=("$name" "$url")
  else
    [[ -z "$command" ]] && { err "  [FAIL] $name missing command for stdio transport"; return 1; }
    cmd+=("$name" "--" "$command")
    while IFS= read -r arg; do
      [[ -z "$arg" ]] && continue
      cmd+=("$arg")
    done < <(jq -r --arg n "$name" '.mcpServers[$n].args // [] | .[]' "$manifest")
  fi

  if "${cmd[@]}" >/dev/null 2>&1; then
    echo "  [OK] $name ($type)"
  else
    err "  [FAIL] $name — re-run: ${cmd[*]}"
    return 1
  fi
}

# Expand ${VAR} references using current env. Returns 1 if any ref is unset.
_expand_env() {
  local input="$1"
  local output="$input"
  local var_name var_value

  while [[ "$output" =~ \$\{([A-Za-z_][A-Za-z0-9_]*)\} ]]; do
    var_name="${BASH_REMATCH[1]}"
    var_value="${!var_name:-}"
    if [[ -z "$var_value" ]]; then
      return 1
    fi
    output="${output//\$\{${var_name}\}/$var_value}"
  done

  echo "$output"
}
