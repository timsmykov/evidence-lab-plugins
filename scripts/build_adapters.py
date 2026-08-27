#!/usr/bin/env python3
"""Generate Claude Code and Codex adapters from host-neutral pack.json files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CORE_CATALOG = PACKS / "core" / "evidence-lab-core" / "catalog" / "packs.json"
CORE_EXTERNAL_PLUGINS = PACKS / "core" / "evidence-lab-core" / "catalog" / "external-plugin-candidates.json"
CORE_EXTERNAL_SELECTOR = PACKS / "core" / "evidence-lab-core" / "skills" / "evidence-lab-onboarding" / "scripts" / "select_external_plugins.py"
HIDDEN_STATUSES = {"reference", "deprecated"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pack_dirs() -> list[Path]:
    return sorted(path.parent for path in PACKS.glob("*/*/pack.json"))


def rendered_json(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def claude_manifest(pack: dict) -> dict:
    return {
        "name": pack["id"], "description": pack["description"], "version": pack["version"],
        "author": pack["author"], "keywords": pack["capabilities"],
        "homepage": "https://github.com/timsmykov/evidence-lab-plugins",
        "repository": "https://github.com/timsmykov/evidence-lab-plugins",
        "license": pack["license"],
    }


def codex_manifest(pack: dict) -> dict:
    interface = pack["interface"]
    return {
        **claude_manifest(pack),
        "skills": "./skills/",
        "interface": {
            "displayName": pack["display_name"], "shortDescription": interface["short_description"],
            "longDescription": interface["long_description"], "developerName": pack["author"]["name"],
            "category": pack["category"], "capabilities": interface["capabilities"],
            "defaultPrompt": interface["default_prompt"],
        },
    }


def build_outputs() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    published: list[tuple[Path, dict, dict]] = []
    for directory in pack_dirs():
        pack = load(directory / "pack.json")
        meta = load(directory / "meta.json")
        outputs[directory / ".claude-plugin" / "plugin.json"] = rendered_json(claude_manifest(pack))
        outputs[directory / ".codex-plugin" / "plugin.json"] = rendered_json(codex_manifest(pack))
        if meta["status"] not in HIDDEN_STATUSES:
            published.append((directory, pack, meta))

    catalog = {"schema_version": 1, "packs": [
        {key: pack[key] for key in ("id", "version", "layer", "display_name", "description", "capabilities", "selection", "dependencies", "conflicts", "runtimes")}
        for _, pack, _ in published
    ]}
    outputs[CORE_CATALOG] = rendered_json(catalog)
    outputs[CORE_EXTERNAL_PLUGINS] = (ROOT / "catalog" / "external-plugin-candidates.json").read_text(encoding="utf-8")
    outputs[CORE_EXTERNAL_SELECTOR] = (ROOT / "scripts" / "select_external_plugins.py").read_text(encoding="utf-8")

    claude_entries, codex_entries = [], []
    for directory, pack, meta in published:
        rel = directory.relative_to(ROOT).as_posix()
        claude_entries.append({
            "name": pack["id"], "description": pack["description"], "version": pack["version"],
            "author": pack["author"], "source": f"./{rel}", "category": meta["category"],
            "keywords": pack["capabilities"],
        })
        codex_entries.append({
            "name": pack["id"], "source": {"source": "local", "path": f"./{rel}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": pack["category"],
        })

    outputs[CLAUDE_MARKETPLACE] = rendered_json({
        "name": "evidence-lab-plugins", "description": "Evidence Lab agent-first research packs for Claude Code and Codex.",
        "owner": {"name": "Evidence Lab"}, "plugins": claude_entries,
    })
    outputs[CODEX_MARKETPLACE] = rendered_json({
        "name": "evidence-lab-plugins", "interface": {"displayName": "Evidence Lab"}, "plugins": codex_entries,
    })
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        for path in stale:
            print(f"FAIL: generated adapter is stale: {path}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(outputs)} generated adapter and catalog file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
