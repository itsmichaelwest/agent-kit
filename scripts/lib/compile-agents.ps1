function Compile-Agents {
    param([string]$DotfilesDir)

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\compile-agents.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing compile script: $scriptPath"
        return 1
    }

    $templatesDir = Join-Path $DotfilesDir "agent-templates"
    if (-not (Test-Path $templatesDir)) {
        Write-Warn "No agent templates directory found; skipping agent compilation"
        return 0
    }

    $python = Resolve-PythonCommand
    if (-not $python) {
        Write-Err "Python 3.11+ is required"
        return 1
    }

    Write-Info "Compiling agent templates..."
    & $python[0] @($python | Select-Object -Skip 1) $scriptPath --repo-root $DotfilesDir | Out-Host
    return $LASTEXITCODE
}
