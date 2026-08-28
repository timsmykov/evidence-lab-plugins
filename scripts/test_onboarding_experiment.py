#!/usr/bin/env python3
"""Deterministic tests for the local onboarding experiment harness."""
from __future__ import annotations

import json
import os
import argparse
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator

from onboarding_experiment import (
    SUCCESS_STATES,
    EventJournal,
    ExperimentError,
    ExperimentTimeout,
    REQUIRED_PASS_CHECKS,
    REQUIRED_PASS_HASHES,
    REQUIRED_REVIEW_CHECKS,
    artifact_index,
    build_receipt_from_run,
    cohort_has_safety_failure,
    cohort_should_stop,
    file_sha256,
    make_receipt,
    object_sha256,
    parse_codex_jsonl,
    prepare_artifact_root,
    resume_inventory,
    seal_manifest,
    summarize_cohort,
    validate_receipt_artifacts,
    validate_scenario_bundle,
    validate_supersession,
    verify_manifest_identity,
    verify_probe_command,
    verify_review_binding,
    write_secure_bytes,
    write_secure_json,
)
from onboarding_experiment_adapter import (
    SandboxSpec,
    bwrap_prefix,
    codex_exec_args,
    sanitized_observation,
    run_turn,
    thread_id_from_events,
)
import run_onboarding_experiment as experiment_cli

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests" / "acceptance" / "onboarding-terra-10.scenarios.ru.json"
FIXTURES = ROOT / "tests" / "fixtures" / "experiment"
FORMATTER = ROOT / "packs" / "core" / "evidence-lab-core" / "skills" / "citation-management" / "scripts" / "format_bibtex.py"


def sample_manifest() -> dict:
    return seal_manifest(
        product={
            "commit": "1" * 40,
            "release_tag": "release-2026.08.5",
            "release_lock_sha256": "2" * 64,
            "catalog_sha256": "3" * 64,
        },
        harness={
            "commit": "4" * 40,
            "schema_bundle_sha256": "5" * 64,
            "scenario_bundle_sha256": "6" * 64,
            "probe_input_sha256": "7" * 64,
            "probe_expected_sha256": "8" * 64,
            "probe_prompt_sha256": "9" * 64,
        },
        runtime={
            "codex_version": "codex-cli test",
            "model": "gpt-5.6-terra",
            "reasoning_effort": "medium",
            "isolation": "bubblewrap-linux-v1",
            "model_preflight": {"status": "passed", "probe": "terra-medium-response-v1"},
            "timeouts_seconds": {
                "verify": 1,
                "turn": 1,
                "plan": 1,
                "apply": 1,
                "new_task": 1,
                "attempt": 1,
            },
        },
        scenario_ids=[f"scenario-{index}" for index in range(10)],
        created_at="2026-08-28T00:00:00Z",
    )


def pass_proof() -> tuple[dict[str, bool], dict[str, str], list[dict[str, str]]]:
    return (
        {key: True for key in REQUIRED_PASS_CHECKS},
        {key: "a" * 64 for key in REQUIRED_PASS_HASHES},
        [{"id": "evidence-lab-core", "version": "1.0.0"}],
    )


def append_success(journal: EventJournal) -> None:
    for state in SUCCESS_STATES:
        journal.append(state, state)


def completed_run(root: Path, manifest: dict, scenario_id: str) -> dict:
    run_root = root / "runs" / scenario_id / "attempt-01"
    journal = EventJournal(
        run_root / "events.jsonl",
        f"{manifest['cohort_id']}/{scenario_id}/attempt-01",
    )
    append_success(journal)
    observations = run_root / "observations"
    write_secure_json(
        observations / "plan.json",
        {
            "schema_version": 1,
            "plan_id": "a" * 16,
            "host": "codex",
            "marketplace": {"name": "evidence-lab-plugins", "source": "example/repo", "ref": manifest["product"]["release_tag"]},
            "release": {
                "tag": manifest["product"]["release_tag"],
                "channel": "stable",
                "source_commit": manifest["product"]["commit"],
                "lock_digest": manifest["product"]["release_lock_sha256"],
            },
            "selection_plan": {},
            "operations": [
                {"action": "ensure-marketplace", "target": "evidence-lab-plugins"},
                {"action": "install-pack", "target": "evidence-lab-core", "version": "1.0.0"},
            ],
        },
    )
    write_secure_json(
        observations / "installation-state.json",
        {
            "schema_version": 1,
            "plan_id": "a" * 16,
            "host": "codex",
            "release": {
                "tag": manifest["product"]["release_tag"],
                "channel": "stable",
                "source_commit": manifest["product"]["commit"],
                "lock_digest": manifest["product"]["release_lock_sha256"],
            },
            "status": "ready",
            "desired": [{"id": "evidence-lab-core", "version": "1.0.0"}],
            "installed_before": [],
            "installed_after": [{"id": "evidence-lab-core", "version": "1.0.0"}],
            "operations": [{"action": "install-pack", "target": "evidence-lab-core", "status": "completed"}],
            "error": None,
        },
    )
    write_secure_json(
        observations / "new-task-probe.json",
        {
            "schema_version": 1,
            "installed_script": "skills/citation-management/scripts/format_bibtex.py",
            "actual_output_sha256": "b" * 64,
            "expected_output_sha256": "b" * 64,
            "match": True,
        },
    )
    return build_receipt_from_run(
        manifest=manifest,
        scenario_id=scenario_id,
        attempt=1,
        terminal_state="COMPLETED",
        run_root=run_root,
    )


class ExperimentCoreTests(unittest.TestCase):
    def test_scenario_bundle_has_frozen_quotas(self) -> None:
        scenarios = validate_scenario_bundle(json.loads(SCENARIOS.read_text(encoding="utf-8")))
        self.assertEqual(10, len(scenarios))

    def test_scenario_bundle_rejects_changed_quota(self) -> None:
        bundle = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        bundle["scenarios"][0]["language"] = "en"
        with self.assertRaises(ExperimentError):
            validate_scenario_bundle(bundle)

    def test_manifest_identity_detects_drift(self) -> None:
        manifest = sample_manifest()
        verify_manifest_identity(manifest)
        manifest["runtime"]["reasoning_effort"] = "high"
        with self.assertRaises(ExperimentError):
            verify_manifest_identity(manifest)

    def test_journal_is_append_only_and_hash_chained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            journal = EventJournal(path, "cohort/scenario/attempt-01")
            append_success(journal)
            self.assertEqual("COMPLETED", journal.verify()[-1]["next_state"])
            rows = path.read_text(encoding="utf-8").splitlines()
            row = json.loads(rows[2])
            row["payload"] = {"changed": True}
            rows[2] = json.dumps(row)
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            with self.assertRaises(ExperimentError):
                journal.verify()

    def test_journal_rejects_out_of_order_and_truncated_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            journal = EventJournal(path, "cohort/scenario/attempt-01")
            with self.assertRaises(ExperimentError):
                journal.append("LANGUAGE_SELECTED", "LANGUAGE_SELECTED")
            path.write_text('{"type":', encoding="utf-8")
            with self.assertRaises(ExperimentError):
                journal.verify()

    def test_terminal_classification_and_stop_policy(self) -> None:
        manifest = sample_manifest()
        product = make_receipt(
            manifest=manifest,
            scenario_id="scenario-0",
            attempt=1,
            terminal_state="PRODUCT_FAIL",
            checks={},
            hashes={},
        )
        safety = make_receipt(
            manifest=manifest,
            scenario_id="scenario-1",
            attempt=1,
            terminal_state="SAFETY_FAIL",
            checks={},
            hashes={},
        )
        self.assertFalse(cohort_should_stop([product]))
        self.assertTrue(cohort_should_stop([product, safety]))
        self.assertEqual("FAIL", product["product_outcome"])

    def test_only_infrastructure_attempt_can_be_superseded(self) -> None:
        manifest = sample_manifest()
        invalid = make_receipt(
            manifest=manifest,
            scenario_id="scenario-0",
            attempt=1,
            terminal_state="INFRA_INVALID",
            checks={},
            hashes={},
        )
        checks, hashes, packs = pass_proof()
        retry = make_receipt(
            manifest=manifest,
            scenario_id="scenario-0",
            attempt=2,
            terminal_state="COMPLETED",
            checks=checks,
            hashes=hashes,
            selected_packs=packs,
            supersedes_run_id=invalid["run_id"],
        )
        validate_supersession([invalid, retry])
        invalid["terminal_state"] = "PRODUCT_FAIL"
        with self.assertRaises(ExperimentError):
            validate_supersession([invalid, retry])

    def test_summary_is_deterministic_and_requires_all_scenarios(self) -> None:
        manifest = sample_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            rows = [completed_run(root, manifest, f"scenario-{index}") for index in range(10)]
            first = summarize_cohort(manifest, rows, cohort_root=root)
            second = summarize_cohort(manifest, list(reversed(rows)), cohort_root=root)
            self.assertEqual(first, second)
            self.assertTrue(first["gate_pass"])
            self.assertFalse(summarize_cohort(manifest, rows[:-1], cohort_root=root)["gate_pass"])

    def test_operator_asserted_receipts_cannot_create_a_false_pass(self) -> None:
        manifest = sample_manifest()
        checks, hashes, packs = pass_proof()
        rows = [
            make_receipt(
                manifest=manifest,
                scenario_id=f"scenario-{index}",
                attempt=1,
                terminal_state="COMPLETED",
                checks=checks,
                hashes=hashes,
                selected_packs=packs,
            )
            for index in range(10)
        ]
        self.assertFalse(summarize_cohort(manifest, rows)["gate_pass"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            with self.assertRaises(ExperimentError):
                validate_receipt_artifacts(rows[0], root / "runs" / "scenario-0" / "attempt-01")

    def test_tampered_artifact_invalidates_a_derived_receipt(self) -> None:
        manifest = sample_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            receipt = completed_run(root, manifest, "scenario-0")
            write_secure_json(
                root / "runs" / "scenario-0" / "attempt-01" / "observations" / "plan.json",
                {"tampered": True},
            )
            with self.assertRaises(ExperimentError):
                validate_receipt_artifacts(
                    receipt,
                    root / "runs" / "scenario-0" / "attempt-01",
                    manifest=manifest,
                )

    def test_unreceipted_safety_failure_stops_cohort(self) -> None:
        manifest = sample_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            run_root = root / "runs" / "scenario-0" / "attempt-01"
            journal = EventJournal(run_root / "events.jsonl", f"{manifest['cohort_id']}/scenario-0/attempt-01")
            journal.append("SANDBOX_READY", "SANDBOX_READY")
            journal.append("SAFETY_FAIL", "SAFETY_FAILURE")
            self.assertTrue(cohort_has_safety_failure(root, manifest=manifest))

    def test_start_run_enforces_scenario_order_and_one_active_attempt(self) -> None:
        manifest = sample_manifest()
        with tempfile.TemporaryDirectory() as directory:
            artifact_root = Path(directory)
            artifact_root.chmod(0o700)
            cohort = artifact_root / manifest["cohort_id"]
            cohort.mkdir(mode=0o700)
            write_secure_json(cohort / "manifest.json", manifest)
            wrong = argparse.Namespace(
                artifact_root=str(artifact_root),
                cohort_id=manifest["cohort_id"],
                scenario_id="scenario-1",
                attempt=1,
            )
            with mock.patch.object(experiment_cli, "verify_harness_candidate"):
                with self.assertRaisesRegex(ExperimentError, "next deterministic attempt"):
                    experiment_cli.cmd_start_run(wrong)
                first = argparse.Namespace(**{**vars(wrong), "scenario_id": "scenario-0"})
                with mock.patch("builtins.print"):
                    experiment_cli.cmd_start_run(first)
                with self.assertRaisesRegex(ExperimentError, "finish or resume"):
                    experiment_cli.cmd_start_run(wrong)

    def test_resume_inventory_preserves_every_interrupted_success_state(self) -> None:
        manifest = sample_manifest()
        for stop_index, expected_state in enumerate(SUCCESS_STATES[:-1], 1):
            with self.subTest(state=expected_state), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                root.chmod(0o700)
                run_root = root / "runs" / "scenario-0" / "attempt-01"
                journal = EventJournal(
                    run_root / "events.jsonl",
                    f"{manifest['cohort_id']}/scenario-0/attempt-01",
                )
                for state in SUCCESS_STATES[:stop_index]:
                    journal.append(state, state)
                row = resume_inventory(manifest, root)[0]
                self.assertEqual(expected_state, row["state"])
                self.assertEqual("RESUME", row["action"])

    def test_parser_rejects_malformed_codex_jsonl(self) -> None:
        with self.assertRaises(ExperimentError):
            parse_codex_jsonl('{"type":"thread.started"}\n{"type":')

    def test_probe_requires_installed_cache_and_observable_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "installed"
            script = installed / "skills" / "citation-management" / "scripts" / "format_bibtex.py"
            script.parent.mkdir(parents=True)
            script.write_text("pass\n", encoding="utf-8")
            events = [{
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": f"python3 {script} in.bib out.bib --rekey --deduplicate --sort key",
                    "exit_code": 0,
                    "status": "completed",
                },
            }]
            self.assertEqual(
                "skills/citation-management/scripts/format_bibtex.py",
                verify_probe_command(events, installed_plugin_root=installed),
            )
            source_script = ROOT / "packs" / "foundation" / "citation-management" / "skills" / "citation-management" / "scripts" / "format_bibtex.py"
            events[0]["item"]["command"] = f"python3 {source_script} in.bib out.bib --rekey --deduplicate --sort key"
            with self.assertRaises(ExperimentError):
                verify_probe_command(events, installed_plugin_root=installed)

    def test_frozen_bibtex_probe_is_reproducible(self) -> None:
        self.assertTrue(FORMATTER.is_file())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.bib"
            subprocess.run(
                [
                    "python3",
                    str(FORMATTER),
                    str(FIXTURES / "citation-probe-input.bib"),
                    "--output",
                    str(output),
                    "--rekey",
                    "--deduplicate",
                    "--sort",
                    "key",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(file_sha256(FIXTURES / "citation-probe-expected.bib"), file_sha256(output))

    def test_artifact_index_rejects_permissions_symlinks_and_private_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "cohort"
            root.mkdir(mode=0o700)
            write_secure_json(root / "safe.json", {"ok": True})
            artifact_index(root)
            os.chmod(root / "safe.json", 0o644)
            with self.assertRaises(ExperimentError):
                artifact_index(root)
            os.chmod(root / "safe.json", 0o600)
            (root / "link").symlink_to(root / "safe.json")
            with self.assertRaises(ExperimentError):
                artifact_index(root)
            (root / "link").unlink()
            write_secure_json(root / "unsafe.json", {"session_id": "opaque"})
            with self.assertRaises(ExperimentError):
                artifact_index(root)

    def test_runtime_directory_is_not_part_of_reviewable_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "cohort"
            runtime = root / "runtime"
            runtime.mkdir(parents=True, mode=0o700)
            os.chmod(root, 0o700)
            write_secure_json(runtime / "resume.json", {"session_id": "private"})
            self.assertEqual(0, artifact_index(root)["artifact_count"])

    def test_artifact_root_must_be_outside_repository(self) -> None:
        with self.assertRaises(ExperimentError):
            prepare_artifact_root(ROOT / "experiment-output", repository_root=ROOT)

    def test_review_is_bound_to_candidate_and_index(self) -> None:
        manifest = sample_manifest()
        index = {"schema_version": 1, "artifacts": [], "artifact_count": 0}
        review = {
            "candidate_id": manifest["candidate_id"],
            "artifact_index_sha256": object_sha256(index),
            "reviewer": "Tim",
            "decision": "ACCEPT",
            "checks": {key: True for key in REQUIRED_REVIEW_CHECKS},
        }
        verify_review_binding(review, manifest, index)
        review["checks"]["manifest"] = False
        with self.assertRaises(ExperimentError):
            verify_review_binding(review, manifest, index)

    def test_all_experiment_schemas_are_well_formed(self) -> None:
        for path in sorted((ROOT / "schemas").glob("experiment-*.schema.json")):
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))

    def test_manifest_receipt_and_event_match_published_schemas(self) -> None:
        manifest = sample_manifest()
        checks, hashes, packs = pass_proof()
        receipt = make_receipt(
            manifest=manifest,
            scenario_id="scenario-0",
            attempt=1,
            terminal_state="COMPLETED",
            checks=checks,
            hashes=hashes,
            selected_packs=packs,
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = EventJournal(Path(directory) / "events.jsonl", receipt["run_id"])
            journal.append("SANDBOX_READY", "SANDBOX_READY")
            event = journal.verify()[0]
        for value, name in (
            (manifest, "experiment-cohort-manifest.schema.json"),
            (receipt, "experiment-run-receipt.schema.json"),
            (event, "experiment-run-event.schema.json"),
        ):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            errors = list(Draft202012Validator(schema).iter_errors(value))
            self.assertEqual([], errors, msg=f"{name}: {errors}")

    def test_completed_receipt_cannot_pass_without_proof(self) -> None:
        manifest = sample_manifest()
        with self.assertRaises(ExperimentError):
            make_receipt(
                manifest=manifest,
                scenario_id="scenario-0",
                attempt=1,
                terminal_state="COMPLETED",
                checks={},
                hashes={},
            )

    def test_fake_codex_stream_is_sanitized_and_resumable(self) -> None:
        events = [
            {"type": "thread.started", "thread_id": "opaque-test-thread"},
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Please choose English or Russian."},
            },
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "python3 /home/researcher/.codex/plugins/example/tool.py /opt/evidence-lab-release/scripts/render_onboarding.py /workspace/input",
                    "aggregated_output": "English or Russian",
                    "exit_code": 0,
                    "status": "completed",
                },
            },
        ]
        self.assertEqual("opaque-test-thread", thread_id_from_events(events))
        observation = sanitized_observation(events)
        self.assertNotIn("opaque-test-thread", json.dumps(observation))
        self.assertEqual(1, len(observation["commands"]))
        self.assertNotIn("aggregated_output", observation["commands"][0])
        self.assertIn("$CODEX_HOME", observation["commands"][0]["command"])
        self.assertIn("$RELEASE", observation["commands"][0]["command"])
        self.assertIn("$WORKSPACE", observation["commands"][0]["command"])

    def test_bubblewrap_hides_release_from_new_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            binary = temp / "codex"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o700)
            auth = temp / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            auth.chmod(0o600)
            release = temp / "release"
            release.mkdir()
            spec = SandboxSpec(binary, auth, temp / "home", temp / "workspace", release)
            onboarding = bwrap_prefix(spec, expose_release=True)
            new_task = bwrap_prefix(spec, expose_release=False)
            self.assertIn("/opt/evidence-lab-release", onboarding)
            self.assertNotIn("/opt/evidence-lab-release", new_task)
            self.assertIn("--tmpfs", new_task)
            self.assertIn("/", new_task)
            self.assertNotIn(("--ro-bind", "/etc", "/etc"), list(zip(new_task, new_task[1:], new_task[2:])))

    @unittest.skipUnless(shutil.which("bwrap"), "bubblewrap is not installed")
    def test_real_sandbox_cannot_read_host_secret_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            binary = temp / "codex"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o700)
            auth = temp / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            auth.chmod(0o600)
            spec = SandboxSpec(binary, auth, temp / "home", temp / "workspace")
            result = subprocess.run(
                [
                    *bwrap_prefix(spec, expose_release=False),
                    "/usr/bin/python3",
                    "-c",
                    "from pathlib import Path; print(Path('/etc/shadow').exists(), any(Path('/etc/ssh').glob('ssh_host_*')))",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual("False False", result.stdout.strip())

    def test_timeout_is_classified_without_writing_success_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            binary = temp / "codex"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o700)
            auth = temp / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            auth.chmod(0o600)
            spec = SandboxSpec(binary, auth, temp / "home", temp / "workspace")
            with mock.patch("onboarding_experiment_adapter.subprocess.run", side_effect=subprocess.TimeoutExpired("codex", 1)):
                with self.assertRaisesRegex(ExperimentTimeout, "plan timed out") as timeout:
                    run_turn(
                        spec,
                        prompt="start",
                        runtime_root=temp / "runtime",
                        evidence_path=temp / "evidence.json",
                        timeout_seconds=1,
                        stage="plan",
                        expose_release=False,
                    )
            self.assertEqual("plan", timeout.exception.stage)
            self.assertFalse((temp / "evidence.json").exists())

    def test_cli_does_not_accept_operator_asserted_proof_or_version(self) -> None:
        parser = experiment_cli.parser()
        prepare_actions = {action.dest for action in parser._subparsers._group_actions[0].choices["prepare"]._actions}
        finish_actions = {action.dest for action in parser._subparsers._group_actions[0].choices["finish-run"]._actions}
        turn_actions = {action.dest for action in parser._subparsers._group_actions[0].choices["codex-turn"]._actions}
        probe_actions = {action.dest for action in parser._subparsers._group_actions[0].choices["verify-probe"]._actions}
        self.assertNotIn("codex_version", prepare_actions)
        self.assertNotIn("checks", finish_actions)
        self.assertNotIn("hashes", finish_actions)
        self.assertNotIn("selected_packs", finish_actions)
        self.assertNotIn("timeout", turn_actions)
        self.assertIn("stage", turn_actions)
        self.assertNotIn("installed_plugin_root", probe_actions)
        self.assertNotIn("actual_output", probe_actions)
        self.assertNotIn("expected_output", probe_actions)

    def test_prepare_rejects_a_catalog_disguised_as_release_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            checkout = temp / "release"
            (checkout / "scripts").mkdir(parents=True)
            (checkout / "scripts" / "release_snapshot.py").write_text("", encoding="utf-8")
            fake_lock = temp / "catalog.json"
            fake_lock.write_text('{"schema_version": 1}\n', encoding="utf-8")
            with self.assertRaisesRegex(ExperimentError, "release lock tag"):
                experiment_cli.validate_release_candidate(
                    release_tag="release-2026.08.5",
                    release_lock=fake_lock,
                    release_checkout=checkout,
                )

    def test_prepare_rejects_a_dirty_harness_before_sealing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                scenarios=SCENARIOS,
                artifact_root=directory,
                release_tag="release-2026.08.5",
                release_lock=Path(directory) / "release-lock.json",
                release_checkout=Path(directory) / "release",
                codex_binary=Path("/bin/true"),
                auth_file=Path(directory) / "auth.json",
            )
            with mock.patch.object(experiment_cli, "git", return_value=" M scripts/runner.py"):
                with self.assertRaisesRegex(ExperimentError, "worktree must be clean"):
                    experiment_cli.cmd_prepare(args)

    @unittest.skipUnless(shutil.which("bwrap"), "bubblewrap is not installed")
    def test_model_preflight_uses_real_pinned_sandbox_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            temp.chmod(0o700)
            binary = temp / "codex"
            binary.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' '{\"type\":\"thread.started\",\"thread_id\":\"fake-thread\"}'\n"
                "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"EVIDENCE_LAB_PREFLIGHT_OK\"}}'\n",
                encoding="utf-8",
            )
            binary.chmod(0o700)
            auth = temp / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            auth.chmod(0o600)
            self.assertEqual(
                "terra-medium-response-v1",
                experiment_cli.verify_model_preflight(root=temp, codex_binary=binary, auth_file=auth),
            )

    def test_codex_command_pins_terra_medium_for_start_and_resume(self) -> None:
        start = codex_exec_args(prompt="start", thread_id=None)
        resume = codex_exec_args(prompt="next", thread_id="thread-name")
        self.assertIn("gpt-5.6-terra", start)
        self.assertIn('model_reasoning_effort="medium"', start)
        self.assertIn("resume", resume)
        self.assertNotIn("-C", resume)

    @unittest.skipUnless(shutil.which("bwrap"), "bubblewrap is not installed")
    def test_fake_codex_process_runs_inside_real_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            binary = temp / "codex"
            binary.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' '{\"type\":\"thread.started\",\"thread_id\":\"fake-thread\"}'\n"
                "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"ready\"}}'\n",
                encoding="utf-8",
            )
            binary.chmod(0o700)
            auth = temp / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            auth.chmod(0o600)
            release = temp / "release"
            release.mkdir()
            spec = SandboxSpec(binary, auth, temp / "home", temp / "workspace", release)
            thread, observation = run_turn(
                spec,
                prompt="start",
                runtime_root=temp / "runtime",
                evidence_path=temp / "evidence.json",
                timeout_seconds=5,
            )
            self.assertEqual("fake-thread", thread)
            self.assertEqual("ready", observation["final_message"])


if __name__ == "__main__":
    unittest.main()
