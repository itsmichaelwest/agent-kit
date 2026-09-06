# XAML and rendering costs

For image-heavy grids, recycling, and connected animations, read [artwork and lifetimes](artwork-and-lifetimes.md).

## Locate the expensive phase

Time XAML initialization, window chrome, navigation population, first layout, and visible-item realization individually. A short XAML file can instantiate expensive templates, and lazy resources move their cost from dictionary initialization to first use.

Compare packaged and unpackaged traces only with matching data, dimensions, configuration, and runtime settings. Attribute a difference to the measured phase before changing title bars, backdrops, or deployment settings.

## Reduce work on the visible path

- Use `x:Load` for elements not needed initially. It requires `x:Name`. Check deferred bindings, event subscriptions, and first-use behavior.
- Simplify templates where profiling shows repeated layout or binding cost. Preserve the repository's XAML declaration conventions.
- Update existing row objects and observable collections when an incremental change represents the operation. Replacing a source can force realization.
- Keep virtualization bounded by the viewport. Check nested scrolling and unconstrained measurement before replacing a list or grid.
- Coalesce background updates and apply a bounded batch per dispatcher turn. Keep initial content and interactive responses from waiting behind progress.
- Defer optional shell integrations until after useful content when their lifecycle allows it. Preserve any required background or resident behavior.

Microsoft recommends `x:Load` over `Visibility=Collapsed` for content that is not initially needed: collapsed elements still have object-instance cost, while an unloaded element has a small placeholder overhead of about 600 bytes until it is realized. Use that number for orientation, then measure the real tree. See [Optimize XAML loading for WinUI](https://learn.microsoft.com/windows/apps/develop/performance/optimize-xaml-loading).

Microsoft's startup guide also offers a rough planning estimate of 1 ms to create each XAML element. Do not multiply that number into a forecast: templates, hardware, framework version, and element type change the result. Use it to spot an implausibly large startup tree, then measure construction and layout. See [Best practices for WinUI app startup performance](https://learn.microsoft.com/windows/apps/develop/performance/app-startup-performance).

For item controls, retain UI virtualization before hand-optimizing templates. The standard `ListView` and `GridView` create and cache containers around the viewport instead of realizing the full collection. Measure UI-thread item creation, binding, layout, and memory separately. See [Optimize ListView and GridView performance](https://learn.microsoft.com/windows/apps/develop/performance/optimize-gridview-and-listview).

Prefer `{x:Bind}` when the source is known at compile time and its semantics fit the view. It generates strongly typed code and Microsoft documents lower runtime cost than general-purpose `{Binding}`. Keep `{Binding}` where late-bound data or the existing data-context contract requires it, and measure repeated template bindings before broad rewrites. See [Windows data binding in depth](https://learn.microsoft.com/windows/apps/develop/data-binding/data-binding-in-depth).

Re-measure after changing publish settings. Removing JIT work can shift the critical path to data arrival; further XAML work may then leave first content unchanged.

## Preserve interaction and presentation

Stock controls already implement keyboard navigation, selection, accessibility, theming, and other platform behavior. First simplify how the app uses and templates them. Replace a control only when the measured benefit outweighs the interaction and maintenance cost.

Keep a loading state visible while content arrives when the launch contract allows it. Increasing page size or delaying reveal can make first content slower even if it reduces the number of later updates. Changing a producer's event contract affects other consumers; diagnose local pacing first.

A successful trimmed build does not verify displayed content. Check bindings and native collection interfaces in the published output, as described in [runtime and publish](runtime-and-publish.md).
