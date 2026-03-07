#!/bin/bash
# Link base dotfiles and config dirs.
# Sourced by setup.sh — expects helpers.sh already loaded and DOTFILES_DIR set.

unlink_dotfiles() {
  info "Removing dotfile links..."
  remove_link "$HOME/.gitconfig"
  remove_link "$HOME/.gitignore_global"
  remove_link "$HOME/.tmux.conf"
  remove_link "$HOME/.vimrc"
  remove_link "$HOME/.config/starship.toml"
}

link_dotfiles() {
  info "Linking base dotfiles..."
  ensure_linked "$DOTFILES_DIR/.gitconfig"        "$HOME/.gitconfig"
  ensure_linked "$DOTFILES_DIR/.gitignore_global" "$HOME/.gitignore_global"
  ensure_linked "$DOTFILES_DIR/.tmux.conf"        "$HOME/.tmux.conf"
  ensure_linked "$DOTFILES_DIR/.vimrc"            "$HOME/.vimrc"

  info "Linking config directories..."
  mkdir -p "$HOME/.config"
  ensure_linked "$DOTFILES_DIR/.config/starship.toml" "$HOME/.config/starship.toml"
}
