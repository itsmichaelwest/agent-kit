#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_desired_config(repo_root: Path) -> dict[str, Any]:
    shared = load_toml(repo_root / ".codex" / "config.toml")
    overlay = load_toml(repo_root / ".codex" / "config.local.toml")
    return deep_merge(shared, overlay)


def command_exists(command: str) -> bool:
    try:
        result = subprocess.run(
            [command, "--version"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def find_codex_command(home_dir: Path, explicit: str | None) -> str | None:
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("CODEX_CLI_PATH"):
        candidates.append(os.environ["CODEX_CLI_PATH"])

    live_config = load_toml(home_dir / ".codex" / "config.toml")
    configured = (
        live_config.get("mcp_servers", {})
        .get("node_repl", {})
        .get("env", {})
        .get("CODEX_CLI_PATH")
    )
    if configured:
        candidates.append(str(configured))

    path_candidate = shutil.which("codex")
    if path_candidate:
        candidates.append(path_candidate)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        runtime_bins = sorted(
            Path(local_app_data).glob("OpenAI/Codex/bin/*/codex.exe"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        candidates.extend(str(path) for path in runtime_bins)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if command_exists(candidate):
            return candidate
    return None


def run_codex(codex: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [codex, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def print_output(output: str, *, indent: str = "    ") -> None:
    text = output.strip()
    if not text:
        return
    for line in text.splitlines():
        print(f"{indent}{line}")


def enabled_plugin_ids(config: dict[str, Any]) -> list[str]:
    plugins = config.get("plugins", {})
    if not isinstance(plugins, dict):
        return []
    return [
        str(plugin_id)
        for plugin_id, plugin_config in plugins.items()
        if isinstance(plugin_config, dict) and plugin_config.get("enabled") is True
    ]


def marketplace_sources(config: dict[str, Any]) -> list[tuple[str, str]]:
    marketplaces = config.get("marketplaces", {})
    if not isinstance(marketplaces, dict):
        return []

    sources: list[tuple[str, str]] = []
    for name, marketplace in marketplaces.items():
        if not isinstance(marketplace, dict):
            continue
        source = marketplace.get("source")
        if source:
            sources.append((str(name), str(source)))
    return sources


def infer_builtin_marketplace_sources(home_dir: Path, plugin_ids: list[str]) -> list[tuple[str, str]]:
    needed = {plugin_id.rsplit("@", 1)[1] for plugin_id in plugin_ids if "@" in plugin_id}
    candidates = {
        "openai-bundled": home_dir / ".codex" / ".tmp" / "bundled-marketplaces" / "openai-bundled",
        "openai-primary-runtime": home_dir
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "plugins"
        / "openai-primary-runtime",
    }
    return [
        (name, str(path))
        for name, path in candidates.items()
        if name in needed and path.exists()
    ]


def load_plugin_state(codex: str) -> dict[str, bool] | None:
    result = run_codex(codex, ["plugin", "list", "--available", "--json"])
    if result.returncode != 0:
        print("  [FAIL] plugin list")
        print_output(result.stdout)
        print_output(result.stderr)
        return None

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"  [FAIL] plugin list returned invalid JSON: {exc}")
        print_output(result.stdout)
        return None

    state: dict[str, bool] = {}
    for group in ("installed", "available"):
        entries = payload.get(group, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            plugin_id = entry.get("pluginId")
            if plugin_id:
                state[str(plugin_id)] = bool(entry.get("enabled", False))
    return state


def bootstrap(repo_root: Path, home_dir: Path, codex_command: str | None) -> int:
    config = load_desired_config(repo_root)
    desired_plugins = enabled_plugin_ids(config)
    desired_marketplaces = marketplace_sources(config)
    declared_marketplaces = {name for name, _ in desired_marketplaces}
    desired_marketplaces.extend(
        (name, source)
        for name, source in infer_builtin_marketplace_sources(home_dir, desired_plugins)
        if name not in declared_marketplaces
    )

    if not desired_plugins and not desired_marketplaces:
        print(f"[INFO] No Codex plugins or marketplaces declared in {repo_root / '.codex' / 'config.toml'}")
        return 0

    codex = find_codex_command(home_dir, codex_command)
    if not codex:
        print("[WARN] codex CLI not found or not runnable; skipping plugin bootstrap")
        return 0

    if desired_marketplaces:
        print(f"[INFO] Registering {len(desired_marketplaces)} Codex marketplace(s)")
        failures = 0
        for name, source in desired_marketplaces:
            result = run_codex(codex, ["plugin", "marketplace", "add", source])
            if result.returncode == 0:
                print(f"  [OK]   {name}")
            else:
                print(f"  [FAIL] {name}")
                print_output(result.stdout)
                print_output(result.stderr)
                failures += 1
        if failures:
            print(f"[ERROR] Failed to register {failures} Codex marketplace(s)")
            return 1

    print("[INFO] Updating Codex plugin marketplaces")
    result = run_codex(codex, ["plugin", "marketplace", "upgrade"])
    if result.returncode == 0:
        print("  [OK]   marketplaces updated")
    else:
        print("  [FAIL] marketplaces")
        print_output(result.stdout)
        print_output(result.stderr)
        return 1

    if not desired_plugins:
        print(f"[INFO] No enabled Codex plugins declared in {repo_root / '.codex' / 'config.toml'}")
        return 0

    state = load_plugin_state(codex)
    if state is None:
        return 1

    print(f"[INFO] Bootstrapping {len(desired_plugins)} Codex plugin(s)")
    ok = 0
    skip = 0
    fail = 0
    for plugin_id in desired_plugins:
        if state.get(plugin_id) is True:
            print(f"  [SKIP] {plugin_id} (already enabled)")
            skip += 1
            continue

        result = run_codex(codex, ["plugin", "add", plugin_id, "--json"])
        if result.returncode == 0:
            print(f"  [OK]   {plugin_id}")
            ok += 1
        else:
            print(f"  [FAIL] {plugin_id}")
            print_output(result.stdout)
            print_output(result.stderr)
            fail += 1

    print("")
    print(f"[INFO] Installed: {ok}, Skipped: {skip}, Failed: {fail}")
    return 1 if fail else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Codex plugins declared in .codex/config.toml")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--home-dir", required=True)
    parser.add_argument("--codex-command")
    args = parser.parse_args()

    return bootstrap(
        Path(args.repo_root).expanduser().resolve(),
        Path(args.home_dir).expanduser().resolve(),
        args.codex_command,
    )


if __name__ == "__main__":
    sys.exit(main())
