"""Approved scope reduction; no live profiles, providers or scheduler calls."""
import unittest

from test_installer import hbt, TPL


class CreatorScope(unittest.TestCase):
    def test_only_script_watchdog_remains(self):
        tpl = hbt.load_template('creator')
        self.assertEqual([j['key'] for j in tpl.jobs], ['memory-watchdog'])
        self.assertTrue(tpl.jobs[0]['no_agent'])
        self.assertEqual(tpl.jobs[0]['requires'], 'openviking')
        self.assertEqual(list((TPL / 'roles/creative-director/skills').glob('*/SKILL.md')), [])
        self.assertEqual(list((TPL / 'roles/ops/skills').glob('*/SKILL.md')), [])

    def test_runtime_assets_do_not_include_retired_scripts(self):
        self.assertEqual({p.name for p in (TPL / 'roles/ops/scripts').glob('*.py')},
                         {'hbt_memory_watch.py'})
        for p in TPL.glob('roles/*/SOUL.md'):
            self.assertNotIn('kanban', p.read_text().lower(), p)
        self.assertNotIn('kanban', (TPL / 'workspace/RULES.md').read_text().lower())

    def test_documentation_preserves_approval_and_security_limits(self):
        text = (TPL.parents[1] / 'README.md').read_text()
        for term in ('not release-ready', 'no chat model', 'Herdr',
                     'not an authorization or hostile-process boundary',
                     'not automatic outage fallback', 'does not install Docker',
                     'Actual container and native-tool enforcement remains unverified',
                     'Customers choose', 'unrelated jobs'):
            self.assertIn(term, text)
        self.assertNotIn('!kanban', text)
        self.assertNotIn('--memory-review add-only', text)


if __name__ == '__main__':
    unittest.main()
