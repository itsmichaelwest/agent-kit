# Install dependencies (Windows).

function Get-WinGetInstallerStatus {
    param([string]$Id, [string]$Architecture)
    $output = winget show --id $Id --exact --source winget --architecture $Architecture --accept-source-agreements --disable-interactivity 2>$null | Out-String
    if ($LASTEXITCODE -eq 0) {
        # `show` succeeds without an applicable installer. An installer has a
        # SHA256 field in the final section; ignore checksums in release notes
        # and match the value without depending on localized labels.
        $installerDetails = ($output -split '(?m)^[^\s:\r\n][^:\r\n]*:[ \t]*\r?$')[-1]
        if ($installerDetails -match '(?m)^ {2}[^:\r\n]+:\s*[0-9a-fA-F]{64}\s*$') { return "available" }
        if ($output -match "\[$([regex]::Escape($Id))\]") { return "unavailable" }
        return "error"
    }
    # APPINSTALLER_CLI_ERROR_NO_APPLICABLE_INSTALLER (0x8A150010).
    if ($LASTEXITCODE -eq -1978335216) { return "unavailable" }
    return "error"
}

function Install-Deps {
    Write-Info "Installing dependencies..."
    $nativeArch = Get-NativeArchitecture
    Refresh-InstallPath

    $packages = @(
        "9NQ7512CXL7T",
        "GitHub.cli",
        "eza-community.eza",
        "junegunn.fzf",
        "BurntSushi.ripgrep.MSVC",
        "sharkdp.bat",
        "sharkdp.fd",
        "JanDeDobbeleer.OhMyPosh",
        "Starship.Starship",
        "Microsoft.Coreutils"
    )
    $packageCommands = @{
        "GitHub.cli" = "gh"; "eza-community.eza" = "eza"; "junegunn.fzf" = "fzf"
        "BurntSushi.ripgrep.MSVC" = "rg"; "sharkdp.bat" = "bat"; "sharkdp.fd" = "fd"
        "JanDeDobbeleer.OhMyPosh" = "oh-my-posh"; "Starship.Starship" = "starship"
        "Microsoft.Coreutils" = "coreutils-manager"
    }
    $skippedPackages = @()
    $x64Packages = @()

    foreach ($id in $packages) {
        $output = winget list --id $id --exact --accept-source-agreements 2>$null | Out-String
        if ($id -eq "9NQ7512CXL7T") {
            if ($output -match [regex]::Escape($id)) {
                Write-Host "  [OK] Python Install Manager"
                continue
            }
            Write-Info "Installing Python Install Manager..."
            winget install --id $id --exact -h --accept-package-agreements --accept-source-agreements | Out-Host
            if ($LASTEXITCODE -ne 0) {
                Write-Err "Could not install Python Install Manager"
                return $LASTEXITCODE
            }
            continue
        }

        if ($nativeArch -ne "arm64" -and $output -match [regex]::Escape($id)) {
            Write-Host "  [OK] $id"
            continue
        }

        $selectedArch = $nativeArch
        $name = $packageCommands[$id]
        if ($nativeArch -eq "arm64") {
            $existingArch = if ($name) { Get-ExecutableArchitecture $name } else { $null }
            if ($existingArch -eq "arm64") {
                Write-Host "  [OK ARM64] $id"
                continue
            }
            $nativeStatus = Get-WinGetInstallerStatus $id "arm64"
            if ($nativeStatus -eq "error") {
                Write-Warn "Could not check ARM64 availability for $id; skipping it without an x64 fallback."
                $skippedPackages += $id
                continue
            }
            if ($nativeStatus -eq "unavailable") {
                $x64Status = Get-WinGetInstallerStatus $id "x64"
                if ($x64Status -ne "available") {
                    Write-Warn "WinGet did not offer an ARM64 or x64 installer for $id; skipping it."
                    $skippedPackages += $id
                    continue
                }
                if ($existingArch -eq "x64") {
                    Write-Host "  [OK x64] $id (already installed)"
                    $x64Packages += "$id (already installed)"
                    continue
                }
                $label = if ($name) { $name } else { $id }
                if (-not (Confirm-X64Fallback $label)) {
                    $skippedPackages += $id
                    continue
                }
                $selectedArch = "x64"
            } elseif ($existingArch -eq "x64") {
                Write-Warn "$name is already x64 on PATH while WinGet offers ARM64. Remove the x64 install before installing the native version."
                $skippedPackages += $id
                continue
            }
        }

        Write-Info "Installing $id ($selectedArch)..."
        winget install --id $id --exact --architecture $selectedArch -h --accept-package-agreements --accept-source-agreements | Out-Host
        $installExitCode = $LASTEXITCODE
        # APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE (0x8A15002B) means
        # an existing package has no update; still verify its executable below.
        $alreadyCurrent = $installExitCode -eq -1978335189 -and $output -match [regex]::Escape($id)
        if ($installExitCode -ne 0 -and -not $alreadyCurrent) {
            Write-Warn "Could not install $id ($selectedArch); skipping it."
            $skippedPackages += $id
            continue
        }
        if ($nativeArch -eq "arm64" -and $name) {
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                        [System.Environment]::GetEnvironmentVariable("Path", "Machine")
            $installedArch = Get-ExecutableArchitecture $name
            if (-not $installedArch) {
                Write-Warn "$id is installed, but could not verify the architecture of $name on PATH. Restart PowerShell or check the package's command aliases."
                $skippedPackages += $id
            } elseif ($installedArch -ne $selectedArch) {
                Write-Warn "$name on PATH is $installedArch, expected $selectedArch; check for a conflicting installation."
                $skippedPackages += $id
            } elseif ($selectedArch -eq "x64") {
                $x64Packages += $id
            } elseif ($alreadyCurrent) {
                Write-Host "  [OK ARM64] $id (already up to date)"
            }
        }
    }

    # Refresh PATH so newly installed tools are available in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")

    $pythonManager = Get-Command pymanager -ErrorAction SilentlyContinue
    if (-not $pythonManager) {
        Write-Err "Python Install Manager was installed but its command is not available. Restart PowerShell and run install again."
        return 1
    }

    Write-Info "Installing/updating the latest stable Python runtime..."
    $pythonTag = if ($nativeArch -eq "arm64") { "3-arm64" } else { "default" }
    & $pythonManager.Source install --update $pythonTag | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Python Install Manager could not install/update the default Python runtime"
        return $LASTEXITCODE
    }
    if (-not (Resolve-PythonCommand)) {
        Write-Err "Python 3.11+ is not available after installation"
        return 1
    }
    if ($nativeArch -eq "arm64") {
        $pythonArch = & $pythonManager.Source exec -V:3-arm64 -c 'import platform; print(platform.machine().lower())'
        if ($LASTEXITCODE -ne 0 -or $pythonArch -ne "arm64") {
            Write-Err "An ARM64 Python runtime is not available after installation"
            return 1
        }
    }

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
            Save-PSResource -Name $mod -Path $localModDir -TrustRepository -IncludeXml | Out-Host
        }
    }

    if ($skippedPackages.Count -gt 0) {
        Write-Warn "Skipped or unverified packages: $($skippedPackages -join ', ')"
    }
    if ($x64Packages.Count -gt 0) {
        Write-Warn "x64 packages on ARM64 Windows: $($x64Packages -join ', ')"
    }
    Write-Info "Dependency installation finished"
    return 0
}

function Uninstall-Deps {
    Write-Info "Removing dependencies..."

    # Winget packages
    $packages = @(
        "eza-community.eza",
        "junegunn.fzf",
        "BurntSushi.ripgrep.MSVC",
        "sharkdp.bat",
        "sharkdp.fd",
        "JanDeDobbeleer.OhMyPosh",
        "Starship.Starship",
        "Microsoft.Coreutils"
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
