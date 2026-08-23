# Rust and gtk-rs architecture

Use this reference for Rust APIs, application structure, GObject lifecycle, ownership, models, templates, actions, async work, and compile failures.

## Resolve the version contract

Read the workspace and package manifests plus `Cargo.lock`. Record the versions and features of `gtk4`, `glib`, `gio`, `gdk4`, `gsk4`, `pango`, and `libadwaita` where present. gtk-rs crates in one dependency graph should come from a compatible release family.

Cargo features such as `v4_12` or `v1_5` expose APIs from that system-library version. The host may have a newer library than the application supports. Use the project's feature floor when choosing an API.

Useful checks include:

```bash
cargo tree -p gtk4
cargo tree -p libadwaita
pkg-config --modversion gtk4
pkg-config --modversion libadwaita-1
```

Match online documentation to the locked crate release. When a signature remains unclear, inspect crate source in the Cargo registry and the installed GIR file. Compile a minimal use site before writing a larger change.

## Diagnose gtk-rs compiler failures

Start from the first meaningful compiler error.

- A missing method can mean the trait is not imported, the Cargo feature is below the API's introduction version, the receiver type is wrong, or the method belongs to another gtk-rs release family.
- Multiple applicable methods usually need a trait-qualified call. Read every candidate before selecting one.
- `IsA<T>` failures often mean the new API uses a different base type or an asynchronous object that no longer subclasses an older dialog class.
- A closure that fails `Send` probably captured a GTK object. Move plain data across the thread boundary and resolve widgets again on the main context.
- Borrow and move failures around callbacks are lifecycle design feedback. Decide which object owns the handler and how long every capture must live before adding clones.
- Variant failures require an exact GVariant type. Check both the Rust tuple shape and the D-Bus or action signature.

Dependency changes are a last step, not the first response.

## Application lifecycle

`gio::Application` and `gtk4::Application` provide process uniqueness, activation, open handling, actions, and D-Bus integration.

- Construct the application with its final application ID and required flags.
- Register actions, accelerators, resources, settings, and process-wide services during startup.
- Chain parent startup behavior when subclassing.
- Reuse and present the existing primary window during activation. Repeated activation should not create duplicate windows by accident.
- Handle file arguments through the application's open contract when the app is a file handler.
- Save durable state through explicit settings or application logic. Shutdown is not guaranteed after a crash or forced termination.
- Use `hold()` and `release()` only for a named background lifecycle. Balance every hold on success, failure, and cancellation.

Keep application, window, and view responsibilities separate. The application owns process-wide actions and services. A window owns window actions and presentation state. Reusable views own only their local behavior.

## GObject subclasses

Use a GObject subclass when GTK must observe identity, properties, signals, interfaces, list-model membership, or template children. Use a normal Rust struct or enum for domain data that does not need GObject behavior.

A gtk-rs subclass has two halves:

- the implementation struct in an `imp` module stores state and implements `ObjectSubclass` plus parent-class traits;
- the public wrapper exposes the GObject type and its safe application-facing methods.

Choose the parent type for required behavior, not convenience. Declare implemented interfaces explicitly. Keep subclass initialization, constructed behavior, and disposal responsibilities easy to locate.

Interior mutability is normal inside an implementation struct because GObject methods usually receive shared references. Choose each cell by access pattern:

- `Cell<T>` for small `Copy` values;
- `RefCell<T>` for main-thread state with runtime borrow checking;
- `OnceCell<T>` for set-once state such as template children or services;
- atomics or locks only for state that truly crosses threads.

Do not keep a `RefCell` borrow alive while calling code that can re-enter the object. Copy or take the required data, drop the borrow, then emit signals or update GTK.

## Ownership, captures, and disposal

Draw the ownership chain for long-lived callbacks. A strong capture from child to parent can form a cycle because the parent already owns the child.

- Use a weak capture when the callback should stop after the target is gone.
- Use a strong capture when the callback is part of the target's ownership and cannot create a cycle.
- Use an owned capture for plain immutable data that the callback needs independently.
- Treat `glib::clone!` as capture syntax. It does not choose the correct lifetime for you.
- Store handler IDs when the signal source can outlive the consumer, then disconnect them during disposal.
- Cancel futures, timeouts, file monitors, subscriptions, and workers during teardown.
- Make disposal idempotent and tolerate callbacks that were already queued.

Never use `unsafe` to bypass a GTK thread or lifetime rule without a documented platform contract and focused tests.

## Properties and bindings

Properties expose observable state to templates, bindings, settings, accessibility, and other GObjects.

- Use stable names and types. A property rename is a public contract for templates and bindings.
- Declare construct-only properties for values required before constructed behavior runs.
- Notify only when the effective value changes. Repeated notifications cause extra bindings, layout, and rendering work.
- Use explicit notify when several fields must change atomically or validation must run first.
- Bind properties for direct synchronization. Use transforms only when the mapping is local, deterministic, and reversible where bidirectional.
- Keep business validation outside generic property setters unless invalid values would break the object's invariant.

Avoid binding loops. If two directions need different policy, use one authoritative state transition instead of two automatic bindings.

## Signals

Signals report events across a GObject interface. Properties report state. Choose the one that matches the contract.

- Use a property when consumers need the current value after they attach.
- Use a signal for a discrete event with a defined payload.
- Use an action for a user command that can have several presentation sources.
- Keep signal payloads owned or GObject-safe. Document ordering when one event depends on another.
- Emit after internal invariants are restored and borrows are released.
- Return promptly from handlers.

Avoid signals that merely duplicate every internal method call. They widen the interface and make ordering harder to reason about.

## Actions, menus, and shortcuts

Actions are the command interface for buttons, menus, keyboard shortcuts, notifications, and external activation.

- Put process-wide commands under `app.*` and window-specific commands under `win.*`.
- Register accelerators against detailed action names.
- Use a stateful action for a persistent toggle or mutually exclusive choice. Keep the action state and application state synchronized through one transition.
- Use a parameterized action when the caller supplies a typed value. Validate the GVariant signature at the boundary.
- Bind widget sensitivity and visibility to command availability rather than duplicating policy in each control.
- Keep labels and icons in the presentation layer. The action name should describe the command contract.

Test actions without clicking a particular widget. Then test that every presentation source invokes the correct action.

## Templates, Blueprint, and resources

Preserve the project's existing UI construction method unless the user requests a migration.

For composite templates:

- register the resource before the class first uses it;
- keep template resource paths consistent with the GResource prefix;
- bind required children with stable IDs;
- initialize the template during instance construction at the point required by gtk-rs;
- keep callback names and signatures synchronized with template declarations;
- fail the build when Blueprint or XML compilation fails.

Use Rust-built widget trees when the project already follows that style or when dynamic composition is clearer in code. Do not introduce templates merely to move ordinary Rust into XML.

## List models and views

Use `GListModel` with `GtkListView`, `GtkGridView`, or `GtkColumnView` for dynamic or large collections.

Pick a selection model deliberately:

- `NoSelection` for display-only collections;
- `SingleSelection` for navigation or one active item;
- `MultiSelection` for explicit selection mode and bulk actions.

In a list-item factory:

- build stable widget structure in `setup`;
- connect handlers once when possible;
- attach current item state in `bind`;
- remove item-specific bindings and handlers in `unbind`;
- release heavy child state in `teardown` when useful.

Rows are recycled. A row index is not durable identity. Store identity in the model item, then map selection or commands back to that identity.

For model refreshes, prefer insert, remove, splice, filter, and sort operations that preserve unchanged objects. Replacing the full model can destroy selection, focus, expanded state, and scroll position.

Use `GtkListBox` for small lists where each row is a distinct widget and virtualization adds no value. Measure before replacing a clear small-list implementation.

## Async work and threads

GIO async operations usually run through the GLib main context without blocking it. Prefer them for files, streams, subprocesses, and D-Bus.

For CPU work or blocking libraries:

1. Capture plain owned input on the main thread.
2. Run the work on an appropriate worker.
3. Return plain owned output or an error.
4. Schedule the result on the owning main context.
5. Check cancellation, view lifetime, and request generation before applying it.

GTK, GDK, Pango layout objects tied to a context, and most GObjects are not worker payloads. Do not make them `Send` through wrappers.

Chunk large model applications. A worker can finish quickly while one enormous main-thread update still freezes input and rendering.

## Error handling

Keep technical detail in logs and present recovery in user terms.

- Propagate errors with context across Rust layers.
- Convert an error to a UI state at the presentation boundary.
- Use a toast for a brief recoverable event, a banner for a persistent condition, and a dialog for a decision that blocks progress.
- Preserve the previous usable state when a refresh fails.
- Attach retry to the operation that failed and make repeated activation safe.
- Avoid panic paths in callbacks for ordinary runtime failure.

## Primary references

- [gtk4-rs book](https://gtk-rs.org/gtk4-rs/stable/latest/book/)
- [gtk4-rs API](https://gtk-rs.org/gtk4-rs/stable/latest/docs/gtk4/)
- [glib subclassing](https://gtk-rs.org/gtk-rs-core/stable/latest/docs/glib/subclass/index.html)
- [GTK list widgets](https://docs.gtk.org/gtk4/section-list-widget.html)
- [Gio.Action](https://docs.gtk.org/gio/iface.Action.html)
- [GLib main loop](https://docs.gtk.org/glib/main-loop.html)
