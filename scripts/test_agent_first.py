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
FOUNDATION_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "catalog" / "foundation-core.json"
POLICY_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding" / "selection-policy.json"
PLAN_COPY_ROOT = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding"
RENDERER_PATH = ROOT / "scripts" / "render_plan.py"
LANGUAGE_SELECTOR_PATH = ROOT / "packs/core/evidence-lab-core/skills/evidence-lab-onboarding/scripts/select_language.py"


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


def load_renderer():
    spec = importlib.util.spec_from_file_location("evidence_lab_plan_renderer", RENDERER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_language_selector():
    spec = importlib.util.spec_from_file_location("evidence_lab_language_selector", LANGUAGE_SELECTOR_PATH)
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


def check_frozen_foundation() -> None:
    selector = load_selector()
    catalog = load(CATALOG_PATH)
    foundation = load(FOUNDATION_PATH)
    policy = load(POLICY_PATH)
    validate(catalog, "pack-catalog.schema.json")
    validate(foundation, "foundation-core.schema.json")
    if foundation["physical_skill_count"] != 20:
        raise AssertionError("frozen foundation must index exactly 20 current physical skills")
    if len(foundation["planned_capabilities"]) != 6:
        raise AssertionError("frozen foundation must retain exactly six planned capabilities")
    declared_packs = [pack["id"] for pack in catalog["packs"] if pack["foundation"]]
    if set(declared_packs) != set(foundation["foundation_pack_ids"]):
        raise AssertionError("runtime catalog foundation packs differ from the frozen skill index")
    indexed = {
        item["id"]: (item["pack_id"], item["quality_status"])
        for item in foundation["skills"]
    }
    catalog_skills = {
        item["id"]: (pack["id"], item["quality_status"])
        for pack in catalog["packs"] if pack["foundation"]
        for item in pack["skills"]
    }
    if any(catalog_skills.get(skill_id) != owner for skill_id, owner in indexed.items()):
        raise AssertionError("runtime pack catalog does not account for every frozen foundation skill")
    profile = load(FIXTURES / "default.profile.json")
    plan = selector.select(profile, catalog, policy)
    installed = {item["id"] for item in plan["packs"]}
    if not set(foundation["foundation_pack_ids"]) <= installed:
        raise AssertionError("default bootstrap plan omits a frozen foundation pack")
    for item in plan["packs"]:
        if item["id"] in foundation["foundation_pack_ids"] and "required-foundation" not in item["rule_ids"]:
            raise AssertionError(f"{item['id']}: foundation installation reason is missing")


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

    contains_all_rule = {
        "id": "contains-all-test", "priority": 1, "reason": "Test exact material-set semantics.",
        "when": {"contains_all": {"materials": ["pdf", "datasets"]}},
    }
    profile["materials"] = ["pdf"]
    if selector.match_rule(profile, contains_all_rule) is not None:
        raise AssertionError("contains_all rule matched a partial value set")
    profile["materials"] = ["pdf", "datasets"]
    if selector.match_rule(profile, contains_all_rule) is None:
        raise AssertionError("contains_all rule rejected a complete value set")

    cycle_catalog = json.loads(json.dumps(catalog))
    cycle_catalog["packs"][0]["dependencies"] = [cycle_catalog["packs"][1]["id"]]
    cycle_catalog["packs"][1]["dependencies"] = [cycle_catalog["packs"][0]["id"]]
    base = {
        "schema_version": 1,
        "domains": [], "workflows": ["full-research-cycle"],
        "materials": [], "stages": [], "methods": [],
    }
    dependency_catalog = json.loads(json.dumps(catalog))
    synthetic_dependency = json.loads(json.dumps(dependency_catalog["packs"][1]))
    synthetic_dependency.update({
        "id": "synthetic-dependency", "selection": {"always": False, "rules": []},
        "dependencies": ["evidence-lab-core"], "conflicts": [],
    })
    dependency_catalog["packs"].append(synthetic_dependency)
    full_cycle = next(pack for pack in dependency_catalog["packs"] if pack["id"] == "full-research-cycle")
    full_cycle["dependencies"].append("synthetic-dependency")
    dependency_plan = selector.select(base, dependency_catalog, policy)
    dependency_result = next(pack for pack in dependency_plan["packs"] if pack["id"] == "synthetic-dependency")
    if dependency_result["rule_ids"] != ["dependency-full-research-cycle"]:
        raise AssertionError("dependency-only selection did not preserve its synthetic reason")

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
    language_english = load(root / "language.json")
    language_russian = load(root / "language.ru.json")
    validate(language_english, "onboarding-language.schema.json")
    validate(language_russian, "onboarding-language.schema.json")
    if [item["id"] for item in language_english["options"]] != ["en", "ru"]:
        raise AssertionError("English language choice must offer en then ru")
    if [item["id"] for item in language_russian["options"]] != ["en", "ru"]:
        raise AssertionError("localized language choice IDs drifted")
    selector = load_language_selector()
    catalogs = (language_english, language_russian)
    expected_answers = {
        "1": "en", "English": "en", "EN": "en", "\u0410\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439": "en",
        "2": "ru", "Russian": "ru", "RU": "ru", "\u0420\u0443\u0441\u0441\u043a\u0438\u0439": "ru",
    }
    for answer, expected in expected_answers.items():
        actual = selector.select_language(answer, catalogs)
        if actual != expected:
            raise AssertionError(f"language answer {answer!r}: expected {expected}, got {actual}")
    try:
        selector.select_language("Deutsch", catalogs)
    except ValueError as exc:
        if "unsupported" not in str(exc):
            raise
    else:
        raise AssertionError("language selector accepted an unsupported locale")
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


def check_plan_copy() -> None:
    catalog = load(CATALOG_PATH)
    english = load(PLAN_COPY_ROOT / "plan-copy.json")
    russian = load(PLAN_COPY_ROOT / "plan-copy.ru.json")
    validate(english, "onboarding-plan-copy.schema.json")
    validate(russian, "onboarding-plan-copy.schema.json")

    expected_packs = {pack["id"] for pack in catalog["packs"]}
    expected_rules = {"required-foundation"}
    for pack in catalog["packs"]:
        expected_rules.update(rule["id"] for rule in pack["selection"]["rules"])

    for label, copy in (("English", english), ("Russian", russian)):
        copy_packs = [item["id"] for item in copy["packs"]]
        copy_rules = [item["id"] for item in copy["rules"]]
        if len(copy_packs) != len(set(copy_packs)) or set(copy_packs) != expected_packs:
            raise AssertionError(f"{label} plan copy does not exactly cover the published pack catalog")
        if len(copy_rules) != len(set(copy_rules)) or set(copy_rules) != expected_rules:
            raise AssertionError(f"{label} plan copy does not exactly cover the selection rules")
    if [item["id"] for item in english["packs"]] != [item["id"] for item in russian["packs"]]:
        raise AssertionError("localized plan-copy pack IDs drifted")
    if [item["id"] for item in english["rules"]] != [item["id"] for item in russian["rules"]]:
        raise AssertionError("localized plan-copy rule IDs drifted")

    selector = load_selector()
    profile = load(FIXTURES / "quantitative-full-cycle.profile.json")
    selection_plan = selector.select(profile, catalog, load(POLICY_PATH))
    installation_plan = {
        "schema_version": 1,
        "host": "codex",
        "release": {"tag": "release-2099.01.1"},
        "selection_plan": selection_plan,
    }
    renderer = load_renderer()
    for copy in (english, russian):
        rendered = renderer.render(installation_plan, copy)
        if f"# {copy['heading']}" not in rendered or copy["confirmation"] not in rendered:
            raise AssertionError("localized plan renderer omitted required user-facing copy")
        if "release-2099.01.1" not in rendered or "evidence-lab-core" in rendered:
            raise AssertionError("plan renderer leaked an internal pack ID or omitted the locked release")
        for selected in selection_plan["packs"]:
            title = next(item["title"] for item in copy["packs"] if item["id"] == selected["id"])
            if title not in rendered:
                raise AssertionError(f"plan renderer omitted selected capability {selected['id']}")

    broken = json.loads(json.dumps(installation_plan))
    broken["selection_plan"]["packs"][0]["rule_ids"] = ["unreviewed-rule"]
    try:
        renderer.render(broken, english)
    except renderer.RenderError:
        pass
    else:
        raise AssertionError("plan renderer accepted an unreviewed selection-rule ID")


def main() -> int:
    validate(load(ROOT / ".agents" / "plugins" / "marketplace.json"), "codex-marketplace.schema.json")
    check_onboarding_catalogs()
    check_plan_copy()
    check_policy_boundaries()
    check_fixtures()
    check_frozen_foundation()
    check_adapter_parity()
    print("OK: agent-first onboarding and Claude/Codex adapter parity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
