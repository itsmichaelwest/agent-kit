#!/bin/bash
# Single entry point for macOS/Linux setup.
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
export DOTFILES_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"

source "$SCRIPTS_DIR/lib/helpers.sh"
source "$SCRIPTS_DIR/lib/install-deps.sh"
source "$SCRIPTS_DIR/lib/link-dotfiles.sh"
source "$SCRIPTS_DIR/lib/link-ai-agents.sh"
source "$SCRIPTS_DIR/lib/shell-config.sh"
source "$SCRIPTS_DIR/lib/update-skills.sh"

ACTION=""
PROJECT_AGENTS=""
SKIP_SUBMODULES=0

usage() {
  cat <<'EOF'
Usage: setup.sh <command> [options]

Commands:
  install             Full setup: deps + links + shell config
  link                Link dotfiles and AI agent configs (no installs)
  link-dotfiles       Link base dotfiles only
  link-ai-agents      Link AI agent configs only
  shell               Inject zsh config into ~/.zshrc
  shell-remove        Remove injected zsh config from ~/.zshrc
  reset               Remove all links and injected shell config
  update-skills       Install/update skills from manifest
  list-skills         Show skills and install status
  status              Show current link status
  project-agents <path>  Link agents into a project

Options:
  --skip-submodules   Skip git submodule initialization
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    install|link|link-dotfiles|link-ai-agents|shell|shell-remove|reset|status|update-skills|list-skills)
      ACTION="$1" ;;
    project-agents)
      ACTION="project-agents"; PROJECT_AGENTS="${2:-}"; shift ;;
    --skip-submodules) SKIP_SUBMODULES=1 ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown: $1"; usage; exit 1 ;;
  esac
  shift
done

if [[ -z "$ACTION" ]]; then usage; exit 1; fi

# Submodules
if [[ $SKIP_SUBMODULES -eq 0 && -f "$DOTFILES_DIR/.gitmodules" ]]; then
  info "Initializing git submodules..."
  git -C "$DOTFILES_DIR" submodule update --init --recursive 2>/dev/null || warn "Submodule init failed"
fi

# Status
show_status() {
  info "Current link status"
  echo ""

  # Dotfiles
  info "Dotfiles:"
  for target in "$HOME/.gitconfig" "$HOME/.gitignore_global" "$HOME/.config/starship.toml"; do
    if [[ -L "$target" ]]; then
      echo -e "  ${GREEN}[OK]${NC} $target -> $(readlink "$target")"
    elif [[ -e "$target" ]]; then
      echo -e "  ${YELLOW}[EXISTS]${NC} $target (not a symlink)"
    else
      echo -e "  ${RED}[MISSING]${NC} $target"
    fi
  done

  # AI agents (from manifest)
  echo ""
  info "AI agent links:"
  show_ai_agent_status

  # Shell config
  echo ""
  if grep -q "# >>> dotfiles zsh start" "$HOME/.zshrc" 2>/dev/null; then
    echo -e "  ${GREEN}[OK]${NC} ~/.zshrc contains dotfiles zsh block"
  else
    echo -e "  ${YELLOW}[MISSING]${NC} ~/.zshrc does not contain dotfiles zsh block"
  fi
}

case "$ACTION" in
  install)        install_deps; link_dotfiles; link_ai_agents; inject_zsh_config ;;
  link)           link_dotfiles; link_ai_agents ;;
  link-dotfiles)  link_dotfiles ;;
  link-ai-agents) link_ai_agents ;;
  shell)          inject_zsh_config ;;
  shell-remove)   remove_zsh_config ;;
  reset)          unlink_dotfiles; unlink_ai_agents; remove_zsh_config ;;
  update-skills)  update_skills ;;
  list-skills)    list_skills ;;
  status)         show_status ;;
  project-agents)
    [[ -z "$PROJECT_AGENTS" ]] && { err "Missing project path"; exit 1; }
    [[ ! -d "$PROJECT_AGENTS" ]] && { err "Not a directory: $PROJECT_AGENTS"; exit 1; }
    info "Linking agents into: $PROJECT_AGENTS"
    ensure_linked "$DOTFILES_DIR/agents" "$PROJECT_AGENTS/.claude/agents"
    ;;
esac

info "Done"
