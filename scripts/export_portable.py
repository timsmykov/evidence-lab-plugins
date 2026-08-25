#!/usr/bin/env python3
"""Flatten plugin skills into a portable layout for non-Claude runtimes.

Claude Code installs plugins whole. Other runtimes load one skill directory at
a time, so this writes dist/portable/<plugin>__<skill>/ with SKILL.md and its
supporting files. A plugin is exported only when meta.json explicitly lists the
requested runtime in portable_to. internal_only plugins are always skipped;
reference plugins are skipped unless --include-reference is given.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
DIST = ROOT / "dist" / "portable"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--runtime",
        choices=("codex", "chatgpt", "hermes"),
        default="codex",
        help="export only plugins verified for this runtime (default: codex)",
    )
    ap.add_argument("--include-reference", action="store_true")
    args = ap.parse_args()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    exported, skipped = 0, []
    for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        meta_path = plugin_dir / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("risk_level") == "internal_only":
            skipped.append(f"{plugin_dir.name} (internal_only)")
            continue
        if args.runtime not in meta.get("portable_to", []):
            skipped.append(f"{plugin_dir.name} (not verified for {args.runtime})")
            continue
        if meta.get("status") in {"reference", "deprecated"} and not args.include_reference:
            skipped.append(f"{plugin_dir.name} ({meta.get('status')})")
            continue
        for skill_dir in sorted((plugin_dir / "skills").iterdir()):
            if not skill_dir.is_dir():
                continue
            target = DIST / f"{plugin_dir.name}__{skill_dir.name}"
            shutil.copytree(skill_dir, target)
            shutil.rmtree(target / "evals", ignore_errors=True)
            exported += 1

    print(f"exported {exported} skill(s) for {args.runtime} to {DIST.relative_to(ROOT)}")
    for item in skipped:
        print(f"skipped {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
