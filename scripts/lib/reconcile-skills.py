#!/usr/bin/env python3
"""Reconcile out-of-band `npx skills` installs with this repo's inventory.

The normal path is to edit scripts/skills-manifest.json and run setup
update-skills. When a skill is installed directly with `npx skills add -g`, the
CLI can write the home lockfile and materialize skills/ before this repo has a
chance to track that provenance. This command recovers entries from the current
repo lockfile and backed-up home lockfiles, then declares matching on-disk
upstream skills in the manifest.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

IGNORE_DIRS = {".system"}


@dataclass(frozen=True)
class ReconcileResult:
    lock_entries_added: list[str]
    manifest_sources_added: list[str]
    manifest_skills_added: list[str]


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] invalid JSON in {path}: {exc}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def disk_skills(skills_dir: Path) -> set[str]:
    if not skills_dir.is_dir():
        raise SystemExit(f"[ERROR] missing skills dir: {skills_dir}")
    return {
        child.name
        for child in skills_dir.iterdir()
        if child.is_dir() and not child.name.startswith(".") and child.name not in IGNORE_DIRS
    }


def git_ignored(root: Path, names: set[str]) -> set[str]:
    if not names:
        return set()
    rels = [f"skills/{name}" for name in sorted(names)]
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--", *rels],
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError):
        return set()
    if proc.returncode not in (0, 1):
        return set()
    ignored: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("skills/"):
            ignored.add(line[len("skills/") :].split("/")[0])
    return ignored


def candidate_lock_paths(root: Path, home: Path) -> list[Path]:
    repo_lock = root / ".skill-lock.json"
    agents_dir = home / ".agents"
    candidates = [repo_lock]
    home_lock = agents_dir / ".skill-lock.json"
    if home_lock.exists() and home_lock.resolve() != repo_lock.resolve():
        candidates.append(home_lock)
    candidates.extend(sorted(agents_dir.glob(".skill-lock.json.backup.*")))

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved not in seen and path.exists():
            unique.append(path)
            seen.add(resolved)
    return unique


def all_lock_entries(root: Path, home: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in candidate_lock_paths(root, home):
        lock = load_json(path)
        for name, entry in lock.get("skills", {}).items():
            if isinstance(entry, dict) and name not in entries:
                entries[name] = entry
    return entries


def manifest_source_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = manifest.setdefault("sources", [])
    return {source["repo"]: source for source in sources if isinstance(source, dict) and source.get("repo")}


def source_covers_skill(source: dict[str, Any], skill_name: str) -> bool:
    skills = source.get("skills")
    return not skills or skill_name in skills or "*" in skills


def manifest_skill_name(entry: dict[str, Any], installed_name: str) -> str:
    skill_path = entry.get("skillPath")
    if not isinstance(skill_path, str):
        return installed_name
    parent = PurePosixPath(skill_path).parent.name
    return parent if parent else installed_name


def declare_manifest_skill(manifest: dict[str, Any], repo: str, skill_name: str) -> tuple[bool, bool]:
    sources = manifest.setdefault("sources", [])
    by_repo = manifest_source_index(manifest)
    source = by_repo.get(repo)
    if source is None:
        sources.append({"repo": repo, "skills": [skill_name]})
        return True, False

    if source_covers_skill(source, skill_name):
        return False, False

    skills = source.setdefault("skills", [])
    if not isinstance(skills, list):
        raise SystemExit(f"[ERROR] manifest source has non-list skills: {repo}")
    skills.append(skill_name)
    skills.sort()
    return False, True


def reconcile(root: Path, home: Path) -> ReconcileResult:
    manifest_path = root / "scripts" / "skills-manifest.json"
    lock_path = root / ".skill-lock.json"
    skills_dir = root / "skills"

    manifest = load_json(manifest_path)
    lock = load_json(lock_path)
    lock.setdefault("version", 3)
    lock_skills = lock.setdefault("skills", {})
    if not isinstance(lock_skills, dict):
        raise SystemExit("[ERROR] lockfile has non-object skills")

    all_on_disk = disk_skills(skills_dir)
    tracked_on_disk = all_on_disk - git_ignored(root, all_on_disk)
    local_skills = set(manifest.get("local", []))
    backup_entries = all_lock_entries(root, home)

    added_lock_entries: list[str] = []
    added_sources: list[str] = []
    added_skills: list[str] = []

    for name in sorted(tracked_on_disk - local_skills):
        folder = skills_dir / name
        if not (folder / "SKILL.md").is_file():
            continue
        entry = lock_skills.get(name) or backup_entries.get(name)
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        if not source:
            continue
        if name not in lock_skills:
            lock_skills[name] = entry
            added_lock_entries.append(name)
        selector = manifest_skill_name(entry, name)
        added_source, added_skill = declare_manifest_skill(manifest, source, selector)
        if added_source:
            added_sources.append(source)
        if added_skill:
            added_skills.append(f"{source}@{selector}")

    if added_lock_entries:
        write_json(lock_path, lock)
    if added_sources or added_skills:
        write_json(manifest_path, manifest)

    return ReconcileResult(
        lock_entries_added=added_lock_entries,
        manifest_sources_added=added_sources,
        manifest_skills_added=added_skills,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile npx skills installs with manifest + lockfile")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--home-dir", required=True, type=Path)
    args = parser.parse_args()

    result = reconcile(args.repo_root, args.home_dir)
    print("Skills reconcile")
    print(f"  lock entries added:       {len(result.lock_entries_added)}")
    print(f"  manifest sources added:   {len(result.manifest_sources_added)}")
    print(f"  manifest skills appended: {len(result.manifest_skills_added)}")
    if result.lock_entries_added:
        print(f"  lock:                     {', '.join(result.lock_entries_added)}")
    if result.manifest_sources_added:
        print(f"  sources:                  {', '.join(result.manifest_sources_added)}")
    if result.manifest_skills_added:
        print(f"  skills:                   {', '.join(result.manifest_skills_added)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
