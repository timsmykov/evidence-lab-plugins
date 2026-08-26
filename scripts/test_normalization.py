#!/usr/bin/env python3
"""Regression tests for deterministic options and untrusted LLM normalization."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
NORMALIZER = ROOT / "packs/core/evidence-lab-core/skills/evidence-lab-onboarding/scripts/normalize_profile.py"
QUESTIONS_PATH = ROOT / "packs/core/evidence-lab-core/onboarding/questions.json"
POLICY_PATH = ROOT / "packs/core/evidence-lab-core/onboarding/selection-policy.json"
CASES_PATH = ROOT / "tests/fixtures/normalization/cases.json"
LOCALIZED_CASES = ROOT / "tests/fixtures/normalization"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_normalizer():
    spec = importlib.util.spec_from_file_location("evidence_lab_normalizer", NORMALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {NORMALIZER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_schema(value, name: str) -> None:
    schema = load(ROOT / "schemas" / name)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors)
        raise AssertionError(f"{name}: {details}")


def expect_error(callable_, fragment: str) -> None:
    try:
        callable_()
    except ValueError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected error containing {fragment!r}, got {exc!r}") from exc
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


def main() -> int:
    normalizer = load_normalizer()
    questions = load(QUESTIONS_PATH)
    policy = load(POLICY_PATH)
    cases = [*load(CASES_PATH)["cases"], *(load(path) for path in sorted(LOCALIZED_CASES.glob("*.ru.json")))]
    cases_by_id = {case["id"]: case for case in cases}
    results: dict[str, dict] = {}

    for case in cases:
        answers = case["answers"]
        assert_schema(answers, "onboarding-answers.schema.json")
        candidate = case.get("candidate")
        expected_error = case.get("expected_error")
        if candidate is not None:
            action = lambda: normalizer.apply_candidate(answers, candidate, questions, policy)
        else:
            action = lambda: normalizer.normalize_options(answers, questions, policy)
        if expected_error:
            expect_error(action, expected_error)
            continue
        if candidate is not None:
            assert_schema(candidate, "normalization-candidate.schema.json")
        result = action()
        assert_schema(result, "normalization-result.schema.json")
        assert_schema(result["profile"], "profile.schema.json")
        if result["status"] != case["expected_status"]:
            raise AssertionError(f"{case['id']}: expected {case['expected_status']}, got {result['status']}")
        for field, expected in case["expected_values"].items():
            if result["profile"][field] != expected:
                raise AssertionError(f"{case['id']}: {field} expected {expected}, got {result['profile'][field]}")
        results[case["id"]] = result

    for field in ("domains", "workflows", "materials", "stages", "methods"):
        left = results["english-free-text"]["profile"][field]
        right = results["russian-semantic-equivalent"]["profile"][field]
        if left != right:
            raise AssertionError(f"RU/EN semantic parity failed for {field}: {left} != {right}")

    base_answers = {
        "schema_version": 1,
        "locale": "en",
        "answers": [{"question_id": "domains", "selected_option_ids": [], "free_text": "Physics"}],
    }
    base_candidate = {
        "schema_version": 1,
        "mappings": [{
            "source_question_id": "domains",
            "field": "domains",
            "value": "physics",
            "confidence": 0.99,
            "rationale": "The researcher explicitly named physics.",
        }],
        "unresolved_question_ids": [],
        "follow_up_question": None,
    }

    malformed = deepcopy(base_answers)
    malformed["answers"][0]["free_text"] = "   "
    expect_error(lambda: normalizer.normalize_options(malformed, questions, policy), "must be non-empty")
    malformed = deepcopy(base_answers)
    malformed["answers"] = []
    expect_error(lambda: normalizer.normalize_options(malformed, questions, policy), "non-empty array")
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["free_text"] = "x" * 10001
    expect_error(lambda: normalizer.normalize_options(malformed, questions, policy), "exceeds 10000")

    answer_failures = []
    malformed = deepcopy(base_answers)
    malformed["extra"] = True
    answer_failures.append((malformed, "unsupported fields"))
    malformed = deepcopy(base_answers)
    malformed["schema_version"] = 2
    answer_failures.append((malformed, "must be 1"))
    malformed = deepcopy(base_answers)
    malformed["locale"] = "english"
    answer_failures.append((malformed, "locale"))
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["extra"] = True
    answer_failures.append((malformed, "onboarding answer contains unsupported fields"))
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["question_id"] = "unknown-question"
    answer_failures.append((malformed, "unknown onboarding question"))
    malformed = deepcopy(base_answers)
    malformed["answers"].append(deepcopy(malformed["answers"][0]))
    answer_failures.append((malformed, "duplicate onboarding answer"))
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["selected_option_ids"] = "physics"
    answer_failures.append((malformed, "array of strings"))
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["selected_option_ids"] = ["physics", "physics"]
    answer_failures.append((malformed, "contains duplicates"))
    malformed = deepcopy(base_answers)
    malformed["answers"][0]["selected_option_ids"] = ["invented-domain"]
    answer_failures.append((malformed, "unknown options"))
    for malformed, fragment in answer_failures:
        expect_error(lambda malformed=malformed: normalizer.normalize_options(malformed, questions, policy), fragment)

    wrong_field = deepcopy(base_candidate)
    wrong_field["mappings"][0]["field"] = "methods"
    wrong_field["mappings"][0]["value"] = "formulas"
    expect_error(lambda: normalizer.apply_candidate(base_answers, wrong_field, questions, policy), "cannot map")

    duplicate = deepcopy(base_candidate)
    duplicate["mappings"].append(deepcopy(duplicate["mappings"][0]))
    expect_error(lambda: normalizer.apply_candidate(base_answers, duplicate, questions, policy), "duplicate mapping")

    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["unresolved_question_ids"] = [["domains"]]
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "must contain strings")
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["field"] = ["domains"]
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "must be strings")

    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["confidence"] = True
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "between 0 and 1")
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["rationale"] = "x"
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "meaningful text")
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["source_question_id"] = "materials"
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "no source free text")

    candidate_failures = []
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["schema_version"] = 2
    candidate_failures.append((malformed_candidate, "candidate.schema_version"))
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"] = {}
    candidate_failures.append((malformed_candidate, "must be arrays"))
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["extra"] = True
    candidate_failures.append((malformed_candidate, "mapping contains unsupported fields"))
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["confidence"] = -0.01
    candidate_failures.append((malformed_candidate, "between 0 and 1"))
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["confidence"] = 1.01
    candidate_failures.append((malformed_candidate, "between 0 and 1"))
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["mappings"][0]["rationale"] = "x" * 501
    candidate_failures.append((malformed_candidate, "meaningful text"))
    for malformed_candidate, fragment in candidate_failures:
        expect_error(
            lambda malformed_candidate=malformed_candidate: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy),
            fragment,
        )

    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["unresolved_question_ids"] = ["materials"]
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "without free text")
    malformed_candidate = deepcopy(base_candidate)
    malformed_candidate["unresolved_question_ids"] = ["domains", "domains"]
    expect_error(lambda: normalizer.apply_candidate(base_answers, malformed_candidate, questions, policy), "duplicate unresolved")

    unresolved = deepcopy(base_candidate)
    unresolved["mappings"] = []
    unresolved["unresolved_question_ids"] = ["domains"]
    expect_error(lambda: normalizer.apply_candidate(base_answers, unresolved, questions, policy), "follow-up question")
    unresolved["unresolved_question_ids"] = []
    expect_error(lambda: normalizer.apply_candidate(base_answers, unresolved, questions, policy), "follow-up question")

    unnecessary_follow_up = deepcopy(base_candidate)
    unnecessary_follow_up["follow_up_question"] = "Do you mean physics?"
    expect_error(lambda: normalizer.apply_candidate(base_answers, unnecessary_follow_up, questions, policy), "only allowed")

    exact_threshold = deepcopy(base_candidate)
    exact_threshold["mappings"][0]["confidence"] = policy["normalization"]["minimum_confidence"]
    if normalizer.apply_candidate(base_answers, exact_threshold, questions, policy)["status"] != "ready":
        raise AssertionError("a mapping exactly at the confidence threshold must be accepted")

    selected_and_mapped = deepcopy(base_answers)
    selected_and_mapped["answers"][0]["selected_option_ids"] = ["physics"]
    deduplicated = normalizer.apply_candidate(selected_and_mapped, base_candidate, questions, policy)
    if deduplicated["profile"]["domains"] != ["physics"]:
        raise AssertionError("option and LLM mappings must not duplicate profile values")

    explicitly_unresolved = deepcopy(base_candidate)
    explicitly_unresolved["mappings"] = []
    explicitly_unresolved["unresolved_question_ids"] = ["domains"]
    explicitly_unresolved["follow_up_question"] = "Which research field is your primary focus?"
    explicit_result = normalizer.apply_candidate(base_answers, explicitly_unresolved, questions, policy)
    if explicit_result["unmapped"][0]["reason"] != "explicitly-unresolved":
        raise AssertionError("explicit unresolved evidence was not preserved")

    unclassified = deepcopy(explicitly_unresolved)
    unclassified["unresolved_question_ids"] = []
    unclassified_result = normalizer.apply_candidate(base_answers, unclassified, questions, policy)
    if unclassified_result["unmapped"][0]["reason"] != "unclassified":
        raise AssertionError("unaccounted free text was not marked unclassified")

    first = normalizer.apply_candidate(base_answers, base_candidate, questions, policy)
    second = normalizer.apply_candidate(deepcopy(base_answers), deepcopy(base_candidate), questions, policy)
    if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
        raise AssertionError("normalization is not deterministic")
    english = cases_by_id["english-free-text"]
    forward = normalizer.apply_candidate(english["answers"], english["candidate"], questions, policy)
    reversed_candidate = deepcopy(english["candidate"])
    reversed_candidate["mappings"].reverse()
    reversed_result = normalizer.apply_candidate(english["answers"], reversed_candidate, questions, policy)
    if json.dumps(forward, sort_keys=True) != json.dumps(reversed_result, sort_keys=True):
        raise AssertionError("candidate mapping order changed the canonical result")

    with tempfile.TemporaryDirectory(prefix="evidence-lab-normalizer-") as temp_dir:
        temp = Path(temp_dir)
        answers_path = temp / "answers.json"
        candidate_path = temp / "candidate.json"
        output_path = temp / "result.json"
        answers_path.write_text(json.dumps(base_answers), encoding="utf-8")
        candidate_path.write_text(json.dumps(base_candidate), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(NORMALIZER), "apply", str(answers_path), str(candidate_path), "--output", str(output_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0 or load(output_path)["status"] != "ready":
            raise AssertionError(f"normalizer CLI apply failed: {completed.stderr}")
        options = subprocess.run(
            [sys.executable, str(NORMALIZER), "options", str(answers_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if options.returncode != 0 or json.loads(options.stdout)["status"] != "needs-review":
            raise AssertionError(f"normalizer CLI options failed: {options.stderr}")
        candidate_path.write_text(json.dumps({**base_candidate, "pack_id": "quantitative-sciences"}), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(NORMALIZER), "apply", str(answers_path), str(candidate_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if rejected.returncode != 2 or "unsupported fields" not in rejected.stderr:
            raise AssertionError("normalizer CLI did not safely reject a smuggled pack ID")
        malformed_json = temp / "malformed.json"
        malformed_json.write_text("not-json", encoding="utf-8")
        malformed_cli = subprocess.run(
            [sys.executable, str(NORMALIZER), "options", str(malformed_json)],
            check=False,
            capture_output=True,
            text=True,
        )
        if malformed_cli.returncode != 2 or "FAIL:" not in malformed_cli.stderr:
            raise AssertionError("normalizer CLI did not safely reject malformed JSON")
        non_object = temp / "array.json"
        non_object.write_text("[]", encoding="utf-8")
        non_object_cli = subprocess.run(
            [sys.executable, str(NORMALIZER), "options", str(non_object)],
            check=False,
            capture_output=True,
            text=True,
        )
        if non_object_cli.returncode != 2 or "expected a JSON object" not in non_object_cli.stderr:
            raise AssertionError("normalizer CLI did not safely reject a non-object document")

    print(f"PASS: {len(cases)} fixtures plus hardening, parity, and determinism checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
