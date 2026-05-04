function Show-PluginStatus {
    param([string]$DotfilesDir)

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\plugin-status.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing status script: $scriptPath"
        return 1
    }

    $python = Get-Command python3 -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Write-Err "Python 3 is required"
        return 1
    }

    $homeDir = if ($env:USERPROFILE) { $env:USERPROFILE } elseif ($env:HOME) { $env:HOME } else { [Environment]::GetFolderPath("UserProfile") }

    Write-Info "Plugin status"
    & $python.Source $scriptPath `
        --repo-root $DotfilesDir `
        --home-dir $homeDir | Out-Host
    return $LASTEXITCODE
}
