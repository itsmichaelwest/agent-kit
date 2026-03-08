<#
.SYNOPSIS
    Lists visible windows or captures a screenshot of a specific window on Windows.

.DESCRIPTION
    -List: Enumerates all visible windows with process name, title, PID, and dimensions.
    -ProcessName / -WindowTitle: Captures a window to a PNG file.
    Uses Win32 PrintWindow for accurate capture (handles off-screen/occluded windows).
    Falls back to BitBlt screen capture if PrintWindow fails.

.PARAMETER List
    List all visible windows with their process name, title, PID, and size.

.PARAMETER ProcessName
    Process name to find (e.g. "MyApp", "devenv"). Takes the first matching window.

.PARAMETER WindowTitle
    Substring match against window titles. Takes the first match.

.PARAMETER OutputPath
    Path for the output PNG file. Defaults to ./screenshot.png

.PARAMETER Delay
    Seconds to wait before capturing (e.g. to let UI settle). Default: 0

.EXAMPLE
    .\capture-window.ps1 -List
    .\capture-window.ps1 -ProcessName "Range" -OutputPath ./before.png
    .\capture-window.ps1 -WindowTitle "MainWindow" -OutputPath ./after.png -Delay 2
#>

param(
    [Parameter(ParameterSetName = 'ListWindows')]
    [switch]$List,

    [Parameter(ParameterSetName = 'ByProcess')]
    [string]$ProcessName,

    [Parameter(ParameterSetName = 'ByTitle')]
    [string]$WindowTitle,

    [string]$OutputPath = "./screenshot.png",

    [int]$Delay = 0
)

Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public class WindowCapture
{
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("user32.dll")]
    public static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll")]
    public static extern IntPtr CreateCompatibleDC(IntPtr hdc);

    [DllImport("gdi32.dll")]
    public static extern IntPtr CreateCompatibleBitmap(IntPtr hdc, int nWidth, int nHeight);

    [DllImport("gdi32.dll")]
    public static extern IntPtr SelectObject(IntPtr hdc, IntPtr hgdiobj);

    [DllImport("gdi32.dll")]
    public static extern bool DeleteObject(IntPtr hObject);

    [DllImport("gdi32.dll")]
    public static extern bool DeleteDC(IntPtr hdc);

    [DllImport("gdi32.dll")]
    public static extern bool BitBlt(IntPtr hdcDest, int xDest, int yDest,
        int wDest, int hDest, IntPtr hdcSrc, int xSrc, int ySrc, uint rop);

    [DllImport("dwmapi.dll")]
    public static extern int DwmGetWindowAttribute(IntPtr hwnd, int dwAttribute,
        out RECT pvAttribute, int cbAttribute);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left, Top, Right, Bottom;
    }

    // PW_RENDERFULLCONTENT = 2 (captures DirectComposition/XAML content)
    private const uint PW_RENDERFULLCONTENT = 2;
    private const uint SRCCOPY = 0x00CC0020;
    // DWMWA_EXTENDED_FRAME_BOUNDS = 9
    private const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;

    public static void Capture(IntPtr hWnd, string outputPath)
    {
        // Use DWM extended frame bounds for accurate size (excludes invisible borders)
        RECT rect;
        int hr = DwmGetWindowAttribute(hWnd, DWMWA_EXTENDED_FRAME_BOUNDS,
            out rect, Marshal.SizeOf(typeof(RECT)));
        if (hr != 0)
        {
            GetWindowRect(hWnd, out rect);
        }

        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;

        if (width <= 0 || height <= 0)
            throw new InvalidOperationException(
                $"Invalid window dimensions: {width}x{height}");

        using (var bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb))
        {
            using (var gfx = Graphics.FromImage(bmp))
            {
                IntPtr hdc = gfx.GetHdc();
                bool ok = PrintWindow(hWnd, hdc, PW_RENDERFULLCONTENT);
                gfx.ReleaseHdc(hdc);

                if (!ok)
                {
                    // Fallback: BitBlt from screen
                    IntPtr screenDC = GetDC(IntPtr.Zero);
                    hdc = gfx.GetHdc();
                    BitBlt(hdc, 0, 0, width, height,
                        screenDC, rect.Left, rect.Top, SRCCOPY);
                    gfx.ReleaseHdc(hdc);
                    ReleaseDC(IntPtr.Zero, screenDC);
                }
            }

            string dir = System.IO.Path.GetDirectoryName(
                System.IO.Path.GetFullPath(outputPath));
            if (!string.IsNullOrEmpty(dir))
                System.IO.Directory.CreateDirectory(dir);

            bmp.Save(outputPath, ImageFormat.Png);
        }
    }
}
"@ -ReferencedAssemblies System.Drawing, System.Drawing.Primitives, System.Runtime.InteropServices -ErrorAction Stop

# --- List all visible windows ---

if ($List) {
    Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

public class WindowLister
{
    [DllImport("user32.dll")]
    static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("dwmapi.dll")]
    static extern int DwmGetWindowAttribute(IntPtr hwnd, int dwAttribute,
        out RECT pvAttribute, int cbAttribute);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public struct WindowInfo
    {
        public string ProcessName;
        public string Title;
        public uint PID;
        public int Width;
        public int Height;
        public int X;
        public int Y;
    }

    public static List<WindowInfo> GetVisibleWindows()
    {
        var results = new List<WindowInfo>();
        EnumWindows((hWnd, _) =>
        {
            if (!IsWindowVisible(hWnd)) return true;

            int len = GetWindowTextLength(hWnd);
            if (len == 0) return true;

            var sb = new StringBuilder(len + 1);
            GetWindowText(hWnd, sb, sb.Capacity);
            string title = sb.ToString();

            uint pid;
            GetWindowThreadProcessId(hWnd, out pid);

            string procName = "";
            try { procName = Process.GetProcessById((int)pid).ProcessName; }
            catch { return true; }

            RECT rect;
            int hr = DwmGetWindowAttribute(hWnd, 9, out rect, Marshal.SizeOf(typeof(RECT)));
            if (hr != 0) GetWindowRect(hWnd, out rect);

            int w = rect.Right - rect.Left;
            int h = rect.Bottom - rect.Top;
            if (w <= 0 || h <= 0) return true;

            results.Add(new WindowInfo {
                ProcessName = procName,
                Title = title,
                PID = pid,
                Width = w, Height = h,
                X = rect.Left, Y = rect.Top
            });
            return true;
        }, IntPtr.Zero);
        return results;
    }
}
"@ -ReferencedAssemblies System.Diagnostics.Process, System.Runtime.InteropServices -ErrorAction Stop

    $windows = [WindowLister]::GetVisibleWindows()
    if ($windows.Count -eq 0) {
        Write-Host "No visible windows found"
        exit 0
    }

    # Table output
    $fmt = "{0,-24} | {1,-50} | {2,6} | {3}"
    Write-Host ($fmt -f "Process", "Title", "PID", "Size")
    Write-Host ("-" * 100)
    foreach ($w in ($windows | Sort-Object { $_.ProcessName })) {
        $title = if ($w.Title.Length -gt 50) { $w.Title.Substring(0, 47) + "..." } else { $w.Title }
        Write-Host ($fmt -f $w.ProcessName, $title, $w.PID, "$($w.Width)x$($w.Height) @ $($w.X),$($w.Y)")
    }
    exit 0
}

# --- Find the target window ---

$hwnd = [IntPtr]::Zero

if ($ProcessName) {
    $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } |
        Select-Object -First 1
    if (-not $proc) {
        Write-Error "No visible window found for process '$ProcessName'"
        exit 1
    }
    $hwnd = $proc.MainWindowHandle
    Write-Host "Found: $($proc.MainWindowTitle) (PID $($proc.Id))"
}
elseif ($WindowTitle) {
    $proc = Get-Process |
        Where-Object {
            $_.MainWindowHandle -ne [IntPtr]::Zero -and
            $_.MainWindowTitle -like "*$WindowTitle*"
        } |
        Select-Object -First 1
    if (-not $proc) {
        Write-Error "No window matching title '*$WindowTitle*'"
        exit 1
    }
    $hwnd = $proc.MainWindowHandle
    Write-Host "Found: $($proc.MainWindowTitle) (PID $($proc.Id))"
}
else {
    Write-Error "Specify -ProcessName or -WindowTitle"
    exit 1
}

if ($Delay -gt 0) {
    Write-Host "Waiting ${Delay}s..."
    Start-Sleep -Seconds $Delay
}

# --- Capture ---

$resolvedPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
[WindowCapture]::Capture($hwnd, $resolvedPath)

$size = (Get-Item $resolvedPath).Length
Write-Host "Saved: $resolvedPath ($([math]::Round($size / 1KB, 1)) KB)"
