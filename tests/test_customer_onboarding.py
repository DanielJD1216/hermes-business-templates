"""Synthetic onboarding receipts. No model calls, live profiles or external sends."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_installer import ROOT, hbt, load

SCRIPT = ROOT / 'skills/customer-onboarding/scripts/checkpoint.py'
checkpoint = load('customer_checkpoint', SCRIPT)


class CustomerOnboarding(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(checkpoint, 'onboarding checkpoint helper is not implemented')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        env = patch.dict(os.environ, HOME=str(self.home), HERMES_HOME=str(self.home / '.hermes'))
        env.start()
        self.addCleanup(env.stop)
        self.root = checkpoint.state_root(str(self.home / 'private-run'), create=True)
        checkpoint.run(self.root, 'init')

    def put(self, stage, name, value):
        path = self.root / 'evidence' / stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value)
        return path

    def populate(self, stage):
        for name in checkpoint.REQUIRED[stage]:
            self.put(stage, name, 'synthetic evidence, not live acceptance')
        if stage == 'exports':
            self.put(stage, 'sources.json', {'skipped': True, 'sources': []})
        if stage == 'review':
            self.put(stage, 'context-review.json', {'claims': []})

    def advance(self, stage, receipt='owner-message-001'):
        proposal = checkpoint.run(self.root, 'status')['proposal_digest']
        return checkpoint.run(self.root, 'advance', stage=stage, expected=proposal, approval=receipt)

    def test_order_evidence_and_approval_gate_the_resumable_lifecycle(self):
        for stage in checkpoint.STAGES:
            with self.subTest(stage=stage):
                status = checkpoint.run(self.root, 'status')
                self.assertEqual(status['stage'], stage)
                self.assertNotIn('proposal_digest', status)
                before = (self.root / 'checkpoint.json').read_bytes()
                with self.assertRaises(ValueError):
                    checkpoint.run(self.root, 'advance', stage=stage, expected='0' * 64)
                self.assertEqual(before, (self.root / 'checkpoint.json').read_bytes())
                self.populate(stage)
                proposal = checkpoint.run(self.root, 'status')['proposal_digest']
                if stage in checkpoint.GATED:
                    with self.assertRaisesRegex(ValueError, 'approval'):
                        checkpoint.run(self.root, 'advance', stage=stage, expected=proposal)
                    self.assertEqual(before, (self.root / 'checkpoint.json').read_bytes())
                self.advance(stage)
        status = checkpoint.run(self.root, 'status')
        self.assertTrue(status['archived'])
        self.assertIsNone(status['stage'])
        self.assertFalse((self.home / '.hermes').exists())
        text = (self.root / 'checkpoint.json').read_text()
        self.assertNotIn('synthetic evidence', text)
        self.assertNotIn(str(self.home), text)
        with self.assertRaises(ValueError):
            checkpoint.run(self.root, 'init')


    def test_review_keeps_uncertainty_private_and_does_not_count_copies_as_independent(self):
        entries = []
        for sid in ('source-001', 'source-002'):
            self.put('exports', sid + '.md', 'Synthetic copied statement, never a customer export.')
            entries.append({'id': sid, 'file': sid + '.md', 'origin': 'origin-001',
                            'platform': 'synthetic', 'model': 'unknown', 'exported_at': 'unknown',
                            'coverage': 'this fixture only', 'lineage': 'same copied original'})
        self.put('exports', 'sources.json', {'skipped': False, 'sources': entries})
        claim = {'id': 'claim-001', 'text': 'Synthetic uncertain preference',
                 'sources': ['source-001', 'source-002'], 'source_locations': 'first line in both',
                 'independent_origins': 1, 'flags': ['conflict', 'stale', 'inferred', 'duplicate', 'domain'],
                 'decision': 'REVIEW', 'domain': 'mixed', 'audience': 'owner',
                 'destination': 'private-review', 'reason': 'Needs an owner clarification.'}
        self.put('review', 'consolidated.md', 'Private REVIEW appendix retains uncertainty, not runtime adoption.')
        self.put('review', 'context-review.json', {'claims': [claim]})
        self.assertEqual(len(checkpoint.snapshot(self.root, 'exports')), 3)
        checkpoint.snapshot(self.root, 'review')  # REVIEW may remain unresolved at approval.
        mutations = [
            {'independent_origins': 2}, {'sources': ['missing']}, {'decision': 'DELETE'},
            {'audience': 'team'}, {'destination': 'shared-business'},
            {'decision': 'INCLUDE', 'domain': 'personal', 'destination': 'owner-personal'},
            {'decision': 'INCLUDE', 'domain': 'personal', 'audience': 'team',
             'destination': 'shared-business', 'resolution_ref': 'owner-answer-001'},
        ]
        for mutation in mutations:
            self.put('review', 'context-review.json', {'claims': [claim | mutation]})
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                checkpoint.snapshot(self.root, 'review')
        # Age flags do not discard facts; explicit resolution permits a scoped adoption.
        resolved = claim | {'decision': 'INCLUDE', 'domain': 'personal',
                            'destination': 'owner-personal', 'resolution_ref': 'owner-answer-001'}
        self.put('review', 'context-review.json', {'claims': [resolved]})
        checkpoint.snapshot(self.root, 'review')
        entries[0]['origin'] = entries[1]['origin'] = None
        self.put('exports', 'sources.json', {'skipped': False, 'sources': entries})
        with self.assertRaises(ValueError):
            checkpoint.snapshot(self.root, 'review')  # unknown lineage isn't independent proof


    def test_even_empty_install_records_block_reinstall_without_writes(self):
        hbt.save_record('creator', {})
        record = hbt.record_dir('creator') / 'record.json'
        before = record.read_bytes()
        for extra in ([], ['--dry-run']):
            args = hbt.build_parser().parse_args(['install', 'creator', '--roles', 'cto', '--no-memory', '-y'] + extra)
            with patch.object(hbt, 'preflight', return_value={'hermes_version': 'synthetic', 'docker': False}), \
                 patch.object(hbt, 'native_skills', side_effect=AssertionError('must not plan a new install')), \
                 patch.object(hbt.Runner, 'hermes_cmd', side_effect=AssertionError('no native writes')):
                with self.assertRaisesRegex(SystemExit, 'already installed'):
                    hbt.cmd_install(args)
            self.assertEqual(record.read_bytes(), before)


    def test_drift_missing_outputs_and_out_of_order_steps_never_advance(self):
        self.populate('host')
        old = checkpoint.run(self.root, 'status')['proposal_digest']
        self.put('host', 'host.md', 'changed before approval')
        with self.assertRaisesRegex(ValueError, 'proposal changed'):
            checkpoint.run(self.root, 'advance', stage='host', expected=old)
        with self.assertRaisesRegex(ValueError, 'out-of-order'):
            checkpoint.run(self.root, 'advance', stage='install', expected=old)
        self.advance('host')
        evidence = self.root / 'evidence/host/host.md'
        before = (self.root / 'checkpoint.json').read_bytes()
        evidence.write_text('unexpected edit after checkpoint')
        with self.assertRaisesRegex(ValueError, 'drift'):
            checkpoint.run(self.root, 'status')
        evidence.unlink()
        with self.assertRaises(ValueError):
            checkpoint.run(self.root, 'status')
        self.assertEqual((self.root / 'checkpoint.json').read_bytes(), before)

    def test_raw_exports_remain_hash_checked_on_resume(self):
        for stage in ('host', 'identity', 'reference'):
            self.populate(stage)
            self.advance(stage)
        sid = 'source-001'
        raw = self.put('exports', sid + '.md', 'immutable synthetic export')
        self.put('exports', 'sources.json', {'skipped': False, 'sources': [{
            'id': sid, 'file': sid + '.md', 'origin': None, 'platform': 'synthetic',
            'model': 'unknown', 'exported_at': 'unknown', 'coverage': 'fixture', 'lineage': 'unknown'}]})
        self.advance('exports')
        raw.write_text('attempt to silently correct the original')
        with self.assertRaisesRegex(ValueError, 'drift'):
            checkpoint.run(self.root, 'status')

    def test_blockers_are_durable_and_require_explicit_resolution(self):
        self.populate('host')
        result = checkpoint.run(self.root, 'block', reason='recovery')
        self.assertEqual(result['next_action'], 'resolve-recovery')
        self.assertEqual(checkpoint.run(self.root, 'status')['blocker'], 'recovery')
        with self.assertRaisesRegex(ValueError, 'blocker'):
            self.advance('host')
        checkpoint.run(self.root, 'block', reason='none')
        self.assertEqual(self.advance('host')['stage'], 'identity')
        state = json.loads((self.root / 'checkpoint.json').read_text())
        state['archived'] = True
        (self.root / 'checkpoint.json').write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError, 'archive'):
            checkpoint.run(self.root, 'status')

    def test_private_paths_and_atomic_write_failure(self):
        public = self.home / 'public'
        public.mkdir(mode=0o755)
        with self.assertRaisesRegex(ValueError, 'owner-only'):
            checkpoint.state_root(str(public))
        checkout = self.home / 'checkout'
        checkout.mkdir()
        (checkout / '.git').mkdir()
        with self.assertRaisesRegex(ValueError, 'Git'):
            checkpoint.state_root(str(checkout / 'state'), create=True)
        self.assertFalse((checkout / 'state').exists())
        self.populate('host')
        file = self.root / 'evidence/host/host.md'
        file.unlink()
        outside = self.home / 'outside'
        outside.write_text('do not read or change')
        file.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            checkpoint.snapshot(self.root, 'host')
        file.unlink()
        os.link(outside, file)
        with self.assertRaisesRegex(ValueError, 'hardlink'):
            checkpoint.snapshot(self.root, 'host')
        file.unlink()
        self.populate('host')
        before = (self.root / 'checkpoint.json').read_bytes()
        with patch.object(checkpoint.os, 'replace', side_effect=OSError('injected write failure')):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.advance('host')
        self.assertEqual((self.root / 'checkpoint.json').read_bytes(), before)
        self.assertEqual(list(self.root.glob('.checkpoint-*')), [])
        self.assertEqual((self.root / 'checkpoint.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual(outside.read_text(), 'do not read or change')

    def test_cli_reports_pending_evidence_and_refuses_malformed_json(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.root), 'status'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['stage'], 'host')
        self.put('exports', 'sources.json', '{"skipped":true,"skipped":false,"sources":[]}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            checkpoint.snapshot(self.root, 'exports')
        directory = self.home / 'not-a-json-file'
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, 'regular file'):
            checkpoint.read_json(directory)
        (self.root / 'checkpoint.json').write_text('{')
        result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.root), 'status'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stdout)['blocked'])

    def test_deleted_specialists_and_tombstones_do_not_make_a_clean_install(self):
        home = Path(os.environ['HERMES_HOME'])
        home.mkdir()
        (home / 'SOUL.md').write_text('Existing main identity')
        (home / 'auth.json').write_text('synthetic login sentinel, not a credential')
        workspace = home / 'workspaces/creator'
        workspace.mkdir(parents=True)
        (workspace / 'USER.md').write_text('Synthetic preserved worksheet')
        rec = {'version': 'fixture', 'profiles': ['cto'], 'workspace': str(workspace), 'setup': {}}
        hbt.save_record('creator', rec)
        marker = home / 'profiles/.deleted/cto'
        marker.parent.mkdir(parents=True)
        marker.touch()
        before = hbt.package_hashes(home)
        with patch.object(hbt, 'cmd_install', side_effect=AssertionError('must not recreate')), \
             patch.object(hbt.Runner, 'hermes_cmd', side_effect=AssertionError('no native changes')), \
             patch.object(hbt, 'say'):
            self.assertEqual(hbt.next_setup_step(hbt.load_template('creator'), rec), ('recover', None))
            self.assertEqual(hbt.main(['setup', 'creator']), 1)
            self.assertEqual(hbt.main(['status', 'creator']), 1)
        self.assertEqual(hbt.package_hashes(home), before)

    def test_entrypoint_and_prompts_are_scoped_source_not_runtime_installation(self):
        import yaml
        skill = ROOT / 'skills/customer-onboarding/SKILL.md'
        text = skill.read_text()
        frontmatter = yaml.safe_load(text.split('---', 2)[1])
        self.assertEqual(frontmatter['name'], 'customer-onboarding')
        self.assertLessEqual(len(frontmatter['description']), 60)
        self.assertIn('one missing question or gives one instruction', text)
        self.assertIn('not an auto-installed', (ROOT / 'AGENTS.md').read_text())
        self.assertTrue((ROOT / 'templates/creator/workspace/skills/project-onboarding/SKILL.md').is_file())
        for name in ('prompt-1-extraction.md', 'prompt-2-consolidation.md'):
            prompt = (skill.parent / 'references' / name).read_text()
            self.assertIn('REVIEW', prompt)
            self.assertIn('credentials', prompt)
            self.assertIn('personal', prompt)
            self.assertIn('business', prompt)


if __name__ == '__main__':
    unittest.main()
