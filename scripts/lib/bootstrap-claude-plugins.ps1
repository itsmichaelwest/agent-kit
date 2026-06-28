# Bootstrap Claude Code plugins declared in .claude/settings.json (Windows).
# See scripts/lib/bootstrap-claude-plugins.sh for full context.

function Get-JsonPropertyValue {
    param(
        [Parameter(Mandatory=$false)] $Object,
        [Parameter(Mandatory=$true)] [string] $Name
    )

    if ($null -eq $Object) { return $null }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        return $Object.$Name
    }
    return $null
}

function Get-ClaudeMarketplaceSourceArg {
    param([Parameter(Mandatory=$true)] $Marketplace)

    $source = Get-JsonPropertyValue $Marketplace "source"
    $sourceKind = Get-JsonPropertyValue $source "source"
    $repo = Get-JsonPropertyValue $source "repo"
    $url = Get-JsonPropertyValue $source "url"
    $path = Get-JsonPropertyValue $source "path"

    if ($sourceKind -eq "github" -and $repo) { return $repo }
    if ($repo) { return $repo }
    if ($url) { return $url }
    if ($path) { return $path }
    if ($sourceKind) { return $sourceKind }
    return $null
}

function Write-IndentedCommandOutput {
    param([Parameter(Mandatory=$false)] $Output)

    if ($null -eq $Output) { return }
    $text = ($Output | Out-String).TrimEnd()
    if (-not $text) { return }
    foreach ($line in ($text -split "`r?`n")) {
        Write-Host "    $line" -ForegroundColor DarkGray
    }
}

function Bootstrap-ClaudePlugins {
    $settings = Join-Path $env:USERPROFILE ".claude\settings.json"

    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Warn "claude CLI not found on PATH; skipping plugin bootstrap"
        return 0
    }

    if (-not (Test-Path $settings)) {
        Write-Warn "$settings not found; run setup.ps1 link first"
        return 0
    }

    $data = Get-Content $settings -Raw | ConvertFrom-Json
    $marketplaces = if ($data.PSObject.Properties.Name -contains "extraKnownMarketplaces") { $data.extraKnownMarketplaces } else { $null }
    if ($marketplaces) {
        $marketplaceSpecs = @()
        foreach ($prop in $marketplaces.PSObject.Properties) {
            $sourceArg = Get-ClaudeMarketplaceSourceArg $prop.Value
            $marketplaceSpecs += [pscustomobject]@{
                Name = $prop.Name
                SourceArg = $sourceArg
            }
        }

        if ($marketplaceSpecs.Count -gt 0) {
            Write-Info ("Registering {0} Claude Code marketplace(s) from {1}" -f $marketplaceSpecs.Count, $settings)
            $marketplaceFail = 0

            foreach ($marketplace in $marketplaceSpecs) {
                if (-not $marketplace.SourceArg) {
                    Write-Host "  [FAIL] $($marketplace.Name) (missing source)" -ForegroundColor Red
                    $marketplaceFail++
                    continue
                }

                $output = & claude plugin marketplace add $marketplace.SourceArg 2>&1
                if ($LASTEXITCODE -eq 0) {
                    if (($output | Out-String) -match "already") {
                        Write-Host "  [SKIP] $($marketplace.Name) (already registered)" -ForegroundColor Yellow
                    } else {
                        Write-Host "  [OK]   $($marketplace.Name)" -ForegroundColor Green
                    }
                } else {
                    Write-Host "  [FAIL] $($marketplace.Name)" -ForegroundColor Red
                    Write-IndentedCommandOutput $output
                    $marketplaceFail++
                }
            }

            if ($marketplaceFail -gt 0) {
                Write-Host ""
                Write-Err "Failed to register $marketplaceFail Claude Code marketplace(s)"
                return 1
            }
        }
    }

    $enabled = if ($data.PSObject.Properties.Name -contains "enabledPlugins") { $data.enabledPlugins } else { $null }
    if (-not $enabled) {
        Write-Info "No enabled plugins declared in $settings"
        return 0
    }

    $specs = @()
    foreach ($prop in $enabled.PSObject.Properties) {
        if ($prop.Value -eq $true) { $specs += $prop.Name }
    }

    if ($specs.Count -eq 0) {
        Write-Info "No enabled plugins declared in $settings"
        return 0
    }

    Write-Info "Updating Claude Code plugin marketplaces"
    $marketplaceUpdateOutput = & claude plugin marketplace update 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK]   marketplaces updated" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] marketplaces" -ForegroundColor Red
        Write-IndentedCommandOutput $marketplaceUpdateOutput
        return 1
    }

    Write-Info ("Bootstrapping {0} Claude Code plugin(s) from {1}" -f $specs.Count, $settings)

    $ok = 0
    $skip = 0
    $fail = 0
    foreach ($spec in $specs) {
        $output = & claude plugin install $spec 2>&1
        if ($LASTEXITCODE -eq 0) {
            if (($output | Out-String) -match "already installed") {
                Write-Host "  [SKIP] $spec (already installed)" -ForegroundColor Yellow
                $skip++
            } else {
                Write-Host "  [OK]   $spec" -ForegroundColor Green
                $ok++
            }
        } else {
            Write-Host "  [FAIL] $spec" -ForegroundColor Red
            Write-IndentedCommandOutput $output
            $fail++
        }
    }

    Write-Host ""
    Write-Info "Installed: $ok, Skipped: $skip, Failed: $fail"
    if ($fail -gt 0) { return 1 }

    Write-Info ("Updating {0} Claude Code plugin(s)" -f $specs.Count)

    $updated = 0
    $updateSkip = 0
    $updateFail = 0
    foreach ($spec in $specs) {
        $output = & claude plugin update $spec 2>&1
        if ($LASTEXITCODE -eq 0) {
            if (($output | Out-String) -match "already|up[- ]to[- ]date|latest") {
                Write-Host "  [SKIP] $spec (already up to date)" -ForegroundColor Yellow
                $updateSkip++
            } else {
                Write-Host "  [OK]   $spec" -ForegroundColor Green
                $updated++
            }
        } else {
            Write-Host "  [FAIL] $spec" -ForegroundColor Red
            Write-IndentedCommandOutput $output
            $updateFail++
        }
    }

    Write-Host ""
    Write-Info "Updated: $updated, Skipped: $updateSkip, Failed: $updateFail"
    if ($updateFail -gt 0) { return 1 }
    return 0
}
