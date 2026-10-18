"""Explicit host-local control route; synthetic sockets, no live Herdr calls."""
import json
import os
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import test_project_onboarding as layout_tests


class ControlRoute(unittest.TestCase):
    cli = layout_tests.Recovery.cli

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(tmp.cleanup)
        self.ws = Path(tmp.name)
        self.home = self.ws / 'hermes'
        self.roles = {slot: {'profile': profile, 'label': slot} for slot, profile in
                      zip(('executive-assistant', 'cto', 'engineer1', 'engineer2'),
                          ('default', 'architect', 'engineer', 'engineer'))}
        for role in self.roles.values():
            path = self.home if role['profile'] == 'default' else self.home / 'profiles' / role['profile']
            path.mkdir(parents=True, exist_ok=True)
            (path / 'config.yaml').write_text('model: {}\n')
        self.helper = layout_tests.load_helper()
        self.api = layout_tests.HerdrDouble()
        self.helper.onboard(self.ws, 'Project', str(self.ws / 'project'), 'Goal', True,
                            self.api, {}, self.roles, self.home)
        self.receipt = self.ws / '.hbt-projects.json'
        self.state = json.loads(self.receipt.read_text())
        self.rec = self.state['projects']['Project']
        self.api.calls.clear()

    def prepare_endpoint(self):
        self.endpoint = self.ws / 'herdr.sock'
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.bind(str(self.endpoint))
        self.endpoint.chmod(0o600)
        info = self.endpoint.stat()
        self.rec['endpoint'] = dict(socket=str(self.endpoint), inode=info.st_ino, device=info.st_dev)
        self.receipt.write_text(json.dumps(self.state))
        self.status = {'client': {'session': 'sandbox'}, 'server': {
            'running': True, 'compatible': True, 'socket': str(self.endpoint)}}
        self.session = 'sandbox'
        self.commands = []

    def native(self, argv, **kwargs):
        self.commands.append(argv)
        self.assertEqual(argv[:3], ['herdr', '--session', self.session])
        self.assertFalse(any(k.startswith('HERDR_') for k in kwargs['env']))
        data = self.status if argv[3:] == ['status', '--json'] else {'result': self.api(*argv[3:])}
        return subprocess.CompletedProcess(argv, 0, json.dumps(data), '')

    def test_explicit_session_inspects_without_inherited_context(self):
        self.prepare_endpoint()
        before = self.receipt.read_bytes()
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native):
            code, out, err = self.cli('--session', 'sandbox', '--inspect', env={
                'HOME': str(self.ws), 'HERMES_HOME': str(self.home),
                'HERDR_PANE_ID': 'foreign:p1', 'HERDR_SOCKET_PATH': '/unapproved/socket'})
        self.assertEqual((code, err), (0, ''))
        report = json.loads(out)
        self.assertEqual(report['layout_status'], 'verified')
        self.assertEqual(report['control']['session'], 'sandbox')
        self.assertEqual(report['readiness'], 'not-verified')
        self.assertEqual(self.receipt.read_bytes(), before)
        self.assertTrue(all(c[1] not in ('create', 'split', 'rename') for c in self.api.calls))

    def test_bad_status_never_reads_layout_or_changes_receipt(self):
        self.prepare_endpoint()
        original = self.status
        cases = [
            {**original, 'client': None}, {**original, 'server': []},
            {**original, 'client': {'session': 'wrong'}},
            {**original, 'server': {**original['server'], 'running': False}},
            {**original, 'server': {**original['server'], 'compatible': False}},
            {**original, 'server': {**original['server'], 'socket': str(self.receipt)}},
        ]
        before = self.receipt.read_bytes()
        for status in cases:
            with self.subTest(status=status):
                self.status = status
                with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native):
                    code, _, err = self.cli('--session', 'sandbox', '--inspect')
                self.assertEqual(code, 1)
                self.assertIn('[endpoint]', err)
                self.assertEqual(self.api.calls, [])
                self.assertEqual(self.receipt.read_bytes(), before)

    def test_default_is_explicit_and_launch_commands_keep_target(self):
        self.prepare_endpoint()
        self.session = 'default'
        self.status['client']['session'] = None
        before = self.receipt.read_bytes()
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native):
            code, out, err = self.cli('--session', 'default')
        self.assertEqual((code, err), (0, ''))
        self.assertTrue(all(c[:3] == ['herdr', '--session', 'default']
                            for c in json.loads(out)['launch'].values()))
        self.assertEqual(self.receipt.read_bytes(), before)

    def test_private_owner_endpoint_and_receipt_identity_are_required(self):
        self.prepare_endpoint()
        before = self.receipt.read_bytes()
        self.endpoint.chmod(0o660)
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native):
            code, _, err = self.cli('--session', 'sandbox', '--inspect')
        self.assertEqual(code, 1)
        self.assertIn('owner-only', err)
        self.endpoint.chmod(0o600)
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native), \
                mock.patch.object(self.helper.os, 'getuid', return_value=-1):
            code, _, err = self.cli('--session', 'sandbox', '--inspect')
        self.assertEqual(code, 1)
        self.assertIn('current user', err)
        self.assertEqual(self.receipt.read_bytes(), before)
        self.rec['endpoint']['inode'] += 1
        self.receipt.write_text(json.dumps(self.state))
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=self.native):
            code, _, err = self.cli('--session', 'sandbox', '--inspect')
        self.assertEqual(code, 1)
        self.assertIn('different server', err)
        self.assertEqual(self.api.calls, [])

    def test_endpoint_replacement_stops_before_next_native_call(self):
        self.prepare_endpoint()
        replacement = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(replacement.close)
        before = self.receipt.read_bytes()
        def replace_after_read(argv, **kwargs):
            response = self.native(argv, **kwargs)
            if argv[3:] == ['workspace', 'list']:
                self.endpoint.rename(self.ws / 'old.sock')
                replacement.bind(str(self.endpoint))
            return response
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=replace_after_read):
            code, _, err = self.cli('--session', 'sandbox', '--inspect')
        self.assertEqual(code, 1)
        self.assertIn('endpoint changed', err)
        self.assertEqual(self.api.calls, [('workspace', 'list')])
        self.assertEqual(self.receipt.read_bytes(), before)


    def test_endpoint_symlink_retarget_stops_before_next_native_call(self):
        self.prepare_endpoint()
        alias = self.ws / 'alias.sock'
        alias.symlink_to(self.endpoint)
        self.status['server']['socket'] = str(alias)
        other = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(other.close)
        other.bind(str(self.ws / 'other.sock'))
        before = self.receipt.read_bytes()
        def retarget_after_read(argv, **kwargs):
            response = self.native(argv, **kwargs)
            if argv[3:] == ['workspace', 'list']:
                alias.unlink()
                alias.symlink_to(self.ws / 'other.sock')
            return response
        with mock.patch.object(self.helper.subprocess, 'run', side_effect=retarget_after_read):
            code, _, err = self.cli('--session', 'sandbox', '--inspect')
        self.assertEqual(code, 1)
        self.assertIn('endpoint changed', err)
        self.assertEqual(self.api.calls, [('workspace', 'list')])
        self.assertEqual(self.receipt.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
