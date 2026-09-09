---
name: improve-agent-environment
description: Assess why agents struggle in a project and propose improvements to their context, tools, and verification. Use when reviewing an agent environment or investigating recurring task friction; ordinary bug fixes and general code reviews stay in their existing workflows.
metadata:
  source: "https://openai.com/index/harness-engineering/"
  source-reviewed: "2026-09-09"
---

# Improve agent environment

Identify the smallest lasting improvements that would help agents complete and verify real work in this project. Start from observed friction: repeated corrections, blocked attempts, unnecessary investigation, or inconclusive validation.

Default to a read-only assessment and return proposals in chat. Treat implementation as a separate scope; if the user already requested it, carry the selected improvements through the normal development workflow within that authorization.

## Establish the evidence

Use the requested project and focus. Read its governing instructions, relevant documentation, and the tooling involved in the reported difficulty. Inspect command definitions before running diagnostics; assessment alone does not authorize setup, installation, configuration changes, or device interaction.

Use available task history, review feedback, logs, and repository evidence to identify where work stalled or required human correction. Retrieve only history relevant to the project and question. If earlier tasks are unavailable, say so and continue from current evidence; ask for a representative failure only when it would materially change the diagnosis. Distinguish a reported recurrence from an observed one.

For a broad assessment without failure history, trace a representative task through discovering requirements, making a change, and verifying its outcome using the existing documented paths. Label gaps inferred from inspection as hypotheses. A missing conventional file or tool is not evidence that the project needs it.

## Trace the missing support

For each candidate problem, identify the task, the point of friction, and what information or capability the agent had at that point. Use these lenses where relevant:

- **Context:** Can the agent discover authoritative constraints, architecture, and current decisions? Is guidance stale, contradictory, duplicated, or difficult to reach?
- **Capabilities:** Can the available tools build, run, inspect, and debug the relevant system? Do platform, isolation, or access limits prevent the required work?
- **Feedback:** Can the agent reproduce the failure and distinguish a successful outcome from a passing build or unrelated test? What observable acceptance criterion is missing?

Check whether adequate support already exists and the agent failed to use it. In that case, examine discovery or adherence before proposing more infrastructure. Distinguish environmental gaps from unclear product requirements, a one-off execution mistake, and judgment or physical verification that still belongs to a person. Separate access unavailable during this assessment from a persistent limitation affecting project work.

## Choose a proportionate improvement

Prefer improving an existing path over adding another one. Match the remedy to the cause: a pointer to authoritative context, an updated decision record, a reusable diagnostic command, a reproducible local setup, or a check that detects the actual failure.

Recommend tooling or automated validation when it can reliably enforce a repeated correction. Keep judgment in prose where a mechanical rule would be misleading. Account for setup and maintenance burden; dependencies, observability stacks, background agents, and additional instructions need a demonstrated benefit for this project.

Place project-specific commands and constraints in the project. Suggest a shared-kit change only when the method is reusable across projects. Preserve working conventions and name any contract an improvement would change.

## Supporting assessment lenses

Adapted from [OpenAI's harness engineering article](https://openai.com/index/harness-engineering/). These are diagnostic options, not mandatory infrastructure.

- **Human attention:** Target repeated intervention and unreliable outcomes; output volume alone is not success.
- **Knowledge continuity:** Use brief entry instructions linking to authoritative records. Preserve decisions, plans, progress, and outstanding debt across sessions.
- **Observable execution:** Consider isolated task environments and accessible UI, logs, metrics, and traces. Tie measurements and before/after evidence to acceptance criteria.
- **Inspectable design:** Prefer understandable, stable abstractions. Investigate opaque dependencies before proposing replacement.
- **Enforceable boundaries:** Encode architectural dependencies, data validation, and recurring conventions in checks where reliable. Diagnostics should explain repairs; preserve implementation freedom within constraints.
- **Complete feedback:** Examine reproduction, implementation, independent review, feedback handling, validation, and recovery. Build missing prerequisites before extending autonomy.
- **Ongoing maintenance:** Look for copied poor patterns. Consider targeted cleanup, checking documentation accuracy, links, ownership, and verification status, and tracking persistent quality gaps.

Evaluate merge gates against consequences and recovery cost. The article's permissive merges, mandatory agent authorship, exact architecture, and tooling choices are contextual. Long-term coherence remains uncertain; reassess improvements against later outcomes.

## Return actionable proposals

Rank the supported proposals by their expected reduction in recurring friction, considering evidence strength and maintenance cost. For each, include:

- **Problem and evidence:** The task failure or correction, with precise source references and whether recurrence is observed, reported, or unknown.
- **Missing support:** The cause and why the existing environment does not address it; state uncertainty separately from impact.
- **Smallest improvement:** Concrete scope in files, tools, or contracts, plus material trade-offs or prerequisites.
- **Success criterion:** How a later task could demonstrate that the improvement works, ideally by replaying the same failure or verification scenario.

Keep the list as short as the evidence warrants. If no worthwhile change is supported, say so. End with the recommended first improvement and any evidence needed to decide; do not present proposals as implemented or verified.
