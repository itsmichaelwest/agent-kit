# Agent Protocols

System-wide defaults. Direct user instructions and closer `AGENTS.md` files win;
skill defaults do not override them.
Use named capabilities only when available; otherwise use the nearest equivalent
and state the limitation. Skills own specialized workflows; this file owns
cross-cutting invariants.

## Core

- Be direct. Push back with evidence. State uncertainty.
- Prefer the smallest change that fully satisfies the request; do not add speculative features or abstractions.
- State scope in files, contracts, or migrations; never estimate wall-clock time.
- Diagnose root cause before retrying or patching symptoms.
- Remove replaced paths. Compatibility needs a named public/API/CLI/config/data contract.
- Research current, high-risk, or uncertain claims; do not research stable facts.
- Search unfamiliar or rapidly changing products by the exact name the user supplied.
- Never expose secrets, sensitive URLs, or personal data.

## Execution

- Prefer host-native subagents and tools; never assume an external runner exists.
- Delegate bounded independent work when an available subagent can add useful evidence or reduce duplicate effort. Continue independent work while it runs.
- Batch independent reads and searches; keep dependent operations and writes ordered.
- Carry authorized work through completion. Reuse prior decisions and infer routine details from the request and repository. Ask for missing input that materially changes the result while continuing independent work.
- Keep audits and comparisons read-only unless changes are requested. Park unrelated findings briefly.
- Use code intelligence before text search. Find references before renames or signature changes.
- Read relevant docs for unfamiliar or non-trivial work. Update docs when behavior or a public contract changes.
- Validate proportionally. New observable behavior gets regression coverage when practical.
- Complete required checks; repeat or expand them only for changes, failures, or unresolved risks. Prefer targeted file edits.
- Before completion claims, provide evidence or name the blocking input.
- If a skill blocks requested work, link the exact file, quote the rule, and explain the unresolved conflict; distinguish the rule from your interpretation.
- For high-risk security, data, concurrency, migration, or public-contract work, obtain independent review when it adds independent evidence. Report GO/NO-GO, evidence, and residual risk. Keep severity separate from confidence.

## Communication

- Lead with the result. Use clear, concise, natural English for a global audience.
- Prefer active voice, present tense, and second person. State conditions before actions.
- Use consistent terms. Avoid idiom, jargon, hype, blame, and claims of ease.
- Use paragraphs, lists, or tables according to what makes the result clearest. Use descriptive sentence-case headings and links, with parallel list items.
- Preserve exact repository terms, templates, UI text, code, commands, and public contracts.
- For user-facing technical documentation, apply [`docs/technical-writing.md`](docs/technical-writing.md); project-specific rules remain authoritative.
- For substantial work, give a brief opening update and report meaningful progress, decisions, or blocks.
- Final handoff: outcome, material changes, evidence, residual risk; understandable without earlier updates.

## Learnings

- Read `LEARNINGS.md`, `/docs/LEARNINGS.md`, or similar files when relevant. Record only durable conventions, decisions, pitfalls, and useful commands.
- When summarizing a long task, preserve the user's objective, boundaries, decisions, completed work, and open items.

## Git

- Inspect status and relevant diffs before edits. Preserve unrelated changes.
- Use recoverable deletion when available. Ask before unexpected deletion or rename.
- Stage task files only. Commit staged content exactly when asked.
- Push, switch branches, amend, or run destructive Git commands only with explicit approval.
- Follow the repository's commit convention. Use structured prefixes only when policy or tooling requires them.
- Prefer small logical commits with concise imperative subjects. Add a body when the reason, impact, or trade-offs are not obvious; explain why instead of restating the diff.
- Use `gh pr view` and `gh pr diff` for PRs.

## Dependencies

- Prefer maintained platform features or libraries when they reduce complexity.
- Before adding a dependency, check release activity, adoption, docs, license, and fit. Compare options only when a choice remains.
