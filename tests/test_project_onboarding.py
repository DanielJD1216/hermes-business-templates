"""Adaptive project layout: stdlib synthetic checks; no agent/provider launches."""
import copy
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'skills/project-onboarding/scripts/onboard.py'


def load_helper():
    spec = importlib.util.spec_from_file_location('project_onboard', HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HerdrDouble:
    def __init__(self):
        self.calls, self.workspaces, self.panes, self.rects = [], [], [], {}

    def __call__(self, *args):
        self.calls.append(args)
        if args == ('workspace', 'list'):
            return {'workspaces': self.workspaces}
        if args[:2] == ('pane', 'list'):
            return {'panes': [p for p in self.panes if '--workspace' not in args
                             or p['workspace_id'] == args[args.index('--workspace') + 1]]}
        if args[:2] == ('workspace', 'create'):
            w = {'workspace_id': f'w{len(self.workspaces) + 1}',
                 'label': args[args.index('--label') + 1]}
            self.workspaces.append(w)
            return {'workspace': w, 'root_pane': self.add(w['workspace_id'], args)}
        if args[:2] == ('pane', 'split'):
            parent = next(p for p in self.panes if p['pane_id'] == args[2])
            child = self.add(parent['workspace_id'], args)
            rect = self.rects[parent['pane_id']]
            direction = args[args.index('--direction') + 1]
            axis, size = ('x', 'width') if direction == 'right' else ('y', 'height')
            extent = int((rect[size] - 1) * float(args[args.index('--ratio') + 1]))
            other = dict(rect)
            other[axis] += extent + 1
            other[size] -= extent + 1
            rect[size] = extent
            self.rects[child['pane_id']] = other
            return {'pane': child}
        if args[:2] == ('pane', 'rename'):
            next(p for p in self.panes if p['pane_id'] == args[2])['label'] = args[3]
            return {}
        if args[:2] == ('pane', 'process-info'):
            return {'process_info': {'foreground_processes': [{'pid': 123, 'argv': ['PRIVATE', '--token=DO-NOT-PRINT']}]}}
        if args[:2] == ('pane', 'layout'):
            selected = next(p for p in self.panes if p['pane_id'] == args[-1])
            panes = [p for p in self.panes if p['workspace_id'] == selected['workspace_id']]
            return {'layout': {'workspace_id': selected['workspace_id'], 'zoomed': False,
                              'panes': [{'pane_id': p['pane_id'], 'rect': self.rects[p['pane_id']]}
                                        for p in panes]}}
        raise AssertionError('Unexpected mutation or agent launch: ' + repr(args))

    def add(self, workspace, args):
        p = {'pane_id': f'{workspace}:p{len(self.panes) + 1}', 'workspace_id': workspace,
             'cwd': args[args.index('--cwd') + 1]}
        self.panes.append(p)
        self.rects[p['pane_id']] = dict(x=0, y=0, width=159, height=49)
        return p


class Onboarding(unittest.TestCase):
    def test_adaptive_project_creation_and_repeat(self):
        self.assertTrue(HELPER.is_file(), 'Published standalone onboarding helper is missing')
        helper = load_helper()
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            ws = Path(tmp) / 'work'; ws.mkdir()
            home = Path(tmp) / 'hermes'; home.mkdir()
            roles = {
                'executive-assistant': {'profile': 'default', 'label': 'Existing assistant'},
                'cto': {'profile': 'tech-lead', 'label': 'Architecture'},
                'engineer1': {'profile': 'engineer', 'label': 'Builder one'},
                'engineer2': {'profile': 'engineer', 'label': 'Builder two'},
            }
            for entry in roles.values():
                p = home if entry['profile'] == 'default' else home / 'profiles' / entry['profile']
                p.mkdir(parents=True, exist_ok=True)
                (p / 'config.yaml').write_text('model: {}\n')
                (p / 'SOUL.md').write_text('Synthetic existing identity, preserve me')
            project = ws / 'existing repo'; project.mkdir()
            (project / 'AGENTS.md').write_text('Owner project instructions')
            api = HerdrDouble()
            identity = {'socket': '/isolated/socket', 'inode': 42, 'device': 1}
            rec = helper.onboard(ws, 'Sample Project', str(project), 'Review a bounded change', False,
                                 api, identity, roles, home)
            self.assertEqual(rec['status'], 'layout-ready')
            self.assertEqual(rec['roles'], roles)
            self.assertEqual([p['label'] for p in api.panes], [r['label'] for r in roles.values()])
            self.assertEqual([c[c.index('--direction') + 1] for c in api.calls if c[:2] == ('pane', 'split')],
                             ['right', 'down', 'down'])
            self.assertEqual((home / 'SOUL.md').read_text(), 'Synthetic existing identity, preserve me')
            self.assertEqual((project / 'AGENTS.md').read_text(), 'Owner project instructions')
            self.assertEqual(list(project.iterdir()), [project / 'AGENTS.md'])
            for role, command in rec['launch'].items():
                self.assertEqual(command[-4:], ['-p', roles[role]['profile'], '--in', str(project)])
            self.assertEqual(len({r['profile'] for r in rec['roles'].values()}), 3)
            self.assertNotEqual(rec['panes']['engineer1'], rec['panes']['engineer2'])
            self.assertNotEqual(rec['launch']['engineer1'][3], rec['launch']['engineer2'][3])
            self.assertTrue(all('--continue' not in c and '--resume' not in c
                                for c in rec['launch'].values()))
            receipt = ws / '.hbt-projects.json'
            first = receipt.read_bytes()
            mutations = [c for c in api.calls if c[1] in ('create', 'split')]
            self.assertTrue(all('--no-focus' in c for c in mutations))
            api.calls.clear()
            self.assertEqual(helper.onboard(ws, 'Sample Project', None, None, False,
                                            api, identity, roles, home), rec)
            self.assertEqual(receipt.read_bytes(), first)
            self.assertFalse(any(c[1] in ('create', 'split', 'rename') for c in api.calls))

            # Distinct projects reuse the selected role mapping, not the first workspace.
            second = helper.onboard(ws, 'Second', str(ws / 'new'), 'Another goal', True,
                                    api, identity, roles, home)
            self.assertNotEqual(second['workspace_id'], rec['workspace_id'])
            self.assertEqual(len(api.panes), 8)
            self.assertEqual(list((ws / 'new').iterdir()), [])

            for bad in [None, {}, {**roles, 'extra': roles['cto']}]:
                with self.subTest(role_map=bad):
                    api.calls.clear()
                    with self.assertRaises(ValueError):
                        helper.onboard(ws, 'Invalid', str(ws / 'absent'), 'Goal', True,
                                       api, identity, bad, home)
                    self.assertEqual(api.calls, [])
                    self.assertFalse((ws / 'absent').exists())
            for slot, alias in [('cto', 'default'), ('engineer1', 'default'),
                                ('engineer2', 'default'), ('engineer1', 'tech-lead'),
                                ('engineer2', 'tech-lead')]:
                invalid = copy.deepcopy(roles); invalid[slot]['profile'] = alias
                with self.subTest(slot=slot, alias=alias), self.assertRaisesRegex(ValueError, 'distinct'):
                    helper.validate_roles(invalid, home)
            distinct = copy.deepcopy(roles); distinct['engineer2']['profile'] = 'second-engineer'
            other = home / 'profiles/second-engineer'; other.mkdir()
            (other / 'config.yaml').write_text('model: {}\n')
            self.assertEqual(helper.validate_roles(distinct, home)[0], distinct)
            for bad_profile in ['../escape', 'BadCase', '--flag', '', None]:
                invalid = copy.deepcopy(roles); invalid['cto']['profile'] = bad_profile
                with self.subTest(profile=bad_profile), self.assertRaises(ValueError):
                    helper.onboard(ws, 'Invalid', str(ws / 'absent'), 'Goal', True,
                                   api, identity, invalid, home)
            invalid = copy.deepcopy(roles); invalid['cto']['profile'] = 'missing'
            with self.assertRaisesRegex(ValueError, 'missing'):
                helper.onboard(ws, 'Invalid', None, None, False, api, identity, invalid, home)
            tombstone = home / 'profiles/.deleted/tech-lead'
            tombstone.parent.mkdir(); tombstone.write_text('Deleted identity')
            with self.assertRaisesRegex(ValueError, 'deleted'):
                helper.onboard(ws, 'Invalid', None, None, False, api, identity, roles, home)
            tombstone.unlink()  # Synthetic marker owned by this test only.

            stable = receipt.read_bytes()
            changed = copy.deepcopy(roles); changed['cto']['label'] = 'Different'
            api.calls.clear()
            with self.assertRaisesRegex(ValueError, 'changed'):
                helper.onboard(ws, 'Sample Project', None, None, False, api, identity, changed, home)
            with self.assertRaisesRegex(ValueError, 'different server'):
                helper.onboard(ws, 'Sample Project', None, None, False, api, {'inode': 99}, roles, home)
            self.assertEqual(api.calls, [])
            self.assertEqual(receipt.read_bytes(), stable)

            state = json.loads(stable)
            state['projects']['Sample Project']['launch']['cto'] = ['wrong']
            receipt.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, 'changed'):
                helper.onboard(ws, 'Sample Project', None, None, False, api, identity, roles, home)
            receipt.write_bytes(stable)
            def fail_split(*args):
                if args[:2] == ('pane', 'split'):
                    raise TimeoutError('Ambiguous native outcome')
                return api(*args)
            with self.assertRaises(TimeoutError):
                helper.onboard(ws, 'Partial', str(ws / 'partial'), 'Goal', True,
                               fail_split, identity, roles, home)
            partial = receipt.read_bytes()
            api.calls.clear()
            with self.assertRaisesRegex(ValueError, 'Interrupted'):
                helper.onboard(ws, 'Partial', None, None, False, api, identity, roles, home)
            self.assertEqual(api.calls, [])
            self.assertEqual(receipt.read_bytes(), partial)
            with self.assertRaisesRegex(ValueError, 'recorded'):
                helper.onboard(ws, 'Alias', str(project), 'Goal', False, api, identity, roles, home)
            with self.assertRaisesRegex(ValueError, 'Missing project'):
                helper.onboard(ws, 'Absent', str(ws / 'absent'), 'Goal', False, api, identity, roles, home)
            self.assertFalse((ws / 'absent').exists())
            foreign = HerdrDouble(); foreign.workspaces = [{'workspace_id': 'w99', 'label': 'Foreign'}]
            with self.assertRaisesRegex(ValueError, 'unrecorded'):
                helper.onboard(ws, 'Foreign', str(ws / 'foreign'), 'Goal', True,
                               foreign, identity, roles, home)
            self.assertFalse((ws / 'foreign').exists())
            receipt.unlink(); sentinel = ws / 'owner-data'; sentinel.write_text('Preserve')
            receipt.symlink_to(sentinel)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                helper.onboard(ws, 'Symlink', None, None, False, api, identity, roles, home)
            self.assertEqual(sentinel.read_text(), 'Preserve')


class Recovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name)
        self.home = self.ws / 'hermes'; self.home.mkdir()
        self.roles = {slot: {'profile': profile, 'label': slot} for slot, profile in
                      zip(('executive-assistant', 'cto', 'engineer1', 'engineer2'),
                          ('default', 'architect', 'engineer', 'engineer'))}
        for entry in self.roles.values():
            p = self.home if entry['profile'] == 'default' else self.home / 'profiles' / entry['profile']
            p.mkdir(parents=True, exist_ok=True)
            (p / 'config.yaml').write_text('model: {}\n')
        self.project = self.ws / 'project'; self.project.mkdir()
        self.helper, self.api = load_helper(), HerdrDouble()
        self.identity = {'socket': '/synthetic/socket', 'inode': 42, 'device': 1}
        self.rec = self.helper.onboard(self.ws, 'Project', str(self.project), 'Goal', False,
                                       self.api, self.identity, self.roles, self.home)
        self.receipt = self.ws / '.hbt-projects.json'
        self.lock = self.ws / '.hbt-projects.lock'
        self.state = json.loads(self.receipt.read_text())
        self.rec = self.state['projects']['Project']
        self.api.calls.clear()

    def pending(self):
        self.rec['status'] = 'creating'
        self.rec.pop('layout', None); self.rec.pop('launch', None)
        self.rec['journal'] = ['preserve original evidence']
        self.receipt.write_text(json.dumps(self.state))
        self.lock.unlink(missing_ok=True)

    def call(self, **kwargs):
        return self.helper.onboard(self.ws, 'Project', None, None, False, self.api,
                                   self.identity, self.roles, self.home, **kwargs)

    def snapshot(self):
        return {str(p.relative_to(self.ws)): p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}

    def assert_read_only(self):
        self.assertTrue(all(c[:2] in [('workspace', 'list'), ('pane', 'list'),
                                     ('pane', 'layout'), ('pane', 'process-info')] for c in self.api.calls))

    def cli(self, *flags, env=None):
        roles_file = self.ws / 'roles.json'
        roles_file.write_text(json.dumps(self.roles))
        argv = ['onboard.py', '--workspace', str(self.ws), '--name', 'Project',
                '--roles', str(roles_file), '--hermes-root', str(self.home), *flags]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, 'argv', argv), mock.patch.dict(os.environ, env or {}, clear=True), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                self.helper.main()
                code = 0
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_profile_directory_aliases_cannot_bypass_role_separation(self):
        for name, target in [('architect', self.home), ('engineer', self.home / 'profiles/architect')]:
            path = self.home / 'profiles' / name
            saved = path.with_name(name + '-saved')
            path.rename(saved)
            path.symlink_to(target, target_is_directory=True)
            try:
                with self.subTest(profile=name), self.assertRaisesRegex(ValueError, 'distinct'):
                    self.call(inspect=True)
                self.assertEqual(self.api.calls, [])
            finally:
                path.unlink()
                saved.rename(path)

    def test_opaque_native_ids_survive_inspection_and_finalization(self):
        self.pending()
        self.rec['workspace_id'] = 'w1N'
        self.rec['panes'] = {slot: pid.replace('w1:', 'w1N:')
                             for slot, pid in self.rec['panes'].items()}
        self.api.workspaces[0]['workspace_id'] = 'w1N'
        for pane in self.api.panes:
            pane['workspace_id'] = 'w1N'
            pane['pane_id'] = pane['pane_id'].replace('w1:', 'w1N:')
        self.api.rects = {pid.replace('w1:', 'w1N:'): rect for pid, rect in self.api.rects.items()}
        self.receipt.write_text(json.dumps(self.state))
        self.assertEqual(self.call(inspect=True)['layout_status'], 'verified')
        result = self.call(finalize=True)
        self.assertEqual(result['panes'], self.rec['panes'])
        self.assertEqual(result['workspace_id'], 'w1N')
        self.assert_read_only()

    def test_cli_modes_and_context_guards(self):
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=AssertionError('No native calls')):
            for mode in ([], ['--inspect'], ['--finalize']):
                code, _, err = self.cli(*mode)
                self.assertEqual(code, 2)
                self.assertIn('authorized Herdr pane', err)
            code, _, err = self.cli('--inspect', '--finalize')
            self.assertEqual(code, 2)
            self.assertIn('not allowed', err)
            code, _, err = self.cli('--inspect', env={'HERDR_ENV': '1', 'HERDR_SOCKET_PATH': str(self.ws / 'missing')})
            self.assertEqual(code, 1)
            self.assertIn('endpoint', err)
            code, _, err = self.cli('--inspect', env={'HERDR_ENV': '1', 'HERDR_SOCKET_PATH': str(self.receipt)})
            self.assertEqual(code, 1)
            self.assertIn('Unix socket', err)
            code, out, _ = self.cli('--help')
            self.assertEqual(code, 0)
            self.assertIn('--inspect', out)
            self.assertIn('--finalize', out)

    def test_cli_inspect_and_finalize_use_only_synthetic_reads(self):
        self.pending()
        socket_file = self.ws / 'fake-socket'; socket_file.touch()
        info = socket_file.stat()
        self.rec['endpoint'] = {'socket': str(socket_file), 'inode': info.st_ino, 'device': info.st_dev}
        self.receipt.write_text(json.dumps(self.state))
        env = {'HERDR_ENV': '1', 'HERDR_SOCKET_PATH': str(socket_file)}
        def native(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, json.dumps({'result': self.api(*argv[1:])}), '')
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=native), \
                mock.patch.object(self.helper.stat, 'S_ISSOCK', return_value=True):
            before = self.receipt.read_bytes()
            code, out, err = self.cli('--inspect', env=env)
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(json.loads(out)['layout_status'], 'verified')
            self.assertEqual(self.receipt.read_bytes(), before)
            self.assertFalse(self.lock.exists())
            code, out, err = self.cli('--finalize', env=env)
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(json.loads(out)['status'], 'layout-ready')
        self.assert_read_only()

    def test_native_errors_retain_stage_exit_code_and_redact(self):
        message = 'split failed api_key=TOPSECRET password="OTHER SECRET" Authorization: Bearer BEARERSECRET'
        response = json.dumps({'error': {'code': 'invalid_pane', 'message': message, 'data': 'PRIVATE DATA'}})
        for returncode, stdout, stderr in [(7, 'PRIVATE STDOUT', response), (0, response, ''),
                                            (2, '', 'PRIVATE STDERR'), (0, 'PRIVATE INVALID JSON', '')]:
            with self.subTest(returncode=returncode, stdout=stdout):
                with mock.patch.object(self.helper.subprocess, 'run', return_value=
                                       subprocess.CompletedProcess(['SECRET COMMAND'], returncode, stdout, stderr)) as native:
                    with self.assertRaises(ValueError) as caught:
                        self.helper.native_api('pane', 'split', 'SECRET ARG')
                text = str(caught.exception)
                self.assertIn('pane split', text)
                self.assertIn('exit=' + str(returncode), text)
                if response in (stdout, stderr):
                    self.assertIn('invalid_pane', text)
                    self.assertIn('split failed', text)
                for secret in ('TOPSECRET', 'OTHER SECRET', 'BEARERSECRET', 'PRIVATE', 'SECRET ARG', 'SECRET COMMAND'):
                    self.assertNotIn(secret, text)
                self.assertLess(len(text), 800)
                self.assertEqual(native.call_count, 1)
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=
                               subprocess.TimeoutExpired(['SECRET COMMAND'], 30, output='PRIVATE', stderr=response)) as native:
            with self.assertRaisesRegex(ValueError, 'pane split.*timeout') as caught:
                self.helper.native_api('pane', 'split', 'SECRET ARG')
            self.assertNotIn('SECRET', str(caught.exception))
            self.assertEqual(native.call_count, 1)

    def test_finalize_rereads_under_lock_and_inspection_never_locks(self):
        self.pending()
        self.lock.write_bytes(b'existing lock sentinel')
        before = self.snapshot()
        with mock.patch.object(self.helper.fcntl, 'flock', side_effect=AssertionError('Inspection locked')):
            self.call(inspect=True)
        self.assertEqual(before, self.snapshot())
        self.api.calls.clear()
        def changed_at_lock(*args):
            self.rec['roles']['cto']['label'] = 'changed after initial read'
            self.receipt.write_text(json.dumps(self.state))
        with mock.patch.object(self.helper.fcntl, 'flock', side_effect=changed_at_lock) as locked:
            with self.assertRaisesRegex(ValueError, 'changed'):
                self.call(finalize=True)
        locked.assert_called_once()
        self.assertEqual(self.api.calls, [])
        self.assertEqual(json.loads(self.receipt.read_text()), self.state)

    def test_inspect_refuses_bad_receipt_or_endpoint_without_writes(self):
        self.pending()
        original = copy.deepcopy(self.rec)
        for key, value in [('roles', {}), ('endpoint', {'inode': 99}), ('panes', []),
                           ('goal', None), ('path', 'relative'), ('status', 'invalid')]:
            with self.subTest(field=key):
                self.state['projects']['Project'] = {**original, key: value}
                self.receipt.write_text(json.dumps(self.state))
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.call(inspect=True)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.api.calls, [])
                self.assertFalse(self.lock.exists())

    def test_inspect_changed_metadata_does_not_read_processes(self):
        self.pending()
        self.api.panes[0]['cwd'] = '/someone-else'
        report = self.call(inspect=True)
        self.assertEqual(report['layout_status'], 'changed')
        self.assertIsNone(report['panes']['executive-assistant']['process_exists'])
        self.assertNotIn(('pane', 'process-info', '--pane', 'w1:p1'), self.api.calls)
        self.api.calls.clear()
        self.api.workspaces[0]['label'] = 'someone else'
        report = self.call(inspect=True)
        self.assertEqual(report['layout_status'], 'unknown')
        self.assertEqual(self.api.calls, [('workspace', 'list')])

    def test_lost_workspace_response_does_not_discover_or_adopt_ids(self):
        def lost(*args):
            result = self.api(*args)
            if args[:2] == ('workspace', 'create'):
                raise TimeoutError('response lost')
            return result
        with self.assertRaises(TimeoutError):
            self.helper.onboard(self.ws, 'Lost', str(self.ws / 'lost'), 'Goal', True,
                                lost, self.identity, self.roles, self.home)
        self.api.calls.clear()
        before = self.receipt.read_bytes()
        report = self.helper.onboard(self.ws, 'Lost', None, None, False, self.api,
                                     self.identity, self.roles, self.home, inspect=True)
        self.assertEqual(report['layout_status'], 'unknown')
        for options in ({}, {'finalize': True}):
            with self.assertRaises(ValueError):
                self.helper.onboard(self.ws, 'Lost', None, None, False, self.api,
                                    self.identity, self.roles, self.home, **options)
        self.assertEqual(self.api.calls, [])
        self.assertEqual(self.receipt.read_bytes(), before)

    def test_inspection_metadata_absence_is_unknown_not_readiness(self):
        native = self.api
        for process_info in (None, {}, {'foreground_processes': None}):
            def missing(*args):
                if args[:2] == ('pane', 'process-info'):
                    return {'process_info': process_info}
                return native(*args)
            with mock.patch.object(self, 'api', missing):
                report = self.call(inspect=True)
            self.assertTrue(all(p['process_exists'] is None for p in report['panes'].values()))
            self.assertTrue(all(p['hermes_recognized'] is None for p in report['panes'].values()))
            self.assertEqual(report['readiness'], 'not-verified')

    def test_inspect_native_failure_does_not_claim_changed_layout(self):
        native = self.api
        def failure(*args):
            if args[:2] == ('pane', 'layout'):
                raise self.helper.ApiError('pane layout', 'exit=7', {'code': 'unavailable', 'message': 'Try later'})
            return native(*args)
        with mock.patch.object(self, 'api', failure):
            with self.assertRaisesRegex(self.helper.ApiError, 'pane layout.*exit=7.*unavailable'):
                self.call(inspect=True)

    def test_finalize_rejects_missing_ready_launch_and_malformed_layout(self):
        for key, value in [('launch', None), ('layout', []), ('layout', {'panes': []})]:
            state = copy.deepcopy(self.state)
            if value is None:
                state['projects']['Project'].pop(key)
            else:
                state['projects']['Project'][key] = value
            self.receipt.write_text(json.dumps(state))
            before = self.receipt.read_bytes()
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.call(finalize=True)
            self.assertEqual(self.receipt.read_bytes(), before)

    def test_redaction_bounds_credentials_and_native_os_errors(self):
        message = 'failed --token TOPSECRET; token="' + 'OTHERSECRET ' * 2000
        payload = json.dumps({'error': {'code': 'failed', 'message': message}})
        with mock.patch.object(self.helper.subprocess, 'run', return_value=
                               subprocess.CompletedProcess([], 0, payload, '')):
            with self.assertRaises(ValueError) as caught:
                self.helper.native_api('pane', 'split')
        self.assertNotIn('TOPSECRET', str(caught.exception))
        self.assertNotIn('OTHERSECRET', str(caught.exception))
        self.assertLess(len(str(caught.exception)), 800)
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=FileNotFoundError(2, 'PRIVATE')):
            with self.assertRaisesRegex(ValueError, 'pane split.*errno=2') as caught:
                self.helper.native_api('pane', 'split')
        self.assertNotIn('PRIVATE', str(caught.exception))

    def test_finalize_complete_pending_preserves_journal(self):
        self.pending()
        result = self.call(finalize=True)
        self.assertEqual(result['status'], 'layout-ready')
        self.assertEqual(result['prior_status'], 'creating')
        self.assertEqual(result['journal'], ['preserve original evidence'])
        self.assertEqual(result['launch'], self.helper.launch_commands(result))
        self.assertEqual(json.loads(self.receipt.read_text())['projects']['Project'], result)
        self.assert_read_only()
        before = self.snapshot()
        self.assertEqual(self.call(finalize=True), result)
        self.assertEqual(self.snapshot(), before)

    def test_finalize_refuses_changed_or_incomplete_receipts(self):
        self.pending()
        original = copy.deepcopy(self.rec)
        changes = [('roles', {}), ('endpoint', {'inode': 99}), ('panes', {}),
                   ('panes', {**original['panes'], 'engineer2': original['panes']['engineer1']}),
                   ('panes', {**original['panes'], 'engineer2': 'unknown'}),
                   ('workspace_id', 'w99'), ('status', 'unexpected'), ('path', 'relative'),
                   ('launch', {'cto': ['unapproved']}), ('name', 'Another')]
        for key, value in changes:
            with self.subTest(field=key, value=value):
                self.state['projects']['Project'] = {**original, key: value}
                self.receipt.write_text(json.dumps(self.state))
                before = self.receipt.read_bytes()
                self.api.calls.clear()
                with self.assertRaises(ValueError):
                    self.call(finalize=True)
                self.assertEqual(self.receipt.read_bytes(), before)
                self.assertEqual(self.api.calls, [])
        for malformed in [[], {'version': 1, 'projects': {}}, {'version': 2, 'projects': {'Project': None}}]:
            self.receipt.write_text(json.dumps(malformed))
            with self.assertRaises(ValueError):
                self.call(finalize=True)
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError, 'receipt'):
            self.call(finalize=True)
        self.assertFalse(self.receipt.exists())

    def test_finalize_rejects_changed_native_layout_without_writes(self):
        self.pending()
        panes, rects = copy.deepcopy(self.api.panes), copy.deepcopy(self.api.rects)
        for change in ('label', 'cwd', 'missing', 'extra', 'duplicate', 'width', 'height', 'direction'):
            with self.subTest(change=change):
                self.api.panes, self.api.rects = copy.deepcopy(panes), copy.deepcopy(rects)
                if change in ('label', 'cwd'):
                    self.api.panes[0][change] = 'changed'
                elif change == 'missing':
                    self.api.panes.pop()
                elif change in ('extra', 'duplicate'):
                    extra = dict(self.api.panes[0])
                    if change == 'extra':
                        extra['pane_id'] = 'w1:p99'
                    self.api.panes.append(extra)
                elif change in ('width', 'height'):
                    self.api.rects['w1:p1'][change] = 1000
                else:
                    self.api.rects['w1:p3']['y'] = 0
                before = self.receipt.read_bytes()
                with self.assertRaises(ValueError):
                    self.call(finalize=True)
                self.assertEqual(self.receipt.read_bytes(), before)
                self.assert_read_only()

    def test_lost_final_rename_response_can_finalize_without_repeating_mutation(self):
        def lost(*args):
            result = self.api(*args)
            if args[:2] == ('pane', 'rename') and args[-1] == self.roles['engineer2']['label']:
                raise TimeoutError('final rename applied, response lost')
            return result
        with self.assertRaises(TimeoutError):
            self.helper.onboard(self.ws, 'Lost', str(self.ws / 'lost'), 'Goal', True,
                                lost, self.identity, self.roles, self.home)
        pending = json.loads(self.receipt.read_text())['projects']['Lost']
        self.assertEqual(pending['status'], 'creating')
        self.assertEqual(len(pending['panes']), 4)
        self.api.calls.clear()
        result = self.helper.onboard(self.ws, 'Lost', None, None, False, self.api,
                                     self.identity, self.roles, self.home, finalize=True)
        self.assertEqual(result['status'], 'layout-ready')
        self.assertEqual(result['prior_status'], 'creating')
        self.assert_read_only()

    def test_response_lost_after_split_blocks_replay_and_finalize(self):
        native = self.api
        def lost(*args):
            result = native(*args)
            if args[:2] == ('pane', 'split'):
                raise TimeoutError('response lost after successful mutation')
            return result
        with self.assertRaises(TimeoutError):
            self.helper.onboard(self.ws, 'Lost', str(self.ws / 'lost'), 'Goal', True,
                                lost, self.identity, self.roles, self.home)
        before = self.receipt.read_bytes()
        native.calls.clear()
        for options in ({}, {'finalize': True}):
            with self.assertRaises(ValueError):
                self.helper.onboard(self.ws, 'Lost', None, None, False, native,
                                    self.identity, self.roles, self.home, **options)
        self.assertEqual(native.calls, [])
        report = self.helper.onboard(self.ws, 'Lost', None, None, False, native,
                                     self.identity, self.roles, self.home, inspect=True)
        self.assertEqual(report['unrecorded_pane_count'], 1)
        self.assertEqual(report['layout_status'], 'incomplete')
        self.assertEqual(self.receipt.read_bytes(), before)
        self.assert_read_only()

    def test_inspect_pending_is_read_only_and_filters_metadata(self):
        self.pending()
        self.api.panes[0].update(agent='hermes', agent_status='blocked',
                                 tokens={'secret': 'DO-NOT-PRINT'}, title='PRIVATE CONVERSATION')
        self.api.workspaces.append({'workspace_id': 'foreign', 'label': 'PRIVATE WORKSPACE'})
        self.api.panes.append({'pane_id': 'foreign:p1', 'workspace_id': 'foreign', 'cwd': '/private'})
        before = self.snapshot()
        report = self.call(inspect=True)
        self.assertEqual(report['receipt_status'], 'creating')
        self.assertEqual(report['layout_status'], 'verified')
        self.assertEqual(report['panes']['executive-assistant']['recognized_state'], 'blocked')
        self.assertTrue(report['panes']['executive-assistant']['process_exists'])
        self.assertEqual(report['readiness'], 'not-verified')
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.lock.exists())
        self.assert_read_only()
        self.assertNotIn('PRIVATE', json.dumps(report))
        self.assertNotIn('DO-NOT-PRINT', json.dumps(report))

    def test_inspect_partial_and_missing_receipt_never_adopts(self):
        self.pending()
        self.rec['panes'].pop('engineer2')
        self.receipt.write_text(json.dumps(self.state))
        before = self.snapshot()
        report = self.call(inspect=True)
        self.assertEqual(report['layout_status'], 'incomplete')
        self.assertEqual(report['unrecorded_pane_count'], 1)
        self.assertNotIn('engineer2', report['panes'])
        self.assertEqual(before, self.snapshot())
        self.assert_read_only()
        self.api.calls.clear()
        self.rec.pop('workspace_id')
        self.rec['panes'] = {}
        self.receipt.write_text(json.dumps(self.state))
        self.assertEqual(self.call(inspect=True)['layout_status'], 'unknown')
        self.assertEqual(self.api.calls, [])
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError, 'receipt'):
            self.call(inspect=True)
        self.assertFalse(self.receipt.exists())
        self.assertFalse(self.lock.exists())


if __name__ == '__main__':
    unittest.main()
