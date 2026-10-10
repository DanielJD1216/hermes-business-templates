"""Launch hbt with an existing native PM environment, without bootstrapping it.

Exit 99 means the selected launcher is not a recognized managed source install.
"""
from __future__ import annotations

from pathlib import Path
import os
import shlex
import subprocess
import sys


def source_for(launcher: Path) -> Path | None:
    # Follow symlinks and the native one-line `exec /path/hermes "$@"` wrapper.
    # Parse paths only: never evaluate shell or execute the launcher during discovery.
    seen = set()
    for _ in range(4):
        launcher = launcher.resolve()
        if launcher in seen:
            break
        seen.add(launcher)
        for parent in launcher.parents:
            if (parent / 'pm/environments.py').is_file() and (parent / 'hermes_cli').is_dir():
                return parent
        try:
            lines = launcher.read_text().splitlines()
            targets = [shlex.split(line)[1] for line in lines
                       if line.startswith('exec ') and len(shlex.split(line)) > 1]
        except (OSError, UnicodeError, ValueError):
            break
        if len(targets) != 1 or not Path(targets[0]).is_absolute():
            break
        launcher = Path(targets[0])
    return None


def main() -> int:
    source = source_for(Path(sys.argv[1]))
    if source is None:
        return 99
    # Native discovery imports also require modern Python. Read the managed
    # launcher's interpreter only; never execute its bootstrap/repair payload.
    if sys.version_info < (3, 10):
        try:
            text = (source / '.hermes/bin/hermes').read_text()
            words = shlex.split(text, comments=True)
            if (len(words) < 5 or words[0] != 'exec'
                    or words[2:4] != ['-I', '-c']
                    or not Path(words[1]).is_absolute()
                    or not Path(words[1]).is_file()):
                raise ValueError('unrecognized managed interpreter wrapper')
            python = words[1]
            probe = subprocess.run([python, '-I', '-c',
                                    'import sys; sys.exit(sys.version_info < (3, 10))'],
                                   capture_output=True, timeout=15)
            if probe.returncode:
                raise ValueError('managed interpreter requires Python 3.10 or newer')
            os.execve(python, [python, '-I', str(Path(__file__).resolve()), *sys.argv[1:]],
                      {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            print(f'hbt: cannot resolve modern managed Python: {exc}. No bootstrap was run.', file=sys.stderr)
            return 1
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source))
    try:
        from pm.environments import committed_venv
        environment = committed_venv(source)
        python = environment / 'bin/python' if environment else None
        if python is None or not python.is_file():
            raise RuntimeError('no committed dependency environment')
        probe = f'import sys; sys.path.insert(0, {str(source)!r}); import hermes_yaml, ruamel.yaml'
        check = subprocess.run([str(python), '-c', probe], capture_output=True, timeout=15,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if check.returncode:
            raise RuntimeError('committed environment lacks native YAML support')
    except (ImportError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'hbt: managed runtime unavailable: {exc}. Repair Hermes separately; no bootstrap was run.', file=sys.stderr)
        return 1
    target = sys.argv[2]
    code = (f'import sys,runpy; sys.path.insert(0,{str(source)!r}); '
            f'sys.argv=[{target!r},*sys.argv[1:]]; runpy.run_path({target!r},run_name="__main__")')
    env = {**os.environ, 'HERMES_DISABLE_LAZY_INSTALLS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    os.execve(str(python), [str(python), '-c', code, *sys.argv[3:]], env)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
