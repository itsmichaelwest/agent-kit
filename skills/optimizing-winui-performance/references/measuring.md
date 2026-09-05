# Measuring a WinUI 3 launch

## Build identity and evidence limits

Identify the executable, architecture, configuration, runtime, package path,
and profile before interpreting a trace. Debug output that loads CoreCLR is
not evidence of a Native AOT run. Keep first-chance C++ exceptions separate
from fatal events; an exception observed by a debugger may be handled normally.

For a fatal regression, correlate the process and build with the event log,
stowed exception, or managed stack. A wrapper failure in `Microsoft.UI.Xaml.dll`
or `CoreMessagingXP.dll` does not identify the faulty application callback.
Inspect the nested HRESULT and application frames before changing code. Prefer
source and existing logs first, especially when the user excludes UI Automation
or app launch. A non-UI native probe is useful only within the permitted scope.

Fatal diagnostics can record a fixed phase identifier, exception type, HRESULT,
and method stack without source filenames. Omit exception messages, `Data`,
arguments, account details, and token-bearing URLs. Bound file size and nested
exception depth, keep logging failures from replacing the original error, and
leave the exception unhandled. Avoid continuous first-chance logging in Release.

Keep measured timings, user observations, and untested hypotheses separate.
Functional success does not establish lower memory use, fewer frame drops,
rendering quality, or correct device behavior.

## The launch trace

A static `LaunchTrace` class in a WinUI-free core assembly, so tests can use
it too:

- `Mark(name)` records a timestamp relative to process start
  (`Process.GetCurrentProcess().StartTime`), from any thread.
- `HasMark(name)` lets a later handler ask whether an earlier phase happened
  (the frame handler uses it to decide whether rows are on screen yet).
- `Complete(name)` records the final mark and writes `ui-launch-<pid>.log` to
  the app's log directory. Each line: time since process creation, gap since
  the previous mark, phase name.

Example phase labels, in the order they usually occur. "Helper" is whatever
process supplies the data; an app that reads its own database marks the
open and the first query instead:

```
app.constructing        first line of the App constructor
helper.probe.*          was the helper already running
helper.spawned          child process started
app.constructed         InitializeComponent finished
launched                OnLaunched entered
helper.connected        connection open and handshake done
startup.requests.sent   the launch burst is on the wire
reply.<name>            each first reply decoded, off the UI thread
window.xaml             MainWindow InitializeComponent finished
window.chrome           backdrop, title bar, icon, placement applied
window.created
sidebar.populated       navigation can draw completely
window.first-frame      CompositionTarget.Rendered fired once after Activate
content.rows            first page applied to the ItemsSource
content.rows.rendered   the next Rendered after that (Complete)
```

`CompositionTarget.Rendered` can serve as a frame marker.
Subscribe before `Activate()`, then keep the subscription until a frame follows
the rows mark. Unsubscribe there. Correlate the marks with pixels or a screen
recording when claiming visible presentation; a callback alone does not show
what the user actually saw.

## Bench loop

Run this loop only when launches and interaction are allowed. User restrictions
on architecture, app launch, and computer use also apply to helper scripts and
UI Automation APIs. Use an explicit target architecture rather than a solution's
default platform.

Use a bounded PowerShell loop for the test instance: close it, stop only helper
processes owned by that instance, launch, wait for its trace with a timeout,
print it, and repeat. Preserve unrelated running instances. Two launch modes:

- Unpackaged: `Start-Process <exe>`.
- Packaged: `Start-Process explorer.exe "shell:AppsFolder\<PFN>!App"` and
  find the process by name after a short wait.

Print the helper's own log next to each trace so request timings line up.
Start with one post-build launch followed by five warm launches. Keep the first
result separate and report every sample, the warm median, and the spread.
A first post-build launch is not proof of a fully cold OS cache; name the
conditions actually controlled. Use the same protocol before and after.
Investigate variability when it obscures the expected gain; increase samples
only when needed to distinguish the effect from noise.

## Activation overhead

For a packaged app, record the time before the activation call and compare it
with process creation. State which activation mechanism was used; a helper
launch command and a direct user action may have different overhead. Keep this
interval separate from the in-process trace.

## Data profiles and package registration

Resolve the actual data roots and overrides for each launch mode. Packaged and
unpackaged runs may use different databases, remembered state, and window sizes.
Use a disposable profile for first-run checks and identify the profile in each
measurement. Package identity alone does not establish storage paths.

When authorized, register the published layout through the project's supported
development workflow. Verify that the registered path and executable match the
intended output; a successful registration command is insufficient evidence.
Account for existing registration and deployment behavior before modifying it.

Use package-aware extraction tools and verify final filenames and resource
paths. Archive encoding can otherwise leave dependencies under names that the
loader does not request.

## Verifying content without pixels

This is still UI Automation and requires it to be within the user's scope.

Check capture-process DPI awareness, bounds, focus, and the capture API before
interpreting a black or incorrectly cropped screenshot as an application bug.

When UI Automation is permitted, locate the intended process and inspect the
expected elements and values. Compare names and item counts with synthetic test
data rather than assuming a fixed tree size. Empty exposed values can help
locate binding failures, but do not prove their cause. UI Automation does not
establish layout, color, or pixel correctness; inspect usable images or
recordings for those claims.

## Screen recordings

When the user supplies a recording, count frames from the click to the first
window pixel and to the first rows, at the recording's frame rate. Compare
with the trace: the difference is activation plus the shell.
