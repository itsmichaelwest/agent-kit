---
name: optimizing-winui-performance
description: >-
  Measure and cut WinUI 3 launch and render time: cold launch, time to first
  frame, first rows, packaged versus unpackaged cost, ReadyToRun and trimming
  and Native AOT for WinUI, x:Load and x:Bind costs, and a UI fed by a
  separate process. Use when a WinUI 3 app launches slowly, a window or list
  draws late, a publish setting is being chosen for speed, or someone asks
  "can we get any faster" on Windows. Also covers artwork-heavy grids and
  native publish regressions introduced during performance work.
license: MIT
---

# Optimizing WinUI 3 performance

Measure the target application's critical path, change the work that delays
visible content, and validate the published result. Treat improvements in
launch time, frame pacing, memory use, and correctness as separate claims.

Keep this skill project-neutral. Use synthetic examples and public platform
APIs. Keep project names, internal types, local paths, package identities,
benchmark results, and session history in the project's own records.

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
- Artwork flickers during navigation, recycled tiles retain work, or an
  optimized native package fails where the Debug build works.

## When not to use

- Steady-state CPU or allocation work in ordinary C# code. Use
  `analyzing-dotnet-performance`.
- Visual defects. Use `polishing-winui`.

## Workflow

### Step 1: Establish the build and evidence

Read the repository's verification instructions and preserve the user's
architecture and interaction limits. If the task is ARM64-only, pass ARM64
explicitly to every build, test, publish, and helper probe. If computer use or
UI Automation is excluded, diagnose from source, generated code, logs, and
non-UI probes within the authorized scope; leave GUI reproduction to the user.
See [measuring](references/measuring.md) for evidence and privacy rules.

Add a process-relative launch trace if the app has none. The pattern and a
bench loop are in `references/measuring.md`. The trace must record, at
minimum: app constructor entry, data source connected (or ready), first
data decoded, window created, window activated, first rendered frame, and
first rows rendered. Without the frame marks you will optimize code that
was never on the path the user sees.

Done when: the trace identifies the relevant phases on the profile the user
actually runs. Use the sampling protocol in `references/measuring.md` and
report variability; investigate noise when it prevents a useful comparison.
For a crash regression, identify the failing build and fatal boundary before
patching. When new measurements are unavailable, label performance claims as
hypotheses or user observations.

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
| Shared artwork, recycling, connected animations, cache ownership | `references/artwork-and-lifetimes.md` |
| AOT collection or COM failures, native teardown crashes | `references/native-boundaries.md` |

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

## Optimization candidates

Use these after locating the bottleneck. Preserve the application's startup,
data, and interaction contracts.

- Reveal the window when navigation and the loading state are ready, if the
  product permits content to arrive afterward.
- Overlap independent data-source startup and serializer warm-up with XAML
  initialization. Keep UI-affine construction on the dispatcher.
- Pace and coalesce event streams off the UI thread while preserving ordering
  and the producer's contract.
- Request what the first screen needs. Avoid oversized pages and per-row lookups.
- Measure the actual distribution profile, including activation and package
  identity, before changing deployment strategy.
- Preserve stock controls' keyboard, touch, selection, and accessibility
  behavior when simplifying templates or layout.
- Validate binding metadata, collection interfaces, native dependencies, and
  resource layout in the published build before declaring an AOT change done.
