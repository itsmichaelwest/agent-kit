from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lib" / "uninstall-skill.py"


def load_module():
    spec = importlib.util.spec_from_file_location("uninstall_skill", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load uninstall-skill.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_inventory(root: Path, manifest: dict, lock: dict) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "skills-manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    (root / ".skill-lock.json").write_text(json.dumps(lock, indent=2), encoding="utf-8")


class UninstallSkillTests(unittest.TestCase):
    def test_plans_and_applies_manifest_removal_for_last_skill_in_source(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_inventory(
                root,
                {
                    "local": [],
                    "sources": [
                        {"repo": "shadcn/improve", "skills": ["improve"]},
                        {"repo": "example/other", "skills": ["other"]},
                    ],
                },
                {
                    "version": 3,
                    "skills": {
                        "improve": {
                            "source": "shadcn/improve",
                            "skillPath": "skills/improve/SKILL.md",
                        }
                    },
                },
            )

            plan = module.plan_uninstall(root, "improve")
            self.assertEqual(plan.source, "shadcn/improve")
            self.assertEqual(plan.selector, "improve")
            self.assertTrue(plan.removes_source)

            result = module.apply_manifest_removal(root, plan)
            manifest = json.loads((root / "scripts" / "skills-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(result.removed_source, "shadcn/improve")
            self.assertIsNone(result.removed_selector)
            self.assertEqual(manifest["sources"], [{"repo": "example/other", "skills": ["other"]}])

    def test_removes_selector_but_keeps_source_when_other_skills_remain(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_inventory(
                root,
                {"local": [], "sources": [{"repo": "example/repo", "skills": ["one", "two"]}]},
                {
                    "version": 3,
                    "skills": {
                        "one-installed": {
                            "source": "example/repo",
                            "skillPath": "skills/one/SKILL.md",
                        }
                    },
                },
            )

            plan = module.plan_uninstall(root, "one-installed")
            result = module.apply_manifest_removal(root, plan)
            manifest = json.loads((root / "scripts" / "skills-manifest.json").read_text(encoding="utf-8"))

            self.assertFalse(plan.removes_source)
            self.assertEqual(result.removed_selector, "one")
            self.assertIsNone(result.removed_source)
            self.assertEqual(manifest["sources"], [{"repo": "example/repo", "skills": ["two"]}])

    def test_refuses_local_skill(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_inventory(root, {"local": ["custom"], "sources": []}, {"version": 3, "skills": {}})

            with self.assertRaisesRegex(SystemExit, "local skill"):
                module.plan_uninstall(root, "custom")

    def test_refuses_source_without_explicit_skills_list(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_inventory(
                root,
                {"local": [], "sources": [{"repo": "example/all"}]},
                {
                    "version": 3,
                    "skills": {
                        "one": {
                            "source": "example/all",
                            "skillPath": "skills/one/SKILL.md",
                        }
                    },
                },
            )

            with self.assertRaisesRegex(SystemExit, "installs all skills"):
                module.plan_uninstall(root, "one")


if __name__ == "__main__":
    unittest.main()
