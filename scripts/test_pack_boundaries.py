#!/usr/bin/env python3
"""Acceptance tests for scenario coverage and R3 pack-boundary evidence."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(value, schema_name: str) -> None:
    errors = sorted(Draft202012Validator(load(SCHEMAS / schema_name)).iter_errors(value), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.path) or "<root>"
        raise AssertionError(f"{schema_name}:{location}: {error.message}")


def load_analyzer():
    path = ROOT / "scripts" / "analyze_pack_boundaries.py"
    spec = importlib.util.spec_from_file_location("pack_boundary_analyzer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    analyzer = load_analyzer()
    matrix = load(ROOT / "catalog" / "scenarios.json")
    decisions = load(ROOT / "catalog" / "pack-boundary-decisions.json")
    catalog = load(ROOT / "packs" / "core" / "evidence-lab-core" / "catalog" / "packs.json")
    policy = load(ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding" / "selection-policy.json")
    validate(matrix, "scenario-matrix.schema.json")
    validate(decisions, "pack-boundary-decisions.schema.json")
    for scenario in matrix["scenarios"]:
        validate(scenario["profile"], "profile.schema.json")
    report = analyzer.analyze(matrix, catalog, policy)
    expected = {scenario["id"]: scenario for scenario in matrix["scenarios"]}
    for row in report["scenarios"]:
        scenario = expected[row["id"]]
        if row["selected_packs"] != scenario["expected_selected_packs"]:
            raise AssertionError(f"{row['id']}: selected-pack drift: {row['selected_packs']}")
        if row["missing_capabilities"] != scenario["expected_missing_capabilities"]:
            raise AssertionError(f"{row['id']}: missing-capability drift: {row['missing_capabilities']}")

    pack_ids = {pack["id"] for pack in catalog["packs"]}
    decision_ids = {decision["pack_id"] for decision in decisions["current_pack_decisions"]}
    addition_ids = {addition["pack_id"] for addition in decisions["prioritized_additions"]}
    covered_ids = decision_ids | addition_ids
    if covered_ids != pack_ids:
        raise AssertionError(f"pack decisions do not cover current catalog: {covered_ids} != {pack_ids}")
    scenario_ids = set(expected)
    for decision in decisions["current_pack_decisions"]:
        if not set(decision["scenario_evidence"]) <= scenario_ids:
            raise AssertionError(f"{decision['pack_id']}: unknown scenario evidence")
    for addition in decisions["prioritized_additions"]:
        if not set(addition["trigger_scenarios"]) <= scenario_ids:
            raise AssertionError(f"{addition['pack_id']}: unknown trigger scenario")
        if addition["lifecycle_status"] == "planned":
            missing = set().union(*(set(expected[item]["expected_missing_capabilities"]) for item in addition["trigger_scenarios"]))
            if not set(addition["capabilities"]) <= missing:
                raise AssertionError(f"{addition['pack_id']}: proposed capability is not missing in its evidence scenarios")
        else:
            implemented = next((pack for pack in catalog["packs"] if pack["id"] == addition["pack_id"]), None)
            if implemented is None or not set(addition["capabilities"]) <= set(implemented["capabilities"]):
                raise AssertionError(f"{addition['pack_id']}: implemented pack does not provide its target capabilities")

    baseline = matrix["baseline_pack"]
    for pack_id, usage in report["pack_usage"].items():
        if not usage["selected_by"]:
            raise AssertionError(f"{pack_id}: no positive scenario")
        if pack_id != baseline and not usage["excluded_by"]:
            raise AssertionError(f"{pack_id}: no negative scenario")
    rendered = analyzer.render(report, decisions)
    report_path = ROOT / "docs" / "pack-boundary-report.md"
    if not report_path.exists() or report_path.read_text(encoding="utf-8") != rendered:
        raise AssertionError("docs/pack-boundary-report.md is stale; run analyze_pack_boundaries.py")
    print(f"PASS: {report['scenario_count']} scenarios, {len(pack_ids)} catalog packs, {len(decisions['prioritized_additions'])} R3 additions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
