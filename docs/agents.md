# Agents

Agent definitions are authored once in `agent-templates/` and compiled into the
provider-specific files used by the rest of the repo. Agents are isolated runtime
roles; reusable domain knowledge and operational methods belong in skills.

## Source of truth

- Editable source: `agent-templates/*.md`
- Generated Claude/Copilot output: `agents/*.md`
- Generated Codex output: `.codex/agents/*.toml`

Do not hand-edit generated files unless you are debugging the compiler. The next `compile-agents` run will overwrite them.

## Compile flow

The compiler lives at [scripts/lib/compile-agents.py](/Users/michael/agent-kit/scripts/lib/compile-agents.py).

It does three things:

1. Reads every template in `agent-templates/`
2. Resolves provider model ids from `agent-templates/config.toml`
3. Writes:
   - `agents/<name>.md`
   - `.codex/agents/<name>.toml`

The setup command also injects the generated Codex agent registrations and
portable settings into the marked block in `~/.codex/config.toml`. That config
file is a real machine-local file, not a symlink. Use `capture-codex-config` to
explicitly import portable live edits back into `config/codex/global.toml`.

It also removes generated agent files whose template no longer exists.
It removes repo-local `agents/*.agent.md` aliases as stale compatibility files;
Copilot aliases are generated only under `~/.copilot/agents` during linking.

### Commands

```bash
./scripts/setup.sh compile-agents
```

```powershell
.\scripts\setup.ps1 compile-agents
```

`link`, `link-ai-agents`, and `install` run agent compilation automatically before linking.

## Template format

Each template is a Markdown file with frontmatter followed by the shared instruction body.

Example:

```md
---
name: "developer"
description: "Use this agent for medium-to-large coding tasks - implement features, fix bugs, or refactor with Test-Driven Development."
model_class: "strong"
claude:
  color: "orange"
codex:
  description: "Medium-to-large coding tasks - implement features, fix bugs, or refactor with Test-Driven Development."
  model_reasoning_effort: "high"
---

# Role

You are a world-class software developer...
```

### Required fields

- `name`
- `description`
- `model_class`

### Supported `model_class` values

- `fast`
- `balanced`
- `strong`

These abstract classes are resolved per provider using `agent-templates/config.toml`.

## Current roster

The transitional roster contains eight agents:

| Agent | Responsibility |
| --- | --- |
| `developer` | Medium-to-large local implementation |
| `developer-lite` | Small bounded implementation; inherits `developer` |
| `investigator` | Read-only location, flow tracing, and diagnosis |
| `planner` | Read-only architecture and implementation planning |
| `reviewer` | Read-only spec, quality, and integration review |
| `researcher` | Current external research and dependency evaluation |
| `security-auditor` | Read-only security audit pending specialist-skill review |
| `performance-engineer` | Read-only performance analysis pending specialist-skill review |

The main session owns user communication, scope, decomposition, integration, and
final evidence. A specialist agent should exist only when it provides a useful
context, permission, model, or independently delegable output boundary.

## Model mapping

Current mappings are:

### Claude

- `fast` -> `haiku`
- `balanced` -> `sonnet`
- `strong` -> `opus`

### Codex

- `fast` -> `gpt-5.6-luna`
- `balanced` -> `gpt-5.6-terra`
- `strong` -> `gpt-5.6-sol`

If you want to change model policy globally, update `agent-templates/config.toml` and re-run `compile-agents`.

## Provider-specific fields

### `claude`

The compiler currently passes through all keys in the `claude` block into the generated Markdown frontmatter.

Current usage in this repo:

- `color`

The compiler validates these supported Claude subagent fields:

- `background`
- `color`
- `disallowedTools`
- `effort`
- `initialPrompt`
- `isolation`
- `maxTurns`
- `mcpServers` (named server references only)
- `memory`
- `permissionMode`
- `skills`
- `tools`

### `codex`

Supported optional keys:

- `description`
- `model_reasoning_effort`
- `web_search`
- `personality`
- `sandbox_mode`

`description` defaults to the top-level template description if omitted.

Supported Codex reasoning efforts are `low`, `medium`, `high`, and `xhigh`.
Supported sandbox modes are `read-only`, `workspace-write`, and
`danger-full-access`.

The compiler rejects unknown template or provider fields. Provider controls are
not assumed to have parity: add a field only to the provider block that supports
it.

## Template inheritance

Use `extends` when agents differ only in model or provider metadata. The child
inherits its parent's instruction body and recursively merges provider blocks.
Child values take precedence.

```md
---
name: "developer-lite"
description: "Implement small, bounded local code changes."
model_class: "balanced"
extends: "developer"
claude:
  color: "yellow"
codex:
  model_reasoning_effort: "high"
---
```

An empty child body inherits the parent body. A non-empty child body replaces it.
The compiler rejects missing parents, inheritance cycles, duplicate names, names
that do not match filenames, missing instruction bodies, and unsupported fields.

## How to add a new agent

1. Create `agent-templates/<agent-name>.md`
2. Add frontmatter:
   - `name`
   - `description`
   - `model_class`
   - optional `extends`
   - optional `claude` block
   - optional `codex` block
3. Write the shared instruction body below the frontmatter
4. Run:

```bash
./scripts/setup.sh compile-agents
```

5. Verify the generated outputs:
   - `agents/<agent-name>.md`
   - `.codex/agents/<agent-name>.toml`
6. Re-link if needed:

```bash
./scripts/setup.sh link-ai-agents
```

Because `compile-agents`, `link`, and `link-ai-agents` update the managed Codex
block automatically, step 6 is usually enough on a machine that already has the
repo linked.

## How to modify an existing agent

1. Edit `agent-templates/<agent-name>.md`
2. Re-run `compile-agents`
3. Review the generated diffs in:
   - `agents/`
   - `.codex/agents/`

## Copilot note

The compiler generates `agents/*.md`. Copilot-compatible `*.agent.md` files are still created as symlinks during the linking step under `~/.copilot/agents/`.

Those symlinked filenames are a runtime compatibility detail, not the source of truth. Keeping `agents/*.agent.md` in the repo creates duplicate custom-agent discoveries in VS Code/Copilot when the same agents are also linked globally.
