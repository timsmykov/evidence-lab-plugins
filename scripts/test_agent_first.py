#!/usr/bin/env python3
"""Acceptance checks for host-neutral packs, onboarding, and adapter parity."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "tests" / "fixtures" / "onboarding"
SELECTOR_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "skills" / "evidence-lab-onboarding" / "scripts" / "select_packs.py"
CATALOG_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "catalog" / "packs.json"
POLICY_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding" / "selection-policy.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(value, schema_name: str) -> None:
    errors = list(Draft202012Validator(load(SCHEMAS / schema_name)).iter_errors(value))
    if errors:
        raise AssertionError(f"{schema_name}: {errors[0].message}")


def load_selector():
    spec = importlib.util.spec_from_file_location("evidence_lab_selector", SELECTOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def check_fixtures() -> None:
    selector = load_selector()
    catalog = load(CATALOG_PATH)
    policy = load(POLICY_PATH)
    for profile_path in sorted(FIXTURES.glob("*.profile.json")):
        profile = load(profile_path)
        expected_path = profile_path.with_name(profile_path.name.replace(".profile.json", ".expected.json"))
        expected = load(expected_path)
        validate(profile, "profile.schema.json")
        plan = selector.select(profile, catalog, policy)
        validate(plan, "selection-plan.schema.json")
        actual_ids = [pack["id"] for pack in plan["packs"]]
        if actual_ids != expected["pack_ids"]:
            raise AssertionError(f"{profile_path.name}: expected {expected['pack_ids']}, got {actual_ids}")
        if "rule_ids" in expected:
            actual_rules = {pack["id"]: pack["rule_ids"] for pack in plan["packs"]}
            if actual_rules != expected["rule_ids"]:
                raise AssertionError(f"{profile_path.name}: expected rules {expected['rule_ids']}, got {actual_rules}")


def check_policy_boundaries() -> None:
    selector = load_selector()
    catalog = load(CATALOG_PATH)
    policy = load(POLICY_PATH)
    validate(policy, "selection-policy.schema.json")
    invalid = {
        "schema_version": 1,
        "domains": ["invented-discipline"],
        "workflows": [], "materials": [], "stages": [], "methods": [],
    }
    try:
        selector.select(invalid, catalog, policy)
    except ValueError as exc:
        if "unknown values" not in str(exc):
            raise
    else:
        raise AssertionError("unknown profile value was accepted")

    duplicated = dict(invalid, domains=["physics", "physics"])
    try:
        selector.select(duplicated, catalog, policy)
    except ValueError as exc:
        if "duplicate" not in str(exc):
            raise
    else:
        raise AssertionError("duplicate profile values were accepted")

    profile = {
        "schema_version": 1,
        "domains": [], "workflows": [], "materials": ["papers"],
        "stages": [], "methods": [],
    }
    all_rule = {
        "id": "all-test", "priority": 1, "reason": "Test all semantics.",
        "when": {"all": {"workflows": ["analyze-data"], "materials": ["papers"]}},
    }
    none_rule = {
        "id": "none-test", "priority": 1, "reason": "Test none semantics.",
        "when": {"any": {"materials": ["papers"]}, "none": {"stages": ["unknown"]}},
    }
    if selector.match_rule(profile, all_rule) is not None:
        raise AssertionError("all rule matched without every field")
    if selector.match_rule(profile, none_rule) is None:
        raise AssertionError("none rule rejected a profile without forbidden values")
    profile["stages"] = ["unknown"]
    if selector.match_rule(profile, none_rule) is not None:
        raise AssertionError("none rule accepted a forbidden value")

    cycle_catalog = json.loads(json.dumps(catalog))
    cycle_catalog["packs"][0]["dependencies"] = [cycle_catalog["packs"][1]["id"]]
    cycle_catalog["packs"][1]["dependencies"] = [cycle_catalog["packs"][0]["id"]]
    base = {
        "schema_version": 1,
        "domains": [], "workflows": ["full-research-cycle"],
        "materials": [], "stages": [], "methods": [],
    }
    try:
        selector.select(base, cycle_catalog, policy)
    except ValueError as exc:
        if "dependency cycle" not in str(exc):
            raise
    else:
        raise AssertionError("dependency cycle was accepted")

    conflict_catalog = json.loads(json.dumps(catalog))
    conflict_catalog["packs"][0]["conflicts"] = ["full-research-cycle"]
    try:
        selector.select(base, conflict_catalog, policy)
    except ValueError as exc:
        if "conflicts with" not in str(exc):
            raise
    else:
        raise AssertionError("selected pack conflict was accepted")

    first = selector.select(base, catalog, policy)
    second = selector.select(json.loads(json.dumps(base)), json.loads(json.dumps(catalog)), json.loads(json.dumps(policy)))
    if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
        raise AssertionError("selector output is not deterministic")

    bad_rule_catalog = json.loads(json.dumps(catalog))
    bad_rule_catalog["packs"][1]["selection"]["rules"][0]["id"] = "required-foundation"
    try:
        selector.select(base, bad_rule_catalog, policy)
    except ValueError as exc:
        if "duplicate selection rule ID" not in str(exc):
            raise
    else:
        raise AssertionError("reserved synthetic rule ID was accepted")


def check_adapter_parity() -> None:
    for pack_path in sorted((ROOT / "packs").glob("*/*/pack.json")):
        pack = load(pack_path)
        validate(pack, "pack.schema.json")
        directory = pack_path.parent
        claude = load(directory / ".claude-plugin" / "plugin.json")
        codex = load(directory / ".codex-plugin" / "plugin.json")
        validate(claude, "plugin.schema.json")
        validate(codex, "codex-plugin.schema.json")
        for field in ("name", "version", "description", "author", "keywords", "license"):
            if claude[field] != codex[field]:
                raise AssertionError(f"{pack['id']}: adapter drift in {field}")
        skills = {path.name for path in (directory / "skills").iterdir() if path.is_dir()}
        if not skills:
            raise AssertionError(f"{pack['id']}: no shared skills")


def check_onboarding_catalogs() -> None:
    root = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding"
    english = load(root / "questions.json")
    russian = load(root / "questions.ru.json")
    policy = load(POLICY_PATH)
    validate(english, "onboarding-questions.schema.json")
    validate(russian, "onboarding-questions.schema.json")
    for left, right in zip(english["questions"], russian["questions"], strict=True):
        if left["id"] != right["id"]:
            raise AssertionError("localized onboarding question IDs drifted")
        if [item["id"] for item in left["options"]] != [item["id"] for item in right["options"]]:
            raise AssertionError(f"localized onboarding option IDs drifted for {left['id']}")
        for option in left["options"]:
            field = option.get("profile_field", left["id"])
            if option["id"] not in policy["profile_fields"][field]["values"]:
                raise AssertionError(f"onboarding option {option['id']} is missing from policy field {field}")


def main() -> int:
    validate(load(ROOT / ".agents" / "plugins" / "marketplace.json"), "codex-marketplace.schema.json")
    check_onboarding_catalogs()
    check_policy_boundaries()
    check_fixtures()
    check_adapter_parity()
    print("OK: agent-first onboarding and Claude/Codex adapter parity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
