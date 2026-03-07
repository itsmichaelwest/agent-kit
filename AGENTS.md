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

## External libs/frameworks

- Prefer existing, well-maintained libraries over custom code when they reduce complexity.
- If multiple good options exist, propose 2-3 with pros/cons and a recommendation.
- Prefer latest library versions unless compatibility concerns.
