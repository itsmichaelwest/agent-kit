# Linking

Setup links shared sources into each tool's global configuration and compiles
agents before linking. Re-run `link` after pulling repository updates or changing
[scripts/ai-agent-links.json](../scripts/ai-agent-links.json). Conflicting static
targets are backed up before replacement; status and doctor report link drift.

## Commands

```bash
./scripts/setup.sh link                 # all config links
./scripts/setup.sh link-dotfiles        # shell/editor dotfiles
./scripts/setup.sh link-ai-agents       # AI tools only
./scripts/setup.sh status
./scripts/setup.sh doctor
```

On Windows, use `.\scripts\setup.ps1` with the same actions. `install` also
links the selected configuration. These commands write to home configuration;
run them on the machine you intend to configure.

## Global AI links

The manifest owns static sources and targets. This table summarizes discovery
paths; [Agents](agents.md) covers generated agent filenames and project scope.

| Asset | Claude Code | Codex | Copilot |
| --- | --- | --- | --- |
| `AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | `~/.copilot/copilot-instructions.md` |
| `prompts/` | `~/.claude/commands` | `~/.codex/prompts` | `~/.copilot/prompts` |
| `skills/` | `~/.claude/skills` | `~/.agents/skills` | `~/.copilot/skills` |
| `docs/` | `~/.claude/docs` | `~/.codex/docs` | `~/.copilot/docs` |

Claude agents link to `~/.claude/agents`; generated Codex agents link to
`~/.codex/agents`. Copilot receives per-file `*.agent.md` aliases in
`~/.copilot/agents`, not a link to the whole generated directory.
`hooks/` links to `~/.agents/hooks`; `config/codex/hooks.json` links to
`~/.codex/hooks.json`. A missing safety-hook link can block shell execution;
see [Hooks](hooks.md) for recovery.

## Stateful configuration

- Claude settings link from `.claude/settings.json` to `~/.claude/settings.json`.
  `~/.claude.json` contains authentication, trust, project history, and user MCP
  state; keep it machine-local.
- Copilot settings are generated from shared settings and an optional local
  overlay. Its `~/.copilot/config.json` remains host-managed. See
  [Plugins](plugins.md) for layering and inventory.
- Codex's real `~/.codex/config.toml` is reconciled by individual owned keys from
  `config/codex/global.toml` and generated agent registrations. It is not linked.
  Preview, capture, conflict handling, and old-installation migration belong in
  [Codex config sync](codex-config-sync.md).

The linker removes or backs up the legacy `~/.copilot/instructions.md` target in
favor of `copilot-instructions.md`. If Codex config is still a legacy symlink,
remove that link and preserve any machine settings in a real file before sync.

## MCP configuration

Declare shared servers in `mcp/mcp-config.json`; validate against
`mcp/mcp-config.schema.json`.

- On macOS/Linux, `./scripts/setup.sh install-mcp` registers Claude user-scope
  servers through `claude mcp add --scope user`. Windows setup has no MCP install
  action; register servers directly with the Claude CLI. Project servers in
  `.mcp.json` and local project entries in `~/.claude.json` can shadow user-scope
  servers with the same name.
- Copilot links the dedicated file to `~/.copilot/mcp-config.json`.
- VS Code uses a `servers` key rather than the CLI `mcpServers` shape; do not
  copy the CLI file into VS Code without adapting it.

Keep credentials outside tracked configuration. Do not link `~/.claude.json`
or replace Codex's runtime MCP state with the shared declarations.

## Shell and editor configuration

Base links include `.gitconfig`, `.gitignore_global`, Starship, and platform
shell/editor files when those sources exist. Missing optional sources are
skipped. Windows also links PowerShell profiles and detects Windows Terminal
stable/preview settings.

```bash
./scripts/setup.sh shell         # inject zsh configuration
./scripts/setup.sh shell-remove  # remove the injected block
```

Zsh injection replaces the `dotfiles zsh start` / `dotfiles zsh end` marked block
in `~/.zshrc`, backs up the file on first use, and appends platform snippets when
present. It does not require replacing the rest of the user's shell config.

## Platform constraints

On Windows, use PowerShell setup. Git Bash, MSYS2, and Cygwin can turn `ln -s`
into plain copies, so `setup.sh` rejects them. `setup.ps1` creates directory
junctions and file symlinks, attempting `gsudo` and then a copy fallback when
necessary. Doctor reports copies that do not satisfy the link contract.

WSL uses the Linux flow and manages the WSL home separately from Windows.
Doctor checks declared targets and the manifest layout digest. A stale marker
or manifest change requires re-running `link` on that machine; compiler and
sync checks alone do not establish that live links are current.
