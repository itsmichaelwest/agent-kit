function Invoke-UninstallSkillManifest {
    param(
        [string]$DotfilesDir,
        [string]$SkillName,
        [switch]$Apply
    )

    $scriptPath = Join-Path $DotfilesDir "scripts\lib\uninstall-skill.py"
    if (-not (Test-Path $scriptPath)) {
        Write-Err "Missing uninstall script: $scriptPath"
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

    $pyArgs = @($scriptPath, "--repo-root", $DotfilesDir, "--skill", $SkillName)
    if ($Apply) { $pyArgs += "--apply" }

    & $python.Source @pyArgs | Out-Host
    return $LASTEXITCODE
}

function Uninstall-Skill {
    param(
        [string]$DotfilesDir,
        [string]$SkillName
    )

    $manifestPath = Join-Path $DotfilesDir "scripts\skills-manifest.json"
    if (-not (Test-SkillsPrereqs -ManifestPath $manifestPath)) { return 1 }
    if (-not $SkillName) {
        Write-Err "Missing skill name. Usage: setup.ps1 uninstall-skill <installed-skill-name>"
        return 1
    }

    Sync-SkillsLockfile -DotfilesDir $DotfilesDir

    $code = Invoke-UninstallSkillManifest $DotfilesDir $SkillName
    if ($code -ne 0) { return $code }

    Write-Info ("Uninstalling skill via npx skills: {0}" -f $SkillName)
    & npx -y skills@latest remove $SkillName -g -y
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

    return Invoke-UninstallSkillManifest $DotfilesDir $SkillName -Apply
}
