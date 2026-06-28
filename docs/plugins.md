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

## What the repo controls

The repo controls:

- which plugins should be enabled
- which extra marketplaces should be known
- which Codex marketplaces should be present in config

The repo does not vendor:

- installed plugin caches
- plugin-bundled skills, agents, hooks, or MCP definitions
- Copilot `installedPlugins` / `installed_plugins` inventory

## Mixing plugins with custom skills

Custom skills remain in the repo and are linked separately from plugin state.

- Plugin-installed skills stay plugin-managed
- Repo skills stay repo-managed
- They can coexist in all three tools

For Copilot specifically, the desired plugin declarations are stored in `settings.json`, while actual installed plugin state is checked against `config.json` during `plugin-status`.
