from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "doctor-skills.py"


class DoctorSkillsTests(unittest.TestCase):
    def test_retained_skill_is_declared_without_active_upstream_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            skill = root / "skills" / "audit-only"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: audit-only\n---\n", encoding="utf-8")
            (root / "scripts" / "skills-manifest.json").write_text(
                json.dumps(
                    {
                        "local": [],
                        "retained": [
                            {"name": "audit-only", "source": "retired/example"}
                        ],
                        "sources": [],
                    }
                ),
                encoding="utf-8",
            )
            (root / ".skill-lock.json").write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            "audit-only": {
                                "source": "retired/example",
                                "skillPath": "skills/audit-only/SKILL.md",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo-root", str(root), "--strict"],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("retained audit snapshots:   1", result.stdout)
            self.assertNotIn("lockfile source not declared", result.stdout)


if __name__ == "__main__":
    unittest.main()
