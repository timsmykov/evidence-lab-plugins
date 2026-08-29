#!/usr/bin/env python3
"""Tests for the single deterministic onboarding driver."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
DRIVER_PATH = ROOT / "packs/core/evidence-lab-core/skills/evidence-lab-onboarding/scripts/onboarding_driver.py"
sys.path.insert(0, str(DRIVER_PATH.parent))
SPEC = importlib.util.spec_from_file_location("evidence_lab_onboarding_driver", DRIVER_PATH)
assert SPEC and SPEC.loader
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class OnboardingDriverTests(unittest.TestCase):
    def start(self, root: Path, locale_answer: str = "2") -> tuple[Path, dict]:
        session_path = root / "onboarding-session.json"
        args = argparse.Namespace(
            session=session_path,
            host="codex",
            source="timsmykov/evidence-lab-plugins",
            ref="release-2026.08.99",
            marketplace="evidence-lab-plugins",
            catalog=ROOT / "packs/core/evidence-lab-core/catalog/packs.json",
            release_lock=root / "release-lock.json",
        )
        session, result = driver.command_start(args)
        self.assertEqual("answer-language", result["next_action"])
        self.assertEqual(60, result["progress_update_seconds"])
        session, result = driver.command_answer(argparse.Namespace(session=session_path, text=locale_answer))
        return session_path, result

    def test_language_is_always_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            session_path = Path(temporary) / "session.json"
            session, result = driver.command_start(argparse.Namespace(
                session=session_path, host="codex", source="source", ref="release-2026.08.99",
                marketplace="evidence-lab-plugins", catalog=ROOT / "packs/core/evidence-lab-core/catalog/packs.json",
                release_lock=Path(temporary) / "lock.json",
            ))
            self.assertEqual("language", session["stage"])
            self.assertIn("English", result["user_message"])
            self.assertEqual([], session["answers"])

    def test_numeric_answers_advance_one_question_at_a_time(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            session_path, result = self.start(Path(temporary), "1")
            self.assertIn("Question 1 of 4", result["user_message"])
            for number in range(1, 4):
                _, result = driver.command_answer(argparse.Namespace(session=session_path, text="1"))
                self.assertIn(f"Question {number + 1} of 4", result["user_message"])
            self.assertEqual(3, len(read(session_path)["answers"]))

    def test_invalid_numeric_answer_repeats_same_question(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            session_path, _ = self.start(Path(temporary), "2")
            _, result = driver.command_answer(argparse.Namespace(session=session_path, text="99"))
            self.assertEqual("INVALID_OPTION", result["diagnostic_code"])
            self.assertIn("\u0412\u043e\u043f\u0440\u043e\u0441 1 \u0438\u0437 4", result["user_message"])
            self.assertEqual([], read(session_path)["answers"])

    def test_numeric_flow_reaches_one_locked_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            session_path, _ = self.start(Path(temporary), "1")
            with patch.object(driver, "build_installation_plan", side_effect=self.fake_plan):
                for _ in range(4):
                    session, result = driver.command_answer(argparse.Namespace(session=session_path, text="1"))
            self.assertEqual("awaiting-confirmation", session["stage"])
            self.assertEqual("confirm-plan", result["next_action"])
            self.assertEqual("RECOMMENDATION", result["user_message"])

    @staticmethod
    def fake_plan(session: dict, session_path: Path, profile: dict) -> str:
        session["profile"] = profile
        session["selected_pack_ids"] = ["evidence-lab-core"]
        session["plan_path"] = str(session_path.parent / "installation-plan.json")
        session["stage"] = "awaiting-confirmation"
        return "RECOMMENDATION"

    def test_free_text_uses_bounded_normalization_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            session_path, _ = self.start(Path(temporary), "2")
            answers = ["\u041c\u043e\u043b\u0435\u043a\u0443\u043b\u044f\u0440\u043d\u0430\u044f \u0430\u0440\u0445\u0435\u043e\u043b\u043e\u0433\u0438\u044f", "4", "1, 2", "2"]
            for answer in answers:
                session, result = driver.command_answer(argparse.Namespace(session=session_path, text=answer))
            self.assertEqual("needs-normalization", session["stage"])
            self.assertEqual("submit-normalization-candidate", result["next_action"])
            self.assertIn("\u0441\u043e\u043f\u043e\u0441\u0442\u0430\u0432\u043b\u044e", result["user_message"])

    def test_confirmation_is_separate_and_idempotent_state_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.json"
            driver.write_json_atomic(path, {
                "schema_version": 1, "stage": "awaiting-confirmation", "locale": "ru",
                "answers": [], "steps": [],
            })
            session, result = driver.command_confirm(argparse.Namespace(session=path, text="\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e"))
            self.assertEqual("awaiting-confirmation", session["stage"])
            self.assertEqual("CONFIRMATION_REQUIRED", result["diagnostic_code"])
            session, result = driver.command_confirm(argparse.Namespace(session=path, text="\u0434\u0430"))
            self.assertEqual("confirmed", session["stage"])
            self.assertEqual("apply", result["next_action"])

    def test_normalization_follow_up_updates_only_the_pending_answer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            session_path = root / "session.json"
            driver.write_json_atomic(session_path, {
                "schema_version": 1, "stage": "needs-normalization", "locale": "en",
                "answers": [], "steps": [], "pending_follow_up_question_id": "domains",
            })
            driver.write_json_atomic(root / "onboarding-answers.json", {
                "schema_version": 1, "locale": "en", "answers": [
                    {"question_id": "domains", "selected_option_ids": [], "free_text": "Applied science"},
                    {"question_id": "workflows", "selected_option_ids": ["writing"]},
                ],
            })
            session, result = driver.command_follow_up(argparse.Namespace(session=session_path, text="Biomedical engineering"))
            answers = read(root / "onboarding-answers.json")["answers"]
            self.assertIn("Biomedical engineering", answers[0]["free_text"])
            self.assertNotIn("Biomedical engineering", json.dumps(answers[1]))
            self.assertNotIn("pending_follow_up_question_id", session)
            self.assertEqual("submit-normalization-candidate", result["next_action"])

    def test_user_copy_has_no_internal_commands_or_paths(self) -> None:
        forbidden = ("python3", "scripts/", "pack.json", "traceback", "--locale", "schema")
        for locale in ("en", "ru"):
            messages = [
                driver.question_message(locale, number, number == 1) for number in range(1, 5)
            ] + list(driver.copy(locale).values())
            for message in messages:
                if isinstance(message, str):
                    self.assertFalse(any(token in message.casefold() for token in forbidden), message)


if __name__ == "__main__":
    unittest.main()
