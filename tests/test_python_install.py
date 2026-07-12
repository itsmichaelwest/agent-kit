from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PythonInstallTests(unittest.TestCase):
    def test_unix_install_bootstraps_python_311_or_newer(self) -> None:
        script = (ROOT / "scripts" / "lib" / "install-deps.sh").read_text(encoding="utf-8")

        self.assertIn("brew install python", script)
        self.assertIn("pacman -S --noconfirm python", script)
        self.assertIn("apt-cache pkgnames", script)
        self.assertIn("sort -V", script)
        self.assertIn("python3-venv", script)
        self.assertIn("require_python", script)

    def test_windows_install_uses_python_install_manager_and_runtime(self) -> None:
        script = (ROOT / "scripts" / "lib" / "install-deps.ps1").read_text(encoding="utf-8")

        self.assertIn("9NQ7512CXL7T", script)
        self.assertIn("install --update default", script)
        self.assertNotIn("install 3.14", script)
        self.assertIn("Resolve-PythonCommand", script)

    def test_windows_script_invocation_requires_supported_python(self) -> None:
        helpers = (ROOT / "scripts" / "lib" / "helpers.ps1").read_text(encoding="utf-8")
        compiler = (ROOT / "scripts" / "lib" / "compile-agents.ps1").read_text(encoding="utf-8")
        sync = (ROOT / "scripts" / "lib" / "sync-codex-config.ps1").read_text(encoding="utf-8")

        self.assertIn('Args = @("exec")', helpers)
        self.assertNotIn('-V:3.14', helpers)
        self.assertIn("sys.version_info >= (3, 11)", helpers)
        self.assertIn("Resolve-PythonCommand", compiler)
        self.assertIn("Resolve-PythonCommand", sync)


if __name__ == "__main__":
    unittest.main()
