# Single entry point for Windows setup.
param(
    [Parameter(Position=0)]
    [ValidateSet("install", "link", "link-dotfiles", "link-ai-agents", "status", "project-agents")]
    [string]$Action,

    [string]$ProjectPath,
    [switch]$SkipSubmodules,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ScriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DotfilesDir = Split-Path -Parent $ScriptsDir

. "$ScriptsDir\lib\helpers.ps1"
. "$ScriptsDir\lib\install-deps.ps1"
. "$ScriptsDir\lib\link-dotfiles.ps1"
. "$ScriptsDir\lib\link-ai-agents.ps1"

if ($Help -or -not $Action) {
    Write-Host @"
Usage: setup.ps1 <command> [options]

Commands:
  install             Full setup: deps + links
  link                Link dotfiles and AI agent configs (no installs)
  link-dotfiles       Link base dotfiles only
  link-ai-agents      Link AI agent configs only
  status              Show current link status
  project-agents      Link agents into a project (-ProjectPath required)

Options:
  -ProjectPath <path>  Project path (for project-agents)
  -SkipSubmodules      Skip git submodule initialization
  -Help                Show this help
"@
    exit 0
}

# Submodules
if (-not $SkipSubmodules -and (Test-Path "$DotfilesDir\.gitmodules")) {
    Write-Info "Initializing git submodules..."
    git -C $DotfilesDir submodule update --init --recursive 2>$null
}

function Show-Status {
    Write-Info "Current link status"
    Write-Host ""

    # Dotfiles
    Write-Info "Dotfiles:"
    $dotfileTargets = @(
        "$env:USERPROFILE\.gitconfig"
        "$env:USERPROFILE\.gitignore_global"
        "$env:USERPROFILE\.config\starship.toml"
        "$env:USERPROFILE\.github\copilot-instructions.md"
        "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
    )
    foreach ($target in $dotfileTargets) {
        if (Test-Path $target) {
            $item = Get-Item $target -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                Write-Host "  [OK] $target -> $($item.Target)" -ForegroundColor Green
            } else {
                Write-Host "  [EXISTS] $target (not a symlink)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [MISSING] $target" -ForegroundColor Red
        }
    }

    # AI agents (from manifest)
    Write-Host ""
    Write-Info "AI agent links:"
    Show-AiAgentStatus $DotfilesDir
}

switch ($Action) {
    "install"        { Install-Deps; Link-Dotfiles $DotfilesDir; Link-AiAgents $DotfilesDir }
    "link"           { Link-Dotfiles $DotfilesDir; Link-AiAgents $DotfilesDir }
    "link-dotfiles"  { Link-Dotfiles $DotfilesDir }
    "link-ai-agents" { Link-AiAgents $DotfilesDir }
    "status"         { Show-Status }
    "project-agents" {
        if (-not $ProjectPath) { Write-Err "Missing -ProjectPath"; exit 1 }
        if (-not (Test-Path $ProjectPath)) { Write-Err "Not a directory: $ProjectPath"; exit 1 }
        Write-Info "Linking agents into: $ProjectPath"
        Ensure-Linked "$DotfilesDir\agents" "$ProjectPath\.claude\agents"
    }
}

Write-Info "Done"
