# Launch choreography

The order that produced a window at about 550 ms and rows at 660 ms
unpackaged (650 and 730 packaged) from process start on a ReadyToRun build,
and 465 and 560 ms on Native AOT.

## App constructor

1. Mark the trace.
2. `Task.Run` the serializer warm-up.
3. Resolve the data root and log directory.
4. Single-instance registration, then start the helper process if this is
   the main instance and none is running.
5. `InitializeComponent()`.

## OnLaunched

1. Connect to the helper and complete the handshake.
2. Start the event router (dispatches to the UI thread).
3. Send the launch burst.
4. If a configuration file exists and this is not a startup launch, build the
   main window now, speculatively. `Populate()` runs on a later dispatcher
   turn so any batch already posted (the summary, usually) applies first and
   its page requests go out before the sidebar is built.
5. Await the configuration reply with a timeout. Only when nothing is
   configured does the inventory matter to the setup decision, so a
   configured app does not wait for it.
6. First run: discard the speculative window, show the wizard.
7. Otherwise gate the reveal on `Task.WhenAll` of the replies the sidebar
   needs, with a deadline (1.5 s) so a slow helper does not hold the window.
   Do not gate on content rows: the page shows its loading state until they
   land.
8. Post the reveal at `DispatcherQueuePriority.Low`.
9. Defer tray icon and notification registration until the first rows have
   rendered, or a 1.5 s deadline when there is nothing to draw. Together they
   held the UI thread for a few hundred milliseconds.

## Window construction

`PrepareLaunchWindow` creates the window and applies chrome (backdrop,
extended title bar, icon, remembered placement) without activating it.
`RevealLaunchWindow` activates. `DiscardLaunchWindow` closes an unrevealed
window when the helper says setup is incomplete. The window subscribes to
`CompositionTarget.Rendered` before activation and marks the first frame and
the first frame after rows.

## Matching another platform

When a macOS or other client already has a launch rule (open once the
sidebar can draw; spinner where the content goes), copy the rule rather than
inventing a stricter one. Parity on the gate makes the two apps feel the
same and removes a whole class of "why does Windows wait" questions.

## What the trace looked like after

ReadyToRun, packaged, with the unpackaged figure in brackets:

```
   119 ms  app.constructing         (86 unpackaged)
   193 ms  helper.spawned
   281 ms  launched
   319 ms  helper.connected         (214 unpackaged)
   326 ms  startup.requests.sent
   417 ms  window.xaml
   487 ms  window.created
   538 ms  sidebar.populated        (442 unpackaged)
   647 ms  window.first-frame       (549 unpackaged)
   663 ms  content.rows
   730 ms  content.rows.rendered    (658 unpackaged)
```
