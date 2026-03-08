---
name: codebase-reviewer
description: Cross-engine codebase review utilities. Dispatch review tasks to Claude, Codex, and Copilot CLI engines with standardized JSON output. Use when asked to "review codebase", "audit code", or "cross-engine review".
---

# Codebase Reviewer

Dispatch review tasks to multiple AI engines (Claude Code, Codex CLI, Copilot CLI) and collect structured results. Scripts live in `scripts/` relative to this skill.

## Scripts

### run-engine.ps1 (Windows)

Dispatches a prompt to an AI engine and returns structured JSON output.

```powershell
pwsh scripts/run-engine.ps1 -Engine claude -Prompt "Review src/ for bugs" -Cwd C:\project
pwsh scripts/run-engine.ps1 -Engine codex -Prompt "Review src/" -Cwd C:\project -Timeout 600
pwsh scripts/run-engine.ps1 -Engine copilot -Prompt "Review src/ for security" -Cwd C:\project
```

### run-engine.sh (macOS/Linux)

```bash
# Claude Code
bash scripts/run-engine.sh --engine claude --prompt "Review src/ for bugs" --cwd /path/to/project

# Codex CLI
bash scripts/run-engine.sh --engine codex --prompt "Review src/ for security issues" --cwd /path/to/project

# Copilot CLI (uses default model)
bash scripts/run-engine.sh --engine copilot --prompt "Review src/ for architecture issues" --cwd /path/to/project

# With timeout (seconds, default 300)
bash scripts/run-engine.sh --engine claude --prompt "Review src/" --cwd /path/to/project --timeout 600
```

Output (both scripts): JSON with `engine`, `status`, `output`, and `error` fields.

## Engine Availability

The scripts auto-detect which engines are installed:

| Engine  | CLI Command | Detection (Windows / macOS+Linux) |
|---------|-------------|-----------------------------------|
| Claude  | `claude`    | `where.exe claude` / `which claude` |
| Codex   | `codex`     | `where.exe codex` / `which codex` |
| Copilot | `copilot`   | `where.exe copilot` / `which copilot` |

If an engine isn't installed, the script returns a JSON error rather than failing.

## Aggregation

The codebase-reviewer agent handles aggregation. Each engine returns its findings as markdown text inside the JSON `output` field. The agent then deduplicates and prioritizes.
