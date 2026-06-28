#!/usr/bin/env python3
"""Merge Codex config layers into a single config.toml.

Inputs:
  shared:  declarative committed config (.codex/config.toml in repo)
  overlay: gitignored personal overrides (.codex/config.local.toml) — optional
  live:    existing ~/.codex/config.toml — used to preserve [projects.*]
           runtime trust entries Codex wrote during normal use

Output (stdout): merged TOML.

Merge order (later wins for scalars; tables deep-merged):
  shared -> overlay -> live's [projects.*] only

Why preserve live [projects.*]: Codex writes trust_level entries directly into
config.toml when users trust a project at runtime. Without preservation, every
`setup.sh link` would clobber those decisions and force re-trusting.
"""

import sys
import tomllib
from pathlib import Path


def deep_merge(base, overlay):
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def emit_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        escaped = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(emit_value(x) for x in v) + "]"
    raise TypeError(f"unsupported value type: {type(v).__name__}")


def emit_key(k):
    bare = k.replace("_", "").replace("-", "")
    if bare and bare.isalnum() and not bare[0].isdigit():
        return k
    return '"' + k.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit_table(name, table, lines):
    scalars = {k: v for k, v in table.items() if not isinstance(v, dict)}
    subtables = {k: v for k, v in table.items() if isinstance(v, dict)}

    if name:
        lines.append(f"[{name}]")
    for k, v in scalars.items():
        lines.append(f"{emit_key(k)} = {emit_value(v)}")
    if name:
        lines.append("")
    for k, sub in subtables.items():
        sub_name = f"{name}.{emit_key(k)}" if name else emit_key(k)
        emit_table(sub_name, sub, lines)


def load(path_str):
    if not path_str:
        return {}
    p = Path(path_str)
    if not p.exists():
        return {}
    return tomllib.loads(p.read_text())


def main():
    if len(sys.argv) < 3:
        print("usage: merge-codex-config.py <shared> <overlay> [<live>]", file=sys.stderr)
        sys.exit(2)

    shared = load(sys.argv[1])
    overlay = load(sys.argv[2])
    live = load(sys.argv[3]) if len(sys.argv) > 3 else {}

    merged = deep_merge(shared, overlay)

    if "projects" in live:
        merged.setdefault("projects", {})
        for path, trust in live["projects"].items():
            merged["projects"].setdefault(path, trust)

    scalars = {k: v for k, v in merged.items() if not isinstance(v, dict)}
    tables = {k: v for k, v in merged.items() if isinstance(v, dict)}

    lines = []
    for k, v in scalars.items():
        lines.append(f"{emit_key(k)} = {emit_value(v)}")
    if scalars:
        lines.append("")
    for k, sub in tables.items():
        emit_table(emit_key(k), sub, lines)

    while lines and lines[-1] == "":
        lines.pop()
    lines.append("")
    sys.stdout.write("\n".join(lines))


if __name__ == "__main__":
    main()
