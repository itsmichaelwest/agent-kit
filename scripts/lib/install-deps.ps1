# Install dependencies (Windows).

function Install-Deps {
    Write-Info "Installing dependencies..."

    $packages = @(
        "GitHub.cli",
        "Schniz.fnm",
        "eza-community.eza",
        "junegunn.fzf",
        "BurntSushi.ripgrep.MSVC",
        "sharkdp.bat",
        "sharkdp.fd",
        "JanDeDobbeleer.OhMyPosh",
        "Starship.Starship"
    )

    foreach ($id in $packages) {
        $output = winget list --id $id --exact --accept-source-agreements 2>$null | Out-String
        if ($output -match [regex]::Escape($id)) {
            Write-Host "  [OK] $id"
        } else {
            Write-Info "Installing $id..."
            winget install --id $id --exact -h --accept-package-agreements --accept-source-agreements
        }
    }

    # Refresh PATH so newly installed tools are available in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")

    # Install PowerShell modules via Save-PSResource to a local (non-OneDrive) path.
    # OneDrive sync breaks Install-PSResource -Scope CurrentUser, so we use a path
    # under AppData/Local and prepend it to PSModulePath in the profile.
    $localModDir = "$env:LOCALAPPDATA\PowerShell\Modules"
    if (-not (Test-Path $localModDir)) { New-Item -ItemType Directory -Path $localModDir -Force | Out-Null }

    $modules = @("Terminal-Icons", "z", "PSFzf", "PSReadLine")
    foreach ($mod in $modules) {
        if (Test-Path "$localModDir\$mod") {
            Write-Host "  [OK] $mod"
        } else {
            Write-Info "Installing module: $mod"
            Save-PSResource -Name $mod -Path $localModDir -TrustRepository -IncludeXml
        }
    }

    # Node.js LTS via fnm
    if (Get-Command fnm -ErrorAction SilentlyContinue) {
        fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression
        $ltsInstalled = fnm list 2>$null | Select-String "lts-latest"
        if ($ltsInstalled) {
            Write-Host "  [OK] Node.js LTS (fnm)"
        } else {
            Write-Info "Installing latest Node.js LTS via fnm..."
            fnm install --lts
            fnm default lts-latest
        }
    }

    Write-Info "Dependencies installed"
}

function Uninstall-Deps {
    Write-Info "Removing dependencies..."

    # Winget packages
    $packages = @(
        "Schniz.fnm",
        "eza-community.eza",
        "junegunn.fzf",
        "BurntSushi.ripgrep.MSVC",
        "sharkdp.bat",
        "sharkdp.fd",
        "JanDeDobbeleer.OhMyPosh",
        "Starship.Starship"
    )

    foreach ($id in $packages) {
        $output = winget list --id $id --exact --accept-source-agreements 2>$null | Out-String
        if ($output -match [regex]::Escape($id)) {
            Write-Info "Uninstalling $id..."
            winget uninstall --id $id --exact --silent 2>$null
        }
    }

    # PowerShell modules (installed via Save-PSResource to local path)
    $localModDir = "$env:LOCALAPPDATA\PowerShell\Modules"
    $modules = @("Terminal-Icons", "z", "PSFzf")
    foreach ($mod in $modules) {
        $modPath = Join-Path $localModDir $mod
        if (Test-Path $modPath) {
            Write-Info "Removing module: $mod"
            Remove-Item $modPath -Recurse -Force
        }
    }

    Write-Info "Dependencies removed"
}
