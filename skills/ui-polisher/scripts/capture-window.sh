#!/usr/bin/env bash
# capture-window.sh — List windows or capture a screenshot on macOS / iOS Simulator
#
# Usage:
#   ./capture-window.sh --list                                     List all visible windows
#   ./capture-window.sh --list-simulators                          List booted simulators
#   ./capture-window.sh --app "App Name" [--output path.png] [--delay N]
#   ./capture-window.sh --simulator [--device UDID] [--output path.png] [--delay N]
#   ./capture-window.sh --url "http://..." --output path.png      (requires Playwright MCP)
#
# Examples:
#   ./capture-window.sh --list
#   ./capture-window.sh --app "Range" --output before.png
#   ./capture-window.sh --simulator --output watch.png
#   ./capture-window.sh --app "Safari" --delay 2

set -euo pipefail

APP_NAME=""
SIMULATOR=false
LIST=false
LIST_SIMS=false
DEVICE=""
OUTPUT="./screenshot.png"
DELAY=0
URL=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --app)             APP_NAME="$2"; shift 2 ;;
        --simulator)       SIMULATOR=true; shift ;;
        --device)          DEVICE="$2"; shift 2 ;;
        --list)            LIST=true; shift ;;
        --list-simulators) LIST_SIMS=true; shift ;;
        --output)          OUTPUT="$2"; shift 2 ;;
        --delay)           DELAY="$2"; shift 2 ;;
        --url)             URL="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,10p' "$0"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# --- List all visible windows ---
if $LIST; then
    if [[ "$(uname)" != "Darwin" ]]; then
        echo "Error: --list only works on macOS" >&2
        exit 1
    fi
    # Step 1: Get window geometry via CoreGraphics (no permissions needed)
    # Step 2: Get window titles via AppleScript (uses accessibility — may prompt once)
    # Merges both sources by PID for best results

    swift -e '
import CoreGraphics
import Foundation

// --- CoreGraphics: window geometry (always works, titles may be empty) ---
let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
guard let windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] else {
    print("No visible windows found")
    exit(0)
}

struct WinInfo {
    var proc: String
    var title: String
    var pid: Int
    var winId: Int
    var w: Int
    var h: Int
    var x: Int
    var y: Int
}

var windows: [WinInfo] = []
for w in windowList {
    let layer = w[kCGWindowLayer as String] as? Int ?? -1
    let bounds = w[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let width = bounds["Width"] as? Int ?? 0
    let height = bounds["Height"] as? Int ?? 0
    guard layer == 0, width > 50, height > 50 else { continue }

    windows.append(WinInfo(
        proc: w[kCGWindowOwnerName as String] as? String ?? "",
        title: w[kCGWindowName as String] as? String ?? "",
        pid: w[kCGWindowOwnerPID as String] as? Int ?? 0,
        winId: w[kCGWindowNumber as String] as? Int ?? 0,
        w: width, h: height,
        x: bounds["X"] as? Int ?? 0,
        y: bounds["Y"] as? Int ?? 0
    ))
}

if windows.isEmpty {
    print("No visible windows found")
    exit(0)
}

// --- AppleScript: get window titles (fills in blanks from CG) ---
// Only attempt for unique process names that have empty titles
let procsNeedingTitles = Set(windows.filter { $0.title.isEmpty }.map { $0.proc })
var titlesByProc: [String: [String]] = [:]

for proc in procsNeedingTitles {
    let script = "tell application \"System Events\" to tell process \"\(proc)\" to get name of every window"
    let task = Process()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    task.arguments = ["-e", script]
    let pipe = Pipe()
    task.standardOutput = pipe
    task.standardError = FileHandle.nullDevice
    do {
        try task.run()
        task.waitUntilExit()
        if task.terminationStatus == 0 {
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines), !output.isEmpty {
                // AppleScript returns "title1, title2, ..."
                titlesByProc[proc] = output.components(separatedBy: ", ")
            }
        }
    } catch {}
}

// Merge: fill in empty CG titles with AppleScript titles (by order per process)
var procTitleIndex: [String: Int] = [:]
for i in 0..<windows.count {
    if windows[i].title.isEmpty, let titles = titlesByProc[windows[i].proc] {
        let idx = procTitleIndex[windows[i].proc, default: 0]
        if idx < titles.count {
            windows[i].title = titles[idx]
        }
        procTitleIndex[windows[i].proc] = idx + 1
    }
}

// --- Output ---
print("Process                  | Title                                              |    PID |  WinID | Size")
print(String(repeating: "-", count: 110))
for r in windows {
    var title = r.title
    if title.count > 50 { title = String(title.prefix(47)) + "..." }
    let procPad = r.proc.padding(toLength: 24, withPad: " ", startingAt: 0)
    let titlePad = title.padding(toLength: 50, withPad: " ", startingAt: 0)
    print("\(procPad) | \(titlePad) | \(String(r.pid).leftPad(6)) | \(String(r.winId).leftPad(6)) | \(r.w)x\(r.h) @ \(r.x),\(r.y)")
}

extension String {
    func leftPad(_ length: Int) -> String {
        if self.count >= length { return self }
        return String(repeating: " ", count: length - self.count) + self
    }
}
' 2>&1
    exit 0
fi

# --- List booted simulators ---
if $LIST_SIMS; then
    xcrun simctl list devices booted -j 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
found = False
for runtime, devices in data.get('devices', {}).items():
    # Extract readable runtime name (e.g. 'iOS 26.0' from 'com.apple.CoreSimulator.SimRuntime.iOS-26-0')
    rt = runtime.rsplit('.', 1)[-1].replace('-', ' ').replace('  ', ' ')
    for d in devices:
        if d.get('state') == 'Booted':
            found = True
            print(f\"{d['name']} | {rt} | {d['udid']} | {d.get('deviceTypeIdentifier','').rsplit('.',1)[-1]}\")
if not found:
    print('No booted simulators found')
    sys.exit(1)
"
    exit 0
fi

mkdir -p "$(dirname "$OUTPUT")"

if [[ $DELAY -gt 0 ]]; then
    echo "Waiting ${DELAY}s..."
    sleep "$DELAY"
fi

# --- iOS/watchOS Simulator ---
if $SIMULATOR; then
    if [[ -n "$DEVICE" ]]; then
        BOOTED="$DEVICE"
    else
        BOOTED=$(xcrun simctl list devices booted -j 2>/dev/null | \
            python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data.get('devices', {}).items():
    for d in devices:
        if d.get('state') == 'Booted':
            print(d['udid'])
            sys.exit(0)
sys.exit(1)
" 2>/dev/null) || {
            echo "Error: No booted simulator found. Use --list-simulators to see available devices." >&2
            exit 1
        }
    fi
    xcrun simctl io "$BOOTED" screenshot --type=png "$OUTPUT"
    echo "Saved simulator screenshot: $OUTPUT ($(du -h "$OUTPUT" | cut -f1) )"
    exit 0
fi

# --- Web URL (prints instructions for Playwright MCP) ---
if [[ -n "$URL" ]]; then
    echo "Web screenshots require Playwright MCP. Use:"
    echo "  1. browser_navigate to '$URL'"
    echo "  2. browser_take_screenshot"
    echo "  (or use the webapp-testing skill)"
    exit 0
fi

# --- macOS App Window ---
if [[ -n "$APP_NAME" ]]; then
    if [[ "$(uname)" != "Darwin" ]]; then
        echo "Error: macOS app capture only works on macOS" >&2
        exit 1
    fi

    # Get the window ID using AppleScript
    WINDOW_ID=$(osascript -e "
        tell application \"System Events\"
            set targetProc to first process whose name is \"$APP_NAME\"
            set targetWindow to first window of targetProc
            return id of targetWindow
        end tell
    " 2>/dev/null) || {
        # Fallback: try to find by bundle name / partial match
        WINDOW_ID=$(osascript -e "
            tell application \"System Events\"
                repeat with p in (every process whose background only is false)
                    if name of p contains \"$APP_NAME\" then
                        set targetWindow to first window of p
                        return id of targetWindow
                    end if
                end repeat
            end tell
        " 2>/dev/null) || {
            echo "Error: No window found for app '$APP_NAME'" >&2
            echo "Running GUI apps:" >&2
            osascript -e '
                tell application "System Events"
                    set appList to name of every process whose background only is false
                    return appList
                end tell
            ' 2>/dev/null >&2
            exit 1
        }
    }

    screencapture -l "$WINDOW_ID" -o "$OUTPUT"
    echo "Saved: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
    exit 0
fi

echo "Error: Specify --app, --simulator, or --url" >&2
exit 1
