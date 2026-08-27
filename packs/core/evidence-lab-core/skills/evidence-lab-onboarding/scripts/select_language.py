#!/usr/bin/env python3
"""Resolve the first-run language choice without LLM classification."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_CATALOGS = (
    PACK_ROOT / "onboarding" / "language.json",
    PACK_ROOT / "onboarding" / "language.ru.json",
)


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def normalized_answer(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def accepted_answers(catalogs: tuple[dict, ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    option_ids: set[str] = set()
    for catalog in catalogs:
        for option in catalog.get("options", []):
            locale = option["id"]
            option_ids.add(locale)
            for answer in option["accepted_answers"]:
                key = normalized_answer(answer)
                previous = result.get(key)
                if previous is not None and previous != locale:
                    raise ValueError(f"ambiguous language answer: {answer}")
                result[key] = locale
    if option_ids != {"en", "ru"}:
        raise ValueError("language catalogs must define exactly en and ru")
    return result


def select_language(answer: str, catalogs: tuple[dict, ...]) -> str:
    locale = accepted_answers(catalogs).get(normalized_answer(answer))
    if locale is None:
        raise ValueError("unsupported language choice")
    return locale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("answer")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        locale = select_language(args.answer, tuple(load_object(path) for path in DEFAULT_CATALOGS))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps({"schema_version": 1, "locale": locale}, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
