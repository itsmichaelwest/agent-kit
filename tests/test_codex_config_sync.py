from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "sync-codex-config.py"


class CodexConfigSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.repo = root / "repo"
        self.home = root / "home"
        self.source = self.repo / "config" / "codex" / "global.toml"
        self.live = self.home / ".codex" / "config.toml"
        self.baseline = self.home / ".codex" / "agent-kit-config-baseline.json"
        (self.repo / "config" / "codex").mkdir(parents=True)
        (self.repo / ".codex" / "agents").mkdir(parents=True)
        self.home.mkdir()
        self.source.write_text(
            textwrap.dedent(
                """\
                #:schema https://developers.openai.com/codex/config-schema.json
                personality = "pragmatic"
                sandbox_mode = "danger-full-access"

                [features]
                multi_agent = true

                [agents]
                max_threads = 16
                """
            ),
            encoding="utf-8",
        )
        (self.repo / ".codex" / "agents" / "developer.toml").write_text(
            textwrap.dedent(
                '''\
                name = "developer"
                description = "Developer agent"
                model = "gpt-5.6-sol"

                developer_instructions = """
                # Developer
                """
                '''
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_sync(self, action: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [sys.executable, str(SCRIPT), action, "--repo-root", str(self.repo), "--home-dir", str(self.home)],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_apply_appends_and_preserves_unmanaged_config(self) -> None:
        self.live.parent.mkdir(parents=True)
        self.live.write_text(
            '[projects."/private/project"]\ntrust_level = "trusted"\n\n[future.runtime]\nvalue = "keep"\n',
            encoding="utf-8",
        )

        result = self.run_sync("apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.live.read_text(encoding="utf-8")
        self.assertIn('[projects."/private/project"]', text)
        self.assertIn('[future.runtime]', text)
        self.assertIn("# >>> agent-kit managed codex config", text)
        self.assertIn('[agents.developer]', text)
        self.assertTrue(self.baseline.exists())

    def test_apply_deduplicates_legacy_managed_settings_before_injection(self) -> None:
        self.live.parent.mkdir(parents=True)
        self.live.write_text(
            textwrap.dedent(
                """\
                personality = "pragmatic"

                [features]
                multi_agent = true

                [agents]
                max_threads = 16

                [agents.old-agent]
                config_file = "agents/old-agent.toml"

                [projects."/private/project"]
                trust_level = "trusted"
                """
            ),
            encoding="utf-8",
        )

        result = self.run_sync("apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        parsed = tomllib.loads(self.live.read_text(encoding="utf-8"))
        self.assertEqual(parsed["personality"], "pragmatic")
        self.assertEqual(parsed["features"]["multi_agent"], True)
        self.assertEqual(parsed["agents"]["max_threads"], 16)
        self.assertIn("developer", parsed["agents"])
        self.assertNotIn("old-agent", parsed["agents"])
        self.assertIn("projects", parsed)

    def test_apply_moves_unknown_settings_out_of_managed_markers(self) -> None:
        self.live.parent.mkdir(parents=True)
        self.live.write_text(
            textwrap.dedent(
                """\
                # >>> agent-kit managed codex config
                personality = "pragmatic"
                model = "machine-preference"

                [features]
                multi_agent = true

                [projects."/private/project"]
                trust_level = "trusted"

                [tui.machine_runtime]
                enabled = true

                # >>> agent-kit generated agents
                [agents.old-agent]
                config_file = "agents/old-agent.toml"
                # <<< agent-kit generated agents
                # <<< agent-kit managed codex config
                """
            ),
            encoding="utf-8",
        )

        result = self.run_sync("apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.live.read_text(encoding="utf-8")
        start = text.index("# >>> agent-kit managed codex config")
        end = text.index("# <<< agent-kit managed codex config")
        managed = text[start:end]
        self.assertNotIn("model =", managed)
        self.assertNotIn("[projects.", managed)
        self.assertNotIn("[tui.machine_runtime]", managed)
        self.assertIn('model = "machine-preference"', text[:start] + text[end:])
        self.assertIn('[projects."/private/project"]', text[end:])
        self.assertIn("[tui.machine_runtime]", text[end:])
        parsed = tomllib.loads(text)
        self.assertEqual(parsed["model"], "machine-preference")
        self.assertIn("projects", parsed)

    def test_apply_replaces_only_marked_block(self) -> None:
        self.live.parent.mkdir(parents=True)
        unmanaged = '[projects."/private/project"]\ntrust_level = "trusted"\n\n'
        self.live.write_text(unmanaged, encoding="utf-8")
        self.assertEqual(self.run_sync("apply").returncode, 0)
        self.source.write_text(
            self.source.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "updated"'
            ),
            encoding="utf-8",
        )

        result = self.run_sync("apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.live.read_text(encoding="utf-8")
        self.assertIn(unmanaged, text)
        self.assertLess(text.index("# >>> agent-kit managed codex config"), text.index(unmanaged))
        self.assertIn('personality = "updated"', text)

    def test_apply_is_noop_when_block_is_unchanged(self) -> None:
        self.assertEqual(self.run_sync("apply").returncode, 0)
        before = self.live.read_bytes()
        result = self.run_sync("apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.live.read_bytes(), before)
        self.assertFalse(list(self.live.parent.glob("config.toml.backup.*")))

    def test_apply_reports_live_only_drift_without_overwriting(self) -> None:
        self.assertEqual(self.run_sync("apply").returncode, 0)
        changed = self.live.read_text(encoding="utf-8").replace(
            'personality = "pragmatic"', 'personality = "calm"'
        )
        self.live.write_text(changed, encoding="utf-8")

        result = self.run_sync("apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('personality = "calm"', self.live.read_text(encoding="utf-8"))

    def test_apply_reports_two_sided_conflict_without_overwriting(self) -> None:
        self.assertEqual(self.run_sync("apply").returncode, 0)
        self.source.write_text(
            self.source.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "focused"'
            ),
            encoding="utf-8",
        )
        self.live.write_text(
            self.live.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "calm"'
            ),
            encoding="utf-8",
        )

        result = self.run_sync("apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('personality = "calm"', self.live.read_text(encoding="utf-8"))

    def test_partial_markers_fail_without_modifying_target(self) -> None:
        self.live.parent.mkdir(parents=True)
        original = "# >>> agent-kit managed codex config\npersonality = \"broken\"\n"
        self.live.write_text(original, encoding="utf-8")

        result = self.run_sync("apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.live.read_text(encoding="utf-8"), original)

    def test_capture_updates_portable_source_but_not_generated_agents(self) -> None:
        self.assertEqual(self.run_sync("apply").returncode, 0)
        self.live.write_text(
            self.live.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "calm"'
            ),
            encoding="utf-8",
        )
        self.baseline.unlink()

        result = self.run_sync("capture")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source_text = self.source.read_text(encoding="utf-8")
        self.assertIn('personality = "calm"', source_text)
        self.assertNotIn("developer_instructions", source_text)

    def test_capture_refuses_two_sided_portable_conflict(self) -> None:
        self.assertEqual(self.run_sync("apply").returncode, 0)
        self.source.write_text(
            self.source.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "focused"'
            ),
            encoding="utf-8",
        )
        self.live.write_text(
            self.live.read_text(encoding="utf-8").replace(
                'personality = "pragmatic"', 'personality = "calm"'
            ),
            encoding="utf-8",
        )
        original_source = self.source.read_text(encoding="utf-8")

        result = self.run_sync("capture")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_text(encoding="utf-8"), original_source)

    def test_setup_wires_capture_and_does_not_link_codex_config(self) -> None:
        shell_setup = (ROOT / "scripts" / "setup.sh").read_text(encoding="utf-8")
        shell_linker = (ROOT / "scripts" / "lib" / "link-ai-agents.sh").read_text(encoding="utf-8")
        powershell_setup = (ROOT / "scripts" / "setup.ps1").read_text(encoding="utf-8")
        powershell_linker = (ROOT / "scripts" / "lib" / "link-ai-agents.ps1").read_text(encoding="utf-8")

        self.assertIn("capture-codex-config", shell_setup)
        self.assertIn("capture-codex-config", powershell_setup)
        self.assertNotIn("link_codex_config", shell_linker)
        self.assertNotIn("Link-CodexConfig", powershell_linker)


if __name__ == "__main__":
    unittest.main()
