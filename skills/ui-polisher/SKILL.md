---
name: ui-polisher
description: Capture screenshots of running applications for visual review and comparison. Works across web (Playwright), Windows (WinUI/WPF), macOS, and iOS/watchOS Simulator. Use when asked to "capture", "screenshot", "polish UI", "compare screenshots", or "check the UI".
---

# UI Polisher

Capture and compare screenshots of running applications across platforms. All scripts live in `scripts/` relative to this skill.

## Scripts

### List Windows

Always list available windows first to get exact identifiers for capture.

**Web:**
Use Playwright MCP `browser_tabs` to see open pages.

**Windows:**
```powershell
pwsh scripts/capture-window.ps1 -List
```
Output: process name, title, PID, and dimensions for all visible windows.

**macOS:**
```bash
bash scripts/capture-window.sh --list
```
Output: process name, window title, PID, window ID, and dimensions.

On first use, macOS may prompt for accessibility permission (for window titles). Approve once — it persists.

### List Simulators (macOS only)

```bash
bash scripts/capture-window.sh --list-simulators
```
Output: device name, runtime, UDID, and device type for booted simulators.

### Capture Screenshots

**Web (Playwright MCP):**
```
browser_navigate → target URL
browser_take_screenshot
```

**Windows:**
```powershell
# By process name
pwsh scripts/capture-window.ps1 -ProcessName "AppName" -OutputPath ./before.png

# By window title substring
pwsh scripts/capture-window.ps1 -WindowTitle "MainWindow" -OutputPath ./before.png

# With delay (seconds) to let UI settle
pwsh scripts/capture-window.ps1 -ProcessName "AppName" -OutputPath ./before.png -Delay 2
```

**macOS app:**
```bash
bash scripts/capture-window.sh --app "AppName" --output ./before.png
bash scripts/capture-window.sh --app "AppName" --output ./before.png --delay 2
```

**iOS/watchOS Simulator:**
```bash
# First booted simulator
bash scripts/capture-window.sh --simulator --output ./before.png

# Specific device by UDID (from --list-simulators)
bash scripts/capture-window.sh --simulator --device <UDID> --output ./before.png
```

## Before/After Comparison

1. Capture "before": `--output /tmp/ui-polish/before.png`
2. Make changes
3. Capture "after": `--output /tmp/ui-polish/after.png`
4. Read both images to compare visually

## Platform Detection

Determine which capture method to use from project files:

| Signal | Platform | Method |
|--------|----------|--------|
| `package.json` with next/react/vue | Web | Playwright MCP |
| `*.csproj` with Blazor | Web | Playwright MCP |
| `*.csproj` with WinUI/WPF/MAUI | Windows | `capture-window.ps1` |
| `*.xcodeproj`, `Package.swift` | iOS/watchOS/macOS | `capture-window.sh` |
