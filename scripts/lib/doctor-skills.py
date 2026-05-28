#!/usr/bin/env python3
"""Detect drift between the skills manifest, the lockfile, and skills/ on disk.

Three sources should agree:
  - scripts/skills-manifest.json  -> declared upstream sources (+ local skills)
  - .skill-lock.json              -> provenance/pin for upstream skills
  - skills/<name>/                -> the committed, vendored output

A fourth tier exists: private skills (machine-local, e.g. client-specific
tooling) that live in skills/ so the tools see them, but are git-ignored so they
never get committed or synced. The doctor asks git which folders are ignored and
skips them entirely, so their names never appear in any tracked file. Add such
names to .git/info/exclude (per-clone, never pushed).

See docs/skills-sync.md for the model. Exit non-zero on any ERROR (and on
WARNINGs too when --strict is given), so this is usable as a CI / pre-commit gate.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Folders under skills/ that are not skills.
IGNORE_DIRS = {".system"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] invalid JSON in {path}: {exc}")


def disk_skills(skills_dir: Path) -> list[str]:
    if not skills_dir.is_dir():
        raise SystemExit(f"[ERROR] missing skills dir: {skills_dir}")
    names = []
    for child in skills_dir.iterdir():
        if child.is_dir() and not child.name.startswith(".") and child.name not in IGNORE_DIRS:
            names.append(child.name)
    return sorted(names)


def git_ignored(root: Path, names: list[str]) -> set[str]:
    """Return the subset of skill folder names that git ignores.

    Uses `git check-ignore`, which honors .gitignore, .git/info/exclude, and the
    global excludesfile. Returns empty set if git is unavailable or errors, so a
    non-git environment (or CI without the private skills) degrades to "nothing
    ignored" — safe, because ignored private skills don't exist there anyway.
    """
    if not names:
        return set()
    rels = [f"skills/{n}" for n in names]
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--", *rels],
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError):
        return set()
    if proc.returncode not in (0, 1):  # 0 = matches printed, 1 = none; else error
        return set()
    ignored: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("skills/"):
            ignored.add(line[len("skills/"):].split("/")[0])
    return ignored


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skills manifest/lockfile/disk consistency.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--home-dir", type=Path, default=None)  # accepted for call-site symmetry
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    root: Path = args.repo_root
    manifest = load_json(root / "scripts" / "skills-manifest.json")
    lock = load_json(root / ".skill-lock.json")
    skills_dir = root / "skills"

    all_on_disk = set(disk_skills(skills_dir))
    private = git_ignored(root, sorted(all_on_disk))  # private, git-ignored, not synced
    on_disk = all_on_disk - private  # the tracked/synced set we actually check

    lock_skills: dict[str, Any] = lock.get("skills", {})
    lock_names = set(lock_skills)
    lock_sources = {entry.get("source") for entry in lock_skills.values()}

    manifest_sources = manifest.get("sources", [])
    manifest_repos = [s.get("repo") for s in manifest_sources if s.get("repo")]
    local_skills = set(manifest.get("local", []))

    errors: list[str] = []
    warnings: list[str] = []

    # ERROR 1: nested .git anywhere under a tracked skill (the npx clone-in footgun).
    # Private (git-ignored) skills may legitimately keep a .git to pull updates from source.
    for p in skills_dir.rglob(".git"):
        parts = p.relative_to(skills_dir).parts
        top = parts[0] if parts else ""
        if top in IGNORE_DIRS or top in private:
            continue
        errors.append(
            f"nested git repo in tree: {p.relative_to(root)} "
            f"(remove it; vendored skills must not carry .git)"
        )

    # ERROR 2: lockfile entry missing on disk or missing SKILL.md.
    for name in sorted(lock_names):
        folder = skills_dir / name
        if name not in on_disk:
            if name in private:
                continue  # handled by WARN below (leak risk)
            errors.append(f"lockfile skill not on disk: {name}")
        elif not (folder / "SKILL.md").is_file():
            errors.append(f"lockfile skill has no SKILL.md: {name}")

    # ERROR 3: on-disk (tracked) folder missing SKILL.md.
    for name in sorted(on_disk):
        if not (skills_dir / name / "SKILL.md").is_file():
            errors.append(f"skill folder has no SKILL.md: {name}")

    # ERROR 4: on-disk folder neither in lockfile nor declared local (orphan).
    undeclared = on_disk - lock_names - local_skills
    for name in sorted(undeclared):
        errors.append(
            f"undeclared skill on disk: {name} "
            f"(add its source to skills-manifest.json + lockfile, list it under "
            f'"local", or git-ignore it if it is private to this machine)'
        )

    # WARN 1: manifest source repo produced no lockfile entry.
    for repo in manifest_repos:
        if repo not in lock_sources:
            warnings.append(f"manifest source not installed (no lockfile entry): {repo}")

    # WARN 2: declared local skill not on disk.
    for name in sorted(local_skills - on_disk - private):
        warnings.append(f"local skill declared but missing on disk: {name}")

    # WARN 3: lockfile source has no manifest entry (provenance gap).
    for src in sorted(s for s in lock_sources if s and s not in set(manifest_repos)):
        warnings.append(f"lockfile source not declared in manifest: {src}")

    # WARN 4: a git-ignored skill is in the tracked lockfile — its name will leak.
    for name in sorted(private & lock_names):
        warnings.append(
            f"git-ignored skill present in tracked lockfile (name will be committed): {name} "
            f"(don't install machine-local skills with `npx skills add -g`)"
        )

    upstream_count = len(lock_names & on_disk)
    local_count = len(local_skills & on_disk)
    print("Skills doctor")
    print(f"  upstream skills (lockfile): {upstream_count}")
    print(f"  local skills:               {local_count}")
    if private:
        print(f"  private (git-ignored):      {len(private)}")
    print(f"  total tracked on disk:      {len(on_disk)}")
    print()

    for msg in errors:
        print(f"[ERROR] {msg}")
    for msg in warnings:
        print(f"[WARN]  {msg}")
    if not errors and not warnings:
        print("[OK] manifest, lockfile, and skills/ are consistent")

    print()
    print(f"Result: {'FAIL' if errors else 'PASS'} ({len(errors)} errors, {len(warnings)} warnings)")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
