function Sync-CodexConfig {
    param(
        [Parameter(Mandatory=$true)][string]$DotfilesDir,
        [ValidateSet("apply", "capture")][string]$Action = "apply"
    )

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\sync-codex-config.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing Codex config sync script: $scriptPath"
        return 1
    }

    $python = Get-Command python3 -ErrorAction SilentlyContinue
    if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
    if (-not $python) {
        Write-Err "Python 3.11+ is required"
        return 1
    }

    & $python.Source $scriptPath $Action --repo-root $DotfilesDir --home-dir $env:USERPROFILE
    return $LASTEXITCODE
}
