# agent-kit

Shared agent instructions, skills, tool configuration, and shell dotfiles for
Windows, macOS, and Linux. Supports Claude Code, Codex, and GitHub Copilot.

## Set up a machine

Clone the repository, then use the entry point for your operating system.
Setup needs Python 3.11+ for compilation and linking; the dependency step can
install it. See [dependencies](docs/dependencies.md) for platform requirements.

```powershell
# Windows
git clone https://github.com/itsmichaelwest/agent-kit.git
cd agent-kit
.\scripts\setup.ps1 install

# Install every component without prompts
.\scripts\setup.ps1 install -All

# Also permit x64 CLI fallbacks on ARM64
.\scripts\setup.ps1 install -All -AllowX64Fallback
```

```bash
# macOS/Linux
git clone https://github.com/itsmichaelwest/agent-kit.git
cd agent-kit
./scripts/setup.sh install

# Install every component without prompts
./scripts/setup.sh install --all
```

To apply repository updates or link existing tools without installing packages:

```bash
./scripts/setup.sh link
./scripts/setup.sh doctor
```

On Windows, use `.\scripts\setup.ps1 link` and
`.\scripts\setup.ps1 doctor`. Use PowerShell rather than Git Bash.

## Maintain the kit

| Task | Reference |
| --- | --- |
| Install tools and toolchains | [Dependencies](docs/dependencies.md) |
| Link configuration and troubleshoot discovery | [Linking](docs/linking.md) |
| Create or modify agents | [Agents](docs/agents.md) |
| Add, update, or remove skills | [Skills](docs/skills-sync.md) |
| Curate skills and review imported guidance | [Skill maintenance](docs/skill-maintenance.md) |
| Preview or capture Codex settings | [Codex config sync](docs/codex-config-sync.md) |
| Declare and install plugins | [Plugins](docs/plugins.md) |
| Configure safety hooks | [Hooks](docs/hooks.md) |
| Change setup scripts and validate the kit | [Maintenance](docs/maintenance.md) |
| Write technical documentation | [Technical writing](docs/technical-writing.md) |

## Repository sources

| Path | Owns |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Shared agent behavior |
| `agent-templates/` | Agent definitions and provider model policy |
| `agents/`, `.codex/agents/` | Generated agent outputs |
| `skills/` | Vendored and local skills |
| `scripts/skills-manifest.json`, `.skill-lock.json` | Skill inventory and upstream provenance |
| `config/codex/global.toml` | Portable Codex setting keys |
| `.claude/settings.json`, `.copilot/settings.json` | Native tool settings and plugin declarations |
| `scripts/ai-agent-links.json` | Static global link targets |
| `prompts/` | Shared commands |
| `docs/` | Operational references |
| `hooks/`, `mcp/`, `shell/` | Safety hooks, MCP configuration, shell configuration |
| `scripts/setup.sh`, `scripts/setup.ps1` | Platform setup entry points |

Runtime credentials, trust, sessions, and plugin caches stay machine-local.

## Acknowledgements

- [BumpyClock/dotfiles](https://github.com/BumpyClock/dotfiles): agent and prompt structure.
- [butter-zone/design-standards](https://github.com/butter-zone/design-standards): design conventions.
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents): community agent catalog.
- [Claude Code LSP guidance](https://karanbansal.in/blog/claude-code-lsp/): code intelligence.
