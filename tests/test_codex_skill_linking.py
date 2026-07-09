import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts" / "ai-agent-links.json"
LINKER = ROOT / "scripts" / "lib" / "link-ai-agents.sh"


class CodexSkillLinkingTests(unittest.TestCase):
    def test_codex_uses_the_documented_user_skills_root(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertIn(
            {"source": "skills", "path": "~/.agents/skills"},
            manifest["targets"],
        )
        self.assertNotIn(
            {"source": "skills", "path": "~/.codex/skills"},
            manifest["targets"],
        )

    def test_linker_does_not_manage_codex_system_skills(self) -> None:
        linker = LINKER.read_text(encoding="utf-8")
        match = re.search(
            r"legacy_ai_agent_targets\(\) \{(?P<body>.*?)^\}",
            linker,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match)
        legacy_block = match.group("body")

        self.assertNotIn('"$HOME/.codex/skills"', legacy_block)
        self.assertNotIn("migrate_codex_system_skills", linker)


if __name__ == "__main__":
    unittest.main()
