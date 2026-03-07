# Link AI agent configs using the JSON manifest (Windows).

function Link-AiAgents {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"

    if (-not (Test-Path $config)) {
        Write-Err "Missing config: $config"
        return
    }

    Write-Info "Linking AI agent configs..."

    $manifest = Get-Content $config -Raw | ConvertFrom-Json

    foreach ($target in $manifest.targets) {
        $sourceRel = $manifest.sources.($target.source)
        if (-not $sourceRel) {
            Write-Warn "Unknown source key '$($target.source)', skipping"
            continue
        }

        $sourceAbs = Join-Path $DotfilesDir $sourceRel
        $targetPath = $target.path -replace '^~', $env:USERPROFILE

        if (-not (Test-Path $sourceAbs)) {
            Write-Warn "Missing source: $sourceAbs, skipping"
            continue
        }

        Ensure-Linked $sourceAbs $targetPath
    }
}

function Show-AiAgentStatus {
    param([string]$DotfilesDir)

    $config = Join-Path $DotfilesDir "scripts\ai-agent-links.json"

    if (-not (Test-Path $config)) {
        Write-Warn "Cannot read manifest"
        return
    }

    $manifest = Get-Content $config -Raw | ConvertFrom-Json

    foreach ($target in $manifest.targets) {
        $targetPath = $target.path -replace '^~', $env:USERPROFILE

        if (Test-Path $targetPath) {
            $item = Get-Item $targetPath -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                Write-Host "  [OK] $targetPath -> $($item.Target)" -ForegroundColor Green
            } else {
                Write-Host "  [EXISTS] $targetPath (not a symlink)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [MISSING] $targetPath" -ForegroundColor Red
        }
    }
}
