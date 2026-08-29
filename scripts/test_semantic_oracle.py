#!/usr/bin/env python3
"""Tests for the independent onboarding pack-selection oracle."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_semantic_oracle import (
    DEFAULT_ORACLE,
    ORACLE_SCHEMA,
    PACK_CATALOG,
    OracleError,
    evaluate_plan,
    load_validated_oracle,
    read_json,
    validate_oracle,
)


ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests/acceptance/onboarding-terra-10.scenarios.ru.json"


class SemanticOracleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index, self.catalog = load_validated_oracle()

    def test_oracle_covers_all_frozen_scenarios(self) -> None:
        bundle = read_json(SCENARIOS)
        self.assertEqual({row["id"] for row in bundle["scenarios"]}, set(self.index))
        self.assertEqual(10, len(self.index))

    def test_every_reference_plan_passes(self) -> None:
        for scenario_id, row in self.index.items():
            with self.subTest(scenario=scenario_id):
                result = evaluate_plan(
                    self.index,
                    self.catalog,
                    scenario_id=scenario_id,
                    selected_packs=row["packs"]["required"],
                )
                self.assertTrue(result["pass"], result)

    def test_allowed_pack_does_not_become_required(self) -> None:
        scenario_id = "ru-02-clinical-review"
        selected = [*self.index[scenario_id]["packs"]["required"], "life-sciences"]
        self.assertTrue(
            evaluate_plan(self.index, self.catalog, scenario_id=scenario_id, selected_packs=selected)["pass"]
        )

    def test_missing_required_pack_fails(self) -> None:
        scenario_id = "ru-02-clinical-review"
        selected = [
            pack_id
            for pack_id in self.index[scenario_id]["packs"]["required"]
            if pack_id != "systematic-review"
        ]
        result = evaluate_plan(self.index, self.catalog, scenario_id=scenario_id, selected_packs=selected)
        self.assertFalse(result["pass"])
        self.assertEqual(["systematic-review"], result["missing_required_packs"])
        self.assertIn("systematic-search", result["missing_required_capabilities"])

    def test_plausible_but_overinstalled_foundation_plan_fails(self) -> None:
        selected = [
            "evidence-lab-core",
            "document-evidence",
            "literature-publication",
            "qualitative-research",
            "quantitative-sciences",
            "research-design",
            "research-images",
            "structured-data-analysis",
            "systematic-review",
        ]
        result = evaluate_plan(
            self.index,
            self.catalog,
            scenario_id="en-h03-archaeology",
            selected_packs=selected,
        )
        self.assertFalse(result["pass"])
        self.assertEqual(
            ["quantitative-sciences", "research-design", "systematic-review"],
            result["forbidden_selected_packs"],
        )

    def test_unknown_pack_fails(self) -> None:
        scenario_id = "ru-h01-pure-mathematics"
        selected = [*self.index[scenario_id]["packs"]["required"], "invented-pack"]
        result = evaluate_plan(self.index, self.catalog, scenario_id=scenario_id, selected_packs=selected)
        self.assertFalse(result["pass"])
        self.assertEqual(["invented-pack"], result["unknown_selected_packs"])

    def test_overlapping_classification_is_rejected(self) -> None:
        oracle = copy.deepcopy(read_json(DEFAULT_ORACLE))
        row = oracle["scenarios"][0]
        row["packs"]["allowed"].append(row["packs"]["required"][0])
        with self.assertRaisesRegex(OracleError, "overlap"):
            validate_oracle(
                oracle,
                scenario_bundle=read_json(SCENARIOS),
                scenario_bundle_path=SCENARIOS,
                catalog=read_json(PACK_CATALOG),
            )

    def test_oracle_is_bound_to_frozen_bundle_hash(self) -> None:
        oracle = copy.deepcopy(read_json(DEFAULT_ORACLE))
        oracle["scenario_bundle"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(OracleError, "not bound"):
            validate_oracle(
                oracle,
                scenario_bundle=read_json(SCENARIOS),
                scenario_bundle_path=SCENARIOS,
                catalog=read_json(PACK_CATALOG),
            )

    def test_oracle_schema_is_well_formed(self) -> None:
        from jsonschema import Draft202012Validator

        Draft202012Validator.check_schema(json.loads(ORACLE_SCHEMA.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
