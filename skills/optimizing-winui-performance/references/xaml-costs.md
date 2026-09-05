# XAML and rendering costs

For image-heavy grids, recycling, and connected animations, read
[artwork and lifetimes](artwork-and-lifetimes.md).

## Locate the expensive phase

Measure XAML initialization, window chrome, navigation population, first layout,
and visible-item realization separately. A short XAML file can instantiate
expensive templates. Resources may load lazily, so the cost can appear at first
use rather than at the resource dictionary's initialization.

Compare packaged and unpackaged traces only with matching data, dimensions,
configuration, and runtime settings. Attribute a difference to the measured
phase before changing title bars, backdrops, or deployment settings.

## Reduce work on the visible path

- Use `x:Load` for elements not needed initially. It requires `x:Name`. Check
  deferred bindings, event subscriptions, and first-use behavior.
- Simplify templates where profiling shows repeated layout or binding cost.
  Preserve the repository's XAML declaration conventions.
- Update existing row objects and observable collections when an incremental
  change represents the operation. Replacing a source can force realization.
- Keep virtualization bounded by the viewport. Check nested scrolling and
  unconstrained measurement before replacing a list or grid.
- Coalesce background updates and apply a bounded batch per dispatcher turn.
  Keep initial content and interactive responses from waiting behind progress.
- Defer optional shell integrations until after useful content when their
  lifecycle allows it. Preserve any required background or resident behavior.

Re-measure after changing publish settings. Removing JIT work can shift the
critical path to data arrival; further XAML work may then leave first content
unchanged.

## Preserve interaction and presentation

Stock controls carry keyboard navigation, selection, accessibility, theming,
and platform behavior. Simplify their usage and templates before considering a
replacement. Any replacement needs evidence that its benefit justifies the
interaction and maintenance cost.

Keep a loading state visible while content arrives when the launch contract
allows it. Increasing page size or delaying reveal can make first content
slower even if it reduces the number of later updates. Changing a producer's
event contract affects other consumers; diagnose local pacing first.

A successful trimmed build does not verify displayed content. Check bindings
and native collection interfaces in the published output, as described in
[runtime and publish](runtime-and-publish.md).
