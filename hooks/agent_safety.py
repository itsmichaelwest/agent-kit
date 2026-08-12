#!/usr/bin/env python3
"""Deterministic global safety hooks shared by Claude Code and Codex.

The hook is deliberately narrow. It denies high-confidence destructive shell
commands before execution and prevents likely secrets from reaching the model.
It emits no output for normal operations.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from typing import Any


SECRET_PATTERNS = (
    re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----.*?"
        r"-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(r"\b(?:sk-(?:proj-|ant-[A-Za-z0-9_-]*-)?)[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bgh[opusr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?(?:key|token)|access[_-]?token|auth[_-]?token|client[_-]?secret|"
        r"password|passwd|private[_-]?key|secret|token)\b\s*[:=]\s*"
        r"(?P<quote>['\"]?)(?!example\b|dummy\b|redacted\b|placeholder\b|\$\{)"
        r"[A-Za-z0-9_./+=:@-]{12,}(?P=quote)"
    ),
)

SENSITIVE_NAME = re.compile(
    r"(?i)(?:TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY|CREDENTIAL|AUTH)"
)


def redact_string(value: str) -> tuple[str, bool]:
    changed = False
    for pattern in SECRET_PATTERNS:
        value, count = pattern.subn("[REDACTED_SECRET]", value)
        changed |= count > 0
    return value, changed


def redact_value(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, list):
        output = []
        changed = False
        for item in value:
            redacted, item_changed = redact_value(item)
            output.append(redacted)
            changed |= item_changed
        return output, changed
    if isinstance(value, dict):
        output = {}
        changed = False
        for key, item in value.items():
            redacted, item_changed = redact_value(item)
            output[key] = redacted
            changed |= item_changed
        return output, changed
    return value, False


def command_value(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "cmd", "script"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def destructive_reason(command: str, cwd: str) -> str | None:
    normalized = re.sub(r"\s+", " ", command.strip())
    lower = normalized.lower()

    if re.search(r"(?:^|[;&|]\s*)git\s+reset\s+--hard(?:\s|$)", lower):
        return "git reset --hard"
    if re.search(
        r"(?:^|[;&|]\s*)git\s+clean\b[^;&|\n]*"
        r"(?:--dry-run\b|\s-(?=[a-z]*n)[a-z]+)",
        lower,
    ):
        pass
    elif re.search(
        r"(?:^|[;&|]\s*)git\s+clean\b[^;&|\n]*"
        r"(?:\s-(?=[a-z]*f)(?=[a-z]*d)[a-z]+|\s-f\b[^;&|\n]*\s-d\b|\s-d\b[^;&|\n]*\s-f\b)",
        lower,
    ):
        return "forced recursive git clean"
    if re.search(
        r"(?:^|[;&|]\s*)git\s+branch\s+(?:-[^ ]*)?D(?:\s|$)|"
        r"(?:^|[;&|]\s*)git\s+branch\b[^;&|\n]*--delete\b[^;&|\n]*--force\b",
        normalized,
    ):
        return "forced branch deletion"
    if re.search(r"(?:^|[;&|]\s*)git\s+push\b[^;&|\n]*(?:--force(?:\s|$)|\s-f(?:\s|$))", lower) and "--force-with-lease" not in lower:
        return "force push without lease"
    if re.search(r"(?:^|[;&|]\s*)git\s+(?:checkout\s+--|restore(?:\s+--[^ ]+)*?)\s+(?:\.|\*|/|~|\$HOME)(?:\s|$)", normalized, re.IGNORECASE):
        return "broad destructive Git restore"
    if re.search(
        r"(?:^|[;&|]\s*)(?:mkfs(?:\.[a-z0-9]+)?|diskutil\s+erase|format\s+[a-z]:|"
        r"format-volume|clear-disk|remove-partition)(?:\s|$)",
        lower,
    ):
        return "filesystem formatting command"
    if re.search(r"(?:^|[;&|]\s*)dd\b[^;&|\n]*\bof=(?:/dev/|\\\\\.\\)", lower):
        return "raw disk write"

    rm_match = re.search(
        r"(?:^|[;&|]\s*)rm\s+(?=[^;&|\n]*(?:-[a-z]*r[a-z]*|--recursive))"
        r"(?=[^;&|\n]*(?:-[a-z]*f[a-z]*|--force))(?P<args>[^;&|\n]+)",
        normalized,
        re.IGNORECASE,
    )
    if rm_match:
        args = rm_match.group("args")
        targets = [
            token.strip("'\"")
            for token in re.findall(r"(?:'[^']*'|\"[^\"]*\"|\S+)", args)
            if not token.startswith("-")
        ]
        home = os.path.realpath(os.path.expanduser("~"))
        resolved_cwd = os.path.realpath(cwd or os.getcwd())
        for target in targets:
            expanded = os.path.expandvars(os.path.expanduser(target))
            if "$" in target or not target:
                return "recursive deletion with an unresolved target"
            if target in {"/", "~", ".", "..", "*", "./*", "$HOME", "${HOME}"}:
                return "recursive deletion of a broad path"
            resolved = os.path.realpath(os.path.join(resolved_cwd, expanded))
            if resolved in {"/", home, resolved_cwd}:
                return "recursive deletion of a protected root"

    remove_item = re.search(r"(?i)(?:^|[;&|]\s*)remove-item\b(?P<args>[^;&|\n]+)", normalized)
    if remove_item:
        args = remove_item.group("args")
        if re.search(r"(?i)(?:^|\s)-(?:recurse|r)\b", args) and re.search(
            r"(?i)(?:^|\s)-(?:force|fo)\b", args
        ):
            try:
                tokens = shlex.split(args, posix=False)
            except ValueError:
                tokens = []
            targets = [token.strip("'\"") for token in tokens if not token.startswith("-")]
            for target in targets:
                if "$" in target or re.fullmatch(r"(?i)(?:[a-z]:[\\/]?|[\\/]+|\.|\.\.|\*)", target):
                    return "recursive deletion of a broad or unresolved PowerShell path"
    return None


def secret_command_reason(command: str) -> str | None:
    _, contains_literal_secret = redact_string(command)
    if contains_literal_secret:
        return "shell command contains a likely literal secret"
    if re.search(r"(?i)(?:^|[;&|]\s*)(?:env|printenv|set|export\s+-p)\s*(?:[;&|]|$)", command):
        return "bulk environment output can expose credentials"
    if re.search(r"(?i)(?:echo|printf|write-output|write-host)[^;&|\n]*[$%]\{?[^\s}\"']+", command):
        variables = re.findall(r"[$%]\{?([A-Za-z_][A-Za-z0-9_]*)", command)
        if any(SENSITIVE_NAME.search(variable) for variable in variables):
            return "printing a sensitive environment variable"
    readers = {"cat", "type", "more", "less", "head", "tail", "get-content"}
    credential_name = re.compile(
        r"(?i)^(?:\.env(?:\..+)?|\.npmrc|\.pypirc|\.netrc|credentials|"
        r"id_(?:rsa|dsa|ecdsa|ed25519)|.+\.(?:pem|key))$"
    )
    for segment in re.split(r"[;&|]", command):
        try:
            tokens = shlex.split(segment.replace("\\", "/"), posix=True)
        except ValueError:
            continue
        if not tokens or os.path.basename(tokens[0]).lower() not in readers:
            continue
        for token in tokens[1:]:
            if not token.startswith("-") and credential_name.match(os.path.basename(token)):
                return "reading a likely credential file into tool output"
    return None


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked by global safety hook: {reason}.",
                }
            }
        )
    )


def handle_pre_tool(payload: dict[str, Any]) -> None:
    command = command_value(payload)
    if not command:
        return
    reason = destructive_reason(command, str(payload.get("cwd") or os.getcwd()))
    if reason is None:
        reason = secret_command_reason(command)
    if reason is not None:
        deny(reason)


def handle_post_tool(payload: dict[str, Any]) -> None:
    response = payload.get("tool_response")
    redacted, changed = redact_value(response)
    if not changed:
        return
    if "model" in payload:  # Codex does not yet support updatedToolOutput.
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Tool output withheld because it contained a likely secret.",
                }
            )
        )
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "updatedToolOutput": redacted,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    event = payload.get("hook_event_name")
    if event == "PreToolUse":
        handle_pre_tool(payload)
    elif event == "PostToolUse":
        handle_post_tool(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
