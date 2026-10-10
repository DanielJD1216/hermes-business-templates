"""Canonical package placement and non-destructive instruction updates."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from test_installer import hbt, TPL


class Canonical(unittest.TestCase):
    def test_workspace_places_canonical_docs_and_preserves_existing_instructions(self):
        tpl = hbt.load_template('creator')
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / 'AGENTS.md').write_text('Owner rules\n')
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual((ws / 'AGENTS.md').read_text(), 'Owner rules\n')
            for name in ('USER.md', 'FILES.md', 'PROJECTS.md', 'skills/project-onboarding/SKILL.md',
                         'skills/project-onboarding/scripts/onboard.py'):
                self.assertTrue((ws / name).is_file(), name)
            self.assertIn('Team workspace operating instructions', (ws / 'media/AGENTS.md').read_text())
            (ws / 'USER.md').write_text('Private owner preferences\n')
            (ws / 'media/AGENTS.md').write_text('Custom role rules\n')
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual((ws / 'USER.md').read_text(), 'Private owner preferences\n')
            self.assertEqual((ws / 'media/AGENTS.md').read_text(), 'Custom role rules\n')

    def test_recorded_updates_and_dry_run(self):
        tpl = hbt.load_template('creator')
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            before = hbt.package_hashes(ws)
            self.assertEqual(hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False), [])
            self.assertEqual(hbt.package_hashes(ws), before)
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=True, bots={'engineer': 'U1234567'})
            self.assertEqual(hbt.package_hashes(ws), before)
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False, bots={'engineer': 'U1234567'})
            self.assertIn('<@U1234567>', (ws / 'build/AGENTS.md').read_text())
            self.assertLess(len((ws / 'build/AGENTS.md').read_text()), 20000)
            script = ws / 'skills/project-onboarding/scripts/onboard.py'
            script.write_text('# owner helper customization\n')
            hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual(script.read_text(), '# owner helper customization\n')
            (ws / 'USER.md').unlink()
            (ws / 'USER.md').symlink_to(ws / 'canon/business.md')
            with self.assertRaisesRegex(SystemExit, 'symlink'):
                hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)

    def test_native_explicit_skill_discovery_and_preservation(self):
        """Real native handlers, no model: use dependency-complete Python + native PYTHONPATH."""
        native = importlib.util.find_spec('hermes_cli')
        if native is None or native.origin is None:
            self.skipTest('Native Hermes source must be on PYTHONPATH')
        source = Path(native.origin).resolve().parent.parent
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ws = root / 'business'
            hbt.build_workspace(hbt.load_template('creator'), [], ws, {}, dry=False)
            script = textwrap.dedent('''
                import copy, hashlib, json, os, sys
                from pathlib import Path
                attempts = []
                def no_network(event, args):
                    if event in ('socket.connect', 'socket.getaddrinfo'):
                        attempts.append(event)
                        raise RuntimeError('Native discovery test forbids network')
                sys.addaudithook(no_network)
                home = Path(os.environ['HERMES_HOME'])
                home.mkdir(parents=True)
                assert home.parent == Path.home()
                package = Path(sys.argv[1]) / 'skills/project-onboarding'
                owner_root = home.parent / 'owner-skills'
                owner_root.mkdir()
                cfg = {'skills': {'external_dirs': [str(owner_root)],
                                  'disabled': ['owner-disabled'],
                                  'platform_disabled': {'slack': ['owner-disabled']},
                                  'create_dir': str(home / 'created-skills')},
                       'model': {'default': 'sentinel-not-a-provider-call'},
                       'custom_owner_setting': {'keep': ['unchanged']},
                       'shared_metrics': {'enabled': False}}
                config = home / 'config.yaml'
                config.write_text(json.dumps(cfg))
                soul = home / 'SOUL.md'
                soul.write_text('Existing main identity. Do not replace.\\n')
                soul_bytes = soul.read_bytes()
                from hermes_cli.config import set_config_value, read_user_config_raw
                from tools.skills_tool import skills_list, skill_view, clear_skills_cache
                from agent.prompt_builder import build_skills_system_prompt, clear_skills_system_prompt_cache
                def names():
                    clear_skills_cache()
                    result = json.loads(skills_list())
                    assert result['success'], result
                    return {s['name'] for s in result['skills']}
                assert 'project-onboarding' not in names()
                expected = copy.deepcopy(cfg)
                expected['skills']['external_dirs'].append(str(package))
                set_config_value('skills.external_dirs', json.dumps(expected['skills']['external_dirs']))
                assert read_user_config_raw() == expected
                assert soul.read_bytes() == soul_bytes
                assert 'project-onboarding' in names()
                view = json.loads(skill_view('project-onboarding', preprocess=False))
                assert view['success'], view
                assert Path(view['_source_path']) == package / 'SKILL.md', view
                assert len(view['description']) <= 60
                support = json.loads(skill_view('project-onboarding', file_path='scripts/onboard.py', preprocess=False))
                assert support['success'] and 'def onboard(' in support['content'], support
                clear_skills_system_prompt_cache()
                assert 'project-onboarding' in build_skills_system_prompt()
                # Repeat adoption skips the write. No duplicate roots or package copies.
                before = config.read_bytes()
                assert str(package) in read_user_config_raw()['skills']['external_dirs']
                assert config.read_bytes() == before
                assert not (home / 'skills/project-onboarding').exists()
                # A same-name owner package takes precedence and is never overwritten.
                local = home / 'skills/project-onboarding'
                local.mkdir(parents=True)
                local_skill = local / 'SKILL.md'
                local_skill.write_text('---\\nname: project-onboarding\\ndescription: Owner procedure.\\n---\\nOwner instructions.\\n')
                owner_bytes = local_skill.read_bytes()
                clear_skills_cache()
                owner_view = json.loads(skill_view('project-onboarding', preprocess=False))
                assert Path(owner_view['_source_path']) == local_skill, owner_view
                assert local_skill.read_bytes() == owner_bytes
                # Withdraw just the added root; retain unrelated settings and owner package.
                set_config_value('skills.external_dirs', json.dumps(cfg['skills']['external_dirs']))
                assert read_user_config_raw() == cfg
                assert soul.read_bytes() == soul_bytes and local_skill.read_bytes() == owner_bytes
                assert not attempts, attempts
                print('NATIVE_DISCOVERY_OK ' + json.dumps({
                    'source': str(package / 'SKILL.md'), 'index': True, 'list': True,
                    'view': True, 'support': True, 'owner_collision_preserved': True,
                    'config_preserved': True, 'soul_sha256': hashlib.sha256(soul_bytes).hexdigest(),
                    'network_attempts': attempts}))
            ''')
            env = {'HOME': str(root), 'HERMES_HOME': str(root / '.hermes'),
                   'PYTHONPATH': str(source), 'PYTHONDONTWRITEBYTECODE': '1',
                   'PATH': os.environ.get('PATH', ''), 'TMPDIR': d}
            result = subprocess.run([sys.executable, '-c', script, str(ws)], cwd=root,
                                    env=env, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('NATIVE_DISCOVERY_OK', result.stdout)
            print(result.stdout.strip())

    def test_role_directory_symlink_never_creates_folders_outside_workspace(self):
        tpl = hbt.load_template('creator')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ws, outside = root / 'workspace', root / 'outside'
            ws.mkdir()
            outside.mkdir()
            (ws / 'media').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(SystemExit, 'symlink'):
                hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
