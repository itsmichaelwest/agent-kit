---
name: optimizing-winui-performance
description: >-
  Measure and cut WinUI 3 launch and render time: cold launch, time to first
  frame, first rows, packaged versus unpackaged cost, ReadyToRun and trimming
  and Native AOT for WinUI, x:Load and x:Bind costs, and a UI fed by a
  separate process. Use when a WinUI 3 app launches slowly, a window or list
  draws late, a publish setting is being chosen for speed, or someone asks
  "can we get any faster" on Windows.
license: MIT
---

# Optimizing WinUI 3 performance

Working method and measured reference for making a WinUI 3 desktop app launch
and draw sooner. Everything here was learned on a real app (a C# WinUI 3
shell over a separate native helper process, Windows App SDK 2.1, .NET 10)
whose cold launch went from 2.8 s to about 0.56 s to first content rows.
Numbers in the references are calibrations from that app, not laws;
re-measure on yours.

"Helper process" throughout means any separate process the app depends on
for its data: a daemon, a service, a worker, a language server. The
connection can be a named pipe, a socket, or anything else; the lessons do
not depend on which.

## When to use

- A WinUI 3 app takes more than a second from click to a useful window.
- The window opens but its main list or page draws late.
- Choosing publish settings (self-contained, ReadyToRun, trimming, AOT).
- The UI is driven by a stream of events from another process and stutters
  or lags while data arrives.

## When not to use

- Steady-state CPU or allocation work in ordinary C# code. Use
  `analyzing-dotnet-performance`.
- Visual defects. Use `polishing-winui`.

## Workflow

### Step 1: Instrument before touching anything

Add a process-relative launch trace if the app has none. The pattern and a
bench loop are in `references/measuring.md`. The trace must record, at
minimum: app constructor entry, data source connected (or ready), first
data decoded, window created, window activated, first rendered frame, and
first rows rendered. Without the frame marks you will optimize code that
was never on the path the user sees.

Done when: the trace identifies the relevant phases on the profile the user
actually runs. Use the sampling protocol in `references/measuring.md` and
report variability; investigate noise when it prevents a useful comparison.

### Step 2: Find the critical path, not the biggest number

Lay the UI-thread marks and the data-arrival marks side by side. The rows
draw at `max(first frame, rows arrived) + realisation`. Speeding up whichever
side is not the later one gains nothing. Decide which thread is the bottleneck
and write it down before choosing a fix.

Done when: you can name the segment that would move the first frame and the
segment that would move the first rows, with their measured cost.

### Step 3: Apply fixes in order of measured cost

Use the reference that matches the segment:

| Segment on the path | Reference |
| --- | --- |
| Time before the app constructor, JIT stalls, publish shape | `references/runtime-and-publish.md` |
| Helper process start, first reply, serializer cost, event streams | `references/helper-process.md` |
| Window build, when to show it, what to defer | `references/launch-choreography.md` |
| XAML load, first frame, list realisation, packaged chrome cost | `references/xaml-costs.md` |

Re-run the same bench after each change. Keep an optimization when the measured
gain is distinguishable from noise and the affected behavior still works.

Done when: the requested improvement is supported by comparable traces, or the
remaining limit and evidence needed to resolve it are identified. Report the
first post-build launch separately from warm launches using the measuring guide.

### Step 4: Report with the trace

Report before and after as a small table of marks, say which profile and
build shape produced them, and name the segments that remain and why. State
the packaged activation overhead separately, since it sits before the process
exists and no in-process change moves it.

## Patterns from the reference application

Use these as hypotheses after locating the target app's bottleneck. Preserve its
startup, data, and interaction contracts; the recorded costs are not guarantees.

- Open the window as soon as the parts a user needs to orient (navigation,
  sidebar) can draw completely, and show a loading state where the data
  goes, when that matches the product's launch contract. On the reference app,
  waiting for rows added 100 to 300 ms of blank screen.
- Start the helper process and the serializer warm-up before
  `InitializeComponent`, build the window while replies are still in
  flight, and gate only the reveal.
- When a stream of events makes the UI stutter, pace and coalesce it in the
  app, off the UI thread. Preserve the producer's event contract for other
  consumers; change it only when the requested scope includes that contract.
- Ask the data source only for what the first screen needs: page requests
  sized for one screen, joins folded into the page query, no lookup per row.
- Measure the distribution profile the user runs. The reference app's package
  identity added roughly 0.1 s inside the process and 0.2 to 0.4 s of activation;
  measure the target app's overhead separately.
- Do not swap a stock WinUI control for a look-alike to save layout time;
  the control is the interaction model. When the target is a cold launch,
  keeping a helper resident does not meet it. Report resident launch separately
  when it is part of the product's lifecycle.
- Check trimming and interop requirements against the project's toolchain.
  The reference app lost binding content until its binding and WinRT metadata
  were preserved (see `references/runtime-and-publish.md`). Validate the target
  app's published behavior before treating trimming or Native AOT as complete.
