#!/usr/bin/env python3
"""Create/reuse a role-labelled Herdr layout. Never send input or start a model.

Run only from an authorized Herdr pane. The SKILL handles discovery, consent,
profile/session startup and handoffs; this helper owns only layout receipts.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

PROFILES = {'executive-assistant': 'default', 'cto': 'cto',
            'engineer1': 'engineer', 'engineer2': 'engineer'}
LABELS = {'engineer1': 'engineer1', 'executive-assistant': 'Executive Assistant',
          'cto': 'CTO', 'engineer2': 'engineer2'}


def plain(text, field):
    if not isinstance(text, str) or not text.strip() or any(ord(c) < 32 or ord(c) == 127 for c in text):
        raise ValueError(f'{field} must be nonblank text without control characters')
    return text


def save(path, data):
    # Replace only our receipt, never project files; interruption leaves the last full journal.
    fd, name = tempfile.mkstemp(prefix='.hbt-receipt-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, indent=2)
            out.write('\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def launch_commands(rec):
    prefix = 'hbt-' + hashlib.sha256(rec['name'].encode()).hexdigest()[:8]
    return {role: ['herdr', 'agent', 'start', prefix + '-' + role,
                   '--kind', 'hermes', '--pane', pid, '--', '-p', PROFILES[role], '--in', rec['path']]
            for role, pid in rec['panes'].items()}


def verify(rec, api):
    workspaces = api('workspace', 'list')['workspaces']
    match = [w for w in workspaces if w['workspace_id'] == rec['workspace_id']]
    if len(match) != 1 or match[0]['label'] != rec['name']:
        raise ValueError('Recorded workspace is missing or changed; inspect it, do not recreate blindly')
    panes = api('pane', 'list', '--workspace', rec['workspace_id'])['panes']
    by_id = {p['pane_id']: p for p in panes}
    if set(by_id) != set(rec['panes'].values()):
        raise ValueError('Recorded pane set changed; no layout edits made')
    for role, pid in rec['panes'].items():
        p = by_id[pid]
        if (p.get('label') != LABELS[role] or p['workspace_id'] != rec['workspace_id']
                or p.get('cwd') != rec['path']):
            raise ValueError('Recorded pane label/location changed; no input sent')
    layout = api('pane', 'layout', '--pane', rec['panes']['engineer1'])['layout']
    rects = {p['pane_id']: p['rect'] for p in layout['panes']}
    if layout['zoomed'] or set(rects) != set(by_id):
        raise ValueError('Recorded layout changed or is zoomed; inspect before reuse')
    a, b, c, d = [rects[rec['panes'][role]] for role in PROFILES]
    if not (a['x'] == c['x'] < b['x'] == d['x'] and a['y'] == b['y'] < c['y'] == d['y']
            and all(r['width'] > 0 and r['height'] > 0 for r in (a, b, c, d))):
        raise ValueError('Expected EA/CTO/engineer1/engineer2 2x2 layout changed')
    return layout


def onboard(workspace, name, path, goal, create, api, identity):
    plain(name, 'Project name')
    if len(name) > 80:
        raise ValueError('Project name exceeds 80 characters')
    workspace = Path(workspace).expanduser().resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError('Business workspace must already be a directory')
    receipt = workspace / '.hbt-projects.json'
    lock = workspace / '.hbt-projects.lock'
    if receipt.is_symlink() or lock.is_symlink():
        raise ValueError('Refusing symlink receipt/lock')
    # ponytail: one local lock per workspace; shard only if onboarding throughput requires it.
    with lock.open('a') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(receipt.read_text()) if receipt.exists() else {'version': 1, 'projects': {}}
        if state.get('version') != 1 or not isinstance(state.get('projects'), dict):
            raise ValueError('Unknown project receipt format; preserve and inspect it')
        old = state['projects'].get(name)
        if old:
            if path and str(Path(path).expanduser().resolve()) != old['path']:
                raise ValueError('Project name already points to a different path')
            if goal is not None and goal != old['goal']:
                raise ValueError('Project has a different recorded goal; review the existing project first')
            if old['endpoint'] != identity or old['status'] != 'ready':
                raise ValueError('Interrupted onboarding or different server; inspect the receipt and native state before recovery')
            if old.get('profiles') != PROFILES or old.get('launch') != launch_commands(old):
                raise ValueError('Recorded profile/launch commands changed; inspect before reuse')
            verify(old, api)
            return old
        if not path or not goal:
            raise ValueError('New project needs --path and --goal; ask only for missing information')
        plain(path, 'Project path')
        plain(goal, 'Goal')
        target = Path(path).expanduser()
        if not target.is_absolute():
            raise ValueError('Project path must be absolute')
        target = target.resolve()
        if any(r['path'] == str(target) for r in state['projects'].values()):
            raise ValueError('Location is already recorded under another project name')
        if target.exists() and not target.is_dir():
            raise ValueError('Project location is not a directory')
        if not target.exists() and (not create or not target.parent.is_dir()):
            raise ValueError('Missing project directory: use --create only for an approved new folder with an existing parent')
        workspaces = api('workspace', 'list')['workspaces']
        panes = api('pane', 'list')['panes']
        if any(w['label'] == name for w in workspaces) or any(p.get('cwd') == str(target) for p in panes):
            raise ValueError('Existing unrecorded Herdr project found; inspect/reuse it manually, never duplicate or rearrange it')
        rec = {'name': name, 'path': str(target), 'goal': goal, 'endpoint': identity,
               'status': 'creating', 'profiles': dict(PROFILES), 'panes': {}}
        state['projects'][name] = rec
        save(receipt, state)  # Intent before any filesystem/API mutation. No blind retry after a timeout.
        if not target.exists():
            target.mkdir()
        made = api('workspace', 'create', '--cwd', str(target), '--label', name, '--no-focus')
        rec['workspace_id'] = made['workspace']['workspace_id']
        rec['panes']['executive-assistant'] = made['root_pane']['pane_id']
        save(receipt, state)
        for role, parent, direction in [('cto', 'executive-assistant', 'right'),
                                        ('engineer1', 'executive-assistant', 'down'),
                                        ('engineer2', 'cto', 'down')]:
            made = api('pane', 'split', rec['panes'][parent], '--direction', direction,
                       '--ratio', '0.5', '--cwd', str(target), '--no-focus')
            rec['panes'][role] = made['pane']['pane_id']
            save(receipt, state)
        for role, pid in rec['panes'].items():
            api('pane', 'rename', pid, LABELS[role])
        rec['layout'] = verify(rec, api)
        rec['launch'] = launch_commands(rec)
        rec['status'] = 'ready'
        save(receipt, state)
        return rec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, help='Business workspace containing PROJECTS.md')
    parser.add_argument('--name', required=True)
    parser.add_argument('--path', help='Existing approved absolute directory, or approved new directory')
    parser.add_argument('--goal')
    parser.add_argument('--create', action='store_true', help='Permit creating the explicit missing directory only')
    args = parser.parse_args()
    if os.environ.get('HERDR_ENV') != '1' or not os.environ.get('HERDR_SOCKET_PATH'):
        parser.error('Run inside an authorized Herdr pane; no focused-session fallback is allowed')
    endpoint = Path(os.environ['HERDR_SOCKET_PATH']).resolve(strict=True)
    info = endpoint.stat()
    if not stat.S_ISSOCK(info.st_mode):
        parser.error('Inherited Herdr endpoint is not a Unix socket')
    identity = {'socket': str(endpoint), 'inode': info.st_ino, 'device': info.st_dev}

    def api(*parts):
        result = subprocess.run(['herdr', *parts], check=True, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        if 'error' in data:
            raise ValueError(str(data['error']))
        return data['result']

    try:
        result = onboard(args.workspace, args.name, args.path, args.goal, args.create, api, identity)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'Onboarding stopped: {exc}\nPreserve the receipt and inspect native state before retrying.\n')


if __name__ == '__main__':
    main()
