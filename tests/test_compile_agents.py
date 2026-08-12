from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "compile-agents.py"


class CompileAgentsTests(unittest.TestCase):
    def run_compiler(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_config(self, templates: Path) -> None:
        templates.joinpath("config.toml").write_text(
            textwrap.dedent(
                """\
                [providers.claude]
                fast = "haiku"
                balanced = "sonnet"
                strong = "opus"

                [providers.codex]
                fast = "gpt-5.6-luna"
                balanced = "gpt-5.6-terra"
                strong = "gpt-5.6-sol"
                """
            ),
            encoding="utf-8",
        )

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

                    Sample body with a Windows path: C:\\tmp\\capture.png
                    """
                ),
                encoding="utf-8",
            )
            agents.joinpath("sample.agent.md").write_text("stale alias", encoding="utf-8")

            result = self.run_compiler(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(agents.joinpath("sample.md").exists())
            self.assertFalse(agents.joinpath("sample.agent.md").exists())
            tomllib.loads(codex_agents.joinpath("sample.toml").read_text(encoding="utf-8"))

    def test_compile_resolves_inherited_body_and_provider_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            templates = repo / "agent-templates"
            templates.mkdir()
            self.write_config(templates)
            templates.joinpath("developer.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: "developer"
                    description: "General implementation."
                    model_class: "strong"
                    claude:
                      color: "orange"
                    codex:
                      model_reasoning_effort: "high"
                    ---

                    Shared developer contract.
                    """
                ),
                encoding="utf-8",
            )
            templates.joinpath("developer-lite.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: "developer-lite"
                    description: "Small bounded implementation."
                    model_class: "balanced"
                    extends: "developer"
                    claude:
                      color: "yellow"
                    codex:
                      model_reasoning_effort: "medium"
                    ---
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_compiler(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            markdown = repo.joinpath("agents/developer-lite.md").read_text(encoding="utf-8")
            codex = tomllib.loads(
                repo.joinpath(".codex/agents/developer-lite.toml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("Shared developer contract.", markdown)
            self.assertIn('color: "yellow"', markdown)
            self.assertEqual(codex["model"], "gpt-5.6-terra")
            self.assertEqual(codex["model_reasoning_effort"], "medium")
            self.assertIn("Shared developer contract.", codex["developer_instructions"])

    def test_compile_rejects_unknown_provider_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            templates = repo / "agent-templates"
            templates.mkdir()
            self.write_config(templates)
            templates.joinpath("sample.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: "sample"
                    description: "Sample agent."
                    model_class: "fast"
                    codex:
                      imaginary_permission: "allow"
                    ---

                    Sample body.
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_compiler(repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsupported codex field", result.stderr)

    def test_compile_rejects_inheritance_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            templates = repo / "agent-templates"
            templates.mkdir()
            self.write_config(templates)
            for name, parent in (("first", "second"), ("second", "first")):
                templates.joinpath(f"{name}.md").write_text(
                    textwrap.dedent(
                        f"""\
                        ---
                        name: "{name}"
                        description: "{name} agent."
                        model_class: "fast"
                        extends: "{parent}"
                        ---
                        """
                    ),
                    encoding="utf-8",
                )

            result = self.run_compiler(repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Inheritance cycle", result.stderr)


if __name__ == "__main__":
    unittest.main()
