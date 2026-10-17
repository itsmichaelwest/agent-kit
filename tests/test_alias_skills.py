from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('alias_skills', ROOT / 'scripts/lib/alias-skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AliasedInstallTests(unittest.TestCase):
    def test_refresh_preserves_collision_and_restores_upstream_provenance(self):
        # Exercise the installer boundary twice: a stale alias must refresh while
        # another publisher's same-named skill and provenance remain untouched.
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            upstream = base / 'upstream'
            upstream.mkdir()
            subprocess.run(['git', 'init', '-q', str(upstream)], check=True)
            for name in ('prototype', 'polish'):
                folder = upstream / 'skills' / name
                folder.mkdir(parents=True)
                (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Example\n---\nNew upstream content\n')
            subprocess.run(['git', '-C', str(upstream), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(upstream), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
            root = base / 'kit'
            (root / 'scripts').mkdir(parents=True)
            (root / 'skills/prototype').mkdir(parents=True)
            (root / 'skills/prototype/SKILL.md').write_text('Matt content')
            (root / 'scripts/skills-manifest.json').write_text(json.dumps({'sources': [{'repo': 'example/skills', 'aliases': {'prototype': 'emil-prototype'}}]}))
            matt = {'source': 'matt/skills', 'skillPath': 'prototype/SKILL.md'}
            (root / '.skill-lock.json').write_text(json.dumps({'version': 3, 'skills': {'prototype': matt}}))
            real_run = subprocess.run
            cli_status = 0

            def run(command, **kwargs):
                if command[:2] == ['git', 'clone']:
                    command = [*command[:-2], str(upstream), command[-1]]
                    return real_run(command, **kwargs)
                if Path(command[0]).stem in ('npx', 'npx.cmd'):
                    self.assertEqual(['-g', '-y', '-s', 'polish', 'emil-prototype', '-a', 'prototype'], command[5:])
                    checkout = Path(command[4])
                    lock = json.loads((root / '.skill-lock.json').read_text())
                    for skill in checkout.glob('skills/*/SKILL.md'):
                        name = next(line.split(': ', 1)[1] for line in skill.read_text().splitlines() if line.startswith('name: '))
                        folder = root / 'skills' / name
                        folder.mkdir(exist_ok=True)
                        (folder / 'SKILL.md').write_text(skill.read_text())
                        lock['skills'][name] = {'source': str(checkout), 'sourceUrl': str(checkout), 'sourceType': 'local'}
                    (root / '.skill-lock.json').write_text(json.dumps(lock))
                    return subprocess.CompletedProcess(command, cli_status)
                return real_run(command, **kwargs)

            with patch.object(module.subprocess, 'run', side_effect=run):
                for cli_status in (0, 1):
                    self.assertEqual(cli_status, module.install(root, 'example/skills', ['-g', '-y', '-s', 'polish', 'prototype', '-a', 'prototype']))
            lock = json.loads((root / '.skill-lock.json').read_text())['skills']
            self.assertEqual(matt, lock['prototype'])
            self.assertEqual('Matt content', (root / 'skills/prototype/SKILL.md').read_text())
            for name, selector in [('emil-prototype', 'prototype'), ('polish', 'polish')]:
                self.assertEqual('example/skills', lock[name]['source'])
                self.assertEqual(f'skills/{selector}/SKILL.md', lock[name]['skillPath'])
                self.assertEqual(40, len(lock[name]['skillFolderHash']))
            self.assertIn('name: emil-prototype\n', (root / 'skills/emil-prototype/SKILL.md').read_text())
