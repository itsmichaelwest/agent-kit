from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "plugin-status.py"


class PluginStatusTests(unittest.TestCase):
    def test_codex_status_uses_plugin_manager_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            home = root / "home"
            bin_dir = root / "bin"
            repo.joinpath(".codex").mkdir(parents=True)
            repo.joinpath(".claude").mkdir()
            repo.joinpath(".copilot").mkdir()
            home.joinpath(".codex").mkdir(parents=True)
            home.joinpath(".claude").mkdir()
            home.joinpath(".copilot").mkdir()
            bin_dir.mkdir()

            codex_config = textwrap.dedent(
                """\
                [plugins."alpha@example"]
                enabled = true

                [plugins."beta@example"]
                enabled = true
                """
            )
            repo.joinpath(".codex", "config.toml").write_text(codex_config, encoding="utf-8")
            home.joinpath(".codex", "config.toml").write_text(codex_config, encoding="utf-8")
            repo.joinpath(".claude", "settings.json").write_text("{}", encoding="utf-8")
            home.joinpath(".claude", "settings.json").write_text("{}", encoding="utf-8")
            repo.joinpath(".copilot", "settings.json").write_text("{}", encoding="utf-8")
            home.joinpath(".copilot", "settings.json").write_text("{}", encoding="utf-8")
            home.joinpath(".copilot", "config.json").write_text("{}", encoding="utf-8")

            payload = json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "alpha@example",
                            "installed": True,
                            "enabled": True,
                        }
                    ],
                    "available": [
                        {
                            "pluginId": "beta@example",
                            "installed": False,
                            "enabled": False,
                        }
                    ],
                }
            )
            payload_file = root / "codex-plugins.json"
            payload_file.write_text(payload, encoding="utf-8")
            codex = bin_dir / ("codex.bat" if os.name == "nt" else "codex")
            if os.name == "nt":
                codex.write_text(
                    textwrap.dedent(
                        f"""\
                        @echo off
                        if "%*"=="plugin list --available --json" (
                          type "{payload_file}"
                          exit /b 0
                        )
                        exit /b 1
                        """
                    ),
                    encoding="utf-8",
                    newline="\r\n",
                )
            else:
                codex.write_text(
                    textwrap.dedent(
                        f"""\
                        #!/usr/bin/env bash
                        if [[ "$*" == "plugin list --available --json" ]]; then
                          cat '{payload_file}'
                          exit 0
                        fi
                        exit 1
                        """
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                codex.chmod(0o755)

            env = os.environ.copy()
            env.pop("CODEX_CLI_PATH", None)
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--home-dir",
                    str(home),
                ],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Codex installed:", result.stdout)
            self.assertIn("[OK] alpha@example enabled=true", result.stdout)
            self.assertIn("[DRIFT] beta@example desired=true actual=missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
