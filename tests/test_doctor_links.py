from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "doctor-links.py"


def make_link(source: Path, target: Path) -> None:
    """Link target -> source, falling back to a junction on Windows.

    Ensure-Linked creates directory junctions rather than symlinks on Windows
    because file symlinks need Developer Mode or elevation. Mirror that here so
    the test exercises the same reparse points the doctor has to recognise.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(source, target, target_is_directory=source.is_dir())
        return
    except (OSError, NotImplementedError):
        pass

    if os.name == "nt" and source.is_dir():
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return

    raise unittest.SkipTest("cannot create links in this environment")


def expected_marker(manifest: dict) -> str:
    """Recompute the marker independently of the implementation under test."""
    sources = manifest["sources"]
    lines = [
        "{}|{}|{}".format(t["source"], sources.get(t["source"], ""), t["path"])
        for t in manifest["targets"]
    ]
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:8]
    return "{}+{}".format(manifest["layoutVersion"], digest)


class DoctorLinksTests(unittest.TestCase):
    def _fixture(self, temp: str) -> tuple[Path, Path, Path, dict]:
        root = Path(temp) / "repo"
        home = Path(temp) / "home"
        state = Path(temp) / "state"

        (root / "scripts").mkdir(parents=True)
        (root / "hooks").mkdir()
        (root / "hooks" / "agent_safety.py").write_text("# hook\n", encoding="utf-8")
        (root / "config" / "codex").mkdir(parents=True)
        (root / "config" / "codex" / "hooks.json").write_text("{}\n", encoding="utf-8")
        (root / "decoy").mkdir()
        home.mkdir()
        state.mkdir()

        manifest = {
            "layoutVersion": "4",
            "sources": {"hooks": "hooks", "codex_hooks": "config/codex/hooks.json"},
            "targets": [
                {"source": "hooks", "path": "~/.agents/hooks"},
                {"source": "codex_hooks", "path": "~/.codex/hooks.json"},
            ],
        }
        self._write_manifest(root, manifest)
        return root, home, state, manifest

    def _write_manifest(self, root: Path, manifest: dict) -> None:
        (root / "scripts" / "ai-agent-links.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def _write_marker(self, state: Path, value: str) -> None:
        marker = state / "agent-kit" / "ai-agent-layout-version"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(value, encoding="utf-8")

    def _link_all(self, root: Path, home: Path) -> None:
        make_link(root / "hooks", home / ".agents" / "hooks")
        make_link(root / "config" / "codex" / "hooks.json", home / ".codex" / "hooks.json")

    def _run(self, root: Path, home: Path, state: Path, strict: bool = False):
        env = dict(os.environ)
        env["LOCALAPPDATA"] = str(state)
        env["XDG_STATE_HOME"] = str(state)

        args = [sys.executable, str(SCRIPT), "--repo-root", str(root), "--home-dir", str(home)]
        if strict:
            args.append("--strict")
        return subprocess.run(args, capture_output=True, text=True, env=env)

    def test_fully_linked_layout_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, home, state, manifest = self._fixture(temp)
            self._link_all(root, home)
            self._write_marker(state, expected_marker(manifest))

            result = self._run(root, home, state, strict=True)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("2 link targets verified", result.stdout)

    def test_missing_link_is_an_error(self) -> None:
        """The outage: a manifest target that setup never created."""
        with tempfile.TemporaryDirectory() as temp:
            root, home, state, manifest = self._fixture(temp)
            make_link(root / "config" / "codex" / "hooks.json", home / ".codex" / "hooks.json")
            self._write_marker(state, expected_marker(manifest))

            result = self._run(root, home, state)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing link", result.stdout)
            self.assertIn(".agents", result.stdout)

    def test_real_directory_instead_of_link_warns(self) -> None:
        """helpers.ps1 falls back to Copy-Item; the copy then silently drifts."""
        with tempfile.TemporaryDirectory() as temp:
            root, home, state, manifest = self._fixture(temp)
            (home / ".agents" / "hooks").mkdir(parents=True)
            make_link(root / "config" / "codex" / "hooks.json", home / ".codex" / "hooks.json")
            self._write_marker(state, expected_marker(manifest))

            lenient = self._run(root, home, state)
            self.assertEqual(lenient.returncode, 0, lenient.stdout + lenient.stderr)
            self.assertIn("not a link", lenient.stdout)

            strict = self._run(root, home, state, strict=True)
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)

    def test_link_pointing_at_the_wrong_source_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, home, state, manifest = self._fixture(temp)
            make_link(root / "decoy", home / ".agents" / "hooks")
            make_link(root / "config" / "codex" / "hooks.json", home / ".codex" / "hooks.json")
            self._write_marker(state, expected_marker(manifest))

            result = self._run(root, home, state)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("expected", result.stdout)

    def test_marker_goes_stale_when_a_target_is_added(self) -> None:
        """Regression for the commit that added `hooks` without a re-link.

        Every previously declared target is still linked, so target checking
        alone reports success. Only the digest notices the manifest moved on.
        """
        with tempfile.TemporaryDirectory() as temp:
            root, home, state, manifest = self._fixture(temp)
            self._link_all(root, home)
            self._write_marker(state, expected_marker(manifest))

            self.assertEqual(self._run(root, home, state, strict=True).returncode, 0)

            (root / "prompts").mkdir()
            manifest["sources"]["prompts"] = "prompts"
            manifest["targets"].append({"source": "prompts", "path": "~/.claude/commands"})
            self._write_manifest(root, manifest)
            make_link(root / "prompts", home / ".claude" / "commands")

            result = self._run(root, home, state, strict=True)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("layout marker", result.stdout)
            self.assertIn("setup link", result.stdout)


if __name__ == "__main__":
    unittest.main()
