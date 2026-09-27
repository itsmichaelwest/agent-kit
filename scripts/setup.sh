#!/bin/bash
# Single entry point for macOS/Linux setup.
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
export DOTFILES_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"

source "$SCRIPTS_DIR/lib/helpers.sh"

# setup.sh manages every target with `ln -s`. Under Git Bash / MSYS2 / Cygwin
# with the default MSYS setting, `ln -s` silently produces a plain copy instead
# of a Windows reparse point: it prints [LINK], returns success, and leaves a
# file that drifts from the repo forever. Windows has its own entry point that
# creates real junctions. OSTYPE is unreliable here (Git Bash reports `cygwin`
# on some builds and `msys` on others), so check uname and MSYSTEM too.
case "${OSTYPE:-}|$(uname -s 2>/dev/null)|${MSYSTEM:-}" in
  msys*|cygwin*|*MINGW*|*MSYS*|*CYGWIN*)
    err "setup.sh is the macOS/Linux entry point; it cannot manage links on Windows."
    err "Under MSYS/Cygwin 'ln -s' creates copies, not junctions, so every link would drift."
    err "Use the PowerShell entry point instead:"
    err "  .\\scripts\\setup.ps1 <command>"
    err "WSL is real Linux and is unaffected, but it manages a separate WSL-side install."
    exit 1
    ;;
esac

source "$SCRIPTS_DIR/lib/install-deps.sh"
source "$SCRIPTS_DIR/lib/install-toolchains.sh"
source "$SCRIPTS_DIR/lib/install-mcp.sh"
source "$SCRIPTS_DIR/lib/sync-codex-config.sh"
source "$SCRIPTS_DIR/lib/compile-agents.sh"
source "$SCRIPTS_DIR/lib/link-dotfiles.sh"
source "$SCRIPTS_DIR/lib/link-ai-agents.sh"
source "$SCRIPTS_DIR/lib/plugin-status.sh"
source "$SCRIPTS_DIR/lib/shell-config.sh"
source "$SCRIPTS_DIR/lib/update-skills.sh"
source "$SCRIPTS_DIR/lib/normalize-skills.sh"
source "$SCRIPTS_DIR/lib/reconcile-skills.sh"
source "$SCRIPTS_DIR/lib/uninstall-skill.sh"
source "$SCRIPTS_DIR/lib/doctor-skills.sh"
source "$SCRIPTS_DIR/lib/doctor-links.sh"
source "$SCRIPTS_DIR/lib/bootstrap-codex-plugins.sh"

bootstrap_claude_plugins() {
  bash "$SCRIPTS_DIR/lib/bootstrap-claude-plugins.sh"
}

ACTION=""
PROJECT_AGENTS=""
SKIP_SUBMODULES=0
DOCTOR_STRICT=""
SKILL_ARGS=()
UNINSTALL_SKILL=""
INSTALL_ALL=0

usage() {
  cat <<'EOF'
Usage: setup.sh <command> [options]

Commands:
  install             Choose dependencies, toolchains, links, and plugins
  compile-agents      Compile agent templates into tool outputs
  preview-codex-config  Preview owned-key updates and conflicts without writes
  capture-codex-config  Import changes to already-owned portable settings
  link                Link dotfiles and AI agent configs (no installs)
  link-dotfiles       Link base dotfiles only
  link-ai-agents      Link AI agent configs only
  shell               Inject zsh config into ~/.zshrc
  shell-remove        Remove injected zsh config from ~/.zshrc
  reset               Remove all links and injected shell config
  update-skills       Install/update skills from manifest and normalize known duplicate wrappers
  normalize-skills    Normalize known duplicate upstream skill wrappers
  install-skill       Interactively install one source via npx skills, reconcile, then doctor
  uninstall-skill     Uninstall one upstream skill, update manifest, then doctor
  list-skills         Show skills and install status
  reconcile-skills    Add out-of-band npx skills installs to manifest + lockfile
  doctor              Check skills manifest/lockfile/disk consistency and that
                      every link in ai-agent-links.json is in place
  bootstrap-claude    Install Claude Code plugins declared in settings.json
  bootstrap-codex     Install Codex plugins declared in config/codex/global.toml
  install-mcp         Install user-scope MCP servers from mcp/servers.json
  plugin-status       Show plugin status vs repo config
  status              Show current link status
  project-agents <path>  Link agents into a project

Options:
  --skip-submodules   Skip git submodule initialization
  --all               Install every component without prompts (install only)
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    install|compile-agents|capture-codex-config|preview-codex-config|link|link-dotfiles|link-ai-agents|shell|shell-remove|reset|status|update-skills|normalize-skills|list-skills|reconcile-skills|doctor|install-mcp|plugin-status|bootstrap-claude|bootstrap-codex)
      ACTION="$1" ;;
    install-skill)
      ACTION="install-skill"; shift; SKILL_ARGS=("$@"); break ;;
    uninstall-skill)
      ACTION="uninstall-skill"; UNINSTALL_SKILL="${2:-}"; shift ;;
    project-agents)
      ACTION="project-agents"; PROJECT_AGENTS="${2:-}"; shift ;;
    --skip-submodules) SKIP_SUBMODULES=1 ;;
    --all) INSTALL_ALL=1 ;;
    --strict) DOCTOR_STRICT="--strict" ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown: $1"; usage; exit 1 ;;
  esac
  shift
done

if [[ -z "$ACTION" ]]; then usage; exit 1; fi
if [[ $INSTALL_ALL -eq 1 && "$ACTION" != install ]]; then
  err "--all is only valid with install"
  exit 1
fi

install_selected() {
  local label="$1" answer
  if [[ $INSTALL_ALL -eq 1 ]]; then return 0; fi
  if [[ ! -r /dev/tty ]]; then
    err "Interactive install requires a terminal. Use 'setup.sh install --all' for unattended setup."
    exit 1
  fi
  while true; do
    read -r -p "$label [y/N]: " answer </dev/tty || {
      err "Could not read install selection. Use --all for unattended setup."
      exit 1
    }
    case "$answer" in
      [Yy]|[Yy][Ee][Ss]) return 0 ;;
      ""|[Nn]|[Nn][Oo]) return 1 ;;
      *) echo "Enter y or n." >/dev/tty ;;
    esac
  done
}

if [[ "$ACTION" == install && $INSTALL_ALL -eq 0 && ! -t 0 ]]; then
  err "Interactive install requires a terminal. Use 'setup.sh install --all' for unattended setup."
  exit 1
fi

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

  echo ""
  show_plugin_status

  # Shell config
  echo ""
  if grep -q "# >>> dotfiles zsh start" "$HOME/.zshrc" 2>/dev/null; then
    echo -e "  ${GREEN}[OK]${NC} ~/.zshrc contains dotfiles zsh block"
  else
    echo -e "  ${YELLOW}[MISSING]${NC} ~/.zshrc does not contain dotfiles zsh block"
  fi
}

case "$ACTION" in
  install)
    if install_selected "Install shell and CLI dependencies (including Python)?"; then install_deps; fi
    if install_selected "Install Node.js LTS and fnm?"; then install_toolchain fnm_node; fi
    if install_selected "Install Rust via rustup?"; then install_toolchain rustup; fi
    if install_selected "Compile agents and link configs?"; then
      compile_agents; sync_codex_config apply; link_dotfiles; link_ai_agents
    fi
    if install_selected "Inject the zsh config?"; then inject_zsh_config; fi
    if install_selected "Install MCP servers?"; then install_mcp; fi
    if install_selected "Install Claude Code plugins?"; then bootstrap_claude_plugins; fi
    if install_selected "Install Codex plugins?"; then bootstrap_codex_plugins; fi
    ;;
  install-mcp)    install_mcp ;;
  compile-agents) compile_agents; sync_codex_config apply ;;
  preview-codex-config) sync_codex_config preview ;;
  capture-codex-config) sync_codex_config capture ;;
  link)           compile_agents; sync_codex_config apply; link_dotfiles; link_ai_agents ;;
  link-dotfiles)  link_dotfiles ;;
  link-ai-agents) compile_agents; sync_codex_config apply; link_ai_agents ;;
  shell)          inject_zsh_config ;;
  shell-remove)   remove_zsh_config ;;
  reset)          unlink_dotfiles; unlink_ai_agents; uninstall_deps; uninstall_toolchains; remove_zsh_config ;;
  update-skills)  update_skills ;;
  normalize-skills) normalize_skills ;;
  install-skill)  install_skill "${SKILL_ARGS[@]}"; reconcile_skills; doctor_skills --strict ;;
  uninstall-skill) uninstall_skill "$UNINSTALL_SKILL"; doctor_skills --strict ;;
  list-skills)    list_skills ;;
  reconcile-skills) reconcile_skills ;;
  doctor)         doctor_rc=0
                  doctor_skills $DOCTOR_STRICT || doctor_rc=$?
                  doctor_links $DOCTOR_STRICT || doctor_rc=$?
                  if [[ $doctor_rc -ne 0 ]]; then exit $doctor_rc; fi
                  ;;
  bootstrap-claude) bootstrap_claude_plugins ;;
  bootstrap-codex) bootstrap_codex_plugins ;;
  plugin-status)  show_plugin_status ;;
  status)         show_status ;;
  project-agents)
    [[ -z "$PROJECT_AGENTS" ]] && { err "Missing project path"; exit 1; }
    [[ ! -d "$PROJECT_AGENTS" ]] && { err "Not a directory: $PROJECT_AGENTS"; exit 1; }
    info "Linking agents into: $PROJECT_AGENTS"
    ensure_linked "$DOTFILES_DIR/agents" "$PROJECT_AGENTS/.claude/agents"
    ;;
esac

info "Done"
