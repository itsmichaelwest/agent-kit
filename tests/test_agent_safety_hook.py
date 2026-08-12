from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "agent_safety.py"


def run_hook(event: str, command: str = "", response=None, *, codex: bool = True):
    payload = {
        "hook_event_name": event,
        "cwd": str(ROOT),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    if response is not None:
        payload["tool_response"] = response
    if codex:
        payload["model"] = "gpt-test"
    result = subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout) if result.stdout else None


class AgentSafetyHookTests(unittest.TestCase):
    def test_provider_configs_use_the_shared_hook(self) -> None:
        claude = json.loads((ROOT / ".claude" / "settings.json").read_text())
        codex = json.loads((ROOT / "config" / "codex" / "hooks.json").read_text())
        links = json.loads((ROOT / "scripts" / "ai-agent-links.json").read_text())

        for config in (claude, codex):
            for event in ("PreToolUse", "PostToolUse"):
                command = config["hooks"][event][0]["hooks"][0]["command"]
                self.assertIn(".agents/hooks/agent_safety.py", command)
        self.assertIn(
            {"source": "codex_hooks", "path": "~/.codex/hooks.json"},
            links["targets"],
        )

    def assert_denied(self, command: str) -> None:
        output = run_hook("PreToolUse", command)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_blocks_high_confidence_destructive_commands(self) -> None:
        for command in (
            "rm -rf /",
            "rm -rf .",
            "rm -rf $UNRESOLVED_TARGET",
            "git reset --hard HEAD~1",
            "git clean -fdx",
            "git push --force origin main",
            "git branch -D old-work",
            "git branch --delete --force old-work",
            "mkfs.ext4 /dev/sdb1",
            "dd if=/dev/zero of=/dev/disk4",
            "Remove-Item -Recurse -Force C:\\",
            "Clear-Disk -Number 2",
        ):
            with self.subTest(command=command):
                self.assert_denied(command)

    def test_allows_narrow_recoverable_commands(self) -> None:
        for command in (
            "rm -rf /tmp/agent-kit-build-123",
            "git push --force-with-lease origin feature",
            "git clean -nfdx",
            "git restore src/example.py",
        ):
            with self.subTest(command=command):
                self.assertIsNone(run_hook("PreToolUse", command))

    def test_blocks_commands_that_print_likely_secrets(self) -> None:
        for command in (
            "printenv",
            "echo $API_TOKEN",
            "cat .env",
            "cat ~/.ssh/id_ed25519",
            "Get-Content C:\\Users\\me\\project\\.env",
        ):
            with self.subTest(command=command):
                self.assert_denied(command)

    def test_codex_withholds_secret_tool_output(self) -> None:
        output = run_hook(
            "PostToolUse",
            response="API_TOKEN=abcdefghijklmnopqrstuvwxyz123456",
        )
        self.assertEqual(output["decision"], "block")
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", json.dumps(output))

    def test_claude_replaces_secret_tool_output(self) -> None:
        output = run_hook(
            "PostToolUse",
            response={"stdout": "password=abcdefghijklmnopqrstuvwxyz123456"},
            codex=False,
        )
        redacted = output["hookSpecificOutput"]["updatedToolOutput"]
        self.assertEqual(redacted["stdout"], "[REDACTED_SECRET]")

    def test_ordinary_output_is_silent(self) -> None:
        self.assertIsNone(
            run_hook("PostToolUse", response={"stdout": "tests passed"})
        )


if __name__ == "__main__":
    unittest.main()
