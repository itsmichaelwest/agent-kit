---
name: review-codebase
description: Full codebase audit using multiple AI engines in parallel. Splits by module, reviews from different perspectives, deduplicates into a prioritized report.
arguments:
  - name: SCOPE
    type: string
    description: Optional path or glob to review (e.g. "src/", "lib/**/*.ts"). If omitted, reviews the entire project.
  - name: ENGINES
    type: string
    description: Optional comma-separated list of engines to use (claude,codex,copilot). If omitted, auto-detects available engines.
---

Spawn a **codebase-reviewer** agent to run a full codebase audit.

**Use the codebase-reviewer skill** for engine dispatch scripts. Resolve `SKILL_DIR` by checking which exists: `~/.claude/skills/codebase-reviewer`, `~/.codex/skills/codebase-reviewer`, or `~/.copilot/skills/codebase-reviewer`.

Scope: $SCOPE
Engines: $ENGINES

Steps:
1. Discover project structure and scope modules to review.
2. Detect available AI engines (claude, codex, copilot).
3. Assign review perspectives per engine (architecture, bugs, security).
4. Dispatch parallel reviews across engines.
5. Aggregate, deduplicate, and validate findings.
6. Output a prioritized report with severity levels and fix suggestions.
