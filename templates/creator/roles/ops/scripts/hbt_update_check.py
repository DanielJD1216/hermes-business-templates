#!/usr/bin/env python3
"""Weekly template update check for the Ops role (no-agent cron job).

Prints one line when the template repository has a newer version than the one
installed, and stays silent otherwise. Never changes anything.
Settings come from ../hbt-settings.json (written by the installer).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PROFILE_HOME = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROFILE_HOME / "hbt-settings.json"
STATE_PATH = PROFILE_HOME / "state" / "hbt-update-check.json"


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3]) or (0,)


def remote_version(repo: Path, template: str) -> str | None:
    fetch = subprocess.run(["git", "-C", str(repo), "fetch", "--quiet", "origin"], capture_output=True, text=True, timeout=120)
    if fetch.returncode != 0:
        return None
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "origin/HEAD"], capture_output=True, text=True)
    ref = head.stdout.strip() if head.returncode == 0 and head.stdout.strip() else "origin/main"
    show = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:templates/{template}/template.yaml"],
                          capture_output=True, text=True, timeout=30)
    if show.returncode != 0:
        return None
    m = re.search(r"^version:\s*['\"]?([0-9][0-9.]*)", show.stdout, re.M)
    return m.group(1) if m else None


def main() -> int:
    try:
        cfg = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    repo = Path(cfg.get("repo_path") or "")
    installed = cfg.get("installed_version") or "0"
    template = cfg.get("template") or "creator"
    if not (repo / ".git").exists():
        return 0
    latest = remote_version(repo, template)
    if not latest or _version_tuple(latest) <= _version_tuple(installed):
        return 0
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    if state.get("announced") == latest:
        return 0
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"announced": latest}) + "\n", encoding="utf-8")
    print(f":package: Template update available: {template} {installed} -> {latest}. "
          f"To update, run on the server: cd {repo} && git pull && ./hbt update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
