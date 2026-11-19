#!/usr/bin/env python3
"""validate_specimens.py — lint the FaultyData specimen catalog.

Checks every specimens/*.yaml for the fields the registry requires.
Exits non-zero on any failure so it can gate PRs in CI.

Usage: python3 validate_specimens.py [specimens_dir]
"""
import re
import sys
from pathlib import Path

import yaml

CATEGORIES = {"status", "latency", "corruption", "sequence", "composite", "headers", "redirect"}
SEVERITIES = {"trivial", "moderate", "severe", "fatal"}
TEST_TAGS = {"retry-logic", "timeouts", "parsing", "headers", "auth", "semantics", "monitoring", "loops"}
ID_RE = re.compile(r"^FD-\d{4}-\d{3}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

FAULT_KEYS = {"status", "headers", "body", "corrupt", "delay", "stall_after", "drip", "hang", "reset", "raw", "sequence", "flaky", "phases", "retry_after"}


def check(path: Path) -> list[str]:
    errs = []
    try:
        sp = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"{path.name}: YAML parse error: {e}"]
    if not isinstance(sp, dict):
        return [f"{path.name}: top level is not a mapping"]

    for field in ("id", "title", "category", "severity", "anatomy", "signature"):
        if field not in sp:
            errs.append(f"{path.name}: missing '{field}'")

    sid = sp.get("id", "")
    if sid and not ID_RE.match(str(sid)):
        errs.append(f"{path.name}: id {sid!r} doesn't match FD-YYYY-NNN")
    slug = sp.get("slug")
    if slug is not None and not SLUG_RE.match(str(slug)):
        errs.append(f"{path.name}: slug {slug!r} must be lowercase-kebab")
    if sp.get("category") and sp["category"] not in CATEGORIES:
        errs.append(f"{path.name}: category {sp['category']!r} unknown")
    if sp.get("severity") and sp["severity"] not in SEVERITIES:
        errs.append(f"{path.name}: severity {sp['severity']!r} unknown")
    for t in sp.get("tests") or []:
        if t not in TEST_TAGS:
            errs.append(f"{path.name}: unknown test tag {t!r}")

    sig = sp.get("signature")
    if isinstance(sig, dict):
        if not any(k in sig for k in FAULT_KEYS):
            errs.append(f"{path.name}: signature has no fault fields")
        if "status" in sig and not isinstance(sig["status"], int):
            errs.append(f"{path.name}: signature.status must be an int")
    elif "signature" in sp:
        errs.append(f"{path.name}: signature must be a mapping")

    cit = sp.get("citation")
    if cit is not None:
        if not isinstance(cit, dict) or not cit.get("url") or not cit.get("source"):
            errs.append(f"{path.name}: citation needs both 'source' and 'url'")
    return errs


def main() -> int:
    d = Path(sys.argv[1] if len(sys.argv) > 1 else "specimens")
    files = sorted(d.glob("*.yaml"))
    if not files:
        sys.exit(f"no yaml files in {d}")
    all_errs = []
    ids = set()
    for f in files:
        all_errs += check(f)
        try:
            sid = yaml.safe_load(f.read_text()).get("id")
            if sid in ids:
                all_errs.append(f"{f.name}: duplicate id {sid}")
            ids.add(sid)
        except Exception:
            pass
    if all_errs:
        print("\n".join(all_errs))
        sys.exit(1)
    print(f"{len(files)} specimens OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
