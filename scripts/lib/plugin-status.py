#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


def strip_jsonc_comments(content: str) -> str:
    lines: list[str] = []
    for line in content.splitlines():
        in_string = False
        escaped = False
        result: list[str] = []
        index = 0
        while index < len(line):
            char = line[index]
            if escaped:
                result.append(char)
                escaped = False
                index += 1
                continue
            if char == "\\" and in_string:
                result.append(char)
                escaped = True
                index += 1
                continue
            if char == '"':
                in_string = not in_string
                result.append(char)
                index += 1
                continue
            if not in_string and char == "/" and index + 1 < len(line) and line[index + 1] == "/":
                break
            result.append(char)
            index += 1
        lines.append("".join(result))
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = strip_jsonc_comments(path.read_text())
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


def normalize_enabled_plugins(values: dict[str, Any]) -> dict[str, bool]:
    return {str(key): bool(value) for key, value in values.items()}


def load_claude_plugins(path: Path) -> dict[str, bool]:
    return normalize_enabled_plugins(load_json(path).get("enabledPlugins", {}))


def load_codex_plugins(path: Path) -> dict[str, bool]:
    if not path.exists():
        return {}
    document = tomllib.loads(path.read_text())
    plugins = document.get("plugins", {})
    if not isinstance(plugins, dict):
        return {}
    return {
        str(plugin_id): bool(config.get("enabled", False))
        for plugin_id, config in plugins.items()
        if isinstance(config, dict)
    }


def load_copilot_declared_plugins(path: Path) -> dict[str, bool]:
    return normalize_enabled_plugins(load_json(path).get("enabledPlugins", {}))


def load_copilot_installed_plugins(path: Path) -> dict[str, bool]:
    document = load_json(path)
    plugins = document.get("installedPlugins", document.get("installed_plugins", []))
    installed: dict[str, bool] = {}
    if not isinstance(plugins, list):
        return installed
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        name = plugin.get("name")
        marketplace = plugin.get("marketplace")
        if not name or not marketplace:
            continue
        installed[f"{name}@{marketplace}"] = bool(plugin.get("enabled", False))
    return installed


def diff_lines(label: str, desired: dict[str, bool], actual: dict[str, bool]) -> list[str]:
    lines = [f"{label}:"]
    for plugin_id, enabled in desired.items():
        state = actual.get(plugin_id)
        if state == enabled:
            lines.append(f"  [OK] {plugin_id} enabled={str(enabled).lower()}")
        else:
            actual_value = "missing" if state is None else str(state).lower()
            lines.append(
                f"  [DRIFT] {plugin_id} desired={str(enabled).lower()} actual={actual_value}"
            )
    for plugin_id, enabled in actual.items():
        if plugin_id not in desired:
            lines.append(f"  [EXTRA] {plugin_id} enabled={str(enabled).lower()}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--home-dir", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    home_dir = Path(args.home_dir).expanduser().resolve()

    lines: list[str] = []
    lines.extend(
        diff_lines(
            "Claude",
            load_claude_plugins(repo_root / ".claude" / "settings.json"),
            load_claude_plugins(home_dir / ".claude" / "settings.json"),
        )
    )
    lines.extend(
        diff_lines(
            "Codex",
            load_codex_plugins(repo_root / ".codex" / "config.toml"),
            load_codex_plugins(home_dir / ".codex" / "config.toml"),
        )
    )
    desired_copilot = load_copilot_declared_plugins(repo_root / ".copilot" / "settings.json")
    lines.extend(
        diff_lines(
            "Copilot settings",
            desired_copilot,
            load_copilot_declared_plugins(home_dir / ".copilot" / "settings.json"),
        )
    )
    lines.extend(
        diff_lines(
            "Copilot installed",
            desired_copilot,
            load_copilot_installed_plugins(home_dir / ".copilot" / "config.json"),
        )
    )

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
