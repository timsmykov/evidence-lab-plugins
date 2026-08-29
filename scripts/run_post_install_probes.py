#!/usr/bin/env python3
"""Validate and run profile-aware probes against installed Evidence Lab packs."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "catalog/post-install-probes.json"
SCHEMA = ROOT / "schemas/post-install-probes.schema.json"
CATALOG = ROOT / "packs/core/evidence-lab-core/catalog/packs.json"


class ProbeError(RuntimeError):
    pass


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def index_registry(registry: dict, catalog: dict) -> dict[str, dict]:
    errors = sorted(Draft202012Validator(load(SCHEMA)).iter_errors(registry), key=lambda error: list(error.path))
    if errors:
        raise ProbeError(f"registry schema: {errors[0].message}")
    rows = registry["packs"]
    index = {row["pack_id"]: row for row in rows}
    if len(index) != len(rows):
        raise ProbeError("registry contains duplicate pack IDs")
    published = {row["id"]: row for row in catalog["packs"] if row["id"] != "example-domain"}
    if set(index) != set(published):
        raise ProbeError(f"registry coverage differs from published catalog: {sorted(set(index) ^ set(published))}")
    probe_ids: set[str] = set()
    for pack_id, row in index.items():
        pack = published[pack_id]
        skills = {item["id"] for item in pack["skills"]}
        capabilities = set(pack["capabilities"])
        for probe in row["probes"]:
            if probe["id"] in probe_ids:
                raise ProbeError(f"duplicate probe ID: {probe['id']}")
            probe_ids.add(probe["id"])
            if probe["skill_id"] not in skills:
                raise ProbeError(f"{probe['id']}: unknown skill {probe['skill_id']}")
            if probe["capability"] not in capabilities:
                raise ProbeError(f"{probe['id']}: unknown capability {probe['capability']}")
    if len(index["evidence-lab-core"]["probes"]) < 3:
        raise ProbeError("core requires at least three distinct probes")
    return index


def parse_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ProbeError("installed roots must use pack-id=/absolute/path")
        pack_id, raw_path = value.split("=", 1)
        path = Path(raw_path).expanduser().resolve()
        if not path.is_absolute() or pack_id in roots:
            raise ProbeError("installed roots must be unique absolute paths")
        roots[pack_id] = path
    return roots


def selected_pack_ids(plan: dict) -> list[str]:
    try:
        rows = plan["selection_plan"]["packs"]
        result = [row["id"] for row in rows]
    except (KeyError, TypeError) as exc:
        raise ProbeError("installation plan has no selected packs") from exc
    if not result or len(result) != len(set(result)):
        raise ProbeError("installation plan has empty or duplicate pack selection")
    return result


def run_pack(pack_id: str, row: dict, root: Path, timeout: int) -> dict:
    pack_file = root / "pack.json"
    if not pack_file.is_file() or load(pack_file).get("id") != pack_id:
        return {"pack_id": pack_id, "pass": False, "failure": "PACK_IDENTITY_MISMATCH", "probes": []}
    results = []
    for probe in row["probes"]:
        missing = [relative for relative in probe["required_paths"] if not (root / relative).is_file()]
        if missing:
            results.append({"id": probe["id"], "pass": False, "failure": "REQUIRED_PATH_MISSING", "missing": missing})
            continue
        command = probe.get("command")
        if command:
            resolved = [sys.executable if value == "{python}" else str(root / value) if value.startswith("skills/") else value for value in command]
            try:
                completed = subprocess.run(resolved, cwd=root, capture_output=True, text=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired:
                results.append({"id": probe["id"], "pass": False, "failure": "PROBE_TIMEOUT"})
                continue
            if completed.returncode:
                results.append({"id": probe["id"], "pass": False, "failure": "PROBE_COMMAND_FAILED", "exit_code": completed.returncode})
                continue
        results.append({"id": probe["id"], "pass": True, "capability": probe["capability"]})
    return {"pack_id": pack_id, "pass": all(item["pass"] for item in results), "probes": results}


def run_plan(plan: dict, registry: dict, catalog: dict, roots: dict[str, Path], repository_root: Path | None = None) -> dict:
    index = index_registry(registry, catalog)
    selected = selected_pack_ids(plan)
    results = []
    for pack_id in selected:
        if pack_id not in roots and repository_root is not None:
            roots[pack_id] = repository_root / index[pack_id]["pack_path"]
        if pack_id not in roots:
            results.append({"pack_id": pack_id, "pass": False, "failure": "INSTALLED_ROOT_NOT_PROVIDED", "probes": []})
            continue
        results.append(run_pack(pack_id, index[pack_id], roots[pack_id], registry["timeout_seconds"]))
    return {
        "schema_version": 1,
        "status": "pass" if all(item["pass"] for item in results) else "fail",
        "selected_pack_ids": selected,
        "packs": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--installed-root", action="append", default=[])
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run_plan(
            load(args.plan), load(args.registry), load(args.catalog), parse_roots(args.installed_root),
            args.repository_root.resolve() if args.repository_root else None,
        )
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0 if result["status"] == "pass" else 1
    except (ProbeError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
