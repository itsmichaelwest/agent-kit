# Agents

Agents define isolated runtime roles; skills hold reusable knowledge and workflows.
The main session owns scope, user communication, integration, and final evidence.
Delegate when a role supplies a useful context, permission, model, or independent
output boundary.

## Sources and discovery

Edit [`agent-templates/*.md`](../agent-templates/). Resolve `fast`, `balanced`,
and `strong` through [`agent-templates/config.toml`](../agent-templates/config.toml)
instead of copying model IDs into documentation. Do not edit generated outputs.

| Surface | User scope | Workspace scope | Generated source |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/agents/*.md` | `.claude/agents/*.md` | `agents/*.md` |
| Codex app / CLI | `~/.codex/agents/*.toml` | `.codex/agents/*.toml` | `.codex/agents/*.toml` |
| Copilot CLI / VS Code Copilot | `~/.copilot/agents/*.agent.md` | `.github/agents/*.agent.md` | `agents/*.md`, linked with the Copilot suffix |

Copilot filename aliases exist only under `~/.copilot/agents`. Compilation removes
repo-local `agents/*.agent.md` aliases to prevent duplicate discovery.
`project-agents <path>` links Claude project agents. Use it only when project
scope is needed; adding the same roles under `.github/agents` also exposes
workspace-scoped Copilot copies alongside user-scoped copies.

## Template schema

Each Markdown template has frontmatter followed by the instruction body:

```markdown
---
name: "developer"
description: "Implement bounded code changes."
model_class: "strong"
claude:
  color: "orange"
codex:
  model_reasoning_effort: "high"
---

Implement the requested behavior and validate it through the project harness.
```

Required fields are `name`, `description`, and `model_class`. Names match the
filename and contain lowercase words separated by hyphens. Optional top-level
fields are `extends`, `claude`, and `codex`; unknown fields are rejected.

Provider controls do not have assumed parity. Add controls only to the block
that supports them:

| Provider | Supported optional fields |
| --- | --- |
| Claude | `background`, `color`, `disallowedTools`, `effort`, `initialPrompt`, `isolation`, `maxTurns`, `mcpServers`, `memory`, `permissionMode`, `skills`, `tools` |
| Codex | `description`, `model_reasoning_effort`, `web_search`, `personality`, `sandbox_mode` |

Claude tool, skill, and MCP fields are string lists; `mcpServers` accepts named
server references rather than inline definitions. `background` is Boolean and
`maxTurns` is a positive integer. Effort values are `low`, `medium`, `high`,
`xhigh`, and `max`; isolation is `worktree`; memory scope is `user`, `project`,
or `local`. See the [compiler](../scripts/lib/compile-agents.py) for validated
colors and permission modes.

Codex `description` defaults to the template description. Supported reasoning
efforts are `low`, `medium`, `high`, and `xhigh`; sandbox modes are `read-only`,
`workspace-write`, and `danger-full-access`. These are the compiler's supported
values, not a guarantee that every host or model supports the same controls.

## Inheritance

Use `extends` when agents differ only in model or provider metadata:

```markdown
---
name: "developer-lite"
description: "Implement small local changes."
model_class: "balanced"
extends: "developer"
claude:
  color: "yellow"
---
```

Provider blocks merge recursively; child values take precedence. An empty child
body inherits its parent's instructions; a non-empty body replaces them. The
compiler rejects missing parents, inheritance cycles, duplicate names, filename
mismatches, missing resolved instruction bodies, and unsupported fields.

## Compile and link

Create or edit a template, compile, and review the generated diffs in `agents/`
and `.codex/agents/`. Re-link to refresh runtime discovery:

```bash
./scripts/setup.sh compile-agents
./scripts/setup.sh link-ai-agents
```

PowerShell equivalents are `.\scripts\setup.ps1 compile-agents` and
`.\scripts\setup.ps1 link-ai-agents`. `link`, `link-ai-agents`, and `install`
compile before linking. Compilation removes generated files whose template no
longer exists.

Setup also reconciles generated Codex registrations and portable settings in
the real machine-local `~/.codex/config.toml`, preserving local path overrides
and unrelated settings. Use `capture-codex-config` to import portable live edits
into [`config/codex/global.toml`](../config/codex/global.toml); see
[Codex config sync](codex-config-sync.md) for ownership and cleanup rules.

## Host references

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Copilot CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
