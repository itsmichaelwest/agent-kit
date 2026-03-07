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
├── skills/                    # Domain-specific skill packs
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

The setup scripts symlink agents, skills, prompts, and docs into the config directories for each supported AI tool (GitHub Copilot CLI, Codex, Claude Code). All links are defined declaratively in [`scripts/ai-agent-links.json`](scripts/ai-agent-links.json).

See [docs/linking.md](docs/linking.md) for the full mapping.

## Agents

Agents are specialized personas with distinct roles, models, and instructions. Each agent is defined twice: as a `.md` file for GitHub Copilot CLI/Claude Code (`agents/`) and a `.toml` file for Codex CLI (`.codex/agents/`).

## Skills

Skills are domain-specific knowledge packs that give agents deeper expertise. Each skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`) and supporting reference files.

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

## Adding a New AI Tool

Add entries to [`scripts/ai-agent-links.json`](scripts/ai-agent-links.json) mapping source directories to the tool's config paths, then re-run `setup.sh link-ai-agents`.

## Acknowledgements

Some agent/skill designs and conventions in this repo were informed by:

- [BumpyClock/dotfiles](https://github.com/BumpyClock/dotfiles) — Agent and prompt structure
- [butter-zone/design-standards](https://github.com/butter-zone/design-standards) — Design standards and conventions
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — Community subagent catalog
