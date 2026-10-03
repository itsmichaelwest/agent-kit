from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lib" / "sync-codex-config.py"


class CodexConfigSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.repo = root / "repo"
        self.home = root / "home"
        self.source = self.repo / "config" / "codex" / "global.toml"
        self.live = self.home / ".codex" / "config.toml"
        self.baseline = self.home / ".codex" / "agent-kit-config-baseline.json"
        (self.repo / "config" / "codex").mkdir(parents=True)
        (self.repo / ".codex" / "agents").mkdir(parents=True)
        self.home.mkdir()
        self.source.write_text(
            textwrap.dedent(
                """\
                #:schema https://developers.openai.com/codex/config-schema.json
                personality = "pragmatic"
                sandbox_mode = "danger-full-access"

                [features]
                multi_agent = true

                [agents]
                max_threads = 16
                """
            ),
            encoding="utf-8",
        )
        (self.repo / ".codex" / "agents" / "developer.toml").write_text(
            textwrap.dedent(
                '''\
                name = "developer"
                description = "Developer agent"
                model = "gpt-5.6-sol"

                developer_instructions = """
                # Developer
                """
                '''
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_sync(self, action: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [sys.executable, str(SCRIPT), action, "--repo-root", str(self.repo), "--home-dir", str(self.home)],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )


    def apply(self):
        result = self.run_sync("apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def change(self, path, old, new):
        path.write_text(path.read_text().replace(old, new), encoding="utf-8")

    def link_generated_agents(self) -> None:
        link = self.home / '.codex' / 'agents'
        target = self.repo / '.codex' / 'agents'
        if os.name == 'nt':
            env = os.environ.copy()
            env['AGENT_KIT_TEST_LINK'] = str(link)
            env['AGENT_KIT_TEST_TARGET'] = str(target)
            result = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command',
                 'New-Item -ItemType Junction -Path $env:AGENT_KIT_TEST_LINK '
                 '-Target $env:AGENT_KIT_TEST_TARGET -ErrorAction Stop | Out-Null'],
                env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            link.symlink_to(target, target_is_directory=True)
        self.assertEqual(link.resolve(), target.resolve())

    def prepare_legacy_retirement(self) -> None:
        self.apply()
        self.link_generated_agents()
        (self.repo / '.codex/agents/developer.toml').unlink()
        previous = json.loads(self.baseline.read_text())
        previous['keys'] = [
            item for item in previous['keys']
            if item['path'][:2] != ['agents', 'developer']
        ]
        self.baseline.write_text(json.dumps(previous), encoding='utf-8')

    def test_fresh_install_and_idempotence(self):
        self.apply()
        before = self.live.read_bytes()
        baseline = self.baseline.read_bytes()
        self.apply()
        self.assertEqual(self.live.read_bytes(), before)
        self.assertEqual(self.baseline.read_bytes(), baseline)
        self.assertNotIn("agent-kit managed", before.decode())
        self.assertEqual(tomllib.loads(before.decode())["agents"]["developer"]["config_file"], "agents/developer.toml")

    def test_preserves_local_keys_comments_and_arrays(self):
        self.live.parent.mkdir()
        original = '# local comment\n[features]\njs_repl = false # keep\n[shell_environment_policy.set]\nLOCAL = "value"\n[[skills.config]]\npath = "local"\nenabled = false\n'
        self.live.write_text(original)
        self.apply()
        text = self.live.read_text()
        self.assertIn('js_repl = false # keep', text)
        self.assertIn('# local comment', text)
        data = tomllib.loads(text)
        self.assertFalse(data['features']['js_repl'])
        self.assertEqual(data['skills']['config'][0]['path'], 'local')
        self.assertEqual(data['shell_environment_policy']['set']['LOCAL'], 'value')

    def test_local_changes_do_not_block_unrelated_repo_changes(self):
        self.apply()
        self.change(self.live, '"pragmatic"', '"friendly"')
        self.change(self.source, 'max_threads = 16', 'max_threads = 8')
        self.apply()
        parsed = tomllib.loads(self.live.read_text())
        self.assertEqual(parsed['personality'], 'friendly')
        self.assertEqual(parsed['agents']['max_threads'], 8)
        self.assertIn('[LOCAL] personality', self.run_sync('preview').stdout)

    def test_conflict_writes_neither_config_nor_baseline(self):
        self.apply()
        self.change(self.live, '"pragmatic"', '"friendly"')
        self.change(self.source, '"pragmatic"', '"none"')
        self.change(self.source, 'max_threads = 16', 'max_threads = 8')
        before = [p.read_bytes() for p in (self.live,self.source,self.baseline)]
        for action in ('apply','capture','preview'):
            result = self.run_sync(action)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('[CONFLICT] personality', result.stdout)
            self.assertEqual(before, [p.read_bytes() for p in (self.live,self.source,self.baseline)])

    def test_converged_two_sided_change(self):
        self.apply()
        for p in (self.live,self.source): self.change(p, '"pragmatic"', '"friendly"')
        self.apply()
        self.assertNotIn('[LOCAL]', self.run_sync('preview').stdout)

    def test_release_keeps_machine_value_and_capture_does_not_reimport(self):
        self.apply()
        self.change(self.source, 'sandbox_mode = "danger-full-access"\n', '')
        self.apply()
        self.assertIn('sandbox_mode', tomllib.loads(self.live.read_text()))
        self.assertEqual(self.run_sync('capture').returncode, 0)
        self.assertNotIn('sandbox_mode', tomllib.loads(self.source.read_text()))

    def test_capture_only_owned_local_changes_and_preserves_repo_changes(self):
        self.apply()
        self.change(self.live, '"pragmatic"', '"friendly"')
        self.live.write_text(self.live.read_text()+'\n[plugins.local]\nenabled = true\n')
        self.change(self.source, 'max_threads = 16', 'max_threads = 8')
        result = self.run_sync('capture')
        self.assertEqual(result.returncode, 0, result.stderr)
        source = tomllib.loads(self.source.read_text())
        self.assertEqual(source['personality'], 'friendly')
        self.assertEqual(source['agents']['max_threads'], 8)
        self.assertNotIn('plugins', source)
        self.apply()
        self.assertEqual(tomllib.loads(self.live.read_text())['agents']['max_threads'], 8)

    def test_capture_deleted_owned_key_releases_it(self):
        self.apply()
        self.change(self.live, 'personality = "pragmatic"\n', '')
        self.assertEqual(self.run_sync('capture').returncode, 0)
        self.assertNotIn('personality', tomllib.loads(self.source.read_text()))
        self.apply()
        self.assertNotIn('personality', tomllib.loads(self.live.read_text()))

    def test_existing_different_value_is_preserved_on_first_install(self):
        self.live.parent.mkdir()
        self.live.write_text('personality = "friendly"\n')
        self.apply()
        self.assertEqual(tomllib.loads(self.live.read_text())['personality'], 'friendly')
        self.assertEqual(self.run_sync('capture').returncode, 0)
        self.assertEqual(tomllib.loads(self.source.read_text())['personality'], 'friendly')

    def test_legacy_migration_preserves_unknowns_and_multiline_marker_text(self):
        self.live.parent.mkdir()
        self.live.write_text('# >>> agent-kit managed codex config\npersonality = "friendly"\nnotify = ["local"]\n[features]\njs_repl = false\n# >>> agent-kit generated agents\n[agents.custom]\nconfig_file = "custom.toml"\n# <<< agent-kit generated agents\n# <<< agent-kit managed codex config\n[other]\ntext = \'\'\'\n# >>> agent-kit managed codex config\n\'\'\'\n')
        self.baseline.write_text('{"block_sha256":"old", "portable_sha256":"old"}')
        self.apply()
        data = tomllib.loads(self.live.read_text())
        self.assertEqual(data['personality'], 'friendly')
        self.assertEqual(data['notify'], ['local'])
        self.assertIn('custom', data['agents'])
        self.assertIn('# >>> agent-kit managed codex config', data['other']['text'])
        self.assertFalse(data['features']['js_repl'])

    def test_incomplete_markers_and_malformed_toml_fail_without_writes(self):
        self.live.parent.mkdir()
        for original in ('# >>> agent-kit managed codex config\npersonality="friendly"\n', 'broken = ['):
            self.live.write_text(original)
            self.assertNotEqual(self.run_sync('apply').returncode,0)
            self.assertEqual(self.live.read_text(),original)
            self.assertFalse(self.baseline.exists())

    def test_preview_is_read_only_even_on_fresh_machine(self):
        result=self.run_sync('preview')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(self.live.parent.exists())

    def test_generated_fields_preserve_custom_neighbors_when_retiring_roles(self):
        self.apply()
        self.live.write_text(self.live.read_text()+'\n[agents.developer.extra]\nvalue = "local"\n')
        (self.repo/'.codex/agents/developer.toml').unlink()
        self.apply()
        data=tomllib.loads(self.live.read_text())
        self.assertEqual(data['agents']['developer']['extra']['value'],'local')
        self.assertNotIn('config_file',data['agents']['developer'])
        self.assertNotIn('description',data['agents']['developer'])

    def test_retired_generated_role_is_removed_and_empty_table_pruned(self):
        self.apply()
        (self.repo / '.codex/agents/developer.toml').unlink()
        result = self.run_sync('apply')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('[REMOVE] agents.developer.config_file', result.stdout)
        self.assertIn('[REMOVE] agents.developer.description', result.stdout)
        self.assertNotIn('developer', tomllib.loads(self.live.read_text())['agents'])
        self.assertNotIn('[agents.developer]', self.live.read_text())
        before = [p.read_bytes() for p in (self.live, self.baseline)]
        self.apply()
        self.assertEqual(before, [p.read_bytes() for p in (self.live, self.baseline)])

    def test_pruned_retired_role_preserves_standalone_and_header_comments(self):
        self.apply()
        self.change(
            self.live, '[agents.developer]',
            '[agents.developer] # Local header note\n# Local standalone note',
        )
        (self.repo / '.codex/agents/developer.toml').unlink()
        self.apply()
        text = self.live.read_text()
        data = tomllib.loads(text)
        self.assertNotIn('developer', data['agents'])
        self.assertNotIn('[agents.developer]', text)
        self.assertIn('# Local header note', text)
        self.assertIn('# Local standalone note', text)
        self.assertEqual(data['agents']['max_threads'], 16)

    def test_retired_role_preserves_edited_local_description(self):
        self.apply()
        self.change(self.live, 'description = "Developer agent"', 'description = "Local notes"')
        (self.repo / '.codex/agents/developer.toml').unlink()
        self.apply()
        role = tomllib.loads(self.live.read_text())['agents']['developer']
        self.assertEqual(role, {'description': 'Local notes'})

    def test_retired_role_with_repurposed_local_path_keeps_metadata(self):
        self.apply()
        self.change(self.live, 'config_file = "agents/developer.toml"', 'config_file = "custom/developer.toml"')
        (self.repo / '.codex/agents/developer.toml').unlink()
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['developer'],
            {'config_file': 'custom/developer.toml', 'description': 'Developer agent'},
        )

    def test_legacy_stale_registration_in_linked_agents_directory_is_removed(self):
        self.prepare_legacy_retirement()
        self.apply()
        self.assertNotIn('developer', tomllib.loads(self.live.read_text())['agents'])

    def test_legacy_retirement_removes_unbaselined_registration_description(self):
        self.prepare_legacy_retirement()
        self.change(self.live, 'description = "Developer agent"', 'description = "Local notes"')
        self.apply()
        self.assertNotIn('developer', tomllib.loads(self.live.read_text())['agents'])

    def test_legacy_cleanup_preserves_local_description_table(self):
        self.prepare_legacy_retirement()
        self.change(self.live, 'description = "Developer agent"\n', '')
        self.live.write_text(self.live.read_text() + '\n[agents.developer.description]\nnote = "keep"\n')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['developer'],
            {'description': {'note': 'keep'}},
        )

    def test_legacy_cleanup_preserves_local_description_array(self):
        self.prepare_legacy_retirement()
        self.change(self.live, 'description = "Developer agent"', 'description = ["keep", "notes"]')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['developer'],
            {'description': ['keep', 'notes']},
        )

    def test_legacy_capture_keeps_pending_cleanup_owned_until_apply(self):
        self.prepare_legacy_retirement()
        before = [p.read_bytes() for p in (self.live, self.source)]
        capture = self.run_sync('capture')
        self.assertEqual(capture.returncode, 0, capture.stdout + capture.stderr)
        self.assertIn('[SKIP] Retired agent field; apply to remove: agents.developer.config_file', capture.stdout)
        self.assertIn('[SKIP] Retired agent field; apply to remove: agents.developer.description', capture.stdout)
        self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source)])
        tracked = {tuple(item['path']): item['state'] for item in json.loads(self.baseline.read_text())['keys']}
        self.assertEqual(tracked[('agents', 'developer', 'config_file')],
                         {'present': True, 'value': 'agents/developer.toml'})
        self.assertEqual(tracked[('agents', 'developer', 'description')],
                         {'present': True, 'value': 'Developer agent'})
        self.apply()
        self.assertNotIn('developer', tomllib.loads(self.live.read_text())['agents'])

    def test_unknown_missing_canonical_registration_in_linked_directory_is_removed(self):
        self.apply()
        self.link_generated_agents()
        self.live.write_text(self.live.read_text() + '\n[agents.missingrole]\n'
                             'config_file = "agents/missingrole.toml"\ndescription = "Custom role"\n')
        self.apply()
        self.assertNotIn('missingrole', tomllib.loads(self.live.read_text())['agents'])

    def test_legacy_local_path_override_in_linked_directory_is_preserved(self):
        self.prepare_legacy_retirement()
        self.change(self.live, 'config_file = "agents/developer.toml"', 'config_file = "custom/developer.toml"')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['developer'],
            {'config_file': 'custom/developer.toml', 'description': 'Developer agent'},
        )

    def test_traversal_role_names_in_linked_directory_are_preserved(self):
        self.apply()
        self.link_generated_agents()
        roles = ('../external', '..\\external')
        text = self.live.read_text()
        for role in roles:
            text += '\n[agents.' + json.dumps(role) + ']\nconfig_file = ' + json.dumps('agents/' + role + '.toml')
            text += '\ndescription = "External role"\n'
        self.live.write_text(text)
        self.apply()
        data = tomllib.loads(self.live.read_text())['agents']
        for role in roles:
            with self.subTest(role=role):
                self.assertEqual(data[role],
                                 {'config_file': 'agents/' + role + '.toml', 'description': 'External role'})

    def test_missing_local_canonical_registration_in_separate_directory_is_preserved(self):
        self.apply()
        (self.home / '.codex/agents').mkdir()
        self.live.write_text(self.live.read_text() + '\n[agents.local]\n'
                             'config_file = "agents/local.toml"\ndescription = "Local role"\n')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['local'],
            {'config_file': 'agents/local.toml', 'description': 'Local role'},
        )

    def test_retired_role_with_valid_local_file_is_preserved(self):
        self.apply()
        local_agents = self.home / '.codex/agents'
        local_agents.mkdir()
        generated = self.repo / '.codex/agents/developer.toml'
        (local_agents / 'developer.toml').write_bytes(generated.read_bytes())
        generated.unlink()
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['developer'],
            {'config_file': 'agents/developer.toml', 'description': 'Developer agent'},
        )

    def test_existing_untracked_local_role_file_absent_from_repo_is_preserved(self):
        self.apply()
        local_agents = self.home / '.codex/agents'
        local_agents.mkdir()
        (local_agents / 'local.toml').write_text('name = "local"\n', encoding='utf-8')
        self.live.write_text(self.live.read_text() + '\n[agents.local]\n'
                             'config_file = "agents/local.toml"\ndescription = "Local role"\n')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['local'],
            {'config_file': 'agents/local.toml', 'description': 'Local role'},
        )

    def test_missing_external_registration_is_preserved(self):
        self.apply()
        self.link_generated_agents()
        external = str(Path(self.temp.name) / 'external' / 'missing.toml')
        self.live.write_text(self.live.read_text() + '\n[agents.external]\nconfig_file = '
                             + json.dumps(external) + '\ndescription = "External role"\n')
        self.apply()
        self.assertEqual(
            tomllib.loads(self.live.read_text())['agents']['external'],
            {'config_file': external, 'description': 'External role'},
        )

    def test_retirement_preview_and_capture_preserve_live_config_and_tracking(self):
        self.apply()
        (self.repo / '.codex/agents/developer.toml').unlink()
        before = [p.read_bytes() for p in (self.live, self.source, self.baseline)]
        preview = self.run_sync('preview')
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn('[REMOVE] agents.developer.config_file', preview.stdout)
        self.assertIn('[REMOVE] agents.developer.description', preview.stdout)
        self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source, self.baseline)])
        capture = self.run_sync('capture')
        self.assertEqual(capture.returncode, 0, capture.stdout + capture.stderr)
        self.assertIn('[SKIP]', capture.stdout)
        self.assertIn('agents.developer.config_file', capture.stdout)
        self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source, self.baseline)])
        self.apply()
        self.assertNotIn('developer', tomllib.loads(self.live.read_text())['agents'])

    def test_conflict_writes_nothing_when_retirement_is_planned(self):
        self.apply()
        (self.repo / '.codex/agents/developer.toml').unlink()
        self.change(self.live, '"pragmatic"', '"friendly"')
        self.change(self.source, '"pragmatic"', '"none"')
        before = [p.read_bytes() for p in (self.live, self.source, self.baseline)]
        for action in ('apply', 'capture', 'preview'):
            with self.subTest(action=action):
                result = self.run_sync(action)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('[CONFLICT] personality', result.stdout)
                self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source, self.baseline)])

    def test_restored_agent_target_aborts_retirement_before_any_write(self):
        import importlib.util

        self.apply()
        generated = self.repo / '.codex/agents/developer.toml'
        agent_bytes = generated.read_bytes()
        generated.unlink()
        before = [p.read_bytes() for p in (self.live, self.source, self.baseline)]
        spec = importlib.util.spec_from_file_location('sync_retirement_race_test', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = module.stale_agent_fields
        calls = 0

        def restore_before_recheck(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                generated.write_bytes(agent_bytes)
            return original(*args, **kwargs)

        with patch.object(module, 'stale_agent_fields', side_effect=restore_before_recheck):
            with self.assertRaisesRegex(module.SyncError, 'Agent files changed during sync'):
                module.sync(self.repo, self.home, 'apply')
        self.assertEqual(calls, 2)
        self.assertEqual(generated.read_bytes(), agent_bytes)
        self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source, self.baseline)])

    def test_invalid_live_agents_root_fails_cleanly_without_writes(self):
        self.apply()
        for value in ('7', '[]', '["custom"]'):
            self.live.write_text('agents = ' + value + '\npersonality = "pragmatic"\n')
            before = [p.read_bytes() for p in (self.live, self.source, self.baseline)]
            for action in ('apply', 'capture', 'preview'):
                with self.subTest(value=value, action=action):
                    result = self.run_sync(action)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('[ERROR]', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertEqual(before, [p.read_bytes() for p in (self.live, self.source, self.baseline)])

    def test_two_machine_round_trip(self):
        self.apply()
        first=self.home
        self.home=Path(self.temp.name)/'second-home'
        self.home.mkdir()
        self.apply()
        second_live=self.home/'.codex/config.toml'
        self.change(second_live,'"pragmatic"','"friendly"')
        self.assertEqual(self.run_sync('capture').returncode,0)
        self.home=first
        self.apply()
        self.assertEqual(tomllib.loads(self.live.read_text())['personality'],'friendly')

    def test_quoted_dotted_keys_inline_tables_and_multiline_arrays(self):
        self.source.write_text('features = { multi_agent = true }\n[tui]\nstatus_line = [\n"model",\n"git-branch",\n]\n')
        self.live.parent.mkdir()
        self.live.write_text('features = { multi_agent = true, js_repl = false } # local\n["projects"."a.b"]\ntrust_level="trusted"\n')
        self.apply()
        data=tomllib.loads(self.live.read_text())
        self.assertFalse(data['features']['js_repl'])
        self.assertEqual(data['projects']['a.b']['trust_level'],'trusted')
        self.assertEqual(data['tui']['status_line'],['model','git-branch'])

    def test_stale_write_rejected(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('sync_test',SCRIPT)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.live.parent.mkdir()
        self.live.write_bytes(b'# changed')
        with self.assertRaises(module.SyncError): module.checked_write(self.live,b'# replacement',b'# original')
        self.assertEqual(self.live.read_bytes(),b'# changed')

    def test_capture_requires_existing_live_file(self):
        original=self.source.read_bytes()
        self.assertNotEqual(self.run_sync('capture').returncode,0)
        self.assertEqual(self.source.read_bytes(),original)
        self.assertFalse(self.baseline.exists())

    def test_capture_does_not_accept_unapplied_new_key(self):
        self.apply()
        self.source.write_text('web_search = "live"\n'+self.source.read_text())
        self.assertEqual(self.run_sync('capture').returncode,0)
        self.apply()
        self.assertEqual(tomllib.loads(self.live.read_text())['web_search'],'live')

    def test_different_toml_types_are_not_equal(self):
        self.apply()
        self.change(self.live,'multi_agent = true','multi_agent = 1')
        self.assertIn('[LOCAL] features.multi_agent',self.run_sync('preview').stdout)
        self.change(self.source,'multi_agent = true','multi_agent = false')
        self.assertNotEqual(self.run_sync('apply').returncode,0)

    def test_capture_does_not_import_generated_agent_fields(self):
        self.apply()
        self.change(self.live,'description = "Developer agent"','description = "Local agent"')
        before=self.source.read_bytes()
        self.assertEqual(self.run_sync('capture').returncode,0)
        self.assertEqual(self.source.read_bytes(),before)

if __name__ == '__main__':
    unittest.main()
