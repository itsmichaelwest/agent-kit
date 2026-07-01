#!/bin/bash
# Bootstrap Claude Code plugins declared in .claude/settings.json.
#
# Claude Code's enabledPlugins (at user scope) only toggles plugins that are
# already installed in ~/.claude/plugins/cache/. It does NOT auto-install on
# first launch the way Codex and Copilot CLI do. This script closes that gap
# by reading extraKnownMarketplaces and enabledPlugins from the linked
# ~/.claude/settings.json, registering declared marketplaces, then running
# `claude plugin install` and `claude plugin update` for each enabled plugin.
#
# Idempotent: already-installed plugins are skipped by Claude itself.
# Safe to run multiple times.

set -u

SETTINGS="${HOME}/.claude/settings.json"
CACHE_DIR="${HOME}/.claude/plugins/cache"

# Install a plugin, self-healing the known ENOTEMPTY failure: Claude's plugin
# manager stages a download in a temp dir then atomically renames it onto the
# final cache path, but POSIX rename() fails with ENOTEMPTY when that path is a
# leftover non-empty dir from a prior partial install. Clear the stale
# destination + temp debris and retry once. Result is left in INSTALL_OUTPUT.
INSTALL_OUTPUT=""
install_plugin() {
  local spec="$1"
  INSTALL_OUTPUT=$(claude plugin install "$spec" 2>&1)
  local rc=$?
  if [[ $rc -ne 0 ]] && echo "$INSTALL_OUTPUT" | grep -q "ENOTEMPTY"; then
    local plugin="${spec%@*}"
    local market="${spec#*@}"
    if [[ -n "$plugin" && -n "$market" && -d "$CACHE_DIR/$market/$plugin" ]]; then
      echo "  [INFO] $spec: clearing stale cache and retrying"
      rm -rf "${CACHE_DIR:?}/$market/$plugin"
    fi
    rm -rf "${CACHE_DIR:?}"/temp_local_* 2>/dev/null
    INSTALL_OUTPUT=$(claude plugin install "$spec" 2>&1)
    rc=$?
  fi
  return $rc
}

if ! command -v jq >/dev/null 2>&1; then
  echo "[ERROR] jq is required" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "[WARN] claude CLI not found on PATH; skipping plugin bootstrap"
  exit 0
fi

if [[ ! -f "$SETTINGS" ]]; then
  echo "[WARN] $SETTINGS not found; run ./scripts/setup.sh link first"
  exit 0
fi

specs=()
while IFS= read -r spec; do
  [[ -n "$spec" ]] && specs+=("$spec")
done < <(jq -r '.enabledPlugins // {} | to_entries[] | select(.value == true) | .key' "$SETTINGS")

marketplaces=()
while IFS=$'\t' read -r name source_arg; do
  [[ -n "$name" ]] && marketplaces+=("$name"$'\t'"$source_arg")
done < <(
  jq -r '
    .extraKnownMarketplaces // {}
    | to_entries[]
    | .key as $name
    | (.value.source // {}) as $source
    | [
        $name,
        (
          if (($source.source // "") == "github") and (($source.repo // "") != "") then
            $source.repo
          elif (($source.repo // "") != "") then
            $source.repo
          elif (($source.url // "") != "") then
            $source.url
          elif (($source.path // "") != "") then
            $source.path
          elif (($source.source // "") != "") then
            $source.source
          else
            ""
          end
        )
      ]
    | @tsv
  ' "$SETTINGS"
)

if [[ ${#marketplaces[@]} -gt 0 ]]; then
  echo "[INFO] Registering ${#marketplaces[@]} Claude Code marketplace(s) from $SETTINGS"
  marketplace_fail=0

  for marketplace in "${marketplaces[@]}"; do
    IFS=$'\t' read -r name source_arg <<< "$marketplace"
    if [[ -z "$source_arg" ]]; then
      echo "  [FAIL] $name (missing source)"
      ((marketplace_fail++))
      continue
    fi

    if output=$(claude plugin marketplace add "$source_arg" 2>&1); then
      if echo "$output" | grep -qi "already"; then
        echo "  [SKIP] $name (already registered)"
      else
        echo "  [OK]   $name"
      fi
    else
      echo "  [FAIL] $name"
      [[ -n "$output" ]] && echo "$output" | sed 's/^/    /'
      ((marketplace_fail++))
    fi
  done

  if [[ $marketplace_fail -gt 0 ]]; then
    echo ""
    echo "[ERROR] Failed to register $marketplace_fail Claude Code marketplace(s)"
    exit 1
  fi
fi

if [[ ${#specs[@]} -eq 0 ]]; then
  echo "[INFO] No enabled plugins declared in $SETTINGS"
  exit 0
fi

echo "[INFO] Updating Claude Code plugin marketplaces"
if output=$(claude plugin marketplace update 2>&1); then
  echo "  [OK]   marketplaces updated"
else
  echo "  [FAIL] marketplaces"
  [[ -n "$output" ]] && echo "$output" | sed 's/^/    /'
  exit 1
fi

echo "[INFO] Bootstrapping ${#specs[@]} Claude Code plugin(s) from $SETTINGS"

ok=0
skip=0
fail=0

for spec in "${specs[@]}"; do
  [[ -z "$spec" ]] && continue
  if install_plugin "$spec"; then
    if echo "$INSTALL_OUTPUT" | grep -q "already installed"; then
      echo "  [SKIP] $spec (already installed)"
      ((skip++))
    else
      echo "  [OK]   $spec"
      ((ok++))
    fi
  else
    echo "  [FAIL] $spec"
    [[ -n "$INSTALL_OUTPUT" ]] && echo "$INSTALL_OUTPUT" | sed 's/^/    /'
    ((fail++))
  fi
done

echo ""
echo "[INFO] Installed: $ok, Skipped: $skip, Failed: $fail"
if [[ $fail -gt 0 ]]; then
  exit 1
fi

echo "[INFO] Updating ${#specs[@]} Claude Code plugin(s)"

updated=0
update_skip=0
update_fail=0

for spec in "${specs[@]}"; do
  [[ -z "$spec" ]] && continue
  if output=$(claude plugin update "$spec" 2>&1); then
    if echo "$output" | grep -Eqi "already|up[- ]to[- ]date|latest"; then
      echo "  [SKIP] $spec (already up to date)"
      ((update_skip++))
    else
      echo "  [OK]   $spec"
      ((updated++))
    fi
  else
    echo "  [FAIL] $spec"
    [[ -n "$output" ]] && echo "$output" | sed 's/^/    /'
    ((update_fail++))
  fi
done

echo ""
echo "[INFO] Updated: $updated, Skipped: $update_skip, Failed: $update_fail"
exit $(( update_fail > 0 ? 1 : 0 ))
