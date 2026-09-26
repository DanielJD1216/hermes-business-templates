#!/usr/bin/env python3
"""hbt: install a Hermes business template as separate role profiles.

Commands
  install <template>   create role profiles, workspace, board, jobs and routes
  update  <template>   re-apply template-owned files after `git pull`
  uninstall <template> remove what install created (workspace and memory kept by default)
  status  <template>   show what is installed and what still needs the owner

Every change is recorded in <HERMES_HOME>/business-templates/<template>/record.json,
so uninstall removes exactly what install created and nothing else.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the wrapper picks a Python that has PyYAML
    sys.exit("hbt needs PyYAML. Run it through ./hbt, which uses Hermes's own Python.")

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
MIN_HERMES = (0, 21, 0)
ROUTE_TAG = "hbt:"  # prefix on every profile route name we add, so we only ever remove our own


# --------------------------------------------------------------------------- helpers

def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3]) or (0,)


class Runner:
    """Runs hermes commands, or only prints them in dry-run mode."""

    def __init__(self, hermes_bin: str, dry_run: bool, verbose: bool = False):
        self.hermes = hermes_bin
        self.dry_run = dry_run
        self.verbose = verbose

    def hermes_cmd(self, *args: str, profile: str | None = None, check: bool = True, mutate: bool = True) -> str:
        cmd = [self.hermes] + (["-p", profile] if profile else []) + list(args)
        if self.dry_run and mutate:
            print("  would run:", " ".join(_q(a) for a in cmd))
            return ""
        if self.verbose:
            print("  run:", " ".join(_q(a) for a in cmd))
        res = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600)
        if check and res.returncode != 0:
            raise SystemExit(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{(res.stderr or res.stdout)[-1500:]}")
        return res.stdout


def _q(a: str) -> str:
    return a if re.fullmatch(r"[\w@%+=:,./-]+", a) else json.dumps(a)


def say(msg: str) -> None:
    print(msg, flush=True)


# --------------------------------------------------------------------------- template model

@dataclass
class Role:
    key: str
    title: str
    kind: str
    channel: str
    folder: str
    reads: list[str] = field(default_factory=list)
    dirs: list[str] = field(default_factory=list)
    starter_files: dict[str, str] = field(default_factory=dict)
    checks: list[str] = field(default_factory=list)


@dataclass
class Template:
    name: str
    title: str
    version: str
    workspace_dir: str
    system_channel: str
    roles: list[Role]
    jobs: list[dict]
    path: Path

    def profile(self, role_key: str) -> str:
        return f"{self.name}-{role_key}"

    @property
    def ops(self) -> Role | None:
        return next((r for r in self.roles if r.kind == "ops"), None)


def load_template(name: str) -> Template:
    path = TEMPLATES_DIR / name
    spec_file = path / "template.yaml"
    if not spec_file.is_file():
        known = ", ".join(sorted(p.name for p in TEMPLATES_DIR.iterdir() if (p / "template.yaml").is_file()))
        raise SystemExit(f"Unknown template {name!r}. Available: {known}")
    spec = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
    roles = [Role(key=r["key"], title=r["title"], kind=r.get("kind", "role"), channel=r["channel"], folder=r["folder"],
                  reads=r.get("reads", []), dirs=r.get("dirs", []), starter_files=r.get("starter_files", {}) or {},
                  checks=r.get("checks", [])) for r in spec["roles"]]
    for r in roles:
        if not (path / "roles" / r.key / "distribution.yaml").is_file():
            raise SystemExit(f"Template {name}: role {r.key} has no roles/{r.key}/distribution.yaml")
    return Template(name=spec["name"], title=spec["title"], version=str(spec["version"]),
                    workspace_dir=spec.get("workspace_dir", spec["name"]), system_channel=spec.get("system_channel", "agents-report"),
                    roles=roles, jobs=spec.get("jobs", []), path=path)


def select_roles(tpl: Template, wanted: str | None) -> list[Role]:
    """All roles by default (Q22). Ops is always included because every job runs there (Q23)."""
    if not wanted:
        return list(tpl.roles)
    keys = {k.strip() for k in wanted.split(",") if k.strip()}
    unknown = keys - {r.key for r in tpl.roles}
    if unknown:
        raise SystemExit(f"Unknown role(s): {', '.join(sorted(unknown))}. Roles: {', '.join(r.key for r in tpl.roles)}")
    if tpl.ops:
        keys.add(tpl.ops.key)
    return [r for r in tpl.roles if r.key in keys]


# --------------------------------------------------------------------------- workspace rendering

def render_roster(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str]) -> str:
    lines = ["| Role | Profile (Kanban assignee) | Folder | Slack channel |", "|---|---|---|---|"]
    for r in roles:
        ch = f"#{r.channel}" + (f" ({channels[r.channel]})" if channels.get(r.channel) else "")
        lines.append(f"| {r.title} | `{tpl.profile(r.key)}` | `{ws / r.folder}` | {ch} |")
    return "\n".join(lines)


def render_role_agents(tpl: Template, role: Role, roles: list[Role], ws: Path, channels: dict[str, str]) -> str:
    rules = (tpl.path / "workspace" / "RULES.md").read_text(encoding="utf-8").strip()
    reads = ", ".join(f"`{ws / p}`" if p != "all" else "every role folder" for p in role.reads) or "none"
    checks = "\n".join(f"- {c}" for c in role.checks) or "- None. This role has no nightly checks of its own."
    return (
        f"# {tpl.title}: {role.title} workspace\n\n"
        f"This file is generated by the business template installer (v{tpl.version}). Template updates rewrite it; "
        f"put your own notes in `NOTES.md` next to it.\n\n"
        f"## You\n- Role: {role.title} (`{tpl.profile(role.key)}`)\n- Write only in: `{ws / role.folder}`\n"
        f"- You may read: {reads}\n- Owner's canon (read-only): `{ws / 'canon'}`\n"
        f"- Kanban board: `{tpl.name}`\n\n"
        f"{rules}\n\n## Roster\n\n{render_roster(tpl, roles, ws, channels)}\n\n"
        f"## Nightly checks for {role.title}\n\n{checks}\n"
    )


def render_root_agents(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str]) -> str:
    rules = (tpl.path / "workspace" / "RULES.md").read_text(encoding="utf-8").strip()
    return (f"# {tpl.title} workspace\n\nGenerated by the business template installer (v{tpl.version}).\n"
            f"Each role works in its own folder and reads its own AGENTS.md there.\n\n{rules}\n\n"
            f"## Roster\n\n{render_roster(tpl, roles, ws, channels)}\n")


def build_workspace(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str], dry: bool) -> list[str]:
    """Create folders and files. Never overwrites owner files (canon, starter files); AGENTS.md is template-owned."""
    actions: list[str] = []

    def put(path: Path, text: str, owned: bool) -> None:
        if path.exists() and not owned:
            return
        actions.append(f"{'update' if path.exists() else 'create'} {path}")
        if not dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    canon_src = tpl.path / "workspace" / "canon"
    for f in sorted(canon_src.iterdir()):
        put(ws / "canon" / f.name, f.read_text(encoding="utf-8"), owned=False)
    put(ws / "AGENTS.md", render_root_agents(tpl, roles, ws, channels), owned=True)
    for r in roles:
        base = ws / r.folder
        for d in r.dirs:
            if not (base / d).is_dir():
                actions.append(f"create {base / d}/")
                if not dry:
                    (base / d).mkdir(parents=True, exist_ok=True)
        for name, text in r.starter_files.items():
            put(base / name, text, owned=False)
        put(base / "AGENTS.md", render_role_agents(tpl, r, roles, ws, channels), owned=True)
    return actions


# --------------------------------------------------------------------------- main-profile config edits

def load_yaml_rt(path: Path):
    """Round-trip YAML that keeps the owner's comments, quotes, line lengths and list indentation."""
    from ruamel.yaml import YAML  # Hermes ships ruamel
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    if _lists_are_indented(text):
        y.indent(mapping=2, sequence=4, offset=2)
    else:
        y.indent(mapping=2, sequence=2, offset=0)
    data = y.load(text) if text else None
    return y, (data if data is not None else {})


def _lists_are_indented(text: str) -> bool:
    """True when list items sit deeper than their parent key (`key:\\n  - a`), the style Hermes writes."""
    lines = text.splitlines()
    for prev, line in zip(lines, lines[1:]):
        key = re.match(r"^(\s*)[^\s#-][^:]*:\s*$", prev)
        item = re.match(r"^(\s*)- ", line)
        if key and item:
            return len(item.group(1)) > len(key.group(1))
    return True


def merge_routes(existing: list | None, wanted: list[dict]) -> tuple[list, list[str]]:
    """Add our routes (named hbt:...) without touching anyone else's. Returns (routes, names_added)."""
    routes = list(existing or [])
    have = {r.get("name") for r in routes if isinstance(r, dict)}
    added = []
    for w in wanted:
        if w["name"] not in have:
            routes.append(w)
            added.append(w["name"])
    return routes, added


def remove_routes(existing: list | None, names: set[str]) -> list:
    return [r for r in (existing or []) if not (isinstance(r, dict) and r.get("name") in names
                                                  and str(r.get("name", "")).startswith(ROUTE_TAG))]


def deleted_marker(name: str) -> Path:
    """Hermes marks a deleted profile with profiles/.deleted/<name> (hermes_constants.profile_tombstone_path)."""
    return hermes_home() / "profiles" / ".deleted" / name


def profile_is_live(name: str) -> bool:
    return (hermes_home() / "profiles" / name).exists() and not deleted_marker(name).exists()


def clear_deleted_marker(name: str, backup_dir: Path, dry: bool) -> None:
    """Let a previously deleted profile name be installed again.

    `hermes profile create` clears this marker itself; `hermes profile install` does not, so it fails
    with "Named profile home does not exist" for any name deleted before (Hermes 0.21.5). A folder
    still sitting at the deleted name is moved aside into the backups, never deleted.
    """
    marker = deleted_marker(name)
    if not marker.exists():
        return
    home = hermes_home() / "profiles" / name
    if home.exists():
        dest = backup_dir / f"deleted-profile-{name}-{_dt.datetime.now():%Y%m%d-%H%M%S}"
        say(f"  {name}: moving the leftover folder of a deleted profile to {dest}")
        if not dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(home), str(dest))
    say(f"  {name}: clearing Hermes's deleted-profile marker so the name can be installed again")
    if not dry:
        marker.unlink()


# Ops profile settings. cron.wrap_response off: Hermes otherwise wraps every post in a
# "Cronjob Response ... send me a new message to stop" header and footer, which is noise for an owner.
OPS_CONFIG = {"cron.wrap_response": "false"}


def job_args(tpl, job: dict, ops_role, target: str, workdir: Path) -> list[str]:
    """`hermes cron create` arguments for one template job.

    Agent jobs get ``--workdir`` (the Ops folder). Without it Hermes skips context files, so the run
    never reads the Ops AGENTS.md with the roster, the board name and the rules.
    """
    args = ["cron", "create", job["schedule"]]
    if job.get("prompt"):
        args.append(job["prompt"])
    args += ["--name", f"{ROUTE_TAG}{tpl.name}:{job['key']}", "--deliver", target]
    if job.get("script"):
        args += ["--script", job["script"]]
    if job.get("no_agent"):
        args.append("--no-agent")
    else:
        args += ["--workdir", str(workdir)]
    if job.get("skill"):
        prefix = f"{tpl.name}-{ops_role.key}-"
        args += ["--skill", prefix + job["skill"].split(prefix)[-1]]
    if job.get("paused_reason"):
        args += ["--paused", "--paused-reason", job["paused_reason"]]
    return args


# Kanban settings every template needs in the main profile. review_dispatch must be off: with it on,
# Hermes re-runs the SAME role to review its own card, so a role would approve its own draft (Q19 says
# the owner approves). Both are gateway-wide settings, read by the one gateway that runs the board.
KANBAN_SETTINGS = {"dispatch_in_gateway": True, "review_dispatch": False}
_MISSING = "__hbt_missing__"


def edit_main_config(cfg_path: Path, routes: list[dict], dispatch: bool, dry: bool, backup_dir: Path,
                     previous: dict | None = None) -> dict:
    """Add our routes and kanban settings. Records each original value once, so uninstall can restore it.

    ``previous`` is the main_config record from an earlier install/update; values already recorded there
    are kept, so an update never overwrites the owner's true original with our own earlier change.
    """
    y, data = load_yaml_rt(cfg_path)
    prev = previous or {}
    changes: dict = {"routes_added": [],
                     "created_sections": prev.get("created_sections",
                                                  [s for s in ("gateway", "kanban") if s not in data]),
                     "kanban_before": dict(prev.get("kanban_before") or {})}
    if prev.get("dispatch_changed") and "dispatch_in_gateway" not in changes["kanban_before"]:
        # record shape from v0.1.0 installs
        old = prev.get("dispatch_before")
        changes["kanban_before"]["dispatch_in_gateway"] = _MISSING if old is None else old
    gw = data.setdefault("gateway", {})
    new_routes, added = merge_routes(gw.get("profile_routes"), routes)
    changes["routes_added"] = added
    if added:
        gw["profile_routes"] = new_routes
    kb = data.setdefault("kanban", {})
    changed_keys = []
    for key, want in (KANBAN_SETTINGS.items() if dispatch else ()):
        if kb.get(key, _MISSING) != want:
            changes["kanban_before"].setdefault(key, kb.get(key, _MISSING))
            kb[key] = want
            changed_keys.append(key)
    if added or changed_keys:
        say(f"  main profile config: {len(added)} route(s) to add; kanban settings changed: {', '.join(changed_keys) or 'none'}")
        if not dry:
            backup_dir.mkdir(parents=True, exist_ok=True)
            if cfg_path.exists():
                shutil.copy2(cfg_path, backup_dir / f"main-config.{_dt.datetime.now():%Y%m%d-%H%M%S}.yaml")
            with cfg_path.open("w", encoding="utf-8") as fh:
                y.dump(data, fh)
    return changes


def revert_main_config(cfg_path: Path, record: dict, dry: bool) -> None:
    if not cfg_path.exists():
        return
    y, data = load_yaml_rt(cfg_path)
    gw = data.get("gateway") or {}
    mc = record.get("main_config", {})
    names = set(mc.get("routes_added", []))
    before = len(gw.get("profile_routes") or [])
    if names and "profile_routes" in gw:
        gw["profile_routes"] = remove_routes(gw.get("profile_routes"), names)
        if not gw["profile_routes"]:
            del gw["profile_routes"]
    removed = before - len(gw.get("profile_routes") or [])
    kanban_before = dict(mc.get("kanban_before") or {})
    if mc.get("dispatch_changed") and "dispatch_in_gateway" not in kanban_before:  # v0.1.0 record shape
        kanban_before["dispatch_in_gateway"] = _MISSING if mc.get("dispatch_before") is None else mc["dispatch_before"]
    restored = []
    kb = data.get("kanban")
    for key, old in kanban_before.items():
        if kb is None:
            break
        if old == _MISSING:
            kb.pop(key, None)
        else:
            kb[key] = old
        restored.append(key)
    for section in mc.get("created_sections", []):
        if section in data and not data[section]:
            del data[section]
            restored.append(section)
    say(f"  main profile config: remove {removed} route(s); restore: {', '.join(restored) or 'nothing'}")
    if not dry and (removed or restored):
        with cfg_path.open("w", encoding="utf-8") as fh:
            y.dump(data, fh)


def read_main_model(cfg_path: Path) -> dict:
    try:
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except OSError:
        return {}
    model = data.get("model") or {}
    if isinstance(model, str):
        return {"default": model}
    return {k: model[k] for k in ("default", "provider", "base_url", "api_mode") if model.get(k)}


# --------------------------------------------------------------------------- env files

def set_env_values(env_path: Path, values: dict[str, str], dry: bool) -> None:
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    out, seen = [], set()
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in values:
            out.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            out.append(line)
    out += [f"{k}={v}" for k, v in values.items() if k not in seen]
    if not dry:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
        os.chmod(env_path, 0o600)


# --------------------------------------------------------------------------- preflight

def preflight(r: Runner) -> dict:
    info: dict = {}
    hb = shutil.which(r.hermes) or (r.hermes if Path(r.hermes).exists() else None)
    if not hb:
        raise SystemExit("Hermes is not installed. Install it first: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash")
    out = subprocess.run([r.hermes, "--version"], capture_output=True, text=True).stdout
    m = re.search(r"(\d+\.\d+\.\d+)", out)
    info["hermes_version"] = m.group(1) if m else "unknown"
    if m and version_tuple(m.group(1)) < MIN_HERMES:
        raise SystemExit(f"Hermes {m.group(1)} is too old; this template needs {'.'.join(map(str, MIN_HERMES))} or newer. Run: hermes update")
    info["docker"] = bool(shutil.which("docker"))
    return info


def openviking_ok(endpoint: str) -> bool:
    import urllib.request
    try:
        with urllib.request.urlopen(f"{endpoint.rstrip('/')}/health", timeout=5) as resp:
            return bool(json.load(resp).get("healthy"))
    except Exception:  # noqa: BLE001
        return False


# --------------------------------------------------------------------------- record

def record_dir(tpl_name: str) -> Path:
    return hermes_home() / "business-templates" / tpl_name


def load_record(tpl_name: str) -> dict | None:
    p = record_dir(tpl_name) / "record.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save_record(tpl_name: str, rec: dict) -> None:
    d = record_dir(tpl_name)
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / "record.json.tmp"
    tmp.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, d / "record.json")


def parse_channels(pairs: list[str]) -> dict[str, str]:
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise SystemExit(f"--channel expects name=ID, got {p!r}")
        k, v = p.split("=", 1)
        k = k.strip().lstrip("#")
        if not re.fullmatch(r"[CG][A-Z0-9]{6,}", v.strip()):
            raise SystemExit(f"Slack channel IDs look like C0123ABCD; got {v!r} for #{k}")
        out[k] = v.strip()
    return out


# --------------------------------------------------------------------------- distribution staging

def stage_distribution(tpl: Template, role: Role) -> Path:
    """Copy the role's distribution to a stable place, so `hermes profile update` can find it again."""
    dest = record_dir(tpl.name) / "dist" / tpl.profile(role.key)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(tpl.path / "roles" / role.key, dest)
    return dest


# --------------------------------------------------------------------------- commands

def cmd_install(a: argparse.Namespace) -> int:
    tpl = load_template(a.template)
    r = Runner(a.hermes, a.dry_run, a.verbose)
    info = preflight(r)
    rec = load_record(tpl.name)
    if rec and not a.dry_run:
        raise SystemExit(f"{tpl.name} is already installed (record: {record_dir(tpl.name)}). Use `hbt update {tpl.name}` or uninstall first.")
    roles = select_roles(tpl, a.roles)
    ws = Path(a.workspace).expanduser().resolve() if a.workspace else (hermes_home() / "workspaces" / tpl.workspace_dir)
    channels = parse_channels(a.channel)
    main_cfg = hermes_home() / "config.yaml"
    model = read_main_model(main_cfg)
    memory = not a.no_memory
    if memory and not openviking_ok(a.memory_endpoint):
        if a.require_memory:
            raise SystemExit(f"Long-term memory (OpenViking) is not reachable at {a.memory_endpoint}.")
        say(f"! Long-term memory is not reachable at {a.memory_endpoint}; roles will use built-in memory. Re-run with --no-memory to silence this.")
        memory = False

    existing = [tpl.profile(x.key) for x in roles if profile_is_live(tpl.profile(x.key))]
    if existing:
        raise SystemExit(f"These profiles already exist: {', '.join(existing)}. Remove them or choose other roles.")

    say(f"Installing {tpl.title} v{tpl.version} ({'dry run' if a.dry_run else 'live'})")
    say(f"  Hermes {info['hermes_version']}; HERMES_HOME {hermes_home()}")
    say(f"  roles: {', '.join(tpl.profile(x.key) for x in roles)}")
    say(f"  workspace: {ws}")
    say(f"  model: {model.get('default', '(profile default)')} via {model.get('provider', '(default)')}; memory: {'OpenViking, one account per role' if memory else 'built-in'}")
    if not info["docker"]:
        say("! Docker not found: roles run commands directly on this server, limited only by their working folder and rules.")
    if not a.yes and not a.dry_run:
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            say("Cancelled.")
            return 1

    rec = {"template": tpl.name, "version": tpl.version, "installed_at": now_iso(), "hermes_version": info["hermes_version"],
           "workspace": str(ws), "workspace_created": not ws.exists(), "profiles": [], "jobs": [], "board": None, "main_config": {},
           "memory": {"enabled": memory, "endpoint": a.memory_endpoint, "accounts": []}, "channels": channels,
           "repo_path": str(REPO_ROOT)}

    def checkpoint():
        if not a.dry_run:
            save_record(tpl.name, rec)

    # 1. workspace
    say("1/6 workspace")
    acts = build_workspace(tpl, roles, ws, channels, a.dry_run)
    say(f"  {len(acts)} folder/file action(s)")

    # 2. profiles
    say("2/6 role profiles")
    for role in roles:
        name = tpl.profile(role.key)
        src = stage_distribution(tpl, role) if not a.dry_run else tpl.path / "roles" / role.key
        clear_deleted_marker(name, record_dir(tpl.name) / "backups", a.dry_run)
        r.hermes_cmd("profile", "install", str(src), "-y")
        rec["profiles"].append(name)
        checkpoint()
        sets = {"terminal.cwd": str(ws / role.folder)}
        if a.timezone:
            # Cron schedules follow the profile's clock. Most VPS images run UTC, so without this
            # the 07:30 morning list lands at 07:30 UTC.
            sets["timezone"] = a.timezone
        for k, v in model.items():
            sets[f"model.{k}"] = v
        if memory and role.kind != "ops":
            sets.update({"memory.provider": "openviking", "memory.openviking.endpoint": a.memory_endpoint,
                         "memory.openviking.agent": name})
            sets.update({"memory.memory_enabled": "false", "memory.user_profile_enabled": "false"})
        if role.kind == "ops":
            # Ops only runs unattended jobs and keeps no memory of its own (Q23): its inputs are files and the board.
            sets.update({"memory.memory_enabled": "false", "memory.user_profile_enabled": "false"})
            sets.update(OPS_CONFIG)
        for k, v in sets.items():
            r.hermes_cmd("config", "set", k, str(v), profile=name)
        if memory and role.kind != "ops":
            account = f"{a.memory_prefix}-{role.key}"
            set_env_values(hermes_home() / "profiles" / name / ".env",
                           {"OPENVIKING_ACCOUNT": account, "OPENVIKING_USER": "owner"}, a.dry_run)
            rec["memory"]["accounts"].append(account)
        home = channels.get(tpl.system_channel)
        if home:
            # Without a home channel Hermes greets each role's first Slack reply with a
            # "No home channel is set" notice. Point every role at the system channel instead.
            set_env_values(hermes_home() / "profiles" / name / ".env", {"SLACK_HOME_CHANNEL": home}, a.dry_run)
        checkpoint()
        say(f"  {name}: ready")

    # 3. ops settings for its scripts
    say("3/6 ops settings")
    ops = tpl.ops if tpl.ops in roles else None
    if ops:
        settings = {"template": tpl.name, "installed_version": tpl.version, "repo_path": str(REPO_ROOT),
                    "workspace": str(ws), "timezone": a.timezone or "",
                    "openviking_endpoint": a.memory_endpoint if memory else "",
                    "openviking_embed_endpoint": a.memory_embed_endpoint or "",
                    "openviking_services": [s for s in (a.memory_services or "").split(",") if s],
                    "openviking_fix_hint": a.memory_fix_hint or ""}
        if not a.dry_run:
            (hermes_home() / "profiles" / tpl.profile(ops.key) / "hbt-settings.json").write_text(
                json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        say(f"  wrote hbt-settings.json for {tpl.profile(ops.key)}")

    # 4. kanban board
    say("4/6 kanban board")
    boards = r.hermes_cmd("kanban", "boards", "list", check=False, mutate=False)
    if re.search(rf"(^|\s){re.escape(tpl.name)}(\s|$)", boards or ""):
        say(f"  board {tpl.name} already exists; reusing it (uninstall will leave it)")
    else:
        r.hermes_cmd("kanban", "boards", "create", tpl.name, "--name", tpl.title,
                     "--description", f"{tpl.title} template board. Created by hbt.")
        rec["board"] = tpl.name
        checkpoint()

    # 5. scheduled jobs (all in ops, Q23)
    say("5/6 scheduled jobs")
    if ops:
        target = f"slack:{channels[tpl.system_channel]}" if channels.get(tpl.system_channel) else "local"
        if target == "local":
            say(f"  ! no --channel {tpl.system_channel}=<ID>: job output stays on the server until you add it (hbt update --channel ...)")
        for job in tpl.jobs:
            if job.get("requires") == "openviking" and not memory:
                continue
            args = job_args(tpl, job, ops, target, ws / ops.folder)
            out = r.hermes_cmd(*args, profile=tpl.profile(ops.key))
            m = re.search(r"\b([0-9a-f]{12})\b", out or "")
            rec["jobs"].append({"key": job["key"], "id": m.group(1) if m else None, "profile": tpl.profile(ops.key)})
            checkpoint()
        say(f"  {len(rec['jobs']) if not a.dry_run else len(tpl.jobs)} job(s) delivering to {target}")

    # 6. main profile: routes + kanban dispatch
    say("6/6 main profile")
    routes = []
    for role in roles:
        cid = channels.get(role.channel)
        if cid:
            routes.append({"name": f"{ROUTE_TAG}{tpl.name}:{role.key}", "platform": "slack", "chat_id": cid,
                           "profile": tpl.profile(role.key)})
    rec["main_config"] = edit_main_config(main_cfg, routes, dispatch=True, dry=a.dry_run,
                                          backup_dir=record_dir(tpl.name) / "backups")
    checkpoint()

    say("\nDone." if not a.dry_run else "\nDry run complete. Nothing was changed.")
    print_next_steps(tpl, roles, channels, memory)
    return 0


def print_next_steps(tpl: Template, roles: list[Role], channels: dict[str, str], memory: bool) -> None:
    missing = [r.channel for r in roles if not channels.get(r.channel)]
    say("\nNext steps for the owner:")
    say("  1. Restart the gateway once so it serves the new roles: hermes gateway restart")
    if missing:
        say(f"  2. Create these Slack channels, invite the bot, then run hbt update {tpl.name} --channel name=ID ...:")
        say("     " + ", ".join(f"#{c}" for c in missing))
    say(f"  3. Fill in the owner canon: ask your main agent to run the interview in canon/INTERVIEW.md")
    if not memory:
        say("  4. Long-term memory is off. See the README Memory section to turn it on later.")


def cmd_update(a: argparse.Namespace) -> int:
    tpl = load_template(a.template)
    rec = load_record(tpl.name)
    if not rec:
        raise SystemExit(f"{tpl.name} is not installed here (no record in {record_dir(tpl.name)}).")
    r = Runner(a.hermes, a.dry_run, a.verbose)
    preflight(r)
    installed = [x for x in tpl.roles if tpl.profile(x.key) in rec["profiles"]]
    ws = Path(rec["workspace"])
    channels = dict(rec.get("channels") or {})
    channels.update(parse_channels(a.channel))
    say(f"Updating {tpl.name} {rec['version']} -> {tpl.version} ({'dry run' if a.dry_run else 'live'})")
    for role in installed:
        name = tpl.profile(role.key)
        if not a.dry_run:
            stage_distribution(tpl, role)
        r.hermes_cmd("profile", "update", name, "-y")
        if role.kind == "ops":
            for k, v in OPS_CONFIG.items():
                r.hermes_cmd("config", "set", k, v, profile=name)
        if channels.get(tpl.system_channel):
            set_env_values(hermes_home() / "profiles" / name / ".env",
                           {"SLACK_HOME_CHANNEL": channels[tpl.system_channel]}, a.dry_run)
    acts = build_workspace(tpl, installed, ws, channels, a.dry_run)
    say(f"  workspace: {len(acts)} action(s); owner files and canon untouched")
    routes = [{"name": f"{ROUTE_TAG}{tpl.name}:{x.key}", "platform": "slack", "chat_id": channels[x.channel],
               "profile": tpl.profile(x.key)} for x in installed if channels.get(x.channel)]
    changes = edit_main_config(hermes_home() / "config.yaml", routes, dispatch=True, dry=a.dry_run,
                               backup_dir=record_dir(tpl.name) / "backups", previous=rec.get("main_config"))
    ops = tpl.ops
    if ops and tpl.profile(ops.key) in rec["profiles"]:
        agent_keys = {j["key"] for j in tpl.jobs if not j.get("no_agent")}
        for j in rec.get("jobs", []):
            if j.get("id") and j.get("key") in agent_keys:  # older installs lacked --workdir
                r.hermes_cmd("cron", "edit", j["id"], "--workdir", str(ws / ops.folder), profile=j["profile"])
    if ops and tpl.profile(ops.key) in rec["profiles"] and channels.get(tpl.system_channel):
        target = f"slack:{channels[tpl.system_channel]}"
        for j in rec.get("jobs", []):
            if j.get("id"):
                r.hermes_cmd("cron", "edit", j["id"], "--deliver", target, profile=j["profile"])
    if not a.dry_run:
        old_routes = list((rec.get("main_config") or {}).get("routes_added", []))
        rec["main_config"] = changes
        rec["main_config"]["routes_added"] = old_routes + [n for n in changes["routes_added"] if n not in old_routes]
        rec["version"], rec["channels"], rec["updated_at"] = tpl.version, channels, now_iso()
        settings = hermes_home() / "profiles" / tpl.profile(ops.key) / "hbt-settings.json" if ops else None
        if settings and settings.exists():
            s = json.loads(settings.read_text(encoding="utf-8"))
            s["installed_version"] = tpl.version
            settings.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
        save_record(tpl.name, rec)
    say("Done." if not a.dry_run else "Dry run complete. Nothing was changed.")
    if changes["routes_added"]:
        say("Restart the gateway once so the new channel routes take effect: hermes gateway restart")
    return 0


def cmd_uninstall(a: argparse.Namespace) -> int:
    rec = load_record(a.template)
    if not rec:
        raise SystemExit(f"{a.template} is not installed here (no record in {record_dir(a.template)}).")
    if a.delete_workspace and not rec.get("workspace_created", False):
        raise SystemExit(f"{rec['workspace']} existed before the install, so hbt will not delete it. Remove it yourself if you mean to.")
    r = Runner(a.hermes, a.dry_run, a.verbose)
    say(f"Uninstalling {a.template} ({'dry run' if a.dry_run else 'live'})")
    say(f"  profiles: {', '.join(rec['profiles']) or 'none'}")
    say(f"  workspace {rec['workspace']}: {'DELETE' if a.delete_workspace else 'kept'}")
    say(f"  memory accounts {', '.join(rec['memory'].get('accounts', [])) or 'none'}: kept (see README to delete them)")
    if not a.yes and not a.dry_run:
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            say("Cancelled.")
            return 1
    revert_main_config(hermes_home() / "config.yaml", rec, a.dry_run)
    for name in rec["profiles"]:
        if (hermes_home() / "profiles" / name).exists():
            r.hermes_cmd("profile", "delete", name, "-y")
    if rec.get("board"):
        # Archives the board (recoverable under kanban/boards/_archived); tasks are never hard-deleted by us.
        out = r.hermes_cmd("kanban", "boards", "rm", rec["board"], check=False)
        say(f"  board {rec['board']}: archived" if not a.dry_run else "")
    if a.delete_workspace:
        say(f"  delete {rec['workspace']}")
        if not a.dry_run:
            shutil.rmtree(rec["workspace"], ignore_errors=True)
    if not a.dry_run:
        shutil.rmtree(record_dir(a.template) / "dist", ignore_errors=True)
        done = record_dir(a.template) / f"record.uninstalled.{_dt.datetime.now():%Y%m%d-%H%M%S}.json"
        os.replace(record_dir(a.template) / "record.json", done)
    say("Done. Restart the gateway once so it stops serving the removed roles." if not a.dry_run else "Dry run complete. Nothing was changed.")
    return 0


def cmd_status(a: argparse.Namespace) -> int:
    rec = load_record(a.template)
    if not rec:
        say(f"{a.template}: not installed")
        return 1
    say(f"{a.template} v{rec['version']} installed {rec['installed_at']}")
    for name in rec["profiles"]:
        say(f"  {'ok     ' if (hermes_home() / 'profiles' / name).exists() else 'MISSING'} {name}")
    cfg = yaml.safe_load((hermes_home() / "config.yaml").read_text(encoding="utf-8")) or {}
    gw = cfg.get("gateway") or {}
    ours = [x for x in gw.get("profile_routes") or [] if str(x.get("name", "")).startswith(ROUTE_TAG)]
    say(f"  routes: {len(ours)} of ours in the main config")
    say(f"  gateway serves every profile: {'yes' if gw.get('multiplex_profiles') else 'not yet (restart the gateway once)'}")
    say(f"  kanban dispatch in gateway: {(cfg.get('kanban') or {}).get('dispatch_in_gateway')}")
    say(f"  kanban auto-review (must be False, the owner approves): {(cfg.get('kanban') or {}).get('review_dispatch', True)}")
    say(f"  memory: {'OpenViking' if rec['memory']['enabled'] else 'built-in'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hbt", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hermes", default=os.environ.get("HBT_HERMES", "hermes"), help="hermes executable")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, confirm=True):
        sp.add_argument("template")
        sp.add_argument("--dry-run", action="store_true", help="show what would change; change nothing")
        if confirm:
            sp.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")

    i = sub.add_parser("install", help="install a template")
    common(i)
    i.add_argument("--roles", help="comma-separated role keys (default: all). Ops is always included.")
    i.add_argument("--workspace", help="shared folder for the business (default: $HERMES_HOME/workspaces/<template>)")
    i.add_argument("--channel", action="append", default=[], metavar="NAME=ID", help="Slack channel ID, e.g. creator-video=C0123ABCD (repeat)")
    i.add_argument("--timezone", help="IANA timezone for alert times, e.g. America/Vancouver")
    i.add_argument("--no-memory", action="store_true", help="skip OpenViking; roles use built-in memory")
    i.add_argument("--require-memory", action="store_true", help="fail if OpenViking is not reachable")
    i.add_argument("--memory-endpoint", default="http://127.0.0.1:1933")
    i.add_argument("--memory-prefix", default=None, help="OpenViking account prefix (default: the template name)")
    i.add_argument("--memory-embed-endpoint", default="", help="local search-model URL checked when memory search fails")
    i.add_argument("--memory-services", default="", help="comma-separated systemd user services to report on outage")
    i.add_argument("--memory-fix-hint", default="", help="one line telling the owner how to fix a memory outage")
    i.set_defaults(func=cmd_install)

    u = sub.add_parser("update", help="re-apply template files after git pull")
    common(u, confirm=False)
    u.add_argument("--channel", action="append", default=[], metavar="NAME=ID")
    u.set_defaults(func=cmd_update)

    x = sub.add_parser("uninstall", help="remove what install created")
    common(x)
    x.add_argument("--delete-workspace", action="store_true", help="also delete the business folder (cannot be undone)")
    x.set_defaults(func=cmd_uninstall)

    s = sub.add_parser("status", help="show install state")
    s.add_argument("template")
    s.set_defaults(func=cmd_status)
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if getattr(a, "memory_prefix", "unset") is None:
        a.memory_prefix = a.template
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
