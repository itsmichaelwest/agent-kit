# Bootstrap Claude Code plugins declared in .claude/settings.json (Windows).
# See scripts/lib/bootstrap-claude-plugins.sh for full context.

function Bootstrap-ClaudePlugins {
    $settings = Join-Path $env:USERPROFILE ".claude\settings.json"

    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Warn "claude CLI not found on PATH; skipping plugin bootstrap"
        return 0
    }

    if (-not (Test-Path $settings)) {
        Write-Warn "$settings not found; run setup.ps1 link first"
        return 0
    }

    $data = Get-Content $settings -Raw | ConvertFrom-Json
    $enabled = if ($data.PSObject.Properties.Name -contains "enabledPlugins") { $data.enabledPlugins } else { $null }
    if (-not $enabled) {
        Write-Info "No enabled plugins declared in $settings"
        return 0
    }

    $specs = @()
    foreach ($prop in $enabled.PSObject.Properties) {
        if ($prop.Value -eq $true) { $specs += $prop.Name }
    }

    if ($specs.Count -eq 0) {
        Write-Info "No enabled plugins declared in $settings"
        return 0
    }

    Write-Info ("Bootstrapping {0} Claude Code plugin(s) from {1}" -f $specs.Count, $settings)

    $ok = 0
    $fail = 0
    foreach ($spec in $specs) {
        & claude plugin install $spec *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK]   $spec" -ForegroundColor Green
            $ok++
        } else {
            Write-Host "  [FAIL] $spec" -ForegroundColor Red
            $fail++
        }
    }

    Write-Host ""
    Write-Info "Installed: $ok, Failed: $fail"
    if ($fail -gt 0) { return 1 }
    return 0
}
