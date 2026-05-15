# Install/update skills via `npx skills` (vercel-labs/skills) on Windows.

function Test-SkillsPrereqs {
    param([string]$ManifestPath)

    if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
        Write-Err "npx (Node.js) is required"
        return $false
    }
    if (-not (Test-Path $ManifestPath)) {
        Write-Err "Missing manifest: $ManifestPath"
        return $false
    }
    return $true
}

function Sync-SkillsLockfile {
    param([string]$DotfilesDir)

    $repoLock = Join-Path $DotfilesDir ".skill-lock.json"
    $homeAgents = Join-Path $env:USERPROFILE ".agents"
    $homeLock = Join-Path $homeAgents ".skill-lock.json"

    if (-not (Test-Path $homeAgents)) {
        New-Item -ItemType Directory -Path $homeAgents -Force | Out-Null
    }

    $existingItem = Get-Item $homeLock -Force -ErrorAction SilentlyContinue
    if ($existingItem -and $existingItem.LinkType -eq "SymbolicLink") {
        return
    }

    if ((Test-Path $homeLock) -and -not (Test-Path $repoLock)) {
        Move-Item $homeLock $repoLock
    }
    if (-not (Test-Path $repoLock)) {
        '{"version":3,"skills":{}}' | Set-Content -Path $repoLock -NoNewline
    }
    if ((Test-Path $homeLock) -and (-not $existingItem -or $existingItem.LinkType -ne "SymbolicLink")) {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Move-Item $homeLock "$homeLock.backup.$stamp" -Force
    }

    New-Item -ItemType SymbolicLink -Path $homeLock -Target $repoLock -Force | Out-Null
}

function Update-Skills {
    param([string]$DotfilesDir)

    $manifestPath = Join-Path $DotfilesDir "scripts\skills-manifest.json"
    if (-not (Test-SkillsPrereqs -ManifestPath $manifestPath)) { return 1 }

    Sync-SkillsLockfile -DotfilesDir $DotfilesDir

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $agentArgs = @()
    foreach ($a in $manifest.agents) { $agentArgs += @("-a", [string]$a) }

    $sources = @($manifest.sources)
    Write-Info ("Installing skills from {0} sources via npx skills..." -f $sources.Count)

    $ok = 0
    $failed = 0
    foreach ($src in $sources) {
        $repo = [string]$src.repo
        $skillArgs = @()
        if ($src.PSObject.Properties.Name -contains "skills" -and $src.skills) {
            foreach ($s in $src.skills) { $skillArgs += @("-s", [string]$s) }
        } else {
            $skillArgs += @("-s", "*")
        }

        Write-Host "  [ADD]  $repo" -ForegroundColor Cyan
        $cmdArgs = @("-y", "skills@latest", "add", $repo, "-g", "-y") + $agentArgs + $skillArgs
        & npx @cmdArgs *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK]   $repo" -ForegroundColor Green
            $ok++
        } else {
            Write-Host "  [FAIL] $repo" -ForegroundColor Red
            $failed++
        }
    }

    Write-Host ""
    Write-Info "Sources installed: $ok, Failed: $failed"
    if ($failed -gt 0) { return 1 }
    return 0
}

function List-Skills {
    param([string]$DotfilesDir)

    $manifestPath = Join-Path $DotfilesDir "scripts\skills-manifest.json"
    if (-not (Test-SkillsPrereqs -ManifestPath $manifestPath)) { return 1 }

    & npx -y skills@latest list -g
    return $LASTEXITCODE
}
