# Application services

Use this reference for settings, resources, files, D-Bus, portals, notifications, background work, session behavior, and XDG storage.

## GSettings

Use GSettings for user preferences and small pieces of durable application state that need schema, defaults, change notification, and desktop integration.

- Keep the schema ID, path, application ID, and installation layout consistent.
- Name keys for meaning, not the current widget.
- Choose stable serialized types. Changing a key type requires a migration or a new key.
- Put valid defaults in the schema and document value ranges or choices there.
- Bind simple preferences to properties. Use a change handler when the setting triggers work or needs translation into domain state.
- Store documents, histories, caches, or large structured state in the proper XDG location instead of GSettings.
- Compile schemas during the build and test with an isolated schema directory or memory backend.

Treat existing keys as a data contract. Preserve old values when renaming or replacing them, unless the user accepts a reset.

## GResource

Bundle UI templates, CSS, icons, menus, and small static data in GResource when they belong to the application binary or installed resource bundle.

- Keep one clear resource prefix derived from the application ID.
- List generated Blueprint output rather than uncompiled source where the build system requires it.
- Register resources before templates, icons, or CSS load.
- Verify every resource path at build time where possible.
- Use file paths for user content and large mutable data. Resources are immutable application assets.

## Files and URIs

Use GIO types and async APIs for files and streams.

- Work with `gio::File` when the input can be a portal document, remote URI, or non-local backend.
- Do not assume every file has a native filesystem path.
- Use `GtkFileDialog` or the current toolkit replacement supported by the project's version floor.
- Preserve atomic-save behavior: write a replacement safely, flush it, then replace the destination.
- Track external changes with `GFileMonitor` only when the product needs them. Suppress reactions to the application's own write through explicit generation or content checks.
- Surface portal or permission failure as an actionable state.

Use the XDG user directories and GLib helpers for configuration, data, state, cache, and runtime files. Never place mutable application state beside the executable.

## D-Bus

Use D-Bus for stable process or desktop interfaces, not as an internal event bus.

- Define interfaces in XML and treat object path, interface name, method names, signals, properties, and signatures as public contracts.
- Keep service activation aligned with the application ID and executable.
- Validate each incoming argument before invoking domain logic.
- Return typed D-Bus errors instead of leaking implementation messages.
- Keep method handlers asynchronous when they perform I/O or long work.
- Subscribe and unsubscribe with the consumer lifecycle.
- Add contract tests for signatures and reply shapes.

Use application actions for commands within the process. Use D-Bus when another process needs a supported interface.

## Portals and sandbox behavior

Prefer XDG Desktop Portal interfaces for sandbox-safe desktop services:

- file and directory selection;
- opening URIs;
- notifications;
- screenshots and screen casting;
- secrets and credentials through an appropriate service;
- inhibit and background requests;
- settings such as color scheme;
- global shortcuts when the current portal and desktop support the required workflow.

Portal calls are asynchronous and user-mediated. Design cancellation, denial, missing implementation, and partial desktop support as normal outcomes.

Test the packaged application. A host build can accidentally pass because it has broader filesystem and bus access.

## Notifications

Use application notifications for events that matter when the window is hidden or the app is not focused. Use in-window feedback for actions performed in a visible window.

- Give a notification a stable ID when updates should replace an earlier one.
- Route buttons through application actions.
- Keep notification text short and free of technical diagnostics.
- Withdraw obsolete notifications when the underlying state clears.
- Respect user attention. Progress belongs in a notification only when background progress is useful outside the app.

## Background and session behavior

Linux desktops place limits on silent background execution. Keep the lifecycle visible and tied to a supported capability.

- Use `hold()` only while a declared background operation needs the process.
- Pair every hold with release, including errors and cancellation.
- Use portal background requests in Flatpak when needed.
- Use a systemd user service only when the product contract genuinely includes a service. Document activation, restart, logs, and shutdown.
- Use desktop autostart only when the user explicitly enables that behavior.

Wayland clients cannot freely position windows, inspect global window coordinates, force focus, remain above other windows, hide from shell surfaces, or intercept arbitrary global input. A supported portal, compositor protocol, or desktop extension must provide such behavior. Keep the app useful when that integration is absent.

## Primary references

- [GSettings](https://docs.gtk.org/gio/class.Settings.html)
- [GResource](https://docs.gtk.org/gio/struct.Resource.html)
- [Gio.DBusConnection](https://docs.gtk.org/gio/class.DBusConnection.html)
- [XDG Desktop Portal](https://flatpak.github.io/xdg-desktop-portal/)
- [XDG base directories](https://specifications.freedesktop.org/basedir-spec/latest/)
