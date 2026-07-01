# Install language toolchains (Windows): fnm/Node.js, Rust (rustup).

function Install-Toolchains {
    Write-Info "Installing toolchains..."

    $toolchainPackages = @(
        "Schniz.fnm",
        "Rustlang.Rustup"
    )

    foreach ($id in $toolchainPackages) {
        $output = winget list --id $id --exact --accept-source-agreements 2>$null | Out-String
        if ($output -match [regex]::Escape($id)) {
            Write-Host "  [OK] $id"
        } else {
            Write-Info "Installing $id..."
            winget install --id $id --exact -h --accept-package-agreements --accept-source-agreements
        }
    }

    # Refresh PATH so fnm/rustup are available in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")

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

    Write-Info "Toolchains installed"
}

function Uninstall-Toolchains {
    Write-Info "Removing toolchains..."

    if (Get-Command rustup -ErrorAction SilentlyContinue) {
        Write-Info "Removing rustup..."
        rustup self uninstall -y
    }
    winget uninstall --id Rustlang.Rustup --exact --silent 2>$null
    winget uninstall --id Schniz.fnm --exact --silent 2>$null

    $fnmDir = "$env:APPDATA\fnm"
    if (Test-Path $fnmDir) {
        Write-Info "Removing fnm data..."
        Remove-Item $fnmDir -Recurse -Force
    }

    Write-Info "Toolchains removed"
}
