"""Exercise the documented capture commands with a shell double, never live Herdr."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AcceptanceEvidence(unittest.TestCase):
    def test_readback_cannot_hide_prompt_wait_failure(self):
        guide = (ROOT / 'skills/project-onboarding/SKILL.md').read_text()
        section = guide.split('### Prove one fresh session before expanding the team', 1)[1]
        match = re.search(r'```bash\n(.*?)\n```', section, re.S)
        assert match is not None, 'The documented evidence-capture commands are missing'
        commands = match.group(1)
        prelude = '''set -eu
herdr() {
    case "$1 $2" in
        'agent prompt') printf '%s\\n' 'synthetic prompt/wait response'; return "$PROMPT_RC" ;;
        'agent read') printf '%s\\n' 'synthetic read response'; return "$READ_RC" ;;
        *) return 99 ;;
    esac
}
target=test-agent
probe=test-marker
timeout_ms=1000
'''
        for prompt_rc, read_rc in ((0, 0), (124, 0), (0, 5), (124, 5)):
            with self.subTest(prompt_rc=prompt_rc, read_rc=read_rc), tempfile.TemporaryDirectory(
                    dir=os.environ.get('TMPDIR')) as tmp:
                root = Path(tmp)
                home = root / 'home'; home.mkdir()
                hermes_home = root / 'hermes'; hermes_home.mkdir()
                evidence = root / 'evidence'; evidence.mkdir()
                env = {'PATH': '/usr/bin:/bin', 'HOME': str(home),
                       'HERMES_HOME': str(hermes_home), 'TMPDIR': tmp,
                       'PROMPT_RC': str(prompt_rc), 'READ_RC': str(read_rc),
                       'evidence': str(evidence)}
                run = subprocess.run(['bash', '-c', prelude + commands], env=env,
                                     cwd=root, capture_output=True, text=True, timeout=5)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual((evidence / 'exits.txt').read_text(),
                                 f'prompt_wait_exit={prompt_rc}\nread_exit={read_rc}\n')
                self.assertEqual((evidence / 'prompt-wait.json').read_text(),
                                 'synthetic prompt/wait response\n')
                self.assertEqual((evidence / 'read.json').read_text(), 'synthetic read response\n')
                self.assertTrue((evidence / 'prompt-wait.stderr').is_file())
                self.assertTrue((evidence / 'read.stderr').is_file())


if __name__ == '__main__':
    unittest.main()
