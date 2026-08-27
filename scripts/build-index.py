#!/usr/bin/env python3
"""Generate index.json, the distribution manifest for virtual-jp.

Every file under skills/ is shipped to a calling repository at a target path
inside .claude/. The manifest is derived from the tree and never edited by
hand; run this script after adding, renaming or removing anything under
skills/, and see CLAUDE.md for the checks.

    python3 scripts/build-index.py            # write index.json
    python3 scripts/build-index.py --check    # fail if index.json is stale
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
INDEX = ROOT / "index.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"

TARGET_ROOT = ".claude"
PREFIX = "vjp-"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_target(target):
    """Enforce the naming rule the calling repository's cleanup depends on.

    An update removes virtual-jp's files by name alone: it sweeps every
    vjp-* entry directly inside .claude/ or inside one of its subdirectories.
    A target that carries no such component could never be removed again, so
    it is rejected here rather than shipped.
    """
    parts = target.split("/")
    if parts[0] != TARGET_ROOT:
        return "target must start with %s/" % TARGET_ROOT
    if len(parts) < 2:
        return "target must name a file below %s/" % TARGET_ROOT
    if parts[1].startswith(PREFIX):
        return None
    if len(parts) > 2 and parts[2].startswith(PREFIX):
        return None
    return (
        "target has no %s* component directly inside a %s/ directory, so an "
        "update could never remove it" % (PREFIX, TARGET_ROOT)
    )


def collect():
    files, errors = [], []
    if not SKILLS.is_dir():
        return files, ["skills/ does not exist"]
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if not skill.name.startswith(PREFIX):
            errors.append(
                "skills/%s: every skill directory must be named %s* - see "
                "CLAUDE.md" % (skill.name, PREFIX)
            )
            continue
        for path in sorted(p for p in skill.rglob("*") if p.is_file()):
            if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
                continue
            source = path.relative_to(ROOT).as_posix()
            target = "%s/skills/%s" % (TARGET_ROOT, path.relative_to(SKILLS).as_posix())
            problem = check_target(target)
            if problem:
                errors.append("%s -> %s: %s" % (source, target, problem))
                continue
            files.append({"source": source, "target": target, "sha256": sha256(path)})
    if not files and not errors:
        errors.append("skills/ contains no files to distribute")
    return files, errors


def build():
    files, errors = collect()
    if errors:
        for error in errors:
            print("error: %s" % error, file=sys.stderr)
        raise SystemExit(1)
    version = json.loads(PLUGIN.read_text())["version"]
    manifest = {
        "name": "virtual-jp",
        "version": version,
        "targetRoot": TARGET_ROOT,
        "files": sorted(files, key=lambda f: f["target"]),
    }
    return json.dumps(manifest, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if index.json differs from what would be written",
    )
    args = parser.parse_args()
    content = build()
    if args.check:
        current = INDEX.read_text() if INDEX.exists() else ""
        if current != content:
            print(
                "error: index.json is stale - run python3 scripts/build-index.py",
                file=sys.stderr,
            )
            raise SystemExit(1)
        print("index.json is up to date (%d files)" % len(json.loads(content)["files"]))
        return
    INDEX.write_text(content)
    print("wrote index.json (%d files)" % len(json.loads(content)["files"]))


if __name__ == "__main__":
    main()
