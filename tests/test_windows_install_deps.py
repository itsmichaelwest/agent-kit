from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell 7 is required")
class WindowsInstallDepsTests(unittest.TestCase):
    def run_powershell(self, body: str, case: dict | None = None) -> dict:
        with tempfile.TemporaryDirectory(prefix="agent-kit-deps-") as directory:
            scratch = Path(directory)
            driver = scratch / "driver.ps1"
            case_path = scratch / "case.json"
            case_path.write_text(json.dumps(case or {}), encoding="utf-8")
            driver.write_text(
                "param($RootPath, $CasePath, $ScratchRoot)\n"
                "$ErrorActionPreference = 'Stop'\n"
                "$case = Get-Content -LiteralPath $CasePath -Raw | ConvertFrom-Json\n"
                ". (Join-Path $RootPath 'scripts/lib/helpers.ps1')\n"
                ". (Join-Path $RootPath 'scripts/lib/install-deps.ps1')\n"
                + body,
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    PWSH,
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(driver),
                    str(ROOT),
                    str(case_path),
                    str(scratch),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)

    def installer_status(self, output: str, exit_code: int = 0) -> str:
        result = self.run_powershell(
            """
function winget {
    $global:LASTEXITCODE = $case.ExitCode
    $case.Output
}
@{ Status = Get-WinGetInstallerStatus 'eza-community.eza' 'arm64' } |
    ConvertTo-Json -Compress
""",
            {"Output": output, "ExitCode": exit_code},
        )
        return result["Status"]

    def test_show_success_without_applicable_installer_is_unavailable(self) -> None:
        self.assertEqual(
            self.installer_status(
                "Found eza [eza-community.eza]\nVersion: 0.23.4\n"
                "Installer:\n  Installer Type: zip\nNo applicable installer found."
            ),
            "unavailable",
        )

    def test_localized_installer_hash_indicates_available(self) -> None:
        self.assertEqual(
            self.installer_status(
                "Paket [eza-community.eza]\nInstaller:\n"
                "  Installationsprogramm SHA256: " + "aB" * 32
            ),
            "available",
        )

    def test_no_applicable_installer_hresult_is_unavailable(self) -> None:
        self.assertEqual(self.installer_status("", -1978335216), "unavailable")

    def test_release_note_checksum_does_not_indicate_available_installer(self) -> None:
        self.assertEqual(
            self.installer_status(
                "Found eza [eza-community.eza]\nRelease Notes:\n"
                "  Windows checksum: " + "a" * 64 +
                "\nInstallationsprogramm:\n  Kein anwendbares Installationsprogramm."
            ),
            "unavailable",
        )

    def test_unknown_failure_is_error_even_with_installer_hash(self) -> None:
        self.assertEqual(
            self.installer_status("  Installer SHA256: " + "a" * 64, -1),
            "error",
        )

    def test_empty_success_is_error(self) -> None:
        self.assertEqual(self.installer_status(""), "error")

    def install_case(self, **case: object) -> dict:
        return self.run_powershell(
            """
$script:installs = [Collections.Generic.List[object]]::new()
$script:prompts = [Collections.Generic.List[string]]::new()
$script:queries = [Collections.Generic.List[string]]::new()
$script:warnings = [Collections.Generic.List[string]]::new()
$script:installed = @{}
function Write-Warn { param($Msg) $script:warnings.Add($Msg) }
function Get-NativeArchitecture { 'arm64' }
function Refresh-InstallPath {}
function Resolve-PythonCommand { 'Fake-PythonManager' }
function Out-Host { process {} }
function Test-Path { $true }
function New-Item { throw 'Unexpected filesystem mutation' }
function Save-PSResource { throw 'Unexpected module installation' }
function Fake-PythonManager {
    $global:LASTEXITCODE = 0
    if ($args[0] -eq 'exec') { 'arm64' }
}
function Get-Command {
    param($Name, $CommandType, $ErrorAction)
    if ($Name -eq 'pymanager') { return [pscustomobject]@{ Source = 'Fake-PythonManager' } }
    throw "Unexpected command resolution: $Name"
}
function Get-ExecutableArchitecture {
    param($Name)
    $script:queries.Add($Name)
    if ($script:installed.ContainsKey($Name)) { return $script:installed[$Name] }
    if ($case.Mode -eq 'fallback' -and $Name -in @('eza', 'fd')) { return $null }
    if ($case.Mode -eq 'no-upgrade' -and $Name -eq 'oh-my-posh') { return $null }
    return 'arm64'
}
function Get-WinGetInstallerStatus {
    param($Id, $Architecture)
    if ($case.Mode -eq 'fallback' -and $Architecture -eq 'arm64' -and
        $Id -in @('eza-community.eza', 'sharkdp.fd')) { return 'unavailable' }
    return 'available'
}
function Confirm-X64Fallback {
    param($Name)
    $script:prompts.Add($Name)
    return $case.AcceptFallback
}
function winget {
    $id = $args[[Array]::IndexOf($args, '--id') + 1]
    if ($args[0] -eq 'list') {
        $global:LASTEXITCODE = 0
        return $id
    }
    if ($args[0] -ne 'install') { throw "Unexpected winget action: $($args[0])" }
    $arch = $args[[Array]::IndexOf($args, '--architecture') + 1]
    $script:installs.Add([pscustomobject]@{ Id = $id; Architecture = $arch })
    if ($case.Mode -eq 'no-upgrade' -and $id -eq 'JanDeDobbeleer.OhMyPosh') {
        $global:LASTEXITCODE = -1978335189
        $script:installed['oh-my-posh'] = $case.VerifiedArchitecture
        return 'No available upgrade found.'
    }
    $global:LASTEXITCODE = 0
    $name = switch ($id) {
        'eza-community.eza' { 'eza' }
        'sharkdp.fd' { 'fd' }
        default { throw "Unexpected package installation: $id" }
    }
    $script:installed[$name] = $arch
}
$exitCode = Install-Deps 6>$null
@{
    ExitCode = $exitCode
    Installs = @($script:installs.ToArray())
    Prompts = @($script:prompts.ToArray())
    Queries = @($script:queries.ToArray())
    Warnings = @($script:warnings.ToArray())
} | ConvertTo-Json -Depth 5 -Compress
""",
            case,
        )

    def test_arm64_unavailable_packages_install_x64_after_opt_in(self) -> None:
        result = self.install_case(Mode="fallback", AcceptFallback=True)
        self.assertEqual(result["ExitCode"], 0)
        self.assertEqual(result["Prompts"], ["eza", "fd"])
        self.assertEqual(
            result["Installs"],
            [
                {"Id": "eza-community.eza", "Architecture": "x64"},
                {"Id": "sharkdp.fd", "Architecture": "x64"},
            ],
        )
        self.assertEqual(result["Queries"].count("eza"), 2)
        self.assertEqual(result["Queries"].count("fd"), 2)
        self.assertTrue(any("x64 packages on ARM64 Windows" in w for w in result["Warnings"]))

    def test_arm64_unavailable_packages_skip_x64_after_opt_out(self) -> None:
        result = self.install_case(Mode="fallback", AcceptFallback=False)
        self.assertEqual(result["ExitCode"], 0)
        self.assertEqual(result["Prompts"], ["eza", "fd"])
        self.assertEqual(result["Installs"], [])
        self.assertTrue(any("eza-community.eza, sharkdp.fd" in w for w in result["Warnings"]))

    def test_coreutils_detection_uses_command_on_path(self) -> None:
        result = self.install_case(Mode="existing")
        self.assertEqual(result["ExitCode"], 0)
        self.assertIn("coreutils-manager", result["Queries"])
        self.assertNotIn("coreutils", result["Queries"])
        self.assertEqual(result["Installs"], [])

    def test_no_upgrade_hresult_still_verifies_installed_architecture(self) -> None:
        result = self.install_case(Mode="no-upgrade", VerifiedArchitecture="arm64")
        self.assertEqual(result["ExitCode"], 0)
        self.assertEqual(result["Queries"].count("oh-my-posh"), 2)
        self.assertEqual(result["Warnings"], [])
        self.assertEqual(
            result["Installs"],
            [{"Id": "JanDeDobbeleer.OhMyPosh", "Architecture": "arm64"}],
        )

    def test_no_upgrade_with_unknown_architecture_warns_about_verification(self) -> None:
        result = self.install_case(Mode="no-upgrade", VerifiedArchitecture=None)
        self.assertEqual(result["Queries"].count("oh-my-posh"), 2)
        self.assertTrue(any("could not verify the architecture" in w for w in result["Warnings"]))
        self.assertFalse(any("Could not install" in w for w in result["Warnings"]))

    def test_no_upgrade_with_x64_architecture_warns_about_conflict(self) -> None:
        result = self.install_case(Mode="no-upgrade", VerifiedArchitecture="x64")
        self.assertEqual(result["Queries"].count("oh-my-posh"), 2)
        self.assertTrue(any("on PATH is x64, expected arm64" in w for w in result["Warnings"]))
        self.assertFalse(any("Could not install" in w for w in result["Warnings"]))

    def architecture_case(self, **case: object) -> dict:
        return self.run_powershell(
            """
$fixture = Join-Path $ScratchRoot 'fixture.exe'
$bytes = [byte[]]::new(256)
$bytes[0] = 0x4d; $bytes[1] = 0x5a
[BitConverter]::GetBytes([int]0x80).CopyTo($bytes, 0x3c)
$bytes[0x80] = 0x50; $bytes[0x81] = 0x45
[BitConverter]::GetBytes([uint16]$case.Machine).CopyTo($bytes, 0x84)
[IO.File]::WriteAllBytes($fixture, $bytes)
function Get-Command {
    param($Name, $CommandType, $ErrorAction)
    [pscustomobject]@{ Source = $fixture }
}
if ($case.Alias) {
    function Get-Item {
        param($LiteralPath, [switch]$Force, $ErrorAction)
        [pscustomobject]@{
            Name = 'oh-my-posh.exe'; Length = 0
            Attributes = [IO.FileAttributes]::ReparsePoint
        }
    }
    function Get-AppxPackage {
        param($ErrorAction)
        foreach ($name in $case.PackageAliases) {
            [pscustomobject]@{ InstallLocation = $ScratchRoot; Alias = $name }
        }
    }
    function Get-AppxPackageManifest {
        param($Package, $ErrorAction)
        [xml]('<Package xmlns="urn:test"><Applications><Application Executable="fixture.exe">' +
            '<Extensions><Extension><AppExecutionAlias><ExecutionAlias Alias="' + $Package.Alias +
            '" /></AppExecutionAlias></Extension></Extensions></Application></Applications></Package>')
    }
}
@{ Architecture = Get-ExecutableArchitecture 'oh-my-posh' } | ConvertTo-Json -Compress
""",
            case,
        )

    def test_pe_machine_detection(self) -> None:
        for machine, architecture in ((0xAA64, "arm64"), (0x8664, "x64"), (0x014C, "x86")):
            with self.subTest(architecture=architecture):
                self.assertEqual(
                    self.architecture_case(Machine=machine, Alias=False)["Architecture"],
                    architecture,
                )

    def test_app_execution_alias_reads_exact_manifest_target(self) -> None:
        result = self.architecture_case(
            Machine=0xAA64,
            Alias=True,
            PackageAliases=["other-oh-my-posh.exe", "oh-my-posh.exe"],
        )
        self.assertEqual(result["Architecture"], "arm64")

    def test_unmatched_app_execution_alias_remains_unverified(self) -> None:
        result = self.architecture_case(
            Machine=0xAA64, Alias=True, PackageAliases=["other-oh-my-posh.exe"]
        )
        self.assertIsNone(result["Architecture"])

    def test_ambiguous_app_execution_alias_remains_unverified(self) -> None:
        result = self.architecture_case(
            Machine=0xAA64, Alias=True, PackageAliases=["oh-my-posh.exe", "oh-my-posh.exe"]
        )
        self.assertIsNone(result["Architecture"])


if __name__ == "__main__":
    unittest.main()
