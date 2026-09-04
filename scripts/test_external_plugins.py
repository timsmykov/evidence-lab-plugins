#!/usr/bin/env python3
"""Behavior tests for audited companion-plugin inventory, selection, and apply."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jsonschema import Draft202012Validator

from inventory_host import collect_inventory
from manage_companion_plugins import apply_plan, verify_plan
from select_external_plugins import select


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "catalog" / "external-plugin-candidates.json").read_text(encoding="utf-8"))
PLAN_SCHEMA = json.loads((ROOT / "schemas" / "external-plugin-plan.schema.json").read_text(encoding="utf-8"))
EMPTY_INVENTORY = {"schema_version": 1, "host": "codex", "plugins": [], "skills": [], "local_apps": [], "digest": "0" * 64}


class ExternalPluginSelectionTests(unittest.TestCase):
    def assert_valid_plan(self, plan):
        errors = list(Draft202012Validator(PLAN_SCHEMA).iter_errors(plan))
        self.assertEqual(errors, [], errors[0].message if errors else "")

    def test_baseline_runtimes_are_installed_only_when_missing(self):
        profile = {field: [] for field in ("domains", "workflows", "materials", "stages", "methods")}
        missing = select(profile, REGISTRY, inventory=EMPTY_INVENTORY)
        self.assert_valid_plan(missing)
        baseline = {row["display_name"]: row["action"] for row in missing["actions"]}
        self.assertEqual(baseline["PDF"], "install-after-confirmation")
        inventory = {**EMPTY_INVENTORY, "plugins": [{"plugin_id": "pdf@openai-primary-runtime", "name": "pdf", "selector": "pdf@openai-primary-runtime", "version": "26.709.11516"}]}
        retained = select(profile, REGISTRY, inventory=inventory)
        pdf = next(row for row in retained["actions"] if row["display_name"] == "PDF")
        self.assertEqual(pdf["action"], "retain-installed")

    def test_disabled_plugin_is_activated_not_reinstalled(self):
        profile = {field: [] for field in ("domains", "workflows", "materials", "stages", "methods")}
        inventory = {
            **EMPTY_INVENTORY,
            "plugins": [{
                "plugin_id": "pdf@openai-primary-runtime", "name": "pdf",
                "selector": "pdf@openai-primary-runtime", "version": "1", "enabled": False,
            }],
        }
        plan = select(profile, REGISTRY, inventory=inventory)
        pdf = next(row for row in plan["actions"] if row["display_name"] == "PDF")
        self.assertEqual(pdf["action"], "activate-after-confirmation")
        self.assertEqual(verify_plan(plan, inventory)["status"], "awaiting-activation")

    def test_publication_profile_requires_latex_activation(self):
        profile = {"domains": [], "workflows": ["prepare-publication"], "materials": ["papers"], "stages": ["writing"], "methods": []}
        actions = {row["display_name"]: row for row in select(profile, REGISTRY, inventory=EMPTY_INVENTORY)["actions"]}
        self.assertEqual(actions["LaTeX Format"]["action"], "activate-after-confirmation")
        self.assertTrue(actions["LaTeX Format"]["required"])
        self.assertEqual(actions["Zotero"]["action"], "withhold-missing-prerequisite")

    def test_profile_installs_free_listed_companions_after_confirmation(self):
        profile = {"domains": ["life-sciences"], "workflows": ["analyze-data"], "materials": ["datasets"], "stages": ["active-research"], "methods": []}
        actions = {row["display_name"]: row["action"] for row in select(profile, REGISTRY, inventory=EMPTY_INVENTORY)["actions"]}
        self.assertEqual(actions["Life Science Research"], "install-after-confirmation")
        self.assertEqual(actions["Build Web Data Visualization"], "install-after-confirmation")
        self.assertNotIn("Life Sciences NGS Analysis", actions)

    def test_explicit_specialist_plugin_is_included_only_when_requested(self):
        profile = {"domains": ["life-sciences"], "workflows": [], "materials": ["datasets"], "stages": [], "methods": []}
        names = [row["display_name"] for row in select(profile, REGISTRY, inventory=EMPTY_INVENTORY)["actions"]]
        self.assertNotIn("Life Sciences NGS Analysis", names)
        requested = select(profile, REGISTRY, requested_plugins=("Life Sciences NGS Analysis",), inventory=EMPTY_INVENTORY)
        ngs = next(row for row in requested["actions"] if row["display_name"] == "Life Sciences NGS Analysis")
        self.assertEqual(ngs["action"], "install-after-confirmation")

    def test_claude_never_receives_codex_directory_plugins(self):
        profile = {field: [] for field in ("domains", "workflows", "materials", "stages", "methods")}
        plan = select(profile, REGISTRY, host="claude-code", inventory=EMPTY_INVENTORY)
        self.assert_valid_plan(plan)
        self.assertEqual(plan["actions"], [])

    def test_inventory_finds_standalone_skills_without_duplicate_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for parent in (root / "a", root / "b"):
                skill = parent / "proof-audit"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("---\nname: proof-audit\n---\n", encoding="utf-8")
            inventory = collect_inventory({"installed": []}, [root / "a", root / "b"])
            self.assertEqual([row["name"] for row in inventory["skills"]], ["proof-audit"])

    def test_apply_skips_retained_and_installs_only_missing_plugins(self):
        before = {**EMPTY_INVENTORY, "plugins": [{"plugin_id": "pdf@openai-primary-runtime", "name": "pdf", "selector": "pdf@openai-primary-runtime", "version": "1"}]}
        profile = {field: [] for field in ("domains", "workflows", "materials", "stages", "methods")}
        plan = select(profile, REGISTRY, inventory=before)
        calls = []

        def runner(command):
            calls.append(command)
            return SimpleNamespace(returncode=0, stdout="{}", stderr="")

        installed = [{"plugin_id": f"{name}@openai-primary-runtime", "name": name, "selector": f"{name}@openai-primary-runtime", "version": "1"} for name in ("pdf", "documents", "spreadsheets", "presentations")]
        after = {**EMPTY_INVENTORY, "plugins": installed}
        result = apply_plan(plan, before, runner=runner, inventory_reader=lambda: after)
        self.assertEqual(result["status"], "ready")
        add_selectors = [command[3] for command in calls if command[:3] == ["codex", "plugin", "add"]]
        self.assertNotIn("pdf@openai-primary-runtime", add_selectors)
        self.assertEqual(set(add_selectors), {"documents@openai-primary-runtime", "spreadsheets@openai-primary-runtime", "presentations@openai-primary-runtime"})


if __name__ == "__main__":
    unittest.main()
