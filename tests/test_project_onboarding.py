"""Adaptive project layout: stdlib synthetic checks; no agent/provider launches."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

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
        self.calls, self.workspaces, self.panes = [], [], []

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
            return {'pane': self.add(parent['workspace_id'], args)}
        if args[:2] == ('pane', 'rename'):
            next(p for p in self.panes if p['pane_id'] == args[2])['label'] = args[3]
            return {}
        if args[:2] == ('pane', 'layout'):
            selected = next(p for p in self.panes if p['pane_id'] == args[-1])
            panes = [p for p in self.panes if p['workspace_id'] == selected['workspace_id']]
            return {'layout': {'workspace_id': selected['workspace_id'], 'zoomed': False,
                              'panes': [{'pane_id': p['pane_id'], 'rect': dict(x=x, y=y, width=79, height=24)}
                                        for p, (x, y) in zip(panes, [(0, 0), (80, 0), (0, 25), (80, 25)])]}}
        raise AssertionError('Unexpected mutation or agent launch: ' + repr(args))

    def add(self, workspace, args):
        p = {'pane_id': f'{workspace}:p{len(self.panes) + 1}', 'workspace_id': workspace,
             'cwd': args[args.index('--cwd') + 1]}
        self.panes.append(p)
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
                'engineer1': {'profile': 'builder-a', 'label': 'Builder one'},
                'engineer2': {'profile': 'builder-b', 'label': 'Builder two'},
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


if __name__ == '__main__':
    unittest.main()
