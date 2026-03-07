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

  # Break lingering symlink
  if [[ -L "$zshrc" ]]; then
    warn "Removing ~/.zshrc symlink so we can manage the file directly"
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

  # Replace existing block or append
  if grep -q "$MARK_START" "$zshrc"; then
    awk -v start="$MARK_START" -v end="$MARK_END" -v block="$block" '
      $0 == start { print block; skip=1; next }
      $0 == end { skip=0; next }
      !skip { print }
    ' "$zshrc" > "$zshrc.tmp" && mv "$zshrc.tmp" "$zshrc"
  else
    printf '\n%s\n' "$block" >> "$zshrc"
  fi

  info "Injected dotfiles zsh config into ~/.zshrc"
}

remove_zsh_config() {
  local zshrc="$HOME/.zshrc"
  if [[ ! -f "$zshrc" ]] || ! grep -q "$MARK_START" "$zshrc"; then
    warn "No managed zsh block found to remove"
    return
  fi

  awk -v start="$MARK_START" -v end="$MARK_END" '
    $0 == start { skip=1; next }
    $0 == end { skip=0; next }
    !skip { print }
  ' "$zshrc" > "$zshrc.tmp" && mv "$zshrc.tmp" "$zshrc"

  info "Removed dotfiles zsh block from ~/.zshrc"
}
