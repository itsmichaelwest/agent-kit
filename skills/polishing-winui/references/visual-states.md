# Visual States

Patterns for verifying and fixing PointerOver, Pressed, Focused, and Disabled visual states in WinUI 3 controls.

## 5-State Matrix

Every interactive control should have distinct visual treatment for each state.

| State | Trigger | Expected behavior |
| --- | --- | --- |
| **Default** | No interaction | Base appearance |
| **PointerOver** | Mouse hover | Subtle fill or border change indicating interactivity |
| **Pressed** | Mouse down / touch | Deeper fill change, slight scale or color shift |
| **Focused** | Keyboard Tab navigation | Focus rectangle visible around the control |
| **Disabled** | `IsEnabled="False"` | Reduced opacity or muted colors, no interaction feedback |

## Verification Process

Choose affected controls and consumers of changed styles. Cover all pages only for a comprehensive audit or application-wide style changes.

1. Launch the app and navigate to the selected surfaces.
2. For each selected interactive control (Button, ToggleButton, CheckBox, RadioButton, ComboBox, ListView items, etc.):
   - Hover the mouse over it. Confirm a visual change.
   - Click/press it. Confirm a distinct pressed appearance.
   - Tab to it with the keyboard. Confirm a focus rectangle appears.
   - Inspect naturally disabled controls or an existing test harness. When edits are authorized, a temporary test fixture may set `IsEnabled="False"`; remove temporary changes afterward. Confirm a visually distinct disabled state.
3. Repeat in both Light and Dark themes.

## VisualStateManager Patterns

### Basic VisualStateGroup

```xml
<VisualStateManager.VisualStateGroups>
    <VisualStateGroup x:Name="CommonStates">
        <VisualState x:Name="Normal" />

        <VisualState x:Name="PointerOver">
            <VisualState.Setters>
                <Setter Target="RootGrid.Background"
                        Value="{ThemeResource SubtleFillColorSecondaryBrush}" />
            </VisualState.Setters>
        </VisualState>

        <VisualState x:Name="Pressed">
            <VisualState.Setters>
                <Setter Target="RootGrid.Background"
                        Value="{ThemeResource SubtleFillColorTertiaryBrush}" />
            </VisualState.Setters>
        </VisualState>

        <VisualState x:Name="Disabled">
            <VisualState.Setters>
                <Setter Target="RootGrid.Opacity" Value="0.5" />
            </VisualState.Setters>
        </VisualState>
    </VisualStateGroup>

    <VisualStateGroup x:Name="FocusStates">
        <VisualState x:Name="Unfocused" />

        <VisualState x:Name="Focused">
            <VisualState.Setters>
                <Setter Target="FocusBorder.Visibility" Value="Visible" />
            </VisualState.Setters>
        </VisualState>
    </VisualStateGroup>
</VisualStateManager.VisualStateGroups>
```

### Using Storyboard animations (for transitions)

```xml
<VisualState x:Name="PointerOver">
    <Storyboard>
        <ObjectAnimationUsingKeyFrames
            Storyboard.TargetName="RootGrid"
            Storyboard.TargetProperty="Background">
            <DiscreteObjectKeyFrame KeyTime="0"
                Value="{ThemeResource SubtleFillColorSecondaryBrush}" />
        </ObjectAnimationUsingKeyFrames>
    </Storyboard>
</VisualState>
```

## Common Fix Patterns

### Button missing PointerOver state

**Symptom:** Hovering over a custom-styled button shows no change.

**Fix:** Add PointerOver VisualState with Setters targeting the background.

```xml
<Style x:Key="SubtleButtonStyle" TargetType="Button">
    <Setter Property="Background" Value="Transparent" />
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="Button">
                <Grid x:Name="RootGrid"
                      Background="{TemplateBinding Background}"
                      Padding="{TemplateBinding Padding}"
                      CornerRadius="{StaticResource ControlCornerRadius}">

                    <VisualStateManager.VisualStateGroups>
                        <VisualStateGroup x:Name="CommonStates">
                            <VisualState x:Name="Normal" />
                            <VisualState x:Name="PointerOver">
                                <VisualState.Setters>
                                    <Setter Target="RootGrid.Background"
                                            Value="{ThemeResource SubtleFillColorSecondaryBrush}" />
                                </VisualState.Setters>
                            </VisualState>
                            <VisualState x:Name="Pressed">
                                <VisualState.Setters>
                                    <Setter Target="RootGrid.Background"
                                            Value="{ThemeResource SubtleFillColorTertiaryBrush}" />
                                </VisualState.Setters>
                            </VisualState>
                            <VisualState x:Name="Disabled">
                                <VisualState.Setters>
                                    <Setter Target="ContentPresenter.Foreground"
                                            Value="{ThemeResource TextFillColorDisabledBrush}" />
                                </VisualState.Setters>
                            </VisualState>
                        </VisualStateGroup>
                    </VisualStateManager.VisualStateGroups>

                    <ContentPresenter
                        x:Name="ContentPresenter"
                        Content="{TemplateBinding Content}"
                        HorizontalAlignment="Center"
                        VerticalAlignment="Center" />
                </Grid>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```

### No focus rectangle

**Symptom:** Tabbing to a control shows no focus indicator.

**Fix:** Set focus visual properties on the control. WinUI 3 provides built-in focus visuals via `UseSystemFocusVisuals`.

```xml
<Button Content="Click me"
        UseSystemFocusVisuals="True"
        FocusVisualPrimaryBrush="{ThemeResource FocusStrokeColorOuterBrush}"
        FocusVisualSecondaryBrush="{ThemeResource FocusStrokeColorInnerBrush}"
        FocusVisualPrimaryThickness="2"
        FocusVisualSecondaryThickness="1" />
```

For custom controls that override the template, ensure `UseSystemFocusVisuals` is set to `True` in the style:

```xml
<Setter Property="UseSystemFocusVisuals" Value="True" />
<Setter Property="FocusVisualMargin" Value="-3" />
```

### Disabled state looks same as default

**Symptom:** A control with `IsEnabled="False"` is visually indistinguishable from its enabled state.

**Fix:** Add a Disabled VisualState that changes opacity or foreground color.

```xml
<VisualState x:Name="Disabled">
    <VisualState.Setters>
        <Setter Target="RootGrid.Opacity" Value="0.4" />
        <Setter Target="ContentText.Foreground"
                Value="{ThemeResource TextFillColorDisabledBrush}" />
    </VisualState.Setters>
</VisualState>
```

## Full Button ControlTemplate Reference

A complete template for a standard Button with all visual states, suitable as a starting point for custom button styles.

```xml
<Style x:Key="PolishedButtonStyle" TargetType="Button">
    <Setter Property="Background" Value="{ThemeResource ControlFillColorDefaultBrush}" />
    <Setter Property="Foreground" Value="{ThemeResource TextFillColorPrimaryBrush}" />
    <Setter Property="BorderBrush" Value="{ThemeResource ControlStrokeColorDefaultBrush}" />
    <Setter Property="BorderThickness" Value="1" />
    <Setter Property="Padding" Value="12,6,12,6" />
    <Setter Property="HorizontalAlignment" Value="Left" />
    <Setter Property="VerticalAlignment" Value="Center" />
    <Setter Property="CornerRadius" Value="{StaticResource ControlCornerRadius}" />
    <Setter Property="UseSystemFocusVisuals" Value="True" />
    <Setter Property="FocusVisualMargin" Value="-3" />
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="Button">
                <Grid x:Name="RootGrid"
                      Background="{TemplateBinding Background}"
                      BorderBrush="{TemplateBinding BorderBrush}"
                      BorderThickness="{TemplateBinding BorderThickness}"
                      CornerRadius="{TemplateBinding CornerRadius}"
                      Padding="{TemplateBinding Padding}">

                    <VisualStateManager.VisualStateGroups>
                        <VisualStateGroup x:Name="CommonStates">
                            <VisualState x:Name="Normal" />

                            <VisualState x:Name="PointerOver">
                                <VisualState.Setters>
                                    <Setter Target="RootGrid.Background"
                                            Value="{ThemeResource ControlFillColorSecondaryBrush}" />
                                    <Setter Target="ContentPresenter.Foreground"
                                            Value="{ThemeResource TextFillColorPrimaryBrush}" />
                                </VisualState.Setters>
                            </VisualState>

                            <VisualState x:Name="Pressed">
                                <VisualState.Setters>
                                    <Setter Target="RootGrid.Background"
                                            Value="{ThemeResource ControlFillColorTertiaryBrush}" />
                                    <Setter Target="ContentPresenter.Foreground"
                                            Value="{ThemeResource TextFillColorSecondaryBrush}" />
                                </VisualState.Setters>
                            </VisualState>

                            <VisualState x:Name="Disabled">
                                <VisualState.Setters>
                                    <Setter Target="RootGrid.Background"
                                            Value="{ThemeResource ControlFillColorDisabledBrush}" />
                                    <Setter Target="RootGrid.BorderBrush"
                                            Value="{ThemeResource ControlStrokeColorDefaultBrush}" />
                                    <Setter Target="ContentPresenter.Foreground"
                                            Value="{ThemeResource TextFillColorDisabledBrush}" />
                                </VisualState.Setters>
                            </VisualState>
                        </VisualStateGroup>
                    </VisualStateManager.VisualStateGroups>

                    <ContentPresenter
                        x:Name="ContentPresenter"
                        Content="{TemplateBinding Content}"
                        ContentTemplate="{TemplateBinding ContentTemplate}"
                        HorizontalContentAlignment="{TemplateBinding HorizontalContentAlignment}"
                        VerticalContentAlignment="{TemplateBinding VerticalContentAlignment}" />
                </Grid>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```

## References

- [VisualStateManager class](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.visualstatemanager)
- [Control templates](https://learn.microsoft.com/en-us/windows/apps/develop/platform/xaml/xaml-control-templates)
- [Visual feedback guidelines](https://learn.microsoft.com/en-us/windows/apps/develop/input/guidelines-for-visualfeedback)
- [Keyboard accessibility / focus visuals](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/keyboard-accessibility)
- [Storyboarded animations](https://learn.microsoft.com/en-us/windows/apps/design/motion/storyboarded-animations)
- [XAML property animations](https://learn.microsoft.com/en-us/windows/apps/design/motion/xaml-property-animations)
