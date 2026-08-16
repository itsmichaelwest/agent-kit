# Link/unlink AI agent configs using the JSON manifest (Windows).

function Get-AiAgentStateFile {
    $stateRoot = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { $env:USERPROFILE }
    return Join-Path $stateRoot "agent-kit\ai-agent-layout-version"
}

function Get-AiAgentManifest {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"
    if (-not (Test-Path $config)) { return $null }
    return Get-Content $config -Raw | ConvertFrom-Json
}

function Resolve-AiAgentTargetPath {
    param([string]$RawPath)

    return ($RawPath -replace '^~', $env:USERPROFILE) -replace '/', '\'
}

# Fingerprint the link topology. Document order, not sorted, so doctor-links.py
# and link-ai-agents.sh reproduce it without agreeing on a collation order.
# Formatting-only edits do not change it; adding, removing, or repointing a
# target does. Kept byte-identical across all three implementations.
function Get-AiAgentManifestDigest {
    param([object]$Manifest)

    $lines = foreach ($target in $Manifest.targets) {
        "{0}|{1}|{2}" -f $target.source, $Manifest.sources.($target.source), $target.path
    }

    $bytes = [Text.Encoding]::UTF8.GetBytes(($lines -join "`n"))
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($bytes)
    } finally {
        $sha.Dispose()
    }

    return ([BitConverter]::ToString($hash) -replace '-', '').ToLowerInvariant().Substring(0, 8)
}

function Get-AiAgentLayoutMarkerValue {
    param([object]$Manifest)

    $version = if ($Manifest.layoutVersion) { $Manifest.layoutVersion } else { "0" }
    return "{0}+{1}" -f $version, (Get-AiAgentManifestDigest $Manifest)
}

function Ensure-DirectoryTarget {
    param([string]$Target)

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $Target -Force
            Write-Host "  [MIGRATED] removed directory link $Target"
        } elseif (-not $item.PSIsContainer) {
            $backup = "$Target.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Move-Item $Target $backup
            Write-Info "Backed up: $Target -> $backup"
        }
    } else {
        [System.IO.Directory]::CreateDirectory($Target) | Out-Null
    }

    [System.IO.Directory]::CreateDirectory($Target) | Out-Null
}

function Get-LegacyAiAgentTargets {
    @(
        (Join-Path $env:USERPROFILE ".copilot\instructions.md")
    )
}

function Cleanup-LegacyAiAgentTargets {
    foreach ($target in Get-LegacyAiAgentTargets) {
        if (-not (Test-Path $target)) { continue }

        $item = Get-Item $target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $target -Force
            Write-Host "  [MIGRATED] removed legacy link $target"
        } else {
            $backup = "$target.legacy-backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Move-Item $target $backup
            Write-Info "Backed up legacy target: $target -> $backup"
        }
    }
}

function Write-AiAgentLayoutMarker {
    param([object]$Manifest)

    $marker = Get-AiAgentStateFile
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $marker)) | Out-Null
    Set-Content -Path $marker -Value (Get-AiAgentLayoutMarkerValue $Manifest) -NoNewline
}

function Link-ManifestAiTargets {
    param([string]$DotfilesDir, [object]$Manifest)

    foreach ($target in $Manifest.targets) {
        $sourceRel = $Manifest.sources.($target.source)
        if (-not $sourceRel) {
            Write-Warn "Unknown source key '$($target.source)', skipping"
            continue
        }

        $sourceAbs = Join-Path $DotfilesDir $sourceRel
        $targetPath = Resolve-AiAgentTargetPath $target.path

        if (-not (Test-Path $sourceAbs)) {
            Write-Warn "Missing source: $sourceAbs, skipping"
            continue
        }

        Ensure-Linked $sourceAbs $targetPath
    }
}

function Link-CopilotAgents {
    param([string]$DotfilesDir)

    $sourceDir = Join-Path $DotfilesDir "agents"
    $targetDir = Join-Path $env:USERPROFILE ".copilot\agents"

    if (-not (Test-Path $sourceDir)) {
        Write-Warn "Missing source directory: $sourceDir"
        return
    }

    Ensure-DirectoryTarget $targetDir

    Get-ChildItem -Path $targetDir -Filter "*.agent.agent.md" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "  [MIGRATED] removed stale $($_.FullName)"
    }

    Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Where-Object { $_.Name -notlike "*.agent.md" } | Sort-Object Name | ForEach-Object {
        $targetPath = Join-Path $targetDir ($_.BaseName + ".agent.md")
        Ensure-Linked $_.FullName $targetPath
    }
}

function Unlink-CopilotAgents {
    param([string]$DotfilesDir)

    $sourceDir = Join-Path $DotfilesDir "agents"
    $targetDir = Join-Path $env:USERPROFILE ".copilot\agents"

    if (-not (Test-Path $sourceDir)) { return }

    Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Where-Object { $_.Name -notlike "*.agent.md" } | Sort-Object Name | ForEach-Object {
        $targetPath = Join-Path $targetDir ($_.BaseName + ".agent.md")
        Remove-Link $targetPath
    }
}

function Show-TargetStatus {
    param([string]$TargetPath)

    if (Test-Path $TargetPath) {
        $item = Get-Item $TargetPath -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Host "  [OK] $TargetPath -> $($item.Target)" -ForegroundColor Green
        } else {
            Write-Host "  [EXISTS] $TargetPath (not a symlink)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [MISSING] $TargetPath" -ForegroundColor Red
    }
}

function Get-AiAgentLayoutStatus {
    param([string]$DotfilesDir)

    $marker = ""
    $markerFile = Get-AiAgentStateFile
    if (Test-Path $markerFile) {
        $marker = (Get-Content $markerFile -Raw).Trim()
    }

    $manifest = Get-AiAgentManifest $DotfilesDir
    if (-not $manifest) { return "unknown" }

    # Derived from the manifest, never a hand-maintained list: a target added to
    # ai-agent-links.json without a re-link must show up here.
    $currentTargets = @($manifest.targets | ForEach-Object { Resolve-AiAgentTargetPath $_.path })
    $currentTargets += (Join-Path $env:USERPROFILE ".copilot\agents")

    $expectedMarker = Get-AiAgentLayoutMarkerValue $manifest

    $currentOk = $true
    foreach ($target in $currentTargets) {
        if (-not (Test-Path $target)) {
            $currentOk = $false
            break
        }
    }

    $legacyPresent = $false
    foreach ($target in Get-LegacyAiAgentTargets) {
        if (Test-Path $target) {
            $legacyPresent = $true
            break
        }
    }

    if ($marker -eq $expectedMarker -and $currentOk -and -not $legacyPresent) {
        return "current"
    }
    if ($legacyPresent -and -not $currentOk) {
        return "legacy"
    }
    if ($legacyPresent -or $currentOk -or $marker -eq $expectedMarker) {
        return "mixed"
    }

    return "unknown"
}

function Unlink-AiAgents {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"

    if (-not (Test-Path $config)) {
        Write-Err "Missing config: $config"
        return
    }

    Write-Info "Removing AI agent links..."

    $manifest = Get-Content $config -Raw | ConvertFrom-Json

    foreach ($target in $manifest.targets) {
        $targetPath = Resolve-AiAgentTargetPath $target.path
        Remove-Link $targetPath
    }

    Unlink-CopilotAgents $DotfilesDir

    $markerFile = Get-AiAgentStateFile
    if (Test-Path $markerFile) {
        Remove-Item $markerFile -Force
    }
}

function Link-CopilotSettings {
    param([string]$DotfilesDir)

    $shared = Join-Path $DotfilesDir ".copilot\settings.json"
    $overlay = Join-Path $DotfilesDir ".copilot\settings.local.json"
    $target = Join-Path $env:USERPROFILE ".copilot\settings.json"

    if (-not (Test-Path $shared)) {
        Write-Warn "Missing $shared"
        return
    }

    $targetDir = Split-Path -Parent $target
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    if (Test-Path $target) {
        $item = Get-Item $target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $target -Force
        } else {
            $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
            Move-Item $target "$target.backup.$stamp"
            Write-Info "Backed up existing settings.json"
        }
    }

    $sharedObj = Get-Content $shared -Raw | ConvertFrom-Json -AsHashtable
    $sharedObj.Remove('$schema_comment') | Out-Null

    if (Test-Path $overlay) {
        $overlayObj = Get-Content $overlay -Raw | ConvertFrom-Json -AsHashtable
        $overlayObj.Remove('$schema_comment') | Out-Null
        foreach ($k in $overlayObj.Keys) { $sharedObj[$k] = $overlayObj[$k] }
        $sharedObj | ConvertTo-Json -Depth 32 | Set-Content -Path $target
        Write-Host "  [MERGE] $target (shared + local overlay)"
    } else {
        $sharedObj | ConvertTo-Json -Depth 32 | Set-Content -Path $target
        Write-Host "  [WRITE] $target (shared only — create .copilot\settings.local.json to override)"
    }
}

function Link-AiAgents {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"

    if (-not (Test-Path $config)) {
        Write-Err "Missing config: $config"
        return
    }

    Write-Info "Linking AI agent configs..."

    $manifest = Get-Content $config -Raw | ConvertFrom-Json

    Cleanup-LegacyAiAgentTargets
    Link-ManifestAiTargets $DotfilesDir $manifest
    Link-CopilotAgents $DotfilesDir
    Link-CopilotSettings $DotfilesDir
    Write-AiAgentLayoutMarker $manifest
}

function Show-AiAgentStatus {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"

    if (-not (Test-Path $config)) {
        Write-Warn "Cannot read manifest"
        return
    }

    $manifest = Get-Content $config -Raw | ConvertFrom-Json

    $markerFile = Get-AiAgentStateFile
    $layoutVersion = if (Test-Path $markerFile) { (Get-Content $markerFile -Raw).Trim() } else { "none" }
    Write-Host "  Layout: $(Get-AiAgentLayoutStatus $DotfilesDir)"
    Write-Host "  Layout version marker: $layoutVersion"

    foreach ($target in $manifest.targets) {
        $targetPath = Resolve-AiAgentTargetPath $target.path
        Show-TargetStatus $targetPath
    }

    $sourceDir = Join-Path $DotfilesDir "agents"
    if (Test-Path $sourceDir) {
        Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Where-Object { $_.Name -notlike "*.agent.md" } | Sort-Object Name | ForEach-Object {
            $targetPath = Join-Path $env:USERPROFILE ".copilot\agents\$($_.BaseName).agent.md"
            Show-TargetStatus $targetPath
        }
    }
}
