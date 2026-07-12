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

    $python = Resolve-PythonCommand
    if (-not $python) {
        Write-Err "Python 3.11+ is required"
        return 1
    }

    & $python[0] @($python | Select-Object -Skip 1) $scriptPath $Action --repo-root $DotfilesDir --home-dir $env:USERPROFILE
    return $LASTEXITCODE
}
