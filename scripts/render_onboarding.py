#!/usr/bin/env python3
"""Render canonical Evidence Lab onboarding messages without LLM rewriting."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
if HERE.parent.parent.name == "evidence-lab-onboarding":
    ONBOARDING = HERE.parents[3] / "onboarding"
else:
    ONBOARDING = HERE.parent.parent / "packs" / "core" / "evidence-lab-core" / "onboarding"

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


def language_message() -> str:
    english = load(ONBOARDING / "language.json")
    russian = load(ONBOARDING / "language.ru.json")
    english_option = next(item for item in english["options"] if item["id"] == "en")
    russian_option = next(item for item in russian["options"] if item["id"] == "ru")
    return "\n".join([
        english["prompt"], "",
        f"1. {english_option['label']}",
        f"2. {russian_option['label']}", "",
        english["instruction"], "",
    ])


def question_message(locale: str, number: int, include_expectation: bool = False) -> str:
    suffix = ".ru.json" if locale == "ru" else ".json"
    catalog = load(ONBOARDING / f"questions{suffix}")
    copy = load(ONBOARDING / f"chat-copy{suffix}")
    questions = catalog.get("questions")
    if not isinstance(questions, list) or not 1 <= number <= len(questions):
        raise RenderError(f"question number must be between 1 and {len(questions or [])}")
    question = questions[number - 1]
    if copy.get("locale") != locale:
        raise RenderError("chat copy locale does not match the requested locale")
    heading = copy["question_heading"].format(number=number, total=len(questions))
    lines: list[str] = []
    if include_expectation:
        lines.extend([copy["expectation"], ""])
    lines.extend([f"{heading}: {question['prompt']}", ""])
    lines.extend(f"{index}. {option['label']}" for index, option in enumerate(question["options"], 1))
    lines.extend(["", copy["footer"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    language = subparsers.add_parser("language")
    language.add_argument("--output", type=Path)
    question = subparsers.add_parser("question")
    question.add_argument("--locale", choices=("en", "ru"), required=True)
    question.add_argument("--number", type=int, required=True)
    question.add_argument("--include-expectation", action="store_true")
    question.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        rendered = language_message() if args.command == "language" else question_message(args.locale, args.number, args.include_expectation)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (RenderError, KeyError, StopIteration, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
