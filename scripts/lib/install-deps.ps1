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
        winget list --id $id --exact --accept-source-agreements 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Info "Installing $id..."
            winget install --id $id --exact -h --accept-package-agreements --accept-source-agreements
        }
    }

    # Refresh PATH so newly installed tools are available in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")

    # Install PowerShell modules (Install-PSResource ships with PS7.4+, defaults to CurrentUser)
    # Ensure the CurrentUser modules directory exists (OneDrive may redirect Documents)
    $userModDir = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PowerShell\Modules'
    if (-not (Test-Path $userModDir)) { New-Item -ItemType Directory -Path $userModDir -Force | Out-Null }

    $modules = @("Terminal-Icons", "z", "PSFzf", "PSReadLine")
    foreach ($mod in $modules) {
        if (-not (Get-Module -ListAvailable -Name $mod)) {
            Write-Info "Installing module: $mod"
            Install-PSResource -Name $mod -Scope CurrentUser -TrustRepository -Quiet
        }
    }

    # Node.js LTS via fnm
    if (Get-Command fnm -ErrorAction SilentlyContinue) {
        fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression
        $ltsInstalled = fnm list 2>$null | Select-String "lts-latest"
        if (-not $ltsInstalled) {
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
        winget list --id $id --exact --accept-source-agreements 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Uninstalling $id..."
            winget uninstall --id $id --exact --silent 2>$null
        }
    }

    # PowerShell modules
    $modules = @("Terminal-Icons", "z", "PSFzf")
    foreach ($mod in $modules) {
        if (Get-Module -ListAvailable -Name $mod) {
            Write-Info "Removing module: $mod"
            Uninstall-PSResource -Name $mod -Scope CurrentUser -SkipDependencyCheck -ErrorAction SilentlyContinue
        }
    }

    Write-Info "Dependencies removed"
}
