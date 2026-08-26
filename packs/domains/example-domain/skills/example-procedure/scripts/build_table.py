#!/usr/bin/env python3
"""Render extracted.json into a stable summary table.

The deterministic half of example-procedure. Same input, same bytes out —
that is the whole point: two runs of the skill can then be compared, and a
reviewer can rebuild the table without rerunning the model.

Input format:

    {
      "features": ["year", "design", "sample"],
      "documents": [
        {"id": "doc-01", "source": "smith2024.pdf", "values": {"year": "2024", ...}}
      ],
      "unreadable": [{"source": "scan_07.pdf", "reason": "no text layer"}]
    }

Missing values must be null in the input. This script renders them as "—";
it never invents a value.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MISSING = "—"


def escape(value: object) -> str:
    if value is None or value == "":
        return MISSING
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render(data: dict) -> str:
    features = list(data.get("features", []))
    documents = sorted(data.get("documents", []), key=lambda d: str(d.get("id", "")))
    unreadable = data.get("unreadable", [])
    if not features:
        raise ValueError("features must not be empty — the confirmed feature set is the contract")

    header = ["Document", *features]
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    filled = 0
    for doc in documents:
        values = doc.get("values", {})
        row = [escape(doc.get("source") or doc.get("id"))]
        for feature in features:
            cell = escape(values.get(feature))
            filled += cell != MISSING
            row.append(cell)
        lines.append("| " + " | ".join(row) + " |")

    total_cells = len(documents) * len(features)
    coverage = f"{filled}/{total_cells}" if total_cells else "0/0"

    out = [
        "## Summary",
        "",
        *lines,
        "",
        "## Coverage",
        "",
        f"- Documents processed: {len(documents)}",
        f"- Values filled: {coverage}",
        f"- Could not be read: {len(unreadable)}",
    ]
    for item in unreadable:
        out.append(f"  - {escape(item.get('source'))} — {escape(item.get('reason'))}")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="path to extracted.json")
    ap.add_argument("--out", default="-", help="output path, '-' for stdout")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        rendered = render(data)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.out == "-":
        sys.stdout.write(rendered)
    else:
        Path(args.out).write_text(rendered, encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
