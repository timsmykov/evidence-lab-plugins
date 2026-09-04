#!/usr/bin/env python3
"""Inventory installed Codex plugins, standalone skills, and local companion apps."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path


def run_json(command: list[str]) -> dict:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"host inventory command failed: {command[0]}")
    try:
        value = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError("host inventory returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError("host inventory returned an unsupported payload")
    return value


def normalize_plugins(payload: dict) -> list[dict]:
    rows = payload.get("installed", [])
    normalized = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        raw_id = str(row.get("pluginId") or row.get("id") or row.get("name") or "")
        name = str(row.get("name") or raw_id.split("@", 1)[0])
        marketplace = row.get("marketplaceName") or row.get("marketplace")
        if marketplace is None and "@" in raw_id:
            marketplace = raw_id.split("@", 1)[1]
        selector = f"{name}@{marketplace}" if marketplace else raw_id
        normalized.append({
            "plugin_id": raw_id,
            "name": name,
            "marketplace": marketplace,
            "selector": selector,
            "version": str(row.get("version") or "unknown"),
            "enabled": bool(row.get("enabled", True)),
        })
    return sorted(normalized, key=lambda item: (item["selector"], item["version"]))


def scan_skills(roots: list[Path]) -> list[dict]:
    rows, seen = [], set()
    for root in roots:
        if not root.is_dir():
            continue
        for skill_file in sorted(root.glob("*/SKILL.md")):
            try:
                resolved = skill_file.resolve(strict=True)
                content = resolved.read_bytes()
            except OSError:
                continue
            identity = (skill_file.parent.name.casefold(), hashlib.sha256(content).hexdigest())
            if identity in seen:
                continue
            seen.add(identity)
            rows.append({
                "name": skill_file.parent.name,
                "path": str(skill_file.parent),
                "content_sha256": identity[1],
            })
    return sorted(rows, key=lambda item: (item["name"].casefold(), item["path"]))


def zotero_available() -> bool:
    if shutil.which("zotero"):
        return True
    try:
        with urllib.request.urlopen("http://127.0.0.1:23119/connector/ping", timeout=0.25) as response:
            return response.status < 500
    except Exception:
        return False


def collect_inventory(plugin_payload: dict | None = None, skill_roots: list[Path] | None = None) -> dict:
    payload = plugin_payload if plugin_payload is not None else run_json(["codex", "plugin", "list", "--json"])
    roots = skill_roots if skill_roots is not None else [Path.home() / ".agents" / "skills", Path.home() / ".codex" / "skills"]
    value = {
        "schema_version": 1,
        "host": "codex",
        "plugins": normalize_plugins(payload),
        "skills": scan_skills(roots),
        "local_apps": ["zotero"] if zotero_available() else [],
    }
    digest_value = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    value["digest"] = hashlib.sha256(digest_value).hexdigest()
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        rendered = json.dumps(collect_inventory(), indent=2, ensure_ascii=False) + "\n"
    except RuntimeError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}))
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
