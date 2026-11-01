# Skill maintenance

Use skills for reusable workflows and domain guidance. Keep cross-cutting
behavior in [AGENTS.md](../AGENTS.md), agent roles in
[agent templates](agents.md), and inventory operations in [Skills](skills-sync.md).

## Review a skill

- Give it a short description with a specific trigger and boundary. Broad or
  overlapping triggers can load unnecessary guidance and crowd the catalog.
- Keep the entrypoint concise. Route to relevant references and scripts instead
  of loading every example or compiled guide on each task.
- State observable outcomes and meaningful constraints. Prescribe exact steps
  only where order or fragility requires them.
- Reuse established decisions and authorization. A skill cannot expand scope,
  grant permissions, or require another confirmation for an already settled step.
- Discover available tools and runners; a copied skill does not install the
  upstream plugin's MCP servers or commands.
- Preserve upstream content and provenance. Put portable kit policy in owned
  instructions; an intentional adaptation belongs under `local[]` with source
  attribution and license notices.
- Store durable conventions, commands, compatibility limits, and unresolved
  constraints. Consolidate them into the owning reference instead of keeping
  session transcripts, completed plans, or duplicate decision reports.

For tests, apply [`test-audit`](../skills/test-audit/SKILL.md): permanent coverage
needs a meaningful contract, a credible regression, and a gap in existing proof.
Existing checks and temporary verification may suffice for a small edit. Preserve
independent security, migration, protocol, and public-contract coverage.

## Imported guidance to interpret carefully

| Source | Constraint |
| --- | --- |
| `dotnet-testing/references/testing-strategy.md` | Test-per-class organization and simple-mapping examples do not require tests that mirror production classes. Decide value before choosing the framework pattern. |
| `improve/references/plan-template.md` | The test section may name existing checks or justify no new tests; its template does not require new coverage for every plan. |
| `winui-ui-testing` | Exhaustive element/requirement coverage fits a whole-app test request. Scope ordinary changes to affected flows and distinct risks. |
| Matt `tdd`, `implement`, `implement-spec` | Reuse confirmed seams; repository checks and Git authorization govern full-suite runs, commits, and branches. Installation alone does not invoke a workflow. |
| SwiftUI and GTK guides | Select one primary guide and only the specialists needed for the task. Retained snapshots are references, not additional required workflows. |
| `better-interface`, `swiftui-expert-skill`, `emil-design-eng` | Load relevant domains and API sections for focused changes. Full audits can justify broader reference loading. |
| `binlog-failure-analysis` | Discover the binlog MCP before using it. Its Bash replay example needs quoted logger parameters containing semicolons; use its documented generation command if the named generation skill is unavailable. |
| `git-commit` | Follow the repository's commit convention; Conventional Commits are a default only when established or requested. |
| `web-design-guidelines` | Infer files from the task or diff and use the available fetch tool instead of assuming `WebFetch`. |

## Evaluate material changes

Use representative tasks in fresh sessions on the actual host/model. Compare
selection, task completion, preserved contracts, unnecessary permanent test code,
repeated checks, and cost. Temporary fixtures can verify a one-off change;
retain an evaluation only when its repeated value warrants maintenance.
Structural checks establish packaging consistency, not behavioral improvement.

Verify model availability and supported effort levels before changing
`agent-templates/config.toml`. Model recommendations expire; keep concrete
routing policy in that config rather than copying model lists into documentation.

## Product skills

The owned product skills divide responsibilities by the work being done:

| Work | Owning guide |
| --- | --- |
| Product positioning, argument, writing, evidence, imagery intent and narrative across formats | [product-storytelling](../skills/product-storytelling/SKILL.md) |
| Product marketing website art direction, composition, typography, reusable presentation patterns, responsive behaviour and rendered review | [product-web-design](../skills/product-web-design/SKILL.md) |
| Product films, motion graphics, screen demonstrations, editorial rhythm, music and sound, and mixed-media production | [product-videos](../skills/product-videos/SKILL.md), with product-storytelling for original films and story revisions |
| Keynotes, presentation scripts and static or interactive deck story and scene direction | product-storytelling's [deck and keynote reference](../skills/product-storytelling/references/slide-decks.md), with the appropriate presentation production tool or guide |
| HTML, CSS and JavaScript code quality | [frontend-guidelines](../skills/frontend-guidelines/SKILL.md), plus a framework specialist when relevant |

For a new product website, develop the argument with product-storytelling and
carry it into product-web-design. For an established page, select the guide for
the actual change; a spacing repair need not reopen the story. The web guide
encodes a specific approach to product presentation, rather than a general
application-UI workflow. Its entrypoint and the storytelling entrypoint carry
these boundaries so they remain visible outside this repository.

Honour explicitly named skills in their requested roles. Use focused specialists
for unresolved questions; do not automatically stack competing complete design
workflows. Keep vendored skills available and unchanged. Keep the reusable
product skills independent of source brands: source attribution, captures and
observational limits belong in research notes, not in the skills.

## Sources

First-party authoring guidance, reviewed 2026-10-08:

- [OpenAI skill and prompt guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
- [OpenAI skill discovery and metadata](https://learn.chatgpt.com/docs/build-skills).
- [OpenAI model prompting guidance](https://developers.openai.com/api/docs/guides/latest-model).
- [Anthropic skill authoring](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- [Anthropic model prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
