from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "compile-agents.py"


class CompileAgentsTests(unittest.TestCase):
    def test_compile_removes_repo_local_copilot_agent_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            templates = repo / "agent-templates"
            agents = repo / "agents"
            codex_agents = repo / ".codex" / "agents"
            templates.mkdir()
            agents.mkdir()
            codex_agents.mkdir(parents=True)

            templates.joinpath("config.toml").write_text(
                textwrap.dedent(
                    """\
                    [providers.claude]
                    fast = "haiku"

                    [providers.codex]
                    fast = "gpt-5.4-mini"
                    """
                ),
                encoding="utf-8",
            )
            templates.joinpath("sample.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: "sample"
                    description: "Sample agent."
                    model_class: "fast"
                    ---

                    # Role

                    Sample body.
                    """
                ),
                encoding="utf-8",
            )
            agents.joinpath("sample.agent.md").write_text("stale alias", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(agents.joinpath("sample.md").exists())
            self.assertFalse(agents.joinpath("sample.agent.md").exists())


if __name__ == "__main__":
    unittest.main()
