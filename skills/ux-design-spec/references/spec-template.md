# UX and design specification template

Use this template when the request needs a complete handoff. Keep concrete
decisions, remove sections that do not apply, and mark unresolved choices
instead of inventing them.

````markdown
# [Feature or surface] UX and design specification

## Goal and success conditions

- User need:
- Primary users:
- Success conditions:
- Constraints:

## Product context

- Platforms and breakpoints:
- Existing components, tokens, and patterns to reuse:
- Content, technical, or compliance constraints:
- Assumptions requiring confirmation:

## Information architecture and flow

1. [Entry point] → [primary action] → [success state]
2. [Alternative or recovery path]

## Layout and responsive behavior

- Desktop:
- Compact/tablet:
- Mobile:

## Wireframe

```text
Desktop
+--------------------------------------------------+
| Header: title                         [Action]   |
+--------------------------------------------------+
| Navigation   | Main content                       |
|              | [Primary panel]                   |
|              | [Supporting content]              |
+--------------------------------------------------+

Mobile
+------------------------------+
| Header                [Menu] |
+------------------------------+
| Main content                 |
| [Primary panel]              |
| [Supporting content]         |
+------------------------------+
```

## Component inventory

| Component | Purpose | Reuse or change | Variants and states |
| --- | --- | --- | --- |
| [Component] | [User task] | [Existing/new] | [Default, focus, error] |

## Interaction and state matrix

| User action or condition | System response | Feedback | Recovery/accessibility |
| --- | --- | --- | --- |
| [Submit valid form] | [Save] | [Confirmation] | [Focus next logical control] |
| [Request fails] | [Preserve input] | [Specific error] | [Retry action] |

Include loading, empty, error, validation, and permission states when they
change the user experience.

## Visual and design-system strategy

- Reused tokens and primitives:
- New token/component only if an identified gap requires it:
- Typography, spacing, and surface decisions:
- Iconography, imagery, and motion decisions:

## Accessibility

- Keyboard order and visible focus:
- Labels, names, roles, and announcements:
- Contrast and non-color state cues:
- Motion and reduced-motion behavior:

## Acceptance checks

- [Observable behavior or visual condition]
- [Responsive or platform condition]
- [Accessibility condition]

## Open decisions

- [Decision owner, information needed, or fallback]
````

## Useful specification examples

Use precise relationships when they matter:

- “The desktop sidebar remains visible at widths above 1024px; below that, it
  moves into the menu and preserves the current destination label.”
- “The save control is disabled only while the request is in flight. A failed
  save preserves entered values, announces the error, and focuses the summary.”
- “The existing 8px spacing scale remains in use. The chart and its summary
  share a 16px gap; separate sections use 24px.”
- “A nested image tile uses the project’s established surface treatment. If a
  new radius is required, document its relationship to the parent padding.”

Avoid aesthetic defaults without evidence. For example, name the existing font,
palette, or elevation rule when known; otherwise record that visual direction
is still a decision rather than prescribing one.
