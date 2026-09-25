#!/usr/bin/env python3
"""Long-term memory (OpenViking) watchdog for the business template's Ops role.

Runs as a no-agent cron job. Prints a message only when memory goes down, is
still down (reminder every 6 hours), or comes back. Empty output means silence.

Settings come from ../hbt-settings.json (written by the installer).
Manual check: python3 hbt_memory_watch.py --status
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE_HOME = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROFILE_HOME / "hbt-settings.json"
STATE_PATH = PROFILE_HOME / "state" / "hbt-memory-watch.json"
REMIND_EVERY = timedelta(hours=6)


def load_settings() -> dict:
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return {
        "endpoint": (data.get("openviking_endpoint") or "http://127.0.0.1:1933").rstrip("/"),
        "embed_endpoint": (data.get("openviking_embed_endpoint") or "").rstrip("/"),
        "services": data.get("openviking_services") or [],
        "fix_hint": data.get("openviking_fix_hint") or "Check the memory server (see the template README, Memory section).",
        "timezone": data.get("timezone") or "",
        "retry_delay": float(os.environ.get("HBT_WATCH_RETRY_DELAY", data.get("retry_delay", 20))),
    }


def _http(method: str, url: str, body: dict | None = None, timeout: float = 10) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _short(exc: Exception) -> str:
    text = str(getattr(exc, "reason", "") or exc).strip()
    return (text or exc.__class__.__name__)[:120]


def check(cfg: dict) -> list[str]:
    """Plain-English problems; empty list means memory is healthy."""
    try:
        if not _http("GET", f"{cfg['endpoint']}/health").get("healthy"):
            return ["the memory server says it is unhealthy"]
    except Exception as exc:  # noqa: BLE001 - any failure is an outage signal
        return [f"the memory server is not reachable ({_short(exc)})"]
    problems: list[str] = []
    try:
        result = _http("POST", f"{cfg['endpoint']}/api/v1/search/find",
                       {"query": "watchdog probe", "limit": 1, "score_threshold": 0}, timeout=20)
        if result.get("status") != "ok":
            problems.append(f"memory search failed ({result.get('error') or result.get('status')})")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"memory search failed ({_short(exc)})")
    if problems and cfg["embed_endpoint"]:
        try:
            _http("GET", f"{cfg['embed_endpoint']}/api/version", timeout=5)
        except Exception:  # noqa: BLE001
            problems.append("the local search model service is not reachable")
    return problems


def service_states(services: list[str]) -> str:
    states = []
    for name in services:
        try:
            out = subprocess.run(["systemctl", "--user", "is-active", name], capture_output=True, text=True, timeout=10)
            states.append(f"{name}={out.stdout.strip() or 'unknown'}")
        except Exception:  # noqa: BLE001
            states.append(f"{name}=unknown")
    return ", ".join(states)


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, STATE_PATH)


def _tz(name: str):
    if name:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(name)
        except Exception:  # noqa: BLE001
            pass
    return datetime.now().astimezone().tzinfo or timezone.utc


def _clock(ts: datetime, tz) -> str:
    return ts.astimezone(tz).strftime("%H:%M %Z")


def _duration(delta: timedelta) -> str:
    minutes = max(1, int(delta.total_seconds() // 60))
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes} min"


def decide(state: dict, problems: list[str], now: datetime, services: str, fix_hint: str, tz) -> tuple[dict, str]:
    """Pure transition logic: (new_state, message). Empty message means stay silent."""
    new = dict(state)
    new["last_checked_at"] = now.isoformat()
    if problems:
        detail = "; ".join(problems)
        svc = f" Services: {services}." if services else ""
        if state.get("status") != "down":
            new.update(status="down", down_since=now.isoformat(), last_alert_at=now.isoformat())
            return new, (
                f":red_circle: Your agents' long-term memory is DOWN as of {_clock(now, tz)}.\n"
                f"What failed: {detail}.{svc}\n"
                "Impact: the roles still work, but they cannot recall or save long-term memories until this is fixed.\n"
                f"{fix_hint}")
        last_alert = datetime.fromisoformat(state.get("last_alert_at") or now.isoformat())
        if now - last_alert >= REMIND_EVERY:
            new["last_alert_at"] = now.isoformat()
            since = datetime.fromisoformat(state["down_since"])
            return new, (
                f":red_circle: Reminder: your agents' long-term memory is still down, for {_duration(now - since)} "
                f"(since {_clock(since, tz)}). What failed: {detail}.\n{fix_hint}")
        return new, ""
    if state.get("status") == "down":
        since = datetime.fromisoformat(state["down_since"])
        new.update(status="up", down_since=None, last_alert_at=None, last_recovered_at=now.isoformat())
        return new, (
            f":large_green_circle: Your agents' long-term memory is back up at {_clock(now, tz)} "
            f"(was down {_duration(now - since)}). Work done during the outage may not have been saved to memory.")
    new["status"] = "up"
    return new, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="print the current result; do not change alert state")
    args = parser.parse_args(argv)
    cfg = load_settings()
    tz = _tz(cfg["timezone"])
    problems = check(cfg)
    if problems and cfg["retry_delay"] > 0:
        time.sleep(cfg["retry_delay"])
        problems = check(cfg)
    now = datetime.now(timezone.utc)
    if args.status:
        print(f"Memory: {'DOWN: ' + '; '.join(problems) if problems else 'healthy'}")
        return 0
    services = service_states(cfg["services"]) if problems and cfg["services"] else ""
    state, message = decide(load_state(), problems, now, services, cfg["fix_hint"], tz)
    save_state(state)
    if message:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
