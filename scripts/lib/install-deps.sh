#!/bin/bash
# Install dependencies (macOS/Linux).
# Sourced by setup.sh — expects helpers.sh already loaded.

install_deps() {
  local os
  os=$(detect_os)
  info "Detected OS: $os"

  if [[ "$os" == "unknown" ]]; then err "Unsupported OS"; exit 1; fi
  if [[ $EUID -eq 0 ]]; then err "Do not run as root"; exit 1; fi

  # Package manager
  case $os in
    macos)
      if ! command -v brew &>/dev/null; then
        info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      fi
      brew update
      ;;
    arch)   sudo pacman -Syu --noconfirm ;;
    ubuntu) sudo apt update ;;
  esac

  # Zsh
  if ! command -v zsh &>/dev/null; then
    info "Installing zsh..."
    case $os in
      macos)  brew install zsh ;;
      arch)   sudo pacman -S --noconfirm zsh ;;
      ubuntu) sudo apt install -y zsh ;;
    esac
  fi

  # Oh My Zsh
  if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
    info "Installing oh-my-zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
  fi

  # Zsh plugins (external)
  local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
  local plugins=(
    "zsh-autosuggestions|https://github.com/zsh-users/zsh-autosuggestions"
    "fast-syntax-highlighting|https://github.com/zdharma-continuum/fast-syntax-highlighting"
  )
  for entry in "${plugins[@]}"; do
    IFS='|' read -r name url <<< "$entry"
    if [[ ! -d "$zsh_custom/plugins/$name" ]]; then
      info "Installing $name..."
      git clone "$url" "$zsh_custom/plugins/$name"
    fi
  done

  # CLI tools
  info "Installing CLI tools..."
  case $os in
    macos)  brew install git gh curl wget ripgrep fd bat fzf eza starship ast-grep ;;
    arch)   sudo pacman -S --noconfirm git github-cli curl wget ripgrep fd bat fzf eza starship ast-grep ;;
    ubuntu)
      sudo apt install -y git gh curl wget ripgrep fd-find bat fzf
      [[ -f /usr/bin/fdfind && ! -f /usr/bin/fd ]] && sudo ln -s /usr/bin/fdfind /usr/bin/fd
      [[ -f /usr/bin/batcat && ! -f /usr/bin/bat ]] && sudo ln -s /usr/bin/batcat /usr/bin/bat
      if ! command -v eza &>/dev/null; then
        sudo apt install -y gpg
        sudo mkdir -p /etc/apt/keyrings
        wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
        echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
        sudo apt update && sudo apt install -y eza
      fi
      command -v starship &>/dev/null || curl -sS https://starship.rs/install.sh | sh -s -- -y
      if ! command -v ast-grep &>/dev/null; then
        if command -v npm &>/dev/null; then npm install -g @ast-grep/cli
        else warn "npm not found, skipping ast-grep"; fi
      fi
      ;;
  esac

  # fnm
  command -v fnm &>/dev/null || {
    info "Installing fnm..."
    curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
  }

  # Default shell
  if [[ "${SHELL##*/}" != "zsh" ]]; then
    info "Setting zsh as default shell..."
    chsh -s "$(which zsh)"
    info "Log out and back in for the shell change to take effect"
  fi
}
