#!/usr/bin/env python3
"""Install a source with renamed skills without overwriting another publisher's skill."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def install(root: Path, repo: str, options: list[str]) -> int:
    manifest = json.loads((root / 'scripts/skills-manifest.json').read_text())
    source = next(source for source in manifest['sources'] if source['repo'] == repo)
    aliases = source.get('aliases', {})
    with tempfile.TemporaryDirectory(prefix='agent-kit-skills-') as temporary:
        checkout = Path(temporary) / 'source'
        subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{repo}.git', str(checkout)], check=True)
        entries = {}
        for path in checkout.rglob('SKILL.md'):
            if '.git' in path.parts:
                continue
            content = path.read_text(encoding='utf-8')
            match = re.search(r'(?m)^name:[ \t]*[\"\']?([^\"\'\n]+)[\"\']?[ \t]*$', content)
            if not match:
                continue
            original = match.group(1).strip()
            installed = aliases.get(original, original)
            relative = path.relative_to(checkout).as_posix()
            tree = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', f'HEAD:{path.parent.relative_to(checkout).as_posix()}'], text=True).strip()
            entries[installed] = (relative, tree)
            if installed != original:
                path.write_text(content[:match.start()] + f'name: {installed}' + content[match.end():], encoding='utf-8')
        translated = []
        selector = False
        for option in options:
            if option.startswith('--skill='):
                value = option.split('=', 1)[1]
                translated.append('--skill=' + aliases.get(value, value))
                selector = False
            elif option.startswith('-'):
                translated.append(option)
                selector = option in ('-s', '--skill')
            else:
                translated.append(aliases.get(option, option) if selector else option)
        result = subprocess.run([shutil.which('npx') or 'npx', '-y', 'skills@latest', 'add', str(checkout), *translated])
        # A failed CLI run may still have installed some skills. Repair those
        # entries before deleting the temporary source so retries remain safe.
        lockpath = root / '.skill-lock.json'
        if not lockpath.exists():
            return result.returncode or 1
        lock = json.loads(lockpath.read_text())
        for name, (relative, tree) in entries.items():
            entry = lock.get('skills', {}).get(name)
            if entry is None:
                continue
            # Only repair entries installed from this temporary checkout.
            checkout_url = checkout.as_posix()
            recorded_source = str(entry.get('source', '')).replace('\\', '/')
            recorded_url = str(entry.get('sourceUrl', '')).replace('\\', '/')
            if checkout_url not in recorded_source and checkout_url not in recorded_url:
                continue
            entry.update(source=repo, sourceType='github', sourceUrl=f'https://github.com/{repo}.git', skillPath=relative, skillFolderHash=tree)
        lockpath.write_text(json.dumps(lock, indent=2) + '\n')
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--source', required=True)
    args, options = parser.parse_known_args()
    return install(args.repo_root, args.source, options)


if __name__ == '__main__':
    raise SystemExit(main())
