#!/usr/bin/env python3
"""Behavior tests for the reviewed external-plugin selection boundary."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from select_external_plugins import select


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "catalog" / "external-plugin-candidates.json").read_text(encoding="utf-8"))
PLAN_SCHEMA = json.loads((ROOT / "schemas" / "external-plugin-plan.schema.json").read_text(encoding="utf-8"))


class ExternalPluginSelectionTests(unittest.TestCase):
    def assert_valid_plan(self, plan):
        self.assertEqual(list(Draft202012Validator(PLAN_SCHEMA).iter_errors(plan)), [])

    def test_quantitative_profile_offers_wolfram_but_never_silent_install(self):
        profile = json.loads((ROOT / "tests" / "fixtures" / "onboarding" / "physics-models.profile.json").read_text(encoding="utf-8"))
        plan = select(profile, REGISTRY)
        self.assert_valid_plan(plan)
        wolfram = next(action for action in plan["actions"] if action["display_name"] == "Wolfram")
        self.assertEqual(wolfram["action"], "offer-connection")
        self.assertNotIn("install-after-confirmation", [action["action"] for action in plan["actions"]])

    def test_life_science_profile_separates_skill_candidate_and_app_connection(self):
        profile = {
            "schema_version": 1,
            "domains": ["life-sciences"],
            "workflows": ["analyze-data"],
            "materials": ["papers", "images"],
            "stages": ["active-research"],
            "methods": [],
        }
        actions = {
            action["display_name"]: action["action"]
            for action in select(profile, REGISTRY, requested_plugins=("Life Sciences NGS Analysis",))["actions"]
        }
        self.assertEqual(actions["Life Science Research"], "recommend-after-validation")
        self.assertEqual(actions["Life Sciences NGS Analysis"], "offer-opt-in")
        self.assertEqual(actions["BioRender"], "offer-connection")

    def test_explicit_opt_in_is_not_shown_without_a_request(self):
        profile = json.loads((ROOT / "tests" / "fixtures" / "onboarding" / "physics-models.profile.json").read_text(encoding="utf-8"))
        names = [action["display_name"] for action in select(profile, REGISTRY)["actions"]]
        self.assertNotIn("Zotero", names)
        requested = select(profile, REGISTRY, requested_plugins=("Zotero",))
        zotero = next(action for action in requested["actions"] if action["display_name"] == "Zotero")
        self.assertEqual(zotero["action"], "offer-opt-in")

    def test_claude_never_receives_codex_directory_plugins(self):
        profile = {field: ["life-sciences"] if field == "domains" else [] for field in ("domains", "workflows", "materials", "stages", "methods")}
        plan = select(profile, REGISTRY, host="claude-code")
        self.assert_valid_plan(plan)
        self.assertEqual(plan["actions"], [])
        self.assertIn("not portable", plan["reason"])

    def test_multi_field_rule_requires_each_declared_signal(self):
        profile = {
            "schema_version": 1,
            "domains": ["mathematics"],
            "workflows": [],
            "materials": ["papers"],
            "stages": ["active-research"],
            "methods": [],
        }
        names = [action["display_name"] for action in select(profile, REGISTRY)["actions"]]
        self.assertNotIn("Wolfram", names)


if __name__ == "__main__":
    unittest.main()
