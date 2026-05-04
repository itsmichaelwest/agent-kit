#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"')
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("\\'", "'")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    return value


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, root)]

    for raw_line in frontmatter.splitlines():
        if not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid frontmatter line: {raw_line!r}")

        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]

        key = key.strip()
        value = value.strip()
        if not value:
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent + 2, child))
        else:
            current[key] = parse_scalar(value)

    return root


def load_template(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing frontmatter in {path}")
    frontmatter = parse_frontmatter(match.group(1))
    body = text[match.end() :].lstrip("\n")
    return frontmatter, body.rstrip() + "\n"


def yaml_quote(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(yaml_quote(item) for item in value) + "]"
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def toml_quote(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(toml_quote(item) for item in value) + "]"
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def render_markdown(template: dict[str, Any], body: str, model: str) -> str:
    claude = template.get("claude", {})
    lines = [
        "---",
        f'name: {template["name"]}',
        f'description: {template["description"]}',
        f"model: {model}",
    ]
    for key, value in claude.items():
        lines.append(f"{key}: {value}")
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def render_codex(template: dict[str, Any], body: str, model: str) -> str:
    codex = template.get("codex", {})
    description = codex.get("description", template["description"])

    lines = [
        f'name = {toml_quote(template["name"])}',
        f"description = {toml_quote(description)}",
        "",
        f"model = {toml_quote(model)}",
    ]

    ordered_optional_keys = [
        "model_reasoning_effort",
        "web_search",
        "personality",
        "sandbox_mode",
    ]
    for key in ordered_optional_keys:
        if key in codex:
            lines.append(f"{key} = {toml_quote(codex[key])}")

    lines.extend(
        [
            "",
            'developer_instructions = """',
            body.rstrip(),
            '"""',
            "",
        ]
    )
    return "\n".join(lines)


def resolve_model(config: dict[str, Any], provider: str, model_class: str) -> str:
    providers = config.get("providers", {})
    provider_config = providers.get(provider, {})
    model = provider_config.get(model_class)
    if not model:
        raise KeyError(f"Missing model mapping for {provider}.{model_class}")
    return str(model)


def compile_templates(repo_root: Path) -> int:
    config_path = repo_root / "agent-templates" / "config.toml"
    templates_dir = repo_root / "agent-templates"
    markdown_dir = repo_root / "agents"
    codex_dir = repo_root / ".codex" / "agents"

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config: {config_path}")
    if not templates_dir.exists():
        raise FileNotFoundError(f"Missing templates dir: {templates_dir}")

    config = tomllib.loads(config_path.read_text())
    markdown_dir.mkdir(parents=True, exist_ok=True)
    codex_dir.mkdir(parents=True, exist_ok=True)

    generated_names: set[str] = set()

    for template_path in sorted(templates_dir.glob("*.md")):
        template, body = load_template(template_path)
        name = str(template["name"])
        model_class = str(template["model_class"])
        generated_names.add(name)

        markdown_model = resolve_model(config, "claude", model_class)
        codex_model = resolve_model(config, "codex", model_class)

        (markdown_dir / f"{name}.md").write_text(
            render_markdown(template, body, markdown_model)
        )
        (codex_dir / f"{name}.toml").write_text(render_codex(template, body, codex_model))

    for agent_path in markdown_dir.glob("*.md"):
        if agent_path.name.endswith(".agent.md"):
            continue
        if agent_path.stem not in generated_names:
            agent_path.unlink()
    for agent_path in codex_dir.glob("*.toml"):
        if agent_path.stem not in generated_names:
            agent_path.unlink()

    print(f"Compiled {len(generated_names)} agent templates")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    return compile_templates(Path(args.repo_root).expanduser().resolve())


if __name__ == "__main__":
    sys.exit(main())
