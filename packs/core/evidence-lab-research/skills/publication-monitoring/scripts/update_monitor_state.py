#!/usr/bin/env python3
"""Deterministically deduplicate monitor records and advance a visible checkpoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("input must be an object")
    checkpoint = data.get("checkpoint")
    if not isinstance(checkpoint, str) or not checkpoint.strip():
        raise SystemExit("checkpoint must be a non-empty string")
    previous_ids = data.get("previous_ids", [])
    if not isinstance(previous_ids, list) or not all(isinstance(item, str) and item.strip() for item in previous_ids):
        raise SystemExit("previous_ids must be an array of non-empty strings")
    previous = {item.strip().lower() for item in previous_ids}
    records = data.get("records", [])
    if not isinstance(records, list) or any(not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip() for row in records):
        raise SystemExit("records must be objects with non-empty string id")
    by_id = {}
    duplicates = []
    for row in records:
        key = row["id"].strip().lower()
        if key in by_id:
            duplicates.append(key)
        else:
            by_id[key] = row
    new_ids = sorted(set(by_id) - previous)
    result = {
        "checkpoint": checkpoint.strip(),
        "new_records": [by_id[key] for key in new_ids],
        "duplicate_ids": sorted(set(duplicates)),
        "known_ids": sorted(previous | set(by_id)),
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
