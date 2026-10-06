#!/usr/bin/env python3
"""Local Creator review digest. Recorded links only; no board mutations or sends."""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import subprocess
import time
import unicodedata
from urllib.parse import parse_qsl, urlsplit


class DigestError(ValueError):
    """The local board could not be read consistently."""


def timestamp(value):
    if isinstance(value, str):
        try:
            parsed = dt.datetime.fromisoformat(value)
            value = parsed.timestamp() if parsed.tzinfo is not None else None
        except (ValueError, OverflowError, OSError):
            return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) and value > 0 else None
    except OverflowError:
        return None


def label(value, fallback):
    if not isinstance(value, str) or not value.strip():
        return fallback
    return " ".join("".join(
        " " if unicodedata.category(c).startswith("C") else "-" if c in "\u2013\u2014" else c
        for c in value).split()) or fallback


def current_review(detail):
    """Native show orders events by created_at ASC, id ASC, including ties."""
    events = detail.get("events")
    if not isinstance(events, list) or any(not isinstance(e, dict) for e in events):
        return None, None, "current review event unavailable"
    reviews = [e for e in events if e.get("kind") == "review_requested"]
    if not reviews:
        return None, None, "current review event unavailable"
    event = reviews[-1]
    run_id = event.get("run_id")
    runs = detail.get("runs")
    if (type(run_id) is not int or run_id <= 0 or not isinstance(runs, list)
            or any(not isinstance(r, dict) for r in runs)):
        return event, None, "current review run unavailable"
    matches = [r for r in runs if r.get("id") == run_id]
    if len(matches) != 1 or sum(e.get("run_id") == run_id for e in reviews) != 1:
        return event, None, "ambiguous current review handoff"
    run = matches[0]
    # Native zero-duration handoffs use the outcome as their run status.
    if run.get("outcome") != "review_requested" or run.get("status") not in ("review", "review_requested"):
        return event, None, "current review run unavailable"
    metadata = run.get("metadata")
    if not isinstance(metadata, dict):
        return event, None, "recorded approval thread missing"
    return event, metadata.get("approval_thread"), None


def recorded_link(record, subscriptions):
    if not isinstance(record, dict):
        return None, "recorded approval thread missing or malformed"
    if record.get("platform") != "slack":
        return None, "non-Slack approval thread"
    keys = ("workspace_url", "chat_id", "thread_id", "url")
    if any(not isinstance(record.get(k), str) or not record[k] for k in keys):
        return None, "recorded approval thread incomplete"
    origin, channel, thread, url = (record[k] for k in keys)
    if not re.fullmatch(r"[CDG][A-Z0-9]{8,}", channel) or not re.fullmatch(r"[0-9]{10}\.[0-9]{6}", thread):
        return None, "invalid channel or thread identifier"
    # Do not let urlsplit silently strip control characters or whitespace.
    if any(c.isspace() or unicodedata.category(c).startswith("C") for c in origin + url):
        return None, "invalid recorded URL"
    try:
        workspace = urlsplit(origin)
        link = urlsplit(url)
        host = workspace.hostname or ""
        if (workspace.scheme != "https" or workspace.netloc != host
                or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.slack\.com", host)
                or host.split(".")[0] in {"www", "api", "app", "help", "status"}
                or workspace.path or workspace.query or workspace.fragment or "?" in origin or "#" in origin):
            return None, "invalid workspace origin"
        if (link.scheme != "https" or link.netloc != workspace.netloc or link.fragment or "#" in url
                or link.path != f"/archives/{channel}/p{thread.replace('.', '')}"):
            return None, "workspace, channel or thread URL mismatch"
        query = parse_qsl(link.query, keep_blank_values=True, strict_parsing=True)
        if len({k for k, _ in query}) != len(query):
            return None, "duplicate URL query fields"
        expected = {"thread_ts": thread, "cid": channel}
        if any(k not in expected or v != expected[k] for k, v in query):
            return None, "conflicting URL query fields"
    except ValueError:
        return None, "invalid recorded URL"
    # Only an exact identified-origin tuple can corroborate this handoff.
    # Other destinations (including other threads in the same channel) nominate nothing.
    for sub in subscriptions:
        if (sub.get("platform"), sub.get("chat_id"), sub.get("thread_id")) != ("slack", channel, thread):
            continue
        delivery = sub.get("delivery_metadata")
        if delivery is not None and not isinstance(delivery, dict):
            return None, "malformed identified-origin evidence"
        if isinstance(delivery, dict) and any(
                key in delivery and delivery[key] != record[key]
                for key in ("platform", "workspace_url", "chat_id", "thread_id", "url")):
            return None, "conflicting identified-origin evidence"
    return url, None


def format_digest(entries, now=None):
    """Pure formatter for collected (show JSON, notify-list JSON) pairs."""
    now = time.time() if now is None else now
    rows = []
    seen = set()
    for detail, subscriptions in entries:
        if not isinstance(detail, dict) or not isinstance(detail.get("task"), dict):
            raise DigestError("invalid card details")
        task = detail["task"]
        card_id = task.get("id")
        if not isinstance(card_id, str) or not re.fullmatch(r"t_[0-9a-f]{8}", card_id) or card_id in seen:
            raise DigestError("invalid or duplicate card identity")
        seen.add(card_id)
        if task.get("status") != "review":
            raise DigestError("board changed during collection; retry the digest")
        if not isinstance(subscriptions, list) or any(not isinstance(s, dict) for s in subscriptions):
            raise DigestError("invalid subscription records")
        event, record, reason = current_review(detail)
        started = timestamp(event.get("created_at")) if event else None
        if started is None or started > now:
            age, started = "waiting time unavailable", None
        else:
            minutes = int((now - started) // 60)
            days, hours = divmod(minutes // 60, 24)
            age = f"waiting {days}d {hours}h" if days else f"waiting {hours}h {minutes % 60}m"
        url = None
        if reason is None:
            url, reason = recorded_link(record, subscriptions)
        thread = f"approval thread {url}" if url else f"approval thread link unavailable ({reason})"
        role = label(task.get("assignee"), "unassigned")
        title = label(task.get("title"), "untitled")
        rows.append((role, started if started is not None else math.inf, card_id,
                     f"- {title} ({card_id}), {age}, {thread}"))
    if not rows:
        return "Nothing waiting for approval."
    output, last_role = [], None
    for role, _, _, line in sorted(rows):
        if role != last_role:
            output.append(role + ":")
            last_role = role
        output.append(line)
    return "\n".join(output)


def read_json(*args):
    try:
        result = subprocess.run(["hermes", "kanban", "--board", "creator", *args],
                                capture_output=True, text=True, timeout=30, check=True)
        return json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # Do not echo raw command output, paths, credentials or task content.
        raise DigestError("local Kanban read failed") from exc


def collect(read=read_json):
    cards = read("list", "--status", "review", "--json")
    if not isinstance(cards, list):
        raise DigestError("invalid review list")
    entries, seen = [], set()
    for card in cards:
        card_id = card.get("id") if isinstance(card, dict) else None
        if not isinstance(card_id, str) or not re.fullmatch(r"t_[0-9a-f]{8}", card_id) or card_id in seen:
            raise DigestError("invalid or duplicate card identity")
        seen.add(card_id)
        detail = read("show", card_id, "--json")
        subscriptions = read("notify-list", card_id, "--json")
        if not isinstance(detail, dict) or not isinstance(detail.get("task"), dict) or detail["task"].get("id") != card_id:
            raise DigestError("card identity changed during collection")
        entries.append((detail, subscriptions))
    return entries


def main():
    try:
        output = format_digest(collect())
    except DigestError as exc:
        print(f"Approval digest failed ({exc}).")
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
