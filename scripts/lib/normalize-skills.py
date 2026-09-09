#!/usr/bin/env python3
"""Apply narrowly-defined, repeatable normalizations to upstream skill packages.

Vendored content normally remains byte-for-byte upstream. The SwiftUI Pro package
is the exception: it ships its current root skill and an older nested Claude
plugin wrapper with the same skill name. All supported agents recursively
discover both entrypoints, so retain the root skill and remove only the stale
duplicate after each managed update.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def frontmatter_value(path: Path, key: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]+)", text)
    return match.group(1).strip() if match else None


def normalize_swiftui_pro(skills_dir: Path) -> bool:
    root = skills_dir / "swiftui-pro"
    outer = root / "SKILL.md"
    duplicate = root / "skills" / "swiftui-pro"
    inner = duplicate / "SKILL.md"
    if not inner.exists():
        return False
    if not outer.is_file():
        raise RuntimeError(f"missing canonical SwiftUI Pro entrypoint: {outer}")
    if frontmatter_value(outer, "name") != "swiftui-pro" or frontmatter_value(inner, "name") != "swiftui-pro":
        raise RuntimeError("refusing to remove a nested entrypoint with an unexpected skill name")
    outer_version = frontmatter_value(outer, "version")
    inner_version = frontmatter_value(inner, "version")
    if outer_version != "1.1" or inner_version != "1.0":
        raise RuntimeError(
            "SwiftUI Pro upstream packaging changed; refusing to remove the nested entrypoint "
            f"(root={outer_version!r}, nested={inner_version!r})"
        )
    shutil.rmtree(duplicate)
    print(f"[NORMALIZED] removed stale nested SwiftUI Pro wrapper: {duplicate}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize known duplicate upstream skill entrypoints.")
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    normalize_swiftui_pro(args.repo_root / "skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
