# =============================================================================
# POWERSHELL PROFILE
# =============================================================================

# Oh-My-Posh prompt
oh-my-posh init pwsh | Invoke-Expression

# =============================================================================
# NODE (fnm)
# =============================================================================

if (Get-Command fnm -ErrorAction SilentlyContinue) {
    fnm env --shell powershell | Out-String | Invoke-Expression
}

# =============================================================================
# MODULES
# =============================================================================

# Terminal Icons (file icons in ls output)
Import-Module Terminal-Icons -ErrorAction SilentlyContinue

# z — jump to frecent directories
Import-Module z -ErrorAction SilentlyContinue

# PSFzf — fuzzy finder (Ctrl+R for history, Ctrl+T for files)
if (Get-Module -ListAvailable -Name PSFzf) {
    Import-Module PSFzf
    Set-PsFzfOption -PSReadlineChordProvider 'Ctrl+t' -PSReadlineChordReverseHistory 'Ctrl+r'
}

# =============================================================================
# PSREADLINE
# =============================================================================

Set-PSReadLineOption -PredictionSource History
Set-PSReadLineOption -PredictionViewStyle ListView
Set-PSReadLineOption -EditMode Windows
Set-PSReadLineOption -MaximumHistoryCount 10000
Set-PSReadLineOption -HistoryNoDuplicates $true
Set-PSReadLineOption -BellStyle None

# =============================================================================
# EZA (modern ls)
# =============================================================================

if (Get-Command eza -ErrorAction SilentlyContinue) {
    function ls-eza { eza --long --group-directories-first --icons --color }
    Set-Alias ls ls-eza

    function ll { eza -l --all --group-directories-first --icons }
    function la { eza -la --group-directories-first --icons }
    function lt { eza --tree --git-ignore --icons }
}

# =============================================================================
# PATH
# =============================================================================

# Bun
if (Test-Path "$env:USERPROFILE\.bun") {
    $env:PATH += ";$env:USERPROFILE\.bun\bin"
}

# Rust
if (Test-Path "$env:USERPROFILE\.cargo\bin") {
    $env:PATH += ";$env:USERPROFILE\.cargo\bin"
}

# User bin
if (Test-Path "$env:USERPROFILE\.local\bin") {
    $env:PATH += ";$env:USERPROFILE\.local\bin"
}

# UTF-8 encoding
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
