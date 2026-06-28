from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "merge-codex-config.py"


class MergeCodexConfigTests(unittest.TestCase):
    def test_preserved_windows_project_paths_emit_valid_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shared = root / "shared.toml"
            overlay = root / "overlay.toml"
            live = root / "live.toml"
            shared.write_text('model = "gpt-5.5"\n', encoding="utf-8")
            overlay.write_text("", encoding="utf-8")
            live.write_text(
                textwrap.dedent(
                    """\
                    [projects.'f:\\repos\\hearth']
                    trust_level = "trusted"
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(shared), str(overlay), str(live)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            parsed = tomllib.loads(result.stdout)
            self.assertEqual(
                parsed["projects"]["f:\\repos\\hearth"]["trust_level"],
                "trusted",
            )


if __name__ == "__main__":
    unittest.main()
