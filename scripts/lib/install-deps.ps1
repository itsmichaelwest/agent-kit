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
        $installed = winget list --id $id --accept-source-agreements 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Info "Installing $id..."
            winget install --id $id -h --accept-package-agreements --accept-source-agreements
        }
    }

    $modules = @("Terminal-Icons", "z", "PSFzf", "PSReadLine")
    foreach ($mod in $modules) {
        if (-not (Get-Module -ListAvailable -Name $mod)) {
            Write-Info "Installing module: $mod"
            Install-Module -Name $mod -Scope CurrentUser -Force -SkipPublisherCheck
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
        $installed = winget list --id $id --accept-source-agreements 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Uninstalling $id..."
            winget uninstall --id $id --silent 2>$null
        }
    }

    # PowerShell modules
    $modules = @("Terminal-Icons", "z", "PSFzf")
    foreach ($mod in $modules) {
        if (Get-Module -ListAvailable -Name $mod) {
            Write-Info "Removing module: $mod"
            Uninstall-Module -Name $mod -AllVersions -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Info "Dependencies removed"
}
