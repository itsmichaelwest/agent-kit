# GNOME HIG Reference

Pattern catalog with code for GTK 4/libadwaita, verified against libadwaita 1.9 / GTK 4.22. Snippets are Python (PyGObject) and show widget wiring; for Vala/Rust syntax use the `developing-gtk-apps` language branches.

## Application Window

`AdwApplicationWindow` as root, `AdwHeaderBar` inside an `AdwToolbarView` (1.4):

```python
class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="My App")
        self.set_default_size(800, 600)

        header = Adw.HeaderBar()

        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Add Item")
        header.pack_end(add_btn)

        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_btn.set_tooltip_text("Main Menu")
        header.pack_end(menu_btn)

        content = Adw.Clamp(maximum_size=600)  # default is also 600

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(content)
        self.set_content(toolbar_view)
```

## Preferences Dialog

`AdwPreferencesDialog` (1.5) — not the deprecated `AdwPreferencesWindow`. It is an `AdwDialog`: no `transient_for`/`modal`, present with `present(parent)`, adapts to a bottom sheet on narrow screens.

```python
class Preferences(Adw.PreferencesDialog):
    def __init__(self):
        super().__init__()

        page = Adw.PreferencesPage(title="General", icon_name="emblem-system-symbolic")
        group = Adw.PreferencesGroup(title="Appearance")

        dark_row = Adw.SwitchRow(title="Dark Mode", subtitle="Use dark color scheme")
        group.add(dark_row)

        font_row = Adw.ComboRow(title="Font Size")
        font_row.set_model(Gtk.StringList.new(["Small", "Medium", "Large"]))
        font_row.set_selected(1)
        group.add(font_row)

        page.add(group)
        self.add(page)

Preferences().present(parent_window)
```

**Scrolling is built in.** `AdwPreferencesPage` and `AdwStatusPage` each contain their own `GtkScrolledWindow` (verified in the 1.9 templates) — put them directly in the dialog/window; wrapping one in another `ScrolledWindow` nests scrollers and breaks the outer one's natural-height measurement. For a custom `AdwDialog` that should size itself to its content, set `follows-content-size=True` on the dialog.

## Alert Dialog

`AdwAlertDialog` (1.5) replaces `AdwMessageDialog` and `GtkMessageDialog`. Heading names the action ("Delete Project?", not "Warning"); Cancel first, specific verb last.

```python
def show_delete_dialog(parent, item_name):
    dialog = Adw.AlertDialog(
        heading=f"Delete {item_name}?",
        body="This item will be permanently deleted. This cannot be undone."
    )
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("delete", "Delete")
    dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
    dialog.set_default_response("cancel")
    dialog.set_close_response("cancel")
    dialog.connect("response", on_delete_response)
    dialog.present(parent)
```

**Response contract** — who closes the dialog:

- A response button closes the dialog itself, then `response` fires with that button's ID. The handler does the work only; a `close()` inside it re-emits `response` with the close response.
- `close()`, Escape, and system close all emit `response` with the *close response* (`"cancel"` above) — put cancellation logic on that ID, and give every dialog an explicit `set_close_response`.
- Emitting `response` from code runs handlers but closes nothing — libadwaita closes from the button, not from the signal.
- The Enter path: `set_default_response("create")` makes that button the dialog's default widget; a `GtkEntry` in `extra-child` reaches it with `activates_default=True`. That is the whole wiring — an `activate` handler that duplicates the work fires twice.

## Boxed List Rows

| Row | For |
|-----|-----|
| `AdwActionRow` | Clickable row, prefix/suffix widgets |
| `AdwSwitchRow` | Toggle (1.4) |
| `AdwComboRow` | Dropdown; `enable-search` for long lists |
| `AdwEntryRow` | Text input (1.2); `apply` signal for explicit commit |
| `AdwSpinRow` | Numbers (1.4) |
| `AdwExpanderRow` | Collapsible group of sub-rows |
| `AdwButtonRow` | Full-width button in a list (1.6) |

```python
row = Adw.ActionRow(title="Account Settings", subtitle="Manage your account")
row.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
row.set_activatable(True)
row.connect("activated", lambda r: open_account_settings())

port_row = Adw.SpinRow.new_with_range(1, 65535, 1)
port_row.set_title("Port")
port_row.set_value(8080)
```

Standalone boxed list (outside preferences): `GtkListBox` with the `boxed-list` style class.

## View Switching (2–4 views)

```python
view_stack = Adw.ViewStack()
view_stack.add_titled_with_icon(page1, "overview", "Overview", "view-grid-symbolic")
view_stack.add_titled_with_icon(page2, "details", "Details", "view-list-symbolic")

view_switcher = Adw.ViewSwitcher(policy=Adw.ViewSwitcherPolicy.WIDE)
view_switcher.set_stack(view_stack)
header.set_title_widget(view_switcher)

# Bottom bar for narrow widths (see Breakpoints below to toggle)
switcher_bar = Adw.ViewSwitcherBar()
switcher_bar.set_stack(view_stack)
toolbar_view.add_bottom_bar(switcher_bar)
```

## Sidebar Navigation

`AdwNavigationSplitView` (1.4) holds sidebar + content as `AdwNavigationPage`s. For the sidebar itself, `AdwSidebar` (1.9) gives sections and items natively:

```python
sidebar = Adw.Sidebar()

section = Adw.SidebarSection(title="Favorites")
home = Adw.SidebarItem(title="Home", subtitle="All files")
home.set_icon_name("user-home-symbolic")
section.append(home)
sidebar.append(section)          # sections; SidebarSection.bind_model for dynamic items

# Selection: `selected` is a flat index across all sections; `selected-item` the object
sidebar.connect("notify::selected-item", lambda s, p: show(s.get_selected_item()))
# Activation (click, including re-clicking the selected item) arrives as a flat index
sidebar.connect("activated", lambda s, index: focus_content(s.get_item(index)))

# Context menu: one model for all items; per-item state via setup-menu
sidebar.set_menu_model(item_menu)             # Gio.Menu of e.g. "sidebar.rename"
def on_setup_menu(sb, item):                  # item is None when the menu closes
    if item is not None:
        rename_action.set_enabled(item.get_enabled())
sidebar.connect("setup-menu", on_setup_menu)

sidebar.set_placeholder(Adw.StatusPage(title="No Folders"))  # empty/filtered-out state

split_view = Adw.NavigationSplitView()
split_view.set_sidebar(Adw.NavigationPage(title="Files", child=sidebar))
split_view.set_content(Adw.NavigationPage(title="Details", child=content))
```

`mode=Adw.SidebarMode.PAGE` restyles it as boxed lists for the collapsed/narrow presentation.

Pre-1.9 / custom row layout: `GtkListBox` with the `navigation-sidebar` style class inside a `GtkScrolledWindow`.

To switch an `AdwViewStack` from a sidebar, use `AdwViewSwitcherSidebar` (1.9) instead of hand-wiring — it supports sections via `ViewStackPage:starts-section`/`section-title` and badges/unread dots.

## Toasts, Banner, Progress

```python
# Overlay wraps the window content once
toast_overlay = Adw.ToastOverlay()
toast_overlay.set_child(main_content)
self.set_content(toast_overlay)

# Toast with undo
toast = Adw.Toast(title="Item deleted")
toast.set_button_label("Undo")
toast.connect("button-clicked", on_undo_delete)
toast_overlay.add_toast(toast)

# Banner for persistent state - add as a top bar
banner = Adw.Banner(title="You are offline")
banner.set_button_label("Retry")
banner.connect("button-clicked", on_retry)
banner.set_revealed(True)
toolbar_view.add_top_bar(banner)

# Progress with count text
progress = Gtk.ProgressBar()
progress.set_fraction(13 / 31)
progress.set_text("Processing 13 of 31 items")
progress.set_show_text(True)
```

## Context Menus

`GtkPopoverMenu` from a `GioMenu` model, shown on right-click (`GtkGestureClick` with `button=3`):

```python
menu = Gio.Menu()
menu.append("Rename", "item.rename")
menu.append("Remove", "item.remove")

popover = Gtk.PopoverMenu.new_from_model(menu)
popover.set_parent(widget)
popover.set_has_arrow(False)

gesture = Gtk.GestureClick(button=3)
def on_pressed(g, n, x, y):
    rect = Gdk.Rectangle()
    rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
    popover.set_pointing_to(rect)
    popover.popup()
gesture.connect("pressed", on_pressed)
widget.add_controller(gesture)
```

## Search

Search bar slides from under the header; three activation routes come from this wiring — Ctrl+F is bound by `GtkSearchBar` itself once connected, the toggle button, and type-to-search via `set_key_capture_widget`:

```python
search_bar = Gtk.SearchBar()
search_entry = Gtk.SearchEntry(hexpand=True)
search_bar.set_child(search_entry)
search_bar.connect_entry(search_entry)
search_bar.set_key_capture_widget(window)   # type-to-search

search_button = Gtk.ToggleButton(icon_name="system-search-symbolic")
search_button.set_tooltip_text("Search")
header.pack_end(search_button)
search_bar.bind_property(
    "search-mode-enabled", search_button, "active",
    GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

toolbar_view.add_top_bar(search_bar)
```

Live filtering — swap a `GtkCustomFilter` on the `GtkFilterListModel`:

```python
def on_search_changed(entry):
    query = entry.get_text().lower()
    if not query:
        filter_model.set_filter(None)
        return
    filter_model.set_filter(Gtk.CustomFilter.new(lambda item: query in item.title.lower()))

search_entry.connect("search-changed", on_search_changed)
```

## Form Validation

Mark invalid rows with the `error` style class (valid ones can use `success`); the classes recolor the row using `--error-color`/`--success-color` automatically:

```python
def validate_name(row):
    ok = len(row.get_text()) >= 3
    if ok:
        row.remove_css_class("error")
        row.set_tooltip_text("")
    else:
        row.add_css_class("error")
        row.set_tooltip_text("Name must be at least 3 characters")
    return ok

name_row.connect("changed", lambda r: validate_name(r))
```

| Timing | Use when |
|--------|----------|
| On change | Format checks (email, URL), character limits |
| On focus out | Expensive/API checks |
| On submit | Final pass; focus the first invalid field |

## Selection Mode

Bulk actions use an explicit mode: a `selection-mode-symbolic` toggle in the header swaps the view's model between `Gtk.SingleSelection` and `Gtk.MultiSelection` and reveals a `GtkActionBar` (Select All / destructive action / Cancel). List/grid factory and model code: `developing-gtk-apps`.

## Primary Menu

Standard items in a final section; no Quit/Close item (windows have close buttons). Tooltip and accessible label: "Main Menu".

```python
menu = Gio.Menu()
# App-specific items first (optional)
menu.append("Import…", "app.import")

section = Gio.Menu()
section.append("Preferences", "app.preferences")
section.append("Keyboard Shortcuts", "app.shortcuts")
section.append("Help", "app.help")
section.append("About App Name", "app.about")
menu.append_section(None, section)

menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
menu_button.set_tooltip_text("Main Menu")
menu_button.set_menu_model(menu)
header.pack_end(menu_button)
```

3–12 items; group with sections, never nested submenus. Ellipsis (…) only on items needing further input.

## Shortcuts Dialog

`AdwShortcutsDialog` (1.8) — `GtkShortcutsWindow` and the `win.show-help-overlay` auto-wiring are deprecated (GTK 4.18); register your own action for the menu item:

```python
def show_shortcuts(win):
    dialog = Adw.ShortcutsDialog()
    section = Adw.ShortcutsSection(title="General")
    section.add(Adw.ShortcutsItem.new("Search", "<Control>f"))
    section.add(Adw.ShortcutsItem.new_from_action("Quit", "app.quit"))  # reads accel
    dialog.add(section)
    dialog.present(win)
```

## About Dialog

`AdwAboutDialog` (1.5) replaces `AdwAboutWindow`:

```python
about = Adw.AboutDialog(
    application_name="App Name",
    application_icon="com.example.AppName",
    version="1.0.0",
    developer_name="Developer Name",
    license_type=Gtk.License.GPL_3_0,
    website="https://example.com",
    issue_url="https://github.com/example/app/issues",
)
about.present(window)
```

## Multiline Text

`GtkTextView` in a `GtkScrolledWindow` with the `card` class to match boxed lists:

```python
text_view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR,
                         top_margin=12, bottom_margin=12,
                         left_margin=12, right_margin=12)
scrolled = Gtk.ScrolledWindow(child=text_view, min_content_height=100)
scrolled.add_css_class("card")
group.add(scrolled)  # inside an AdwPreferencesGroup
```

## Rich Text Colors (GtkTextTag)

`GtkTextTag` takes no CSS classes — its colors are RGBA properties (`foreground-rgba`, `background-rgba`, `underline-rgba`, …), so tagged text keeps its original colors when the theme flips to dark or the accent changes. Derive tag colors from the live theme and recompute on change:

```python
def retint_tags(view, tags):
    fg = view.get_color()                    # themed foreground of the TextView
    sm = Adw.StyleManager.get_default()
    accent = sm.get_accent_color_rgba()      # 1.6; matches var(--accent-color)
    tags["heading"].set_property("foreground-rgba", fg)
    tags["link"].set_property("foreground-rgba", accent)

sm = Adw.StyleManager.get_default()
sm.connect("notify::dark", lambda *_: retint_tags(view, tags))
sm.connect("notify::accent-color-rgba", lambda *_: retint_tags(view, tags))
retint_tags(view, tags)                      # once at startup too
```

Structural tag properties (`weight`, `style`, `scale`, `underline`, `family="monospace"`) are theme-independent and can be set once.

## File Dialogs

`GtkFileDialog` (4.10, async) replaces `GtkFileChooserDialog`/`Native`. Dismissal raises `GLib.Error` with `Gtk.DialogError.DISMISSED`:

```python
def on_open_clicked(button):
    dialog = Gtk.FileDialog(title="Open Document")

    text_filter = Gtk.FileFilter()
    text_filter.set_name("Text Files")
    text_filter.add_mime_type("text/plain")
    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(text_filter)
    dialog.set_filters(filters)
    dialog.set_default_filter(text_filter)

    dialog.open(window, None, on_open_response)

def on_open_response(dialog, result):
    try:
        file = dialog.open_finish(result)
        load(file.get_path())
    except GLib.Error as e:
        if e.code != Gtk.DialogError.DISMISSED:
            show_error_toast(f"Could not open file: {e.message}")

# Saving: Gtk.FileDialog(title=..., initial_name="Untitled.txt")
#         dialog.save(window, None, cb) / dialog.save_finish(result)
# Folders: dialog.select_folder(...) / select_folder_finish(result)
```

## Dark/Light Mode

Apps follow the system preference with no code. To offer an override:

```python
style_manager = Adw.StyleManager.get_default()
style_manager.get_dark()  # current effective mode
style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)   # or FORCE_LIGHT
style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)      # back to system

# React to changes for custom-drawn elements
style_manager.connect("notify::dark", lambda sm, p: redraw(sm.get_dark()))
```

## Breakpoints (Adaptive Layout)

`AdwBreakpoint` (1.4) is the whole adaptive story — setters flip properties at a width, replacing the deprecated `AdwLeaflet`/`AdwFlap`/`AdwSqueezer`:

```python
# Collapse sidebar on narrow windows
bp = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 600sp"))
bp.add_setter(split_view, "collapsed", True)
window.add_breakpoint(bp)

# Move view switcher to a bottom bar when narrow
bp = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 550sp"))
bp.add_setter(header, "title-widget", None)
bp.add_setter(switcher_bar, "reveal", True)
window.add_breakpoint(bp)
```

Units are `sp` (scale-independent pixels, tracks text scaling). Width constraints on large screens: `Adw.Clamp` / `Adw.ClampScrollable` (`maximum_size` default 600, `tightening_threshold`).

## Typography

Style classes instead of font CSS:

| Class | Use for |
|-------|---------|
| `title-1` … `title-4` | Display headings, welcome screens |
| `heading` | Section headings, group titles |
| `body` | Default text, descriptions |
| `caption` / `caption-heading` | Secondary info, timestamps |
| `monospace` | Code, technical values |
| `dimmed` | De-emphasized text (`.dim-label` is the deprecated alias) |
| `numeric` | Tabular figures |

## Writing Style

| Context | Style | Example |
|---------|-------|---------|
| Button labels | Header caps, imperative verb | "Save Document" |
| Menu items | Header caps | "Find and Replace" |
| Checkbox/switch labels | Sentence caps | "Show notifications" |
| Descriptions | Sentence caps, no period | "Changes take effect after restart" |
| Toast messages | Short, sentence-style | "Document saved" |
| Dialog headings | Name the action | "Delete Project?" not "Warning" |

**Header capitalization:** capitalize words of 4+ letters, all verbs and nouns of any length, first and last words, both parts of hyphenated words ("Self-Test"). Avoid "you"/"my" (use "your" if possession is needed); avoid Latin abbreviations ("e.g.") — screen readers stumble on them.

## Spacing

Libadwaita widgets carry their own spacing — add margins only on hand-built boxes: 12px between sections, 6px between related items.

## Color Reference

CSS variables via `var(--…)` — the `@define-color` named colors (`@accent_color`) are the deprecated pre-1.6 form:

| Variable | Use |
|----------|-----|
| `--accent-color` | Standalone accent (text/icons on neutral bg) |
| `--accent-bg-color` / `--accent-fg-color` | Accent fills and text on them |
| `--destructive-color` (+`-bg`/`-fg`) | Destructive actions |
| `--success-color`, `--warning-color`, `--error-color` | State colors (pair with `success`/`warning`/`error` classes) |
| `--window-bg-color` / `--view-bg-color` | Window vs content-view backgrounds |
| `--headerbar-bg-color` | Header bar |
| `--card-bg-color` | Cards / boxed lists |
| `--monospace-font-family`, `--document-font-family` | System fonts (1.7) |

```css
my-widget { background-color: var(--accent-bg-color); color: var(--accent-fg-color); }
```

## Standard Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+W / Ctrl+Q | Close window / quit app |
| Ctrl+N | New item |
| Ctrl+S | Save |
| Ctrl+Z / Ctrl+Shift+Z | Undo / redo |
| Ctrl+F | Search |
| Escape | Close dialog/popover, cancel, leave search |
| F1 | Help |

## Accessibility Checks

```bash
GTK_THEME=Adwaita:hc ./myapp     # high contrast
orca & ./myapp                    # screen reader
# 200% text scaling: GNOME Settings > Accessibility
# Keyboard only: full app via Tab/Enter/Space/Escape
```

Icon-only buttons and meaningful images need accessible labels (PyGObject override of the varargs C API):

```python
button.update_property([Gtk.AccessibleProperty.LABEL], ["Add new item"])
```

## External Resources

- [GNOME HIG](https://developer.gnome.org/hig/)
- [Libadwaita docs](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/) — including the CSS variables page
- [GNOME Icon Library](https://apps.gnome.org/IconLibrary/) — bundle any icon not in the system theme
- [GTK 4 docs](https://docs.gtk.org/gtk4/)
