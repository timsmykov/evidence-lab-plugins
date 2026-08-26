#!/usr/bin/env python3
"""Normalize onboarding options and validate an untrusted free-text candidate."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_QUESTIONS = PACK_ROOT / "onboarding" / "questions.json"
DEFAULT_POLICY = PACK_ROOT / "onboarding" / "selection-policy.json"
PROFILE_FIELDS = ("domains", "workflows", "materials", "stages", "methods")
LOCALE = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def question_index(questions: dict) -> dict[str, dict]:
    rows = questions.get("questions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("questions catalog must contain questions")
    result = {row["id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("questions catalog contains duplicate IDs")
    return result


def option_index(question: dict) -> dict[str, dict]:
    result = {option["id"]: option for option in question["options"]}
    if len(result) != len(question["options"]):
        raise ValueError(f"question {question['id']} contains duplicate option IDs")
    return result


def allowed_fields(question: dict) -> set[str]:
    return {option.get("profile_field", question["id"]) for option in question["options"]}


def validate_answers(answers: dict, questions: dict, policy: dict) -> None:
    if set(answers) != {"schema_version", "locale", "answers"}:
        raise ValueError("answers contains unsupported fields")
    if answers.get("schema_version") != 1:
        raise ValueError("answers.schema_version must be 1")
    if not isinstance(answers.get("locale"), str) or not LOCALE.fullmatch(answers["locale"]):
        raise ValueError("answers.locale must be a supported locale identifier")
    rows = answers.get("answers")
    if not isinstance(rows, list) or not rows:
        raise ValueError("answers.answers must be a non-empty array")
    known_questions = question_index(questions)
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not {"question_id", "selected_option_ids"} <= set(row) <= {"question_id", "selected_option_ids", "free_text"}:
            raise ValueError("onboarding answer contains unsupported fields")
        question_id = row.get("question_id")
        if question_id not in known_questions:
            raise ValueError(f"unknown onboarding question: {question_id}")
        if question_id in seen:
            raise ValueError(f"duplicate onboarding answer: {question_id}")
        seen.add(question_id)
        selected = row.get("selected_option_ids")
        if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
            raise ValueError(f"{question_id}.selected_option_ids must be an array of strings")
        if len(selected) != len(set(selected)):
            raise ValueError(f"{question_id}.selected_option_ids contains duplicates")
        options = option_index(known_questions[question_id])
        unknown = sorted(set(selected) - set(options))
        if unknown:
            raise ValueError(f"{question_id} contains unknown options: {', '.join(unknown)}")
        free_text = row.get("free_text")
        if free_text is not None:
            if not isinstance(free_text, str) or not free_text.strip():
                raise ValueError(f"{question_id}.free_text must be non-empty text")
            if len(free_text) > 10000:
                raise ValueError(f"{question_id}.free_text exceeds 10000 characters")
        for option_id in selected:
            option = options[option_id]
            field = option.get("profile_field", question_id)
            if option_id not in policy["profile_fields"][field]["values"]:
                raise ValueError(f"{question_id}.{option_id} is outside Selection Policy")


def sorted_mappings(mappings: list[dict], order: dict[str, int]) -> list[dict]:
    return sorted(mappings, key=lambda item: (order[item["source_question_id"]], item["field"], item["value"], item["source"]))


def normalize_options(answers: dict, questions: dict, policy: dict) -> dict:
    validate_answers(answers, questions, policy)
    questions_by_id = question_index(questions)
    order = {question["id"]: index for index, question in enumerate(questions["questions"])}
    profile = {field: [] for field in PROFILE_FIELDS}
    profile["schema_version"] = 1
    profile["locale"] = answers.get("locale", "en")
    mappings: list[dict] = []
    unmapped: list[dict] = []
    specializations: list[str] = []
    for answer in answers["answers"]:
        question = questions_by_id[answer["question_id"]]
        options = option_index(question)
        for option_id in answer["selected_option_ids"]:
            option = options[option_id]
            field = option.get("profile_field", question["id"])
            if option_id not in profile[field]:
                profile[field].append(option_id)
            mappings.append({
                "source_question_id": question["id"],
                "source": "option",
                "field": field,
                "value": option_id,
                "confidence": 1.0,
                "rationale": "Selected onboarding option.",
            })
        if "free_text" in answer:
            text = answer["free_text"].strip()
            specializations.append(text)
            unmapped.append({
                "source_question_id": question["id"],
                "text": text,
                "reason": "free-text-needs-review",
            })
    for field in PROFILE_FIELDS:
        profile[field] = sorted(profile[field])
    if specializations:
        profile["specialization"] = "\n\n".join(specializations)
    return {
        "schema_version": 1,
        "status": "needs-review" if unmapped else "ready",
        "profile": profile,
        "mappings": sorted_mappings(mappings, order),
        "unmapped": unmapped,
        "follow_up_question": None,
    }


def apply_candidate(answers: dict, candidate: dict, questions: dict, policy: dict) -> dict:
    result = normalize_options(answers, questions, policy)
    expected_candidate_fields = {"schema_version", "mappings", "unresolved_question_ids", "follow_up_question"}
    if set(candidate) != expected_candidate_fields:
        raise ValueError("candidate contains unsupported fields")
    if candidate.get("schema_version") != 1:
        raise ValueError("candidate.schema_version must be 1")
    free_text = {
        answer["question_id"]: answer["free_text"].strip()
        for answer in answers["answers"] if "free_text" in answer
    }
    questions_by_id = question_index(questions)
    mappings = candidate.get("mappings")
    unresolved = candidate.get("unresolved_question_ids")
    if not isinstance(mappings, list) or not isinstance(unresolved, list):
        raise ValueError("candidate mappings and unresolved_question_ids must be arrays")
    if not all(isinstance(question_id, str) for question_id in unresolved):
        raise ValueError("candidate unresolved_question_ids must contain strings")
    if len(unresolved) != len(set(unresolved)):
        raise ValueError("candidate contains duplicate unresolved question IDs")
    unknown_unresolved = sorted(set(unresolved) - set(free_text))
    if unknown_unresolved:
        raise ValueError(f"candidate references questions without free text: {', '.join(unknown_unresolved)}")
    threshold = policy["normalization"]["minimum_confidence"]
    seen: set[tuple[str, str, str]] = set()
    accepted_by_question: set[str] = set()
    low_confidence_questions: set[str] = set()
    for mapping in mappings:
        expected_mapping_fields = {"source_question_id", "field", "value", "confidence", "rationale"}
        if not isinstance(mapping, dict) or set(mapping) != expected_mapping_fields:
            raise ValueError("candidate mapping contains unsupported fields")
        question_id = mapping.get("source_question_id")
        field = mapping.get("field")
        value = mapping.get("value")
        confidence = mapping.get("confidence")
        rationale = mapping.get("rationale")
        if not all(isinstance(item, str) for item in (question_id, field, value)):
            raise ValueError("candidate mapping IDs and values must be strings")
        if question_id not in free_text:
            raise ValueError(f"candidate mapping has no source free text: {question_id}")
        if field not in allowed_fields(questions_by_id[question_id]):
            raise ValueError(f"candidate cannot map {question_id} to field {field}")
        allowed = set(policy["profile_fields"][field]["values"])
        if value not in allowed:
            raise ValueError(f"candidate contains unknown {field} value: {value}")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            raise ValueError("candidate confidence must be between 0 and 1")
        if not isinstance(rationale, str) or not 3 <= len(rationale.strip()) <= 500:
            raise ValueError("candidate rationale must be meaningful text")
        identity = (question_id, field, value)
        if identity in seen:
            raise ValueError(f"candidate contains duplicate mapping: {'/'.join(identity)}")
        seen.add(identity)
        if confidence < threshold:
            low_confidence_questions.add(question_id)
            continue
        accepted_by_question.add(question_id)
        if value not in result["profile"][field]:
            result["profile"][field].append(value)
        result["mappings"].append({
            "source_question_id": question_id,
            "source": "llm",
            "field": field,
            "value": value,
            "confidence": float(confidence),
            "rationale": rationale.strip(),
        })

    unresolved_set = set(unresolved) | low_confidence_questions
    unaccounted = set(free_text) - accepted_by_question - unresolved_set
    unresolved_set.update(unaccounted)
    result["unmapped"] = [
        {
            "source_question_id": question_id,
            "text": free_text[question_id],
            "reason": (
                "low-confidence" if question_id in low_confidence_questions
                else "explicitly-unresolved" if question_id in set(unresolved)
                else "unclassified"
            ),
        }
        for question_id in sorted(unresolved_set)
    ]
    follow_up = candidate.get("follow_up_question")
    if unresolved_set and (not isinstance(follow_up, str) or not 3 <= len(follow_up.strip()) <= 500):
        raise ValueError("candidate must provide a follow-up question for unresolved free text")
    if not unresolved_set and follow_up is not None:
        raise ValueError("candidate follow-up question is only allowed for unresolved free text")
    result["follow_up_question"] = follow_up.strip() if isinstance(follow_up, str) else None
    result["status"] = "needs-follow-up" if unresolved_set else "ready"
    for field in PROFILE_FIELDS:
        result["profile"][field] = sorted(set(result["profile"][field]))
    order = {question["id"]: index for index, question in enumerate(questions["questions"])}
    result["mappings"] = sorted_mappings(result["mappings"], order)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("options", "apply"):
        command = subparsers.add_parser(name)
        command.add_argument("answers", type=Path)
        if name == "apply":
            command.add_argument("candidate", type=Path)
        command.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
        command.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
        command.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        answers = load_object(args.answers)
        questions = load_object(args.questions)
        policy = load_object(args.policy)
        if args.command == "options":
            result = normalize_options(answers, questions, policy)
        else:
            result = apply_candidate(answers, load_object(args.candidate), questions, policy)
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
