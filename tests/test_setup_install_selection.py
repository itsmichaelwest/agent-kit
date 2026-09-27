from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SetupInstallSelectionTests(unittest.TestCase):
    def test_unattended_install_requires_all_flag(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/setup.sh", "install"],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("install --all", result.stdout + result.stderr)
        self.assertNotIn("Initializing git submodules", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
