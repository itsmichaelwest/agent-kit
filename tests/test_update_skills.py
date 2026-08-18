from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.sh"
POWERSHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.ps1"


class UpdateSkillsTests(unittest.TestCase):
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
                    "HOME": str(temp / "home"),
                    "NPX_LOG": str(npx_log),
                    "PATH": f"{bin_dir}:{Path(jq).parent}:{env['PATH']}",
                }
            )
            command = f'''
set -u
source "{ROOT / 'scripts/lib/helpers.sh'}"
DOTFILES_DIR="{ROOT}"
source "{SHELL_WRAPPER}"
install_skill LukeberryPi/skills
'''
            result = subprocess.run(
                ["bash", "-c", command],
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
