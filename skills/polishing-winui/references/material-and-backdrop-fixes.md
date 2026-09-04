# Material and Backdrop Fixes

Patterns for setting up and fixing Mica, MicaAlt, and DesktopAcrylic backdrops in WinUI 3 apps.

## SystemBackdrop Property (Simplest Approach)

WinUI 3 1.3+ supports setting the backdrop directly on the Window in XAML or C#.

### XAML

```xml
<Window
    x:Class="MyApp.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <Window.SystemBackdrop>
        <MicaBackdrop />
    </Window.SystemBackdrop>

    <!-- window content -->
</Window>
```

For MicaAlt:

```xml
<Window.SystemBackdrop>
    <MicaBackdrop Kind="BaseAlt" />
</Window.SystemBackdrop>
```

For DesktopAcrylic:

```xml
<Window.SystemBackdrop>
    <DesktopAcrylicBackdrop />
</Window.SystemBackdrop>
```

### C# (App.xaml.cs or Window constructor)

```csharp
// In MainWindow constructor, after InitializeComponent()
this.SystemBackdrop = new MicaBackdrop();
```

```csharp
// MicaAlt variant
this.SystemBackdrop = new MicaBackdrop { Kind = MicaKind.BaseAlt };
```

```csharp
// DesktopAcrylic
this.SystemBackdrop = new DesktopAcrylicBackdrop();
```

## Fallback Logic for Unsupported Systems

Mica requires Windows 11 Build 22000+. Always provide a fallback.

```csharp
// In MainWindow constructor
if (MicaController.IsSupported())
{
    this.SystemBackdrop = new MicaBackdrop();
}
else if (DesktopAcrylicController.IsSupported())
{
    this.SystemBackdrop = new DesktopAcrylicBackdrop();
}
else
{
    // Solid color fallback — use a theme-aware resource
    // The default Window background will apply automatically
    // if no SystemBackdrop is set.
}
```

## Title Bar Integration

For the backdrop to show through the title bar, you must extend content into it.

```csharp
// In MainWindow constructor
ExtendsContentIntoTitleBar = true;

// Optionally set a custom title bar element
SetTitleBar(AppTitleBar); // where AppTitleBar is a XAML element
```

Without `ExtendsContentIntoTitleBar = true`, the title bar renders with an opaque system chrome that hides the backdrop in that region.

### Custom Title Bar XAML

```xml
<Grid>
    <Grid.RowDefinitions>
        <RowDefinition Height="48" />
        <RowDefinition Height="*" />
    </Grid.RowDefinitions>

    <!-- Custom title bar -->
    <Grid x:Name="AppTitleBar" Grid.Row="0">
        <TextBlock
            Text="My App"
            Style="{StaticResource CaptionTextBlockStyle}"
            VerticalAlignment="Center"
            Margin="16,0,0,0" />
    </Grid>

    <!-- Page content -->
    <Frame Grid.Row="1" x:Name="ContentFrame" />
</Grid>
```

## Common Fix Patterns

### App has no backdrop

**Symptom:** Window background is a flat solid color.

**Fix:** Add the `SystemBackdrop` property.

```csharp
// MainWindow.xaml.cs constructor
public MainWindow()
{
    InitializeComponent();
    this.SystemBackdrop = new MicaBackdrop();
}
```

### Backdrop appears but title bar is opaque

**Symptom:** The content area shows Mica but the title bar is a solid color strip.

**Fix:** Extend content into the title bar.

```csharp
public MainWindow()
{
    InitializeComponent();
    ExtendsContentIntoTitleBar = true;
    SetTitleBar(AppTitleBar);
    this.SystemBackdrop = new MicaBackdrop();
}
```

### Backdrop falls back to solid color on older Windows

**Symptom:** On Windows 10 or older Windows 11 builds, the window shows a plain background.

**Fix:** Add fallback chain with `IsSupported()` checks (see Fallback Logic section above).

### Backdrop works in light but not dark (or vice versa)

**Symptom:** Switching themes causes the backdrop to disappear or look wrong.

**Fix:** Verify that you are not setting `Window.Background` to an opaque brush that covers the backdrop. Remove any explicit `Background` on the Window or root Grid that is not `Transparent`.

```xml
<!-- Wrong: opaque background covers the backdrop -->
<Grid Background="{ThemeResource ApplicationPageBackgroundThemeBrush}">

<!-- Right: transparent so backdrop shows through -->
<Grid Background="Transparent">
```

Note: Pages hosted in a Frame can use `ApplicationPageBackgroundThemeBrush` if the Frame itself is on a backdrop-visible surface. The key is that nothing between the Window and the backdrop surface is opaque.

## References

- [Mica material](https://learn.microsoft.com/en-us/windows/apps/design/style/mica)
- [Acrylic material](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic)
- [Materials overview](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/materials)
- [SystemBackdropController](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/system-backdrop-controller)
- [Title bar customization](https://learn.microsoft.com/en-us/windows/apps/develop/title-bar)
- [MicaBackdrop class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.media.micabackdrop)
- [Window.SystemBackdrop property](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.window.systembackdrop)
