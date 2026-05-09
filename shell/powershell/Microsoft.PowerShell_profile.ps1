# =============================================================================
# POWERSHELL PROFILE
# =============================================================================

# Oh-My-Posh prompt
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    $profileDir = Split-Path -Parent $PROFILE
    oh-my-posh init pwsh --config "$profileDir\pure.omp.json" | Invoke-Expression
}

# =============================================================================
# NODE (fnm)
# =============================================================================

if (Get-Command fnm -ErrorAction SilentlyContinue) {
    fnm env --shell powershell | Out-String | Invoke-Expression
}

# =============================================================================
# MODULES
# =============================================================================

# Local module path (avoids OneDrive sync issues)
$localModDir = "$env:LOCALAPPDATA\PowerShell\Modules"
if ((Test-Path $localModDir) -and ($env:PSModulePath -notlike "*$localModDir*")) {
    $env:PSModulePath = "$localModDir;$env:PSModulePath"
}

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

Set-PSReadLineOption -EditMode Windows
Set-PSReadLineOption -MaximumHistoryCount 10000
Set-PSReadLineOption -HistoryNoDuplicates
Set-PSReadLineOption -BellStyle None

# Prediction needs an interactive TTY — skip in non-console hosts (Codex, redirected I/O)
# to avoid "predictive IntelliSense cannot be used" warnings.
$isInteractiveConsole = $Host.Name -eq 'ConsoleHost' -and
    -not [Console]::IsInputRedirected -and
    -not [Console]::IsOutputRedirected -and
    -not [Console]::IsErrorRedirected
if ($isInteractiveConsole) {
    Set-PSReadLineOption -PredictionSource History
    Set-PSReadLineOption -PredictionViewStyle ListView
}

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
