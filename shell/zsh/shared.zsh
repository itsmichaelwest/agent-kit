# =============================================================================
# ZSH CONFIGURATION
# =============================================================================

# Oh My Zsh Setup
export ZSH="$HOME/.oh-my-zsh"

plugins=(
    git                        # git aliases (gst, gp, gcmsg, etc.)
    sudo                       # double-tap Esc to prepend sudo
    z                          # jump to frecent dirs (z proj → ~/Projects)
    zsh-autosuggestions        # ghost-text from history, accept with →
    fast-syntax-highlighting   # colors valid/invalid commands
)

source $ZSH/oh-my-zsh.sh

# =============================================================================
# PATH
# =============================================================================

export PATH="$HOME/.local/bin:$PATH"

# Node (fnm)
if [ -d "$HOME/.local/share/fnm" ]; then
  export PATH="$HOME/.local/share/fnm:$PATH"
  eval "$(fnm env --use-on-cd --shell zsh)"
fi

# Bun
[ -d "$HOME/.bun/bin" ] && export PATH="$HOME/.bun/bin:$PATH"

# Rust
[ -d "$HOME/.cargo/bin" ] && export PATH="$HOME/.cargo/bin:$PATH"

# =============================================================================
# PROMPT & TOOLS
# =============================================================================

# Prompt + line-editor integrations need a real terminal. Skip them when there
# isn't one (e.g. `zsh -i -c "..."`) to avoid "can't change option: zle" noise.
if [[ -t 1 ]]; then
  eval "$(starship init zsh)"

  # fzf: prefer the modern integration, fall back to legacy files for older fzf
  # (e.g. Debian/Ubuntu apt ships 0.44.x, but `--zsh` was added in 0.48.0).
  if command -v fzf &>/dev/null; then
    if fzf --help 2>&1 | grep -q -- '--zsh'; then
      source <(fzf --zsh)
    else
      for f in \
        /usr/share/doc/fzf/examples/key-bindings.zsh \
        /usr/share/doc/fzf/examples/completion.zsh \
        /usr/share/fzf/key-bindings.zsh \
        /usr/share/fzf/completion.zsh; do
        [[ -f "$f" ]] && source "$f"
      done
    fi
  fi
fi
