# Link/unlink base dotfiles and PowerShell profile (Windows).

function Unlink-Dotfiles {
    Write-Info "Removing dotfile links..."
    Remove-Link "$env:USERPROFILE\.gitconfig"
    Remove-Link "$env:USERPROFILE\.gitignore_global"
    Remove-Link "$env:USERPROFILE\.config\starship.toml"

    # PowerShell profile (copied, not symlinked — just delete it)
    $psDir = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PowerShell'
    $profilePath = "$psDir\Microsoft.PowerShell_profile.ps1"
    if (Test-Path $profilePath) {
        Remove-Item $profilePath -Force
        Write-Host "  [REMOVED] $profilePath"
    }

    # Windows Terminal
    @(
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
    ) | ForEach-Object {
        if (Test-Path $_) { Remove-Link $_ }
    }
}

function Link-Dotfiles {
    param([string]$DotfilesDir)

    Write-Info "Linking base dotfiles..."
    Ensure-Linked "$DotfilesDir\.gitconfig"        "$env:USERPROFILE\.gitconfig"
    Ensure-Linked "$DotfilesDir\.gitignore_global" "$env:USERPROFILE\.gitignore_global"

    # PowerShell profile — copy instead of symlink (OneDrive breaks symlinks in Documents)
    Write-Info "Copying PowerShell profile..."
    $psDir = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PowerShell'
    [System.IO.Directory]::CreateDirectory($psDir) | Out-Null
    $profileSource = "$DotfilesDir\shell\powershell\Microsoft.PowerShell_profile.ps1"
    $profileTarget = "$psDir\Microsoft.PowerShell_profile.ps1"
    if (Test-Path $profileSource) {
        Copy-Item $profileSource $profileTarget -Force
        Write-Host "  [COPY] $profileSource -> $profileTarget"
    }

    Write-Info "Linking config directories..."
    Ensure-Linked "$DotfilesDir\.config\starship.toml" "$env:USERPROFILE\.config\starship.toml"

    # Windows Terminal
    @(
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState",
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState"
    ) | ForEach-Object {
        if (Test-Path $_) {
            Ensure-Linked "$DotfilesDir\.config\windows-terminal\settings.json" "$_\settings.json"
        }
    }
}
