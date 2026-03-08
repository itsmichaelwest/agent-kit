param(
    [Parameter(Mandatory)][ValidateSet("claude","codex","copilot")][string]$Engine,
    [Parameter(Mandatory)][string]$Prompt,
    [string]$Cwd = ".",
    [int]$Timeout = 300
)

$ErrorActionPreference = "Stop"

function Format-JsonOutput {
    param([string]$Engine, [string]$Status, [string]$Output, [string]$Error)
    $obj = @{ engine = $Engine; status = $Status; output = $Output; error = $Error }
    return ($obj | ConvertTo-Json -Compress)
}

function Test-EngineAvailable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Engine {
    param([string]$Engine, [string]$Command, [string[]]$Args)

    if (-not (Test-EngineAvailable $Engine)) {
        Format-JsonOutput -Engine $Engine -Status "unavailable" -Output "" -Error "$Engine CLI not found"
        return
    }

    try {
        Push-Location $Cwd
        $job = Start-Job -ScriptBlock {
            param($cmd, $a)
            & $cmd @a 2>&1 | Out-String
        } -ArgumentList $Command, $Args

        $completed = Wait-Job $job -Timeout $Timeout
        if ($null -eq $completed) {
            Stop-Job $job
            Remove-Job $job -Force
            Format-JsonOutput -Engine $Engine -Status "timeout" -Output "" -Error "Timed out after ${Timeout}s"
        } else {
            $out = Receive-Job $job
            Remove-Job $job
            Format-JsonOutput -Engine $Engine -Status "ok" -Output $out -Error ""
        }
    } catch {
        Format-JsonOutput -Engine $Engine -Status "error" -Output "" -Error $_.Exception.Message
    } finally {
        Pop-Location
    }
}

switch ($Engine) {
    "claude"  { Invoke-Engine -Engine "claude"  -Command "claude"  -Args @("-p", $Prompt, "--output-format", "text") }
    "codex"   { Invoke-Engine -Engine "codex"   -Command "codex"   -Args @("exec", $Prompt) }
    "copilot" { Invoke-Engine -Engine "copilot" -Command "copilot" -Args @("-p", $Prompt) }
}
