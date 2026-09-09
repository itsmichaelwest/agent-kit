from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("normalize_skills", ROOT / "scripts" / "lib" / "normalize-skills.py")
assert SPEC and SPEC.loader
NORMALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NORMALIZE)


class NormalizeSkillsTests(unittest.TestCase):
    def write_skill(self, path: Path, version: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'---\nname: swiftui-pro\nmetadata:\n  version: "{version}"\n---\n', encoding="utf-8")

    def test_removes_only_the_known_stale_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp) / "skills"
            self.write_skill(skills / "swiftui-pro" / "SKILL.md", "1.1")
            self.write_skill(skills / "swiftui-pro" / "skills" / "swiftui-pro" / "SKILL.md", "1.0")

            self.assertTrue(NORMALIZE.normalize_swiftui_pro(skills))
            self.assertTrue((skills / "swiftui-pro" / "SKILL.md").is_file())
            self.assertFalse((skills / "swiftui-pro" / "skills" / "swiftui-pro").exists())

    def test_refuses_changed_upstream_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp) / "skills"
            self.write_skill(skills / "swiftui-pro" / "SKILL.md", "1.2")
            nested = skills / "swiftui-pro" / "skills" / "swiftui-pro" / "SKILL.md"
            self.write_skill(nested, "1.0")

            with self.assertRaisesRegex(RuntimeError, "packaging changed"):
                NORMALIZE.normalize_swiftui_pro(skills)
            self.assertTrue(nested.is_file())
