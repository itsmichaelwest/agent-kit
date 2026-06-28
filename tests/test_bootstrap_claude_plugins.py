from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "bootstrap-claude-plugins.sh"


def bash_path(path: Path) -> str:
    resolved = path.resolve()
    if os.name != "nt":
        return str(resolved)

    drive = resolved.drive.rstrip(":").lower()
    rest = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{rest}"


class BootstrapClaudePluginsTests(unittest.TestCase):
    def test_installs_then_updates_enabled_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            settings = json.dumps(
                {
                    "enabledPlugins": {
                        "alpha@example-market": True,
                        "disabled@example-market": False,
                        "beta@example-market": True,
                    },
                    "extraKnownMarketplaces": {
                        "example-market": {
                            "source": {
                                "source": "github",
                                "repo": "example/market",
                            }
                        }
                    },
                }
            )
            runner = root / "runner.sh"
            runner.write_text(
                textwrap.dedent(
                    f"""\
                    #!/usr/bin/env bash
                    set -euo pipefail

                    tmp=$(mktemp -d)
                    mkdir -p "$tmp/home/.claude" "$tmp/bin"
                    cat > "$tmp/home/.claude/settings.json" <<'JSON'
                    {settings}
                    JSON

                    cat > "$tmp/bin/claude" <<'EOF'
                    #!/usr/bin/env bash
                    echo "$*" >> "$AK_CALLS"

                    if [[ "$*" == "plugin marketplace add example/market" ]]; then
                      echo "Marketplace added"
                      exit 0
                    fi

                    if [[ "$*" == "plugin marketplace update" ]]; then
                      echo "Marketplaces updated"
                      exit 0
                    fi

                    if [[ "$1 $2" == "plugin install" ]]; then
                      echo "Plugin already installed"
                      exit 0
                    fi

                    if [[ "$1 $2" == "plugin update" ]]; then
                      echo "Plugin updated"
                      exit 0
                    fi

                    echo "unexpected args: $*" >&2
                    exit 1
                    EOF

                    chmod +x "$tmp/bin/claude"
                    AK_CALLS="$tmp/calls.log" HOME="$tmp/home" PATH="$tmp/bin:/usr/bin:/bin" "{bash_path(SCRIPT)}"
                    cat "$tmp/calls.log"
                    """
                ),
                encoding="utf-8",
                newline="\n",
            )
            runner.chmod(0o755)

            result = subprocess.run(
                ["bash", bash_path(runner)],
                env=os.environ,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = [
                line
                for line in result.stdout.splitlines()
                if line.startswith("plugin ")
            ]
            self.assertEqual(
                calls,
                [
                    "plugin marketplace add example/market",
                    "plugin marketplace update",
                    "plugin install alpha@example-market",
                    "plugin install beta@example-market",
                    "plugin update alpha@example-market",
                    "plugin update beta@example-market",
                ],
            )


if __name__ == "__main__":
    unittest.main()
