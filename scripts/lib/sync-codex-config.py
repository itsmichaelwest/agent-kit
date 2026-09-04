#!/usr/bin/env python3
"""Sync explicitly owned Codex keys; keep all other configuration local."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
import tomlkit

BASELINE_NAME = 'agent-kit-config-baseline.json'
LOCK_NAME = 'agent-kit-config-sync.lock'
MARKERS = ('# >>> agent-kit managed codex config', '# <<< agent-kit managed codex config',
           '# >>> agent-kit generated agents', '# <<< agent-kit generated agents')

class SyncError(RuntimeError):
    pass


def read(path):
    return path.read_bytes() if path.exists() else b''


def parse(raw):
    try:
        text = raw.decode('utf-8')
        tomllib.loads(text)
        return tomlkit.parse(text)
    except (ValueError, tomllib.TOMLDecodeError) as exc:
        raise SyncError('Invalid TOML; no configuration changed') from exc


def flatten(data, prefix=()):
    result = {}
    for key, value in data.items():
        path = prefix + (key,)
        if isinstance(value, dict):
            result.update(flatten(value, path))
        else:
            result[path] = value
    return result


def state(data, path):
    value = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return {'present': False}
        value = value[key]
    return {'present': True, 'value': value}


def same(left, right):
    """TOML types matter: booleans, integers, and floats are distinct."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def put(document, path, value):
    node = document
    for key in path[:-1]:
        if key not in node:
            node[key] = tomlkit.table()
        elif not hasattr(node[key], 'items'):
            raise SyncError('Cannot edit key through a scalar: ' + '.'.join(path))
        node = node[key]
    if value['present']:
        node[path[-1]] = value['value']
    else:
        node.pop(path[-1], None)


def label(path):
    # JSON-quoted segments keep dotted role names unambiguous.
    return '.'.join(json.dumps(k) if '.' in k else k for k in path)


def load_source(repo):
    path = repo / 'config/codex/global.toml'
    if not path.exists():
        raise SyncError('Missing portable config: ' + str(path))
    raw = read(path)
    doc = parse(raw)
    data = tomllib.loads(raw.decode())
    if 'projects' in data:
        raise SyncError('Project trust must stay local')
    for key, value in data.get('agents', {}).items():
        if isinstance(value, dict):
            raise SyncError('Agent registrations are compiler-owned')
    return path, raw, doc, data


def desired_keys(repo, data):
    portable = flatten(data)
    desired = {p: {'present': True, 'value': v} for p, v in portable.items()}
    for path in sorted((repo / '.codex/agents').glob('*.toml')):
        agent = tomllib.loads(path.read_text(encoding='utf-8'))
        name = agent.get('name', path.stem)
        for key, value in {'config_file': 'agents/' + path.name,
                           'description': agent.get('description', '')}.items():
            desired[('agents', name, key)] = {'present': True, 'value': value}
    return portable, desired


def load_baseline(path):
    if not path.exists():
        return {}, True
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('version') == 2:
            entries = data['keys']
            result = {}
            for item in entries:
                p = tuple(item['path'])
                if not p or not all(isinstance(k, str) for k in p) or p in result:
                    raise ValueError('invalid path')
                v = item['state']
                if not isinstance(v.get('present'), bool) or (v['present'] and 'value' not in v):
                    raise ValueError('invalid state')
                result[p] = v
            return result, False
        if data.get('block_sha256') and data.get('portable_sha256'):
            # Old hashes cannot recover individual values. Adopt equal keys,
            # preserve differing values and expose them for explicit capture.
            return {}, True
        raise ValueError('unknown baseline')
    except (ValueError, KeyError, TypeError) as exc:
        raise SyncError('Invalid sync baseline: ' + str(path)) from exc


def migrate_comments(raw):
    # Remove only actual comment items, never marker text inside string values.
    doc = parse(raw)
    found = []
    def visit(container):
        body = container.body if hasattr(container, 'body') else container.value.body
        for _, item in list(body):
            if isinstance(item, tomlkit.items.Comment) and item.as_string().strip() in MARKERS:
                found.append(item.as_string().strip())
            elif isinstance(item, tomlkit.items.Table):
                visit(item)
    visit(doc)
    for start, end in ((MARKERS[0], MARKERS[1]), (MARKERS[2], MARKERS[3])):
        if found.count(start) != found.count(end) or found.count(start) > 1:
            raise SyncError('Incomplete or duplicate legacy managed markers')
        if start in found and found.index(start) > found.index(end):
            raise SyncError('Invalid legacy marker order')
    # Container.remove cannot address anonymous comments. Clear only their text.
    def clear(container):
        body = container.body if hasattr(container, 'body') else container.value.body
        for _, item in list(body):
            if isinstance(item, tomlkit.items.Comment) and item.as_string().strip() in MARKERS:
                item.trivia.comment = ''
            elif isinstance(item, tomlkit.items.Table):
                clear(item)
    clear(doc)
    return doc


def checked_write(path, payload, expected):
    """Atomic replacement with optimistic concurrency; not an app-wide lock."""
    if path.is_symlink():
        raise SyncError('Refusing to replace symlink: ' + str(path))
    if read(path) != expected:
        raise SyncError('File changed during sync; retry: ' + str(path))
    if payload == expected:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if read(path) != expected:
            raise SyncError('File changed during sync; retry: ' + str(path))
        if expected:
            backup = path.with_name(path.name + '.backup.' + str(time.time_ns()))
            backup.write_bytes(expected)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sync(repo, home, action):
    source, source_raw, source_doc, source_data = load_source(repo)
    portable, desired = desired_keys(repo, source_data)
    live = home / '.codex/config.toml'
    baseline = home / '.codex' / BASELINE_NAME
    if live.is_symlink():
        raise SyncError('Live config must not be a symlink')
    if action == 'capture' and not live.exists():
        raise SyncError('Missing live config; apply before capture')
    live_raw, baseline_raw = read(live), read(baseline)
    live_doc = migrate_comments(live_raw)
    live_data = tomllib.loads(live_raw.decode())
    previous, migrating = load_baseline(baseline)
    next_base = {}
    edits = []
    conflicts = []
    reported = 0
    for path, wanted in sorted(desired.items()):
        actual = state(live_data, path)
        old = previous.get(path)
        if same(actual, wanted):
            status = 'UNCHANGED'
            next_base[path] = wanted
        elif old is None:
            status = 'APPLY' if not actual['present'] else 'LOCAL'
            if status != 'APPLY' or action != 'capture':
                next_base[path] = wanted
        elif same(wanted, old):
            status = 'LOCAL'
            next_base[path] = old
        elif same(actual, old):
            status = 'APPLY'
            next_base[path] = old
        else:
            status = 'CONFLICT'
            conflicts.append(path)
        if status != 'UNCHANGED':
            print(f'[{status}] {label(path)}')
            reported += 1
        if status == 'APPLY' and action != 'capture':
            edits.append((path, wanted))
            next_base[path] = wanted
        elif status == 'LOCAL' and action == 'capture' and path in portable:
            edits.append((path, actual))
            next_base[path] = actual
        elif status == 'LOCAL' and action == 'capture':
            print('[SKIP] Compiler-owned field: ' + label(path))
    for path in sorted(set(previous) - set(desired)):
        print('[RELEASE] ' + label(path))
    if migrating:
        print('[MIGRATE] Adopt per-key baseline; preserve existing local values')
    if conflicts:
        raise SyncError('Conflicting keys; no writes. Make repo and local values agree, then retry.')
    if action == 'preview':
        if not reported and not migrating and set(previous) == set(desired):
            print('[OK] All owned settings are synchronized')
        return 0
    target, expected, document = (source, source_raw, source_doc) if action == 'capture' else (live, live_raw, live_doc)
    for path, value in edits:
        put(document, path, value)
    output = tomlkit.dumps(document).encode('utf-8')
    parse(output)
    # Capture can remove ownership; don't leave deleted source keys in baseline.
    if action == 'capture':
        remaining = flatten(tomllib.loads(output.decode()))
        next_base = {p: v for p, v in next_base.items() if p not in portable or p in remaining}
    payload = json.dumps({'version': 2, 'keys': [{'path': list(p), 'state': s}
                         for p, s in sorted(next_base.items())]}, indent=2).encode() + b'\n'
    # Check all inputs before any write. Baseline is committed last; if interrupted,
    # converged keys are accepted on the next run.
    for path, raw in ((source, source_raw), (live, live_raw), (baseline, baseline_raw)):
        if read(path) != raw:
            raise SyncError('Input changed during sync; retry: ' + str(path))
    checked_write(target, output, expected)
    checked_write(baseline, payload, baseline_raw)
    print('[OK] ' + ('Captured owned local values' if action == 'capture' else 'Synced owned settings'))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'capture', 'preview'))
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--home-dir', type=Path, required=True)
    args = parser.parse_args()
    lock = args.home_dir / '.codex' / LOCK_NAME
    acquired = False
    try:
        if args.action != 'preview':
            try:
                lock.mkdir(parents=True)
                acquired = True
            except FileExistsError as exc:
                raise SyncError('Another config sync is running: ' + str(lock)) from exc
        return sync(args.repo_root, args.home_dir, args.action)
    except (SyncError, OSError, ValueError) as exc:
        print('[ERROR] ' + str(exc), file=sys.stderr)
        return 1
    finally:
        if acquired:
            lock.rmdir()


if __name__ == '__main__':
    sys.exit(main())
