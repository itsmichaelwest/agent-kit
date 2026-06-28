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
├── agent-templates/           # Canonical agent source templates
├── agents/                    # Generated Claude/Copilot agent definitions (.md)
├── .claude/                   # Claude Code settings
├── .codex/
│   ├── config.toml            # Codex config + agent registry
│   └── agents/                # Generated Codex agent definitions (.toml)
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
See [docs/agents.md](docs/agents.md) for the agent template and compilation workflow.
See [docs/plugins.md](docs/plugins.md) for the plugin model and config surfaces.

For existing machines, the supported upgrade path is to pull the latest repo and re-run `./scripts/setup.sh link` or `.\scripts\setup.ps1 link`. The scripts migrate legacy targets in place, back up conflicting non-symlink files or directories, and relink the current global layout.

## Agents

Agents are specialized personas with distinct roles, models, and instructions. The editable source of truth lives in `agent-templates/`. Those templates compile into:

- `agents/*.md` for Claude Code and Copilot
- `.codex/agents/*.toml` for Codex

During setup, Copilot-compatible global agent links are created with the required `*.agent.md` filenames under `~/.copilot/agents/`.

### Managing agents

```bash
# Rebuild generated agent outputs from templates
./scripts/setup.sh compile-agents
```

```powershell
.\scripts\setup.ps1 compile-agents
```

See [docs/agents.md](docs/agents.md) for the template schema, model mapping, and how to add a new agent.

## Skills

Skills are domain-specific knowledge packs that give agents deeper expertise. Each skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`) and supporting reference files. The repo `skills/` directory is the canonical global source: it is symlinked into `~/.agents/skills` (the universal location read by GitHub Copilot CLI and Codex) and `~/.claude/skills` for Claude Code.

Skills are managed via [`vercel-labs/skills`](https://github.com/vercel-labs/skills) (`npx skills`). The repo's [`scripts/skills-manifest.json`](scripts/skills-manifest.json) declares the desired set of upstream skills; the lockfile committed at [`.skill-lock.json`](.skill-lock.json) is the symlinked source of truth that `npx skills` reads at `~/.agents/.skill-lock.json`.

See [docs/skills-sync.md](docs/skills-sync.md) for the sync strategy — why skills are vendored rather than restored from a lockfile, how upstream updates work, and when to revisit this as `npx skills` matures.

### Managing skills

```bash
# Install/update all skills declared in the manifest
./scripts/setup.sh update-skills

# Add a new upstream skill source, then reconcile and doctor
./scripts/setup.sh install-skill shadcn/improve
.\scripts\setup.ps1 install-skill vercel-labs/agent-skills -s react-best-practices

# Remove one upstream skill, update the manifest, then doctor
./scripts/setup.sh uninstall-skill improve

# Show currently installed skills (delegates to `npx skills list -g`)
./scripts/setup.sh list-skills

# Reconcile skills installed directly with `npx skills add -g`
./scripts/setup.sh reconcile-skills

# Check manifest/lockfile/disk consistency (add --strict to fail on warnings)
./scripts/setup.sh doctor

# Pull latest versions of already-installed skills (no manifest read)
npx skills update -g -y
```

### Adding a skill

Add an entry to `scripts/skills-manifest.json`. Either group with an existing `repo` source or add a new one:

```jsonc
{
  "repo": "owner/repo",
  "skills": ["specific-skill-name"]   // omit "skills" to install all skills from the repo
}
```

Then run `./scripts/setup.sh update-skills`, or use `./scripts/setup.sh install-skill owner/repo -s skill-name` to install one source and update the lockfile/manifest in one pass. Skill names follow the upstream package's canonical naming (the CLI may apply a vendor prefix on collision — e.g. `react-best-practices` from `vercel-labs/agent-skills` lands as `vercel-react-best-practices`).

If you installed a skill directly with `npx skills add -g`, run `./scripts/setup.sh reconcile-skills` (or `.\scripts\setup.ps1 reconcile-skills` on Windows) before `doctor`. It recovers matching lockfile entries from the repo/global lockfiles and backed-up `~/.agents/.skill-lock.json.backup.*` files, then adds on-disk upstream skills to the manifest for review in git.

To remove an upstream skill, use `./scripts/setup.sh uninstall-skill installed-skill-name` (or `.\scripts\setup.ps1 uninstall-skill installed-skill-name`). The command refuses local skills and manifest entries that install every skill from a source, because those cases need an explicit manual inventory decision.

### Local skills

To author a local skill, drop a folder into `skills/` with a `SKILL.md` containing YAML frontmatter, then list its folder name under `"local"` in [`scripts/skills-manifest.json`](scripts/skills-manifest.json). Local skills are not tracked in the lockfile and coexist alongside `npx skills`-managed ones; the `local` list tells `setup.sh doctor` they're intentional (otherwise it flags them as undeclared).

### Private skills

For skills that should stay on one machine and never be committed or synced (anything whose name is private), git-ignore the folder — add it to `.git/info/exclude` (per-clone, never pushed). `setup.sh doctor` detects ignored skills via `git check-ignore` and skips them, so their names never appear in any tracked file. Don't install them with `npx skills add -g` (that writes the shared lockfile); the doctor warns if a git-ignored skill leaks into the lockfile. See [docs/skills-sync.md](docs/skills-sync.md#private-skills-machine-local-not-synced).

## Plugins

Plugins are declared per tool and installed automatically on first launch where the tool supports it.

```bash
./scripts/setup.sh plugin-status
```

| Tool | Declared in | Auto-installs on launch? |
|------|------------|---------------------------|
| Copilot | `.copilot/settings.json` `enabledPlugins` | Yes — documented as "Declarative plugin auto-install" |
| Codex | `.codex/config.toml` `[plugins."x@y"]` | Yes — background curated-marketplace sync at startup |
| Claude | `.claude/settings.json` `enabledPlugins` | No — requires `./scripts/setup.sh bootstrap-claude` to install (run once per machine) |

### Per-tool layering

**Copilot** — `~/.copilot/settings.json` is **generated** at link time by jq-merging the committed `.copilot/settings.json` (shared) with an optional `.copilot/settings.local.json` (gitignored, per-machine: `model`, `trustedFolders`). Copy `.copilot/settings.local.example.json` to bootstrap your local file. Runtime state (installed plugin cache paths, login info, first-launch timestamp) stays in `~/.copilot/config.json`, which Copilot CLI manages itself and is never touched by setup.

**Codex** — `~/.codex/config.toml` is **generated** at link time from three sources: the committed `.codex/config.toml` (shared declarative — model, agents, plugins, MCP), an optional `.codex/config.local.toml` (gitignored — pre-declared trust, per-machine overrides), and any `[projects.*]` trust entries Codex has written into the live file during runtime. Copy `.codex/config.local.example.toml` to start your local file. Re-running `setup.sh link` preserves runtime trust; it does not preserve other ad-hoc edits Codex makes to its config.

**Claude** — `~/.claude/settings.json` is a plain symlink to the committed `.claude/settings.json`. Claude stores runtime state (OAuth, MCP user-scope configs, per-project trust) in a separate `~/.claude.json` file, so the symlinked settings file stays clean. Use `.claude/settings.local.json` (gitignored, project-scope per Claude convention) for any per-machine overrides.

### Bootstrapping Claude plugins on a new machine

```bash
./scripts/setup.sh bootstrap-claude
```

Reads `enabledPlugins` from `~/.claude/settings.json` and runs `claude plugin install` for each entry. Idempotent — already-installed plugins are skipped. `setup.sh install` runs this automatically.

## Adding a New AI Tool

Add entries to [`scripts/ai-agent-links.json`](scripts/ai-agent-links.json) for simple link targets, then re-run `setup.sh link-ai-agents`. Tool-specific migrations such as Copilot agent filename rewriting live in the setup scripts rather than the manifest.

## Acknowledgements

Some agent/skill designs and conventions in this repo were informed by:

- [BumpyClock/dotfiles](https://github.com/BumpyClock/dotfiles) — Agent and prompt structure
- [butter-zone/design-standards](https://github.com/butter-zone/design-standards) — Design standards and conventions
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — Community subagent catalog
