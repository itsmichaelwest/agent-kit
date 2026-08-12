#!/usr/bin/env python3
"""Plan and apply manifest updates for uninstalling one upstream skill."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


@dataclass(frozen=True)
class UninstallPlan:
    name: str
    source: str
    selector: str
    removes_source: bool
    retained: bool = False


@dataclass(frozen=True)
class UninstallResult:
    removed_selector: str | None
    removed_source: str | None


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] invalid JSON in {path}: {exc}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_plan(path: Path, plan: UninstallPlan) -> None:
    write_json(
        path,
        {
            "name": plan.name,
            "source": plan.source,
            "selector": plan.selector,
            "removes_source": plan.removes_source,
            "retained": plan.retained,
        },
    )


def read_plan(path: Path) -> UninstallPlan:
    data = load_json(path)
    name = data.get("name")
    source = data.get("source")
    selector = data.get("selector")
    removes_source = data.get("removes_source")
    retained = data.get("retained", False)
    if not all(isinstance(value, str) and value for value in (name, source, selector)):
        raise SystemExit(f"[ERROR] invalid uninstall plan: {path}")
    if not isinstance(removes_source, bool):
        raise SystemExit(f"[ERROR] invalid uninstall plan: {path}")
    if not isinstance(retained, bool):
        raise SystemExit(f"[ERROR] invalid uninstall plan: {path}")
    return UninstallPlan(
        name=name,
        source=source,
        selector=selector,
        removes_source=removes_source,
        retained=retained,
    )


def manifest_skill_name(entry: dict[str, Any], installed_name: str) -> str:
    skill_path = entry.get("skillPath")
    if not isinstance(skill_path, str):
        return installed_name
    parent = PurePosixPath(skill_path).parent.name
    return parent if parent else installed_name


def inventory(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    manifest_path = root / "scripts" / "skills-manifest.json"
    manifest = load_json(manifest_path)
    lock = load_json(root / ".skill-lock.json")
    return manifest_path, manifest, lock


def source_for(manifest: dict[str, Any], repo: str) -> dict[str, Any] | None:
    for source in manifest.get("sources", []):
        if isinstance(source, dict) and source.get("repo") == repo:
            return source
    return None


def plan_uninstall(root: Path, name: str) -> UninstallPlan:
    _, manifest, lock = inventory(root)

    local_skills = set(manifest.get("local", []))
    if name in local_skills:
        raise SystemExit(
            f"[ERROR] cannot uninstall local skill with this command: {name} "
            f"(remove the folder and manifest local entry manually)"
        )

    retained = manifest.get("retained", [])
    if isinstance(retained, list):
        for item in retained:
            if isinstance(item, dict) and item.get("name") == name:
                source = item.get("source")
                if not isinstance(source, str) or not source:
                    raise SystemExit(f"[ERROR] retained skill has no source: {name}")
                return UninstallPlan(
                    name=name,
                    source=source,
                    selector=name,
                    removes_source=False,
                    retained=True,
                )

    lock_skills = lock.get("skills", {})
    entry = lock_skills.get(name) if isinstance(lock_skills, dict) else None
    if not isinstance(entry, dict):
        raise SystemExit(f"[ERROR] lockfile skill not found: {name}")

    repo = entry.get("source")
    if not isinstance(repo, str) or not repo:
        raise SystemExit(f"[ERROR] lockfile skill has no source: {name}")

    source = source_for(manifest, repo)
    if source is None:
        raise SystemExit(f"[ERROR] lockfile source not declared in manifest: {repo}")

    skills = source.get("skills")
    if not isinstance(skills, list):
        installed_from_source = [
            installed_name
            for installed_name, installed_entry in lock_skills.items()
            if isinstance(installed_entry, dict) and installed_entry.get("source") == repo
        ]
        if installed_from_source != [name]:
            raise SystemExit(
                f"[ERROR] manifest source installs all skills and cannot remove one safely: {repo}"
            )
        return UninstallPlan(
            name=name,
            source=repo,
            selector=manifest_skill_name(entry, name),
            removes_source=True,
        )

    selector = manifest_skill_name(entry, name)
    if selector not in skills:
        raise SystemExit(f"[ERROR] manifest source does not declare skill selector: {repo}@{selector}")

    return UninstallPlan(name=name, source=repo, selector=selector, removes_source=len(skills) == 1)


def apply_manifest_removal(root: Path, plan: UninstallPlan) -> UninstallResult:
    manifest_path, manifest, lock = inventory(root)
    if plan.retained:
        retained = manifest.get("retained", [])
        if not isinstance(retained, list):
            raise SystemExit("[ERROR] manifest retained is not a list")
        remaining = [
            item for item in retained
            if not (isinstance(item, dict) and item.get("name") == plan.name)
        ]
        if len(remaining) == len(retained):
            raise SystemExit(f"[ERROR] retained skill no longer exists: {plan.name}")
        manifest["retained"] = remaining
        write_json(manifest_path, manifest)
        lock_skills = lock.get("skills", {})
        if isinstance(lock_skills, dict) and plan.name in lock_skills:
            del lock_skills[plan.name]
            write_json(root / ".skill-lock.json", lock)
        folder = root / "skills" / plan.name
        if folder.is_dir():
            shutil.rmtree(folder)
        return UninstallResult(removed_selector=plan.name, removed_source=None)

    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        raise SystemExit("[ERROR] manifest sources is not a list")

    for index, source in enumerate(sources):
        if not isinstance(source, dict) or source.get("repo") != plan.source:
            continue
        skills = source.get("skills")
        if plan.removes_source and not isinstance(skills, list):
            del sources[index]
            write_json(manifest_path, manifest)
            return UninstallResult(removed_selector=None, removed_source=plan.source)
        if not isinstance(skills, list) or plan.selector not in skills:
            raise SystemExit(f"[ERROR] manifest no longer declares skill selector: {plan.source}@{plan.selector}")
        remaining = [skill for skill in skills if skill != plan.selector]
        if remaining:
            source["skills"] = remaining
            write_json(manifest_path, manifest)
            return UninstallResult(removed_selector=plan.selector, removed_source=None)
        del sources[index]
        write_json(manifest_path, manifest)
        return UninstallResult(removed_selector=None, removed_source=plan.source)

    raise SystemExit(f"[ERROR] manifest source no longer exists: {plan.source}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or apply manifest updates for uninstalling a skill")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--write-plan", type=Path)
    parser.add_argument("--apply-plan", type=Path)
    args = parser.parse_args()

    if args.write_plan and args.apply_plan:
        parser.error("--write-plan and --apply-plan are mutually exclusive")

    if args.apply_plan:
        plan = read_plan(args.apply_plan)
        if plan.name != args.skill:
            raise SystemExit(f"[ERROR] uninstall plan skill does not match request: {plan.name}")
        result = apply_manifest_removal(args.repo_root, plan)
        if result.removed_source:
            print(f"  removed:     source {result.removed_source}")
        if result.removed_selector:
            print(f"  removed:     selector {plan.source}@{result.removed_selector}")
        return 0

    plan = plan_uninstall(args.repo_root, args.skill)
    print("Skills uninstall")
    print(f"  skill:       {plan.name}")
    print(f"  source:      {plan.source}")
    print(f"  selector:    {plan.selector}")
    manifest_action = "remove retained snapshot" if plan.retained else ("remove source" if plan.removes_source else "remove selector")
    print(f"  manifest:    {manifest_action}")

    if args.write_plan:
        write_plan(args.write_plan, plan)
        return 0

    if args.apply:
        result = apply_manifest_removal(args.repo_root, plan)
        if result.removed_source:
            print(f"  removed:     source {result.removed_source}")
        if result.removed_selector:
            print(f"  removed:     selector {plan.source}@{result.removed_selector}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
