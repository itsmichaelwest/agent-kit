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

    $python = Get-Command python3 -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Write-Err "Python 3 is required"
        return 1
    }

    Write-Info "Compiling agent templates..."
    & $python.Source $scriptPath --repo-root $DotfilesDir | Out-Host
    return $LASTEXITCODE
}
