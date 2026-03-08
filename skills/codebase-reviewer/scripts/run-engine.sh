#!/bin/bash
# Dispatch a review prompt to an AI engine and return structured JSON.
# Usage: run-engine.sh --engine <claude|codex|copilot> --prompt "..." --cwd /path [--timeout 300]
set -euo pipefail

ENGINE=""
PROMPT=""
CWD="."
TIMEOUT=300

while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine)  ENGINE="$2"; shift 2 ;;
    --prompt)  PROMPT="$2"; shift 2 ;;
    --cwd)     CWD="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) echo "{\"engine\":\"unknown\",\"status\":\"error\",\"output\":\"\",\"error\":\"Unknown arg: $1\"}"; exit 1 ;;
  esac
done

if [[ -z "$ENGINE" || -z "$PROMPT" ]]; then
  echo '{"engine":"","status":"error","output":"","error":"Missing --engine or --prompt"}'
  exit 1
fi

json_escape() {
  python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null
}

run_claude() {
  if ! command -v claude &>/dev/null; then
    echo "{\"engine\":\"claude\",\"status\":\"unavailable\",\"output\":\"\",\"error\":\"claude CLI not found\"}"
    return
  fi
  local out
  out=$(cd "$CWD" && timeout "$TIMEOUT" claude -p "$PROMPT" --output-format text 2>&1) || true
  local escaped
  escaped=$(echo "$out" | json_escape)
  echo "{\"engine\":\"claude\",\"status\":\"ok\",\"output\":$escaped,\"error\":\"\"}"
}

run_codex() {
  if ! command -v codex &>/dev/null; then
    echo "{\"engine\":\"codex\",\"status\":\"unavailable\",\"output\":\"\",\"error\":\"codex CLI not found\"}"
    return
  fi
  local out
  out=$(cd "$CWD" && timeout "$TIMEOUT" codex exec "$PROMPT" 2>&1) || true
  local escaped
  escaped=$(echo "$out" | json_escape)
  echo "{\"engine\":\"codex\",\"status\":\"ok\",\"output\":$escaped,\"error\":\"\"}"
}

run_copilot() {
  if ! command -v copilot &>/dev/null; then
    echo "{\"engine\":\"copilot\",\"status\":\"unavailable\",\"output\":\"\",\"error\":\"copilot CLI not found\"}"
    return
  fi
  local out
  out=$(cd "$CWD" && timeout "$TIMEOUT" copilot -p "$PROMPT" 2>&1) || true
  local escaped
  escaped=$(echo "$out" | json_escape)
  echo "{\"engine\":\"copilot\",\"status\":\"ok\",\"output\":$escaped,\"error\":\"\"}"
}

case "$ENGINE" in
  claude)  run_claude ;;
  codex)   run_codex ;;
  copilot) run_copilot ;;
  *) echo "{\"engine\":\"$ENGINE\",\"status\":\"error\",\"output\":\"\",\"error\":\"Unknown engine: $ENGINE. Use claude, codex, or copilot.\"}" ;;
esac
