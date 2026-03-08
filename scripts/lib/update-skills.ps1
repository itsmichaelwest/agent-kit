# Install/update skills from the skills manifest (Windows).

function Resolve-PythonCommand {
    $candidates = @(
        @{ Exe = "python3"; Args = @("--version") },
        @{ Exe = "python";  Args = @("--version") },
        @{ Exe = "py";      Args = @("-3", "--version") }
    )

    foreach ($candidate in $candidates) {
        $cmd = Get-Command $candidate.Exe -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }

        & $cmd.Source @($candidate.Args) *> $null
        if ($LASTEXITCODE -eq 0) {
            if ($candidate.Exe -eq "py") { return @($cmd.Source, "-3") }
            return @($cmd.Source)
        }
    }

    return $null
}

function Compare-DirectoriesIgnoringLineEndings {
    param([string]$Left, [string]$Right)

    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { return $false }

    & $git.Source diff --no-index --ignore-cr-at-eol --exit-code -- $Left $Right *> $null
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq 1) { return $false }
    return $false
}

function Update-Skills {
    param([string]$DotfilesDir)

    $skillsDir = Join-Path $DotfilesDir "skills"
    $manifestPath = Join-Path $DotfilesDir "scripts\skills-manifest.json"
    $installer = Join-Path $skillsDir ".system\skill-installer\scripts\install-skill-from-github.py"

    if (-not (Test-Path $manifestPath)) { Write-Err "Missing manifest: $manifestPath"; return 1 }
    if (-not (Test-Path $installer)) { Write-Err "Missing installer: $installer"; return 1 }

    $pythonCommand = @(Resolve-PythonCommand)
    if (-not $pythonCommand) { Write-Err "Python 3 is required"; return 1 }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $skills = @($manifest.skills)
    $count = $skills.Count
    $updated = 0
    $skipped = 0
    $failed = 0
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("skills-update-" + [Guid]::NewGuid().ToString("N"))

    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Info "Updating $count skills from manifest..."

    try {
        foreach ($skill in $skills) {
            $name = [string]$skill.name
            $repo = [string]$skill.repo
            $path = [string]$skill.path
            $ref = if ($skill.PSObject.Properties.Name -contains "ref" -and $skill.ref) { [string]$skill.ref } else { "main" }

            if (-not $name -or -not $repo -or -not $path) {
                Write-Host "  [FAIL] Invalid manifest entry" -ForegroundColor Red
                $failed++
                continue
            }

            $dest = Join-Path $skillsDir $name
            $staged = Join-Path $tempRoot $name
            if (Test-Path $staged) {
                Remove-Item $staged -Recurse -Force
            }

            $args = @()
            if ($pythonCommand.Count -gt 1) {
                $args += $pythonCommand[1..($pythonCommand.Count - 1)]
            }
            $args += @(
                $installer
                "--repo", $repo
                "--path", $path
                "--ref", $ref
                "--dest", $tempRoot
                "--name", $name
            )

            & $pythonCommand[0] @args 2>$null
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path $staged)) {
                Write-Host "  [FAIL] $name (from $repo)" -ForegroundColor Red
                $failed++
                continue
            }

            if ((Test-Path $dest) -and (Compare-DirectoriesIgnoringLineEndings $dest $staged)) {
                Remove-Item $staged -Recurse -Force
                Write-Host "  [SKIP] $name (unchanged)" -ForegroundColor Yellow
                $skipped++
                continue
            }

            if (Test-Path $dest) {
                Remove-Item $dest -Recurse -Force
            }
            Move-Item $staged $dest
            Write-Host "  [OK] $name (from $repo)" -ForegroundColor Green
            $updated++
        }
    }
    finally {
        if (Test-Path $tempRoot) {
            Remove-Item $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Host ""
    Write-Info "Updated: $updated, Skipped: $skipped, Failed: $failed"
    if ($failed -gt 0) { return 1 }
    return 0
}

function List-Skills {
    param([string]$DotfilesDir)

    $skillsDir = Join-Path $DotfilesDir "skills"
    $manifestPath = Join-Path $DotfilesDir "scripts\skills-manifest.json"

    if (-not (Test-Path $manifestPath)) { Write-Err "Missing manifest: $manifestPath"; return 1 }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $skills = @($manifest.skills)
    $count = $skills.Count

    Write-Info "Skills manifest ($count skills):"
    Write-Host ""

    foreach ($skill in $skills) {
        $name = [string]$skill.name
        $repo = [string]$skill.repo
        $dest = Join-Path $skillsDir $name

        if (Test-Path $dest) {
            Write-Host "  [INSTALLED] $name  ($repo)" -ForegroundColor Green
        } else {
            Write-Host "  [MISSING]   $name  ($repo)" -ForegroundColor Red
        }
    }

    return 0
}
