#!/usr/bin/env python3
"""Render a locked Evidence Lab installation plan as plain-language Markdown."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "onboarding-plan-copy.schema.json"
COPY_ROOT = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding"


class RenderError(ValueError):
    pass


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RenderError(f"could not read valid JSON from {path}") from exc
    if not isinstance(value, dict):
        raise RenderError(f"{path} must contain a JSON object")
    return value


def normalized_locale(requested: str | None, plan: dict) -> str:
    value = requested or plan.get("selection_plan", {}).get("profile", {}).get("locale") or "en"
    return "ru" if str(value).casefold().startswith("ru") else "en"


def load_copy(locale: str, copy_root: Path = COPY_ROOT) -> dict:
    suffix = ".ru.json" if locale == "ru" else ".json"
    path = copy_root / f"plan-copy{suffix}"
    copy = load(path)
    errors = sorted(Draft202012Validator(load(SCHEMA)).iter_errors(copy), key=lambda item: list(item.path))
    if errors:
        raise RenderError(f"{path}: {'/'.join(map(str, errors[0].path)) or '<root>'}: {errors[0].message}")
    if copy["locale"] != locale:
        raise RenderError(f"{path}: locale does not match its filename")
    return copy


def indexed(rows: list[dict], label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for row in rows:
        identity = row["id"]
        if identity in result:
            raise RenderError(f"duplicate {label} copy: {identity}")
        result[identity] = row
    return result


def render(plan: dict, copy: dict) -> str:
    if plan.get("schema_version") != 1 or plan.get("host") not in copy["hosts"]:
        raise RenderError("unsupported installation plan or host")
    release = plan.get("release", {}).get("tag")
    packs = plan.get("selection_plan", {}).get("packs")
    if not isinstance(release, str) or not isinstance(packs, list) or not packs:
        raise RenderError("installation plan has no locked release or selected packs")

    pack_copy = indexed(copy["packs"], "pack")
    rule_copy = indexed(copy["rules"], "rule")
    lines = [f"# {copy['heading']}", "", copy["intro"], ""]
    for number, pack in enumerate(packs, 1):
        pack_id = pack.get("id")
        if pack_id not in pack_copy:
            raise RenderError(f"missing localized copy for pack: {pack_id}")
        item = pack_copy[pack_id]
        reasons: list[str] = []
        for rule_id in pack.get("rule_ids", []):
            if rule_id.startswith("dependency-"):
                continue
            if rule_id not in rule_copy:
                raise RenderError(f"missing localized copy for selection rule: {rule_id}")
            reason = rule_copy[rule_id]["reason"]
            if reason not in reasons:
                reasons.append(reason)
        if not reasons:
            reasons.append(item["purpose"])
        lines.extend([
            f"{number}. **{item['title']}**",
            f"   {item['purpose']}",
            f"   {copy['why_label']}: {' '.join(reasons)}",
            "",
        ])

    lines.extend([
        copy["details"].format(
            count=len(packs),
            host=copy["hosts"][plan["host"]],
            release=release,
        ),
        "",
        f"**{copy['pending']}**",
        "",
        copy["confirmation"],
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--locale", choices=("en", "ru"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        plan = load(args.plan)
        locale = normalized_locale(args.locale, plan)
        rendered = render(plan, load_copy(locale))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except RenderError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
