#!/usr/bin/env python3
"""Validate a minimal, non-diagnostic provenance record for research images."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("source_id", "original_path", "acquisition_context", "transformations", "measurements", "interpretation_limits")
TEXT_FIELDS = ("source_id", "original_path", "acquisition_context", "interpretation_limits")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    data = json.loads(args.record.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print(json.dumps({"valid": False, "errors": ["record must be an object"]}, indent=2))
        return 1
    errors = [f"missing {field}" for field in REQUIRED if field not in data]
    for field in TEXT_FIELDS:
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} must be a non-empty string")
    if "transformations" in data and not isinstance(data["transformations"], list):
        errors.append("transformations must be an array")
    elif "transformations" in data and any(not isinstance(item, dict) for item in data["transformations"]):
        errors.append("transformations entries must be objects")
    if "measurements" in data and not isinstance(data["measurements"], list):
        errors.append("measurements must be an array")
    elif "measurements" in data and any(not isinstance(item, dict) for item in data["measurements"]):
        errors.append("measurements entries must be objects")
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
