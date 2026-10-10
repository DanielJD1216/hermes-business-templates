"""Managed-runtime discovery without invoking Hermes bootstrap or an installer."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ManagedLauncher(unittest.TestCase):

    def test_native_descriptor_dispatches_without_running_the_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            source = home / 'native source'
            (source / 'pm').mkdir(parents=True)
            (source / 'hermes_cli').mkdir()
            (source / 'pm/__init__.py').write_text('')
            (source / 'pm/environments.py').write_text(
                'from pathlib import Path\ndef committed_venv(root):\n'
                f'    return Path({sys.prefix!r})\n')
            (source / 'hermes_yaml.py').write_text('')
            native = source / '.hermes/bin/hermes'
            native.parent.mkdir(parents=True)
            native.write_text('#!/bin/sh\nexit 97\n')
            native.chmod(0o755)
            wrapper = home / 'hermes'
            wrapper.write_text('#!/bin/sh\nexec ' + shlex.quote(str(native)) + ' "$@"\n')
            wrapper.chmod(0o755)
            env = {**os.environ, 'HOME': str(home), 'HERMES_HOME': str(home / '.hermes'),
                   'PYTHONDONTWRITEBYTECODE': '1'}
            result = subprocess.run([sys.executable, str(ROOT / 'installer/managed_runtime.py'),
                                     str(wrapper), str(ROOT / 'installer/hbt.py'), '--help'],
                                    env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('hbt: install a Hermes business template', result.stdout)
            self.assertFalse((home / '.hermes').exists())
            # A recognized install with no committed environment must refuse, not bootstrap.
            (source / 'pm/environments.py').write_text('def committed_venv(root):\n    return None\n')
            result = subprocess.run([sys.executable, str(ROOT / 'installer/managed_runtime.py'),
                                     str(wrapper), str(ROOT / 'installer/hbt.py'), '--help'],
                                    env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('committed', result.stderr)
            self.assertFalse((home / '.hermes').exists())


if __name__ == '__main__':
    unittest.main()
