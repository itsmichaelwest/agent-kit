from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CodexPluginPolicyTests(unittest.TestCase):
    def test_default_codex_config_does_not_mirror_claude_marketplaces(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))

        marketplaces = config.get("marketplaces", {})
        plugins = config.get("plugins", {})

        self.assertNotIn("claude-plugins-official", marketplaces)
        self.assertFalse(
            [plugin_id for plugin_id in plugins if plugin_id.endswith("@claude-plugins-official")]
        )


if __name__ == "__main__":
    unittest.main()
