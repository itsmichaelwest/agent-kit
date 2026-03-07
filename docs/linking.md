# Linking

The setup scripts create symlinks from this repo into tool-specific config directories. Everything uses `ensure_linked` which is idempotent — safe to re-run at any time.

## Commands

```bash
# macOS/Linux
./scripts/setup.sh link              # link everything
./scripts/setup.sh link-dotfiles     # base dotfiles only
./scripts/setup.sh link-ai-agents    # AI agent configs only
./scripts/setup.sh shell             # inject zsh config into ~/.zshrc
./scripts/setup.sh shell-remove      # remove injected zsh block
./scripts/setup.sh status            # show what's linked
./scripts/setup.sh project-agents ~/Developer/my-project  # per-project agents
```

```powershell
# Windows
.\scripts\setup.ps1 link
.\scripts\setup.ps1 link-dotfiles
.\scripts\setup.ps1 link-ai-agents
.\scripts\setup.ps1 status
.\scripts\setup.ps1 project-agents -ProjectPath F:\my-project
```

## Base Dotfiles

| Source | Target | Notes |
|--------|--------|-------|
| `.gitconfig` | `~/.gitconfig` | Only if file exists in repo |
| `.gitignore_global` | `~/.gitignore_global` | Only if file exists in repo |
| `.tmux.conf` | `~/.tmux.conf` | macOS/Linux only |
| `.vimrc` | `~/.vimrc` | macOS/Linux only |
| `.config/starship.toml` | `~/.config/starship.toml` | Only if file exists in repo |
| `shell/powershell/...` | `~/Documents/PowerShell/...` | Windows only |

All base dotfile links are optional — if the source file doesn't exist in the repo, it's silently skipped.

## GitHub / Copilot (VS Code)

| Source | Target |
|--------|--------|
| `.github/copilot-instructions.md` | `~/.github/copilot-instructions.md` |
| `.github/prompts` | `~/.github/prompts` |
| `agents/` | `~/.github/agents` |

## AI Agent Configs

### Claude Code

| Source | Target |
|--------|--------|
| `AGENTS.md` | `~/.claude/CLAUDE.md` |
| `prompts/` | `~/.claude/commands` |
| `skills/` | `~/.claude/skills` |
| `docs/` | `~/.claude/docs` |
| `agents/` | `~/.claude/agents` |

### Codex CLI

| Source | Target |
|--------|--------|
| `AGENTS.md` | `~/.codex/AGENTS.md` |
| `prompts/` | `~/.codex/prompts` |
| `skills/` | `~/.codex/skills` |
| `docs/` | `~/.codex/docs` |

### Copilot CLI

| Source | Target |
|--------|--------|
| `AGENTS.md` | `~/.copilot/instructions.md` |
| `prompts/` | `~/.copilot/prompts` |
| `skills/` | `~/.copilot/skills` |
| `docs/` | `~/.copilot/docs` |
| `agents/` | `~/.copilot/agents` |

## Shell Config (macOS/Linux)

`setup.sh shell` injects the contents of `shell/zsh/shared.zsh` into `~/.zshrc` between markers:

```
# >>> dotfiles zsh start
(contents of shared.zsh)
# <<< dotfiles zsh end
```

This is idempotent — re-running replaces the block in place. A backup of `~/.zshrc` is created on first run. Platform-specific snippets (`shell/zsh/macos.zsh`, `shell/zsh/linux.zsh`) are appended if present.

Use `setup.sh shell-remove` to cleanly remove the injected block.

## Windows-Specific

On Windows, `link-dotfiles` also handles:
- **PowerShell profile** → `~/Documents/PowerShell/` and `~/Documents/WindowsPowerShell/`
- **Windows Terminal settings** → auto-detected from installed Terminal package (stable + preview)

## Per-Project Agents

Link your global agents into a specific project:

```bash
./scripts/setup.sh project-agents ~/Developer/my-project
# Creates: my-project/.claude/agents -> dotfiles/agents
```
