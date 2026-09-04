#!/usr/bin/env python3
"""Validate minimum life-science protocol metadata without judging scientific merit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = (
    "biological_system", "protocol_id", "protocol_version", "unit_of_analysis",
    "controls", "endpoints", "timing", "bias_risks", "exclusion_rules", "responsible_authority"
)
TEXT_FIELDS = ("biological_system", "protocol_id", "protocol_version", "unit_of_analysis", "timing", "responsible_authority")
LIST_FIELDS = ("controls", "endpoints", "bias_risks", "exclusion_rules")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    data = json.loads(args.record.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print(json.dumps({"valid": False, "errors": ["record must be an object"]}, indent=2))
        return 1
    errors = []
    for field in REQUIRED:
        if field not in data:
            errors.append(f"missing {field}")
    for field in TEXT_FIELDS:
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} must be a non-empty string")
    for field in LIST_FIELDS:
        if field in data and (
            not isinstance(data[field], list)
            or not data[field]
            or any(not isinstance(item, str) or not item.strip() for item in data[field])
        ):
            errors.append(f"{field} must be a non-empty array of non-empty strings")
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
