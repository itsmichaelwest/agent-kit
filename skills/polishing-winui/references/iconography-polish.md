# Iconography Polish

Patterns for auditing and fixing icon usage in WinUI 3 apps: font family, sizing, and color inheritance.

## Icon Fonts

### Segoe Fluent Icons (preferred for WinUI 3)

WinUI 3 apps should use **Segoe Fluent Icons** as the icon font. This is the modern Fluent Design icon set that ships with Windows 11 and is included with the Windows App SDK.

### Segoe MDL2 Assets (legacy)

`Segoe MDL2 Assets` is the older icon font from Windows 10 / UWP. It is still available but should be replaced with Segoe Fluent Icons in WinUI 3 apps. Many glyphs have the same code points, but the visual design is updated in the Fluent set.

## Icon Size Ramp

Snap icon sizes to the standard ramp.

| Size | Usage |
| --- | --- |
| 12px | Small/secondary indicators, badge overlays, compact status icons |
| 16px | **Default for controls** — buttons, toolbars, CommandBar, NavigationView items, menu items, inline text |
| 20px | Prominent standalone icons, large inline icons |
| 24px | Hero/feature icons, section headers |
| 32px | Hero illustrations, empty state artwork, large touch targets |

Avoid arbitrary sizes like 18px, 22px, or 28px.

## FontIcon vs SymbolIcon

### FontIcon (preferred for flexibility)

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}" Glyph="&#xE710;" FontSize="16" />
```

`SymbolThemeFontFamily` resolves to `Segoe Fluent Icons` on supported systems.

### SymbolIcon (simpler but less flexible)

```xml
<SymbolIcon Symbol="Add" />
```

`SymbolIcon` uses the system symbol font automatically but offers less control over size and font.

For consistent control over size and font, prefer `FontIcon` with `SymbolThemeFontFamily`.

## Color Inheritance

Icons should inherit their foreground color from the parent control. This ensures they respond correctly to theme changes and visual states (PointerOver, Pressed, Disabled).

### Correct: inherited foreground

```xml
<Button>
    <FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
              Glyph="&#xE710;" FontSize="16" />
</Button>
```

The `FontIcon` inherits the Button's `Foreground`, which changes with visual states and themes.

### Wrong: hardcoded foreground

```xml
<Button>
    <FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
              Glyph="&#xE710;" FontSize="16"
              Foreground="#333333" />
</Button>
```

This hardcoded color will not change in dark mode or when the button is disabled.

### Exception: deliberate accent or status color

If an icon must use a specific semantic color (e.g., a red error icon), use a ThemeResource:

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
          Glyph="&#xEA39;" FontSize="16"
          Foreground="{ThemeResource SystemFillColorCriticalBrush}" />
```

## Audit Steps

1. **Find all FontIcon and SymbolIcon instances** in the XAML codebase.
2. **Verify FontFamily.** Every `FontIcon` should use `{StaticResource SymbolThemeFontFamily}` or explicitly `"Segoe Fluent Icons"`. Flag any instance of `"Segoe MDL2 Assets"`.
3. **Verify FontSize.** Every `FontIcon.FontSize` should be on the ramp: 16, 20, 24, or 32. Flag arbitrary sizes.
4. **Verify Foreground.** Icons should not have a hardcoded `Foreground` unless it is a deliberate semantic color using a `ThemeResource`. Flag any `Foreground="#..."`.
5. **Verify in both themes.** Switch to dark mode and confirm all icons are visible and correctly colored.

## Fix Examples

### Wrong font family

**Before:**

```xml
<FontIcon FontFamily="Segoe MDL2 Assets" Glyph="&#xE711;" FontSize="20" />
```

**After:**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}" Glyph="&#xE711;" FontSize="20" />
```

### Off-ramp size

**Before:**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}" Glyph="&#xE710;" FontSize="18" />
```

**After:**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}" Glyph="&#xE710;" FontSize="16" />
```

Or if the icon needs to be larger:

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}" Glyph="&#xE710;" FontSize="20" />
```

### Hardcoded color

**Before:**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
          Glyph="&#xE74E;"
          FontSize="20"
          Foreground="Black" />
```

**After (inherited):**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
          Glyph="&#xE74E;"
          FontSize="20" />
```

**After (semantic color, if needed):**

```xml
<FontIcon FontFamily="{StaticResource SymbolThemeFontFamily}"
          Glyph="&#xE74E;"
          FontSize="20"
          Foreground="{ThemeResource SystemFillColorSuccessBrush}" />
```

## References

- [Segoe Fluent Icons — glyph table](https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-fluent-icons-font)
- [Icons in Windows apps](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/icons)
- [Iconography design guidance](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/iconography)
- [FontIcon class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls.fonticon)
- [SymbolIcon class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls.symbolicon)
- [Symbol enum](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls.symbol)
