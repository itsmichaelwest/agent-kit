# Dependencies

`scripts/setup.sh install` (macOS/Linux) and `scripts/setup.ps1 install` (Windows)
prompt for dependencies, Node.js, Rust, linking, and plugin setup. The macOS/Linux
installer also prompts for zsh config and MCP servers. Answer `y` for each
component you want; Enter skips it. Use `install --all` or `install -All` to
attempt every component without prompts. The unattended flags require no
prompt library. Linking still needs Python 3.11+; install it first or select
the dependency step.

## macOS / Linux

| Tool | Purpose | Install method |
|------|---------|----------------|
| zsh | Shell | brew / apt / pacman |
| [Oh My Zsh](https://ohmyz.sh/) | Zsh plugin framework | install script |
| [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) | History-based command suggestions | git clone into OMZ |
| [fast-syntax-highlighting](https://github.com/zdharma-continuum/fast-syntax-highlighting) | Command syntax coloring | git clone into OMZ |
| Python 3.11+ | Runtime for setup/compiler scripts | Homebrew `python` (macOS), apt/pacman (Linux) |
| [Starship](https://starship.rs/) | Cross-shell prompt | install script / brew |
| [fnm](https://github.com/Schniz/fnm) | Fast Node version manager | install script |
| [rustup](https://rustup.rs/) | Rust toolchain installer/manager | install script |
| [eza](https://eza.rocks/) | Modern `ls` replacement | brew / apt / pacman |
| [fzf](https://github.com/junegunn/fzf) | Fuzzy finder | brew / apt / pacman |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep | brew / apt / pacman |
| [fd](https://github.com/sharkdp/fd) | Fast find | brew / apt / pacman |
| [bat](https://github.com/sharkdp/bat) | `cat` with syntax highlighting | brew / apt / pacman |
| [ast-grep](https://ast-grep.github.io/) | Structural code search | brew / npm |
| git, curl, wget | Essentials | brew / apt / pacman |

### Zsh plugins (built into Oh My Zsh, no install needed)

| Plugin | Purpose |
|--------|---------|
| `git` | Git aliases (`gst`, `gp`, `gcmsg`, etc.) |
| `sudo` | Double-tap Escape to prepend `sudo` |
| `z` | Jump to frequently-used directories |

## Windows

The installer supports x64 and ARM64 Windows. It stops with an explicit error
on x86 Windows, where the current fnm package has no native installer.

| Tool | Purpose | Install method |
|------|---------|----------------|
| [PowerShell 7](https://github.com/PowerShell/PowerShell) | Modern PowerShell runtime | winget (auto-installed by setup) |
| [Oh My Posh](https://ohmyposh.dev/) | Prompt theming | winget |
| [Starship](https://starship.rs/) | Cross-shell prompt | winget |
| [fnm](https://github.com/Schniz/fnm) | Fast Node version manager on x64 | winget |
| Node.js LTS (ARM64) | Native Node runtime on Windows ARM64 | winget `OpenJS.NodeJS.LTS --architecture arm64` |
| [rustup](https://rustup.rs/) | Rust toolchain installer/manager | Architecture-specific rustup-init |
| [eza](https://eza.rocks/) | Modern `ls` replacement | winget |
| [fzf](https://github.com/junegunn/fzf) | Fuzzy finder | winget |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep | winget |
| [fd](https://github.com/sharkdp/fd) | Fast find | winget |
| [bat](https://github.com/sharkdp/bat) | `cat` with syntax highlighting | winget |
| [GitHub CLI](https://cli.github.com/) | GitHub from the terminal | winget |
| [Python Install Manager](https://apps.microsoft.com/detail/9nq7512cxl7t) + latest stable Python | Runtime for setup/compiler scripts | WinGet Store package, then `pymanager install --update default` (or `3-arm64` on ARM64) |

The Windows installer selects packages with WinGet's `--architecture` option.
On ARM64, setup checks WinGet for a native installer first. When only an x64
installer is available, it asks whether to install that version under Windows
emulation. The default answer skips it. `-All` also skips x64 fallbacks; use
`-All -AllowX64Fallback` to opt in without prompts. Packages that still fail
are listed as skipped. Setup installs an ARM64 Python runtime by
explicit tag and checks the resulting Python, Node, and Rust architectures.
PowerShell, Python, Node.js, and Rust remain native-only install steps.
Setup resolves WinGet's portable-command symbolic links, verifies installed
MSIX commands through their app aliases, and checks Coreutils through
`coreutils-manager`. WinGet's "No available upgrade found"
result still requires an architecture check; it does not mean installation failed.
If an x64 Node.js or rustup executable already exists on ARM64, toolchain
installation stops and asks you to remove that conflicting installation.
Rust's MSVC target also needs Visual Studio C++ build tools and a Windows SDK
to link native programs; install those separately if they are not already present.

### Choose Windows install components

In an interactive PowerShell session, `setup.ps1 install` asks these questions
in order. Press Enter to skip a step. The PowerShell 7 question appears only
when setup starts in Windows PowerShell 5.1 and PowerShell 7 is absent.

```text
Install PowerShell 7 to run setup? [y/N]:
Install CLI dependencies and Python? [y/N]:
WinGet found no ARM64 installer for eza. Install its x64 version under emulation? [y/N]:
Install Node.js LTS? [y/N]:
Install Rust via rustup? [y/N]:
Compile agents and link configs? [y/N]:
Install Claude Code plugins? [y/N]:
Install Codex plugins? [y/N]:
```

The x64 question appears once per selected CLI package only when WinGet offers
an x64 installer but no ARM64 installer. The package name in that question
varies with the available installers. `-All` skips selection questions and x64
fallbacks. Add `-AllowX64Fallback` to `-All` to install those x64 packages
without questions.

### PowerShell modules

| Module | Purpose |
|--------|---------|
| [PSReadLine](https://github.com/PowerShell/PSReadLine) | History predictions, syntax coloring |
| [Terminal-Icons](https://github.com/devblackops/Terminal-Icons) | File icons in directory listings |
| [z](https://github.com/badmotorfinger/z) | Jump to frecent directories |
| [PSFzf](https://github.com/kelleyma49/PSFzf) | Fuzzy finder (Ctrl+R history, Ctrl+T files) |
