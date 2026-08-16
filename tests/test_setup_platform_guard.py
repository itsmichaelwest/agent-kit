from __future__ import annotations

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup.sh"


def find_git_bash() -> str | None:
    """Locate a Git Bash / MSYS / Cygwin bash, never WSL's.

    `shutil.which("bash")` on Windows normally resolves to System32\\bash.exe,
    the WSL launcher. WSL is real Linux, so the guard deliberately allows it --
    testing against it would prove nothing. Identify a candidate by asking it
    what it is.
    """
    candidates = [
        shutil.which("bash"),
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]

    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            result = subprocess.run(
                [candidate, "-c", "uname -s"], capture_output=True, text=True, timeout=30
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if re.search(r"MINGW|MSYS|CYGWIN", result.stdout, re.IGNORECASE):
            return candidate
    return None


class SetupPlatformGuardTests(unittest.TestCase):
    """setup.sh must refuse to run under Git Bash / MSYS2 / Cygwin.

    It links every target with `ln -s`, which on those shells silently produces
    a plain copy instead of a Windows reparse point: it prints [LINK], returns
    success, and leaves a file that drifts from the repo. Windows must go
    through setup.ps1, which creates real junctions.
    """

    @unittest.skipUnless(os.name == "nt", "the guard only fires on Windows shells")
    def test_setup_sh_refuses_to_run_on_windows(self) -> None:
        bash = find_git_bash()
        if not bash:
            self.skipTest("no Git Bash / MSYS / Cygwin bash available")

        result = subprocess.run(
            [bash, "scripts/setup.sh", "doctor"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr

        self.assertEqual(result.returncode, 1, output)
        self.assertIn("macOS/Linux entry point", output)
        self.assertIn("setup.ps1", output)

    def test_guard_pattern_matches_windows_shells_only(self) -> None:
        """The live case pattern, checked against real identifier triples.

        The pattern is read out of setup.sh rather than restated here, so
        editing the guard cannot leave this test passing against a stale copy.

        OSTYPE alone is not enough: Git Bash reports `cygwin` on some builds and
        `msys` on others, so the guard also consults uname -s and MSYSTEM.
        """
        bash = find_git_bash()
        if not bash:
            self.skipTest("no Git Bash / MSYS / Cygwin bash available")

        match = re.search(
            r"^\s*(msys\*\|[^)\n]+)\)", SETUP.read_text(encoding="utf-8"), re.MULTILINE
        )
        self.assertIsNotNone(match, "could not find the platform guard case pattern")
        pattern = match.group(1)

        cases = {
            "linux-gnu|Linux|": "allowed",
            "linux-musl|Linux|": "allowed",
            "darwin24|Darwin|": "allowed",
            "cygwin|MINGW64_NT-10.0-26200|MINGW64": "blocked",
            "msys|MSYS_NT-10.0|MSYS": "blocked",
            "cygwin|CYGWIN_NT-10.0|": "blocked",
        }

        script = f'case "$1" in\n  {pattern}) echo blocked ;;\n  *) echo allowed ;;\nesac\n'

        for identifiers, expected in cases.items():
            with self.subTest(identifiers=identifiers):
                result = subprocess.run(
                    [bash, "-c", script, "guard", identifiers],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.stdout.strip(), expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
