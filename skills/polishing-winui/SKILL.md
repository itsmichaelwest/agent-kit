---
name: polishing-winui
description: Audit or fix visual polish in existing WinUI 3 apps, including materials, themes, spacing, typography, icons, and interaction states. Use for visual reviews or requested polish; app scaffolding and performance profiling belong to other skills.
---

# Polishing WinUI

Review visual defects or implement requested polish within the named surfaces and shared resources.

## Scope and workflow

- For an audit or review, inspect and report findings without editing source. A request to fix or polish authorizes relevant edits; continue within that scope without asking again.
- Identify the affected views, controls, and shared resource consumers. Use [the issue taxonomy](references/issue-taxonomy.md) to classify supported findings; read only the matching references below.
- Capture and inspect the running UI when available. Use `ui-polisher` if installed, or discover an available capture tool and its actual arguments. If runtime access is unavailable, provide a source review and name the visual checks that remain unverified. Build success or UI Automation state alone does not prove visual correctness.
- For requested fixes, diagnose the cause and change the relevant XAML, styles, resources, or minimal backdrop/theme setup code. Keep business logic and data flow outside a visual-only task.
- Verify the affected surface and shared consumers after changes. Check light and dark themes for theme-sensitive changes, contrast themes for affected colors or accessibility, and relevant interaction states for changed controls. Broaden coverage for shared theme resources or an explicitly comprehensive audit.
- After an unsuccessful check, revise the diagnosis using its evidence. Continue while a concrete check or repair can advance the task. Finish when the requested fixes and relevant checks pass, or report the unresolved defect and unavailable input or capability. Repeat passed checks only when new changes or evidence justify it.
- Report findings or changes with locations, observed evidence, and remaining limitations. Distinguish screenshot observations from source-based inferences.

## Reference index

| When investigating | Read |
| --- | --- |
| Classifying visual defects | [Issue taxonomy](references/issue-taxonomy.md) |
| Mica, MicaAlt, Acrylic, and fallback behavior | [Materials and backdrops](references/material-and-backdrop-fixes.md) |
| Theme switching, system brushes, and theme resources | [Theme verification](references/theme-verification.md) |
| Spacing, corner radius, and typography | [Geometry and spacing](references/geometry-and-spacing.md) |
| Hover, press, focus, and disabled states | [Visual states](references/visual-states.md) |
| Fluent icons, sizing, and color inheritance | [Iconography](references/iconography-polish.md) |

## Resource and API choices

Prefer WinUI system resources and the project's established design tokens. Use theme-aware resources for colors that vary by theme. Confirm uncertain or version-sensitive API behavior against current Microsoft documentation for the project's Windows App SDK version; the links below are starting points. Project requirements govern the intended design, and installed SDK APIs govern implementation availability.

## Documentation Sources

### Microsoft Learn (Official)

- [Mica material](https://learn.microsoft.com/en-us/windows/apps/design/style/mica) — design guidance, variants, XAML setup
- [Acrylic material](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic) — in-app vs background acrylic
- [Materials overview](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/materials) — comparison of all Windows materials
- [SystemBackdropController](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/system-backdrop-controller) — lower-level controller API
- [Title bar customization](https://learn.microsoft.com/en-us/windows/apps/develop/title-bar) — ExtendContentIntoTitleBar, drag regions
- [XAML theme resources](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-theme-resources) — brush/color key reference
- [Theming in Windows apps](https://learn.microsoft.com/en-us/windows/apps/develop/ui/theming) — dark/light, accent, RequestedTheme
- [Color](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/color) — Fluent Design color guidance
- [Contrast themes](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes) — high contrast accessibility
- [Spacing and sizes](https://learn.microsoft.com/en-us/windows/apps/design/style/spacing) — spacing ramp, compact density
- [Typography](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography) — type ramp, Segoe UI Variable
- [Rounded corners](https://learn.microsoft.com/en-us/windows/apps/design/style/rounded-corner) — CornerRadius design guidance
- [VisualStateManager](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.visualstatemanager) — visual state API
- [Control templates](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-control-templates) — styles and templates
- [Keyboard accessibility / focus visuals](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/keyboard-accessibility)
- [Visual feedback guidelines](https://learn.microsoft.com/en-us/windows/apps/develop/input/guidelines-for-visualfeedback) — hover, press, focus states
- [Segoe Fluent Icons](https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-fluent-icons-font) — glyph table / character map
- [Icons in Windows apps](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/icons) — SymbolIcon vs FontIcon guidance
- [FontIcon class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls.fonticon) · [SymbolIcon class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls.symbolicon)
- [XAML styles](https://learn.microsoft.com/en-us/windows/apps/design/style/xaml-styles) · [ResourceDictionary](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-resource-dictionary)

### Design Systems & Samples

- [Fluent 2 Design System](https://fluent2.microsoft.design/) — current-gen design system
- [WinUI Gallery source](https://github.com/microsoft/WinUI-Gallery) — definitive WinUI 3 example app
- [WinUI Gallery (Microsoft Store)](https://apps.microsoft.com/detail/9p3jfpwwdzrc) — browse controls interactively
- [WindowsAppSDK-Samples](https://github.com/microsoft/WindowsAppSDK-Samples) — feature-specific samples
- [Windows Community Toolkit](https://github.com/CommunityToolkit/Windows) · [docs](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/windows/)

### Community

- [Nick's .NET Travels — WinUI](https://nicksnettravels.builttoroam.com/tag/winui/) — architecture, patterns
- [Windows Developer Blog — WinUI](https://blogs.windows.com/windowsdeveloper/category/winui/) — official announcements
- [#ifdef Windows — WinUI3](https://devblogs.microsoft.com/ifdef-windows/tag/winui3/) — engineering deep dives
