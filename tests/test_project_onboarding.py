"""Synthetic Herdr contract checks. Native layout proof is a separate sandbox run."""
import json
import tempfile
import unittest
from pathlib import Path

from test_installer import load, TPL

HELPER = TPL / 'workspace/skills/project-onboarding/scripts/onboard.py'


class HerdrDouble:
    def __init__(self):
        self.calls = []
        self.workspaces = []
        self.panes = []

    def __call__(self, *args):
        self.calls.append(args)
        if args == ('workspace', 'list'):
            return {'workspaces': self.workspaces}
        if args[:2] == ('pane', 'list'):
            return {'panes': self.panes}
        if args[:2] == ('workspace', 'create'):
            self.workspaces = [{'workspace_id': 'w7', 'label': args[args.index('--label') + 1]}]
            p = self.add_pane(args)
            return {'workspace': self.workspaces[0], 'root_pane': p}
        if args[:2] == ('pane', 'split'):
            return {'pane': self.add_pane(args)}
        if args[:2] == ('pane', 'rename'):
            next(p for p in self.panes if p['pane_id'] == args[2])['label'] = args[3]
            return {}
        if args[:2] == ('pane', 'layout'):
            positions = [(0, 0), (80, 0), (0, 25), (80, 25)]
            return {'layout': {'workspace_id': 'w7', 'tab_id': 'w7:t3', 'zoomed': False,
                               'panes': [{'pane_id': p['pane_id'],
                                          'rect': dict(x=x, y=y, width=79, height=24)}
                                         for p, (x, y) in zip(self.panes, positions)]}}
        raise AssertionError('Unexpected call, especially sends/start: ' + repr(args))

    def add_pane(self, args):
        p = {'pane_id': f'w7:p{10 + len(self.panes)}', 'workspace_id': 'w7',
             'tab_id': 'w7:t3', 'cwd': args[args.index('--cwd') + 1]}
        self.panes.append(p)
        return p


class Onboarding(unittest.TestCase):
    def test_safe_create_reuse_and_refusal(self):
        self.assertTrue(HELPER.is_file(), 'Working onboarding helper is missing')
        helper = load('hbt_onboard_test', HELPER)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ws = root / 'business'
            ws.mkdir()
            project = root / 'existing repo'
            project.mkdir()
            (project / 'AGENTS.md').write_text('Owner instructions')
            api = HerdrDouble()
            identity = {'socket': '/isolated/socket', 'inode': 42}
            rec = helper.onboard(ws, 'A Project', str(project), 'Ship a bounded fix', False, api, identity)
            self.assertEqual(list(rec['panes']), ['executive-assistant', 'cto', 'engineer1', 'engineer2'])
            self.assertEqual([c[2:5] for c in api.calls if c[:2] == ('pane', 'split')],
                             [('w7:p10', '--direction', 'right'),
                              ('w7:p10', '--direction', 'down'),
                              ('w7:p11', '--direction', 'down')])
            self.assertEqual(rec['profiles']['executive-assistant'], 'default')
            self.assertEqual(rec['profiles']['engineer1'], rec['profiles']['engineer2'])
            self.assertEqual(rec['profiles']['engineer2'], 'engineer')
            self.assertEqual((project / 'AGENTS.md').read_text(), 'Owner instructions')
            self.assertEqual(len(list(project.iterdir())), 1)
            mutations = [c for c in api.calls if c[1] in ('create', 'split', 'rename')]
            self.assertTrue(all('--no-focus' in c for c in mutations if c[1] != 'rename'))
            first = (ws / '.hbt-projects.json').read_bytes()
            api.calls.clear()
            again = helper.onboard(ws, 'A Project', None, None, False, api, identity)
            self.assertEqual(again, rec)
            self.assertEqual((ws / '.hbt-projects.json').read_bytes(), first)
            self.assertFalse(any(c[1] in ('create', 'split', 'rename') for c in api.calls))
            with self.assertRaisesRegex(ValueError, 'different'):
                helper.onboard(ws, 'A Project', str(root), None, False, api, identity)
            with self.assertRaisesRegex(ValueError, 'recorded'):
                helper.onboard(ws, 'Alias', str(project), 'Goal', False, api, identity)
            api.panes[0]['label'] = 'Owner changed this'
            with self.assertRaisesRegex(ValueError, 'changed'):
                helper.onboard(ws, 'A Project', None, None, False, api, identity)

    def test_changed_launch_or_old_layout_never_reuses_or_migrates(self):
        helper = load('hbt_onboard_receipts', HELPER)
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            project = ws / 'repo'
            project.mkdir()
            api = HerdrDouble()
            identity = {'socket': '/isolated/socket', 'inode': 42}
            rec = helper.onboard(ws, 'Project', str(project), 'Goal', False, api, identity)
            receipt = ws / '.hbt-projects.json'
            original = receipt.read_text()
            for field in ('launch', 'profiles'):
                state = json.loads(original)
                state['projects']['Project'][field]['executive-assistant'] = 'changed'
                receipt.write_text(json.dumps(state))
                before = receipt.read_bytes()
                api.calls.clear()
                with self.assertRaisesRegex(ValueError, 'launch|profile'):
                    helper.onboard(ws, 'Project', None, None, False, api, identity)
                self.assertEqual(receipt.read_bytes(), before)
                self.assertFalse(any(c[1] in ('create', 'split', 'rename') for c in api.calls))
            receipt.write_text(original)
            # Prior layout: engineer1 top-left, EA top-right, CTO bottom-left.
            by_id = {p['pane_id']: p for p in api.panes}
            api.panes = [by_id[rec['panes'][r]] for r in
                         ('engineer1', 'executive-assistant', 'cto', 'engineer2')]
            api.calls.clear()
            with self.assertRaisesRegex(ValueError, 'layout changed'):
                helper.onboard(ws, 'Project', None, None, False, api, identity)
            self.assertEqual(receipt.read_text(), original)
            self.assertFalse(any(c[1] in ('create', 'split', 'rename') for c in api.calls))

    def test_new_directory_partial_failure_and_foreign_layout_are_safe(self):
        helper = load('hbt_onboard_failures', HELPER)
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            identity = {'socket': '/isolated/socket', 'inode': 42}
            api = HerdrDouble()
            target = ws / 'new'
            with self.assertRaisesRegex(ValueError, 'Missing project'):
                helper.onboard(ws, 'New', str(target), 'Goal', False, api, identity)
            self.assertFalse(target.exists())
            rec = helper.onboard(ws, 'New', str(target), 'Goal', True, api, identity)
            self.assertEqual(list(target.iterdir()), [])
            self.assertTrue(all(len(v[3]) <= 32 for v in rec['launch'].values()))
            self.assertTrue(all(v[-4:-2] == ['-p', rec['profiles'][k]] for k, v in rec['launch'].items()))
            self.assertTrue(all(v[-2:] == ['--in', str(target)] for v in rec['launch'].values()))
            api.calls.clear()
            with self.assertRaisesRegex(ValueError, 'different server'):
                helper.onboard(ws, 'New', None, None, False, api, {'inode': 99})
            self.assertEqual(api.calls, [])
            foreign = HerdrDouble()
            foreign.workspaces = [{'workspace_id': 'w99', 'label': 'Existing'}]
            with self.assertRaisesRegex(ValueError, 'unrecorded'):
                helper.onboard(ws, 'Existing', str(ws / 'absent'), 'Goal', True, foreign, identity)
            self.assertFalse((ws / 'absent').exists())
            broken = HerdrDouble()
            def fail_after_create(*args):
                if args[:2] == ('pane', 'split'):
                    raise TimeoutError('Simulated ambiguous split failure')
                return broken(*args)
            with self.assertRaises(TimeoutError):
                helper.onboard(ws, 'Partial', str(ws / 'partial'), 'Goal', True, fail_after_create, identity)
            self.assertEqual(json.loads((ws / '.hbt-projects.json').read_text())['projects']['Partial']['status'], 'creating')
            broken.calls.clear()
            with self.assertRaisesRegex(ValueError, 'Interrupted'):
                helper.onboard(ws, 'Partial', None, None, False, broken, identity)
            self.assertEqual(broken.calls, [])
            with self.assertRaisesRegex(ValueError, 'control'):
                helper.onboard(ws, 'Unsafe\nname', str(ws), 'Goal', False, broken, identity)
            (ws / '.hbt-projects.json').unlink()
            sentinel = ws / 'sentinel'
            sentinel.write_text('owner data')
            (ws / '.hbt-projects.json').symlink_to(sentinel)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                helper.onboard(ws, 'Symlink', str(ws), 'Goal', False, broken, identity)
            self.assertEqual(sentinel.read_text(), 'owner data')


if __name__ == '__main__':
    unittest.main()
