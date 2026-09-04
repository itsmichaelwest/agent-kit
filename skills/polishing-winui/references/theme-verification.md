# Theme Verification

Workflow and fix patterns for verifying Light, Dark, and HighContrast theme correctness in WinUI 3 apps.

## Verification Workflow

Choose the affected surfaces and shared resource consumers. Cover all pages for a comprehensive audit or changes to application-wide theme resources. For an audit, inspect existing behavior without editing source.

1. **Launch the app in Light theme.** Inspect the selected surfaces and controls.
2. **Switch to Dark theme.** Verify the selected surfaces, text, and icons adapt correctly.
3. **Switch to HighContrast.** Verify readability and that no elements disappear.
4. **Switch back to Light.** Confirm the round-trip works without artifacts.

## Switching Themes Programmatically

### At the application level (App.xaml)

```xml
<Application
    x:Class="MyApp.App"
    RequestedTheme="Dark">
    <!-- Forces Dark. Remove the attribute to follow the system setting. -->
</Application>
```

### At the window or element level (C#)

```csharp
// Switch a specific element (and its subtree) to Dark
if (Content is FrameworkElement rootElement)
{
    rootElement.RequestedTheme = ElementTheme.Dark;
}
```

### For testing, toggle at runtime

```csharp
public void ToggleTheme()
{
    if (Content is FrameworkElement root)
    {
        root.RequestedTheme = root.RequestedTheme == ElementTheme.Dark
            ? ElementTheme.Light
            : ElementTheme.Dark;
    }
}
```

Note: HighContrast cannot be set programmatically from the app. It must be toggled in Windows Settings > Accessibility > Contrast themes.

## Common Fix Patterns

### Hardcoded color to ThemeResource

**Before (broken in dark mode):**

```xml
<TextBlock Foreground="#333333" Text="Hello" />
<Border Background="#FFFFFF" CornerRadius="4">
    <TextBlock Foreground="#000000" Text="Card content" />
</Border>
```

**After (theme-aware):**

```xml
<TextBlock Foreground="{ThemeResource TextFillColorPrimaryBrush}" Text="Hello" />
<Border Background="{ThemeResource CardBackgroundFillColorDefaultBrush}"
        CornerRadius="{StaticResource ControlCornerRadius}">
    <TextBlock Foreground="{ThemeResource TextFillColorPrimaryBrush}" Text="Card content" />
</Border>
```

### Missing HighContrastAdjust

Some custom controls need to opt into HighContrast adjustment.

```xml
<Border HighContrastAdjust="Auto">
    <!-- Content will automatically adjust for high contrast -->
</Border>
```

Set `HighContrastAdjust="None"` only on decorative elements that should not be modified (e.g., images).

### Background not responding to theme change

**Symptom:** Switching theme does not change the background.

**Cause:** Using `{StaticResource ...}` for a brush that changes per theme. StaticResource is resolved once; ThemeResource re-evaluates on theme change.

**Fix:** Change `{StaticResource SomeBrush}` to `{ThemeResource SomeBrush}` for any brush that differs between Light and Dark.

```xml
<!-- Wrong: does not update on theme switch -->
<Grid Background="{StaticResource ApplicationPageBackgroundThemeBrush}" />

<!-- Right: updates on theme switch -->
<Grid Background="{ThemeResource ApplicationPageBackgroundThemeBrush}" />
```

## System Brush Reference

Key WinUI 3 system brushes to use instead of hardcoded colors.

### Backgrounds

| Resource key | Usage |
| --- | --- |
| `ApplicationPageBackgroundThemeBrush` | Primary page/window background |
| `CardBackgroundFillColorDefaultBrush` | Card or container surface |
| `CardBackgroundFillColorSecondaryBrush` | Nested or secondary card surface |
| `LayerFillColorDefaultBrush` | Layered surface on top of a card |
| `SolidBackgroundFillColorBaseBrush` | Solid opaque background (no transparency) |
| `SolidBackgroundFillColorSecondaryBrush` | Secondary solid background |

### Text

| Resource key | Usage |
| --- | --- |
| `TextFillColorPrimaryBrush` | Primary text (headings, body) |
| `TextFillColorSecondaryBrush` | Secondary/caption text |
| `TextFillColorTertiaryBrush` | Placeholder or hint text |
| `TextFillColorDisabledBrush` | Disabled text |
| `AccentTextFillColorPrimaryBrush` | Accent-colored text (links, emphasis) |

### Controls

| Resource key | Usage |
| --- | --- |
| `ControlFillColorDefaultBrush` | Default control fill (buttons, inputs) |
| `ControlFillColorSecondaryBrush` | PointerOver control fill |
| `ControlFillColorTertiaryBrush` | Pressed control fill |
| `ControlFillColorDisabledBrush` | Disabled control fill |
| `ControlStrokeColorDefaultBrush` | Control border |
| `ControlStrokeColorSecondaryBrush` | Secondary control border |

### Accent and Status

| Resource key | Usage |
| --- | --- |
| `AccentFillColorDefaultBrush` | Primary accent (active toggle, primary button) |
| `AccentFillColorSecondaryBrush` | PointerOver accent |
| `AccentFillColorTertiaryBrush` | Pressed accent |
| `AccentFillColorDisabledBrush` | Disabled accent |
| `SystemFillColorCriticalBrush` | Error/destructive states |
| `SystemFillColorCautionBrush` | Warning states |
| `SystemFillColorSuccessBrush` | Success states |
| `SystemFillColorAttentionBrush` | Informational states |

### Subtle and Transparent

| Resource key | Usage |
| --- | --- |
| `SubtleFillColorTransparentBrush` | Default state for subtle buttons (transparent) |
| `SubtleFillColorSecondaryBrush` | PointerOver for subtle buttons |
| `SubtleFillColorTertiaryBrush` | Pressed for subtle buttons |
| `SubtleFillColorDisabledBrush` | Disabled subtle button |

### Dividers

| Resource key | Usage |
| --- | --- |
| `DividerStrokeColorDefaultBrush` | Separator lines between sections |
| `CardStrokeColorDefaultBrush` | Card border stroke |

## References

- [XAML theme resources](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-theme-resources)
- [Theming in Windows apps](https://learn.microsoft.com/en-us/windows/apps/develop/ui/theming)
- [Color](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/color)
- [Contrast themes](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes)
- [ResourceDictionary and XAML resource references](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-resource-dictionary)
- [ThemeResource markup extension](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/themeresource-markup-extension)
