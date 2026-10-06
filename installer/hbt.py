#!/usr/bin/env python3
"""hbt: install a Hermes business template as separate bots, one Slack app each.

Commands
  setup   <template>   guided setup, one action at a time (start here)
  install <template>   create the bots' profiles, workspace, board and jobs
  connect <template> <role>  save a bot's Slack tokens and find its channels
  update  <template>   re-apply template-owned files after `git pull`
  desk    <template> <desk> --name <person>  add a desk for one outside person
  uninstall <template> remove what install created (workspace and memory kept by default)
  status  <template>   show what is installed and what still needs the owner

Every change is recorded in <HERMES_HOME>/business-templates/<template>/record.json,
so uninstall removes exactly what install created and nothing else.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as _dt
import io
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

try:
    import yaml
except ImportError:  # pragma: no cover - the wrapper picks a Python that has PyYAML
    sys.exit("hbt needs PyYAML. Run it through ./hbt, which uses Hermes's own Python.")

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
MIN_HERMES = (0, 21, 0)
ROUTE_TAG = "hbt:"  # prefix on every profile route name we add, so we only ever remove our own
MEMORY_REVIEW_KEY = "memory-draft-review"
MEMORY_REVIEW_MODES = ("off", "add-only", "add-replace")


# --------------------------------------------------------------------------- helpers

def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser().absolute()


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
    channels: list[str]
    folder: str
    reads: list[str] = field(default_factory=list)
    dirs: list[str] = field(default_factory=list)
    starter_files: dict[str, str] = field(default_factory=dict)
    checks: list[str] = field(default_factory=list)
    peers: list[str] = field(default_factory=list)          # bots this one may @mention, and hear from
    slack_toolsets: list[str] = field(default_factory=list)  # added to the bot's Slack tools
    takes_cards: bool = False                                # runs Kanban cards in the background
    builds: bool = False                                     # builds projects in the projects folder
    section: str = ""
    stock_skills: list[str] = field(default_factory=list)

    @property
    def channel(self) -> str:
        """The bot's home channel: its first one."""
        return self.channels[0]


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
    desks: list[Role] = field(default_factory=list)

    def profile(self, role_key: str) -> str:
        # v0.2: plain names (creative-director, cto, engineer, ops), the names the owner sees in Slack.
        return role_key

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

    def to_role(r: dict) -> Role:
        return Role(key=r["key"], title=r["title"], kind=r.get("kind", "role"),
                    channels=r.get("channels") or [r["channel"]], folder=r["folder"],
                    reads=r.get("reads", []), dirs=r.get("dirs", []), starter_files=r.get("starter_files", {}) or {},
                    checks=r.get("checks", []), peers=r.get("peers", []), slack_toolsets=r.get("slack_toolsets", []),
                    takes_cards=bool(r.get("takes_cards")), builds=bool(r.get("builds")), section=r.get("section", ""),
                    stock_skills=r.get("stock_skills", []))
    roles = [to_role(r) for r in spec["roles"]]
    desks = [to_role(r) for r in spec.get("desks") or []]
    for r in roles + desks:
        if not (path / "roles" / r.key / "distribution.yaml").is_file():
            raise SystemExit(f"Template {name}: role {r.key} has no roles/{r.key}/distribution.yaml")
    return Template(name=spec["name"], title=spec["title"], version=str(spec["version"]),
                    workspace_dir=spec.get("workspace_dir", spec["name"]), system_channel=spec.get("system_channel", "agents-report"),
                    roles=roles, jobs=spec.get("jobs", []), path=path, desks=desks)


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

def render_roster(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str],
                  bots: dict[str, str] | None = None) -> str:
    bots = bots or {}
    lines = ["| Role | Profile (Kanban assignee) | Slack mention | Folder | Slack channels |", "|---|---|---|---|---|"]
    for r in roles:
        ch = ", ".join(f"#{c}" + (f" ({channels[c]})" if channels.get(c) else "") for c in r.channels)
        mention = f"`<@{bots[r.key]}>`" if bots.get(r.key) else ("none" if r.kind == "ops" else "not set up yet")
        lines.append(f"| {r.title} | `{tpl.profile(r.key)}` | {mention} | `{ws / r.folder}` | {ch} |")
    return "\n".join(lines)


def render_role_agents(tpl: Template, role: Role, roles: list[Role], ws: Path, channels: dict[str, str],
                       bots: dict[str, str] | None = None, projects: str = "") -> str:
    rules = (tpl.path / "workspace" / "RULES.md").read_text(encoding="utf-8").strip()
    reads = ", ".join(f"`{ws / p}`" if p != "all" else "every role folder" for p in role.reads) or "none"
    checks = "\n".join(f"- {c}" for c in role.checks) or "- None. This role has no nightly checks of its own."
    build = ""
    if projects and (role.builds or "kanban" in role.slack_toolsets):  # the builder, and the lead that hands it cards
        build = (f"- Projects folder: `{projects}`. Each project gets its own subfolder, named in lowercase with "
                 f"hyphens; build work happens only there.\n")
    return (
        f"# {tpl.title}: {role.title} workspace\n\n"
        f"This file is generated by the business template installer (v{tpl.version}). Template updates rewrite it; "
        f"put your own notes in `NOTES.md` next to it.\n\n"
        f"## You\n- Role: {role.title} (`{tpl.profile(role.key)}`)\n- Write only in: `{ws / role.folder}`\n"
        f"- You may read: {reads}\n- Owner's canon (read-only): `{ws / 'canon'}`\n"
        f"- Kanban board: `{tpl.name}`\n{build}\n"
        f"{rules}\n\n## Roster\n\n{render_roster(tpl, roles, ws, channels, bots)}\n\n"
        f"## Nightly checks for {role.title}\n\n{checks}\n"
    )


def render_root_agents(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str],
                       bots: dict[str, str] | None = None) -> str:
    rules = (tpl.path / "workspace" / "RULES.md").read_text(encoding="utf-8").strip()
    return (f"# {tpl.title} workspace\n\nGenerated by the business template installer (v{tpl.version}).\n"
            f"Each role works in its own folder and reads its own AGENTS.md there.\n\n{rules}\n\n"
            f"## Roster\n\n{render_roster(tpl, roles, ws, channels, bots)}\n")


def build_workspace(tpl: Template, roles: list[Role], ws: Path, channels: dict[str, str], dry: bool,
                    bots: dict[str, str] | None = None, projects: str = "") -> list[str]:
    """Create folders and files. Never overwrites owner files (canon, starter files); AGENTS.md is template-owned."""
    actions: list[str] = []

    def put(path: Path, text: str, owned: bool) -> None:
        if path.exists() and not owned:
            return
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return
        actions.append(f"{'update' if path.exists() else 'create'} {path}")
        if not dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    canon_src = tpl.path / "workspace" / "canon"
    for f in sorted(canon_src.iterdir()):
        put(ws / "canon" / f.name, f.read_text(encoding="utf-8"), owned=False)
    put(ws / "AGENTS.md", render_root_agents(tpl, roles, ws, channels, bots), owned=True)
    for r in roles:
        base = ws / r.folder
        for d in r.dirs:
            if not (base / d).is_dir():
                actions.append(f"create {base / d}/")
                if not dry:
                    (base / d).mkdir(parents=True, exist_ok=True)
        for name, text in r.starter_files.items():
            put(base / name, text, owned=False)
        put(base / "AGENTS.md", render_role_agents(tpl, r, roles, ws, channels, bots, projects), owned=True)
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


def slack_settings(role: Role, channels: dict[str, str], owner: str, bots: dict[str, str]) -> tuple[dict, dict]:
    """(config, env) for one bot's own Slack app. The settings the template was proven with:

    - it answers in its own channels without an @mention (free_response_channels);
    - it stays quiet when the owner @mentions another bot there (ignore_other_user_mentions);
    - it hears its peers only when they @mention it, and a thread follow-up wakes only the bot
      that was mentioned (allow_bots: mentions + strict_mention), so two bots never loop.
    Hermes denies everyone by default, so the owner (and each peer bot) must be on the allowlist.
    """
    cfg: dict[str, str] = {"slack.ignore_other_user_mentions": "true"}
    if owner:  # "@bot !approve" from a peer bot is a command; only the owner may run commands
        cfg.update({"slack.allow_admin_from": owner, "slack.group_allow_admin_from": owner})
    ids = [channels[c] for c in role.channels if channels.get(c)]
    if ids:
        cfg["slack.free_response_channels"] = ",".join(ids)
    peers = [bots[p] for p in role.peers if bots.get(p)]
    if role.peers:
        cfg.update({"slack.allow_bots": "mentions", "slack.strict_mention": "true"})
    env: dict[str, str] = {}
    allowed = [u for u in [owner] + peers if u]
    if allowed:
        env["SLACK_ALLOWED_USERS"] = ",".join(allowed)
    if ids:
        env["SLACK_HOME_CHANNEL"] = ids[0]  # its own channel, so Hermes never posts a "no home channel" notice
    return cfg, env


def peer_channels(tpl: Template, role: Role, profiles: list[str] | None = None) -> list[str]:
    """Channels of the (installed) bots that hand this one work. Handoffs are a mention in the sender's
    own thread and a bot only hears channels it is in, so the receiver must be a member of each."""
    senders = [x for x in tpl.roles if role.key in x.peers and (profiles is None or tpl.profile(x.key) in profiles)]
    return [c for x in senders for c in x.channels if c not in role.channels]


def card_takers(existing, wanted: list[str]):
    """New ``kanban.dispatch_profiles`` value, or None to leave it alone.

    The key absent means every profile's cards run, ours included, so we never add it (adding it would stop
    the owner's other profiles). When the owner has a list, our card takers are appended to it.
    """
    if existing is None or existing == _MISSING:
        return None
    names = [str(n) for n in existing] if isinstance(existing, (list, tuple)) else \
        [n.strip() for n in str(existing).split(",") if n.strip()]
    merged = names + [w for w in wanted if w not in names]
    return merged if merged != names else None


def new_jobs(tpl: Template, rec: dict) -> list[dict]:
    """Template jobs this install does not have yet. A job the owner removed stays in the record, so it is not re-added."""
    have = {j.get("key") for j in rec.get("jobs", [])}
    memory = bool((rec.get("memory") or {}).get("enabled"))
    return [j for j in tpl.jobs if j["key"] != MEMORY_REVIEW_KEY and j["key"] not in have and not (j.get("requires") == "openviking" and not memory)]


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
                     previous: dict | None = None, card_profiles: list[str] | None = None) -> dict:
    """Add our routes and kanban settings. Records each original value once, so uninstall can restore it.

    ``previous`` is the main_config record from an earlier install/update; values already recorded there
    are kept, so an update never overwrites the owner's true original with our own earlier change.
    v0.2 installs pass no routes: each bot has its own Slack app, so nothing needs routing.
    """
    checked_path(cfg_path, cfg_path.parent)
    y, data = load_yaml_rt(cfg_path)
    prev = previous or {}
    changes: dict = {"routes_added": [],
                     "created_sections": prev.get("created_sections",
                                                  [s for s in ("gateway", "kanban") if s not in data]),
                     "kanban_before": dict(prev.get("kanban_before") or {}),
                     "kanban_applied": dict(prev.get("kanban_applied") or {})}
    if prev.get("dispatch_changed") and "dispatch_in_gateway" not in changes["kanban_before"]:
        # record shape from v0.1.0 installs
        old = prev.get("dispatch_before")
        changes["kanban_before"]["dispatch_in_gateway"] = _MISSING if old is None else old
    added = []
    if routes:
        gw = data.setdefault("gateway", {})
        new_routes, added = merge_routes(gw.get("profile_routes"), routes)
        if added:
            gw["profile_routes"] = new_routes
    changes["routes_added"] = added
    kb = data.setdefault("kanban", {})
    changed_keys = []
    wanted: dict = dict(KANBAN_SETTINGS) if dispatch else {}
    takers = card_takers(kb.get("dispatch_profiles", _MISSING), card_profiles or [])
    if takers is not None:
        wanted["dispatch_profiles"] = takers
    for key, want in wanted.items():
        changes["kanban_applied"][key] = want
        cur = kb.get(key, _MISSING)
        if (list(cur) if isinstance(cur, (list, tuple)) else cur) != want:
            changes["kanban_before"].setdefault(key, list(cur) if isinstance(cur, (list, tuple)) else cur)
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
    checked_path(cfg_path, cfg_path.parent)
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
        applied = mc.get("kanban_applied", {}).get(key, KANBAN_SETTINGS.get(key, _MISSING))
        if applied != _MISSING and kb.get(key, _MISSING) != applied:
            if key == "dispatch_profiles" and isinstance(applied, list) and isinstance(kb.get(key), list):
                original_names = old if isinstance(old, list) else []
                added = set(applied) - set(original_names)
                kb[key] = [p for p in kb[key] if p not in added]
                restored.append(key)
            continue  # owner changed this value since install
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


def read_env_value(env_path: Path, key: str) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []:
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip("\"'")
    return ""


# --------------------------------------------------------------------------- preflight

def preflight(r: Runner) -> dict:
    info: dict = {}
    checked_path(hermes_home() / "config.yaml", hermes_home())
    hb = shutil.which(r.hermes) or (r.hermes if Path(r.hermes).exists() else None)
    if not hb:
        raise SystemExit("Hermes is not installed. Install it first: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash")
    out = native_skills()["version"]
    m = re.search(r"(\d+\.\d+\.\d+)", out)
    info["hermes_version"] = out.strip() or "unknown"
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


def unique_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid JSON number")))


def load_record(tpl_name: str) -> dict | None:
    p = record_dir(tpl_name) / "record.json"
    checked_path(p, hermes_home())
    if not p.exists():
        return None
    try:
        result = unique_json(p.read_bytes())
        if not isinstance(result, dict):
            raise ValueError()
        return result
    except (OSError, ValueError):
        raise SystemExit("Installation record is unreadable or malformed; restore it before retry.") from None


def save_record(tpl_name: str, rec: dict) -> None:
    d = record_dir(tpl_name)
    checked_path(d, hermes_home())
    checked_path(d / "record.json", d)
    checked_path(d / "record.json.tmp", d)
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / "record.json.tmp"
    with tmp.open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(rec, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, d / "record.json")
    fd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


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

def checked_path(path: Path, root: Path) -> Path:
    """Reject escapes and symlinks before reading or writing installer-owned trees."""
    path, root = path.absolute(), root.absolute()
    if ".." in path.parts or ".." in root.parts:
        raise SystemExit(f"Shared skills conflict: parent traversal in {path}")
    if not path.is_relative_to(root):
        raise SystemExit(f"Shared skills conflict: path escapes owned root: {path}")
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise SystemExit(f"Shared skills conflict: symlink at {part}; resolve it manually.")
    return path


def package_hashes(path: Path) -> dict[str, str]:
    checked_path(path, path)
    result = {}
    for f in sorted(path.rglob("*")):
        checked_path(f, path)
        if f.is_file():
            result[f.relative_to(path).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
        elif not f.is_dir():
            raise SystemExit(f"Shared skills conflict: unsupported file at {f}")
    return result


def skill_packages(root: Path) -> dict[str, Path]:
    """Index package and frontmatter names; never silently choose one duplicate."""
    checked_path(root, root)
    result = {}
    for md in sorted(root.rglob("SKILL.md")):
        if any(p.startswith(".") for p in md.relative_to(root).parts):
            continue
        checked_path(md, root)
        text = md.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1]) if text.startswith("---\n") else {}
        for name in {md.parent.name, str((front or {}).get("name", md.parent.name))}:
            if name in result and result[name] != md.parent:
                raise SystemExit(f"Shared skills conflict: duplicate name {name} in {root}")
            result[name] = md.parent
    return result


def native_skills() -> dict:
    """Resolve stock from the installed Hermes Python, not any user's skills tree."""
    try:
        import inspect
        import hermes_cli
        sys.path.insert(0, str(Path(hermes_cli.__file__).resolve().parent.parent))
        from tools import skills_sync as native
        from agent import skill_utils
        from hermes_cli import profile_distribution
        from hermes_cli.version_info import get_version_info
        assert native.NO_BUNDLED_SKILLS_MARKER == ".no-bundled-skills"
        assert "hermes-agent" in native.ESSENTIAL_SKILLS
        assert callable(native._matches_origin_hash)
        assert "include_runtime_cache" in inspect.signature(native._dir_hash).parameters
        assert callable(skill_utils.get_external_skills_dirs)
        assert callable(skill_utils.get_disabled_skill_names)
        assert "essential_only" in inspect.getsource(native.sync_skills)
        assert "preserve_config" in inspect.getsource(profile_distribution.update_distribution)
        root = native._get_bundled_dir().absolute()
        checked_path(root, root)
        # An override pointing at personal/hub content is not proof of bundled provenance.
        shipped_root = Path(native.__file__).resolve().parent.parent / "skills"
        if root != shipped_root:
            raise ValueError("unverified bundled-source override; use the installed Hermes stock source")
        home = hermes_home().absolute()
        if root == home / "skills" or root.is_relative_to(home / "profiles"):
            raise ValueError("the bundled resolver points into a user profile")
        packages = skill_packages(root)
        if "hermes-agent" not in packages:
            raise ValueError("essential hermes-agent package missing")
        version = get_version_info()
        return {"root": root, "packages": packages,
                "matches": lambda p, expected: bool(expected) and native._dir_hash(p, include_runtime_cache=True) == expected,
                "source": str(root), "module": native, "version": version.derived_version,
                "commit": version.commit}
    except (ImportError, AttributeError, AssertionError, ValueError) as exc:
        raise SystemExit("Shared skills need Hermes native external_dirs, essential-only bundled sync and "
                         "profile distributions. Upgrade Hermes and run hbt with its Python "
                         "(HBT_PYTHON=<Hermes Python>); no changes made. " + str(exc)) from exc


def shared_state(tpl_name: str, rec: dict) -> dict:
    state = rec.get("shared_skills", {})
    expected = record_dir(tpl_name) / "skills"
    checked_path(expected, hermes_home())
    if "shared_skills" in rec and (not isinstance(state, dict) or state.get("schema") != 1
                                   or state.get("root") != str(expected.absolute())):
        raise SystemExit("Shared skills conflict: unknown schema or changed install root; restore the original record.")
    for rel in state.get("packages", {}):
        checked_path(expected / rel, expected)
        if Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise SystemExit("Shared skills conflict: invalid recorded package path")
    for name, entry in state.get("profiles", {}).items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            raise SystemExit("Shared skills conflict: invalid recorded profile name")
        selected_paths = set()
        for rel in entry.get("selected", []):
            if not rel.startswith(("template/", "bundled/")) or Path(rel).name == "hermes-agent":
                raise SystemExit("Shared skills conflict: invalid recorded selection")
            selected_paths.add(str(checked_path(expected / rel, expected)))
        if any(p not in selected_paths for p in entry.get("managed", [])):
            raise SystemExit("Shared skills conflict: managed path is outside the recorded selection")
    return state


def profile_skill_path(entry: str, prof: Path) -> Path:
    """Resolve native skill paths without borrowing the installer's HERMES_HOME."""
    entry = re.sub(r"\$(?:\{HERMES_HOME\}|HERMES_HOME\b)", lambda _: str(prof), entry.strip())
    path = Path(os.path.expandvars(entry)).expanduser()
    return path if path.is_absolute() else prof / path


def plan_shared_skills(tpl: Template, roles: list[Role], rec: dict, native: dict, fresh: bool = False) -> dict:
    """Read-only preflight. Capture old distribution provenance before any restaging."""
    previous = shared_state(tpl.name, rec)
    root = record_dir(tpl.name) / "skills"
    package_hashes(root)
    package_hashes(record_dir(tpl.name) / "dist")
    state = copy.deepcopy(previous) if previous else {
        "schema": 1, "root": str(root.absolute()), "packages": {}, "profiles": {}, "backups": []}
    state.update(source=native["source"], source_version=rec.get("hermes_version", "unknown"),
                 source_commit=native.get("commit"), migration="planned")
    sources, removals, source_names = {}, {}, {}
    state["conflicts"] = []
    for role in roles:
        name = tpl.profile(role.key)
        prof = checked_path(hermes_home() / "profiles" / name, hermes_home() / "profiles")
        local = skill_packages(prof / "skills")
        package_hashes(prof / "skills")
        for filename in ("config.yaml", ".no-bundled-skills", "skills/.bundled_manifest"):
            checked_path(prof / filename, prof)
        cfg = _profile_cfg(name)
        skills = cfg.get("skills", {})
        if not isinstance(skills, dict):
            raise SystemExit(f"{name}: skills settings must be a mapping; no changes made.")
        ext = skills.get("external_dirs", [])
        if not isinstance(ext, list) or any(not isinstance(p, str) for p in ext):
            raise SystemExit(f"{name}: skills.external_dirs must be a YAML list of paths; no changes made.")
        old = state["profiles"].get(name)
        if old is None:
            old = {"original_skills": copy.deepcopy(skills), "skills_present": "skills" in cfg,
                   "original_marker": (prof / ".no-bundled-skills").read_text()
                   if (prof / ".no-bundled-skills").exists() else None, "managed": [], "selected": []}
            state["profiles"][name] = old
        custom_ext = [p for p in ext if p not in old["managed"]]
        external = set()
        for entry in custom_ext:
            if not entry.strip():
                continue
            p = profile_skill_path(entry, prof)
            names = set(skill_packages(p))
            if names & external:
                state["conflicts"].append(f"{name}: pre-existing external ambiguity retained: {', '.join(sorted(names & external))}")
            external.update(names)
        if external & set(local):
            state["conflicts"].append(f"{name}: pre-existing local/external ambiguity retained: {', '.join(sorted(external & set(local)))}")
        manifest_path = prof / "skills" / ".bundled_manifest"
        manifest = dict(line.split(":", 1) for line in manifest_path.read_text().splitlines() if ":" in line) \
            if manifest_path.exists() else {}
        authored = skill_packages(tpl.path / "roles" / role.key / "skills")
        staged = record_dir(tpl.name) / "dist" / name
        staged_manifest = staged / "distribution.yaml"
        installed_manifest = checked_path(prof / "distribution.yaml", prof)
        installed_origin = (yaml.safe_load(installed_manifest.read_text()) or {}) if installed_manifest.exists() else {}
        baseline_ok = (installed_origin.get("source") == str(staged) and staged_manifest.is_file()
                       and str((yaml.safe_load(staged_manifest.read_text()) or {}).get("version")) == rec.get("version"))
        baseline = skill_packages(staged / "skills") if baseline_ok else {}
        selected = list(old["selected"]) if previous else []
        # Validate defaults even during migration, but never resurrect deleted old packages.
        missing = [s for s in role.stock_skills if s not in native["packages"]]
        if missing:
            raise SystemExit(f"Upgrade Hermes: required bundled packages missing: {', '.join(missing)}. No changes made.")
        if not previous:
            for skill, src in authored.items():
                if skill != src.name:
                    continue
                if fresh or skill in local:
                    selected.append(f"template/{role.key}/{src.name}")
            stock = role.stock_skills if fresh else [s for s in manifest if s in local and s in native["packages"]
                                                     and re.fullmatch(r"[0-9a-f]{32,64}", manifest[s])]
            selected += ["bundled/" + native["packages"][s].relative_to(native["root"]).as_posix()
                         for s in stock if s != "hermes-agent"]
        old["selected"] = list(dict.fromkeys(selected))
        old["managed"] = []
        removals[name] = []
        for rel in old["selected"]:
            dest = checked_path(root / rel, root)
            if Path(rel).is_absolute() or ".." in Path(rel).parts:
                raise SystemExit("Shared skills conflict: invalid selection")
            src = tpl.path / "roles" / role.key / "skills" / dest.name if rel.startswith("template/") \
                else native["packages"].get(dest.name)
            if src is None or not (src / "SKILL.md").is_file():
                raise SystemExit(f"Upgrade Hermes or restore source: missing selected package {rel}")
            hashes = package_hashes(src)
            if rel in sources and sources[rel] != src:
                raise SystemExit(f"Shared skills conflict: same-name sources for {rel}")
            sources[rel] = src
            prior = previous.get("packages", {}).get(rel)
            current = package_hashes(dest) if dest.exists() else {}
            conflict = dest.exists() and (not prior or any(prior["hashes"].get(k) != v for k, v in current.items()))
            if conflict:
                state["conflicts"].append(f"shared:{rel}: modified/unowned library package retained")
            else:
                state["packages"][rel] = {"hashes": hashes}
            aliases = set(skill_packages(src))
            for alias in aliases:
                if alias in source_names and source_names[alias] != src:
                    raise SystemExit(f"Shared skills conflict: same-name source collision: {alias}")
                source_names[alias] = src
            shadows = {local[s] for s in aliases if s in local}
            safe = not (aliases & external)
            if not safe:
                state["conflicts"].append(f"{name}:{dest.name}: custom external source retained")
            for path in shadows:
                package_hashes(path)  # validate the whole tree, including added support files
                origin = baseline.get(dest.name)
                pristine = (origin is not None and package_hashes(path) == package_hashes(origin)) \
                    if rel.startswith("template/") else native["matches"](path, manifest.get(dest.name, ""))
                # Once migrated, a new local shadow belongs to the user even if bytes match stock.
                if previous or not pristine:
                    safe = False
                    state["conflicts"].append(f"{name}:{dest.name}: customized/unknown local package retained at {path}")
                elif not conflict:
                    removals[name].append(path)
            if safe and not conflict:
                old["managed"].append(str(dest.absolute()))
            elif safe and conflict and str(dest.absolute()) in (previous.get("profiles", {}).get(name, {}).get("managed", [])):
                old["managed"].append(str(dest.absolute()))
        old["external_dirs"] = custom_ext + old["managed"]
        # Never remove a local copy unless this profile will receive its shared replacement.
        removals[name] = [p for p in removals[name] if any(Path(e).name == p.name for e in old["managed"])]
    state["conflicts"] = sorted(set(state["conflicts"]))
    for conflict in state["conflicts"]:
        say("  CONFLICT " + conflict)
    for name, entry in state["profiles"].items():
        say(f"  {name}: {len(entry['selected'])} selected, {len(entry['managed'])} shared paths; "
            f"archive/remove {len(removals.get(name, []))} pristine local packages; enable bundled opt-out")
    return {"state": state, "sources": sources, "removals": removals}


def preview_shared_skills(plan: dict) -> None:
    state = plan["state"]
    for rel, source in plan["sources"].items():
        say(f"  would verify/repair owned shared package: {source} -> {Path(state['root']) / rel}; retain conflicts")
    for name, paths in plan["removals"].items():
        for path in paths:
            say(f"  would archive then remove pristine local package: {path}")
        entry = state["profiles"][name]
        say(f"  would set {name} skills.external_dirs to YAML list: {json.dumps(entry['external_dirs'])}")
        say(f"  would preserve {name} other skills settings and original marker; set native bundled opt-out")


def seed_shared_manual(native: dict, name: str) -> None:
    env = dict(os.environ, HERMES_HOME=str(hermes_home() / "profiles" / name),
               HERMES_DISABLE_LAZY_INSTALLS="1", PYTHONDONTWRITEBYTECODE="1")
    source = str(Path(native["module"].__file__).resolve().parent.parent)
    code = "import sys; sys.path.insert(0, sys.argv[1]); from tools.skills_sync import sync_skills; sync_skills(quiet=True)"
    subprocess.run([sys.executable, "-c", code, source], env=env, check=True, timeout=60)


def configure_desk_skills(tpl: Template, rec: dict, name: str, native: dict) -> None:
    """Desks gain no shared roots or mounts, only native essential-only seeding."""
    state = shared_state(tpl.name, rec)
    if not state:
        raise SystemExit("Update the template before adding a desk: shared skill ownership is not recorded.")
    prof = checked_path(hermes_home() / "profiles" / name, hermes_home() / "profiles")
    marker = checked_path(prof / ".no-bundled-skills", prof)
    cfg = _profile_cfg(name)
    skills = cfg.get("skills") or {}
    state["profiles"].setdefault(name, {"original_skills": copy.deepcopy(skills),
        "skills_present": "skills" in cfg, "original_marker": marker.read_text() if marker.exists() else None,
        "selected": [], "managed": [], "external_dirs": list(skills.get("external_dirs", []))})
    save_record(tpl.name, rec)
    marker.write_text("hbt shared skills\n")
    seed_shared_manual(native, name)


def atomic_yaml(path: Path, y, data) -> None:
    checked_path(path, path.parent)
    out = io.StringIO()
    y.dump(data, out)
    temp = path.with_name(path.name + ".hbt-" + uuid.uuid4().hex)
    temp.write_text(out.getvalue(), encoding="utf-8")
    os.replace(temp, path)


def backup_skill_state(tpl_name: str, rec: dict) -> Path:
    """Durable full-package snapshot; never reuse/overwrite a previous recovery copy."""
    dest = checked_path(record_dir(tpl_name) / "backups" / ("skills-" + uuid.uuid4().hex), hermes_home())
    dest.mkdir(parents=True, mode=0o700)
    for name in rec.get("profiles", []):
        src = checked_path(hermes_home() / "profiles" / name, hermes_home() / "profiles")
        for item in ("skills", "config.yaml", ".no-bundled-skills", "distribution.yaml"):
            p, target = src / item, dest / "profiles" / name / item
            checked_path(p, src)
            if p.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if p.is_dir():
                    package_hashes(p)
                    # An earlier profile's external root may already have
                    # archived packages from this same profile tree.
                    shutil.copytree(p, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(p, target)
        # Only archive skill packages in profile trees that native deletion removes.
        # Outside roots remain in place; never copy arbitrary files from a root.
        settings = _profile_cfg(name).get("skills") or {}
        roots = settings.get("external_dirs", [])
        if not isinstance(roots, list) or any(not isinstance(p, str) for p in roots):
            raise SystemExit(f"{name}: invalid external_dirs; cannot safely archive skills")
        create_dir = settings.get("create_dir")
        if create_dir is not None and not isinstance(create_dir, str):
            raise SystemExit(f"{name}: invalid create_dir; cannot safely archive skills")
        for raw in roots + ([create_dir] if create_dir else []):
            if not raw.strip():
                continue
            root = profile_skill_path(raw, src)
            for owner in rec.get("profiles", []):
                removed = checked_path(hermes_home() / "profiles" / owner, hermes_home() / "profiles")
                if root.is_relative_to(removed):
                    endangered = checked_path(root, removed)
                elif removed.is_relative_to(root):
                    # Native discovery can start above a deleted profile. Limit
                    # enumeration to its endangered subtree, not outside packages.
                    checked_path(root, root)
                    endangered = removed
                else:
                    continue
                for package in set(skill_packages(endangered).values()):
                    target = dest / "profiles" / owner / package.relative_to(removed)
                    hashes = package_hashes(package)
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(package, target)
                    if package_hashes(target) != hashes:
                        raise SystemExit(f"Skill archive verification failed: {package}; deletion refused")
    for item in ("dist", "skills"):
        src = record_dir(tpl_name) / item
        if src.exists():
            package_hashes(src)
            shutil.copytree(src, dest / item)
    (dest / "record.json").write_text(json.dumps(rec, indent=2) + "\n")
    say(f"  recovery archive: {dest}")
    return dest


def apply_shared_skills(tpl: Template, rec: dict, plan: dict) -> None:
    """Publish verified packages, then each profile; journal removals for interrupted retries."""
    state = plan["state"]
    backup = backup_skill_state(tpl.name, rec)
    state["backups"].append(str(backup))
    state["migration"] = "activating"
    rec["shared_skills"] = state
    rec["shared_skills"]["pending"] = {"backup": str(backup), "removals": {
        name: [str(p) for p in paths] for name, paths in plan["removals"].items()}}
    save_record(tpl.name, rec)
    root = Path(state["root"])
    for rel, src in plan["sources"].items():
        dest = root / rel
        want = state["packages"].get(rel, {}).get("hashes")
        if want != package_hashes(src):  # retained modified/unowned package
            continue
        if dest.exists() and package_hashes(dest) != want:
            old = (json.loads((backup / "record.json").read_text()).get("shared_skills") or {}).get("packages", {}).get(rel)
            if not old or any(old["hashes"].get(k) != v for k, v in package_hashes(dest).items()):
                continue
        if dest.exists() and package_hashes(dest) == want:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        staging = dest.with_name("." + dest.name + ".hbt-" + uuid.uuid4().hex)
        shutil.copytree(src, staging)
        if package_hashes(staging) != want:
            raise SystemExit(f"Package verification failed: {rel}; archive: {backup}")
        if dest.exists():
            shutil.rmtree(dest)  # already snapshotted and verified pristine
        os.replace(staging, dest)
    for name, entry in state["profiles"].items():
        prof = hermes_home() / "profiles" / name
        if not prof.exists() or name in rec.get("desks", {}):
            continue  # fresh install activates after native profile creation
        activate_shared_profile(tpl, rec, name, plan["removals"].get(name, []))
    state.pop("pending", None)
    state["migration"] = "conflicts" if state["conflicts"] else "active"
    save_record(tpl.name, rec)


def activate_shared_profile(tpl: Template, rec: dict, name: str, removals: list[Path]) -> None:
    entry = rec["shared_skills"]["profiles"][name]
    prof = hermes_home() / "profiles" / name
    y, cfg = load_yaml_rt(prof / "config.yaml")
    cfg.setdefault("skills", {})["external_dirs"] = entry["external_dirs"]
    # The journal and archive exist before removal. Recovery also handles partial deletion.
    for path in removals:
        shutil.rmtree(path)
    atomic_yaml(prof / "config.yaml", y, cfg)
    (prof / ".no-bundled-skills").write_text("hbt shared skills\n")


def recover_shared_skills(tpl_name: str, rec: dict, dry: bool) -> None:
    state = shared_state(tpl_name, rec)
    pending = state.get("pending")
    if not pending:
        return
    backup = checked_path(Path(pending["backup"]), record_dir(tpl_name) / "backups")
    say(f"  interrupted skill activation: recovery archive {backup}")
    if dry:
        raise SystemExit("Recovery required before planning: run update without --dry-run to restore the checkpoint.")
    original = json.loads(checked_path(backup / "record.json", backup).read_text())
    for name, paths in pending["removals"].items():
        prof = checked_path(hermes_home() / "profiles" / name, hermes_home() / "profiles")
        if not prof.exists():
            continue
        y, cfg = load_yaml_rt(prof / "config.yaml")
        ext = cfg.setdefault("skills", {}).get("external_dirs", [])
        old_cfg_path = checked_path(backup / "profiles" / name / "config.yaml", backup)
        old_cfg = yaml.safe_load(old_cfg_path.read_text()) or {} if old_cfg_path.exists() else {}
        old_skills = old_cfg.get("skills") or {}
        old_ext = old_skills.get("external_dirs", [])
        if ext not in (old_ext, state["profiles"][name]["external_dirs"]):
            raise SystemExit(f"Recovery conflict: {name} external_dirs changed since checkpoint; retained. Archive: {backup}")
        if "external_dirs" in old_skills:
            cfg["skills"]["external_dirs"] = old_ext
        else:
            cfg["skills"].pop("external_dirs", None)
        if not cfg["skills"] and "skills" not in old_cfg:
            cfg.pop("skills")
        atomic_yaml(prof / "config.yaml", y, cfg)
        for raw in paths:
            dst = checked_path(Path(raw), prof / "skills")
            src = checked_path(backup / "profiles" / name / dst.relative_to(prof), backup)
            expected = package_hashes(src)
            actual = package_hashes(dst)
            if not (src / "SKILL.md").is_file():
                raise SystemExit(f"Recovery conflict: incomplete archive for {dst}; retained journal: {backup}")
            if any(expected.get(k) != v for k, v in actual.items()):
                raise SystemExit(f"Recovery conflict: owner edits at {dst}; retained journal: {backup}")
            # Restore missing bytes only. Never overwrite surviving or newly edited files.
            for rel in expected:
                target = checked_path(dst / rel, dst)
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src / rel, target)
            if package_hashes(dst) != expected:
                raise SystemExit(f"Recovery verification failed: {dst}; retained journal: {backup}")
        marker = prof / ".no-bundled-skills"
        old_marker = checked_path(backup / "profiles" / name / ".no-bundled-skills", backup)
        if marker.exists() and marker.read_text() == "hbt shared skills\n":
            if old_marker.exists():
                shutil.copy2(old_marker, marker)
            else:
                marker.unlink()
    root = record_dir(tpl_name) / "skills"
    for rel, info in state["packages"].items():
        dest = checked_path(root / rel, root)
        old_package = backup / "skills" / rel
        actual = package_hashes(dest)
        before = package_hashes(old_package)
        if actual and actual not in (info["hashes"], before):
            raise SystemExit(f"Recovery conflict at {dest}; owner edits retained. Archive: {backup}")
        if dest.exists():
            shutil.rmtree(dest)
        if old_package.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(old_package, dest)
    if original.get("shared_skills"):
        rec["shared_skills"] = original["shared_skills"]
    else:
        rec.pop("shared_skills", None)
    save_record(tpl_name, rec)


def shared_gaps(tpl_name: str, rec: dict) -> list[str]:
    state = shared_state(tpl_name, rec)
    if not state:
        return []
    gaps = ["Shared skills conflict: " + c + ". See recovery archives and README; update does not overwrite custom work."
            for c in state.get("conflicts", [])]
    if state.get("migration") == "activating":
        gaps.append("Shared skills activation interrupted. Fix: hbt update " + tpl_name)
    root = Path(state["root"])
    for rel, info in state["packages"].items():
        if package_hashes(root / rel) != info["hashes"]:
            gaps.append(f"Shared skills: missing/changed package {rel}. Fix: hbt update {tpl_name}; customized files are retained.")
    for name, entry in state["profiles"].items():
        prof = hermes_home() / "profiles" / name
        cfg = _profile_cfg(name)
        ext = (cfg.get("skills") or {}).get("external_dirs", [])
        local = skill_packages(prof / "skills")
        if not (prof / ".no-bundled-skills").exists():
            gaps.append(f"{name}: bundled opt-out missing. Fix: hbt update {tpl_name}")
        if "hermes-agent" not in local:
            gaps.append(f"{name}: local hermes-agent missing. Fix: preserve any manual edits, then "
                        f"hermes -p {name} skills reset hermes-agent --restore.")
        seen = set(local)
        for path in ext:
            if not path.strip():
                continue
            p = profile_skill_path(path, prof)
            names = set(skill_packages(p))
            duplicate = names & seen
            if duplicate:
                gaps.append(f"{name}: duplicate/ambiguous local or external skills: {', '.join(sorted(duplicate))}. Fix: hbt update {tpl_name} and resolve retained sources manually.")
            seen.update(names)
        for path in entry["managed"]:
            if path not in ext or not Path(path).is_dir():
                gaps.append(f"{name}: selected root missing: {path}. Fix: hbt update {tpl_name}")
    return gaps

def uninstall_shared_skills(tpl_name: str, rec: dict, dry: bool) -> None:
    state = shared_state(tpl_name, rec)
    if dry:
        say("  would archive all local skills/settings and remove only recorded pristine shared assets")
        return
    archive = backup_skill_state(tpl_name, rec)
    rec.setdefault("skill_uninstall_archives", []).append(str(archive))
    for name, entry in state.get("profiles", {}).items():
        prof = hermes_home() / "profiles" / name
        if not prof.exists():
            continue
        y, cfg = load_yaml_rt(prof / "config.yaml")
        skills = cfg.get("skills", {})
        current = skills.get("external_dirs", [])
        if isinstance(current, list):
            remaining = [p for p in current if p not in entry["managed"]]
            if not remaining and "external_dirs" not in entry["original_skills"]:
                skills.pop("external_dirs", None)
            else:
                skills["external_dirs"] = remaining
        if not skills and not entry["skills_present"]:
            cfg.pop("skills", None)
        atomic_yaml(prof / "config.yaml", y, cfg)
        marker = prof / ".no-bundled-skills"
        if marker.exists() and marker.read_text() == "hbt shared skills\n":
            if entry["original_marker"] is None:
                marker.unlink()
            else:
                marker.write_text(entry["original_marker"])
        restored = archive / "restored" / name
        restored.mkdir(parents=True)
        shutil.copy2(prof / "config.yaml", restored / "config.yaml")
    root = record_dir(tpl_name) / "skills"
    for rel, info in state.get("packages", {}).items():
        dest = checked_path(root / rel, root)
        if dest.exists() and package_hashes(dest) == info["hashes"]:
            shutil.rmtree(dest)
        elif dest.exists():
            say(f"  retained modified shared package: {dest}")
    say(f"  custom local skills/settings retained in {archive}; removed profiles no longer load them")
    say(f"  any unrecognized shared content remains at {root}")
    save_record(tpl_name, rec)


def stage_distribution(tpl: Template, role: Role, name: str | None = None) -> Path:
    """Copy the role's distribution to a stable place, so `hermes profile update` can find it again."""
    dest = record_dir(tpl.name) / "dist" / (name or tpl.profile(role.key))
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(tpl.path / "roles" / role.key, dest, ignore=shutil.ignore_patterns("skills"))
    return dest


# --------------------------------------------------------------------------- Slack

SLACK_ID = re.compile(r"[UW][A-Z0-9]{6,}")


def slack_api(token: str, method: str, **params: str) -> dict:
    """Call one Slack Web API method. The token travels in a header and is never printed."""
    import urllib.parse
    import urllib.request
    req = urllib.request.Request(f"https://slack.com/api/{method}", data=urllib.parse.urlencode(params).encode(),
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"could not reach Slack ({type(exc).__name__})"}


def find_channels(token: str, names: list[str]) -> dict[str, dict]:
    """{name: {"id", "member"}} for the named channels this bot can see."""
    found: dict[str, dict] = {}
    cursor = ""
    while True:
        res = slack_api(token, "conversations.list", types="public_channel,private_channel",
                        exclude_archived="true", limit="1000", cursor=cursor)
        if not res.get("ok"):
            raise SystemExit(f"Slack refused the channel list ({res.get('error')}). "
                             "Was the app created from the manifest and installed to the workspace?")
        for c in res.get("channels", []):
            if c.get("name") in names:
                found[c["name"]] = {"id": c["id"], "member": bool(c.get("is_member"))}
        cursor = (res.get("response_metadata") or {}).get("next_cursor") or ""
        if not cursor:
            return found


def token_holder(token: str) -> str:
    """The profile that already holds this bot token ('main' for the main agent), or ''.
    Two profiles with one token is a fatal duplicate for the Hermes gateway."""
    if token == read_env_value(hermes_home() / ".env", "SLACK_BOT_TOKEN"):
        return "main"
    for env in sorted((hermes_home() / "profiles").glob("*/.env")):
        if read_env_value(env, "SLACK_BOT_TOKEN") == token:
            return env.parent.name
    return ""


def ask_tokens(title: str, profile: str) -> tuple[str, str]:
    import getpass
    bot = getpass.getpass(f"{title} bot token, starts with xoxb- (hidden): ").strip()
    app = getpass.getpass(f"{title} app token, starts with xapp- (hidden): ").strip()
    if not (bot.startswith("xoxb-") and app.startswith("xapp-")):
        raise SystemExit("Those do not look like Slack tokens. Nothing was saved.")
    holder = token_holder(bot)
    if holder and holder != profile:
        raise SystemExit(f"That bot token already belongs to {'your main agent' if holder == 'main' else holder}. "
                         f"{title} needs its own Slack app. Nothing was saved.")
    return bot, app


def write_manifest(r: Runner, tpl: Template, title: str, name: str, *extra: str) -> Path:
    """The stock Hermes Slack manifest for this bot, plus reactions:write so it can mark what it picked up."""
    path = record_dir(tpl.name) / f"{name}-slack-manifest.json"
    r.hermes_cmd("slack", "manifest", "--name", title, "--description", f"{tpl.title}: {title}", *extra,
                 "--write", str(path), profile=name)
    if path.exists():
        m = json.loads(path.read_text(encoding="utf-8"))
        scopes = m.setdefault("oauth_config", {}).setdefault("scopes", {}).setdefault("bot", [])
        if "reactions:write" not in scopes:
            scopes.append("reactions:write")
            path.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    return path


def apply_slack(r: Runner, tpl: Template, role: Role, rec: dict, dry: bool) -> None:
    name = tpl.profile(role.key)
    cfg, env = slack_settings(role, rec.get("channels") or {}, rec.get("owner", ""), rec.get("bots") or {})
    for k, v in cfg.items():
        r.hermes_cmd("config", "set", k, v, profile=name)
    set_env_values(hermes_home() / "profiles" / name / ".env", env, dry)


def wire_system_channel(r: Runner, tpl: Template, rec: dict, dry: bool) -> bool:
    """Point Ops at the system channel: a route through the main agent's bot, and job delivery.
    Ops has no Slack app of its own. Returns True when a gateway restart is needed."""
    ops, cid = tpl.ops, (rec.get("channels") or {}).get(tpl.system_channel)
    installed = [x for x in tpl.roles if tpl.profile(x.key) in rec["profiles"]]
    routes = []
    if ops and cid and tpl.profile(ops.key) in rec["profiles"]:
        routes = [{"name": f"{ROUTE_TAG}{tpl.name}:{ops.key}", "platform": "slack", "chat_id": cid,
                   "profile": tpl.profile(ops.key)}]
        for j in rec.get("jobs", []):
            if j.get("id") and j.get("key") != MEMORY_REVIEW_KEY:
                r.hermes_cmd("cron", "edit", j["id"], "--deliver", f"slack:{cid}", profile=j["profile"])
    changes = edit_main_config(hermes_home() / "config.yaml", routes, dispatch=True, dry=dry,
                               backup_dir=record_dir(tpl.name) / "backups", previous=rec.get("main_config"),
                               card_profiles=[tpl.profile(x.key) for x in installed if x.takes_cards])
    added = list(changes["routes_added"])
    old = list((rec.get("main_config") or {}).get("routes_added", []))
    changes["routes_added"] = old + [n for n in added if n not in old]
    rec["main_config"] = changes
    return bool(added)


# --------------------------------------------------------------------------- commands

def memory_review_policy(tpl: Template, rec: dict, mode: str | None) -> dict:
    previous = rec.get("memory_review")
    if previous is not None and (not isinstance(previous, dict) or type(previous.get("schema_version")) is not int or previous.get("schema_version") != 1
            or previous.get("mode") not in MEMORY_REVIEW_MODES or previous.get("install_root") != str(hermes_home())):
        raise SystemExit("Memory review policy is invalid; restore the installation record before retry.")
    if mode is not None and mode not in MEMORY_REVIEW_MODES:
        raise SystemExit("Unknown memory review mode.")
    if previous is not None:
        enrollment = previous.get("enrolled")
        permitted = {tpl.profile(role.key) for role in tpl.roles if role.kind != "ops"} & set(rec["profiles"])
        if (not isinstance(enrollment, list) or any(not isinstance(n, str) or n not in permitted for n in enrollment)
                or len(enrollment) != len(set(enrollment)) or not isinstance(previous.get("policy_at"), str)
                or not isinstance(previous.get("job"), dict)):
            raise SystemExit("Memory review enrollment or ownership record is invalid; restore it before retry.")
    result = copy.deepcopy(previous) if previous else {
        "schema_version": 1, "mode": "off", "install_root": str(hermes_home()),
        "state_path": str(record_dir(tpl.name) / "memory-review/state.json"),
        "recovery_path": str(record_dir(tpl.name) / "backups/memory-review"),
        "policy_at": now_iso(), "enrolled": [], "job": {}}
    if mode is not None:
        result["mode"], result["policy_at"] = mode, now_iso()
    result["enrolled"] = [tpl.profile(role.key) for role in tpl.roles
        if role.kind != "ops" and tpl.profile(role.key) in rec["profiles"]]
    for key, relative in (("state_path", "memory-review/state.json"), ("recovery_path", "backups/memory-review")):
        if result.get(key) != str(record_dir(tpl.name) / relative):
            raise SystemExit("Memory review path changed; restore the recorded installation root.")
        checked_path(Path(result[key]), hermes_home())
    return result


def create_memory_review_job(policy: dict) -> dict:
    """Use native cron in an Ops-scoped process with a persisted ownership nonce."""
    import hermes_cli
    source = str(Path(hermes_cli.__file__).resolve().parent.parent)
    code = ("import json,sys; sys.path.insert(0,sys.argv[1]); from cron.jobs import create_job; "
            "p=json.load(sys.stdin); j=create_job(None,'30 21 * * *',name='hbt:creator:memory-draft-review',"
            "script='hbt_memory_review.py',no_agent=True,deliver='local',failure_deliver='local',"
            "origin={'hbt_owner':p['job']['owner']},paused=True,paused_reason='Memory review requires explicit owner opt-in'); "
            "print(json.dumps(j))")
    result = subprocess.run([sys.executable, "-c", code, source], input=json.dumps(policy), text=True,
        capture_output=True, timeout=60, env={**os.environ, "HERMES_HOME": str(hermes_home() / "profiles/ops")})
    if result.returncode:
        raise SystemExit("Native memory-review job creation failed; retry update to reconcile the ownership checkpoint.")
    return json.loads(result.stdout)


def sync_memory_review(tpl: Template, rec: dict, mode: str | None, runner: Runner) -> None:
    with uninstall_review_lock(tpl.name, runner.dry_run):
        _sync_memory_review_locked(tpl, rec, mode, runner)


def _sync_memory_review_locked(tpl: Template, rec: dict, mode: str | None, runner: Runner) -> None:
    policy = memory_review_policy(tpl, rec, mode)
    if not tpl.ops or tpl.profile(tpl.ops.key) not in rec["profiles"]:
        return
    jobs = read_jobs_without_bootstrap("ops")
    identity = policy["job"]
    same_name = [j for j in jobs if j.get("name") == f"{ROUTE_TAG}{tpl.name}:{MEMORY_REVIEW_KEY}"]
    current = None
    if identity.get("id"):
        current = next((j for j in jobs if j["id"] == identity["id"]), None)
    elif identity.get("owner"):
        matches = [j for j in jobs if j.get("origin") == {"hbt_owner": identity["owner"]}]
        if len(matches) > 1:
            raise SystemExit("Memory review ownership checkpoint is ambiguous; reconcile jobs manually.")
        current = matches[0] if matches else None
    if same_name and (len(same_name) != 1 or same_name[0] != current):
        raise SystemExit("Memory review found a same-name job without exact ownership; no adoption or deletion is authorized.")
    if current and (current.get("origin") != {"hbt_owner": identity.get("owner")}
            or current.get("name") != f"{ROUTE_TAG}{tpl.name}:{MEMORY_REVIEW_KEY}"
            or current.get("script") != "hbt_memory_review.py" or current.get("no_agent") is not True
            or current.get("deliver") != "local" or current.get("failure_deliver", "local") != "local"
            or (identity.get("created_at") and identity["created_at"] != current.get("created_at"))):
        raise SystemExit("Memory review job identity or local-only delivery changed; resolve the conflict before retry.")
    if runner.dry_run:
        say(f"  would set memory review policy: {policy['mode']}; local job only; preserve owner pauses/deletions")
        return
    rec["memory_review"] = policy
    settings_path = checked_path(hermes_home() / "profiles/ops/hbt-settings.json", hermes_home())
    settings = json.loads(settings_path.read_bytes())
    if "install_root" in settings and settings["install_root"] != str(hermes_home()):
        raise SystemExit("Ops install-root reference conflicts with this installation; owner settings were retained.")
    settings["install_root"] = str(hermes_home())
    from utils import atomic_json_write
    atomic_json_write(settings_path, settings)
    save_record(tpl.name, rec)
    if current is None and not identity.get("id"):
        identity.setdefault("owner", uuid.uuid4().hex)
        save_record(tpl.name, rec)
        current = create_memory_review_job(policy)
    if current is None:
        say("  memory review job was deleted by its owner; kept deleted")
        return
    identity.update({"id": current["id"], "profile": "ops", "created_at": current["created_at"],
        "script": current["script"], "deliver": current["deliver"], "schedule": current["schedule"],
        "enabled": current["enabled"], "state": current["state"]})
    entry = {"key": MEMORY_REVIEW_KEY, "id": current["id"], "profile": "ops"}
    existing = [j for j in rec["jobs"] if j.get("key") == MEMORY_REVIEW_KEY]
    if existing and existing != [entry]:
        raise SystemExit("Memory review recorded job identities disagree; reconcile the record.")
    if not existing:
        rec["jobs"].append(entry)
    save_record(tpl.name, rec)
    if policy["mode"] == "off":
        runner.hermes_cmd("cron", "pause", current["id"], profile="ops")
    elif mode is not None:
        runner.hermes_cmd("cron", "resume", current["id"], profile="ops")
    verified = next((j for j in read_jobs_without_bootstrap("ops") if j["id"] == current["id"]), None)
    if verified is None or verified.get("deliver") != "local" or verified.get("script") != "hbt_memory_review.py":
        raise SystemExit("Memory review job readback failed; inspect the recorded ownership checkpoint.")
    if policy["mode"] == "off" and verified.get("enabled"):
        raise SystemExit("Memory review job did not pause.")
    identity.update({k: verified[k] for k in ("enabled", "state", "schedule")})
    save_record(tpl.name, rec)


def cmd_install(a: argparse.Namespace) -> int:
    tpl = load_template(a.template)
    r = Runner(a.hermes, a.dry_run, a.verbose)
    info = preflight(r)
    rec = load_record(tpl.name)
    if rec and not a.dry_run:
        raise SystemExit(f"{tpl.name} is already installed (record: {record_dir(tpl.name)}). "
                         f"Use `hbt setup {tpl.name}` to continue, or `hbt update {tpl.name}`.")
    roles = select_roles(tpl, a.roles)
    ws = Path(a.workspace).expanduser().resolve() if a.workspace else (hermes_home() / "workspaces" / tpl.workspace_dir)
    projects = str(Path(a.projects).expanduser().resolve()) if a.projects else str(Path.home() / "projects")
    channels = parse_channels(a.channel)
    owner = (a.owner or read_env_value(hermes_home() / ".env", "SLACK_ALLOWED_USERS").split(",")[0]).strip()
    if owner and not SLACK_ID.fullmatch(owner):
        raise SystemExit(f"Slack member IDs look like U0123ABCD (your profile > three dots > Copy member ID); got {owner!r}")
    main_cfg = hermes_home() / "config.yaml"
    model = read_main_model(main_cfg)
    memory = not a.no_memory
    if memory and not openviking_ok(a.memory_endpoint):
        if a.require_memory:
            raise SystemExit(f"Long-term memory (OpenViking) is not reachable at {a.memory_endpoint}.")
        say(f"! Long-term memory is not reachable at {a.memory_endpoint}; bots will use built-in memory. Re-run with --no-memory to silence this.")
        memory = False

    existing = [tpl.profile(x.key) for x in roles if profile_is_live(tpl.profile(x.key))]
    if existing:
        raise SystemExit(f"These profiles already exist: {', '.join(existing)}. hbt never overwrites a profile; "
                         "remove them or install on another server.")

    say(f"Installing {tpl.title} v{tpl.version} ({'dry run' if a.dry_run else 'live'})")
    say(f"  Hermes {info['hermes_version']}; HERMES_HOME {hermes_home()}")
    say(f"  bots: {', '.join(tpl.profile(x.key) for x in roles)}")
    say(f"  workspace: {ws}; projects: {projects}")
    say(f"  owner: {owner or 'not set (only you should be able to talk to the bots; set --owner)'}")
    say(f"  model: {model.get('default', '(profile default)')} via {model.get('provider', '(default)')}; memory: {'OpenViking, one account per bot' if memory else 'built-in'}")
    if not info["docker"]:
        say("! Docker not found: bots run commands directly on this server, limited only by their working folder and rules.")
    if not a.yes and not a.dry_run:
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            say("Cancelled.")
            return 1

    rec = {"template": tpl.name, "version": "pending", "target_version": tpl.version,
           "installed_at": now_iso(), "hermes_version": info["hermes_version"],
           "workspace": str(ws), "workspace_created": not ws.exists(), "profiles": [], "jobs": [], "board": None, "main_config": {},
           "memory": {"enabled": memory, "endpoint": a.memory_endpoint, "accounts": []}, "channels": channels,
           "bots": {}, "owner": owner, "projects": projects, "manifests": {}, "setup": {}, "repo_path": str(REPO_ROOT)}

    native = native_skills()
    skills_plan = plan_shared_skills(tpl, roles, rec, native, fresh=True)
    if a.dry_run:
        preview_shared_skills(skills_plan)
    else:
        apply_shared_skills(tpl, rec, skills_plan)

    def checkpoint():
        if not a.dry_run:
            save_record(tpl.name, rec)

    # 1. workspace
    say("1/6 workspace")
    acts = build_workspace(tpl, roles, ws, channels, a.dry_run, projects=projects)
    if not a.dry_run:
        Path(projects).mkdir(parents=True, exist_ok=True)
    say(f"  {len(acts)} folder/file action(s)")

    # 2. profiles
    say("2/6 bot profiles")
    for role in roles:
        name = tpl.profile(role.key)
        src = stage_distribution(tpl, role) if not a.dry_run else tpl.path / "roles" / role.key
        clear_deleted_marker(name, record_dir(tpl.name) / "backups", a.dry_run)
        r.hermes_cmd("profile", "install", str(src), "-y")
        rec["profiles"].append(name)
        checkpoint()
        if not a.dry_run:
            activate_shared_profile(tpl, rec, name, [])
            seed_shared_manual(native, name)
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
        if role.takes_cards:
            # Cards run in the background, where nobody can click a memory approval: it would hang the card.
            sets["memory.write_approval"] = "false"
        if role.kind == "ops":
            # Ops only runs unattended jobs and keeps no memory of its own (Q23): its inputs are files and the board.
            sets.update({"memory.memory_enabled": "false", "memory.user_profile_enabled": "false"})
            sets.update(OPS_CONFIG)
        for k, v in sets.items():
            r.hermes_cmd("config", "set", k, str(v), profile=name)
        for toolset in role.slack_toolsets:
            r.hermes_cmd("tools", "enable", toolset, "--platform", "slack", profile=name)
        if memory and role.kind != "ops":
            account = f"{a.memory_prefix}-{role.key}"
            set_env_values(hermes_home() / "profiles" / name / ".env",
                           {"OPENVIKING_ACCOUNT": account, "OPENVIKING_USER": "owner"}, a.dry_run)
            rec["memory"]["accounts"].append(account)
        if role.kind != "ops":
            apply_slack(r, tpl, role, rec, a.dry_run)
            rec["manifests"][role.key] = str(write_manifest(r, tpl, role.title, name)) if not a.dry_run else ""
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
    # Native read commands bootstrap config/logs on a new home, so dry-run must not invoke them.
    boards = "" if a.dry_run else r.hermes_cmd("kanban", "boards", "list", check=False, mutate=False)
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
        for job in tpl.jobs:
            if job["key"] == MEMORY_REVIEW_KEY:
                continue
            if job.get("requires") == "openviking" and not memory:
                continue
            args = job_args(tpl, job, ops, target, ws / ops.folder)
            out = r.hermes_cmd(*args, profile=tpl.profile(ops.key))
            m = re.search(r"\b([0-9a-f]{12})\b", out or "")
            rec["jobs"].append({"key": job["key"], "id": m.group(1) if m else None, "profile": tpl.profile(ops.key)})
            checkpoint()
        say(f"  {len(rec['jobs']) if not a.dry_run else len(tpl.jobs)} job(s) delivering to {target}")

    # 6. main profile: kanban settings (and the Ops route, once the system channel is known)
    sync_memory_review(tpl, rec, getattr(a, "memory_review", None), r)
    say("6/6 main profile")
    wire_system_channel(r, tpl, rec, a.dry_run)
    rec["version"] = tpl.version
    rec.pop("target_version", None)
    checkpoint()

    say("\nInstalled with unresolved skill conflicts; see status/check and recovery archives."
        if skills_plan["state"]["conflicts"] and not a.dry_run else
        "\nDone." if not a.dry_run else "\nDry run complete. Nothing was changed.")
    say(f"Next: ./hbt setup {tpl.name}  (connects each bot to Slack, one step at a time)")
    return 2 if skills_plan["state"]["conflicts"] else 0


def cmd_connect(a: argparse.Namespace) -> int:
    """Save one bot's Slack tokens (hidden), check them with Slack, and find its channels by name."""
    tpl = load_template(a.template)
    rec = load_record(tpl.name)
    if not rec:
        raise SystemExit(f"Install the template first: ./hbt setup {tpl.name}")
    bots = [x for x in tpl.roles if x.kind != "ops"]
    role = next((x for x in bots if x.key == a.role), None)
    if not role or tpl.profile(role.key) not in rec["profiles"]:
        raise SystemExit(f"Unknown bot {a.role!r}. Bots: {', '.join(x.key for x in bots)}")
    name = tpl.profile(role.key)
    env = hermes_home() / "profiles" / name / ".env"
    r = Runner(a.hermes, a.dry_run, a.verbose)
    token = read_env_value(env, "SLACK_BOT_TOKEN")
    if a.tokens or not token:
        token, app = ask_tokens(role.title, name)
        me = slack_api(token, "auth.test")
        if not me.get("ok"):
            raise SystemExit(f"Slack did not accept that bot token ({me.get('error')}). Nothing was saved.")
        set_env_values(env, {"SLACK_BOT_TOKEN": token, "SLACK_APP_TOKEN": app}, a.dry_run)
    else:
        me = slack_api(token, "auth.test")
        if not me.get("ok"):
            raise SystemExit(f"{role.title}'s saved token no longer works ({me.get('error')}). "
                             f"Save new ones: ./hbt connect {tpl.name} {role.key} --tokens")
    rec.setdefault("bots", {})[role.key] = me["user_id"]
    rec.setdefault("channels", {})
    handoff = peer_channels(tpl, role, rec["profiles"])
    wanted = role.channels + handoff + [tpl.system_channel]
    found = find_channels(token, wanted)
    for ch, info in found.items():
        rec["channels"][ch] = info["id"]
    # This bot, and every bot that lists it as a peer (they need its ID on their allowlist).
    for x in [role] + [p for p in bots if role.key in p.peers and tpl.profile(p.key) in rec["profiles"]]:
        apply_slack(r, tpl, x, rec, a.dry_run)
    installed = [x for x in tpl.roles if tpl.profile(x.key) in rec["profiles"]]
    build_workspace(tpl, installed, Path(rec["workspace"]), rec["channels"], a.dry_run,
                    bots=rec["bots"], projects=rec.get("projects", ""))
    wire_system_channel(r, tpl, rec, a.dry_run)
    if not a.dry_run:
        save_record(tpl.name, rec)
    missing = [c for c in role.channels + handoff if c not in found]
    outside = [c for c in role.channels + handoff if c in found and not found[c]["member"]]
    say(f"{role.title} is connected to Slack as <@{me['user_id']}>.")
    if any(c in handoff for c in outside):
        say(f"  {role.title} also joins the channels of the bots that hand it work, so their mentions reach it.")
    if missing:
        say(f"  Channels not found: {', '.join('#' + c for c in missing)}. Create them in Slack. "
            f"If one exists but is private, invite {role.title} to it: a bot cannot see a private channel it is not in.")
    if outside:
        say(f"  Not invited yet: {', '.join('#' + c for c in outside)}. In each one, type /invite @{role.title}")
    return 2 if missing or outside else 0


# --------------------------------------------------------------------------- guided setup

def setup_install_incomplete(tpl: Template, rec: dict) -> bool:
    """Do not turn an interrupted install or missing selected role into setup success."""
    profiles = rec.get("profiles") or []
    state = rec.get("shared_skills") or {}
    selected = set(state.get("profiles") or {})
    return bool(
        not rec.get("version") or rec["version"] == "pending" or rec.get("target_version")
        or state.get("pending") or state.get("migration") == "activating"
        or not profiles or not selected.issubset(profiles)
        or not any(tpl.profile(role.key) in profiles for role in tpl.roles)
        or any(not profile_is_live(name)
               or not (hermes_home() / "profiles" / name / "config.yaml").is_file()
               for name in profiles)
    )


def setup_recovery_hint(tpl: Template) -> str:
    return (f"Installation is incomplete; setup cannot continue. Inspect `./hbt status {tpl.name}` "
            f"and the recovery archives in {record_dir(tpl.name)}. "
            f"For an interrupted fresh install, run `./hbt uninstall {tpl.name}` to preserve archives, "
            "resolve any ownership refusal, then retry install. "
            f"For an interrupted update, run `./hbt update {tpl.name}`. Do not mark the record complete manually.")


def next_setup_step(tpl: Template, rec: dict | None) -> tuple[str, Role | None]:
    """The single next thing the owner has to do, worked out from what is already true.
    Setup can stop anywhere and pick up here: nothing but the record and Slack decide the step."""
    if not rec:
        return "install", None
    if setup_install_incomplete(tpl, rec):
        return "recover", None
    done = rec.get("setup") or {}
    bots = [x for x in tpl.roles if x.kind != "ops" and tpl.profile(x.key) in rec["profiles"]]
    for role in bots:
        if role.key not in (rec.get("bots") or {}):
            return "connect", role
        if role.key not in (done.get("channels_ok") or []):
            return "channels", role
    if tpl.ops and tpl.profile(tpl.ops.key) in rec["profiles"] and not done.get("system_channel_ok"):
        return "system-channel", None
    if not done.get("restarted"):
        return "restart", None
    for role in bots:
        if role.key not in (done.get("tested") or []):
            return "test", role
    builder = next((x for x in bots if x.builds), None)
    if builder and not done.get("first_card"):
        return "first-card", builder
    return "done", None


def _wait(prompt: str) -> None:
    input(f"\n{prompt}\nPress Enter when done (Ctrl+C to stop; run ./hbt setup again to pick up here). ")


def _ask(question: str, default: str = "") -> str:
    got = input(f"{question}{f' [{default}]' if default else ''}: ").strip()
    return got or default


def _bot_replied(token: str, channel: str, bot_id: str, since: float) -> bool:
    """True when the bot answered anything posted in the channel after `since`, in a thread or not."""
    hist = slack_api(token, "conversations.history", channel=channel, oldest=f"{since:.6f}", limit="50")
    for m in hist.get("messages", []):
        if m.get("user") == bot_id:
            return True
        if m.get("reply_count"):
            thread = slack_api(token, "conversations.replies", channel=channel, ts=m["ts"], limit="50")
            if any(x.get("user") == bot_id for x in thread.get("messages", [])):
                return True
    return False


def cmd_setup(a: argparse.Namespace) -> int:
    import time
    tpl = load_template(a.template)
    say(f"{tpl.title} setup. One action at a time; each one is checked before the next.\n")
    while True:
        rec = load_record(tpl.name)
        step, role = next_setup_step(tpl, rec)
        done = (rec or {}).get("setup") or {}

        if step == "recover":
            say(setup_recovery_hint(tpl))
            return 1

        elif step == "install":
            say("This installs: " + ", ".join(f"{x.title}" for x in tpl.roles) + ". Ops runs scheduled jobs and has no Slack app.")
            tz = _ask("Your timezone (for the morning list)", _system_timezone())
            projects = _ask("Folder where Engineer builds your projects", str(Path.home() / "projects"))
            owner = _ask("Your Slack member ID (Slack > your profile > three dots > Copy member ID)",
                         read_env_value(hermes_home() / ".env", "SLACK_ALLOWED_USERS").split(",")[0].strip())
            args = ["--hermes", a.hermes, "install", tpl.name, "--yes", "--projects", projects, "--owner", owner]
            if tz:
                args += ["--timezone", tz]
            if main(args) != 0:
                return 1

        elif step == "connect":
            manifest = rec["manifests"].get(role.key) or "(run ./hbt update to write it)"
            _wait(f"Step: create the {role.title} Slack app.\n"
                  f"  1. api.slack.com/apps > Create New App > From a manifest > pick your workspace.\n"
                  f"  2. Paste the contents of {manifest}, create it, then Install to Workspace.\n"
                  f"  3. Basic Information > App-Level Tokens > Generate Token with the scope connections:write.\n"
                  f"  Keep the page open: the next prompt asks for the Bot User OAuth Token (xoxb-) and that app token (xapp-).")
            try:
                main(["--hermes", a.hermes, "connect", tpl.name, role.key, "--tokens"])
            except SystemExit as exc:
                say(f"! {exc}")

        elif step == "channels":
            code = main(["--hermes", a.hermes, "connect", tpl.name, role.key])
            if code == 0:
                done.setdefault("channels_ok", []).append(role.key)
                _with_setup(tpl.name, done)
                say(f"  {role.title} is in all its channels.")
            else:
                _wait(f"Step: create any missing channels above and invite {role.title} to each: /invite @{role.title}")

        elif step == "system-channel":
            token = read_env_value(hermes_home() / ".env", "SLACK_BOT_TOKEN")
            if not token:
                say(f"! Your main agent has no Slack bot on this server, so Ops output stays on the server "
                    f"(`hermes -p {tpl.profile(tpl.ops.key)} cron list`).")
                _with_setup(tpl.name, done | {"system_channel_ok": "skipped"})
                continue
            found = find_channels(token, [tpl.system_channel]).get(tpl.system_channel)
            if found and found["member"]:
                rec["channels"][tpl.system_channel] = found["id"]
                wire_system_channel(Runner(a.hermes, False, a.verbose), tpl, rec, False)
                rec["setup"] = done | {"system_channel_ok": True}
                save_record(tpl.name, rec)
                say(f"  Ops will post the morning list and alerts in #{tpl.system_channel}.")
            else:
                _wait(f"Step: create #{tpl.system_channel} (if it does not exist) and invite your main agent's bot to it. "
                      f"Ops posts its morning list and alerts there.")

        elif step == "restart":
            _wait("Step: restart Hermes once so it starts the new bots. In a terminal on this server run:\n"
                  "  hermes gateway restart")
            _with_setup(tpl.name, done | {"restarted": now_iso()})

        elif step == "test":
            cid = rec["channels"][role.channel]
            since = time.time()
            _wait(f"Step: in #{role.channel}, post this (no @mention needed):\n  what's your job here?")
            token = read_env_value(hermes_home() / "profiles" / tpl.profile(role.key) / ".env", "SLACK_BOT_TOKEN")
            say(f"  Waiting up to 3 minutes for {role.title} to answer...")
            answered = False
            for _ in range(18):
                answered = _bot_replied(token, cid, rec["bots"][role.key], since)
                if answered:
                    break
                time.sleep(10)
            if answered:
                done.setdefault("tested", []).append(role.key)
                _with_setup(tpl.name, done)
                say(f"  {role.title} answered. That bot works.")
            else:
                say(f"! No answer from {role.title} yet. Check `hermes gateway status`, then try the step again.")

        elif step == "first-card":
            lead = next(x for x in tpl.roles if role.key in x.peers and "kanban" in x.slack_toolsets)
            projects = rec.get("projects")
            if not isinstance(projects, str) or not os.path.isabs(projects):
                say("! The recorded absolute projects folder is missing; setup cannot identify the hello-world card. "
                    "Inspect ./hbt status before retrying. Setup remains incomplete.")
                return 1
            expected_workspace = os.path.normpath(os.path.join(projects, "hello-world"))
            since = time.time()
            _wait(f"Step: your first build. In #{lead.channel}, post:\n"
                  f"  Create a new project called \"hello world\". Plan a tiny hello world script and execute.\n"
                  f"  {lead.title} plans it and hands it to {role.title} on a card; the result posts in #{role.channel}.")
            say(_owner_review_guidance(tpl.name))
            say("  Waiting up to 10 minutes for the matching card to reach Done after owner review...")
            card = None
            for _ in range(60):
                card = _finished_card(Runner(a.hermes, False, a.verbose), tpl, tpl.profile(role.key),
                                      since, expected_workspace)
                if card:
                    break
                time.sleep(10)
            if card:
                _with_setup(tpl.name, done | {"first_card": card["id"]})
                say(f"  Card {card.get('id')} is done: {card.get('title')}. Your build team works.")
            else:
                say(f"! No unique completed hello-world card yet. Setup remains incomplete. "
                    f"Inspect `hermes kanban --board {tpl.name} list`. "
                    "A draft in review needs your verdict in its original approval thread; "
                    "changes, archive, blocked work or text-only approval do not finish setup. "
                    "No automatic approval was recorded.")
                return 1

        else:
            say("\nSetup is complete for the installed roles. Required bot replies and build checks passed.")
            if tpl.desks:
                d = tpl.desks[0]
                say(f"When an outside editor starts working with you, give them their own desk:\n"
                    f"  ./hbt desk {tpl.name} {d.key} --name <editor> --guest <their member ID> "
                    f"--channel {d.channel}-<editor>=<channel ID>")
            say(f"Fill in your business details: ask your main agent to run the interview in "
                f"{Path(rec['workspace']) / 'canon' / 'INTERVIEW.md'}")
            say(f"Ops runs ./hbt check {tpl.name} every morning and posts any gap in #{tpl.system_channel} "
                f"with its fix. Run it yourself any time.")
            return 0


def _with_setup(tpl_name: str, done: dict) -> dict:
    rec = load_record(tpl_name) or {}
    rec["setup"] = done
    save_record(tpl_name, rec)
    return rec


def _system_timezone() -> str:
    p = Path("/etc/timezone")
    return p.read_text(encoding="utf-8").strip() if p.is_file() else ""


def _owner_review_guidance(board: str, card_id: str = "<card-id>") -> str:
    return ("Engineer hands a checked draft to review, without reviewer reassignment. "
            "Inspect the draft and record one verdict on that exact card in its original approval thread. "
            "Use the card ID from that thread in place of <card-id> when needed:\n"
            f'  Approve draft: !kanban --board {board} complete {card_id} --summary "Owner approved this draft only"\n'
            f'  Request changes: !kanban --board {board} reopen-review {card_id} --reason "<required changes>"\n'
            f"  Reject/stop card: !kanban --board {board} archive {card_id}\n"
            "Archive keeps the record and stops active work; it is not Done. "
            "For a terminal fallback, replace !kanban with hermes kanban in the same command. "
            "This is one decision, not a second confirmation. !approve is for tool approval, not a card verdict. "
            "Conversational approve/change/reject is intent, not proof of a recorded board outcome. "
            "Draft completion does not authorize publishing, deployment, external sends, scheduling or signing.")


def _finished_card(r: Runner, tpl: Template, assignee: str, since: float,
                   expected_workspace: str) -> dict | None:
    import math
    import time
    if (not isinstance(expected_workspace, str) or not os.path.isabs(expected_workspace)
            or isinstance(since, bool) or not isinstance(since, (int, float)) or not math.isfinite(since)):
        return None
    out = r.hermes_cmd("kanban", "--board", tpl.name, "list", "--assignee", assignee, "--status", "done", "--json",
                       check=False, mutate=False)
    try:
        cards = json.loads(out)
    except (json.JSONDecodeError, TypeError):
        return None
    cards = cards.get("tasks") if isinstance(cards, dict) else cards
    if not isinstance(cards, list) or any(not isinstance(c, dict) for c in cards):
        return None
    matches = []
    for c in cards:
        workspace = c.get("workspace_path")
        if (c.get("status") != "done" or c.get("assignee") != assignee
                or c.get("workspace_kind") != "dir" or not isinstance(workspace, str)
                or not os.path.isabs(workspace)
                or os.path.normpath(workspace) != os.path.normpath(expected_workspace)
                or not isinstance(c.get("id"), str) or not re.fullmatch(r"t_[0-9a-f]{8}", c["id"])):
            continue
        created = c.get("created_at")
        if isinstance(created, str):
            try:
                parsed = _dt.datetime.fromisoformat(created)
                created = parsed.timestamp() if parsed.tzinfo is not None else None
            except (ValueError, OverflowError, OSError):
                created = None
        if (isinstance(created, bool) or not isinstance(created, (int, float))
                or created <= 0 or created > time.time() or not math.isfinite(created)):
            continue
        if created >= since - 60:
            matches.append(c)
    return matches[0] if len(matches) == 1 else None


def cmd_update(a: argparse.Namespace) -> int:
    tpl = load_template(a.template)
    rec = load_record(tpl.name)
    if not rec:
        raise SystemExit(f"{tpl.name} is not installed here (no record in {record_dir(tpl.name)}).")
    if rec.get("target_version") and not (rec.get("memory_review") or {}).get("job", {}).get("owner"):
        raise SystemExit("Fresh installation is incomplete. Run uninstall to preserve recovery archives, then retry install.")
    r = Runner(a.hermes, a.dry_run, a.verbose)
    memory_review_policy(tpl, rec, getattr(a, "memory_review", None))
    info = preflight(r)
    recover_shared_skills(tpl.name, rec, a.dry_run)
    installed = [x for x in tpl.roles if tpl.profile(x.key) in rec["profiles"]]
    native = native_skills()
    rec["hermes_version"] = info["hermes_version"]
    skills_plan = plan_shared_skills(tpl, installed, rec, native)
    if a.dry_run:
        preview_shared_skills(skills_plan)
    else:
        try:
            apply_shared_skills(tpl, rec, skills_plan)
        except (Exception, SystemExit):
            recover_shared_skills(tpl.name, rec, False)
            raise
    ws = Path(rec["workspace"])
    rec.setdefault("channels", {}).update(parse_channels(a.channel))
    say(f"Updating {tpl.name} {rec['version']} -> {tpl.version} ({'dry run' if a.dry_run else 'live'})")
    for role in installed:
        name = tpl.profile(role.key)
        if not a.dry_run:
            stage_distribution(tpl, role)
        r.hermes_cmd("profile", "update", name, "-y")
        if not a.dry_run:
            seed_shared_manual(native, name)
        if role.kind == "ops":
            for k, v in OPS_CONFIG.items():
                r.hermes_cmd("config", "set", k, v, profile=name)
        else:
            apply_slack(r, tpl, role, rec, a.dry_run)
            if not a.dry_run:
                rec.setdefault("manifests", {})[role.key] = str(write_manifest(r, tpl, role.title, name))
    acts = build_workspace(tpl, installed, ws, rec["channels"], a.dry_run, bots=rec.get("bots"),
                           projects=rec.get("projects", ""))
    say(f"  workspace: {len(acts)} action(s); owner files and canon untouched")
    for name, entry in (rec.get("desks") or {}).items():
        desk = next((d for d in tpl.desks if d.key == entry.get("desk", name)), None)
        if desk:
            if not a.dry_run:
                configure_desk_skills(tpl, rec, name, native)
                stage_distribution(tpl, desk, name)
            r.hermes_cmd("profile", "update", name, "-y")
            for k, v in desk_config(ws / entry.get("folder", desk.folder), entry["channel"]).items():
                r.hermes_cmd("config", "set", k, v, profile=name)
    ops = tpl.ops
    if ops and tpl.profile(ops.key) in rec["profiles"]:
        agent_keys = {j["key"] for j in tpl.jobs if not j.get("no_agent")}
        for j in rec.get("jobs", []):
            if j.get("id") and j.get("key") in agent_keys:  # older installs lacked --workdir
                r.hermes_cmd("cron", "edit", j["id"], "--workdir", str(ws / ops.folder), profile=j["profile"])
        for job in new_jobs(tpl, rec):  # jobs the template gained since this install (v0.3: drift-check)
            cid = (rec.get("channels") or {}).get(tpl.system_channel)
            out = r.hermes_cmd(*job_args(tpl, job, ops, f"slack:{cid}" if cid else "local", ws / ops.folder),
                               profile=tpl.profile(ops.key))
            m = re.search(r"\b([0-9a-f]{12})\b", out or "")
            rec.setdefault("jobs", []).append({"key": job["key"], "id": m.group(1) if m else None,
                                               "profile": tpl.profile(ops.key)})
            say(f"  new scheduled job: {job['key']}")
    sync_memory_review(tpl, rec, getattr(a, "memory_review", None), r)
    wire_system_channel(r, tpl, rec, a.dry_run)
    if not a.dry_run:
        rec["version"], rec["updated_at"] = tpl.version, now_iso()
        rec.pop("target_version", None)
        settings = hermes_home() / "profiles" / tpl.profile(ops.key) / "hbt-settings.json" if ops else None
        if settings and settings.exists():
            s = json.loads(settings.read_text(encoding="utf-8"))
            s["installed_version"] = tpl.version
            settings.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
        save_record(tpl.name, rec)
    say("Updated with unresolved skill conflicts; see status/check and recovery archives."
        if skills_plan["state"]["conflicts"] and not a.dry_run else
        "Done." if not a.dry_run else "Dry run complete. Nothing was changed.")
    if not a.dry_run:
        say("Restart the gateway once so the bots pick up the changes: hermes gateway restart")
    return 2 if skills_plan["state"]["conflicts"] else 0


# --------------------------------------------------------------------------- desks (Q20, Q26)

DESK_IMAGE = "debian:bookworm-slim"  # file tools need bash in the container; Alpine has none


def docker_rootless() -> str:
    """'' when rootless Docker answers for this user, else why desks cannot be added."""
    try:
        res = subprocess.run(["docker", "info", "--format", "{{json .SecurityOptions}}"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return "Docker is not installed or did not answer."
    if res.returncode != 0:
        return "Docker is installed but not running for this user."
    if "rootless" not in res.stdout:
        return "Docker runs as root here, so anything that can use it controls the whole server."
    return ""


def desk_config(folder: Path, channel_id: str) -> dict[str, str]:
    """A desk answers outsiders, so everything it can do is pinned: file tools only, inside a
    container that sees only the desk folder and has no network, one Slack channel, no memory,
    and no admin slash commands for anyone."""
    return {
        "platform_toolsets.slack": '["file"]',
        "terminal.backend": "docker",
        "terminal.cwd": "/workspace",
        "terminal.docker_image": DESK_IMAGE,
        "terminal.docker_volumes": json.dumps([f"{folder}:/workspace"]),
        "terminal.docker_mount_cwd_to_workspace": "false",
        "terminal.docker_network": "false",
        "memory.memory_enabled": "false",
        "memory.user_profile_enabled": "false",
        "slack.allowed_channels": channel_id,
        "slack.unauthorized_dm_behavior": "ignore",
        "slack.gateway_restart_notification": "false",
        "slack.allow_admin_from": '["nobody"]',  # gating on, no admins: guests keep only /help and /whoami
        "slack.group_allow_admin_from": '["nobody"]',
    }


def parse_guests(ids: list[str]) -> list[str]:
    out = [g.strip() for g in ids or [] if g.strip()]
    bad = [g for g in out if not SLACK_ID.fullmatch(g)]
    if bad:
        raise SystemExit(f"Slack member IDs look like U0123ABCD (profile > three dots > Copy member ID); got {', '.join(bad)}")
    return out


def desk_names(desk: Role, person: str) -> tuple[str, str, str]:
    """(profile, channel, folder) for one person's desk: desk-editor-sam, ext-editor-sam, desks/editor-sam."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,30}", person or ""):
        raise SystemExit(f"--name is the person's short name in lowercase, e.g. sam or sam-lee; got {person!r}")
    return f"{desk.key}-{person}", f"{desk.channel}-{person}", f"{desk.folder}-{person}"


def cmd_desk(a: argparse.Namespace) -> int:
    tpl = load_template(a.template)
    desk = next((d for d in tpl.desks if d.key == a.desk), None)
    if not desk:
        raise SystemExit(f"Unknown desk {a.desk!r}. Desks in {tpl.name}: {', '.join(d.key for d in tpl.desks) or 'none'}")
    rec = load_record(tpl.name)
    if not rec:
        raise SystemExit(f"Install the template first: ./hbt setup {tpl.name}")
    name, channel, folder_rel = desk_names(desk, a.name)
    env = hermes_home() / "profiles" / name / ".env"

    if a.tokens:
        if name not in rec["profiles"]:
            raise SystemExit(f"Add the desk first: ./hbt desk {tpl.name} {desk.key} --name {a.name} "
                             f"--channel {channel}=<ID> --guest <ID>")
        bot, app = ask_tokens(f"{desk.title} ({a.name})", name)
        set_env_values(env, {"SLACK_BOT_TOKEN": bot, "SLACK_APP_TOKEN": app}, a.dry_run)
        say("Saved. The desk bot connects when the gateway next scans profiles; if it has not answered in a few "
            "minutes, restart the gateway once.")
        return 0

    reason = docker_rootless()
    if reason:
        raise SystemExit(f"Desks serve people outside your business, so they run only inside rootless Docker. {reason} "
                         "See the README Desks section.")
    cid = parse_channels(a.channel).get(channel)
    if not cid:
        raise SystemExit(f"Give this desk's own Slack channel: --channel {channel}=C0123ABCD")
    guests = parse_guests(a.guest)
    if not guests:
        raise SystemExit("Name at least one guest: --guest U0123ABCD")
    r = Runner(a.hermes, a.dry_run, a.verbose)
    preflight(r)
    if not shared_state(tpl.name, rec):
        raise SystemExit("Update the template before adding a desk: shared skill ownership is not recorded.")
    folder = Path(rec["workspace"]) / folder_rel
    say(f"Adding {desk.title} for {a.name} ({name}) {'dry run' if a.dry_run else 'live'}: folder {folder}, "
        f"channel {cid}, {len(guests)} guest(s)")
    if not a.dry_run:
        for d in desk.dirs:
            (folder / d).mkdir(parents=True, exist_ok=True)
        for fname, text in desk.starter_files.items():
            if not (folder / fname).exists():  # the brief is the owner's once written
                (folder / fname).write_text(text, encoding="utf-8")
    if name not in rec["profiles"]:
        if profile_is_live(name):
            raise SystemExit(f"A profile named {name} already exists and hbt did not create it. Nothing was changed.")
        src = stage_distribution(tpl, desk, name) if not a.dry_run else tpl.path / "roles" / desk.key
        clear_deleted_marker(name, record_dir(tpl.name) / "backups", a.dry_run)
        r.hermes_cmd("profile", "install", str(src), "--name", name, "-y")
        if not a.dry_run:
            rec["profiles"].append(name)
            save_record(tpl.name, rec)
    if not a.dry_run:
        configure_desk_skills(tpl, rec, name, native_skills())
    sets = desk_config(folder, cid)
    sets.update({f"model.{k}": v for k, v in read_main_model(hermes_home() / "config.yaml").items()})
    for k, v in sets.items():
        r.hermes_cmd("config", "set", k, v, profile=name)
    # The home channel is the desk's own channel: it silences Hermes's "no home channel" notice to guests.
    set_env_values(env, {"SLACK_ALLOWED_USERS": ",".join(guests), "SLACK_HOME_CHANNEL": cid}, a.dry_run)
    manifest = write_manifest(r, tpl, f"{desk.title} {a.name}", name, "--no-assistant") if not a.dry_run else ""
    if not a.dry_run:
        rec.setdefault("desks", {})[name] = {"desk": desk.key, "person": a.name, "channel": cid, "folder": folder_rel,
                                             "guests": guests, "updated_at": now_iso()}
        save_record(tpl.name, rec)
    say("Done." if not a.dry_run else "Dry run complete. Nothing was changed.")
    if not read_env_value(env, "SLACK_BOT_TOKEN"):
        say("\nNext steps for the owner:")
        say(f"  1. api.slack.com/apps > Create New App > From a manifest > paste {manifest}. Install it to the workspace.")
        say("     Then Basic Information > App-Level Tokens > generate one with connections:write.")
        say(f"  2. Save both tokens with hidden input (never paste them into a chat): "
            f"./hbt desk {tpl.name} {desk.key} --name {a.name} --tokens")
    say(f"  Invite the desk bot to #{channel}, and fill in {folder / 'brief.md'}. {a.name} can see only that folder.")
    return 0


def read_jobs_without_bootstrap(profile: str) -> list[dict]:
    """Read all native jobs without creating a store, lock, log or repair file."""
    path = checked_path(hermes_home() / "profiles" / profile / "cron/jobs.json", hermes_home())
    if not path.exists():
        return []
    try:
        if not path.is_file() or not path.stat().st_mode & 0o444:
            raise ValueError()
        data = unique_json(path.read_bytes())
        jobs = data["jobs"] if isinstance(data, dict) else data
        if not isinstance(jobs, list):
            raise ValueError()
        ids = []
        for job in jobs:
            if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not re.fullmatch(r"[0-9a-f]{12}", job["id"]):
                raise ValueError()
            ids.append(job["id"])
        if len(set(ids)) != len(ids):
            raise ValueError()
        return jobs
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit(f"Uninstall refused: {profile}/cron/jobs.json is unreadable or malformed; repair it before retry.") from None


def private_archive_file(source: Path, target: Path, expected: str) -> None:
    """Copy only a preflight-covered file, then verify bytes and private permissions."""
    checked_path(source, source)
    checked_path(target, target)
    missing = []
    parent = target.parent
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(source.read_bytes())
        out.flush()
        os.fsync(out.fileno())
    if _sha(source) != expected or _sha(target) != expected or target.stat().st_mode & 0o077:
        raise SystemExit("Uninstall preservation verification failed; no unsafe deletion is authorized.")
    fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def uninstall_review_lock(template: str, dry: bool):
    if dry:
        yield
        return
    import fcntl
    folder = checked_path(record_dir(template) / "memory-review", hermes_home())
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = checked_path(folder / "state.lock", folder)
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("Memory review coordination refused: a run holds the lock; pause its job and retry after it stops.") from None
        yield
    finally:
        os.close(fd)


def uninstall_inventory(template: str, rec: dict, delete_workspace: bool = False) -> dict:
    """Global, zero-write refusal gate. Familiar directories do not establish ownership."""
    def refuse(name, rel, reason) -> NoReturn:
        raise SystemExit(f"Uninstall refused: {name}/{rel}: {reason}. Preserve uncovered data outside deletion roots or relocate the unrelated workload and verify it before retry.")

    tpl = load_template(template)
    names = rec.get("profiles")
    if (not isinstance(names, list) or any(not isinstance(n, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", n) or n == "default" for n in names)
            or len(set(names)) != len(names)):
        refuse("record", "profiles", "invalid profile identity")
    roots = [checked_path(hermes_home() / "profiles" / n, hermes_home() / "profiles") for n in names]
    if delete_workspace:
        roots.append(checked_path(Path(rec["workspace"]), Path(rec["workspace"])))
    archive_root = checked_path(record_dir(template) / "backups", hermes_home())
    if any(archive_root.is_relative_to(root) for root in roots):
        refuse("record", "backups", "recovery location is inside a deletion root")
    if "memory_review" in rec:
        policy = memory_review_policy(tpl, rec, None)
        for recovery in (Path(policy["state_path"]).parent, Path(policy["recovery_path"])):
            if any(recovery.is_relative_to(root) for root in roots):
                refuse("record", "memory_review", "recovery state is inside a deletion root")
            package_hashes(recovery)
    state = shared_state(template, rec)
    if state.get("pending") or state.get("migration") == "activating":
        refuse("record", "shared_skills", "interrupted activation requires explicit update recovery first")
    owned = {}
    for job in rec.get("jobs", []):
        if (not isinstance(job, dict) or job.get("profile") not in names
                or not isinstance(job.get("id"), str) or not re.fullmatch(r"[0-9a-f]{12}", job["id"])):
            refuse("record", "jobs", "invalid recorded job identity")
        key = job["profile"], job["id"]
        if key in owned:
            refuse(*key, "duplicate recorded identity")
        owned[key] = job
    # Coverage is the same bounded discovery as backup_skill_state, including ancestor roots.
    packages = set()
    for name, prof in zip(names, roots):
        cfg_path = checked_path(prof / "config.yaml", prof)
        try:
            cfg = yaml.safe_load(cfg_path.read_text()) if cfg_path.exists() else {}
            settings = (cfg or {}).get("skills") or {}
            external = settings.get("external_dirs", [])
            create = settings.get("create_dir")
            if not isinstance(external, list) or any(not isinstance(p, str) for p in external) or (create is not None and not isinstance(create, str)):
                raise ValueError()
            for raw in external + ([create] if create else []):
                if not raw.strip():
                    continue
                origin = profile_skill_path(raw, prof)
                for removed in roots[:len(names)]:
                    endangered = origin if origin.is_relative_to(removed) else removed if removed.is_relative_to(origin) else None
                    if endangered is not None:
                        packages.update(skill_packages(checked_path(endangered, removed)).values())
        except (OSError, ValueError, TypeError, AttributeError, yaml.YAMLError):
            refuse(name, "config.yaml", "unverifiable skill coverage")
    archives = list(state.get("backups", [])) + rec.get("skill_uninstall_archives", []) + rec.get("memory_uninstall_archives", [])
    for raw in archives:
        saved = checked_path(Path(raw), archive_root)
        if any(saved.is_relative_to(root) for root in roots) or not saved.is_dir():
            refuse("record", "backups", "unverifiable recorded archive")
    result = {}
    for name, prof in zip(names, roots):
        if not prof.exists():
            result[name] = {}
            continue
        if not prof.is_dir():
            refuse(name, ".", "profile root is not a directory")
        role_key = (rec.get("desks", {}).get(name) or {}).get("desk", name)
        role = next((r for r in tpl.roles + tpl.desks if r.key == role_key), None)
        if role is None:
            refuse(name, "distribution.yaml", "unknown installed role")
        manifest_path = checked_path(prof / "distribution.yaml", prof)
        if manifest_path.exists():
            manifest = yaml.safe_load(manifest_path.read_bytes())
            if not isinstance(manifest, dict) or manifest.get("source") != str(record_dir(template) / "dist" / name):
                refuse(name, "distribution.yaml", "distribution source identity changed")
        jobs = read_jobs_without_bootstrap(name)
        for job in jobs:
            owner = owned.get((name, job["id"]))
            if not owner or job.get("name") != f"{ROUTE_TAG}{template}:{owner['key']}":
                refuse(name, "cron/" + job["id"], "job ownership is not established; preserving bytes does not preserve a running job")
            if owner["key"] == MEMORY_REVIEW_KEY:
                identity = (rec.get("memory_review") or {}).get("job", {})
                if (identity.get("id") != job["id"] or identity.get("profile") != name
                        or job.get("created_at") != identity.get("created_at")
                        or job.get("origin") != {"hbt_owner": identity.get("owner")}
                        or job.get("script") != "hbt_memory_review.py" or job.get("no_agent") is not True):
                    refuse(name, "cron/" + job["id"], "memory review identity changed")
        dist = checked_path(record_dir(template) / "dist" / name, record_dir(template))
        files = {}
        for directory, dirs, leaves in os.walk(prof, followlinks=False, onerror=lambda exc: refuse(name, ".", "unreadable directory")):
            for leaf in dirs + leaves:
                checked_path(Path(directory) / leaf, prof)
            for leaf in leaves:
                path = Path(directory) / leaf
                rel = path.relative_to(prof).as_posix()
                if not path.is_file() or not path.stat().st_mode & 0o444:
                    refuse(name, rel, "unreadable or nonregular file")
                try:
                    sha = _sha(path)
                except OSError:
                    refuse(name, rel, "unreadable file")
                covered = (rel in {"config.yaml", ".no-bundled-skills", "distribution.yaml"}
                    or rel.startswith(("skills/", "memories/", "pending/memory/"))
                    or any(path.is_relative_to(p) for p in packages)
                    or re.fullmatch(r"backups/config/config\.yaml\.good\.[^/]+", rel)
                    or re.fullmatch(r"logs/(agent|errors)\.log(?:\.[1-9][0-9]*)?", rel))
                # Native POSIX rotating handlers use numeric suffixes. Cron's lock is empty scaffolding.
                disposable = rel == "cron/jobs.json" or (rel == "cron/.jobs.lock" and path.stat().st_size == 0)
                if rel == ".env":
                    # set_env_values({}, dry=False) writes exactly one newline on
                    # an unconfigured fresh role. No key, comment or secret qualifies.
                    disposable = path.read_bytes() == b"\n"
                if rel == "SOUL.md" or rel.startswith("scripts/"):
                    source = checked_path(dist / rel, dist)
                    shipped = tpl.path / "roles" / role.key / rel
                    disposable = source.is_file() and shipped.is_file() and _sha(source) == _sha(shipped) == sha
                if rel == "hbt-settings.json" and name == "ops":
                    # Only reconstructible installer output is disposable. Extra or
                    # customized settings need an existing verified archive.
                    expected = {"template": template, "installed_version": rec["version"],
                        "repo_path": rec.get("repo_path", ""), "workspace": rec["workspace"],
                        "timezone": (yaml.safe_load((prof / "config.yaml").read_text()) or {}).get("timezone", ""),
                        "openviking_endpoint": "", "openviking_embed_endpoint": "",
                        "openviking_services": [], "openviking_fix_hint": ""}
                    actual = json.loads(path.read_bytes())
                    if "memory_review" in rec:
                        expected["install_root"] = str(hermes_home())
                    # A missing install timezone is deliberately stored as empty.
                    if actual.get("timezone") == "":
                        expected["timezone"] = ""
                    disposable = actual == expected
                if not covered and not disposable:
                    covered = any(_sha(checked_path(Path(saved) / "profiles" / name / rel, Path(saved))) == sha for saved in archives)
                if not covered and not disposable:
                    refuse(name, rel, "current bytes have no verified preservation coverage or disposable provenance")
                stat = path.stat()
                files[rel] = {"sha256": sha, "preserve": bool(covered),
                              "mode": stat.st_mode & 0o777, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        result[name] = files
    return result


def archive_uninstall_inventory(template: str, rec: dict, inventory: dict) -> Path:
    folder = checked_path(record_dir(template) / "backups" / ("memory-uninstall-" + uuid.uuid4().hex), hermes_home())
    folder.parent.mkdir(mode=0o700, exist_ok=True)
    folder.mkdir(mode=0o700)
    for name, files in inventory.items():
        for rel, info in files.items():
            if info["preserve"]:
                private_archive_file(hermes_home() / "profiles" / name / rel,
                                     folder / "profiles" / name / rel, info["sha256"])
    from utils import atomic_json_write
    atomic_json_write(folder / "inventory.json", inventory, mode=0o600, fsync_dir=True)
    if json.loads((folder / "inventory.json").read_bytes()) != inventory:
        raise SystemExit("Uninstall archive inventory verification failed; deletion refused.")
    rec.setdefault("memory_uninstall_archives", []).append(str(folder))
    save_record(template, rec)
    return folder


def cmd_uninstall(a: argparse.Namespace) -> int:
    checked_path(record_dir(a.template) / "record.json", hermes_home())
    rec = load_record(a.template)
    if not rec:
        raise SystemExit(f"{a.template} is not installed here (no record in {record_dir(a.template)}).")
    checked_path(hermes_home() / "config.yaml", hermes_home())
    if a.delete_workspace and not rec.get("workspace_created", False):
        raise SystemExit(f"{rec['workspace']} existed before the install, so hbt will not delete it. Remove it yourself if you mean to.")
    inventory = uninstall_inventory(a.template, rec, a.delete_workspace)
    r = Runner(a.hermes, a.dry_run, a.verbose)
    say(f"Uninstalling {a.template} ({'dry run' if a.dry_run else 'live'})")
    say(f"  profiles: {', '.join(rec['profiles']) or 'none'}")
    say(f"  workspace {rec['workspace']}: {'DELETE' if a.delete_workspace else 'kept'}")
    say(f"  memory accounts {', '.join(rec['memory'].get('accounts', [])) or 'none'}: kept (see README to delete them)")
    if rec.get("bots"):
        say("  Slack apps: kept. Delete them at api.slack.com/apps if you no longer need them.")
    if not a.yes and not a.dry_run:
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            say("Cancelled.")
            return 1
    final = inventory
    with uninstall_review_lock(a.template, a.dry_run):
        if not a.dry_run:
            if uninstall_inventory(a.template, rec, a.delete_workspace) != inventory:
                raise SystemExit("Uninstall refused: inventory changed; retry after stopping writers.")
            archive_uninstall_inventory(a.template, rec, inventory)
            if uninstall_inventory(a.template, rec, a.delete_workspace) != inventory:
                raise SystemExit("Uninstall stopped: inventory changed during preservation; no profile deletion performed.")
        uninstall_shared_skills(a.template, rec, a.dry_run)
        if not a.dry_run:
            # Native cron operations may append profile logs. Preserve their final
            # bytes after stopping owned jobs, never assume the first archive suffices.
            uninstall_inventory(a.template, rec, a.delete_workspace)
            for job in rec.get("jobs", []):
                if any(j["id"] == job["id"] for j in read_jobs_without_bootstrap(job["profile"])):
                    r.hermes_cmd("cron", "remove", job["id"], profile=job["profile"])
            final = uninstall_inventory(a.template, rec, a.delete_workspace)
            for name in rec["profiles"]:
                if read_jobs_without_bootstrap(name):
                    raise SystemExit(f"Uninstall stopped: {name} still has a job; no profile deletion performed.")
            archive_uninstall_inventory(a.template, rec, final)
        revert_main_config(hermes_home() / "config.yaml", rec, a.dry_run)
        for name in rec["profiles"]:
            if (hermes_home() / "profiles" / name).exists():
                if not a.dry_run:
                    latest = uninstall_inventory(a.template, rec, a.delete_workspace)
                    if any(latest[n] != final[n] for n in rec["profiles"] if (hermes_home() / "profiles" / n).exists()):
                        raise SystemExit("Uninstall stopped: profile data changed during teardown; preserve the changes and retry. Some earlier profiles may already be removed.")
                r.hermes_cmd("profile", "delete", name, "-y")
                if not a.dry_run and (hermes_home() / "profiles" / name).exists():
                    raise SystemExit(f"Uninstall stopped: {name} still exists after native deletion; inspect partial state and recovery archives.")
    if rec.get("board"):
        # Archives the board (recoverable under kanban/boards/_archived); tasks are never hard-deleted by us.
        r.hermes_cmd("kanban", "boards", "rm", rec["board"])
        say(f"  board {rec['board']}: archived" if not a.dry_run else "")
    if a.delete_workspace:
        say(f"  delete {rec['workspace']}")
        if not a.dry_run:
            if Path(rec["workspace"]).exists():
                shutil.rmtree(rec["workspace"])
    if not a.dry_run:
        shutil.rmtree(record_dir(a.template) / "dist", ignore_errors=True)
        done = record_dir(a.template) / f"record.uninstalled.{_dt.datetime.now():%Y%m%d-%H%M%S}.json"
        os.replace(record_dir(a.template) / "record.json", done)
    say("Done. Restart the gateway once so it stops serving the removed bots." if not a.dry_run else "Dry run complete. Nothing was changed.")
    return 0


def cmd_status(a: argparse.Namespace) -> int:
    rec = load_record(a.template)
    if not rec:
        say(f"{a.template}: not installed")
        return 1
    tpl = load_template(a.template)
    if setup_install_incomplete(tpl, rec):
        say(setup_recovery_hint(tpl))
        return 1
    say(f"{a.template} v{rec['version']} installed {rec['installed_at']}")
    policy = memory_review_policy(tpl, rec, None)
    say(f"  memory review: {policy['mode']}; enrolled: {', '.join(policy['enrolled']) or 'none'}; delivery: local only")
    say(f"  memory review job: {policy.get('job', {}).get('id', 'not installed')}")
    say(f"  memory review recovery: {policy['recovery_path']}; state: {policy['state_path']}")
    for gap in memory_review_gaps(tpl, rec):
        say("  " + gap)
    if rec.get("target_version"):
        say(f"  INCOMPLETE installation, target {rec['target_version']}; archive with uninstall before retrying install")
    state = shared_state(a.template, rec)
    if state:
        say(f"  shared library: {state['root']}; source: {state['source']} ({state['source_version']})")
        say(f"  migration: {state['migration']}; recovery archives: {', '.join(state['backups'])}")
        for name, entry in state["profiles"].items():
            say(f"  {name} selected packages: {', '.join(entry['selected'])}")
        for conflict in state.get("conflicts", []):
            say("  CONFLICT " + conflict)
    for name in rec["profiles"]:
        key = next((x.key for x in tpl.roles if tpl.profile(x.key) == name), "")
        slack = f"Slack <@{rec['bots'][key]}>" if key in (rec.get("bots") or {}) else ""
        say(f"  {'ok     ' if (hermes_home() / 'profiles' / name).exists() else 'MISSING'} {name} {slack}")
    cfg = yaml.safe_load((hermes_home() / "config.yaml").read_text(encoding="utf-8")) or {}
    kb = cfg.get("kanban") or {}
    say(f"  kanban dispatch in gateway: {kb.get('dispatch_in_gateway')}")
    say(f"  kanban auto-review (must be False, the owner approves): {kb.get('review_dispatch', True)}")
    say(f"  memory: {'OpenViking' if rec['memory']['enabled'] else 'built-in'}")
    step, role = next_setup_step(tpl, rec)
    say(f"  setup: {'complete' if step == 'done' else f'next step is {step}' + (f' ({role.title})' if role else '')}")
    return 0


# --------------------------------------------------------------------------- drift check

def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _profile_cfg(name: str) -> dict:
    f = hermes_home() / "profiles" / name / "config.yaml"
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.is_file() else {}


def _truthy(v) -> bool:
    return str(v).strip().lower() in ("true", "yes", "on", "1")


def memory_review_gaps(tpl: Template, rec: dict) -> list[str]:
    if "memory_review" not in rec:
        return []
    p = memory_review_policy(tpl, rec, None)
    gaps = []
    identity = p.get("job", {})
    job = next((j for j in read_jobs_without_bootstrap("ops") if j["id"] == identity.get("id")), None)
    if job is None:
        gaps.append("Memory review job is missing; a deleted recorded job stays deleted. Inspect the installation record.")
    elif job.get("deliver") != "local" or job.get("script") != "hbt_memory_review.py":
        gaps.append("Memory review job conflicts with local-only ownership. Resolve its identity before update.")
    elif not job.get("enabled") or job.get("state") == "paused":
        gaps.append(f"Memory review job is paused ({p['mode']}); ordinary updates preserve owner pauses.")
    path = checked_path(Path(p["state_path"]), hermes_home())
    if path.exists():
        try:
            state = json.loads(path.read_bytes())
            receipts = state["receipts"]
            pending = sum(r.get("status") != "complete" for r in receipts.values())
            attempts = sum(a.get("count", 0) >= 3 for a in state["attempts"].values())
            if pending or attempts:
                gaps.append(f"Memory review recovery: unfinished={pending}; attempt-limited={attempts}; inspect {path} locally.")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            gaps.append("Memory review recovery state is unreadable or invalid; keep drafts pending and reconcile it locally.")
    return gaps


def check_gaps(tpl: Template, rec: dict, live: bool = True) -> list[str]:
    """Drift between what the template set up and what is true now, one line per gap with its fix.
    Each check is a gap that broke a real install: copies drifting apart, a handoff nobody hears,
    a tool that lost its sign-in, a failing job. ``live`` adds the Slack membership checks."""
    gaps: list[str] = []
    gaps.extend(memory_review_gaps(tpl, rec))
    home = hermes_home()
    installed = [x for x in tpl.roles if tpl.profile(x.key) in rec.get("profiles", [])]
    bots = [x for x in installed if x.kind != "ops"]
    ids, channels = rec.get("bots") or {}, rec.get("channels") or {}
    for x in installed:
        if not (home / "profiles" / tpl.profile(x.key)).is_dir():
            gaps.append(f"{tpl.profile(x.key)}: profile is missing. Fix: ./hbt update {tpl.name}")

    # 2. Use installed provenance, not a newer checkout, to diagnose shared assets.
    gaps.extend(shared_gaps(tpl.name, rec))
    for x in ([] if rec.get("shared_skills") else installed):
        src = tpl.path / "roles" / x.key / "skills"
        stale = sorted(f.parent.name for f in src.rglob("SKILL.md")
                       if _sha(f) != _sha(home / "profiles" / tpl.profile(x.key) / "skills" / f.relative_to(src)))
        if stale:
            gaps.append(f"{tpl.profile(x.key)}: {len(stale)} playbook(s) differ from the template "
                        f"({', '.join(stale[:3])}{'...' if len(stale) > 3 else ''}). Fix: ./hbt update {tpl.name}")
    # 3. Sign-in tools: turned on but never signed in, or signed out since.
    for x in installed:
        name = tpl.profile(x.key)
        prof = home / "profiles" / name
        for server, sc in (_profile_cfg(name).get("mcp_servers") or {}).items():
            sc = sc or {}
            if sc.get("auth") != "oauth" or not _truthy(sc.get("enabled", True)):
                continue
            token = prof / "mcp-tokens" / f"{server}.json"
            if not token.is_file():
                gaps.append(f"{name}: {server} is on but not signed in. "
                            f"Fix: hermes -p {name} mcp login {server}, or turn it off if this bot does not need it.")
                continue
            log = prof / "logs" / "agent.log"
            if log.is_file() and log.stat().st_mtime > token.stat().st_mtime:
                with log.open("rb") as fh:  # the tail is enough: a sign-in loss repeats on every connect attempt
                    fh.seek(max(0, log.stat().st_size - 2_000_000))
                    tail = fh.read().decode("utf-8", "replace")
                if f"re-authenticate with `hermes mcp login {server}`" in tail:
                    gaps.append(f"{name}: {server} lost its sign-in. Fix: hermes -p {name} mcp login {server}")
    # 4. Handoffs: each bot hears its peers, wakes on their mentions, and is in their channels.
    owner = rec.get("owner", "")
    for x in bots:
        name, prof = tpl.profile(x.key), home / "profiles" / tpl.profile(x.key)
        allowed = {u.strip() for u in read_env_value(prof / ".env", "SLACK_ALLOWED_USERS").split(",")}
        need = [(owner, "you")] + [(ids[s.key], s.title) for s in bots if x.key in s.peers and ids.get(s.key)]
        deaf = [who for uid, who in need if uid and uid not in allowed]
        if deaf:
            gaps.append(f"{name}: ignores Slack messages from {', '.join(deaf)}. Fix: ./hbt update {tpl.name}")
        slack = _profile_cfg(name).get("slack") or {}
        if owner and any(str(slack.get(k) or "").strip() != owner for k in ("allow_admin_from", "group_allow_admin_from")):
            gaps.append(f"{name}: other bots can run its commands (!approve, !restart). Fix: ./hbt update {tpl.name}")
        if x.peers and (slack.get("allow_bots") != "mentions" or not _truthy(slack.get("strict_mention"))):
            gaps.append(f"{name}: not set to wake on a peer's mention only. Fix: ./hbt update {tpl.name}")
        token = read_env_value(prof / ".env", "SLACK_BOT_TOKEN")
        wanted = [c for c in peer_channels(tpl, x, rec.get("profiles")) if c in channels]
        if live and token and wanted and x.key in ids:
            res = slack_api(token, "users.conversations", types="public_channel,private_channel", limit="1000")
            if not res.get("ok"):
                gaps.append(f"{name}: Slack check failed ({res.get('error')}). Fix: ./hbt connect {tpl.name} {x.key}")
                continue
            member = {c.get("id") for c in res.get("channels", [])}
            for c in wanted:
                if channels[c] not in member:
                    gaps.append(f"{name}: not in #{c}, so handoffs there never reach it. Fix: /invite @{x.title} in #{c}")
    # 5. Scheduled jobs: on, but the last run did not work.
    for j in rec.get("jobs", []):
        f = home / "profiles" / j["profile"] / "cron" / "jobs.json"
        data = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else []
        for job in data.get("jobs", []) if isinstance(data, dict) else data:
            if job.get("id") == j.get("id") and job.get("enabled", True) and job.get("state") != "paused" \
                    and job.get("last_status") not in (None, "ok"):
                gaps.append(f"{j['profile']}: scheduled job {j['key']} last run: {job['last_status']}. "
                            f"Fix: hermes -p {j['profile']} cron runs {j['id']}")
    # 6. Offers: a date in canon/offers.md that has passed means the file needs its outcome.
    offers = Path(rec.get("workspace", "")) / "canon" / "offers.md"
    if offers.is_file():
        text = offers.read_text(encoding="utf-8")
        upcoming = text.split("## Dates coming up", 1)[-1].split("\n## ", 1)[0] if "## Dates coming up" in text else ""
        passed = sorted({d for d in re.findall(r"\b20\d\d-\d\d-\d\d\b", upcoming) if d < _dt.date.today().isoformat()})
        if passed:
            gaps.append(f"canon/offers.md: {', '.join(passed)} passed. Fix: ask {bots[0].title if bots else 'your lead'} "
                        f"to record what happened and move it out of Dates coming up.")
    return gaps


def cmd_check(a: argparse.Namespace) -> int:
    rec = load_record(a.template)
    if not rec:
        say(f"{a.template}: not installed")
        return 1
    tpl = load_template(a.template)
    gaps = check_gaps(tpl, rec, live=not a.offline)
    if a.quiet:  # Ops runs this on a schedule: say something only when the list changes, and weekly while open
        state = record_dir(tpl.name) / "check-state.json"
        key = hashlib.sha256("\n".join(gaps).encode()).hexdigest()
        last = json.loads(state.read_text(encoding="utf-8")) if state.is_file() else {}
        today = _dt.date.today().isoformat()
        if not gaps or (last.get("key") == key and
                        (_dt.date.fromisoformat(today) - _dt.date.fromisoformat(last.get("posted", today))).days < 7):
            if not gaps and last:
                state.write_text("{}\n", encoding="utf-8")
            return 0
        state.write_text(json.dumps({"key": key, "posted": today}) + "\n", encoding="utf-8")
    if gaps:
        say(f"{tpl.title} check: {len(gaps)} gap(s).\n" + "\n".join(f"- {g}" for g in gaps))
    elif not a.quiet:
        say(f"{tpl.title} check: no gaps.")
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

    k = sub.add_parser("check", help="find drift between the bots (sign-ins, handoffs, copies, failing jobs)")
    k.add_argument("template")
    k.add_argument("--quiet", action="store_true", help="scheduled mode: print only when the gaps change")
    k.add_argument("--offline", action="store_true", help="skip the Slack membership checks")
    k.set_defaults(func=cmd_check)

    g = sub.add_parser("setup", help="guided setup, one action at a time (start here)")
    g.add_argument("template")
    g.set_defaults(func=cmd_setup)

    i = sub.add_parser("install", help="install a template (setup runs this for you)")
    common(i)
    i.add_argument("--roles", help="comma-separated role keys (default: all). Ops is always included.")
    i.add_argument("--workspace", help="shared folder for the business (default: $HERMES_HOME/workspaces/<template>)")
    i.add_argument("--projects", help="folder where Engineer builds projects (default: ~/projects)")
    i.add_argument("--owner", help="your Slack member ID; the only person the bots answer (default: your main agent's first allowed user)")
    i.add_argument("--channel", action="append", default=[], metavar="NAME=ID", help="Slack channel ID, e.g. media-video=C0123ABCD (repeat)")
    i.add_argument("--timezone", help="IANA timezone for alert times, e.g. America/Vancouver")
    i.add_argument("--no-memory", action="store_true", help="skip OpenViking; bots use built-in memory")
    i.add_argument("--memory-review", choices=MEMORY_REVIEW_MODES, help="opt in to original background drafts; add-replace can remove facts from an entry (default: off)")
    i.add_argument("--require-memory", action="store_true", help="fail if OpenViking is not reachable")
    i.add_argument("--memory-endpoint", default="http://127.0.0.1:1933")
    i.add_argument("--memory-prefix", default=None, help="OpenViking account prefix (default: the template name)")
    i.add_argument("--memory-embed-endpoint", default="", help="local search-model URL checked when memory search fails")
    i.add_argument("--memory-services", default="", help="comma-separated systemd user services to report on outage")
    i.add_argument("--memory-fix-hint", default="", help="one line telling the owner how to fix a memory outage")
    i.set_defaults(func=cmd_install)

    c = sub.add_parser("connect", help="save a bot's Slack tokens (hidden) and find its channels")
    common(c, confirm=False)
    c.add_argument("role", help="bot key, e.g. cto")
    c.add_argument("--tokens", action="store_true", help="ask for new tokens even if some are saved")
    c.set_defaults(func=cmd_connect)

    u = sub.add_parser("update", help="re-apply template files after git pull")
    common(u, confirm=False)
    u.add_argument("--channel", action="append", default=[], metavar="NAME=ID")
    u.add_argument("--memory-review", choices=MEMORY_REVIEW_MODES, help="explicit memory review policy; omission preserves the recorded mode")
    u.set_defaults(func=cmd_update)

    k = sub.add_parser("desk", help="add or refresh one outside person's desk (needs rootless Docker)")
    common(k, confirm=False)
    k.add_argument("desk", help="desk key, e.g. desk-editor")
    k.add_argument("--name", required=True, help="the person's short name, e.g. sam; gives desk-editor-sam and #ext-editor-sam")
    k.add_argument("--channel", action="append", default=[], metavar="NAME=ID", help="the desk's own Slack channel")
    k.add_argument("--guest", action="append", default=[], metavar="USER_ID",
                   help="Slack member ID allowed to use the desk (repeat; replaces the current list)")
    k.add_argument("--tokens", action="store_true", help="save the desk bot's Slack tokens (hidden prompt)")
    k.set_defaults(func=cmd_desk)

    x = sub.add_parser("uninstall", help="remove what install created")
    common(x)
    x.add_argument("--delete-workspace", action="store_true", help="also delete the business folder (cannot be undone)")
    x.set_defaults(func=cmd_uninstall)

    s = sub.add_parser("status", help="show install state and the next setup step")
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
