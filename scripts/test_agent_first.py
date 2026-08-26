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
    for profile_path in sorted(FIXTURES.glob("*.profile.json")):
        profile = load(profile_path)
        expected_path = profile_path.with_name(profile_path.name.replace(".profile.json", ".expected.json"))
        expected = load(expected_path)
        validate(profile, "profile.schema.json")
        plan = selector.select(profile, catalog)
        validate(plan, "selection-plan.schema.json")
        actual_ids = [pack["id"] for pack in plan["packs"]]
        if actual_ids != expected["pack_ids"]:
            raise AssertionError(f"{profile_path.name}: expected {expected['pack_ids']}, got {actual_ids}")


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
    validate(english, "onboarding-questions.schema.json")
    validate(russian, "onboarding-questions.schema.json")
    for left, right in zip(english["questions"], russian["questions"], strict=True):
        if left["id"] != right["id"]:
            raise AssertionError("localized onboarding question IDs drifted")
        if [item["id"] for item in left["options"]] != [item["id"] for item in right["options"]]:
            raise AssertionError(f"localized onboarding option IDs drifted for {left['id']}")


def main() -> int:
    validate(load(ROOT / ".agents" / "plugins" / "marketplace.json"), "codex-marketplace.schema.json")
    check_onboarding_catalogs()
    check_fixtures()
    check_adapter_parity()
    print("OK: agent-first onboarding and Claude/Codex adapter parity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
