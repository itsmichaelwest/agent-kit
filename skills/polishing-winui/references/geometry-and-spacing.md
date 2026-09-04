# Geometry and Spacing

WinUI 3 spacing ramp, corner radius resources, and type ramp resources for consistent visual geometry.

## Spacing Ramp

WinUI uses a 4px-based spacing scale. Snap all Margin, Padding, and gap values to this ramp.

| Token | Value | Common usage |
| --- | --- | --- |
| — | 0px | No spacing |
| — | 4px | Tight spacing between related inline elements |
| — | 8px | Default compact spacing (e.g., between icon and label) |
| — | 12px | Moderate spacing within a group |
| — | 16px | Standard content padding, spacing between controls |
| — | 24px | Section spacing within a page |
| — | 32px | Major section breaks |
| — | 48px | Page-level padding or large visual breaks |

Values outside this ramp (e.g., 5, 10, 15, 20, 30) are off-ramp and should be corrected unless there is a specific justified reason.

## Corner Radius Resources

Use system resources instead of hardcoded numeric values.

| Resource key | Default value | Usage |
| --- | --- | --- |
| `ControlCornerRadius` | 4px | Standard controls (Button, TextBox, ComboBox, cards) |
| `OverlayCornerRadius` | 8px | Overlays, dialogs, flyouts, teaching tips |

### Nested corner radius rule

When a bordered element is nested inside another, the inner corner radius should be the outer radius minus the border thickness, so the curves stay concentric.

```
Inner radius = Outer radius - Border thickness
```

For example, if a card has `OverlayCornerRadius` (8px) and a 1px border, content corners should be 7px. In practice, using `ControlCornerRadius` (4px) for inner content within an 8px container is acceptable.

## Type Ramp Resources

Use named text styles instead of inline `FontSize` and `FontWeight` properties.

| Style resource | Size | Weight | Usage |
| --- | --- | --- | --- |
| `CaptionTextBlockStyle` | 12px | Regular | Captions, timestamps, metadata |
| `BodyTextBlockStyle` | 14px | Regular | Default body text |
| `BodyStrongTextBlockStyle` | 14px | SemiBold | Emphasized body text |
| `SubtitleTextBlockStyle` | 20px | SemiBold | Section headings |
| `TitleTextBlockStyle` | 28px | SemiBold | Page titles |
| `TitleLargeTextBlockStyle` | 40px | SemiBold | Hero text, large display |
| `DisplayTextBlockStyle` | 68px | SemiBold | Largest display text |

## Fix Examples

### Hardcoded margin to ramp value

**Before:**

```xml
<StackPanel Margin="10" Spacing="15">
    <TextBlock Text="Section title" />
    <Button Content="Action" Margin="0,10,0,0" />
</StackPanel>
```

**After:**

```xml
<StackPanel Margin="8" Spacing="16">
    <TextBlock Text="Section title" />
    <Button Content="Action" Margin="0,8,0,0" />
</StackPanel>
```

### Hardcoded corner radius to resource

**Before:**

```xml
<Border CornerRadius="5" Background="{ThemeResource CardBackgroundFillColorDefaultBrush}">
    <TextBlock Text="Card content" Margin="12" />
</Border>
```

**After:**

```xml
<Border CornerRadius="{StaticResource ControlCornerRadius}"
        Background="{ThemeResource CardBackgroundFillColorDefaultBrush}">
    <TextBlock Text="Card content" Margin="12" />
</Border>
```

### Hardcoded corner radius on overlay

**Before:**

```xml
<Border CornerRadius="10" Background="{ThemeResource AcrylicBackgroundFillColorDefaultBrush}">
    <!-- dialog content -->
</Border>
```

**After:**

```xml
<Border CornerRadius="{StaticResource OverlayCornerRadius}"
        Background="{ThemeResource AcrylicBackgroundFillColorDefaultBrush}">
    <!-- dialog content -->
</Border>
```

### Inline font properties to type ramp style

**Before:**

```xml
<TextBlock Text="Welcome" FontSize="28" FontWeight="SemiBold" />
<TextBlock Text="Description here" FontSize="14" />
<TextBlock Text="Last updated" FontSize="12" Foreground="{ThemeResource TextFillColorSecondaryBrush}" />
```

**After:**

```xml
<TextBlock Text="Welcome" Style="{StaticResource TitleTextBlockStyle}" />
<TextBlock Text="Description here" Style="{StaticResource BodyTextBlockStyle}" />
<TextBlock Text="Last updated" Style="{StaticResource CaptionTextBlockStyle}"
           Foreground="{ThemeResource TextFillColorSecondaryBrush}" />
```

## References

- [Spacing and sizes](https://learn.microsoft.com/en-us/windows/apps/design/style/spacing)
- [Alignment, margin, padding](https://learn.microsoft.com/en-us/windows/apps/design/layout/alignment-margin-padding)
- [Typography](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography)
- [Rounded corners / geometry](https://learn.microsoft.com/en-us/windows/apps/design/style/rounded-corner)
- [XAML styles](https://learn.microsoft.com/en-us/windows/apps/design/style/xaml-styles)
- [Layout overview](https://learn.microsoft.com/en-us/windows/apps/design/layout/)
