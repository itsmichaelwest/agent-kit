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

eval "$(starship init zsh)"
source <(fzf --zsh)
