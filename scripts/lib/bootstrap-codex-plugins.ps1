# Bootstrap Codex plugins declared in .codex/config.toml (Windows).

function Bootstrap-CodexPlugins {
    param([string]$DotfilesDir)

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\bootstrap-codex-plugins.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing Codex bootstrap script: $scriptPath"
        return 1
    }

    $pythonCommand = @(Resolve-PythonCommand)
    if (-not $pythonCommand) {
        Write-Err "python3 (3.11+) required to bootstrap Codex plugins"
        return 1
    }

    $homeDir = if ($env:USERPROFILE) { $env:USERPROFILE } elseif ($env:HOME) { $env:HOME } else { [Environment]::GetFolderPath("UserProfile") }

    $args = @()
    if ($pythonCommand.Count -gt 1) {
        $args += $pythonCommand[1..($pythonCommand.Count - 1)]
    }
    $args += @(
        $scriptPath,
        "--repo-root", $DotfilesDir,
        "--home-dir", $homeDir
    )

    & $pythonCommand[0] @args | Out-Host
    return $LASTEXITCODE
}
