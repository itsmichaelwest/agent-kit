#!/usr/bin/env python3
"""Verify every link declared in scripts/ai-agent-links.json is actually in place.

The manifest is the single source of truth for where agent configs get linked,
but until now nothing verified it. `doctor` only inspected skills, and the
"Layout:" summary in link-ai-agents.{sh,ps1} compared against a hardcoded list
of targets duplicated in both scripts. That list drifted from the manifest: the
`hooks` target was added without being added to the list, so ~/.agents/hooks was
never created while status kept reporting "current". Because
.claude/settings.json runs the safety hook from that path and a PreToolUse hook
exiting non-zero denies the call, every Bash and PowerShell call in every
session was blocked until the link was restored by hand.

Reports:
  ERROR    target missing, resolving somewhere unexpected, or naming an unknown
           source key
  WARNING  target is a real file/directory rather than a link (the Copy-Item
           fallback in helpers.ps1), so repo edits no longer propagate
  WARNING  layout marker missing or stale, meaning the manifest changed since
           the last `setup link`

Exit non-zero on any ERROR (and on WARNINGs too when --strict is given), so this
is usable as a CI / pre-commit gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

MANIFEST_REL = Path("scripts") / "ai-agent-links.json"
MARKER_REL = Path("agent-kit") / "ai-agent-layout-version"


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] missing manifest: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] invalid JSON in {path}: {exc}")


def manifest_digest(manifest: dict[str, Any]) -> str:
    """Fingerprint the link topology.

    Document order, not sorted, so the shell and PowerShell implementations can
    reproduce it without agreeing on a collation order. Formatting-only edits to
    the manifest do not change it; adding, removing, or repointing a target
    does.
    """
    sources: dict[str, str] = manifest.get("sources", {})
    lines = [
        "{}|{}|{}".format(
            target.get("source", ""),
            sources.get(target.get("source", ""), ""),
            target.get("path", ""),
        )
        for target in manifest.get("targets", [])
    ]
    payload = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:8]


def expected_marker(manifest: dict[str, Any]) -> str:
    return f"{manifest.get('layoutVersion', '0')}+{manifest_digest(manifest)}"


def state_file(home: Path) -> Path:
    """Mirror ai_agent_state_file() in link-ai-agents.sh / .ps1."""
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or str(home)
    else:
        root = os.environ.get("XDG_STATE_HOME") or str(home / ".local" / "state")
    return Path(root) / MARKER_REL


def expand_target(raw: str, home: Path) -> Path:
    if raw.startswith("~"):
        raw = str(home) + raw[1:]
    return Path(raw)


def link_destination(path: Path) -> str | None:
    """Return the raw link target, or None when path is not a link.

    Uses os.readlink rather than os.path.islink because a Windows directory
    junction -- what Ensure-Linked creates for every directory target -- is a
    reparse point that islink() reports as False.
    """
    try:
        return os.readlink(path)
    except OSError:
        return None


def same_path(left: str, right: str) -> bool:
    return os.path.normcase(os.path.realpath(left)) == os.path.normcase(
        os.path.realpath(right)
    )


def check_targets(
    manifest: dict[str, Any], root: Path, home: Path
) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    sources: dict[str, str] = manifest.get("sources", {})
    targets = manifest.get("targets", [])

    for target in targets:
        key = target.get("source", "")
        raw_path = target.get("path", "")
        source_rel = sources.get(key)

        if source_rel is None:
            errors.append(f"unknown source key {key!r} for target {raw_path}")
            continue

        source_abs = root / source_rel
        target_path = expand_target(raw_path, home)

        if not source_abs.exists():
            errors.append(f"missing source {source_abs} declared for {target_path}")
            continue

        destination = link_destination(target_path)

        if destination is None and not target_path.exists():
            errors.append(f"missing link {target_path} -> {source_abs}")
            continue

        if destination is None:
            warnings.append(
                f"{target_path} is a real file/directory, not a link to "
                f"{source_abs}; repo edits will not propagate"
            )
            continue

        if not same_path(str(target_path), str(source_abs)):
            errors.append(
                f"{target_path} resolves to {os.path.realpath(target_path)}, "
                f"expected {source_abs}"
            )

    return errors, warnings, len(targets)


def check_marker(manifest: dict[str, Any], home: Path) -> list[str]:
    marker_path = state_file(home)
    wanted = expected_marker(manifest)

    if not marker_path.is_file():
        return [f"no layout marker at {marker_path}; run `setup link`"]

    found = marker_path.read_text(encoding="utf-8").strip()
    if found != wanted:
        return [
            f"layout marker is {found!r}, expected {wanted!r}; the link manifest "
            f"changed since the last `setup link`"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that every link in ai-agent-links.json is in place."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--home-dir", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    root: Path = args.repo_root
    home: Path = args.home_dir or Path.home()
    manifest = load_manifest(root / MANIFEST_REL)

    errors, warnings, checked = check_targets(manifest, root, home)
    warnings += check_marker(manifest, home)

    for message in errors:
        print(f"[ERROR] {message}")
    for message in warnings:
        print(f"[WARNING] {message}")

    if not errors and not warnings:
        print(f"[OK] {checked} link targets verified")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
