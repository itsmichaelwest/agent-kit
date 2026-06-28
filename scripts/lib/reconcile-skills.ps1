function Invoke-ReconcileSkills {
    param([string]$DotfilesDir)

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\reconcile-skills.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing reconcile script: $scriptPath"
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
    $pyArgs = @($scriptPath, "--repo-root", $DotfilesDir, "--home-dir", $homeDir)

    Write-Info "Skills reconcile"
    & $python.Source @pyArgs | Out-Host
    return $LASTEXITCODE
}
