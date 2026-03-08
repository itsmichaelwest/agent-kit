---
name: polish-ui
description: Capture screenshots, identify visual issues, fix them, and verify. Works across web, Windows, macOS, and iOS/watchOS.
arguments:
  - name: TARGET
    type: string
    description: Optional target — app name, URL, or "simulator". If omitted, auto-detects from project files.
---

Spawn a **ui-polisher** agent to run the full polish loop on this project.

**Use the ui-polisher skill** for capture scripts. Resolve `SKILL_DIR` by checking which exists: `~/.claude/skills/ui-polisher`, `~/.codex/skills/ui-polisher`, or `~/.copilot/skills/ui-polisher`.

Target: $TARGET

Steps:
1. Detect platform from project files in the current working directory.
2. List available windows/simulators to find the target.
3. Capture a "before" screenshot.
4. Analyze for visual issues (layout, typography, contrast, platform conventions, interaction states).
5. Plan and apply high-confidence fixes only.
6. Rebuild, re-capture "after" screenshot.
7. Compare before/after, verify fixes, flag regressions.
8. Loop up to 3 times if issues remain.

If a reference image was provided in the conversation, compare against it.
