# Link base dotfiles, GitHub config, PowerShell profile (Windows).

function Link-Dotfiles {
    param([string]$DotfilesDir)

    Write-Info "Linking base dotfiles..."
    Ensure-Linked "$DotfilesDir\.gitconfig"        "$env:USERPROFILE\.gitconfig"
    Ensure-Linked "$DotfilesDir\.gitignore_global" "$env:USERPROFILE\.gitignore_global"

    Write-Info "Linking PowerShell profile..."
    Ensure-Linked "$DotfilesDir\shell\powershell\Microsoft.PowerShell_profile.ps1" `
        "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
    Ensure-Linked "$DotfilesDir\shell\powershell\Microsoft.PowerShell_profile.ps1" `
        "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

    Write-Info "Linking GitHub configuration..."
    $ghRoot = "$env:USERPROFILE\.github"
    New-Item -ItemType Directory -Path $ghRoot -Force | Out-Null
    Ensure-Linked "$DotfilesDir\.github\copilot-instructions.md" "$ghRoot\copilot-instructions.md"
    Ensure-Linked "$DotfilesDir\.github\prompts"                 "$ghRoot\prompts"
    Ensure-Linked "$DotfilesDir\agents"                          "$ghRoot\agents"

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
