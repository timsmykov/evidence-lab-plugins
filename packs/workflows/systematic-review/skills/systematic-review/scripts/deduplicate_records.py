#!/usr/bin/env python3
"""Deduplicate review records by normalized DOI, then normalized title and year."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def key(row: dict) -> str:
    doi = re.sub(r"^(?:https?://doi\.org/|doi:\s*)", "", str(row.get("doi", "")).strip().lower())
    if doi:
        return f"doi:{doi}"
    raw_title = str(row.get("title", "")).casefold()
    title = " ".join("".join(character if character.isalnum() else " " for character in raw_title).split())
    year = str(row.get("year", "")).strip()
    if not title:
        raise ValueError("each record needs a DOI or title")
    return f"title-year:{title}|{year}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise SystemExit("input must be an array of record objects")
    canonical = {}
    duplicates = []
    for index, row in enumerate(records):
        identity = key(row)
        record_id = str(row.get("id", index))
        if identity in canonical:
            duplicates.append({"duplicate_id": record_id, "canonical_id": canonical[identity]["id"], "key": identity})
        else:
            canonical[identity] = {"id": record_id, "record": row}
    result = {"records": [canonical[item]["record"] for item in sorted(canonical)], "duplicates": sorted(duplicates, key=lambda row: (row["canonical_id"], row["duplicate_id"]))}
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
