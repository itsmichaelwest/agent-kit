# Install dependencies (Windows).

function Install-Deps {
    Write-Info "Installing dependencies..."

    $packages = @(
        "Git.Git",
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
