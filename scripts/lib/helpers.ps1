# Shared helpers: logging and symlink logic.

function Write-Info  { param($Msg) Write-Host "[INFO] $Msg" -ForegroundColor Green }
function Write-Warn  { param($Msg) Write-Host "[WARN] $Msg" -ForegroundColor Yellow }
function Write-Err   { param($Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }

function Remove-Link {
    param([string]$Target)

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $Target -Force
            Write-Host "  [REMOVED] $Target"

            # Restore the most recent backup created by Ensure-Linked
            $backups = Get-ChildItem -Path (Split-Path -Parent $Target) -Filter "$(Split-Path -Leaf $Target).backup.*" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending
            if ($backups) {
                Move-Item $backups[0].FullName $Target
                Write-Host "  [RESTORED] $Target (from $($backups[0].Name))"
            }
        } else {
            Write-Warn "Not a symlink, skipping: $Target"
        }
    }
}

function Ensure-Linked {
    param([string]$Source, [string]$Target)

    if (-not (Test-Path $Source)) { return }

    $targetParent = Split-Path -Parent $Target
    [System.IO.Directory]::CreateDirectory($targetParent) | Out-Null

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            if ($item.Target -eq $Source) {
                Write-Host "  [SKIP] $Target"
                return
            }
            Remove-Item $Target -Force
        } else {
            $backup = "$Target.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Move-Item $Target $backup
            Write-Info "Backed up: $Target -> $backup"
        }
    }

    $sourceItem = Get-Item $Source -Force
    if ($sourceItem.PSIsContainer) {
        New-Item -ItemType Junction -Path $Target -Target $Source -Force | Out-Null
        Write-Host "  [LINK] $Source -> $Target"
    } else {
        try {
            New-Item -ItemType SymbolicLink -Path $Target -Target $Source -Force | Out-Null
            Write-Host "  [LINK] $Source -> $Target"
        } catch {
            # File symlinks need Developer Mode or elevation — try gsudo, then copy
            if (Get-Command gsudo -ErrorAction SilentlyContinue) {
                Write-Info "Elevating to create symlink..."
                gsudo New-Item -ItemType SymbolicLink -Path $Target -Target $Source -Force | Out-Null
                Write-Host "  [LINK] $Source -> $Target (elevated)"
            } else {
                Copy-Item $Source $Target -Force
                Write-Host "  [COPY] $Source -> $Target" -ForegroundColor Yellow
                Write-Warn "Install gsudo (winget install gerardog.gsudo) or enable Developer Mode for symlinks"
            }
        }
    }
}
