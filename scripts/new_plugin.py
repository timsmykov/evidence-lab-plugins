#!/usr/bin/env python3
"""Scaffold a new plugin from templates/plugin.

    python3 scripts/new_plugin.py systematic-review --skill screening --owner Tim

Creates plugins/<name>/ with one skill, a command, a subagent and an eval set,
all wired to pass verify_repo.py once you replace the placeholder prose.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "plugin"
PLUGINS = ROOT / "plugins"

PLACEHOLDERS = ("__PLUGIN__", "__SKILL__", "__OWNER__", "__REVIEWER__", "__DATE__")
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


def render(text: str, values: dict[str, str]) -> str:
    for key in PLACEHOLDERS:
        text = text.replace(key, values[key])
    return text


def validate_name(value: str, label: str) -> None:
    if not NAME_RE.fullmatch(value):
        raise ValueError(f"{label} must be kebab-case using lowercase letters, digits, and hyphens")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="plugin name, kebab-case")
    ap.add_argument("--skill", required=True, help="name of the first skill, kebab-case")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--reviewer", required=True)
    args = ap.parse_args()

    try:
        validate_name(args.name, "plugin name")
        validate_name(args.skill, "skill name")
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2

    target = PLUGINS / args.name
    if target.exists():
        print(f"FAIL: {target.relative_to(ROOT)} already exists")
        return 1

    values = {
        "__PLUGIN__": args.name,
        "__SKILL__": args.skill,
        "__OWNER__": args.owner,
        "__REVIEWER__": args.reviewer,
        "__DATE__": date.today().isoformat(),
    }

    for src in sorted(TEMPLATE.rglob("*")):
        rel = Path(render(str(src.relative_to(TEMPLATE)), values))
        dst = target / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in {".md", ".json", ".py", ".sh"}:
            dst.write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")
            shutil.copymode(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"created {target.relative_to(ROOT)}")
    print("next: write the real procedure, fill the eval set, then run scripts/verify_repo.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
