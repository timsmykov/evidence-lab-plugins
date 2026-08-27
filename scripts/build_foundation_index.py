#!/usr/bin/env python3
"""Build the immutable inventory used by bootstrap to account for foundation skills."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FOUNDATION = ROOT / "catalog" / "foundation-skills.json"
OUTPUT = ROOT / "catalog" / "foundation-core.json"
PACKS = ROOT / "packs"
POLICY = PACKS / "core" / "evidence-lab-core" / "onboarding" / "selection-policy.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if not files:
        raise ValueError(f"{root}: foundation skill has no files")
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def build() -> dict:
    foundation = load(FOUNDATION)
    layer_order = {
        layer: index
        for index, layer in enumerate(load(POLICY)["ordering"]["layers"])
    }
    owners: dict[str, dict] = {}
    for meta_path in sorted(PACKS.glob("*/*/meta.json")):
        pack_dir = meta_path.parent
        pack = load(pack_dir / "pack.json")
        meta = load(meta_path)
        for item in meta.get("skills", []):
            name = item["name"]
            if name in owners:
                raise ValueError(f"foundation skill has multiple owning packs: {name}")
            owners[name] = {"pack": pack, "meta": item, "directory": pack_dir}

    capabilities_by_skill: dict[str, list[str]] = {}
    planned = []
    for capability in foundation["skills"]:
        current = capability.get("current_skill")
        if current:
            capabilities_by_skill.setdefault(current, []).append(capability["id"])
        else:
            planned.append({
                key: capability[key]
                for key in ("id", "priority", "rationale", "upstream_candidate_ids")
                if key in capability
            })

    rows = []
    for name, capability_ids in capabilities_by_skill.items():
        owner = owners.get(name)
        if owner is None:
            raise ValueError(f"foundation skill has no owning pack: {name}")
        status = owner["meta"]["quality_status"]
        if status in {"support-only", "reference-only"}:
            raise ValueError(f"foundation skill cannot have {status} quality: {name}")
        directory = owner["directory"] / "skills" / name
        if not (directory / "SKILL.md").is_file():
            raise ValueError(f"foundation skill is missing SKILL.md: {name}")
        pack = owner["pack"]
        rows.append({
            "id": name,
            "pack_id": pack["id"],
            "pack_version": pack["version"],
            "layer": pack["layer"],
            "path": directory.relative_to(ROOT).as_posix(),
            "quality_status": status,
            "capabilities": sorted(capability_ids),
            "content_sha256": tree_digest(directory),
        })

    rows.sort(key=lambda item: (layer_order[item["layer"]], item["pack_id"], item["id"]))
    pack_ids = []
    for row in rows:
        if row["pack_id"] not in pack_ids:
            pack_ids.append(row["pack_id"])
    planned.sort(key=lambda item: (item["priority"], item["id"]))
    return {
        "schema_version": 1,
        "generated_from": [
            "catalog/foundation-skills.json",
            "packs/*/*/pack.json",
            "packs/*/*/meta.json",
            "packs/*/*/skills/*",
        ],
        "capability_count": sum(len(item["capabilities"]) for item in rows),
        "physical_skill_count": len(rows),
        "foundation_pack_ids": pack_ids,
        "skills": rows,
        "planned_capabilities": planned,
    }


def render(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    content = render(build())
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != content:
            print(f"FAIL: generated foundation index is stale: {args.output.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"verified {args.output.relative_to(ROOT)}")
        return 0
    args.output.write_text(content, encoding="utf-8")
    print(f"wrote {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
