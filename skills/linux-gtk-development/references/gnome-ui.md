# GNOME UI design

Use this reference for every user-visible GTK or libadwaita change. Start with the task and information architecture, then choose a GNOME pattern and widget.

## Design source

Use the [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/) as the design contract for a GNOME-facing application. Check [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/) and [GTK 4](https://docs.gtk.org/gtk4/) for the API supported by the project.

Read [libadwaita and Adwaita Demo](libadwaita-adwaita-demo.md) before selecting navigation, dialogs, adaptive layout, toolbar structure, preferences, banners, toasts, or libadwaita CSS. It records current replacements for designs that older examples still teach.

GNOME design favors focused applications, direct manipulation, clear language, progressive disclosure, undo, and low user effort. Start from the constrained window size and input method. Add room for larger displays after the narrow design works.

## Map the task before choosing widgets

Write down:

- the user's goal and the object they act on;
- primary, secondary, and destructive commands;
- loading, empty, populated, partial, offline, error, and completion states;
- navigation depth and whether context must remain visible;
- selection behavior and what persists across refreshes;
- minimum useful window size and narrow-layout behavior;
- keyboard, pointer, touch, and assistive-technology paths.

Remove duplicate affordances that invoke the same command without improving discovery or efficiency. Keep the primary action close to its content.

## Window and navigation patterns

For a libadwaita application, the common base is `AdwApplicationWindow` with `AdwToolbarView` and `AdwHeaderBar`. Use the repository's existing shell when it already provides the required behavior.

Choose navigation from the content structure:

- one view needs no navigation control;
- a few peer views fit a view switcher, with a bottom switcher at narrow widths when needed;
- hierarchical drill-down fits `AdwNavigationView`;
- sidebar and detail content fits `AdwNavigationSplitView`;
- a utility pane that overlays at narrow widths fits `AdwOverlaySplitView`;
- tabs fit document-like content where users create, close, reorder, and revisit several independent items.

Use the current libadwaita navigation widgets available at the project's minimum version. Do not build adaptive behavior by destroying and recreating the whole view tree. Use breakpoints and container state so focus, selection, and model identity survive resize.

## Controls

Select controls by meaning:

- use a switch row for an immediate on or off preference;
- use a check button when several independent options form part of a task or form;
- use a combo row for one choice from a larger set;
- use entry, password, spin, and expander rows for their matching preference data;
- use a split button when one primary command has closely related variants;
- use a menu button for secondary commands, not the only route to the main task;
- use search mode for transient search and a persistent entry when search is the view's main purpose;
- use list, grid, or column views for dynamic data and preference rows for settings.

Use specific verbs for buttons and menu items. Reserve suggested appearance for the single primary action in the current context. Reserve destructive appearance for commands that destroy data or access.

## Feedback and status

Match feedback duration to the condition:

- use an `AdwToast` for a brief completed action or recoverable event;
- use a toast with Undo for a reversible destructive action;
- use an `AdwBanner` for a persistent condition that affects the view;
- use an `AdwStatusPage` for empty, unavailable, or failed content that occupies the main view;
- use a spinner for a short indeterminate wait;
- use progress with meaningful text when duration or item count matters;
- use `AdwAlertDialog` when the user must make a decision before continuing;
- use a desktop notification when an event matters outside the visible window.

Keep the last usable content visible during a refresh when possible. Distinguish "no results" from "nothing exists," and both from "loading failed."

## Destructive actions

Prefer undo when the application can restore the prior state reliably. Confirm an action when it is hard to reverse, costly, surprising, or affects data outside the application.

A confirmation names the object, explains the consequence, and uses a specific destructive verb. The safe response comes first in keyboard order. Requiring users to type an identifier is appropriate only for unusually consequential operations.

## Adaptive layout

Support the project's declared minimum size. GNOME applications should remain usable when tiled and at large text scale.

- Start with the narrow layout.
- Use breakpoints to collapse split views, move controls, or change navigation presentation.
- Keep every command and piece of information available after the breakpoint.
- Constrain text and forms at wide sizes so line length and control distance remain readable.
- Preserve selection, focus, scroll position, and in-progress input while resizing.
- Test continuously around each breakpoint for oscillation, clipping, and abrupt jumps.

## Styling

Use libadwaita style classes and semantic colors before custom CSS. They adapt to system accent, light, dark, and high-contrast modes.

- Use typography classes to express hierarchy instead of fixed font sizes.
- Use spacing from existing patterns and containers instead of a private spacing system.
- Use symbolic icons for interface actions and full-color application icons for identity.
- Verify every icon name against the installed theme or bundled resources.
- Keep custom CSS local to a component and avoid selectors that depend on GTK's private widget tree.
- Do not use fixed light-theme colors, color alone for status, or CSS that removes visible focus.
- Allow system fonts and text scaling to control metrics.

A GTK application can have its own visual identity without replacing Adwaita. Content, illustrations, app icon, empty states, domain-specific visualizations, and careful hierarchy provide room for that identity.

## Motion

Use motion to explain a state or spatial relationship. Navigation, expansion, reveal, reordering, and direct manipulation are good candidates.

- Respect the toolkit animation setting.
- Keep interaction available during transitions.
- Preserve the apparent source and destination of moved content.
- Avoid looping decoration and large motion without a task benefit.
- Test reduced-animation behavior and low-powered hardware where motion is substantial.

## UI writing

Use short, concrete text that names the user's object and action.

- Use established GNOME terminology.
- Use header capitalization and sentence capitalization according to the HIG.
- Use an ellipsis only when the command needs more input before it can run.
- Keep error headings useful without technical codes. Put diagnostics in logs or expandable details when the product needs them.
- Write complete translatable strings. Do not assemble sentences from fragments in separate controls.
- Give destructive and irreversible commands specific labels rather than "OK" or "Yes."

## Visual review

Render every state the change can produce. Inspect normal and narrow widths, long labels, empty content, dense content, disabled controls, focus, menus, popovers, dialogs, error states, destructive states, and in-progress operations.

Check alignment, grouping, hierarchy, density, text wrapping, truncation, target size, focus visibility, scroll behavior, breakpoint transitions, and whether one action reads as primary.

## Primary references

- [GNOME design principles](https://developer.gnome.org/hig/principles.html)
- [GNOME guidelines](https://developer.gnome.org/hig/guidelines.html)
- [GNOME patterns](https://developer.gnome.org/hig/patterns.html)
- [Scaling and adaptiveness](https://developer.gnome.org/hig/guidelines/adaptive.html)
- [UI styling](https://developer.gnome.org/hig/guidelines/ui-styling.html)
- [Writing style](https://developer.gnome.org/hig/guidelines/writing-style.html)
