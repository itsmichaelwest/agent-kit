# Performance, debugging, and testing

Use this reference for freezes, slow startup, resize or scrolling problems, excess CPU or memory, rendering faults, runtime warnings, regressions, and CI.

## Define the failure

Write a repeatable workload before changing code. Name the build profile, data set, display backend, window state, machine constraints, and observable measure.

Examples include activation to first usable frame, frame time while scrolling a populated list, latency from search input to visible results, time to apply a model refresh, main-loop stall duration during device access, or retained memory after repeated window open and close.

Separate correctness from speed. A missing update, stale selection, duplicate handler, or feedback loop can look like a performance problem.

## Runtime diagnostics

Useful environment settings include:

```bash
G_MESSAGES_DEBUG=all path/to/app
G_DEBUG=fatal-criticals path/to/app
GTK_DEBUG=interactive path/to/app
GSETTINGS_BACKEND=memory path/to/app
GDK_BACKEND=wayland path/to/app
```

Use only settings supported by the installed toolkit. Capture complete warnings and the first critical message. Later warnings often follow from earlier state corruption.

Make logs reachable. A GUI process started from a desktop file may write to the user journal rather than the invoking terminal. Check the process's journal and application-specific structured logs before adding new logging.

Use GDB or LLDB for native crashes. Build with debug information. Break on GLib critical logging when a warning precedes the crash.

## GTK Inspector

Use GTK Inspector to examine:

- widget hierarchy and visibility;
- layout allocation and size requests;
- CSS nodes, classes, colors, and provider order;
- focus and accessibility trees;
- object properties and signals;
- list-item recycling;
- render and frame information;
- adaptive layouts at different sizes where the installed version supports it.

Inspector evidence is better than guessing from source. Confirm that the expected widget exists, has the expected state, and receives the expected style.

## Sysprof

Use Sysprof for main-loop scheduling, CPU samples, frame timing, allocations, I/O, thread activity, and startup.

1. Capture a baseline with a repeatable workload.
2. Mark the interaction or time range under review.
3. Find long main-thread slices, repeated hot functions, allocation bursts, I/O waits, and frame misses.
4. Attribute the cost to a concrete call path.
5. Change one cause.
6. Repeat the same capture and compare the same range.

State the measured result. Do not call a change an optimization without a trace, benchmark, or other repeatable evidence.

## Common GTK bottlenecks

Check these patterns against evidence:

- blocking files, network, subprocesses, devices, or locks in a callback;
- creating a widget for every item instead of using a virtualized list;
- rebuilding an entire model for a small change;
- reconnecting handlers every time a list row binds;
- repeated property notifications for the same effective value;
- filter or sort functions doing I/O or expensive normalization;
- decoding full-size images that display as thumbnails;
- CSS selectors that cause broad restyling or depend on deep widget trees;
- custom layout that repeatedly measures expensive children;
- snapshot code that allocates or performs domain work every frame;
- timers or idle callbacks that never stop;
- strong-reference cycles that retain windows, models, textures, or services;
- applying one huge worker result in a single main-thread batch.

Fix the responsible interface where possible. A domain query that returns a full data set for every keystroke may need a cancellable search interface, not a faster row widget.

## Responsiveness patterns

- Debounce only when the product tolerates delayed response. Cancel superseded work in either case.
- Keep stable model objects and apply bounded changes.
- Decode and scale media near the required display size.
- Cache expensive immutable or versioned results with a clear invalidation rule.
- Prioritize visible content and cancel off-screen work.
- Coalesce notifications and redraw requests after a logical state transition.
- Apply large results in chunks when one batch would block input.
- Use release-like optimization when measuring CPU cost, with symbols retained for profiles.

## Test layers

Put most behavior below GTK and test it as normal Rust:

- reducers and state transitions;
- domain adapters and command results;
- validation and formatting;
- filtering, sorting, grouping, and stable identity;
- cancellation and stale-result rejection;
- metadata and serialization.

Test GObject-facing contracts where GTK behavior matters:

- property defaults, mutation, and notifications;
- signal payloads and ordering;
- action presence, enabled state, parameters, and state;
- list-model item counts and change notifications;
- selection behavior after model changes;
- template construction and required children;
- disposal and late callbacks.

Use a display-backed integration test for behavior that depends on focus, layout, rendering, input dispatch, drag and drop, popovers, or accessibility. State the backend and compositor used.

## Regression tests

A regression test should fail for the original cause and pass for the repair. Prefer the lowest layer that still expresses the behavior.

Avoid tests that pass only because queued main-context work never ran. Drain or iterate the main context according to the async contract, with a bounded timeout and useful failure output.

Isolate GSettings and filesystem state. Use temporary directories, memory settings backends, and test-specific application IDs where the platform permits them.

Tests must clean up windows, sources, subscriptions, workers, and environment changes. Order-dependent green tests are not reliable evidence.

## Visual and interaction verification

For a changed view, inspect normal, narrow, large-text, translated, loading, empty, populated, disabled, error, and destructive states that can occur. Exercise keyboard focus, repeated activation, cancellation, model refresh, selection persistence, window close and reopen, and late async completion.

Capture screenshots when visual comparison matters. A screenshot does not cover focus behavior, keyboard input, screen-reader output, animation, or resize transitions, so keep those as separate checks.

## CI

- Run CI against the declared system-library floor. Testing only the newest toolkit does not prove compatibility.
- Build the correct Cargo workspace and all targets.
- Run formatting and Clippy with repository policy.
- Compile Blueprint, resources, schemas, and translations.
- Provide a supported display backend for display tests.
- Keep display-dependent tests separate enough to diagnose environment failure.
- Validate package metadata and build the sandboxed artifact where release risk justifies it.
- Preserve logs, backtraces, screenshots, and traces for failures.

## Primary references

- [GTK running and debugging](https://docs.gtk.org/gtk4/running.html)
- [GTK Inspector](https://docs.gtk.org/gtk4/running.html#interactive-debugging)
- [Sysprof](https://apps.gnome.org/Sysprof/)
- [Gtk.test_init](https://docs.gtk.org/gtk4/func.test_init.html)
- [Rust backtraces](https://doc.rust-lang.org/std/backtrace/)
