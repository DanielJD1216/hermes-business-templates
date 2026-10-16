#!/usr/bin/env python3
"""Read a private Markdown checkpoint; calculate evidence coverage without writes or network."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
BASELINE = SKILL / "references/baseline.md"
TEMPLATE = SKILL / "templates/progress.md"
FOLLOWUP = "Owner decisions and additional outcomes"
FIELDS = (
    "Template revision", "Baseline SHA256", "Checkpoint state", "Current component",
    "Just verified", "Next incomplete action and prerequisite", "Next actor",
    "Owner action needed", "Blocker", "Continuation evidence",
    "Additional owner-required outcomes", "Setup complete",
)


def table(text, name, columns=None):
    # ponytail: canonical inline tables only; cells must not contain pipe characters.
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("| " + name + " |")]
    if len(starts) != 1:
        raise ValueError("Expected one " + name + " table")
    start = starts[0]
    headers = [cell.strip() for cell in lines[start].split("|")[1:-1]]
    if columns is not None and headers != columns:
        raise ValueError("Unexpected column names/order: " + name)
    width = len(headers)
    separator = lines[start + 1] if start + 1 < len(lines) else ""
    separators = separator.split("|")[1:-1]
    if not separator.startswith("|") or not separator.endswith("|") or len(separators) != width or any(not re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in separators):
        raise ValueError("Missing table separator: " + name)
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != width:
            raise ValueError("Malformed " + name + " table row")
        rows.append(cells)
    return rows


def fields(text):
    result = {}
    for name in FIELDS:
        matches = re.findall(r"^- " + re.escape(name) + r":[ \t]*(.*)$", text, re.M)
        if len(matches) != 1:
            raise ValueError("Expected one field: " + name)
        result[name] = matches[0].strip()
    return result


def meaningful(value):
    return bool(value) and value.casefold() not in {"none", "unknown", "pending", "todo", "n/a"} and not value.startswith("[")


def check(text):
    values = fields(text)
    required = [row[0] for row in table(BASELINE.read_text(encoding="utf-8"), "Component")]
    rows = table(text, "Component", ["Component", "State", "Evidence basis", "Evidence / observed time", "Limitation", "Next action / actor"])
    names = [row[0] for row in rows]
    if len(names) != len(set(names)) or set(names) != set(required):
        raise ValueError("Baseline rows must match the selected guide exactly, without duplicates")
    if values["Baseline SHA256"] != hashlib.sha256(BASELINE.read_bytes()).hexdigest():
        raise ValueError("Baseline fingerprint changed; reconcile evidence with the selected guide before updating it")
    if not re.fullmatch(r"[0-9a-f]{40}", values["Template revision"]):
        raise ValueError("Template revision must be the full source commit, not a moving branch name")
    for row in rows:
        if len(row) != 6 or row[1] not in {"verified", "failed", "not-tested"}:
            raise ValueError("Expected six baseline columns and a valid evidence state")
        if row[2] not in {"none", "fresh", "historical", "owner-relayed"}:
            raise ValueError("Unknown evidence basis")
        if row[1] in {"verified", "failed"} and (row[2] == "none" or not meaningful(row[3])):
            raise ValueError("Verified/failed rows need an evidence basis and a non-placeholder receipt/reference")
        if row[1] != "verified" and not meaningful(row[5]):
            raise ValueError("Every unfinished baseline row needs a next action and actor")
    decisions = table(text, "Decision", ["Decision", "State", "Implementation / reason", "Owner authority reference", "Affected baseline row"])
    decision_names = [row[0] for row in decisions]
    required_decisions = {row[0] for row in table(TEMPLATE.read_text(encoding="utf-8"), "Decision")}
    if len(decision_names) != len(set(decision_names)) or not required_decisions.issubset(decision_names):
        raise ValueError("Required owner decisions are missing or duplicated")
    unresolved = 0
    for row in decisions:
        if len(row) != 5 or row[1] not in {"not-offered", "not-decided", "selected", "declined", "deferred"}:
            raise ValueError("Malformed owner decision or unknown decision state")
        if row[1] in {"selected", "declined"}:
            if not meaningful(row[2]) or not meaningful(row[3]):
                raise ValueError("Resolved decisions need a reason and owner-authority reference")
            if row[1] == "declined" and row[0] in required_decisions:
                affected = {name.strip() for name in row[4].split(";")}
                if not affected.issubset(required):
                    raise ValueError("Declined required decisions must identify affected baseline rows")
                if any(component[0] in affected and component[1] == "verified" for component in rows):
                    raise ValueError("A declined required decision contradicts a verified affected baseline row")
                unresolved += 1
        else:
            unresolved += 1
    verified = sum(row[1] == "verified" for row in rows)
    owner = sum(row[1] == "verified" and row[2] == "owner-relayed" for row in rows)
    percent = round(100 * verified / len(required), 1)
    complete = values["Checkpoint state"] == "complete"
    state, actor = values["Checkpoint state"], values["Next actor"]
    actors = {"continue": {"agent"}, "owner-action": {"owner"}, "waiting": {"job"},
              "blocked": {"agent", "owner", "external"}, "paused": {"owner"}, "complete": {"none"}}
    if state not in actors or actor not in actors[state]:
        raise ValueError("Checkpoint state and next actor are unknown or contradictory")
    for name in ("Just verified", "Owner action needed", "Blocker", "Continuation evidence"):
        if values[name] != "none" and not meaningful(values[name]):
            raise ValueError("Use concrete text or literal none for: " + name)
    if actor == "owner" and not meaningful(values["Owner action needed"]):
        raise ValueError("Owner action must identify the exact next owner step")
    if actor != "owner" and values["Owner action needed"] != "none":
        raise ValueError("Owner action must be none when the next actor is not the owner")
    if state == "blocked" and not meaningful(values["Blocker"]):
        raise ValueError("Blocked checkpoints must identify the blocker")
    if state == "waiting" and not meaningful(values["Continuation evidence"]):
        raise ValueError("Waiting requires a job reference and registered continuation/delivery evidence")
    if state != "waiting" and values["Continuation evidence"] != "none":
        raise ValueError("Only waiting checkpoints may claim a pending continuation")
    extras = values["Additional owner-required outcomes"]
    if not extras or extras.startswith("["):
        raise ValueError("Record remaining owner outcomes, unknown, or none outstanding")
    if values["Setup complete"] != ("yes" if complete else "no"):
        raise ValueError("Setup complete contradicts the checkpoint state")
    if complete:
        if verified != len(required) or unresolved or extras != "none outstanding":
            raise ValueError("Completion requires all baseline evidence, resolved decisions and no outstanding owner outcomes")
        if any(values[name] != "none" for name in ("Current component", "Next incomplete action and prerequisite", "Blocker")):
            raise ValueError("A completed setup cannot retain an active component, next action or blocker")
    else:
        if not meaningful(values["Next incomplete action and prerequisite"]):
            raise ValueError("An unfinished setup needs a concrete next action and prerequisite")
        current = values["Current component"]
        states = {row[0]: row[1] for row in rows}
        if current == FOLLOWUP:
            if not unresolved and extras == "none outstanding":
                raise ValueError("No remaining owner decisions or outcomes justify this checkpoint")
        elif current not in states or states[current] == "verified":
            raise ValueError("Current component must be unfinished; invalidate affected evidence before reworking a verified row")
    footer = (f"Baseline verified: {verified}/{len(required)} ({percent:.1f}%; {owner} owner-confirmed)\n"
              f"Setup: {values['Checkpoint state']} | Current: {values['Current component']}\n"
              f"Just verified: {values['Just verified']}\n"
              f"Next ({values['Next actor']}): {values['Next incomplete action and prerequisite']}\n"
              f"Your action: {values['Owner action needed']}")
    if values["Blocker"] != "none":
        footer += "\nBlocker: " + values["Blocker"]
    if state == "waiting":
        footer += "\nContinuation: " + values["Continuation evidence"]
    return {"status": "valid", "verified": verified, "total": len(required), "percent": percent,
            "owner_confirmed": owner, "unresolved_decisions": unresolved,
            "complete": complete, "footer": footer}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, nargs="?")
    parser.add_argument("--describe", action="store_true", help="Show the local baseline fingerprint and required row names")
    args = parser.parse_args()
    if bool(args.record) == args.describe:
        parser.error("Supply either a private record or --describe")
    try:
        if args.describe:
            report = {"baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
                      "components": [row[0] for row in table(BASELINE.read_text(encoding="utf-8"), "Component")]}
        else:
            report = check(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "invalid", "error": str(error)}))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
