# Agent Protocols

- Workspace: `~/Developer` (macOS), `F:\` (Windows Dev Drive).
- Editor: `code <path>`.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- PRs: `gh pr view` / `gh pr diff`; no browser URLs.
- Deletes go to trash.
- Bugs: add regression test when appropriate.
- Keep files <= ~500 LOC; split/refactor as needed.
- Prefer end-to-end verification; if blocked, state what is missing.
- New deps: quick health check (recent releases/commits, adoption).
- Before coding: check `docs/` if present, follow links until domain is clear.

## Git

- When asked to "commit staged changes", commit exactly what is staged - do not stage or unstage files yourself.
- If the staging looks wrong, warn but still follow the instruction.
- Only run `git add -A` or `git add .` if nothing is staged.
- Stage specific files by name when you need to stage.

## External libs/frameworks

- Prefer existing, well-maintained libraries over custom code when they reduce complexity.
- If multiple good options exist, propose 2-3 with pros/cons and a recommendation.
- Prefer latest library versions unless compatibility concerns.
