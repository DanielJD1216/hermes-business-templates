#!/usr/bin/env python3
"""Create/reuse a role-labelled Herdr layout. Never send input or start a model.

Use inherited pane context or an explicitly approved host-local --session.
The SKILL handles discovery, consent,
profile/session startup and handoffs; this helper owns only layout receipts.
"""
import argparse
from contextlib import nullcontext
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import stat
import subprocess
import tempfile

SLOTS = ('executive-assistant', 'cto', 'engineer1', 'engineer2')


def validate_roles(roles, hermes_root):
    """Validate selected names and profile presence without reading private config."""
    if not isinstance(roles, dict) or set(roles) != set(SLOTS):
        raise ValueError('Role map must contain exactly the four documented slots')
    home = Path(hermes_root).expanduser().resolve(strict=True)
    if not home.is_dir():
        raise ValueError('Hermes root must be an existing directory')
    result, homes = {}, {}
    for slot in SLOTS:
        entry = roles[slot]
        if not isinstance(entry, dict) or set(entry) != {'profile', 'label'}:
            raise ValueError('Each role needs exactly profile and label')
        profile, label = entry['profile'], entry['label']
        if not isinstance(profile, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', profile):
            raise ValueError('Profile identifier is invalid; do not normalize it silently')
        plain(label, 'Display label')
        if len(label) > 80:
            raise ValueError('Display label exceeds 80 characters')
        path = home if profile == 'default' else home / 'profiles' / profile
        marker = home / 'profiles' / '.deleted' / profile
        if profile != 'default' and (marker.exists() or marker.is_symlink()):
            raise ValueError('Selected profile is deleted; do not reactivate it automatically')
        if not path.resolve().is_relative_to(home) or not (path / 'config.yaml').is_file():
            raise ValueError('Selected profile is missing or outside the approved Hermes root')
        result[slot] = dict(entry)
        homes[slot] = path.resolve()
    if len({r['label'] for r in result.values()}) != len(SLOTS):
        raise ValueError('Pane display labels must be distinct')
    leads = {homes[slot] for slot in SLOTS[:2]}
    if len(leads) != 2 or any(homes[slot] in leads for slot in SLOTS[2:]):
        raise ValueError('EA, CTO and Engineer responsibilities need distinct profiles')
    return result, home


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
                   '--kind', 'hermes', '--pane', pid, '--', '-p', rec['roles'][role]['profile'], '--in', rec['path']]
            for role, pid in rec['panes'].items()}


def verify(rec, api):
    workspaces = api('workspace', 'list')['workspaces']
    match = [w for w in workspaces if w['workspace_id'] == rec['workspace_id']]
    if len(match) != 1 or match[0]['label'] != rec['name']:
        raise ValueError('Recorded workspace is missing or changed; inspect it, do not recreate blindly')
    panes = api('pane', 'list', '--workspace', rec['workspace_id'])['panes']
    by_id = {p['pane_id']: p for p in panes}
    if (set(rec['panes']) != set(SLOTS) or len(panes) != 4
            or len(set(rec['panes'].values())) != 4 or set(by_id) != set(rec['panes'].values())):
        raise ValueError('Recorded pane set changed; no layout edits made')
    for role, pid in rec['panes'].items():
        p = by_id[pid]
        if (p.get('label') != rec['roles'][role]['label'] or p['workspace_id'] != rec['workspace_id']
                or p.get('cwd') != rec['path']):
            raise ValueError('Recorded pane label/location changed; no input sent')
    layout = api('pane', 'layout', '--pane', rec['panes']['engineer1'])['layout']
    rects = {p['pane_id']: p['rect'] for p in layout['panes']}
    if (layout['zoomed'] or layout.get('workspace_id') != rec['workspace_id']
            or len(layout['panes']) != 4 or set(rects) != set(by_id)):
        raise ValueError('Recorded layout changed or is zoomed; inspect before reuse')
    a, b, c, d = [rects[rec['panes'][role]] for role in SLOTS]
    if not (a['x'] == c['x'] < b['x'] == d['x'] and a['y'] == b['y'] < c['y'] == d['y']
            and all(type(r[k]) is int for r in (a, b, c, d) for k in ('x', 'y', 'width', 'height'))
            and all(r['width'] > 0 and r['height'] > 0 for r in (a, b, c, d))
            and a['width'] == c['width'] and b['width'] == d['width']
            and a['height'] == b['height'] and c['height'] == d['height']
            and abs(a['width'] - b['width']) <= 1 and abs(a['height'] - c['height']) <= 1
            and b['x'] - a['x'] - a['width'] in (0, 1)
            and c['y'] - a['y'] - a['height'] in (0, 1)):
        raise ValueError('Expected EA/CTO/engineer1/engineer2 2x2 layout changed')
    return layout


def inspect_record(rec, api):
    """Read only recorded targets; process recognition is not session readiness."""
    report = {'receipt_status': rec['status'], 'layout_status': 'unknown',
              'readiness': 'not-verified', 'panes': {}}
    wid = rec.get('workspace_id')
    if not wid:
        report['reason'] = 'No recorded workspace ID; manual authorized reconciliation required'
        return report
    matches = [w for w in api('workspace', 'list')['workspaces'] if w['workspace_id'] == wid]
    if len(matches) != 1 or matches[0].get('label') != rec['name']:
        report['reason'] = 'Recorded workspace missing or changed; ownership uncertain'
        return report
    panes = api('pane', 'list', '--workspace', wid)['panes']
    report['unrecorded_pane_count'] = sum(p['pane_id'] not in rec['panes'].values() for p in panes)
    for slot, pid in rec['panes'].items():
        found = [p for p in panes if p['pane_id'] == pid and p['workspace_id'] == wid]
        obs = {'pane_id': pid, 'exists': len(found) == 1,
               'process_exists': None, 'recognized_state': 'unknown', 'hermes_recognized': None}
        report['panes'][slot] = obs
        if len(found) != 1:
            continue
        pane = found[0]
        obs['metadata_matches'] = (pane.get('label') == rec['roles'][slot]['label']
                                   and pane.get('cwd') == rec['path'])
        if not obs['metadata_matches']:
            continue  # Changed identity is not permission to inspect a new occupant.
        status = pane.get('agent_status')
        if status in ('idle', 'working', 'blocked', 'done', 'unknown'):
            obs['recognized_state'] = status
        if 'agent' in pane and (pane['agent'] is None or isinstance(pane['agent'], str)):
            obs['hermes_recognized'] = pane['agent'] == 'hermes'
        info = api('pane', 'process-info', '--pane', pid).get('process_info')
        processes = info.get('foreground_processes') if isinstance(info, dict) else None
        if isinstance(processes, list):
            obs['process_exists'] = any(isinstance(p, dict) and type(p.get('pid')) is int
                                        and p['pid'] > 0 for p in processes)
    report['layout_status'] = 'incomplete'
    if set(rec['panes']) == set(SLOTS):
        try:
            verify(rec, api)
            report['layout_status'] = 'verified'
        except ApiError:
            raise
        except ValueError as exc:
            report['layout_status'] = 'changed'
            report['reason'] = str(exc)
    return report


def onboard(workspace, name, path, goal, create, api, identity, roles, hermes_root, *, inspect=False, finalize=False):
    if inspect and finalize or (inspect or finalize) and create:
        raise ValueError("Inspection/finalization cannot be combined with creation or each other")
    roles, home = validate_roles(roles, hermes_root)
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
    if (inspect or finalize) and not receipt.is_file():
        raise ValueError('Inspection/finalization requires an existing receipt; nothing created')
    with nullcontext() if inspect else lock.open('a') as guard:
        if guard is not None:
            fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(receipt.read_text()) if receipt.exists() else {'version': 2, 'projects': {}}
        if not isinstance(state, dict) or state.get('version') != 2 or not isinstance(state.get('projects'), dict):
            raise ValueError('Unknown project receipt format; preserve and inspect it')
        old = state['projects'].get(name)
        if (inspect or finalize) and old is None:
            raise ValueError('Project is not recorded in the receipt')
        if old is not None:
            if not isinstance(old, dict) or old.get('name') != name:
                raise ValueError('Malformed project receipt')
            if old.get('endpoint') != identity:
                raise ValueError('Interrupted onboarding or different server; inspect the receipt before recovery')
            if old.get('roles') != roles or old.get('hermes_root') != str(home):
                raise ValueError('Recorded profile mapping changed; inspect before reuse')
            plain(old.get('goal'), 'Recorded goal')
            recorded_path = old.get('path')
            if (not isinstance(recorded_path, str) or not Path(recorded_path).is_absolute()
                    or str(Path(recorded_path).resolve(strict=True)) != recorded_path
                    or not Path(recorded_path).is_dir()):
                raise ValueError('Recorded project path is missing or changed')
            panes = old.get('panes')
            if (old.get('status') not in ('creating', 'layout-ready') or not isinstance(panes, dict)
                    or not set(panes).issubset(SLOTS)):
                raise ValueError('Malformed receipt status or pane IDs')
            for pid in panes.values():
                plain(pid, 'Recorded pane ID')  # Opaque native handles may contain letters.
            if len(set(panes.values())) != len(panes):
                raise ValueError('Duplicate recorded pane IDs')
            wid = old.get('workspace_id')
            if wid is not None:
                plain(wid, 'Recorded workspace ID')
            if panes and (not wid or any(not pid.startswith(wid + ':') for pid in panes.values())):
                raise ValueError('Malformed recorded workspace ID')
            if path and str(Path(path).expanduser().resolve()) != old['path']:
                raise ValueError('Project name already points to a different path')
            if goal is not None and goal != old['goal']:
                raise ValueError('Project has a different recorded goal; review the existing project first')
            if inspect:
                return inspect_record(old, api)
            if finalize:
                if not wid or set(panes) != set(SLOTS):
                    raise ValueError('Incomplete recorded IDs; manual authorized reconciliation required')
                if ('launch' in old or old['status'] == 'layout-ready') and old.get('launch') != launch_commands(old):
                    raise ValueError('Recorded launch commands changed; no finalization')
                layout = verify(old, api)
                if 'layout' in old or old['status'] == 'layout-ready':
                    recorded = old.get('layout')
                    if (not isinstance(recorded, dict) or recorded.get('workspace_id') != wid
                            or recorded.get('zoomed') is not False
                            or not isinstance(recorded.get('panes'), list)
                            or len(recorded['panes']) != 4
                            or any(not isinstance(p, dict) for p in recorded['panes'])
                            or {p.get('pane_id'): p.get('rect') for p in recorded['panes']}
                            != {p['pane_id']: p['rect'] for p in layout['panes']}):
                        raise ValueError('Recorded geometry changed or malformed; no finalization')
                if old['status'] != 'layout-ready':
                    old.setdefault('prior_status', old['status'])
                    old.update(layout=layout, launch=launch_commands(old), status='layout-ready')
                    save(receipt, state)
                return old
            if old['status'] != 'layout-ready':
                raise ValueError('Interrupted onboarding or different server; inspect the receipt and native state before recovery')
            if old.get('launch') != launch_commands(old):
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
               'status': 'creating', 'roles': roles, 'hermes_root': str(home), 'panes': {}}
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
            api('pane', 'rename', pid, rec['roles'][role]['label'])
        rec['layout'] = verify(rec, api)
        rec['launch'] = launch_commands(rec)
        rec['status'] = 'layout-ready'
        save(receipt, state)
        return rec


class ApiError(ValueError):
    def __init__(self, operation, outcome, error=None):
        # Only structured code/message, never command argv, raw streams or error data.
        detail = ''
        if isinstance(error, dict):
            fields = []
            for key in ('code', 'message'):
                value = error.get(key)
                if not isinstance(value, (str, int)):
                    continue
                text = str(value)[:8192]
                text = re.sub(r'(?i)\b(?:bearer|basic)\s+[^\s,;]+', '[REDACTED]', text)
                text = re.sub(r'''(?ix)([\w-]*(?:token|secret|password|passwd|api[_-]?key|credential|authorization|cookie)[\w-]*["']?\s*[:=]\s*)(?:"[^"]*(?:"|$)|'[^']*(?:'|$)|[^\s,;]+)''',
                              r'\1[REDACTED]', text)
                text = re.sub(r'''(?ix)(--[\w-]*(?:token|secret|password|passwd|api[_-]?key|credential)[\w-]*\s+)(?:"[^"]*(?:"|$)|'[^']*(?:'|$)|[^\s,;]+)''',
                              r'\1[REDACTED]', text)
                text = re.sub(r'https?://[^\s]+', '[REDACTED-URL]', text)
                text = re.sub(r'\b(?:sk-|gh[pousr]_|xox[baprs]-)[\w-]+', '[REDACTED]', text)
                text = ''.join(c if 32 <= ord(c) != 127 else ' ' for c in text)
                fields.append(f'{key}={text[:256]}')
            detail = '; ' + '; '.join(fields) if fields else ''
        super().__init__(f'{operation}: {outcome}{detail}')


def native_api(*parts, session=None):
    operation = ' '.join(parts[:2])
    prefix = ['herdr'] if session is None else ['herdr', '--session', session]
    # Explicit server selection must not carry another pane's caller identity.
    env = None if session is None else {k: v for k, v in os.environ.items() if not k.startswith('HERDR_')}
    try:
        result = subprocess.run([*prefix, *parts], env=env, check=False, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise ApiError(operation, 'timeout=30s; outcome unknown') from None
    except OSError as exc:
        raise ApiError(operation, f'OS error errno={exc.errno}') from None
    outcome = f'exit={result.returncode}'
    if result.returncode:
        error = None
        for stream in (result.stderr, result.stdout):
            if len(stream) > 16384:
                continue
            try:
                data = json.loads(stream)
            except ValueError:
                continue
            if isinstance(data, dict) and isinstance(data.get('error'), dict):
                error = data['error']
                break
        raise ApiError(operation, outcome, error)
    try:
        data = json.loads(result.stdout)
    except ValueError:
        raise ApiError(operation, outcome + '; invalid JSON response') from None
    if not isinstance(data, dict):
        raise ApiError(operation, outcome + '; invalid response envelope')
    if 'error' in data:
        raise ApiError(operation, outcome, data['error'])
    if parts == ('status', '--json'):
        return data  # Native status has no result envelope.
    if not isinstance(data.get('result'), dict):
        raise ApiError(operation, outcome + '; missing result object')
    return data['result']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, help='Approved workspace containing the private project receipt')
    parser.add_argument('--name', required=True)
    parser.add_argument('--roles', required=True, help='Approved JSON mapping of slots to profile IDs and display labels')
    parser.add_argument('--hermes-root', required=True, help='Discovered default Hermes home containing named profiles')
    parser.add_argument('--path', help='Existing approved absolute directory, or approved new directory')
    parser.add_argument('--goal')
    parser.add_argument('--create', action='store_true', help='Permit creating the explicit missing directory only')
    parser.add_argument('--session', help='Owner-approved host-local Herdr session; use default explicitly for the default server')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--inspect', action='store_true', help='Read recorded native metadata without writing files or opening a lock; not a readiness check')
    modes.add_argument('--finalize', action='store_true', help='Finalize only an already complete matching recorded layout under lock; never mutate Herdr')
    args = parser.parse_args()
    if args.create and (args.inspect or args.finalize):
        parser.error('--create cannot be combined with --inspect or --finalize')
    if args.session is None and (os.environ.get('HERDR_ENV') != '1' or not os.environ.get('HERDR_SOCKET_PATH')):
        parser.error('Run inside an authorized Herdr pane or supply an approved --session; no focused-session fallback is allowed')
    stage = 'endpoint'
    try:
        if args.session is not None:
            plain(args.session, 'Herdr session')
            status = native_api('status', '--json', session=args.session)
            client, server = status.get('client'), status.get('server')
            expected = None if args.session == 'default' else args.session
            if (not isinstance(client, dict) or not isinstance(server, dict)
                    or 'session' not in client or client['session'] != expected
                    or server.get('running') is not True or server.get('compatible') is not True):
                raise ValueError('Selected Herdr session is unavailable, incompatible or mismatched; no automatic start or fallback')
            socket_path = server.get('socket')
        else:
            socket_path = os.environ['HERDR_SOCKET_PATH']
        if not isinstance(socket_path, str) or not Path(socket_path).is_absolute():
            raise ValueError('Herdr endpoint must be an absolute Unix socket path')
        endpoint = Path(socket_path).resolve(strict=True)
        info = endpoint.stat()
        if not stat.S_ISSOCK(info.st_mode):
            raise ValueError('Herdr endpoint is not a Unix socket')
        if args.session is not None and (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077):
            raise ValueError('Explicit Herdr endpoint must be owner-only and owned by the current user')
        identity = {'socket': str(endpoint), 'inode': info.st_ino, 'device': info.st_dev}

        def api(*parts):
            current = endpoint.stat()
            if (Path(socket_path).resolve(strict=True) != endpoint
                    or (current.st_ino, current.st_dev) != (info.st_ino, info.st_dev)):
                raise ValueError('Herdr endpoint changed during onboarding; stop and reconcile')
            return native_api(*parts, session=args.session)

        stage = 'roles'
        roles = json.loads(Path(args.roles).read_text(encoding='utf-8'))
        stage = 'inspect' if args.inspect else 'finalize' if args.finalize else 'onboard'
        result = onboard(args.workspace, args.name, args.path, args.goal, args.create,
                         api, identity, roles, args.hermes_root,
                         inspect=args.inspect, finalize=args.finalize)
        result = dict(result)  # Never rewrite old receipts merely to select a transport.
        result['control'] = {'mode': 'inherited' if args.session is None else 'explicit-session',
                             'session': args.session, 'endpoint': identity}
        if args.session is not None and 'launch' in result:
            result['launch'] = {slot: ['herdr', '--session', args.session, *command[1:]]
                                for slot, command in result['launch'].items()}
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Onboarding stopped [{stage}]: {exc}\nPreserve the receipt and inspect native state before retrying.\n')


if __name__ == '__main__':
    main()
