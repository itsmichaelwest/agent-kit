from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lib" / "reconcile-skills.py"


def load_module():
    spec = importlib.util.spec_from_file_location("reconcile_skills", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reconcile-skills.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReconcileSkillsTests(unittest.TestCase):
    def test_removes_empty_non_skill_folders_but_preserves_nonempty_folders(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            home = Path(temp) / "home"
            skills = root / "skills"
            (root / "scripts").mkdir(parents=True)
            (skills / "empty-leftover").mkdir(parents=True)
            (skills / "nested-leftover" / "references").mkdir(parents=True)
            (skills / "valid-skill").mkdir()
            (skills / "valid-skill" / "SKILL.md").write_text("---\nname: valid-skill\n---\n", encoding="utf-8")
            (skills / "valid-skill" / "references").mkdir()
            (skills / "nonempty-unknown").mkdir()
            (skills / "nonempty-unknown" / "README.md").write_text("keep me\n", encoding="utf-8")
            (skills / ".system").mkdir()
            home.joinpath(".agents").mkdir(parents=True)

            root.joinpath("scripts", "skills-manifest.json").write_text(
                json.dumps({"agents": ["codex"], "local": ["valid-skill"], "sources": []}, indent=2),
                encoding="utf-8",
            )
            root.joinpath(".skill-lock.json").write_text(json.dumps({"version": 3, "skills": {}}, indent=2), encoding="utf-8")

            result = module.reconcile(root, home)

            self.assertEqual(
                result.empty_folders_removed,
                ["empty-leftover", "nested-leftover", "nested-leftover/references"],
            )
            self.assertFalse((skills / "empty-leftover").exists())
            self.assertFalse((skills / "nested-leftover").exists())
            self.assertTrue((skills / "valid-skill").is_dir())
            self.assertTrue((skills / "valid-skill" / "references").is_dir())
            self.assertTrue((skills / "nonempty-unknown").is_dir())
            self.assertTrue((skills / ".system").is_dir())

    def test_merges_recoverable_backup_lock_entries_and_updates_manifest(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            home = Path(temp) / "home"
            (root / "scripts").mkdir(parents=True)
            (root / "skills" / "existing").mkdir(parents=True)
            (root / "skills" / "improve").mkdir(parents=True)
            (root / "skills" / "find-skills").mkdir(parents=True)
            (root / "skills" / "existing" / "SKILL.md").write_text("---\nname: existing\n---\n", encoding="utf-8")
            (root / "skills" / "improve" / "SKILL.md").write_text("---\nname: improve\n---\n", encoding="utf-8")
            (root / "skills" / "find-skills" / "SKILL.md").write_text("---\nname: find-skills\n---\n", encoding="utf-8")

            manifest_path = root / "scripts" / "skills-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "agents": ["codex"],
                        "local": [],
                        "sources": [{"repo": "example/existing", "skills": ["existing"]}],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            repo_lock_path = root / ".skill-lock.json"
            repo_lock_path.write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            "existing": {
                                "source": "example/existing",
                                "sourceType": "github",
                                "sourceUrl": "https://github.com/example/existing.git",
                                "skillPath": "skills/existing/SKILL.md",
                            }
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            backup_dir = home / ".agents"
            backup_dir.mkdir(parents=True)
            (backup_dir / ".skill-lock.json.backup.20260628_124544").write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            "improve": {
                                "source": "shadcn/improve",
                                "sourceType": "github",
                                "sourceUrl": "https://github.com/shadcn/improve.git",
                                "skillPath": "skills/improve/SKILL.md",
                            },
                            "find-skills": {
                                "source": "vercel-labs/skills",
                                "sourceType": "github",
                                "sourceUrl": "https://github.com/vercel-labs/skills.git",
                                "skillPath": "skills/find-skills/SKILL.md",
                            },
                            "missing": {
                                "source": "example/missing",
                                "sourceType": "github",
                                "sourceUrl": "https://github.com/example/missing.git",
                                "skillPath": "skills/missing/SKILL.md",
                            },
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = module.reconcile(root, home)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            lock = json.loads(repo_lock_path.read_text(encoding="utf-8"))

            self.assertEqual(result.lock_entries_added, ["find-skills", "improve"])
            self.assertEqual(result.manifest_sources_added, ["vercel-labs/skills", "shadcn/improve"])
            self.assertIn("improve", lock["skills"])
            self.assertIn("find-skills", lock["skills"])
            self.assertNotIn("missing", lock["skills"])
            self.assertIn({"repo": "shadcn/improve", "skills": ["improve"]}, manifest["sources"])
            self.assertIn({"repo": "vercel-labs/skills", "skills": ["find-skills"]}, manifest["sources"])

    def test_existing_source_uses_upstream_skill_path_not_installed_folder_name(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            home = Path(temp) / "home"
            (root / "scripts").mkdir(parents=True)
            (root / "skills" / "vercel-react-best-practices").mkdir(parents=True)
            (root / "skills" / "vercel-react-best-practices" / "SKILL.md").write_text(
                "---\nname: react-best-practices\n---\n",
                encoding="utf-8",
            )
            (home / ".agents").mkdir(parents=True)

            manifest_path = root / "scripts" / "skills-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "agents": ["codex"],
                        "local": [],
                        "sources": [
                            {
                                "repo": "vercel-labs/agent-skills",
                                "skills": ["react-best-practices"],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (root / ".skill-lock.json").write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            "vercel-react-best-practices": {
                                "source": "vercel-labs/agent-skills",
                                "sourceType": "github",
                                "sourceUrl": "https://github.com/vercel-labs/agent-skills.git",
                                "skillPath": "skills/react-best-practices/SKILL.md",
                            }
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = module.reconcile(root, home)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(result.manifest_skills_added, [])
            self.assertEqual(manifest["sources"][0]["skills"], ["react-best-practices"])

    def test_migrates_a_selector_when_its_installed_skill_changes_source(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            home = Path(temp) / "home"
            (root / "scripts").mkdir(parents=True)
            skill_dir = root / "skills" / "emil-design-eng"
            skill_dir.mkdir(parents=True)
            skill_dir.joinpath("SKILL.md").write_text(
                "---\nname: emil-design-eng\n---\n",
                encoding="utf-8",
            )
            (home / ".agents").mkdir(parents=True)

            manifest_path = root / "scripts" / "skills-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "agents": ["codex"],
                        "local": [],
                        "sources": [
                            {
                                "repo": "emilkowalski/skill",
                                "skills": ["emil-design-eng"],
                            },
                            {
                                "repo": "emilkowalski/skills",
                                "skills": ["animation-vocabulary", "emil-design-eng"],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (root / ".skill-lock.json").write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            "emil-design-eng": {
                                "source": "emilkowalski/skills",
                                "skillPath": "skills/emil-design-eng/SKILL.md",
                            }
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = module.reconcile(root, home)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(result.manifest_sources_added, [])
            self.assertEqual(
                manifest["sources"],
                [
                    {
                        "repo": "emilkowalski/skills",
                        "skills": ["animation-vocabulary", "emil-design-eng"],
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
