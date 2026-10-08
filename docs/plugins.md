# Plugins

Track desired plugin state in each host's native config. Hosts install their own
packages and maintain runtime inventories. This repo does not vendor plugin
caches or bundled skills, agents, hooks, and MCP definitions unless it owns or
intentionally forks the plugin. Pin Git marketplace sources to a release tag
or commit when reproducibility matters.

## Sources and runtime state

| Surface | Desired state in this repo | Runtime inventory |
| --- | --- | --- |
| Claude Code | [`.claude/settings.json`](../.claude/settings.json): `enabledPlugins`, `extraKnownMarketplaces` | Claude plugin cache |
| Codex app / CLI | [`config/codex/global.toml`](../config/codex/global.toml): `[marketplaces.<name>]`, `[plugins."<id>@<marketplace>"]` | Codex plugin manager |
| Copilot CLI | [`.copilot/settings.json`](../.copilot/settings.json): `enabledPlugins`, `extraKnownMarketplaces` | `~/.copilot/config.json`: installed-plugin inventory and account/session state |

Marketplace declarations remain separate across hosts. Cross-tool overlap must
be intentional in that host's shared config; put machine experiments in its
matching local overlay. Codex/OpenAI marketplaces are the default for Codex,
and Copilot-native marketplaces are the default for Copilot.
`superpowers@superpowers-marketplace`, sourced from `obra/superpowers-marketplace`,
is intentional Copilot policy.

Linking writes `~/.copilot/settings.json` as a real file from the shared config
and optional gitignored `.copilot/settings.local.json` overlay. It backs up an
existing real file; settings are not symlinked and runtime edits are not imported
back into the repo. Put persistent machine overrides in the overlay before
linking again. The shell linker merges nested objects; the PowerShell linker
replaces top-level keys supplied by the overlay, so provide complete nested
values when an overlay must work on both platforms. Copilot's `config.json`
remains host-managed and is not linked.

Codex's `~/.codex/config.toml` is also a real machine-local file, reconciled from
the portable source and generated agent registrations. See [Codex config sync](codex-config-sync.md)
for ownership and capture rules.

## Commands

Run from the repo root:

```bash
./scripts/setup.sh plugin-status
./scripts/setup.sh bootstrap-claude
./scripts/setup.sh bootstrap-codex
```

PowerShell uses `.\scripts\setup.ps1` with the same subcommands. `link` applies
repo-owned config and overlays. `install` links config and runs both bootstrap
commands.

`bootstrap-claude` registers and refreshes declared marketplaces, installs
missing enabled plugins, and updates them. `bootstrap-codex` reads only Codex
desired state and runs `codex plugin marketplace add`,
`codex plugin marketplace upgrade`, and `codex plugin add`. TOML declarations
alone do not install a package in the Codex plugin manager. For declared
app-managed marketplaces such as `openai-bundled` and `openai-primary-runtime`,
the bootstrapper infers local runtime paths.

`plugin-status` compares desired state with each host's runtime state. Copilot
status checks `config.json` inventory against Copilot settings; it does not
import another host's marketplaces. This kit has no Copilot bootstrap command.

## Skills and plugins

Repo skills are vendored and linked separately. Plugin-installed skills stay
plugin-managed. Both can coexist, but avoid installing the same skill through
both paths unless duplicate discovery is intentional.

## Host references

- [Copilot CLI plugins](https://docs.github.com/copilot/concepts/agents/copilot-cli/about-cli-plugins)
- [Copilot CLI plugin marketplaces](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
