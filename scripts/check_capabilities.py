#!/usr/bin/env python3
"""Offline catalog/reference/asset checks. Stdlib only; never import or boot Hermes."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"total": 333, "included": 198, "excluded": 39, "unknown": 96}
KINDS = {"skill": 160, "plugin": 8, "mcp": 13, "core_toolset": 17}
ROUTES = {"generic-procedure", "upstream-package", "upstream-reference",
          "blocked", "vendor-service", "native-runtime", "rights-review-required"}
SHA256 = re.compile(r"[a-f0-9]{64}")
PRIVATE = re.compile(
    r"/home/|/mnt/|\bjinni\b|DOO[ -]MADE|\bJayden\b|\bDaniel\b|"
    r"(?:sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+|gh[pousr]_[A-Za-z0-9]+)|"
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", re.I)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def local(ref):
    path, _, anchor = ref.partition("#")
    p = (ROOT / path).resolve()
    need(p.is_relative_to(ROOT), f"Outside repository: {ref}")
    need(p.is_file(), f"Missing local file: {ref}")
    if anchor:
        need(f'id="{anchor}"' in p.read_text(), f"Missing anchor: {ref}")
    return p


def url(value):
    u = urlsplit(value)
    need(u.scheme == "https" and u.hostname and not u.username and not u.password,
         f"Not a public HTTPS reference: {value}")
    need(u.hostname not in {"localhost", "127.0.0.1", "0.0.0.0"}, "Local endpoint leaked")
    need(not u.query, f"Query-bearing acquisition URL: {value}")


def check(catalog, sources):
    rows = catalog["capabilities"]
    ids = [r["id"] for r in rows]
    need(len(ids) == len(set(ids)), "Duplicate capability ID")
    counts = {"total": len(rows), **dict(Counter(r["catalog_partition"] for r in rows))}
    need(counts == catalog["counts"] == EXPECTED, "Partition coverage/count drift")
    included = [r for r in rows if r["catalog_partition"] == "included"]
    need(dict(Counter(r["kind"] for r in included)) == catalog["included_by_kind"] == KINDS,
         "Included kind coverage/count drift")
    need(dict(Counter(r["delivery"] for r in included)) == catalog["delivery_counts"],
         "Delivery count drift")
    safety = catalog["safety"]
    need(safety["preserve_existing_main"] is True and safety["fixed_roster"] is True,
         "Main-agent/roster invariant")
    need(safety["required_tools"] == ["LEANN", "Obsidian", "Parsec"],
         "Required search/viewer/debugging invariant")
    need(safety["slack"] == "mention-only"
         and safety["baseline_schedule"].startswith("memory-watchdog and LEANN index-refresh;"),
         "Slack/schedule invariant")
    sheet = (ROOT / "capabilities/REFERENCE.md").read_text()
    blocked = {(b["id"], b["scope"]) for b in catalog["blockers"]}
    need(len(blocked) == len(catalog["blockers"]), "Duplicate blocker")
    for b in catalog["blockers"]:
        need(b["id"] in ids and b["reason"] and b["required_to_unblock"], "Incomplete blocker")
        need(b["id"] in sheet and b["reason"] in sheet, "Blocker missing from reference sheet")
    for r in rows:
        need(r["runtime_verified"] is False, f'False runtime claim: {r["id"]}')
        need(re.fullmatch(re.escape(r["kind"]) + r"-\d{4}", r["id"]), "Malformed capability ID")
        if r["catalog_partition"] != "included":
            need(r["delivery"] == "not-selected" and r["source_ref"] is None
                 and r["bundled_ref"] is None and r["verification"] == "not-tested",
                 f'Unassessed entry promoted: {r["id"]}')
            continue
        need(r["delivery"] in ROUTES, f'Unknown route: {r["id"]}')
        for key in ("name", "purpose", "acquisition", "platform", "dependencies",
                    "authentication", "cost", "access", "license", "redistribution", "verification"):
            need(isinstance(r.get(key), str) and r[key].strip(), f'Missing {key}: {r["id"]}')
            need(not re.search(r"\bTODO\b|Need verification against selected capability", r[key]),
                 f'Placeholder: {r["id"]}/{key}')
        need(sheet.count(f'id="{r["id"]}"') == 1, f'Reference coverage: {r["id"]}')
        if r["delivery"] == "blocked":
            need((r["id"], "source-and-license") in blocked and r["bundled_ref"] is None,
                 "Missing unavailable-source blocker")
            continue
        need(r["source_ref"] in sources, f'Missing source: {r["id"]}')
        if r["source_url"]:
            url(r["source_url"])
        if r["delivery"] == "generic-procedure":
            local(r["bundled_ref"])
            need(r["license"].startswith("MIT") and r["source_ref"] == "generic",
                 "Bundled procedure licensing")
        elif r["delivery"] != "vendor-service":
            source = sources[r["source_ref"]]
            need(re.fullmatch(r"[a-f0-9]{40}", source["revision"]), "Unpinned source")
            need(SHA256.fullmatch(r["source_sha256"] or ""), "Missing public source hash")
            expected_url = source["repository"].replace("github.com", "raw.githubusercontent.com")
            expected_url += "/" + source["revision"] + "/" + r["source_path"]
            need(r["source_url"] == expected_url, f'Source path/revision mismatch: {r["id"]}')
        if r["license"].startswith("UNRESOLVED"):
            need(r["delivery"] == "rights-review-required"
                 and (r["id"], "redistribution") in blocked and r["bundled_ref"] is None,
                 "Unresolved rights must prohibit bundling")
        if r["delivery"] == "rights-review-required":
            need(r["license"].startswith("UNRESOLVED"), "Rights-review route must name unresolved rights")
    asset_ids = []
    asset_paths = []
    for asset in catalog["bundled_files"]:
        p = local(asset["path"])
        need(hashlib.sha256(p.read_bytes()).hexdigest() == asset["sha256"], "Bundled file hash drift")
        local(asset["license_path"])
        asset_paths.append(asset["path"])
        asset_ids.extend(asset["capability_ids"])
        for capability_id in asset["capability_ids"]:
            local(asset["path"] + "#" + capability_id)
    generic_ids = [r["id"] for r in included if r["delivery"] == "generic-procedure"]
    need(sorted(asset_ids) == sorted(generic_ids), "Bundled capability coverage mismatch")
    actual_assets = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "reusable").rglob("*") if p.is_file())
    need(actual_assets == sorted(asset_paths), "Missing or unlisted bundled asset")
    for source in sources.values():
        for key in ("repository", "tree_url", "archive_url", "license_url", "url"):
            if source.get(key):
                url(source[key])
    for text in (json.dumps(catalog), json.dumps(sources), sheet,
                 (ROOT / "reusable/procedures.md").read_text()):
        need(not PRIVATE.search(text), "Private identifier/path/credential pattern")
    for path in (ROOT / "capabilities/REFERENCE.md", ROOT / "reusable/procedures.md"):
        for ref in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if ref.startswith("https://"):
                url(ref)
            else:
                target, _, anchor = ref.partition("#")
                relative = (path.parent / target).resolve().relative_to(ROOT)
                local(str(relative) + ("#" + anchor if anchor else ""))
    return {"result": "PASS", "counts": counts, "included_by_kind": KINDS,
            "delivery_counts": catalog["delivery_counts"], "bundled_files": len(asset_paths),
            "bundled_procedures": len(asset_ids), "explicit_blockers": len(blocked),
            "runtime_checks": "not performed"}


def self_test(catalog, sources):
    def reject(mutator):
        c = deepcopy(catalog)
        mutator(c)
        try:
            check(c, sources)
        except (ValueError, KeyError):
            return
        raise ValueError("Negative fixture was accepted")
    reject(lambda c: c["capabilities"].pop())
    reject(lambda c: c["capabilities"][0].update(runtime_verified=True))
    reject(lambda c: c["capabilities"][0].update(bundled_ref="../../outside.md"))
    reject(lambda c: c["bundled_files"][0].update(sha256="0" * 64))
    reject(lambda c: c["blockers"].clear())
    reject(lambda c: c["capabilities"][0].update(dependencies=""))
    def bypass_rights(c):
        record = next(r for r in c["capabilities"] if r["delivery"] == "rights-review-required")
        record["delivery"] = "upstream-package"
        c["delivery_counts"] = dict(Counter(r["delivery"] for r in c["capabilities"]
                                          if r["catalog_partition"] == "included"))
    reject(bypass_rights)
    return 7


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "capabilities/catalog.json").read_text())
    sources = json.loads((ROOT / "capabilities/sources.json").read_text())
    result = check(catalog, sources)
    if args.self_test:
        result["negative_fixtures_rejected"] = self_test(catalog, sources)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
