function Invoke-DoctorSkills {
    param(
        [string]$DotfilesDir,
        [switch]$Strict
    )

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\doctor-skills.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing doctor script: $scriptPath"
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
    if ($Strict) { $pyArgs += "--strict" }

    Write-Info "Skills doctor"
    & $python.Source @pyArgs | Out-Host
    return $LASTEXITCODE
}
