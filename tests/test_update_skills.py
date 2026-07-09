from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.sh"
POWERSHELL_WRAPPER = ROOT / "scripts" / "lib" / "update-skills.ps1"


class UpdateSkillsTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
