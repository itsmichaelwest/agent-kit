from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CLAUDE_MARKETPLACES = {"claude-plugins-official"}
CODEX_MARKETPLACES = {"openai-bundled", "openai-curated", "openai-primary-runtime"}
COPILOT_MARKETPLACES = {"awesome-copilot", "copilot-plugins"}


class CodexPluginPolicyTests(unittest.TestCase):
    def test_default_codex_config_does_not_mirror_claude_marketplaces(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))

        marketplaces = config.get("marketplaces", {})
        plugins = config.get("plugins", {})

        self.assertNotIn("claude-plugins-official", marketplaces)
        self.assertFalse(
            [plugin_id for plugin_id in plugins if plugin_id.endswith("@claude-plugins-official")]
        )

    def test_default_codex_config_does_not_mirror_copilot_marketplaces(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))

        marketplaces = config.get("marketplaces", {})
        plugins = config.get("plugins", {})

        self.assertFalse(COPILOT_MARKETPLACES & set(marketplaces))
        self.assertFalse(
            [
                plugin_id
                for plugin_id in plugins
                if any(plugin_id.endswith(f"@{marketplace}") for marketplace in COPILOT_MARKETPLACES)
            ]
        )


class CopilotPluginPolicyTests(unittest.TestCase):
    def test_default_copilot_settings_do_not_mirror_claude_or_codex_marketplaces(self) -> None:
        settings = json.loads((ROOT / ".copilot" / "settings.json").read_text(encoding="utf-8"))

        forbidden_marketplaces = CLAUDE_MARKETPLACES | CODEX_MARKETPLACES
        marketplaces = settings.get("extraKnownMarketplaces", {})
        plugins = settings.get("enabledPlugins", {})

        self.assertFalse(forbidden_marketplaces & set(marketplaces))
        self.assertFalse(
            [
                plugin_id
                for plugin_id in plugins
                if any(plugin_id.endswith(f"@{marketplace}") for marketplace in forbidden_marketplaces)
            ]
        )

    def test_default_copilot_settings_include_intentional_superpowers_marketplace(self) -> None:
        settings = json.loads((ROOT / ".copilot" / "settings.json").read_text(encoding="utf-8"))

        self.assertEqual(
            settings["extraKnownMarketplaces"]["superpowers-marketplace"]["source"]["repo"],
            "obra/superpowers-marketplace",
        )
        self.assertTrue(settings["enabledPlugins"]["superpowers@superpowers-marketplace"])


if __name__ == "__main__":
    unittest.main()
