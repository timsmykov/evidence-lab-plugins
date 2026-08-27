#!/usr/bin/env python3
"""Regression tests for the complete Codex researcher-plugin inventory."""
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "catalog" / "openai-plugin-audit.json").read_text(encoding="utf-8"))


class ResearchMarketplaceAuditTests(unittest.TestCase):
    def test_target_inventory_is_complete_and_unique(self):
        rows = DATA["target_inventory"]
        self.assertEqual(len(rows), DATA["target_category_entries"])
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        self.assertEqual(sum(DATA["target_component_types"].values()), len(rows))

    def test_target_pure_skill_bundles_are_explicitly_classified(self):
        bundles = {
            row["display_name"]: row
            for row in DATA["target_inventory"]
            if row["component_type"] == "skills-only"
        }
        self.assertEqual(set(bundles), {
            "Boltz", "Life Science Research", "Life Sciences NGS Analysis",
            "Mixpanel Headless", "Zotero",
        })
        for row in bundles.values():
            self.assertNotIn(row["provider_access"], {"requires-bundle-review", "external-service-terms-unverified"})

    def test_connected_services_are_never_treated_as_free_or_automatic(self):
        for row in DATA["target_inventory"]:
            if row["component_type"] in {"app-only", "hybrid"}:
                self.assertEqual(row["provider_access"], "external-service-terms-unverified")
                self.assertNotIn(row["bootstrap_decision"], {"approved-baseline", "automatic-install"})

    def test_skill_only_does_not_imply_self_contained(self):
        rows = {row["display_name"]: row for row in DATA["target_inventory"]}
        self.assertEqual(rows["Mixpanel Headless"]["provider_access"], "external-account-required")
        self.assertIn("spend-confirmation", rows["Boltz"]["provider_access"])
        self.assertEqual(rows["Zotero"]["provider_access"], "local-application-required")

    def test_official_access_evidence_is_recorded_for_priority_services(self):
        rows = {row["display_name"]: row for row in DATA["reviewed_candidates"]}
        for name in ("Consensus", "Elicit", "Readwise", "SciSpace", "Scite", "Zotero"):
            evidence = rows[name]["official_access_evidence"]
            self.assertTrue(evidence["access_summary"])
            self.assertTrue(evidence["evidence_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
