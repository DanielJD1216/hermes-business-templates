"""Team and path configuration, always in disposable HOME and HERMES_HOME."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_installer import hbt


class TeamConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / '.hermes'
        self.home.mkdir()
        env = patch.dict(os.environ, HOME=str(self.root), HERMES_HOME=str(self.home))
        env.start()
        self.addCleanup(env.stop)
        self.tpl = hbt.load_template('creator')

    def test_projects_require_a_real_absolute_folder_not_a_placeholder(self):
        for raw in ('not setup yet', 'later', 'projects', '', '.', '/', '~/not setup yet',
                    '/some/path/../other', '$HOME/projects', '/path\nother'):
            with self.subTest(raw=raw), self.assertRaises(SystemExit):
                hbt.validate_projects(raw)
        self.assertEqual(hbt.validate_projects('~/My Projects'), str(self.root / 'My Projects'))
        existing = self.root / 'existing'
        existing.mkdir()
        (existing / 'keep.txt').write_text('keep')
        self.assertEqual(hbt.validate_projects(str(existing)), str(existing))
        for raw in (str(existing / 'keep.txt'), str(existing / 'keep.txt/child')):
            with self.assertRaises(SystemExit):
                hbt.validate_projects(raw)
        (self.root / 'linked').symlink_to(existing, target_is_directory=True)
        with self.assertRaises(SystemExit):
            hbt.validate_projects(str(self.root / 'linked/new'))
        self.assertFalse((self.root / 'My Projects').exists())

    def test_team_subset_alias_and_custom_purpose_are_explicit_and_persistable(self):
        team = {'schema': 1, 'roles': [
            {'key': 'cto', 'title': 'Technical Lead'},
            {'key': 'researcher', 'title': 'Researcher', 'purpose': 'Summarize public sources.',
             'permissions': 'draft-only', 'tools': ['web']}]}
        tpl = hbt.configure_team(self.tpl, team)
        self.assertEqual([r.key for r in tpl.roles], ['cto', 'researcher'])
        self.assertIsNone(tpl.ops)
        self.assertEqual(tpl.roles[0].title, 'Technical Lead')
        self.assertEqual(tpl.profile('cto'), 'cto')
        role = tpl.roles[1]
        self.assertEqual(role.purpose, 'Summarize public sources.')
        self.assertEqual(role.stock_skills, [])
        self.assertEqual(role.peers, [])
        staged = hbt.stage_distribution(tpl, role)
        self.assertIn(role.purpose, (staged / 'SOUL.md').read_text())
        self.assertFalse((staged / '.env').exists())
        cfg = hbt.yaml.safe_load((staged / 'config.yaml').read_text())
        self.assertEqual(cfg['platform_toolsets']['slack'], ['web', 'no_mcp'])
        self.assertEqual(cfg['platform_toolsets']['cli'], ['web', 'no_mcp'])
        self.assertEqual(cfg['approvals']['mode'], 'manual')
        self.assertEqual(cfg['mcp_servers'], {})
        self.assertNotIn('terminal', cfg)
        for mutation in (
            {'key': '../escape', 'title': 'Bad'}, {'key': 'default', 'title': 'Bad'},
            {'key': 'CTO', 'title': 'Bad'}, {'key': 'cto', 'title': 'bad\nname'},
            {'key': 'cto', 'title': 'Changed', 'purpose': 'Escalate'},
            {'key': 'new', 'title': 'New', 'purpose': 'Draft'},
            team['roles'][1] | {'tools': ['terminal']},
            team['roles'][1] | {'permissions': 'admin'},
            team['roles'][1] | {'clone': 'cto'},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(SystemExit):
                hbt.configure_team(self.tpl, {'schema': 1, 'roles': [mutation]})
        for entries in ([], [team['roles'][0], team['roles'][0]],
                        [team['roles'][1], team['roles'][1] | {'key': 'other'}]):
            with self.assertRaises(SystemExit):
                hbt.configure_team(self.tpl, {'schema': 1, 'roles': entries})
        # Deliberate same-purpose second instance needs a distinct ID AND display name.
        repeated = team['roles'][1] | {'key': 'researcher-two', 'title': 'Second Researcher'}
        self.assertEqual(len(hbt.configure_team(self.tpl, team | {'roles': [team['roles'][1], repeated]}).roles), 2)


    def test_install_custom_team_and_resume_uses_record_not_source_file(self):
        import shutil
        team = {'schema': 1, 'roles': [{'key': 'analyst', 'title': 'Analyst',
                'purpose': 'Draft summaries of public reports.', 'permissions': 'draft-only', 'tools': []}]}
        source = self.root / 'team.json'
        source.write_text(json.dumps(team))
        def native(*args, **kwargs):
            if args[:2] == ('profile', 'install'):
                src = Path(args[2])
                dest = self.home / 'profiles' / src.name
                shutil.copytree(src, dest)
                manifest = hbt.yaml.safe_load((dest / 'distribution.yaml').read_text())
                manifest['source'] = str(src)
                (dest / 'distribution.yaml').write_text(hbt.yaml.safe_dump(manifest))
            elif args[:2] == ('slack', 'manifest'):
                title = args[args.index('--name') + 1]
                Path(args[args.index('--write') + 1]).write_text(json.dumps({
                    'display_information': {'name': title}, 'features': {'bot_user': {'display_name': title}}}))
            return ''
        stock = self.root / 'stock'
        stock.mkdir()
        metadata = {'source': 'synthetic', 'root': stock, 'packages': {}, 'matches': lambda *a: False}
        with patch.object(hbt, 'preflight', return_value={'hermes_version': 'fixture', 'docker': False}), \
             patch.object(hbt, 'native_skills', return_value=metadata), \
             patch.object(hbt, 'seed_shared_manual'), patch.object(hbt.Runner, 'hermes_cmd', side_effect=native), \
             patch.object(hbt, 'say') as say:
            self.assertEqual(hbt.main(['install', 'creator', '--team', str(source), '--no-memory', '-y']), 0)
            rec = hbt.load_record('creator')
            self.assertEqual(rec['profiles'], ['analyst'])
            self.assertEqual(rec['team'], team)
            self.assertEqual(rec['jobs'], [])
            self.assertIn('operating-system account', '\n'.join(c.args[0] for c in say.call_args_list))
            self.assertNotIn('limited only by their working folder', '\n'.join(c.args[0] for c in say.call_args_list))
            source.unlink()
            self.assertEqual(hbt.main(['status', 'creator']), 0)
            with patch.object(hbt, '_wait', side_effect=KeyboardInterrupt) as wait:
                self.assertEqual(hbt.main(['setup', 'creator']), 1)
                self.assertIn('Analyst Slack app', wait.call_args.args[0])
            self.assertEqual(hbt.main(['update', 'creator']), 0)
            self.assertEqual(hbt.load_record('creator')['team'], team)
            inventory = hbt.uninstall_inventory('creator', hbt.load_record('creator'))
            self.assertIn('analyst', inventory)


    def test_guided_custom_team_and_invalid_projects_reprompt_before_writes(self):
        team = {'schema': 1, 'roles': [{'key': 'engineer', 'title': 'Builder'}]}
        source = self.root / 'team.json'
        source.write_text(json.dumps(team))
        before = hbt.package_hashes(self.root)
        answers = ['customize', str(source), 'Etc/UTC', 'not setup yet', str(self.root / 'projects'), 'U00000001']
        with patch('builtins.input', side_effect=answers), patch.object(hbt, 'cmd_install', return_value=1) as install, \
             patch.object(hbt, 'say'):
            self.assertEqual(hbt.main(['setup', 'creator']), 1)
        args = install.call_args.args[0]
        self.assertEqual(args.team_definition, team)
        self.assertEqual(args.projects, str(self.root / 'projects'))
        self.assertEqual(hbt.package_hashes(self.root), before)

    def test_invalid_install_path_refuses_without_native_mutation(self):
        before = hbt.package_hashes(self.root)
        with patch.object(hbt, 'preflight', return_value={'hermes_version': 'fixture', 'docker': False}), \
             patch.object(hbt.Runner, 'hermes_cmd', side_effect=AssertionError('native mutation')):
            with self.assertRaises(SystemExit):
                hbt.main(['install', 'creator', '--projects', 'not setup yet', '--no-memory', '-y'])
        self.assertEqual(hbt.package_hashes(self.root), before)


    def installed(self):
        roles = self.tpl.roles
        ws = self.root / 'workspace'
        old = self.root / 'Downloads/template/not setup yet'
        old.mkdir(parents=True)
        (old / 'keep.txt').write_text('original project')
        rec = {'version': self.tpl.version, 'installed_at': 'fixture', 'profiles': [r.key for r in roles],
               'workspace': str(ws), 'projects': str(old), 'jobs': [], 'channels': {}, 'bots': {},
               'owner': '', 'setup': {}, 'memory': {'enabled': False}, 'manifests': {}}
        for role in roles:
            prof = self.home / 'profiles' / role.key
            prof.mkdir(parents=True)
            (prof / 'config.yaml').write_text('# owner config\n{}\n')
            (prof / 'SOUL.md').write_text('keep canonical responsibilities')
            if role.kind != 'ops':
                dest = hbt.record_dir('creator') / f'{role.key}-slack-manifest.json'
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps({'display_information': {'name': role.title},
                                           'features': {'bot_user': {'display_name': role.title}}}))
                rec['manifests'][role.key] = str(dest)
        hbt.build_workspace(self.tpl, roles, ws, {}, False, projects=str(old))
        hbt.save_record('creator', rec)
        return rec

    def test_correction_is_narrow_backed_up_and_idempotent(self):
        rec = self.installed()
        target = self.root / 'New Projects'
        target.mkdir()
        (target / 'also-keep.txt').write_text('unrelated project')
        args = ['configure', 'creator', '--projects', str(target), '--rename', 'creative-director=Studio Lead']
        before = hbt.package_hashes(self.root)
        with patch.object(hbt.Runner, 'hermes_cmd', side_effect=AssertionError('native')), \
             patch.object(hbt, 'slack_api', side_effect=AssertionError('Slack')), patch.object(hbt, 'say'):
            self.assertEqual(hbt.main(args + ['--dry-run']), 0)
            self.assertEqual(hbt.package_hashes(self.root), before)
            self.assertEqual(hbt.main(args + ['-y']), 0)
            after = hbt.package_hashes(self.root)
            self.assertEqual(hbt.main(args + ['-y']), 0)
            self.assertEqual(hbt.package_hashes(self.root), after)
        current = hbt.load_record('creator')
        self.assertEqual(current['profiles'], rec['profiles'])
        self.assertEqual(current['projects'], str(target))
        self.assertEqual(current['team']['roles'][0]['title'], 'Studio Lead')
        self.assertEqual(current['setup'], rec['setup'])
        self.assertEqual(hbt.package_hashes(self.home / 'profiles'),
                         {k[len('.hermes/profiles/'):]: v for k, v in before.items() if k.startswith('.hermes/profiles/')})
        for role in ('build', 'engineering'):
            text = (Path(rec['workspace']) / role / 'AGENTS.md').read_text()
            self.assertIn(str(target), text)
            self.assertNotIn(rec['projects'], text)
            self.assertIn('Studio Lead', text)
        self.assertEqual((Path(rec['projects']) / 'keep.txt').read_text(), 'original project')
        self.assertEqual((target / 'also-keep.txt').read_text(), 'unrelated project')
        saved = list(hbt.record_dir('creator').glob('backups/configure-*/record.json'))
        self.assertEqual(len(saved), 1)
        self.assertEqual(json.loads(saved[0].read_text()), rec)
        manifest = json.loads(Path(rec['manifests']['creative-director']).read_text())
        self.assertEqual(manifest['display_information']['name'], 'Studio Lead')
        self.assertEqual(manifest['features']['bot_user']['display_name'], 'Studio Lead')


    def test_correction_refuses_owner_edits_connected_renames_and_unsafe_paths(self):
        rec = self.installed()
        args = ['configure', 'creator', '--projects', str(self.root / 'new'), '-y']
        instructions = Path(rec['workspace']) / 'engineering/AGENTS.md'
        original = instructions.read_bytes()
        instructions.write_bytes(original + b'\nOwner rule\n')
        before = hbt.package_hashes(self.root)
        with self.assertRaisesRegex(SystemExit, 'Owner edits'):
            hbt.main(args)
        self.assertEqual(hbt.package_hashes(self.root), before)
        instructions.write_bytes(original)
        for extra in (['--projects', 'not setup yet'], ['--rename', 'missing=Name'],
                      ['--rename', 'cto=Ops'], ['--rename', 'cto=Name', '--rename', 'cto=Other']):
            before = hbt.package_hashes(self.root)
            with self.assertRaises(SystemExit):
                hbt.main(['configure', 'creator', '-y'] + extra)
            self.assertEqual(hbt.package_hashes(self.root), before)
        env = self.home / 'profiles/cto/.env'
        env.write_text('SLACK_APP_TOKEN=synthetic-never-sent\n')
        before = hbt.package_hashes(self.root)
        with self.assertRaisesRegex(SystemExit, 'already connected'):
            hbt.main(['configure', 'creator', '--rename', 'cto=Lead', '-y'])
        self.assertEqual(hbt.package_hashes(self.root), before)
        env.unlink()
        instructions.unlink()
        instructions.symlink_to(Path(rec['workspace']) / 'AGENTS.md')
        with self.assertRaisesRegex(SystemExit, 'symlink'):
            hbt.main(args)
        self.assertFalse((self.root / 'new').exists())

    def test_correction_rolls_back_ordinary_failure_and_preserves_new_owner_bytes(self):
        rec = self.installed()
        args = ['configure', 'creator', '--projects', str(self.root / 'new'), '-y']
        before = hbt.package_hashes(self.root)
        replace = hbt.os.replace
        def fail(source, target):
            if Path(target).name == '.hbt-workspace.json':
                raise OSError('injected storage failure')
            return replace(source, target)
        with patch.object(hbt.os, 'replace', side_effect=fail), patch.object(hbt, 'say'):
            with self.assertRaisesRegex(OSError, 'injected'):
                hbt.main(args)
        after = hbt.package_hashes(self.root)
        self.assertTrue(all(after.get(k) == v for k, v in before.items()))
        self.assertEqual(hbt.load_record('creator'), rec)
        with patch.object(hbt, 'say'):
            self.assertEqual(hbt.main(args), 0)

    def test_owner_change_during_confirmation_is_not_adopted_as_baseline(self):
        rec = self.installed()
        changed = Path(rec['workspace']) / 'build/AGENTS.md'
        def confirm(_):
            changed.write_text('new owner rules')
            return 'y'
        with patch('builtins.input', side_effect=confirm), patch.object(hbt, 'say'):
            with self.assertRaisesRegex(SystemExit, 'changed while planning'):
                hbt.main(['configure', 'creator', '--projects', str(self.root / 'new')])
        self.assertEqual(changed.read_text(), 'new owner rules')
        self.assertEqual(hbt.load_record('creator'), rec)
        self.assertFalse((self.root / 'new').exists())

    def test_native_custom_tool_resolution_is_no_tools_or_web_only(self):
        from hermes_cli.tools_config import _get_platform_tools
        for tools in ([], ['web']):
            tpl = hbt.configure_team(self.tpl, {'schema': 1, 'roles': [{
                'key': 'analyst', 'title': 'Analyst', 'purpose': 'Draft reports.',
                'permissions': 'draft-only', 'tools': tools}]})
            cfg = hbt.yaml.safe_load(hbt.custom_distribution(tpl, tpl.roles[0])['config.yaml'])
            # Even subsequently configured MCP servers do not defeat the explicit sentinel.
            cfg['mcp_servers'] = {'example': {'command': 'never-run', 'enabled': True}}
            for platform in ('cli', 'slack'):
                self.assertEqual(_get_platform_tools(cfg, platform), set(tools))


    def test_resume_blocks_placeholder_projects_before_slack_setup(self):
        rec = self.installed()
        before = hbt.package_hashes(self.root)
        self.assertEqual(hbt.next_setup_step(self.tpl, rec), ('projects', None))
        with patch.object(hbt, '_wait', side_effect=AssertionError('Slack setup')), patch.object(hbt, 'say') as say:
            self.assertEqual(hbt.main(['setup', 'creator']), 1)
            text = '\n'.join(c.args[0] for c in say.call_args_list)
            self.assertIn('configure creator --projects', text)
        self.assertEqual(hbt.package_hashes(self.root), before)


    def test_invalid_team_json_never_falls_back_to_default_privileges(self):
        source = self.root / 'team.json'
        for text in ('null', '[]', '{"schema":1,"schema":1,"roles":[]}', '{'):
            source.write_text(text)
            before = hbt.package_hashes(self.root)
            with self.assertRaises(SystemExit):
                hbt.read_team(str(source))
            self.assertEqual(hbt.package_hashes(self.root), before)

    def test_recorded_team_mismatch_blocks_resume_without_reinstall(self):
        rec = self.installed()
        rec['team'] = hbt.team_spec(self.tpl.roles[:1])
        hbt.save_record('creator', rec)
        before = hbt.package_hashes(self.root)
        with patch.object(hbt, 'cmd_install', side_effect=AssertionError('reinstall')), patch.object(hbt, 'say'):
            self.assertEqual(hbt.main(['setup', 'creator']), 1)
            with self.assertRaises(SystemExit):
                hbt.main(['configure', 'creator', '--projects', str(self.root / 'new'), '-y'])
        self.assertEqual(hbt.package_hashes(self.root), before)


if __name__ == '__main__':
    unittest.main()
