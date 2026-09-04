---
name: linux-gtk-development
description: Build, review, debug, profile, test, and package Rust applications that use GTK 4 or libadwaita on Linux. Use for gtk4-rs architecture, GObject lifecycle, GNOME HIG work, accessibility, Wayland and portal integration, D-Bus, performance, Flatpak, Flathub eligibility, AppStream, or distribution packaging. Use a toolkit-specific skill instead when the application does not use GTK.
---

# Linux GTK development

Build Linux desktop software with Rust, GTK 4, and libadwaita. The repository defines the product and dependency contracts. Use current GNOME, GTK, gtk-rs, Flatpak, and freedesktop documentation for platform behavior.

## Start with the repository

Read the applicable `AGENTS.md` and project documentation. Trace the affected behavior to its owning code and validation path. Inspect installed artifacts when packaging, resources, activation, or runtime differences affect the task.

Establish the relevant facts below; revisit them when the change crosses another boundary:

- the Cargo workspace boundary and the package that owns the GTK binary;
- exact `gtk4`, `glib`, `gio`, and `libadwaita` versions, Cargo features, and system-library minimums;
- whether the project builds widgets in Rust, XML templates, Blueprint files, or a mix;
- the state and command boundary between GTK presentation code and domain code;
- the build system, resource compiler, schema compiler, translation setup, and package manifests;
- the application ID, executable name, D-Bus name, desktop file, icon name, AppStream ID, GSettings prefix, and Flatpak ID;
- the current validation commands and any display, native-library, or sandbox prerequisites.

Inspect the current type, enum, trait, and feature definition before treating a compiler error as a dependency problem. Keep the existing GTK, libadwaita, Rust, and runtime minimums unless the requested behavior needs a newer version and the user accepts that compatibility change.

## Read the relevant references

Load every reference that matches the task. A feature often crosses more than one branch.

- [Rust and gtk-rs architecture](references/rust-gtk.md): Cargo contracts, application lifecycle, GObject subclasses, ownership, properties, signals, actions, models, templates, async work, and error handling.
- [Blueprint UI and Rust](references/blueprint-ui.md): when to use Blueprint, Workbench-to-application transfer, composite templates, build integration, resources, translation, version control, and current gtk-rs constraints.
- [Application services](references/application-services.md): GSettings, resources, files, D-Bus, portals, notifications, background work, session behavior, and XDG storage.
- [GNOME UI design](references/gnome-ui.md): HIG principles, information architecture, adaptive layout, controls, feedback, styling, motion, and writing.
- [Libadwaita and Adwaita Demo](references/libadwaita-adwaita-demo.md): version gates, current widget composition, source-backed examples, deprecated API replacements, and traps caused by older GTK or libadwaita designs.
- [Interaction and accessibility](references/interaction-accessibility.md): keyboard, focus, pointer and touch, drag and drop, selection, shortcuts, AT-SPI, screen readers, high contrast, large text, and custom widgets.
- [Performance, debugging, and testing](references/performance-and-testing.md): GTK Inspector, Sysprof, main-loop stalls, rendering, memory, logging, regression tests, display-backed tests, and CI.
- [Internationalization](references/internationalization.md): gettext, resources, translator context, plurals, formatting, expansion, right-to-left layouts, and localized desktop metadata.
- [Packaging and release](references/packaging.md): installed layout, AppStream, desktop files, icons, Flatpak, self-hosted repositories, release bundles, the Flathub eligibility gate, native packages, sandbox permissions, and distribution compatibility.

## Work from contracts

Keep these contracts explicit while designing or reviewing a change:

- Rust and Cargo control language and crate availability.
- GTK and libadwaita control widget behavior, lifecycle, rendering, and supported APIs.
- The GNOME HIG controls GNOME-facing design decisions.
- Wayland controls what a client can know or request about windows and global input.
- Portals and D-Bus interfaces control sandbox-safe desktop integration.
- AppStream, desktop-entry, icon-theme, XDG, and Flatpak specifications control distribution metadata.
- The product's domain model and public interfaces control policy. GTK presents that policy; it does not invent a second copy.

Use installed GIR data, crate source, generated documentation, and official specifications when versions or signatures matter. Search current source before renaming an action, property, signal, resource path, schema key, application ID, or wire type.

## Implementation rules

- Keep every GTK object on the thread that owns the GLib main context. Worker tasks return owned, thread-safe data to that context.
- Keep signal handlers, action callbacks, list factories, snapshot functions, and frame callbacks short. Move blocking I/O and CPU-heavy work away from the main loop.
- Release interior-mutability borrows before code that can emit signals, change properties, mutate models, present UI, or re-enter application code.
- Model commands as actions when menus, buttons, shortcuts, notifications, or D-Bus activation can invoke the same behavior.
- Use `GListModel` and GTK list widgets for dynamic collections. Preserve stable identity, selection, focus, and scroll position during updates.
- Tie async work to cancellation and freshness. Ignore results for disposed views, replaced selections, or superseded requests.
- Use libadwaita patterns and semantic styling before custom CSS. Keep light, dark, and high-contrast modes working.
- Give every user task a keyboard path. Add accessible names and relationships where GTK cannot infer them.
- Design for Wayland. Use portals or compositor protocols for privileged integration. Present unavailable capabilities honestly in the UI.
- Keep application identity consistent across code, resources, metadata, settings, D-Bus, and packages.
- Request only the sandbox permissions required by tested behavior.

## Validation

Run the repository's required checks and select tests for the affected behavior. For a conventional Rust GTK workspace, choose the relevant commands from:

```bash
cargo fmt --all --check
cargo check --manifest-path path/to/Cargo.toml
cargo test --manifest-path path/to/Cargo.toml --all-targets
cargo clippy --manifest-path path/to/Cargo.toml --all-targets -- -D warnings
git diff --check
```

Add the checks that match the change:

- compile resources and GSettings schemas;
- validate desktop and AppStream metadata;
- build and run the Flatpak without build-time network access;
- run the linters for the target package repository;
- exercise light, dark, high-contrast, large-text, narrow-window, and translated layouts;
- complete the affected task with keyboard only and with a screen reader when accessibility changed;
- inspect loading, empty, populated, disabled, error, offline, destructive, and long-content states;
- repeat the same trace or benchmark before and after a performance change.

Render and inspect the affected states of every changed view. Broaden coverage for shared styles, resources, packaging, or release work. A successful compile does not validate layout, focus, accessibility, or interaction. When a required runtime or display is unavailable, complete source checks and identify the visual or interaction evidence still missing.

## Handoff

Lead with the result. Name the files and contracts changed, the commands that passed, and the user-visible checks performed. Separate confirmed evidence from residual risk. State any untested distribution, compositor, toolkit version, assistive technology, hardware path, or package format.
