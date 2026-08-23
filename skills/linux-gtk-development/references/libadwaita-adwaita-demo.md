# Libadwaita and Adwaita Demo

Use this reference for libadwaita widget selection, adaptive composition, dialogs, navigation, preferences, feedback, and styling. It also covers older patterns that remain common in tutorials and generated code.

## Set the version floor first

Libadwaita API availability depends on both the system library and the Cargo feature selected for `libadwaita-rs`.

1. Read the `libadwaita` dependency and features in `Cargo.toml` and `Cargo.lock`.
2. Check the installed library with `pkg-config --modversion libadwaita-1`.
3. Open the matching [libadwaita API version](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/) and [libadwaita-rs documentation](https://world.pages.gitlab.gnome.org/Rust/libadwaita-rs/stable/latest/docs/libadwaita/).
4. Check the `since` and `deprecated` annotations for every widget, method, property, and CSS feature used by the change.
5. Select an Adwaita Demo tag or branch that matches the application's floor before copying a pattern.

The [Adwaita Demo source](https://gitlab.gnome.org/GNOME/libadwaita/-/tree/main/demo) tracks libadwaita development. Its `main` branch can use APIs that the latest stable release or the application cannot use. Treat the demo as an implementation reference after version matching, not as proof that an API exists in the current project.

In Rust, a Cargo feature such as `v1_5` exposes methods introduced in libadwaita 1.5. It does not install that system library. The build still needs a compatible `libadwaita-1` package.

## Current application shell

Adwaita Demo uses `AdwApplicationWindow` and sets its `content` property. A `GtkHeaderBar` passed through the old `GtkWindow:titlebar` model is not the current libadwaita shell.

For a single-page window, compose:

```text
AdwApplicationWindow
└── AdwToolbarView
    ├── top: AdwHeaderBar
    ├── top: GtkSearchBar, when search belongs above the content
    └── content: application view
```

The Rust object graph has the same shape:

```rust
use adw::prelude::*;

let toolbar = adw::ToolbarView::new();
toolbar.add_top_bar(&adw::HeaderBar::new());
toolbar.set_content(Some(&content));
window.set_content(Some(&toolbar));
```

Match the imported crate name used by the project. Some repositories alias `libadwaita` as `adw` in `Cargo.toml`; others import it under its package name.

`AdwToolbarView` owns top and bottom bars. This matters for header-bar integration, undershoot shadows, fullscreen reveal behavior, split views, view-switcher bars, tab bars, search bars, and action bars. Do not put these bars into an ordinary vertical box unless the design needs them to scroll as content.

Source examples:

- [Adwaita Demo main window](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/adw-demo-window.ui)
- [AdwToolbarView API](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/class.ToolbarView.html)
- [AdwWindow API](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/class.Window.html)

## Main window pattern from Adwaita Demo

The demo's main window uses this hierarchy:

```text
AdwApplicationWindow
└── AdwToastOverlay
    └── AdwNavigationSplitView
        ├── sidebar: AdwNavigationPage
        │   └── AdwToolbarView
        │       ├── AdwHeaderBar
        │       ├── GtkSearchBar
        │       └── AdwSidebar
        └── content: AdwNavigationPage
            └── page content
```

One breakpoint performs related changes together: it collapses the split view and changes the sidebar from sidebar presentation to page presentation. Search uses a `GtkSearchBar` as a toolbar top bar, binds its search mode to the header button, and sets the window as its key-capture widget. An `AdwStatusPage` supplies the no-results state.

Reuse the composition, not the demo's exact breakpoint value or newest sidebar type. Setting only `collapsed = true` can leave a navigation sidebar styled for the desktop after it becomes a narrow page. Copying the visual shell alone can omit search key capture, empty search state, and navigation activation.

`AdwSidebar` is newer than the original split-view API. If the application floor does not provide it, use the sidebar pattern supported by that floor while keeping the same `AdwNavigationPage` and breakpoint structure.

## Navigation split view

`AdwNavigationSplitView` models sidebar and content navigation. Both children are `AdwNavigationPage`, not arbitrary widgets. Each page owns its title, optional tag, and child. A page normally contains its own `AdwToolbarView` and `AdwHeaderBar` so title and back-button behavior come from navigation state.

The demo's [navigation split view example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/split-views/adw-navigation-split-view-demo-dialog.ui) shows:

```xml
<object class="AdwBreakpoint">
  <condition>max-width: 400sp</condition>
  <setter object="split_view" property="collapsed">True</setter>
</object>

<object class="AdwNavigationSplitView" id="split_view">
  <property name="sidebar">
    <object class="AdwNavigationPage">
      <property name="title">Sidebar</property>
      <property name="tag">sidebar</property>
      <!-- AdwToolbarView and sidebar content -->
    </object>
  </property>
  <property name="content">
    <object class="AdwNavigationPage">
      <property name="title">Content</property>
      <property name="tag">content</property>
      <!-- AdwToolbarView and content -->
    </object>
  </property>
</object>
```

The example opens content through the detailed action `navigation.push` with target `'content'`. It does not manually show and hide pages or build a separate back button. `AdwHeaderBar` reads the page title and supplies navigation behavior.

Common errors:

- passing a `GtkBox` directly as `sidebar` or `content` instead of wrapping it in `AdwNavigationPage`;
- setting header titles independently from page titles;
- keeping custom back-button stacks beside the navigation stack;
- switching child widgets manually when the `navigation.push` and `navigation.pop` actions already express the command;
- collapsing without a breakpoint, which leaves minimum-size behavior and related presentation changes scattered through callbacks.

## Overlay split view

Use `AdwOverlaySplitView` for a utility pane that overlays content when collapsed. It does not turn the sidebar into navigation history.

The demo's [overlay split view example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/split-views/adw-overlay-split-view-demo-dialog.ui) places one `AdwToolbarView` around the split view, keeps the header shared, and binds a header toggle to `show-sidebar` in both directions. Its breakpoint changes `collapsed`; the toggle continues to control whether the overlaid pane is visible.

This differs from `AdwNavigationSplitView`, where sidebar and content are navigation pages with separate page headers. Pick the type from the pane's meaning:

- choose navigation split view when selecting a sidebar item navigates to content;
- choose overlay split view when the pane is a utility that can appear beside or over the same content.

Do not choose between them based only on whether the wide layout looks like a sidebar. They look similar when expanded but have different narrow behavior.

## View switcher

The demo's [view switcher example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/view-switcher/adw-view-switcher-demo-dialog.ui) uses one `AdwViewStack`, one header `AdwViewSwitcher`, and one bottom `AdwViewSwitcherBar`.

At the narrow breakpoint, it reveals the bottom bar and clears the header bar's `title-widget`. Both switchers point to the same stack. The app does not maintain two copies of the selected page.

Use this pattern for a small set of peer views. Use navigation view for drill-down, split view for sidebar and detail, and tab view for user-managed documents or sessions. `AdwViewSwitcherTitle` belongs to the older adaptive design and is deprecated from libadwaita 1.4.

## Adaptive breakpoints

`AdwBreakpoint` applies property setters while its condition matches and restores the previous values when it no longer matches. It can belong to `AdwWindow`, `AdwApplicationWindow`, `AdwDialog`, or `AdwBreakpointBin` at supported versions.

Use setters for property changes that form one adaptive transition. Use `apply` and `unapply` signals only when a property setter cannot express the layout change.

Breakpoints remove the normal minimum-size constraint from their containing adaptive surface. Set a tested `width-request` and `height-request` that describe the smallest supported layout. The demo dialogs do this before adding their breakpoint.

Use scalable length units supported by the application's libadwaita floor. Do not copy a condition such as `400sp` from `main` without checking when that syntax became available.

The [adaptive layouts guide](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/adaptive-layouts.html) is authoritative for current composition. The [breakpoint migration guide](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/migrating-to-breakpoints.html) covers replacements for the earlier leaflet, flap, and squeezer designs.

## Dialogs

Libadwaita 1.5 introduced adaptive `AdwDialog` and dialog replacements. Libadwaita 1.6 deprecated the older window-based types.

| Older design | Current design | Availability and change |
|---|---|---|
| `AdwMessageDialog` | `AdwAlertDialog` | Alert dialog since 1.5; old type deprecated in 1.6 |
| `AdwPreferencesWindow` | `AdwPreferencesDialog` | Dialog since 1.5; old type deprecated in 1.6 |
| `AdwAboutWindow` | `AdwAboutDialog` | Dialog since 1.5; old type deprecated in 1.6 |
| custom transient `GtkWindow` used as a dialog | `AdwDialog` or a specific dialog subclass | Present against a parent widget; let libadwaita choose floating or bottom-sheet presentation |

An `AdwDialog` is not a `GtkWindow`. Do not set `transient-for`, call a nested `run()` loop, or destroy it as if it were a GTK 3 dialog. Present it with a parent widget. The parent surface must use `AdwWindow` or `AdwApplicationWindow` for embedded adaptive presentation.

The [adaptive-dialog migration guide](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/migrating-to-adaptive-dialogs.html) also requires moving title bars and action bars into `AdwToolbarView` when converting the parent window.

### Alert dialog in Rust

Adwaita Demo's [alert example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/alerts/adw-demo-page-alerts.c) defines response IDs, marks discard as destructive and save as suggested, sets safe close behavior, and uses the async choose API.

The equivalent gtk-rs shape for a project with the `v1_5` feature is:

```rust
use adw::prelude::*;

let dialog = adw::AlertDialog::new(
    Some("Save Changes?"),
    Some("Open document contains unsaved changes."),
);
dialog.add_responses(&[
    ("cancel", "_Cancel"),
    ("discard", "_Discard"),
    ("save", "_Save"),
]);
dialog.set_response_appearance("discard", adw::ResponseAppearance::Destructive);
dialog.set_response_appearance("save", adw::ResponseAppearance::Suggested);
dialog.set_default_response(Some("save"));
dialog.set_close_response("cancel");

let response = dialog.choose_future(Some(parent)).await;
match response.as_str() {
    "save" => save_document().await,
    "discard" => discard_changes(),
    _ => {}
}
```

This example matches the current stable binding signatures. Check the locked `libadwaita-rs` documentation when the project uses an older release. The constructor and async helper remain unavailable unless the selected crate features include their libadwaita version.

The response ID drives behavior. Closing maps to the safe response, while the async result replaces a nested modal loop.

### Preferences dialog

Adwaita Demo's [preferences template](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/adw-demo-preferences-dialog.ui) subclasses `AdwPreferencesDialog`, enables search explicitly, adds pages and groups, can show a page banner, and uses current row types. Its [implementation](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/adw-demo-preferences-dialog.c) pushes `AdwNavigationPage` subpages and adds toasts through the dialog.

`AdwPreferencesDialog` defaults `search-enabled` to false. Older `AdwPreferencesWindow` examples can lead agents to assume search is on. Enable it only when the number and structure of preferences make search useful.

Present preferences with `dialog.present(Some(parent))`. Do not create a second application window for preferences unless the product explicitly requires a persistent independent window and accepts the loss of adaptive-dialog behavior.

## Toasts and banners

Adwaita Demo places one `AdwToastOverlay` high enough in the main content tree for page-level features to find it. A toast is then independent of the individual page's widget layout.

The [toast example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/toasts/adw-demo-page-toasts.c) stores the active Undo toast. Repeated deletions update its title and add it again to reset the timeout instead of creating a queue of stale Undo actions. The dismissed signal clears stored state and disables actions that no longer apply.

Use this pattern when repeated operations share one reversible batch. Use separate toasts when each event has a distinct action or consequence.

The [banner example](https://gitlab.gnome.org/GNOME/libadwaita/-/blob/main/demo/pages/banners/adw-demo-page-banners.ui) keeps persistent contextual information in the content surface, binds `revealed` and `title` to state, and routes its button through an action. Use a banner for an ongoing condition such as offline mode or unsaved data. A toast can disappear before the user understands or resolves such a condition.

## Styling and CSS

Use documented style classes and CSS variables for the application's version floor.

- Libadwaita 1.6 introduced standard CSS variables such as `--accent-bg-color`, `--window-bg-color`, and foreground pairs.
- Compatibility named colors use older GTK syntax and do not follow application overrides. New styling at a 1.6 or newer floor should use CSS variables.
- Pair semantic background and foreground variables. Do not assume white text has enough contrast on every accent or status color.
- Use `.suggested-action`, `.destructive-action`, `.pill`, `.circular`, `.flat`, `.card`, and typography classes only for the meanings documented by libadwaita.
- Keep CSS selectors local and independent of private widget descendants.
- Let standard widgets follow system accent, light, dark, and high-contrast settings.

Read [styles and appearance](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/styles-and-appearance.html) and [CSS variables](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/css-variables.html) for the matched release.

## Deprecated designs and current replacements

Check the matched API docs before applying this table. The replacement can require a higher minimum version.

| Older or unsupported pattern | Current direction |
|---|---|
| `GtkWindow:titlebar` as the main libadwaita shell | `AdwWindow` or `AdwApplicationWindow` with `AdwToolbarView` and `AdwHeaderBar` |
| `AdwLeaflet` | `AdwNavigationView` or `AdwNavigationSplitView`, depending on information structure |
| `AdwFlap` | `AdwOverlaySplitView` for a utility pane or `AdwNavigationSplitView` for navigation |
| `AdwSqueezer` | `AdwBreakpoint` property changes or a view-switcher pattern |
| `AdwViewSwitcherTitle` | `AdwWindowTitle` plus a header `AdwViewSwitcher` and narrow `AdwViewSwitcherBar` |
| manual width callbacks that rebuild the widget tree | `AdwBreakpoint` setters and adaptive containers |
| `AdwMessageDialog` | `AdwAlertDialog` |
| `AdwPreferencesWindow` | `AdwPreferencesDialog` |
| `AdwAboutWindow` | `AdwAboutDialog` |
| GTK 3 `GtkDialog::run()` patterns | async `present`, `choose`, or `choose_future` behavior |
| `GtkFileChooserDialog` on a GTK 4.10 or newer floor | `GtkFileDialog` async API |
| fixed `@theme_*` colors in new libadwaita 1.6 or newer CSS | documented libadwaita CSS variables and semantic style classes |

Do not perform a mechanical rename when the object model changed. Window-based dialogs become adaptive widgets, split-view children become navigation pages, and breakpoints restore property state automatically. The migration must update ownership, presentation, focus, and async control flow as well as type names.

## Review checklist

Before accepting libadwaita code, confirm:

- every API exists at the Cargo and system-library floor;
- every deprecated symbol has a supported replacement or a named compatibility reason;
- the window uses `content` and `AdwToolbarView` where libadwaita integration needs them;
- navigation pages own titles and tags;
- breakpoints change all related properties and preserve state when they unapply;
- the smallest supported size is explicit and tested;
- dialog control flow is async and has a safe close response;
- preferences search is an explicit choice;
- persistent state uses a banner and transient events use toasts;
- repeated Undo behavior does not produce stale actions;
- CSS uses classes and variables available at the declared floor;
- the view works in light, dark, high contrast, large text, and narrow layout;
- examples copied from Adwaita Demo came from a compatible tag or were adapted with documented version checks.

## Primary sources

- [Libadwaita documentation index](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/)
- [Latest stable libadwaita API](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/)
- [Libadwaita-rs API](https://world.pages.gitlab.gnome.org/Rust/libadwaita-rs/stable/latest/docs/libadwaita/)
- [Adwaita Demo source](https://gitlab.gnome.org/GNOME/libadwaita/-/tree/main/demo)
- [Adaptive layouts](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/adaptive-layouts.html)
- [Migrating to breakpoints](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/migrating-to-breakpoints.html)
- [Migrating to adaptive dialogs](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/migrating-to-adaptive-dialogs.html)
- [Styles and appearance](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/styles-and-appearance.html)
- [CSS variables](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/css-variables.html)
