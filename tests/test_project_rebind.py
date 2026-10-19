"""Receipt-only recovery after endpoint replacement; no live Herdr operations."""
import hashlib
import copy
import json
from pathlib import Path
import unittest
from unittest import mock

import test_project_control_route as control_tests


class Rebind(unittest.TestCase):
    def setUp(self):
        self.fx = control_tests.ControlRoute()
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.fx.prepare_endpoint()
        self.current = dict(self.fx.rec['endpoint'])
        self.fx.rec['endpoint']['inode'] += 1  # A prior incarnation at the same path.
        self.previous = dict(self.fx.rec['endpoint'])
        self.fx.state['projects']['Unrelated'] = {'owner_data': 'preserve'}
        self.fx.receipt.write_text(json.dumps(self.fx.state))
        self.original = self.fx.receipt.read_bytes()
        self.backups = self.fx.ws / 'backups'
        self.backups.mkdir(mode=0o700)

    def run_rebind(self, *extra):
        with mock.patch.object(self.fx.helper.subprocess, 'run', side_effect=self.fx.native):
            return self.fx.cli('--session', 'sandbox', '--rebind',
                               '--backup-dir', str(self.backups), *extra)

    def test_same_path_restart_rebinds_only_endpoint_and_preserves_backup(self):
        code, out, err = self.run_rebind()
        self.assertEqual((code, err), (0, ''))
        report = json.loads(out)
        self.assertEqual(report['binding_status'], 'rebound')
        self.assertEqual(report['readiness'], 'not-verified')
        state = json.loads(self.fx.receipt.read_text())
        record = state['projects']['Project']
        audit = record.pop('endpoint_rebindings')
        self.assertEqual(record, {**self.fx.rec, 'endpoint': self.current})
        self.assertEqual(state['projects']['Unrelated'], {'owner_data': 'preserve'})
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]['previous'], self.previous)
        self.assertEqual(audit[0]['current'], self.current)
        self.assertEqual(audit[0]['receipt_sha256'], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(Path(audit[0]['backup']).read_bytes(), self.original)
        self.assertEqual(Path(audit[0]['backup']).stat().st_mode & 0o777, 0o600)
        self.assertTrue(all(c[:2] in [('workspace', 'list'), ('pane', 'list'), ('pane', 'layout')]
                            for c in self.fx.api.calls))
        before = self.fx.receipt.read_bytes()
        code, out, err = self.run_rebind()
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['binding_status'], 'unchanged')
        self.assertEqual(self.fx.receipt.read_bytes(), before)
        self.assertEqual(len(list(self.backups.iterdir())), 1)


    def test_other_modes_still_refuse_changed_endpoint(self):
        for flags in [[], ['--inspect'], ['--finalize']]:
            with self.subTest(flags=flags), mock.patch.object(
                    self.fx.helper.subprocess, 'run', side_effect=self.fx.native):
                code, _, err = self.fx.cli('--session', 'sandbox', *flags)
                self.assertEqual(code, 1)
                self.assertIn('different server', err)
        self.assertEqual(self.fx.receipt.read_bytes(), self.original)
        self.assertEqual(self.fx.api.calls, [])

    def resize(self, width=60, height=20):
        for slot, (x, y) in zip(self.fx.helper.SLOTS, ((0, 0), (1, 0), (0, 1), (1, 1))):
            self.fx.api.rects[self.fx.rec['panes'][slot]] = {
                'x': x * width, 'y': y * height, 'width': width, 'height': height}

    def test_resize_rebind_preserves_identity_and_audits_both_layouts(self):
        for row in self.fx.rec['layout']['panes']:
            rect = row['rect']
            right, bottom = rect['x'] > 0, rect['y'] > 0
            row['rect'] = {'x': 40 if right else 0, 'y': 25 if bottom else 0,
                           'width': 38 if right else 39, 'height': 24}
        self.fx.receipt.write_text(json.dumps(self.fx.state))
        self.original = self.fx.receipt.read_bytes()
        self.resize()
        code, out, err = self.run_rebind()
        self.assertEqual((code, err), (0, ''))
        report = json.loads(out)
        self.assertEqual(report['geometry_status'], 'updated')
        record = json.loads(self.fx.receipt.read_text())['projects']['Project']
        event, = record.pop('endpoint_rebindings')
        self.assertEqual(event['previous_layout'], self.fx.rec['layout'])
        self.assertEqual(event['current_layout'], record['layout'])
        self.assertEqual(record, {**self.fx.rec, 'endpoint': self.current, 'layout': record['layout']})
        self.assertEqual(Path(event['backup']).read_bytes(), self.original)
        self.assertTrue(all(c[:2] in [('workspace', 'list'), ('pane', 'list'), ('pane', 'layout')]
                            for c in self.fx.api.calls))
        before = self.fx.receipt.read_bytes()
        self.assertEqual(self.run_rebind()[0], 0)
        self.assertEqual(self.fx.receipt.read_bytes(), before)
        with mock.patch.object(self.fx.helper.subprocess, 'run', side_effect=self.fx.native):
            code, out, err = self.fx.cli('--session', 'sandbox', '--inspect')
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['layout_status'], 'verified')
        self.assertEqual(json.loads(out)['readiness'], 'not-verified')

    def test_same_endpoint_resize_is_not_mistaken_for_noop(self):
        self.fx.rec['endpoint'] = self.current
        self.fx.receipt.write_text(json.dumps(self.fx.state))
        original = self.fx.receipt.read_bytes()
        self.resize()
        with mock.patch.object(self.fx.helper.subprocess, 'run', side_effect=self.fx.native):
            self.assertEqual(self.fx.cli('--session', 'sandbox', '--finalize')[0], 1)
        self.assertEqual(self.fx.receipt.read_bytes(), original)
        code, out, err = self.run_rebind()
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['binding_status'], 'unchanged')
        self.assertEqual(json.loads(out)['geometry_status'], 'updated')
        self.assertEqual(next(self.backups.iterdir()).read_bytes(), original)

    def test_resize_rejects_corrupt_history_and_changed_positions(self):
        self.resize()
        for source in ('recorded', 'current'):
            with self.subTest(source=source):
                state = copy.deepcopy(self.fx.state)
                rects = (state['projects']['Project']['layout']['panes'] if source == 'recorded'
                         else [{'rect': r} for r in self.fx.api.rects.values()])
                rects[0]['rect'], rects[1]['rect'] = rects[1]['rect'], rects[0]['rect']
                if source == 'current':
                    for pid, row in zip(self.fx.api.rects, rects):
                        self.fx.api.rects[pid] = row['rect']
                self.fx.receipt.write_text(json.dumps(state))
                before = self.fx.receipt.read_bytes()
                self.assertEqual(self.run_rebind()[0], 1)
                self.assertEqual(self.fx.receipt.read_bytes(), before)
                self.assertEqual(list(self.backups.iterdir()), [])

    def test_second_resize_during_backup_is_rejected(self):
        self.resize()
        real_sync = self.fx.helper.sync_directory
        def resize_again(path):
            real_sync(path)
            self.resize(70, 22)
        with mock.patch.object(self.fx.helper, 'sync_directory', side_effect=resize_again):
            self.assertEqual(self.run_rebind()[0], 1)
        self.assertEqual(self.fx.receipt.read_bytes(), self.original)
        self.assertEqual(next(self.backups.iterdir()).read_bytes(), self.original)

    def test_incomplete_changed_or_migrated_record_is_not_rebound(self):
        original = copy.deepcopy(self.fx.state)
        changes = [('endpoint', {**self.previous, 'socket': '/different/socket'}),
                   ('endpoint', {**self.previous, 'inode': True}),
                   ('status', 'creating'), ('panes', {}), ('roles', {}),
                   ('launch', {}), ('layout', {}), ('endpoint_rebindings', {})]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                state = copy.deepcopy(original)
                state['projects']['Project'][key] = value
                self.fx.receipt.write_text(json.dumps(state))
                before = self.fx.receipt.read_bytes()
                code, _, _ = self.run_rebind()
                self.assertEqual(code, 1)
                self.assertEqual(self.fx.receipt.read_bytes(), before)
                self.assertEqual(list(self.backups.iterdir()), [])

    def test_native_mismatch_is_not_rebound(self):
        panes = copy.deepcopy(self.fx.api.panes)
        for field in ('label', 'cwd', 'workspace_id'):
            with self.subTest(field=field):
                self.fx.api.panes = copy.deepcopy(panes)
                self.fx.api.panes[0][field] = 'changed'
                code, _, _ = self.run_rebind()
                self.assertEqual(code, 1)
                self.assertEqual(self.fx.receipt.read_bytes(), self.original)
                self.assertEqual(list(self.backups.iterdir()), [])

    def test_backup_failures_preserve_original(self):
        self.backups.chmod(0o755)
        self.assertEqual(self.run_rebind()[0], 1)
        self.backups.chmod(0o700)
        with mock.patch.object(self.fx.helper.tempfile, 'mkstemp', side_effect=OSError('backup failed')):
            self.assertEqual(self.run_rebind()[0], 1)
        self.assertEqual(self.fx.receipt.read_bytes(), self.original)
        self.assertEqual(list(self.backups.iterdir()), [])

    def test_midflight_receipt_edit_is_preserved(self):
        real_sync = self.fx.helper.sync_directory
        def concurrent_edit(path):
            real_sync(path)
            self.fx.receipt.write_text('owner changed this receipt')
        with mock.patch.object(self.fx.helper, 'sync_directory', side_effect=concurrent_edit):
            code, _, err = self.run_rebind()
        self.assertEqual(code, 1)
        self.assertIn('Receipt changed', err)
        self.assertEqual(self.fx.receipt.read_text(), 'owner changed this receipt')
        self.assertEqual(next(self.backups.iterdir()).read_bytes(), self.original)

    def test_layout_change_after_backup_stops_rebind(self):
        real_sync = self.fx.helper.sync_directory
        def resize(path):
            real_sync(path)
            for rect in self.fx.api.rects.values():
                rect['x'] *= 2
                rect['width'] = rect['width'] * 2 + 1
        with mock.patch.object(self.fx.helper, 'sync_directory', side_effect=resize):
            code, _, _ = self.run_rebind()
        self.assertEqual(code, 1)
        self.assertEqual(self.fx.receipt.read_bytes(), self.original)
        self.assertEqual(next(self.backups.iterdir()).read_bytes(), self.original)

    def test_same_binding_still_checks_endpoint_after_native_reads(self):
        self.fx.rec['endpoint'] = self.current
        self.fx.receipt.write_text(json.dumps(self.fx.state))
        before = self.fx.receipt.read_bytes()
        def permission_change(argv, **kwargs):
            result = self.fx.native(argv, **kwargs)
            if argv[3:5] == ['pane', 'layout']:
                self.fx.endpoint.chmod(0o666)
            return result
        with mock.patch.object(self.fx.helper.subprocess, 'run', side_effect=permission_change):
            code, _, _ = self.fx.cli('--session', 'sandbox', '--rebind', '--backup-dir', str(self.backups))
        self.assertEqual(code, 1)
        self.assertEqual(self.fx.receipt.read_bytes(), before)

    def test_cli_requires_explicit_exclusive_rebind_and_backup(self):
        for flags in [ ['--rebind'], ['--backup-dir', str(self.backups)],
                       ['--rebind', '--inspect', '--backup-dir', str(self.backups)],
                       ['--rebind', '--create', '--backup-dir', str(self.backups)]]:
            with self.subTest(flags=flags), mock.patch.object(
                    self.fx.helper.subprocess, 'run', side_effect=AssertionError('No native call')):
                self.assertEqual(self.fx.cli('--session', 'sandbox', *flags)[0], 2)


if __name__ == '__main__':
    unittest.main()
