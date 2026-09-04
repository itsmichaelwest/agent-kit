# Measuring a WinUI 3 launch

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

Marks that matter, in the order they usually land. "Helper" is whatever
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

The reference app uses `CompositionTarget.Rendered` as its frame marker.
Subscribe before `Activate()`, then keep the subscription until a frame follows
the rows mark. Unsubscribe there. Correlate the marks with pixels or a screen
recording when claiming visible presentation; a callback alone does not show
what the user actually saw.

## Bench loop

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

For a packaged app, record the time before the shell launch call and compare
it with the process `StartTime`. Launching through `explorer.exe` overstates a
Start menu click, so treat the result as an upper bound. Measured 360 to
410 ms through explorer; a screen recording of a real click showed nearer
200 ms. Nothing in the process can move this.

## Two data profiles

In the reference app, a packaged run stored data under
`%LOCALAPPDATA%\Packages\<PFN>\LocalCache\{Local,Roaming}`. The same exe run
unpackaged stored data under `%APPDATA%` and `%LOCALAPPDATA%` directly. They held
different databases, window sizes, and remembered state, so a bench on one
does not describe the other. Offer an environment variable to point an
unpackaged run at any root (used for first-run smokes that must never touch
the real profile), and always say which profile a number came from. Resolve the
target app's actual data roots and any explicit overrides before measuring;
package identity alone does not establish its storage paths.

## Registering a published layout without a certificate

To measure a publish with package identity, register its folder loosely, as
Visual Studio does. Developer mode is the only requirement:

```powershell
Add-AppxPackage -Register <layout>\AppxManifest.xml -ForceApplicationShutdown -ForceUpdateFromAnyVersion
```

Two traps:

- Registering the same version at a new path is a no-op. Bump the manifest
  `Version` in the copy first.
- An MSIX stores `+` in file names percent-encoded (`libstdc%2B%2B-6.dll`).
  A plain zip extract keeps the encoded name and the app dies with a missing
  DLL dialog. Decode names with `[Uri]::UnescapeDataString` after extracting.

Registration replaces the dev package Visual Studio registered; the next
Visual Studio deploy replaces it back. App data survives both.

## Verifying content without pixels

`PrintWindow` and `CopyFromScreen` both produced black or wrong-region
captures of a WinUI window from a non-DPI-aware PowerShell process. Before
trusting a black screenshot, call `SetProcessDpiAwarenessContext(-4)` in the
capturing process. In the reference session, `SetForegroundWindow` opened the
Start menu over the app; verify capture state instead of assuming focus worked.
Use UI Automation to check exposed content:
load `UIAutomationClient` in Windows PowerShell 5.1, find the window by
process id, and count descendants by control type. A working page shows
hundreds of `Text` and `ListItem` elements with names; a trimmed-away
binding shows the elements with empty names. The same API selects sidebar
items and presses buttons, which is how the wizard and settings pages get
exercised without a hand on the mouse. These checks do not establish visual
layout, color, or pixel correctness. For those claims, inspect a usable image
or recording; otherwise state that visual verification remains incomplete.

## Screen recordings

When the user supplies a recording, count frames from the click to the first
window pixel and to the first rows, at the recording's frame rate. Compare
with the trace: the difference is activation plus the shell.
