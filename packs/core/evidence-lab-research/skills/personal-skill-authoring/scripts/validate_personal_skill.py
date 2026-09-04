#!/usr/bin/env python3
"""Validate the portable structure and trigger boundary of a personal skill."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    block = text[4:text.index("\n---\n", 4)]
    result: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("\"'")
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_personal_skill.py PATH_TO_SKILL", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    eval_path = root / "evals" / "trigger_eval.json"
    if not skill_path.is_file():
        errors.append("missing SKILL.md")
    else:
        fields = frontmatter(skill_path.read_text(encoding="utf-8"))
        if not NAME.fullmatch(fields.get("name", "")):
            errors.append("frontmatter name is missing or invalid")
        if len(fields.get("description", "")) < 40:
            errors.append("description must explain the job and activation boundary")
    if not eval_path.is_file():
        errors.append("missing evals/trigger_eval.json")
    else:
        try:
            cases = json.loads(eval_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"invalid trigger eval: {exc}")
        else:
            positives = sum(case.get("should_trigger") is True for case in cases)
            negatives = sum(case.get("should_trigger") is False for case in cases)
            if positives < 5 or negatives < 3:
                errors.append("trigger eval needs at least five positive and three negative cases")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
