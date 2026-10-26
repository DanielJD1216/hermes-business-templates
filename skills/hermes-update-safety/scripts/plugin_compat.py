"""Read-only: do user plugins import Hermes internals, hooks or memory-provider methods the target lacks?

usage: plugin_compat.py <target-commit>   (run from anywhere; HERMES_REPO overrides the checkout)
Static check only: signature or behaviour changes still need tests."""
import ast, os, re, subprocess, sys
from pathlib import Path

REPO = Path(os.environ.get('HERMES_REPO', Path.home() / '.hermes/hermes-agent'))
HEAD = 'HEAD'
T = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: plugin_compat.py <target-commit>  (from hermes update --check)')
git = lambda *a: subprocess.run(['git', '-C', str(REPO), *a], capture_output=True, text=True)
exists = lambda rev, p: git('cat-file', '-e', f'{rev}:{p}').returncode == 0
TOPS = {l.removesuffix('.py') for l in git('ls-tree', '--name-only', HEAD).stdout.split()} - {'tests', 'website', 'docs', 'scripts'}

def module_path(rev, mod):
    p = mod.replace('.', '/')
    return next((c for c in (f'{p}.py', f'{p}/__init__.py') if exists(rev, c)), None)

_defs = {}
def top_names(rev, path):
    if (rev, path) not in _defs:
        names = set()
        try:
            for n in ast.parse(git('show', f'{rev}:{path}').stdout).body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): names.add(n.name)
                elif isinstance(n, (ast.Assign, ast.AnnAssign)):
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                        names |= {x.id for x in ast.walk(t) if isinstance(x, ast.Name)}
                elif isinstance(n, (ast.Import, ast.ImportFrom)): names |= {a.asname or a.name.split('.')[0] for a in n.names}
                elif isinstance(n, (ast.If, ast.Try)): names |= {x.name for x in ast.walk(n) if isinstance(x, (ast.FunctionDef, ast.ClassDef))} | {a.asname or a.name for x in ast.walk(n) if isinstance(x, (ast.Import, ast.ImportFrom)) for a in x.names}
        except SyntaxError:
            names.add('*unparseable*')
        _defs[(rev, path)] = names
    return _defs[(rev, path)]

roots = set()
for base in [Path.home() / '.hermes/plugins', *Path.home().glob('.hermes/profiles/*/plugins')]:
    if base.is_dir():
        roots |= {p.resolve() for p in base.iterdir() if p.is_dir()}

hooks_t = git('show', f'{T}:hermes_cli/plugins.py').stdout
broken, checked = {}, 0
for root in sorted(roots):
    for f in root.rglob('*.py'):
        if any(x in f.parts for x in ('node_modules', '__pycache__', '.venv', 'venv', 'site-packages')): continue
        try: tree = ast.parse(f.read_text(errors='replace'))
        except SyntaxError: continue
        src = f.read_text(errors='replace')
        for hook in set(re.findall(r'register_hook\(\s*["\']([a-z_]+)["\']', src)):
            if f'"{hook}"' not in hooks_t and f"'{hook}'" not in hooks_t:
                broken.setdefault(root.name, set()).add(f'hook {hook} not in target plugins.py')
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 and n.module.split('.')[0] in TOPS:
                checked += 1
                mh, mt = module_path(HEAD, n.module), module_path(T, n.module)
                if mh and not mt:
                    broken.setdefault(root.name, set()).add(f'module {n.module} removed')
                elif mh and mt:
                    for a in n.names:
                        if a.name == '*': continue
                        if a.name in top_names(HEAD, mh) and a.name not in top_names(T, mt) and not module_path(T, f'{n.module}.{a.name}'):
                            broken.setdefault(root.name, set()).add(f'{n.module}.{a.name} removed')
            elif isinstance(n, ast.Import):
                for a in n.names:
                    if a.name.split('.')[0] in TOPS and '.' in a.name:
                        checked += 1
                        if module_path(HEAD, a.name) and not module_path(T, a.name):
                            broken.setdefault(root.name, set()).add(f'module {a.name} removed')

print(f'plugins scanned: {len(roots)} | internal imports checked: {checked}')
print('plugins:', ', '.join(sorted(r.name for r in roots)))
for k, v in sorted(broken.items()):
    print(f'BREAKS {k}:'); [print('   ', x) for x in sorted(v)]
if not broken: print('no removed internal imports or hooks found')
mp = 'agent/memory_provider.py'
abstract = lambda rev: sorted(re.findall(r'@abstractmethod\s+def (\w+)', git('show', f'{rev}:{mp}').stdout))
print('memory provider abstract methods  HEAD:', abstract(HEAD), '| target:', abstract(T))
print('bundled openviking provider  HEAD:', bool(module_path(HEAD, 'plugins.memory.openviking')), '| target:', bool(module_path(T, 'plugins.memory.openviking')))
