#!/bin/bash
# Inject/remove zsh config in ~/.zshrc.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

MARK_START="# >>> dotfiles zsh start"
MARK_END="# <<< dotfiles zsh end"
SHELL_DIR="$DOTFILES_DIR/shell/zsh"

inject_zsh_config() {
  local zshrc="$HOME/.zshrc"

  if [[ ! -f "$SHELL_DIR/shared.zsh" ]]; then
    err "Missing: $SHELL_DIR/shared.zsh"
    exit 1
  fi

  if [[ -L "$zshrc" ]]; then
    local target
    target="$(readlink "$zshrc")"
    warn "Removing ~/.zshrc symlink ($target) so we can manage the file directly"
    rm "$zshrc"
  fi

  # Backup on first run
  if [[ -f "$zshrc" ]]; then
    if ! grep -q "$MARK_START" "$zshrc"; then
      cp "$zshrc" "$zshrc.backup.$(date +%Y%m%d_%H%M%S)"
      info "Created ~/.zshrc backup"
    fi
  else
    touch "$zshrc"
  fi

  # Build the block
  local block
  block="$MARK_START"$'\n'
  block+="$(cat "$SHELL_DIR/shared.zsh")"$'\n'
  local uname_s
  uname_s="$(uname -s)"
  case "$uname_s" in
    Darwin) [[ -f "$SHELL_DIR/macos.zsh" ]] && block+=$'\n'"$(cat "$SHELL_DIR/macos.zsh")"$'\n' ;;
    Linux)  [[ -f "$SHELL_DIR/linux.zsh" ]] && block+=$'\n'"$(cat "$SHELL_DIR/linux.zsh")"$'\n' ;;
  esac
  block+="$MARK_END"

  python3 - "$zshrc" "$MARK_START" "$MARK_END" "$block" <<'PY'
from pathlib import Path
import re
import sys

zshrc = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
block = sys.argv[4]
content = zshrc.read_text() if zshrc.exists() else ""
pattern = re.compile(rf"\n?{re.escape(start)}\n.*?\n{re.escape(end)}\n?", re.DOTALL)
replacement = f"\n{block}\n"

if re.search(pattern, content):
    updated = re.sub(pattern, replacement, content, count=1)
else:
    updated = content.rstrip("\n") + replacement

zshrc.write_text(updated.lstrip("\n"))
PY

  info "Injected dotfiles zsh config into ~/.zshrc"
}

remove_zsh_config() {
  local zshrc="$HOME/.zshrc"
  if [[ -L "$zshrc" ]]; then
    local target
    target="$(readlink "$zshrc")"
    warn "Removing ~/.zshrc symlink ($target) so we can manage the file directly"
    rm "$zshrc"
    touch "$zshrc"
  fi

  if [[ ! -f "$zshrc" ]] || ! grep -q "$MARK_START" "$zshrc"; then
    warn "No managed zsh block found to remove"
    return
  fi

  python3 - "$zshrc" "$MARK_START" "$MARK_END" <<'PY'
from pathlib import Path
import re
import sys

zshrc = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
content = zshrc.read_text()
pattern = re.compile(rf"\n?{re.escape(start)}\n.*?\n{re.escape(end)}\n?", re.DOTALL)
updated = re.sub(pattern, "\n", content, count=1).strip("\n")
zshrc.write_text(updated + ("\n" if updated else ""))
PY

  info "Removed dotfiles zsh block from ~/.zshrc"
}
