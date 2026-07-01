#!/bin/bash
# Install language toolchains (macOS/Linux): fnm/Node.js, Rust (rustup).
# Sourced by setup.sh — expects helpers.sh already loaded.

toolchains=(fnm_node rustup)

toolchain_installed_fnm_node() {
  command -v fnm &>/dev/null || return 1
  eval "$(fnm env)" 2>/dev/null
  fnm list 2>/dev/null | grep -q lts-latest
}

toolchain_install_fnm_node() {
  command -v fnm &>/dev/null || {
    info "Installing fnm..."
    curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
  }
  eval "$(fnm env)" 2>/dev/null
  if command -v fnm &>/dev/null && ! fnm list | grep -q lts-latest; then
    info "Installing latest Node.js LTS via fnm..."
    fnm install --lts
    fnm default lts-latest
  fi
}

toolchain_installed_rustup() {
  command -v rustup &>/dev/null
}

toolchain_install_rustup() {
  info "Installing rustup..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile default
}

install_toolchains() {
  info "Installing toolchains..."
  local name
  for name in "${toolchains[@]}"; do
    if "toolchain_installed_${name}"; then
      info "[OK] $name"
    else
      "toolchain_install_${name}"
    fi
  done
}

uninstall_toolchains() {
  info "Removing toolchains..."

  if command -v rustup &>/dev/null; then
    info "Removing rustup..."
    rustup self uninstall -y
  fi

  if [[ -d "$HOME/.local/share/fnm" ]]; then
    info "Removing fnm..."
    rm -rf "$HOME/.local/share/fnm"
  elif [[ -d "$HOME/.fnm" ]]; then
    info "Removing fnm..."
    rm -rf "$HOME/.fnm"
  fi
}
