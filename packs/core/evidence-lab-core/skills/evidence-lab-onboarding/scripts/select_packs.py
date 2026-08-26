#!/usr/bin/env python3
"""Build a deterministic Evidence Lab pack plan from a normalized profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_CATALOG = PACK_ROOT / "catalog" / "packs.json"
DEFAULT_POLICY = PACK_ROOT / "onboarding" / "selection-policy.json"
FIELDS = ("domains", "workflows", "materials", "stages", "methods")


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def validate_policy(policy: dict) -> None:
    if policy.get("schema_version") != 1:
        raise ValueError("selection_policy.schema_version must be 1")
    if set(policy.get("profile_fields", {})) != set(FIELDS):
        raise ValueError("selection_policy.profile_fields must declare every profile field")


def validate_profile(profile: dict, policy: dict) -> None:
    if profile.get("schema_version") != 1:
        raise ValueError("profile.schema_version must be 1")
    for field in FIELDS:
        value = profile.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"profile.{field} must be an array of strings")
        if len(value) != len(set(value)):
            raise ValueError(f"profile.{field} must not contain duplicate values")
        allowed = set(policy["profile_fields"][field]["values"])
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"profile.{field} contains unknown values: {', '.join(unknown)}")


def validate_catalog(catalog: dict, policy: dict) -> None:
    packs = catalog.get("packs")
    if not isinstance(packs, list) or not packs:
        raise ValueError("catalog.packs must be a non-empty array")
    pack_ids = [pack.get("id") for pack in packs]
    if len(pack_ids) != len(set(pack_ids)):
        raise ValueError("catalog contains duplicate pack IDs")
    known_packs = set(pack_ids)
    rule_ids: set[str] = {"required-foundation"}
    for pack in packs:
        for related in (*pack.get("dependencies", []), *pack.get("conflicts", [])):
            if related not in known_packs:
                raise ValueError(f"{pack['id']}: unknown related pack {related}")
        for rule in pack["selection"].get("rules", []):
            if rule["id"].startswith("dependency-"):
                raise ValueError(f"reserved selection rule ID: {rule['id']}")
            if rule["id"] in rule_ids:
                raise ValueError(f"duplicate selection rule ID: {rule['id']}")
            rule_ids.add(rule["id"])
            for conditions in rule["when"].values():
                for field, values in conditions.items():
                    allowed = set(policy["profile_fields"][field]["values"])
                    unknown = sorted(set(values) - allowed)
                    if unknown:
                        raise ValueError(f"{rule['id']}: unknown {field} values: {', '.join(unknown)}")


def overlap(profile: dict, conditions: dict) -> dict[str, list[str]]:
    return {
        field: sorted(set(profile[field]) & set(values))
        for field, values in conditions.items()
    }


def match_rule(profile: dict, rule: dict) -> dict | None:
    when = rule["when"]
    evidence: dict[str, set[str]] = {}
    if "any" in when:
        matches = overlap(profile, when["any"])
        if not any(matches.values()):
            return None
        for field, values in matches.items():
            evidence.setdefault(field, set()).update(values)
    if "all" in when:
        matches = overlap(profile, when["all"])
        if not all(matches.values()):
            return None
        for field, values in matches.items():
            evidence.setdefault(field, set()).update(values)
    if "contains_all" in when:
        for field, values in when["contains_all"].items():
            if not set(values) <= set(profile[field]):
                return None
            evidence.setdefault(field, set()).update(values)
    if "none" in when and any(overlap(profile, when["none"]).values()):
        return None
    rendered_evidence = {field: sorted(values) for field, values in sorted(evidence.items())}
    return {"id": rule["id"], "priority": rule["priority"], "reason": rule["reason"], "evidence": rendered_evidence}


def matches(profile: dict, pack: dict) -> list[dict]:
    selection = pack["selection"]
    matched: list[dict] = []
    if selection.get("always"):
        matched.append({"id": "required-foundation", "priority": 1000, "reason": "Required research foundation.", "evidence": {}})
    for rule in selection.get("rules", []):
        result = match_rule(profile, rule)
        if result:
            matched.append(result)
    return sorted(matched, key=lambda item: (-item["priority"], item["id"]))


def ordered_pack_ids(selected: set[str], packs: dict[str, dict], policy: dict) -> list[str]:
    layer_order = {layer: index for index, layer in enumerate(policy["ordering"]["layers"])}
    remaining = set(selected)
    ordered: list[str] = []
    while remaining:
        ready = [
            pack_id for pack_id in remaining
            if not (set(packs[pack_id].get("dependencies", [])) & remaining)
        ]
        if not ready:
            raise ValueError(f"dependency cycle among selected packs: {', '.join(sorted(remaining))}")
        ready.sort(key=lambda item: (layer_order[packs[item]["layer"]], item))
        for pack_id in ready:
            ordered.append(pack_id)
            remaining.remove(pack_id)
    return ordered


def select(profile: dict, catalog: dict, policy: dict | None = None) -> dict:
    policy = policy or load_object(DEFAULT_POLICY)
    validate_policy(policy)
    validate_profile(profile, policy)
    validate_catalog(catalog, policy)
    packs = {pack["id"]: pack for pack in catalog.get("packs", [])}
    selected: dict[str, list[dict]] = {}
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
                selected[dependency] = [{
                    "id": f"dependency-{pack_id}",
                    "priority": 1000,
                    "reason": f"Required by {pack_id}.",
                    "evidence": {},
                }]
                pending.append(dependency)

    for pack_id in selected:
        conflicts = set(packs[pack_id].get("conflicts", [])) & set(selected)
        if conflicts:
            raise ValueError(f"{pack_id}: conflicts with {', '.join(sorted(conflicts))}")

    plan_packs = []
    for pack_id in ordered_pack_ids(set(selected), packs, policy):
        pack = packs[pack_id]
        matched_rules = selected[pack_id]
        plan_packs.append({
            "id": pack_id,
            "version": pack["version"],
            "layer": pack["layer"],
            "reason": "; ".join(item["reason"] for item in matched_rules),
            "rule_ids": [item["id"] for item in matched_rules],
            "matched_rules": [
                {"id": item["id"], "reason": item["reason"], "evidence": item["evidence"]}
                for item in matched_rules
            ],
        })
    return {"schema_version": 2, "policy_version": policy["schema_version"], "profile": profile, "packs": plan_packs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    plan = select(load_object(args.profile), load_object(args.catalog), load_object(args.policy))
    rendered = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
