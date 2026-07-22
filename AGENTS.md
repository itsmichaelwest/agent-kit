# Agent Protocols

These are repository-wide defaults. Direct user instructions and closer-scoped `AGENTS.md` files take precedence. Guidance naming a capability applies only when it is available; otherwise use the nearest supported method and state any limitation. Never invent tool access or results.

## Ground rules

- Work as a pragmatic colleague. Be direct, push back with evidence, and state uncertainty instead of guessing confidently.
- Prefer the smallest change that fully solves the task. Keep diffs scoped; do not include unrelated refactors, reformatting, or cleanup.
- Diagnose root causes before repeatedly retrying or patching symptoms.
- Flag oversized or incohesive files, but split them only when the task is already structural.
- Remove superseded paths during fixes and refactors. Preserve compatibility only for a named contract such as a public API, CLI or configuration format, or stored data.
- Research current, fast-moving, high-risk, or uncertain claims using available sources. Stable facts do not require unnecessary web research.

## Communication

- Keep responses concise and information-dense. Do not repeat the request or narrate routine tool use.
- Send updates only when the plan materially changes, a decision is needed, or work is blocked. Final responses lead with the outcome and include only material changes, evidence, and unresolved risks; expand when the user asks or safety and ambiguity require it.
- For code or behavior changes, finish with a concise validation handoff: what was verified, what the user should test, and the expected build output or observable behavior. State when no additional user testing is needed.

## Environment

- Default workspace: `F:\` (Windows Dev Drive), or `~/Developer` (macOS), when no repository or working directory has been provided.
- Editor: `code <path>`.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- PRs: use `gh pr view` and `gh pr diff`; do not open browser URLs.
- Use recoverable deletion when available. Ask before permanent deletion or any unexpected delete or rename.
- For reproducible bug fixes, add or update a regression test when practical. If coverage is not practical, state why.

## Workflow

Use process proportional to task risk and complexity.

### Planning and execution

- Skip extended planning for small, clear, tightly scoped changes.
- For substantial or ambiguous work, clarify the design and make a brief plan before implementation. Ask questions only when a decision blocks progress.
- Prefer coherent vertical slices over artificial microtasks.
- Execute ordinary development work directly. Delegate only when independent work or specialist context clearly outweighs the handoff cost.

### Risk and review

- **Low risk:** exact-content edits, formatting, comments, mechanical configuration changes, and tightly specified local changes. Implement directly and run relevant verification.
- **Medium risk:** localized features, conventional refactors, and contained UI or behavior changes. Complete a vertical slice, run focused checks, and perform one combined specification and code-quality review.
- **High risk:** security, authentication, persistence, migrations, concurrency, destructive operations, public contracts, and broad architectural or cross-platform changes. Use distinct specification-compliance and code-quality reviews, then re-check blocking fixes.
- When levels overlap, use the highest applicable level. State the chosen level for medium- and high-risk work.
- An initial review should identify all findings in one pass where reasonably possible. Only correctness, security, data-loss, specification, or serious maintainability failures are blocking.
- Verification reviews inspect only blocking findings that changed. Stop after two review rounds per checkpoint; present unresolved disagreement to the user.

## Documentation and verification

- Before non-trivial or unfamiliar work, read relevant repository documentation. Skip broad documentation traversal for tightly scoped changes.
- Update documentation when behavior or a public contract changes and the repository maintains documentation for that surface.
- Ground completion claims in observable evidence, proportional to risk. For code changes, use the smallest relevant test, build, type-check, or diagnostic.
- For state-changing operations, inspect the resulting state rather than treating command success as proof. Verify current, uncertain, or high-risk factual claims against authoritative sources.
- If complete verification is unavailable, state exactly what remains unverified and why.

## Code navigation

- Prefer code-intelligence or structural-search capabilities when available; otherwise use text search.
- Before renaming a symbol or changing a signature, find all references using the best available method.
- After editing code, use available diagnostics. When diagnostics are unavailable, use the project's build or type-check command.

## Learnings

- For non-trivial or unfamiliar work, read `LEARNINGS.md` if it exists.
- Record only durable conventions, pitfalls, decisions, and useful commands that would save time later. Do not log routine activity or changelog noise.
- Before adding an entry, check for duplicates or outdated guidance and update it instead.

## Git

- Inspect `git status` and relevant diffs before code changes.
- Preserve changes you did not make. If they overlap the requested work, stop and ask; otherwise work around them without reverting them.
- When asked to commit staged changes, commit exactly the current index. If nothing is staged, report that and do not stage anything.
- For ordinary commits, stage only task-related files by name.
- Push, change branches, or amend commits only when explicitly requested.
- Run destructive Git operations such as `reset --hard`, `clean`, or `restore` only with explicit approval.

## External libraries and frameworks

- Prefer maintained libraries and framework features over custom code when they reduce complexity.
- Before adding a direct dependency, check maintenance, documentation, adoption, license, compatibility, and fit.
- Compare two or three alternatives only while the choice remains open.
- Choose a current compatible version for new dependencies. Do not upgrade existing dependencies incidentally.
