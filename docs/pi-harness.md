# Pi harness

[Pi](https://pi.dev) (`@earendil-works/pi-coding-agent`) is a terminal-based AI coding agent with a TypeScript extension system and 30+ provider support. This document covers how to add Pi as a fourth compilation target to this repo alongside Claude, Codex, and Copilot.

> **Status: proposed.** Nothing described here is implemented yet. This is the implementation plan.

---

## Background

Pi uses `pi-subagents` (npm package) to load custom agent files from:

- `~/.pi/agent/agents/**/*.md` — user-global scope
- `.pi/agents/**/*.md` — project scope

The format is Markdown + YAML frontmatter, identical in structure to Claude's format, but with different field names. The system prompt body below `---` is shared across all harnesses unchanged.

Pi also supports a global config at `~/.pi/agent/settings.json` (packages, model defaults, subagent overrides, UI settings) and loads skills from `~/.pi/agent/skills/`.

---

## Field comparison across harnesses

| Concept | Pi (`pi-subagents`) | Claude Code | Codex CLI |
|---|---|---|---|
| File format | Markdown + YAML | Markdown + YAML | TOML |
| System prompt | Markdown body | Markdown body | `developer_instructions` string |
| User agents path | `~/.pi/agent/agents/` | `~/.claude/agents/` | `~/.codex/agents/` |
| Project agents path | `.pi/agents/` | `.claude/agents/` | `.codex/agents/` |
| `name` | Required | Required | Required |
| `description` | Required | Required | Required |
| Model | `model: provider/id` | `model: alias\|id\|inherit` | `model = "id"` |
| Thinking level | `thinking: off\|low\|medium\|high\|xhigh` | `effort: low\|medium\|high\|max` | `model_reasoning_effort = "low\|medium\|high"` |
| Read-only | `tools: read, grep, find, ls` | `tools: Read, Grep, Glob` | `sandbox_mode = "read-only"` |
| Tool granularity | Fine-grained allowlist | Fine-grained allow + deny | Coarse (3 sandbox modes) |
| UI colour | Not supported | `color: orange` etc. | Not supported |
| Context mode | `defaultContext: fresh\|fork` | No per-agent frontmatter equiv. | No equivalent |
| Project context | `inheritProjectContext: true\|false` | Auto-loaded (always) | No equivalent |
| Skills injection | `skills: name1, name2` | `skills: [name1]` | `[[skills.config]]` |
| Fallback models | `fallbackModels: model-a, model-b` | Not supported | Not supported |
| System prompt mode | `systemPromptMode: replace\|append` | Not supported | Not supported |

Sources: `npmjs.com/package/pi-subagents`, `code.claude.com/docs/en/sub-agents`, `developers.openai.com/codex/subagents`.

---

## Implementation: 8 touch points

### 1. `agent-templates/config.toml`

Add a `[providers.pi]` section:

```toml
[providers.pi]
fast     = "github-copilot/claude-haiku-4.5"
balanced = "github-copilot/claude-sonnet-4.6"
strong   = "github-copilot/claude-opus-4.7"
```

### 2. Agent templates — add `pi:` block

Each of the 19 templates in `agent-templates/` gets a `pi:` block in the frontmatter. The body is untouched. See [per-agent spec](#per-agent-pi-frontmatter) below.

### 3. `scripts/lib/compile-agents.py`

Add a `render_pi()` function and write `.pi/agents/<name>.md` from each template:

```python
def render_pi(template: dict, model: str) -> str:
    pi_cfg = template.get('pi', {})

    lines = [
        f'name: {template["name"]}',
        f'description: "{template["description"]}"',
        f'model: {model}',
    ]

    passthrough = [
        'thinking', 'tools', 'defaultContext', 'inheritProjectContext',
        'inheritSkills', 'systemPromptMode', 'skills', 'output',
        'defaultReads', 'defaultProgress', 'completionGuard',
        'maxTokens', 'maxExecutionTimeMs', 'fallbackModels',
    ]
    for field in passthrough:
        if field in pi_cfg:
            lines.append(f'{field}: {pi_cfg[field]}')

    return f'---\n' + '\n'.join(lines) + f'\n---\n\n{template["body"]}'
```

In the main compile loop, after writing Claude and Codex outputs:

```python
pi_model = resolve_model(template['model_class'], config['providers']['pi'])
pi_output = render_pi(template, pi_model)
write_file(os.path.join(repo_root, '.pi', 'agents', f'{name}.md'), pi_output)
```

Also add `.pi/agents/<name>.md` to the cleanup pass when a template is removed.

### 4. `scripts/ai-agent-links.json`

Add to `sources`:

```json
"pi_agents": ".pi/agents"
```

Add to `targets`:

```json
{ "source": "pi_agents",    "path": "~/.pi/agent/agents"   },
{ "source": "skills",       "path": "~/.pi/agent/skills"   },
{ "source": "instructions", "path": "~/.pi/agent/AGENTS.md" }
```

No prompts target — Pi slash commands are registered via TypeScript extensions, not file-based.

### 5. `scripts/lib/link-ai-agents.sh` and `.ps1`

Add two new functions and call them from `link_ai_agents()`:

```bash
link_pi_agents() {
    # Pi uses the same .md format as Claude.
    # Symlink the whole directory (no per-file rename needed, unlike Copilot).
    ensure_linked "$REPO_ROOT/.pi/agents" "$HOME/.pi/agent/agents"
}

link_pi_settings() {
    python3 "$SCRIPTS_DIR/lib/merge-pi-settings.py" \
        --shared  "$REPO_ROOT/.pi/settings.json" \
        --overlay "$REPO_ROOT/.pi/settings.local.json" \
        --target  "$HOME/.pi/agent/settings.json"
}
```

Insert both calls in `link_ai_agents()` after `link_codex_config`.

### 6. New file: `agent-kit/.pi/settings.json`

Shared Pi config tracked in this repo. Not symlinked — merged on each `link-ai-agents` run to preserve runtime-mutable fields (`lastChangelogVersion`). See [Pi settings](#pi-settings) below.

### 7. New file: `scripts/lib/merge-pi-settings.py`

Mirrors `merge-codex-config.py`. Merges shared config + optional local overlay onto the existing `~/.pi/agent/settings.json`, preserving runtime-only keys:

```python
PRESERVE_KEYS = {'lastChangelogVersion'}

def merge(existing: dict, shared: dict, overlay: dict | None) -> dict:
    result = {**shared}
    if overlay:
        result = deep_merge(result, overlay)
    for key in PRESERVE_KEYS:
        if key in existing:
            result[key] = existing[key]
    return result
```

### 8. New file: `.pi/settings.local.example.json`

```json
{
  "_comment": "Copy to .pi/settings.local.json (gitignored). Overrides shared settings.",
  "defaultProvider": "anthropic",
  "defaultModel": "claude-opus-4-7"
}
```

---

## Per-agent Pi frontmatter

These are the `pi:` block values for each of the 19 templates. `model` is resolved from `model_class` at compile time.

| Agent | `model_class` | `tools` | `thinking` | `defaultContext` | `inheritProjectContext` | Notes |
|---|---|---|---|---|---|---|
| `architect` | strong | `read, grep, find, ls, bash` | `high` | `fresh` | `true` | No write |
| `code-flow-analyzer` | strong | `read, grep, find, ls` | `high` | `fresh` | `true` | Pure read |
| `codebase-investigator` | fast | `read, grep, find, ls` | `low` | `fresh` | `true` | Pure read |
| `codebase-reviewer` | strong | `read, grep, find, ls, bash` | `high` | `fresh` | `true` | Bash for build/test |
| `debugger` | strong | `read, grep, find, ls, bash, edit, write` | `high` | `fork` | `true` | |
| `developer` | strong | `read, grep, find, ls, bash, edit, write, contact_supervisor` | `high` | `fork` | `true` | `contact_supervisor` for pi-intercom |
| `developer-lite` | balanced | `read, grep, find, ls, bash, edit, write` | `medium` | `fork` | `true` | |
| `developer-mini` | balanced | `read, grep, find, ls, bash, edit, write` | `medium` | `fork` | `true` | |
| `explore` | fast | `read, grep, find, ls` | `off` | `fresh` | `true` | |
| `git-workflow` | balanced | `read, grep, find, ls, bash, edit, write` | `low` | `fork` | `true` | |
| `performance-engineer` | balanced | `read, grep, find, ls, bash` | `medium` | `fresh` | `true` | |
| `planner` | strong | `read, grep, find, ls, bash` | `high` | `fresh` | `true` | Also add `output: plan.md` |
| `researcher` | balanced | `read, grep, find, ls, bash, web_search, fetch_content` | `medium` | `fresh` | `false` | No project context |
| `reviewer` | balanced | `read, grep, find, ls, bash` | `medium` | `fresh` | `true` | |
| `security-auditor` | balanced | `read, grep, find, ls, bash` | `medium` | `fresh` | `true` | |
| `technical-writer` | balanced | `read, grep, find, ls, bash, edit, write` | `low` | `fork` | `true` | |
| `ui-polisher` | strong | `read, grep, find, ls, bash, edit, write` | `high` | `fork` | `true` | |
| `ux-designer` | strong | `read, grep, find, ls` | `high` | `fresh` | `false` | Design advice; no project context |

`defaultContext: fork` means the child Pi session starts from the parent's current conversation branch. `fresh` means an isolated clean context. For analysis and planning agents, `fresh` keeps them narrow; for implementation agents, `fork` lets them see what the parent established.

`researcher` and `ux-designer` set `inheritProjectContext: false` intentionally — researcher benefits from a clean slate for unbiased web research; ux-designer is consulted for design opinions that should not be anchored to project-specific instructions.

Example compiled output for `developer`:

```yaml
---
name: developer
description: "Use this agent for medium-to-large coding tasks..."
model: github-copilot/claude-opus-4.7
thinking: high
tools: read, grep, find, ls, bash, edit, write, contact_supervisor
defaultContext: fork
inheritProjectContext: true
---

# Role

You are a world-class software developer...
```

---

## Pi settings

`agent-kit/.pi/settings.json` is the shared tracked config. It is merged (not symlinked) into `~/.pi/agent/settings.json` during setup.

Key sections:

**Packages** — all Pi extensions installed on first launch:

```json
"packages": [
  "npm:pi-subagents",
  "npm:pi-mcp-adapter",
  "npm:pi-web-access",
  "npm:pi-lens",
  "npm:@juicesharp/rpiv-btw",
  "npm:@juicesharp/rpiv-advisor",
  "npm:@juicesharp/rpiv-ask-user-question",
  "npm:@bumpyclock/pi-statusbar",
  "npm:@bumpyclock/pi-tasque",
  "npm:@narumitw/pi-goal",
  "npm:pi-intercom",
  "npm:@ifi/oh-pi-themes"
]
```

**`subagents.agentOverrides`** — intentionally empty. Per-agent model and thinking level come from the compiled agent files; override only when you need a temporary per-machine deviation.

**`extensionSettings.personalitySwitcher`** — matches the existing AGENTS.md communication style:

```json
"extensionSettings": {
  "personalitySwitcher": {
    "personality": "caveman",
    "styles": ["explanatory"]
  }
}
```

---

## What is shared across all harnesses

| Asset | Pi path | Claude path | Codex path | Copilot path |
|---|---|---|---|---|
| Agent system prompts | `~/.pi/agent/agents/` | `~/.claude/agents/` | `~/.codex/agents/` | `~/.copilot/agents/` |
| Skills | `~/.pi/agent/skills/` | `~/.claude/skills/` | — | `~/.copilot/skills/` |
| Global instructions | `~/.pi/agent/AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | `~/.copilot/copilot-instructions.md` |

All four point at the same source files in this repo. One edit propagates everywhere on the next `link-ai-agents` run.

---

## How to add a new agent with Pi support

1. Create `agent-templates/<name>.md`
2. Add frontmatter:
   - Required: `name`, `description`, `model_class`
   - Add `claude:` block (at minimum `color`)
   - Add `codex:` block (`sandbox_mode`, `model_reasoning_effort`)
   - Add `pi:` block (`tools`, `thinking`, `defaultContext`, `inheritProjectContext`)
3. Write the shared instruction body
4. Run:

```bash
./scripts/setup.sh compile-agents
```

5. Verify generated outputs:
   - `agents/<name>.md`
   - `.codex/agents/<name>.toml`
   - `.pi/agents/<name>.md`

---

## Known open questions

- **`model_profile` field** — appears in the colleague's Pi templates (`pi.model_profile: economy`) but is not documented in `pi-subagents`. Either an undocumented feature or a local convention. Omit until clarified.
- **Copilot agent format** — Copilot uses the same compiled Claude `.md` files (renamed to `.agent.md` during linking). Pi uses its own compiled output. The two are separate even though the format looks similar.
- **Pi extensions** — `personality-switcher` and `pi-cloak` extensions from the colleague's dotfiles are not part of this repo. They live in `~/.pi/agent/extensions/` and are managed separately. The `settings.json` packages list handles Pi's equivalent functionality via npm packages.
