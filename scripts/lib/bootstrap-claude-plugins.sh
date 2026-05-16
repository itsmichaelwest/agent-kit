#!/bin/bash
# Bootstrap Claude Code plugins declared in .claude/settings.json.
#
# Claude Code's enabledPlugins (at user scope) only toggles plugins that are
# already installed in ~/.claude/plugins/cache/. It does NOT auto-install on
# first launch the way Codex and Copilot CLI do. This script closes that gap
# by reading enabledPlugins from the linked ~/.claude/settings.json and
# running `claude plugin install` for each entry where value=true.
#
# Idempotent: already-installed plugins are skipped by Claude itself.
# Safe to run multiple times.

set -u

SETTINGS="${HOME}/.claude/settings.json"

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

if [[ ${#specs[@]} -eq 0 ]]; then
  echo "[INFO] No enabled plugins declared in $SETTINGS"
  exit 0
fi

echo "[INFO] Bootstrapping ${#specs[@]} Claude Code plugin(s) from $SETTINGS"

ok=0
skip=0
fail=0

for spec in "${specs[@]}"; do
  [[ -z "$spec" ]] && continue
  if output=$(claude plugin install "$spec" 2>&1); then
    if echo "$output" | grep -q "already installed"; then
      echo "  [SKIP] $spec (already installed)"
      ((skip++))
    else
      echo "  [OK]   $spec"
      ((ok++))
    fi
  else
    echo "  [FAIL] $spec"
    ((fail++))
  fi
done

echo ""
echo "[INFO] Installed: $ok, Skipped: $skip, Failed: $fail"
exit $(( fail > 0 ? 1 : 0 ))
