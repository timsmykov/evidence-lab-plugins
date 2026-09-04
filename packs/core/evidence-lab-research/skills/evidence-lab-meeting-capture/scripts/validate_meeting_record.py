#!/usr/bin/env python3
"""Validate a proposed Evidence Lab meeting-registry record before a Notion write."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED_TEXT = ("title", "date", "project", "meeting_type", "participants", "source_url")


def load_record(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON: {exc}") from exc


def validate(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["input must be an object"]

    errors: list[str] = []
    for field in REQUIRED_TEXT:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    date = record.get("date")
    if isinstance(date, str) and date.strip() and not DATE_RE.fullmatch(date):
        errors.append("date must use YYYY-MM-DD")

    title = record.get("title")
    if isinstance(title, str) and isinstance(date, str) and DATE_RE.fullmatch(date):
        if not title.startswith(f"{date} — "):
            errors.append("title must start with the meeting date followed by an em dash")

    source_url = record.get("source_url")
    if isinstance(source_url, str) and source_url.strip():
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("source_url must be an absolute HTTP(S) URL")

    for field in ("summary_checked", "source_review_complete"):
        if not isinstance(record.get(field), bool):
            errors.append(f"{field} must be a boolean")

    if record.get("summary_checked") is True and record.get("source_review_complete") is not True:
        errors.append("summary_checked cannot be true before source_review_complete")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON file containing the proposed registry record")
    args = parser.parse_args()

    try:
        record = load_record(args.input)
        errors = validate(record)
    except ValueError as exc:
        errors = [str(exc)]

    result = {"valid": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
