#!/usr/bin/env python3
"""Validate and evaluate the frozen onboarding semantic oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORACLE = ROOT / "catalog/onboarding-semantic-oracle.json"
PACK_CATALOG = ROOT / "packs/core/evidence-lab-core/catalog/packs.json"
ORACLE_SCHEMA = ROOT / "schemas/onboarding-semantic-oracle.schema.json"


class OracleError(RuntimeError):
    """Raised when the oracle is inconsistent or a plan violates it."""


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OracleError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OracleError(f"{path} must contain a JSON object")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classification_sets(value: Mapping[str, object], *, label: str) -> dict[str, set[str]]:
    groups = {name: set(value.get(name, [])) for name in ("required", "allowed", "forbidden")}
    for left, right in (("required", "allowed"), ("required", "forbidden"), ("allowed", "forbidden")):
        overlap = groups[left] & groups[right]
        if overlap:
            raise OracleError(f"{label}: {left}/{right} overlap: {sorted(overlap)}")
    return groups


def pack_index(catalog: Mapping[str, object]) -> dict[str, set[str]]:
    packs = catalog.get("packs")
    if not isinstance(packs, list):
        raise OracleError("pack catalog has no packs array")
    result: dict[str, set[str]] = {}
    for raw in packs:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            raise OracleError("pack catalog contains an invalid pack")
        if raw.get("distribution_bundle", False):
            continue
        capabilities = raw.get("capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
            raise OracleError(f"pack {raw['id']} has invalid capabilities")
        result[raw["id"]] = set(capabilities)
    return result


def validate_oracle(
    oracle: Mapping[str, object],
    *,
    scenario_bundle: Mapping[str, object],
    scenario_bundle_path: Path,
    catalog: Mapping[str, object],
) -> dict[str, dict]:
    schema = read_json(ORACLE_SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(oracle), key=lambda item: list(item.path))
    if errors:
        raise OracleError(f"oracle schema: {errors[0].message}")
    binding = oracle["scenario_bundle"]
    if binding["sha256"] != file_sha256(scenario_bundle_path):
        raise OracleError("oracle is not bound to the current frozen scenario bundle")
    raw_scenarios = scenario_bundle.get("scenarios")
    if not isinstance(raw_scenarios, list):
        raise OracleError("scenario bundle has no scenarios array")
    expected_ids = [item.get("id") for item in raw_scenarios if isinstance(item, dict)]
    rows = oracle["scenarios"]
    oracle_ids = [item["id"] for item in rows]
    if len(set(oracle_ids)) != len(oracle_ids):
        raise OracleError("oracle scenario ids must be unique")
    if set(oracle_ids) != set(expected_ids):
        raise OracleError("oracle scenario ids do not exactly cover the frozen bundle")

    packs = pack_index(catalog)
    pack_universe = set(packs)
    capability_universe = set().union(*packs.values())
    indexed: dict[str, dict] = {}
    for row in rows:
        scenario_id = row["id"]
        pack_groups = classification_sets(row["packs"], label=f"{scenario_id}.packs")
        capability_groups = classification_sets(row["capabilities"], label=f"{scenario_id}.capabilities")
        if set().union(*pack_groups.values()) != pack_universe:
            raise OracleError(f"{scenario_id}: pack classification must cover the catalog exactly")
        if set().union(*capability_groups.values()) != capability_universe:
            raise OracleError(f"{scenario_id}: capability classification must cover the catalog exactly")
        required_pack_capabilities = set().union(*(packs[pack_id] for pack_id in pack_groups["required"]))
        permitted_pack_capabilities = set().union(
            *(packs[pack_id] for pack_id in pack_groups["required"] | pack_groups["allowed"])
        )
        forbidden_capabilities = set().union(*(packs[pack_id] for pack_id in pack_groups["forbidden"]))
        if not capability_groups["required"].issubset(required_pack_capabilities):
            raise OracleError(f"{scenario_id}: a required capability has no required pack")
        if capability_groups["required"] | capability_groups["allowed"] != permitted_pack_capabilities:
            raise OracleError(f"{scenario_id}: required and allowed capabilities drift from permitted packs")
        if capability_groups["forbidden"] != forbidden_capabilities:
            raise OracleError(f"{scenario_id}: forbidden capabilities drift from forbidden packs")
        indexed[scenario_id] = row
    return indexed


def evaluate_plan(
    oracle_index: Mapping[str, Mapping[str, object]],
    catalog: Mapping[str, object],
    *,
    scenario_id: str,
    selected_packs: Sequence[str],
) -> dict:
    if scenario_id not in oracle_index:
        raise OracleError(f"unknown scenario: {scenario_id}")
    packs = pack_index(catalog)
    selected = set(selected_packs)
    unknown = selected - set(packs)
    row = oracle_index[scenario_id]
    groups = classification_sets(row["packs"], label=f"{scenario_id}.packs")
    selected_capabilities = set().union(*(packs[pack_id] for pack_id in selected - unknown)) if selected - unknown else set()
    capability_groups = classification_sets(row["capabilities"], label=f"{scenario_id}.capabilities")
    result = {
        "scenario_id": scenario_id,
        "pass": False,
        "missing_required_packs": sorted(groups["required"] - selected),
        "forbidden_selected_packs": sorted(groups["forbidden"] & selected),
        "unknown_selected_packs": sorted(unknown),
        "missing_required_capabilities": sorted(capability_groups["required"] - selected_capabilities),
        "forbidden_selected_capabilities": sorted(capability_groups["forbidden"] & selected_capabilities),
    }
    result["pass"] = not any(result[key] for key in result if key not in {"scenario_id", "pass"})
    return result


def load_validated_oracle(path: Path = DEFAULT_ORACLE) -> tuple[dict[str, dict], dict]:
    oracle = read_json(path)
    relative_bundle = Path(oracle.get("scenario_bundle", {}).get("path", ""))
    bundle_path = (ROOT / relative_bundle).resolve()
    if ROOT.resolve() not in bundle_path.parents:
        raise OracleError("scenario bundle path leaves the repository")
    catalog = read_json(PACK_CATALOG)
    index = validate_oracle(
        oracle,
        scenario_bundle=read_json(bundle_path),
        scenario_bundle_path=bundle_path,
        catalog=catalog,
    )
    return index, catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--scenario-id")
    parser.add_argument("--selected-pack", action="append", default=[])
    args = parser.parse_args()
    try:
        index, catalog = load_validated_oracle(args.oracle)
        if args.scenario_id:
            result = evaluate_plan(index, catalog, scenario_id=args.scenario_id, selected_packs=args.selected_pack)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 0 if result["pass"] else 1
        print(json.dumps({"valid": True, "scenario_count": len(index)}, sort_keys=True))
        return 0
    except OracleError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
