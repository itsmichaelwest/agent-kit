# agent-kit

AI agent workspace, personal dotfiles, and shell configs for Windows, macOS, and Linux.

## Getting Started

### Windows (PowerShell)

```powershell
git clone https://github.com/itsmichaelwest/agent-kit.git
cd agent-kit

# Full setup: installs deps via winget, links configs
.\scripts\setup.ps1 install

# Or just link configs (no installs)
.\scripts\setup.ps1 link
```

### macOS / Linux

```bash
git clone https://github.com/itsmichaelwest/agent-kit.git
cd agent-kit

# Full setup: installs deps, links configs, sets up shell
./scripts/setup.sh install

# Or just link configs (no installs)
./scripts/setup.sh link
```

## Repository Layout

```
agent-kit/
├── AGENTS.md                  # Global AI agent instructions
├── agents/                    # Claude agent definitions (.md)
├── .claude/                   # Claude Code settings
├── .codex/
│   ├── config.toml            # Codex config + agent registry
│   └── agents/                # Codex agent definitions (.toml)
├── prompts/                   # Slash commands (shared across tools)
├── skills/                    # Canonical global skill source
├── docs/                      # Reference docs for agents
├── shell/
│   ├── zsh/shared.zsh         # Zsh config (injected into ~/.zshrc)
│   └── powershell/            # PowerShell profile
└── scripts/
    ├── setup.sh               # macOS/Linux entry point
    ├── setup.ps1              # Windows entry point
    ├── ai-agent-links.json    # Symlink manifest for AI tools
    ├── skills-manifest.json   # Skills to install from GitHub repos
    └── lib/                   # Modular script components
```

## What Gets Installed

See [docs/dependencies.md](docs/dependencies.md) for the full list of tools installed by `setup.sh install` / `setup.ps1 install`.

## What Gets Linked

The setup scripts symlink agents, skills, prompts, and docs into the config directories for each supported AI tool (GitHub Copilot CLI, Codex, Claude Code). Most static link targets are defined declaratively in [`scripts/ai-agent-links.json`](scripts/ai-agent-links.json); a few tool-specific migrations are handled directly in the setup scripts.

See [docs/linking.md](docs/linking.md) for the full mapping.
See [docs/plugins.md](docs/plugins.md) for the plugin model and config surfaces.

For existing machines, the supported upgrade path is to pull the latest repo and re-run `./scripts/setup.sh link` or `.\scripts\setup.ps1 link`. The scripts migrate legacy targets in place, back up conflicting non-symlink files or directories, and relink the current global layout.

## Agents

Agents are specialized personas with distinct roles, models, and instructions. Each agent is defined twice: as a `.md` source file for Claude Code and Copilot (`agents/`) and a `.toml` file for Codex CLI (`.codex/agents/`). During setup, Copilot-compatible global agent links are created with the required `*.agent.md` filenames under `~/.copilot/agents/`.

## Skills

Skills are domain-specific knowledge packs that give agents deeper expertise. Each skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`) and supporting reference files. The repo `skills/` directory is the canonical global source and is linked into both `~/.agents/skills` and tool-specific locations that still need them.

### Managing skills

Skills are sourced from community GitHub repos and tracked in [`scripts/skills-manifest.json`](scripts/skills-manifest.json).

```bash
# Install/update all skills from the manifest
./scripts/setup.sh update-skills

# Show installed vs missing skills
./scripts/setup.sh list-skills
```

### Adding a skill

To add a community skill, add an entry to `scripts/skills-manifest.json`:

```json
{ "name": "my-skill", "repo": "owner/repo", "path": "skills/my-skill" }
```

Then run `./scripts/setup.sh update-skills`.

To create a local skill, drop a folder into `skills/` with a `SKILL.md` containing YAML frontmatter.

## Plugins

Plugins are managed from the tool-native config files already in the repo.

```bash
./scripts/setup.sh plugin-status
```

Plugin payloads are not committed to the repo. Desired plugin declarations live in the repo-owned tool configs:

- Claude: `.claude/settings.json`
- Codex: `.codex/config.toml`
- Copilot: `.copilot/settings.json`

`link` and `install` link those desired configs into the home-directory tool locations. Copilot's installed plugin inventory remains auto-managed in `~/.copilot/config.json`.

## Adding a New AI Tool

Add entries to [`scripts/ai-agent-links.json`](scripts/ai-agent-links.json) for simple link targets, then re-run `setup.sh link-ai-agents`. Tool-specific migrations such as Copilot agent filename rewriting live in the setup scripts rather than the manifest.

## Acknowledgements

Some agent/skill designs and conventions in this repo were informed by:

- [BumpyClock/dotfiles](https://github.com/BumpyClock/dotfiles) — Agent and prompt structure
- [butter-zone/design-standards](https://github.com/butter-zone/design-standards) — Design standards and conventions
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — Community subagent catalog
