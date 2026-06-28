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
SCRIPT = ROOT / "scripts" / "lib" / "bootstrap-codex-plugins.py"


class BootstrapCodexPluginsTests(unittest.TestCase):
    def test_registers_marketplaces_then_installs_missing_enabled_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            home = root / "home"
            bin_dir = root / "bin"
            repo.joinpath(".codex").mkdir(parents=True)
            home.mkdir()
            bin_dir.mkdir()

            repo.joinpath(".codex", "config.toml").write_text(
                textwrap.dedent(
                    """\
                    [marketplaces.example-market]
                    source_type = "git"
                    source = "https://github.com/example/market.git"

                    [plugins."alpha@example-market"]
                    enabled = true

                    [plugins."beta@example-market"]
                    enabled = true

                    [plugins."disabled@example-market"]
                    enabled = false
                    """
                ),
                encoding="utf-8",
                newline="\n",
            )

            list_payload = json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "alpha@example-market",
                            "installed": True,
                            "enabled": True,
                        }
                    ],
                    "available": [
                        {
                            "pluginId": "beta@example-market",
                            "installed": False,
                            "enabled": False,
                        }
                    ],
                }
            )
            list_file = root / "plugin-list.json"
            list_file.write_text(list_payload, encoding="utf-8", newline="\n")
            codex = bin_dir / ("codex.bat" if os.name == "nt" else "codex")
            if os.name == "nt":
                codex.write_text(
                    textwrap.dedent(
                        f"""\
                        @echo off
                        echo %*>>"%AK_CALLS%"
                        if "%*"=="--version" exit /b 0
                        if "%*"=="plugin marketplace add https://github.com/example/market.git" exit /b 0
                        if "%*"=="plugin marketplace upgrade" exit /b 0
                        if "%*"=="plugin list --available --json" (
                          type "{list_file}"
                          exit /b 0
                        )
                        if "%*"=="plugin add beta@example-market --json" exit /b 0
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
                        echo "$*" >> "$AK_CALLS"

                        case "$*" in
                          "--version") exit 0 ;;
                          "plugin marketplace add https://github.com/example/market.git") exit 0 ;;
                          "plugin marketplace upgrade") exit 0 ;;
                          "plugin list --available --json") cat '{list_file}'; exit 0 ;;
                          "plugin add beta@example-market --json") exit 0 ;;
                        esac

                        echo "unexpected args: $*" >&2
                        exit 1
                        """
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                codex.chmod(0o755)

            calls = root / "calls.log"
            env = os.environ.copy()
            env.pop("CODEX_CLI_PATH", None)
            env["AK_CALLS"] = str(calls)
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
            plugin_calls = [
                line
                for line in calls.read_text(encoding="utf-8").splitlines()
                if line.startswith("plugin ")
            ]
            self.assertEqual(
                plugin_calls,
                [
                    "plugin marketplace add https://github.com/example/market.git",
                    "plugin marketplace upgrade",
                    "plugin list --available --json",
                    "plugin add beta@example-market --json",
                ],
            )

    def test_registers_builtin_marketplace_paths_when_declared_plugins_need_them(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            home = root / "home"
            bin_dir = root / "bin"
            bundled = home / ".codex" / ".tmp" / "bundled-marketplaces" / "openai-bundled"
            repo.joinpath(".codex").mkdir(parents=True)
            bundled.mkdir(parents=True)
            bin_dir.mkdir()

            repo.joinpath(".codex", "config.toml").write_text(
                textwrap.dedent(
                    """\
                    [plugins."browser@openai-bundled"]
                    enabled = true
                    """
                ),
                encoding="utf-8",
                newline="\n",
            )

            payload_file = root / "plugin-list.json"
            payload_file.write_text(
                json.dumps(
                    {
                        "installed": [],
                        "available": [
                            {
                                "pluginId": "browser@openai-bundled",
                                "installed": False,
                                "enabled": False,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            codex = bin_dir / ("codex.bat" if os.name == "nt" else "codex")
            if os.name == "nt":
                codex.write_text(
                    textwrap.dedent(
                        f"""\
                        @echo off
                        echo %*>>"%AK_CALLS%"
                        if "%*"=="--version" exit /b 0
                        if "%*"=="plugin marketplace add {bundled}" exit /b 0
                        if "%*"=="plugin marketplace upgrade" exit /b 0
                        if "%*"=="plugin list --available --json" (
                          type "{payload_file}"
                          exit /b 0
                        )
                        if "%*"=="plugin add browser@openai-bundled --json" exit /b 0
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
                        echo "$*" >> "$AK_CALLS"
                        case "$*" in
                          "--version") exit 0 ;;
                          "plugin marketplace add {bundled}") exit 0 ;;
                          "plugin marketplace upgrade") exit 0 ;;
                          "plugin list --available --json") cat '{payload_file}'; exit 0 ;;
                          "plugin add browser@openai-bundled --json") exit 0 ;;
                        esac
                        exit 1
                        """
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                codex.chmod(0o755)

            calls = root / "calls.log"
            env = os.environ.copy()
            env.pop("CODEX_CLI_PATH", None)
            env["AK_CALLS"] = str(calls)
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
            plugin_calls = [
                line
                for line in calls.read_text(encoding="utf-8").splitlines()
                if line.startswith("plugin ")
            ]
            self.assertEqual(
                plugin_calls,
                [
                    f"plugin marketplace add {bundled}",
                    "plugin marketplace upgrade",
                    "plugin list --available --json",
                    "plugin add browser@openai-bundled --json",
                ],
            )


if __name__ == "__main__":
    unittest.main()
