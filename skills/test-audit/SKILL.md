---
name: test-audit
description: Gate new or changed tests; audit unnecessary, duplicate, or implementation-coupled tests. Use when authoring or reviewing tests, or asked to reduce test maintenance.
license: MIT
metadata:
  source: https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md
  source-reviewed: "2026-10-08"
  adaptation: "Kit-owned; portable authoring gate and focused audit, without OpenClaw runners or campaign dependencies."
---

# Test audit

Optimize confidence per maintenance cost. Use the authoring gate for new or
changed tests; use the audit workflow for existing test cleanup. A request to
assess tests is read-only unless edits are also authorized. Choose the project's
existing runner and required checks; this skill adds no framework or tooling.

## Authoring gate

Before keeping a test, establish:

1. The observable behavior, invariant, or independent contract it protects.
2. A credible regression that makes it fail.
3. Why existing tests miss that failure. Prefer extending the owning test or a
   table-driven case; another layer needs a distinct transport, lifecycle, or
   integration risk.
4. Whether it requires exports, flags, wrappers, or injection hooks without a
   production use. Prefer the real boundary over a test-only production seam.

These are decision criteria, not a questionnaire for the user or a required
report for every test. If no meaningful gap exists, run existing checks or use
temporary verification. Match scope to the requested change and project policy.
When TDD is requested, apply this gate within its red/green cycle.

For a bug regression, demonstrate failure on the pre-fix behavior for the
intended reason and success after repair when practical. If baseline reproduction
is unavailable, report the limitation; a post-fix pass alone is weaker evidence.

## Low-value patterns

- Assertions that compare a value with itself, copy constants, or calculate the
  expected result using the implementation under test.
- Assertion-free coverage probes, copied inventories, or source/import greps
  that have no independent contract.
- Private call-shape tests and repeated scenarios already covered at the owning
  public boundary.
- Mocks or fixtures that implement the behavior or supply the ordering the
  production path should produce.
- Tests maintained only to keep test-only exports, globals, wrappers, or dead
  production paths alive.
- Negative tests that pass because of an unrelated guard, or names claiming
  behavior the input and assertions never exercise.

A pattern is a review lead, not permission to delete. Ask whether a
behavior-preserving refactor would break the test and whether the apparent
implementation detail is itself a required contract.

## Retention bar

Keep independent public API, security, protocol, migration, storage, platform,
configuration, release, generated-code, or architecture contracts. Keep observable
ordering, defaults, exact bytes, and source checks when they are the cheapest
independent guard of an actual contract. Multiple layers can be justified by
different failure modes. Static or slow tests are not automatically low-value.
A baseline failure may reveal a product bug; investigate it instead of deleting
the test to obtain a green suite.

## Audit workflow

1. Read applicable instructions and the relevant test, production owner, entry
   point, callers, overlapping tests, CI routing, and history. Inspect dependency
   types or source when the test claims dependency behavior. Bound discovery to
   the requested area; prefer a few proven candidates over a speculative sweep.
2. Record each candidate's exact name and location, failure it detects, non-test
   users of any seam, stronger remaining proof (or why proof is unnecessary),
   historical purpose, cleanup enabled, risk, and focused validation command.
   Missing evidence means retain it pending investigation.
3. Report the evidence before editing. Within authorized cleanup, make one
   coherent batch: consolidate duplicates, move useful regressions to their
   owner, and remove proven obsolete seams. Check callers before removing APIs.
   Prefer simpler production code; deletion count is not a success criterion.
4. Pause test/watch processes you started before editing their checkout. For
   unrelated or shared runs, use an isolated checkout or obtain authorization
   before stopping them. Run focused
   owner and affected sibling tests, executable or dry-run contract checks where
   appropriate, formatting, `git diff --check`, and required repository gates.
   Broaden checks only for integration risks, failures, or repository policy.

Finish with candidates removed or rewritten, retained false positives, owner
simplifications, validation actually run, and remaining uncertainty. For a broad
cleanup, report production and test changes separately. Follow the repository's
authorization for commits, pushes, and PRs.
