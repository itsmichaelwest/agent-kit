---
name: frontend-guidelines
description: Review or implement HTML, CSS, and JavaScript with semantic markup, maintainable CSS, and readable dependency-light JavaScript. Use for framework-agnostic frontend coding-style work, not framework-specific performance or visual-design reviews.
metadata:
  source: bendc/frontend-guidelines
  source-url: https://github.com/bendc/frontend-guidelines
  reviewed: 2026-09-09
---

# Frontend Guidelines

Apply this skill to framework-agnostic frontend code. Preserve the repository's
formatter, linter, browser support policy, design system, and public contracts;
they take precedence over a general style preference.

## HTML

- Prefer elements that communicate the content structure and interaction
  semantics. Do not introduce a semantic element when its meaning is wrong.
- Make interactive controls real links or buttons, associate every form control
  with an accessible label, write useful image alternatives, and ensure state
  is not conveyed by color alone.
- Declare the document language and UTF-8 encoding for complete HTML
  documents. Keep markup concise without sacrificing clarity or accessibility.
- Do not block initial content on nonessential scripts. Load critical styles
  promptly and defer noncritical work when it improves the visible loading
  experience.

## CSS

- Establish a consistent box model at the document level. Use Flexbox or Grid
  before absolute positioning, and keep content in normal flow where practical.
- Prefer selectors that express component intent over selectors coupled to a
  fragile DOM structure. Keep specificity low; avoid `!important` and avoid
  cascade overrides when a direct selector or component structure expresses the
  intent.
- Inherit common typography and visual properties instead of duplicating them.
  Use shorthands only when all included values are intentional and readability
  remains clear.
- Use standards-based properties. Add vendor prefixes only for browsers the
  project supports and put a necessary prefix before the standard declaration.
- Prefer transitions for interruptible state changes and animate compositor-
  friendly properties such as `transform` and `opacity` where they meet the
  intended effect. Never use `transition: all`.
- Do not use browser hacks or cargo-cult rendering workarounds. Diagnose the
  layout or performance problem first.

## JavaScript

- Prefer readable, correct code over micro-optimizations. Measure before
  optimizing JavaScript, and investigate network, image, and DOM work first.
- Keep functions pure where that does not obscure the task; do not mutate an
  input merely for convenience.
- Use platform APIs and language features before adding a dependency or custom
  utility. Add a dependency only when its value exceeds its maintenance and
  bundle costs.
- Use `const` by default and `let` when reassignment is required; do not add
  new `var` declarations. Prefer rest parameters and spread syntax to legacy
  `arguments` and `apply` patterns.
- Choose collection operations, loops, or recursion for clarity and runtime
  characteristics. Do not force functional methods or recursion where a simple
  loop is clearer or safer.
- Avoid clever coercion, terse control-flow tricks, and unnecessary currying.
  Favor explicit code that makes the condition and data transformation easy to
  review.
- Use `Map` or `Set` when their key, ordering, or uniqueness semantics fit the
  problem better than a plain object or array.

## Interpret the source in current context

The upstream guide is a durable set of preferences, not a compatibility target.
Do not enforce historical implementation details that conflict with current
standards, security, accessibility, browser support, or project tooling. In
particular, do not require hexadecimal colors over modern color syntax, avoid a
loop solely because `Array` methods exist, or replace project-approved tooling
without a concrete benefit.

For code review, report only material findings with `file:line`, the violated
principle, impact, and a concrete repair. State any browser- or framework-
specific assumption. For source examples and rationale, consult the upstream
[Frontend Guidelines](https://github.com/bendc/frontend-guidelines).
