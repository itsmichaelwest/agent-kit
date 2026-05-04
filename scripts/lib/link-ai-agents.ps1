# Link/unlink AI agent configs using the JSON manifest (Windows).

$script:AiAgentLayoutVersion = "2"

function Get-AiAgentStateFile {
    $stateRoot = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { $env:USERPROFILE }
    return Join-Path $stateRoot "agent-kit\ai-agent-layout-version"
}

function Ensure-DirectoryTarget {
    param([string]$Target)

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if (-not $item.PSIsContainer) {
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
        (Join-Path $env:USERPROFILE ".codex\skills")
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
    $marker = Get-AiAgentStateFile
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $marker)) | Out-Null
    Set-Content -Path $marker -Value $script:AiAgentLayoutVersion -NoNewline
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
        $targetPath = ($target.path -replace '^~', $env:USERPROFILE) -replace '/', '\'

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

    Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Sort-Object Name | ForEach-Object {
        $targetPath = Join-Path $targetDir ($_.BaseName + ".agent.md")
        Ensure-Linked $_.FullName $targetPath
    }
}

function Unlink-CopilotAgents {
    param([string]$DotfilesDir)

    $sourceDir = Join-Path $DotfilesDir "agents"
    $targetDir = Join-Path $env:USERPROFILE ".copilot\agents"

    if (-not (Test-Path $sourceDir)) { return }

    Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Sort-Object Name | ForEach-Object {
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
    $marker = ""
    $markerFile = Get-AiAgentStateFile
    if (Test-Path $markerFile) {
        $marker = (Get-Content $markerFile -Raw).Trim()
    }

    $currentTargets = @(
        (Join-Path $env:USERPROFILE ".claude\skills")
        (Join-Path $env:USERPROFILE ".codex\agents")
        (Join-Path $env:USERPROFILE ".agents\skills")
        (Join-Path $env:USERPROFILE ".copilot\copilot-instructions.md")
        (Join-Path $env:USERPROFILE ".copilot\agents")
    )

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

    if ($marker -eq $script:AiAgentLayoutVersion -and $currentOk -and -not $legacyPresent) {
        return "current"
    }
    if ($legacyPresent -and -not $currentOk) {
        return "legacy"
    }
    if ($legacyPresent -or $currentOk -or $marker -eq $script:AiAgentLayoutVersion) {
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
        $targetPath = ($target.path -replace '^~', $env:USERPROFILE) -replace '/', '\'
        Remove-Link $targetPath
    }

    Unlink-CopilotAgents $DotfilesDir

    $markerFile = Get-AiAgentStateFile
    if (Test-Path $markerFile) {
        Remove-Item $markerFile -Force
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
    Write-AiAgentLayoutMarker
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
    Write-Host "  Layout: $(Get-AiAgentLayoutStatus)"
    Write-Host "  Layout version marker: $layoutVersion"

    foreach ($target in $manifest.targets) {
        $targetPath = ($target.path -replace '^~', $env:USERPROFILE) -replace '/', '\'
        Show-TargetStatus $targetPath
    }

    $sourceDir = Join-Path $DotfilesDir "agents"
    if (Test-Path $sourceDir) {
        Get-ChildItem -Path $sourceDir -Filter "*.md" -File | Sort-Object Name | ForEach-Object {
            $targetPath = Join-Path $env:USERPROFILE ".copilot\agents\$($_.BaseName).agent.md"
            Show-TargetStatus $targetPath
        }
    }
}
