# Latency budgets and scale

Turn complaints such as "slow," "janky," or "not instant" into a measured interval. The thresholds below help set a budget. The trace determines whether an implementation meets it.

## Budget the experience

Josh Puckett's *Numbers software designers should know* gives a compact set of interaction thresholds:

| User-facing interval | Working interpretation |
| --- | --- |
| 8.3 ms | One frame at 120 Hz |
| 16.7 ms | One frame at 60 Hz |
| 100 ms | A response feels instantaneous |
| 200-300 ms | A transition feels snappy |
| 300-500 ms | A transition feels deliberate |
| 1 second | A delay interrupts thought |
| 10 seconds | Waiting loses attention |

Source: [Josh Puckett, "Numbers software designers should know"](https://x.com/joshpuckett/status/2095983268080636274).

Match the budget to the interaction:

- A pointer or scrolling frame must fit the display's frame interval. Leave headroom for input, composition, and work outside the code under review; do not allocate the whole 16.7 ms or 8.3 ms to application logic.
- A command acknowledged within about 100 ms can feel immediate even if its result continues asynchronously. Show the state change before optional work.
- A transition may last 200-500 ms while its animation still meets every frame deadline. The duration is not a UI-thread work allowance.
- At about one second, preserve the user's train of thought with visible, stable progress. Longer work needs cancellation or a useful background path when the product permits it. Never delay useful content merely to satisfy an animation duration.

Refresh rate changes the frame budget. Read the actual presentation rate when possible. Report the distribution of missed or over-budget frames because an average hides isolated hitches.

## Use system latency as scale intuition

Jeff Dean's *Numbers Everyone Should Know*, captured by Peter Norvig and published by Brennan O'Connor, compares operations on circa-2012 hardware:

| Operation | Historical order of magnitude |
| --- | ---: |
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock or unlock | 100 ns |
| Main-memory reference | 100 ns |
| Compress 1 KB with Snappy | 0.01 ms |
| Read 1 MB sequentially from memory | 0.25 ms |
| Same-datacenter round trip | 0.5 ms |
| Disk seek | 10 ms |
| Read 1 MB sequentially from a 1 Gbps network | 10 ms |
| Read 1 MB sequentially from disk | 30 ms |
| California-Netherlands-California packet round trip | 150 ms |

Source: [Jeff Dean's numbers, with visualizations and source notes](https://brenocon.com/dean_perf.html).

The table describes old hardware, so it cannot predict a current device, SSD, network, or cloud service. Its orders of magnitude are still useful when reviewing architecture. A network round trip cannot fit inside a frame. Many small synchronous reads can consume a launch budget, and millions of cheap operations can become visible. Measure the actual hardware and workload before changing code.

Convert units before comparing costs: 1 millisecond is 1,000,000 nanoseconds. At 60 Hz, one 16.7 ms frame spans roughly 16.7 million nanoseconds; at 120 Hz, one 8.3 ms frame spans roughly 8.3 million nanoseconds.

## Translate budgets into trace marks

Attach each budget to an observable interval:

| Experience | Start | End |
| --- | --- | --- |
| Launch response | Activation request | First visible frame |
| Useful launch | Activation request | First useful content rendered |
| Command response | Input event | Visible acknowledgement |
| Transition | Committed navigation or state change | Stable destination frame |
| Scroll or animation | Frame start | Presented frame |
| Data wait | Request sent | Content applied and rendered |

Time activation, process startup, data arrival, UI realization, and animation individually. A 90 ms in-process first frame still feels slow after a 600 ms activation delay. Likewise, a fast first frame may show an empty shell for a second.

Microsoft's WinUI startup guidance divides startup into process launch, window creation, main-page creation, and first-frame layout/render, and recommends deferring work that does not contribute to visible content. See [Best practices for WinUI app startup performance](https://learn.microsoft.com/windows/apps/develop/performance/app-startup-performance).

## Interpret one measured desktop case study

An anonymized packaged WinUI 3 app produced these warm-disk medians on one x64 machine, using matching data and five retained runs:

| Mark | Initial build | After launch-path changes | Speed-optimized Native AOT |
| --- | ---: | ---: | ---: |
| First frame | 926 ms | 690 ms | 503 ms |
| First useful content | 1,364 ms | 1,008 ms | 731 ms |

The launch-path changes overlapped safe initialization, deferred optional shell services, and avoided creating initially hidden card content. Native AOT then reduced time before launch handling and XAML construction. The same AOT pilot optimized for size reached about 1,031 ms to first frame, slower than ReadyToRun. A first launch after package registration reached about 5.4 seconds to first frame, far outside the steady warm-disk cluster.

The measurements show:

- Launch-path work and the runtime both contributed measurable gains. Test them independently.
- Benchmark `OptimizationPreference=Size` and `Speed` separately. Microsoft documents the trade-off; the property name is not a performance result. See [Optimize AOT deployments](https://learn.microsoft.com/dotnet/core/deploying/native-aot/optimizing).
- Report post-build or post-registration launches separately. Cache and deployment effects can dominate the application work.
- Test rendered bindings, collection contents, native interop, and clean exit on the exact AOT artifact. A fast trace from a broken trimmed UI is invalid.
- Do not reuse these milliseconds as a target or forecast for another app or machine. Reuse the measurement design and the causal checks.

## Profile the missed budget

Application trace marks provide cheap, repeatable comparisons. If source inspection cannot explain an over-budget mark, capture Event Tracing for Windows (ETW) with Windows Performance Recorder and open it in Windows Performance Analyzer. Microsoft's current WinUI tooling includes a XAML Frame Analysis table that calculates frame durations and highlights frame regions likely to cause responsiveness problems. See [WinUI 3 performance
optimization](https://learn.microsoft.com/windows/apps/develop/performance/winui-perf) and [Windows Performance Recorder](https://learn.microsoft.com/windows-hardware/test/wpt/windows-performance-recorder).
