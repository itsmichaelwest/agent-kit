# Issue Taxonomy

Seven categories for classifying WinUI 3 visual polish defects. Use this file as the audit checklist before applying fixes from the category-specific reference files.

## Severity Levels

- **Critical** — Broken UX. The user cannot read content, interact with a control, or the app looks fundamentally wrong (e.g., white text on white background in dark mode).
- **Major** — Noticeable. A reasonable user would spot the issue and perceive the app as unfinished (e.g., Mica not applied, hardcoded light-only color visible in dark mode).
- **Minor** — Polish. Only noticeable on close inspection or side-by-side comparison with a correct implementation (e.g., 10px margin instead of 8px, slightly inconsistent corner radius).

---

## 1. Materials

Mica, MicaAlt, or Acrylic backdrop is missing, falls back to a solid color, or does not extend through the title bar.

**Common symptoms:**
- Window background is a flat solid color instead of showing the desktop wallpaper tint.
- Title bar area has a different background from the rest of the window.
- Backdrop works in one theme but not the other.

**Severity guidance:**
- Critical: No backdrop on the main window when the design requires one.
- Major: Backdrop present but does not extend into the title bar, or fallback is a jarring solid color.
- Minor: Backdrop type is slightly wrong (e.g., Mica instead of MicaAlt) but still looks acceptable.

**Quick audit checklist:**
- [ ] Does the window have a `SystemBackdrop` property set?
- [ ] Does the backdrop show through the title bar area?
- [ ] On an unsupported system, does the fallback look acceptable?

---

## 2. Theme

Hardcoded colors that do not respond to Light/Dark/HighContrast theme changes.

**Common symptoms:**
- Text or icons become invisible when switching themes.
- A control has a hardcoded `Background`, `Foreground`, or `BorderBrush` that ignores the current theme.
- HighContrast mode shows broken contrast or missing elements.

**Severity guidance:**
- Critical: Content is invisible or unreadable in one theme.
- Major: Color is visibly wrong but content is still readable.
- Minor: A non-primary element uses a slightly off shade.

**Quick audit checklist:**
- [ ] Are there any hardcoded `#RRGGBB` or `Color` values in XAML (outside of theme dictionaries)?
- [ ] Does every visible surface respond correctly to Light, Dark, and HighContrast?
- [ ] Are all color references using `{ThemeResource ...}` or theme-aware `{StaticResource ...}`?

---

## 3. Corner Radius

Inconsistent corner radii or hardcoded values instead of system resources.

**Common symptoms:**
- Adjacent controls have visibly different corner radii.
- A card or container uses a hardcoded `CornerRadius="5"` instead of the system token.
- Nested elements have conflicting radii, creating visual clipping or gaps.

**Severity guidance:**
- Critical: Severe visual clipping caused by mismatched radii.
- Major: Visibly inconsistent radii on prominent controls or containers.
- Minor: Slightly off radius on a secondary element.

**Quick audit checklist:**
- [ ] Are all `CornerRadius` values using `{StaticResource ControlCornerRadius}` or `{StaticResource OverlayCornerRadius}`?
- [ ] Do nested elements have compatible radii (inner radius = outer radius - border thickness)?
- [ ] Are adjacent cards/containers using the same radius resource?

---

## 4. Spacing

Off-ramp padding, margins, or gaps that do not follow the WinUI spacing scale.

**Common symptoms:**
- Uneven spacing between controls or sections.
- Hardcoded margins like `Margin="10"` or `Margin="15"` that are not on the 4px ramp.
- Inconsistent padding between similar containers on the same page.

**Severity guidance:**
- Critical: Spacing causes content to overlap or be clipped.
- Major: Noticeably uneven spacing between similar elements.
- Minor: Spacing is slightly off the ramp but visually acceptable.

**Quick audit checklist:**
- [ ] Do all Margin and Padding values snap to the ramp: 0, 4, 8, 12, 16, 24, 32, 48?
- [ ] Are equivalent containers using the same spacing values?
- [ ] Is the spacing between page sections consistent?

---

## 5. Visual States

Missing or broken PointerOver, Pressed, Focused, or Disabled states on interactive controls.

**Common symptoms:**
- Hovering over a button shows no visual change.
- A control has no visible focus indicator when navigating with keyboard.
- A disabled control looks the same as an enabled one.
- Pressed state is missing or uses the wrong color.

**Severity guidance:**
- Critical: No keyboard focus indicator on an interactive control (accessibility failure).
- Major: Missing PointerOver or Pressed state on a prominent button or control.
- Minor: Visual state exists but uses a slightly wrong brush.

**Quick audit checklist:**
- [ ] Does every interactive control show a visual change on hover?
- [ ] Does every interactive control show a focus rectangle when tabbed to?
- [ ] Do disabled controls look visually distinct from enabled ones?

---

## 6. Typography

Wrong TypeRamp resource, inconsistent font sizes, or hardcoded font properties instead of system text styles.

**Common symptoms:**
- Inline `FontSize="14"` or `FontWeight="SemiBold"` instead of a named style.
- Headings and body text using inconsistent sizes that do not follow the type ramp.
- Text that does not scale or respond correctly to accessibility text size settings.

**Severity guidance:**
- Critical: Text is too small to read or does not respect accessibility scaling.
- Major: Heading hierarchy is inconsistent or body text uses a non-standard size.
- Minor: One element uses an inline font property instead of the matching style.

**Quick audit checklist:**
- [ ] Are all TextBlock elements using a named `Style` (e.g., `BodyTextBlockStyle`, `SubtitleTextBlockStyle`)?
- [ ] Are inline `FontSize`, `FontWeight`, or `FontFamily` properties justified or should they be replaced with styles?
- [ ] Does the heading hierarchy flow logically (Title > Subtitle > Body)?

---

## 7. Icons

Wrong icon font, incorrect sizing, or hardcoded icon colors that break theme inheritance.

**Common symptoms:**
- Icons use `Segoe MDL2 Assets` instead of `Segoe Fluent Icons`.
- Icon sizes are arbitrary (e.g., `FontSize="18"`) instead of on the ramp (16, 20, 24, 32).
- Icons have a hardcoded `Foreground` that does not change with the theme.

**Severity guidance:**
- Critical: Icons are invisible or unreadable in one theme due to hardcoded color.
- Major: Wrong icon font is used throughout the app.
- Minor: One icon is slightly off the size ramp.

**Quick audit checklist:**
- [ ] Are all `FontIcon` elements using `FontFamily="Segoe Fluent Icons"`?
- [ ] Do icon `FontSize` values match the ramp: 16, 20, 24, 32?
- [ ] Do icons inherit their `Foreground` from the parent rather than hardcoding a color?

---

## Audit Worksheet Template

Copy and fill in for each window or page being audited.

```
Window/Page: _______________
Date: _______________
Theme tested: [ ] Light  [ ] Dark  [ ] HighContrast

| # | Category      | Element/Location | Description              | Severity | Fixed? |
|---|---------------|------------------|--------------------------|----------|--------|
| 1 |               |                  |                          |          |        |
| 2 |               |                  |                          |          |        |
| 3 |               |                  |                          |          |        |

Summary:
- Total defects: ___
- Critical: ___  Major: ___  Minor: ___
- Fixed this pass: ___
- Remaining: ___
```

## References

- [Windows app design overview](https://learn.microsoft.com/en-us/windows/apps/design/)
- [Fluent 2 Design System](https://fluent2.microsoft.design/)
- [WinUI Gallery](https://github.com/microsoft/WinUI-Gallery)
