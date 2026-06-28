# Tool Surfaces

This repo supports several coding-agent surfaces that look similar but do not
share the same discovery rules. Keep each surface explicit; do not mirror files
or marketplaces across tools unless that overlap is intentional.

## Agent Files

| Surface | User scope | Workspace scope | Repo source |
|--------|------------|-----------------|-------------|
| Claude Code | `~/.claude/agents/*.md` | `.claude/agents/*.md` | `agents/*.md` |
| Codex app / CLI | `~/.codex/agents/*.toml` | `.codex/agents/*.toml` | `.codex/agents/*.toml` |
| Copilot CLI / VS Code Copilot | `~/.copilot/agents/*.agent.md` | `.github/agents/*.agent.md` | `agents/*.md` linked as `*.agent.md` only under `~/.copilot/agents` |

`agent-templates/*.md` is the only editable agent source. The compiler writes
`agents/*.md` for Claude-style Markdown agents and `.codex/agents/*.toml` for
Codex. Repo-local `agents/*.agent.md` files are intentionally removed because
they make VS Code/Copilot see duplicate custom agents when the same personas
also exist in `~/.copilot/agents`.

Use `project-agents` only when a project really needs project-scoped agents.
It currently links Claude project agents; do not also add `.github/agents` for
the same project unless you want those agents to appear as workspace-scoped
Copilot agents in addition to the user-scoped `~/.copilot/agents` copies.

## Plugin Markets

| Surface | Desired state | Runtime inventory |
|--------|---------------|-------------------|
| Claude Code | `.claude/settings.json` `enabledPlugins` / `extraKnownMarketplaces` | Claude plugin cache |
| Codex app / CLI | `.codex/config.toml` `[plugins.*]` / `[marketplaces.*]` | Codex plugin manager |
| Copilot CLI | `.copilot/settings.json` `enabledPlugins` / `extraKnownMarketplaces` | `~/.copilot/config.json` `installedPlugins` |

Marketplace names can overlap technically, but this repo does not treat that as
sync. Claude marketplaces stay in Claude config, Codex marketplaces stay in
Codex config, and Copilot marketplaces stay in Copilot config. Cross-tool
marketplace overlap belongs in that tool's shared config only when it is a
deliberate repo policy, or in the matching `.local` overlay for one machine.
`superpowers@superpowers-marketplace` is deliberate Copilot state, sourced from
`obra/superpowers-marketplace`.

## Current References

- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Codex subagents: https://developers.openai.com/codex/subagents
- GitHub Copilot CLI plugins: https://docs.github.com/copilot/concepts/agents/copilot-cli/about-cli-plugins
- GitHub Copilot CLI custom agents: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- Copilot CLI plugin marketplaces: https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace
- VS Code custom agents: https://code.visualstudio.com/docs/agent-customization/custom-agents
