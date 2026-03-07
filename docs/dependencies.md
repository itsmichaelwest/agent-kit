# Dependencies

Tools installed by `scripts/setup.sh install` (macOS/Linux) and `scripts/setup.ps1 install` (Windows).

## macOS / Linux

| Tool | Purpose | Install method |
|------|---------|----------------|
| zsh | Shell | brew / apt / pacman |
| [Oh My Zsh](https://ohmyz.sh/) | Zsh plugin framework | install script |
| [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) | History-based command suggestions | git clone into OMZ |
| [fast-syntax-highlighting](https://github.com/zdharma-continuum/fast-syntax-highlighting) | Command syntax coloring | git clone into OMZ |
| [Starship](https://starship.rs/) | Cross-shell prompt | install script / brew |
| [fnm](https://github.com/Schniz/fnm) | Fast Node version manager | install script |
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

| Tool | Purpose | Install method |
|------|---------|----------------|
| [Oh My Posh](https://ohmyposh.dev/) | Prompt theming | winget |
| [Starship](https://starship.rs/) | Cross-shell prompt | winget |
| [fnm](https://github.com/Schniz/fnm) | Fast Node version manager | winget |
| [eza](https://eza.rocks/) | Modern `ls` replacement | winget |
| [fzf](https://github.com/junegunn/fzf) | Fuzzy finder | winget |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep | winget |
| [fd](https://github.com/sharkdp/fd) | Fast find | winget |
| [bat](https://github.com/sharkdp/bat) | `cat` with syntax highlighting | winget |
| [GitHub CLI](https://cli.github.com/) | GitHub from the terminal | winget |
| Git | Version control | winget |

### PowerShell modules

| Module | Purpose |
|--------|---------|
| [PSReadLine](https://github.com/PowerShell/PSReadLine) | History predictions, syntax coloring |
| [Terminal-Icons](https://github.com/devblackops/Terminal-Icons) | File icons in directory listings |
| [z](https://github.com/badmotorfinger/z) | Jump to frecent directories |
| [PSFzf](https://github.com/kelleyma49/PSFzf) | Fuzzy finder (Ctrl+R history, Ctrl+T files) |
