from __future__ import annotations

import os
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_setup_platform_guard import find_git_bash


ROOT = Path(__file__).resolve().parents[1]
SHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.sh"
POWERSHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.ps1"


class UpdateSkillsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
    def test_update_uses_full_depth_only_for_selected_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            (temp / "scripts").mkdir()
            (temp / "scripts/skills-manifest.json").write_text(
                json.dumps({
                    "agents": ["codex"],
                    "sources": [
                        {"repo": "example/deep", "fullDepth": True,
                         "skills": ["wanted"]},
                        {"repo": "example/normal", "skills": ["ordinary"]},
                    ],
                }),
                encoding="utf-8",
            )
            driver = temp / "test.ps1"
            driver.write_text("""
param([string]$Wrapper, [string]$Fixture)
. $Wrapper
function Sync-SkillsLockfile { param($DotfilesDir) }
function Write-Info { param($Message) }
$script:Calls = [Collections.Generic.List[object]]::new()
function npx {
    $script:Calls.Add(@($args))
    $global:LASTEXITCODE = 0
}
$result = Update-Skills -DotfilesDir $Fixture
if ($result -ne 0) { throw "Update failed: $result" }
ConvertTo-Json -InputObject @($script:Calls.ToArray()) -Compress -Depth 5 |
    Set-Content -LiteralPath (Join-Path $Fixture 'calls.json')
""", encoding="utf-8")
            result = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(driver),
                 str(POWERSHELL_WRAPPER), str(temp)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            calls = json.loads((temp / "calls.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(3, len(calls))
            self.assertIn("--full-depth", calls[0])
            self.assertEqual("wanted", calls[0][calls[0].index("-s") + 1])
            self.assertNotIn("--full-depth", calls[1])
            self.assertEqual(["-y", "skills@latest", "update", "-g", "-y"], calls[2])

    def test_jqr_options_are_separate_shell_arguments(self) -> None:
        malformed = re.compile(r"\bjqr\s+-r(?:['\"]|--)")
        offenders = []
        for script in (ROOT / "scripts").rglob("*.sh"):
            for line_number, line in enumerate(
                script.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if malformed.search(line):
                    offenders.append(f"{script.relative_to(ROOT)}:{line_number}")

        self.assertEqual([], offenders)

    def test_install_skill_reads_default_agents_with_jq(self) -> None:
        jq = shutil.which("jq")
        self.assertIsNotNone(jq, "jq is required for this integration test")
        bash = find_git_bash() if os.name == "nt" else shutil.which("bash")
        self.assertIsNotNone(bash, "a host-compatible bash is required")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            bin_dir = temp / "bin"
            bin_dir.mkdir()
            npx_log = temp / "npx-args"
            npx = bin_dir / "npx"
            npx.write_text(
                '#!/bin/bash\nprintf "%s\\n" "$@" > "$NPX_LOG"\n',
                encoding="utf-8",
            )
            npx.chmod(0o755)

            env = os.environ.copy()
            env.update(
                {
                    "HOME": (temp / "home").as_posix(),
                    "NPX_LOG": npx_log.as_posix(),
                    "PATH": os.pathsep.join([str(bin_dir), str(Path(jq).parent), env["PATH"]]),
                }
            )
            command = f'''
set -u
source "{(ROOT / 'scripts/lib/helpers.sh').as_posix()}"
DOTFILES_DIR="{ROOT.as_posix()}"
source "{SHELL_WRAPPER.as_posix()}"
install_skill LukeberryPi/skills
'''
            result = subprocess.run(
                [bash, "-c", command],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            arguments = npx_log.read_text(encoding="utf-8").splitlines()
            expected_agents = [
                agent
                for name, agent in zip(arguments, arguments[1:])
                if name == "-a"
            ]
            self.assertGreater(len(expected_agents), 0)

    def test_install_skill_leaves_confirmation_to_the_caller(self) -> None:
        shell = SHELL_WRAPPER.read_text(encoding="utf-8")
        powershell = POWERSHELL_WRAPPER.read_text(encoding="utf-8")

        self.assertIn(
            'npx -y skills@latest add "$@" -g "${agent_args[@]}"',
            shell,
        )
        self.assertIn(
            '$cmdArgs = @("-y", "skills@latest", "add") + $SkillArgs + @("-g") + $agentArgs',
            powershell,
        )

    def test_update_skills_stays_unattended(self) -> None:
        shell = SHELL_WRAPPER.read_text(encoding="utf-8")
        powershell = POWERSHELL_WRAPPER.read_text(encoding="utf-8")

        self.assertIn('add "$repo" -g -y "${agent_args[@]}"', shell)
        self.assertIn('@("-y", "skills@latest", "add", $repo, "-g", "-y")', powershell)
        self.assertIn("npx -y skills@latest update -g -y", shell)
        self.assertIn("& npx -y skills@latest update -g -y", powershell)


if __name__ == "__main__":
    unittest.main()
