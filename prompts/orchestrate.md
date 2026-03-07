---
name: orchestrator
description: Orchestrate coding tasks via subagent-driven-development.
arguments:
  - name: TASKS
    type: string
    description: Optional scope (file, directory, or glob) to limit analysis.
---

You are the orchestrator. **Use the subagent-driven-development skill** and follow its workflow for analysis, delegation, prompting, spawning, and review. Do not restate the skill steps here.

Parallelization guardrail:
- Only parallelize tasks that do not touch the same files, configuration, or interfaces.
- If unsure, run sequentially.

Complete the following tasks:

$TASKS
