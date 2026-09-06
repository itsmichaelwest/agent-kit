# Measuring a WinUI 3 launch

## Build identity and evidence limits

Record the executable, architecture, configuration, runtime, package path, and profile with each trace. Debug output that loads CoreCLR did not come from a Native AOT run. A debugger may also show a handled first-chance C++ exception, which is different from a fatal event.

For a fatal regression, correlate the process and build with the event log, stowed exception, or managed stack. A wrapper failure in `Microsoft.UI.Xaml.dll` or `CoreMessagingXP.dll` does not identify the faulty application callback.
Inspect the nested HRESULT and application frames before changing code. Prefer source and existing logs first, especially when the user excludes UI Automation or app launch. A non-UI native probe is useful only within the permitted scope.

Fatal diagnostics can record a fixed phase identifier, exception type, HRESULT, and method stack without source filenames. Omit exception messages, `Data`, arguments, account details, and token-bearing URLs. Bound file size and nested exception depth, keep logging failures from replacing the original error, and leave the exception unhandled. Avoid continuous first-chance logging in Release.

Label measured timings, user observations, and untested hypotheses. A working feature says nothing by itself about memory use, frame drops, rendering quality, or device behavior.

Choose the user-facing threshold before collecting a trace. [Latency budgets and scale](latency-budgets.md) lists frame and response budgets. Record the interval the user experiences alongside the internal segments that explain it.

## The launch trace

Put a static `LaunchTrace` class in a WinUI-free core assembly so tests can use it:

- `Mark(name)` records a timestamp relative to process start (`Process.GetCurrentProcess().StartTime`), from any thread.
- `HasMark(name)` lets a later handler ask whether an earlier phase happened (the frame handler uses it to decide whether rows are on screen yet).
- `Complete(name)` records the final mark and writes `ui-launch-<pid>.log` to the app's log directory. Each line: time since process creation, gap since the previous mark, phase name.

These phase labels usually occur in this order. "Helper" means the process that supplies data. An app with its own database records the open and first query instead:

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

`CompositionTarget.Rendered` can serve as a frame marker. Subscribe before `Activate()`, then keep the subscription until a frame follows the rows mark. Unsubscribe there. Correlate the marks with pixels or a screen recording when claiming visible presentation; a callback alone does not show what the user actually saw.

## Bench loop

Run the loop only when app launches and interaction are allowed. Restrictions on architecture, launch, and computer use also cover helper scripts and UI Automation APIs. Pass the target architecture explicitly instead of accepting the solution default.

A bounded PowerShell loop closes the test instance, stops only its helper processes, launches it, waits for the trace with a timeout, prints the result, and repeats. Leave unrelated instances running. Launch it in one of two ways:

- Unpackaged: `Start-Process <exe>`.
- Packaged: `Start-Process explorer.exe "shell:AppsFolder\<PFN>!App"` and find the process by name after a short wait.

Print the helper's own log next to each trace so request timings line up. Start with one post-build launch followed by five warm launches. Keep the first result separate and report every sample, the warm median, and the spread. A first post-build launch has an unknown OS-cache state unless the test controls it. State the conditions that were controlled and use the same protocol before and after. Investigate variability when it obscures the expected gain; increase samples only when needed to distinguish the effect from noise.

Package registration, install, update, reboot, antivirus scanning, and a new binary can each change file-cache or deployment behavior. Name which of these occurred. Never merge a multi-second post-registration outlier into a warm-run median or silently discard it; report it as a separate launch class and repeat it when that class matters to users.

For frame pacing, report the count or percentage of frames over the applicable deadline and useful percentiles. An average below 16.7 ms can hide visible 60 Hz hitches. When application marks cannot locate the work, use the ETW-based XAML Frame Analysis workflow in Microsoft's [WinUI performance optimization guide](https://learn.microsoft.com/windows/apps/develop/performance/winui-perf).

## Activation overhead

For a packaged app, record the time before the activation call and compare it with process creation. State which activation mechanism was used; a helper launch command and a direct user action may have different overhead. Keep this interval separate from the in-process trace.

## Data profiles and package registration

Resolve the actual data roots and overrides for each launch mode. Packaged and unpackaged runs may use different databases, remembered state, and window sizes. Use a disposable profile for first-run checks and identify the profile in each measurement. Resolve the storage paths rather than inferring them from package identity.

When authorized, register the published layout through the project's supported development workflow. Verify that the registered path and executable match the intended output; a successful registration command is insufficient evidence. Account for existing registration and deployment behavior before modifying it.

Use package-aware extraction tools and verify final filenames and resource paths. Archive encoding can otherwise leave dependencies under names that the loader does not request.

## Verifying content without pixels

This method uses UI Automation and must be within the user's scope.

Check capture-process DPI awareness, bounds, focus, and the capture API before interpreting a black or incorrectly cropped screenshot as an application bug.

When UI Automation is permitted, locate the intended process and inspect the expected elements and values. Compare names and item counts with synthetic test data rather than assuming a fixed tree size. Empty exposed values can help locate binding failures, but do not prove their cause. UI Automation does not establish layout, color, or pixel correctness; inspect usable images or recordings for those claims.

## Screen recordings

When the user supplies a recording, count frames from the click to the first window pixel and to the first rows, at the recording's frame rate. Compare with the trace: the difference is activation plus the shell.
