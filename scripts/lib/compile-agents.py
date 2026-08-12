#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

TOP_LEVEL_FIELDS = {"name", "description", "model_class", "extends", "claude", "codex"}
CLAUDE_FIELDS = {
    "background",
    "color",
    "disallowedTools",
    "effort",
    "initialPrompt",
    "isolation",
    "maxTurns",
    "mcpServers",
    "memory",
    "permissionMode",
    "skills",
    "tools",
}
CODEX_FIELDS = {
    "description",
    "model_reasoning_effort",
    "personality",
    "sandbox_mode",
    "web_search",
}
CODEX_EFFORTS = {"low", "medium", "high", "xhigh"}
CODEX_SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
CLAUDE_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
CLAUDE_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CLAUDE_ISOLATION_MODES = {"worktree"}
CLAUDE_MEMORY_SCOPES = {"user", "project", "local"}
CLAUDE_PERMISSION_MODES = {
    "default",
    "acceptEdits",
    "auto",
    "dontAsk",
    "bypassPermissions",
    "plan",
}


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
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


def merge_dicts(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    merged = dict(parent)
    for key, value in child.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_template(
    name: str,
    raw_templates: dict[str, tuple[dict[str, Any], str, Path]],
    resolved: dict[str, tuple[dict[str, Any], str, Path]],
    visiting: list[str],
) -> tuple[dict[str, Any], str, Path]:
    if name in resolved:
        return resolved[name]
    if name in visiting:
        chain = " -> ".join([*visiting, name])
        raise ValueError(f"Inheritance cycle: {chain}")

    template, body, path = raw_templates[name]
    parent_name = template.get("extends")
    if parent_name is None:
        result = (dict(template), body, path)
    else:
        if not isinstance(parent_name, str) or not parent_name:
            raise ValueError(f"Invalid extends value in {path}")
        if parent_name not in raw_templates:
            raise ValueError(f"Unknown parent agent {parent_name!r} in {path}")
        parent, parent_body, _ = resolve_template(
            parent_name, raw_templates, resolved, [*visiting, name]
        )
        merged = merge_dicts(parent, template)
        merged.pop("extends", None)
        result = (merged, body if body.strip() else parent_body, path)

    resolved[name] = result
    return result


def validate_template(template: dict[str, Any], body: str, path: Path) -> None:
    unknown = sorted(set(template) - TOP_LEVEL_FIELDS)
    if unknown:
        raise ValueError(f"Unsupported template field(s) in {path}: {', '.join(unknown)}")

    for field in ("name", "description", "model_class"):
        if not isinstance(template.get(field), str) or not template[field].strip():
            raise ValueError(f"Missing or invalid {field} in {path}")
    if not NAME_RE.fullmatch(template["name"]):
        raise ValueError(f"Invalid agent name {template['name']!r} in {path}")
    if path.stem != template["name"]:
        raise ValueError(
            f"Agent name {template['name']!r} does not match filename {path.name!r}"
        )
    if not body.strip():
        raise ValueError(f"Missing agent instructions in {path}")

    for provider, allowed in (("claude", CLAUDE_FIELDS), ("codex", CODEX_FIELDS)):
        fields = template.get(provider, {})
        if not isinstance(fields, dict):
            raise ValueError(f"{provider} must be a mapping in {path}")
        unsupported = sorted(set(fields) - allowed)
        if unsupported:
            raise ValueError(
                f"Unsupported {provider} field(s) in {path}: {', '.join(unsupported)}"
            )

    claude = template.get("claude", {})
    string_fields = {
        "color",
        "effort",
        "initialPrompt",
        "isolation",
        "memory",
        "permissionMode",
    }
    list_fields = {"disallowedTools", "mcpServers", "skills", "tools"}
    for field in string_fields:
        if field in claude and not isinstance(claude[field], str):
            raise ValueError(f"Claude field {field} must be a string in {path}")
    for field in list_fields:
        if field in claude and (
            not isinstance(claude[field], list)
            or not all(isinstance(item, str) for item in claude[field])
        ):
            raise ValueError(f"Claude field {field} must be a string list in {path}")
    if "background" in claude and not isinstance(claude["background"], bool):
        raise ValueError(f"Claude field background must be a boolean in {path}")
    if "maxTurns" in claude and (
        not isinstance(claude["maxTurns"], int) or claude["maxTurns"] <= 0
    ):
        raise ValueError(f"Claude field maxTurns must be a positive integer in {path}")
    enum_fields = {
        "color": CLAUDE_COLORS,
        "effort": CLAUDE_EFFORTS,
        "isolation": CLAUDE_ISOLATION_MODES,
        "memory": CLAUDE_MEMORY_SCOPES,
        "permissionMode": CLAUDE_PERMISSION_MODES,
    }
    for field, allowed_values in enum_fields.items():
        if field in claude and claude[field] not in allowed_values:
            raise ValueError(f"Unsupported Claude {field} {claude[field]!r} in {path}")

    codex = template.get("codex", {})
    effort = codex.get("model_reasoning_effort")
    if effort is not None and effort not in CODEX_EFFORTS:
        raise ValueError(f"Unsupported Codex reasoning effort {effort!r} in {path}")
    sandbox = codex.get("sandbox_mode")
    if sandbox is not None and sandbox not in CODEX_SANDBOX_MODES:
        raise ValueError(f"Unsupported Codex sandbox mode {sandbox!r} in {path}")


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
        lines.append(f"{key}: {yaml_quote(value)}")
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
            "developer_instructions = '''",
            body.rstrip(),
            "'''",
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

    raw_templates: dict[str, tuple[dict[str, Any], str, Path]] = {}
    for template_path in sorted(templates_dir.glob("*.md")):
        template, body = load_template(template_path)
        name = str(template.get("name", ""))
        if not name:
            raise ValueError(f"Missing agent name in {template_path}")
        if name in raw_templates:
            raise ValueError(f"Duplicate agent name {name!r}")
        raw_templates[name] = (template, body, template_path)

    generated_names: set[str] = set()
    resolved: dict[str, tuple[dict[str, Any], str, Path]] = {}
    for name in sorted(raw_templates):
        template, body, template_path = resolve_template(
            name, raw_templates, resolved, []
        )
        validate_template(template, body, template_path)
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
            agent_path.unlink()
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
