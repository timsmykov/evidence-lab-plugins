#!/usr/bin/env python3
"""Build a deterministic Evidence Lab pack plan from a normalized profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_CATALOG = PACK_ROOT / "catalog" / "packs.json"
FIELDS = ("domains", "workflows", "materials", "stages", "methods")


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def validate_profile(profile: dict) -> None:
    if profile.get("schema_version") != 1:
        raise ValueError("profile.schema_version must be 1")
    for field in FIELDS:
        value = profile.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"profile.{field} must be an array of strings")


def matches(profile: dict, pack: dict) -> list[str]:
    selection = pack["selection"]
    reasons: list[str] = []
    if selection.get("always"):
        reasons.append("required research foundation")
    for field in FIELDS:
        overlap = sorted(set(profile[field]) & set(selection.get(field, [])))
        if overlap:
            reasons.append(f"{field}: {', '.join(overlap)}")
    return reasons


def select(profile: dict, catalog: dict) -> dict:
    validate_profile(profile)
    packs = {pack["id"]: pack for pack in catalog.get("packs", [])}
    selected: dict[str, list[str]] = {}
    for pack in packs.values():
        reasons = matches(profile, pack)
        if reasons:
            selected[pack["id"]] = reasons

    pending = list(selected)
    while pending:
        pack_id = pending.pop()
        for dependency in packs[pack_id].get("dependencies", []):
            if dependency not in packs:
                raise ValueError(f"{pack_id}: unknown dependency {dependency}")
            if dependency not in selected:
                selected[dependency] = [f"required by {pack_id}"]
                pending.append(dependency)

    for pack_id in selected:
        conflicts = set(packs[pack_id].get("conflicts", [])) & set(selected)
        if conflicts:
            raise ValueError(f"{pack_id}: conflicts with {', '.join(sorted(conflicts))}")

    layer_order = {"core": 0, "workflow": 1, "domain": 2, "local": 3}
    plan_packs = []
    for pack_id in sorted(selected, key=lambda item: (layer_order[packs[item]["layer"]], item)):
        pack = packs[pack_id]
        plan_packs.append({
            "id": pack_id,
            "version": pack["version"],
            "layer": pack["layer"],
            "reason": "; ".join(selected[pack_id]),
        })
    return {"schema_version": 1, "profile": profile, "packs": plan_packs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    plan = select(load_object(args.profile), load_object(args.catalog))
    rendered = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
