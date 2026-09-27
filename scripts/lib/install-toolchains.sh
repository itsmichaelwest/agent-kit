#!/bin/bash
# Install language toolchains (macOS/Linux): fnm/Node.js, Rust (rustup).
# Sourced by setup.sh — expects helpers.sh already loaded.

check_native_toolchain_host() {
  if [[ "$(uname -s)" == Darwin && "$(sysctl -n hw.optional.arm64 2>/dev/null || true)" == 1 && "$(uname -m)" != arm64 ]]; then
    err "This terminal is running under Rosetta on Apple silicon. Open a native terminal before installing toolchains."
    return 1
  fi
}

toolchain_installed_fnm_node() {
  command -v fnm &>/dev/null || return 1
  eval "$(fnm env)" 2>/dev/null
  fnm list 2>/dev/null | grep -q lts-latest || return 1
  fnm use lts-latest &>/dev/null || return 1
  [[ "$(node -p 'process.arch' 2>/dev/null)" == "$(native_node_arch)" ]]
}

native_node_arch() {
  case "$(uname -m)" in
    arm64|aarch64) echo arm64 ;;
    x86_64|amd64) echo x64 ;;
    i386|i686) echo x86 ;;
    *) err "Unsupported Node.js architecture: $(uname -m)"; return 1 ;;
  esac
}

toolchain_install_fnm_node() {
  command -v fnm &>/dev/null || {
    info "Installing fnm..."
    if [[ "$(uname -s)" == Darwin ]]; then
      curl -fsSL https://fnm.vercel.app/install | bash -s -- --force-install --skip-shell
      export PATH="$HOME/Library/Application Support/fnm:$HOME/.fnm:$PATH"
    else
      curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
      export PATH="$HOME/.local/share/fnm:$HOME/.fnm:$PATH"
    fi
  }
  command -v fnm &>/dev/null || { err "fnm is not available after installation"; return 1; }
  eval "$(fnm env)" 2>/dev/null
  if command -v fnm &>/dev/null; then
    local node_arch
    node_arch="$(native_node_arch)" || return 1
    if fnm list | grep -q lts-latest; then
      fnm use lts-latest &>/dev/null || true
      if [[ "$(node -p 'process.arch' 2>/dev/null)" == "$node_arch" ]]; then return 0; fi
    fi
    info "Installing latest Node.js LTS via fnm..."
    fnm install --lts --arch "$node_arch"
    fnm default lts-latest
    fnm use lts-latest
    [[ "$(node -p 'process.arch' 2>/dev/null)" == "$node_arch" ]] || {
      err "Node.js is not running as native $node_arch"
      return 1
    }
  fi
}

toolchain_installed_rustup() {
  command -v rustup &>/dev/null || return 1
  local host
  host="$(rustc -vV 2>/dev/null | sed -n 's/^host: //p')"
  [[ "$host" == "$(native_rust_host)" ]]
}

native_rust_host() {
  case "$(uname -s):$(uname -m)" in
    Darwin:arm64) echo aarch64-apple-darwin ;;
    Darwin:x86_64) echo x86_64-apple-darwin ;;
    Linux:aarch64) echo aarch64-unknown-linux-gnu ;;
    Linux:x86_64) echo x86_64-unknown-linux-gnu ;;
    *) err "Unsupported Rust host: $(uname -s) $(uname -m)"; return 1 ;;
  esac
}

toolchain_install_rustup() {
  local host
  host="$(native_rust_host)" || return 1
  if command -v rustup &>/dev/null; then
    info "Selecting native Rust host $host..."
    rustup set default-host "$host"
    rustup toolchain install stable --profile default
    rustup default stable
  else
    info "Installing rustup for $host..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile default --default-host "$host"
    export PATH="$HOME/.cargo/bin:$PATH"
  fi
  toolchain_installed_rustup || {
    err "Rust is not using the native host target"
    return 1
  }
}

install_toolchain() {
  local name="$1"
  check_native_toolchain_host || return 1
  if "toolchain_installed_${name}"; then
    info "[OK] $name"
  else
    "toolchain_install_${name}"
  fi
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
