#!/usr/bin/env python3
"""Check local links in the customer reading set. Stdlib only; no network/writes."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def local_links(document):
    # ponytail: inline Markdown links only; extend if reference-style links appear.
    return re.findall(r"\]\(([^\s)]+)\)", document.read_text(encoding="utf-8"))


def check(root):
    files = [root / "README.md", root / "AGENTS.md"]
    for folder in ("skills/customer-onboarding", "skills/hermes-update-safety", "capabilities", "reusable"):
        files.extend(sorted((root / folder).rglob("*.md")))
    checked = 0
    errors = []
    for source in files:
        if not source.is_file():
            errors.append(f"Missing reading-set file: {source.relative_to(root)}")
            continue
        for link in local_links(source):
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (source.parent / unquote(url.path)).resolve() if url.path else source
            if not target.is_relative_to(root.resolve()):
                errors.append(f"Link leaves the package: {source.relative_to(root)} -> {link}")
                continue
            checked += 1
            if not target.exists():
                errors.append(f"Missing: {source.relative_to(root)} -> {link}")
            elif url.fragment and target.is_file() and target.suffix == ".md":
                headings = re.findall(r"^#{1,6} (.+)$", target.read_text(encoding="utf-8"), re.M)
                anchors = {re.sub(r"[^\w-]", "", h.lower().replace(" ", "-")) for h in headings}
                anchors.update(re.findall(r'<a id="([^"]+)"', target.read_text(encoding="utf-8")))
                if unquote(url.fragment) not in anchors:
                    errors.append(f"Missing heading: {source.relative_to(root)} -> {link}")
    return len(files), checked, errors


if __name__ == "__main__":
    documents, links, errors = check(ROOT)
    for error in errors:
        print(error)
    print(f"Customer guide: {documents} documents, {links} local links, {len(errors)} failures")
    raise SystemExit(bool(errors))
