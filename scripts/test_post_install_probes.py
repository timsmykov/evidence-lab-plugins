#!/usr/bin/env python3
"""Tests for profile-aware post-install probes."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "scripts/run_post_install_probes.py"
SPEC = importlib.util.spec_from_file_location("post_install_probes", PATH)
assert SPEC and SPEC.loader
probes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probes)


class PostInstallProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = probes.load(probes.REGISTRY)
        self.catalog = probes.load(probes.CATALOG)
        self.index = probes.index_registry(self.registry, self.catalog)

    def plan(self, pack_ids: list[str]) -> dict:
        return {"selection_plan": {"packs": [{"id": pack_id} for pack_id in pack_ids]}}

    def test_registry_covers_every_published_pack(self) -> None:
        published = {row["id"] for row in self.catalog["packs"] if row["id"] != "example-domain"}
        self.assertEqual(published, set(self.index))

    def test_core_has_three_distinct_capability_probes(self) -> None:
        rows = self.index["evidence-lab-core"]["probes"]
        self.assertGreaterEqual(len(rows), 3)
        self.assertEqual(len(rows), len({row["capability"] for row in rows}))

    def test_representative_profile_runs_selected_pack_probes(self) -> None:
        selected = ["evidence-lab-core", "document-evidence", "literature-publication", "qualitative-research"]
        result = probes.run_plan(self.plan(selected), self.registry, self.catalog, {}, ROOT)
        self.assertEqual("pass", result["status"], result)
        self.assertEqual(selected, [row["pack_id"] for row in result["packs"]])

    def test_missing_skill_breaks_the_corresponding_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = ROOT / self.index["research-images"]["pack_path"]
            target = Path(temporary) / "research-images"
            shutil.copytree(source, target)
            (target / "skills/research-image-analysis/SKILL.md").unlink()
            result = probes.run_plan(self.plan(["research-images"]), self.registry, self.catalog, {"research-images": target})
            self.assertEqual("fail", result["status"])
            self.assertEqual("REQUIRED_PATH_MISSING", result["packs"][0]["probes"][0]["failure"])

    def test_missing_manifest_entry_breaks_registry_validation(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["packs"] = [row for row in registry["packs"] if row["pack_id"] != "systematic-review"]
        with self.assertRaisesRegex(probes.ProbeError, "coverage"):
            probes.index_registry(registry, self.catalog)


if __name__ == "__main__":
    unittest.main()
