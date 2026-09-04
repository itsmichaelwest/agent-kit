---
name: ui-polisher
description: Capture screenshots of running applications for visual review and comparison. Works across web (Playwright), Windows (WinUI/WPF), macOS, and iOS/watchOS Simulator. Use when asked to "capture", "screenshot", "polish UI", "compare screenshots", or "check the UI".
---

# UI Polisher

Capture and compare screenshots of running applications across platforms. All scripts live in `scripts/` relative to this skill.

For capture, audit, or comparison requests, inspect and report without changing application source. Apply fixes only when requested, then capture the affected state again. Use supplied images directly when they provide the evidence needed.

Resolve script paths from this `SKILL.md` directory, not the project working directory. Use the host's shell and a writable output directory; examples below use skill-relative paths. Discover the available browser or capture tool and follow its documented interface. Playwright MCP names below apply only when that tool is available.

## Scripts

### List Windows

For a new capture, identify the intended window or tab. List available targets when its identity is not already established.

**Web:**
Use the available browser tool's tab inventory (for example, Playwright MCP `browser_tabs`).

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

1. Use supplied before/after images, or capture the baseline in the selected output directory.
2. When fixes are requested, make the scoped changes and capture the same window, theme, scale, and state again.
3. Open both images and compare the affected region. Use crop or zoom when available for small details.
4. Report visible differences and any missing evidence. A saved file alone does not prove a useful capture; inspect for black frames, occlusion, incorrect bounds, or scaling artifacts. UI Automation can verify exposed content but does not replace pixel inspection.

Complete when the requested captures or comparison are delivered and their limits are stated. If capture is unavailable, continue any useful source or supplied-image review and name the missing capability.

## Platform Detection

Determine which capture method to use from project files:

| Signal | Platform | Method |
|--------|----------|--------|
| `package.json` with next/react/vue | Web | Playwright MCP |
| `*.csproj` with Blazor | Web | Playwright MCP |
| `*.csproj` with WinUI/WPF/MAUI | Windows | `capture-window.ps1` |
| `*.xcodeproj`, `Package.swift` | iOS/watchOS/macOS | `capture-window.sh` |
