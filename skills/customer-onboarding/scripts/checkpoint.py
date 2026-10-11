#!/usr/bin/env python3
"""Private evidence receipts, not an installer or human-approval authenticator."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

REQUIRED = {
    "host": ("host.md",), "identity": ("identity.md",), "reference": ("reference.md",),
    "exports": ("sources.json",), "review": ("consolidated.md", "context-review.json"),
    "boundaries": ("boundaries.md",),
    "files": ("SOUL.md", "AGENTS.md", "USER.md", "context.md", "tools.md", "team.json", "write-plan.md"),
    "install": ("install.md",), "connections": ("connections.md",), "closeout": ("closeout.md",),
}
STAGES = tuple(REQUIRED)
GATED = {"identity", "review", "boundaries", "files", "closeout"}
BLOCKERS = ("none", "access", "prerequisite", "approval", "source", "privacy", "recovery", "drift", "verification")
ID = re.compile(r"[a-zA-Z0-9_-]{1,80}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(safe(path).is_file(), "JSON evidence must be a regular file")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, "invalid JSON number"))


def safe(path):
    require(path.is_absolute() and ".." not in path.parts, "absolute non-traversing path required")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink refused")
    if path.is_file():
        require(path.stat().st_nlink == 1, "hardlink refused")
    return path


def state_root(raw, create=False):
    root = safe(Path(raw).expanduser())
    require(not any((p / ".git").exists() for p in (root, *root.parents)), "state must be outside Git checkouts")
    if create:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(root.is_dir(), "private state directory missing")
    require(root.stat().st_uid == os.getuid() and root.stat().st_mode & 0o077 == 0,
            "state directory must be owner-only (0700)")
    return root


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sources(root):
    data = read_json(safe(root / "evidence/exports/sources.json"))
    require(isinstance(data, dict) and type(data.get("skipped")) is bool
            and isinstance(data.get("sources"), list), "invalid sources manifest")
    require(data["skipped"] == (not data["sources"]), "sources must be present or explicitly skipped")
    origins = {}
    for entry in data["sources"]:
        require(isinstance(entry, dict), "invalid source entry")
        sid, origin = entry.get("id"), entry.get("origin")
        require(isinstance(sid, str) and re.fullmatch(r"source-[0-9]{3}", sid) and sid not in origins,
                "invalid/duplicate source ID")
        require(origin is None or isinstance(origin, str) and ID.fullmatch(origin), "invalid origin ID")
        require(entry.get("file") == sid + ".md", "source filename must match ID")
        for key in ("platform", "model", "exported_at", "coverage", "lineage"):
            require(isinstance(entry.get(key), str) and entry[key].strip(), "source provenance missing: " + key)
        require(safe(root / "evidence/exports" / entry["file"]).is_file(), "raw export missing: " + sid)
        origins[sid] = origin
    return origins


def validate_review(root):
    origins = sources(root)
    data = read_json(safe(root / "evidence/review/context-review.json"))
    require(isinstance(data, dict) and isinstance(data.get("claims"), list), "invalid review ledger")
    seen = set()
    for claim in data["claims"]:
        require(isinstance(claim, dict), "invalid claim")
        cid = claim.get("id")
        require(isinstance(cid, str) and ID.fullmatch(cid) and cid not in seen, "invalid/duplicate claim ID")
        seen.add(cid)
        refs, flags = claim.get("sources"), claim.get("flags")
        require(isinstance(refs, list) and refs and all(isinstance(s, str) and s in (set(origins) | {"owner"}) for s in refs),
                "claim source is unavailable")
        require(isinstance(flags, list) and all(isinstance(f, str) and f in {"conflict", "stale", "inferred", "duplicate", "domain"} for f in flags),
                "invalid review flags")
        available = {origins[s] for s in refs if s != "owner" and origins[s] is not None}
        if "owner" in refs:
            available.add("owner")
        count = claim.get("independent_origins")
        require(type(count) is int and 0 <= count <= len(available), "copied/unknown sources are not independent evidence")
        for key in ("text", "reason", "source_locations"):
            require(isinstance(claim.get(key), str) and claim[key].strip(), "claim detail missing: " + key)
        domain, audience = claim.get("domain"), claim.get("audience")
        decision, dest = claim.get("decision"), claim.get("destination")
        require(domain in ("personal", "business", "mixed", "unknown") and audience in ("owner", "team"), "invalid domain/audience")
        if decision == "REVIEW":
            require(audience == "owner" and dest == "private-review", "REVIEW stays owner-private")
        elif decision == "EXCLUDE":
            require(dest == "none", "EXCLUDE has no adoption destination")
        elif decision == "INCLUDE":
            require((domain, audience, dest) in {("personal", "owner", "owner-personal"),
                    ("business", "owner", "owner-business"), ("business", "team", "shared-business")},
                    "unsafe adoption domain/audience/destination")
            require(not flags or isinstance(claim.get("resolution_ref"), str)
                    and ID.fullmatch(claim["resolution_ref"]), "flagged adoption needs a resolution reference")
        else:
            raise ValueError("invalid claim decision")


def snapshot(root, stage):
    directory = safe(root / "evidence" / stage)
    require(directory.is_dir(), "missing evidence directory: " + stage)
    names = set(REQUIRED[stage])
    if stage == "exports":
        names |= {sid + ".md" for sid in sources(root)}
    if stage == "review":
        validate_review(root)
    require({p.name for p in directory.iterdir()} == names, "missing or unexpected artifacts: " + stage)
    files = {}
    for name in sorted(names):
        path = safe(directory / name)
        require(path.is_file() and path.stat().st_size, "empty/missing artifact: " + name)
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def verify(root, state):
    require(isinstance(state, dict) and set(state) == {"schema", "stages", "blocker", "archived"}
            and state["schema"] == 1, "invalid checkpoint schema")
    require(state["blocker"] in BLOCKERS and isinstance(state["stages"], list), "invalid checkpoint state")
    require(len(state["stages"]) <= len(STAGES), "invalid stage count")
    for index, receipt in enumerate(state["stages"]):
        require(isinstance(receipt, dict) and set(receipt) == {"stage", "files", "digest", "approval"}
                and receipt["stage"] == STAGES[index], "invalid stage sequence")
        stage, approval = receipt["stage"], receipt["approval"]
        require(approval is None or isinstance(approval, str) and ID.fullmatch(approval), "invalid approval reference")
        require(stage not in GATED or approval is not None, "approval missing: " + stage)
        files = snapshot(root, stage)
        require(files == receipt["files"] and digest(files) == receipt["digest"], "evidence drift: " + stage)
    require(type(state["archived"]) is bool and state["archived"] == (len(state["stages"]) == len(STAGES)), "invalid archive state")


@contextmanager
def locked(root):
    # ponytail: local single-writer setup; a distributed service needs another store.
    fd = os.open(safe(root / ".lock"), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def save(root, state):
    target = safe(root / "checkpoint.json")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=root, prefix=".checkpoint-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def run(root, command, stage=None, expected=None, approval=None, reason=None):
    with locked(root):
        checkpoint = safe(root / "checkpoint.json")
        if command == "init":
            require(not checkpoint.exists(), "checkpoint exists; use status")
            state = {"schema": 1, "stages": [], "blocker": "none", "archived": False}
            save(root, state)
        else:
            state = read_json(checkpoint)
        verify(root, state)
        current = STAGES[len(state["stages"])] if not state["archived"] else None
        if command == "block":
            require(reason in BLOCKERS, "invalid blocker")
            state["blocker"] = reason
            save(root, state)
        if command == "advance":
            require(current is not None and stage == current, "out-of-order stage")
            require(state["blocker"] == "none", "resolve recorded blocker before advancing")
            files = snapshot(root, current)
            require(digest(files) == expected, "proposal changed or digest missing")
            require(approval is None or isinstance(approval, str) and ID.fullmatch(approval), "invalid approval reference")
            require(current not in GATED or approval is not None, "owner approval reference required")
            state["stages"].append({"stage": current, "files": files, "digest": expected, "approval": approval})
            state["archived"] = len(state["stages"]) == len(STAGES)
            save(root, state)
            current = STAGES[len(state["stages"])] if not state["archived"] else None
        result = {"stage": current, "archived": state["archived"], "blocker": state["blocker"],
                  "next_action": "resolve-" + state["blocker"] if state["blocker"] != "none" else current or "archive-complete"}
        if current:
            try:
                result["proposal_digest"] = digest(snapshot(root, current))
                result["approval_required"] = current in GATED
            except (ValueError, OSError) as error:
                result["pending_evidence"] = str(error)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    advance = sub.add_parser("advance")
    advance.add_argument("--stage", required=True, choices=STAGES)
    advance.add_argument("--digest", required=True)
    advance.add_argument("--receipt")
    block = sub.add_parser("block")
    block.add_argument("--reason", choices=BLOCKERS, required=True)
    args = parser.parse_args(argv)
    try:
        root = state_root(args.state_dir, create=args.command == "init")
        result = run(root, args.command, stage=getattr(args, "stage", None), expected=getattr(args, "digest", None),
                     approval=getattr(args, "receipt", None), reason=getattr(args, "reason", None))
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"blocked": True, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
