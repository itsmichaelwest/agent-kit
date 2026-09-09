---
name: ux-design-spec
description: Produce an implementation-ready UX and design specification without writing application code. Use when the user asks for a UX spec, design brief, wireframe, interaction/state design, or handoff document before implementation.
---

# UX design specification

Create a decision-ready specification for the requested surface. This skill
plans the experience; it does not implement application code or replace an
existing product's visual identity.

Inspect the current product, design system, and constraints first when they
exist. Ask only about gaps that materially affect the specification. Preserve
established components, tokens, platform conventions, and factual content.

Cover the decisions needed to implement and review the work:

1. Goal, users, success conditions, and constraints.
2. Information architecture and primary user flows.
3. Layout and responsive behavior, with an ASCII wireframe when spatial
   structure would otherwise be ambiguous.
4. Component inventory, variants, and interaction states, including loading,
   empty, error, and validation states when relevant.
5. Reused and genuinely needed design-system tokens or primitives.
6. Accessibility: keyboard/focus behavior, labels, contrast, and motion.
7. Open decisions, assumptions, and implementation acceptance checks.

Use concrete labels, measurements, behavior, and state transitions. Explain
the rationale only where it resolves a real trade-off. Keep visual direction
appropriate to the product rather than imposing fonts, palettes, depth, or
motion for their own sake.

Complete when another engineer can implement the requested scope without
having to infer the intended hierarchy, states, or design-system strategy.

For a full handoff document, start from
[the specification template](references/spec-template.md). Adapt it to the
scope; omit sections that do not affect the requested surface.
