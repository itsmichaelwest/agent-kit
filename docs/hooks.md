# Global hooks

Global hooks are limited to deterministic safety policy. Formatting, tests,
generated-file checks, UI review, and completion checks belong in the project
that owns those contracts.

## Shared safety hook

`hooks/agent_safety.py` is linked to `~/.agents/hooks/agent_safety.py` and used
by both Claude Code and Codex.

It runs synchronously for shell `PreToolUse` and `PostToolUse` events:

- Before execution, it denies high-confidence destructive operations such as a
  broad forced recursive deletion, `git reset --hard`, forced recursive
  `git clean`, force-push without lease, forced branch deletion, filesystem
  formatting, or a raw disk write.
- Before execution, it denies commands that print a sensitive environment
  variable, dump the full environment, contain a likely literal credential, or
  read a likely credential file into tool output.
- After execution, it detects common live-token formats, private-key blocks,
  and explicit credential assignments. Claude receives a shape-preserving
  redacted result. Codex withholds the result because its current hook surface
  cannot replace arbitrary tool output.
- Normal operations produce no hook output.

This is defense in depth, not a security boundary. It does not cover hosted
tools that bypass local tool hooks, arbitrary assistant prose, encrypted or
unknown credential formats, or side effects that occur before `PostToolUse`.
Repository secret scanning still belongs in pre-commit and CI.

## Configuration

- Claude reads the hook from `.claude/settings.json`. Claude merges matching
  user, project, plugin, skill, and managed hooks; it does not replace one level
  with another. `PreToolUse` can deny before permission evaluation.
- Codex reads `config/codex/hooks.json`, linked to `~/.codex/hooks.json`.
  Review or trust a changed command hook with `/hooks` before expecting it to
  run. Matching hooks from other active sources are additive.

Run the local checks with:

```bash
python3 -m unittest tests.test_agent_safety_hook
```
