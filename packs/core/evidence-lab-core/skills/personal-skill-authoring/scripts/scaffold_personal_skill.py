#!/usr/bin/env python3
"""Create a minimal personal-skill draft without overwriting existing work."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--positive", action="append", default=[])
    parser.add_argument("--negative", action="append", default=[])
    args = parser.parse_args()

    if not NAME.fullmatch(args.name):
        parser.error("name must be 3-64 lowercase letters, digits, or hyphens")
    if len(args.description.strip()) < 40:
        parser.error("description must explain the job and activation boundary")
    if len(args.positive) < 5 or len(args.negative) < 3:
        parser.error("provide at least five positive and three negative trigger examples")

    target = args.output_dir.resolve() / args.name
    if target.exists():
        parser.error(f"refusing to overwrite existing path: {target}")

    (target / "evals").mkdir(parents=True)
    skill = (
        "---\n"
        f"name: {args.name}\n"
        f"description: {json.dumps(args.description.strip(), ensure_ascii=False)}\n"
        "---\n\n"
        f"# {args.name.replace('-', ' ').title()}\n\n"
        "## Inputs\n\n- TODO: Define the required inputs.\n\n"
        "## Workflow\n\n1. TODO: Define the repeatable steps.\n\n"
        "## Human decisions\n\n- TODO: Define confirmation and stop points.\n\n"
        "## Output and acceptance\n\n- TODO: Define the artifact and quality checks.\n"
    )
    (target / "SKILL.md").write_text(skill, encoding="utf-8")
    cases = [
        *({"query": query, "should_trigger": True} for query in args.positive),
        *({"query": query, "should_trigger": False} for query in args.negative),
    ]
    (target / "evals" / "trigger_eval.json").write_text(
        json.dumps(cases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
