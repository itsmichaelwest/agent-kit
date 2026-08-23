# Interaction and accessibility

Use this reference for keyboard and focus behavior, pointer and touch input, selection, drag and drop, shortcuts, AT-SPI, screen readers, high contrast, large text, and custom widgets.

## Keyboard contract

Every task must work without a pointer.

- Use GTK's standard focus behavior before adding custom key handling.
- Keep focus order consistent with visual and reading order.
- Give initial focus to the task's main control when that does not disrupt normal navigation.
- Restore focus to a meaningful control after a dialog closes, a row disappears, navigation returns, or an async operation replaces content.
- Keep Escape, Enter, Space, arrow-key, tab, and selection behavior consistent with the widget pattern.
- Add accelerators through actions. Avoid raw key controllers for application commands unless text input and widget behavior require context-sensitive handling.
- Show shortcuts in menus and a shortcuts dialog when the application has enough commands to justify one.

Do not intercept text-editing shortcuts globally. Let entries and text views handle editing commands in their focused context.

## Focus and default actions

Visible focus is part of the interface. Do not remove the focus ring through CSS.

- A dialog should have a safe default response.
- Destructive responses should not become the accidental default.
- Moving focus must not activate the command.
- When content becomes insensitive or hidden, move focus to the nearest meaningful surviving control.
- For composite custom widgets, expose one predictable focus entry and internal arrow navigation where the pattern calls for it.

Test focus after data refresh, row recycling, sorting, filtering, breakpoint changes, popover closure, and validation errors.

## Pointer and touch

Use standard GTK gestures and event controllers. Keep essential behavior available without hover, right click, precise pointing, or multiple buttons.

- Give controls a target size suitable for touch and imprecise pointing.
- Use tooltips for unlabeled icon buttons, but do not hide required instructions in a tooltip.
- Put context-menu commands in another discoverable surface when they are important.
- Avoid hover-only state changes that alter layout.
- Make double click a shortcut for an action that remains available through selection and activation.

## Selection

Selection and activation are separate contracts. A click may select an item without invoking its primary command.

- Use single selection for navigation and one active object.
- Enter an explicit selection mode for multi-select and show bulk actions in a stable surface.
- Keep bulk actions disabled when the current selection cannot support them.
- Preserve selection by stable item identity across sorting, filtering, and refresh.
- Announce selection-count changes where a screen-reader user needs them.
- Define what happens when the selected item disappears.

## Context menus and popovers

Open a context menu for the item under the pointer, not an unrelated stale selection. Update action state before presenting the menu.

Use menu models for command menus. Use a general popover for richer transient content that is not a command menu. Keep focus contained while open and return it on close.

## Drag and drop

Treat drag and drop as an alternate interaction path.

- Provide buttons, menus, or keyboard commands for the same essential operation.
- Use typed content providers and accept only declared formats and actions.
- Show a clear drop target and insertion position.
- Distinguish copy, move, and link semantics.
- Preserve stable item identity while reordering.
- Reject invalid drops without mutating the model.
- Support external file drops through GIO file or URI types rather than assuming local paths.
- Test cancellation, dropping on self, dropping across filtered views, and model changes during a drag.

## Accessible names and relationships

GTK exposes built-in widgets through its accessibility API, but application semantics still need review.

- Every interactive element needs a concise accessible name.
- Associate labels with entries and other controls.
- Expose descriptions for help text that changes how a control is understood.
- Expose state, value, role, and relationships for custom widgets.
- Mark decorative images so they do not add noise.
- Announce important dynamic status without repeatedly interrupting the user.
- Keep accessible names stable when visible labels contain counters or rapidly changing data.

Use `GtkAccessible` properties and relations supported by the project's GTK floor. Check the accessibility tree in GTK Inspector.

## Custom widgets

A custom-painted or composite widget must provide the semantics that native controls would have supplied.

Define:

- accessible role and name;
- current value, range, state, and description;
- focus behavior and keyboard commands;
- pointer and touch behavior;
- high-contrast and large-text rendering;
- hit testing and target size;
- reduced-animation behavior;
- announcements for meaningful changes.

Prefer composing existing accessible widgets when custom rendering does not require a new interaction model.

## Visual accessibility

- Preserve sufficient contrast in light, dark, and high-contrast modes.
- Provide text, shape, icon, or position in addition to color.
- Let system font and scaling settings control text size.
- Allow labels to wrap where truncation would remove meaning.
- Avoid flashing and repeated motion.
- Keep content usable at 200 percent text scaling.
- Test both left-to-right and right-to-left layout when the application is translated.

## Assistive-technology test pass

Complete the changed task with:

1. keyboard only;
2. high-contrast mode;
3. large text;
4. a screen reader such as Orca when semantics changed;
5. pointer or touch where gesture behavior changed;
6. reduced animations where motion changed.

Listen to the actual names, roles, states, and reading order. A visually correct widget can still expose the wrong object or no useful name.

## Primary references

- [GNOME accessibility HIG](https://developer.gnome.org/hig/guidelines/accessibility.html)
- [GNOME keyboard guidelines](https://developer.gnome.org/hig/guidelines/keyboard.html)
- [GTK accessibility](https://docs.gtk.org/gtk4/section-accessibility.html)
- [GtkAccessible](https://docs.gtk.org/gtk4/iface.Accessible.html)
- [AT-SPI source and documentation](https://gitlab.gnome.org/GNOME/at-spi2-core)
