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

Measure the path to visible content, fix the part that holds it up, and test the published build. Launch time, frame pacing, memory use, and correctness need their own evidence.

In this skill, a "helper process" is any separate process that supplies the app with data, such as a daemon, service, worker, or language server. The transport may be a named pipe, socket, or something else.

## When to use

- A WinUI 3 app takes more than a second from click to a useful window.
- The window opens but its main list or page draws late.
- Choosing publish settings (self-contained, ReadyToRun, trimming, AOT).
- The UI is driven by a stream of events from another process and stutters or lags while data arrives.
- Artwork flickers during navigation, recycled tiles retain work, or an optimized native package fails where the Debug build works.

## When not to use

- Steady-state CPU or allocation work in ordinary C# code. Use `analyzing-dotnet-performance`.
- Visual defects. Use `polishing-winui`.

## Workflow

### Step 1: Establish the build and evidence

Start with the repository's verification instructions and the user's limits on architecture and interaction. Pass the user's current architecture to every build, test, publish, and helper probe. Running x64 builds and benchmarks on ARM64 will introduce additional latency due to runtime emulation. If the user excludes computer use or UI Automation, work from source, generated code, logs, and permitted non-UI probes. The user handles GUI reproduction. See [measuring](references/measuring.md) for evidence and privacy rules.

If the app has no process-relative launch trace, add one using the pattern and bench loop in `references/measuring.md`. Record at least the app constructor, data source readiness, first decoded data, window creation and activation, first rendered frame, and first rendered rows. Frame marks prevent work on code that never delayed the screen.

Choose a user-facing budget before choosing a fix. Read [`references/latency-budgets.md`](references/latency-budgets.md) for frame, response, transition, and waiting thresholds, and for how to use hardware latency tables without mistaking them for current benchmarks.

The evidence is ready when the trace covers the profile the user runs and names the relevant phases. Follow the sampling protocol in `references/measuring.md` and report its variability. If noise hides the difference, investigate it. For a crash, identify the failing build and native boundary before patching. If no new measurement is available, call the claim a hypothesis or user observation.

### Step 2: Find the critical path, not the biggest number

Compare the UI-thread marks with the data-arrival marks. Rows draw at `max(first frame, rows arrived) + realisation`, so improving the earlier side does not move the result. Name the bottleneck before choosing a fix.

Before moving on, identify which measured segment controls the first frame and which controls the first rows.

### Step 3: Apply fixes in order of measured cost

Use the reference that matches the segment:

| Segment on the path | Reference |
| --- | --- |
| Frame, response, transition, and waiting budgets | `references/latency-budgets.md` |
| Time before the app constructor, JIT stalls, publish shape | `references/runtime-and-publish.md` |
| Helper process start, first reply, serializer cost, event streams | `references/helper-process.md` |
| Window build, when to show it, what to defer | `references/launch-choreography.md` |
| XAML load, first frame, list realisation, packaged chrome cost | `references/xaml-costs.md` |
| Shared artwork, recycling, connected animations, cache ownership | `references/artwork-and-lifetimes.md` |
| AOT collection or COM failures, native teardown crashes | `references/native-boundaries.md` |

Run the same benchmark after each change. Retain a change only when its gain is larger than the noise and the affected behavior still works.

Finish when comparable traces support the improvement, or when they expose the remaining limit and the evidence needed to resolve it. Report the first launch after a build separately from warm launches.

### Step 4: Report with the trace

Use a small before-and-after table of trace marks. Include the profile and build shape, then explain the remaining time. Packaged activation happens before the process exists, so report that interval on its own.

## Optimization candidates

Once the trace identifies the bottleneck, consider these options without changing the app's startup, data, or interaction contracts:

- Reveal the window when navigation and the loading state are ready, if the product permits content to arrive afterward.
- Overlap independent data-source startup and serializer warm-up with XAML initialization. Keep UI-affine construction on the dispatcher.
- Pace and coalesce event streams off the UI thread while preserving ordering and the producer's contract.
- Request what the first screen needs. Avoid oversized pages and per-row lookups.
- Measure the actual distribution profile, including activation and package identity, before changing deployment strategy.
- Preserve stock controls' keyboard, touch, selection, and accessibility behavior when simplifying templates or layout.
- Validate binding metadata, collection interfaces, native dependencies, and resource layout in the published build before declaring an AOT change done.
