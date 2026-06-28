# Plugins

Plugin state is managed per tool. Plugin payloads are not tracked in this repo.

The source of truth is the tool-native config already stored in this repo.

## Storage model

### Claude Code

- Desired plugin state lives in `.claude/settings.json`
- Repo-managed keys:
  - `enabledPlugins`
  - `extraKnownMarketplaces`

### Codex

- Desired plugin state lives in `.codex/config.toml`
- Repo-managed sections:
  - `[marketplaces.<name>]`
  - `[plugins."<plugin-id>@<marketplace>"]`
- Codex does not mirror Claude Code marketplaces. Any overlap with Claude plugin
  marketplaces must be declared intentionally in Codex config.

### Copilot CLI

- Desired plugin state lives in `.copilot/settings.json`
- That file is linked into `~/.copilot/settings.json`
- Installed plugin inventory is auto-managed in `~/.copilot/config.json`
- Repo-managed keys:
  - `enabledPlugins`
  - `extraKnownMarketplaces`

`config.json` is not linked from this repo because Copilot manages it automatically and uses it for installed plugin inventory and account/session state.

## Commands

```bash
./scripts/setup.sh plugin-status
```

```powershell
.\scripts\setup.ps1 plugin-status
```

`install` and `link` relink the repo-owned tool config files into the home-directory tool locations.
`bootstrap-claude` also registers and refreshes Claude Code marketplaces before installing and updating `enabledPlugins`, because a first-run machine may not have the marketplace checkout yet and an existing machine may have stale plugin caches.
`bootstrap-codex` registers Codex marketplaces from `.codex/config.toml`, refreshes marketplace snapshots, and installs enabled plugins with `codex plugin add`. `install` runs both bootstrap commands after linking config.
The two bootstrap commands read separate desired-state files; `bootstrap-codex` never reads `.claude/settings.json` or imports Claude marketplace declarations.

## What the repo controls

The repo controls:

- which plugins should be enabled
- which extra marketplaces should be known
- which Codex marketplaces should be present in config
- which Codex plugins should be installed by `bootstrap-codex`

The repo does not vendor:

- installed plugin caches
- plugin-bundled skills, agents, hooks, or MCP definitions
- Copilot `installedPlugins` / `installed_plugins` inventory

## Bootstrapping Codex plugins

```bash
./scripts/setup.sh bootstrap-codex
```

```powershell
.\scripts\setup.ps1 bootstrap-codex
```

Codex app and CLI plugin availability is not just TOML state. The bootstrap command uses `codex plugin marketplace add`, `codex plugin marketplace upgrade`, and `codex plugin add` so the plugin manager converges on the repo-owned declarations. For app-managed local marketplaces such as `openai-bundled` and `openai-primary-runtime`, the bootstrapper infers their local runtime paths when those plugins are declared.

By default, committed Codex config should stay on Codex/OpenAI marketplaces. If you want a Codex install to use a third-party or Claude-origin marketplace, add that marketplace and its `[plugins.*]` entries explicitly to `.codex/config.local.toml` for one machine, or to `.codex/config.toml` when the cross-tool overlap is an intentional shared policy.

## Mixing plugins with custom skills

Custom skills remain in the repo and are linked separately from plugin state.

- Plugin-installed skills stay plugin-managed
- Repo skills stay repo-managed
- They can coexist in all three tools

For Copilot specifically, the desired plugin declarations are stored in `settings.json`, while actual installed plugin state is checked against `config.json` during `plugin-status`.
