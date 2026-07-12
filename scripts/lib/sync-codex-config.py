#!/usr/bin/env python3
"""Synchronize Agent Kit's managed block in the user's Codex config."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Literal


START_MARKER = "# >>> agent-kit managed codex config"
END_MARKER = "# <<< agent-kit managed codex config"
GENERATED_START_MARKER = "# >>> agent-kit generated agents"
GENERATED_END_MARKER = "# <<< agent-kit generated agents"
BASELINE_NAME = "agent-kit-config-baseline.json"
LOCK_NAME = "agent-kit-config-sync.lock"
TABLE_HEADER_RE = re.compile(r"^\s*\[\[?([A-Za-z0-9_-]+)(?:[.\]]|\]\])")
TABLE_DETAIL_RE = re.compile(r"^\s*\[\[?([A-Za-z0-9_-]+)(?:\.([^\]]+))?")
TOP_LEVEL_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*=")
MARKERS = {START_MARKER, END_MARKER, GENERATED_START_MARKER, GENERATED_END_MARKER}

Classification = Literal["new", "unchanged", "repo-only", "live-only", "conflict"]


class SyncError(RuntimeError):
    pass


def codex_dir(home_dir: Path) -> Path:
    return home_dir / ".codex"


def live_config_path(home_dir: Path) -> Path:
    return codex_dir(home_dir) / "config.toml"


def baseline_path(home_dir: Path) -> Path:
    return codex_dir(home_dir) / BASELINE_NAME


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SyncError(f"Invalid TOML in {path}: {exc}") from exc


def validate_portable_source(source_path: Path, source: dict) -> None:
    forbidden = []
    if "projects" in source:
        forbidden.append("[projects]")
    agents = source.get("agents")
    if agents is not None and (
        not isinstance(agents, dict)
        or any(key != "max_threads" or isinstance(value, dict) for key, value in agents.items())
    ):
        forbidden.append("generated [agents.*]")
    if forbidden:
        joined = ", ".join(forbidden)
        raise SyncError(f"{source_path} contains non-portable/generated sections: {joined}")


def render_generated_agents(repo_root: Path) -> str:
    generated_dir = repo_root / ".codex" / "agents"
    lines = [GENERATED_START_MARKER]
    paths = sorted(generated_dir.glob("*.toml")) if generated_dir.exists() else []
    for path in paths:
        agent = load_toml(path)
        name = str(agent.get("name", path.stem))
        description = str(agent.get("description", "")).replace("\\", "\\\\").replace('"', '\\"')
        lines.extend(
            [
                f"[agents.{name}]",
                f'config_file = "agents/{path.name}"',
                f'description = "{description}"',
                "",
            ]
        )
    lines.append(GENERATED_END_MARKER)
    return "\n".join(lines) + "\n"


def render_managed_block(repo_root: Path) -> str:
    source_path = repo_root / "config" / "codex" / "global.toml"
    if not source_path.exists():
        raise SyncError(f"Missing portable Codex config: {source_path}")
    source_text = source_path.read_text(encoding="utf-8")
    source = load_toml(source_path)
    validate_portable_source(source_path, source)
    source_text = source_text.rstrip() + "\n"
    return f"{START_MARKER}\n{source_text}\n{render_generated_agents(repo_root)}{END_MARKER}\n"


def managed_roots(repo_root: Path) -> set[str]:
    source_path = repo_root / "config" / "codex" / "global.toml"
    source = load_toml(source_path)
    validate_portable_source(source_path, source)
    # Agent registrations are always compiler-owned, even when the source also
    # contains portable [agents] settings such as max_threads.
    return set(source) | {"agents"}


def strip_legacy_managed_content(text: str, roots: set[str], *, drop_comments: bool = False) -> str:
    """Remove unmarked Agent Kit-owned TOML roots while preserving other text."""
    output: list[str] = []
    skipping = False
    for line in text.splitlines(keepends=True):
        if line.strip() in MARKERS:
            continue
        if drop_comments and line.lstrip().startswith("#"):
            continue
        header = TABLE_DETAIL_RE.match(line)
        if header:
            root = header.group(1)
            nested = header.group(2)
            skipping = root in roots and not (nested is not None and root != "agents")
            if not skipping:
                output.append(line)
            continue
        if skipping:
            continue
        key = TOP_LEVEL_KEY_RE.match(line)
        if key and key.group(1) in roots and not output_has_table(output):
            continue
        output.append(line)
    return "".join(output)


def output_has_table(output: list[str]) -> bool:
    return any(TABLE_HEADER_RE.match(line) for line in output)


def split_root_prelude(text: str) -> tuple[str, str]:
    """Separate root assignments/comments from the first TOML table."""
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if TABLE_HEADER_RE.match(line):
            return "".join(lines[:index]), "".join(lines[index:])
    return text, ""


def canonical_config(unmanaged: str, desired: str, roots: set[str]) -> str:
    cleaned = strip_legacy_managed_content(unmanaged, roots)
    prelude, tables = split_root_prelude(cleaned)
    if prelude and not prelude.endswith("\n"):
        prelude += "\n"
    result = prelude + desired + tables
    try:
        tomllib.loads(result)
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"Rendered Codex config is invalid TOML: {exc}") from exc
    return result


def split_managed_block(text: str) -> tuple[str, str | None, str]:
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if (start == -1) != (end == -1):
        raise SyncError("Codex config has an incomplete Agent Kit managed block")
    if start == -1:
        return text, None, ""
    if end < start:
        raise SyncError("Codex config has an invalid Agent Kit marker order")
    end += len(END_MARKER)
    if text.startswith("\n", end):
        end += 1
    if text.find(START_MARKER, start + len(START_MARKER)) != -1:
        raise SyncError("Codex config has multiple Agent Kit managed blocks")
    block = text[start:end]
    generated_start = block.find(GENERATED_START_MARKER)
    generated_end = block.find(GENERATED_END_MARKER)
    if (generated_start == -1) != (generated_end == -1) or (
        generated_start != -1 and generated_end < generated_start
    ):
        raise SyncError("Codex config has malformed generated-agent markers")
    prefix = text[:start]
    suffix = text[end:]
    return prefix, block, suffix


def portable_from_block(block: str) -> str:
    generated_start = block.find(GENERATED_START_MARKER)
    if generated_start == -1:
        raise SyncError("Managed block is missing generated-agent markers")
    portable = block[len(START_MARKER) : generated_start].strip("\n")
    if not portable:
        raise SyncError("Managed block has no portable Codex settings")
    portable += "\n"
    try:
        tomllib.loads(portable)
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"Managed portable settings are invalid TOML: {exc}") from exc
    return portable


def managed_portable_from_block(block: str, roots: set[str]) -> str:
    body = block[len(START_MARKER) : block.find(END_MARKER)]
    lines: list[str] = []
    include = False
    for line in body.splitlines(keepends=True):
        if line.strip() in MARKERS:
            continue
        header = TABLE_DETAIL_RE.match(line)
        if header:
            root = header.group(1)
            nested = header.group(2)
            include = root in roots and (nested is None or (root == "agents" and nested is None))
            if root == "agents" and nested is not None:
                include = False
            if include:
                lines.append(line)
            continue
        if include:
            lines.append(line)
        elif not output_has_table(lines):
            key = TOP_LEVEL_KEY_RE.match(line)
            if key and key.group(1) in roots:
                lines.append(line)
    portable = "".join(lines).strip() + "\n"
    try:
        tomllib.loads(portable)
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"Managed portable settings are invalid TOML: {exc}") from exc
    return portable


def load_baseline(home_dir: Path) -> dict | None:
    path = baseline_path(home_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"Invalid baseline file {path}: {exc}") from exc
    if not isinstance(data, dict) or not data.get("block_sha256") or not data.get("portable_sha256"):
        raise SyncError(f"Invalid baseline file {path}")
    return data


def save_baseline(home_dir: Path, block: str) -> None:
    path = baseline_path(home_dir)
    payload = {
        "block_sha256": sha256(block),
        "portable_sha256": sha256(portable_from_block(block)),
    }
    atomic_write(path, json.dumps(payload, indent=2) + "\n", backup=False)


def classify(current: str | None, desired: str, baseline: dict | None) -> Classification:
    if current is None:
        return "new"
    current_hash = sha256(current)
    desired_hash = sha256(desired)
    if current_hash == desired_hash:
        return "unchanged"
    if baseline is None:
        return "live-only"
    baseline_hash = baseline["block_sha256"]
    if current_hash == baseline_hash:
        return "repo-only"
    if desired_hash == baseline_hash:
        return "live-only"
    return "conflict"


def acquire_lock(home_dir: Path) -> Path:
    path = codex_dir(home_dir) / LOCK_NAME
    try:
        path.mkdir(parents=True)
    except FileExistsError as exc:
        raise SyncError(f"Another Codex config sync is already running: {path}") from exc
    return path


def atomic_write(path: Path, text: str, *, backup: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        stamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_name(f"{path.name}.backup.{stamp}")
        backup_path.write_bytes(path.read_bytes())
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def apply_config(repo_root: Path, home_dir: Path) -> int:
    target = live_config_path(home_dir)
    if target.is_symlink():
        raise SyncError(f"Refusing to manage symlink target; remove it manually first: {target}")
    desired = render_managed_block(repo_root)
    roots = managed_roots(repo_root)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    prefix, current, suffix = split_managed_block(existing)
    prefix = strip_legacy_managed_content(prefix, roots)
    suffix = strip_legacy_managed_content(suffix, roots)
    baseline = load_baseline(home_dir)
    state = classify(current, desired, baseline)
    legacy_inside = (
        strip_legacy_managed_content(current, roots, drop_comments=True) if current is not None else ""
    )
    if not legacy_inside.strip():
        legacy_inside = ""
    if legacy_inside.strip():
        state = "repo-only"
    if state == "live-only":
        raise SyncError("Codex managed block has live-only changes; run capture-codex-config")
    if state == "conflict":
        raise SyncError("Codex managed block changed in both repository and live config; resolve before linking")
    unmanaged = prefix + legacy_inside + suffix
    updated = canonical_config(unmanaged, desired, roots)
    if state == "unchanged" and updated == existing:
        save_baseline(home_dir, current or desired)
        return 0
    atomic_write(target, updated, backup=target.exists())
    save_baseline(home_dir, desired)
    print(f"[WRITE] {target}")
    return 0


def capture_config(repo_root: Path, home_dir: Path) -> int:
    target = live_config_path(home_dir)
    if target.is_symlink():
        raise SyncError(f"Refusing to capture from symlink target; remove it manually first: {target}")
    if not target.exists():
        raise SyncError(f"Missing Codex config: {target}")
    existing = target.read_text(encoding="utf-8")
    _, current, _ = split_managed_block(existing)
    if current is None:
        raise SyncError("Codex config has no Agent Kit managed block to capture")
    roots = managed_roots(repo_root)
    portable = managed_portable_from_block(current, roots)
    source_path = repo_root / "config" / "codex" / "global.toml"
    source = load_toml(source_path)
    validate_portable_source(source_path, source)
    baseline = load_baseline(home_dir)
    if baseline:
        current_portable_hash = sha256(portable)
        source_portable_hash = sha256(source_path.read_text(encoding="utf-8").rstrip() + "\n")
        baseline_portable_hash = baseline["portable_sha256"]
        if current_portable_hash != baseline_portable_hash and source_portable_hash != baseline_portable_hash:
            raise SyncError("Portable Codex settings changed in both repository and live config; resolve before capture")
    if portable != source_path.read_text(encoding="utf-8"):
        atomic_write(source_path, portable, backup=True)
        print(f"[CAPTURE] {source_path}")
    save_baseline(home_dir, current)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("apply", "capture"))
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--home-dir", required=True, type=Path)
    args = parser.parse_args()
    lock = None
    try:
        lock = acquire_lock(args.home_dir)
        if args.action == "apply":
            return apply_config(args.repo_root, args.home_dir)
        return capture_config(args.repo_root, args.home_dir)
    except SyncError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    finally:
        if lock is not None:
            lock.rmdir()


if __name__ == "__main__":
    sys.exit(main())
