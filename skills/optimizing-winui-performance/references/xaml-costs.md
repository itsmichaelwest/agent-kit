# XAML and rendering costs

Measured on a NavigationView shell with a Frame, a status bar, three
InfoBars, and a content page with a ListView. ReadyToRun, packaged unless
noted.

| Work | Cost | Notes |
| --- | --- | --- |
| App constructor end to `OnLaunched` | ~55 ms | WinUI's own `Application.Start` work. App.xaml's `InitializeComponent` itself took under 3 ms: `XamlControlsResources` and the CommunityToolkit control styles load lazily on first use, so there is nothing to move out of App.xaml. |
| MainWindow `InitializeComponent` | ~90 ms | Compiled XBF, still 90 ms for a 274-line window whose tree is dominated by NavigationView and its item templates. |
| Mica backdrop | 7 ms | Cheap enough to keep. |
| `ExtendsContentIntoTitleBar` + `SetTitleBar` | 46 ms packaged, 13 ms unpackaged | The one packaged anomaly in the trace; unexplained. Investigate before larger work. |
| `AppWindow.SetIcon` | 3 ms | |
| Sidebar build (code-behind items) | 26 ms | |
| Sidebar populated to first frame | ~110 ms | First layout and render of NavigationView, the page, and the loading state. The largest UI-thread block left. |
| First page of rows to rows rendered | ~65 ms | ListView realising the visible items and their templates. |
| Tray icon + notification registration | few hundred ms | Never on the launch path. Defer until after first rows. |

## Reductions that worked

- `x:Load` on anything not in the first frame. It requires `x:Name` on the
  element. Checkboxes in a column browser, an analysis banner, secondary
  panels.
- Build sidebar items in code rather than binding a template per header;
  the stock `NavigationViewItemHeader` template binds `Content` through a
  path that costs per item.
- Update existing row objects on a change instead of replacing a grouped
  source; replacing forces WinUI to lay out the whole list again.
- Keep the tray `TaskbarIcon` in application resources so a tray-only
  process has it, but create it after the first rows.
- Coalesce incoming batches off the UI thread and apply one batch per
  dispatcher turn (see `helper-process.md`).

## Native AOT, measured

With the same XAML compiled Native AOT (see `runtime-and-publish.md`), the
UI-thread costs above fell together, unpackaged, warm:

| Mark | ReadyToRun | Native AOT |
| --- | --- | --- |
| App constructor starts | 86 ms | 38 ms |
| Helper connected | 214 ms | 90 ms |
| Sidebar complete | 442 ms | 365 ms |
| First frame | 549 ms | 465 ms |
| Rows rendered | 658 ms | 560 ms |

After AOT the helper's replies, not the UI thread, gate the sidebar: the
requests go out at about 90 ms and the navigation replies land around
300 ms later. The next win is on the data side.

## Reductions not yet done, in order of expected gain

1. Defer the InfoBars, the status bar, and header template resources with
   `x:Load`; simplify the item templates. Expected 30 to 50 ms off the first
   frame. Only worth doing once the UI thread is again the later side.
2. Explain or avoid the packaged title bar cost.

## Off the table

- Replacing a fundamental WinUI control (NavigationView, ListView,
  ContentDialog) with something that looks similar. The control carries the
  interaction model: keyboard navigation, selection, accessibility, theming,
  and every future platform update. A look-alike changes all of it and the
  saving is never worth what it costs users. Do not propose it as a
  performance fix.

## Things that look like wins and are not

- Waiting for rows before showing the window. It costs blank screen, and a
  loading state is what users expect to see there.
- Throttling the producer's event rate. That moves the problem to every
  consumer instead of solving it in the one that stutters.
- Raising the first page size. Page cost is proportional to the rows
  requested, so a bigger first page arrives later.
- Trimming without the binding and interop work. It builds and runs, then
  draws nothing.
