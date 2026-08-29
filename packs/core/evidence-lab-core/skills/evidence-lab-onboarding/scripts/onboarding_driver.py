#!/usr/bin/env python3
"""One stateful, deterministic entrypoint for Evidence Lab onboarding."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from bootstrap import apply_plan, load_object, make_plan, release_identity, render_recommendation
from normalize_profile import apply_candidate, normalize_options
from render_onboarding import language_message, question_message
from select_language import select_language


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_CATALOG = PACK_ROOT / "catalog" / "packs.json"
QUESTION_IDS = ("domains", "workflows", "materials", "stages")
YES = {"en": {"yes", "y", "confirm", "1"}, "ru": {"\u0434\u0430", "\u0434", "\u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044e", "1"}}
NO = {"en": {"no", "n", "cancel", "2"}, "ru": {"\u043d\u0435\u0442", "\u043d", "\u043e\u0442\u043c\u0435\u043d\u0430", "2"}}


class DriverError(RuntimeError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json_atomic(path: Path, value: dict) -> None:
    from bootstrap import write_json_atomic as write

    write(path, value)


def locale_file(stem: str, locale: str) -> Path:
    return PACK_ROOT / "onboarding" / f"{stem}{'.ru' if locale == 'ru' else ''}.json"


def copy(locale: str) -> dict:
    return load_object(locale_file("chat-copy", locale))


def load_session(path: Path) -> dict:
    session = load_object(path)
    if session.get("schema_version") != 1 or session.get("stage") not in {
        "language", "questions", "needs-normalization", "awaiting-confirmation",
        "confirmed", "applying", "ready", "declined", "failed",
    }:
        raise DriverError("INVALID_SESSION", "The onboarding session is invalid.")
    return session


def record_step(session: dict, name: str, started: float, status: str, code: str | None = None) -> None:
    row = {
        "name": name,
        "status": status,
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "completed_at": utc_now(),
    }
    if code:
        row["diagnostic_code"] = code
    session.setdefault("steps", []).append(row)


def timing_summary(session: dict) -> dict:
    values = sorted(float(row["duration_ms"]) for row in session.get("steps", []))
    if not values:
        return {"count": 0, "p50_ms": 0, "p95_ms": 0, "total_ms": 0}

    def percentile(q: float) -> float:
        index = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
        return round(values[index], 3)

    return {
        "count": len(values),
        "p50_ms": percentile(0.50),
        "p95_ms": percentile(0.95),
        "total_ms": round(sum(values), 3),
    }


def envelope(session: dict, message: str, next_action: str, *, code: str | None = None) -> dict:
    result = {
        "schema_version": 1,
        "stage": session["stage"],
        "locale": session.get("locale"),
        "user_message": message,
        "next_action": next_action,
        "progress_update_seconds": 60,
        "timing": timing_summary(session),
    }
    if code:
        result["diagnostic_code"] = code
    return result


def parse_answer(text: str, question: dict) -> dict:
    stripped = text.strip()
    option_ids = [option["id"] for option in question["options"]]
    if re.fullmatch(r"\s*\d+(?:\s*[,;+]\s*\d+)*\s*", stripped):
        numbers = [int(value) for value in re.findall(r"\d+", stripped)]
        if len(numbers) != len(set(numbers)) or any(number < 1 or number > len(option_ids) for number in numbers):
            raise DriverError("INVALID_OPTION", "The selected option is not available.")
        return {"question_id": question["id"], "selected_option_ids": [option_ids[number - 1] for number in numbers]}
    if not stripped:
        raise DriverError("EMPTY_ANSWER", "The answer cannot be empty.")
    return {"question_id": question["id"], "selected_option_ids": [], "free_text": stripped}


def build_installation_plan(session: dict, session_path: Path, profile: dict) -> str:
    catalog_path = Path(session["catalog"])
    lock_path = Path(session["release_lock"])
    catalog = load_object(catalog_path)
    from select_packs import select

    selection = select(profile, catalog)
    release = release_identity(
        load_object(lock_path), session["ref"], session["source"], selection, catalog_path
    )
    plan = make_plan(
        profile, catalog, session["host"], session["source"], session["ref"],
        session["marketplace"], release,
    )
    plan_path = session_path.parent / "installation-plan.json"
    recommendation_path = session_path.parent / "recommendation.md"
    write_json_atomic(plan_path, plan)
    rendered = render_recommendation(plan, session["locale"], recommendation_path)
    session["profile"] = profile
    session["plan_path"] = str(plan_path)
    session["recommendation_path"] = str(recommendation_path)
    session["selected_pack_ids"] = [row["id"] for row in plan["selection_plan"]["packs"]]
    session["stage"] = "awaiting-confirmation"
    return rendered


def command_start(args: argparse.Namespace) -> tuple[dict, dict]:
    if args.session.exists():
        raise DriverError("SESSION_EXISTS", "An onboarding session already exists.")
    session = {
        "schema_version": 1,
        "stage": "language",
        "locale": None,
        "answers": [],
        "host": args.host,
        "source": args.source,
        "ref": args.ref,
        "marketplace": args.marketplace,
        "catalog": str(args.catalog.resolve()),
        "release_lock": str(args.release_lock.resolve()),
        "created_at": utc_now(),
        "steps": [],
        "error": None,
    }
    started = time.monotonic()
    message = language_message()
    record_step(session, "language-prompt", started, "completed")
    write_json_atomic(args.session, session)
    return session, envelope(session, message, "answer-language")


def command_answer(args: argparse.Namespace) -> tuple[dict, dict]:
    session = load_session(args.session)
    started = time.monotonic()
    if session["stage"] == "language":
        catalogs = (load_object(locale_file("language", "en")), load_object(locale_file("language", "ru")))
        try:
            session["locale"] = select_language(args.text, catalogs)
        except ValueError:
            record_step(session, "language-answer", started, "rejected", "UNSUPPORTED_LANGUAGE")
            write_json_atomic(args.session, session)
            return session, envelope(session, language_message(), "answer-language", code="UNSUPPORTED_LANGUAGE")
        session["stage"] = "questions"
        record_step(session, "language-answer", started, "completed")
        message = question_message(session["locale"], 1, True)
        write_json_atomic(args.session, session)
        return session, envelope(session, message, "answer-question-1")

    if session["stage"] != "questions":
        raise DriverError("WRONG_STAGE", "This session is not waiting for a research answer.")
    questions = load_object(locale_file("questions", session["locale"]))["questions"]
    index = len(session["answers"])
    if index >= len(questions):
        raise DriverError("QUESTIONS_COMPLETE", "All research questions are already answered.")
    try:
        row = parse_answer(args.text, questions[index])
    except DriverError as exc:
        record_step(session, f"question-{index + 1}", started, "rejected", exc.code)
        write_json_atomic(args.session, session)
        return session, envelope(session, question_message(session["locale"], index + 1), f"answer-question-{index + 1}", code=exc.code)
    session["answers"].append(row)
    record_step(session, f"question-{index + 1}", started, "completed")
    if len(session["answers"]) < len(questions):
        number = len(session["answers"]) + 1
        write_json_atomic(args.session, session)
        return session, envelope(session, question_message(session["locale"], number), f"answer-question-{number}")

    answers = {"schema_version": 1, "locale": session["locale"], "answers": session["answers"]}
    write_json_atomic(args.session.parent / "onboarding-answers.json", answers)
    result = normalize_options(answers, questions={"schema_version": 1, "questions": questions}, policy=load_object(PACK_ROOT / "onboarding" / "selection-policy.json"))
    if result["status"] == "needs-review":
        session["stage"] = "needs-normalization"
        session["normalization_request"] = result["unmapped"]
        message = copy(session["locale"])["normalizing"]
        next_action = "submit-normalization-candidate"
    else:
        message = build_installation_plan(session, args.session, result["profile"])
        next_action = "confirm-plan"
    write_json_atomic(args.session, session)
    return session, envelope(session, message, next_action)


def command_normalize(args: argparse.Namespace) -> tuple[dict, dict]:
    session = load_session(args.session)
    if session["stage"] != "needs-normalization":
        raise DriverError("WRONG_STAGE", "This session is not waiting for normalization.")
    started = time.monotonic()
    answers = load_object(args.session.parent / "onboarding-answers.json")
    questions = load_object(locale_file("questions", session["locale"]))
    policy = load_object(PACK_ROOT / "onboarding" / "selection-policy.json")
    result = apply_candidate(answers, load_object(args.candidate), questions, policy)
    if result["status"] != "ready":
        question_id = result.get("question_id") or result.get("unmapped", [{}])[0].get("question_id")
        if not question_id:
            request = session.get("normalization_request", [])
            question_id = request[0].get("question_id") if request else None
        session["pending_follow_up_question_id"] = question_id
        record_step(session, "normalization", started, "rejected", "NORMALIZATION_NEEDS_FOLLOW_UP")
        write_json_atomic(args.session, session)
        response = envelope(session, result["follow_up_question"], "record-normalization-follow-up", code="NORMALIZATION_NEEDS_FOLLOW_UP")
        response["normalization_question_id"] = question_id
        return session, response
    rendered = build_installation_plan(session, args.session, result["profile"])
    record_step(session, "normalization", started, "completed")
    write_json_atomic(args.session, session)
    return session, envelope(session, rendered, "confirm-plan")


def command_follow_up(args: argparse.Namespace) -> tuple[dict, dict]:
    session = load_session(args.session)
    if session["stage"] != "needs-normalization":
        raise DriverError("WRONG_STAGE", "This session is not waiting for normalization follow-up.")
    question_id = session.get("pending_follow_up_question_id")
    if not question_id:
        raise DriverError("NO_PENDING_FOLLOW_UP", "No normalization follow-up is pending.")
    text = args.text.strip()
    if not text:
        raise DriverError("EMPTY_ANSWER", "The answer cannot be empty.")
    started = time.monotonic()
    answers_path = args.session.parent / "onboarding-answers.json"
    answers = load_object(answers_path)
    row = next((item for item in answers["answers"] if item["question_id"] == question_id), None)
    if row is None:
        raise DriverError("FOLLOW_UP_TARGET_MISSING", "The original answer is missing.")
    original = row.get("free_text", "")
    row["free_text"] = f"{original}\n\nFollow-up: {text}".strip()
    write_json_atomic(answers_path, answers)
    session.pop("pending_follow_up_question_id", None)
    record_step(session, "normalization-follow-up", started, "completed")
    write_json_atomic(args.session, session)
    return session, envelope(session, copy(session["locale"])["normalizing"], "submit-normalization-candidate")


def command_confirm(args: argparse.Namespace) -> tuple[dict, dict]:
    session = load_session(args.session)
    if session["stage"] != "awaiting-confirmation":
        raise DriverError("WRONG_STAGE", "This session is not waiting for confirmation.")
    started = time.monotonic()
    answer = args.text.strip().casefold()
    if answer in NO[session["locale"]]:
        session["stage"] = "declined"
        record_step(session, "confirmation", started, "declined")
        write_json_atomic(args.session, session)
        return session, envelope(session, copy(session["locale"])["declined"], "done")
    if answer not in YES[session["locale"]]:
        record_step(session, "confirmation", started, "rejected", "CONFIRMATION_REQUIRED")
        write_json_atomic(args.session, session)
        return session, envelope(session, copy(session["locale"])["confirmation_retry"], "confirm-plan", code="CONFIRMATION_REQUIRED")
    session["stage"] = "confirmed"
    record_step(session, "confirmation", started, "completed")
    write_json_atomic(args.session, session)
    return session, envelope(session, copy(session["locale"])["installing"], "apply")


def command_apply(args: argparse.Namespace) -> tuple[dict, dict]:
    session = load_session(args.session)
    if session["stage"] != "confirmed":
        raise DriverError("CONFIRMATION_REQUIRED", "Installation has not been confirmed.")
    started = time.monotonic()
    session["stage"] = "applying"
    write_json_atomic(args.session, session)
    state_path = args.session.parent / "installation-state.json"
    state = apply_plan(
        load_object(Path(session["plan_path"])), state_path,
        load_object(Path(session["release_lock"])), Path(session["catalog"]),
    )
    if state["status"] != "ready":
        session["stage"] = "failed"
        session["error"] = {"code": "INSTALLATION_FAILED", "state": state["status"]}
        record_step(session, "apply", started, "failed", "INSTALLATION_FAILED")
        message = copy(session["locale"])["installation_failed"]
        next_action = "inspect-or-recover"
        code = "INSTALLATION_FAILED"
    else:
        from bootstrap import render_completion

        session["stage"] = "ready"
        session["installation_state_path"] = str(state_path)
        session["error"] = None
        record_step(session, "apply", started, "completed")
        message = render_completion(session["locale"])
        next_action = "open-new-task-and-run-probes"
        code = None
    write_json_atomic(args.session, session)
    return session, envelope(session, message, next_action, code=code)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--session", type=Path, required=True)
    start.add_argument("--host", choices=("codex", "claude-code"), required=True)
    start.add_argument("--source", default="timsmykov/evidence-lab-plugins")
    start.add_argument("--ref", required=True)
    start.add_argument("--marketplace", default="evidence-lab-plugins")
    start.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    start.add_argument("--release-lock", type=Path, required=True)
    for name in ("answer", "confirm", "follow-up"):
        command = sub.add_parser(name)
        command.add_argument("--session", type=Path, required=True)
        command.add_argument("--text", required=True)
    normalize = sub.add_parser("normalize")
    normalize.add_argument("--session", type=Path, required=True)
    normalize.add_argument("--candidate", type=Path, required=True)
    apply = sub.add_parser("apply")
    apply.add_argument("--session", type=Path, required=True)
    status = sub.add_parser("status")
    status.add_argument("--session", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "start":
            session, result = command_start(args)
        elif args.command == "answer":
            session, result = command_answer(args)
        elif args.command == "normalize":
            session, result = command_normalize(args)
        elif args.command == "follow-up":
            session, result = command_follow_up(args)
        elif args.command == "confirm":
            session, result = command_confirm(args)
        elif args.command == "apply":
            session, result = command_apply(args)
        else:
            session = load_session(args.session)
            result = envelope(session, "", "none")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if session["stage"] not in {"failed"} else 1
    except (DriverError, ValueError, OSError, json.JSONDecodeError) as exc:
        code = exc.code if isinstance(exc, DriverError) else "DRIVER_ERROR"
        print(json.dumps({"schema_version": 1, "diagnostic_code": code, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
