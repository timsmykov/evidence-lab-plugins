#!/usr/bin/env python3
"""Representative deterministic behavior checks for implemented R3 draft packs."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
TESTED_PACK_IDS = {
    "publication-monitoring", "systematic-review", "qualitative-research",
    "research-images", "life-sciences", "evidence-lab-meeting-capture",
}


def run(script: Path, payload, expected_code: int = 0) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "input.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(script), str(source)], capture_output=True, text=True)
    if completed.returncode != expected_code:
        raise AssertionError(f"{script.name}: expected {expected_code}, got {completed.returncode}: {completed.stderr}")
    return json.loads(completed.stdout)


def fails(script: Path, payload, message: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "input.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(script), str(source)], capture_output=True, text=True)
    if completed.returncode == 0 or message not in completed.stderr:
        raise AssertionError(f"{script.name}: invalid input did not fail clearly: {completed.stderr}")


def main() -> int:
    meeting = ROOT / "packs/workflows/evidence-lab-meeting-capture/skills/evidence-lab-meeting-capture/scripts/validate_meeting_record.py"
    meeting_record = {
        "title": "2026-08-28 — Evidence Lab: meeting capture",
        "date": "2026-08-28",
        "project": "Evidence Lab",
        "meeting_type": "Team meeting",
        "participants": "Tim, Artem",
        "source_url": "https://example.org/transcript",
        "summary_checked": True,
        "source_review_complete": True,
    }
    if not run(meeting, meeting_record)["valid"]:
        raise AssertionError("valid Evidence Lab meeting record rejected")
    invalid_meeting = dict(meeting_record, title="Meeting capture", source_review_complete=False)
    invalid_result = run(meeting, invalid_meeting, expected_code=1)
    if invalid_result["valid"] or len(invalid_result["errors"]) != 2:
        raise AssertionError("invalid meeting title or review state accepted")
    if run(meeting, [], expected_code=1)["valid"]:
        raise AssertionError("non-object meeting record accepted")

    monitor = ROOT / "packs/workflows/publication-monitoring/skills/publication-monitoring/scripts/update_monitor_state.py"
    monitored = run(monitor, {
        "checkpoint": "2026-08-26", "previous_ids": ["doi:old"],
        "records": [{"id": "DOI:NEW", "title": "New"}, {"id": "doi:new", "title": "Duplicate"}, {"id": "doi:old", "title": "Old"}],
    })
    if [row["id"] for row in monitored["new_records"]] != ["DOI:NEW"] or monitored["duplicate_ids"] != ["doi:new"]:
        raise AssertionError("publication monitor did not deduplicate stable IDs")
    fails(monitor, [], "input must be an object")
    fails(monitor, {"records": []}, "checkpoint must be a non-empty string")

    dedupe = ROOT / "packs/workflows/systematic-review/skills/systematic-review/scripts/deduplicate_records.py"
    multilingual_records = json.loads((ROOT / "tests/fixtures/pack-behaviors/systematic-records.ru.json").read_text(encoding="utf-8"))
    deduped = run(dedupe, multilingual_records)
    if len(deduped["records"]) != 3 or {row["canonical_id"] for row in deduped["duplicates"]} != {"a", "d"}:
        raise AssertionError("systematic-review deduplication drift")

    codebook = ROOT / "packs/workflows/qualitative-research/skills/qualitative-analysis/scripts/validate_codebook.py"
    valid_code = {"id": "access", "label": "Access", "definition": "Access barrier", "include_when": "Barrier stated", "exclude_when": "No barrier"}
    if not run(codebook, {"codes": [valid_code]})["valid"]:
        raise AssertionError("valid qualitative codebook rejected")
    invalid_codes = {"codes": [valid_code, valid_code]}
    if run(codebook, invalid_codes, expected_code=1)["valid"]:
        raise AssertionError("duplicate qualitative code IDs accepted")
    spaced_code = dict(valid_code, id=" access ")
    if run(codebook, {"codes": [valid_code, spaced_code]}, expected_code=1)["valid"]:
        raise AssertionError("non-canonical qualitative code ID accepted")
    if run(codebook, [], expected_code=1)["valid"]:
        raise AssertionError("non-object qualitative codebook accepted")

    image = ROOT / "packs/workflows/research-images/skills/research-image-analysis/scripts/validate_image_provenance.py"
    image_record = {"source_id": "img-1", "original_path": "source.tif", "acquisition_context": "microscope run", "transformations": [], "measurements": [], "interpretation_limits": "No diagnosis"}
    if not run(image, image_record)["valid"] or run(image, {"source_id": "img-1"}, expected_code=1)["valid"]:
        raise AssertionError("image provenance validation drift")
    if run(image, [], expected_code=1)["valid"]:
        raise AssertionError("non-object image provenance accepted")
    invalid_image = dict(image_record, source_id="", original_path=None, acquisition_context={}, interpretation_limits="")
    if run(image, invalid_image, expected_code=1)["valid"]:
        raise AssertionError("empty or incorrectly typed image provenance accepted")

    protocol = ROOT / "packs/domains/life-sciences/skills/life-science-protocols/scripts/validate_protocol_record.py"
    protocol_record = {
        "biological_system": "cell line", "protocol_id": "P-1", "protocol_version": "1",
        "unit_of_analysis": "well", "controls": ["negative"], "endpoints": ["signal"],
        "timing": "24h", "bias_risks": ["batch"], "exclusion_rules": ["contamination"],
        "responsible_authority": "institutional biosafety lead",
    }
    if not run(protocol, protocol_record)["valid"] or run(protocol, {}, expected_code=1)["valid"]:
        raise AssertionError("life-science protocol validation drift")
    if run(protocol, [], expected_code=1)["valid"]:
        raise AssertionError("non-object life-science protocol accepted")

    invalid_protocol = dict(protocol_record, protocol_id=123, protocol_version={}, controls="negative")
    if run(protocol, invalid_protocol, expected_code=1)["valid"]:
        raise AssertionError("incorrectly typed life-science protocol accepted")

    decisions = json.loads((ROOT / "catalog/pack-boundary-decisions.json").read_text(encoding="utf-8"))
    required_behavior_ids = {
        item["pack_id"] for item in decisions["prioritized_additions"]
        if item["lifecycle_status"] != "planned"
    }
    if TESTED_PACK_IDS != required_behavior_ids:
        raise AssertionError(f"draft-pack behavior coverage drift: {TESTED_PACK_IDS} != {required_behavior_ids}")

    print(f"PASS: {len(TESTED_PACK_IDS)} draft-pack behavior checks plus invalid-input boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
