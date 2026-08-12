#!/usr/bin/env python3
"""Rebuild .claude-plugin/marketplace.json from the plugins/ directory.

The marketplace file is generated, never hand-edited. `--check` compares the
generated result against the committed file and exits non-zero on drift; CI
runs that mode so a plugin can never be added without appearing in the shop
window (and vice versa).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
TARGET = ROOT / ".claude-plugin" / "marketplace.json"

HEADER = {
    "name": "evidence-lab-plugins",
    "description": (
        "Evidence Lab plugin marketplace: domain plugins that bundle research skills, "
        "commands and subagents into installable units."
    ),
    "owner": {"name": "Evidence Lab"},
}

# Reference implementations are the template made real. They must stay visible in
# the repository and out of the shop window.
HIDDEN_STATUSES = {"reference", "deprecated"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect() -> dict:
    entries = []
    for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        meta_path = plugin_dir / "meta.json"
        if not manifest_path.exists() or not meta_path.exists():
            print(f"skip {plugin_dir.name}: missing plugin.json or meta.json", file=sys.stderr)
            continue
        manifest, meta = load(manifest_path), load(meta_path)
        if meta.get("status") in HIDDEN_STATUSES:
            continue
        entry = {
            "name": manifest["name"],
            "description": manifest["description"],
            "version": manifest["version"],
            "author": manifest["author"],
            "source": f"./plugins/{plugin_dir.name}",
            "category": meta["category"],
        }
        if manifest.get("keywords"):
            entry["keywords"] = manifest["keywords"]
        entries.append(entry)
    return {**HEADER, "plugins": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed file is stale")
    args = ap.parse_args()

    generated = collect()
    rendered = json.dumps(generated, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not TARGET.exists():
            print("FAIL: .claude-plugin/marketplace.json is missing; run scripts/build_marketplace.py")
            return 1
        if TARGET.read_text(encoding="utf-8") != rendered:
            print("FAIL: marketplace.json is stale; run scripts/build_marketplace.py and commit the result")
            return 1
        print(f"OK: marketplace.json matches {len(generated['plugins'])} published plugin(s)")
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)} with {len(generated['plugins'])} published plugin(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
