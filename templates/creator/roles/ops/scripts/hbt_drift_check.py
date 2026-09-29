#!/usr/bin/env python3
"""Daily drift check for the Ops role (no-agent cron job).

Runs `hbt check <template> --quiet` from the template repository and prints its
report, which Ops posts to the system channel. Silent when nothing changed.
Never changes anything. Settings come from ../hbt-settings.json (written by the installer).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

PROFILE_HOME = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROFILE_HOME / "hbt-settings.json"
# Cron runs this with HERMES_HOME set to the Ops profile; the install record lives in the main Hermes home.
ROOT_HOME = PROFILE_HOME.parent.parent if PROFILE_HOME.parent.name == "profiles" else PROFILE_HOME


def main() -> int:
    try:
        cfg = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    launcher = Path(cfg.get("repo_path") or "") / "hbt"
    if not launcher.is_file():
        print(f"Drift check skipped: the template repository is gone ({launcher.parent}). Re-clone it there.")
        return 0
    done = subprocess.run([str(launcher), "check", cfg.get("template") or "creator", "--quiet"],
                          capture_output=True, text=True, timeout=300, env={**os.environ, "HERMES_HOME": str(ROOT_HOME)})
    out = (done.stdout or "").strip()
    if done.returncode != 0:
        err = (done.stderr or out).strip().splitlines()
        out = f"Drift check failed: {err[-1] if err else 'exit ' + str(done.returncode)}"
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
