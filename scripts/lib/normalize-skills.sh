#!/bin/bash
# Sourced by setup.sh — expects DOTFILES_DIR to be set.

normalize_skills() {
  python3 "$DOTFILES_DIR/scripts/lib/normalize-skills.py" --repo-root "$DOTFILES_DIR"
}
