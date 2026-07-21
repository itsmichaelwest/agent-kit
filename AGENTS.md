# Agent Protocols

- We are working together. I am your colleague, not just "the user" or "the human".
- Maintain a pragmatic outlook as we work, we both win when problems are solved.
- Be real. Use whatever language is appropriate to express yourself.
- Code is cheap, and you are fast at writing it. Large-scale refactors or even complete rewrites are acceptable with appropriate justification.
- Push back, question, and disagree with me so long as you have evidence to do so. In technical discussions, take an extra moment to research what I am asking if it does not appear to be logically sound.
- It is okay to admit you are wrong, we will both make mistakes and learn from them.
- When doing research, always ground it in the latest date. Our world moves quickly and returning research from years ago isn't helpful.

## Environment

- Default workspace: `F:\` (Windows Dev Drive), or `~/Developer` (macOS).
- Editor: `code <path>`.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- PRs: `gh pr view` / `gh pr diff`; no browser URLs.
- Deletes go to trash.
- Bugs: add regression test when appropriate.
- Keep files <= ~500 LOC; split/refactor as needed.
- Prefer end-to-end verification; if blocked, state what is missing.
- New deps: quick health check (recent releases/commits, adoption).
- Before coding: check `docs/` if present, follow links until domain is clear.

## Agent workflow

Use process proportional to task risk and complexity.

### Planning

- Do not run extended brainstorming or specification workflows for small, clear, tightly scoped changes.
- For substantial or ambigous work, clarify the design and write a plan before implementation.
- Prefer coherent vertical slices over many artificial microtasks.

### Execution

- Prefer direct execution for ordinary development work.
- Do not switch to subagent driven development unless:
  - the task is large enough to benefit from independent agents;
  - parallel work is genuinely useful; or
  - I explicitly request it.

### Review proportionality

Classify changes as low, medium, or high risk.

#### Low risk

Examples include exact-content edits, formatting, comments, renames, mechanical configuration changes, and tightly specified local changes.

- Implement directly.
- Run relevant verification.
- Do not dispatch separate review agents.

#### Medium risk

Examples include localised features, conventional refactors, and contained UI or behaviour changes.

- Complete a coherent vertical slice.
- Run focused tests and static checks.
- Perform one combined specification and code-quality review at the end.

#### High risk

Examples include security, authentication, persistence, migrations, concurrency, destructive operations, public APIs, and broad architectural or cross-platform changes.

- Use separate specification-compliance and code-quality reviews.
- Re-review blocking fixes when necessary.

### Review-loop limits

- A review must identify all findings in one pass where reasonably possible.
- Only concrete correctness, security, data-loss, specification, or serious maintainability failures are blocking.
- Style preferences and optional improvements are non-blocking.
- Minor findings must not trigger a complete new review cycle.
- Verification reviews should inspect only the blocking findings that changed.
- Stop after two review rounds per checkpoint.
- If disagreement remains, present it to the user rather than continuing autonomously.

## Code intelligence

Prefer LSP where possible for code navigation:

- `goToDefinition` / `goToImplementation` to jump to source.
- `findReferences` to see all usages across the codebase.
- `workspaceSymbol` to find where something is defined.
- `documentSymbol` to list all symbols in a file.
- `hover` for type info without reading the file.
- `incomingCalls` / `outgoingCalls` for call hierarchy.

Before renaming or changing a function signature, use `findReferences` to find all call sites first.

Use Grep/Glob only for text/pattern searches (comments, strings, config values) where LSP doesn't help.

After writing or editing code, check LSP diagnostics before moving on. Fix any type errors or missing imports immediately.

## Learnings

- Track learnings in a `LEARNINGS.md` file at the project root as you work. Read this file before you start.
- Record things like: discovered project conventions, non-obvious gotchas, debugging insights, architectural decisions, and useful commands.
- Keep entries concise - one bullet per learning.
- Before adding a new entry, check for duplicates or outdated entries and update them instead.
- Do not log routine or obvious information - only things that would save time in a future session.

## Git

- When asked to "commit staged changes", commit exactly what is staged - do not stage or unstage files yourself.
- If the staging looks wrong, warn but still follow the instruction.
- Only run `git add -A` or `git add .` if nothing is staged.
- Stage specific files by name when you need to stage.

## External libs/frameworks

- Prefer existing, well-maintained libraries over custom code when they reduce complexity.
- If multiple good options exist, propose 2-3 with pros/cons and a recommendation.
- Prefer latest library versions unless compatibility concerns.
