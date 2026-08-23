---
name: designing-gnome-ui
description: Use for every user-visible change in a GNOME app, new or existing, whether or not the request uses design vocabulary. Trigger on the repo rather than the wording — if it depends on gtk4/libadwaita (or is a GNOME-targeted Qt/PySide6 app), anything a user can see or interact with goes through this skill, including requests phrased purely as symptoms ("can I right-click to delete", "the window opens too small", "reordering doesn't work"). Covers choosing widgets, icons, dialogs, menus, sidebars, navigation, and empty states; interaction bugs in context menus, drag-and-drop reordering, window sizing, layout, duplicate affordances, and controls missing or inert at launch; and HIG review. Complements developing-gtk-apps, which owns architecture, threading, language syntax, and build/test plumbing.
---

# Designing GNOME UI

Design GNOME UIs that are HIG-compliant, polished, and user-centered.

**Core principle:** No UI code without design decisions. Pattern selection happens before implementation.

**Companion skill:** For app architecture (lifecycle, threading, GSettings, actions, list-model/factory code, packaging), use `developing-gtk-apps`. Snippets in this skill are Python (PyGObject) and illustrate *which widget and how it fits together*; for Vala or Rust syntax, use that skill's language branch files.

**Subagents:** a subagent given UI work loads no skills on its own — its prompt must tell it to invoke `designing-gnome-ui` (and `developing-gtk-apps` for plumbing).

## What's Current (libadwaita 1.9, GTK 4.22)

Training data reaches for APIs that are now deprecated. Write the current column, every time:

| Deprecated (when) | Current (since) |
|---|---|
| `AdwPreferencesWindow` (1.6) | `AdwPreferencesDialog` (1.5) |
| `AdwMessageDialog` (1.6), `GtkMessageDialog` (4.10) | `AdwAlertDialog` (1.5) |
| `AdwAboutWindow` (1.6) | `AdwAboutDialog` (1.5) |
| `AdwLeaflet`, `AdwFlap`, `AdwSqueezer`, `AdwViewSwitcherTitle` (all 1.4) | `AdwBreakpoint` + `AdwNavigationSplitView`/`AdwNavigationView`/`AdwOverlaySplitView`, `AdwToolbarView` (all 1.4) |
| `GtkShortcutsWindow` (4.18) | `AdwShortcutsDialog` (1.8) |
| `GtkFileChooserDialog`/`Native` (4.10) | `GtkFileDialog` (4.10, async) |
| `GtkColorChooserWidget`/`Button` (4.10) | `GtkColorDialog` + `GtkColorDialogButton` (4.10) |
| `GtkVolumeButton` (4.10) | `GtkScaleButton` or `GtkScale` |
| `GtkSpinner` (in Adw apps) | `AdwSpinner` (1.6) — works with animations disabled |
| `.dim-label` CSS class | `.dimmed` |
| `@accent_color` named colors, `@define-color` | `var(--accent-color)` CSS variables |

**Why the `*Window` → `*Dialog` shift:** `AdwDialog` (1.5) presents adaptively — a centered dialog on desktop, a bottom sheet on narrow/mobile screens — and attaches with `dialog.present(parent)` instead of `transient_for`. Every window-based dialog type was retired in its favor; when you meet a new `Adw*Window`/`Adw*Dialog` pair, the `*Dialog` one is current.

**Widgets newer than training data** (verify the API, don't guess it):

| Need | Widget (since) |
|------|----------------|
| Exclusive toggles (view mode) | `AdwToggleGroup` + `AdwToggle` (1.7) |
| Persistent bottom controls (player) | `AdwBottomSheet` (1.6) |
| Wrapping content (tag chips) | `AdwWrapBox` (1.7) — `child-spacing`/`line-spacing`, no `spacing` property |
| Inline view switching (cards, sidebars) | `AdwInlineViewSwitcher` (1.7) |
| Full-width button in boxed list | `AdwButtonRow` (1.6) |
| Sectioned sidebar | `AdwSidebar` + `AdwSidebarSection`/`AdwSidebarItem` (1.9) |
| Sidebar that switches an `AdwViewStack` | `AdwViewSwitcherSidebar` (1.9) |
| Keyboard shortcuts dialog | `AdwShortcutsDialog` (1.8) |
| System monospace/document fonts | `AdwStyleManager` `get_monospace_font_name()`/`get_document_font_name()` (1.7); CSS `--monospace-font-family`, `--document-font-family` |
| System accent color | Automatic via portal; `--accent-bg-color` etc. |

```python
# AdwToggleGroup - view mode switching (note: Adw.Toggle objects, not buttons)
toggle_group = Adw.ToggleGroup()
toggle_group.add(Adw.Toggle(icon_name="view-grid-symbolic", name="grid"))
toggle_group.add(Adw.Toggle(icon_name="view-list-symbolic", name="list"))
toggle_group.connect("notify::active-name", lambda g, p: set_view(g.get_active_name()))
header.pack_start(toggle_group)

# AdwBottomSheet - music player controls
bottom_sheet = Adw.BottomSheet()
bottom_sheet.set_content(main_content)
bottom_sheet.set_sheet(player_controls)
bottom_sheet.set_open(True)
window.set_content(bottom_sheet)

# AdwWrapBox - tag display (child_spacing/line_spacing, NOT spacing)
wrap_box = Adw.WrapBox(child_spacing=6, line_spacing=6)
for tag in ["Python", "GTK", "GNOME"]:
    wrap_box.append(Gtk.Label(label=tag))
```

## Verify, Then Claim

A widget or version claim is confirmed by the installed introspection data, not by memory: `/usr/share/gir-1.0/Adw-1.gir` and `Gtk-4.0.gir` carry `version="1.x"` (since) and `deprecated-version="1.x"` attributes on each class — parse them (attributes span multiple lines; plain grep on the class name misses them). A CSS class is confirmed by the shipped stylesheet: `gresource extract /usr/lib/x86_64-linux-gnu/libadwaita-1.so.0 /org/gnome/Adwaita/styles/default-light-yaru-default.css` (path varies by distro patching; `gresource list` shows what's there). Presence in the stylesheet proves a class exists; only the GIR/docs settle whether it is current or a deprecated alias (`.dim-label` still ships beside `.dimmed`). An icon name is confirmed by the installed theme:

```bash
find /usr/share/icons/Adwaita -name 'NAME-symbolic.svg' | head -1
```

Some icons ship inside GTK/libadwaita gresources, so an empty result is a strong signal rather than proof — `gtk4-icon-browser` is the exhaustive check.

## Container Selection

| Scenario | Default | Notes |
|----------|---------|-------|
| App window | `AdwApplicationWindow` + `AdwHeaderBar` in `AdwToolbarView` | Remember user size, start ~800x600 |
| Settings | `AdwPreferencesDialog` | Pages, groups, search built in; `present(parent)` |
| List of settings/items | `AdwPreferencesGroup` with rows | Boxed list style |
| Modal action / decision | `AdwDialog` / `AdwAlertDialog` | Adaptive; bottom sheet on narrow screens |
| Primary action | Single button, header bar end | `suggested-action` class; one per view |
| Destructive action | `destructive-action` class | Pair with undo or confirmation |

## Navigation Selection

| Structure | Default Pattern |
|-----------|-----------------|
| Single view | None needed |
| 2-4 views | `AdwViewSwitcher` in header bar + `AdwViewSwitcherBar` below breakpoint |
| Many/dynamic views | `AdwNavigationSplitView` with `AdwSidebar` (1.9) or `GtkListBox.navigation-sidebar` |
| View switching via sidebar | `AdwViewSwitcherSidebar` (1.9) |
| Hierarchical (drill-down) | `AdwNavigationView` |
| Utility pane that overlays when narrow | `AdwOverlaySplitView` |

Adaptivity comes from `AdwBreakpoint` setters on the window (`max-width: 600sp` → set `collapsed`), never from swapping widget trees by hand.

## Control Defaults

| Need | Default | Instead of |
|------|---------|-----------|
| On/Off | `AdwSwitchRow` | Checkbox for settings |
| Choose one (few) | `AdwComboRow` | Radio buttons outside dialogs |
| Choose one (many) | `AdwComboRow` + `enable-search` | Long unsearchable dropdowns |
| Text input | `AdwEntryRow` | Bare `GtkEntry` in lists |
| Multiline text | `GtkTextView` in `ScrolledWindow` + `card` class | Bare unstyled text view |
| Number | `AdwSpinRow` | Text entry for numbers |
| One primary action with related variants (a `+` that can create several kinds of thing) | `AdwSplitButton` — main action on the button, siblings in `menu-model` | A single button that silently picks one variant |
| Button in a boxed list | `AdwButtonRow` (1.6) | Hand-styled full-width `GtkButton` |
| Action in list | `AdwActionRow` + one suffix button | Multiple buttons per row |
| Search | `GtkSearchBar` + header toggle, `set_key_capture_widget(window)` | Always-visible search box |

## List Widget Selection

| Content | Widget | Tie-breaker |
|---------|--------|-----|
| Settings/preferences | `AdwPreferencesGroup` | Static rows, boxed style |
| Navigation/selection list | `GtkListBox` | Row widgets, `.navigation-sidebar` class, fine under ~hundreds of rows |
| Large/dynamic data | `GtkListView` | Recycled widgets via factory — required for thousands of rows |
| Grid of items | `GtkGridView` | Same factory model as ListView |

Selection: `Gtk.SingleSelection` for navigation, `Gtk.MultiSelection` behind an explicit selection mode (header toggle + `GtkActionBar` for bulk actions). Factory/model code lives in `developing-gtk-apps`.

## Iconography

Symbolic icons only (`-symbolic`, monochrome). Header bar buttons are icon-only with tooltips. Icons beyond the system theme (browse the GNOME Icon Library app) must be bundled as resources — a bare `icon_name` string only resolves from the installed theme.

| Action | Icon (verified in Adwaita theme) |
|--------|------|
| Add/New | `list-add-symbolic` |
| Delete | `user-trash-symbolic` |
| Settings | `emblem-system-symbolic` |
| Menu | `open-menu-symbolic` |
| Search | `system-search-symbolic` |
| Edit | `document-edit-symbolic` |
| Back | `go-previous-symbolic` |
| Drill-down | `go-next-symbolic` |
| Offline | `network-offline-symbolic` |
| Warning / Error | `dialog-warning-symbolic` / `dialog-error-symbolic` |
| Select mode | `selection-mode-symbolic` |
| Check/Done | `object-select-symbolic` |
| Close | `window-close-symbolic` |
| Refresh/Sync | `view-refresh-symbolic` |
| Open / Save | `document-open-symbolic` / `document-save-symbolic` |
| Copy | `edit-copy-symbolic` |
| Find in content | `edit-find-symbolic` |
| Link | `insert-link-symbolic` |
| Attach | `mail-attachment-symbolic` |
| Toggle sidebar | `sidebar-show-symbolic` |
| New folder | `folder-new-symbolic` |
| Overflow/More | `view-more-symbolic` |
| Sort | `view-sort-ascending-symbolic` |
| Move up / down | `go-up-symbolic` / `go-down-symbolic` |
| Remove from list | `list-remove-symbolic` |
| Favorite | `star-new-symbolic` |
| Expand/Collapse | `pan-down-symbolic` |
| Play | `media-playback-start-symbolic` |

Plausible-sounding names are routinely absent (`chain-link-`, `attach-`, `dock-left-`, `view-sidebar-start-`, `emblem-ok-symbolic` all fail on this system) — run any name not in this table through the `find` check in "Verify, Then Claim" before using it.

## Designing Against Platform Limits

Some controls cannot work on GNOME Wayland without a companion shell extension:
positioning a window, keeping it above others, hiding it from the dock, grabbing
a global shortcut. The design question is what the UI does when the capability
is absent — and the answer is never "look like it worked".

| State | Do | Not |
|-------|----|----|
| Capability unavailable | Show the control **insensitive**, with a tooltip naming what is missing | Leave it interactive; a toggle that latches while nothing happens reads as a bug in your app |
| Capability unavailable | Keep the control **present** | Hide it — a control that appears and disappears between sessions is harder to learn than one that greys out |
| Degraded, not broken | Say what still works ("content and size still persist") | Imply total failure |

```python
pin_button.set_sensitive(available)
pin_button.set_tooltip_text(
    "Keep on Top" if available else
    "Keep on Top needs the … extension — Wayland does not let apps raise "
    "their own windows")
```

Architecture for this lives in `developing-gtk-apps`
(`gnome-shell-companion-reference.md`).

## Feedback Selection

| Scenario | Default | Details |
|----------|---------|---------|
| Action done | `AdwToast` | Short message, optional button |
| Destructive action | `AdwToast` + Undo button | Prefer over confirmation dialog |
| Error (recoverable) | `AdwToast` | Brief, auto-retry silently |
| Error (blocking) / needs decision | `AdwAlertDialog` | Cancel first, specific verb last, `DESTRUCTIVE` appearance |
| Persistent state (offline, auth) | `AdwBanner` | Top of content, optional button |
| **Data not being saved** | `AdwBanner`, and keep it up | Ongoing condition, not an event. A toast is missed while typing, and the cost of missing it is lost work. Log once, show until fixed |
| Capability missing (needs a shell extension) | Insensitive control + tooltip | Never a dialog on startup; it is a limit, not an error |
| Short wait (<5s) | `AdwSpinner` | No progress bar |
| Long operation | `GtkProgressBar` + text | "13 of 42 processed" |
| Empty list | `AdwStatusPage` | Icon + title + `pill`+`suggested-action` button |
| Event while backgrounded | `GNotification` | Not toasts — those need the window visible |

**Escalation:** Toast (transient) → Banner (persists) → Dialog (requires action).

## Typography & Color

Style classes, not custom CSS: `title-1`…`title-4`, `heading`, `body`, `caption`, `caption-heading`, `monospace`, `numeric`, `dimmed` — and `card`, `pill`, `flat`, `boxed-list`, `navigation-sidebar`, `toolbar`, `osd`, `error`/`warning`/`success` (all present in the 1.9 stylesheet). Colors via `var(--accent-color)`-style variables only — full table in `gnome-hig-reference.md`.

Writing: header capitalization for buttons/menus/titles, sentence capitalization for descriptions/switch labels, no trailing periods, verbs not "OK". Details in `gnome-hig-reference.md`.

## Definition of Done

The design is implemented when the assembled window has been rendered and looked at, and every line checks out against the code.

**Render first.** Launch the app (or a screenshot harness — `developing-gtk-apps` has the run/render plumbing) and inspect the actual window before calling anything done; compiling and passing tests draw zero frames. Check in the render:

- Close/minimise/maximise are visible in every pane state — libadwaita puts window controls on the outermost header bar, so `show-end-title-buttons(false)` on the wrong pane's header removes them entirely.
- The shortcuts dialog shows its accelerators — accelerator strings in code are plain `<Control>n`; XML-escaped entities (`&lt;Control&gt;n`) belong only inside `.ui` files.
- Sidebars/panes start in their intended state — set the split view's `show-sidebar` explicitly and bind the toggle *from* it; a `sync_create` bind from a default-inactive toggle hides the sidebar at launch.
- Content fills the window — a custom widget sets `vexpand`/`hexpand` on itself; a scroller expanding inside a 30px-tall parent means the parent lacks the flag.

**Then line checks:**

- Every `Adw`/`Gtk` class used appears non-deprecated in the installed GIR (the "What's Current" table has the swaps; anything unfamiliar goes through "Verify, Then Claim").
- Dialogs are `AdwDialog` subclasses presented with `present(parent)`.
- Windows that can go narrow have `AdwBreakpoint`s driving `collapsed`/switcher-bar changes.
- Colors and fonts come from `var(--…)` variables or style classes — zero hardcoded hex values.
- Text uses `.dimmed`, never `.dim-label`.
- Every icon-only button has `tooltip_text`; every icon name either exists in the Adwaita theme or is bundled.
- Each user action has exactly one affordance in the visible view — count across header bar, sidebar, and content together (a header `+`, a sidebar pill, and a content pill for the same "New" is two too many), and at most one empty state is on screen at a time.
- At most one `suggested-action` per view and destructive actions carry undo or an `AdwAlertDialog` confirmation.
- Controls for capabilities the platform may not provide are insensitive with an explanatory tooltip, never silently inert.
- Failures that lose user data raise a persistent banner, not a toast.
- Labels follow the capitalization table (header caps for buttons/menus, sentence caps for descriptions).

## Non-GTK Apps (Qt/PySide6)

No maintained Adwaita Qt theme exists — style via QSS using the color variables above, map header bar → fixed toolbar, and reuse this skill's pattern/spacing/typography decisions. Test beside a native GNOME app.

## Reference Files

| The question in front of you | Read |
|------|------|
| "How is this pattern wired?" — the `AdwAlertDialog` response contract (who closes the dialog, the Enter path), `AdwSidebar` sections/selection/context menus, which containers already scroll, theming `GtkTextTag` colors for dark mode, search, file dialogs, breakpoints, menus, writing style, the color-variable table | `gnome-hig-reference.md` |
| "How do I build drag & drop / tabs (`AdwTabView`) / system notifications / zoom gestures / paned views / an onboarding carousel / widget-scoped shortcuts?" | `gnome-advanced-patterns.md` |
