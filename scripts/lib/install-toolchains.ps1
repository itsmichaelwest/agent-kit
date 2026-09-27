# Install native language toolchains on Windows.

function Get-NativeArchitecture {
    $arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
    if ($arch -notin @("x64", "arm64")) { throw "Unsupported Windows architecture: $arch" }
    return $arch
}

function Refresh-InstallPath {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

function Install-NodeToolchain {
    $arch = Get-NativeArchitecture
    if ($arch -eq "arm64") {
        $existingNodeArch = Get-ExecutableArchitecture "node"
        if ($existingNodeArch -and $existingNodeArch -ne "arm64") {
            Write-Err "Existing Node.js is $existingNodeArch. Remove it before installing native ARM64 Node.js."
            return 1
        }
        if ($existingNodeArch -eq "arm64") {
            $installedLts = winget list --id OpenJS.NodeJS.LTS --exact --accept-source-agreements 2>$null | Out-String
            if ($installedLts -match [regex]::Escape("OpenJS.NodeJS.LTS")) {
                Write-Host "  [OK ARM64] Node.js LTS"
                return 0
            }
            Write-Err "An ARM64 Node.js is already on PATH, but it is not the WinGet LTS package. Remove or manage that installation before selecting Node.js LTS."
            return 1
        }
        # fnm's Windows release is x64. Use Node's native ARM64 installer.
        Write-Info "Installing native ARM64 Node.js LTS..."
        winget install --id OpenJS.NodeJS.LTS --exact --architecture arm64 -h --accept-package-agreements --accept-source-agreements | Out-Host
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        Refresh-InstallPath
        $nodeArch = node -p "process.arch" 2>$null
        if ($LASTEXITCODE -ne 0 -or $nodeArch -ne "arm64") {
            Write-Err "Node.js is not running as ARM64; check for an x64 Node.js earlier on PATH."
            return 1
        }
        if (-not $existingNodeArch) {
            $markerDir = Join-Path $env:LOCALAPPDATA "agent-kit"
            New-Item -ItemType Directory -Path $markerDir -Force | Out-Null
            New-Item -ItemType File -Path (Join-Path $markerDir "node-arm64.installed") -Force | Out-Null
        }
        return 0
    }

    if (-not (Get-Command fnm -ErrorAction SilentlyContinue)) {
        Write-Info "Installing fnm ($arch)..."
        winget install --id Schniz.fnm --exact --architecture $arch -h --accept-package-agreements --accept-source-agreements | Out-Host
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        Refresh-InstallPath
    }
    if (-not (Get-Command fnm -ErrorAction SilentlyContinue)) {
        Write-Err "fnm is not available after installation"
        return 1
    }
    fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression | Out-Null
    $ltsInstalled = fnm list 2>$null | Select-String "lts-latest"
    if (-not $ltsInstalled) {
        Write-Info "Installing latest Node.js LTS ($arch) via fnm..."
        fnm install --lts --arch $arch | Out-Host
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        fnm default lts-latest | Out-Host
        if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    }
    fnm use lts-latest | Out-Null
    $nodeArch = node -p "process.arch" 2>$null
    if ($LASTEXITCODE -ne 0 -or $nodeArch -ne $arch) {
        Write-Err "Node.js is not running as $arch"
        return 1
    }
    return 0
}

function Install-RustToolchain {
    $arch = Get-NativeArchitecture
    $hostTriple = switch ($arch) {
        "arm64" { "aarch64-pc-windows-msvc" }
        "x64"   { "x86_64-pc-windows-msvc" }
        default { Write-Err "Unsupported Windows architecture: $arch"; return 1 }
    }
    $existingRustupArch = Get-ExecutableArchitecture "rustup"
    if ($existingRustupArch -and $existingRustupArch -ne $arch) {
        Write-Err "Existing rustup is $existingRustupArch. Remove it before installing native $arch Rust."
        return 1
    }
    if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
        # Use the architecture-specific bootstrap to avoid an emulated x64 installer.
        $download = Join-Path ([IO.Path]::GetTempPath()) "agent-kit-rustup-init-$arch.exe"
        $url = "https://static.rust-lang.org/rustup/dist/$hostTriple/rustup-init.exe"
        Write-Info "Installing native Rust toolchain ($hostTriple)..."
        try {
            Invoke-WebRequest -Uri $url -OutFile $download
            $expectedHash = ((Invoke-RestMethod -Uri "$url.sha256") -split '\s+')[0]
            $actualHash = (Get-FileHash -Path $download -Algorithm SHA256).Hash
            if ($actualHash -ine $expectedHash) {
                Write-Err "rustup-init SHA-256 checksum mismatch"
                return 1
            }
            & $download -y --profile default --default-host $hostTriple | Out-Host
            if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
        } finally {
            Remove-Item $download -Force -ErrorAction SilentlyContinue
        }
        Refresh-InstallPath
        $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    }
    if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
        Write-Err "rustup is not available after installation"
        return 1
    }
    rustup set default-host $hostTriple | Out-Host
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    rustup toolchain install stable --profile default | Out-Host
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    rustup default stable | Out-Host
    if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }
    $installedHost = rustc -vV | Select-String '^host: (.+)$'
    if (-not $installedHost -or $installedHost.Matches[0].Groups[1].Value -ne $hostTriple) {
        Write-Err "Rust host is not $hostTriple"
        return 1
    }
    $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    $vcComponent = if ($arch -eq "arm64") { "Microsoft.VisualStudio.Component.VC.Tools.ARM64" } else { "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" }
    if (-not (Test-Path $vswhere) -or -not (& $vswhere -latest -requires $vcComponent -property installationPath)) {
        Write-Warn "Rust is installed for $hostTriple, but native MSVC C++ build tools were not found. Install the Visual Studio C++ tools and Windows SDK before linking programs."
    }
    return 0
}

function Uninstall-Toolchains {
    Write-Info "Removing toolchains..."
    if (Get-Command rustup -ErrorAction SilentlyContinue) { rustup self uninstall -y }
    winget uninstall --id Rustlang.Rustup --exact --silent 2>$null
    winget uninstall --id Schniz.fnm --exact --silent 2>$null
    $nodeMarker = Join-Path $env:LOCALAPPDATA "agent-kit\node-arm64.installed"
    if (Test-Path $nodeMarker) {
        winget uninstall --id OpenJS.NodeJS.LTS --exact --silent 2>$null
        if ($LASTEXITCODE -eq 0) { Remove-Item $nodeMarker -Force }
    }
    $fnmDir = "$env:APPDATA\fnm"
    if (Test-Path $fnmDir) { Remove-Item $fnmDir -Recurse -Force }
    Write-Info "Toolchains removed"
}
