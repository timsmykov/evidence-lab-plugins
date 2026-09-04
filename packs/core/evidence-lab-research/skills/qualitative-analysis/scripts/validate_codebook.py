#!/usr/bin/env python3
"""Validate the minimum traceability contract for a qualitative codebook."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FIELDS = ("id", "label", "definition", "include_when", "exclude_when")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("codebook", type=Path)
    args = parser.parse_args()
    data = json.loads(args.codebook.read_text(encoding="utf-8"))
    codes = data.get("codes") if isinstance(data, dict) else None
    errors = []
    if not isinstance(codes, list) or not codes:
        errors.append("codes must be a non-empty array")
        codes = []
    ids = []
    for index, code in enumerate(codes):
        if not isinstance(code, dict):
            errors.append(f"codes[{index}] must be an object")
            continue
        for field in FIELDS:
            if not isinstance(code.get(field), str) or not code[field].strip():
                errors.append(f"codes[{index}].{field} must be a non-empty string")
        if isinstance(code.get("id"), str):
            normalized_id = code["id"].strip()
            ids.append(normalized_id)
            if code["id"] != normalized_id or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", normalized_id):
                errors.append(f"codes[{index}].id must be canonical kebab-case without surrounding whitespace")
    if len(ids) != len(set(ids)):
        errors.append("code ids must be unique")
    print(json.dumps({"valid": not errors, "code_count": len(codes), "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
